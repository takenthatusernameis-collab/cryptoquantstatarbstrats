"""Tests for C411 runner (scripts/run_c411_semcorr_xsec_oos.py): pure-function tests
on synthetic arrays (including a brute-force equality test for the vectorized
SEMCORR sign-conditional average pairwise correlation asymmetry kernel vs the
per-window reference) plus schema/flag validation of emitted real-data artifacts.
No network, no fabricated market data."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import run_c411_semcorr_xsec_oos as R  # noqa: E402


# ---------------------------------------------------------------- multiple testing
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
    assert R.N_TRIALS == 1944
    assert len(R.SIGNALS) == 6
    assert len(R.LOOKBACKS) == 6
    assert len(R.REBALANCES) == 3
    assert len(R.FEES) == 3 and len(R.SLIPS) == 3 and len(R.COST_VARIANTS) == 2
    assert R.N_TRIALS == (len(R.SIGNALS) * len(R.LOOKBACKS) * len(R.REBALANCES)
                          * len(R.FEES) * len(R.SLIPS) * len(R.COST_VARIANTS))
    for pb in ("up_corr_placebo", "down_corr_placebo", "semcorr_asym_placebo"):
        assert pb in R.SIGNALS
    for real in ("up_corr_dev", "down_corr_dev", "semcorr_asym_dev"):
        assert real in R.SIGNALS


# ---------------------------------------------------------------- single-leg costs
def test_cost_rate_taker_and_maker_blend():
    assert np.isclose(R.cost_rate(0.0004, 0.0001, "taker"), 0.0005)
    assert np.isclose(R.cost_rate(0.0004, 0.0001, "maker_blend"), 0.0003)
    for fee in R.FEES:
        for slip in R.SLIPS:
            assert R.cost_rate(fee, slip, "taker") >= R.cost_rate(fee, slip, "maker_blend")


# ---------------------------------------------------------------- positions
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


# ---------------------------------------------------------------- walk-forward
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


# ---------------------------------------------------------------- SEMCORR metric (brute-force equality)
def test_semcorr_matches_brute_force():
    """The vectorized SEMCORR kernel MUST equal the brute-force reference
    (per-window loop with explicit np.corrcoef for each pairwise leg on each
    conditional subset). Compared with maxdiff < 1e-12 with matching NaN patterns."""
    rng = np.random.default_rng(20261275)
    n_assets, n_bars = 5, 4000
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    fast = R.compute_semcorr_metrics(log_return, R.SEMCORR_W)
    brute = R._semcorr_bruteforce(log_return, R.SEMCORR_W)
    for key in ("up_corr", "down_corr", "semcorr_asym"):
        fv, fb = fast[key], brute[key]
        fin = np.isfinite(fv) & np.isfinite(fb)
        assert fin.sum() > 0, f"{key}: no finite overlapping points"
        assert np.array_equal(np.isnan(fv), np.isnan(fb)), f"{key}: NaN pattern mismatch"
        maxdiff = float(np.max(np.abs(fv[fin] - fb[fin]))) if fin.sum() else 0.0
        assert maxdiff < 1e-12, f"{key}: maxdiff={maxdiff} >= 1e-12"


def test_semcorr_matches_brute_force_10_assets():
    """Brute-force equality with the full 10-asset panel (the real universe width)."""
    rng = np.random.default_rng(4112)
    n_assets, n_bars = 10, 1500
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    fast = R.compute_semcorr_metrics(log_return, R.SEMCORR_W)
    brute = R._semcorr_bruteforce(log_return, R.SEMCORR_W)
    for key in ("up_corr", "down_corr", "semcorr_asym"):
        fv, fb = fast[key], brute[key]
        fin = np.isfinite(fv) & np.isfinite(fb)
        assert fin.sum() > 0, key
        maxdiff = float(np.max(np.abs(fv[fin] - fb[fin])))
        assert maxdiff < 1e-12, f"{key}: maxdiff={maxdiff}"


def test_semcorr_defined_after_window_nan_before():
    rng = np.random.default_rng(3)
    n_assets, n_bars = 3, 600
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    W = R.SEMCORR_W
    m = R.compute_semcorr_metrics(log_return, W)
    for key in ("up_corr", "down_corr", "semcorr_asym"):
        assert np.isnan(m[key][:, :W]).all(), key
        assert np.isfinite(m[key][:, W:]).any(), key


def test_semcorr_bounds_in_unit_interval():
    """up_corr and down_corr are averages of Pearson correlations => within [-1, 1]."""
    rng = np.random.default_rng(11)
    n_assets, n_bars = 6, 800
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    m = R.compute_semcorr_metrics(log_return, R.SEMCORR_W)
    for key in ("up_corr", "down_corr"):
        fin = np.isfinite(m[key])
        assert fin.sum() > 0
        assert float(np.max(np.abs(m[key][fin]))) <= 1.0 + 1e-9


def test_semcorr_non_finite_return_propagates():
    """A non-finite return in any asset's window -> NaN for all SEMCORR outputs
    in affected bars (the whole panel window is non-finite)."""
    rng = np.random.default_rng(9)
    n_assets, n_bars = 4, 600
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    log_return[0, 300] = np.inf
    W = R.SEMCORR_W
    m = R.compute_semcorr_metrics(log_return, W)
    for t in range(300, min(300 + W, n_bars)):
        assert np.isnan(m["up_corr"][:, t]).all(), f"up_corr t={t} should be NaN"
        assert np.isnan(m["down_corr"][:, t]).all(), f"down_corr t={t} should be NaN"
        assert np.isnan(m["semcorr_asym"][:, t]).all(), f"semcorr_asym t={t} should be NaN"
    for t in range(W, 300):
        assert np.isfinite(m["up_corr"][:, t]).any(), f"up_corr t={t} should be finite"


def test_semcorr_params():
    assert R.SEMCORR_W == 256


def test_reference_config_matches_pre_registered_spec():
    assert R.ATTR_REPRESENTATIVES == {
        "up_corr_dev": "up_corr_dev",
        "down_corr_dev": "down_corr_dev",
        "semcorr_asym_dev": "semcorr_asym_dev",
    }
    assert R.PLACEBO_SEED == 20261275
    assert R.STABILITY_MIN_SIGN_CONSISTENCY == 0.70
    assert R.STABILITY_MIN_SHARPE_CORR == 0.50
    assert R.DOMINANT_SHARE_MIN == 0.50
    assert R.TRAIN_M == 12 and R.TEST_M == 3 and R.ROLL_M == 3
    assert R.SEMCORR_W == 256
    assert R.SIGNALS[0] == "up_corr_dev"


# ---------------------------------------------------------------- phase-randomized surrogate
def test_phase_randomized_surrogate_same_marginal_deterministic():
    rng = np.random.default_rng(0)
    x = rng.standard_normal(500) * 3.0 + 5.0
    s1 = R._phase_randomized_surrogate(x, R.PLACEBO_SEED)
    s2 = R._phase_randomized_surrogate(x, R.PLACEBO_SEED)
    assert np.array_equal(s1, s2)
    assert np.isclose(np.sort(s1[np.isfinite(s1)]), np.sort(x[np.isfinite(x)]), equal_nan=True).all()


# ---------------------------------------------------------------- build_underlying / build_scores
def _synthetic_bs(n_assets=3, n_days=8, seed=1):
    rng = np.random.default_rng(seed)
    T = 288
    lr = rng.standard_normal((n_assets, n_days * T)) * 0.001
    c = 100.0 * np.exp(np.cumsum(lr, axis=1))
    return {
        "perp_close": c, "log_return": lr,
        "bucket": np.tile(np.arange(T), n_days),
        "n_assets": n_assets, "n_days": n_days, "n_bars": n_days * T,
    }


def test_build_underlying_shapes_and_keys():
    bs = _synthetic_bs()
    series = R.build_underlying(bs)
    assert set(series.keys()) == {"up_corr", "down_corr", "semcorr_asym"}
    for k in ("up_corr", "down_corr", "semcorr_asym"):
        assert series[k].shape == (bs["n_assets"], bs["n_bars"])


def test_build_scores_signals_lookbacks_causal():
    bs = _synthetic_bs()
    series = R.build_underlying(bs)
    scores = R.build_scores(series, bs["bucket"])
    for sig in R.SIGNALS:
        for L in R.LOOKBACKS:
            assert (sig, L) in scores
            assert scores[(sig, L)].shape == (bs["n_assets"], bs["n_bars"])
    for key, sc in scores.items():
        assert np.isnan(sc[:, 0]).all(), key


# ---------------------------------------------------------------- kernel distinctness guards
def test_semcorr_kernel_not_degenerate():
    """Rewrite guard: SEMCORR metrics are not degenerate (not allclose to 0 where defined)."""
    rng = np.random.default_rng(55)
    n_assets, n_bars = 5, 1600
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    W = R.SEMCORR_W
    mm = R.compute_semcorr_metrics(log_return, W)
    for name in ("up_corr", "down_corr", "semcorr_asym"):
        arr = mm[name]
        fin = np.isfinite(arr)
        assert fin.sum() > 0, f"{name}: no finite values"
        assert not np.allclose(arr[fin], 0.0, atol=1e-12), f"{name} collapses to 0"


def test_semcorr_up_and_down_are_distinct_objects():
    """Rewrite guard: up_corr (avg coupling on up-market bars) and down_corr
    (avg coupling on down-market bars) are different objects — never equal
    across the panel."""
    rng = np.random.default_rng(156)
    n_assets, n_bars = 5, 1200
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    W = R.SEMCORR_W
    mm = R.compute_semcorr_metrics(log_return, W)
    a = mm["up_corr"][:, W:]
    d = mm["down_corr"][:, W:]
    fin = np.isfinite(a) & np.isfinite(d)
    assert fin.sum() > 0
    assert not np.allclose(a[fin], d[fin], atol=1e-6), "up_corr and down_corr coincide"


def test_semcorr_asym_not_zero_where_defined():
    """Rewrite guard: semcorr_asym = up_corr - down_corr is not identically zero."""
    rng = np.random.default_rng(157)
    n_assets, n_bars = 5, 1200
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    W = R.SEMCORR_W
    mm = R.compute_semcorr_metrics(log_return, W)
    a = mm["semcorr_asym"][:, W:]
    fin = np.isfinite(a)
    assert fin.sum() > 0
    assert not np.allclose(a[fin], 0.0, atol=1e-12), "semcorr_asym collapses to 0"


def _xcorr_style_stat(log_return, W):
    """Inline C410 XCORR mean: unconditional average pairwise Pearson correlation."""
    X = np.asarray(log_return, dtype=float)
    n_assets, n = X.shape
    out = np.full((n_assets, n), np.nan)
    for t in range(W, n):
        span = X[:, t - W + 1:t + 1]
        if not np.isfinite(span).all():
            continue
        sd = span.std(axis=1)
        if not (sd > 0.0).all():
            continue
        for i in range(n_assets):
            corrs = []
            for j in range(n_assets):
                if j == i:
                    continue
                corrs.append(float(np.corrcoef(span[i], span[j])[0, 1]))
            out[i, t] = float(np.mean(corrs))
    return out


def _betaasym_style_stat(X, M, W):
    """Inline C406 BETAASYM same-bar full-window market beta."""
    n = len(X)
    out = np.full(n, np.nan)
    for t in range(W, n):
        Xw = X[t - W + 1:t + 1]
        Mw = M[t - W + 1:t + 1]
        if not (np.isfinite(Xw).all() and np.isfinite(Mw).all()):
            continue
        var_m = float(((Mw - Mw.mean()) ** 2).mean())
        if var_m <= 0:
            continue
        cov = float(((Xw - Xw.mean()) * (Mw - Mw.mean())).mean())
        out[t] = cov / var_m
    return out


def _coskew_style_stat(X, M, W):
    """Inline C405 COSKEW co-skewness of asset with market: mean(zx^2 * zm)."""
    n = len(X)
    out = np.full(n, np.nan)
    for t in range(W, n):
        Xw = X[t - W + 1:t + 1]
        Mw = M[t - W + 1:t + 1]
        if not (np.isfinite(Xw).all() and np.isfinite(Mw).all()):
            continue
        sx = Xw.std()
        sm = Mw.std()
        if sx <= 0 or sm <= 0:
            continue
        zx = (Xw - Xw.mean()) / sx
        zm = (Mw - Mw.mean()) / sm
        out[t] = float(np.mean(zx ** 2 * zm))
    return out


def _semicov_style_stat(X, W):
    """Inline C380 SEMICOV lag-1 signed-conditional covariance: mean(r_t*r_{t-1}
    | r_{t-1}<0) - mean(r_t*r_{t-1} | r_{t-1}>0) over the window."""
    n = len(X)
    out = np.full(n, np.nan)
    for t in range(W, n):
        Xw = X[t - W + 1:t + 1]
        if not np.isfinite(Xw).all():
            continue
        a = Xw[1:]
        b = Xw[:-1]
        prod = a * b
        neg = prod[b < 0]
        pos = prod[b > 0]
        if len(neg) < 2 or len(pos) < 2:
            continue
        out[t] = float(neg.mean() - pos.mean())
    return out


def _acovk_style_stat(X, W):
    """Inline C375 ACOVK lag-1 realized autocovariance: mean(x_t * x_{t-1})."""
    n = len(X)
    out = np.full(n, np.nan)
    for t in range(W, n):
        Xw = X[t - W + 1:t + 1]
        if not np.isfinite(Xw).all():
            continue
        out[t] = float(np.mean(Xw[1:] * Xw[:-1]))
    return out


def _xsrank_style_stat(X, W):
    """Inline C407 XSRANK-style rank persistence: lag-1 autocorrelation of the
    asset's within-window return ranks."""
    n = len(X)
    out = np.full(n, np.nan)
    for t in range(W, n):
        Xw = X[t - W + 1:t + 1]
        if not np.isfinite(Xw).all():
            continue
        r = np.argsort(np.argsort(Xw)).astype(float)
        if r.std() <= 0:
            continue
        out[t] = float(np.corrcoef(r[1:], r[:-1])[0, 1])
    return out


