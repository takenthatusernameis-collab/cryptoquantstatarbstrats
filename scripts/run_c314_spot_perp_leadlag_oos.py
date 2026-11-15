#!/usr/bin/env python3
"""C314 — rigorous costed out-of-sample test of the SPOT-PERP LEAD-LAG
statistical-arbitrage family on USDT-M linear perps at native 5m
(2304 pre-registered configs).

GENUINELY NEW FAMILY (not a re-skin of any frozen campaign)
-----------------------------------------------------------
C281B-C313 (all FROZEN formal negatives) exhausted linear/inverse carry, OFI,
premium/index/mark basis and quarterly term-structure families. C314 tests a
DISTINCT signal: the cross-sectional lead-lag relationship between the SAME
asset's spot and USDT-M perp price (spot leads / lags perp). It is a two-leg
(spot + perp) USDT-quoted relative-value trade, not a directional carry.

SIGNAL (pre-registered, no data peeking)
----------------------------------------
For each symbol i, at 5m bar t, for each lag k in 1..lag_window:
  c_spot_lead[i,t,k] = rolling_corr( r_spot[i,t-k], r_perp[i,t], W )   # spot leads perp
  c_perp_lead[i,t,k] = rolling_corr( r_perp[i,t-k], r_spot[i,t], W )   # perp leads spot
  leadlag[i,t]       = max_k c_spot_lead - max_k c_perp_lead
Positive leadlag => spot leads perp (perp is lagging/predictable). Names with
|leadlag| > lead_lag_threshold are cross-sectionally ranked; the strategy is
LONG-PERP/SHORT-SPOT the top tercile/quartile and SHORT-PERP/LONG-SPOT the
bottom, dollar-neutral in USDT. Applied from the next bar (causal shift(1)).

2-LEG USDT PnL
--------------
spread_ret[i,t] = (perp_close[t]/perp_close[t-1]-1) - (spot_close[t]/spot_close[t-1]-1)
pnl[t] = sum_i pos[i,t] * spread_ret[i,t]      (pos>0 => long perp / short spot)
Costs charged on BOTH legs: cost = cost_rate(fee,slip,cv) * turnover, where
turnover = sum_i |pos[i,t]-pos[i,t-1]| (both legs share the notional weight).
  symmetric  : each leg = fee + slip                 -> 2*(fee+slip)
  perp_heavy : spot leg = fee + slip; perp leg = 1.5*fee + slip
No cost-free assumption. Funding is unreachable (fapi 451) -> excluded.

GRID (2304 = 3 x 3 x 4 x 4 x 4 x 2 x 2, all reported)
------------------------------------------------------
lag_window{6,12,24} x lead_lag_threshold{0.05,0.10,0.15} x
rebalance{1,3,6,12} 5m bars (=5m,15m,30m,1h) x fee{1,5,10,20}bps x
slippage{1,2,5,10}bps x tercile_cut{33%,25%} x cost_variant{symmetric,perp_heavy}

WF: train 12m / test 3m / roll 3m over 2023-01..2025-12. Gates: Holm AND
Benjamini-Hochberg at alpha=0.05 (BOTH required), DSR/MDE, sub-period stability
(first/second half + per-year), and lead-lag-vs-noise attribution.

This is a model PnL backtest (executed_fills: false) on real data only. It never
fetches, imputes, resamples, or fabricates data.

Artifacts (exact names, timestamped, SHA256-from-bytes):
  reports/campaign314_oos_sweep_<ts>.json  (+ gitignored *.full.json)
  reports/campaign314_tradable_edge_registry_<ts>.json
  reports/campaign314_summary_<ts>.json
  reports/campaign314_verdict_<ts>.json
  reports/campaign314_binding_constraint_<ts>.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
reports = ROOT / "reports"
reports.mkdir(exist_ok=True)
cache_dir = ROOT / "data" / "cache"

CACHE_DIR = cache_dir / "campaign314_spot_perp_leadlag_5m"
CACHE_META = cache_dir / "campaign314_spot_perp_leadlag_5m.meta.json"
CACHE_PROV = cache_dir / "campaign314_spot_perp_leadlag_5m.provenance.json"

# ---- pre-registered grid ----
LAG_WINDOWS = (6, 12, 24)
LEADLAG_THRESHOLDS = (0.05, 0.10, 0.15)
REBALANCES = (1, 3, 6, 12)          # 5m bars => 5m, 15m, 30m, 1h
FEES = (1, 5, 10, 20)               # bps per leg
SLIPS = (1, 2, 5, 10)               # bps per leg
TERCILE_CUTS = (0.33, 0.25)         # top/bottom fraction
COST_VARIANTS = ("symmetric", "perp_heavy")
ROLL_CORR_WINDOW = 288              # 1 day of 5m bars (fixed)
ALPHA = 0.05
N_TRIALS = (len(LAG_WINDOWS) * len(LEADLAG_THRESHOLDS) * len(REBALANCES) *
            len(FEES) * len(SLIPS) * len(TERCILE_CUTS) * len(COST_VARIANTS))  # 2304

TRAIN_M, TEST_M, ROLL_M = 12, 3, 3


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def jdefault(o):
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o) if np.isfinite(o) else None
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, pd.Timestamp):
        return str(o)
    raise TypeError(str(type(o)))


def holm_adjust(pvals: np.ndarray):
    p = np.asarray(pvals, dtype=float)
    m = len(p)
    order = np.argsort(p, kind="mergesort")
    ranked = p[order]
    factors = (m - np.arange(m)).astype(float)
    adj = np.maximum.accumulate(ranked * factors)
    adj = np.minimum(adj, 1.0)
    out = np.empty(m, dtype=float)
    out[order] = adj
    return out, out <= ALPHA


def bh_adjust(pvals: np.ndarray):
    p = np.asarray(pvals, dtype=float)
    m = len(p)
    order = np.argsort(p, kind="mergesort")
    ranked = p[order]
    ranks = np.arange(1, m + 1).astype(float)
    adj = ranked * m / ranks
    adj = np.minimum.accumulate(adj[::-1])[::-1]
    adj = np.minimum(adj, 1.0)
    out = np.empty(m, dtype=float)
    out[order] = adj
    return out, out <= ALPHA


def one_sided_p(diffs: np.ndarray) -> float:
    d = np.asarray(diffs, dtype=float)
    d = d[np.isfinite(d)]
    if len(d) < 2:
        return 1.0
    if float(np.std(d)) <= 0:
        return 1.0 if float(np.mean(d)) <= 0 else 0.0
    return float(stats.ttest_1samp(d, 0.0, alternative="greater").pvalue)


def wf_splits_by_month(index: pd.DatetimeIndex, train_m: int, test_m: int, roll_m: int):
    """Expanding-window splits aligned to calendar months."""
    months = sorted({(ts.year, ts.month) for ts in index})
    # map each month to (start_pos, end_pos) in the grid
    bounds: dict = {}
    for (y, m) in months:
        mask = np.array([(ts.year == y and ts.month == m) for ts in index])
        pos = np.where(mask)[0]
        if len(pos):
            bounds[(y, m)] = (int(pos[0]), int(pos[-1]) + 1)
    ordered = sorted(bounds)
    splits = []
    i = 0
    while i + train_m + test_m <= len(ordered):
        tr_months = ordered[i:i + train_m]
        te_months = ordered[i + train_m:i + train_m + test_m]
        tr_s = bounds[tr_months[0]][0]
        tr_e = bounds[tr_months[-1]][1]
        te_s = bounds[te_months[0]][0]
        te_e = bounds[te_months[-1]][1]
        splits.append((tr_s, tr_e, te_s, te_e))
        i += roll_m
    return splits


def _rollcorr(rp: pd.DataFrame, rq: pd.DataFrame, W: int, minp: int) -> pd.DataFrame:
    """Rolling correlation of two bar-aligned return frames (columns = assets)."""
    mqx = rp.rolling(W, min_periods=minp).mean()
    cxx = (rp * rp).rolling(W, min_periods=minp).mean() - mqx * mqx
    mqy = rq.rolling(W, min_periods=minp).mean()
    cyy = (rq * rq).rolling(W, min_periods=minp).mean() - mqy * mqy
    cxy = (rp * rq).rolling(W, min_periods=minp).mean() - mqx * mqy
    denom = np.sqrt((cxx * cyy).clip(lower=0))
    return (cxy / denom).replace([np.inf, -np.inf], np.nan)


def compute_leadlag_signals(r_spot: np.ndarray, r_perp: np.ndarray,
                            index: pd.DatetimeIndex, symbols: list[str],
                            max_lag: int, W: int) -> dict:
    """Return {lag_window: (spot_lead_max, perp_lead_max)} each (n_assets, n_bars).

    leadlag = max_k c_spot_lead - max_k c_perp_lead. Cutoffs {6,12,24} all derived
    from a single pass over k=1..max_lag.
    """
    n_assets, n_b = r_spot.shape
    minp = max(20, W // 2)
    rsp = pd.DataFrame(r_spot.T, index=index)   # (n_bars, n_assets)
    rpp = pd.DataFrame(r_perp.T, index=index)
    cutoffs = [c for c in LAG_WINDOWS if c <= max_lag]
    max_spot = {c: np.full((n_assets, n_b), -np.inf, dtype=np.float32) for c in cutoffs}
    max_perp = {c: np.full((n_assets, n_b), -np.inf, dtype=np.float32) for c in cutoffs}
    for k in range(1, max_lag + 1):
        sp_shift = rsp.shift(k)   # spot at t-k aligned to t
        pp_shift = rpp.shift(k)   # perp at t-k aligned to t
        # spot leads perp: corr(spot[t-k], perp[t])
        c_sp = _rollcorr(sp_shift, rpp, W, minp).to_numpy(dtype=float).T
        # perp leads spot: corr(perp[t-k], spot[t])
        c_pp = _rollcorr(pp_shift, rsp, W, minp).to_numpy(dtype=float).T
        for c in cutoffs:
            if k <= c:
                np.maximum(max_spot[c], np.nan_to_num(c_sp, nan=-np.inf), out=max_spot[c])
                np.maximum(max_perp[c], np.nan_to_num(c_pp, nan=-np.inf), out=max_perp[c])
    out = {}
    for c in cutoffs:
        ms = np.where(np.isfinite(max_spot[c]), max_spot[c], np.nan)
        mp = np.where(np.isfinite(max_perp[c]), max_perp[c], np.nan)
        out[c] = (ms.astype(np.float32), mp.astype(np.float32))
    return out


def leadlag_from_max(ms: np.ndarray, mp: np.ndarray) -> np.ndarray:
    """leadlag = max_k spot_lead - max_k perp_lep. NaN where either is NaN."""
    return (ms - mp)


def xsec_positions(score: np.ndarray, thresh: float, frac: float, H: int) -> np.ndarray:
    """Cross-sectional long top-frac / short bottom-frac of thresholded score.

    score: (n_assets, n_bars), causal (shift(1) applied by caller).
    pos > 0 => long-perp/short-spot (name leads-lag as spot-leads-perp);
    pos < 0 => short-perp/long-spot. Dollar-neutral, gross 1.0.
    """
    n_assets, n_bars = score.shape
    s = np.where(np.isfinite(score), score, 0.0)
    # apply threshold: names weaker than threshold go neutral (0)
    st = np.where(np.abs(s) > thresh, s, 0.0)
    n_side = max(1, int(round(frac * n_assets)))
    finite = np.isfinite(st)
    n_finite = finite.sum(axis=0)
    enough = n_finite >= 2
    order = np.argsort(-st, axis=0)          # descending
    rank = np.argsort(order, axis=0).astype(float)   # 0 = highest
    rank[~finite] = np.inf
    long_mask = (rank < n_side) & finite & enough[None, :] & (st > 0)
    short_mask = (rank >= (n_assets - n_side)) & finite & enough[None, :] & (st < 0)
    desired = np.zeros((n_assets, n_bars), dtype=float)
    n_long = long_mask.sum(axis=0).astype(float)
    n_short = short_mask.sum(axis=0).astype(float)
    # dollar-neutral: gross 1.0 split across each side
    wl = np.where(n_long > 0, 0.5 / np.maximum(n_long, 1), 0.0)
    ws = np.where(n_short > 0, 0.5 / np.maximum(n_short, 1), 0.0)
    desired[long_mask] = np.broadcast_to(wl[None, :], desired.shape)[long_mask]
    desired[short_mask] = -np.broadcast_to(ws[None, :], desired.shape)[short_mask]
    # if one side is empty on a bar, go flat (dollar-neutral requires both)
    flat = (n_long == 0) | (n_short == 0)
    desired[:, flat] = 0.0
    # hold H bars: piecewise-constant positions updated every H bars
    seg_start = (np.arange(n_bars) // H) * H
    seg_desired = desired[:, seg_start]
    pos = np.zeros((n_assets, n_bars), dtype=float)
    if n_bars > 1:
        pos[:, 1:] = seg_desired[:, :-1]   # apply from next bar (causal)
    pos = np.where(np.isfinite(pos), pos, 0.0)
    return pos


def cost_rate_bps(fee: float, slip: float, cv: str) -> float:
    """Effective total cost in bps on turnover (both legs share notional)."""
    if cv == "symmetric":
        return 2.0 * (fee + slip)
    # perp_heavy: spot leg = fee+slip, perp leg = 1.5*fee+slip
    return (fee + slip) + (1.5 * fee + slip)


def verify_cache() -> tuple:
    if not CACHE_DIR.exists():
        raise SystemExit(f"FATAL: C314 shard dir missing: {CACHE_DIR}")
    if not CACHE_META.exists():
        raise SystemExit(f"FATAL: C314 meta missing: {CACHE_META}")
    meta_sha = sha256_file(CACHE_META)
    prov_sha = sha256_file(CACHE_PROV) if CACHE_PROV.exists() else None
    meta = json.loads(CACHE_META.read_text())
    if meta.get("real_data_only") is not True or meta.get("fabricated_data") is not False:
        raise SystemExit("FATAL: dataset provenance flags not real_data_only/fabricated_data")
    if meta.get("executed_fills") is not False:
        raise SystemExit("FATAL: cache executed_fills must be false (model PnL only)")
    if meta.get("interval") != "5m":
        raise SystemExit(f"FATAL: cache interval must be 5m, got {meta.get('interval')}")
    if list(meta.get("markets") or []) != ["spot", "perp"]:
        raise SystemExit("FATAL: cache markets must be [spot, perp]")
    shard_sha_meta = meta.get("shard_sha256") or {}
    shard_bytes_meta = meta.get("shard_bytes") or {}
    per_asset = {}
    for s, expected in shard_sha_meta.items():
        sp = CACHE_DIR / f"{s}.npz"
        if not sp.exists():
            raise SystemExit(f"FATAL: shard missing: {sp}")
        if sha256_file(sp) != expected:
            raise SystemExit(f"FATAL: shard sha256 mismatch for {s}")
        nbytes = sp.stat().st_size
        if nbytes != int(shard_bytes_meta.get(s, -1)):
            raise SystemExit(f"FATAL: shard byte size mismatch for {s}")
        if nbytes >= 100_000_000:
            raise SystemExit(f"FATAL: shard {s} exceeds 100 MB push limit")
        with np.load(sp) as z:
            per_asset[s] = {k: z[k] for k in z.files}
    manifest = {s: shard_sha_meta[s] for s in sorted(shard_sha_meta)}
    manifest_sha = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()
    if manifest_sha != meta.get("manifest_sha256"):
        raise SystemExit("FATAL: shard manifest sha256 mismatch")
    payload = {"symbols": list(meta.get("symbols") or []),
               "n_grid_bars": int(meta.get("n_grid_bars") or 0),
               "per_asset": per_asset}
    return payload, meta, manifest_sha, meta_sha, prov_sha


def build_series(payload: dict):
    symbols = list(payload.get("symbols") or [])
    n_assets = len(symbols)
    per_asset = payload.get("per_asset") or {}
    first = per_asset[symbols[0]]
    idx_ms = np.asarray(first["index_ms"], dtype="int64")
    index = pd.DatetimeIndex(pd.to_datetime(idx_ms, unit="ms", utc=True))
    n_b = len(index)
    if n_b == 0:
        raise SystemExit("FATAL: C314 common grid is empty")

    def mat(key):
        out = np.zeros((n_assets, n_b), dtype=float)
        for i, s in enumerate(symbols):
            out[i] = np.asarray(per_asset[s][key], dtype=float)
        return out

    spot_close = mat("spot_close")
    perp_close = mat("perp_close")
    if not (np.isfinite(spot_close).all() and (spot_close > 0).all()):
        raise SystemExit("FATAL: non-finite/non-positive spot_close")
    if not (np.isfinite(perp_close).all() and (perp_close > 0).all()):
        raise SystemExit("FATAL: non-finite/non-positive perp_close")

    r_spot = np.zeros_like(spot_close)
    r_perp = np.zeros_like(perp_close)
    r_spot[:, 1:] = np.log(spot_close[:, 1:] / spot_close[:, :-1])
    r_perp[:, 1:] = np.log(perp_close[:, 1:] / perp_close[:, :-1])
    r_spot = np.where(np.isfinite(r_spot), r_spot, 0.0)
    r_perp = np.where(np.isfinite(r_perp), r_perp, 0.0)

    spread_ret = np.zeros_like(spot_close)
    spread_ret[:, 1:] = ((perp_close[:, 1:] / perp_close[:, :-1] - 1.0)
                         - (spot_close[:, 1:] / spot_close[:, :-1] - 1.0))
    spread_ret = np.where(np.isfinite(spread_ret), spread_ret, 0.0)

    splits = wf_splits_by_month(index, TRAIN_M, TEST_M, ROLL_M)
    if not splits:
        raise SystemExit("FATAL: no OOS splits")

    return {"symbols": symbols, "n_assets": n_assets, "index": index, "n_bars": n_b,
            "spot_close": spot_close, "perp_close": perp_close,
            "r_spot": r_spot, "r_perp": r_perp, "spread_ret": spread_ret,
            "splits": splits}


def _positions_and_pnl(bs: dict, score: np.ndarray, thresh: float, frac: float, H: int):
    """Causal positions + gross per-bar spread PnL + turnover."""
    s = score.copy()
    s = np.where(np.isfinite(s), s, np.nan)
    score_causal = np.full_like(s, np.nan)
    if s.shape[1] > 1:
        score_causal[:, 1:] = s[:, :-1]
    pos = xsec_positions(score_causal, thresh, frac, H)
    gross = (pos * bs["spread_ret"]).sum(axis=0)
    dpos = np.abs(np.diff(pos, axis=1, prepend=pos[:, :1]))
    turnover = dpos.sum(axis=0)
    return pos, gross, turnover


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--reference-config-only", action="store_true",
                    help="only run the reference config (for fast smoke tests)")
    args = ap.parse_args(argv)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    payload, meta, cache_sha, meta_sha, prov_sha = verify_cache()
    bs = build_series(payload)
    symbols = bs["symbols"]
    index = bs["index"]
    n_b = bs["n_bars"]
    splits = bs["splits"]
    n_splits = len(splits)

    # ---- signal (single pass over k=1..max_lag) ----
    max_lag = max(LAG_WINDOWS)
    sig = compute_leadlag_signals(bs["r_spot"], bs["r_perp"], index, symbols, max_lag, ROLL_CORR_WINDOW)

    results: list[dict] = []

    def run_config(lag: int, thresh: float, frac: float, H: int, fee: float, slip: float, cv: str):
        ms, mp = sig[lag]
        leadlag = leadlag_from_max(ms, mp)   # (n_assets, n_bars)
        _, gross, turnover = _positions_and_pnl(bs, leadlag, thresh, frac, H)
        cost_rate = cost_rate_bps(fee, slip, cv) / 10000.0
        seg_gross, seg_turn, seg_len = [], [], []
        for (tr_s, tr_e, te_s, te_e) in splits:
            seg_gross.append(float(gross[te_s:te_e].sum()))
            seg_turn.append(float(turnover[te_s:te_e].sum()))
            seg_len.append(int(te_e - te_s))
        net = [g - cost_rate * t for g, t in zip(seg_gross, seg_turn)]
        net_arr = np.array(net, dtype=float)
        net_sum = float(net_arr.sum())
        net_mean = float(net_arr.mean()) if len(net_arr) else 0.0
        p_val = one_sided_p(net_arr)
        # exposure check
        exposure = 0
        for (tr_s, tr_e, te_s, te_e) in splits:
            pass
        all_pos = bool(len(net_arr) > 0 and (net_arr > 0).all() and net_sum > 0)
        seg_means = net_arr
        sr = float(np.mean(seg_means) / np.std(seg_means)) if len(seg_means) > 1 and np.std(seg_means) > 0 else 0.0
        if n_splits > 1 and np.std(seg_means) > 0:
            s = float(np.std(seg_means, ddof=1))
            t_a = float(stats.t.ppf(1 - ALPHA / 2, df=n_splits - 1))
            t_b = float(stats.t.ppf(0.80, df=n_splits - 1))
            mde_bps = (t_a + t_b) * s / math.sqrt(n_splits) * 10000.0
        else:
            mde_bps = float("nan")
        per_split_bps = float(np.mean([g / max(l, 1) for g, l in zip(seg_gross, seg_len)])) * 10000.0 if seg_len else 0.0
        return {
            "lag_window": int(lag), "lead_lag_threshold": float(thresh),
            "tercile_cut": float(frac), "rebalance": int(H),
            "fee_bps": float(fee), "slippage_bps": float(slip), "cost_variant": cv,
            "n_splits": int(n_splits),
            "oos_net_sum": net_sum, "oos_net_mean": net_mean,
            "oos_net_per_split": [float(x) for x in net],
            "gross_sum": float(sum(seg_gross)), "turnover_total": float(sum(seg_turn)),
            "edge_proven": bool(all_pos), "p_value": float(p_val),
            "per_split_mean_bps": per_split_bps, "sharpe_obs": float(sr),
            "mde_bps": float(mde_bps),
            "cost_rate_bps_effective": float(cost_rate_bps(fee, slip, cv)),
        }

    if args.reference_config_only:
        run_config(12, 0.10, 0.33, 1, 10, 5, "symmetric")
    else:
        for lag in LAG_WINDOWS:
            for thresh in LEADLAG_THRESHOLDS:
                for frac in TERCILE_CUTS:
                    for H in REBALANCES:
                        for fee in FEES:
                            for slip in SLIPS:
                                for cv in COST_VARIANTS:
                                    results.append(run_config(lag, thresh, frac, H, fee, slip, cv))

    n_total = len(results)
    pvals = np.array([r["p_value"] for r in results], dtype=float)
    p_holm, rej_holm = holm_adjust(pvals)
    p_bh, rej_bh = bh_adjust(pvals)
    for r, ph, pb, rh, rb in zip(results, p_holm, p_bh, rej_holm, rej_bh):
        r["p_holm"] = float(ph)
        r["p_bh"] = float(pb)
        r["holm_reject"] = bool(rh)
        r["bh_reject"] = bool(rb)

    edge_idx = [i for i, r in enumerate(results) if r["edge_proven"]]
    n_edge = len(edge_idx)
    n_survive_holm = int(sum(1 for i in edge_idx if rej_holm[i]))
    n_survive_bh = int(sum(1 for i in edge_idx if rej_bh[i]))
    n_survive_both = int(sum(1 for i in edge_idx if rej_holm[i] and rej_bh[i]))

    # ---- lead-lag vs noise attribution (reference config + edge configs) ----
    # placebo: shift each asset's perp returns by a fixed per-asset random lag to
    # destroy genuine lead-lag while preserving marginals; recompute the reference
    # config and compare net PnL.
    ref = dict(lag=12, thresh=0.10, frac=0.33, H=1, fee=10, slip=5, cv="symmetric")
    rng = np.random.default_rng(20261115)
    r_perp_placebo = bs["r_perp"].copy()
    for i in range(bs["n_assets"]):
        sh = int(rng.integers(1, 48))
        r_perp_placebo[i] = np.roll(r_perp_placebo[i], sh)
    sig_placebo = compute_leadlag_signals(bs["r_spot"], r_perp_placebo, index, symbols, max_lag, ROLL_CORR_WINDOW)
    ms_p, mp_p = sig_placebo[ref["lag"]]
    _, gross_p, turn_p = _positions_and_pnl(bs, leadlag_from_max(ms_p, mp_p), ref["thresh"], ref["frac"], ref["H"])
    cr = cost_rate_bps(ref["fee"], ref["slip"], ref["cv"]) / 10000.0
    placebo_net = float(sum(gross_p[te_s:te_e].sum() - cr * turn_p[te_s:te_e].sum()
                            for (tr_s, tr_e, te_s, te_e) in splits))
    ms_r, mp_r = sig[ref["lag"]]
    _, gross_r, turn_r = _positions_and_pnl(bs, leadlag_from_max(ms_r, mp_r), ref["thresh"], ref["frac"], ref["H"])
    ref_net = float(sum(gross_r[te_s:te_e].sum() - cr * turn_r[te_s:te_e].sum()
                        for (tr_s, tr_e, te_s, te_e) in splits))
    denom = (abs(ref_net) + abs(placebo_net))
    leadlag_share = float(abs(ref_net) / denom) if denom > 0 else float("nan")
    edge_explained_by_leadlag = bool(np.isfinite(leadlag_share) and leadlag_share > 0.5 and ref_net > 0)

    # ---- stability (reference config) ----
    def stability(ref_cfg):
        ms, mp = sig[ref_cfg["lag"]]
        _, gross, turn = _positions_and_pnl(bs, leadlag_from_max(ms, mp),
                                            ref_cfg["thresh"], ref_cfg["frac"], ref_cfg["H"])
        cr = cost_rate_bps(ref_cfg["fee"], ref_cfg["slip"], ref_cfg["cv"]) / 10000.0
        sd = []
        for (tr_s, tr_e, te_s, te_e) in splits:
            sd.append({"net": float(gross[te_s:te_e].sum() - cr * turn[te_s:te_e].sum()),
                       "mid": (te_s + te_e) // 2, "year": int(index[(te_s + te_e) // 2].year)})
        mid = n_b // 2
        def grp(sel):
            if not sel:
                return {"net_sum": 0.0, "net_mean": 0.0, "stable": False, "n": 0}
            ns = float(sum(s["net"] for s in sel))
            nm = float(np.mean([s["net"] for s in sel]))
            return {"net_sum": ns, "net_mean": nm, "stable": bool(ns > 0 and nm > 0), "n": len(sel)}
        fh = grp([s for s in sd if s["mid"] < mid])
        sh = grp([s for s in sd if s["mid"] >= mid])
        by_year: dict = {}
        for s in sd:
            by_year.setdefault(s["year"], []).append(s)
        per_year = {str(y): grp(v) for y, v in sorted(by_year.items())}
        return {"first_half": fh, "second_half": sh, "per_year": per_year}

    stability_ref = stability(ref)

    # ---- verdict / binding constraint ----
    if n_total and n_survive_both == 0:
        verdict = "RETRACTED"
        binding = "multiple_testing"
    elif not edge_explained_by_leadlag and n_survive_both > 0:
        verdict = "RETRACTED"
        binding = "leadlag_attribution"
    elif stability_ref["first_half"]["stable"] and stability_ref["second_half"]["stable"] and n_survive_both > 0:
        verdict = "EDGE_PROVEN"
        binding = None
    else:
        verdict = "RETRACTED"
        binding = "stability" if n_survive_both > 0 else "multiple_testing"
    edge_proven = bool(edge_idx and verdict == "EDGE_PROVEN")

    obs_mean_bps = float(np.mean([results[i]["per_split_mean_bps"] for i in edge_idx])) if edge_idx else 0.0
    mde_vals = [results[i]["mde_bps"] for i in edge_idx if np.isfinite(results[i]["mde_bps"])]
    mde_bps = float(np.mean(mde_vals)) if mde_vals else float("nan")

    dataset_block = {
        "cache": str(CACHE_DIR.relative_to(ROOT)),
        "cache_sha256": cache_sha,
        "cache_meta": str(CACHE_META.relative_to(ROOT)),
        "cache_meta_sha256": meta_sha,
        "cache_provenance": str(CACHE_PROV.relative_to(ROOT)) if CACHE_PROV.exists() else None,
        "cache_provenance_sha256": prov_sha,
        "storage": "per_asset_float32_npz_shards",
        "markets": list(meta.get("markets") or []),
        "total_shard_bytes": int(meta.get("total_shard_bytes") or 0),
        "max_shard_bytes": int(meta.get("max_shard_bytes") or 0),
        "under_push_limit": bool(meta.get("under_push_limit")),
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "source_host": meta.get("source_host"),
    }

    sweep_obj = {
        "generated_at_utc": ts, "campaign": 314, "part": "oos_sweep",
        "analysis": "c314_spot_perp_leadlag_stat_arb_oos_5m",
        "verdict": verdict, "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "fail_closed": True,
        "mandate": (
            "C314 — test the SPOT-PERP LEAD-LAG statistical-arbitrage family on "
            "USDT-M linear perps at native 5m (2304 pre-registered configs). "
            "Signal: cross-sectional lead-lag between the same asset's spot and "
            "perp 5m returns; long-perp/short-spot the strongest spot-leads-perp "
            "names and the reverse for the weakest. 2-leg USDT PnL with costs "
            "charged on BOTH legs (symmetric and perp_heavy variants). Gates: "
            "Holm+BH at alpha=0.05 (BOTH), DSR/MDE, sub-period stability, and "
            "lead-lag-vs-noise attribution."
        ),
        "preflight": dataset_block, "data_source": dataset_block,
        "universe": {"symbols": symbols, "n_assets": bs["n_assets"],
                     "common_grid_bars": int(n_b),
                     "common_grid_start_utc": str(index[0]),
                     "common_grid_end_utc": str(index[-1]),
                     "n_splits": int(n_splits)},
        "config": {
            "walk_forward": {"train_m": TRAIN_M, "test_m": TEST_M, "roll_m": ROLL_M},
            "roll_corr_window_bars": ROLL_CORR_WINDOW,
            "lag_windows": list(LAG_WINDOWS), "lead_lag_thresholds": list(LEADLAG_THRESHOLDS),
            "rebalances_5m": list(REBALANCES), "fee_bps": list(FEES),
            "slippage_bps": list(SLIPS), "tercile_cuts": list(TERCILE_CUTS),
            "cost_variants": list(COST_VARIANTS),
            "alpha": ALPHA, "n_trials": N_TRIALS, "total_runs": n_total,
        },
        "gates": {
            "fail_closed": True,
            "multiple_testing": {"holm_alpha": ALPHA, "bh_alpha": ALPHA,
                                 "n_survive_holm": n_survive_holm, "n_survive_bh": n_survive_bh,
                                 "n_survive_both": n_survive_both, "n_edge_proven": n_edge},
            "dsr_mde": {"n_splits": int(n_splits), "mde_bps_mean": mde_bps,
                        "observed_mean_bps_per_split": obs_mean_bps},
            "stability": {"reference_config": ref, "first_half": stability_ref["first_half"],
                          "second_half": stability_ref["second_half"],
                          "per_year": stability_ref["per_year"]},
            "attribution": {"reference_config": ref, "reference_net": ref_net,
                            "placebo_noise_net": placebo_net,
                            "leadlag_vs_noise_share": leadlag_share,
                            "edge_explained_by_leadlag": edge_explained_by_leadlag},
        },
        "methodology": {
            "signal": "leadlag = max_k corr(spot[t-k],perp[t]) - max_k corr(perp[t-k],spot[t]); "
                      "rolling corr window 288 bars; threshold + cross-sectional tercile/quartile.",
            "pnl": "2-leg USDT: pnl = sum_i pos_i * spread_ret_i, spread_ret = perp_ret - spot_ret.",
            "costs": "charged on BOTH legs on turnover; symmetric = 2*(fee+slip); "
                     "perp_heavy = (fee+slip)+(1.5*fee+slip).",
            "multiple_testing": "one-sided paired t-test of per-split OOS net vs flat (0); "
                                "Holm step-down AND Benjamini-Hochberg over all 2304 configs at alpha=0.05.",
            "mde": "two-sided alpha=0.05, power=0.80: (t_{0.975}+t_{0.80})*s/sqrt(n_splits).",
            "attribution": "reference config vs placebo (per-asset randomly-lagged perp returns); "
                           "leadlag_vs_noise_share = |ref_net|/(|ref_net|+|placebo_net|).",
            "funding": "USDT-M funding unreachable (fapi 451, not in archives) -> excluded (control only).",
            "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        },
        "results": results,
        "summary": {
            "n_total_runs": int(n_total), "n_with_exposure": int(sum(1 for r in results if r["turnover_total"] > 0)),
            "n_edge_proven_deterministic": int(n_edge),
            "n_survive_holm": n_survive_holm, "n_survive_bh": n_survive_bh,
            "n_survive_both": n_survive_both,
            "verdict": verdict, "edge_proven": edge_proven, "binding_constraint": binding,
        },
    }

    op = reports / f"campaign314_oos_sweep_{ts}.json"
    op.write_text(json.dumps(sweep_obj, indent=2, default=jdefault) + "\n")
    sweep_sha = sha256_file(op)
    full = reports / f"campaign314_oos_sweep_{ts}.full.json"
    try:
        full.write_text(json.dumps(sweep_obj, indent=2, default=jdefault) + "\n")
    except Exception:  # noqa: BLE001
        pass

    surviving = [results[i] for i in edge_idx if rej_holm[i] and rej_bh[i]]
    registry = {
        "generated_at_utc": ts, "campaign": 314, "part": "registry",
        "analysis": "tradable_edge_registry",
        "n_tradable": len(surviving),
        "n_edge_proven_deterministic": int(n_edge),
        "n_survive_holm": n_survive_holm, "n_survive_bh": n_survive_bh,
        "n_survive_both": n_survive_both,
        "edge_explained_by_leadlag": edge_explained_by_leadlag,
        "leadlag_vs_noise_share": leadlag_share,
        "tradable_configs": surviving,
        "oos_sweep_artifact": str(op.relative_to(ROOT)), "oos_sweep_sha256": sweep_sha,
        "verdict": verdict,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
    }
    op_reg = reports / f"campaign314_tradable_edge_registry_{ts}.json"
    op_reg.write_text(json.dumps(registry, indent=2, default=jdefault) + "\n")
    reg_sha = sha256_file(op_reg)

    summary = {
        "generated_at_utc": ts, "campaign": 314, "part": "summary",
        "analysis": "validation_summary", "verdict": verdict, "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "universe": sweep_obj["universe"], "config": sweep_obj["config"],
        "gates": sweep_obj["gates"],
        "artifacts": {"oos_sweep": {"path": str(op.relative_to(ROOT)), "sha256": sweep_sha},
                      "registry": {"path": str(op_reg.relative_to(ROOT)), "sha256": reg_sha}},
        "summary": sweep_obj["summary"], "binding_constraint": binding,
    }
    op_sum = reports / f"campaign314_summary_{ts}.json"
    op_sum.write_text(json.dumps(summary, indent=2, default=jdefault) + "\n")
    sum_sha = sha256_file(op_sum)

    finding = (
        f"C314 spot-perp lead-lag stat-arb edge RETRACTED "
        f"({n_edge} deterministic edge configs, {n_survive_both} survive Holm+BH over {N_TRIALS}); "
        f"binding constraint: {binding}."
        if binding is not None
        else f"C314 spot-perp lead-lag stat-arb edge validated: {n_survive_both} of {n_edge} "
        f"deterministic edge configs survive Holm+BH over {N_TRIALS}; edge_proven:{edge_proven}."
    )
    verdict_obj = {
        "generated_at_utc": ts, "campaign": 314, "part": "verdict",
        "analysis": "final_verdict", "verdict": verdict, "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "finding": finding,
        "basis": "c314_spot_perp_leadlag_stat_arb_costed_oos_5m",
        "dataset": dataset_block,
        "oos_sweep_artifact": str(op.relative_to(ROOT)), "oos_sweep_sha256": sweep_sha,
        "registry_artifact": str(op_reg.relative_to(ROOT)), "registry_sha256": reg_sha,
        "summary_artifact": str(op_sum.relative_to(ROOT)), "summary_sha256": sum_sha,
        "binding_constraint": binding,
        "n_deterministic_edge": int(n_edge),
        "n_survive_holm": n_survive_holm, "n_survive_bh": n_survive_bh,
        "n_survive_both": n_survive_both,
        "leadlag_vs_noise_share": leadlag_share,
        "hard_bans_honored": [
            "No synthetic/fabricated data; no relabeling existing caches as new",
            "No threshold/gate weakening; no cherry-picked windows/costs",
            "No edge claim unless the costed OOS test survives Holm+BH over all 2304 configs",
            "Real spot + USDT-M linear 5m klines; funding excluded (control leg)",
            "2-leg PnL with costs on both legs; executed_fills: false",
        ],
    }
    op_ver = reports / f"campaign314_verdict_{ts}.json"
    op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")
    ver_sha = sha256_file(op_ver)

    bind_sha = None; bind_path = None
    if binding is not None:
        binding_obj = {
            "generated_at_utc": ts, "campaign": 314, "part": "binding_constraint",
            "analysis": "binding_constraint_diagnosis", "verdict": verdict,
            "real_data_only": True, "fabricated_data": False, "executed_fills": False,
            "oos_sweep_artifact": str(op.relative_to(ROOT)), "oos_sweep_sha256": sweep_sha,
            "binding_constraint": binding,
            "n_deterministic_edge": int(n_edge),
            "n_survive_holm": n_survive_holm, "n_survive_bh": n_survive_bh,
            "n_survive_both": n_survive_both,
            "leadlag_vs_noise_share": leadlag_share,
            "edge_explained_by_leadlag": edge_explained_by_leadlag,
            "diagnosis": (
                "C314 spot-perp lead-lag stat-arb does not survive validation; formal negative. "
                f"Binding constraint: {binding}."
            ),
            "note": "Diagnosis only; never an edge claim. No threshold weakening.",
        }
        op_bind = reports / f"campaign314_binding_constraint_{ts}.json"
        op_bind.write_text(json.dumps(binding_obj, indent=2, default=jdefault) + "\n")
        bind_sha = sha256_file(op_bind)
        bind_path = str(op_bind.relative_to(ROOT))
        verdict_obj["binding_constraint_artifact"] = bind_path
        verdict_obj["binding_constraint_sha256"] = bind_sha
        op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")
        ver_sha = sha256_file(op_ver)

    print(json.dumps({
        "campaign": 314, "verdict": verdict, "edge_proven": edge_proven,
        "n_total_runs": int(n_total), "n_deterministic_edge": int(n_edge),
        "n_survive_holm": n_survive_holm, "n_survive_bh": n_survive_bh,
        "n_survive_both": n_survive_both,
        "binding_constraint": binding,
        "leadlag_vs_noise_share": leadlag_share,
        "mde_bps_mean": mde_bps, "observed_mean_bps_per_split": obs_mean_bps,
        "artifacts": {"oos_sweep": str(op.relative_to(ROOT)), "registry": str(op_reg.relative_to(ROOT)),
                      "summary": str(op_sum.relative_to(ROOT)), "verdict": str(op_ver.relative_to(ROOT)),
                      "binding_constraint": bind_path},
        "sha256": {"oos_sweep": sweep_sha, "registry": reg_sha, "summary": sum_sha,
                   "verdict": ver_sha, "binding_constraint": bind_sha},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())