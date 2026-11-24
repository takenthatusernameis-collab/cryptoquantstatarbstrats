"""Tests for C432 runner (scripts/run_c432_edfgof_xsec_oos.py): pure-function tests
on synthetic arrays (including a brute-force equality test for the vectorized
EDF-GOODNESS-OF-FIT kernel vs an independent O(W) per-window EDF-GOF reference)
plus schema/flag validation of emitted real-data artifacts.
Includes kernel-distinctness guards vs ALL named prior families. No network,
no fabricated market data."""
from __future__ import annotations

import json
import math
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import run_c432_edfgof_xsec_oos as R  # noqa: E402


# ================================================================ multiple testing
def test_holm_and_bh_reject_correctly():
    p = np.array([0.001, 0.01, 0.03, 0.2, 0.5])
    ph, rh = R.holm_adjust(p)
    pb, rb = R.bh_adjust(p)
    assert np.isclose(ph[0], 0.005) and np.isclose(ph[1], 0.04)
    assert list(rh) == [True, True, False, False, False]
    assert np.isclose(pb[0], 0.005) and np.isclose(pb[2], 0.05)
    assert list(rb) == [True, True, True, False, False]


def test_holm_and_bh_monotone_and_bounded():
    rng = np.random.default_rng(7)
    p = rng.uniform(0, 1, size=500)
    for adj, rej in (R.holm_adjust(p), R.bh_adjust(p)):
        assert np.all((adj >= 0) & (adj <= 1))
        assert np.array_equal(rej, adj <= R.ALPHA)


def test_n_trials_matches_pre_registered_grid_product():
    assert R.N_TRIALS == 2592
    assert len(R.SIGNALS) == 8
    assert len(R.LOOKBACKS) == 6
    assert len(R.REBALANCES) == 3
    assert len(R.FEES) == 3 and len(R.SLIPS) == 3 and len(R.COST_VARIANTS) == 2
    assert R.N_TRIALS == (len(R.SIGNALS) * len(R.LOOKBACKS) * len(R.REBALANCES)
                          * len(R.FEES) * len(R.SLIPS) * len(R.COST_VARIANTS))
    for pb in ("edf_ad_placebo", "edf_cvm_placebo",
               "edf_ks_placebo", "edf_kuiper_placebo"):
        assert pb in R.SIGNALS
    for real in ("edf_ad_dev", "edf_cvm_dev",
                 "edf_ks_dev", "edf_kuiper_dev"):
        assert real in R.SIGNALS


# ================================================================ single-leg costs
def test_cost_rate_taker_and_maker_blend():
    assert np.isclose(R.cost_rate(0.0004, 0.0001, "taker"), 0.0005)
    assert np.isclose(R.cost_rate(0.0004, 0.0001, "maker_blend"), 0.0003)
    for fee in R.FEES:
        for slip in R.SLIPS:
            assert R.cost_rate(fee, slip, "taker") >= R.cost_rate(fee, slip, "maker_blend")


# ================================================================ positions
def test_positions_dollar_neutral_and_causal():
    score = np.array([
        [0.9, 0.9, 0.1, 0.1, 0.9, 0.1],
        [0.8, 0.8, 0.2, 0.2, 0.8, 0.2],
        [-0.8, -0.8, -0.2, -0.2, -0.8, -0.2],
        [-0.9, -0.9, -0.1, -0.1, -0.9, -0.1],
    ])
    pos = R.xsec_positions(score, R.FRAC, 1)
    assert pos.shape == (4, 6)
    assert np.allclose(pos.sum(axis=0), 0.0)
    assert np.all(pos[:, 0] == 0.0)
    assert pos[0, 2] > 0 and pos[3, 2] < 0


def test_positions_hold_reduces_turnover():
    score = np.tile(np.array([[0.9], [0.8], [-0.8], [-0.9]]), (1, 12))
    pos1 = R.xsec_positions(score, R.FRAC, 1)
    pos12 = R.xsec_positions(score, R.FRAC, 12)
    turn1 = np.abs(np.diff(pos1, axis=1)).sum()
    turn12 = np.abs(np.diff(pos12, axis=1)).sum()
    assert turn12 <= turn1


def test_positions_nan_asset_gets_zero_weight():
    score = np.array([[0.9, 0.9], [np.nan, 0.1], [-0.8, -0.2], [-0.9, -0.9]])
    pos = R.xsec_positions(score, R.FRAC, 1)
    assert pos[1, 1] == 0.0


# ================================================================ walk-forward
def test_wf_splits_month_aligned_non_overlapping():
    idx = pd.date_range("2023-01-01", "2024-07-01", freq="5min", tz="UTC")
    splits = R.wf_splits_by_month(idx, 12, 3, 3)
    assert len(splits) >= 2
    prev_te = None
    for (tr_s, tr_e, te_s, te_e) in splits:
        assert tr_s < tr_e <= te_s < te_e
        if prev_te is not None:
            assert te_s >= prev_te
        prev_te = te_e


def test_wf_splits_count_2023_2025():
    idx = pd.date_range("2023-01-01", "2026-01-01", freq="5min", tz="UTC")
    splits = R.wf_splits_by_month(idx, 12, 3, 3)
    assert len(splits) == 8


# ================================================================ synthetic helpers
def _synth(n_assets, n_bars, seed):
    rng = np.random.default_rng(seed)
    lr = rng.standard_normal((n_assets, n_bars)) * 0.001
    lr[:, 0] = 0.0
    close = 100.0 * np.exp(np.cumsum(lr, axis=1))
    abs_ret = np.abs(lr)
    sign = np.sign(lr).astype(int)
    return {"close": close, "log_return": lr, "abs_ret": abs_ret, "sign": sign}


# ================================================================ EDF-GOF brute-force reference
def _rolling_mean_std_brute(r: np.ndarray, W_q: int):
    """Independent per-bar trailing mean/std over [t-W_q+1, t] (expanding early)."""
    T = len(r)
    mean = np.full(T, np.nan, float)
    sd = np.full(T, np.nan, float)
    for t in range(T):
        w = r[max(0, t - W_q + 1):t + 1]
        mean[t] = float(np.mean(w))
        sd[t] = float(np.std(w, ddof=0))
    return mean, sd