def _leadlag_style_stat(X, M, W):
    """Inline C408 LEADLAG asymmetry vs market: lag_beta - lead_beta where
    lead_beta = cov(r_i[t], m[t-1])/var(m[t-1]) (asset follows market),
    lag_beta = cov(r_i[t-1], m[t])/var(m[t]) (asset leads market)."""
    n = len(X)
    out = np.full(n, np.nan)
    for t in range(W, n):
        Xi = X[t - W + 1:t + 1]
        Mi = M[t - W + 1:t + 1]
        if not (np.isfinite(Xi).all() and np.isfinite(Mi).all()):
            continue
        xm = Mi[:-1]
        xi_lag = Xi[:-1]
        var_m = float(((xm - xm.mean()) ** 2).mean())
        if var_m <= 0:
            continue
        lead_beta = float(((xi_lag - xi_lag.mean()) * (xm - xm.mean())).mean()) / var_m
        xm2 = Mi[1:]
        xi_cur = Xi[1:]
        var_m2 = float(((xm2 - xm2.mean()) ** 2).mean())
        if var_m2 <= 0:
            continue
        lag_beta = float(((xi_cur - xi_cur.mean()) * (xm2 - xm2.mean())).mean()) / var_m2
        out[t] = lead_beta - lag_beta
    return out


