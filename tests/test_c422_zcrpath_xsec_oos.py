"""Tests for C422 runner (scripts/run_c422_zcrpath_xsec_oos.py): pure-function
tests on synthetic arrays (including a brute-force equality test for the
vectorized ZCRPATH zero-crossing-rate-of-cumulative-return-path kernel vs the
per-window explicit cumsum + crossing-count reference) plus schema/flag
validation of emitted real-data artifacts. No network, no fabricated market
data."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import run_c422_zcrpath_xsec_oos as R  # noqa: E402


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
    assert R.N_TRIALS == 1296
    assert len(R.SIGNALS) == 4
    assert len(R.LOOKBACKS) == 6
    assert len(R.REBALANCES) == 3
    assert len(R.FEES) == 3 and len(R.SLIPS) == 3 and len(R.COST_VARIANTS) == 2
    assert R.N_TRIALS == (len(R.SIGNALS) * len(R.LOOKBACKS) * len(R.REBALANCES)
                          * len(R.FEES) * len(R.SLIPS) * len(R.COST_VARIANTS))
    for pb in ("zcr_path_placebo", "zcr_asym_placebo"):
        assert pb in R.SIGNALS
    for real in ("zcr_path_dev", "zcr_asym_dev"):
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


# ---------------------------------------------------------------- ZCRPATH kernel (brute-force equality)
def test_zcrpath_matches_brute_force():
    """The vectorized ZCRPATH kernel MUST equal the brute-force reference
    (per-window loop with explicit cumsum + crossing count). Compared with
    maxdiff < 1e-9 and matching NaN patterns."""
    rng = np.random.default_rng(20261286)
    n_assets, n_bars = 5, 4000
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    fast = R.compute_zcrpath_metrics(log_return, W=R.ZCRPATH_W)
    brute = R._zcrpath_bruteforce(log_return, W=R.ZCRPATH_W)
    for key in ("zcr_path", "zcr_asym"):
        fv, fb = fast[key], brute[key]
        fin = np.isfinite(fv) & np.isfinite(fb)
        assert fin.sum() > 0, f"{key}: no finite overlapping points"
        assert np.array_equal(np.isnan(fv), np.isnan(fb)), f"{key}: NaN pattern mismatch"
        maxdiff = float(np.max(np.abs(fv[fin] - fb[fin]))) if fin.sum() else 0.0
        assert maxdiff < 1e-9, f"{key}: maxdiff={maxdiff} >= 1e-9"


def test_zcrpath_matches_brute_force_10_assets():
    """Brute-force equality with the full 10-asset panel (the real universe width)."""
    rng = np.random.default_rng(4222)
    n_assets, n_bars = 10, 1500
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    fast = R.compute_zcrpath_metrics(log_return, W=R.ZCRPATH_W)
    brute = R._zcrpath_bruteforce(log_return, W=R.ZCRPATH_W)
    for key in ("zcr_path", "zcr_asym"):
        fv, fb = fast[key], brute[key]
        fin = np.isfinite(fv) & np.isfinite(fb)
        assert fin.sum() > 0, key
        maxdiff = float(np.max(np.abs(fv[fin] - fb[fin])))
        assert maxdiff < 1e-9, f"zcrpath_{key}: maxdiff={maxdiff}"


def test_zcrpath_matches_brute_force_with_nan():
    """Brute-force equality when the panel contains NaNs (global across assets)."""
    rng = np.random.default_rng(99)
    n_assets, n_bars = 4, 1200
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    log_return[1, 400] = np.nan
    log_return[2, 401] = np.nan
    fast = R.compute_zcrpath_metrics(log_return, W=R.ZCRPATH_W)
    brute = R._zcrpath_bruteforce(log_return, W=R.ZCRPATH_W)
    for key in ("zcr_path", "zcr_asym"):
        fv, fb = fast[key], brute[key]
        fin = np.isfinite(fv) & np.isfinite(fb)
        assert np.array_equal(np.isnan(fv), np.isnan(fb)), f"{key}: NaN mismatch"
        maxdiff = float(np.max(np.abs(fv[fin] - fb[fin]))) if fin.sum() else 0.0
        assert maxdiff < 1e-9, f"{key}: maxdiff={maxdiff}"


def test_zcrpath_defined_after_window_nan_before():
    rng = np.random.default_rng(3)
    n_assets, n_bars = 3, 600
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.005
    W = R.ZCRPATH_W
    m = R.compute_zcrpath_metrics(log_return, W=W)
    for key in ("zcr_path", "zcr_asym"):
        assert np.isnan(m[key][:, :W]).all(), key
        assert np.isfinite(m[key][:, W:]).any(), key


def test_zcrpath_non_finite_return_propagates():
    """A non-finite return in any asset at a bar -> NaN for all ZCRPATH outputs
    in every window covering that bar (global-across-assets finiteness gate)."""
    rng = np.random.default_rng(9)
    n_assets, n_bars = 4, 600
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.005
    log_return[0, 300] = np.inf
    W = R.ZCRPATH_W
    m = R.compute_zcrpath_metrics(log_return, W=W)
    for t in range(300, min(300 + W, n_bars)):
        for key in ("zcr_path", "zcr_asym"):
            assert np.isnan(m[key][:, t]).all(), f"zcrpath_{key} t={t} should be NaN"
    for t in range(W, 300):
        for key in ("zcr_path", "zcr_asym"):
            assert np.isfinite(m[key][:, t]).any(), f"zcrpath_{key} t={t} should be finite"


def test_zcrpath_params():
    assert R.ZCRPATH_W == 256
    assert R.ZCRPATH_EPS == 1e-12


def test_zcrpath_bounds():
    """zcr_path in [0,1], zcr_asym in [-1,1] where defined."""
    rng = np.random.default_rng(2026)
    n_assets, n_bars = 2, 1000
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    W = R.ZCRPATH_W
    m = R.compute_zcrpath_metrics(log_return, W=W)
    for key in ("zcr_path",):
        fin = np.isfinite(m[key])
        assert (m[key][fin] >= 0.0 - 1e-12).all() and (m[key][fin] <= 1.0 + 1e-12).all()
    fina = np.isfinite(m["zcr_asym"])
    assert (m["zcr_asym"][fina] >= -1.0 - 1e-12).all() and (m["zcr_asym"][fina] <= 1.0 + 1e-12).all()


def test_reference_config_matches_pre_registered_spec():
    assert R.ATTR_REPRESENTATIVES == {
        "zcr_path_dev": "zcr_path_dev",
        "zcr_asym_dev": "zcr_asym_dev",
    }
    assert R.PLACEBO_SEED == 20261286
    assert R.STABILITY_MIN_SIGN_CONSISTENCY == 0.70
    assert R.STABILITY_MIN_SHARPE_CORR == 0.50
    assert R.DOMINANT_SHARE_MIN == 0.50
    assert R.TRAIN_M == 12 and R.TEST_M == 3 and R.ROLL_M == 3
    assert R.ZCRPATH_W == 256
    assert R.SIGNALS[0] == "zcr_path_dev"


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
    assert set(series.keys()) == {"zcr_path", "zcr_asym"}
    for k in ("zcr_path", "zcr_asym"):
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
def test_zcrpath_kernel_not_degenerate():
    """Rewrite guard: ZCRPATH metrics are not degenerate (not allclose to 0 where
    defined)."""
    rng = np.random.default_rng(55)
    n_assets, n_bars = 5, 1600
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    W = R.ZCRPATH_W
    mm = R.compute_zcrpath_metrics(log_return, W=W)
    for name in ("zcr_path", "zcr_asym"):
        arr = mm[name]
        fin = np.isfinite(arr)
        assert fin.sum() > 0, f"zcrpath_{name}: no finite values"
        assert not np.allclose(arr[fin], 0.0, atol=1e-12), f"zcrpath_{name} collapses to 0"


# ---- inline prior-family reference statistics (distinctness guards)
def _signchop_style_stat(log_return, W):
    """Inline C344-style statistic: sign-change / chop rate of the return sign
    sequence over the window — sign flips of Δprice, NOT zero-crossings of the
    cumulative-return path."""
    X = np.asarray(log_return, dtype=float)
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


def _turningpt_style_stat(log_return, W):
    """Inline C383 TURNINGPT-style statistic: second-difference turning-point rate
    — fraction of bars where sign(diff(r)) changes (local peaks/troughs in the
    price path), NOT zero-crossings of the cumulative-return path."""
    X = np.asarray(log_return, dtype=float)
    n_assets, n = X.shape
    out = np.full((n_assets, n), np.nan)
    for t in range(W, n):
        span = X[:, t - W + 1:t + 1]
        if not np.isfinite(span).all():
            continue
        for i in range(n_assets):
            d = np.diff(span[i])
            if len(d) < 2:
                continue
            s = np.sign(d)
            out[i, t] = float(np.mean(s[1:] != s[:-1])) if len(s) > 1 else np.nan
    return out


def _ker_style_stat(log_return, W):
    """Inline C365 KER-style statistic: Kaufman efficiency ratio — net
    displacement / gross path length over the window, |sum(X)| / sum(|X|),
    NOT zero-crossings of the cumulative path."""
    X = np.asarray(log_return, dtype=float)
    n_assets, n = X.shape
    out = np.full((n_assets, n), np.nan)
    for t in range(W, n):
        span = X[:, t - W + 1:t + 1]
        if not np.isfinite(span).all():
            continue
        for i in range(n_assets):
            x = span[i]
            net = abs(float(np.sum(x)))
            path = float(np.sum(np.abs(x)))
            out[i, t] = net / path if path > 0 else np.nan
    return out


def _pslope_style_stat(log_return, W):
    """Inline C377 PSLOPE-style statistic: OLS trend-slope t-stat of log-price
    (reconstructed via cumsum of log-returns) on bar index over the window,
    NOT zero-crossings of the cumulative-return path."""
    X = np.asarray(log_return, dtype=float)
    n_assets, n = X.shape
    out = np.full((n_assets, n), np.nan)
    idx = np.arange(W, dtype=float)
    idx_c = idx - idx.mean()
    denom = float(np.sum(idx_c * idx_c))
    for t in range(W, n):
        span = X[:, t - W + 1:t + 1]
        if not np.isfinite(span).all():
            continue
        for i in range(n_assets):
            p = np.cumsum(span[i])  # log-price levels over window
            y_c = p - p.mean()
            if denom <= 0:
                continue
            slope = float(np.sum(idx_c * y_c) / denom)
            resid = y_c - slope * idx_c
            s2 = float(np.sum(resid * resid) / (W - 2)) if W > 2 else np.nan
            if not np.isfinite(s2) or s2 <= 0:
                continue
            se = float(np.sqrt(s2 / denom))
            out[i, t] = slope / se if se > 0 else np.nan
    return out


def _acovk_style_stat(log_return, W):
    """Inline C375 ACOVK-style statistic: sum of raw-return autocovariances
    gamma_k = mean(x[:-k]*x[k:]) over lags {1,2,4,8} — autocovariance of the RAW
    return series, NOT zero-crossings of the cumulative-return path."""
    X = np.asarray(log_return, dtype=float)
    n_assets, n = X.shape
    out = np.full((n_assets, n), np.nan)
    for t in range(W, n):
        span = X[:, t - W + 1:t + 1]
        if not np.isfinite(span).all():
            continue
        for i in range(n_assets):
            x = span[i]
            vals = []
            for k in (1, 2, 4, 8):
                vals.append(float(np.mean(x[:-k] * x[k:])))
            out[i, t] = float(np.sum(vals))
    return out


def _assert_distinct(sa, ref, name):
    fin = np.isfinite(sa) & np.isfinite(ref)
    assert fin.sum() > 0, name
    assert not np.allclose(sa[fin], ref[fin], atol=1e-6), f"ZCRPATH degenerates to {name}"


def test_zcrpath_kernel_distinct_from_signchop():
    """C344 sign-change/chop rate: legitimate distinctness-guard ref
    (sign flips of Δprice vs zero-crossings of cumulative-return path)."""
    rng = np.random.default_rng(214)
    n_assets, n_bars = 5, 1200
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    W = R.ZCRPATH_W
    mm = R.compute_zcrpath_metrics(log_return, W=W)
    sa = mm["zcr_path"][0, W:]
    ref = _signchop_style_stat(log_return, W)[0, W:]
    _assert_distinct(sa, ref, "SIGNCHOP")


def test_zcrpath_kernel_distinct_from_turningpt():
    """C383 TURNINGPT (second-difference turning points): legitimate
    distinctness-guard ref (turning-point rate vs cumulative-path zero-crossings)."""
    rng = np.random.default_rng(217)
    n_assets, n_bars = 5, 1200
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    W = R.ZCRPATH_W
    mm = R.compute_zcrpath_metrics(log_return, W=W)
    sa = mm["zcr_path"][0, W:]
    ref = _turningpt_style_stat(log_return, W)[0, W:]
    _assert_distinct(sa, ref, "TURNINGPT")


def test_zcrpath_kernel_distinct_from_ker():
    """C365 KER (net displacement / gross path length): legitimate
    distinctness-guard ref (path-straightness vs cumulative-path zero-crossings)."""
    rng = np.random.default_rng(218)
    n_assets, n_bars = 5, 1200
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    W = R.ZCRPATH_W
    mm = R.compute_zcrpath_metrics(log_return, W=W)
    sa = mm["zcr_path"][0, W:]
    ref = _ker_style_stat(log_return, W)[0, W:]
    _assert_distinct(sa, ref, "KER")


def test_zcrpath_kernel_distinct_from_pslope():
    """C377 PSLOPE (OLS trend-slope t-stat): legitimate distinctness-guard ref
    (fitted-trend significance vs cumulative-path zero-crossings)."""
    rng = np.random.default_rng(219)
    n_assets, n_bars = 5, 1200
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    W = R.ZCRPATH_W
    mm = R.compute_zcrpath_metrics(log_return, W=W)
    sa = mm["zcr_path"][0, W:]
    ref = _pslope_style_stat(log_return, W)[0, W:]
    _assert_distinct(sa, ref, "PSLOPE")


def test_zcrpath_kernel_distinct_from_acovk():
    """C375 ACOVK (raw-return autocovariance profile): legitimate distinctness-guard ref
    (raw-return autocovariance vs cumulative-path zero-crossings)."""
    rng = np.random.default_rng(220)
    n_assets, n_bars = 5, 1200
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    W = R.ZCRPATH_W
    mm = R.compute_zcrpath_metrics(log_return, W=W)
    sa = mm["zcr_path"][0, W:]
    ref = _acovk_style_stat(log_return, W)[0, W:]
    _assert_distinct(sa, ref, "ACOVK")


# ---------------------------------------------------------------- guard tests (rewrite guards)
def test_artifact_campaign_is_422():
    """Rewrite guard: every emitted artifact self-identifies campaign 422."""
    for part in ("verdict", "summary", "registry", "oos_sweep"):
        files = sorted((ROOT / "reports").glob(f"campaign422_{part}_*.json"))
        files = [f for f in files if ".full." not in f.name]
        if not files:
            continue
        obj = json.loads(files[-1].read_text())
        assert obj["campaign"] == 422, f"{part} artifact campaign != 422: {obj.get('campaign')}"


def test_mandate_contains_zcrpath():
    """Rewrite guard: the C422 mandate names the ZCRPATH zero-crossing-rate
    family (never prior families)."""
    p = sorted((ROOT / "reports").glob("campaign422_oos_sweep_*.json"))
    p = [f for f in p if ".full." not in f.name]
    if not p:
        return
    mandate = json.loads(p[-1].read_text())["mandate"]
    assert "ZCRPATH" in mandate, "mandate missing ZCRPATH"
    assert "ZERO-CROSSING" in mandate.upper(), "mandate missing ZERO-CROSSING"
    assert "CUMULATIVE-RETURN" in mandate.upper(), "mandate missing CUMULATIVE-RETURN"
    assert "zcr_path" in mandate, "mandate missing zcr_path"
    assert "zcr_asym" in mandate, "mandate missing zcr_asym"
    for bad in ("SIGNCOH", "SIGN-SEQUENCE", "AUTOCORRELATION", "PEARSON",
                "SPECTRAL COHERENCE", "WELCH", "CROSS-SPECTRUM", "ACOVK",
                "AUTOCOVARIANCE", "SIGNCHOP", "TURNINGPT", "TURNING POINT",
                "KER", "EFFICIENCY RATIO", "PSLOPE", "TREND-SLOPE",
                "QREG", "QUANTILE-REGRESSION", "QUANTILE REGRESSION",
                "SCOH", "COH_MEAN", "COH_LOW"):
        assert bad not in mandate, f"mandate must not reference {bad} (prior campaign)"


def test_placebo_seed_is_20261286():
    assert R.PLACEBO_SEED == 20261286


def test_placebo_seed_unique_not_reserved():
    """Rewrite guard: C422 placebo seed must not collide with reserved seeds
    used by prior campaigns (C360..C421 used 20261224..20261285)."""
    assert not (20261224 <= R.PLACEBO_SEED <= 20261285), \
        "placebo seed must be outside 20261224-20261285"


# ---------------------------------------------------------------- real artifacts schema (if present)
def _find_latest(prefix: str):
    files = sorted((ROOT / "reports").glob(f"campaign422_{prefix}_*.json"))
    files = [f for f in files if ".full." not in f.name]
    return files[-1] if files else None


def test_artifacts_if_present_have_required_flags():
    p = _find_latest("verdict")
    if p is None:
        return
    v = json.loads(p.read_text())
    assert v["campaign"] == 422
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
    assert sw["config"]["zcrpath_params"]["window_W"] == 256


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
    test_zcrpath_matches_brute_force()
    test_zcrpath_matches_brute_force_10_assets()
    test_zcrpath_matches_brute_force_with_nan()
    test_zcrpath_defined_after_window_nan_before()
    test_zcrpath_non_finite_return_propagates()
    test_zcrpath_params()
    test_zcrpath_bounds()
    test_reference_config_matches_pre_registered_spec()
    test_phase_randomized_surrogate_same_marginal_deterministic()
    test_build_underlying_shapes_and_keys()
    test_build_scores_signals_lookbacks_causal()
    test_zcrpath_kernel_not_degenerate()
    test_zcrpath_kernel_distinct_from_signchop()
    test_zcrpath_kernel_distinct_from_turningpt()
    test_zcrpath_kernel_distinct_from_ker()
    test_zcrpath_kernel_distinct_from_pslope()
    test_zcrpath_kernel_distinct_from_acovk()
    test_artifact_campaign_is_422()
    test_mandate_contains_zcrpath()
    test_placebo_seed_is_20261286()
    test_placebo_seed_unique_not_reserved()
    test_artifacts_if_present_have_required_flags()
    print("All C422 ZCRPATH runner tests passed")
