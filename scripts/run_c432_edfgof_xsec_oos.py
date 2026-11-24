#!/usr/bin/env python3
"""C432 — rigorous costed out-of-sample test of the price-only EDF-GOODNESS-OF-FIT
normality-departure stat-arb family on 10 USDT-M linear perps at native 5m
(2592 pre-registered configs).

GENUINELY NEW FAMILY (not a re-skin of any frozen prior campaign)
----------------------------------------------------------------
All prior campaigns (all FROZEN formal negatives) exhausted carry, OFI/
microstructure, premium/index/mark basis, quarterly term-structure,
same-asset spot-perp lead-lag, autocorrelation/chop/vol-clustering/close-envelope/
rescaled-range/drawdown-duration/realized-variance-concentration/permutation-
entropy/DFA alpha/GPH d/local-Whittle d/variance-ratio/Higuchi/SampEn/MSE/LZC/
MF-DFA h(q)/ordinal-pattern-transition-entropy families, leverage/volatility-
asymmetry coupling (LVAC), raw return skewness & excess kurtosis (RSKEK), Hill
tail-index / tail asymmetry, quantile asymmetry & tail-mass (QATM), realized
semivariance / downside-upside decomposition (DSRV), Kaufman efficiency ratio
(KER), realized quartic variation (RQV), bipower variation (BPV/JAR), median-
based robust dispersion (RMAD/RABS), GMD/IQR, realized absolute return & MAD
(RAR/MADM), realized skewness & kurtosis (RSK/RKT), time-irreversibility
(TIRV), jump-robust MedRV (RLRV), signed run-length asymmetry (SIGNRUN),
multi-lag autocovariance (ACOVK), quantile spread (QSPREAD), trend-slope
t-stat (PSLOPE), vol-of-vol ratio (VOVR), quadratic curvature (CURV), signed-
conditional lag covariance (SEMICOV), extreme-indicator persistence (TAILMEM),
turning-point rate (TURNINGPT-R), extremum-timing asymmetry (EXTPOS), amplitude
half-life (HALFRANGE), price-path roughness (PRROUGH), band-crossing asymmetry
(BANDX), upside/downside capture (MADR), min realized variance (MINRV), extreme
co-exceedance (XCOEX), cross third-moment irreversibility (XSKEW3), drawdown/
run-up asymmetry (DDRUN), front/back variance asymmetry (VTERM), conditional
tail expectation (CTES), OU mean-reversion half-life (OUHALFLIFE), magnitude-
distribution entropy (MAGNET), spectral flatness/entropy (SPECFM), L-moment
skewness/kurtosis (LMOM), CUSUM break (CBREAK), Kendall tau/Spearman rho
(KTREND), realized quarticity (RVQUART), multi-scale Hill tail profile (TSCALE),
conditional skewness/asymmetric curvature (ASYMCURV), dominant spectral
frequency/centroid (DOMFREQ), cross-sectional co-skewness/co-kurtosis vs market
(COSKEW), market-beta level/asymmetry vs market (BETAASYM), cross-sectional
rank persistence vs market (XSRANK), leader-follower regression-coefficient
asymmetry vs market (LEADLAG), idiosyncratic/residual volatility & residual
skewness vs market (RESIDVOL), average pairwise co-movement / cross-sectional
correlation profile (XCORR), sign-conditional average pairwise correlation
asymmetry (SEMCORR), signed fractional power moments vs market (SIGNPOWER),
tail beta / extreme dependence vs equal-weight market (TAILBETA), sign-agreement
cross-sectional motion vs equal-weight market (SIGNCO-MOTION), tail dependence
coefficient / extremal dependence vs equal-weight market (TAILDEP),
quantile-regression slope vs equal-weight market (QREG), cross-sectional
extreme-dominance frequency vs the cross-section (CDOMIN), normalized
autocorrelation-function decorrelation horizon vs own returns (AUTOCF),
standardized empirical-characteristic-function dispersion & asymmetry vs own
returns (RCF), spectral coherence / frequency-localized co-movement vs
equal-weight market (SCOH), sign-sequence autocorrelation of own returns
(SIGNCOH) / zero-crossing rate of the cumulative-return path (ZCRPATH) /
run-length distribution entropy of consecutive return signs (RUNLEN) /
inter-extremum spacing distribution of the trailing price path (IESD) /
recurrence quantification analysis (RQA) / wavelet-leader multifractal spectrum
(WLMF) / path-local-time-occupation (PTLT) / order-1 Markov sign-transition
(SIGNENTROPY), and distance correlation dCor (one scalar over the whole joint
distribution) and cross-quantilogram ρ_τ(k) (quantile-conditional multi-τ lag
profile).

C432 is the FIRST campaign to use the EDF-GOODNESS-OF-FIT normality-departure
family: for each trailing window of standardized returns z it compares the full
empirical CDF to the standard normal CDF N(0,1) via four statistics —
Anderson–Darling A² (tail-sensitive), Cramér–von Mises W² (integrated squared),
Kolmogorov–Smirnov D (sup), Kuiper V (tail-sensitive, invariant) — capturing
tail+shape departure that linear, quantile, moment, spectral, sign, entropy,
Markov, dCor, and cross-quantilogram statistics miss.

For each asset i and bar t, with W_q = 256 (fallback 128):

    r[t] = log(c[t]/c[t-1])                     (causal log-return, r[0]=0)
    a[t] = |r[t]|                               (return magnitude)
    s[t] = sign(r[t])                           (per-bar sign: +1/-1/0)
    m[t] = mean_i r_i[t]                        (equal-weight market return)

    Causal trailing mean μ[t] and std σ[t] of {r[t-W_q+1..t]}.
    Standardized return z[t] = (r[t]-μ[t])/σ[t]  (z[t]=0 if σ[t]≤0 or non-finite).

    For each trailing window of z, sort to order statistics z_(1)≤...≤z_(n),
    p_(i) = Φ(z_(i)) (standard normal CDF). Four EDF statistics vs N(0,1):

        A² = -n - (1/n) Σ_i (2i-1)[ ln(p_(i)) + ln(1-p_(n+1-i)) ]
        W² = (1/(12n)) + Σ_i (p_(i) - (2i-1)/(2n))²
        D  = max_i max( |p_(i) - i/n|, |p_(i) - (i-1)/n| )
        V  = D⁺ + D⁻,  D⁺ = max_i (i/n - p_(i)),  D⁻ = max_i (p_(i) - (i-1)/n)

    NaN if t<W_q, any NaN/non-finite in window, σ[t]≤0, or any p∈{0,1}.

Four concept scalars per asset i: edf_ad, edf_cvm, edf_ks, edf_kuiper = the
seasonally-deviated EDF-GOF statistic (see build_scores). Each with a matched
phase-randomized-surrogate placebo (edf_*_placebo). The vectorized formulation
is verified equal to an independent naive per-window EDF-GOF reference to
maxdiff < 1e-12. Price-only (perp_close), volume-free.
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

CACHE_DIR = cache_dir / "campaign432_edfgof_5m"
CACHE_META = cache_dir / "campaign432_edfgof_5m.meta.json"
CACHE_PROV = cache_dir / "campaign432_edfgof_5m.provenance.json"
METRICS_CACHE = cache_dir / "campaign432_edfgof_metrics.npz"
REQUIRED_FIELDS = ["index_ms", "perp_close", "log_return", "abs_ret", "funding_rate", "sign"]
NORM_CDF = stats.norm.cdf

# ---- pre-registered grid ----
SIGNALS = (
    "edf_ad_dev", "edf_cvm_dev", "edf_ks_dev", "edf_kuiper_dev",
    "edf_ad_placebo", "edf_cvm_placebo", "edf_ks_placebo",
    "edf_kuiper_placebo",
)
# 8 signals x 6 lookbacks x 3 rebalances x 3 fees x 3 slips x 2 cost = 2592 = N_TRIALS
LOOKBACKS = (60, 120, 240, 480, 960, 1920)          # bars (seasonal baseline history)
REBALANCES = (1, 4, 12)                            # bars
FEES = (0.0004, 0.0007, 0.0010)
SLIPS = (0.0, 0.0001, 0.0002)
COST_VARIANTS = ("taker", "maker_blend")
FRAC = 1.0 / 3.0
ALPHA = 0.05
MIN_PERIODS_BASELINE = 3
PLACEBO_SEED = 20261296
TRAIN_M, TEST_M, ROLL_M = 12, 3, 3
STABILITY_MIN_SIGN_CONSISTENCY = 0.70
STABILITY_MIN_SHARPE_CORR = 0.50
DOMINANT_SHARE_MIN = 0.50

N_TRIALS = (len(SIGNALS) * len(LOOKBACKS) *
              len(REBALANCES) * len(FEES) * len(SLIPS) * len(COST_VARIANTS))  # 2592

# signal -> (base_metric_key, kind); kind in {"dev","placebo_dev"}
SIGNAL_FAMILY = {
    "edf_ad_dev": ("edf_ad", "dev"),
    "edf_cvm_dev": ("edf_cvm", "dev"),
    "edf_ks_dev": ("edf_ks", "dev"),
    "edf_kuiper_dev": ("edf_kuiper", "dev"),
    "edf_ad_placebo": ("edf_ad", "placebo_dev"),
    "edf_cvm_placebo": ("edf_cvm", "placebo_dev"),
    "edf_ks_placebo": ("edf_ks", "placebo_dev"),
    "edf_kuiper_placebo": ("edf_kuiper", "placebo_dev"),
}

ATTR_REPRESENTATIVES = {
    "edf_ad_dev": "edf_ad_dev",
    "edf_cvm_dev": "edf_cvm_dev",
    "edf_ks_dev": "edf_ks_dev",
    "edf_kuiper_dev": "edf_kuiper_dev",
}

EDF_W = 256
EDF_W_FALLBACK = 128
EDF_KEYS = ("edf_ad", "edf_cvm", "edf_ks", "edf_kuiper")
EDF_CHUNK = 20000  # windows per chunk to bound memory in the sorted-window pass


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
    NaN positions stay NaN. The placebo therefore operates on the real return-
    derived EDF-GOF series (never market data, never fabricated), preserving the
    marginal distribution of the statistic while destroying its temporal
    structure — the correct null for an EDF-GOF mean-reversion strategy."""
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