def _residvol_style_stat(X, M, W):
    """Inline C409 RESIDVOL residual volatility vs equal-weight market."""
    n = len(X)
    out = np.full(n, np.nan)
    for t in range(W, n):
        Xw = X[t - W + 1:t + 1]
        Mw = M[t - W + 1:t + 1]
        if not (np.isfinite(Xw).all() and np.isfinite(Mw).all()):
            continue
        var_m = float(((Mw - Mw.mean()) ** 2).mean())
        if var_m <= 0:
            continue
        cov = float(((Xw - Xw.mean()) * (Mw - Mw.mean())).mean())
        beta = cov / var_m
        resid = (Xw - Xw.mean()) - beta * (Mw - Mw.mean())
        out[t] = float(np.sqrt((resid * resid).mean()))
    return out


def _assert_distinct(semc, ref, name):
    fin = np.isfinite(semc) & np.isfinite(ref)
    assert fin.sum() > 0, name
    assert not np.allclose(semc[fin], ref[fin], atol=1e-6), f"SEMCORR degenerates to {name}"


def test_semcorr_kernel_distinct_from_xcorr():
    rng = np.random.default_rng(201)
    n_assets, n_bars = 5, 1200
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    W = R.SEMCORR_W
    mm = R.compute_semcorr_metrics(log_return, W)
    sc = mm["semcorr_asym"][0, W:]
    ref = _xcorr_style_stat(log_return, W)[0, W:]
    _assert_distinct(sc, ref, "XCORR")


