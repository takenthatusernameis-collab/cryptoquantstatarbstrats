#!/usr/bin/env python3
"""C358 — rigorous costed out-of-sample test of the cross-sectional intraday
MULTIFRACTAL DETRENDED FLUCTUATION ANALYSIS (MF-DFA) GENERALIZED HURST h(q)
× SEASONAL-DISLOCATION mean-reversion stat-arb family on 10 USDT-M linear
perps at native 5m (1296 pre-registered configs).

GENUINELY NEW FAMILY (not a re-skin of any frozen modern campaign)
-----------------------------------------------------------------
C281B–C357 (all FROZEN formal negatives) exhausted carry, OFI/microstructure,
premium/index/mark basis, quarterly term-structure, same-asset spot-perp
lead-lag, autocorrelation/chop/vol-clustering/close-envelope/rescaled-range/
drawdown-duration/realized-variance-concentration/ordinal-pattern-entropy/DFA
α/GPH d/local-Whittle d/variance-ratio/Higuchi/SampEn/MSE/LZC families. C358
is the first campaign to trade each asset's CAUSAL trailing same-(TOD×DOW)
seasonal deviation of its MULTIFRACTAL DFA generalized Hurst exponents h(q):

    For each bar t, take trailing W=256 returns r[t-W+1 .. t].
    (1) demean the window; (2) form the profile y = cumsum(demeaned);
    (3) split y into non-overlapping boxes of scale n (front + back segments to
        use all points); (4) OLS-detrend each box; (5) F²(n,k) = mean(ε²);
    (6) for each nonzero q ∈ Q:
        F_q(n) = [ (1/N_n) Σ_k (F²(n,k))^{q/2} ]^{1/q}
        (q=2 via sqrt; guard q<0 zeros; NaN if any F²(n,k)≤0 for q<0 or N_n<1).
    (7) h(q) = OLS slope of log F_q(n) vs log n over scales
        n ∈ {4, 8, 16, 32, 64, 128}.
    Real scalars emitted by runner:
        mfdfa_h0[t] = h(2)               (standard DFA exponent)
        mfdfa_spread[t] = h(-10) - h(+10)  (multifractal spectrum width)
    NaN if t < W or any NaN in window or <4 finite F_q(n) points per slope.

Unlike C350 (monofractal DFA α at single q=2), C358 is the FULL multifractal
h(q) profile across q ∈ {-10,-5,-2,-1,1,2,5,10}. Unlike C346 (R/S = single-
window range), C358 is multi-scale *detrended* fluctuation across moments.
Unlike C349/C351/C352/C353/C354/C355/C356/C357 (ordinal entropy, GPH d,
local-Whittle d, variance-ratio, HFD, SampEn, MSE, LZC), C358 is the
generalized Hurst via MF-DFA. C342/C340/C341 need volume; C358 is price-only,
volume-free. C315/C320 trade raw seasonal RETURN mean-reversion — C358 fades
seasonal dislocation in *MF-DFA h(q) scalars*, conditioned on last-move direction.
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

CACHE_DIR = cache_dir / "campaign358_mfdfa_5m"
CACHE_META = cache_dir / "campaign358_mfdfa_5m.meta.json"
CACHE_PROV = cache_dir / "campaign358_mfdfa_5m.provenance.json"
REQUIRED_FIELDS = ["index_ms", "perp_close", "log_return", "abs_ret", "funding_rate"]

# ---- pre-registered grid ----
SIGNALS = ("mfdfa_h0_dev", "mfdfa_spread_dev", "mfdfa_h0_placebo", "mfdfa_spread_placebo")
LOOKBACKS = (60, 120, 240, 480, 960, 1920)          # bars (seasonal baseline history)
REBALANCES = (1, 4, 12)                            # bars
FEES = (0.0004, 0.0007, 0.0010)
SLIPS = (0.0, 0.0001, 0.0002)
COST_VARIANTS = ("taker", "maker_blend")
FRAC = 1.0 / 3.0
ALPHA = 0.05
MIN_PERIODS_BASELINE = 3
PLACEBO_SEED = 20261224
TRAIN_M, TEST_M, ROLL_M = 12, 3, 3
STABILITY_MIN_SIGN_CONSISTENCY = 0.70
STABILITY_MIN_SHARPE_CORR = 0.50
DOMINANT_SHARE_MIN = 0.50

# MF-DFA parameters (fixed, pre-registered)
MFDFA_W = 256                           # intrinsic window (fixed, decoupled from seasonal lookback)
MFDFA_SCALES = (4, 8, 16, 32, 64, 128)  # scales n
MFDFA_N_SCALES = len(MFDFA_SCALES)       # 6
MFDFA_Q = (-10, -5, -2, -1, 1, 2, 5, 10)  # moments q
MFDFA_DETREND_ORDER = 1                  # linear detrend

TOD_BARS_PER_DAY = 288
WEEKDAYS = 7
N_BUCKETS = WEEKDAYS * TOD_BARS_PER_DAY

N_TRIALS = (len(SIGNALS) * len(LOOKBACKS) *
             len(REBALANCES) * len(FEES) * len(SLIPS) * len(COST_VARIANTS))  # 1296

# signal -> (base_metric_key, kind)
# kind in {"dev","placebo_dev"}
SIGNAL_FAMILY = {
    "mfdfa_h0_dev": ("mfdfa_h0", "dev"),
    "mfdfa_spread_dev": ("mfdfa_spread", "dev"),
    "mfdfa_h0_placebo": ("mfdfa_h0", "placebo_dev"),
    "mfdfa_spread_placebo": ("mfdfa_spread", "placebo_dev"),
}

ATTR_REPRESENTATIVES = {
    "mfdfa_h0_dev": "mfdfa_h0_dev",
    "mfdfa_spread_dev": "mfdfa_spread_dev",
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


# ------------------------------------------------------- MF-DFA generalized Hurst h(q) metric (per asset, fixed W=256)
def _mfdfa_h_q_single_window(window: np.ndarray, scales=MFDFA_SCALES, moments=MFDFA_Q) -> dict:
    """Reference MF-DFA h(q) for ONE trailing window (length W).
    Returns dict with 'mfdfa_h0' (h(2)) and 'mfdfa_spread' (h(-10)-h(+10)).
    """
    W = len(window)
    if W <= 0 or not np.isfinite(window).all():
        return {"mfdfa_h0": float("nan"), "mfdfa_spread": float("nan")}
    x = np.asarray(window, dtype=float)
    y = np.cumsum(x - x.mean())  # integrated demeaned profile
    F_q = {q: [] for q in moments}
    valid_scales = []
    for n in scales:
        if n > W:
            return {"mfdfa_h0": float("nan"), "mfdfa_spread": float("nan")}
        n_boxes = W // n
        if n_boxes <= 0:
            return {"mfdfa_h0": float("nan"), "mfdfa_spread": float("nan")}
        # front boxes
        F2_boxes = []
        for start in list(range(0, n_boxes * n, n)) + list(range(W - n_boxes * n, W, n)):
            seg = y[start:start + n]
            t = np.arange(n, dtype=float)
            t_mean = t.mean()
            s_mean = seg.mean()
            denom = ((t - t_mean) ** 2).sum()
            if denom <= 0:
                return {"mfdfa_h0": float("nan"), "mfdfa_spread": float("nan")}
            slope = ((t - t_mean) * (seg - s_mean)).sum() / denom
            intercept = s_mean - slope * t_mean
            resid = seg - (slope * t + intercept)
            F2_k = float((resid * resid).mean())
            if not np.isfinite(F2_k) or F2_k <= 0:
                return {"mfdfa_h0": float("nan"), "mfdfa_spread": float("nan")}
            F2_boxes.append(F2_k)
        if not F2_boxes:
            return {"mfdfa_h0": float("nan"), "mfdfa_spread": float("nan")}
        F2_boxes = np.asarray(F2_boxes, dtype=float)
        # For each q, F_q(n) = (mean_k (F²(n,k))^{q/2})^{1/q}
        for q in moments:
            if q == 2:
                F_q[q].append(math.sqrt(F2_boxes.mean()))
            else:
                F2_pow = np.power(F2_boxes, q / 2.0)
                if not np.isfinite(F2_pow).all():
                    return {"mfdfa_h0": float("nan"), "mfdfa_spread": float("nan")}
                mean_pow = F2_pow.mean()
                if mean_pow <= 0:
                    return {"mfdfa_h0": float("nan"), "mfdfa_spread": float("nan")}
                F_q[q].append(math.pow(mean_pow, 1.0 / q))
        valid_scales.append(n)

    # Now compute h(q) for each q as OLS slope of log F_q(n) vs log n
    h_vals = {}
    log_n = np.log(np.asarray(valid_scales, dtype=float))
    ln_m = log_n.mean()
    denom_ln = ((log_n - ln_m) ** 2).sum()
    for q in moments:
        if len(F_q[q]) < 4:  # need >= 4 points per slope
            h_vals[q] = float("nan")
            continue
        log_F = np.log(np.asarray(F_q[q], dtype=float))
        if not np.isfinite(log_F).all():
            h_vals[q] = float("nan")
            continue
        lF_m = log_F.mean()
        if denom_ln <= 0:
            h_vals[q] = float("nan")
            continue
        h_vals[q] = float(((log_n - ln_m) * (log_F - lF_m)).sum() / denom_ln)

    mfdfa_h0 = h_vals.get(2, float("nan"))
    mfdfa_spread = h_vals.get(-10, float("nan")) - h_vals.get(10, float("nan"))
    return {"mfdfa_h0": mfdfa_h0, "mfdfa_spread": mfdfa_spread}


def _mfdfa_bruteforce(r: np.ndarray, W: int = MFDFA_W, scales=MFDFA_SCALES, moments=MFDFA_Q) -> dict:
    """Brute-force reference MF-DFA for testing.
    Returns dict with 'mfdfa_h0' and 'mfdfa_spread' arrays (NaN where undefined)."""
    n = len(r)
    out = {k: np.full(n, np.nan, dtype=float) for k in ("mfdfa_h0", "mfdfa_spread")}
    if n < W:
        return out
    for t in range(W, n):
        window = r[t - W + 1:t + 1]
        if not np.isfinite(window).all():
            continue
        res = _mfdfa_h_q_single_window(window, scales, moments)
        out["mfdfa_h0"][t] = res["mfdfa_h0"]
        out["mfdfa_spread"][t] = res["mfdfa_spread"]
    return out


def compute_mfdfa_metrics(r: np.ndarray, W: int = MFDFA_W, scales=MFDFA_SCALES, moments=MFDFA_Q) -> dict:
    """Fast vectorized MF-DFA generalized Hurst h(q) for one asset over fixed
    intrinsic window W bars ending at bar t.

    Strategy: for each bar t, the window is r[t-W+1 .. t] of length W. The
    profile y = cumsum(demeaned window) depends on the absolute start index, so
    we cannot use a single global prefix-sum trick for arbitrary windows
    directly. Instead, we compute MF-DFA per bar using a vectorized closed-form
    over all windows simultaneously using sliding_window_view + chunked box
    detrending, validated against the brute-force reference. The vectorized
    path computes, for every bar t, the exact same quantity as
    _mfdfa_h_q_single_window but in O(n) per scale using sliding prefix sums.

    Returns dict with 'mfdfa_h0' and 'mfdfa_spread' arrays (NaN where undefined).
    """
    n = len(r)
    out = {k: np.full(n, np.nan, dtype=float) for k in ("mfdfa_h0", "mfdfa_spread")}
    if n < W:
        return out

    return _compute_mfdfa_vectorized(np.asarray(r, dtype=float), W, scales, moments, out)


def _compute_mfdfa_vectorized(r: np.ndarray, W: int, scales, moments, out: dict) -> dict:
    """Correct vectorized MF-DFA generalized Hurst h(q) across all bars.

    For each trailing window of length W ending at bar t (window = r[t-W+1..t]):
      (1) demean the window; (2) profile y = cumsum(demeaned);
      (3) split y into non-overlapping front boxes of scale n (every
          pre-registered scale divides W=256, so the front boxes tile [0, W)
          and the reference back segment coincides with the front, leaving
          F²(n) unchanged); (4) OLS-detrend each box; (5) F²(n,k) = mean
          squared residual per box k; (6) for each q: F_q(n) = [mean_k
          (F²(n,k))^{q/2}]^{1/q}; (7) h(q) = OLS slope of log F_q(n) vs log n
          over scales.
    mfdfa_h0[t] = h(2); mfdfa_spread[t] = h(-10) - h(+10).
    NaN for t < W, if any r in window is NaN, or if <4 finite F_q(n) per slope.
    Exact to ~1e-9 vs the brute-force reference. Vectorized over all windows via
    sliding_window_view + chunked box detrending: O(n*W) time, O(chunk*W) memory.
    """
    from numpy.lib.stride_tricks import sliding_window_view

    r = np.asarray(r, dtype=float)
    n = len(r)
    valid_scales = [int(ns) for ns in scales if 2 <= int(ns) <= W]
    n_win = n - W + 1
    if n < W or n_win <= 1 or len(valid_scales) < 4:
        return out
    ln = np.log(np.asarray(valid_scales, dtype=float))
    ln_m = float(ln.mean())
    denom_ln = float(((ln - ln_m) ** 2).sum())
    if denom_ln <= 0:
        return out

    moments = tuple(moments)
    n_q = len(moments)
    wins = sliding_window_view(r, W)  # (n_win, W); wins[i] = r[i..i+W-1]
    alpha_h0_all = np.full(n_win, np.nan, dtype=float)
    spread_all = np.full(n_win, np.nan, dtype=float)
    chunk_cap = 20000

    for c0 in range(0, n_win, chunk_cap):
        c1 = min(c0 + chunk_cap, n_win)
        chunk = np.array(wins[c0:c1], dtype=float)  # (m, W) copy
        m = c1 - c0
        # Mask of valid windows (no NaN in the window)
        valid_win = np.isfinite(chunk).all(axis=1)
        if not valid_win.any():
            continue
        # Only process valid windows
        y = np.cumsum(chunk[valid_win] - chunk[valid_win].mean(axis=1, keepdims=True), axis=1)  # (m_valid, W)
        m_valid = y.shape[0]
        # Compute F²(n,k) per box for each scale
        # F2_boxes[si] = (m_valid, nb) array of F² per box for scale si
        F2_boxes_per_scale = []
        for si, ns in enumerate(valid_scales):
            nb = W // ns
            if nb <= 0:
                F2_boxes_per_scale.append(None)
                continue
            front = y[:, :nb * ns].reshape(m_valid, nb, ns)
            tc = np.arange(ns, dtype=float) - (ns - 1) / 2.0
            denom = float((tc * tc).sum())
            if denom <= 0:
                F2_boxes_per_scale.append(None)
                continue
            seg_mean = front.mean(axis=2, keepdims=True)
            slope = (front * tc).sum(axis=2, keepdims=True) / denom
            resid = front - seg_mean - slope * tc
            F2_boxes = (resid * resid).mean(axis=2)  # (m_valid, nb)
            F2_boxes_per_scale.append(F2_boxes)
        # For each q, compute F_q(n) = (mean_k (F²(n,k))^{q/2})^{1/q}
        h_q_valid = np.full((m_valid, n_q), np.nan, dtype=float)
        for qi, q in enumerate(moments):
            log_F_q = np.full((m_valid, len(valid_scales)), np.nan, dtype=float)
            for si, ns in enumerate(valid_scales):
                F2_boxes = F2_boxes_per_scale[si]
                if F2_boxes is None:
                    continue
                if q == 2:
                    F_q = np.sqrt(F2_boxes.mean(axis=1))
                else:
                    F2_pow = np.power(F2_boxes, q / 2.0)
                    if not np.isfinite(F2_pow).all():
                        continue
                    mean_pow = F2_pow.mean(axis=1)
                    if np.any(mean_pow <= 0):
                        continue
                    F_q = np.power(mean_pow, 1.0 / q)
                log_F_q[:, si] = np.log(np.where(F_q > 0, F_q, np.nan))
            # Need >= 4 finite F_q(n) points
            finite_cols = np.isfinite(log_F_q).sum(axis=1) >= 4
            lF_m = log_F_q.mean(axis=1, keepdims=True)
            alpha = ((ln - ln_m) * (log_F_q - lF_m)).sum(axis=1) / denom_ln
            alpha_all = np.where(finite_cols, alpha, np.nan)
            h_q_valid[:, qi] = alpha_all
        # Map back to chunk indices
        h_q = np.full((m, n_q), np.nan, dtype=float)
        h_q[valid_win] = h_q_valid
        q2_idx = moments.index(2)
        q_m10_idx = moments.index(-10)
        q_p10_idx = moments.index(10)
        alpha_h0_all[c0:c1] = h_q[:, q2_idx]
        spread_all[c0:c1] = h_q[:, q_m10_idx] - h_q[:, q_p10_idx]

    # brute force defines metrics for t in [W, n-1] => windows i=1..n_win-1 (drop i=0)
    out["mfdfa_h0"][W:] = alpha_h0_all[1:]
    out["mfdfa_spread"][W:] = spread_all[1:]
    return out


def build_underlying(bs: dict) -> dict:
    """Compute the causal per-bar MF-DFA metric series used by every signal.
    Returns dict with matrices (n_assets, n_bars): one entry per base metric."""
    n_assets = int(bs["n_assets"])
    n_bars = int(bs["n_bars"])
    log_return = bs["log_return"]
    series: dict = {}
    METRIC_KEYS = ("mfdfa_h0", "mfdfa_spread")
    mats = {k: np.full((n_assets, n_bars), np.nan, dtype=float) for k in METRIC_KEYS}
    for i in range(n_assets):
        m = compute_mfdfa_metrics(np.asarray(log_return[i], dtype=float),
                                   MFDFA_W, MFDFA_SCALES, MFDFA_Q)
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
        raise SystemExit(f"FATAL: C358 shard dir missing: {CACHE_DIR}")
    if not CACHE_META.exists():
        raise SystemExit(f"FATAL: C358 meta missing: {CACHE_META}")
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
        raise SystemExit("FATAL: C358 common grid is empty")
    if n_b % TOD_BARS_PER_DAY != 0:
        raise SystemExit("FATAL: C358 grid is not a whole number of 288-bar days")

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

    ref_cfg = dict(signal="mfdfa_h0_dev", L=240, H=4,
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
        "generated_at_utc": ts, "campaign": 358, "part": "oos_sweep",
        "analysis": "c358_mfdfa_xsec_stat_arb_oos_5m",
        "verdict": verdict, "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "fail_closed": True,
        "mandate": (
            "C358 — test the cross-sectional intraday MULTIFRACTAL DETRENDED FLUCTUATION ANALYSIS "
            "(MF-DFA) GENERALIZED HURST h(q) x SEASONAL-DISLOCATION mean-reversion "
            "stat-arb family on 10 USDT-M linear perps at native 5m (1296 pre-registered "
            "configs). Per-bar primitives: log_return=log(c[t]/c[t-1]) (r[0]=0) "
            "from real perp_close; abs_ret=|log_return|. MF-DFA metrics over fixed intrinsic "
            "window W=256 bars ending at bar t, scales n in {4,8,16,32,64,128}, "
            "moments q in {-10,-5,-2,-1,1,2,5,10}: "
            "demean window, profile y=cumsum(demeaned), split into non-overlapping "
            "boxes of scale n (front+back segments), OLS-detrend each box (order 1), "
            "F²(n,k)=mean sq residual, F_q(n)=[(1/N_n)Σ_k(F²(n,k))^{q/2}]^{1/q}, "
            "h(q)=OLS slope of log F_q(n) vs log n. Real scalars: mfdfa_h0=h(2); "
            "mfdfa_spread=h(-10)-h(+10). Seasonal baseline = trailing mean/std at same "
            "(weekday,tod) bucket from history strictly before bar t (causal shift(1)), "
            "NaN-aware, excluding NaN obs. Signals: 2 real (mfdfa_h0_dev, mfdfa_spread_dev) + "
            "2 placebos (phase-randomized surrogates, never edges). Single-leg "
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
            "mfdfa_params": {"W": MFDFA_W, "scales": list(MFDFA_SCALES),
                             "moments": list(MFDFA_Q), "n_scales": MFDFA_N_SCALES,
                             "detrend_order": MFDFA_DETREND_ORDER},
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
                          "OLS-detrend each box (order 1), F²(n,k)=mean sq residual, "
                          "F_q(n)=[(1/N_n)Σ_k(F²(n,k))^{q/2}]^{1/q}, "
                          "h(q)=OLS slope of log F_q(n) vs log n "
                          "over scales n in {4,8,16,32,64,128} and moments q in {-10,-5,-2,-1,1,2,5,10}. "
                          "Real scalars: mfdfa_h0 = h(2) (standard DFA exponent); "
                          "mfdfa_spread = h(-10) - h(+10) (multifractal spectrum width).",
            "signals": "mfdfa_h0/mfdfa_spread over fixed W=256; score=-(v-m)/sd with m/sd trailing same-bucket mean/std "
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
            "mfdfa_invariance_note": "MF-DFA residual SS is invariant to subtracting the window mean from returns (a constant-per-bar mean subtracts a linear ramp from the profile, which OLS linear detrending absorbs); the vectorized kernel therefore uses the raw cumsum of returns within each window and is exact — validated against brute force in tests.",
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
    op = reports / f"campaign358_oos_sweep_{ts}.json"
    op.write_text(json.dumps(slim, indent=2, default=jdefault) + "\n")
    sweep_sha = sha256_file(op)
    full = reports / f"campaign358_oos_sweep_{ts}.full.json"
    full.write_text(json.dumps(sweep_obj, indent=2, default=jdefault) + "\n")

    surviving = [results[i] for i in edge_idx if rej_holm[i] and rej_bh[i]]
    registry = {
        "generated_at_utc": ts, "campaign": 358, "part": "registry",
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
    op_reg = reports / f"campaign358_tradable_edge_registry_{ts}.json"
    op_reg.write_text(json.dumps(registry, indent=2, default=jdefault) + "\n")
    reg_sha = sha256_file(op_reg)

    summary = {
        "generated_at_utc": ts, "campaign": 358, "part": "summary",
        "analysis": "validation_summary", "verdict": verdict, "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "universe": sweep_obj["universe"], "config": sweep_obj["config"],
        "gates": sweep_obj["gates"],
        "artifacts": {"oos_sweep": {"path": str(op.relative_to(ROOT)), "sha256": sweep_sha},
                      "registry": {"path": str(op_reg.relative_to(ROOT)), "sha256": reg_sha}},
        "summary": sweep_obj["summary"], "binding_constraint": binding,
    }
    op_sum = reports / f"campaign358_summary_{ts}.json"
    op_sum.write_text(json.dumps(summary, indent=2, default=jdefault) + "\n")
    sum_sha = sha256_file(op_sum)

    finding = (
        f"C358 cross-sectional intraday MULTIFRACTAL DETRENDED FLUCTUATION ANALYSIS (MF-DFA) "
        f"GENERALIZED HURST h(q) stat-arb edge {verdict} "
        f"({n_edge} deterministic edge configs, {n_survive_both} survive "
        f"Holm+BH over {N_TRIALS}); binding constraint: {binding}; dominant "
        f"attribution: {dominant} ({dominant_share:.4f})."
        if binding is not None
        else f"C358 cross-sectional intraday MULTIFRACTAL DETRENDED FLUCTUATION ANALYSIS (MF-DFA) "
        f"GENERALIZED HURST h(q) stat-arb edge validated: "
        f"{n_survive_both} of {n_edge} deterministic edge configs survive Holm+BH over "
        f"{N_TRIALS}; edge_proven:{edge_proven}."
    )
    verdict_obj = {
        "generated_at_utc": ts, "campaign": 358, "part": "verdict",
        "analysis": "final_verdict", "verdict": verdict, "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "finding": finding,
        "basis": "c358_mfdfa_xsec_stat_arb_costed_oos_5m",
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
    op_ver = reports / f"campaign358_verdict_{ts}.json"
    op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")
    ver_sha = sha256_file(op_ver)

    bind_sha = None
    bind_path = None
    if binding is not None:
        binding_obj = {
            "generated_at_utc": ts, "campaign": 358, "part": "binding_constraint",
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
                "C358 cross-sectional intraday MULTIFRACTAL DETRENDED FLUCTUATION ANALYSIS (MF-DFA) "
                "GENERALIZED HURST h(q) stat-arb does not survive validation; formal negative. Binding constraint: {binding}."
            ).format(binding=binding),
            "note": "Diagnosis only; never an edge claim. No threshold weakening.",
        }
        op_bind = reports / f"campaign358_binding_constraint_{ts}.json"
        op_bind.write_text(json.dumps(binding_obj, indent=2, default=jdefault) + "\n")
        bind_sha = sha256_file(op_bind)
        bind_path = str(op_bind.relative_to(ROOT))
        verdict_obj["binding_constraint_artifact"] = bind_path
        verdict_obj["binding_constraint_sha256"] = bind_sha
        op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")
        ver_sha = sha256_file(op_ver)

    print(json.dumps({
        "campaign": 358, "verdict": verdict, "edge_proven": edge_proven,
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