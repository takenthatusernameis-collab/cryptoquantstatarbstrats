"""Tests for C416 runner (scripts/run_c416_qreg_xsec_oos.py): pure-function
tests on synthetic arrays (including a brute-force equality test for the
vectorized QREG quantile regression kernel vs the per-window reference)
plus schema/flag validation of emitted real-data artifacts.
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

import run_c416_qreg_xsec_oos as R  # noqa: E402


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
    assert R.N_TRIALS == 2592
    assert len(R.SIGNALS) == 8
    assert len(R.LOOKBACKS) == 6
    assert len(R.REBALANCES) == 3
    assert len(R.FEES) == 3 and len(R.SLIPS) == 3 and len(R.COST_VARIANTS) == 2
    assert R.N_TRIALS == (len(R.SIGNALS) * len(R.LOOKBACKS) * len(R.REBALANCES)
                          * len(R.FEES) * len(R.SLIPS) * len(R.COST_VARIANTS))
    for pb in ("qreg_slope_0.1_placebo", "qreg_slope_0.5_placebo",
               "qreg_slope_0.9_placebo", "qreg_spread_placebo"):
        assert pb in R.SIGNALS
    for real in ("qreg_slope_0.1_dev", "qreg_slope_0.5_dev",
                 "qreg_slope_0.9_dev", "qreg_spread_dev"):
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


# ---------------------------------------------------------------- QREG kernel (brute-force equality)
def test_qreg_matches_brute_force():
    """The vectorized QREG kernel MUST equal the brute-force reference
    (per-window loop with identical LP solve). Compared with maxdiff < 1e-12
    with matching NaN patterns."""
    rng = np.random.default_rng(20261280)
    n_assets, n_bars = 5, 4000
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    fast = R.compute_qreg_metrics(log_return, R.QREG_W, R.QREG_TAUS)
    brute = R._qreg_bruteforce(log_return, R.QREG_W, R.QREG_TAUS)
    for key in ("qreg_slope_0.1", "qreg_slope_0.5", "qreg_slope_0.9", "qreg_spread"):
        fv, fb = fast[key], brute[key]
        fin = np.isfinite(fv) & np.isfinite(fb)
        assert fin.sum() > 0, f"{key}: no finite overlapping points"
        assert np.array_equal(np.isnan(fv), np.isnan(fb)), f"{key}: NaN pattern mismatch"
        maxdiff = float(np.max(np.abs(fv[fin] - fb[fin]))) if fin.sum() else 0.0
        assert maxdiff < 1e-12, f"{key}: maxdiff={maxdiff} >= 1e-12"


def test_qreg_matches_brute_force_10_assets():
    """Brute-force equality with the full 10-asset panel (the real universe width)."""
    rng = np.random.default_rng(4162)
    n_assets, n_bars = 10, 1500
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    fast = R.compute_qreg_metrics(log_return, R.QREG_W, R.QREG_TAUS)
    brute = R._qreg_bruteforce(log_return, R.QREG_W, R.QREG_TAUS)
    for key in ("qreg_slope_0.1", "qreg_slope_0.5", "qreg_slope_0.9", "qreg_spread"):
        fv, fb = fast[key], brute[key]
        fin = np.isfinite(fv) & np.isfinite(fb)
        assert fin.sum() > 0, key
        maxdiff = float(np.max(np.abs(fv[fin] - fb[fin])))
        assert maxdiff < 1e-12, f"qreg_{key}: maxdiff={maxdiff}"


def test_qreg_defined_after_window_nan_before():
    rng = np.random.default_rng(3)
    n_assets, n_bars = 3, 600
    common = rng.standard_normal(n_bars) * 0.005
    log_return = common[None, :] + rng.standard_normal((n_assets, n_bars)) * 0.001
    W = R.QREG_W
    m = R.compute_qreg_metrics(log_return, W)
    for key in ("qreg_slope_0.1", "qreg_slope_0.5", "qreg_slope_0.9", "qreg_spread"):
        assert np.isnan(m[key][:, :W]).all(), key
        assert np.isfinite(m[key][:, W:]).any(), key


def test_qreg_non_finite_return_propagates():
    """A non-finite return in any asset's window -> NaN for all QREG
    outputs in affected bars (the whole panel window is non-finite)."""
    rng = np.random.default_rng(9)
    n_assets, n_bars = 4, 600
    common = rng.standard_normal(n_bars) * 0.005
    log_return = common[None, :] + rng.standard_normal((n_assets, n_bars)) * 0.001
    log_return[0, 300] = np.inf
    W = R.QREG_W
    m = R.compute_qreg_metrics(log_return, W)
    for t in range(300, min(300 + W, n_bars)):
        for key in ("qreg_slope_0.1", "qreg_slope_0.5", "qreg_slope_0.9", "qreg_spread"):
            assert np.isnan(m[key][:, t]).all(), f"qreg_{key} t={t} should be NaN"
    for t in range(W, 300):
        for key in ("qreg_slope_0.1", "qreg_slope_0.5", "qreg_slope_0.9", "qreg_spread"):
            assert np.isfinite(m[key][:, t]).any(), f"qreg_{key} t={t} should be finite"


def test_qreg_params():
    assert R.QREG_W == 256
    assert tuple(R.QREG_TAUS) == (0.1, 0.5, 0.9)


def test_reference_config_matches_pre_registered_spec():
    assert R.ATTR_REPRESENTATIVES == {
        "qreg_slope_0.1_dev": "qreg_slope_0.1_dev",
        "qreg_slope_0.5_dev": "qreg_slope_0.5_dev",
        "qreg_slope_0.9_dev": "qreg_slope_0.9_dev",
        "qreg_spread_dev": "qreg_spread_dev",
    }
    assert R.PLACEBO_SEED == 20261280
    assert R.STABILITY_MIN_SIGN_CONSISTENCY == 0.70
    assert R.STABILITY_MIN_SHARPE_CORR == 0.50
    assert R.DOMINANT_SHARE_MIN == 0.50
    assert R.TRAIN_M == 12 and R.TEST_M == 3 and R.ROLL_M == 3
    assert R.QREG_W == 256
    assert R.SIGNALS[0] == "qreg_slope_0.1_dev"


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
    assert set(series.keys()) == {"qreg_slope_0.1", "qreg_slope_0.5", "qreg_slope_0.9", "qreg_spread"}
    for k in ("qreg_slope_0.1", "qreg_slope_0.5", "qreg_slope_0.9", "qreg_spread"):
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
def test_qreg_kernel_not_degenerate():
    """Rewrite guard: QREG metrics are not degenerate (not allclose to 0 where defined)."""
    rng = np.random.default_rng(55)
    n_assets, n_bars = 5, 1600
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    W = R.QREG_W
    mm = R.compute_qreg_metrics(log_return, W)
    for name in ("qreg_slope_0.1", "qreg_slope_0.5", "qreg_slope_0.9", "qreg_spread"):
        arr = mm[name]
        fin = np.isfinite(arr)
        assert fin.sum() > 0, f"qreg_{name}: no finite values"
        assert not np.allclose(arr[fin], 0.0, atol=1e-12), f"qreg_{name} collapses to 0"


# ---- inline prior-family reference statistics (distinctness guards)
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


def _semcorr_style_stat(log_return, W):
    """Inline C411 SEMCORR asymmetry: sign-conditional average pairwise
    Pearson correlation asymmetry (up_corr - down_corr)."""
    X = np.asarray(log_return, dtype=float)
    n_assets, n = X.shape
    out = np.full((n_assets, n), np.nan)
    for t in range(W, n):
        span = X[:, t - W + 1:t + 1]
        if not np.isfinite(span).all():
            continue
        m = span.mean(axis=0)
        up_mask = m > 0
        down_mask = m < 0
        cu = int(up_mask.sum())
        cd = int(down_mask.sum())
        if cu < 3 or cd < 3:
            continue
        xi_up_all = []
        xi_down_all = []
        ok = True
        for i in range(n_assets):
            xi_up = span[i][up_mask]
            xi_down = span[i][down_mask]
            if xi_up.std() <= 0 or xi_down.std() <= 0:
                ok = False
                break
            xi_up_all.append(xi_up)
            xi_down_all.append(xi_down)
        if not ok:
            continue
        asyms = []
        for i in range(n_assets):
            corrs_up = []
            corrs_down = []
            for j in range(n_assets):
                if j == i:
                    continue
                corrs_up.append(float(np.corrcoef(xi_up_all[i], xi_up_all[j])[0, 1]))
                corrs_down.append(float(np.corrcoef(xi_down_all[i], xi_down_all[j])[0, 1]))
            asyms.append(float(np.mean(corrs_up)) - float(np.mean(corrs_down)))
        for i, v in enumerate(asyms):
            out[i, t] = v
    return out


def _signpower_style_stat(X, W, p):
    """Inline C412 SIGNPOWER signed fractional power moment: mean(sign(X)*|X|^p)."""
    n = len(X)
    out = np.full(n, np.nan)
    for t in range(W, n):
        Xw = X[t - W + 1:t + 1]
        if not np.isfinite(Xw).all():
            continue
        out[t] = float(np.mean(np.sign(Xw) * np.abs(Xw) ** p))
    return out


def _signcomotion_style_stat(log_return, W):
    """Inline C414 SIGNCO-MOTION sign_agree_asym: same-sign co-motion fraction
    vs equal-weight market, up-market minus down-market agreement."""
    X = np.asarray(log_return, dtype=float)
    n_assets, n = X.shape
    m = X.mean(axis=0)
    out = np.full((n_assets, n), np.nan)
    for t in range(W, n):
        Mw = m[t - W + 1:t + 1]
        if not np.isfinite(Mw).all():
            continue
        for i in range(n_assets):
            Xw = X[i, t - W + 1:t + 1]
            if not np.isfinite(Xw).all():
                continue
            sx = np.sign(Xw)
            sm = np.sign(Mw)
            same = (sx == sm) & (sx != 0) & (sm != 0)
            up = Mw > 0
            down = Mw < 0
            up_cnt = int(up.sum())
            down_cnt = int(down.sum())
            if up_cnt > 0 and down_cnt > 0:
                out[i, t] = float(same[up].mean() - same[down].mean())
    return out


def _tailbeta_style_stat(log_return, W, q=0.10):
    """Inline C413 TAILBETA tail-beta asymmetry: joint lower-tail beta minus
    joint upper-tail beta over trailing W with q-tail quantile masking."""
    X = np.asarray(log_return, dtype=float)
    n_assets, n = X.shape
    m = X.mean(axis=0)
    out = np.full((n_assets, n), np.nan)
    for t in range(W, n):
        span = X[:, t - W + 1:t + 1]
        if not np.isfinite(span).all():
            continue
        mw = m[t - W + 1:t + 1]
        if not np.isfinite(mw).all():
            continue
        for i in range(n_assets):
            Xw = span[i]
            qx_lo, qx_hi = np.quantile(Xw, q), np.quantile(Xw, 1 - q)
            qm_lo, qm_hi = np.quantile(mw, q), np.quantile(mw, 1 - q)
            lo_mask = (Xw <= qx_lo) & (mw <= qm_lo)
            hi_mask = (Xw >= qx_hi) & (mw >= qm_hi)
            if int(lo_mask.sum()) < 10 or int(hi_mask.sum()) < 10:
                continue
            Mw_lo = mw[lo_mask]
            if float(Mw_lo.var()) <= 0:
                continue
            beta_lo = float(np.cov(Xw[lo_mask], Mw_lo, ddof=0)[0, 1]) / float(Mw_lo.var())
            Mw_hi = mw[hi_mask]
            if float(Mw_hi.var()) <= 0:
                continue
            beta_hi = float(np.cov(Xw[hi_mask], Mw_hi, ddof=0)[0, 1]) / float(Mw_hi.var())
            out[i, t] = beta_hi - beta_lo
    return out


def _taildep_style_stat(log_return, W=256, q=0.10):
    """Inline C415 TAILDEP tail dependence asymmetry."""
    X = np.asarray(log_return, dtype=float)
    n_assets, n = X.shape
    m = X.mean(axis=0)
    out = np.full((n_assets, n), np.nan)
    for t in range(W, n):
        Mw = m[t - W + 1:t + 1]
        if not np.isfinite(Mw).all():
            continue
        qm_lo = float(np.quantile(Mw, q))
        qm_hi = float(np.quantile(Mw, 1 - q))
        m_lo_cnt = int((Mw <= qm_lo).sum())
        m_hi_cnt = int((Mw >= qm_hi).sum())
        for i in range(n_assets):
            Xw = X[i, t - W + 1:t + 1]
            if not np.isfinite(Xw).all():
                continue
            qx_lo = float(np.quantile(Xw, q))
            qx_hi = float(np.quantile(Xw, 1 - q))
            lo_mask = (Xw <= qx_lo) & (Mw <= qm_lo)
            hi_mask = (Xw >= qx_hi) & (Mw >= qm_hi)
            if m_lo_cnt >= 10 and m_hi_cnt >= 10:
                low = float(lo_mask.sum()) / float(m_lo_cnt)
                high = float(hi_mask.sum()) / float(m_hi_cnt)
                out[i, t] = high - low
    return out


def _assert_distinct(sa, ref, name):
    fin = np.isfinite(sa) & np.isfinite(ref)
    assert fin.sum() > 0, name
    assert not np.allclose(sa[fin], ref[fin], atol=1e-6), f"QREG degenerates to {name}"


def test_qreg_kernel_distinct_from_betaasym():
    rng = np.random.default_rng(214)
    n_assets, n_bars = 5, 1200
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    market = log_return.mean(axis=0)
    W = R.QREG_W
    mm = R.compute_qreg_metrics(log_return, W)
    sa = mm["qreg_spread"][0, W:]
    _assert_distinct(sa, _betaasym_style_stat(log_return[0], market, W)[W:], "BETAASYM")


def test_qreg_kernel_distinct_from_residvol():
    rng = np.random.default_rng(215)
    n_assets, n_bars = 5, 1200
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    market = log_return.mean(axis=0)
    W = R.QREG_W
    mm = R.compute_qreg_metrics(log_return, W)
    sa = mm["qreg_slope_0.5"][0, W:]
    _assert_distinct(sa, _residvol_style_stat(log_return[0], market, W)[W:], "RESIDVOL")


def test_qreg_kernel_distinct_from_xcorr():
    rng = np.random.default_rng(212)
    n_assets, n_bars = 5, 1200
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    W = R.QREG_W
    mm = R.compute_qreg_metrics(log_return, W)
    sa = mm["qreg_spread"][0, W:]
    _assert_distinct(sa, _xcorr_style_stat(log_return, W)[0, W:], "XCORR")


def test_qreg_kernel_distinct_from_semcorr():
    rng = np.random.default_rng(213)
    n_assets, n_bars = 5, 1200
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    W = R.QREG_W
    mm = R.compute_qreg_metrics(log_return, W)
    sa = mm["qreg_slope_0.1"][0, W:]
    _assert_distinct(sa, _semcorr_style_stat(log_return, W)[0, W:], "SEMCORR")


def test_qreg_kernel_distinct_from_signpower():
    rng = np.random.default_rng(216)
    n_assets, n_bars = 5, 1200
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    W = R.QREG_W
    mm = R.compute_qreg_metrics(log_return, W)
    sa = mm["qreg_slope_0.1"][0, W:]
    for p in (0.5, 1.5, 2.5):
        ref = _signpower_style_stat(log_return[0], W, p)[W:]
        _assert_distinct(sa, ref, f"SIGNPOWER_p{p}")


def test_qreg_kernel_distinct_from_signcomotion():
    """C414 SIGNCO-MOTION: legitimate distinctness-guard ref (prior family)."""
    rng = np.random.default_rng(217)
    n_assets, n_bars = 5, 1200
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    W = R.QREG_W
    mm = R.compute_qreg_metrics(log_return, W)
    sa = mm["qreg_spread"][0, W:]
    _assert_distinct(sa, _signcomotion_style_stat(log_return, W)[0, W:], "SIGNCO-MOTION")


def test_qreg_kernel_distinct_from_tailbeta():
    """C413 TAILBETA: legitimate distinctness-guard ref (prior family)."""
    rng = np.random.default_rng(211)
    n_assets, n_bars = 5, 1200
    market = rng.standard_normal(n_bars) * 0.02
    log_return = market[None, :] + rng.standard_normal((n_assets, n_bars)) * 0.001
    W = R.QREG_W
    mm = R.compute_qreg_metrics(log_return, W)
    sa = mm["qreg_spread"][0, W:]
    _assert_distinct(sa, _tailbeta_style_stat(log_return, W)[0, W:], "TAILBETA")


def test_qreg_kernel_distinct_from_taildep():
    """C415 TAILDEP: legitimate distinctness-guard ref (prior family)."""
    rng = np.random.default_rng(210)
    n_assets, n_bars = 5, 1200
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    W = R.QREG_W
    mm = R.compute_qreg_metrics(log_return, W)
    sa = mm["qreg_slope_0.1"][0, W:]
    _assert_distinct(sa, _taildep_style_stat(log_return, W)[0, W:], "TAILDEP")


# ---------------------------------------------------------------- guard tests (rewrite guards)
def test_artifact_campaign_is_416():
    """Rewrite guard: every emitted artifact self-identifies campaign 416."""
    for part in ("verdict", "summary", "registry", "oos_sweep"):
        files = sorted((ROOT / "reports").glob(f"campaign416_{part}_*.json"))
        files = [f for f in files if ".full." not in f.name]
        if not files:
            continue
        obj = json.loads(files[-1].read_text())
        assert obj["campaign"] == 416, f"{part} artifact campaign != 416: {obj.get('campaign')}"


def test_mandate_contains_qreg():
    """Rewrite guard: the C416 mandate names QREG quantile regression vs
    equal-weight market (never prior families)."""
    p = sorted((ROOT / "reports").glob("campaign416_oos_sweep_*.json"))
    p = [f for f in p if ".full." not in f.name]
    if not p:
        return
    mandate = json.loads(p[-1].read_text())["mandate"]
    assert "QREG" in mandate, "mandate missing QREG"
    assert "quantile regression" in mandate.lower(), "mandate missing quantile regression"
    assert "EQUAL-WEIGHT MARKET" in mandate, "mandate missing EQUAL-WEIGHT MARKET"
    for bad in ("SIGNCO-MOTION", "SAME-SIGN", "TAILBETA", "TAIL BETA", "EXTREME",
                "SIGNPOWER", "FRACTIONAL", "POWER", "XCORR", "SEMCORR",
                "CONDITIONAL", "PAIRWISE", "CORRELATION", "RESIDVOL",
                "IDIOSYNCRATIC", "RESIDUAL", "LEADLAG", "LEADER-FOLLOWER",
                "BETAASYM", "COSKEW", "COKURT", "ASYMCURV", "TSCALE", "HILL",
                "RVQUART", "QUARTICITY", "KTREND", "CBREAK", "SPECFM", "MAGNET",
                "OUHALFLIFE", "CTES", "VTERM", "DDRUN", "XSKEW3", "XCOEX",
                "MINRV", "MADR", "BANDX", "PRROUGH", "HALFRANGE", "LMOM",
                "SEMICOV", "LVAC", "DSRV", "RSKEK", "DOMINANT", "SPECTRAL",
                "CENTROID", "ACOVK", "TIRV", "XSRANK", "RANK-PERSISTENCE",
                "SIGNRUN", "RUN-LENGTH", "TAILDEP", "TAIL DEPENDENCE", "EXCEEDANCE",
                "TAIL COPULA"):
        assert bad not in mandate, f"mandate must not reference {bad} (prior campaign)"


def test_placebo_seed_is_20261280():
    assert R.PLACEBO_SEED == 20261280


def test_placebo_seed_unique_not_reserved():
    """Rewrite guard: C416 placebo seed 20261280 must not collide with reserved
    seeds 20261224–20261279 used by prior campaigns."""
    assert not (20261224 <= R.PLACEBO_SEED <= 20261279), "placebo seed must be outside 20261224-20261279"


# ---------------------------------------------------------------- real artifacts schema (if present)
def _find_latest(prefix: str):
    files = sorted((ROOT / "reports").glob(f"campaign416_{prefix}_*.json"))
    files = [f for f in files if ".full." not in f.name]
    return files[-1] if files else None


def test_artifacts_if_present_have_required_flags():
    p = _find_latest("verdict")
    if p is None:
        return
    v = json.loads(p.read_text())
    assert v["campaign"] == 416
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
    assert sw["config"]["qreg_params"]["window_W"] == 256
    assert sw["config"]["qreg_params"]["taus"] == [0.1, 0.5, 0.9]


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
    test_qreg_matches_brute_force()
    test_qreg_matches_brute_force_10_assets()
    test_qreg_defined_after_window_nan_before()
    test_qreg_non_finite_return_propagates()
    test_qreg_params()
    test_reference_config_matches_pre_registered_spec()
    test_phase_randomized_surrogate_same_marginal_deterministic()
    test_build_underlying_shapes_and_keys()
    test_build_scores_signals_lookbacks_causal()
    test_qreg_kernel_not_degenerate()
    test_qreg_kernel_distinct_from_betaasym()
    test_qreg_kernel_distinct_from_residvol()
    test_qreg_kernel_distinct_from_xcorr()
    test_qreg_kernel_distinct_from_semcorr()
    test_qreg_kernel_distinct_from_signpower()
    test_qreg_kernel_distinct_from_signcomotion()
    test_qreg_kernel_distinct_from_tailbeta()
    test_qreg_kernel_distinct_from_taildep()
    test_artifact_campaign_is_416()
    test_mandate_contains_qreg()
    test_placebo_seed_is_20261280()
    test_placebo_seed_unique_not_reserved()
    test_artifacts_if_present_have_required_flags()
    print("All C416 QREG runner tests passed")