def test_semcorr_kernel_distinct_from_betaasym():
    rng = np.random.default_rng(202)
    n_assets, n_bars = 5, 1200
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    market = log_return.mean(axis=0)
    W = R.SEMCORR_W
    mm = R.compute_semcorr_metrics(log_return, W)
    sc = mm["semcorr_asym"][0, W:]
    _assert_distinct(sc, _betaasym_style_stat(log_return[0], market, W)[W:], "BETAASYM")


def test_semcorr_kernel_distinct_from_coskew():
    rng = np.random.default_rng(203)
    n_assets, n_bars = 5, 1200
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    market = log_return.mean(axis=0)
    W = R.SEMCORR_W
    mm = R.compute_semcorr_metrics(log_return, W)
    sc = mm["semcorr_asym"][0, W:]
    _assert_distinct(sc, _coskew_style_stat(log_return[0], market, W)[W:], "COSKEW")


def test_semcorr_kernel_distinct_from_semicov():
    rng = np.random.default_rng(204)
    n_assets, n_bars = 5, 1200
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    W = R.SEMCORR_W
    mm = R.compute_semcorr_metrics(log_return, W)
    sc = mm["semcorr_asym"][0, W:]
    _assert_distinct(sc, _semicov_style_stat(log_return[0], W)[W:], "SEMICOV")


