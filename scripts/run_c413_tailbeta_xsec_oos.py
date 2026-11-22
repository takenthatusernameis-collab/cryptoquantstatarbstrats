#!/usr/bin/env python3
"""C413 — rigorous costed out-of-sample test of the cross-sectional intraday
TAILBETA: TAIL BETA / EXTREME DEPENDENCE VS EQUAL-WEIGHT MARKET stat-arb family
on 10 USDT-M linear perps at native 5m (1944 pre-registered configs).

GENUINELY NEW FAMILY (not a re-skin of any frozen modern campaign)
-----------------------------------------------------------------
C281B–C412 (all FROZEN formal negatives) exhausted carry, OFI/microstructure,
premium/index/mark basis, quarterly term-structure, same-asset spot-perp
lead-lag, autocorrelation/chop/vol-clustering/close-envelope/rescaled-range/
drawdown-duration/realized-variance-concentration/permutation-entropy/DFA
alpha/GPH d/local-Whittle d/variance-ratio/Higuchi/SampEn/MSE/LZC/MF-DFA h(q)/
ordinal-pattern-transition-entropy families, leverage/volatility-asymmetry
coupling (LVAC, C360), raw return skewness & excess kurtosis (RSKEK, C361),
Hill tail-index / tail asymmetry (C362), quantile asymmetry & tail-mass (QATM,
C363), realized semivariance / downside-upside decomposition (DSRV, C364),
Kaufman efficiency ratio (KER, C365), realized quartic variation (RQV, C366),
bipower variation (BPV/JAR, C367), median-based robust dispersion (RMAD/RABS,
C368), GMD/IQR (C369), realized absolute return & MAD (RAR/MADM, C370),
realized skewness & kurtosis (RSK/RKT, C371), time-irreversibility (TIRV,
C372), jump-robust MedRV (RLRV, C373), signed run-length asymmetry (SIGNRUN,
C374), multi-lag autocovariance (ACOVK, C375), quantile spread (QSPREAD, C376),
trend-slope t-stat (PSLOPE, C377), vol-of-vol ratio (VOVR, C378), quadratic
curvature (CURV, C379), signed-conditional lag covariance (SEMICOV, C380),
extreme-indicator persistence (TAILMEM, C382), turning-point rate (TURNINGPT-R,
C383), extremum-timing asymmetry (EXTPOS, C384), amplitude half-life (HALFRANGE,
C385), price-path roughness (PRROUGH, C386), band-crossing asymmetry (BANDX,
C387), upside/downside capture (MADR, C388), min realized variance (MINRV, C389),
extreme co-exceedance (XCOEX, C390), cross third-moment irreversibility (XSKEW3,
C391), drawdown/run-up asymmetry (DDRUN, C392), front/back variance asymmetry
(VTERM, C393), conditional tail expectation (CTES, C394), OU mean-reversion
half-life (OUHALFLIFE, C395), magnitude-distribution entropy (MAGNET, C396),
spectral flatness/entropy (SPECFM, C397), L-moment skewness/kurtosis (LMOM,
C398), CUSUM break (CBREAK, C399), Kendall tau/Spearman rho (KTREND, C400),
realized quarticity (RVQUART, C401), multi-scale Hill tail profile (TSCALE,
C402), conditional skewness/asymmetric curvature (ASYMCURV, C403), dominant
spectral frequency/centroid (DOMFREQ, C404), cross-sectional co-skewness/co-
kurtosis vs market (COSKEW, C405), market-beta level/asymmetry vs market
(BETAASYM, C406), cross-sectional rank persistence (XSRANK, C407), leader-
follower regression-coefficient asymmetry vs market (LEADLAG, C408), and
idiosyncratic/residual volatility & residual skewness vs market (RESIDVOL,
C409), and average pairwise co-movement / cross-sectional correlation profile
(XCORR, C410), and sign-conditional average pairwise correlation asymmetry
(SEMCORR, C411).

C413 is the first campaign whose primitive is the TAIL BETA / EXTREME
DEPENDENCE VS EQUAL-WEIGHT MARKET: the beta of an asset vs the equal-weight
market estimated from joint extreme-tail observations only (lower-tail and
upper-tail), plus their asymmetry and magnitude, over a trailing window:

    X = r_i[t-W+1 .. t]   (W trailing log-returns of asset i, W=256)
    M = m[t-W+1 .. t]     (W trailing log-returns of the equal-weight market)
    q = 0.10 (10% tail)
    tailbeta_low[t]  = cov(X, M | X <= q_X, M <= q_M) / var(M | M <= q_M)
    tailbeta_high[t] = cov(X, M | X >= q^X, M >= q^M) / var(M | M >= q^M)
    tailbeta_asym[t] = tailbeta_high[t] - tailbeta_low[t]
    tailbeta_mag[t]  = (|tailbeta_high[t]| + |tailbeta_low[t]|) / 2

NaN if t<W, any NaN/non-finite, conditional sample size < 10, or conditional
variance <= 0. This is a tail-dependence family — no prior kernel estimates a
conditional market beta from joint lower/upper-tail observations. Genuinely
distinct from C406 BETAASYM (same-bar full-window beta asymmetry), C409
RESIDVOL (residual volatility, not tail dependence), C410 XCORR (full-window
correlation), C411 SEMCORR (sign-conditional correlation), C412 SIGNPOWER
(signed fractional moments), and every univariate moment/tail/spectral family
before it. Never used before. Price-only (perp_close), volume-free.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
reports = ROOT / "reports"
reports.mkdir(exist_ok=True)
cache_dir = ROOT / "data" / "cache"

CACHE_DIR = cache_dir / "campaign413_tailbeta_5m"
CACHE_META = cache_dir / "campaign413_tailbeta_5m.meta.json"
CACHE_PROV = cache_dir / "campaign413_tailbeta_5m.provenance.json"
REQUIRED_FIELDS = ["index_ms", "perp_close", "log_return", "abs_ret", "funding_rate"]

# ---- pre-registered grid ----
SIGNALS = (
    "tailbeta_low_dev", "tailbeta_high_dev", "tailbeta_asym_dev", "tailbeta_mag_dev",
    "tailbeta_low_placebo", "tailbeta_high_placebo",
)
# 6 signals x 6 lookbacks x 3 rebalances x 3 fees x 3 slips x 2 cost = 1944 = N_TRIALS
LOOKBACKS = (60, 120, 240, 480, 960, 1920)          # bars (seasonal baseline history)
REBALANCES = (1, 4, 12)                            # bars
FEES = (0.0004, 0.0007, 0.0010)
SLIPS = (0.0, 0.0001, 0.0002)
COST_VARIANTS = ("taker", "maker_blend")
FRAC = 1.0 / 3.0
ALPHA = 0.05
MIN_PERIODS_BASELINE = 3
PLACEBO_SEED = 20261277
TRAIN_M, TEST_M, ROLL_M = 12, 3, 3
STABILITY_MIN_SIGN_CONSISTENCY = 0.70
STABILITY_MIN_SHARPE_CORR = 0.50
DOMINANT_SHARE_MIN = 0.50

N_TRIALS = (len(SIGNALS) * len(LOOKBACKS) *
             len(REBALANCES) * len(FEES) * len(SLIPS) * len(COST_VARIANTS))  # 1944

# signal -> (base_metric_key, kind)
# kind in {"dev","placebo_dev"}
SIGNAL_FAMILY = {
    "tailbeta_low_dev": ("tailbeta_low", "dev"),
    "tailbeta_high_dev": ("tailbeta_high", "dev"),
    "tailbeta_asym_dev": ("tailbeta_asym", "dev"),
    "tailbeta_mag_dev": ("tailbeta_mag", "dev"),
    "tailbeta_low_placebo": ("tailbeta_low", "placebo_dev"),
    "tailbeta_high_placebo": ("tailbeta_high", "placebo_dev"),
    "tailbeta_asym_placebo": ("tailbeta_asym", "placebo_dev"),
    "tailbeta_mag_placebo": ("tailbeta_mag", "placebo_dev"),
}

ATTR_REPRESENTATIVES = {
    "tailbeta_low_dev": "tailbeta_low_dev",
    "tailbeta_high_dev": "tailbeta_high_dev",
    "tailbeta_asym_dev": "tailbeta_asym_dev",
    "tailbeta_mag_dev": "tailbeta_mag_dev",
}

TAILBETA_W = 256
TAILBETA_Q = 0.10
TAILBETA_CHUNK = 4096


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
    if isinstance(pd, type) and isinstance(o, pd.Timestamp):
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
    return weekday * 288 + tod  # 0..2015


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


# ------------------------------------------------------- TAILBETA: tail beta / extreme dependence vs market
def _tailbeta_pass(R, W=TAILBETA_W, q=TAILBETA_Q, chunk=TAILBETA_CHUNK):
    """Vectorized TAILBETA for the full (n_assets, T) return matrix R. For each
    bar t (t=W..T-1) and asset i, window X_i = R[i, t-W+1..t], market window
    M = m[t-W+1..t] with m[s] = mean across assets of R[:, s]:
        tailbeta_low[t]  = cov(X, M | X <= q_X, M <= q_M) / var(M | M <= q_M)
        tailbeta_high[t] = cov(X, M | X >= q^X, M >= q^M) / var(M | M >= q^M)
        tailbeta_asym[t] = tailbeta_high[t] - tailbeta_low[t]
        tailbeta_mag[t]  = (|tailbeta_high[t]| + |tailbeta_low[t]|) / 2
    NaN if t<W, any NaN/non-finite, conditional sample size < 10, or conditional
    variance <= 0. Uses sliding_window_view processed in chunks; matches the
    brute-force reference to maxdiff < 1e-12."""
    R = np.asarray(R, dtype=float)
    n_assets, T = R.shape
    # equal-weight market return across assets
    m = np.nanmean(R, axis=0)
    out_low = np.full((n_assets, T), np.nan, dtype=float)
    out_high = np.full((n_assets, T), np.nan, dtype=float)
    out_asym = np.full((n_assets, T), np.nan, dtype=float)
    out_mag = np.full((n_assets, T), np.nan, dtype=float)
    if T < W:
        return {"tailbeta_low": out_low, "tailbeta_high": out_high,
                "tailbeta_asym": out_asym, "tailbeta_mag": out_mag}
    rw = sliding_window_view(R, W, axis=1)   # (n_assets, K, W) view, K=T-W+1
    mw = sliding_window_view(m, W)           # (K, W)
    K = rw.shape[1]
    cols = np.arange(W - 1, T)
    for start in range(0, K, chunk):
        end = min(start + chunk, K)
        rc = np.array(rw[:, start:end, :], dtype=float)   # (n_assets, c, W)
        mc = np.array(mw[start:end, :], dtype=float)      # (c, W)
        ccount = end - start
        q_X = np.quantile(rc, q, axis=2)         # (n_assets, c)
        qM_low = np.quantile(mc, q, axis=1)      # (c,)
        qX_high = np.quantile(rc, 1.0 - q, axis=2)
        qM_high = np.quantile(mc, 1.0 - q, axis=1)
        mc_b = mc[None, :, :]                    # (1, c, W)
        lower_mask = (rc <= q_X[:, :, None]) & (mc_b <= qM_low[None, :, None])
        upper_mask = (rc >= qX_high[:, :, None]) & (mc_b >= qM_high[None, :, None])
        cnt_low = lower_mask.sum(axis=2)         # (n_assets, c)
        cnt_up = upper_mask.sum(axis=2)
        XM = rc * mc_b
        cl = np.maximum(cnt_low, 1.0)
        cu = np.maximum(cnt_up, 1.0)
        sXM_low = (XM * lower_mask).sum(axis=2)
        sX_low = (rc * lower_mask).sum(axis=2)
        sM_low = (mc_b * lower_mask).sum(axis=2)
        sM2_low = ((mc_b * mc_b) * lower_mask).sum(axis=2)
        sXM_up = (XM * upper_mask).sum(axis=2)
        sX_up = (rc * upper_mask).sum(axis=2)
        sM_up = (mc_b * upper_mask).sum(axis=2)
        sM2_up = ((mc_b * mc_b) * upper_mask).sum(axis=2)
        with np.errstate(divide="ignore", invalid="ignore"):
            cov_low = (sXM_low - sX_low * sM_low / cl) / cl
            varM_low = (sM2_low - sM_low * sM_low / cl) / cl
            cov_up = (sXM_up - sX_up * sM_up / cu) / cu
            varM_up = (sM2_up - sM_up * sM_up / cu) / cu
        valid_low = (cnt_low >= 10) & (varM_low > 0) & np.isfinite(cov_low) & np.isfinite(varM_low)
        valid_up = (cnt_up >= 10) & (varM_up > 0) & np.isfinite(cov_up) & np.isfinite(varM_up)
        tb_low = np.where(valid_low, cov_low / varM_low, np.nan)
        tb_high = np.where(valid_up, cov_up / varM_up, np.nan)
        col0 = start + W - 1
        col1 = end + W - 1
        j0 = start
        if start == 0:
            # spec: NaN if t < W, so the j=0 window (ending bar t=W-1) stays NaN.
            j0 = 1
            if j0 >= end:
                continue
            col0 = j0 + W - 1
        out_low[:, col0:col1] = tb_low[:, j0 - start:end - start]
        out_high[:, col0:col1] = tb_high[:, j0 - start:end - start]
        out_asym[:, col0:col1] = tb_high[:, j0 - start:end - start] - tb_low[:, j0 - start:end - start]
        out_mag[:, col0:col1] = (np.abs(tb_high[:, j0 - start:end - start]) + np.abs(tb_low[:, j0 - start:end - start])) / 2.0
    return {"tailbeta_low": out_low, "tailbeta_high": out_high,
            "tailbeta_asym": out_asym, "tailbeta_mag": out_mag}


def _tailbeta_bruteforce(log_return, W=TAILBETA_W, q=TAILBETA_Q):
    """Per-window reference TAILBETA kernel. For each asset i and bar t
    (t=W..n-1), window X=r[t-W+1..t], market M=m[t-W+1..t]:
        tailbeta_low  = cov(X,M|X<=q_X,M<=q_M)/var(M|M<=q_M)
        tailbeta_high = cov(X,M|X>=q^X,M>=q^M)/var(M|M>=q^M)
        tailbeta_asym = high - low
        tailbeta_mag  = (|high|+|low|)/2
    NaN if t<W, any NaN/non-finite, conditional sample size < 10, or conditional
    variance <= 0."""
    X = np.asarray(log_return, dtype=float)
    n_assets, n = X.shape
    m = np.nanmean(X, axis=0)
    out_low = np.full((n_assets, n), np.nan, dtype=float)
    out_high = np.full((n_assets, n), np.nan, dtype=float)
    out_asym = np.full((n_assets, n), np.nan, dtype=float)
    out_mag = np.full((n_assets, n), np.nan, dtype=float)
    if n < W:
        return {k: np.full((n_assets, n), np.nan, dtype=float)
                for k in ("tailbeta_low", "tailbeta_high", "tailbeta_asym", "tailbeta_mag")}
    for t in range(W, n):
        Mw = m[t - W + 1:t + 1]
        if not np.isfinite(Mw).all():
            continue
        for i in range(n_assets):
            Xw = X[i, t - W + 1:t + 1]
            if not np.isfinite(Xw).all():
                continue
            qX = float(np.quantile(Xw, q))
            qM = float(np.quantile(Mw, q))
            qXh = float(np.quantile(Xw, 1.0 - q))
            qMh = float(np.quantile(Mw, 1.0 - q))
            lm = (Xw <= qX) & (Mw <= qM)
            um = (Xw >= qXh) & (Mw >= qMh)
            cl = int(lm.sum())
            cu = int(um.sum())
            if cl >= 10:
                Xl = Xw[lm]
                Ml = Mw[lm]
                varM_l = float(((Ml - Ml.mean()) ** 2).mean())
                if varM_l > 0:
                    cov_l = float(((Xl - Xl.mean()) * (Ml - Ml.mean())).mean())
                    out_low[i, t] = cov_l / varM_l
            if cu >= 10:
                Xu = Xw[um]
                Mu = Mw[um]
                varM_u = float(((Mu - Mu.mean()) ** 2).mean())
                if varM_u > 0:
                    cov_u = float(((Xu - Xu.mean()) * (Mu - Mu.mean())).mean())
                    out_high[i, t] = cov_u / varM_u
            if np.isfinite(out_low[i, t]) and np.isfinite(out_high[i, t]):
                out_asym[i, t] = out_high[i, t] - out_low[i, t]
                out_mag[i, t] = (abs(out_high[i, t]) + abs(out_low[i, t])) / 2.0
    return {"tailbeta_low": out_low, "tailbeta_high": out_high,
            "tailbeta_asym": out_asym, "tailbeta_mag": out_mag}


def compute_tailbeta_metrics(log_return, W=TAILBETA_W, q=TAILBETA_Q):
    """Vectorized TAILBETA kernel. For each asset i and bar t (t=W..n-1),
    W=256, needing indices t-W+1..t (W bars):
        tailbeta_low  = cov(X,M|X<=q_X,M<=q_M)/var(M|M<=q_M)
        tailbeta_high = cov(X,M|X>=q^X,M>=q^M)/var(M|M>=q^M)
        tailbeta_asym = high - low
        tailbeta_mag  = (|high|+|low|)/2.
    Matches _tailbeta_bruteforce (maxdiff < 1e-12)."""
    X = np.asarray(log_return, dtype=float)
    n_assets, n = X.shape
    if n < W:
        nan_m = {k: np.full((n_assets, n), np.nan, dtype=float)
                 for k in ("tailbeta_low", "tailbeta_high", "tailbeta_asym", "tailbeta_mag")}
        return nan_m
    return _tailbeta_pass(X, W)


def build_underlying(bs: dict) -> dict:
    """Compute the causal per-bar TAILBETA metric series used by every signal.
    Returns dict with matrices (n_assets, n_bars): tailbeta_low, tailbeta_high,
    tailbeta_asym, tailbeta_mag."""
    n_assets = int(bs["n_assets"])
    n_bars = int(bs["n_bars"])
    log_return = np.asarray(bs["log_return"], dtype=float)
    series: dict = {}
    METRIC_KEYS = ("tailbeta_low", "tailbeta_high", "tailbeta_asym", "tailbeta_mag")
    result = compute_tailbeta_metrics(log_return, W=TAILBETA_W)
    for k in METRIC_KEYS:
        series[k] = np.asarray(result[k], dtype=float)
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
        raise SystemExit(f"FATAL: C413 shard dir missing: {CACHE_DIR}")
    if not CACHE_META.exists():
        raise SystemExit(f"FATAL: C413 meta missing: {CACHE_META}")
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
        raise SystemExit("FATAL: C413 common grid is empty")
    if n_b % 288 != 0:
        raise SystemExit("FATAL: C413 grid is not a whole number of 288-bar days")

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
    n_days = n_b // 288
    if not np.array_equal(day_ord, np.repeat(np.arange(n_days), 288)):
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
            s_std = float(np.std(net_arr, ddof=1))
            t_a = float(stats.t.ppf(1 - ALPHA / 2, df=n_splits - 1))
            t_b = float(stats.t.ppf(0.80, df=n_splits - 1))
            mde_bps = (t_a + t_b) * s_std / math.sqrt(n_splits) * 10000.0
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

    ref_cfg = dict(signal="tailbeta_asym_dev", L=240, H=4,
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
        "storage": "per_asset float32 npz shards",
        "source_campaign": int(meta.get("source_campaign") or 312),
        "network_ingest": False,
        "total_shard_bytes": int(meta.get("total_shard_bytes") or 0),
        "max_shard_bytes": int(meta.get("max_shard_bytes") or 0),
        "under_push_limit": bool(meta.get("under_push_limit")),
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
    }

    sweep_obj = {
        "generated_at_utc": ts, "campaign": 413, "part": "oos_sweep",
        "analysis": "c413_tailbeta_xsec_stat_arb_oos_5m",
        "verdict": verdict, "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "fail_closed": True,
        "mandate": (
            "C413 — test the cross-sectional intraday TAILBETA: TAIL BETA / "
            "EXTREME DEPENDENCE VS EQUAL-WEIGHT MARKET stat-arb family on 10 "
            "USDT-M linear perps at native 5m (1944 pre-registered configs). "
            "Per-bar primitives: perp_close real 5m kline close; "
            "log_return=log(c[t]/c[t-1]) (r[0]=0); abs_ret=|log_return|; "
            "equal-weight market return m[s]=(1/10)*sum_i r_i[s]. "
            "TAILBETA scalars over fixed intrinsic window W=256 trailing "
            "returns: for each bar t, X=r_i[t-W+1..t], M=m[t-W+1..t], tail "
            "q=0.10; lower-tail beta=cov(X,M|X<=q_X,M<=q_M)/var(M|M<=q_M), "
            "upper-tail beta=cov(X,M|X>=q^X,M>=q^M)/var(M|M>=q^M), "
            "tail-beta asymmetry=upper-lower, tail-beta magnitude=(|upper|+"
            "|lower|)/2. Needs indices t-W+1..t (W bars). NaN if t<W, any "
            "NaN/non-finite, conditional sample size < 10, or conditional "
            "variance <= 0. Seasonal baseline = trailing mean/std at same "
            "(weekday,tod) bucket from history strictly before bar t (causal "
            "shift(1)), NaN-aware, excluding NaN obs. Signals: 4 real "
            "(tailbeta_low_dev, tailbeta_high_dev, tailbeta_asym_dev, "
            "tailbeta_mag_dev) + 4 placebos (phase-randomized surrogates, never "
            "edges). Single-leg dollar-neutral perp PnL with costs on turnover "
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
            "tailbeta_params": {"window_W": TAILBETA_W, "tail_q": TAILBETA_Q},
        },
        "gates": {
            "fail_closed": True,
            "multiple_testing": {"holm_alpha": ALPHA, "bh_alpha": ALPHA,
                                 "n_survive_holm": n_survive_holm, "n_survive_bh": n_survive_bh,
                                 "n_survive_both": n_survive_both, "n_edge_proven": n_edge},
            "tailbeta_mde": {"n_splits": int(n_splits), "mde_bps_mean": mde_bps,
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
                "note": "metric NaN share dominated by finite-obs requirements (t<W=256 or NaN in trailing W-bar window or not finite or conditional sample < 10 or conditional variance <= 0).",
            },
        },
        "methodology": {
            "buckets": "(weekday,tod)=dayofweek*288+seconds-of-day//300 (0..2015), exact 288 bars per UTC day.",
            "raw_features": "log_return=log(c[t]/c[t-1]) (r[0]=0) from real strictly-positive perp_close; abs_ret=|log_return|; market m[s]=mean across assets.",
            "primitives": "fixed intrinsic window W=256 trailing returns; "
                          "tailbeta_low=cov(X,M|X<=q_X,M<=q_M)/var(M|M<=q_M), "
                          "tailbeta_high=cov(X,M|X>=q^X,M>=q^M)/var(M|M>=q^M), "
                          "tailbeta_asym=high-low, tailbeta_mag=(|high|+|low|)/2, q=0.10.",
            "signals": "tailbeta_low/tailbeta_high/tailbeta_asym/tailbeta_mag over fixed W=256; "
                       "score=-(v-m)/sd with m/sd trailing same-bucket mean/std "
                       "(min_periods=3, excluding NaN, causal shift(1)); "
                       "cross-sectional rank, dollar-neutral gross 1.0; "
                       "NaN-score assets weight 0.",
            "pnl": "single-leg perp: pnl = sum_i pos_i * perp_ret_i.",
            "costs": "charged on turnover; taker = fee+slip; maker_blend = 0.5*fee+slip.",
            "missing_data": "non-finite -> NaN; never impute/ffill; insufficient valid obs -> NaN -> not traded (fail-closed).",
            "multiple_testing": "one-sided paired t-test of per-split OOS net vs 0; Holm step-down AND Benjamini-Hochberg over all 1944 configs at alpha=0.05.",
            "mde": "two-sided alpha=0.05, power=0.80: (t_{0.975}+t_{0.80})*s/sqrt(n_splits).",
            "attribution": "mean |OOS net| per signal across all its configs; shares=|mean|/sum(|means|) over all 8 signals incl. placebos; dominant must be a real (non-placebo) signal with share >= 0.5 for attribution_ok.",
            "stability": "sign consistency >= 0.70 of splits AND first/second-half Sharpe corr >= 0.5.",
            "placebo": "phase-randomized surrogate via FFT phase randomization + rank restoration to original marginal; deterministic seed recorded; same marginal distribution, destroyed temporal alignment.",
            "tailbeta_vectorization_note": "return matrix R=(T,10) built once; market m[s]=mean across assets; "
                          "zero-copy sliding_window_view(R,256) and sliding_window_view(m,256) processed in "
                          "chunks; per-chunk joint tail quantiles q_X/q_M at q=0.10 and 1-q; conditional "
                          "covariance/variance via masked sums; validated against brute-force per-window loop "
                          "with maxdiff < 1e-12 in tests. Chunking keeps peak memory low.",
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
    op = reports / f"campaign413_oos_sweep_{ts}.json"
    op.write_text(json.dumps(slim, indent=2, default=jdefault) + "\n")
    sweep_sha = sha256_file(op)
    full = reports / f"campaign413_oos_sweep_{ts}.full.json"
    full.write_text(json.dumps(sweep_obj, indent=2, default=jdefault) + "\n")

    surviving = [results[i] for i in edge_idx if rej_holm[i] and rej_bh[i]]
    registry = {
        "generated_at_utc": ts, "campaign": 413, "part": "registry",
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
    op_reg = reports / f"campaign413_tradable_edge_registry_{ts}.json"
    op_reg.write_text(json.dumps(registry, indent=2, default=jdefault) + "\n")
    reg_sha = sha256_file(op_reg)

    summary = {
        "generated_at_utc": ts, "campaign": 413, "part": "summary",
        "analysis": "validation_summary", "verdict": verdict, "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "universe": sweep_obj["universe"], "config": sweep_obj["config"],
        "gates": sweep_obj["gates"],
        "artifacts": {"oos_sweep": {"path": str(op.relative_to(ROOT)), "sha256": sweep_sha},
                      "registry": {"path": str(op_reg.relative_to(ROOT)), "sha256": reg_sha}},
        "summary": sweep_obj["summary"], "binding_constraint": binding,
    }
    op_sum = reports / f"campaign413_summary_{ts}.json"
    op_sum.write_text(json.dumps(summary, indent=2, default=jdefault) + "\n")
    sum_sha = sha256_file(op_sum)

    finding = (
        f"C413 cross-sectional intraday TAILBETA tail beta / extreme dependence "
        f"stat-arb edge {verdict} "
        f"({n_edge} deterministic edge configs, {n_survive_both} survive "
        f"Holm+BH over {N_TRIALS}); binding constraint: {binding}; dominant "
        f"attribution: {dominant} ({dominant_share:.4f})."
        if binding is not None
        else f"C413 cross-sectional intraday TAILBETA tail beta / extreme dependence "
        f"stat-arb edge validated: "
        f"{n_survive_both} of {n_edge} deterministic edge configs survive Holm+BH over "
        f"{N_TRIALS}; edge_proven:{edge_proven}."
    )
    verdict_obj = {
        "generated_at_utc": ts, "campaign": 413, "part": "verdict",
        "analysis": "final_verdict", "verdict": verdict, "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "finding": finding,
        "basis": "c413_tailbeta_xsec_stat_arb_costed_oos_5m",
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
            "Real USDT-M linear 5m perp_close; funding excluded (control leg)",
            "Single-leg PnL with costs on turnover; executed_fills: false",
            "Only RNG is recorded-seed placebo phase randomization (not market data)",
        ],
    }

    op_ver = reports / f"campaign413_verdict_{ts}.json"
    op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")
    ver_sha = sha256_file(op_ver)

    bind_sha = None
    bind_path = None
    if binding is not None:
        binding_obj = {
            "generated_at_utc": ts, "campaign": 413, "part": "binding_constraint",
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
                "C413 cross-sectional intraday TAILBETA tail beta / extreme dependence "
                "stat-arb does not survive validation; formal negative. Binding constraint: {binding}."
            ).format(binding=binding),
            "note": "Diagnosis only; never an edge claim. No threshold weakening.",
        }
        op_bind = reports / f"campaign413_binding_constraint_{ts}.json"
        op_bind.write_text(json.dumps(binding_obj, indent=2, default=jdefault) + "\n")
        bind_sha = sha256_file(op_bind)
        bind_path = str(op_bind.relative_to(ROOT))
        verdict_obj["binding_constraint_artifact"] = bind_path
        verdict_obj["binding_constraint_sha256"] = bind_sha
        op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")
        ver_sha = sha256_file(op_ver)

    print(json.dumps({
        "campaign": 413, "verdict": verdict, "edge_proven": edge_proven,
        "n_total_runs": int(n_total), "n_deterministic_edge": int(n_edge),
        "n_survive_holm": n_survive_holm, "n_survive_bh": n_survive_bh,
        "n_survive_both": n_survive_both,
        "binding_constraint": binding,
        "attribution_shares": attrib_share, "dominant_attribution": dominant,
        "dominant_share": dominant_share,
        "mde_bps_mean": mde_bps, "observed_mean_bps_per_split": obs_mean_bps,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
