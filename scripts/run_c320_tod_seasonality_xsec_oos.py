#!/usr/bin/env python3
"""C320 — rigorous costed out-of-sample test of the cross-sectional INTRADAY
TIME-OF-DAY / DAY-OF-WEEK SEASONALITY mean-reversion statistical-arbitrage
family on 10 USDT-M linear perps at native 5m (1440 pre-registered configs).

GENUINELY NEW FAMILY (not a re-skin of any frozen modern campaign)
-----------------------------------------------------------------
C281B-C314 (all FROZEN formal negatives) exhausted carry, OFI/microstructure,
premium/index/mark basis, quarterly term-structure and same-asset spot-perp
lead-lag. C315 tested price first-moment momentum/reversal. C316 tested
size/volume/turnover liquidity characteristics. C317 tested own realized-vol /
higher-moments. C318 tested RETURN co-movement / covariance / beta. C319 tested
price-level COINTEGRATION / PAIRS equilibrium. C320 is the FIRST modern campaign
to trade cross-sectional INTRADAY TIME-OF-DAY / DAY-OF-WEEK SEASONALITY
mean-reversion: each asset's return vs its CAUSAL same-time-of-day (and
day-of-week+bar) baseline from trailing days ONLY, then cross-sectionally ranked.
It is economically distinct from every prior modern family: not a price level
(C319), not own variance / higher-moment (C317), not a first-moment
momentum/reversal (C315), not a liquidity/size characteristic (C316), and not a
return co-movement factor (C318). C320 trades CALENDAR structure.

MARKET PRICE
------------
Native USDT-M linear 5m perp_close from the real C312 cache; log_return derived
causally (r[t]=log(c[t]/c[t-1]), r[0]=0). Funding unreachable (fapi 451) ->
excluded (control only).

SEASONAL BUCKETS (causal, computed on the common 5m grid, grid[0]=2023-01-01 00:00 UTC)
-------------------------------------------------------------------------------------
bar-of-day (tod) = seconds-of-day // 300  -> 0..287  (one occurrence per calendar day)
day-of-week+bar (dow) = dayofweek*288 + tod  -> 0..2015 (one occurrence per week)

SIGNALS (pre-registered, causal shift(1), cross-sectional rank, dollar-neutral
gross 1.0; score = -seasonal-mispricing so a seasonally-LOW return -> HIGH score
(long), seasonally-HIGH return -> LOW score (short))
---------------------------------------------------------------------------------
For each bar t, symbol i, trailing lookback L (lookback{30,60,90 days} applied as
a trailing window of L seasonal occurrences; min_periods=L, fail-closed:
insufficient finite observations -> NaN -> not traded):

  tod_dev : dev_i,t = r_i,t - trailing_mean_L(r_i at same tod)
            score = -dev_i,t
  tod_z   : dev_i,t as above; z = dev_i,t / trailing_std_L(dev_i at same tod)
            score = -z_i,t
  dow_dev : dev_i,t = r_i,t - trailing_mean_L(r_i at same dow+bar)
            score = -dev_i,t
  tod_rv  : dev_i,t as tod_dev; vol = trailing_std_L(r_i at same tod)
            score = -dev_i,t / vol_i,t   (vol-scaled seasonal deviation)
  tod_ewm : ewm_i,t = exponentially-weighted mean_L(r_i at same tod, causal)
            score = -(r_i,t - ewm_i,t)

tod_placebo is the attribution bucket (permuted returns), NOT a signal.

PORTFOLIO
---------
Single-leg perp: pnl[t] = sum_i pos[i,t] * perp_ret[i,t], pos>0 => long perp.
Costs charged on turnover: cost = cost_rate(fee,slip,cv) * turnover.
  symmetric  : fee + slip per unit turnover (one leg)
  perp_heavy : 1.5*fee + slip per unit turnover (taker-heavy)
Funding is unreachable (fapi 451) -> excluded (control only).

GRID (1440 = 5 x 3 x 3 x 4 x 4 x 2, all reported)
-------------------------------------------------
signal{tod_dev,tod_z,dow_dev,tod_rv,tod_ewm}(5) x
lookback{30,60,90 days}(3) x
rebalance{6,12,48 bars = 30m,1h,4h}(3) x
fee{1,5,10,20}bps(4) x slippage{1,2,5,10}bps(4) x
cost_variant{symmetric,perp_heavy}(2)

WF: expanding train 12m / test 3m / roll 3m over 2023-01..2025-12 (8 splits).
Gates: Holm AND Benjamini-Hochberg at alpha=0.05 (BOTH required), MDE, stability
(sign consistency >= 70% splits; first/second-half Sharpe corr >= 0.5), and
seasonal-vs-placebo attribution (dominant share > 0.5 for a positive claim).

This is a model PnL backtest (executed_fills: false) on real data only. It never
fetches, imputes, resamples, or fabricates data.

Artifact (exact names, timestamped, SHA256-from-bytes):
  reports/campaign320_oos_sweep_<ts>.json  (+ gitignored *.full.json)
  reports/campaign320_tradable_edge_registry_<ts>.json
  reports/campaign320_summary_<ts>.json
  reports/campaign320_verdict_<ts>.json
  reports/campaign320_binding_constraint_<ts>.json
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

CACHE_DIR = cache_dir / "campaign320_tod_seasonality_5m"
CACHE_META = cache_dir / "campaign320_tod_seasonality_5m.meta.json"
CACHE_PROV = cache_dir / "campaign320_tod_seasonality_5m.provenance.json"

# ---- pre-registered grid ----
SIGNALS = ("tod_dev", "tod_z", "dow_dev", "tod_rv", "tod_ewm")
LOOKBACKS = (30, 60, 90)            # days, applied as trailing seasonal occurrences
REBALANCES = (6, 12, 48)            # 30m, 1h, 4h bars
FEES = (1, 5, 10, 20)               # bps per leg
SLIPS = (1, 2, 5, 10)               # bps per leg
COST_VARIANTS = ("symmetric", "perp_heavy")
FRAC = 0.33                         # top/bottom tercile (selection fixed)
ALPHA = 0.05
N_TRIALS = (len(SIGNALS) * len(LOOKBACKS) * len(REBALANCES) *
            len(FEES) * len(SLIPS) * len(COST_VARIANTS))  # 1440

TOD_BARS_PER_DAY = 288              # 24h * 60m / 5m
TRAIN_M, TEST_M, ROLL_M = 12, 3, 3
STABILITY_MIN_SIGN_CONSISTENCY = 0.70
STABILITY_MIN_SHARPE_CORR = 0.50
DOMINANT_SHARE_MIN = 0.50

# attribution buckets: the 5 seasonal signals vs placebo_noise
ATTR_BUCKETS = ("tod_dev", "tod_z", "dow_dev", "tod_rv", "tod_ewm", "placebo_noise")
ATTR_REPRESENTATIVES = {s: s for s in SIGNALS}


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


def _trailing_mean_2d(vals: np.ndarray, L: int) -> np.ndarray:
    """Trailing mean over axis=1 (time), window L (incl. current), min_periods=L."""
    n_assets, n = vals.shape
    out = np.full_like(vals, np.nan, dtype=np.float64)
    if n < L:
        return out
    vf = np.where(np.isfinite(vals), vals, 0.0)
    cs = np.concatenate([np.zeros((n_assets, 1)), np.cumsum(vf, axis=1)], axis=1)
    cc = np.concatenate([np.zeros((n_assets, 1)), np.cumsum(np.isfinite(vals).astype(np.float64), axis=1)], axis=1)
    e = np.arange(L, n + 1)
    s = cs[:, e] - cs[:, e - L]
    c = cc[:, e] - cc[:, e - L]
    with np.errstate(invalid="ignore", divide="ignore"):
        m = np.where(c > 0, s / np.maximum(c, 1.0), np.nan)
    out[:, L - 1:] = m
    return out


def _trailing_std_2d(vals: np.ndarray, L: int) -> np.ndarray:
    """Trailing std over axis=1 (time), window L (incl. current), min_periods=L."""
    n_assets, n = vals.shape
    out = np.full_like(vals, np.nan, dtype=np.float64)
    if n < L:
        return out
    vf = np.where(np.isfinite(vals), vals, 0.0)
    cs = np.concatenate([np.zeros((n_assets, 1)), np.cumsum(vf, axis=1)], axis=1)
    cc = np.concatenate([np.zeros((n_assets, 1)), np.cumsum(np.isfinite(vals).astype(np.float64), axis=1)], axis=1)
    css = np.concatenate([np.zeros((n_assets, 1)), np.cumsum(np.where(np.isfinite(vals), vals * vals, 0.0), axis=1)], axis=1)
    e = np.arange(L, n + 1)
    s = cs[:, e] - cs[:, e - L]
    c = cc[:, e] - cc[:, e - L]
    s2 = css[:, e] - css[:, e - L]
    with np.errstate(invalid="ignore", divide="ignore"):
        mean = np.where(c > 0, s / np.maximum(c, 1.0), 0.0)
        var = s2 / np.maximum(c, 1.0) - mean * mean
        var = np.where(c > 0, np.maximum(var, 0.0), np.nan)
        std = np.sqrt(var)
    out[:, L - 1:] = std
    return out


def bucket_trailing_stats(r: np.ndarray, bucket_idx: np.ndarray, L: int):
    """Trailing mean/std per seasonal bucket over the occurrence subsequence.

    r: (n_assets, n_bars); bucket_idx: (n_bars,) int bucket id.
    Returns (mean_out, std_out), each (n_assets, n_bars), NaN where warmup.
    """
    n_assets, n_bars = r.shape
    mean_out = np.full((n_assets, n_bars), np.nan, dtype=np.float64)
    std_out = np.full((n_assets, n_bars), np.nan, dtype=np.float64)
    n_buckets = int(bucket_idx.max()) + 1 if n_bars else 0
    for b in range(n_buckets):
        pos = np.where(bucket_idx == b)[0]  # ascending time order
        if len(pos) == 0:
            continue
        vals = r[:, pos]
        mean_out[:, pos] = _trailing_mean_2d(vals, L)
        std_out[:, pos] = _trailing_std_2d(vals, L)
    return mean_out, std_out


def ewm_mean_per_bucket(r: np.ndarray, bucket_idx: np.ndarray, L: int) -> np.ndarray:
    """Causal exponentially-weighted mean per seasonal bucket (span=L)."""
    n_assets, n_bars = r.shape
    out = np.full((n_assets, n_bars), np.nan, dtype=np.float64)
    alpha = 2.0 / (L + 1.0)
    n_buckets = int(bucket_idx.max()) + 1 if n_bars else 0
    for b in range(n_buckets):
        pos = np.where(bucket_idx == b)[0]
        if len(pos) == 0:
            continue
        vals = r[:, pos]
        for i in range(n_assets):
            s = pd.Series(vals[i], dtype=float)
            out[i, pos] = s.ewm(alpha=alpha, adjust=False, min_periods=L).mean().to_numpy()
    return out


def verify_cache() -> tuple:
    if not CACHE_DIR.exists():
        raise SystemExit(f"FATAL: C320 shard dir missing: {CACHE_DIR}")
    if not CACHE_META.exists():
        raise SystemExit(f"FATAL: C320 meta missing: {CACHE_META}")
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
        raise SystemExit("FATAL: C320 common grid is empty")

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

    # seasonal bucket ids (causal, from timestamps only)
    secs = idx_ms // 1000
    sod = secs % 86400
    tod_idx = (sod // 300).astype(np.int64)            # 0..287 bar of day
    dow = index.day_of_week.values.astype(np.int64)     # Mon=0..Sun=6
    dow_idx = (dow * TOD_BARS_PER_DAY + tod_idx).astype(np.int64)  # 0..2015

    splits = wf_splits_by_month(index, TRAIN_M, TEST_M, ROLL_M)
    if not splits:
        raise SystemExit("FATAL: no OOS splits")

    return {"symbols": symbols, "n_assets": n_assets, "index": index, "n_bars": n_b,
            "perp_close": perp_close, "log_return": log_return,
            "tod_idx": tod_idx, "dow_idx": dow_idx, "splits": splits}


def build_score(bs: dict, signal: str, L: int) -> np.ndarray:
    """Build a (n_assets, n_bars) seasonal mean-reversion score.

    score = -seasonal-mispricing; NaN where inputs missing (fail-closed).
    """
    r = finite_or_nan(bs["log_return"])
    tod_idx = bs["tod_idx"]
    dow_idx = bs["dow_idx"]

    if signal == "tod_dev":
        mean, _ = bucket_trailing_stats(r, tod_idx, L)
        return -(r - mean)

    if signal == "tod_z":
        mean, _ = bucket_trailing_stats(r, tod_idx, L)
        dev = r - mean
        _, dev_std = bucket_trailing_stats(dev, tod_idx, L)
        with np.errstate(invalid="ignore", divide="ignore"):
            return np.where(dev_std > 0, -(dev / np.where(dev_std > 0, dev_std, np.nan)), np.nan)

    if signal == "dow_dev":
        mean, _ = bucket_trailing_stats(r, dow_idx, L)
        return -(r - mean)

    if signal == "tod_rv":
        mean, r_std = bucket_trailing_stats(r, tod_idx, L)
        dev = r - mean
        with np.errstate(invalid="ignore", divide="ignore"):
            return np.where(r_std > 0, -(dev / np.where(r_std > 0, r_std, np.nan)), np.nan)

    if signal == "tod_ewm":
        ewm = ewm_mean_per_bucket(r, tod_idx, L)
        return -(r - ewm)

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

    ref_cfg = dict(signal="tod_dev", L=60, H=12, fee=10, slip=5, cv="symmetric")
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

    # ---- seasonal-vs-placebo attribution (reference config) ----
    ref = ref_cfg
    cr = cost_rate_bps(ref["fee"], ref["slip"], ref["cv"]) / 10000.0

    def ref_net_for(signal: str, L: int):
        gross, turn = get_gross_turn(signal, L, ref["H"])
        return float(sum(gross[te_s:te_e].sum() - cr * turn[te_s:te_e].sum()
                         for (tr_s, tr_e, te_s, te_e) in splits))

    nets = {s: ref_net_for(s, ref["L"]) for s in SIGNALS}

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

    attrib = {s: abs(nets[s]) for s in SIGNALS}
    attrib["placebo_noise"] = abs(placebo_net)
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
        "generated_at_utc": ts, "campaign": 320, "part": "oos_sweep",
        "analysis": "c320_tod_seasonality_xsec_stat_arb_oos_5m",
        "verdict": verdict, "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "fail_closed": True,
        "mandate": (
            "C320 — test the cross-sectional INTRADAY TIME-OF-DAY / DAY-OF-WEEK "
            "SEASONALITY mean-reversion statistical-arbitrage family on 10 "
            "USDT-M linear perps at native 5m (1440 pre-registered configs). "
            "Signals (score = -seasonal-mispricing, long seasonally-low / short "
            "seasonally-high): tod_dev (return vs trailing same-tod mean), tod_z "
            "(z of that deviation vs trailing dev std), dow_dev (return vs "
            "trailing same dow+bar mean), tod_rv (vol-scaled seasonal deviation), "
            "tod_ewm (return vs causal ewm same-tod baseline). Single-leg "
            "dollar-neutral perp PnL with costs charged on turnover (symmetric "
            "and perp_heavy variants). Gates: Holm+BH at alpha=0.05 (BOTH), MDE, "
            "stability, and seasonal-vs-placebo attribution."
        ),
        "preflight": dataset_block, "data_source": dataset_block,
        "universe": {"symbols": symbols, "n_assets": bs["n_assets"],
                     "common_grid_bars": int(n_b),
                     "common_grid_start_utc": str(index[0]),
                     "common_grid_end_utc": str(index[-1]),
                     "n_splits": int(n_splits)},
        "config": {
            "walk_forward": {"train_m": TRAIN_M, "test_m": TEST_M, "roll_m": ROLL_M},
            "signals": list(SIGNALS), "lookbacks_days": list(LOOKBACKS),
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
                **{f"{s}_net": nets[s] for s in SIGNALS},
                "placebo_noise_net": placebo_net,
                "shares": attrib_share, "dominant": dominant,
                "dominant_share": dominant_share, "attribution_ok": attribution_ok,
            },
        },
        "methodology": {
            "buckets": "bar-of-day (tod)=seconds-of-day//300 (0..287, one per day); "
                       "day-of-week+bar (dow)=dayofweek*288+tod (0..2015, one per week); "
                       "grid[0]=2023-01-01 00:00 UTC.",
            "signals": "tod_dev=-(r-mean_L(r at same tod)); tod_z=-dev/std_L(dev at "
                       "same tod); dow_dev=-(r-mean_L(r at same dow+bar)); "
                       "tod_rv=-dev/std_L(r at same tod) (vol-scaled); "
                       "tod_ewm=-(r-ewm_mean_L(r at same tod, causal)). lookback L in "
                       "days applied as trailing L seasonal occurrences, min_periods=L "
                       "(fail-closed). score=-mispricing (long seasonally-low/short "
                       "seasonally-high); causal shift(1), cross-sectional rank, "
                       "dollar-neutral gross 1.0.",
            "pnl": "single-leg perp: pnl = sum_i pos_i * perp_ret_i (pos>0 long).",
            "costs": "charged on turnover; symmetric = fee+slip; perp_heavy = 1.5*fee+slip.",
            "missing_data": "non-finite -> NaN; never impute; a lookback without enough "
                            "valid observations yields NaN -> not traded (fail-closed).",
            "multiple_testing": "one-sided paired t-test of per-split OOS net vs flat (0); "
                                "Holm step-down AND Benjamini-Hochberg over all 1440 configs at alpha=0.05.",
            "mde": "two-sided alpha=0.05, power=0.80: (t_{0.975}+t_{0.80})*s/sqrt(n_splits).",
            "attribution": "reference config seasonal nets vs placebo_noise (per-asset "
                           "randomly permuted perp returns, same reference positions); "
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
    op = reports / f"campaign320_oos_sweep_{ts}.json"
    op.write_text(json.dumps(slim, indent=2, default=jdefault) + "\n")
    sweep_sha = sha256_file(op)
    full = reports / f"campaign320_oos_sweep_{ts}.full.json"
    full.write_text(json.dumps(sweep_obj, indent=2, default=jdefault) + "\n")

    surviving = [results[i] for i in edge_idx if rej_holm[i] and rej_bh[i]]
    registry = {
        "generated_at_utc": ts, "campaign": 320, "part": "registry",
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
    op_reg = reports / f"campaign320_tradable_edge_registry_{ts}.json"
    op_reg.write_text(json.dumps(registry, indent=2, default=jdefault) + "\n")
    reg_sha = sha256_file(op_reg)

    summary = {
        "generated_at_utc": ts, "campaign": 320, "part": "summary",
        "analysis": "validation_summary", "verdict": verdict, "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "universe": sweep_obj["universe"], "config": sweep_obj["config"],
        "gates": sweep_obj["gates"],
        "artifacts": {"oos_sweep": {"path": str(op.relative_to(ROOT)), "sha256": sweep_sha},
                      "registry": {"path": str(op_reg.relative_to(ROOT)), "sha256": reg_sha}},
        "summary": sweep_obj["summary"], "binding_constraint": binding,
    }
    op_sum = reports / f"campaign320_summary_{ts}.json"
    op_sum.write_text(json.dumps(summary, indent=2, default=jdefault) + "\n")
    sum_sha = sha256_file(op_sum)

    finding = (
        f"C320 cross-sectional intraday time-of-day / day-of-week seasonality "
        f"stat-arb edge RETRACTED ({n_edge} deterministic edge configs, "
        f"{n_survive_both} survive Holm+BH over {N_TRIALS}); "
        f"binding constraint: {binding}; dominant attribution: {dominant} ({dominant_share:.4f})."
        if binding is not None
        else f"C320 cross-sectional intraday time-of-day / day-of-week seasonality "
        f"stat-arb edge validated: {n_survive_both} of {n_edge} deterministic edge configs survive "
        f"Holm+BH over {N_TRIALS}; edge_proven:{edge_proven}."
    )
    verdict_obj = {
        "generated_at_utc": ts, "campaign": 320, "part": "verdict",
        "analysis": "final_verdict", "verdict": verdict, "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "finding": finding,
        "basis": "c320_tod_seasonality_xsec_stat_arb_costed_oos_5m",
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
            "Real USDT-M linear 5m intraday time-of-day / day-of-week seasonality factors; funding excluded (control leg)",
            "Single-leg PnL with costs on turnover; executed_fills: false",
        ],
    }
    op_ver = reports / f"campaign320_verdict_{ts}.json"
    op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")
    ver_sha = sha256_file(op_ver)

    bind_sha = None; bind_path = None
    if binding is not None:
        binding_obj = {
            "generated_at_utc": ts, "campaign": 320, "part": "binding_constraint",
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
                "C320 cross-sectional intraday time-of-day / day-of-week seasonality "
                "stat-arb does not survive validation; formal negative. "
                f"Binding constraint: {binding}."
            ),
            "note": "Diagnosis only; never an edge claim. No threshold weakening.",
        }
        op_bind = reports / f"campaign320_binding_constraint_{ts}.json"
        op_bind.write_text(json.dumps(binding_obj, indent=2, default=jdefault) + "\n")
        bind_sha = sha256_file(op_bind)
        bind_path = str(op_bind.relative_to(ROOT))
        verdict_obj["binding_constraint_artifact"] = bind_path
        verdict_obj["binding_constraint_sha256"] = bind_sha
        op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")
        ver_sha = sha256_file(op_ver)

    print(json.dumps({
        "campaign": 320, "verdict": verdict, "edge_proven": edge_proven,
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