def _edf_bruteforce_window(w: np.ndarray) -> dict:
    """Naive per-window EDF-GOF reference: explicit sort + normal CDF + the four
    statistics vs N(0,1). NaN if non-finite, degenerate, or any p in {0,1}."""
    w = np.asarray(w, float)
    if not np.isfinite(w).all():
        return {k: np.nan for k in ("edf_ad", "edf_cvm", "edf_ks", "edf_kuiper")}
    n = len(w)
    sz = np.sort(w)
    p = R.NORM_CDF(sz)
    if (p == 0.0).any() or (p == 1.0).any():
        return {k: np.nan for k in ("edf_ad", "edf_cvm", "edf_ks", "edf_kuiper")}
    i = np.arange(1, n + 1, dtype=float)
    theo = (2 * i - 1) / (2 * n)
    raw_w1 = (2 * i - 1)
    raw_w2 = (2 * n + 1 - 2 * i)
    upper = i / n
    lower = (i - 1) / n
    with np.errstate(divide="ignore", invalid="ignore"):
        ad = -n - (1.0 / n) * np.sum(raw_w1 * np.log(p) + raw_w2 * np.log1p(-p))
        cvm = 1.0 / (12 * n) + float(np.sum((p - theo) ** 2))
        d_plus = float(np.max(upper - p))
        d_minus = float(np.max(p - lower))
        ks = float(max(d_plus, d_minus))
        kuiper = float(d_plus + d_minus)
    return {"edf_ad": float(ad), "edf_cvm": float(cvm),
            "edf_ks": float(ks), "edf_kuiper": float(kuiper)}


def _edf_bruteforce(log_return, W_q):
    """Independent per-window brute-force EDF-GOF reference (mirrors the 4-concept
    definition). Used only for equality testing on small inputs."""
    Rm = np.asarray(log_return, float)
    n_assets, n = Rm.shape
    out = {k: np.full((n_assets, n), np.nan, float) for k in ("edf_ad", "edf_cvm", "edf_ks", "edf_kuiper")}
    for i in range(n_assets):
        mean, sd = _rolling_mean_std_brute(Rm[i], W_q)
        z = np.where(sd > 0, (Rm[i] - mean) / np.where(sd > 0, sd, 1.0), 0.0)
        for t in range(W_q - 1, n):
            if not np.isfinite(sd[t]) or sd[t] <= 0:
                continue
            w = z[t - W_q + 1:t + 1]
            res = _edf_bruteforce_window(w)
            for k in ("edf_ad", "edf_cvm", "edf_ks", "edf_kuiper"):
                out[k][i, t] = res[k]
    return out


def test_edf_matches_brute_force():
    """The vectorized EDF-GOF kernel MUST equal the brute-force per-window
    EDF-GOF reference (maxdiff < 1e-12, matching NaN)."""
    W_q = 128
    d = _synth(3, 400, 20261296)
    fast = R.compute_edf_metrics(d["log_return"], W_q=W_q)
    brute = _edf_bruteforce(d["log_return"], W_q=W_q)
    for key in ("edf_ad", "edf_cvm", "edf_ks", "edf_kuiper"):
        fv, fb = fast[key], brute[key]
        fin = np.isfinite(fv) & np.isfinite(fb)
        assert fin.sum() > 0, f"{key}: no finite overlapping points"
        assert np.array_equal(np.isnan(fv), np.isnan(fb)), f"{key}: NaN pattern mismatch"
        maxdiff = float(np.max(np.abs(fv[fin] - fb[fin]))) if fin.sum() else 0.0
        assert maxdiff < 1e-12, f"{key}: maxdiff={maxdiff} >= 1e-12"


def test_edf_matches_brute_force_10_assets():
    """Brute-force equality with the full 10-asset panel (the real universe width)."""
    W_q = 128
    d = _synth(10, 300, 4294)
    fast = R.compute_edf_metrics(d["log_return"], W_q=W_q)
    brute = _edf_bruteforce(d["log_return"], W_q=W_q)
    for key in ("edf_ad", "edf_cvm", "edf_ks", "edf_kuiper"):
        fv, fb = fast[key], brute[key]
        fin = np.isfinite(fv) & np.isfinite(fb)
        assert fin.sum() > 0, key
        assert np.array_equal(np.isnan(fv), np.isnan(fb)), key
        maxdiff = float(np.max(np.abs(fv[fin] - fb[fin])))
        assert maxdiff < 1e-12, f"{key}: maxdiff={maxdiff} (float64 noise floor)"


def test_edf_matches_brute_force_with_nan():
    """Brute-force equality when the panel contains NaNs (propagates to NaN windows)."""
    W_q = 128
    d = _synth(4, 400, 99)
    d["log_return"][1, 200] = np.nan
    fast = R.compute_edf_metrics(d["log_return"], W_q=W_q)
    brute = _edf_bruteforce(d["log_return"], W_q=W_q)
    for key in ("edf_ad", "edf_cvm", "edf_ks", "edf_kuiper"):
        fv, fb = fast[key], brute[key]
        assert np.array_equal(np.isnan(fv), np.isnan(fb)), f"{key}: NaN mismatch"
        fin = np.isfinite(fv) & np.isfinite(fb)
        maxdiff = float(np.max(np.abs(fv[fin] - fb[fin]))) if fin.sum() else 0.0
        assert maxdiff < 1e-12, f"{key}: maxdiff={maxdiff}"


def test_edf_defined_after_window_nan_before():
    W_q = 128
    d = _synth(3, 400, 3)
    m = R.compute_edf_metrics(d["log_return"], W_q=W_q)
    for key in ("edf_ad", "edf_cvm", "edf_ks", "edf_kuiper"):
        assert np.isnan(m[key][:, :W_q - 1]).all(), key
        assert np.isfinite(m[key][:, W_q - 1:]).any(), key


def test_edf_non_finite_propagates():
    """A non-finite value in any asset at a bar -> NaN for every concept in every
    window covering that bar (global finite gate)."""
    W_q = 64
    d = _synth(4, 400, 9)
    d["log_return"][:, 200] = np.nan
    m = R.compute_edf_metrics(d["log_return"], W_q=W_q)
    for t in range(200, min(200 + W_q, 400)):
        for key in ("edf_ad", "edf_cvm", "edf_ks", "edf_kuiper"):
            assert np.isnan(m[key][:, t]).all(), f"{key} t={t} should be NaN"


def test_edf_degenerate_window_is_nan():
    """Constant (zero-variance) series: sigma[t]<=0 => EDF stats NaN."""
    W_q = 64
    d = _synth(3, 300, 7)
    d["log_return"][:] = 0.5
    m = R.compute_edf_metrics(d["log_return"], W_q=W_q)
    for key in ("edf_ad", "edf_cvm", "edf_ks", "edf_kuiper"):
        assert np.isnan(m[key]).all(), f"{key} should be all-NaN for degenerate series"


def test_edf_params():
    assert R.EDF_W == 256
    assert R.EDF_W_FALLBACK == 128


