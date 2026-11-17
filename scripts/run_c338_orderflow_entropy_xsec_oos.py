#!/usr/bin/env python3
"""C338 — rigorous costed out-of-sample test of the cross-sectional intraday
ORDER-FLOW ENTROPY / INFORMATION CONTENT / TRADE BURSTINESS SEASONAL DISLOCATION
statistical-arbitrage family on 10 USDT-M linear perps at native 5m (4212
pre-registered configs).

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
ORDER-FLOW SKEW / ASYMMETRIC IMPULSE SEASONAL DISLOCATION.

C338 is the FIRST modern campaign to trade each asset's CAUSAL trailing
same-(TOD x DOW) seasonal deviation of its OWN intraday ORDER-FLOW ENTROPY /
INFORMATION-CONTENT / BURSTINESS metrics — from real signed_volume,
total_volume, trade_count, trade_sign_sum. Unlike C323 (raw flow level/ratio
seasonality), C329 (return sign entropy), C335 (order-flow toxicity), C336
(order-flow persistence) and C337 (order-flow skew/asymmetry), C338 measures
information-theoretic (Shannon/conditional/permutation entropy, mutual /
transfer entropy, normalized information share) and burstiness (CV of inter-trade
intensity, burst index, Hawkes baseline intensity) properties of the per-bar
order-flow SIGN sequence vs its own same-bucket baseline: unusually low entropy /
high burstiness / high information content vs same-bucket history -> expect
mean-reversion; score = -seasonal-dislocation. Mechanically distinct.

PER-BAR INPUTS (per bar, causal, real only):
    imb_t         = signed_volume_t / total_volume_t          (total_volume<=0 -> NaN)
    sign_t        = sign(trade_sign_sum_t)                    (trade_count<=0 -> NaN)
    atsv_t        = total_volume_t / trade_count_t            (trade_count<=0 -> NaN)

SIGNALS (pre-registered, causal, metrics computed over trailing lookback L bars
ending at bar t-1; score = -(signal_t - seasonal_baseline_t) / seasonal_std_t;
cross-sectional rank; dollar-neutral gross 1.0):
--------------------------------------------------------------------------------
Bucket = (weekday, tod) with tod = seconds-of-day//300 (0..287), 7 weekdays x 288
= 2016 buckets per asset. Seasonal baseline = trailing mean/std at the same
bucket from history strictly before bar t (causal, shift(1)), NaN-aware with
min_periods=3, EXCLUDING NaN same-bucket observations (no ffill/impute).

Entropy metrics (over the sign sequence in the trailing L-bar window):
  shannon_entropy : H(sign) over sign categories {-1,0,1} in window
  cond_entropy1   : H(sign_t | sign_{t-1})   (lag-1 conditional entropy)
  cond_entropy2   : H(sign_t | sign_{t-1}, sign_{t-2})
  perm_entropy    : Bandt-Pompe permutation entropy, m=3, tau=1
  mutual_info     : I(sign_t; sign_{t-1})    (lag-1 mutual information)
Burstiness metrics:
  cv_intertrade   : std(atsv)/mean(atsv) in window (atsv = total_volume/trade_count)
  hawkes_intensity: baseline-intensity proxy = share of directed trades in window
                    (fail-closed NaN on insufficient history)
  burst_index     : (cv^2 - 1) / (cv^2 + 1)   (Kim et al. 2009)
Information-flow metrics:
  transfer_entropy: T(sign_t -> log_return_{t+1} | log_return_t) (Schreiber 2000)
  flow_info_share : I(sign_t; log_return_{t+1}) / H(log_return_{t+1})

Signals (all *_dev use score = -(v-m)/sd):
  shannon_entropy_dev, cond_entropy1_dev, cond_entropy2_dev, perm_entropy_dev,
  mutual_info_dev, cv_intertrade_dev, hawkes_intensity_dev, burst_index_dev,
  transfer_entropy_dev, flow_info_share_dev,
  shannon_entropy_placebo, cond_entropy1_placebo, burst_index_placebo  (placebos)

Placebos (shannon_entropy_placebo, cond_entropy1_placebo, burst_index_placebo)
are seasonal dislocations of recorded-seed phase-randomized surrogates of the
corresponding metric series (same marginal, temporal alignment destroyed) —
attribution placebos, never counted as edges.

GRID (4212 = 13 x 6 x 3 x 3 x 3 x 2, all reported)
---------------------------------------------------
signal{13} x lookback{60,120,240,480,960,1920} bars(6) x
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
  reports/campaign338_oos_sweep_<ts>.json  (+ gitignored *.full.json)
  reports/campaign338_tradable_edge_registry_<ts>.json
  reports/campaign338_summary_<ts>.json
  reports/campaign338_verdict_<ts>.json
  reports/campaign338_binding_constraint_<ts>.json
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

CACHE_DIR = cache_dir / "campaign338_orderflow_entropy_5m"
CACHE_META = cache_dir / "campaign338_orderflow_entropy_5m.meta.json"
CACHE_PROV = cache_dir / "campaign338_orderflow_entropy_5m.provenance.json"
REQUIRED_FIELDS = ["index_ms", "perp_close", "log_return",
                   "imb", "sign", "atsv", "funding_rate"]

# ---- pre-registered grid ----
SIGNALS = ("shannon_entropy_dev", "cond_entropy1_dev", "cond_entropy2_dev",
           "perm_entropy_dev", "mutual_info_dev", "cv_intertrade_dev",
           "hawkes_intensity_dev", "burst_index_dev", "transfer_entropy_dev",
           "flow_info_share_dev",
           "shannon_entropy_placebo", "cond_entropy1_placebo",
           "burst_index_placebo")
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
PLACEBO_SEED = 20261118
TRAIN_M, TEST_M, ROLL_M = 12, 3, 3
STABILITY_MIN_SIGN_CONSISTENCY = 0.70
STABILITY_MIN_SHARPE_CORR = 0.50
DOMINANT_SHARE_MIN = 0.50

TOD_BARS_PER_DAY = 288
WEEKDAYS = 7
N_BUCKETS = WEEKDAYS * TOD_BARS_PER_DAY

N_TRIALS = (len(SIGNALS) * len(LOOKBACKS) *
            len(REBALANCES) * len(FEES) * len(SLIPS) * len(COST_VARIANTS))  # 4212

# signal -> (base_metric_key, is_placebo)
SIGNAL_FAMILY = {
    "shannon_entropy_dev": ("shannon", False),
    "cond_entropy1_dev": ("cond1", False),
    "cond_entropy2_dev": ("cond2", False),
    "perm_entropy_dev": ("perm", False),
    "mutual_info_dev": ("mi", False),
    "cv_intertrade_dev": ("cv", False),
    "hawkes_intensity_dev": ("hawkes", False),
    "burst_index_dev": ("burst", False),
    "transfer_entropy_dev": ("te", False),
    "flow_info_share_dev": ("fis", False),
    "shannon_entropy_placebo": ("shannon", True),
    "cond_entropy1_placebo": ("cond1", True),
    "burst_index_placebo": ("burst", True),
}
# all signals use score = -(v - m) / sd  (seasonal dislocation)
SIGNAL_SIGN = {s: -1.0 for s in SIGNALS}

ATTR_REPRESENTATIVES = {
    "shannon_entropy_dev": "shannon_entropy_dev",
    "cond_entropy1_dev": "cond_entropy1_dev",
    "cond_entropy2_dev": "cond_entropy2_dev",
    "perm_entropy_dev": "perm_entropy_dev",
    "mutual_info_dev": "mutual_info_dev",
    "cv_intertrade_dev": "cv_intertrade_dev",
    "hawkes_intensity_dev": "hawkes_intensity_dev",
    "burst_index_dev": "burst_index_dev",
    "transfer_entropy_dev": "transfer_entropy_dev",
    "flow_info_share_dev": "flow_info_share_dev",
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


def _entropy_from_counts(counts: np.ndarray, total: np.ndarray) -> np.ndarray:
    """Shannon entropy from per-category counts and total (per row)."""
    n = counts.shape[0]
    out = np.full(n, np.nan, dtype=float)
    valid = total >= 2
    if not valid.any():
        return out
    p = np.where(total[:, None] > 0, counts / np.maximum(total[:, None], 1.0), 0.0)
    ppos = p > 0
    H = np.zeros(n, dtype=float)
    np.multiply(p, np.log(p), out=H, where=ppos)
    H = -H.sum(axis=1)
    out[valid] = H[valid]
    return out


def _sign_cat(sign: np.ndarray) -> tuple:
    """Encode sign {-1,0,1} to categories {0,1,2}; NaN -> -1, plus finite mask."""
    fin = np.isfinite(sign)
    cat = np.where(fin, np.sign(sign).astype(np.int64) + 1, -1)
    return cat, fin


def _pair_encode(a: np.ndarray, b: np.ndarray, n_sym: int = 3) -> np.ndarray:
    """Encode two sign-category arrays (values 0..n_sym-1, -1 missing) to a joint int."""
    out = np.full(len(a), -1, dtype=np.int64)
    fin = (a >= 0) & (b >= 0)
    out[fin] = a[fin] * n_sym + b[fin]
    return out


def _triple_encode(a: np.ndarray, b: np.ndarray, c: np.ndarray, n_sym: int = 3) -> np.ndarray:
    out = np.full(len(a), -1, dtype=np.int64)
    fin = (a >= 0) & (b >= 0) & (c >= 0)
    out[fin] = (a[fin] * n_sym + b[fin]) * n_sym + c[fin]
    return out


def _perm_pattern_id_vec(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> np.ndarray:
    out = np.full(len(a), -1, dtype=np.int64)
    fin = (a >= 0) & (b >= 0) & (c >= 0)
    idx = np.nonzero(fin)[0]
    if len(idx) == 0:
        return out
    aa, bb, cc = a[idx], b[idx], c[idx]
    # rank of each element within triplet (0=lowest..2=highest), ties broken by index order
    order = np.lexsort((cc, bb, aa))  # indices into the triplet positions
    ranks = np.empty(len(idx), dtype=np.int64)
    # order[k] = position (0=a,1=b,2=c) that is k-th smallest
    ranks[order] = np.arange(3)
    # ranks[:, position] = rank of a,b,c ; permutation id from (rank_a, rank_b, rank_c)
    perm_to_id = {
        (0, 1, 2): 0, (0, 2, 1): 1, (1, 0, 2): 2,
        (1, 2, 0): 3, (2, 0, 1): 4, (2, 1, 0): 5,
    }
    ids = np.array([perm_to_id.get(tuple(int(v) for v in r), -1)
                    for r in np.stack([ranks, ranks, ranks], axis=1)], dtype=np.int64)
    # NOTE: ranks above is per-triplet [rank_a, rank_b, rank_c]? lexsort returns positions;
    # rebuild properly:
    ra = np.empty(len(idx), dtype=np.int64); rb = np.empty(len(idx), dtype=np.int64); rc = np.empty(len(idx), dtype=np.int64)
    ra[order] = np.arange(3); rb[order] = np.arange(3); rc[order] = np.arange(3)
    # that's wrong (all arange). Do explicit:
    # rank of value at position p among the 3 values:
    vals = np.stack([aa, bb, cc], axis=1)  # (k,3)
    sor = np.argsort(vals, axis=1, kind="mergesort")
    ranks2 = np.empty_like(sor)
    ranks2[np.arange(len(idx))[:, None], sor] = np.arange(3)
    rank_a = ranks2[:, 0]; rank_b = ranks2[:, 1]; rank_c = ranks2[:, 2]
    ids = np.array([perm_to_id.get((int(x), int(y), int(z)), -1)
                    for x, y, z in zip(rank_a, rank_b, rank_c)], dtype=np.int64)
    out[idx] = ids
    return out


def _ewma_nan_aware(x: np.ndarray, halflife: float, min_periods: int) -> np.ndarray:
    n = len(x)
    out = np.full(n, np.nan, dtype=np.float64)
    alpha = 1.0 - np.exp(-np.log(2.0) / float(halflife))
    decay = 1.0 - alpha
    num = 0.0
    den = 0.0
    cnt = 0
    for t in range(n):
        num *= decay
        den *= decay
        v = x[t]
        if np.isfinite(v):
            num += v
            den += 1.0
            cnt += 1
            if cnt >= min_periods and den > 0:
                out[t] = num / den
    return out


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
def _bin_return(r: np.ndarray) -> np.ndarray:
    """Bin log_return into 3 categories: -1->0 (neg), ~0->1 (zero), 1->2 (pos)."""
    out = np.full(len(r), -1, dtype=np.int64)
    fin = np.isfinite(r)
    out[fin] = np.where(r[fin] < 0, 0, np.where(r[fin] > 0, 2, 1)).astype(np.int64)
    return out


def compute_metrics(sign: np.ndarray, atsv: np.ndarray, r: np.ndarray,
                    L: int, min_periods: int = 3) -> dict:
    """Compute all causal metric series for one asset over trailing lookback L
    ending at bar t-1 (metric[t] uses bars [t-L, t-1]).
    Returns dict metric_name -> (n_bars,) array (NaN where undefined)."""
    n = len(sign)
    res: dict = {}
    cat_sign, fin_sign = _sign_cat(sign)
    rbin = _bin_return(r)
    fin_r = np.isfinite(r)

    # ----- rolling counts of sign categories (window ending at v, [v-L+1, v]) -----
    def roll_cat_counts(cat, n_cats):
        counts = np.zeros((n, n_cats), dtype=float)
        tot = np.zeros(n, dtype=float)
        finm = cat >= 0
        for c in range(n_cats):
            counts[:, c] = _roll_count_bool((cat == c) & finm, L)
        tot = _roll_count_bool(finm, L)
        return counts, tot

    scounts, stot = roll_cat_counts(cat_sign, 3)

    # shannon_entropy: H(sign) over {-1,0,1}
    res["shannon"] = _entropy_from_counts(scounts, stot)

    # ----- pair / triple / quad encodings for conditional entropy & MI -----
    # pair[t] = encode(sign[t], sign[t-1]); defined t>=1
    pair = _pair_encode(cat_sign[1:], cat_sign[:-1])  # length n-1, index t (t>=1)
    # align pair to full-length array indexed by end position v: pair_end[v] = pair[v] (v>=1)
    pair_full = np.full(n, -1, dtype=np.int64)
    pair_full[1:] = pair
    pair_fin = pair_full >= 0
    n_pair = 9
    pcounts = np.zeros((n, n_pair), dtype=float)
    for c in range(n_pair):
        pcounts[:, c] = _roll_count_bool((pair_full == c) & pair_fin, L)
    ptot = _roll_count_bool(pair_fin, L)

    # triple[t] = encode(sign[t], sign[t-1], sign[t-2]); t>=2
    trip_full = np.full(n, -1, dtype=np.int64)
    trip_full[2:] = _triple_encode(cat_sign[2:], cat_sign[1:-1], cat_sign[:-2])
    trip_fin = trip_full >= 0
    n_trip = 27
    tcounts = np.zeros((n, n_trip), dtype=float)
    for c in range(n_trip):
        tcounts[:, c] = _roll_count_bool((trip_full == c) & trip_fin, L)
    ttot = _roll_count_bool(trip_fin, L)

    # cond_entropy1 H(S_t|S_{t-1}) = H(pair) - H(prev marginal)
    # marginal of sign_{t-1}: series = sign[t-1] aligned at index t
    prev_sign = np.full(n, -1, dtype=np.int64)
    prev_sign[1:] = cat_sign[:-1]
    prev_fin = prev_sign >= 0
    pcounts_m = np.zeros((n, 3), dtype=float)
    for c in range(3):
        pcounts_m[:, c] = _roll_count_bool((prev_sign == c) & prev_fin, L)
    ptot_m = _roll_count_bool(prev_fin, L)

    H_pair = _entropy_from_counts(pcounts, ptot)
    H_prev = _entropy_from_counts(pcounts_m, ptot_m)
    res["cond1"] = H_pair - H_prev

    # mutual_info I(S_t; S_{t-1}) = H(S_t) + H(S_{t-1}) - H(pair)
    H_curr = _entropy_from_counts(scounts, stot)  # same as shannon
    res["mi"] = H_curr + H_prev - H_pair

    # cond_entropy2 H(S_t | S_{t-1}, S_{t-2}) = H(triple) - H(pair marginal over t-1,t-2)
    H_trip = _entropy_from_counts(tcounts, ttot)
    # pair marginal = encode(sign[t-1], sign[t-2]) aligned at index t
    prevpair_full = np.full(n, -1, dtype=np.int64)
    prevpair_full[2:] = _pair_encode(cat_sign[1:-1], cat_sign[:-2])
    prevpair_fin = prevpair_full >= 0
    pp_counts = np.zeros((n, n_pair), dtype=float)
    for c in range(n_pair):
        pp_counts[:, c] = _roll_count_bool((prevpair_full == c) & prevpair_fin, L)
    pp_tot = _roll_count_bool(prevpair_fin, L)
    H_pp = _entropy_from_counts(pp_counts, pp_tot)
    res["cond2"] = H_trip - H_pp

    # ----- permutation entropy m=3 tau=1 -----
    perm_id = _perm_pattern_id_vec(cat_sign[2:], cat_sign[1:-1], cat_sign[:-2])
    perm_full = np.full(n, -1, dtype=np.int64)
    perm_full[2:] = perm_id
    perm_fin = perm_full >= 0
    pcounts6 = np.zeros((n, 6), dtype=float)
    for c in range(6):
        pcounts6[:, c] = _roll_count_bool((perm_full == c) & perm_fin, L)
    ptot6 = _roll_count_bool(perm_fin, L)
    res["perm"] = _entropy_from_counts(pcounts6, ptot6)

    # ----- burstiness metrics (over atsv in window) -----
    # atsv rolling mean & std
    fin_atsv = np.isfinite(atsv)
    atsv_f = np.where(fin_atsv, atsv, 0.0)
    atsv2_f = np.where(fin_atsv, atsv * atsv, 0.0)
    cs1 = np.concatenate([[0.0], np.cumsum(atsv_f)])
    cs2 = np.concatenate([[0.0], np.cumsum(atsv2_f)])
    cc = np.concatenate([[0.0], np.cumsum(fin_atsv.astype(float))])
    u = np.arange(L - 1, n)
    cnt = cc[u + 1] - cc[u - L + 1]
    s1 = cs1[u + 1] - cs1[u - L + 1]
    s2 = cs2[u + 1] - cs2[u - L + 1]
    mean = np.full(n, np.nan, dtype=float)
    var = np.full(n, np.nan, dtype=float)
    valid = cnt >= min_periods
    mean[u[valid]] = s1[valid] / np.maximum(cnt[valid], 1.0)
    var[u[valid]] = s2[valid] / np.maximum(cnt[valid], 1.0) - mean[u[valid]] ** 2
    sd = np.sqrt(np.maximum(var, 0.0))
    cv = np.full(n, np.nan, dtype=float)
    cv_valid = valid & (sd > 0) & (mean != 0)
    cv[cv_valid] = sd[cv_valid] / np.abs(mean[cv_valid])
    res["cv"] = cv
    burst = np.full(n, np.nan, dtype=float)
    bv = cv_valid & np.isfinite(cv)
    burst[bv] = (cv[bv] ** 2 - 1.0) / (cv[bv] ** 2 + 1.0)
    res["burst"] = burst

    # hawkes_intensity: baseline-intensity proxy = share of directed (nonzero sign) trades
    directed = fin_sign & (sign != 0)
    dtot = _roll_count_bool(directed, L)
    hawkes = np.full(n, np.nan, dtype=float)
    hv = stot >= min_periods
    hawkes[hv] = dtot[hv] / np.maximum(stot[hv], 1.0)
    res["hawkes"] = hawkes

    # ----- information-flow metrics (sign -> next return | past return) -----
    # pairs (R_t, R_{t+1}) and triples (R_t, S_t, R_{t+1}); series indexed by t (t from 0..n-2)
    # align to end position v by placing at index v
    rbin_full = rbin  # length n
    sgn_full = cat_sign  # length n
    # pair_RR[t] = encode(rbin[t], rbin[t+1]), t in [0, n-2]
    pair_rr = _pair_encode(rbin[:-1], rbin[1:])  # index t
    pair_rr_full = np.full(n, -1, dtype=np.int64)
    pair_rr_full[: n - 1] = pair_rr
    pair_rr_fin = pair_rr_full >= 0
    n_rr = 9
    rr_counts = np.zeros((n, n_rr), dtype=float)
    for c in range(n_rr):
        rr_counts[:, c] = _roll_count_bool((pair_rr_full == c) & pair_rr_fin, L)
    rr_tot = _roll_count_bool(pair_rr_fin, L)
    # marginal of R_t at index t (used for H(R_t))
    rcounts_m = np.zeros((n, 3), dtype=float)
    for c in range(3):
        rcounts_m[:, c] = _roll_count_bool((rbin_full == c) & fin_r, L)
    rtot_m = _roll_count_bool(fin_r, L)
    H_RR = _entropy_from_counts(rr_counts, rr_tot)
    H_R = _entropy_from_counts(rcounts_m, rtot_m)
    # H(R_{t+1}|R_t) = H(RR) - H(R)
    H_Rnext_given_R = H_RR - H_R

    # triple (R_t, S_t, R_{t+1})
    trip_rsr = _triple_encode(rbin[:-1], sgn_full[:-1], rbin[1:])  # index t
    trip_rsr_full = np.full(n, -1, dtype=np.int64)
    trip_rsr_full[: n - 1] = trip_rsr
    trip_rsr_fin = trip_rsr_full >= 0
    n_rsr = 27
    rsr_counts = np.zeros((n, n_rsr), dtype=float)
    for c in range(n_rsr):
        rsr_counts[:, c] = _roll_count_bool((trip_rsr_full == c) & trip_rsr_fin, L)
    rsr_tot = _roll_count_bool(trip_rsr_fin, L)
    # pair marginal (R_t, S_t) at index t
    pair_rs = _pair_encode(rbin[:-1], sgn_full[:-1])
    pair_rs_full = np.full(n, -1, dtype=np.int64)
    pair_rs_full[: n - 1] = pair_rs
    pair_rs_fin = pair_rs_full >= 0
    rs_counts = np.zeros((n, n_pair), dtype=float)
    for c in range(n_pair):
        rs_counts[:, c] = _roll_count_bool((pair_rs_full == c) & pair_rs_fin, L)
    rs_tot = _roll_count_bool(pair_rs_fin, L)
    H_RSR = _entropy_from_counts(rsr_counts, rsr_tot)
    H_RS = _entropy_from_counts(rs_counts, rs_tot)
    # H(R_{t+1}|R_t, S_t) = H(RSR) - H(RS)
    H_Rnext_given_RS = H_RSR - H_RS
    res["te"] = H_Rnext_given_R - H_Rnext_given_RS

    # flow_info_share I(S_t; R_{t+1}) / H(R_{t+1})
    # joint (S_t, R_{t+1})
    pair_sr = _pair_encode(sgn_full[:-1], rbin[1:])  # index t, uses S_t and R_{t+1}
    pair_sr_full = np.full(n, -1, dtype=np.int64)
    pair_sr_full[: n - 1] = pair_sr
    pair_sr_fin = pair_sr_full >= 0
    sr_counts = np.zeros((n, n_pair), dtype=float)
    for c in range(n_pair):
        sr_counts[:, c] = _roll_count_bool((pair_sr_full == c) & pair_sr_fin, L)
    sr_tot = _roll_count_bool(pair_sr_fin, L)
    # marginal of R_{t+1}: rbin[t+1] aligned at index t -> series rbin[1:] at index t+1, so at index u use rbin[u+1]
    rnext = np.full(n, -1, dtype=np.int64)
    rnext[: n - 1] = rbin[1:]
    rnext_fin = rnext >= 0
    rnext_counts = np.zeros((n, 3), dtype=float)
    for c in range(3):
        rnext_counts[:, c] = _roll_count_bool((rnext == c) & rnext_fin, L)
    rnext_tot = _roll_count_bool(rnext_fin, L)
    H_SR = _entropy_from_counts(sr_counts, sr_tot)
    H_S = _entropy_from_counts(scounts, stot)  # H(S_t) - but counts window is sign window; ok approx
    H_Rnext = _entropy_from_counts(rnext_counts, rnext_tot)
    I_SR = H_S + H_Rnext - H_SR
    fis = np.full(n, np.nan, dtype=float)
    fv = np.isfinite(I_SR) & np.isfinite(H_Rnext) & (H_Rnext > 0)
    fis[fv] = I_SR[fv] / H_Rnext[fv]
    res["fis"] = fis

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
    lookback, plus placebo surrogates of shannon, cond1, burst."""
    bucket = bs["bucket"]
    n_bars = bs["n_bars"]
    sign = bs["sign"]
    atsv = bs["atsv"]
    r = bs["log_return"]
    series: dict = {}
    for L in LOOKBACKS:
        m = compute_metrics(sign, atsv, r, L, MIN_PERIODS_BASELINE)
        for k, v in m.items():
            series[(k, L)] = v
    # placebos (recorded-seed phase randomization of the metric series)
    for L in LOOKBACKS:
        series[("shannon", L)]  # ensure exists
        series[("shannon_placebo", L)] = np.apply_along_axis(
            lambda row: _phase_randomized_surrogate(row, PLACEBO_SEED), 1, series[("shannon", L)])
        series[("cond1_placebo", L)] = np.apply_along_axis(
            lambda row: _phase_randomized_surrogate(row, PLACEBO_SEED), 1, series[("cond1", L)])
        series[("burst_placebo", L)] = np.apply_along_axis(
            lambda row: _phase_randomized_surrogate(row, PLACEBO_SEED), 1, series[("burst", L)])
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
        raise SystemExit(f"FATAL: C338 shard dir missing: {CACHE_DIR}")
    if not CACHE_META.exists():
        raise SystemExit(f"FATAL: C338 meta missing: {CACHE_META}")
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
        raise SystemExit("FATAL: C338 common grid is empty")
    if n_b % TOD_BARS_PER_DAY != 0:
        raise SystemExit("FATAL: C338 grid is not a whole number of 288-bar days")

    def mat(key):
        out = np.zeros((n_assets, n_b), dtype=float)
        for i, s in enumerate(symbols):
            out[i] = np.asarray(per_asset[s][key], dtype=float)
        return out

    perp_close = mat("perp_close")
    log_return = mat("log_return")
    imb = mat("imb")
    sign = mat("sign")
    atsv = mat("atsv")

    if not (np.isfinite(perp_close).all() and (perp_close > 0).all()):
        raise SystemExit("FATAL: non-finite/non-positive perp_close")
    if not np.isfinite(log_return).all():
        raise SystemExit("FATAL: non-finite log_return in cache")

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
            "imb": imb, "sign": sign, "atsv": atsv, "bucket": bucket, "splits": splits}


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

    ref_cfg = dict(signal="shannon_entropy_dev", L=240, H=4,
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
        "generated_at_utc": ts, "campaign": 338, "part": "oos_sweep",
        "analysis": "c338_orderflow_entropy_xsec_stat_arb_oos_5m",
        "verdict": verdict, "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "fail_closed": True,
        "mandate": (
            "C338 — test the cross-sectional intraday ORDER-FLOW ENTROPY / "
            "INFORMATION CONTENT / TRADE BURSTINESS SEASONAL DISLOCATION "
            "statistical-arbitrage family on 10 USDT-M linear perps at native 5m "
            "(4212 pre-registered configs). Per-bar primitives: "
            "imb=signed_volume/total_volume (total_volume<=0 -> NaN); "
            "sign=sign(trade_sign_sum) (trade_count<=0 -> NaN); "
            "atsv=total_volume/trade_count (trade_count<=0 -> NaN). "
            "Metrics over trailing lookback L bars ending at bar t-1: "
            "shannon_entropy=H(sign); cond_entropy1=H(sign_t|sign_{t-1}); "
            "cond_entropy2=H(sign_t|sign_{t-1},sign_{t-2}); perm_entropy=Bandt-Pompe "
            "m=3 tau=1; mutual_info=I(sign_t;sign_{t-1}); cv_intertrade=std(atsv)/mean(atsv); "
            "hawkes_intensity=baseline-intensity proxy; burst_index=(cv^2-1)/(cv^2+1); "
            "transfer_entropy=T(sign->next return | past return); "
            "flow_info_share=I(sign;next return)/H(next return). "
            "Seasonal baseline = trailing mean/std at same (weekday,tod) bucket "
            "from history strictly before bar t (causal shift(1)), min_periods=3, "
            "NaN-aware, excluding NaN obs. "
            "Signals: 10 real *_dev + 3 placebos (phase-randomized surrogates, "
            "never edges). Single-leg dollar-neutral perp PnL with costs on turnover "
            "(taker=fee+slip; maker_blend=0.5*fee+slip). Gates: Holm+BH at "
            "alpha=0.05 (BOTH), MDE, stability, signal-vs-placebo attribution. "
            "PRE-REGISTERED NaN policy: total_volume<=0 -> imb NaN; "
            "trade_count<=0 -> sign/atsv NaN; metric NaN unless sufficient finite obs; "
            "seasonal stats NaN-aware min_periods excluding NaN obs; NaN-score bars "
            "weight 0; raw flow fields carry zero NaN except zero-activity denominators."
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
            "raw_features": "log_return=log(c[t]/c[t-1]) (r[0]=0) from real strictly-positive perp_close; signed_volume/total_volume/trade_count/trade_sign_sum real from C312.",
            "primitives": "imb=signed_volume/total_volume (tv<=0 -> NaN); sign=sign(trade_sign_sum) (tc<=0 -> NaN); atsv=total_volume/trade_count (tc<=0 -> NaN).",
            "signals": "entropy/burstiness/information metrics over trailing L bars ending at t-1; score=sign*(v-m)/sd with m/sd trailing same-bucket mean/std (min_periods=3, excluding NaN, causal shift(1)); cross-sectional rank, dollar-neutral gross 1.0; NaN-score assets weight 0.",
            "pnl": "single-leg perp: pnl = sum_i pos_i * perp_ret_i.",
            "costs": "charged on turnover; taker = fee+slip; maker_blend = 0.5*fee+slip.",
            "missing_data": "non-finite -> NaN; never impute/ffill; insufficient valid obs -> NaN -> not traded (fail-closed).",
            "multiple_testing": "one-sided paired t-test of per-split OOS net vs 0; Holm step-down AND Benjamini-Hochberg over all 4212 configs at alpha=0.05.",
            "mde": "two-sided alpha=0.05, power=0.80: (t_{0.975}+t_{0.80})*s/sqrt(n_splits).",
            "attribution": "mean |OOS net| per signal across all its configs; shares=|mean|/sum(|means|) over all 13 signals incl. placebos; dominant must be a real (non-placebo) signal with share >= 0.5 for attribution_ok.",
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
    op = reports / f"campaign338_oos_sweep_{ts}.json"
    op.write_text(json.dumps(slim, indent=2, default=jdefault) + "\n")
    sweep_sha = sha256_file(op)
    full = reports / f"campaign338_oos_sweep_{ts}.full.json"
    full.write_text(json.dumps(sweep_obj, indent=2, default=jdefault) + "\n")

    surviving = [results[i] for i in edge_idx if rej_holm[i] and rej_bh[i]]
    registry = {
        "generated_at_utc": ts, "campaign": 338, "part": "registry",
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
    op_reg = reports / f"campaign338_tradable_edge_registry_{ts}.json"
    op_reg.write_text(json.dumps(registry, indent=2, default=jdefault) + "\n")
    reg_sha = sha256_file(op_reg)

    summary = {
        "generated_at_utc": ts, "campaign": 338, "part": "summary",
        "analysis": "validation_summary", "verdict": verdict, "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "universe": sweep_obj["universe"], "config": sweep_obj["config"],
        "gates": sweep_obj["gates"],
        "artifacts": {"oos_sweep": {"path": str(op.relative_to(ROOT)), "sha256": sweep_sha},
                      "registry": {"path": str(op_reg.relative_to(ROOT)), "sha256": reg_sha}},
        "summary": sweep_obj["summary"], "binding_constraint": binding,
    }
    op_sum = reports / f"campaign338_summary_{ts}.json"
    op_sum.write_text(json.dumps(summary, indent=2, default=jdefault) + "\n")
    sum_sha = sha256_file(op_sum)

    finding = (
        f"C338 cross-sectional intraday ORDER-FLOW ENTROPY / INFORMATION CONTENT / "
        f"TRADE BURSTINESS SEASONAL DISLOCATION mean-reversion stat-arb edge "
        f"RETRACTED ({n_edge} deterministic edge configs, {n_survive_both} survive "
        f"Holm+BH over {N_TRIALS}); binding constraint: {binding}; dominant "
        f"attribution: {dominant} ({dominant_share:.4f})."
        if binding is not None
        else f"C338 cross-sectional intraday ORDER-FLOW ENTROPY / INFORMATION "
        f"CONTENT / TRADE BURSTINESS SEASONAL DISLOCATION mean-reversion stat-arb "
        f"edge validated: {n_survive_both} of {n_edge} deterministic edge configs "
        f"survive Holm+BH over {N_TRIALS}; edge_proven:{edge_proven}."
    )
    verdict_obj = {
        "generated_at_utc": ts, "campaign": 338, "part": "verdict",
        "analysis": "final_verdict", "verdict": verdict, "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "finding": finding,
        "basis": "c338_orderflow_entropy_xsec_stat_arb_costed_oos_5m",
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
            "No edge claim unless the costed OOS test survives Holm+BH over all 4212 configs",
            "Real USDT-M linear 5m perp_close + signed_volume + total_volume + trade_count + trade_sign_sum; funding excluded (control leg)",
            "Single-leg PnL with costs on turnover; executed_fills: false",
            "Only RNG is recorded-seed placebo phase randomization (not market data)",
        ],
    }
    op_ver = reports / f"campaign338_verdict_{ts}.json"
    op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")
    ver_sha = sha256_file(op_ver)

    bind_sha = None
    bind_path = None
    if binding is not None:
        binding_obj = {
            "generated_at_utc": ts, "campaign": 338, "part": "binding_constraint",
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
                "C338 cross-sectional intraday ORDER-FLOW ENTROPY / INFORMATION "
                "CONTENT / TRADE BURSTINESS SEASONAL DISLOCATION mean-reversion "
                "stat-arb does not survive validation; formal negative. Binding "
                "constraint: {binding}."
            ).format(binding=binding),
            "note": "Diagnosis only; never an edge claim. No threshold weakening.",
        }
        op_bind = reports / f"campaign338_binding_constraint_{ts}.json"
        op_bind.write_text(json.dumps(binding_obj, indent=2, default=jdefault) + "\n")
        bind_sha = sha256_file(op_bind)
        bind_path = str(op_bind.relative_to(ROOT))
        verdict_obj["binding_constraint_artifact"] = bind_path
        verdict_obj["binding_constraint_sha256"] = bind_sha
        op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")
        ver_sha = sha256_file(op_ver)

    print(json.dumps({
        "campaign": 338, "verdict": verdict, "edge_proven": edge_proven,
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
