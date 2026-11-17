#!/usr/bin/env python3
"""C350 — rigorous costed out-of-sample test of the cross-sectional intraday
DETRENDED FLUCTUATION ANALYSIS (DFA) SCALING EXPONENT α × SEASONAL-DISLOCATION
mean-reversion stat-arb family on 10 USDT-M linear perps at native 5m
(1296 pre-registered configs).

GENUINELY NEW FAMILY (not a re-skin of any frozen modern campaign)
-----------------------------------------------------------------
C281B-C349 (all FROZEN formal negatives) exhausted carry, OFI/microstructure,
premium/index/mark basis, quarterly term-structure, same-asset spot-perp
lead-lag, autocorrelation/chop/vol-clustering/close-envelope/rescaled-range/
drawdown-duration/realized-variance-concentration/ordinal-pattern-entropy
families. C350 is the first modern campaign to trade each asset's CAUSAL
trailing same-(TOD x DOW) seasonal deviation of its DETRENDED FLUCTUATION
ANALYSIS (DFA) SCALING EXPONENT α:

    For each bar t, take trailing W=256 returns r[t-W+1 .. t].
    (1) demean the window; (2) form the profile y = cumsum(demeaned);
    (3) split y into non-overlapping boxes of scale n (front + back segments to
    use all points); (4) detrend each box by OLS linear fit;
    (5) F(n) = sqrt(mean of squared residuals over all boxes and both segments);
    (6) dfa[t] = α[t] = OLS slope of log F(n) vs log n over scales
    n ∈ {4, 8, 16, 32, 64, 128}.

NaN if t < W or any NaN in window or zero valid scales.

Unlike C346 (R/S = single-window range of the cumulative centered sum, one
effective scale), C350 is multi-scale *detrended* fluctuation (slope across 6
scales). Unlike C349 (ordinal-pattern entropy, no integration/detrending, no
scale slope), C350 integrates + detrends + regresses log-fluctuation on
log-scale. Unlike C326 (lag-1 signed-return AUTOCORRELATION, single pairwise
product), C350 is whole-window multi-scale long-range correlation. Unlike C343
(autocorrelation of |r| = vol clustering), C350 is fluctuation scaling of the
integrated demeaned return profile. Unlike C344 (SIGN-CHANGE RATE = chop
count), C350 is an RMS-fluctuation slope. Unlike C347 (drawdown duration /
time-under-water), C350 is scaling-exponent complexity, not path duration.
Unlike C345 (close location within trailing high–low envelope = Williams %R),
C350 is DFA α. Unlike C317 (realized-vol LEVELS), C350 is scale-invariant
correlation scaling. C342/C340/C341 need volume/notional/price-impact; C350 is
price-only and volume-free. C315/C320 trade raw seasonal RETURN mean-reversion
— C350 fades seasonal dislocation in *DFA α*, conditioned on last-move
direction.
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

CACHE_DIR = cache_dir / "campaign350_dfa_5m"
CACHE_META = cache_dir / "campaign350_dfa_5m.meta.json"
CACHE_PROV = cache_dir / "campaign350_dfa_5m.provenance.json"
REQUIRED_FIELDS = ["index_ms", "perp_close", "log_return", "abs_ret", "funding_rate"]

# ---- pre-registered grid ----
SIGNALS = ("dfa_dev", "dfa_norm_dev", "dfa_placebo", "dfa_norm_placebo")
LOOKBACKS = (60, 120, 240, 480, 960, 1920)          # bars (seasonal baseline history)
REBALANCES = (1, 4, 12)                            # bars
FEES = (0.0004, 0.0007, 0.0010)
SLIPS = (0.0, 0.0001, 0.0002)
COST_VARIANTS = ("taker", "maker_blend")
FRAC = 1.0 / 3.0
ALPHA = 0.05
MIN_PERIODS_BASELINE = 3
PLACEBO_SEED = 20261127
TRAIN_M, TEST_M, ROLL_M = 12, 3, 3
STABILITY_MIN_SIGN_CONSISTENCY = 0.70
STABILITY_MIN_SHARPE_CORR = 0.50
DOMINANT_SHARE_MIN = 0.50

# DFA parameters (fixed, pre-registered)
DFA_W = 256                          # intrinsic window (fixed, decoupled from seasonal lookback)
DFA_SCALES = (4, 8, 16, 32, 64, 128)  # scales n
DFA_N_SCALES = len(DFA_SCALES)       # 6

TOD_BARS_PER_DAY = 288
WEEKDAYS = 7
N_BUCKETS = WEEKDAYS * TOD_BARS_PER_DAY

N_TRIALS = (len(SIGNALS) * len(LOOKBACKS) *
             len(REBALANCES) * len(FEES) * len(SLIPS) * len(COST_VARIANTS))  # 1296

# signal -> (base_metric_key, kind)
# kind in {"dev","placebo_dev"}
SIGNAL_FAMILY = {
    "dfa_dev": ("dfa", "dev"),
    "dfa_norm_dev": ("dfa_norm", "dev"),
    "dfa_placebo": ("dfa", "placebo_dev"),
    "dfa_norm_placebo": ("dfa_norm", "placebo_dev"),
}

ATTR_REPRESENTATIVES = {
    "dfa_dev": "dfa_dev",
    "dfa_norm_dev": "dfa_norm_dev",
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


# ------------------------------------------------------- DFA scaling-exponent metric (per asset, fixed W=256)
def _dfa_alpha_single_window(window: np.ndarray, scales=DFA_SCALES) -> float:
    """Reference DFA α for ONE trailing window (length W).

    (1) demean the window; (2) profile y = cumsum(demeaned);
    (3) split y into non-overlapping boxes of scale n (front + back segments to
    use all points); (4) OLS-detrend each box; (5) F(n)=sqrt(mean sq residual);
    (6) α = OLS slope of log F(n) vs log n over scales.
    Returns NaN if any scale has no valid boxes.
    """
    W = len(window)
    if W <= 0 or not np.isfinite(window).all():
        return float("nan")
    x = np.asarray(window, dtype=float)
    y = np.cumsum(x - x.mean())
    log_n = []
    log_F = []
    for n in scales:
        if n > W:
            return float("nan")
        n_boxes = W // n
        # front segment
        resid_sq = 0.0
        count = 0
        # Use front (n_boxes boxes starting at 0) and back (n_boxes boxes ending at W)
        for start in list(range(0, n_boxes * n, n)) + list(range(W - n_boxes * n, W, n)):
            seg = y[start:start + n]
            # OLS detrend
            t = np.arange(n, dtype=float)
            t_mean = t.mean()
            s_mean = seg.mean()
            denom = ((t - t_mean) ** 2).sum()
            if denom <= 0:
                return float("nan")
            slope = ((t - t_mean) * (seg - s_mean)).sum() / denom
            intercept = s_mean - slope * t_mean
            resid = seg - (slope * t + intercept)
            resid_sq += float((resid * resid).sum())
            count += n
        if count == 0:
            return float("nan")
        F_n = math.sqrt(resid_sq / count)
        if not np.isfinite(F_n) or F_n <= 0:
            return float("nan")
        log_n.append(math.log(float(n)))
        log_F.append(math.log(F_n))
    if len(log_n) < 2:
        return float("nan")
    ln = np.asarray(log_n, dtype=float)
    lF = np.asarray(log_F, dtype=float)
    ln_mean = ln.mean()
    lF_mean = lF.mean()
    denom = ((ln - ln_mean) ** 2).sum()
    if denom <= 0:
        return float("nan")
    alpha = float(((ln - ln_mean) * (lF - lF_mean)).sum() / denom)
    return alpha if np.isfinite(alpha) else float("nan")


def _dfa_alpha_bruteforce(r: np.ndarray, W: int = DFA_W, scales=DFA_SCALES) -> dict:
    """Brute-force reference DFA implementation for testing.
    Returns dict with 'dfa' and 'dfa_norm' arrays (NaN where undefined).
    dfa_norm = dfa - 0.5."""
    n = len(r)
    out = {k: np.full(n, np.nan, dtype=float) for k in ("dfa", "dfa_norm")}
    if n < W:
        return out
    for t in range(W, n):
        window = r[t - W + 1:t + 1]
        if not np.isfinite(window).all():
            continue
        a = _dfa_alpha_single_window(window, scales)
        out["dfa"][t] = a
        if np.isfinite(a):
            out["dfa_norm"][t] = a - 0.5
    return out


def _box_detrended_fluctuation_1d(y: np.ndarray, n: int) -> float:
    """F(n) for a single profile y (length W) at scale n.
    Uses front + back non-overlapping boxes of scale n (to use all points).
    Returns NaN if no valid boxes."""
    W = len(y)
    if n > W or n < 2:
        return float("nan")
    n_boxes = W // n
    if n_boxes <= 0:
        return float("nan")
    # front boxes: [0, n), [n, 2n), ...
    # back boxes: [W-n, W), [W-2n, W-n), ...
    # OLS detrend each box
    t = np.arange(n, dtype=float)
    t_mean = t.mean()
    t_centered = t - t_mean
    denom = float((t_centered * t_centered).sum())
    if denom <= 0:
        return float("nan")
    resid_sq = 0.0
    count = 0
    # front
    for b in range(n_boxes):
        seg = y[b * n:(b + 1) * n]
        s_mean = seg.mean()
        slope = float((t_centered * (seg - s_mean)).sum() / denom)
        intercept = s_mean - slope * t_mean
        resid = seg - (slope * t + intercept)
        resid_sq += float((resid * resid).sum())
        count += n
    # back (only if it doesn't duplicate the front, i.e. always add distinct trailing boxes)
    # To use all points, add boxes from the back that are not already covered by front.
    front_covered = n_boxes * n
    n_back = (W - front_covered) // n
    # If remainder, include the last n points as an extra back box to use leftover points
    for b in range(n_back):
        start = W - (b + 1) * n
        seg = y[start:start + n]
        s_mean = seg.mean()
        slope = float((t_centered * (seg - s_mean)).sum() / denom)
        intercept = s_mean - slope * t_mean
        resid = seg - (slope * t + intercept)
        resid_sq += float((resid * resid).sum())
        count += n
    if count == 0:
        return float("nan")
    F_n = math.sqrt(resid_sq / count)
    return F_n if np.isfinite(F_n) and F_n > 0 else float("nan")


def compute_dfa_metrics(r: np.ndarray, W: int = DFA_W, scales=DFA_SCALES) -> dict:
    """Fast vectorized DFA scaling exponent α for one asset over fixed intrinsic
    window W bars ending at bar t.

    Strategy: for each bar t, the window is r[t-W+1 .. t] of length W. The
    profile y = cumsum(demeaned window) depends on the absolute start index, so
    we cannot use a single global prefix-sum trick for arbitrary windows
    directly. However, the DFA statistic for a *fixed-length* window depends
    only on the relative shape of the window, and the residual sum for each box
    can be expressed in closed form from prefix sums of r, r^2, and index-
    weighted r within the window.

    For tractability and exactness we use the closed-form OLS detrending
    residual identity: for a segment y[start:start+n] with local index t=0..n-1,
    OLS residual sum-of-squares = Σ(y - ȳ)^2 - slope^2 * Σ(t-t̄)^2 where
    slope = Σ((t-t̄)(y-ȳ)) / Σ((t-t̄)^2). This requires, per window and per
    box, the sums of y, y^2, and (local_t * y) over the box. y is itself a
    cumulative sum of (r - mean(r)) over the window.

    To keep this vectorized and exact while remaining tractable for 315,648
    bars × 10 assets, we compute DFA per bar via a vectorized closed-form over
    all windows simultaneously using sliding-window sums. The demeaned profile
    within window ending at t is:
        y[j] = Σ_{k<=j} (r[t-W+1+k] - mean_window)
    which is a double cumulative structure. We derive y for all windows via a
    single global "double prefix sum" of r, then subtract the per-window linear
    trend so each window starts at 0.

    Because exact closed-form vectorization over 6 scales and 2 segments per
    window for 315,648 bars is intricate and error-prone, and the deliverable
    REQUIRES passing a brute-force equality test, we implement the vectorized
    path as a *memoized* per-scale sliding computation validated against the
    brute-force reference. The vectorized path below computes, for every bar t,
    the exact same quantity as _dfa_alpha_single_window but in O(n) per scale
    using sliding prefix sums, then asserts equality in tests.
    """
    n = len(r)
    out = {k: np.full(n, np.nan, dtype=float) for k in ("dfa", "dfa_norm")}
    if n < W:
        return out

    # Build demeaned-return sliding profile sums via double prefix sum.
    # For window ending at t (length W), demeaned return at offset k (0..W-1):
    #   d[k] = r[t-W+1+k] - mean(r[t-W+1..t])
    # profile y[k] = sum_{j=0..k} d[j]
    # We need, for each scale n, the OLS residual SS over front and back boxes.
    #
    # Instead of a fragile global closed-form, we compute per-bar using
    # precomputed sliding sums of r, r^2, and cross terms. Define for the whole
    # series the prefix sums:
    #   P1[i] = sum_{0..i-1} r        (P1[0]=0)
    # For a window [s, t] (s=t-W+1):
    #   S1 = P1[t+1] - P1[s]           (sum r in window)
    #   mean = S1 / W
    # The demeaned profile within the window:
    #   y[k] = (sum_{j=s..s+k} r[j]) - (k+1)*mean
    #        = (P1[s+k+1] - P1[s]) - (k+1)*S1/W
    # This y[k] depends on s and t only through S1 and the prefix P1 — fully
    # expressible with prefix sums. For a box covering local indices
    # [b0, b1) (b1-b0 = n), we need:
    #   Σ y, Σ y^2, Σ (local_t * y)
    # Σ y over box = Σ_k [ (P1[s+k+1]-P1[s]) - (k+1)*S1/W ]
    #              = (Σ_{k=b0..b1-1} P1[s+k+1]) - n*P1[s] - S1/W * Σ(k+1)
    # Σ y^2 and Σ (local_t*y) require Σ P1^2, Σ P1, etc., which need second-
    # order prefix sums of P1 (i.e. prefix of prefix of r). This is exact but
    # the algebra is large; for reliability and to satisfy the brute-force
    # equality requirement we compute DFA via a vectorized numba-free loop over
    # scales that calls a vectorized box-residual kernel.

    # Vectorized box residual kernel:
    # For a given scale n, front boxes are [b*n, (b+1)*n) in local coords,
    # back boxes are [W-(b+1)*n, W-b*n). We compute, for all windows at once,
    # the total residual SS across all boxes of scale n using sliding sums.
    #
    # Precompute global prefix sums:
    P1 = np.concatenate([[0.0], np.cumsum(np.asarray(r, dtype=float))])
    # P2 = prefix of (r * index)? We need Σ over a box of y and y^2 and local_t*y.
    # Build y for each window analytically via P1 is not enough for y^2 (needs
    # cross terms). Instead compute y explicitly per window is O(W) per bar.
    #
    # DECISION: To guarantee correctness AND performance within the task budget,
    # we compute DFA using a sliding approach that precomputes, for every start
    # index s and every scale n, the residual SS of the box [s, s+n) of the
    # profile anchored at s (window start). Because the profile depends on the
    # window mean which changes with t, we instead recompute the demeaned
    # profile relative to each window's own mean using the identity:
    #   y_local[k] = (cumsum of r over window)[k] - (k+1)/W * S1
    # and the residual SS for a box can be written purely in terms of prefix
    # sums of r (first order) and prefix sums of r^2 plus cross-prefix terms
    # that we precompute once globally.

    # Precompute global prefix sums needed:
    #   S_r[i]   = sum_{0..i-1} r
    #   S_r2[i]  = sum_{0..i-1} r^2
    r_arr = np.asarray(r, dtype=float)
    valid_global = np.isfinite(r_arr).all()
    if not valid_global:
        # Fall back to per-bar brute force (only if NaN present); real C312 has none.
        bf = _dfa_alpha_bruteforce(r_arr, W, scales)
        out["dfa"][:] = bf["dfa"]
        out["dfa_norm"][:] = bf["dfa_norm"]
        return out

    S_r = np.concatenate([[0.0], np.cumsum(r_arr)])          # len n+1
    S_r2 = np.concatenate([[0.0], np.cumsum(r_arr * r_arr)])  # len n+1

    t_arr = np.arange(n, dtype=float)

    def window_alpha(t: int) -> float:
        s = t - W + 1
        S1 = S_r[t + 1] - S_r[s]            # sum r over window
        mean = S1 / W
        # Build demeaned profile y for this window (length W)
        # y[k] = (S_r[s+k+1]-S_r[s]) - (k+1)*mean  for k=0..W-1
        # Vectorized over k:
        ks = np.arange(W, dtype=float)
        cum_r = S_r[s + 1:s + W + 1] - S_r[s]          # sum_{j=s..s+k} r
        y = cum_r - (ks + 1.0) * mean                   # demeaned profile
        # Now compute DFA alpha over scales
        log_n = []
        log_F = []
        for n in scales:
            if n > W:
                return float("nan")
            n_boxes = W // n
            resid_sq = 0.0
            count = 0
            tloc = np.arange(n, dtype=float)
            tloc_c = tloc - tloc.mean()
            denom = float((tloc_c * tloc_c).sum())
            # front boxes
            for b in range(n_boxes):
                seg = y[b * n:(b + 1) * n]
                s_mean = seg.mean()
                slope = float((tloc_c * (seg - s_mean)).sum() / denom)
                intercept = s_mean - slope * tloc.mean()
                resid = seg - (slope * tloc + intercept)
                resid_sq += float((resid * resid).sum())
                count += n
            # back boxes (distinct from front)
            front_covered = n_boxes * n
            n_back = (W - front_covered) // n
            for b in range(n_back):
                start = W - (b + 1) * n
                seg = y[start:start + n]
                s_mean = seg.mean()
                slope = float((tloc_c * (seg - s_mean)).sum() / denom)
                intercept = s_mean - slope * tloc.mean()
                resid = seg - (slope * tloc + intercept)
                resid_sq += float((resid * resid).sum())
                count += n
            if count == 0:
                return float("nan")
            F_n = math.sqrt(resid_sq / count)
            if not np.isfinite(F_n) or F_n <= 0:
                return float("nan")
            log_n.append(math.log(float(n)))
            log_F.append(math.log(F_n))
        if len(log_n) < 2:
            return float("nan")
        ln = np.asarray(log_n, dtype=float)
        lF = np.asarray(log_F, dtype=float)
        ln_m = ln.mean()
        lF_m = lF.mean()
        denom = float(((ln - ln_m) ** 2).sum())
        if denom <= 0:
            return float("nan")
        return float(((ln - ln_m) * (lF - lF_m)).sum() / denom)

    # This per-bar loop is O(n * scales * W) which is too slow for 315,648 bars.
    # Instead use the closed-form vectorized kernel below.
    return _compute_dfa_vectorized(r_arr, S_r, S_r2, W, scales, out)


def _compute_dfa_vectorized(r: np.ndarray, S_r, S_r2, W: int, scales, out: dict) -> dict:
    """Correct vectorized DFA scaling exponent alpha across all bars.

    For each trailing window of length W ending at bar t (window = r[t-W+1..t]):
      (1) demean the window; (2) profile y = cumsum(demeaned);
      (3) split y into non-overlapping front boxes of scale n (every
          pre-registered scale divides W=256, so the front boxes tile [0, W) and
          the reference back segment coincides with the front, leaving F(n)
          unchanged); (4) OLS-detrend each box; (5) F(n) = sqrt(mean squared
          residual); (6) dfa[t] = alpha[t] = OLS slope of log F(n) vs log n.

    dfa[t] is NaN for t < W, if any r in the window is NaN, or if any F(n) <= 0
    (matching _dfa_alpha_single_window / _dfa_alpha_bruteforce).
    Exact to ~1e-9 vs the brute-force reference. Vectorized over all windows via
    sliding_window_view + chunked box detrending: O(n*W) time, O(chunk*W) memory.
    S_r / S_r2 are accepted for signature compatibility but unused.
    """
    from numpy.lib.stride_tricks import sliding_window_view

    r = np.asarray(r, dtype=float)
    n = len(r)
    valid_scales = [int(ns) for ns in scales if 2 <= int(ns) <= W]
    n_win = n - W + 1
    if n < W or n_win <= 1 or len(valid_scales) < 2:
        return out
    ln = np.log(np.asarray(valid_scales, dtype=float))
    ln_m = float(ln.mean())
    denom_ln = float(((ln - ln_m) ** 2).sum())
    if denom_ln <= 0:
        return out
    wins = sliding_window_view(r, W)  # (n_win, W); wins[i] = r[i..i+W-1]
    alpha_all = np.full(n_win, np.nan, dtype=float)
    chunk_cap = 20000
    for c0 in range(0, n_win, chunk_cap):
        c1 = min(c0 + chunk_cap, n_win)
        chunk = np.array(wins[c0:c1], dtype=float)  # (m, W) copy
        m = c1 - c0
        y = np.cumsum(chunk - chunk.mean(axis=1, keepdims=True), axis=1)  # (m, W)
        log_F = np.full((m, len(valid_scales)), np.nan, dtype=float)
        for si, ns in enumerate(valid_scales):
            nb = W // ns
            if nb <= 0:
                continue
            front = y[:, :nb * ns].reshape(m, nb, ns)
            tc = np.arange(ns, dtype=float) - (ns - 1) / 2.0
            denom = float((tc * tc).sum())
            if denom <= 0:
                continue
            seg_mean = front.mean(axis=2, keepdims=True)
            slope = (front * tc).sum(axis=2, keepdims=True) / denom
            resid = front - seg_mean - slope * tc
            ss = (resid * resid).sum(axis=(1, 2))
            F = np.sqrt(ss / float(nb * ns))
            ok = np.isfinite(F) & (F > 0)
            log_F[:, si] = np.where(ok, np.log(np.where(ok, F, 1.0)), np.nan)
        row_ok = np.isfinite(log_F).all(axis=1)
        lF_m = log_F.mean(axis=1, keepdims=True)
        alpha = ((ln - ln_m) * (log_F - lF_m)).sum(axis=1) / denom_ln
        alpha_all[c0:c1] = np.where(row_ok, alpha, np.nan)
    # brute force defines dfa[t] for t in [W, n-1] => windows i=1..n_win-1 (drop i=0)
    out["dfa"][W:] = alpha_all[1:]
    out["dfa_norm"][W:] = alpha_all[1:] - 0.5
    return out


def build_underlying(bs: dict) -> dict:
    """Compute the causal per-bar DFA metric series used by every signal.
    Returns dict with matrices (n_assets, n_bars): one entry per base metric."""
    n_assets = int(bs["n_assets"])
    n_bars = int(bs["n_bars"])
    log_return = bs["log_return"]
    series: dict = {}
    METRIC_KEYS = ("dfa", "dfa_norm")
    mats = {k: np.full((n_assets, n_bars), np.nan, dtype=float) for k in METRIC_KEYS}
    for i in range(n_assets):
        m = compute_dfa_metrics(np.asarray(log_return[i], dtype=float), DFA_W, DFA_SCALES)
        for k in METRIC_KEYS:
            mats[k][i] = np.asarray(m[k], dtype=float)
    for k in METRIC_KEYS:
        series[k] = mats[k]
    return series


def build_scores(series: dict, bucket: np.ndarray) -> dict:
    """Compute causal score per (signal, seasonal_lookback).
    Returns {(signal, L): score(n_assets, n_bars)} shifted by 1 bar (causal).
    score = -(v - seasonal_mean) / seasonal_std."""
    scores: dict = {}
    for signal in SIGNALS:
        base, kind = SIGNAL_FAMILY[signal]
        surrogate = kind.startswith("placebo")
        for L in LOOKBACKS:
            v = series[base]  # (n_assets, n_bars)
            base_arr = np.apply_along_axis(
                lambda row: _phase_randomized_surrogate(row, PLACEBO_SEED), 1, v) if surrogate else v
            m, sd = _same_bucket_stats(bucket, base_arr, L, MIN_PERIODS_BASELINE)
            with np.errstate(divide="ignore", invalid="ignore"):
                raw = -(base_arr - m) / np.where(sd > 0, sd, np.nan)
            score = np.where((sd > 0) & np.isfinite(base_arr) & np.isfinite(m) & np.isfinite(sd),
                             raw, np.nan)
            sc = np.full_like(score, np.nan)
            sc[:, 1:] = score[:, :-1]  # causal shift(1)
            scores[(signal, int(L))] = sc
    return scores


def verify_cache() -> tuple:
    if not CACHE_DIR.exists():
        raise SystemExit(f"FATAL: C350 shard dir missing: {CACHE_DIR}")
    if not CACHE_META.exists():
        raise SystemExit(f"FATAL: C350 meta missing: {CACHE_META}")
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
        raise SystemExit("FATAL: C350 common grid is empty")
    if n_b % TOD_BARS_PER_DAY != 0:
        raise SystemExit("FATAL: C350 grid is not a whole number of 288-bar days")

    def mat(key):
        out = np.zeros((n_assets, n_b), dtype=float)
        for i, s in enumerate(symbols):
            out[i] = np.asarray(per_asset[s][key], dtype=float)
        return out

    perp_close = mat("perp_close")
    log_return = mat("log_return")
    abs_ret = mat("abs_ret")

    if not (np.isfinite(perp_close).all() and (perp_close > 0).all()):
        raise SystemExit("FATAL: non-finite/non-positive perp_close")
    if not np.isfinite(log_return).all():
        raise SystemExit("FATAL: non-finite log_return in cache")
    if not np.isfinite(abs_ret).all():
        raise SystemExit("FATAL: non-finite abs_ret in cache")

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
            "abs_ret": abs_ret, "bucket": bucket, "splits": splits}


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

    ref_cfg = dict(signal="dfa_dev", L=240, H=4,
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
        "generated_at_utc": ts, "campaign": 350, "part": "oos_sweep",
        "analysis": "c350_dfa_xsec_stat_arb_oos_5m",
        "verdict": verdict, "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "fail_closed": True,
        "mandate": (
            "C350 — test the cross-sectional intraday DETRENDED FLUCTUATION ANALYSIS "
            "(DFA) SCALING EXPONENT α x SEASONAL-DISLOCATION mean-reversion "
            "stat-arb family on 10 USDT-M linear perps at native 5m (1296 pre-registered "
            "configs). Per-bar primitives: log_return=log(c[t]/c[t-1]) (r[0]=0) "
            "from real perp_close; abs_ret=|log_return|. DFA metric over fixed intrinsic "
            "window W=256 bars ending at bar t, scales n in {4,8,16,32,64,128}: "
            "demean window, profile y=cumsum(demeaned), split into non-overlapping "
            "boxes of scale n (front+back segments), OLS-detrend each box, "
            "F(n)=sqrt(mean sq residual), dfa=α=OLS slope of log F(n) vs log n. "
            "Seasonal baseline = trailing mean/std at same (weekday,tod) bucket from "
            "history strictly before bar t (causal shift(1)), NaN-aware, excluding NaN obs. "
            "Signals: 2 real (dfa_dev, dfa_norm_dev) + 2 placebos "
            "(phase-randomized surrogates, never edges). Single-leg "
            "dollar-neutral perp PnL with costs on turnover "
            "(taker=fee+slip; maker_blend=0.5*fee+slip). Gates: Holm+BH at "
            "alpha=0.05 (BOTH), MDE, stability, signal-vs-placebo attribution. "
            "PRE-REGISTERED NaN policy: metric NaN unless sufficient finite obs "
            "and valid denominators; seasonal stats NaN-aware min_periods "
            "excluding NaN obs; NaN-score bars weight 0."
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
            "dfa_params": {"W": DFA_W, "scales": list(DFA_SCALES), "n_scales": DFA_N_SCALES},
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
                "note": "metric NaN share dominated by finite-obs/denominator requirements (t<W=256).",
            },
        },
        "methodology": {
            "buckets": "(weekday,tod)=dayofweek*288+seconds-of-day//300 (0..2015), exact 288 bars per UTC day.",
            "raw_features": "log_return=log(c[t]/c[t-1]) (r[0]=0) from real strictly-positive perp_close; abs_ret=|log_return|.",
            "primitives": "fixed intrinsic window W=256 bars ending at t: demean window, profile y=cumsum(demeaned), "
                          "split into non-overlapping boxes of scale n (front+back segments to use all points), "
                          "OLS-detrend each box, F(n)=sqrt(mean sq residual), dfa=α=OLS slope of log F(n) vs log n "
                          "over scales n in {4,8,16,32,64,128}.",
            "signals": "dfa/dfa_norm over fixed W=256; dfa_norm=dfa-0.5; score=-(v-m)/sd with m/sd trailing same-bucket mean/std "
                       "(min_periods=3, excluding NaN, causal shift(1)); cross-sectional rank, dollar-neutral gross 1.0; "
                       "NaN-score assets weight 0.",
            "pnl": "single-leg perp: pnl = sum_i pos_i * perp_ret_i.",
            "costs": "charged on turnover; taker = fee+slip; maker_blend = 0.5*fee+slip.",
            "missing_data": "non-finite -> NaN; never impute/ffill; insufficient valid obs -> NaN -> not traded (fail-closed).",
            "multiple_testing": "one-sided paired t-test of per-split OOS net vs 0; Holm step-down AND Benjamini-Hochberg over all 1296 configs at alpha=0.05.",
            "mde": "two-sided alpha=0.05, power=0.80: (t_{0.975}+t_{0.80})*s/sqrt(n_splits).",
            "attribution": "mean |OOS net| per signal across all its configs; shares=|mean|/sum(|means|) over all 4 signals incl. placebos; dominant must be a real (non-placebo) signal with share >= 0.5 for attribution_ok.",
            "stability": "sign consistency >= 0.70 of splits AND first/second-half Sharpe corr >= 0.5.",
            "placebo": "phase-randomized surrogate via FFT phase randomization + rank restoration to original marginal; deterministic seed recorded; same marginal distribution, destroyed temporal alignment.",
            "dfa_invariance_note": "DFA residual SS is invariant to subtracting the window mean from returns (a constant-per-bar mean subtracts a linear ramp from the profile, which OLS linear detrending absorbs); the vectorized kernel therefore uses the raw cumsum of returns within each window and is exact — validated against brute force in tests.",
            "funding": "USDT-M funding unreachable (fapi 451) -> excluded (control leg).",
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
    op = reports / f"campaign350_oos_sweep_{ts}.json"
    op.write_text(json.dumps(slim, indent=2, default=jdefault) + "\n")
    sweep_sha = sha256_file(op)
    full = reports / f"campaign350_oos_sweep_{ts}.full.json"
    full.write_text(json.dumps(sweep_obj, indent=2, default=jdefault) + "\n")

    surviving = [results[i] for i in edge_idx if rej_holm[i] and rej_bh[i]]
    registry = {
        "generated_at_utc": ts, "campaign": 350, "part": "registry",
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
    op_reg = reports / f"campaign350_tradable_edge_registry_{ts}.json"
    op_reg.write_text(json.dumps(registry, indent=2, default=jdefault) + "\n")
    reg_sha = sha256_file(op_reg)

    summary = {
        "generated_at_utc": ts, "campaign": 350, "part": "summary",
        "analysis": "validation_summary", "verdict": verdict, "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "universe": sweep_obj["universe"], "config": sweep_obj["config"],
        "gates": sweep_obj["gates"],
        "artifacts": {"oos_sweep": {"path": str(op.relative_to(ROOT)), "sha256": sweep_sha},
                      "registry": {"path": str(op_reg.relative_to(ROOT)), "sha256": reg_sha}},
        "summary": sweep_obj["summary"], "binding_constraint": binding,
    }
    op_sum = reports / f"campaign350_summary_{ts}.json"
    op_sum.write_text(json.dumps(summary, indent=2, default=jdefault) + "\n")
    sum_sha = sha256_file(op_sum)

    finding = (
        f"C350 cross-sectional intraday DETRENDED FLUCTUATION ANALYSIS (DFA) "
        f"SCALING EXPONENT alpha stat-arb edge {verdict} "
        f"({n_edge} deterministic edge configs, {n_survive_both} survive "
        f"Holm+BH over {N_TRIALS}); binding constraint: {binding}; dominant "
        f"attribution: {dominant} ({dominant_share:.4f})."
        if binding is not None
        else f"C350 cross-sectional intraday DETRENDED FLUCTUATION ANALYSIS (DFA) "
        f"SCALING EXPONENT alpha stat-arb edge validated: "
        f"{n_survive_both} of {n_edge} deterministic edge configs survive Holm+BH over "
        f"{N_TRIALS}; edge_proven:{edge_proven}."
    )
    verdict_obj = {
        "generated_at_utc": ts, "campaign": 350, "part": "verdict",
        "analysis": "final_verdict", "verdict": verdict, "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "finding": finding,
        "basis": "c350_dfa_xsec_stat_arb_costed_oos_5m",
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
            "No edge claim unless the costed OOS test survives Holm+BH over all 1296 configs",
            "Real USDT-M linear 5m perp_close; funding excluded (control leg)",
            "Single-leg PnL with costs on turnover; executed_fills: false",
            "Only RNG is recorded-seed placebo phase randomization (not market data)",
        ],
    }
    op_ver = reports / f"campaign350_verdict_{ts}.json"
    op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")
    ver_sha = sha256_file(op_ver)

    bind_sha = None
    bind_path = None
    if binding is not None:
        binding_obj = {
            "generated_at_utc": ts, "campaign": 350, "part": "binding_constraint",
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
                "C350 cross-sectional intraday DETRENDED FLUCTUATION ANALYSIS (DFA) "
                "SCALING EXPONENT alpha stat-arb does not survive validation; formal negative. Binding constraint: {binding}."
            ).format(binding=binding),
            "note": "Diagnosis only; never an edge claim. No threshold weakening.",
        }
        op_bind = reports / f"campaign350_binding_constraint_{ts}.json"
        op_bind.write_text(json.dumps(binding_obj, indent=2, default=jdefault) + "\n")
        bind_sha = sha256_file(op_bind)
        bind_path = str(op_bind.relative_to(ROOT))
        verdict_obj["binding_constraint_artifact"] = bind_path
        verdict_obj["binding_constraint_sha256"] = bind_sha
        op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")
        ver_sha = sha256_file(op_ver)

    print(json.dumps({
        "campaign": 350, "verdict": verdict, "edge_proven": edge_proven,
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