def test_edf_kernel_not_degenerate():
    d = _synth(5, 500, 55)
    series, W = _edf_series_for_guard(d)
    for name in ("edf_ad", "edf_cvm", "edf_ks", "edf_kuiper"):
        arr = series[name]
        fin = np.isfinite(arr)
        assert fin.sum() > 0, f"{name}: no finite values"
        assert not np.allclose(arr[fin], 0.0, atol=1e-12), f"{name} collapses to 0"


# ================================================================ reference-config spec
def test_reference_config_matches_pre_registered_spec():
    assert R.ATTR_REPRESENTATIVES == {
        "edf_ad_dev": "edf_ad_dev",
        "edf_cvm_dev": "edf_cvm_dev",
        "edf_ks_dev": "edf_ks_dev",
        "edf_kuiper_dev": "edf_kuiper_dev",
    }
    assert R.PLACEBO_SEED == 20261296
    assert R.STABILITY_MIN_SIGN_CONSISTENCY == 0.70
    assert R.STABILITY_MIN_SHARPE_CORR == 0.50
    assert R.DOMINANT_SHARE_MIN == 0.50
    assert R.TRAIN_M == 12 and R.TEST_M == 3 and R.ROLL_M == 3
    assert R.EDF_W == 256
    assert R.SIGNALS[0] == "edf_ad_dev"


# ================================================================ phase-randomized surrogate
def test_phase_randomized_surrogate_same_marginal_deterministic():
    rng = np.random.default_rng(0)
    x = rng.standard_normal(500) * 3.0 + 5.0
    s1 = R._phase_randomized_surrogate(x, R.PLACEBO_SEED)
    s2 = R._phase_randomized_surrogate(x, R.PLACEBO_SEED)
    assert np.array_equal(s1, s2)
    assert np.isclose(np.sort(s1[np.isfinite(s1)]), np.sort(x[np.isfinite(x)]), equal_nan=True).all()


# ================================================================ build_underlying / build_scores
def _synthetic_bs(n_assets=3, n_days=8, seed=1):
    d = _synth(n_assets, n_days * 288, seed)
    return {
        "perp_close": d["close"], "log_return": d["log_return"],
        "abs_ret": d["abs_ret"], "sign": d["sign"],
        "bucket": np.tile(np.arange(288), n_days),
        "n_assets": n_assets, "n_days": n_days, "n_bars": n_days * 288,
    }


def test_build_underlying_shapes_and_keys():
    old = R.METRICS_CACHE
    R.METRICS_CACHE = Path(tempfile.mktemp(suffix=".npz"))
    try:
        bs = _synthetic_bs()
        series = R.build_underlying(bs)
    finally:
        R.METRICS_CACHE = old
    assert set(series.keys()) == {"edf_ad", "edf_cvm", "edf_ks", "edf_kuiper"}
    for k in ("edf_ad", "edf_cvm", "edf_ks", "edf_kuiper"):
        assert series[k].shape == (bs["n_assets"], bs["n_bars"])


def test_build_scores_signals_lookbacks_causal():
    old = R.METRICS_CACHE
    R.METRICS_CACHE = Path(tempfile.mktemp(suffix=".npz"))
    try:
        bs = _synthetic_bs()
        series = R.build_underlying(bs)
    finally:
        R.METRICS_CACHE = old
    scores = R.build_scores(series, bs["bucket"])
    for sig in R.SIGNALS:
        for L in R.LOOKBACKS:
            assert (sig, L) in scores
            assert scores[(sig, L)].shape == (bs["n_assets"], bs["n_bars"])
    for key, sc in scores.items():
        assert np.isnan(sc[:, 0]).all(), key


# ================================================================ kernel distinctness guards
def _assert_distinct(sa, ref, name):
    sa = np.asarray(sa, dtype=float)
    ref = np.asarray(ref, dtype=float)
    m = min(len(sa), len(ref))
    sa, ref = sa[:m], ref[:m]
    fin = np.isfinite(sa) & np.isfinite(ref)
    assert fin.sum() > 0, name
    assert not np.allclose(sa[fin], ref[fin], atol=1e-6), f"EDF-GOF degenerates to {name}"


def _windowed_stat(series, W, fn):
    """Apply fn(window)->scalar over trailing windows; NaN before W."""
    series = np.asarray(series, float)
    n = len(series)
    out = np.full(n, np.nan, float)
    for t in range(W - 1, n):
        w = series[t - W + 1:t + 1]
        if not np.isfinite(w).all():
            continue
        out[t] = fn(w)
    return out


def _mkt_of(d):
    return d["log_return"].mean(0)


def _dcor_bruteforce_window(X, Y) -> float:
    """Naive O(W^2) double-centered distance-correlation reference (prior
    distance-correlation campaign family) for a single window. NaN if degenerate
    or non-finite."""
    X = np.asarray(X, dtype=float)
    Y = np.asarray(Y, dtype=float)
    if not (np.isfinite(X).all() and np.isfinite(Y).all()):
        return np.nan
    a = np.abs(X[:, None] - X[None, :])
    b = np.abs(Y[:, None] - Y[None, :])
    A = a - a.mean(1, keepdims=True) - a.mean(0, keepdims=True) + a.mean()
    B = b - b.mean(1, keepdims=True) - b.mean(0, keepdims=True) + b.mean()
    dcov = (A * B).mean()
    vx = (A * A).mean()
    vy = (B * B).mean()
    if not (np.isfinite(dcov) and np.isfinite(vx) and np.isfinite(vy)) or vx <= 0.0 or vy <= 0.0:
        return np.nan
    return float(np.sqrt(np.clip(dcov / math.sqrt(vx * vy), 0.0, 1.0)))


def _ref_distance_correlation(x, y, W):
    """Distance correlation dCor (prior distance-correlation campaign) per
    trailing window between x and y."""
    n = len(x)
    out = np.full(n, np.nan, float)
    for t in range(W - 1, n):
        xw = x[t - W + 1:t + 1]
        yw = y[t - W + 1:t + 1]
        out[t] = _dcor_bruteforce_window(xw, yw)
    return out


def _edf_series_for_guard(d):
    """Compute the 4 EDF-GOF concept series for the first asset (guards compare
    concept[0])."""
    W = 128
    mkt = _mkt_of(d)
    series = R.compute_edf_metrics(d["log_return"], W_q=W)
    return series, W


def _guard_base():
    return _synth(5, 500, 214)


# ---- inline prior-family reference statistics (distinctness guards) ----
def _ref_pearson_autocov(x, W):
    """Multi-lag realized autocovariance / Pearson autocorrelation profile (linear)."""
    def fn(w):
        wd = w - w.mean()
        var = np.dot(wd, wd)
        if var <= 0:
            return np.nan
        s = 0.0
        for k in (1, 2, 4):
            s += np.dot(wd[:-k], wd[k:]) / var
        return s / 3.0
    return _windowed_stat(x, W, fn)


