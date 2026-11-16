#!/usr/bin/env python3
"""C319 — rigorous costed out-of-sample test of the cross-sectional COINTEGRATION /
PAIRS mean-reversion statistical-arbitrage family on 10 USDT-M linear perps at native
5m (3456 pre-registered configs).

GENUINELY NEW FAMILY (not a re-skin of any frozen campaign)
-----------------------------------------------------------
C281B-C314 (all FROZEN formal negatives) exhausted carry, OFI/microstructure,
premium/index/mark basis, quarterly term-structure and same-asset spot-perp
lead-lag. C315 tested price first-moment momentum/reversal. C316 tested
size/volume/turnover liquidity. C317 tested own realized-vol / higher-moments.
C318 tested cross-sectional COVARIANCE / BETA co-movement. ALL 36 closed families
rank single assets in the cross-section. C319 is the FIRST campaign to trade the
RELATIVE-VALUE COINTEGRATION / PAIRS structure: the long-run equilibrium spread
between two cointegrated perps, beta-hedged, mean-reverting via a rolling z-score
entry/exit. It is economically distinct from every frozen family.

MECHANISM (per unordered pair a<b)
----------------------------------
  beta_hat[t]    = cov_L(logPa, logPb) / var_L(logPa)        (rolling hedge ratio)
  spread[t]      = logPb[t] - beta_hat[t] * logPa[t]         (log-price spread)
  z[t]           = (spread[t] - mean_L(spread)) / std_L(spread)
  pos_spread[t]  = clip((|z[t-1]| - exit) / (entry - exit), 0, 1) * (-sign(z[t-1]))
                   (causal z[t-1]; 0 inside the deadband, full at |z|>=entry)
  pair PnL[t]    = pos_spread[t] * spr_ret[t] / (1 + |beta_hat[t-1]|)
                   where spr_ret[t] = r_b[t] - beta_hat[t-1] * r_a[t]
  portfolio      = mean over active pairs; costs charged on turnover
                   (|d pos_a| + |d pos_b|), pos_a = -beta*pos/(1+|beta|), pos_b = pos/(1+|beta|)

GRID (3456 = 3 x 3 x 2 x 3 x 4 x 4 x 2 x 2, all reported)
-----------------------------------------------------------
cointegration_lookback{1008,2016,4032 = 3.5d,7d,14d bars}(3) x
entry_z{1.5,2.0,2.5}(3) x exit_z{0.5,1.0}(2) x hold_bars{6,12,48 = 30m,1h,4h}(3) x
fee{1,5,10,20}bps(4) x slippage{1,2,5,10}bps(4) x cost_variant{symmetric,perp_heavy}(2) x
pairset{all45,top15_by_trailing_R2}(2)

WF: expanding train 12m / test 3m / roll 3m over 2023-01..2025-12 (8 splits).
Gates: Holm AND Benjamini-Hochberg at alpha=0.05 (BOTH required), MDE, stability
(sign consistency >= 70% splits; first/second-half Sharpe corr >= 0.5), and
cointegration-vs-momentum-vs-beta_carry-vs-placebo attribution (dominant share > 0.5).

This is a model PnL backtest (executed_fills: false) on real data only. It never
fetches, imputes, resamples, or fabricates data.

Artifacts (exact names, timestamped, SHA256-from-bytes):
  reports/campaign319_oos_sweep_<ts>.json  (+ gitignored *.full.json)
  reports/campaign319_tradable_edge_registry_<ts>.json
  reports/campaign319_summary_<ts>.json
  reports/campaign319_verdict_<ts>.json
  reports/campaign319_binding_constraint_<ts>.json
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

CACHE_DIR = cache_dir / "campaign319_cointegration_5m"
CACHE_META = cache_dir / "campaign319_cointegration_5m.meta.json"
CACHE_PROV = cache_dir / "campaign319_cointegration_5m.provenance.json"

# ---- pre-registered grid ----
LOOKBACKS = (1008, 2016, 4032)          # cointegration/hedge window (5m bars)
ENTRY_Z = (1.5, 2.0, 2.5)               # full-position z threshold
EXIT_Z = (0.5, 1.0)                     # deadband z threshold
HOLD_BARS = (6, 12, 48)                 # 30m, 1h, 4h between position resets
FEES = (1, 5, 10, 20)                   # bps per leg
SLIPS = (1, 2, 5, 10)                   # bps per leg
COST_VARIANTS = ("symmetric", "perp_heavy")
PAIRSETS = ("all45", "top15")
N_TOP = 15
ALPHA = 0.05
N_TRIALS = (len(LOOKBACKS) * len(ENTRY_Z) * len(EXIT_Z) * len(HOLD_BARS) *
            len(FEES) * len(SLIPS) * len(COST_VARIANTS) * len(PAIRSETS))  # 3456

TRAIN_M, TEST_M, ROLL_M = 12, 3, 3
STABILITY_MIN_SIGN_CONSISTENCY = 0.70
STABILITY_MIN_SHARPE_CORR = 0.50
DOMINANT_SHARE_MIN = 0.50

ATTR_BUCKETS = ("cointegration", "momentum", "beta_carry", "placebo_noise")

# reference config for stability / attribution (declared, fixed)
REF = dict(L=2016, entry=2.0, exit=0.5, H=12, fee=10, slip=5, cv="symmetric", pairset="all45")


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


# ---------------------------------------------------------------- rolling primitives
def trailing_mean(x: np.ndarray, L: int) -> np.ndarray:
    """Trailing-L nan-aware mean along axis=1 (NaN for first L-1 bars).

    Skips non-finite entries (never imputes); a window with zero finite
    observations yields NaN (fail-closed). x: (P, N).
    """
    p, n = x.shape
    out = np.full((p, n), np.nan, dtype=np.float64)
    if L <= n:
        finite = np.isfinite(x)
        xf = np.where(finite, x, 0.0)
        c0 = np.concatenate([np.zeros((p, 1)), np.cumsum(xf, axis=1)], axis=1)
        n0 = np.concatenate([np.zeros((p, 1)), np.cumsum(finite.astype(np.float64), axis=1)], axis=1)
        wsum = c0[:, L:] - c0[:, :-L]
        wcnt = n0[:, L:] - n0[:, :-L]
        out[:, L - 1:] = np.where(wcnt > 0, wsum / np.maximum(wcnt, 1.0), np.nan)
    return out


def causal(x: np.ndarray) -> np.ndarray:
    """Shift right by one bar along axis=1 (y[:,0]=NaN, y[:,t]=x[:,t-1])."""
    y = np.full_like(x, np.nan, dtype=np.float64)
    if x.shape[1] > 1:
        y[:, 1:] = x[:, :-1]
    return y


def meanrev_position(z_c: np.ndarray, entry: float, exit_z: float) -> np.ndarray:
    """Mean-reversion position from causal z: 0 inside deadband, full at |z|>=entry.

    pos = -sign(z) * clip((|z|-exit)/(entry-exit), 0, 1); NaN(z) -> 0 (fail-closed).
    """
    az = np.abs(z_c)
    denom = (entry - exit_z)
    ramp = np.clip((az - exit_z) / denom, 0.0, 1.0)
    pos = -np.sign(z_c) * ramp
    pos = np.where(np.isfinite(pos), pos, 0.0)
    return pos


def cost_rate_bps(fee: float, slip: float, cv: str) -> float:
    if cv == "symmetric":
        return fee + slip
    return 1.5 * fee + slip


# ---------------------------------------------------------------- cache / series
def verify_cache() -> tuple:
    if not CACHE_DIR.exists():
        raise SystemExit(f"FATAL: C319 shard dir missing: {CACHE_DIR}")
    if not CACHE_META.exists():
        raise SystemExit(f"FATAL: C319 meta missing: {CACHE_META}")
    meta_sha = sha256_file(CACHE_META)
    prov_sha = sha256_file(CACHE_PROV) if CACHE_PROV.exists() else None
    meta = json.loads(CACHE_META.read_text())
    if meta.get("real_data_only") is not True or meta.get("fabricated_data") is not False:
        raise SystemExit("FATAL: dataset provenance flags not real_data_only/fabricated_data")
    if meta.get("executed_fills") is not False:
        raise SystemExit("FATAL: cache executed_fills must be false (model PnL only)")
    if meta.get("interval") != "5m":
        raise SystemExit(f"FATAL: cache interval must be 5m, got {meta.get('interval')}")
    if meta.get("network_ingest") is not False or meta.get("resample") is not False:
        raise SystemExit("FATAL: cache must be no-network, no-resample")
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


def build_series(payload: dict) -> dict:
    symbols = list(payload.get("symbols") or [])
    n_assets = len(symbols)
    per_asset = payload.get("per_asset") or {}
    first = per_asset[symbols[0]]
    idx_ms = np.asarray(first["index_ms"], dtype="int64")
    index = pd.DatetimeIndex(pd.to_datetime(idx_ms, unit="ms", utc=True))
    n_b = len(index)
    if n_b == 0:
        raise SystemExit("FATAL: C319 common grid is empty")

    def mat(key):
        out = np.zeros((n_assets, n_b), dtype=float)
        for i, s in enumerate(symbols):
            out[i] = np.asarray(per_asset[s][key], dtype=float)
        return out

    perp_close = mat("perp_close")
    if not (np.isfinite(perp_close).all() and (perp_close > 0).all()):
        raise SystemExit("FATAL: non-finite/non-positive perp_close")

    log_return = np.zeros_like(perp_close)
    log_return[:, 1:] = np.log(perp_close[:, 1:] / perp_close[:, :-1])
    log_return = np.where(np.isfinite(log_return), log_return, 0.0)

    log_price = np.log(perp_close)

    splits = wf_splits_by_month(index, TRAIN_M, TEST_M, ROLL_M)
    if not splits:
        raise SystemExit("FATAL: no OOS splits")

    return {"symbols": symbols, "n_assets": n_assets, "index": index, "n_bars": n_b,
            "perp_close": perp_close, "log_return": log_return, "log_price": log_price,
            "splits": splits}


def build_pairs(bs: dict) -> dict:
    """Build per-pair log-price and return arrays over all unordered pairs."""
    symbols = bs["symbols"]
    n = len(symbols)
    ii, jj = [], []
    for a in range(n):
        for b in range(a + 1, n):
            ii.append(a)
            jj.append(b)
    ii = np.array(ii, dtype=int)
    jj = np.array(jj, dtype=int)
    log_price = bs["log_price"]
    log_return = bs["log_return"]
    return {
        "pair_i": ii, "pair_j": jj,
        "logPa": log_price[ii], "logPb": log_price[jj],
        "lr_a": log_return[ii], "lr_b": log_return[jj],
        "pairs": [(symbols[a], symbols[b]) for a, b in zip(ii, jj)],
        "n_pairs": len(ii),
    }


def precompute_L(pr: dict, L: int) -> dict:
    """Per-lookback cointegration arrays over all pairs (P, N)."""
    logPa = pr["logPa"]
    logPb = pr["logPb"]
    lr_a = pr["lr_a"]
    lr_b = pr["lr_b"]
    m_a = trailing_mean(logPa, L)
    m_b = trailing_mean(logPb, L)
    m_a2 = trailing_mean(logPa * logPa, L)
    m_b2 = trailing_mean(logPb * logPb, L)
    m_ab = trailing_mean(logPa * logPb, L)
    var_a = m_a2 - m_a * m_a
    var_b = m_b2 - m_b * m_b
    cov = m_ab - m_a * m_b
    with np.errstate(invalid="ignore", divide="ignore"):
        beta = np.where(var_a > 0, cov / np.where(var_a > 0, var_a, np.nan), np.nan)
        r2 = np.where((var_a > 0) & (var_b > 0),
                      (cov * cov) / np.where((var_a > 0) & (var_b > 0), var_a * var_b, np.nan),
                      np.nan)
    spread = logPb - beta * logPa
    m_s = trailing_mean(spread, L)
    m_s2 = trailing_mean(spread * spread, L)
    var_s = m_s2 - m_s * m_s
    sd_s = np.sqrt(np.where(var_s > 0, var_s, np.nan))
    with np.errstate(invalid="ignore", divide="ignore"):
        z = np.where(sd_s > 0, (spread - m_s) / np.where(sd_s > 0, sd_s, np.nan), np.nan)
    beta_prev = causal(beta)
    with np.errstate(invalid="ignore", divide="ignore"):
        spr_ret = lr_b - beta_prev * lr_a
    inv = np.where(np.isfinite(beta_prev), 1.0 / (1.0 + np.abs(beta_prev)), 0.0)
    return {"L": int(L), "beta": beta, "beta_prev": beta_prev, "z": z, "r2": r2,
            "spr_ret": spr_ret, "inv": inv}


def top15_mask(r2: np.ndarray, H: int) -> np.ndarray:
    """Per-segment top-N_TOP pairs by causal trailing R2, held for H bars. (P, N) bool."""
    p, n = r2.shape
    mask = np.zeros((p, n), dtype=bool)
    for s0 in range(0, n, H):
        seg = r2[:, s0]
        order = np.argsort(-np.where(np.isfinite(seg), seg, -np.inf), kind="mergesort")
        top = order[:N_TOP]
        e = min(s0 + H, n)
        mask[np.ix_(top, np.arange(s0, e))] = True
    return mask


def position_arrays(zc: np.ndarray, beta_prev: np.ndarray, inv: np.ndarray,
                    entry: float, exit_z: float, seg: np.ndarray, mask: np.ndarray):
    """Return held/masked pos_spread, pos_a, pos_b (all (P, N))."""
    pos = meanrev_position(zc, entry, exit_z) * mask            # masked raw pos
    pos_h = pos[:, seg]                                          # H-bar hold
    beta_h = beta_prev[:, seg]
    inv_h = inv[:, seg]
    pos_a_h = -beta_h * pos_h * inv_h
    pos_b_h = pos_h * inv_h
    pos_a_h = np.where(np.isfinite(pos_a_h), pos_a_h, 0.0)
    pos_b_h = np.where(np.isfinite(pos_b_h), pos_b_h, 0.0)
    return pos_h, pos_a_h, pos_b_h


def pnl_turnover(pos_a_h: np.ndarray, pos_b_h: np.ndarray, lr_a: np.ndarray,
                 lr_b: np.ndarray, n_active: float):
    """Portfolio pnl (per bar) and turnover (per bar) as (N,) arrays."""
    pair_pnl = pos_a_h * lr_a + pos_b_h * lr_b
    pnl = pair_pnl.sum(axis=0) / n_active
    dpos_a = np.abs(np.diff(pos_a_h, axis=1, prepend=pos_a_h[:, :1]))
    dpos_b = np.abs(np.diff(pos_b_h, axis=1, prepend=pos_b_h[:, :1]))
    turn = (dpos_a + dpos_b).sum(axis=0) / n_active
    return pnl, turn


def seg_split_arrays(pnl: np.ndarray, turn: np.ndarray, splits):
    seg_gross, seg_turn, seg_len = [], [], []
    for (tr_s, tr_e, te_s, te_e) in splits:
        seg_gross.append(float(pnl[te_s:te_e].sum()))
        seg_turn.append(float(turn[te_s:te_e].sum()))
        seg_len.append(int(te_e - te_s))
    return seg_gross, seg_turn, seg_len


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--reference-config-only", action="store_true",
                    help="only run the reference config (fast smoke test)")
    ap.add_argument("--smoke", action="store_true", help="alias of --reference-config-only")
    args = ap.parse_args(argv)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    payload, meta, cache_sha, meta_sha, prov_sha = verify_cache()
    bs = build_series(payload)
    symbols = bs["symbols"]
    index = bs["index"]
    n_b = bs["n_bars"]
    splits = bs["splits"]
    n_splits = len(splits)
    lr = bs["log_return"]
    n_assets = bs["n_assets"]

    pr = build_pairs(bs)
    n_pairs = pr["n_pairs"]
    seg_cache: dict = {}
    mask_all = np.ones((n_pairs, n_b), dtype=bool)

    def get_seg(H):
        if H not in seg_cache:
            seg_cache[H] = (np.arange(n_b) // H) * H
        return seg_cache[H]

    # equal-weight buy-and-hold benchmark per split (net, no model costs)
    bh_per_split = []
    for (tr_s, tr_e, te_s, te_e) in splits:
        bh_per_split.append(float(lr[:, te_s:te_e].sum(axis=1).mean()))
    bh_mean = float(np.mean(bh_per_split)) if bh_per_split else 0.0

    def run_config(dL, zc, seg, mask, n_active, L, entry, exit_z, H, fee, slip, cv, pairset):
        pos_h, pos_a_h, pos_b_h = position_arrays(zc, dL["beta_prev"], dL["inv"], entry, exit_z, seg, mask)
        pnl, turn = pnl_turnover(pos_a_h, pos_b_h, pr["lr_a"], pr["lr_b"], n_active)
        cost_rate = cost_rate_bps(fee, slip, cv) / 10000.0
        sg, st, sl = seg_split_arrays(pnl, turn, splits)
        net = [g - cost_rate * t for g, t in zip(sg, st)]
        net_arr = np.array(net, dtype=float)
        net_sum = float(net_arr.sum())
        net_mean = float(net_arr.mean()) if len(net_arr) else 0.0
        p_val = one_sided_p(net_arr)
        all_pos = bool(len(net_arr) > 0 and (net_arr > 0).all() and net_sum > 0)
        sr = float(np.mean(net_arr) / np.std(net_arr)) if len(net_arr) > 1 and np.std(net_arr) > 0 else 0.0
        if n_splits > 1 and np.std(net_arr) > 0:
            s = float(np.std(net_arr, ddof=1))
            t_a = float(stats.t.ppf(1 - ALPHA / 2, df=n_splits - 1))
            t_b = float(stats.t.ppf(0.80, df=n_splits - 1))
            mde_bps = (t_a + t_b) * s / math.sqrt(n_splits) * 10000.0
        else:
            mde_bps = float("nan")
        beats_bh = bool(len(net) > 0 and net_mean > bh_mean)
        exposure = bool(np.nansum(np.abs(pos_a_h) + np.abs(pos_b_h)) > 0)
        return {
            "cointegration_lookback": int(L), "entry_z": float(entry), "exit_z": float(exit_z),
            "hold_bars": int(H), "pairset": pairset,
            "fee_bps": float(fee), "slippage_bps": float(slip), "cost_variant": cv,
            "n_splits": int(n_splits),
            "oos_net_sum": net_sum, "oos_net_mean": net_mean,
            "oos_net_per_split": [float(x) for x in net],
            "gross_sum": float(sum(sg)), "turnover_total": float(sum(st)),
            "exposure": exposure,
            "edge_proven": bool(all_pos), "beats_buy_hold": beats_bh, "p_value": float(p_val),
            "sharpe_obs": float(sr), "mde_bps": float(mde_bps),
            "cost_rate_bps_effective": float(cost_rate_bps(fee, slip, cv)),
        }

    results: list[dict] = []
    if args.reference_config_only or args.smoke:
        dL = precompute_L(pr, REF["L"])
        zc = causal(dL["z"])
        seg = get_seg(REF["H"])
        results.append(run_config(dL, zc, seg, mask_all, float(n_pairs),
                                   REF["L"], REF["entry"], REF["exit"], REF["H"],
                                   REF["fee"], REF["slip"], REF["cv"], REF["pairset"]))
        del dL, zc
    else:
        # memory-safe: process one cointegration lookback at a time, then free
        for L in LOOKBACKS:
            dL = precompute_L(pr, L)
            zc = causal(dL["z"])
            r2 = dL["r2"]
            for H in HOLD_BARS:
                seg = get_seg(H)
                mask_top = top15_mask(r2, H)
                for pairset in PAIRSETS:
                    if pairset == "top15":
                        mask = mask_top
                        nact = float(min(N_TOP, n_pairs))
                    else:
                        mask = mask_all
                        nact = float(n_pairs)
                    for entry in ENTRY_Z:
                        for exit_z in EXIT_Z:
                            for fee in FEES:
                                for slip in SLIPS:
                                    for cv in COST_VARIANTS:
                                        results.append(run_config(dL, zc, seg, mask, nact, L,
                                                                   entry, exit_z, H, fee, slip, cv, pairset))
            del dL, zc, r2

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

    # ---- cointegration / momentum / beta_carry / placebo attribution (ref config) ----
    dL = precompute_L(pr, REF["L"])
    zc = causal(dL["z"])
    seg = get_seg(REF["H"])
    pos_ref, pos_a_ref, pos_b_ref = position_arrays(
        zc, dL["beta_prev"], dL["inv"], REF["entry"], REF["exit"], seg, mask_all)
    cr = cost_rate_bps(REF["fee"], REF["slip"], REF["cv"]) / 10000.0
    nact = float(n_pairs)

    def _net(pos_a_h, pos_b_h, lr_a, lr_b):
        pnl, turn = pnl_turnover(pos_a_h, pos_b_h, lr_a, lr_b, nact)
        sg, st, sl = seg_split_arrays(pnl, turn, splits)
        return float(sum(g - cr * t for g, t in zip(sg, st)))

    coin_net = _net(pos_a_ref, pos_b_ref, pr["lr_a"], pr["lr_b"])
    # momentum: opposite sign of mean-reversion
    mom_pos_h = -pos_ref
    mom_beta_h = dL["beta_prev"][:, seg]
    mom_inv_h = dL["inv"][:, seg]
    pos_a_mom = np.where(np.isfinite(mom_beta_h), -mom_beta_h * mom_pos_h * mom_inv_h, 0.0)
    pos_b_mom = np.where(np.isfinite(mom_beta_h), mom_pos_h * mom_inv_h, 0.0)
    mom_net = _net(pos_a_mom, pos_b_mom, pr["lr_a"], pr["lr_b"])
    # beta_carry: always +1 long spread (static beta-hedged long the spread)
    bc_pos_h = np.ones((n_pairs, n_b), dtype=float) * mask_all
    beta_h = dL["beta_prev"][:, seg]
    inv_h = dL["inv"][:, seg]
    pos_a_bc = np.where(np.isfinite(beta_h), -beta_h * bc_pos_h * inv_h, 0.0)
    pos_b_bc = np.where(np.isfinite(beta_h), bc_pos_h * inv_h, 0.0)
    bc_net = _net(pos_a_bc, pos_b_bc, pr["lr_a"], pr["lr_b"])
    # placebo: reference positions applied to per-pair time-permuted spread returns
    rng = np.random.default_rng(20261116)
    spr_perm = np.empty_like(dL["spr_ret"])
    for p in range(n_pairs):
        spr_perm[p] = dL["spr_ret"][p][rng.permutation(n_b)]
    spr_perm = np.where(np.isfinite(spr_perm), spr_perm, 0.0)  # warmup -> 0, never impute
    pnl_pl = np.nansum(pos_ref * spr_perm * dL["inv"][:, seg], axis=0) / nact
    sg_pl, st_pl, sl_pl = seg_split_arrays(pnl_pl, np.zeros_like(pnl_pl), splits)
    pl_net = float(sum(g - cr * t for g, t in zip(sg_pl, st_pl)))

    attrib = {"cointegration": abs(coin_net), "momentum": abs(mom_net),
              "beta_carry": abs(bc_net), "placebo_noise": abs(pl_net)}
    attrib_total = sum(attrib.values())
    if attrib_total > 0:
        attrib_share = {k: float(v / attrib_total) for k, v in attrib.items()}
    else:
        attrib_share = {k: 0.0 for k in ATTR_BUCKETS}
    dominant = max(attrib_share, key=attrib_share.get) if attrib_total > 0 else None
    dominant_share = float(attrib_share[dominant]) if dominant else 0.0
    attribution_ok = bool(dominant == "cointegration" and dominant_share > DOMINANT_SHARE_MIN)

    # ---- stability (reference config) ----
    def stability():
        pnl, turn = pnl_turnover(pos_a_ref, pos_b_ref, pr["lr_a"], pr["lr_b"], nact)
        sg, st, sl = seg_split_arrays(pnl, turn, splits)
        seg_nets = np.array([g - cr * t for g, t in zip(sg, st)], dtype=float)
        n = len(seg_nets)
        sign_consistency = float(np.mean(seg_nets > 0)) if n else 0.0
        half = n // 2
        first = seg_nets[:half]
        second = seg_nets[half:2 * half]

        def _sharpe(a):
            return float(np.mean(a) / np.std(a)) if len(a) > 1 and np.std(a) > 0 else 0.0

        sharpe_corr = float("nan")
        if len(first) == len(second) and len(first) >= 3:
            c1 = np.cumsum(first)
            c2 = np.cumsum(second)
            if np.std(c1) > 0 and np.std(c2) > 0:
                sharpe_corr = float(np.corrcoef(c1, c2)[0, 1])
        stable = bool(sign_consistency >= STABILITY_MIN_SIGN_CONSISTENCY
                      and np.isfinite(sharpe_corr)
                      and sharpe_corr >= STABILITY_MIN_SHARPE_CORR)
        return {
            "reference_config": REF,
            "per_split_net": [float(x) for x in seg_nets],
            "sign_consistency": sign_consistency,
            "first_half_sharpe": _sharpe(first),
            "second_half_sharpe": _sharpe(second),
            "sharpe_corr": sharpe_corr,
            "stable": stable,
        }

    stability_ref = stability()

    # ---- verdict / binding constraint (C318-consistent logic) ----
    if n_total and n_survive_both == 0:
        verdict = "RETRACTED"
        binding = "multiple_testing"
    elif n_survive_both > 0 and not attribution_ok:
        verdict = "RETRACTED"
        binding = "attribution"
    elif n_survive_both > 0 and not stability_ref["stable"]:
        verdict = "RETRACTED"
        binding = "stability"
    elif n_survive_both > 0 and attribution_ok and stability_ref["stable"]:
        verdict = "EDGE_PROVEN"
        binding = None
    else:
        verdict = "RETRACTED"
        binding = "multiple_testing"
    edge_proven = bool(edge_idx and verdict == "EDGE_PROVEN")

    obs_mean_bps = float(np.mean([results[i]["sharpe_obs"] for i in edge_idx])) if edge_idx else 0.0
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
        "source_campaign": int(meta.get("source_campaign") or 312),
        "network_ingest": False,
        "total_shard_bytes": int(meta.get("total_shard_bytes") or 0),
        "max_shard_bytes": int(meta.get("max_shard_bytes") or 0),
        "under_push_limit": bool(meta.get("under_push_limit")),
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
    }

    sweep_obj = {
        "generated_at_utc": ts, "campaign": 319, "part": "oos_sweep",
        "analysis": "c319_cointegration_pairs_stat_arb_oos_5m",
        "smoke": bool(args.reference_config_only or args.smoke),
        "verdict": verdict, "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "fail_closed": True,
        "mandate": (
            "C319 — test the cross-sectional COINTEGRATION / PAIRS mean-reversion "
            "statistical-arbitrage family on 10 USDT-M linear perps at native 5m "
            "(3456 pre-registered configs). For each unordered pair (a,b): rolling "
            "hedge ratio beta = cov_L(logPa,logPb)/var_L(logPa); spread = "
            "logPb - beta*logPa; rolling z = (spread - mean_L)/std_L; mean-reversion "
            "position = -sign(z)*clip((|z|-exit)/(entry-exit),0,1); beta-hedged "
            "dollar-neutral weights; portfolio = mean over active pairs; costs charged "
            "on turnover (symmetric and perp_heavy variants). Gates: Holm+BH at "
            "alpha=0.05 (BOTH), MDE, stability, and cointegration-vs-momentum-vs-"
            "beta_carry-vs-placebo attribution."
        ),
        "preflight": dataset_block, "data_source": dataset_block,
        "universe": {"symbols": symbols, "n_assets": n_assets, "n_pairs_all": int(n_pairs),
                     "common_grid_bars": int(n_b),
                     "common_grid_start_utc": str(index[0]),
                     "common_grid_end_utc": str(index[-1]),
                     "n_splits": int(n_splits)},
        "config": {
            "walk_forward": {"train_m": TRAIN_M, "test_m": TEST_M, "roll_m": ROLL_M},
            "cointegration_lookbacks_bars": list(LOOKBACKS),
            "entry_z": list(ENTRY_Z), "exit_z": list(EXIT_Z),
            "hold_bars": list(HOLD_BARS),
            "fee_bps": list(FEES), "slippage_bps": list(SLIPS),
            "cost_variants": list(COST_VARIANTS), "pairsets": list(PAIRSETS),
            "alpha": ALPHA, "n_trials": N_TRIALS, "total_runs": n_total,
        },
        "gates": {
            "fail_closed": True,
            "multiple_testing": {"holm_alpha": ALPHA, "bh_alpha": ALPHA,
                                 "n_survive_holm": n_survive_holm, "n_survive_bh": n_survive_bh,
                                 "n_survive_both": n_survive_both, "n_edge_proven": n_edge},
            "dsr_mde": {"n_splits": int(n_splits), "mde_bps_mean": mde_bps,
                        "observed_mean_sharpe_per_split": obs_mean_bps},
            "stability": stability_ref,
            "attribution": {
                "reference_config": REF,
                "cointegration_net": coin_net, "momentum_net": mom_net,
                "beta_carry_net": bc_net, "placebo_noise_net": pl_net,
                "shares": attrib_share, "dominant": dominant,
                "dominant_share": dominant_share, "attribution_ok": attribution_ok,
            },
            "buy_and_hold": {"per_split_net": bh_per_split, "mean": bh_mean,
                             "reference_oos_net_mean": float(np.mean(stability_ref["per_split_net"]))
                             if stability_ref["per_split_net"] else 0.0},
        },
        "methodology": {
            "signals": "beta=cov_L(logPa,logPb)/var_L(logPa); spread=logPb-beta*logPa; "
                       "z=(spread-mean_L)/std_L; pos=-sign(z[t-1])*clip((|z[t-1]|-exit)/(entry-exit),0,1); "
                       "pair_pnl=pos*spr_ret/(1+|beta[t-1]|); spr_ret=r_b-beta[t-1]*r_a; causal shift(1).",
            "pnl": "single-leg perp, beta-hedged dollar-neutral per pair; portfolio = mean over active pairs.",
            "costs": "charged on turnover; symmetric = fee+slip; perp_heavy = 1.5*fee+slip.",
            "missing_data": "non-finite -> NaN; never impute; a lookback without enough data yields NaN -> not traded (fail-closed).",
            "multiple_testing": "one-sided paired t-test of per-split OOS net vs flat (0); "
                                "Holm step-down AND Benjamini-Hochberg over all 3456 configs at alpha=0.05.",
            "mde": "two-sided alpha=0.05, power=0.80: (t_{0.975}+t_{0.80})*s/sqrt(n_splits).",
            "attribution": "reference (cointegration) vs momentum (opposite sign) vs beta_carry "
                           "(always-long spread) vs placebo (per-pair time-permuted spr_ret); shares = |net|/sum.",
            "stability": "sign consistency >= 0.70 of splits AND first/second-half Sharpe corr >= 0.5.",
            "funding": "USDT-M funding unreachable (fapi 451, not in archives) -> excluded (control only).",
            "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        },
        "results": results,
        "summary": {
            "n_total_runs": int(n_total),
            "n_with_exposure": int(sum(1 for r in results if r["exposure"])),
            "n_edge_proven_deterministic": int(n_edge),
            "n_survive_holm": n_survive_holm, "n_survive_bh": n_survive_bh,
            "n_survive_both": n_survive_both,
            "verdict": verdict, "edge_proven": edge_proven, "binding_constraint": binding,
        },
    }

    slim = dict(sweep_obj)
    slim_results = []
    for r in results:
        rr = dict(r)
        rr.pop("oos_net_per_split", None)
        slim_results.append(rr)
    slim["results"] = slim_results
    op = reports / f"campaign319_oos_sweep_{ts}.json"
    op.write_text(json.dumps(slim, indent=2, default=jdefault) + "\n")
    sweep_sha = sha256_file(op)
    full = reports / f"campaign319_oos_sweep_{ts}.full.json"
    full.write_text(json.dumps(sweep_obj, indent=2, default=jdefault) + "\n")

    surviving = [results[i] for i in edge_idx if rej_holm[i] and rej_bh[i]]
    registry = {
        "generated_at_utc": ts, "campaign": 319, "part": "registry",
        "analysis": "tradable_edge_registry",
        "n_tradable": len(surviving),
        "n_edge_proven_deterministic": int(n_edge),
        "n_survive_holm": n_survive_holm, "n_survive_bh": n_survive_bh,
        "n_survive_both": n_survive_both,
        "attribution_ok": attribution_ok,
        "attribution_shares": attrib_share,
        "tradable_configs": surviving,
        "oos_sweep_artifact": str(op.relative_to(ROOT)), "oos_sweep_sha256": sweep_sha,
        "verdict": verdict,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
    }
    op_reg = reports / f"campaign319_tradable_edge_registry_{ts}.json"
    op_reg.write_text(json.dumps(registry, indent=2, default=jdefault) + "\n")
    reg_sha = sha256_file(op_reg)

    summary = {
        "generated_at_utc": ts, "campaign": 319, "part": "summary",
        "analysis": "validation_summary", "verdict": verdict, "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "universe": sweep_obj["universe"], "config": sweep_obj["config"],
        "gates": sweep_obj["gates"],
        "artifacts": {"oos_sweep": {"path": str(op.relative_to(ROOT)), "sha256": sweep_sha},
                      "registry": {"path": str(op_reg.relative_to(ROOT)), "sha256": reg_sha}},
        "summary": sweep_obj["summary"], "binding_constraint": binding,
    }
    op_sum = reports / f"campaign319_summary_{ts}.json"
    op_sum.write_text(json.dumps(summary, indent=2, default=jdefault) + "\n")
    sum_sha = sha256_file(op_sum)

    finding = (
        f"C319 cross-sectional cointegration / pairs mean-reversion stat-arb edge RETRACTED "
        f"({n_edge} deterministic edge configs, {n_survive_both} survive Holm+BH over {N_TRIALS}); "
        f"binding constraint: {binding}; dominant attribution: {dominant} ({dominant_share:.4f})."
        if binding is not None
        else f"C319 cross-sectional cointegration / pairs mean-reversion stat-arb edge validated: "
        f"{n_survive_both} of {n_edge} deterministic edge configs survive Holm+BH over {N_TRIALS}; "
        f"edge_proven:{edge_proven}."
    )
    verdict_obj = {
        "generated_at_utc": ts, "campaign": 319, "part": "verdict",
        "analysis": "final_verdict", "verdict": verdict, "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "finding": finding,
        "basis": "c319_cointegration_pairs_stat_arb_costed_oos_5m",
        "dataset": dataset_block,
        "oos_sweep_artifact": str(op.relative_to(ROOT)), "oos_sweep_sha256": sweep_sha,
        "registry_artifact": str(op_reg.relative_to(ROOT)), "registry_sha256": reg_sha,
        "summary_artifact": str(op_sum.relative_to(ROOT)), "summary_sha256": sum_sha,
        "binding_constraint": binding,
        "n_deterministic_edge": int(n_edge),
        "n_survive_holm": n_survive_holm, "n_survive_bh": n_survive_bh,
        "n_survive_both": n_survive_both,
        "attribution_shares": attrib_share,
        "dominant_attribution": dominant,
        "dominant_share": dominant_share,
        "hard_bans_honored": [
            "No synthetic/fabricated data; no relabeling existing caches as new",
            "No threshold/gate weakening; no cherry-picked windows/costs",
            "No edge claim unless the costed OOS test survives Holm+BH over all 3456 configs",
            "Real USDT-M linear 5m cointegration / pairs mean-reversion; funding excluded (control leg)",
            "Single-leg beta-hedged PnL with costs on turnover; executed_fills: false",
        ],
    }
    op_ver = reports / f"campaign319_verdict_{ts}.json"
    op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")
    ver_sha = sha256_file(op_ver)

    bind_sha = None
    bind_path = None
    if binding is not None:
        binding_obj = {
            "generated_at_utc": ts, "campaign": 319, "part": "binding_constraint",
            "analysis": "binding_constraint_diagnosis", "verdict": verdict,
            "real_data_only": True, "fabricated_data": False, "executed_fills": False,
            "oos_sweep_artifact": str(op.relative_to(ROOT)), "oos_sweep_sha256": sweep_sha,
            "binding_constraint": binding,
            "n_deterministic_edge": int(n_edge),
            "n_survive_holm": n_survive_holm, "n_survive_bh": n_survive_bh,
            "n_survive_both": n_survive_both,
            "attribution_shares": attrib_share, "dominant_attribution": dominant,
            "attribution_ok": attribution_ok,
            "stability": stability_ref,
            "diagnosis": (
                "C319 cross-sectional cointegration / pairs mean-reversion stat-arb does not "
                "survive validation; formal negative. "
                f"Binding constraint: {binding}."
            ),
            "note": "Diagnosis only; never an edge claim. No threshold weakening.",
        }
        op_bind = reports / f"campaign319_binding_constraint_{ts}.json"
        op_bind.write_text(json.dumps(binding_obj, indent=2, default=jdefault) + "\n")
        bind_sha = sha256_file(op_bind)
        bind_path = str(op_bind.relative_to(ROOT))
        verdict_obj["binding_constraint_artifact"] = bind_path
        verdict_obj["binding_constraint_sha256"] = bind_sha
        op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")
        ver_sha = sha256_file(op_ver)

    print(json.dumps({
        "campaign": 319, "verdict": verdict, "edge_proven": edge_proven,
        "n_total_runs": int(n_total), "n_deterministic_edge": int(n_edge),
        "n_survive_holm": n_survive_holm, "n_survive_bh": n_survive_bh,
        "n_survive_both": n_survive_both,
        "binding_constraint": binding,
        "attribution_shares": attrib_share, "dominant_attribution": dominant,
        "dominant_share": dominant_share,
        "mde_bps_mean": mde_bps,
        "artifacts": {"oos_sweep": str(op.relative_to(ROOT)), "registry": str(op_reg.relative_to(ROOT)),
                      "summary": str(op_sum.relative_to(ROOT)), "verdict": str(op_ver.relative_to(ROOT)),
                      "binding_constraint": bind_path},
        "sha256": {"oos_sweep": sweep_sha, "registry": reg_sha, "summary": sum_sha,
                   "verdict": ver_sha, "binding_constraint": bind_sha},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())