def test_semcorr_kernel_distinct_from_acovk():
    rng = np.random.default_rng(205)
    n_assets, n_bars = 5, 1200
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    W = R.SEMCORR_W
    mm = R.compute_semcorr_metrics(log_return, W)
    sc = mm["semcorr_asym"][0, W:]
    _assert_distinct(sc, _acovk_style_stat(log_return[0], W)[W:], "ACOVK")


def test_semcorr_kernel_distinct_from_xsrank():
    rng = np.random.default_rng(206)
    n_assets, n_bars = 5, 1200
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    W = R.SEMCORR_W
    mm = R.compute_semcorr_metrics(log_return, W)
    sc = mm["semcorr_asym"][0, W:]
    _assert_distinct(sc, _xsrank_style_stat(log_return[0], W)[W:], "XSRANK")


def test_semcorr_kernel_distinct_from_leadlag():
    rng = np.random.default_rng(207)
    n_assets, n_bars = 5, 1200
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    market = log_return.mean(axis=0)
    W = R.SEMCORR_W
    mm = R.compute_semcorr_metrics(log_return, W)
    sc = mm["semcorr_asym"][0, W:]
    _assert_distinct(sc, _leadlag_style_stat(log_return[0], market, W)[W:], "LEADLAG")


def test_semcorr_kernel_distinct_from_residvol():
    rng = np.random.default_rng(208)
    n_assets, n_bars = 5, 1200
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    market = log_return.mean(axis=0)
    W = R.SEMCORR_W
    mm = R.compute_semcorr_metrics(log_return, W)
    sc = mm["semcorr_asym"][0, W:]
    _assert_distinct(sc, _residvol_style_stat(log_return[0], market, W)[W:], "RESIDVOL")


# ---------------------------------------------------------------- guard tests (rewrite guards)
def test_artifact_campaign_is_411():
    """Rewrite guard: every emitted artifact self-identifies campaign 411."""
    for part in ("verdict", "summary", "registry", "oos_sweep"):
        files = sorted((ROOT / "reports").glob(f"campaign411_{part}_*.json"))
        files = [f for f in files if ".full." not in f.name]
        if not files:
            continue
        obj = json.loads(files[-1].read_text())
        assert obj["campaign"] == 411, f"{part} artifact campaign != 411: {obj.get('campaign')}"


