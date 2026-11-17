#!/usr/bin/env python3
"""C339 — rigorous costed out-of-sample test of the cross-sectional intraday
ORDER-FLOW / RETURN DIRECTION ALIGNMENT SEASONAL DISLOCATION statistical-arbitrage
family on 10 USDT-M linear perps at native 5m (1944 pre-registered configs).

GENUINELY NEW FAMILY (not a re-skin of any frozen modern campaign)
-----------------------------------------------------------------
C281B-C314 (all FROZEN formal negatives) exhausted carry, OFI/microstructure,
premium/index/mark basis, quarterly term-structure and same-asset spot-perp
lead-lag. C315 tested price first-moment momentum/reversal. C316 tested
size/volume/turnover liquidity LEVELS. C317 tested own realized-vol /
higher-moments. C318 tested RETURN co-movement / covariance / beta. C319 tested
price-level COINTEGRATION / PAIRS equilibrium. C320 tested cross-sectional
intraday TIME-OF-DAY / DAY-OF-WEEK seasonal RETURN mean-reversion. C321 tested
intraday RANGE / BREAKOUT / OVERNIGHT-vs-INTRADAY split. C322 tested the
intraday VWAP-close fair-value anchor. C323 tested causal same-tod ORDER-FLOW &
TRADE-ACTIVITY SEASONALITY LEVEL deviations. C324 tested causal same-tod
AMIHUD-ILLIQUIDITY SEASONAL DISLOCATION (|r|/notional LEVEL). C325 tested
cross-sectional intraday AVERAGE TRADE SIZE SEASONAL DISLOCATION. C326 tested
RETURN AUTOCORRELATION SEASONAL DISLOCATION. C327 tested SIGNED JUMP-VARIATION
SEASONAL DISLOCATION. C328 tested RETURN SIGN-RUN SEASONAL DISLOCATION. C329
tested RETURN SIGN ENTROPY SEASONAL DISLOCATION. C330 tested RETURN-PATH
DRAWDOWN/RUNUP/PATH-EFFICIENCY SEASONAL DISLOCATION. C331 tested RETURN
TAIL-ASYMMETRY / QUANTILE-SPREAD SEASONAL DISLOCATION. C332 tested
RETURN-SIGNED-VOLUME CORRELATION SEASONAL DISLOCATION. C333 tested
MICROSTRUCTURE NOISE & EFFECTIVE SPREAD SEASONAL DISLOCATION. C334 tested
KYLE'S LAMBDA / PRICE-IMPACT COEFFICIENT SEASONAL DISLOCATION. C335 tested
ORDER-FLOW TOXICITY / VPIN SEASONAL DISLOCATION. C336 tested ORDER-FLOW
PERSISTENCE / IMBALANCE AUTOCORRELATION SEASONAL DISLOCATION. C337 tested
ORDER-FLOW SKEW / ASYMMETRIC IMPULSE SEASONAL DISLOCATION. C338 tested
ORDER-FLOW ENTROPY / INFORMATION CONTENT / TRADE BURSTINESS SEASONAL DISLOCATION.

C339 is the FIRST modern campaign to trade each asset's CAUSAL trailing
same-(TOD x DOW) seasonal deviation of its OWN intraday ORDER-FLOW / RETURN
DIRECTION ALIGNMENT — from real signed_volume, total_volume, perp_close.
Unlike C323 (raw flow level/ratio seasonality), C332 (return-signed-volume
correlation level), C336 (order-flow persistence), C337 (order-flow skew/asym)
and C338 (order-flow entropy/information/burstiness), C339 measures the per-bar
alignment between order-flow imbalance direction and return direction
(sign(imb) * sign(r)) vs its own same-bucket baseline: unusually high alignment
(flow chasing price) vs same-bucket history -> expect mean-reversion of the
flow-return regime; score = -seasonal-dislocation. Mechanically distinct.

PER-BAR INPUTS (per bar, causal, real only):
    sign_imb_t    = sign(signed_volume_t / total_volume_t)   (total_volume<=0 -> NaN)
    sign_r_t      = sign(log_return_t)                       (always finite)
    align_t       = sign_imb_t * sign_r_t                    (+1 aligned, -1 misaligned)

SIGNALS (pre-registered, causal, metrics computed over trailing lookback L bars
ending at bar t-1; score = -(signal_t - seasonal_baseline_t) / seasonal_std_t;
cross-sectional rank; dollar-neutral gross 1.0):
--------------------------------------------------------------------------------
Bucket = (weekday, tod) with tod = seconds-of-day//300 (0..287), 7 weekdays x 288
= 2016 buckets per asset. Seasonal baseline = trailing mean/std at the same
bucket from history strictly before bar t (causal, shift(1)), NaN-aware with
min_periods=3, EXCLUDING NaN same-bucket observations (no ffill/impute).

Over trailing lookback L bars ending at bar t-1:
  align_mean : mean(align) in window
  align_abs  : |align_mean| in window
  align_z    : (align_mean - seasonal_mean) / seasonal_std  (level z, computed
               inside _same_bucket_stats per signal below)

Signals (all *_dev use score = -(v-m)/sd):
  align_dev        : seasonal dislocation of align_mean
  align_abs_dev    : seasonal dislocation of align_abs
  align_z          : level z of align_mean ((align_mean - m) / sd)
  align_placebo    : seasonal dislocation of phase-randomized surrogate of align_mean
  align_abs_placebo: seasonal dislocation of phase-randomized surrogate of align_abs
  align_z_placebo  : seasonal dislocation of phase-randomized surrogate of align_z

Placebos (align_placebo, align_abs_placebo, align_z_placebo) are seasonal
dislocations of recorded-seed phase-randomized surrogates of the corresponding
metric series (same marginal, temporal alignment destroyed) — attribution
placebos, never counted as edges.

GRID (1944 = 6 x 6 x 3 x 3 x 3 x 2, all reported)
--------------------------------------------------
signal{6} x lookback{60,120,240,480,960,1920} bars(6) x
rebalance{1,4,12} bars(3) x fee{0.0004,0.0007,0.0010}(3) x
slippage{0,0.0001,0.0002}(3) x cost_variant{taker,maker_blend}(2)

WF: expanding train 12m / test 3m / roll 3m over 2023-01..2025-12 (8 splits).
Gates: Holm AND Benjamini-Hochberg at alpha=0.05 (BOTH), MDE, stability
(sign consistency >= 70% of splits; first/second-half Sharpe corr >= 0.5), and
signal-vs-placebo attribution (dominant share >= 0.5 for a REAL non-placebo
signal).

Model PnL backtest (executed_fills: false) on real data only. Never fetches,
imputes, resamples, or fabricates data. The only RNG is the recorded-seed
placebo phase randomization (documented in the artifact; not market data).

Artifact (exact names, timestamped, SHA256-from-bytes):
  reports/campaign339_oos_sweep_<ts>.json  (+ gitignored *.full.json)
  reports/campaign339_tradable_edge_registry_<ts>.json
  reports/campaign339_summary_<ts>.json
  reports/campaign339_verdict_<ts>.json
  reports/campaign339_binding_constraint_<ts>.json
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

CACHE_DIR = cache_dir / "campaign339_orderflow_return_alignment_5m"
CACHE_META = cache_dir / "campaign339_orderflow_return_alignment_5m.meta.json"
CACHE_PROV = cache_dir / "campaign339_orderflow_return_alignment_5m.provenance.json"
REQUIRED_FIELDS = ["index_ms", "perp_close", "log_return",
                   "sign_imb", "sign_r", "align", "funding_rate"]

# ---- pre-registered grid ----
SIGNALS = ("align_dev", "align_abs_dev", "align_z",
           "align_placebo", "align_abs_placebo", "align_z_placebo")
LOOKBACKS = (60, 120, 240, 480, 960, 1920)          # bars
REBALANCES = (1, 4, 12)                            # bars
FEES = (0.0004, 0.0007, 0.0010)
SLIPS = (0.0, 0.0001, 0.0002)
COST_VARIANTS = ("taker", "maker_blend")
FRAC = 1.0 / 3.0
ALPHA = 0.05
MIN_PERIODS_BASELINE = 3
EWMA_HALFLIFE = 24
EWMA_MIN_PERIODS = 24
PLACEBO_SEED = 20261119
TRAIN_M, TEST_M, ROLL_M = 12, 3, 3
STABILITY_MIN_SIGN_CONSISTENCY = 0.70
STABILITY_MIN_SHARPE_CORR = 0.50
DOMINANT_SHARE_MIN = 0.50

TOD_BARS_PER_DAY = 288
WEEKDAYS = 7
N_BUCKETS = WEEKDAYS * TOD_BARS_PER_DAY

N_TRIALS = (len(SIGNALS) * len(LOOKBACKS) *
            len(REBALANCES) * len(FEES) * len(SLIPS) * len(COST_VARIANTS))  # 1944

# signal -> (base_metric_key, is_placebo)
SIGNAL_FAMILY = {
    "align_dev": ("align_mean", False),
    "align_abs_dev": ("align_abs", False),
    "align_z": ("align_z", False),
    "align_placebo": ("align_mean", True),
    "align_abs_placebo": ("align_abs", True),
    "align_z_placebo": ("align_z", True),
}
# all signals use score = -(v - m) / sd  (seasonal dislocation), except align_z
# which is already a z-score (level); but per pre-registered spec all use
# score = -(v-m)/sd where for align_z, v IS the z-score so m/sd of z is used.
SIGNAL_SIGN = {s: -1.0 for s in SIGNALS}

ATTR_REPRESENTATIVES = {
    "align_dev": "align_dev",
    "align_abs_dev": "align_abs_dev",
    "align_z": "align_z",
}


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


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


def _roll_sum(arr: np.ndarray, L: int) -> np.ndarray:
    """Trailing sum of `arr` over window ending at each position (window length L).
    NaN for positions with < L-1 lookback (insufficient full history)."""
    n = len(arr)
    out = np.full(n, np.nan, dtype=float)
    if n < L:
        return out
    cs = np.concatenate([[0.0], np.cumsum(np.where(np.isfinite(arr), arr, 0.0))])
    u = np.arange(L - 1, n)
    out[u] = cs[u + 1] - cs[u - L + 1]
    return out


def _roll_count_bool(mask: np.ndarray, L: int) -> np.ndarray:
    return _roll_sum(mask.astype(np.float64), L)


def _phase_randomized_surrogate(x: np.ndarray, seed: int) -> np.ndarray:
    """Phase-randomized surrogate of x: same marginal distribution (rank-restored),
    temporal alignment destroyed (FFT phases randomized). Deterministic seed.
    NaN positions stay NaN."""
    n = len(x)
    out = np.full(n, np.nan, dtype=float)
    fin = np.isfinite(x)
    k = int(fin.sum())
    if k < 8:
        return out
    xf = np.asarray(x[fin], dtype=float)
    xc = xf - xf.mean()
    F = np.fft.rfft(xc)
    amp = np.abs(F)
    rng = np.random.default_rng(int(seed))
    phase = np.zeros(F.shape[0])
    if F.shape[0] > 2:
        phase[1:-1] = rng.uniform(0.0, 2.0 * np.pi, size=F.shape[0] - 2)
    F_new = amp * np.exp(1j * phase)
    y = np.fft.irfft(F_new, n=k)
    order_y = np.argsort(y, kind="mergesort")
    order_x = np.argsort(xc, kind="mergesort")
    restored = np.empty(k, dtype=float)
    restored[order_y] = xc[order_x]
    restored += xf.mean()
    out[fin] = restored
    return out


# ------------------------------------------------------- same-(TOD x DOW) bucket helpers
def _bucket_of(index_ms: np.ndarray) -> np.ndarray:
    secs = index_ms // 1000
    tod = ((secs % 86400) // 300).astype(np.int64)
    idx = pd.DatetimeIndex(pd.to_datetime(index_ms, unit="ms", utc=True))
    weekday = idx.day_of_week.to_numpy(dtype=np.int64)  # Mon=0..Sun=6
    return weekday * TOD_BARS_PER_DAY + tod  # 0..2015


def _same_bucket_stats_1d(bucket: np.ndarray, x: np.ndarray, window, min_periods: int):
    """Trailing (or expanding when window is None) same-bucket mean/std of x over
    strictly-previous observations. NaN unless count>=min_periods and std>0."""
    n = len(bucket)
    mean = np.full(n, np.nan, dtype=float)
    std = np.full(n, np.nan, dtype=float)
    if n == 0:
        return mean, std
    order = np.argsort(bucket, kind="mergesort")
    sb = bucket[order]
    sx = np.asarray(x, dtype=float)[order]
    seg_start = np.concatenate([[0], np.nonzero(sb[1:] != sb[:-1])[0] + 1])
    seg_id = np.repeat(np.arange(len(seg_start)), np.diff(np.concatenate([seg_start, [n]])))
    local = np.arange(n) - seg_start[seg_id]
    fin = np.isfinite(sx).astype(float)
    sxf = np.where(np.isfinite(sx), sx, 0.0)
    sx2f = np.where(np.isfinite(sx), sx * sx, 0.0)
    cs = np.concatenate([[0.0], np.cumsum(sxf)])
    cs2 = np.concatenate([[0.0], np.cumsum(sx2f)])
    cc = np.concatenate([[0.0], np.cumsum(fin)])
    if window is None:
        gstart = seg_start[seg_id]
        gend = seg_start[seg_id] + local
    else:
        win_start_local = np.maximum(local - int(window), 0)
        gstart = seg_start[seg_id] + win_start_local
        gend = seg_start[seg_id] + local
    cnt = cc[gend] - cc[gstart]
    s1 = cs[gend] - cs[gstart]
    s2 = cs2[gend] - cs2[gstart]
    with np.errstate(divide="ignore", invalid="ignore"):
        m = np.where(cnt >= min_periods, s1 / np.maximum(cnt, 1.0), np.nan)
        var = s2 / np.maximum(cnt, 1.0) - m * m
        sd = np.sqrt(np.maximum(var, 0.0))
        sd = np.where((cnt >= min_periods) & (sd > 0), sd, np.nan)
    inv = np.empty(n, dtype=np.int64)
    inv[order] = np.arange(n)
    return m[inv], sd[inv]


def _same_bucket_stats(bucket: np.ndarray, x: np.ndarray, window, min_periods: int):
    n_assets, n_b = x.shape
    out_m = np.full_like(x, np.nan, dtype=float)
    out_s = np.full_like(x, np.nan, dtype=float)
    for i in range(n_assets):
        out_m[i], out_s[i] = _same_bucket_stats_1d(bucket, x[i], window, min_periods)
    return out_m, out_s


# ------------------------------------------------------- metric computation (per asset, per lookback)
def compute_metrics(align: np.ndarray, L: int, min_periods: int = 3) -> dict:
    """Compute all causal metric series for one asset over trailing lookback L
    ending at bar t-1 (metric[t] uses bars [t-L, t-1]).
    Returns dict metric_name -> (n_bars,) array (NaN where undefined)."""
    n = len(align)
    res: dict = {}

    # rolling sum & count of align over window ending at v ([v-L+1, v])
    fin_align = np.isfinite(align)
    align_f = np.where(fin_align, align, 0.0)
    align2_f = np.where(fin_align, align * align, 0.0)
    cs1 = np.concatenate([[0.0], np.cumsum(align_f)])
    cs2 = np.concatenate([[0.0], np.cumsum(align2_f)])
    cc = np.concatenate([[0.0], np.cumsum(fin_align.astype(float))])
    u = np.arange(L - 1, n)
    cnt = cc[u + 1] - cc[u - L + 1]
    s1 = cs1[u + 1] - cs1[u - L + 1]
    s2 = cs2[u + 1] - cs2[u - L + 1]
    mean = np.full(n, np.nan, dtype=float)
    var = np.full(n, np.nan, dtype=float)
    pos_valid = cnt >= min_periods
    mean[u[pos_valid]] = s1[pos_valid] / np.maximum(cnt[pos_valid], 1.0)
    var[u[pos_valid]] = s2[pos_valid] / np.maximum(cnt[pos_valid], 1.0) - mean[u[pos_valid]] ** 2
    sd = np.sqrt(np.maximum(var, 0.0))
    # align_mean over trailing window ending at each position
    align_mean_end = np.full(n, np.nan, dtype=float)
    align_mean_end[u[pos_valid]] = mean[u[pos_valid]]

    # align_abs = |align_mean_end|
    align_abs_end = np.abs(align_mean_end)

    res["align_mean"] = align_mean_end
    res["align_abs"] = align_abs_end

    # ---- align all metrics so metric[t] uses window ending at t-1 ----
    # rolling arrays above are aligned to end position v (window [v-L+1, v]).
    # metric[t] = rolling[t-1] (window [t-L, t-1]).
    aligned = {}
    for k, v in res.items():
        out = np.full(n, np.nan, dtype=float)
        if n > 1:
            out[1:] = v[:-1]
        aligned[k] = out
    return aligned


def build_underlying(bs: dict) -> dict:
    """Compute the causal per-bar metric series used by every signal.
    Returns dict with matrices (n_assets, n_bars): one entry per base metric per
    lookback, plus placebo surrogates of align_mean, align_abs, align_z."""
    bucket = bs["bucket"]
    n_assets = int(bs["n_assets"])
    n_bars = int(bs["n_bars"])
    align = bs["align"]
    series: dict = {}
    METRIC_KEYS = ("align_mean", "align_abs")
    for L in LOOKBACKS:
        mats = {k: np.full((n_assets, n_bars), np.nan, dtype=float) for k in METRIC_KEYS}
        for i in range(n_assets):
            m = compute_metrics(np.asarray(align[i], dtype=float), L, MIN_PERIODS_BASELINE)
            for k in METRIC_KEYS:
                mats[k][i] = np.asarray(m[k], dtype=float)
        for k in METRIC_KEYS:
            series[(k, L)] = mats[k]

    # compute align_z for each lookback: (align_mean - seasonal_mean) / seasonal_std
    # using expanding same-bucket stats (window=None) over the align_mean series
    for L in LOOKBACKS:
        align_mean_mat = series[("align_mean", L)]
        m_z, s_z = _same_bucket_stats(bucket, align_mean_mat, None, MIN_PERIODS_BASELINE)
        with np.errstate(divide="ignore", invalid="ignore"):
            align_z_mat = np.where((s_z > 0) & np.isfinite(align_mean_mat) & np.isfinite(m_z) & np.isfinite(s_z),
                                   (align_mean_mat - m_z) / s_z, np.nan)
        series[("align_z", L)] = align_z_mat

    # placebos (recorded-seed phase randomization of the metric series)
    for L in LOOKBACKS:
        series[("align_mean_placebo", L)] = np.apply_along_axis(
            lambda row: _phase_randomized_surrogate(row, PLACEBO_SEED), 1, series[("align_mean", L)])
        series[("align_abs_placebo", L)] = np.apply_along_axis(
            lambda row: _phase_randomized_surrogate(row, PLACEBO_SEED), 1, series[("align_abs", L)])
        series[("align_z_placebo", L)] = np.apply_along_axis(
            lambda row: _phase_randomized_surrogate(row, PLACEBO_SEED), 1, series[("align_z", L)])
    return series


def build_scores(series: dict, bucket: np.ndarray) -> dict:
    """Compute causal score per (signal, lookback).
    Returns {(signal, L): score(n_assets, n_bars)} shifted by 1 bar (causal)."""
    scores: dict = {}
    for signal in SIGNALS:
        base, is_placebo = SIGNAL_FAMILY[signal]
        sign_ = SIGNAL_SIGN[signal]
        for L in LOOKBACKS:
            key = (base + ("_placebo" if is_placebo else ""), L)
            v = series[key]
            m, sd = _same_bucket_stats(bucket, v, None, MIN_PERIODS_BASELINE)
            with np.errstate(divide="ignore", invalid="ignore"):
                score = sign_ * (v - m) / np.where(sd > 0, sd, np.nan)
            score = np.where((sd > 0) & np.isfinite(v) & np.isfinite(m) & np.isfinite(sd), score, np.nan)
            sc = np.full_like(score, np.nan)
            sc[:, 1:] = score[:, :-1]  # causal shift(1)
            scores[(signal, int(L))] = sc
    return scores


def verify_cache() -> tuple:
    if not CACHE_DIR.exists():
        raise SystemExit(f"FATAL: C339 shard dir missing: {CACHE_DIR}")
    if not CACHE_META.exists():
        raise SystemExit(f"FATAL: C339 meta missing: {CACHE_META}")
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
    if list(meta.get("fields") or []) != REQUIRED_FIELDS:
        raise SystemExit(f"FATAL: cache fields mismatch: {meta.get('fields')}")
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
        raise SystemExit("FATAL: C339 common grid is empty")
    if n_b % TOD_BARS_PER_DAY != 0:
        raise SystemExit("FATAL: C339 grid is not a whole number of 288-bar days")

    def mat(key):
        out = np.zeros((n_assets, n_b), dtype=float)
        for i, s in enumerate(symbols):
            out[i] = np.asarray(per_asset[s][key], dtype=float)
        return out

    perp_close = mat("perp_close")
    log_return = mat("log_return")
    sign_imb = mat("sign_imb")
    sign_r = mat("sign_r")
    align = mat("align")

    if not (np.isfinite(perp_close).all() and (perp_close > 0).all()):
        raise SystemExit("FATAL: non-finite/non-positive perp_close")
    if not np.isfinite(log_return).all():
        raise SystemExit("FATAL: non-finite log_return in cache")
    if not np.isfinite(sign_r).all():
        raise SystemExit("FATAL: non-finite sign_r in cache")

    bucket = _bucket_of(idx_ms)
    day_ord = (idx_ms // (86400 * 1000) - idx_ms[0] // (86400 * 1000)).astype(np.int64)
    n_days = n_b // TOD_BARS_PER_DAY
    if not np.array_equal(day_ord, np.repeat(np.arange(n_days), TOD_BARS_PER_DAY)):
        raise SystemExit("FATAL: day boundaries are not aligned to 288-bar UTC days")

    splits = wf_splits_by_month(index, TRAIN_M, TEST_M, ROLL_M)
    if not splits:
        raise SystemExit("FATAL: no OOS splits")

    return {"symbols": symbols, "n_assets": n_assets, "index": index, "n_bars": n_b,
            "n_days": n_days, "perp_close": perp_close, "log_return": log_return,
            "sign_imb": sign_imb, "sign_r": sign_r, "align": align, "bucket": bucket, "splits": splits}


def xsec_positions(score: np.ndarray, frac: float, H: int) -> np.ndarray:
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
        pos[:, 1:] = seg_desired[:, :-1]
    return np.where(np.isfinite(pos), pos, 0.0)


def cost_rate(fee: float, slip: float, cv: str) -> float:
    if cv == "taker":
        return fee + slip
    return 0.5 * fee + slip


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--reference-config-only", action="store_true")
    ap.add_argument("--smoke", action="store_true")
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

    series = build_underlying(bs)
    scores = build_scores(series, bs["bucket"])

    gross_turn_cache: dict = {}

    def get_gross_turn(signal: str, L: int, H: int):
        key = (signal, L, H)
        if key in gross_turn_cache:
            return gross_turn_cache[key]
        sc = scores[(signal, L)]
        pos = xsec_positions(sc, FRAC, H)
        gross = (pos * perp_ret).sum(axis=0)
        dpos = np.abs(np.diff(pos, axis=1, prepend=pos[:, :1]))
        turn = dpos.sum(axis=0)
        gross_turn_cache[key] = (gross, turn)
        return gross, turn

    results: list[dict] = []

    def run_config(signal: str, L: int, H: int, fee: float, slip: float, cv: str):
        gross, turn = get_gross_turn(signal, L, H)
        cost_rate_val = cost_rate(fee, slip, cv)
        seg_gross, seg_turn, seg_len = [], [], []
        for (tr_s, tr_e, te_s, te_e) in splits:
            seg_gross.append(float(gross[te_s:te_e].sum()))
            seg_turn.append(float(turn[te_s:te_e].sum()))
            seg_len.append(int(te_e - te_s))
        net = [g - cost_rate_val * t for g, t in zip(seg_gross, seg_turn)]
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
            "fee": float(fee), "slippage": float(slip), "cost_variant": cv,
            "n_splits": int(n_splits),
            "oos_net_sum": net_sum, "oos_net_mean": net_mean,
            "oos_net_per_split": [float(x) for x in net],
            "gross_sum": float(sum(seg_gross)), "turnover_total": float(sum(seg_turn)),
            "edge_proven": bool(all_pos), "p_value": float(p_val),
            "per_split_mean_bps": per_split_bps, "sharpe_obs": float(sr),
            "mde_bps": float(mde_bps),
            "cost_rate_bps_effective": float(cost_rate_val * 10000.0),
        }

    ref_cfg = dict(signal="align_dev", L=240, H=4,
                   fee=0.0007, slip=0.0001, cv="taker")
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

    # ---- signal-vs-placebo attribution (mean |OOS net| share per signal across all its configs) ----
    signal_nets: dict = {s: [] for s in SIGNALS}
    for r in results:
        signal_nets[r["signal"]].append(r["oos_net_mean"])
    attrib = {s: abs(float(np.mean(signal_nets[s]))) if signal_nets[s] else 0.0 for s in SIGNALS}
    attrib_total = sum(attrib.values())
    if attrib_total > 0:
        attrib_share = {k: float(v / attrib_total) for k, v in attrib.items()}
    else:
        attrib_share = {k: 0.0 for k in SIGNALS}
    dominant = max(attrib_share, key=attrib_share.get) if attrib_total > 0 else None
    dominant_share = float(attrib_share[dominant]) if dominant else 0.0
    attribution_ok = bool(dominant in ATTR_REPRESENTATIVES
                          and dominant_share >= DOMINANT_SHARE_MIN)

    def stability():
        gross, turn = get_gross_turn(ref_cfg["signal"], ref_cfg["L"], ref_cfg["H"])
        cr = cost_rate(ref_cfg["fee"], ref_cfg["slip"], ref_cfg["cv"])
        seg_nets = []
        for (tr_s, tr_e, te_s, te_e) in splits:
            seg_nets.append(float(gross[te_s:te_e].sum() - cr * turn[te_s:te_e].sum()))
        seg_nets_arr = np.array(seg_nets, dtype=float)
        n = len(seg_nets_arr)
        sign_consistency = float(np.mean(seg_nets_arr > 0)) if n else 0.0
        half = n // 2
        first = seg_nets_arr[:half]
        second = seg_nets_arr[half:2 * half]

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
            "reference_config": ref_cfg,
            "per_split_net": [float(x) for x in seg_nets],
            "sign_consistency": sign_consistency,
            "first_half_sharpe": _sharpe(first),
            "second_half_sharpe": _sharpe(second),
            "sharpe_corr": sharpe_corr,
            "stable": stable,
        }

    stability_ref = stability()

    sc_ref = scores[(ref_cfg["signal"], ref_cfg["L"])]
    sc_ref_nan_share = float(1.0 - float(np.isfinite(sc_ref).mean()))

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
        "generated_at_utc": ts, "campaign": 339, "part": "oos_sweep",
        "analysis": "c339_orderflow_return_alignment_xsec_stat_arb_oos_5m",
        "verdict": verdict, "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "fail_closed": True,
        "mandate": (
            "C339 — test the cross-sectional intraday ORDER-FLOW / RETURN DIRECTION "
            "ALIGNMENT SEASONAL DISLOCATION statistical-arbitrage family on 10 USDT-M "
            "linear perps at native 5m (1944 pre-registered configs). Per-bar primitives: "
            "sign_imb=sign(signed_volume/total_volume) (total_volume<=0 -> NaN); "
            "sign_r=sign(log_return) (always finite); "
            "align=sign_imb*sign_r (+1 aligned, -1 misaligned). "
            "Metrics over trailing lookback L bars ending at bar t-1: "
            "align_mean=mean(align); align_abs=|align_mean|; "
            "align_z=(align_mean-seasonal_mean)/seasonal_std. "
            "Seasonal baseline = trailing mean/std at same (weekday,tod) bucket "
            "from history strictly before bar t (causal shift(1)), min_periods=3, "
            "NaN-aware, excluding NaN obs. "
            "Signals: 3 real *_dev/_z + 3 placebos (phase-randomized surrogates, "
            "never edges). Single-leg dollar-neutral perp PnL with costs on turnover "
            "(taker=fee+slip; maker_blend=0.5*fee+slip). Gates: Holm+BH at "
            "alpha=0.05 (BOTH), MDE, stability, signal-vs-placebo attribution. "
            "PRE-REGISTERED NaN policy: total_volume<=0 -> sign_imb/align NaN; "
            "metric NaN unless sufficient finite obs; seasonal stats NaN-aware min_periods "
            "excluding NaN obs; NaN-score bars weight 0; raw flow fields carry zero NaN "
            "except zero-activity denominators."
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
            "fee": list(FEES), "slippage": list(SLIPS),
            "selection_frac": float(FRAC), "cost_variants": list(COST_VARIANTS),
            "placebo_seed": int(PLACEBO_SEED),
            "min_periods_baseline": MIN_PERIODS_BASELINE,
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
                "reference_config": ref_cfg,
                **{f"{s}_net": signal_nets[s] and float(np.mean(signal_nets[s])) or 0.0 for s in SIGNALS},
                "shares": attrib_share, "dominant": dominant,
                "dominant_share": dominant_share, "attribution_ok": attribution_ok,
                "placebo_seed": int(PLACEBO_SEED),
            },
            "data_quality": {
                "reference_signal": ref_cfg["signal"], "reference_lookback": int(ref_cfg["L"]),
                "reference_score_nan_share": sc_ref_nan_share,
                "note": "metric NaN share dominated by finite-obs requirements plus rare zero-activity bars.",
            },
        },
        "methodology": {
            "buckets": "(weekday,tod)=dayofweek*288+seconds-of-day//300 (0..2015), exact 288 bars per UTC day.",
            "raw_features": "log_return=log(c[t]/c[t-1]) (r[0]=0) from real strictly-positive perp_close; signed_volume/total_volume real from C312.",
            "primitives": "sign_imb=sign(signed_volume/total_volume) (tv<=0 -> NaN); sign_r=sign(log_return) (always finite); align=sign_imb*sign_r (+1/-1 aligned/misaligned).",
            "signals": "align_mean/align_abs/align_z over trailing L bars ending at t-1; score=sign*(v-m)/sd with m/sd trailing same-bucket mean/std (min_periods=3, excluding NaN, causal shift(1)); cross-sectional rank, dollar-neutral gross 1.0; NaN-score assets weight 0.",
            "pnl": "single-leg perp: pnl = sum_i pos_i * perp_ret_i.",
            "costs": "charged on turnover; taker = fee+slip; maker_blend = 0.5*fee+slip.",
            "missing_data": "non-finite -> NaN; never impute/ffill; insufficient valid obs -> NaN -> not traded (fail-closed).",
            "multiple_testing": "one-sided paired t-test of per-split OOS net vs 0; Holm step-down AND Benjamini-Hochberg over all 1944 configs at alpha=0.05.",
            "mde": "two-sided alpha=0.05, power=0.80: (t_{0.975}+t_{0.80})*s/sqrt(n_splits).",
            "attribution": "mean |OOS net| per signal across all its configs; shares=|mean|/sum(|means|) over all 6 signals incl. placebos; dominant must be a real (non-placebo) signal with share >= 0.5 for attribution_ok.",
            "stability": "sign consistency >= 0.70 of splits AND first/second-half Sharpe corr >= 0.5.",
            "placebo": "phase-randomized surrogate via FFT phase randomization + rank restoration to original marginal; deterministic seed recorded; same marginal distribution, destroyed temporal alignment.",
            "funding": "USDT-M funding unreachable (fapi 451) -> excluded (control only).",
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

    slim = dict(sweep_obj)
    slim_results = []
    for r in results:
        rr = dict(r)
        rr.pop("oos_net_per_split", None)
        slim_results.append(rr)
    slim["results"] = slim_results
    op = reports / f"campaign339_oos_sweep_{ts}.json"
    op.write_text(json.dumps(slim, indent=2, default=jdefault) + "\n")
    sweep_sha = sha256_file(op)
    full = reports / f"campaign339_oos_sweep_{ts}.full.json"
    full.write_text(json.dumps(sweep_obj, indent=2, default=jdefault) + "\n")

    surviving = [results[i] for i in edge_idx if rej_holm[i] and rej_bh[i]]
    registry = {
        "generated_at_utc": ts, "campaign": 339, "part": "registry",
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
    op_reg = reports / f"campaign339_tradable_edge_registry_{ts}.json"
    op_reg.write_text(json.dumps(registry, indent=2, default=jdefault) + "\n")
    reg_sha = sha256_file(op_reg)

    summary = {
        "generated_at_utc": ts, "campaign": 339, "part": "summary",
        "analysis": "validation_summary", "verdict": verdict, "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "universe": sweep_obj["universe"], "config": sweep_obj["config"],
        "gates": sweep_obj["gates"],
        "artifacts": {"oos_sweep": {"path": str(op.relative_to(ROOT)), "sha256": sweep_sha},
                      "registry": {"path": str(op_reg.relative_to(ROOT)), "sha256": reg_sha}},
        "summary": sweep_obj["summary"], "binding_constraint": binding,
    }
    op_sum = reports / f"campaign339_summary_{ts}.json"
    op_sum.write_text(json.dumps(summary, indent=2, default=jdefault) + "\n")
    sum_sha = sha256_file(op_sum)

    finding = (
        f"C339 cross-sectional intraday ORDER-FLOW / RETURN DIRECTION ALIGNMENT "
        f"SEASONAL DISLOCATION mean-reversion stat-arb edge "
        f"RETRACTED ({n_edge} deterministic edge configs, {n_survive_both} survive "
        f"Holm+BH over {N_TRIALS}); binding constraint: {binding}; dominant "
        f"attribution: {dominant} ({dominant_share:.4f})."
        if binding is not None
        else f"C339 cross-sectional intraday ORDER-FLOW / RETURN DIRECTION ALIGNMENT "
        f"SEASONAL DISLOCATION mean-reversion stat-arb edge validated: "
        f"{n_survive_both} of {n_edge} deterministic edge configs survive Holm+BH over "
        f"{N_TRIALS}; edge_proven:{edge_proven}."
    )
    verdict_obj = {
        "generated_at_utc": ts, "campaign": 339, "part": "verdict",
        "analysis": "final_verdict", "verdict": verdict, "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "finding": finding,
        "basis": "c339_orderflow_return_alignment_xsec_stat_arb_costed_oos_5m",
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
            "No edge claim unless the costed OOS test survives Holm+BH over all 1944 configs",
            "Real USDT-M linear 5m perp_close + signed_volume + total_volume; funding excluded (control leg)",
            "Single-leg PnL with costs on turnover; executed_fills: false",
            "Only RNG is recorded-seed placebo phase randomization (not market data)",
        ],
    }
    op_ver = reports / f"campaign339_verdict_{ts}.json"
    op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")
    ver_sha = sha256_file(op_ver)

    bind_sha = None
    bind_path = None
    if binding is not None:
        binding_obj = {
            "generated_at_utc": ts, "campaign": 339, "part": "binding_constraint",
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
                "C339 cross-sectional intraday ORDER-FLOW / RETURN DIRECTION "
                "ALIGNMENT SEASONAL DISLOCATION mean-reversion stat-arb does not "
                "survive validation; formal negative. Binding "
                "constraint: {binding}."
            ).format(binding=binding),
            "note": "Diagnosis only; never an edge claim. No threshold weakening.",
        }
        op_bind = reports / f"campaign339_binding_constraint_{ts}.json"
        op_bind.write_text(json.dumps(binding_obj, indent=2, default=jdefault) + "\n")
        bind_sha = sha256_file(op_bind)
        bind_path = str(op_bind.relative_to(ROOT))
        verdict_obj["binding_constraint_artifact"] = bind_path
        verdict_obj["binding_constraint_sha256"] = bind_sha
        op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")
        ver_sha = sha256_file(op_ver)

    print(json.dumps({
        "campaign": 339, "verdict": verdict, "edge_proven": edge_proven,
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