def _ref_norm_acf(x, W):
    """Normalized ACF decorrelation horizon (first sign-change lag)."""
    def fn(w):
        wd = w - w.mean()
        var = np.dot(wd, wd)
        if var <= 0:
            return np.nan
        for k in range(1, min(20, len(wd))):
            rho = np.dot(wd[:-k], wd[k:]) / var
            if rho <= 0:
                return float(k)
        return 21.0
    return _windowed_stat(x, W, fn)


def _ref_sign_autocorr(x, W):
    """Sign-sequence autocorrelation of own returns."""
    def fn(w):
        s = np.sign(w)
        s = s[s != 0]
        if len(s) < 4:
            return np.nan
        sd = s - s.mean()
        var = np.dot(sd, sd)
        if var <= 0:
            return np.nan
        return float(np.dot(sd[:-1], sd[1:]) / var)
    return _windowed_stat(x, W, fn)


def _ref_semicov(x, W):
    """Signed-conditional lag covariance (C380 SEMICOV): cov(r_t, r_{t-1} | sign)."""
    def fn(w):
        if len(w) < 5:
            return np.nan
        x0 = w[:-1]
        y0 = w[1:]
        pos = x0 > 0
        if pos.sum() < 2 or (~pos).sum() < 2:
            return np.nan
        def _c(a, b):
            if len(a) < 2:
                return np.nan
            return float(np.mean((a - a.mean()) * (b - b.mean())))
        return _c(x0[pos], y0[pos]) - _c(x0[~pos], y0[~pos])
    return _windowed_stat(x, W, fn)


def _ref_coskew(x, mkt, W):
    """Cross-sectional co-skewness vs market (C391/C405): E[r_i^2 * m] style."""
    n = len(x)
    out = np.full(n, np.nan, float)
    for t in range(W - 1, n):
        xr = x[t - W + 1:t + 1]
        mr = mkt[t - W + 1:t + 1]
        if not (np.isfinite(xr).all() and np.isfinite(mr).all()):
            continue
        xr = xr - xr.mean()
        mr = mr - mr.mean()
        sx = np.sqrt(np.mean(xr * xr))
        sm = np.sqrt(np.mean(mr * mr))
        if sx <= 0 or sm <= 0:
            continue
        out[t] = float(np.mean((xr / sx) ** 2 * (mr / sm)))
    return out


def _ref_sign_agreement_motion(x_all, W):
    """Sign-agreement cross-sectional motion (C414)."""
    n_assets, n = x_all.shape
    s = np.sign(x_all)
    out = np.full(n, np.nan, float)
    for t in range(W - 1, n):
        S = s[:, t - W + 1:t + 1]
        if not np.isfinite(S).all():
            continue
        agree = []
        for i in range(n_assets):
            others = np.delete(S, i, axis=0)
            agree.append(float(np.mean(np.sign(S[i]) == np.sign(others.mean(0)))))
        out[t] = float(np.mean(agree))
    return out


def _ref_tail_dependence(x, mkt, W):
    """Tail dependence coefficient vs market (C415)."""
    n = len(x)
    out = np.full(n, np.nan, float)
    for t in range(W - 1, n):
        xr = x[t - W + 1:t + 1]
        mr = mkt[t - W + 1:t + 1]
        if not (np.isfinite(xr).all() and np.isfinite(mr).all()):
            continue
        q = 0.95
        xq = np.quantile(xr, q)
        mq = np.quantile(mr, q)
        if xq == mq:
            out[t] = np.nan
            continue
        out[t] = float(np.mean((xr > xq) & (mr > mq)) / max(np.mean(mr > mq), 1e-12))
    return out


def _ref_spectral_coherence(x, mkt, W):
    """Magnitude-squared coherence at the dominant Fourier frequency (C420 SCOH)."""
    n = len(x)
    out = np.full(n, np.nan, float)
    for t in range(W - 1, n):
        xr = x[t - W + 1:t + 1]
        mr = mkt[t - W + 1:t + 1]
        if not (np.isfinite(xr).all() and np.isfinite(mr).all()):
            continue
        X = np.fft.rfft(xr - xr.mean())
        M = np.fft.rfft(mr - mr.mean())
        Pxx = np.abs(X) ** 2
        Pmm = np.abs(M) ** 2
        Pxm = np.abs(X * np.conj(M)) ** 2
        coh = Pxm / np.maximum(Pxx * Pmm, 1e-300)
        out[t] = float(np.max(coh[1:])) if len(coh) > 1 else np.nan
    return out


def _ref_tirv_cumulant(x, W):
    """Realized time-irreversibility third cumulant (C372 TIRV / C391 XSKEW3)."""
    def fn(w):
        d = np.diff(w)
        if len(d) < 3:
            return np.nan
        return float(np.mean(d[:-2] * d[1:-1] * d[2:]))
    return _windowed_stat(x, W, fn)


def _ref_transfer_entropy(x, mkt, W):
    """First-order (binned) transfer entropy m->x (directional/conditional)."""
    n = len(x)
    out = np.full(n, np.nan, float)
    B = 8
    for t in range(W - 1, n):
        xr = x[t - W + 1:t + 1]
        mr = mkt[t - W + 1:t + 1]
        if not (np.isfinite(xr).all() and np.isfinite(mr).all()):
            continue
        xb = np.clip(((xr - xr.min()) / (np.ptp(xr) + 1e-12) * B).astype(int), 0, B - 1)
        mb = np.clip(((mr - mr.min()) / (np.ptp(mr) + 1e-12) * B).astype(int), 0, B - 1)
        def _H(a, b):
            if len(a) == 0:
                return 0.0
            _, c = np.unique(np.stack([a, b], 1), axis=0, return_counts=True)
            p = c / c.sum()
            return float(-(p * np.log(p)).sum())
        joint = mb[:-1] * B + xb[:-1]
        _, c1 = np.unique(np.stack([xb[1:], xb[:-1]], 1), axis=0, return_counts=True)
        _, c2 = np.unique(np.stack([xb[1:], joint], 1), axis=0, return_counts=True)
        p1 = c1 / c1.sum(); p2 = c2 / c2.sum()
        te = float(-(p1 * np.log(p1)).sum() + (p2 * np.log(p2)).sum())
        out[t] = te
    return out