def test_mandate_contains_semcorr():
    """Rewrite guard: the C411 mandate names SEMCORR sign-conditional average
    pairwise correlation asymmetry (never prior families)."""
    p = sorted((ROOT / "reports").glob("campaign411_oos_sweep_*.json"))
    p = [f for f in p if ".full." not in f.name]
    if not p:
        return
    mandate = json.loads(p[-1].read_text())["mandate"]
    assert "SEMCORR" in mandate, "mandate missing SEMCORR"
    assert "CONDITIONAL" in mandate, "mandate missing CONDITIONAL"
    assert "PAIRWISE" in mandate, "mandate missing PAIRWISE"
    assert "CORRELATION" in mandate, "mandate missing CORRELATION"
    assert "ASYMMETRY" in mandate, "mandate missing ASYMMETRY"
    for bad in ("XCORR", "RESIDVOL", "IDIOSYNCRATIC", "RESIDUAL",
                "LEADLAG", "LEADER-FOLLOWER", "BETAASYM", "COSKEW", "COKURT",
                "ASYMCURV", "TSCALE", "HILL",
                "RVQUART", "QUARTICITY", "KTREND", "CBREAK", "SPECFM", "MAGNET",
                "OUHALFLIFE", "CTES", "VTERM", "DDRUN", "XSKEW3", "XCOEX", "MINRV",
                "MADR", "BANDX", "PRROUGH", "HALFRANGE", "LMOM", "SEMICOV", "LVAC", "DSRV",
                "RSKEK", "DOMINANT", "SPECTRAL", "CENTROID", "ACOVK", "TIRV", "XSRANK",
                "RANK-PERSISTENCE"):
        assert bad not in mandate, f"mandate must not reference {bad} (prior campaign)"


def test_placebo_seed_is_20261275():
    assert R.PLACEBO_SEED == 20261275


def test_placebo_seed_unique_not_reserved():
    """Rewrite guard: C411 placebo seed 20261275 must not collide with reserved
    seeds 20261224–20261274 used by prior campaigns."""
    assert not (20261224 <= R.PLACEBO_SEED <= 20261274), "placebo seed must be outside 20261224-20261274"


# ---------------------------------------------------------------- real artifacts schema (if present)
def _find_latest(prefix: str):
    files = sorted((ROOT / "reports").glob(f"campaign411_{prefix}_*.json"))
    files = [f for f in files if ".full." not in f.name]
    return files[-1] if files else None


def test_artifacts_if_present_have_required_flags():
    p = _find_latest("verdict")
    if p is None:
        return
    v = json.loads(p.read_text())
    assert v["campaign"] == 411
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
    assert sw["config"]["semcorr_params"]["window_W"] == 256


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
    test_semcorr_matches_brute_force()
    test_semcorr_matches_brute_force_10_assets()
    test_semcorr_defined_after_window_nan_before()
    test_semcorr_bounds_in_unit_interval()
    test_semcorr_non_finite_return_propagates()
    test_semcorr_params()
    test_reference_config_matches_pre_registered_spec()
    test_phase_randomized_surrogate_same_marginal_deterministic()
    test_build_underlying_shapes_and_keys()
    test_build_scores_signals_lookbacks_causal()
    test_semcorr_kernel_not_degenerate()
    test_semcorr_up_and_down_are_distinct_objects()
    test_semcorr_asym_not_zero_where_defined()
    test_semcorr_kernel_distinct_from_xcorr()
    test_semcorr_kernel_distinct_from_betaasym()
    test_semcorr_kernel_distinct_from_coskew()
    test_semcorr_kernel_distinct_from_semicov()
    test_semcorr_kernel_distinct_from_acovk()
    test_semcorr_kernel_distinct_from_xsrank()
    test_semcorr_kernel_distinct_from_leadlag()
    test_semcorr_kernel_distinct_from_residvol()
    test_artifact_campaign_is_411()
    test_mandate_contains_semcorr()
    test_placebo_seed_is_20261275()
    test_placebo_seed_unique_not_reserved()
    test_artifacts_if_present_have_required_flags()
    print("All C411 SEMCORR runner tests passed")