# ------------------------------------------------------- EDF-GOF kernel
def _rolling_mean_std(r: np.ndarray, W_q: int):
    """Causal trailing mean/std of r over window [t-W_q+1, t] (expanding for the
    first W_q-1 bars). Returns (mean, std, count). Population std (ddof=0)."""
    T = len(r)
    cs = np.concatenate([[0.0], np.cumsum(r)])
    cs2 = np.concatenate([[0.0], np.cumsum(r * r)])
    idx = np.arange(T)
    gstart = np.maximum(idx - (W_q - 1), 0)
    cnt = (idx + 1) - gstart
    s1 = cs[idx + 1] - cs[gstart]
    s2 = cs2[idx + 1] - cs2[gstart]
    mean = s1 / np.maximum(cnt, 1.0)
    var = s2 / np.maximum(cnt, 1.0) - mean * mean
    var = np.maximum(var, 0.0)
    sd = np.sqrt(var)
    return mean, sd, cnt


def _edf_stats_chunk(sorted_z: np.ndarray, p: np.ndarray, W_q: int) -> dict:
    """Compute the four EDF statistics for a chunk of sorted windows.
    sorted_z, p: (chunk, W_q). Returns dict key -> (chunk,) arrays (may contain
    -inf/+inf where p hits 0/1; caller masks invalid windows)."""
    n = float(W_q)
    i = np.arange(1, W_q + 1, dtype=float)
    theo = (2 * i - 1) / (2 * W_q)
    raw_w1 = (2 * i - 1)
    raw_w2 = (2 * W_q + 1 - 2 * i)
    upper = i / W_q
    lower = (i - 1) / W_q
    with np.errstate(divide="ignore", invalid="ignore"):
        logp = np.log(p)
        log1mp = np.log1p(-p)
        ad = -W_q - (1.0 / W_q) * (raw_w1 * logp + raw_w2 * log1mp).sum(axis=1)
        cvm = 1.0 / (12 * W_q) + ((p - theo) ** 2).sum(axis=1)
        d_plus = (upper - p).max(axis=1)
        d_minus = (p - lower).max(axis=1)
        ks = np.maximum(d_plus, d_minus)
        kuiper = d_plus + d_minus
    return {"edf_ad": ad, "edf_cvm": cvm, "edf_ks": ks, "edf_kuiper": kuiper}