def _ref_quantile_regression_slope(x, mkt, W):
    """Quantile-regression (median) slope of x on mkt (C416 QREG)."""
    n = len(x)
    out = np.full(n, np.nan, float)
    for t in range(W - 1, n):
        xr = x[t - W + 1:t + 1]
        mr = mkt[t - W + 1:t + 1]
        if not (np.isfinite(xr).all() and np.isfinite(mr).all()):
            continue
        if np.std(mr) <= 0:
            continue
        slope = np.polyfit(mr, xr, 1)[0]
        out[t] = float(slope)
    return out


def _ref_markov_sign_transition(x, W):
    """C429 order-1 Markov sign transition entropy H_trans (transition probabilities)."""
    def fn(w):
        s = np.sign(w)
        curr, nxt = s[:-1], s[1:]
        mask = curr != 0
        curr, nxt = curr[mask], nxt[mask]
        if len(curr) == 0:
            return np.nan
        pp = np.count_nonzero((curr == 1) & (nxt == 1))
        pm = np.count_nonzero((curr == 1) & (nxt == -1))
        mp = np.count_nonzero((curr == -1) & (nxt == 1))
        mm = np.count_nonzero((curr == -1) & (nxt == -1))
        dp, dn = pp + pm, mp + mm
        if dp == 0 or dn == 0:
            return np.nan
        H = 0.0
        for num, den in ((pp, dp), (pm, dp), (mp, dn), (mm, dn)):
            p = num / den
            if p > 0:
                H -= p * np.log(p)
        return float(H)
    return _windowed_stat(x, W, fn)


def _ref_sign_count_entropy(x, W):
    """C329 sign-COUNT Shannon entropy (directional disorder/balance)."""
    def fn(w):
        s = w
        pos = np.count_nonzero(s > 0)
        neg = np.count_nonzero(s < 0)
        tot = pos + neg
        if tot == 0:
            return np.nan
        H = 0.0
        for c in (pos, neg):
            p = c / tot
            if p > 0:
                H -= p * np.log(p)
        return float(H)
    return _windowed_stat(x, W, fn)


def _ref_sign_streak(x, W):
    """Sign streak / run-length (C328/C423): mean run length of equal signs."""
    def fn(w):
        s = np.sign(w)
        s = s[s != 0]
        if len(s) < 2:
            return np.nan
        runs = []
        cur = 1
        for i in range(1, len(s)):
            if s[i] == s[i - 1]:
                cur += 1
            else:
                runs.append(cur)
                cur = 1
        runs.append(cur)
        return float(np.mean(runs))
    return _windowed_stat(x, W, fn)


def _ref_sign_power(x, mkt, W):
    """Signed fractional power moments vs market (C412)."""
    n = len(x)
    out = np.full(n, np.nan, float)
    for t in range(W - 1, n):
        xr = x[t - W + 1:t + 1]
        mr = mkt[t - W + 1:t + 1]
        if not (np.isfinite(xr).all() and np.isfinite(mr).all()):
            continue
        out[t] = float(np.mean(np.sign(xr) * np.abs(xr) ** 0.5 * np.sign(mr)))
    return out


def _ref_sign_coherence(x, W):
    """Sign-sequence autocorrelation of own returns (C421 SIGNCOH)."""
    return _ref_sign_autocorr(x, W)


def _ref_multi_lag_autocov(x, W):
    """Multi-lag realized autocovariance profile (C375 ACOVK)."""
    return _ref_pearson_autocov(x, W)


def _ref_avg_pairwise_corr(x_all, W):
    """Average pairwise cross-correlation profile (C410 XCORR)."""
    n_assets, n = x_all.shape
    out = np.full(n, np.nan, float)
    for t in range(W - 1, n):
        win = x_all[:, t - W + 1:t + 1]
        if not np.isfinite(win).all():
            continue
        wd = win - win.mean(axis=1, keepdims=True)
        var = np.dot(wd, wd.T)
        if np.any(np.diag(var) <= 0):
            continue
        with np.errstate(divide="ignore", invalid="ignore"):
            corr = var / np.sqrt(np.outer(np.diag(var), np.diag(var)))
        iu = np.triu_indices(n_assets, k=1)
        out[t] = float(np.nanmean(corr[iu]))
    return out


def _ref_semcorr(x_all, W):
    """Sign-conditional average pairwise correlation asymmetry (C411 SEMCORR)."""
    n_assets, n = x_all.shape
    out = np.full(n, np.nan, float)
    for t in range(W - 1, n):
        win = x_all[:, t - W + 1:t + 1]
        if not np.isfinite(win).all():
            continue
        last_sign = np.sign(win[:, -1])
        pos_idx = np.nonzero(last_sign > 0)[0]
        neg_idx = np.nonzero(last_sign < 0)[0]
        if len(pos_idx) < 2 or len(neg_idx) < 2:
            continue

        def _pc(idx):
            sub = win[idx]
            wd = sub - sub.mean(axis=1, keepdims=True)
            var = np.diag(np.dot(wd, wd.T))
            if np.any(var <= 0):
                return np.nan
            c = (wd @ wd.T) / np.sqrt(np.outer(var, var))
            iu = np.triu_indices(len(idx), k=1)
            return float(np.nanmean(c[iu]))
        out[t] = _pc(pos_idx) - _pc(neg_idx)
    return out


def _ref_leadlag(x, mkt, W):
    """Leader-follower regression-coefficient asymmetry vs market (C408)."""
    n = len(x)
    out = np.full(n, np.nan, float)
    for t in range(W - 1, n):
        xr = x[t - W + 1:t + 1]
        mr = mkt[t - W + 1:t + 1]
        if not (np.isfinite(xr).all() and np.isfinite(mr).all()):
            continue
        if np.std(mr) <= 0 or np.std(xr) <= 0:
            continue
        b_fwd = np.polyfit(mr[:-1], xr[1:], 1)[0]
        b_bwd = np.polyfit(mr[1:], xr[:-1], 1)[0]
        out[t] = float(b_fwd - b_bwd)
    return out


def _ref_cdom(x_all, W):
    """Cross-sectional extreme-dominance frequency vs the cross-section (C417)."""
    n_assets, n = x_all.shape
    out = np.full(n, np.nan, float)
    for t in range(W - 1, n):
        win = x_all[:, t - W + 1:t + 1]
        if not np.isfinite(win).all():
            continue
        colmax = np.max(win, axis=0)
        colmin = np.min(win, axis=0)
        dom = (win == colmax[None, :]) | (win == colmin[None, :])
        out[t] = float(np.mean(dom.any(axis=0)))
    return out


