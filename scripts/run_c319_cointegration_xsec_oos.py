#!/usr/bin/env python3
"""C319 — rigorous costed out-of-sample test of the cross-sectional COINTEGRATION /
PAIRS mean-reversion statistical-arbitrage family on 10 USDT-M linear perps at
native 5m (1440 pre-registered configs).

GENUINELY NEW FAMILY (not a re-skin of any frozen modern campaign)
-----------------------------------------------------------------
C281B-C314 (all FROZEN formal negatives) exhausted carry, OFI/microstructure,
premium/index/mark basis, quarterly term-structure and same-asset spot-perp
lead-lag. C315 tested price first-moment momentum/reversal. C316 tested
size/volume/turnover liquidity characteristics. C317 tested own realized-vol /
higher-moments. C318 tested RETURN co-movement / covariance / beta. C319 is the
FIRST modern campaign to trade cross-sectional COINTEGRATION / PAIRS
mean-reversion — it models the long-run PRICE-LEVEL equilibrium spread between
assets (rolling hedge-ratio residual of log-price vs an equal-weight market
basket) and trades the transient mispricing (z-score of the equilibrium residual)
as it reverts. It is economically distinct from every prior modern family: not a
return co-movement factor (C318), not own variance / higher-moment (C317), not a
first-moment momentum/reversal (C315), and not a liquidity/size characteristic
(C316). The only prior cointegration work (campaign38, 2026-11-03) ran on 1h/4h/1d
timeframes under an older, pre-C281B gating regime; C319 is the modern, native-5m,
Holm+BH-corrected test.

MARKET PRICE
------------
Equal-weight cross-sectional mean of log-price per bar:
    p_m,t = mean_i log(perp_close_i,t)
All cointegration signals measure each asset's log-price vs this market log-price.

SIGNALS (pre-registered, causal shift(1), cross-sectional rank, dollar-neutral
gross 1.0; mean-reversion sign so LONG cheap (z<0) / SHORT rich (z>0))
-----------------------------------------------------------------------
For each bar t, each symbol i, trailing lookback L (min_periods=L, fail-closed:
insufficient finite observations -> NaN -> not traded):
  spread_z  : z_i = resid_i / std_L(resid_i), where resid_i is the rolling
              hedge-ratio equilibrium residual (beta_i = cov_L(p_i,p_m)/var_L(p_m));
              score = -z_i (betting on reversion to equilibrium).
  spread_zxs: cross-sectionally demeaned z_i (relative value vs peers each bar);
              score = -(z_i - mean_j z_j) (long the cheapest vs the basket).
  z_hedge1  : z1_i = resid1_i / std_L(resid1_i) with an UNHEDGED spread
              (beta fixed at 1); score = -z1_i (classic share-price pairs spread).
  z_hl      : half-life-scaled z; phi_i = rolling AR(1) of resid_i,
              half_life = -ln2/ln(phi) (clipped [0,500] bars);
              score = -z_i / (1 + half_life_i) (fade harder where reversion is fast).
  z_corr    : level-correlation-scaled z; corr_i = corr_L(p_i, p_m) in LEVELS;
              score = -z_i * clip(corr_i, 0, 1) (fade only where cointegration is
              strong).

PORTFOLIO
---------
Single-leg perp: pnl[t] = sum_i pos[i,t] * perp_ret[i,t], pos>0 => long perp.
Costs charged on turnover: cost = cost_rate(fee,slip,cv) * turnover.
  symmetric  : fee + slip per unit turnover (one leg)
  perp_heavy : 1.5*fee + slip per unit turnover (taker-heavy)
Funding is unreachable (fapi 451) -> excluded (control only).

GRID (1440 = 5 x 3 x 3 x 4 x 4 x 2, all reported)
-------------------------------------------------
signal{spread_z,spread_zxs,z_hedge1,z_hl,z_corr}(5) x
lookback{288,1008,2016 = 1d,3.5d,7d bars}(3) x
rebalance{30m,1h,4h = 6,12,48 bars}(3) x
fee{1,5,10,20}bps(4) x slippage{1,2,5,10}bps(4) x
cost_variant{symmetric,perp_heavy}(2)

WF: expanding train 12m / test 3m / roll 3m over 2023-01..2025-12 (8 splits).
Gates: Holm AND Benjamini-Hochberg at alpha=0.05 (BOTH required), MDE, stability
(sign consistency >= 70% splits; first/second-half Sharpe corr >= 0.5), and
hedge-z-vs-relative-value-vs-halflife-vs-placebo attribution (dominant share > 0.5
for a positive claim).

This is a model PnL backtest (executed_fills: false) on real data only. It never
fetches, imputes, resamples, or fabricates data.

Artifact (exact names, timestamped, SHA256-from-bytes):
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
SIGNALS = ("spread_z", "spread_zxs", "z_hedge1", "z_hl", "z_corr")
LOOKBACKS = (288, 1008, 2016)          # 1d, 3.5d, 7d of 5m bars
REBALANCES = (6, 12, 48)               # 30m, 1h, 4h
FEES = (1, 5, 10, 20)                  # bps per leg
SLIPS = (1, 2, 5, 10)                  # bps per leg
COST_VARIANTS = ("symmetric", "perp_heavy")
FRAC = 0.33                            # top/bottom tercile (selection fixed)
ALPHA = 0.05
N_TRIALS = (len(SIGNALS) * len(LOOKBACKS) * len(REBALANCES) *
            len(FEES) * len(SLIPS) * len(COST_VARIANTS))  # 1440

TRAIN_M, TEST_M, ROLL_M = 12, 3, 3
STABILITY_MIN_SIGN_CONSISTENCY = 0.70
STABILITY_MIN_SHARPE_CORR = 0.50
DOMINANT_SHARE_MIN = 0.50
HALF_LIFE_MAX = 500.0

# attribution buckets (spec: hedge-z / relative-value / halflife / placebo_noise)
ATTR_BUCKETS = ("hedge_z", "relative_value", "halflife", "placebo_noise")
ATTR_REPRESENTATIVES = {"hedge_z": "spread_z", "relative_value": "spread_zxs",
                        "halflife": "z_hl"}


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


def _cum_padded(x: np.ndarray):
    finite = np.isfinite(x)
    xf = np.where(finite, x, 0.0)
    cs = np.concatenate([np.zeros((x.shape[0], 1)), np.cumsum(xf, axis=1)], axis=1)
    cc = np.concatenate([np.zeros((x.shape[0], 1)), np.cumsum(finite.astype(np.float64), axis=1)], axis=1)
    return cs, cc


def trailing_nanmean(x: np.ndarray, L: int) -> np.ndarray:
    """Trailing-L nan-aware mean (full window, min_periods=L); NaN before L."""
    out = np.full(x.shape, np.nan, dtype=np.float64)
    if L <= x.shape[1]:
        cs, cc = _cum_padded(x)
        wsum = cs[:, L:] - cs[:, :-L]
        wcnt = cc[:, L:] - cc[:, :-L]
        with np.errstate(invalid="ignore", divide="ignore"):
            out[:, L - 1:] = np.where(wcnt > 0, wsum / np.maximum(wcnt, 1.0), np.nan)
    return out


def finite_or_nan(x: np.ndarray) -> np.ndarray:
    """Non-finite -> NaN (fail-closed; never impute)."""
    return np.where(np.isfinite(x), x, np.nan)


def xsec_positions(score: np.ndarray, frac: float, H: int) -> np.ndarray:
    """Cross-sectional long top-frac / short bottom-frac of score.

    score: (n_assets, n_bars), causal (shift(1) applied by caller).
    Dollar-neutral, gross 1.0. Hold H bars.
    """
    n_assets, n_bars = score.shape
    n_side = max(1, int(round(frac * n_assets)))
    finite = np.isfinite(score)
    s = np.where(finite, score, 0.0)
    order = np.argsort(-s, axis=0)
    rank = np.argsort(order, axis=0).astype(float)
    rank[~finite] = np.inf
    enough = finite.sum(axis=0) >= 2
    long_mask = (rank < n_side) & finite & enough[None, :]
    short_mask = (rank >= (n_assets - n_side)) & finite & enough[None, :]
    desired = np.zeros((n_assets, n_bars), dtype=float)
    n_long = long_mask.sum(axis=0).astype(float)
    n_short = short_mask.sum(axis=0).astype(float)
    wl = np.where(n_long > 0, 0.5 / np.maximum(n_long, 1), 0.0)
    ws = np.where(n_short > 0, 0.5 / np.maximum(n_short, 1), 0.0)
    desired[long_mask] = np.broadcast_to(wl[None, :], desired.shape)[long_mask]
    desired[short_mask] = -np.broadcast_to(ws[None, :], desired.shape)[short_mask]
    flat = (n_long == 0) | (n_short == 0)
    desired[:, flat] = 0.0
    seg_start = (np.arange(n_bars) // H) * H
    seg_desired = desired[:, seg_start]
    pos = np.zeros((n_assets, n_bars), dtype=float)
    if n_bars > 1:
        pos[:, 1:] = seg_desired[:, :-1]   # apply from next bar (causal)
    return np.where(np.isfinite(pos), pos, 0.0)


def cost_rate_bps(fee: float, slip: float, cv: str) -> float:
    """Effective total cost in bps on turnover (single perp leg)."""
    if cv == "symmetric":
        return fee + slip
    return 1.5 * fee + slip


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


def build_series(payload: dict):
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
    # equal-weight market log-price per bar (cointegration basket)
    p_m = np.nanmean(log_price, axis=0)
    p_m = np.where(np.isfinite(p_m), p_m, 0.0)

    splits = wf_splits_by_month(index, TRAIN_M, TEST_M, ROLL_M)
    if not splits:
        raise SystemExit("FATAL: no OOS splits")

    return {"symbols": symbols, "n_assets": n_assets, "index": index, "n_bars": n_b,
            "perp_close": perp_close, "log_return": log_return, "log_price": log_price,
            "p_m": p_m, "splits": splits}


def _base_residual(bs: dict, L: int):
    """Compute shared rolling cointegration quantities (per asset) at lookback L.

    Returns dict with beta, resid, resid_std, z, resid_lag (for AR(1)), and
    level correlation (for z_corr). All causal (trailing, min_periods=L).
    """
    log_p = finite_or_nan(bs["log_price"])
    p_m = bs["p_m"]
    n_assets, n_bars = log_p.shape
    p_m_row = np.broadcast_to(p_m, (1, n_bars)).copy()

    tnm = lambda x: trailing_nanmean(x, L)  # noqa: E731

    mean_pi = tnm(log_p)
    mean_pm = tnm(p_m_row)
    mean_pm2 = tnm(p_m_row * p_m_row)
    mean_pi2 = tnm(log_p * log_p)
    mean_pi_pm = tnm(log_p * p_m_row)

    var_pm = mean_pm2 - mean_pm * mean_pm
    var_pi = mean_pi2 - mean_pi * mean_pi
    cov = mean_pi_pm - mean_pi * mean_pm

    with np.errstate(invalid="ignore", divide="ignore"):
        beta = np.where(var_pm > 0, cov / np.where(var_pm > 0, var_pm, np.nan), np.nan)
        std_pi = np.sqrt(np.where(var_pi > 0, var_pi, np.nan))
        std_pm = np.sqrt(np.where(var_pm > 0, var_pm, np.nan))
        denom = np.where((std_pi > 0) & (std_pm > 0), std_pi * std_pm, np.nan)
        level_corr = np.where(denom > 0, cov / denom, np.nan)

    resid = (log_p - mean_pi) - beta * (p_m_row - mean_pm)
    m_resid2 = tnm(resid * resid)
    resid_std = np.sqrt(np.where(m_resid2 > 0, m_resid2, np.nan))
    with np.errstate(invalid="ignore", divide="ignore"):
        z = np.where(resid_std > 0, resid / np.where(resid_std > 0, resid_std, np.nan), np.nan)

    # AR(1) phi on resid (for half-life); resid_lag[t] = resid[t-1]
    resid_lag = np.full_like(resid, np.nan)
    if n_bars > 1:
        resid_lag[:, 1:] = resid[:, :-1]
    m_r = tnm(resid)
    m_rl = tnm(resid_lag)
    m_rr_l = tnm(resid * resid_lag)
    m_rl2 = tnm(resid_lag * resid_lag)
    cov1 = m_rr_l - m_r * m_rl
    var1 = m_rl2 - m_rl * m_rl
    with np.errstate(invalid="ignore", divide="ignore"):
        phi = np.where(var1 > 0, cov1 / np.where(var1 > 0, var1, np.nan), np.nan)
        # half-life: -ln2/ln(phi) for 0<phi<1; phi<=0 -> fast reversion (hl=0);
        # phi>=1 -> non-mean-reverting (hl=HALF_LIFE_MAX)
        hl = np.full_like(phi, HALF_LIFE_MAX)
        pos = (phi > 0) & (phi < 1)
        hl = np.where(pos, -math.log(2.0) / np.log(np.where(pos, phi, 0.5)), hl)
        hl = np.where(phi <= 0, 0.0, hl)
        hl = np.clip(hl, 0.0, HALF_LIFE_MAX)

    return {"beta": beta, "resid": resid, "resid_std": resid_std, "z": z,
            "level_corr": level_corr, "phi": phi, "half_life": hl, "n_bars": n_bars}


def _unhedged_z(bs: dict, L: int) -> np.ndarray:
    """z-score of the UNHEDGED (beta=1) log-price spread vs market."""
    log_p = finite_or_nan(bs["log_price"])
    p_m = bs["p_m"]
    n_assets, n_bars = log_p.shape
    p_m_row = np.broadcast_to(p_m, (1, n_bars)).copy()
    tnm = lambda x: trailing_nanmean(x, L)  # noqa: E731
    mean_pi = tnm(log_p)
    mean_pm = tnm(p_m_row)
    resid1 = (log_p - mean_pi) - (p_m_row - mean_pm)
    m_r2 = tnm(resid1 * resid1)
    std1 = np.sqrt(np.where(m_r2 > 0, m_r2, np.nan))
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(std1 > 0, resid1 / np.where(std1 > 0, std1, np.nan), np.nan)


def build_score(bs: dict, signal: str, L: int) -> np.ndarray:
    """Build a (n_assets, n_bars) cointegration / pairs mean-reversion score.

    Mean-reversion convention: score = -(z-like mispricing measure) so a CHEAP
    asset (residual below equilibrium, z<0) -> HIGH score (long), and a RICH asset
    (z>0) -> LOW score (short). NaN where inputs are missing (fail-closed).
    """
    if signal == "spread_z":
        return -_base_residual(bs, L)["z"]

    if signal == "spread_zxs":
        z = _base_residual(bs, L)["z"]
        visible = np.isfinite(z)
        cnt = visible.sum(axis=0)
        zsum = np.where(visible, np.nan_to_num(z), 0.0).sum(axis=0)
        zbar = np.where(cnt > 0, zsum / np.maximum(cnt, 1), 0.0)
        z_xs = z - zbar[None, :]
        return -z_xs

    if signal == "z_hedge1":
        return -_unhedged_z(bs, L)

    if signal == "z_hl":
        b = _base_residual(bs, L)
        w = 1.0 / (1.0 + b["half_life"])
        with np.errstate(invalid="ignore"):
            return -b["z"] * w

    if signal == "z_corr":
        b = _base_residual(bs, L)
        w = np.clip(b["level_corr"], 0.0, 1.0)
        w = np.where(np.isfinite(w), w, 0.0)
        return -b["z"] * w

    raise ValueError(f"unknown signal {signal}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--reference-config-only", action="store_true",
                    help="only run the reference config (for fast smoke tests)")
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
    perp_ret = bs["log_return"]

    gross_turn_cache: dict = {}
    score_cache: dict = {}

    def get_score(signal: str, L: int):
        key = (signal, L)
        if key not in score_cache:
            score_cache[key] = build_score(bs, signal, L)
        return score_cache[key]

    def get_gross_turn(signal: str, L: int, H: int):
        key = (signal, L, H)
        if key in gross_turn_cache:
            return gross_turn_cache[key]
        sc = get_score(signal, L)
        sc_causal = np.full_like(sc, np.nan)
        if sc.shape[1] > 1:
            sc_causal[:, 1:] = sc[:, :-1]   # causal shift(1)
        pos = xsec_positions(sc_causal, FRAC, H)
        gross = (pos * perp_ret).sum(axis=0)
        dpos = np.abs(np.diff(pos, axis=1, prepend=pos[:, :1]))
        turn = dpos.sum(axis=0)
        gross_turn_cache[key] = (gross, turn)
        return gross, turn

    results: list[dict] = []

    def run_config(signal: str, L: int, H: int, fee: float, slip: float, cv: str):
        gross, turn = get_gross_turn(signal, L, H)
        cost_rate = cost_rate_bps(fee, slip, cv) / 10000.0
        seg_gross, seg_turn, seg_len = [], [], []
        for (tr_s, tr_e, te_s, te_e) in splits:
            seg_gross.append(float(gross[te_s:te_e].sum()))
            seg_turn.append(float(turn[te_s:te_e].sum()))
            seg_len.append(int(te_e - te_s))
        net = [g - cost_rate * t for g, t in zip(seg_gross, seg_turn)]
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
        per_split_bps = float(np.mean([g / max(l, 1) for g, l in zip(seg_gross, seg_len)])) * 10000.0 if seg_len else 0.0
        return {
            "signal": signal, "lookback": int(L), "rebalance": int(H),
            "selection": float(FRAC),
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

    ref_cfg = dict(signal="spread_z", L=1008, H=12, fee=10, slip=5, cv="symmetric")
    if args.reference_config_only or args.smoke:
        run_config(ref_cfg["signal"], ref_cfg["L"], ref_cfg["H"],
                   ref_cfg["fee"], ref_cfg["slip"], ref_cfg["cv"])
    else:
        for signal in SIGNALS:
            for L in LOOKBACKS:
                for H in REBALANCES:
                    for fee in FEES:
                        for slip in SLIPS:
                            for cv in COST_VARIANTS:
                                results.append(run_config(signal, L, H, fee, slip, cv))

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

    # ---- hedge-z / relative-value / halflife / placebo attribution (ref config) ----
    ref = ref_cfg
    cr = cost_rate_bps(ref["fee"], ref["slip"], ref["cv"]) / 10000.0

    def ref_net_for(signal: str, L: int):
        gross, turn = get_gross_turn(signal, L, ref["H"])
        return float(sum(gross[te_s:te_e].sum() - cr * turn[te_s:te_e].sum()
                         for (tr_s, tr_e, te_s, te_e) in splits))

    hedge_net = ref_net_for(ATTR_REPRESENTATIVES["hedge_z"], ref["L"])
    relval_net = ref_net_for(ATTR_REPRESENTATIVES["relative_value"], ref["L"])
    halflife_net = ref_net_for(ATTR_REPRESENTATIVES["halflife"], ref["L"])

    rng = np.random.default_rng(20261116)
    perp_ret_placebo = perp_ret.copy()
    for i in range(bs["n_assets"]):
        perp_ret_placebo[i] = perp_ret_placebo[i][rng.permutation(n_b)]
    _, turn_ref = get_gross_turn(ref["signal"], ref["L"], ref["H"])
    sc_ref = get_score(ref["signal"], ref["L"])
    sc_ref_causal = np.full_like(sc_ref, np.nan)
    if sc_ref.shape[1] > 1:
        sc_ref_causal[:, 1:] = sc_ref[:, :-1]
    pos_ref = xsec_positions(sc_ref_causal, FRAC, ref["H"])
    gross_placebo = (pos_ref * perp_ret_placebo).sum(axis=0)
    placebo_net = float(sum(gross_placebo[te_s:te_e].sum() - cr * turn_ref[te_s:te_e].sum()
                            for (tr_s, tr_e, te_s, te_e) in splits))

    attrib = {"hedge_z": abs(hedge_net), "relative_value": abs(relval_net),
              "halflife": abs(halflife_net), "placebo_noise": abs(placebo_net)}
    attrib_total = sum(attrib.values())
    if attrib_total > 0:
        attrib_share = {k: float(v / attrib_total) for k, v in attrib.items()}
    else:
        attrib_share = {k: 0.0 for k in ATTR_BUCKETS}
    dominant = max(attrib_share, key=attrib_share.get) if attrib_total > 0 else None
    dominant_share = float(attrib_share[dominant]) if dominant else 0.0
    attribution_ok = bool(dominant in ATTR_REPRESENTATIVES
                          and dominant_share > DOMINANT_SHARE_MIN)

    # ---- stability (reference config) ----
    def stability():
        gross, turn = get_gross_turn(ref["signal"], ref["L"], ref["H"])
        seg_nets = []
        for (tr_s, tr_e, te_s, te_e) in splits:
            nseg = float(gross[te_s:te_e].sum() - cr * turn[te_s:te_e].sum())
            seg_nets.append(nseg)
        seg_nets = np.array(seg_nets, dtype=float)
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
            "reference_config": ref,
            "per_split_net": [float(x) for x in seg_nets],
            "sign_consistency": sign_consistency,
            "first_half_sharpe": _sharpe(first),
            "second_half_sharpe": _sharpe(second),
            "sharpe_corr": sharpe_corr,
            "stable": stable,
        }

    stability_ref = stability()

    # ---- verdict / binding constraint ----
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
        "source_campaign": int(meta.get("source_campaign") or 312),
        "network_ingest": False,
        "total_shard_bytes": int(meta.get("total_shard_bytes") or 0),
        "max_shard_bytes": int(meta.get("max_shard_bytes") or 0),
        "under_push_limit": bool(meta.get("under_push_limit")),
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
    }

    sweep_obj = {
        "generated_at_utc": ts, "campaign": 319, "part": "oos_sweep",
        "analysis": "c319_cointegration_xsec_stat_arb_oos_5m",
        "verdict": verdict, "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "fail_closed": True,
        "mandate": (
            "C319 — test the cross-sectional COINTEGRATION / PAIRS mean-reversion "
            "statistical-arbitrage family on 10 USDT-M linear perps at native 5m "
            "(1440 pre-registered configs). Signals (score = -mispricing, long "
            "cheap/short rich): spread_z (rolling hedge-ratio residual z vs "
            "equal-weight market), spread_zxs (cross-sectionally demeaned z / "
            "relative value), z_hedge1 (unhedged beta=1 spread z), z_hl "
            "(half-life-scaled residual z), z_corr (level-correlation-scaled z). "
            "Single-leg dollar-neutral perp PnL with costs charged on turnover "
            "(symmetric and perp_heavy variants). Gates: Holm+BH at alpha=0.05 "
            "(BOTH), MDE, stability, and hedge-z-vs-relative-value-vs-halflife-"
            "vs-placebo attribution."
        ),
        "preflight": dataset_block, "data_source": dataset_block,
        "universe": {"symbols": symbols, "n_assets": bs["n_assets"],
                     "common_grid_bars": int(n_b),
                     "common_grid_start_utc": str(index[0]),
                     "common_grid_end_utc": str(index[-1]),
                     "n_splits": int(n_splits)},
        "config": {
            "walk_forward": {"train_m": TRAIN_M, "test_m": TEST_M, "roll_m": ROLL_M},
            "signals": list(SIGNALS), "lookbacks_bars": list(LOOKBACKS),
            "rebalances_bars": list(REBALANCES),
            "fee_bps": list(FEES), "slippage_bps": list(SLIPS),
            "selection_frac": float(FRAC), "cost_variants": list(COST_VARIANTS),
            "alpha": ALPHA, "n_trials": N_TRIALS, "total_runs": n_total,
        },
        "gates": {
            "fail_closed": True,
            "multiple_testing": {"holm_alpha": ALPHA, "bh_alpha": ALPHA,
                                 "n_survive_holm": n_survive_holm, "n_survive_bh": n_survive_bh,
                                 "n_survive_both": n_survive_both, "n_edge_proven": n_edge},
            "dsr_mde": {"n_splits": int(n_splits), "mde_bps_mean": mde_bps,
                        "observed_mean_bps_per_split": obs_mean_bps},
            "stability": stability_ref,
            "attribution": {
                "reference_config": ref,
                "hedge_z_net": hedge_net, "relative_value_net": relval_net,
                "halflife_net": halflife_net, "placebo_noise_net": placebo_net,
                "shares": attrib_share, "dominant": dominant,
                "dominant_share": dominant_share, "attribution_ok": attribution_ok,
            },
        },
        "methodology": {
            "signals": "hedge-ratio beta=cov_L(p_i,p_m)/var_L(p_m) on log-price LEVELS; "
                       "resid=(p_i-mean_i)-beta*(p_m-mean_m); z=resid/std_L(resid); "
                       "spread_z=-z; spread_zxs=-(z-mean_j z); z_hedge1=-z of unhedged "
                       "(beta=1) spread; z_hl=-z/(1+half_life) with half_life=-ln2/ln(phi) "
                       "(AR(1) of resid, clipped [0,500]); z_corr=-z*clip(corr_L(p_i,p_m),0,1); "
                       "score=-mispricing (long cheap/short rich); causal shift(1), "
                       "cross-sectional rank, dollar-neutral gross 1.0. p_m=equal-weight "
                       "cross-sectional mean log-price.",
            "pnl": "single-leg perp: pnl = sum_i pos_i * perp_ret_i (pos>0 long).",
            "costs": "charged on turnover; symmetric = fee+slip; perp_heavy = 1.5*fee+slip.",
            "missing_data": "non-finite -> NaN; never impute; a lookback without enough valid "
                            "observations yields NaN -> not traded (fail-closed).",
            "multiple_testing": "one-sided paired t-test of per-split OOS net vs flat (0); "
                                "Holm step-down AND Benjamini-Hochberg over all 1440 configs at alpha=0.05.",
            "mde": "two-sided alpha=0.05, power=0.80: (t_{0.975}+t_{0.80})*s/sqrt(n_splits).",
            "attribution": "reference config vs hedge_z/relative_value/halflife vs placebo "
                           "(per-asset randomly permuted perp returns, same reference positions); "
                           "shares = |net| / sum(|buckets|).",
            "stability": "sign consistency >= 0.70 of splits AND first/second-half Sharpe corr >= 0.5.",
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

    # slim artifact: drop per-split series (bounded < 100 MB)
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
        "basis": "c319_cointegration_xsec_stat_arb_costed_oos_5m",
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
            "No edge claim unless the costed OOS test survives Holm+BH over all 1440 configs",
            "Real USDT-M linear 5m price-level cointegration / pairs mean-reversion factors; funding excluded (control leg)",
            "Single-leg PnL with costs on turnover; executed_fills: false",
        ],
    }
    op_ver = reports / f"campaign319_verdict_{ts}.json"
    op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")
    ver_sha = sha256_file(op_ver)

    bind_sha = None; bind_path = None
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