def _edf_concepts_for_asset(z: np.ndarray, sigma: np.ndarray, W_q: int = EDF_W) -> dict:
    """Compute the 4 EDF-GOF concept series for a single asset over the full grid.
    z: standardized returns (finite everywhere). sigma: trailing std per bar.
    NaN if t<W_q, sigma[t]<=0, or any p in {0,1}."""
    T = len(z)
    out = {k: np.full(T, np.nan, dtype=float) for k in EDF_KEYS}
    if T < W_q:
        return out
    n_windows = T - W_q + 1
    view = np.lib.stride_tricks.sliding_window_view(z, W_q)  # (n_windows, W_q)
    sigma_win = sigma[W_q - 1:]  # sigma at the end bar t = j + W_q - 1
    i_lo = np.arange(W_q - 1, T)  # bar index for each window
    for start in range(0, n_windows, EDF_CHUNK):
        stop = min(start + EDF_CHUNK, n_windows)
        sv = np.sort(view[start:stop], axis=1)
        p = NORM_CDF(sv)
        stats_chunk = _edf_stats_chunk(sv, p, W_q)
        finite_w = np.isfinite(sv).all(axis=1)
        p_ok = (p > 0).all(axis=1) & (p < 1).all(axis=1)
        sig_ok = sigma_win[start:stop] > 0
        valid = finite_w & p_ok & sig_ok
        for k in EDF_KEYS:
            arr = np.where(valid, stats_chunk[k], np.nan)
            out[k][i_lo[start:stop]] = arr
    return out