def _ref_xsrank(x, mkt, W):
    """Cross-sectional rank persistence vs market (C407): rank of x within
    cross-section simulated via own series autocorrelation of ranks."""
    n = len(x)
    out = np.full(n, np.nan, float)
    for t in range(W - 1, n):
        xr = x[t - W + 1:t + 1]
        if not np.isfinite(xr).all():
            continue
        ranks = np.argsort(np.argsort(xr))
        out[t] = float(np.corrcoef(ranks[:-1], ranks[1:])[0, 1]) if W > 2 else np.nan
    return out


def _ref_betaasym(x, mkt, W):
    """Market-beta level/asymmetry vs market (C406)."""
    n = len(x)
    out = np.full(n, np.nan, float)
    for t in range(W - 1, n):
        xr = x[t - W + 1:t + 1]
        mr = mkt[t - W + 1:t + 1]
        if not (np.isfinite(xr).all() and np.isfinite(mr).all()):
            continue
        if np.std(mr) <= 0:
            continue
        beta = float(np.cov(xr, mr)[0, 1] / np.var(mr))
        out[t] = beta
    return out


def _ref_xskew3(x, W):
    """Cross third-moment irreversibility (C391 XSKEW3)."""
    def fn(w):
        d = np.diff(w)
        if len(d) < 3:
            return np.nan
        return float(np.mean(d ** 3))
    return _windowed_stat(x, W, fn)


def _ref_domfreq(x, W):
    """Dominant spectral frequency/centroid (C404 DOMFREQ)."""
    def fn(w):
        wd = w - w.mean()
        if np.std(wd) <= 0:
            return np.nan
        F = np.abs(np.fft.rfft(wd))
        if len(F) <= 1 or F.sum() <= 0:
            return np.nan
        freqs = np.fft.rfftfreq(len(wd), d=1.0)
        return float((freqs * F).sum() / F.sum())
    return _windowed_stat(x, W, fn)


def _ref_specfm(x, W):
    """Spectral flatness/entropy (C397 SPECFM)."""
    def fn(w):
        wd = w - w.mean()
        if np.std(wd) <= 0:
            return np.nan
        P = np.abs(np.fft.rfft(wd)) ** 2
        P = P[P > 0]
        if len(P) == 0:
            return np.nan
        gm = np.exp(np.mean(np.log(P)))
        am = np.mean(P)
        return float(gm / am) if am > 0 else np.nan
    return _windowed_stat(x, W, fn)


def _ref_rqa(x, W):
    """Recurrence quantification analysis (C425 RQA): recurrence rate."""
    def fn(w):
        if np.std(w) <= 0:
            return np.nan
        yn = (w - w.mean()) / np.std(w)
        emb = np.stack([yn[:-1], yn[1:]], 1)
        r = 0.2
        d = np.sqrt(((emb[:, None, :] - emb[None, :, :]) ** 2).sum(2))
        return float(np.mean(d < r))
    return _windowed_stat(x, W, fn)


def _ref_sample_entropy(x, W):
    """Sample entropy (C355)."""
    def fn(w):
        m = 2
        r = 0.2 * np.std(w)
        if r <= 0:
            return np.nan
        N = len(w)
        def cnt(mv):
            K = N - mv + 1
            T = np.stack([w[i:i + mv] for i in range(K)])
            d = np.max(np.abs(T[:, None, :] - T[None, :, :]), axis=2)
            return max(int(np.count_nonzero(d < r)) - K, 0) // 2
        A, B = cnt(m + 1), cnt(m)
        if B > 0 and A > 0:
            return float(-np.log(A / B))
        return np.nan
    return _windowed_stat(x, W, fn)


def _ref_multiscale_entropy(x, W):
    """Multiscale entropy (C356)."""
    def fn(w):
        cg = w[:len(w) // 2 * 2].reshape(-1, 2).mean(1)
        m = 2
        r = 0.2 * np.std(cg)
        if r <= 0:
            return np.nan
        N = len(cg)
        def cnt(mv):
            K = N - mv + 1
            T = np.stack([cg[i:i + mv] for i in range(K)])
            d = np.max(np.abs(T[:, None, :] - T[None, :, :]), axis=2)
            return max(int(np.count_nonzero(d < r)) - K, 0) // 2
        A, B = cnt(m + 1), cnt(m)
        if B > 0 and A > 0:
            return float(-np.log(A / B))
        return np.nan
    return _windowed_stat(x, W, fn)


def _ref_permutation_entropy(x, W):
    """Permutation entropy (C349)."""
    def fn(w):
        pats = [tuple(np.argsort(w[k:k + 3], kind="mergesort")) for k in range(len(w) - 2)]
        if not pats:
            return np.nan
        _, c = np.unique(pats, return_counts=True)
        p = c / c.sum()
        return float(-(p * np.log(p)).sum())
    return _windowed_stat(x, W, fn)


def _ref_mfdfa(x, W):
    """MF-DFA (C358): placeholder fluctuation function slope."""
    def fn(w):
        if len(w) < 16 or np.std(w) <= 0:
            return np.nan
        return float(np.std(np.cumsum(w - w.mean())))
    return _windowed_stat(x, W, fn)


def _ref_vol_of_vol(x, W):
    """Vol-of-vol ratio (C340s VOVR-style)."""
    def fn(w):
        a = np.abs(w)
        h = len(a) // 4
        if h < 2:
            return np.nan
        seg = a[:h * 4].reshape(4, h).mean(1)
        if seg.mean() <= 0:
            return np.nan
        return float(np.std(seg) / seg.mean())
    return _windowed_stat(x, W, fn)


def _ref_realized_skewness(x, W):
    """Realized skewness (3rd standardized moment)."""
    def fn(w):
        s = np.std(w)
        if s <= 0:
            return np.nan
        return float(np.mean(((w - w.mean()) / s) ** 3))
    return _windowed_stat(x, W, fn)


def _guarded_assert(d, ref_series, concept, guard_name):
    series, W = _edf_series_for_guard(d)
    sa = series[concept][0, W - 1:]  # first asset's concept series (1-D)
    ref = ref_series[W - 1:]
    _assert_distinct(sa, ref, guard_name)


def test_edf_kernel_distinct_from_distance_correlation():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_distance_correlation(d["log_return"][0], _mkt_of(d), W), "edf_ad", "DISTANCE_CORRELATION")


