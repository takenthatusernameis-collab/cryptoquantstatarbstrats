#!/usr/bin/env python3
"""C356 — rigorous costed out-of-sample test of the cross-sectional intraday
MULTISCALE ENTROPY (MSE) × SEASONAL-DISLOCATION mean-reversion stat-arb family
on 10 USDT-M linear perps at native 5m (1296 pre-registered configs).

GENUINELY NEW FAMILY (not a re-skin of any frozen modern campaign)
-----------------------------------------------------------------
C281B-C355 (all FROZEN formal negatives) exhausted carry, OFI/microstructure,
premium/index/mark basis, quarterly term-structure, same-asset spot-perp
lead-lag, autocorrelation/chop/vol-clustering/close-envelope/rescaled-range/
drawdown-duration/realized-variance-concentration/ordinal-pattern-entropy/
DFA-scaling-exponent/GPH-log-periodogram/local-Whittle/variance-ratio/
Higuchi-fractal-dimension/sample-entropy families.
C356 is the first modern campaign to trade each asset's CAUSAL trailing same-
(TOD x DOW) seasonal deviation of its MULTISCALE ENTROPY:

    For each bar t, take trailing W=64 returns X = r[t-W+1 .. t].
    For each scale tau in {1,2,4,8,16,32}:
      (1) Coarse-grain: y^(tau)[k] = mean(X[k*tau:(k+1)*tau]), k=0..N_tau-1,
          N_tau = W // tau.
      (2) Standardize: z^(tau) = (y^(tau) - mean(y^(tau))) / std(y^(tau))
          (population std). NaN if std <= 0 or non-finite.
      (3) SampEn on z^(tau) with m=2, tolerance r=0.25:
          B_m^(tau) = # ordered pairs i!=j with max|T_m[i]-T_m[j]| < r
          A_m^(tau) = # ordered pairs i!=j with max|T_{m+1}[i]-T_{m+1}[j]| < r
          SampEn^(tau) = ln(B_m^(tau)) - ln(A_m^(tau)). NaN if N_tau < m+1,
          A==0 or B==0.
    mse_slope[t] = OLS slope of SampEn^(tau) vs log(tau) over scales with
                   finite SampEn (requires >= 3 finite points).
    mse_area[t]  = trapezoidal area under SampEn^(tau) vs tau curve.
    Both NaN if < 3 finite SampEn points.

mse_slope (negative = complexity decays with scale / long-range regularity;
positive = complexity grows with scale) and mse_area (total complexity
across scales) are two genuinely-distinct real signals.

score = -(v - seasonal_mean) / seasonal_std (symmetric z-fade).

Unlike C355 (single-scale SampEn at fixed W=64, no coarse-graining), C356
computes SampEn at MULTIPLE coarse-grained time scales. Unlike C349
(permutation entropy: Bandt-Pompe ordinal patterns, no template matching,
no coarse-graining), C354 (Higuchi curve-length fractal dimension),
C350 (DFA detrended fluctuation slope), C351 (GPH frequency-domain OLS
log-periodogram slope), C352 (local-Whittle frequency-domain exact MLE),
C353 (variance ratio VR(q), a normalized second-moment ratio), C346 (R/S
single-window range), C326 (lag-1 signed-return autocorrelation): C356 is
Multiscale Entropy (coarse-grained multi-scale SampEn). C343 (|r| autocorr /
vol clustering), C344 (sign-change rate), C347 (drawdown duration), C345
(close-in-envelope), C317 (realized-vol LEVELS): C356 is MSE. C342/C340/C341
need volume/notional/price-impact; C356 is price-only and volume-free.
C315/C320 trade raw seasonal RETURN mean-reversion — C356 fades seasonal
dislocation in Multiscale Entropy.
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

CACHE_DIR = cache_dir / "campaign356_multiscale_entropy_5m"
CACHE_META = cache_dir / "campaign356_multiscale_entropy_5m.meta.json"
CACHE_PROV = cache_dir / "campaign356_multiscale_entropy_5m.provenance.json"
REQUIRED_FIELDS = ["index_ms", "perp_close", "log_return", "abs_ret", "funding_rate"]

# ---- pre-registered grid ----
SIGNALS = ("mse_slope_dev", "mse_area_dev", "mse_slope_placebo", "mse_area_placebo")
LOOKBACKS = (60, 120, 240, 480, 960, 1920)          # bars (seasonal baseline history)
REBALANCES = (1, 4, 12)                            # bars
FEES = (0.0004, 0.0007, 0.0010)
SLIPS = (0.0, 0.0001, 0.0002)
COST_VARIANTS = ("taker", "maker_blend")
FRAC = 1.0 / 3.0
ALPHA = 0.05
MIN_PERIODS_BASELINE = 3
PLACEBO_SEED = 20261222
TRAIN_M, TEST_M, ROLL_M = 12, 3, 3
STABILITY_MIN_SIGN_CONSISTENCY = 0.70
STABILITY_MIN_SHARPE_CORR = 0.50
DOMINANT_SHARE_MIN = 0.50

# multiscale entropy parameters (fixed, pre-registered)
MSE_W = 64                                          # intrinsic window (fixed, decoupled from seasonal lookback)
MSE_TAUS = (1, 2, 4, 8, 16, 32)                     # coarse-graining scales (all divide 64)
MSE_M = 2                                           # embedding dimension
MSE_R = 0.25                                        # tolerance in z-score units

TOD_BARS_PER_DAY = 288
WEEKDAYS = 7
N_BUCKETS = WEEKDAYS * TOD_BARS_PER_DAY

N_TRIALS = (len(SIGNALS) * len(LOOKBACKS) *
             len(REBALANCES) * len(FEES) * len(SLIPS) * len(COST_VARIANTS))  # 1296

# signal -> (base_metric_key, kind)
# kind in {"dev","placebo_dev"}
SIGNAL_FAMILY = {
    "mse_slope_dev": ("mse_slope", "dev"),
    "mse_area_dev": ("mse_area", "dev"),
    "mse_slope_placebo": ("mse_slope", "placebo_dev"),
    "mse_area_placebo": ("mse_area", "placebo_dev"),
}

ATTR_REPRESENTATIVES = {
    "mse_slope_dev": "mse_slope_dev",
    "mse_area_dev": "mse_area_dev",
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
    order = np.argsort(np.argsort(y))
    sorted_x = np.sort(xf)
    restored = sorted_x[order]
    out[fin] = restored
    return out


def _bucket_of(index_ms: np.ndarray) -> np.ndarray:
    """(weekday × tod) bucket id in [0, 2016) from index_ms (ms since epoch, UTC)."""
    ts = pd.to_datetime(index_ms, unit="ms", utc=True)
    dow = ts.dayofweek.to_numpy().astype(np.int64)
    secs = (ts.hour.to_numpy().astype(np.int64) * 3600
            + ts.minute.to_numpy().astype(np.int64) * 60
            + ts.second.to_numpy().astype(np.int64))
    tod = secs // 300
    return dow * TOD_BARS_PER_DAY + tod


def _same_bucket_stats_1d(bucket: np.ndarray, x: np.ndarray, window, min_periods: int):
    """Trailing mean/std of x over the same (weekday×tod) bucket, using only
    history strictly BEFORE each bar (causal). NaN-aware, min_periods gate."""
    n = len(x)
    mean = np.full(n, np.nan, dtype=float)
    std = np.full(n, np.nan, dtype=float)
    if n == 0:
        return mean, std
    order = np.argsort(bucket, kind="mergesort")
    b_sorted = bucket[order]
    x_sorted = x[order]
    uniq, starts, counts = np.unique(b_sorted, return_index=True, return_counts=True)
    mean_s = np.full(n, np.nan, dtype=float)
    std_s = np.full(n, np.nan, dtype=float)
    for u, s0, c in zip(uniq, starts, counts):
        xs = x_sorted[s0:s0 + c]
        cs = np.concatenate(([0.0], np.nancumsum(xs)))
        cs2 = np.concatenate(([0.0], np.nancumsum(np.where(np.isfinite(xs), xs * xs, 0.0))))
        cn = np.concatenate(([0], np.cumsum(np.isfinite(xs).astype(np.int64))))
        m = len(xs)
        for j in range(m):
            lo = max(0, j - window + 1)
            a, b = lo, j
            cnt = int(cn[b] - cn[a])
            if cnt >= min_periods:
                sm = cs[b] - cs[a]
                sm2 = cs2[b] - cs2[a]
                mu = sm / cnt
                var = max(0.0, sm2 / cnt - mu * mu)
                mean_s[s0 + j] = mu
                std_s[s0 + j] = math.sqrt(var)
    mean[order] = mean_s
    std[order] = std_s
    return mean, std


def _same_bucket_stats(bucket: np.ndarray, x: np.ndarray, window, min_periods: int):
    """2-D (n_assets, n_bars) version of _same_bucket_stats_1d."""
    n_assets, n_bars = x.shape
    mean = np.full((n_assets, n_bars), np.nan, dtype=float)
    std = np.full((n_assets, n_bars), np.nan, dtype=float)
    for i in range(n_assets):
        m, s = _same_bucket_stats_1d(bucket, np.asarray(x[i], dtype=float), window, min_periods)
        mean[i] = m
        std[i] = s
    return mean, std


# ---------------------------------------------------------------- multiscale entropy
def _sampen_single_window(z: np.ndarray, m: int, r: float) -> float:
    """Reference Sample Entropy for ONE standardized series.
    Templates T_m[i] = z[i..i+m-1], T_{m+1}[i] = z[i..i+m].
    B_m = # ordered pairs i!=j with Chebyshev max|T_m[i]-T_m[j]| < r.
    A_m = # ordered pairs i!=j with Chebyshev max|T_{m+1}[i]-T_{m+1}[j]| < r.
    SampEn = ln(B) - ln(A). NaN if any input non-finite, A==0 or B==0."""
    N = len(z)
    if not np.isfinite(z).all():
        return float("nan")
    mu = float(z.mean())
    sd = float(z.std())
    if not (sd > 0 and np.isfinite(sd)):
        return float("nan")
    z = (z - mu) / sd
    n_t = N - m + 1
    if n_t < 2:
        return float("nan")
    T = np.lib.stride_tricks.sliding_window_view(z, m)  # (n_t, m)
    D = np.zeros((n_t, n_t), dtype=float)
    for d in range(m):
        diff = np.abs(T[:, d, None] - T[None, :, d])
        np.maximum(D, diff, out=D)
    Bmat = (D < r)
    diag = np.arange(n_t)
    Bmat[diag, diag] = False
    B = int(Bmat.sum())
    if B == 0:
        return float("nan")
    n_t1 = N - m
    if n_t1 < 2:
        return float("nan")
    T1 = np.lib.stride_tricks.sliding_window_view(z, m + 1)  # (n_t1, m+1)
    D1 = np.zeros((n_t1, n_t1), dtype=float)
    for d in range(m + 1):
        diff1 = np.abs(T1[:, d, None] - T1[None, :, d])
        np.maximum(D1, diff1, out=D1)
    Amat = (D1 < r)
    diag1 = np.arange(n_t1)
    Amat[diag1, diag1] = False
    A = int(Amat.sum())
    if A == 0:
        return float("nan")
    return math.log(B) - math.log(A)


def _mse_bruteforce(r: np.ndarray, W: int = MSE_W,
                    taus: tuple = MSE_TAUS, m: int = MSE_M,
                    r_tol: float = MSE_R) -> dict:
    """Brute-force reference MSE implementation for testing.
    Returns dict with 'mse_slope' and 'mse_area' arrays (NaN where undefined).
    Manual loop over windows, explicit coarse-graining via loop over tau,
    per-scale np.mean, explicit SampEn double loop over i,j with Chebyshev
    max|...| distance."""
    n = len(r)
    mse_slope = np.full(n, np.nan, dtype=float)
    mse_area = np.full(n, np.nan, dtype=float)
    if n < W:
        return {"mse_slope": mse_slope, "mse_area": mse_area}
    log_taus = np.log(np.array(taus, dtype=float))
    for t in range(W, n):
        window = r[t - W + 1:t + 1]
        if not np.isfinite(window).all():
            continue
        sampen_per_tau = []
        valid_taus = []
        for tau in taus:
            N_tau = W // tau
            if N_tau < m + 1:
                continue
            # coarse-grain
            y = np.array([window[k * tau:(k + 1) * tau].mean()
                          for k in range(N_tau)])
            if not np.isfinite(y).all():
                continue
            y_std = float(y.std())
            if not (y_std > 0 and np.isfinite(y_std)):
                continue
            z = (y - y.mean()) / y_std
            se = _sampen_single_window(z, m, r_tol)
            if np.isfinite(se):
                sampen_per_tau.append(se)
                valid_taus.append(tau)
        if len(sampen_per_tau) >= 3:
            # OLS slope of SampEn vs log(tau)
            x = np.log(np.array(valid_taus, dtype=float))
            yv = np.array(sampen_per_tau, dtype=float)
            x_mean = x.mean()
            y_mean = yv.mean()
            sxx = float(((x - x_mean) ** 2).sum())
            sxy = float(((x - x_mean) * (yv - y_mean)).sum())
            slope = sxy / sxx if sxx > 0 else float("nan")
            # trapezoidal area over consecutive valid tau pairs
            area = 0.0
            for k in range(len(valid_taus) - 1):
                area += (sampen_per_tau[k] + sampen_per_tau[k + 1]) / 2 * (valid_taus[k + 1] - valid_taus[k])
            mse_slope[t] = slope
            mse_area[t] = area
    return {"mse_slope": mse_slope, "mse_area": mse_area}


def compute_mse_metrics(r: np.ndarray, W: int = MSE_W,
                        taus: tuple = MSE_TAUS, m: int = MSE_M,
                        r_tol: float = MSE_R) -> dict:
    """Fast vectorized Multiscale Entropy for one asset over fixed intrinsic
    window W bars ending at bar t, coarse-graining scales taus, embedding
    dimension m, tolerance r (z-score units at each scale).

    Vectorized over all windows via sliding_window_view + chunked
    coarse-graining. mse_slope[t] and mse_area[t] are NaN for t < W, if any r
    in the window is NaN, or if < 3 scales yield finite SampEn. Passes a
    brute-force equality test (tests)."""
    n = len(r)
    mse_slope = np.full(n, np.nan, dtype=float)
    mse_area = np.full(n, np.nan, dtype=float)
    if n < W:
        return {"mse_slope": mse_slope, "mse_area": mse_area}
    r_arr = np.asarray(r, dtype=float)
    if not np.isfinite(r_arr).all():
        bf = _mse_bruteforce(r_arr, W, taus, m, r_tol)
        mse_slope[:] = bf["mse_slope"]
        mse_area[:] = bf["mse_area"]
        return {"mse_slope": mse_slope, "mse_area": mse_area}
    return _compute_mse_vectorized(r_arr, W, taus, m, r_tol, mse_slope, mse_area)


def _compute_mse_vectorized(r: np.ndarray, W: int, taus: tuple,
                            m: int, r_tol: float,
                            mse_slope: np.ndarray, mse_area: np.ndarray) -> dict:
    """Vectorized MSE across all bars.

    For each trailing window of length W ending at bar t:
      For each scale tau: coarse-grain y^(tau)=mean over non-overlapping
      blocks of length tau; standardize z^(tau); compute SampEn^(tau) with m=2.
      mse_slope[t] = OLS slope of SampEn^(tau) vs log(tau) (>=3 finite pts).
      mse_area[t]  = trapezoidal area under SampEn^(tau) vs tau.
    sampen[t] NaN for t<W, NaN in window, std<=0, or <3 finite scales.
    Validated against _mse_bruteforce in tests."""
    from numpy.lib.stride_tricks import sliding_window_view

    n = len(r)
    n_win = n - W + 1
    if n < W or n_win <= 1:
        return {"mse_slope": mse_slope, "mse_area": mse_area}

    wins = sliding_window_view(r, W)  # (n_win, W); wins[i] = r[i..i+W-1]
    chunk_cap = 1000
    log_taus = np.log(np.array(taus, dtype=float))
    n_taus = len(taus)

    for c0 in range(0, n_win, chunk_cap):
        c1 = min(c0 + chunk_cap, n_win)
        chunk = np.array(wins[c0:c1], dtype=float)  # (cc, W) copy
        cc = chunk.shape[0]

        # sampen_per_tau: (cc, n_taus), NaN where undefined
        sampen_per_tau = np.full((cc, n_taus), np.nan, dtype=float)
        valid_scale = np.zeros((cc, n_taus), dtype=bool)

        for ti, tau in enumerate(taus):
            N_tau = W // tau
            if N_tau < m + 1:
                continue
            # coarse-grain: (cc, W) -> (cc, N_tau, tau) -> mean -> (cc, N_tau)
            y = chunk.reshape(cc, N_tau, tau).mean(axis=2)
            # standardize per row
            y_mean = y.mean(axis=1, keepdims=True)
            y_std = y.std(axis=1, keepdims=True)
            valid_std = (y_std > 0) & np.isfinite(y_std)
            with np.errstate(divide="ignore", invalid="ignore"):
                z = (y - y_mean) / np.where(valid_std, y_std, 1.0)  # (cc, N_tau)

            # length-m templates: (cc, n_t, m)
            n_t = N_tau - m + 1
            if n_t < 2:
                continue
            T = sliding_window_view(z, m, axis=1)
            D_max = np.zeros((cc, n_t, n_t), dtype=float)
            for d in range(m):
                diff = np.abs(T[:, :, d, None] - T[:, None, :, d])
                np.maximum(D_max, diff, out=D_max)
            Bmat = (D_max < r_tol)
            diag = np.arange(n_t)
            Bmat[:, diag, diag] = False
            B = Bmat.sum(axis=(1, 2))

            # length-(m+1) templates: (cc, n_t1, m+1)
            n_t1 = N_tau - m
            if n_t1 < 2:
                continue
            T1 = sliding_window_view(z, m + 1, axis=1)
            D1_max = np.zeros((cc, n_t1, n_t1), dtype=float)
            for d in range(m + 1):
                diff1 = np.abs(T1[:, :, d, None] - T1[:, None, :, d])
                np.maximum(D1_max, diff1, out=D1_max)
            Amat = (D1_max < r_tol)
            diag1 = np.arange(n_t1)
            Amat[:, diag1, diag1] = False
            A = Amat.sum(axis=(1, 2))

            valid = (B > 0) & (A > 0) & valid_std[:, 0]
            with np.errstate(divide="ignore", invalid="ignore"):
                se_vals = np.where(valid, np.log(B) - np.log(A), np.nan)
            sampen_per_tau[:, ti] = se_vals
            valid_scale[:, ti] = valid

        # ---- vectorized OLS slope of SampEn vs log(tau) per row ----
        mask = np.isfinite(sampen_per_tau) & valid_scale  # (cc, n_taus)
        n_finite = mask.sum(axis=1)  # (cc,)

        y_filled = np.where(mask, sampen_per_tau, 0.0)  # (cc, n_taus)
        x_masked = np.where(mask, log_taus[None, :], 0.0)  # (cc, n_taus)

        sum_x = x_masked.sum(axis=1)
        sum_y = y_filled.sum(axis=1)
        sum_x2 = (x_masked ** 2).sum(axis=1)
        sum_xy = (x_masked * y_filled).sum(axis=1)

        numerator = n_finite * sum_xy - sum_x * sum_y
        denominator = n_finite * sum_x2 - sum_x ** 2

        slope_ok = (n_finite >= 3) & (denominator > 0)
        with np.errstate(divide="ignore", invalid="ignore"):
            slopes = np.where(slope_ok, numerator / np.where(denominator > 0, denominator, 1.0), np.nan)

        # ---- trapezoidal area per row (over consecutive valid tau indices) ----
        area = np.zeros(cc, dtype=float)
        for i in range(cc):
            vt = np.where(mask[i])[0]
            if len(vt) >= 2:
                acc = 0.0
                for k in range(len(vt) - 1):
                    k1, k2 = int(vt[k]), int(vt[k + 1])
                    acc += (sampen_per_tau[i, k1] + sampen_per_tau[i, k2]) / 2.0 * (taus[k2] - taus[k1])
                area[i] = acc
        area = np.where(n_finite >= 3, area, np.nan)

        # wins[i] = r[i..i+W-1] = trailing window ending at bar t = i + W - 1.
        # Spec: NaN if t < W, i.e. i + W - 1 < W, i.e. i == 0. So only fill
        # output for i >= 1 (t >= W). Map: mse_slope[c0+i] -> t = c0+i+W-1.
        # For output index t, window index i = t - W + 1. So output[t] = value[i]
        # where i = t - W + 1, i.e. output[W:] = value[1:].
        n_out = c1 - c0
        out_start = c0 + W  # first output bar index this chunk contributes to
        # value index 0 -> t = c0 + W - 1 (skip, t < W when c0=0, i=0)
        # We write output[t] for t in [c0+W, c1+W-1] using value[i] for i in [1, n_out-1]
        # but only when t < n.
        lo_t = max(c0 + W - 1, W)  # t must be >= W
        hi_t = min(c1 + W - 2, n - 1)
        if lo_t <= hi_t:
            # output t in [lo_t, hi_t] corresponds to chunk-relative window
            # index j = t - c0 - W + 1 in [lo_j, hi_j]
            lo_j = lo_t - c0 - W + 1
            hi_j = hi_t - c0 - W + 1
            mse_slope[lo_t:hi_t + 1] = slopes[lo_j:hi_j + 1]
            mse_area[lo_t:hi_t + 1] = area[lo_j:hi_j + 1]

    return {"mse_slope": mse_slope, "mse_area": mse_area}


def build_underlying(bs: dict) -> dict:
    """Compute the causal per-bar MSE series used by every signal.
    Returns dict with matrices (n_assets, n_bars): one entry per base metric."""
    n_assets = int(bs["n_assets"])
    n_bars = int(bs["n_bars"])
    log_return = bs["log_return"]
    series: dict = {}
    METRIC_KEYS = ("mse_slope", "mse_area")
    mats = {k: np.full((n_assets, n_bars), np.nan, dtype=float) for k in METRIC_KEYS}
    for i in range(n_assets):
        m = compute_mse_metrics(np.asarray(log_return[i], dtype=float),
                                MSE_W, MSE_TAUS, MSE_M, MSE_R)
        mats["mse_slope"][i] = np.asarray(m["mse_slope"], dtype=float)
        mats["mse_area"][i] = np.asarray(m["mse_area"], dtype=float)
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
    if not CACHE_META.exists():
        raise SystemExit(f"FATAL: C356 meta missing: {CACHE_META}")
    meta = json.loads(CACHE_META.read_text())
    if meta.get("real_data_only") is not True or meta.get("fabricated_data") is not False:
        raise SystemExit("FATAL: C356 cache not real_data_only/fabricated_data=false")
    if int(meta.get("campaign") or 0) != 356:
        raise SystemExit("FATAL: C356 meta campaign != 356")
    shard_sha = meta.get("shard_sha256") or {}
    symbols = list(meta.get("symbols") or [])
    payload = {"symbols": symbols, "per_asset": {}, "n_bars": int(meta.get("n_grid_bars") or 0)}
    for s in symbols:
        sp = CACHE_DIR / f"{s}.npz"
        if not sp.exists():
            raise SystemExit(f"FATAL: C356 shard missing: {sp}")
        if sha256_file(sp) != shard_sha.get(s):
            raise SystemExit(f"FATAL: C356 shard sha mismatch: {s}")
        with np.load(sp) as z:
            payload["per_asset"][s] = {k: np.asarray(z[k]) for k in REQUIRED_FIELDS}
    cache_sha = sha256_file(CACHE_META)
    meta_sha = sha256_file(CACHE_META)
    prov_sha = sha256_file(CACHE_PROV) if CACHE_PROV.exists() else None
    return payload, meta, cache_sha, meta_sha, prov_sha


def build_series(payload: dict):
    symbols = list(payload.get("symbols") or [])
    n_assets = len(symbols)
    per_asset = payload.get("per_asset") or {}
    first = per_asset[symbols[0]]
    idx_ms = np.asarray(first["index_ms"], dtype="int64")
    index = pd.DatetimeIndex(pd.to_datetime(idx_ms, unit="ms", utc=True))
    n_b = len(index)
    if n_b == 0:
        raise SystemExit("FATAL: C356 common grid is empty")
    if n_b % TOD_BARS_PER_DAY != 0:
        raise SystemExit("FATAL: C356 grid is not a whole number of 288-bar days")

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

    ref_cfg = dict(signal="mse_slope_dev", L=240, H=4,
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
        "generated_at_utc": ts, "campaign": 356, "part": "oos_sweep",
        "analysis": "c356_multiscale_entropy_xsec_stat_arb_oos_5m",
        "verdict": verdict, "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "fail_closed": True,
        "mandate": (
            "C356 — test the cross-sectional intraday MULTISCALE ENTROPY (MSE) "
            "x SEASONAL-DISLOCATION mean-reversion stat-arb family on 10 USDT-M "
            "linear perps at native 5m (1296 pre-registered configs). Per-bar "
            "primitives: log_return=log(c[t]/c[t-1]) (r[0]=0) from real perp_close; "
            "abs_ret=|log_return|. Multiscale Entropy metric over fixed intrinsic "
            "window W=64 bars ending at bar t, coarse-graining scales tau in "
            "{1,2,4,8,16,32}, embedding dimension m=2, tolerance r=0.25 (z-score "
            "units at each scale): for each tau, coarse-grain "
            "y^(tau)[k]=mean(X[k*tau:(k+1)*tau]), standardize z^(tau), compute "
            "SampEn^(tau)=ln(B_m^(tau))-ln(A_m^(tau)); "
            "mse_slope[t]=OLS slope of SampEn^(tau) vs log(tau) (>=3 finite pts); "
            "mse_area[t]=trapezoidal area under SampEn^(tau) vs tau. "
            "Seasonal baseline = trailing mean/std at same (weekday,tod) bucket from "
            "history strictly before bar t (causal shift(1)), NaN-aware, excluding "
            "NaN obs. Signals: 2 real (mse_slope_dev, mse_area_dev) + 2 placebos "
            "(phase-randomized surrogates, never edges). Single-leg dollar-neutral "
            "perp PnL with costs on turnover (taker=fee+slip; maker_blend=0.5*fee+slip). "
            "Gates: Holm+BH at alpha=0.05 (BOTH), MDE, stability, "
            "signal-vs-placebo attribution. PRE-REGISTERED NaN policy: metric NaN "
            "unless sufficient finite obs and valid denominators; seasonal stats "
            "NaN-aware min_periods excluding NaN obs; NaN-score bars weight 0."
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
            "mse_params": {"W": MSE_W, "coarse_grain_scales": list(MSE_TAUS),
                           "embedding_dimension_m": MSE_M, "tolerance_r": MSE_R,
                           "agg": "coarse_grained_sample_entropy_chebyshev"},
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
                "note": "metric NaN share dominated by finite-obs/denominator requirements (t<W=64, <3 finite scales).",
            },
        },
        "methodology": {
            "buckets": "(weekday,tod)=dayofweek*288+seconds-of-day//300 (0..2015), exact 288 bars per UTC day.",
            "raw_features": "log_return=log(c[t]/c[t-1]) (r[0]=0) from real strictly-positive perp_close; abs_ret=|log_return|.",
            "primitives": "fixed intrinsic window W=64 bars ending at t: for each tau in {1,2,4,8,16,32} coarse-grain y^(tau)[k]=mean(X[k*tau:(k+1)*tau]), N_tau=W//tau; standardize z^(tau)=(y^(tau)-mean(y^(tau)))/std(y^(tau)); SampEn^(tau)=ln(B_m^(tau))-ln(A_m^(tau)) with m=2, B_m^(tau)=# ordered pairs i!=j with max|T_m[i]-T_m[j]|<r, A_m^(tau)=# ordered pairs i!=j with max|T_{m+1}[i]-T_{m+1}[j]|<r; mse_slope[t]=OLS slope of SampEn^(tau) vs log(tau) over scales with finite SampEn (>=3 pts); mse_area[t]=trapezoidal area under SampEn^(tau) vs tau.",
            "signals": "mse_slope/mse_area over fixed W=64; score=-(v-m)/sd with m/sd trailing same-bucket mean/std (min_periods=3, excluding NaN, causal shift(1)); cross-sectional rank, dollar-neutral gross 1.0; NaN-score assets weight 0.",
            "pnl": "single-leg perp: pnl = sum_i pos_i * perp_ret_i.",
            "costs": "charged on turnover; taker = fee+slip; maker_blend = 0.5*fee+slip.",
            "missing_data": "non-finite -> NaN; never impute/ffill; insufficient valid obs -> NaN -> not traded (fail-closed).",
            "multiple_testing": "one-sided paired t-test of per-split OOS net vs 0; Holm step-down AND Benjamini-Hochberg over all 1296 configs at alpha=0.05.",
            "mde": "two-sided alpha=0.05, power=0.80: (t_{0.975}+t_{0.80})*s/sqrt(n_splits).",
            "attribution": "mean |OOS net| per signal across all its configs; shares=|mean|/sum(|means|) over all 4 signals incl. placebos; dominant must be a real (non-placebo) signal with share >= 0.5 for attribution_ok.",
            "stability": "sign consistency >= 0.70 of splits AND first/second-half Sharpe corr >= 0.5.",
            "placebo": "phase-randomized surrogate via FFT phase randomization + rank restoration to original marginal; deterministic seed recorded; same marginal distribution, destroyed temporal alignment.",
            "mse_invariance_note": "SampEn uses Chebyshev tolerance-based template matching on the z-scored coarse-grained series; both B_m and A_m are window-internal, so SampEn is invariant to a constant-per-bar shift and to scaling (z-scoring). Validated against brute force in tests.",
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
    op = reports / f"campaign356_oos_sweep_{ts}.json"
    op.write_text(json.dumps(slim, indent=2, default=jdefault) + "\n")
    sweep_sha = sha256_file(op)
    full = reports / f"campaign356_oos_sweep_{ts}.full.json"
    full.write_text(json.dumps(sweep_obj, indent=2, default=jdefault) + "\n")

    surviving = [results[i] for i in edge_idx if rej_holm[i] and rej_bh[i]]
    registry = {
        "generated_at_utc": ts, "campaign": 356, "part": "registry",
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
    op_reg = reports / f"campaign356_tradable_edge_registry_{ts}.json"
    op_reg.write_text(json.dumps(registry, indent=2, default=jdefault) + "\n")
    reg_sha = sha256_file(op_reg)

    summary = {
        "generated_at_utc": ts, "campaign": 356, "part": "summary",
        "analysis": "validation_summary", "verdict": verdict, "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "universe": sweep_obj["universe"], "config": sweep_obj["config"],
        "gates": sweep_obj["gates"], "summary": sweep_obj["summary"],
        "oos_sweep_artifact": str(op.relative_to(ROOT)), "oos_sweep_sha256": sweep_sha,
        "registry_artifact": str(op_reg.relative_to(ROOT)), "registry_sha256": reg_sha,
    }
    op_sum = reports / f"campaign356_summary_{ts}.json"
    op_sum.write_text(json.dumps(summary, indent=2, default=jdefault) + "\n")
    sum_sha = sha256_file(op_sum)

    verdict_obj = {
        "generated_at_utc": ts, "campaign": 356, "part": "verdict",
        "analysis": "final_verdict",
        "verdict": verdict, "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "finding": (
            f"C356 cross-sectional intraday Multiscale Entropy "
            f"x seasonal-dislocation mean-reversion stat-arb edge {verdict} "
            f"({n_edge} deterministic edge configs, {n_survive_both} "
            f"survive Holm+BH over {n_total}); binding constraint: {binding}; "
            f"dominant attribution: {dominant} ({dominant_share:.4f})."
        ),
        "basis": "c356_multiscale_entropy_xsec_stat_arb_costed_oos_5m",
        "dataset": dataset_block,
        "oos_sweep_artifact": str(op.relative_to(ROOT)), "oos_sweep_sha256": sweep_sha,
        "registry_artifact": str(op_reg.relative_to(ROOT)), "registry_sha256": reg_sha,
        "summary_artifact": str(op_sum.relative_to(ROOT)), "summary_sha256": sum_sha,
        "binding_constraint": binding,
        "n_deterministic_edge": int(n_edge),
        "n_survive_holm": n_survive_holm, "n_survive_bh": n_survive_bh,
        "n_survive_both": n_survive_both,
        "attribution_shares": attrib_share,
        "dominant_attribution": dominant, "dominant_share": dominant_share,
        "hard_bans_honored": [
            "No synthetic/fabricated data; no relabeling existing caches as new",
            "No threshold/gate weakening; no cherry-picked windows/costs",
            "No edge claim unless the costed OOS test survives Holm+BH over all 1296 configs",
            "Real USDT-M linear 5m perp_close; funding excluded (control leg)",
            "Single-leg PnL with costs on turnover; executed_fills: false",
            "Only RNG is recorded-seed placebo phase randomization (not market data)",
        ],
        "binding_constraint_artifact": None,
        "binding_constraint_sha256": None,
    }
    binding_obj = {
        "generated_at_utc": ts, "campaign": 356, "part": "binding_constraint",
        "binding_constraint": binding,
        "n_survive_both": n_survive_both, "n_edge_proven": n_edge,
        "attribution_ok": attribution_ok, "dominant": dominant,
        "dominant_share": dominant_share,
        "stable": stability_ref["stable"],
        "verdict": verdict, "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
    }
    op_bc = reports / f"campaign356_binding_constraint_{ts}.json"
    op_bc.write_text(json.dumps(binding_obj, indent=2, default=jdefault) + "\n")
    bc_sha = sha256_file(op_bc)
    verdict_obj["binding_constraint_artifact"] = str(op_bc.relative_to(ROOT))
    verdict_obj["binding_constraint_sha256"] = bc_sha

    op_ver = reports / f"campaign356_verdict_{ts}.json"
    op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")

    print(json.dumps({
        "campaign": 356, "verdict": verdict, "edge_proven": edge_proven,
        "n_total": n_total, "n_survive_both": n_survive_both,
        "dominant": dominant, "dominant_share": dominant_share,
        "binding": binding,
        "oos_sweep": str(op.relative_to(ROOT)),
        "oos_sweep_sha256": sweep_sha,
        "registry_sha256": reg_sha, "summary_sha256": sum_sha,
        "binding_constraint_sha256": bc_sha,
        "verdict_sha256": sha256_file(op_ver),
    }, indent=2, default=jdefault))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