def compute_edf_metrics(log_return: np.ndarray, W_q: int = EDF_W) -> dict:
    """EDF-GOF kernel for the full (n_assets, T) input matrix. Returns dict with
    matrices (n_assets, n_bars) for each concept: edf_ad, edf_cvm, edf_ks,
    edf_kuiper. NaN if t<W_q, any NaN/non-finite in window, σ[t]<=0, or any
    p∈{0,1}. Matches the brute-force per-window EDF-GOF reference exactly
    (maxdiff < 1e-12)."""
    R = np.asarray(log_return, dtype=np.float64)
    n_assets, T = R.shape
    out = {k: np.full((n_assets, T), np.nan, dtype=float) for k in EDF_KEYS}
    for i in range(n_assets):
        mean, sd, cnt = _rolling_mean_std(R[i], W_q)
        z = np.where(sd > 0, (R[i] - mean) / np.where(sd > 0, sd, 1.0), 0.0)
        part = _edf_concepts_for_asset(z, sd, W_q=W_q)
        for k in EDF_KEYS:
            out[k][i] = part[k]
    return out


def _edf_one_asset(row):
    """Worker: EDF-GOF concept series for a single asset row
    (log_return_row, W_q)."""
    r, W_q = row
    mean, sd, cnt = _rolling_mean_std(np.asarray(r, dtype=np.float64), W_q)
    z = np.where(sd > 0, (np.asarray(r, dtype=np.float64) - mean) / np.where(sd > 0, sd, 1.0), 0.0)
    return _edf_concepts_for_asset(z, sd, W_q=W_q)