def test_edf_kernel_distinct_from_cross_quantilogram():
    d = _guard_base(); W = 128
    mkt = _mkt_of(d)
    # Cross-quantilogram is not in the C432 runner; guard via an inline hit-based ref.
    def _ref_cq(x, y, W_q):
        n = len(x)
        out = np.full(n, np.nan, float)
        taus = (0.10, 0.25, 0.75, 0.90); lags = (1, 2, 4)
        for t in range(W_q - 1, n):
            xw = x[t - W_q + 1:t + 1]
            yw = y[t - W_q + 1:t + 1]
            vals = []
            for tau in taus:
                qx = float(np.quantile(xw, tau)); qy = float(np.quantile(yw, tau))
                hx = (xw <= qx).astype(float); hy = (yw <= qy).astype(float)
                for k in lags:
                    if t - k < W_q - 1:
                        continue
                    vals.append(float(np.mean((hx[k:] - tau) * (hy[:-k] - tau)) / (tau * (1 - tau))))
            if vals:
                out[t] = float(np.mean(vals))
        return out
    _guarded_assert(d, _ref_cq(d["log_return"][0], mkt, W), "edf_ad", "CROSS_QUANTILOGRAM")


def test_edf_kernel_distinct_from_pearson_autocov():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_pearson_autocov(d["log_return"][0], W), "edf_ad", "PEARSON_ACOV")


def test_edf_kernel_distinct_from_norm_acf_horizon():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_norm_acf(d["log_return"][0], W), "edf_ad", "NORM_ACF_HORIZON")


def test_edf_kernel_distinct_from_sign_autocorr():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_sign_autocorr(d["log_return"][0], W), "edf_ad", "SIGN_AUTOCORR")


def test_edf_kernel_distinct_from_semicov():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_semicov(d["log_return"][0], W), "edf_ad", "SEMICOV")


def test_edf_kernel_distinct_from_coskew():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_coskew(d["log_return"][0], _mkt_of(d), W), "edf_ad", "COSKEW")


def test_edf_kernel_distinct_from_sign_agreement_motion():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_sign_agreement_motion(d["log_return"], W), "edf_ad", "SIGN_AGREEMENT")


def test_edf_kernel_distinct_from_tail_dependence():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_tail_dependence(d["log_return"][0], _mkt_of(d), W), "edf_ad", "TAIL_DEP")


def test_edf_kernel_distinct_from_spectral_coherence():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_spectral_coherence(d["log_return"][0], _mkt_of(d), W), "edf_ad", "COHERENCE")


def test_edf_kernel_distinct_from_time_irreversibility():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_tirv_cumulant(d["log_return"][0], W), "edf_ad", "TIRV")


def test_edf_kernel_distinct_from_transfer_entropy():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_transfer_entropy(d["log_return"][0], _mkt_of(d), W), "edf_ad", "TRANSFER_ENTROPY")


def test_edf_kernel_distinct_from_quantile_regression_slope():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_quantile_regression_slope(d["log_return"][0], _mkt_of(d), W), "edf_ad", "QREG_SLOPE")


def test_edf_kernel_distinct_from_markov_sign_transition():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_markov_sign_transition(d["log_return"][0], W), "edf_ad", "C429_MARKOV")


def test_edf_kernel_distinct_from_sign_count_entropy():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_sign_count_entropy(d["log_return"][0], W), "edf_ad", "C329_SIGN_COUNT_ENTROPY")


def test_edf_kernel_distinct_from_sign_streak():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_sign_streak(d["log_return"][0], W), "edf_ad", "SIGN_STREAK")


def test_edf_kernel_distinct_from_sign_power():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_sign_power(d["log_return"][0], _mkt_of(d), W), "edf_ad", "SIGN_POWER")


def test_edf_kernel_distinct_from_sign_coherence():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_sign_coherence(d["log_return"][0], W), "edf_ad", "SIGN_COHERENCE")


def test_edf_kernel_distinct_from_sign_comotion():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_sign_agreement_motion(d["log_return"], W), "edf_ad", "SIGN_COMOTION")


def test_edf_kernel_distinct_from_multi_lag_autocov():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_multi_lag_autocov(d["log_return"][0], W), "edf_ad", "MULTI_LAG_AUTOCOV")


def test_edf_kernel_distinct_from_avg_pairwise_corr():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_avg_pairwise_corr(d["log_return"], W), "edf_ad", "AVG_PAIRWISE_CORR")


def test_edf_kernel_distinct_from_semcorr():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_semcorr(d["log_return"], W), "edf_ad", "SEMICORR")


def test_edf_kernel_distinct_from_leadlag():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_leadlag(d["log_return"][0], _mkt_of(d), W), "edf_ad", "LEADLAG")


def test_edf_kernel_distinct_from_cdom():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_cdom(d["log_return"], W), "edf_ad", "CDOM")


def test_edf_kernel_distinct_from_xsrank():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_xsrank(d["log_return"][0], _mkt_of(d), W), "edf_ad", "XSRANK")


def test_edf_kernel_distinct_from_betaasym():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_betaasym(d["log_return"][0], _mkt_of(d), W), "edf_ad", "BETAASYM")


def test_edf_kernel_distinct_from_xskew3():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_xskew3(d["log_return"][0], W), "edf_ad", "XSKEW3")


def test_edf_kernel_distinct_from_domfreq():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_domfreq(d["log_return"][0], W), "edf_ad", "DOMFREQ")


def test_edf_kernel_distinct_from_specfm():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_specfm(d["log_return"][0], W), "edf_ad", "SPECFM")


def test_edf_kernel_distinct_from_rqa():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_rqa(d["log_return"][0], W), "edf_ad", "RQA")


def test_edf_kernel_distinct_from_sample_entropy():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_sample_entropy(d["log_return"][0], W), "edf_ad", "SAMPLE_ENTROPY")


def test_edf_kernel_distinct_from_multiscale_entropy():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_multiscale_entropy(d["log_return"][0], W), "edf_ad", "MULTISCALE_ENTROPY")


def test_edf_kernel_distinct_from_permutation_entropy():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_permutation_entropy(d["log_return"][0], W), "edf_ad", "PERMUTATION_ENTROPY")


def test_edf_kernel_distinct_from_mfdfa():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_mfdfa(d["log_return"][0], W), "edf_ad", "MF_DFA")


def test_edf_kernel_distinct_from_vol_of_vol():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_vol_of_vol(d["log_return"][0], W), "edf_ad", "VOL_OF_VOL")


def test_edf_kernel_distinct_from_realized_skewness():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_realized_skewness(d["log_return"][0], W), "edf_ad", "REALIZED_SKEWNESS")


# ================================================================ guard tests (rewrite guards)
def test_artifact_campaign_is_432():
    """Rewrite guard: every emitted artifact self-identifies campaign 432."""
    for part in ("verdict", "summary", "registry", "oos_sweep"):
        files = sorted((ROOT / "reports").glob(f"campaign432_{part}_*.json"))
        files = [f for f in files if ".full." not in f.name]
        if not files:
            continue
        obj = json.loads(files[-1].read_text())
        assert obj["campaign"] == 432, f"{part} artifact campaign != 432: {obj.get('campaign')}"


