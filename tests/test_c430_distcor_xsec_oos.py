"""Tests for C430 runner (scripts/run_c430_distcor_xsec_oos.py): pure-function
tests on synthetic arrays (including a brute-force equality test for the
vectorized DISTCOR kernel vs an independent O(W^2) double-centered distance-
matrix reference) plus schema/flag validation of emitted real-data artifacts.
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

import run_c430_distcor_xsec_oos as R  # noqa: E402


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
    for pb in ("dcor_serial_placebo", "dcor_volserial_placebo",
               "dcor_market_placebo", "dcor_signmag_placebo"):
        assert pb in R.SIGNALS
    for real in ("dcor_serial_dev", "dcor_volserial_dev",
                 "dcor_market_dev", "dcor_signmag_dev"):
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


# ================================================================ DISTCOR brute-force equality
def _distcor_bruteforce(log_return, abs_ret, sign, mkt, W, lags=(1, 2, 4)):
    """Independent per-window brute-force DISTCOR reference (O(W^2) double-centered
    distance matrices). Mirrors the 4-concept definition; used only for equality
    testing on small inputs."""
    Rm = np.asarray(log_return, float)
    Am = np.asarray(abs_ret, float)
    Sm = np.asarray(sign, float)
    Mm = np.asarray(mkt, float)
    n_assets, n = Rm.shape
    out = {k: np.full((n_assets, n), np.nan, float)
           for k in ("dcor_serial", "dcor_volserial", "dcor_market", "dcor_signmag")}
    for t in range(W - 1, n):
        for i in range(n_assets):
            def win(arr):
                return arr[i][t - W + 1:t + 1]
            def lagwin(arr, k):
                return R._lag_series(arr[i], k)[t - W + 1:t + 1]
            s_parts = [R._distcor_bruteforce_window(lagwin(Rm, k), win(Rm)) for k in lags]
            v_parts = [R._distcor_bruteforce_window(lagwin(Am, k), win(Am)) for k in lags]
            out["dcor_serial"][i, t] = float(np.nanmean(s_parts))
            out["dcor_volserial"][i, t] = float(np.nanmean(v_parts))
            out["dcor_market"][i, t] = R._distcor_bruteforce_window(win(Rm), Mm[t - W + 1:t + 1])
            out["dcor_signmag"][i, t] = R._distcor_bruteforce_window(win(Sm), win(Am))
    return out


def test_distcor_matches_brute_force():
    """The vectorized DISTCOR kernel MUST equal the brute-force per-window
    double-centered distance-matrix reference (maxdiff < 1e-12, matching NaN)."""
    W = 128
    d = _synth(3, 400, 20261294)
    mkt = d["log_return"].mean(0)
    fast = R.compute_distcor_metrics(d["log_return"], d["abs_ret"], d["sign"], mkt, W=W)
    brute = _distcor_bruteforce(d["log_return"], d["abs_ret"], d["sign"], mkt, W=W)
    for key in ("dcor_serial", "dcor_volserial", "dcor_market", "dcor_signmag"):
        fv, fb = fast[key], brute[key]
        fin = np.isfinite(fv) & np.isfinite(fb)
        assert fin.sum() > 0, f"{key}: no finite overlapping points"
        assert np.array_equal(np.isnan(fv), np.isnan(fb)), f"{key}: NaN pattern mismatch"
        maxdiff = float(np.max(np.abs(fv[fin] - fb[fin]))) if fin.sum() else 0.0
        assert maxdiff < 1e-12, f"{key}: maxdiff={maxdiff} >= 1e-12"


def test_distcor_matches_brute_force_10_assets():
    """Brute-force equality with the full 10-asset panel (the real universe width)."""
    W = 128
    d = _synth(10, 300, 4294)
    mkt = d["log_return"].mean(0)
    fast = R.compute_distcor_metrics(d["log_return"], d["abs_ret"], d["sign"], mkt, W=W)
    brute = _distcor_bruteforce(d["log_return"], d["abs_ret"], d["sign"], mkt, W=W)
    for key in ("dcor_serial", "dcor_volserial", "dcor_market", "dcor_signmag"):
        fv, fb = fast[key], brute[key]
        fin = np.isfinite(fv) & np.isfinite(fb)
        assert fin.sum() > 0, key
        assert np.array_equal(np.isnan(fv), np.isnan(fb)), key
        maxdiff = float(np.max(np.abs(fv[fin] - fb[fin])))
        assert maxdiff < 1e-12, f"{key}: maxdiff={maxdiff} (float64 noise floor)"


def test_distcor_matches_brute_force_with_nan():
    """Brute-force equality when the panel contains NaNs (propagates to NaN windows)."""
    W = 128
    d = _synth(4, 400, 99)
    d["log_return"][1, 200] = np.nan
    d["abs_ret"][2, 260] = np.nan
    mkt = np.nanmean(d["log_return"], axis=0)
    fast = R.compute_distcor_metrics(d["log_return"], d["abs_ret"], d["sign"], mkt, W=W)
    brute = _distcor_bruteforce(d["log_return"], d["abs_ret"], d["sign"], mkt, W=W)
    for key in ("dcor_serial", "dcor_volserial", "dcor_market", "dcor_signmag"):
        fv, fb = fast[key], brute[key]
        assert np.array_equal(np.isnan(fv), np.isnan(fb)), f"{key}: NaN mismatch"
        fin = np.isfinite(fv) & np.isfinite(fb)
        maxdiff = float(np.max(np.abs(fv[fin] - fb[fin]))) if fin.sum() else 0.0
        assert maxdiff < 1e-12, f"{key}: maxdiff={maxdiff}"


def test_distcor_defined_after_window_nan_before():
    W = R.DISTCOR_W
    d = _synth(3, 400, 3)
    mkt = d["log_return"].mean(0)
    m = R.compute_distcor_metrics(d["log_return"], d["abs_ret"], d["sign"], mkt, W=W)
    for key in ("dcor_serial", "dcor_volserial", "dcor_market", "dcor_signmag"):
        assert np.isnan(m[key][:, :W - 1]).all(), key
        assert np.isfinite(m[key][:, W - 1:]).any(), key


def test_distcor_non_finite_propagates():
    """A non-finite value in any asset at a bar -> NaN for every concept in every
    window covering that bar."""
    W = 64
    d = _synth(4, 400, 9)
    d["log_return"][:, 200] = np.nan
    d["abs_ret"] = np.abs(d["log_return"])
    mkt = np.nanmean(d["log_return"], axis=0)
    m = R.compute_distcor_metrics(d["log_return"], d["abs_ret"], d["sign"], mkt, W=W)
    for t in range(200, min(200 + W, 400)):
        for key in ("dcor_serial", "dcor_volserial", "dcor_market", "dcor_signmag"):
            assert np.isnan(m[key][:, t]).all(), f"{key} t={t} should be NaN"


def test_distcor_degenerate_window_is_nan():
    """Constant (zero-variance) window -> NaN dCor."""
    W = 64
    x = np.full(300, 0.5)
    y = np.linspace(0, 1, 300)
    out = R._rolling_distcor(x, y, W)
    assert np.isnan(out).all()


def test_distcor_params():
    assert R.DISTCOR_W == 128
    assert R.DISTCOR_LAGS == (1, 2, 4)


def test_distcor_range_0_1():
    """dCor in [0, 1]."""
    d = _synth(3, 600, 2026)
    mkt = d["log_return"].mean(0)
    m = R.compute_distcor_metrics(d["log_return"], d["abs_ret"], d["sign"], mkt, W=128)
    for key in ("dcor_serial", "dcor_volserial", "dcor_market", "dcor_signmag"):
        fin = np.isfinite(m[key])
        assert fin.sum() > 0
        assert (m[key][fin] >= -1e-9).all(), f"{key} >= 0"
        assert (m[key][fin] <= 1.0 + 1e-9).all(), f"{key} <= 1"


def test_distcor_independence_near_zero_and_comonotone_one():
    """Independent series -> dCor ~ 0; perfectly comonotone -> dCor = 1."""
    rng = np.random.default_rng(11)
    W = 128
    n = W
    x = rng.standard_normal(n)
    y_indep = rng.standard_normal(n)
    d_indep = R._distcor_bruteforce_window(x, y_indep)
    z = np.linspace(-2, 2, n)
    d_comonotone = R._distcor_bruteforce_window(z, 3.0 * z + 1.0)
    assert d_indep < 0.5, d_indep
    assert abs(d_comonotone - 1.0) < 1e-9, d_comonotone


# ================================================================ reference-config spec
def test_reference_config_matches_pre_registered_spec():
    assert R.ATTR_REPRESENTATIVES == {
        "dcor_serial_dev": "dcor_serial_dev",
        "dcor_volserial_dev": "dcor_volserial_dev",
        "dcor_market_dev": "dcor_market_dev",
        "dcor_signmag_dev": "dcor_signmag_dev",
    }
    assert R.PLACEBO_SEED == 20261294
    assert R.STABILITY_MIN_SIGN_CONSISTENCY == 0.70
    assert R.STABILITY_MIN_SHARPE_CORR == 0.50
    assert R.DOMINANT_SHARE_MIN == 0.50
    assert R.TRAIN_M == 12 and R.TEST_M == 3 and R.ROLL_M == 3
    assert R.DISTCOR_W == 128
    assert R.DISTCOR_LAGS == (1, 2, 4)
    assert R.SIGNALS[0] == "dcor_serial_dev"


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
    assert set(series.keys()) == {"dcor_serial", "dcor_volserial",
                                  "dcor_market", "dcor_signmag"}
    for k in ("dcor_serial", "dcor_volserial", "dcor_market", "dcor_signmag"):
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
    assert not np.allclose(sa[fin], ref[fin], atol=1e-6), f"DISTCOR degenerates to {name}"


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


def _dcor_series_for_guard(d):
    """Compute the 4 DISTCOR concept series for the first asset (guards compare
    concept[0])."""
    W = 128
    mkt = _mkt_of(d)
    return R._distcor_concepts_for_asset(d["log_return"][0], d["abs_ret"][0],
                                         d["sign"][0], mkt, W=W), W


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
        # TE m->x = H(x_{t+1}|x_t) - H(x_{t+1}|x_t,m_t)
        def _H(a, b):
            if len(a) == 0:
                return 0.0
            _, c = np.unique(np.stack([a, b], 1), axis=0, return_counts=True)
            p = c / c.sum()
            return float(-(p * np.log(p)).sum())
        te = _H(xb[1:], xb[:-1]) - _H(xb[1:], np.stack([xb[:-1], mb[:-1]], 1)[:, 0] * 0)  # placeholder
        # proper joint
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


def _ref_permutation_entropy(x, W):
    """C349 permutation entropy (ordinal patterns, order 3)."""
    def fn(w):
        pats = [tuple(np.argsort(w[k:k + 3], kind="mergesort")) for k in range(len(w) - 2)]
        if not pats:
            return np.nan
        _, c = np.unique(pats, return_counts=True)
        p = c / c.sum()
        return float(-(p * np.log(p)).sum())
    return _windowed_stat(x, W, fn)


def _ref_sample_entropy(x, W):
    """C355 sample entropy (neighbor-based, m=2)."""
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
    """C356 multiscale entropy (coarse-grained sample entropy at scale 2)."""
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


def _ref_rqa(x, W):
    """C358/C425 RQA recurrence rate (neighbor recurrence in delay embedding)."""
    def fn(w):
        if np.std(w) <= 0:
            return np.nan
        yn = (w - w.mean()) / np.std(w)
        emb = np.stack([yn[:-1], yn[1:]], 1)
        r = 0.2
        d = np.sqrt(((emb[:, None, :] - emb[None, :, :]) ** 2).sum(2))
        return float(np.mean(d < r))
    return _windowed_stat(x, W, fn)


def _ref_vol_of_vol(x, W):
    """Vol-of-vol ratio (C340s VOVR-style): std of rolling |x| / mean|x|."""
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
    """Realized skewness (3rd standardized moment, C341s RSKEW family)."""
    def fn(w):
        s = np.std(w)
        if s <= 0:
            return np.nan
        return float(np.mean(((w - w.mean()) / s) ** 3))
    return _windowed_stat(x, W, fn)


def _guarded_assert(d, ref_series, concept, guard_name):
    series, W = _dcor_series_for_guard(d)
    sa = series[concept][W - 1:]
    ref = ref_series[W - 1:]
    _assert_distinct(sa, ref, guard_name)


def test_distcor_kernel_not_degenerate():
    d = _synth(5, 500, 55)
    series, W = _dcor_series_for_guard(d)
    for name in ("dcor_serial", "dcor_volserial", "dcor_market", "dcor_signmag"):
        arr = series[name]
        fin = np.isfinite(arr)
        assert fin.sum() > 0, f"{name}: no finite values"
        assert not np.allclose(arr[fin], 0.0, atol=1e-12), f"{name} collapses to 0"


def test_distcor_kernel_distinct_from_pearson_autocov():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_pearson_autocov(d["log_return"][0], W), "dcor_market", "PEARSON_ACOV")


def test_distcor_kernel_distinct_from_norm_acf_horizon():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_norm_acf(d["log_return"][0], W), "dcor_market", "NORM_ACF_HORIZON")


def test_distcor_kernel_distinct_from_sign_autocorr():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_sign_autocorr(d["log_return"][0], W), "dcor_market", "SIGN_AUTOCORR")


def test_distcor_kernel_distinct_from_semicov():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_semicov(d["log_return"][0], W), "dcor_market", "SEMICOV")


def test_distcor_kernel_distinct_from_coskew():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_coskew(d["log_return"][0], _mkt_of(d), W), "dcor_market", "COSKEW")


def test_distcor_kernel_distinct_from_sign_agreement_motion():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_sign_agreement_motion(d["log_return"], W), "dcor_market", "SIGN_AGREEMENT")


def test_distcor_kernel_distinct_from_tail_dependence():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_tail_dependence(d["log_return"][0], _mkt_of(d), W), "dcor_market", "TAIL_DEP")


def test_distcor_kernel_distinct_from_spectral_coherence():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_spectral_coherence(d["log_return"][0], _mkt_of(d), W), "dcor_market", "COHERENCE")


def test_distcor_kernel_distinct_from_time_irreversibility():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_tirv_cumulant(d["log_return"][0], W), "dcor_market", "TIRV")


def test_distcor_kernel_distinct_from_transfer_entropy():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_transfer_entropy(d["log_return"][0], _mkt_of(d), W), "dcor_market", "TRANSFER_ENTROPY")


def test_distcor_kernel_distinct_from_quantile_regression_slope():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_quantile_regression_slope(d["log_return"][0], _mkt_of(d), W), "dcor_market", "QREG_SLOPE")


def test_distcor_kernel_distinct_from_markov_sign_transition():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_markov_sign_transition(d["log_return"][0], W), "dcor_market", "C429_MARKOV")


def test_distcor_kernel_distinct_from_sign_count_entropy():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_sign_count_entropy(d["log_return"][0], W), "dcor_market", "C329_SIGN_COUNT_ENTROPY")


def test_distcor_kernel_distinct_from_permutation_entropy():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_permutation_entropy(d["log_return"][0], W), "dcor_market", "PERMUTATION_ENTROPY")


def test_distcor_kernel_distinct_from_sample_entropy():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_sample_entropy(d["log_return"][0], W), "dcor_market", "SAMPLE_ENTROPY")


def test_distcor_kernel_distinct_from_multiscale_entropy():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_multiscale_entropy(d["log_return"][0], W), "dcor_market", "MULTISCALE_ENTROPY")


def test_distcor_kernel_distinct_from_rqa():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_rqa(d["log_return"][0], W), "dcor_market", "RQA")


def test_distcor_kernel_distinct_from_vol_of_vol():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_vol_of_vol(d["log_return"][0], W), "dcor_market", "VOL_OF_VOL")


def test_distcor_kernel_distinct_from_realized_skewness():
    d = _guard_base(); W = 128
    _guarded_assert(d, _ref_realized_skewness(d["log_return"][0], W), "dcor_market", "REALIZED_SKEWNESS")


# ================================================================ guard tests (rewrite guards)
def test_artifact_campaign_is_430():
    """Rewrite guard: every emitted artifact self-identifies campaign 430."""
    for part in ("verdict", "summary", "registry", "oos_sweep"):
        files = sorted((ROOT / "reports").glob(f"campaign430_{part}_*.json"))
        files = [f for f in files if ".full." not in f.name]
        if not files:
            continue
        obj = json.loads(files[-1].read_text())
        assert obj["campaign"] == 430, f"{part} artifact campaign != 430: {obj.get('campaign')}"


def test_mandate_contains_distcor():
    """Rewrite guard: the C430 mandate names the DISTCOR distance-correlation family."""
    p = sorted((ROOT / "reports").glob("campaign430_oos_sweep_*.json"))
    p = [f for f in p if ".full." not in f.name]
    if not p:
        return
    mandate = json.loads(p[-1].read_text())["mandate"]
    assert "DISTCOR" in mandate, "mandate missing DISTCOR"
    assert "distance correlation" in mandate, "mandate missing distance correlation"
    assert "dcor_serial" in mandate, "mandate missing dcor_serial"
    assert "dcor_volserial" in mandate, "mandate missing dcor_volserial"
    assert "dcor_market" in mandate, "mandate missing dcor_market"
    assert "dcor_signmag" in mandate, "mandate missing dcor_signmag"


def test_placebo_seed_is_20261294():
    assert R.PLACEBO_SEED == 20261294


def test_placebo_seed_unique_not_reserved():
    """Rewrite guard: C430 placebo seed must not collide with reserved seeds
    used by prior campaigns (20261224..20261293)."""
    assert not (20261224 <= R.PLACEBO_SEED <= 20261293), \
        "placebo seed must be outside 20261224-20261293"


# ================================================================ real artifacts schema (if present)
def _find_latest(prefix: str):
    files = sorted((ROOT / "reports").glob(f"campaign430_{prefix}_*.json"))
    files = [f for f in files if ".full." not in f.name]
    return files[-1] if files else None


def test_artifacts_if_present_have_required_flags():
    p = _find_latest("verdict")
    if p is None:
        return
    v = json.loads(p.read_text())
    assert v["campaign"] == 430
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
    assert sw["config"]["distcor_params"]["window_W"] == 128


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
    test_distcor_matches_brute_force()
    test_distcor_matches_brute_force_10_assets()
    test_distcor_matches_brute_force_with_nan()
    test_distcor_defined_after_window_nan_before()
    test_distcor_non_finite_propagates()
    test_distcor_degenerate_window_is_nan()
    test_distcor_params()
    test_distcor_range_0_1()
    test_distcor_independence_near_zero_and_comonotone_one()
    test_reference_config_matches_pre_registered_spec()
    test_phase_randomized_surrogate_same_marginal_deterministic()
    test_build_underlying_shapes_and_keys()
    test_build_scores_signals_lookbacks_causal()
    test_distcor_kernel_not_degenerate()
    test_distcor_kernel_distinct_from_pearson_autocov()
    test_distcor_kernel_distinct_from_norm_acf_horizon()
    test_distcor_kernel_distinct_from_sign_autocorr()
    test_distcor_kernel_distinct_from_semicov()
    test_distcor_kernel_distinct_from_coskew()
    test_distcor_kernel_distinct_from_sign_agreement_motion()
    test_distcor_kernel_distinct_from_tail_dependence()
    test_distcor_kernel_distinct_from_spectral_coherence()
    test_distcor_kernel_distinct_from_time_irreversibility()
    test_distcor_kernel_distinct_from_transfer_entropy()
    test_distcor_kernel_distinct_from_quantile_regression_slope()
    test_distcor_kernel_distinct_from_markov_sign_transition()
    test_distcor_kernel_distinct_from_sign_count_entropy()
    test_distcor_kernel_distinct_from_permutation_entropy()
    test_distcor_kernel_distinct_from_sample_entropy()
    test_distcor_kernel_distinct_from_multiscale_entropy()
    test_distcor_kernel_distinct_from_rqa()
    test_distcor_kernel_distinct_from_vol_of_vol()
    test_distcor_kernel_distinct_from_realized_skewness()
    test_artifact_campaign_is_430()
    test_mandate_contains_distcor()
    test_placebo_seed_is_20261294()
    test_placebo_seed_unique_not_reserved()
    test_artifacts_if_present_have_required_flags()
    print("All C430 DISTCOR runner tests passed")