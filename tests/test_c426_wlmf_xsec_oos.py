"""Tests for C425 runner (scripts/run_c425_rqa_xsec_oos.py): pure-function
tests on synthetic arrays (including a brute-force equality test for the
vectorized RQA recurrence-quantification-analysis kernel vs the per-window
explicit embedding + distance matrix + RQA-measures reference) plus
schema/flag validation of emitted real-data artifacts. No network, no
fabricated market data."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import run_c425_rqa_xsec_oos as R  # noqa: E402


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
    for pb in ("rqa_rr_placebo", "rqa_det_placebo", "rqa_lam_placebo", "rqa_tt_placebo"):
        assert pb in R.SIGNALS
    for real in ("rqa_rr_dev", "rqa_det_dev", "rqa_lam_dev", "rqa_tt_dev"):
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


# ---------------------------------------------------------------- RQA kernel (brute-force equality)
def test_rqa_matches_brute_force():
    """The vectorized RQA kernel MUST equal the brute-force reference
    (per-window loop with explicit embedding + distance matrix + RQA measures).
    Compared with maxdiff < 1e-12 and matching NaN patterns."""
    rng = np.random.default_rng(20261289)
    n_assets, n_bars = 5, 4000
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    fast = R.compute_rqa_metrics(close, W=R.RQA_W)
    brute = R._rqa_bruteforce(close, W=R.RQA_W)
    for key in ("rqa_rr", "rqa_det", "rqa_lam", "rqa_tt"):
        fv, fb = fast[key], brute[key]
        fin = np.isfinite(fv) & np.isfinite(fb)
        assert fin.sum() > 0, f"{key}: no finite overlapping points"
        assert np.array_equal(np.isnan(fv), np.isnan(fb)), f"{key}: NaN pattern mismatch"
        maxdiff = float(np.max(np.abs(fv[fin] - fb[fin]))) if fin.sum() else 0.0
        assert maxdiff < 1e-12, f"{key}: maxdiff={maxdiff} >= 1e-12"


def test_rqa_matches_brute_force_10_assets():
    """Brute-force equality with the full 10-asset panel (the real universe width)."""
    rng = np.random.default_rng(4254)
    n_assets, n_bars = 10, 1500
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    fast = R.compute_rqa_metrics(close, W=R.RQA_W)
    brute = R._rqa_bruteforce(close, W=R.RQA_W)
    for key in ("rqa_rr", "rqa_det", "rqa_lam", "rqa_tt"):
        fv, fb = fast[key], brute[key]
        fin = np.isfinite(fv) & np.isfinite(fb)
        assert fin.sum() > 0, key
        maxdiff = float(np.max(np.abs(fv[fin] - fb[fin])))
        assert maxdiff < 1e-12, f"rqa_{key}: maxdiff={maxdiff}"


def test_rqa_matches_brute_force_with_nan():
    """Brute-force equality when the panel contains NaNs (global across assets)."""
    rng = np.random.default_rng(99)
    n_assets, n_bars = 4, 1200
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    close[1, 400] = np.nan
    close[2, 401] = np.nan
    fast = R.compute_rqa_metrics(close, W=R.RQA_W)
    brute = R._rqa_bruteforce(close, W=R.RQA_W)
    for key in ("rqa_rr", "rqa_det", "rqa_lam", "rqa_tt"):
        fv, fb = fast[key], brute[key]
        fin = np.isfinite(fv) & np.isfinite(fb)
        assert np.array_equal(np.isnan(fv), np.isnan(fb)), f"{key}: NaN mismatch"
        maxdiff = float(np.max(np.abs(fv[fin] - fb[fin]))) if fin.sum() else 0.0
        assert maxdiff < 1e-12, f"{key}: maxdiff={maxdiff}"


def test_rqa_defined_after_window_nan_before():
    rng = np.random.default_rng(3)
    n_assets, n_bars = 3, 600
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.005, axis=1))
    W = R.RQA_W
    m = R.compute_rqa_metrics(close, W=W)
    for key in ("rqa_rr", "rqa_det", "rqa_lam", "rqa_tt"):
        assert np.isnan(m[key][:, :W]).all(), key
        assert np.isfinite(m[key][:, W:]).any(), key


def test_rqa_non_finite_close_propagates():
    """A non-finite close in any asset at a bar -> NaN for all RQA outputs
    in every window covering that bar (global-across-assets finiteness gate)."""
    rng = np.random.default_rng(9)
    n_assets, n_bars = 4, 600
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.005, axis=1))
    close[0, 300] = np.inf
    W = R.RQA_W
    m = R.compute_rqa_metrics(close, W=W)
    for t in range(300, min(300 + W, n_bars)):
        for key in ("rqa_rr", "rqa_det", "rqa_lam", "rqa_tt"):
            assert np.isnan(m[key][:, t]).all(), f"rqa_{key} t={t} should be NaN"
    # Before the bad bar the gate must not over-NaN. rqa_rr is finite whenever any
    # recurrence point exists, so it is the reliable probe; rqa_tt (mean vertical
    # line length for v>=v_min) is legitimately NaN when a window has no such line.
    for t in range(W, 300):
        assert np.isfinite(m["rqa_rr"][:, t]).any(), f"rqa_rr t={t} should be finite"


def test_rqa_params():
    assert R.RQA_W == 256
    assert R.RQA_M == 3
    assert R.RQA_TAU == 1
    assert R.RQA_EPS_SIGMA_MULT == 0.1
    assert R.RQA_L_MIN == 2
    assert R.RQA_V_MIN == 2


def test_rqa_rr_range():
    """rqa_rr in [0,1] where defined (density of recurrence points)."""
    rng = np.random.default_rng(2026)
    n_assets, n_bars = 2, 1000
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    W = R.RQA_W
    m = R.compute_rqa_metrics(close, W=W)
    fin = np.isfinite(m["rqa_rr"])
    assert (m["rqa_rr"][fin] >= 0.0).all()
    assert (m["rqa_rr"][fin] <= 1.0 + 1e-12).all()


def test_rqa_det_range():
    """rqa_det in [0,1] where defined."""
    rng = np.random.default_rng(2027)
    n_assets, n_bars = 2, 1000
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    W = R.RQA_W
    m = R.compute_rqa_metrics(close, W=W)
    fine = np.isfinite(m["rqa_det"])
    assert (m["rqa_det"][fine] >= 0.0 - 1e-12).all()
    assert (m["rqa_det"][fine] <= 1.0 + 1e-12).all()


def test_rqa_lam_range():
    """rqa_lam in [0,1] where defined."""
    rng = np.random.default_rng(2028)
    n_assets, n_bars = 2, 1000
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    W = R.RQA_W
    m = R.compute_rqa_metrics(close, W=W)
    fine = np.isfinite(m["rqa_lam"])
    assert (m["rqa_lam"][fine] >= 0.0 - 1e-12).all()
    assert (m["rqa_lam"][fine] <= 1.0 + 1e-12).all()


def test_rqa_tt_range():
    """rqa_tt >= 1 where defined (minimum vertical line length is 1)."""
    rng = np.random.default_rng(2029)
    n_assets, n_bars = 2, 1000
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    W = R.RQA_W
    m = R.compute_rqa_metrics(close, W=W)
    fine = np.isfinite(m["rqa_tt"])
    assert (m["rqa_tt"][fine] >= 1.0 - 1e-12).all()


def test_reference_config_matches_pre_registered_spec():
    assert R.ATTR_REPRESENTATIVES == {
        "rqa_rr_dev": "rqa_rr_dev",
        "rqa_det_dev": "rqa_det_dev",
        "rqa_lam_dev": "rqa_lam_dev",
        "rqa_tt_dev": "rqa_tt_dev",
    }
    assert R.PLACEBO_SEED == 20261289
    assert R.STABILITY_MIN_SIGN_CONSISTENCY == 0.70
    assert R.STABILITY_MIN_SHARPE_CORR == 0.50
    assert R.DOMINANT_SHARE_MIN == 0.50
    assert R.TRAIN_M == 12 and R.TEST_M == 3 and R.ROLL_M == 3
    assert R.RQA_W == 256
    assert R.SIGNALS[0] == "rqa_rr_dev"


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
    assert set(series.keys()) == {"rqa_rr", "rqa_det", "rqa_lam", "rqa_tt"}
    for k in ("rqa_rr", "rqa_det", "rqa_lam", "rqa_tt"):
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
def test_rqa_kernel_not_degenerate():
    """Rewrite guard: RQA metrics are not degenerate (not allclose to 0 where
    defined)."""
    rng = np.random.default_rng(55)
    n_assets, n_bars = 5, 1600
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    W = R.RQA_W
    mm = R.compute_rqa_metrics(close, W=W)
    for name in ("rqa_rr", "rqa_det", "rqa_lam", "rqa_tt"):
        arr = mm[name]
        fin = np.isfinite(arr)
        assert fin.sum() > 0, f"rqa_{name}: no finite values"
        assert not np.allclose(arr[fin], 0.0, atol=1e-12), f"rqa_{name} collapses to 0"


# ---- inline prior-family reference statistics (distinctness guards)
def _signchop_style_stat(close, W):
    """Inline C344-style statistic: sign-change / chop rate of the return sign
    sequence over the window — sign flips of the return sign, NOT recurrence-plot
    topology."""
    X = np.diff(np.log(close), axis=1)
    n_assets, n = X.shape
    out = np.full((n_assets, n), np.nan)
    for t in range(W, n):
        span = X[:, t - W + 1:t + 1]
        if not np.isfinite(span).all():
            continue
        for i in range(n_assets):
            s = np.sign(span[i])
            out[i, t] = float(np.mean(s[1:] != s[:-1])) if W > 1 else np.nan
    return out


def _signrun_style_stat(close, W):
    """Inline C374 SIGNRUN-style statistic: max run share / mean run length of
    signed runs — a single max/mean summary, NOT recurrence-plot topology."""
    X = np.diff(np.log(close), axis=1)
    n_assets, n = X.shape
    out = np.full((n_assets, n), np.nan)
    for t in range(W, n):
        span = X[:, t - W + 1:t + 1]
        if not np.isfinite(span).all():
            continue
        for i in range(n_assets):
            s = np.sign(span[i])
            s2 = s[s != 0]
            if len(s2) < 2:
                continue
            change = s2[1:] != s2[:-1]
            starts = np.concatenate([[0], np.nonzero(change)[0] + 1])
            lens = np.diff(np.concatenate([starts, [len(s2)]]))
            out[i, t] = float(lens.max() / lens.mean()) if lens.mean() > 0 else np.nan
    return out


def _zcrpath_style_stat(close, W):
    """Inline C422 ZCRPATH-style statistic: zero-crossing rate of the
    cumulative-return path — crossings of cumsum(X), NOT recurrence-plot topology."""
    X = np.diff(np.log(close), axis=1)
    n_assets, n = X.shape
    out = np.full((n_assets, n), np.nan)
    for t in range(W, n):
        span = X[:, t - W + 1:t + 1]
        if not np.isfinite(span).all():
            continue
        for i in range(n_assets):
            x = span[i]
            C = np.cumsum(x)
            chg = C[:-1] * C[1:] < 0
            out[i, t] = float(chg.sum() / (W - 1))
    return out


def _runlen_style_stat(close, W):
    """Inline C423 RUNLEN-style statistic: run-length distribution entropy of
    consecutive same-sign returns — full run-length entropy, NOT recurrence-plot
    topology."""
    X = np.diff(np.log(close), axis=1)
    n_assets, n = X.shape
    out = np.full((n_assets, n), np.nan)
    for t in range(W, n):
        span = X[:, t - W + 1:t + 1]
        if not np.isfinite(span).all():
            continue
        for i in range(n_assets):
            x = span[i]
            s = np.sign(x)
            s2 = s[s != 0.0]
            if len(s2) < 2:
                continue
            change = s2[1:] != s2[:-1]
            starts = np.concatenate([[0], np.nonzero(change)[0] + 1])
            lens = np.diff(np.concatenate([starts, [len(s2)]])).astype(float)
            signs_r = s2[starts]
            total = float(lens.sum())
            p = lens / total
            out[i, t] = float(-(p * np.log(p)).sum())
    return out


def _iesd_style_stat(close, W):
    """Inline C424 IESD-style statistic: mean spacing and spacing entropy of
    local-extremum gaps — inter-extremum spacing distribution, NOT recurrence-plot
    topology."""
    n_assets, n = close.shape
    out_mean = np.full((n_assets, n), np.nan)
    out_ent = np.full((n_assets, n), np.nan)
    for t in range(W, n):
        span = close[:, t - W:t + 1]
        if not np.isfinite(span).all():
            continue
        for i in range(n_assets):
            C = span[i]
            is_max = (C[1:-1] > C[:-2]) & (C[1:-1] > C[2:])
            is_min = (C[1:-1] < C[:-2]) & (C[1:-1] < C[2:])
            ext_rel = np.flatnonzero(is_max | is_min)
            if len(ext_rel) < 2:
                continue
            ext_pos = ext_rel + 1
            spacings = np.diff(ext_pos).astype(float)
            mean_g = float(spacings.mean())
            vals, counts = np.unique(spacings, return_counts=True)
            p = counts / float(counts.sum())
            ent = float(-(p * np.log(p)).sum())
            out_mean[i, t] = mean_g
            out_ent[i, t] = ent
    return out_mean, out_ent


def _assert_distinct(sa, ref, name):
    fin = np.isfinite(sa) & np.isfinite(ref)
    assert fin.sum() > 0, name
    assert not np.allclose(sa[fin], ref[fin], atol=1e-6), f"RQA degenerates to {name}"


def test_rqa_kernel_distinct_from_signchop():
    """C344 sign-change/chop rate: legitimate distinctness-guard ref
    (sign flips of the return sign vs recurrence-plot topology)."""
    rng = np.random.default_rng(214)
    n_assets, n_bars = 5, 1200
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    W = R.RQA_W
    mm = R.compute_rqa_metrics(close, W=W)
    sa = mm["rqa_det"][0, W:]
    ref = _signchop_style_stat(close, W)[0, W - 1:]
    _assert_distinct(sa, ref, "SIGNCHOP")


def test_rqa_kernel_distinct_from_signrun():
    """C374 SIGNRUN (max run share / mean run length): legitimate
    distinctness-guard ref (single max/mean summary vs recurrence-plot topology)."""
    rng = np.random.default_rng(217)
    n_assets, n_bars = 5, 1200
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    W = R.RQA_W
    mm = R.compute_rqa_metrics(close, W=W)
    sa = mm["rqa_det"][0, W:]
    ref = _signrun_style_stat(close, W)[0, W - 1:]
    _assert_distinct(sa, ref, "SIGNRUN")


def test_rqa_kernel_distinct_from_zcrpath():
    """C422 ZCRPATH (zero-crossing rate of cumulative-return path): legitimate
    distinctness-guard ref (cumulative-path crossings vs recurrence-plot topology)."""
    rng = np.random.default_rng(219)
    n_assets, n_bars = 5, 1200
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    W = R.RQA_W
    mm = R.compute_rqa_metrics(close, W=W)
    sa = mm["rqa_det"][0, W:]
    ref = _zcrpath_style_stat(close, W)[0, W - 1:]
    _assert_distinct(sa, ref, "ZCRPATH")


def test_rqa_kernel_distinct_from_runlen():
    """C423 RUNLEN (run-length distribution entropy of consecutive return signs):
    legitimate distinctness-guard ref (run-length entropy vs recurrence-plot topology)."""
    rng = np.random.default_rng(220)
    n_assets, n_bars = 5, 1200
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    W = R.RQA_W
    mm = R.compute_rqa_metrics(close, W=W)
    sa = mm["rqa_det"][0, W:]
    ref = _runlen_style_stat(close, W)[0, W - 1:]
    _assert_distinct(sa, ref, "RUNLEN")


def test_rqa_kernel_distinct_from_iesd():
    """C424 IESD (inter-extremum spacing distribution): legitimate
    distinctness-guard ref (spacing between local extrema vs recurrence-plot topology)."""
    rng = np.random.default_rng(224)
    n_assets, n_bars = 5, 1200
    close = 100.0 * np.exp(np.cumsum(rng.standard_normal((n_assets, n_bars)) * 0.001, axis=1))
    W = R.RQA_W
    mm = R.compute_rqa_metrics(close, W=W)
    sa = mm["rqa_det"][0, W:]
    ref_mean, ref_ent = _iesd_style_stat(close, W)
    ref = ref_mean[0, W:]
    _assert_distinct(sa, ref, "IESD")


# ---------------------------------------------------------------- guard tests (rewrite guards)
def test_artifact_campaign_is_425():
    """Rewrite guard: every emitted artifact self-identifies campaign 425."""
    for part in ("verdict", "summary", "registry", "oos_sweep"):
        files = sorted((ROOT / "reports").glob(f"campaign425_{part}_*.json"))
        files = [f for f in files if ".full." not in f.name]
        if not files:
            continue
        obj = json.loads(files[-1].read_text())
        assert obj["campaign"] == 425, f"{part} artifact campaign != 425: {obj.get('campaign')}"


def test_mandate_contains_rqa():
    """Rewrite guard: the C425 mandate names the RQA recurrence-quantification
    family (never prior families)."""
    p = sorted((ROOT / "reports").glob("campaign425_oos_sweep_*.json"))
    p = [f for f in p if ".full." not in f.name]
    if not p:
        return
    mandate = json.loads(p[-1].read_text())["mandate"]
    assert "RQA" in mandate, "mandate missing RQA"
    assert "rqa_rr" in mandate, "mandate missing rqa_rr"
    assert "rqa_det" in mandate, "mandate missing rqa_det"
    assert "rqa_lam" in mandate, "mandate missing rqa_lam"
    assert "rqa_tt" in mandate, "mandate missing rqa_tt"
    for bad in ("IESD", "INTER-EXTREMUM", "spacing_ent", "mean_spacing",
                "RUNLEN", "RUN-LENGTH", "runlen_ent", "runlen_asym",
                "ZCRPATH", "ZERO-CROSSING", "CUMULATIVE-RETURN", "SIGNCOH",
                "SIGN-SEQUENCE", "AUTOCORRELATION", "PEARSON",
                "SPECTRAL COHERENCE", "WELCH", "CROSS-SPECTRUM", "ACOVK",
                "AUTOCOVARIANCE", "SIGNCHOP", "TURNINGPT", "TURNING POINT",
                "KER", "EFFICIENCY RATIO", "PSLOPE", "TREND-SLOPE",
                "QREG", "QUANTILE-REGRESSION", "QUANTILE REGRESSION",
                "SCOH", "COH_MEAN", "COH_LOW"):
        assert bad not in mandate, f"mandate must not reference {bad} (prior campaign)"


def test_placebo_seed_is_20261289():
    assert R.PLACEBO_SEED == 20261289


def test_placebo_seed_unique_not_reserved():
    """Rewrite guard: C425 placebo seed must not collide with reserved seeds
    used by prior campaigns (20261224..20261288)."""
    assert not (20261224 <= R.PLACEBO_SEED <= 20261288), \
        "placebo seed must be outside 20261224-20261288"


# ---------------------------------------------------------------- real artifacts schema (if present)
def _find_latest(prefix: str):
    files = sorted((ROOT / "reports").glob(f"campaign425_{prefix}_*.json"))
    files = [f for f in files if ".full." not in f.name]
    return files[-1] if files else None


def test_artifacts_if_present_have_required_flags():
    p = _find_latest("verdict")
    if p is None:
        return
    v = json.loads(p.read_text())
    assert v["campaign"] == 425
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
    assert sw["config"]["rqa_params"]["window_W"] == 256


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
    test_rqa_matches_brute_force()
    test_rqa_matches_brute_force_10_assets()
    test_rqa_matches_brute_force_with_nan()
    test_rqa_defined_after_window_nan_before()
    test_rqa_non_finite_close_propagates()
    test_rqa_params()
    test_rqa_rr_range()
    test_rqa_det_range()
    test_rqa_lam_range()
    test_rqa_tt_range()
    test_reference_config_matches_pre_registered_spec()
    test_phase_randomized_surrogate_same_marginal_deterministic()
    test_build_underlying_shapes_and_keys()
    test_build_scores_signals_lookbacks_causal()
    test_rqa_kernel_not_degenerate()
    test_rqa_kernel_distinct_from_signchop()
    test_rqa_kernel_distinct_from_signrun()
    test_rqa_kernel_distinct_from_zcrpath()
    test_rqa_kernel_distinct_from_runlen()
    test_rqa_kernel_distinct_from_iesd()
    test_artifact_campaign_is_425()
    test_mandate_contains_rqa()
    test_placebo_seed_is_20261289()
    test_placebo_seed_unique_not_reserved()
    test_artifacts_if_present_have_required_flags()
    print("All C425 RQA runner tests passed")