def test_mandate_contains_edfgof():
    """Rewrite guard: the C432 mandate names the EDF-GOODNESS-OF-FIT family."""
    p = sorted((ROOT / "reports").glob("campaign432_oos_sweep_*.json"))
    p = [f for f in p if ".full." not in f.name]
    if not p:
        return
    mandate = json.loads(p[-1].read_text())["mandate"]
    assert "EDF-GOODNESS-OF-FIT" in mandate, "mandate missing EDF-GOODNESS-OF-FIT"
    assert "Anderson" in mandate, "mandate missing Anderson-Darling"
    assert "Cram" in mandate, "mandate missing Cramer-von-Mises"
    assert "Kolmogorov" in mandate, "mandate missing Kolmogorov-Smirnov"
    assert "Kuiper" in mandate, "mandate missing Kuiper"
    assert "edf_ad" in mandate, "mandate missing edf_ad"
    assert "edf_cvm" in mandate, "mandate missing edf_cvm"
    assert "edf_ks" in mandate, "mandate missing edf_ks"
    assert "edf_kuiper" in mandate, "mandate missing edf_kuiper"


def test_placebo_seed_is_20261296():
    assert R.PLACEBO_SEED == 20261296


def test_placebo_seed_unique_not_reserved():
    """Rewrite guard: C432 placebo seed must not collide with reserved seeds
    used by prior campaigns (20261224..20261295)."""
    assert not (20261224 <= R.PLACEBO_SEED <= 20261295), \
        "placebo seed must be outside 20261224-20261295"


# ================================================================ real artifacts schema (if present)
def _find_latest(prefix: str):
    files = sorted((ROOT / "reports").glob(f"campaign432_{prefix}_*.json"))
    files = [f for f in files if ".full." not in f.name]
    return files[-1] if files else None


def test_artifacts_if_present_have_required_flags():
    p = _find_latest("verdict")
    if p is None:
        return
    v = json.loads(p.read_text())
    assert v["campaign"] == 432
    assert v["real_data_only"] is True and v["fabricated_data"] is False
    assert v["executed_fills"] is False
    assert v["verdict"] in ("EDGE_PROVEN", "RETRACTED")
    assert isinstance(v["edge_proven"], bool)
    for k in ("oos_sweep_sha256", "registry_sha256", "summary_sha256"):
        assert isinstance(v[k], str) and len(v[k]) == 64
    reg = json.loads((ROOT / v["registry_artifact"]).read_text())
    assert reg["real_data_only"] is True and reg["fabricated_data"] is False
    sw = json.loads((ROOT / v["oos_sweep_artifact"]).read_text())
    assert sw["summary"]["n_total_runs"] == R.N_TRIALS
    assert sw["config"]["n_trials"] == R.N_TRIALS
    assert sw["real_data_only"] is True and sw["fabricated_data"] is False
    assert sw["config"]["placebo_seed"] == R.PLACEBO_SEED
    assert sw["config"]["edfgof_params"]["window_W_q"] == 256


if __name__ == "__main__":
    test_holm_and_bh_reject_correctly()
    test_holm_and_bh_monotone_and_bounded()
    test_n_trials_matches_pre_registered_grid_product()
    test_cost_rate_taker_and_maker_blend()
    test_positions_dollar_neutral_and_causal()
    test_positions_hold_reduces_turnover()
    test_positions_nan_asset_gets_zero_weight()
    test_wf_splits_month_aligned_non_overlapping()
    test_wf_splits_count_2023_2025()
    test_edf_matches_brute_force()
    test_edf_matches_brute_force_10_assets()
    test_edf_matches_brute_force_with_nan()
    test_edf_defined_after_window_nan_before()
    test_edf_non_finite_propagates()
    test_edf_degenerate_window_is_nan()
    test_edf_params()
    test_edf_kernel_not_degenerate()
    test_reference_config_matches_pre_registered_spec()
    test_phase_randomized_surrogate_same_marginal_deterministic()
    test_build_underlying_shapes_and_keys()
    test_build_scores_signals_lookbacks_causal()
    test_edf_kernel_not_degenerate()
    test_edf_kernel_distinct_from_distance_correlation()
    test_edf_kernel_distinct_from_cross_quantilogram()
    test_edf_kernel_distinct_from_pearson_autocov()
    test_edf_kernel_distinct_from_norm_acf_horizon()
    test_edf_kernel_distinct_from_sign_autocorr()
    test_edf_kernel_distinct_from_semicov()
    test_edf_kernel_distinct_from_coskew()
    test_edf_kernel_distinct_from_sign_agreement_motion()
    test_edf_kernel_distinct_from_tail_dependence()
    test_edf_kernel_distinct_from_spectral_coherence()
    test_edf_kernel_distinct_from_time_irreversibility()
    test_edf_kernel_distinct_from_transfer_entropy()
    test_edf_kernel_distinct_from_quantile_regression_slope()
    test_edf_kernel_distinct_from_markov_sign_transition()
    test_edf_kernel_distinct_from_sign_count_entropy()
    test_edf_kernel_distinct_from_sign_streak()
    test_edf_kernel_distinct_from_sign_power()
    test_edf_kernel_distinct_from_sign_coherence()
    test_edf_kernel_distinct_from_sign_comotion()
    test_edf_kernel_distinct_from_multi_lag_autocov()
    test_edf_kernel_distinct_from_avg_pairwise_corr()
    test_edf_kernel_distinct_from_semcorr()
    test_edf_kernel_distinct_from_leadlag()
    test_edf_kernel_distinct_from_cdom()
    test_edf_kernel_distinct_from_xsrank()
    test_edf_kernel_distinct_from_betaasym()
    test_edf_kernel_distinct_from_xskew3()
    test_edf_kernel_distinct_from_domfreq()
    test_edf_kernel_distinct_from_specfm()
    test_edf_kernel_distinct_from_rqa()
    test_edf_kernel_distinct_from_sample_entropy()
    test_edf_kernel_distinct_from_multiscale_entropy()
    test_edf_kernel_distinct_from_permutation_entropy()
    test_edf_kernel_distinct_from_mfdfa()
    test_edf_kernel_distinct_from_vol_of_vol()
    test_edf_kernel_distinct_from_realized_skewness()
    test_artifact_campaign_is_432()
    test_mandate_contains_edfgof()
    test_placebo_seed_is_20261296()
    test_placebo_seed_unique_not_reserved()
    test_artifacts_if_present_have_required_flags()
    print("All C432 EDF-GOF runner tests passed")