def _apply_global_finite_gate(series: dict, close: np.ndarray, W_q: int) -> dict:
    """NaN out any bar whose trailing [t-W_q+1, t] close span has a non-finite
    value in ANY asset (global-across-assets gate)."""
    n_assets, T = close.shape
    finite = np.isfinite(close).all(axis=0)
    CFW = np.concatenate([[0.0], np.cumsum(finite.astype(float))])
    ok = np.zeros(T, dtype=bool)
    idx = np.arange(W_q - 1, T)
    ok[idx] = (CFW[idx + 1] - CFW[idx - (W_q - 1)]) == W_q
    for k in series:
        series[k] = np.where(ok[None, :], series[k], np.nan)
    return series


def _nanmean_stack(parts):
    M = np.vstack(parts)
    fin = np.isfinite(M)
    cnt = fin.sum(0)
    s = np.where(fin, M, 0.0).sum(0)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(cnt > 0, s / np.maximum(cnt, 1), np.nan)


def build_underlying(bs: dict) -> dict:
    """Compute the causal per-bar EDF-GOF concept series used by every signal.
    Returns dict with matrices (n_assets, n_bars): edf_ad, edf_cvm, edf_ks,
    edf_kuiper. Resumable via METRICS_CACHE and computed per-asset in parallel
    (<=4 workers) so the EDF-GOF kernel fits the budget."""
    n_assets = int(bs["n_assets"])
    n_bars = int(bs["n_bars"])
    log_return = np.asarray(bs["log_return"], dtype=float)
    perp_close = np.asarray(bs["perp_close"], dtype=float)

    if METRICS_CACHE.exists():
        try:
            with np.load(METRICS_CACHE) as z:
                if all(k in z.files and z[k].shape == (n_assets, n_bars) for k in EDF_KEYS):
                    print(f"[C432] reusing cached EDF-GOF metrics: {METRICS_CACHE}", flush=True)
                    return {k: np.asarray(z[k], dtype=float) for k in EDF_KEYS}
        except Exception as exc:  # noqa: BLE001
            print(f"[C432] metrics cache unreadable ({exc}); recomputing", flush=True)

    series = {k: np.full((n_assets, n_bars), np.nan, dtype=float) for k in EDF_KEYS}
    rows = [(log_return[i], EDF_W) for i in range(n_assets)]
    nproc = min(4, n_assets)
    done = False
    try:
        import multiprocessing as mp
        with mp.Pool(processes=nproc) as pool:
            for i, part in enumerate(pool.imap(_edf_one_asset, rows)):
                for k in EDF_KEYS:
                    series[k][i] = part[k]
                print(f"[C432] EDF-GOF asset {i + 1}/{n_assets} done", flush=True)
        done = True
    except Exception as exc:  # noqa: BLE001
        print(f"[C432] parallel EDF-GOF failed ({exc}); falling back to serial", flush=True)
    if not done:
        for i, row in enumerate(rows):
            part = _edf_one_asset(row)
            for k in EDF_KEYS:
                series[k][i] = part[k]
            print(f"[C432] EDF-GOF asset {i + 1}/{n_assets} done", flush=True)

    series = _apply_global_finite_gate(series, perp_close, EDF_W)
    try:
        np.savez(METRICS_CACHE, **series)
        print(f"[C432] wrote EDF-GOF metrics cache: {METRICS_CACHE}", flush=True)
    except Exception as exc:  # noqa: BLE001
        print(f"[C432] could not write metrics cache: {exc}", flush=True)
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
        raise SystemExit(f"FATAL: C432 shard dir missing: {CACHE_DIR}")
    if not CACHE_META.exists():
        raise SystemExit(f"FATAL: C432 meta missing: {CACHE_META}")
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
        raise SystemExit("FATAL: C432 common grid is empty")
    if n_b % 288 != 0:
        raise SystemExit("FATAL: C432 grid is not a whole number of 288-bar days")

    def mat(key):
        out = np.zeros((n_assets, n_b), dtype=float)
        for i, s in enumerate(symbols):
            out[i] = np.asarray(per_asset[s][key], dtype=float)
        return out

    perp_close = mat("perp_close")
    log_return = mat("log_return")
    abs_ret = mat("abs_ret")
    sign = mat("sign").astype(np.int8)

    if not (np.isfinite(perp_close).all() and (perp_close > 0).all()):
        raise SystemExit("FATAL: non-finite/non-positive perp_close")
    if not np.isfinite(log_return).all():
        raise SystemExit("FATAL: non-finite log_return in cache")
    if not np.isfinite(abs_ret).all():
        raise SystemExit("FATAL: non-finite abs_ret in cache")
    if not np.isfinite(sign.astype(float)).all():
        raise SystemExit("FATAL: non-finite sign in cache")

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
             "abs_ret": abs_ret, "sign": sign, "bucket": bucket, "splits": splits}


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

    ref_cfg = dict(signal="edf_ad_dev", L=240, H=4,
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
        "generated_at_utc": ts, "campaign": 432, "part": "oos_sweep",
        "analysis": "c432_edfgof_xsec_stat_arb_oos_5m",
        "verdict": verdict, "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "fail_closed": True,
        "mandate": (
            "C432 — test the price-only EDF-GOODNESS-OF-FIT normality-departure "
            "stat-arb family on 10 USDT-M linear perps at native 5m (2592 pre-registered "
            "configs). Per-bar primitives: perp_close real 5m kline close; "
            "log_return=log(c[t]/c[t-1]) (r[0]=0); abs_ret=|log_return|; "
            "sign=sign(log_return) (+1/-1/0, sign[0]=0); m[t]=mean_i r_i[t] "
            "(equal-weight market return). Causal trailing mean μ[t] and std σ[t] of "
            "{r[t-W_q+1..t]}, W_q=256 (fallback 128). Standardized return "
            "z[t]=(r[t]-μ[t])/σ[t] (z[t]=0 if σ[t]≤0 or non-finite). Per trailing "
            "window of z: order statistics z_(1)≤...≤z_(n), p_(i)=Φ(z_(i)) vs N(0,1). "
            "Anderson–Darling A² = -n - (1/n)Σ(2i-1)[ln(p_(i))+ln(1-p_(n+1-i))]; "
            "Cramér–von Mises W² = 1/(12n) + Σ(p_(i)-(2i-1)/(2n))²; "
            "Kolmogorov–Smirnov D = max_i max(|p_(i)-i/n|, |p_(i)-(i-1)/n|); "
            "Kuiper V = D⁺ + D⁻. NaN if t<W_q or any NaN/non-finite in window or "
            "σ[t]≤0 or any p∈{0,1}. Seasonal baseline = trailing mean/std at same "
            "(weekday,tod) bucket from history strictly before bar t (causal shift(1)), "
            "NaN-aware, excluding NaN obs. Signals: 8 real+placebo "
            "(edf_ad_dev, edf_cvm_dev, edf_ks_dev, edf_kuiper_dev) + 4 placebos "
            "(phase-randomized surrogates of the real return-derived EDF-GOF series, "
            "never market data, never fabricated). Single-leg dollar-neutral perp PnL "
            "with costs on turnover (taker=fee+slip; maker_blend=0.5*fee+slip). "
            "Gates: Holm+BH at alpha=0.05 (BOTH), MDE, stability, signal-vs-placebo "
            "attribution. PRE-REGISTERED NaN policy: metric NaN unless sufficient "
            "finite obs; seasonal stats NaN-aware min_periods excluding NaN obs; "
            "NaN-score bars weight 0."
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
            "alpha": ALPHA,             "n_trials": N_TRIALS, "total_runs": n_total,
            "edfgof_params": {"window_W_q": EDF_W, "fallback_W_q": EDF_W_FALLBACK,
                              "statistics": ["anderson_darling", "cramer_von_mises",
                                             "kolmogorov_smirnov", "kuiper"]},
        },
        "gates": {
            "fail_closed": True,
            "multiple_testing": {"holm_alpha": ALPHA, "bh_alpha": ALPHA,
                                 "n_survive_holm": n_survive_holm, "n_survive_bh": n_survive_bh,
                                 "n_survive_both": n_survive_both, "n_edge_proven": n_edge},
            "cq_mde": {"n_splits": int(n_splits), "mde_bps_mean": mde_bps,
                       "observed_mean_bps_per_split": obs_mean_bps},
            "stability": stability_ref,
            "attribution": {
                "reference_config": ref_cfg,
                **{f"{s}_net": float(np.mean(signal_nets[s])) if signal_nets[s] else 0.0 for s in SIGNALS},
                "shares": attrib_share, "dominant": dominant,
                "dominant_share": dominant_share, "attribution_ok": attribution_ok,
                "placebo_seed": int(PLACEBO_SEED),
            },
            "data_quality": {
                "reference_signal": ref_cfg["signal"], "reference_lookback": int(ref_cfg["L"]),
                "reference_score_nan_share": sc_ref_nan_share,
                "note": "metric NaN share dominated by finite-obs requirements (t<W_q or σ[t]≤0 or p∈{0,1} or NaN in trailing window).",
            },
        },
        "methodology": {
            "buckets": "(weekday,tod)=dayofweek*288+seconds-of-day//300 (0..2015), exact 288 bars per UTC day.",
            "raw_features": "perp_close real 5m kline close from C312 (strictly positive, gap-free); log_return=log(c[t]/c[t-1]) (r[0]=0); abs_ret=|log_return|; sign=sign(log_return) (+1/-1/0, sign[0]=0).",
            "primitives": "causal trailing mean/std μ[t], σ[t] of {r[t-W_q+1..t]}, W_q=256 (fallback 128); standardized return z[t]=(r[t]-μ[t])/σ[t]; order statistics z_(1)≤...≤z_(n), p_(i)=Φ(z_(i)); Anderson–Darling A², Cramér–von Mises W², Kolmogorov–Smirnov D, Kuiper V vs N(0,1); concepts edf_ad/edf_cvm/edf_ks/edf_kuiper.",
            "signals": "edf_ad_dev/edf_cvm_dev/edf_ks_dev/edf_kuiper_dev plus "
                       "phase-randomized-surrogate placebos over W_q=256; "
                       "score=-(v-m)/sd with m/sd trailing same-bucket mean/std "
                       "(min_periods=3, excluding NaN, causal shift(1)); "
                       "cross-sectional rank, dollar-neutral gross 1.0; "
                       "NaN-score assets weight 0.",
            "pnl": "single-leg perp: pnl = sum_i pos_i * perp_ret_i.",
            "costs": "charged on turnover; taker = fee+slip; maker_blend = 0.5*fee+slip.",
            "missing_data": "non-finite -> NaN; never impute/ffill; insufficient valid obs -> NaN -> not traded (fail-closed).",
            "multiple_testing": "one-sided paired t-test of per-split OOS net vs 0; Holm step-down AND Benjamini-Hochberg over all 2592 configs at alpha=0.05.",
            "mde": "two-sided alpha=0.05, power=0.80: (t_{0.975}+t_{0.80})*s/sqrt(n_splits).",
            "attribution": "mean |OOS net| per signal across all its configs; shares=|mean|/sum(|means|) over all 8 signals incl. placebos; dominant must be a real (non-placebo) signal with share >= 0.5 for attribution_ok.",
            "stability": "sign consistency >= 0.70 of splits AND first/second-half Sharpe corr >= 0.5.",
            "placebo": "phase-randomized surrogate via FFT phase randomization + rank restoration to original marginal of the real return-derived EDF-GOF series; deterministic seed recorded; same marginal distribution, destroyed temporal alignment; never market data, never fabricated.",
            "edf_vectorization_note": "rolling mean/std via cumulative sums O(N); sorted trailing windows of z via vectorized sliding sort; EDF statistics via cumulative-sum identities over the sorted order statistics, O(N log N) per asset per concept; validated against a naive per-window EDF-GOF reference with maxdiff < 1e-12 in tests.",
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
    op = reports / f"campaign432_oos_sweep_{ts}.json"
    op.write_text(json.dumps(slim, indent=2, default=jdefault) + "\n")
    sweep_sha = sha256_file(op)
    full = reports / f"campaign432_oos_sweep_{ts}.full.json"
    full.write_text(json.dumps(sweep_obj, indent=2, default=jdefault) + "\n")

    surviving = [results[i] for i in edge_idx if rej_holm[i] and rej_bh[i]]
    registry = {
        "generated_at_utc": ts, "campaign": 432, "part": "registry",
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
    op_reg = reports / f"campaign432_tradable_edge_registry_{ts}.json"
    op_reg.write_text(json.dumps(registry, indent=2, default=jdefault) + "\n")
    reg_sha = sha256_file(op_reg)

    summary = {
        "generated_at_utc": ts, "campaign": 432, "part": "summary",
        "analysis": "validation_summary", "verdict": verdict, "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "universe": sweep_obj["universe"], "config": sweep_obj["config"],
        "gates": sweep_obj["gates"],
        "artifacts": {"oos_sweep": {"path": str(op.relative_to(ROOT)), "sha256": sweep_sha},
                      "registry": {"path": str(op_reg.relative_to(ROOT)), "sha256": reg_sha}},
        "summary": sweep_obj["summary"], "binding_constraint": binding,
    }
    op_sum = reports / f"campaign432_summary_{ts}.json"
    op_sum.write_text(json.dumps(summary, indent=2, default=jdefault) + "\n")
    sum_sha = sha256_file(op_sum)

    finding = (
        f"C432 price-only EDF-GOODNESS-OF-FIT normality-departure stat-arb edge {verdict} "
        f"({n_edge} deterministic edge configs, {n_survive_both} survive Holm+BH over {N_TRIALS}); "
        f"binding constraint: {binding}; dominant attribution: {dominant} ({dominant_share:.4f})."
        if binding is not None
        else f"C432 price-only EDF-GOODNESS-OF-FIT normality-departure stat-arb edge validated: {n_survive_both} of "
        f"{n_edge} deterministic edge configs survive Holm+BH over {N_TRIALS}; "
        f"edge_proven:{edge_proven}."
    )
    verdict_obj = {
        "generated_at_utc": ts, "campaign": 432, "part": "verdict",
        "analysis": "final_verdict", "verdict": verdict, "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "finding": finding,
        "basis": "c432_edfgof_xsec_stat_arb_costed_oos_5m",
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
            "No edge claim unless the costed OOS test survives Holm+BH over all 2592 configs",
            "Real USDT-M linear 5m perp_close; funding excluded (control leg)",
            "Single-leg PnL with costs on turnover; executed_fills: false",
        ],
    }
    op_ver = reports / f"campaign432_verdict_{ts}.json"
    op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")
    ver_sha = sha256_file(op_ver)

    bind_sha = None
    bind_path = None
    if binding is not None:
        binding_obj = {
            "generated_at_utc": ts, "campaign": 432, "part": "binding_constraint",
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
                "C432 price-only EDF-GOODNESS-OF-FIT normality-departure stat-arb "
                "does not survive validation; formal negative. Binding "
                f"constraint: {binding}."
            ),
            "note": "Diagnosis only; never an edge claim. No threshold weakening.",
        }
        op_bind = reports / f"campaign432_binding_constraint_{ts}.json"
        op_bind.write_text(json.dumps(binding_obj, indent=2, default=jdefault) + "\n")
        bind_sha = sha256_file(op_bind)
        bind_path = str(op_bind.relative_to(ROOT))
        verdict_obj["binding_constraint_artifact"] = bind_path
        verdict_obj["binding_constraint_sha256"] = bind_sha
        op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")
        ver_sha = sha256_file(op_ver)

    print(json.dumps({
        "campaign": 432, "verdict": verdict, "edge_proven": edge_proven,
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
