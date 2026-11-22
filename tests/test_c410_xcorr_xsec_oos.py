"""Tests for C409 runner (scripts/run_c409_residvol_xsec_oos.py): pure-function tests
on synthetic arrays (including a brute-force equality test for the vectorized
RESIDVOL idiosyncratic/residual volatility kernel vs the per-window reference)
plus schema/flag validation of emitted real-data artifacts. No network, no
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

import run_c409_residvol_xsec_oos as R  # noqa: E402


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
    for pb in ("residvol_placebo", "idioskew_placebo"):
        assert pb in R.SIGNALS
    for real in ("residvol_dev", "idioskew_dev"):
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


# ---------------------------------------------------------------- RESIDVOL metric (brute-force equality)
def test_residvol_matches_brute_force():
    """The vectorized RESIDVOL kernel MUST equal the brute-force reference
    (per-window loop with explicit market series and centered OLS residual).
    Compared with maxdiff < 1e-12 with matching NaN patterns."""
    rng = np.random.default_rng(20261273)
    n_assets, n_bars = 5, 4000
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    market_return = log_return.mean(axis=0)
    fast = R.compute_residvol_metrics(log_return, market_return, R.RESIDVOL_W)
    brute = R._residvol_bruteforce(log_return, market_return, R.RESIDVOL_W)
    for key in ("residvol", "idioskew"):
        fv, fb = fast[key], brute[key]
        fin = np.isfinite(fv) & np.isfinite(fb)
        assert fin.sum() > 0, f"{key}: no finite overlapping points"
        assert np.array_equal(np.isnan(fv), np.isnan(fb)), f"{key}: NaN pattern mismatch"
        maxdiff = float(np.max(np.abs(fv[fin] - fb[fin]))) if fin.sum() else 0.0
        assert maxdiff < 1e-12, f"{key}: maxdiff={maxdiff} >= 1e-12"


def test_residvol_defined_after_window_nan_before():
    rng = np.random.default_rng(3)
    n_assets, n_bars = 3, 600
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    market_return = log_return.mean(axis=0)
    W = R.RESIDVOL_W
    m = R.compute_residvol_metrics(log_return, market_return, W)
    for key in ("residvol", "idioskew"):
        assert np.isnan(m[key][:, :W]).all(), key
        assert np.isfinite(m[key][:, W:]).any(), key


def test_residvol_non_finite_return_propagates():
    """A non-finite return in any asset's window -> NaN for all RESIDVOL outputs
    in affected bars (because the market return m[s] also becomes non-finite)."""
    rng = np.random.default_rng(9)
    n_assets, n_bars = 4, 600
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    market_return = log_return.mean(axis=0)
    log_return[0, 300] = np.inf
    market_return = log_return.mean(axis=0)  # rebuild so m[300] is inf
    W = R.RESIDVOL_W
    m = R.compute_residvol_metrics(log_return, market_return, W)
    for t in range(300, min(300 + W, n_bars)):
        assert np.isnan(m["residvol"][:, t]).all(), f"residvol t={t} should be NaN"
        assert np.isnan(m["idioskew"][:, t]).all(), f"idioskew t={t} should be NaN"
    for t in range(W, 300):
        assert np.isfinite(m["residvol"][:, t]).any(), f"residvol t={t} should be finite"


def test_residvol_params():
    assert R.RESIDVOL_W == 256


def test_reference_config_matches_pre_registered_spec():
    assert R.ATTR_REPRESENTATIVES == {
        "residvol_dev": "residvol_dev",
        "idioskew_dev": "idioskew_dev",
    }
    assert R.PLACEBO_SEED == 20261273
    assert R.STABILITY_MIN_SIGN_CONSISTENCY == 0.70
    assert R.STABILITY_MIN_SHARPE_CORR == 0.50
    assert R.DOMINANT_SHARE_MIN == 0.50
    assert R.TRAIN_M == 12 and R.TEST_M == 3 and R.ROLL_M == 3
    assert R.RESIDVOL_W == 256
    assert R.SIGNALS[0] == "residvol_dev"


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
    assert set(series.keys()) == {"residvol", "idioskew"}
    for k in ("residvol", "idioskew"):
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
def test_residvol_kernel_not_degenerate():
    """Rewrite guard: RESIDVOL metrics are not degenerate (not allclose to 0 where defined)."""
    rng = np.random.default_rng(55)
    n_assets, n_bars = 4, 1600
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    market_return = log_return.mean(axis=0)
    W = R.RESIDVOL_W
    mm = R.compute_residvol_metrics(log_return, market_return, W)
    for name in ("residvol", "idioskew"):
        arr = mm[name]
        fin = np.isfinite(arr)
        assert fin.sum() > 0, f"{name}: no finite values"
        assert not np.allclose(arr[fin], 0.0, atol=1e-12), f"{name} collapses to 0"


def _rv_style_stat(X, W):
    """Inline C317 RV total realized volatility: sqrt(sum(x^2)) over window."""
    n = len(X)
    out = np.full(n, np.nan)
    for t in range(W, n):
        Xw = X[t - W + 1:t + 1]
        if not np.isfinite(Xw).all():
            continue
        out[t] = float(np.sqrt(np.sum(Xw ** 2)))
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


def _dsrv_style_stat(X, W):
    """Inline C364 DSRV log-ratio of downside vs upside semivariance."""
    n = len(X)
    out = np.full(n, np.nan)
    for t in range(W, n):
        Xw = X[t - W + 1:t + 1]
        if not np.isfinite(Xw).all():
            continue
        rv_down = float(np.sum(Xw[Xw < 0] ** 2))
        rv_up = float(np.sum(Xw[Xw > 0] ** 2))
        if rv_down <= 0 or rv_up <= 0:
            continue
        out[t] = float(np.log(rv_down / rv_up))
    return out


def _rqv_style_stat(X, W):
    """Inline C366 RQV realized quarticity: mean(x^4) over window."""
    n = len(X)
    out = np.full(n, np.nan)
    for t in range(W, n):
        Xw = X[t - W + 1:t + 1]
        if not np.isfinite(Xw).all():
            continue
        out[t] = float(np.mean(Xw ** 4))
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


def test_residvol_kernel_distinct_from_rv():
    """Rewrite guard: RESIDVOL residvol is residual dispersion, a different object
    from C317 RV total realized volatility."""
    rng = np.random.default_rng(128)
    n_assets, n_bars = 4, 1200
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    market_return = log_return.mean(axis=0)
    W = R.RESIDVOL_W
    mm = R.compute_residvol_metrics(log_return, market_return, W)
    rv = mm["residvol"][0, W:]
    rv_ref = _rv_style_stat(log_return[0], W)[W:]
    fin = np.isfinite(rv) & np.isfinite(rv_ref)
    assert fin.sum() > 0
    assert not np.allclose(rv[fin], rv_ref[fin], atol=1e-6), "RESIDVOL degenerates to RV"


def test_residvol_kernel_distinct_from_betaasym():
    """Rewrite guard: RESIDVOL residvol (residual dispersion) is a different object
    from C406 BETAASYM market-beta coefficient."""
    rng = np.random.default_rng(129)
    n_assets, n_bars = 4, 1200
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    market_return = log_return.mean(axis=0)
    W = R.RESIDVOL_W
    mm = R.compute_residvol_metrics(log_return, market_return, W)
    rv = mm["residvol"][0, W:]
    ba = _betaasym_style_stat(log_return[0], market_return, W)[W:]
    fin = np.isfinite(rv) & np.isfinite(ba)
    assert fin.sum() > 0
    assert not np.allclose(rv[fin], ba[fin], atol=1e-6), "RESIDVOL degenerates to BETAASYM"


def test_residvol_kernel_distinct_from_dsrv():
    """Rewrite guard: RESIDVOL residvol is a different object from C364 DSRV
    downside/upside semivariance log-ratio."""
    rng = np.random.default_rng(130)
    n_assets, n_bars = 4, 1200
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    market_return = log_return.mean(axis=0)
    W = R.RESIDVOL_W
    mm = R.compute_residvol_metrics(log_return, market_return, W)
    rv = mm["residvol"][0, W:]
    ds = _dsrv_style_stat(log_return[0], W)[W:]
    fin = np.isfinite(rv) & np.isfinite(ds)
    assert fin.sum() > 0
    assert not np.allclose(rv[fin], ds[fin], atol=1e-6), "RESIDVOL degenerates to DSRV"


def test_residvol_kernel_distinct_from_rqv():
    """Rewrite guard: RESIDVOL residvol is a different object from C366 RQV
    realized quarticity (4th moment)."""
    rng = np.random.default_rng(131)
    n_assets, n_bars = 4, 1200
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    market_return = log_return.mean(axis=0)
    W = R.RESIDVOL_W
    mm = R.compute_residvol_metrics(log_return, market_return, W)
    rv = mm["residvol"][0, W:]
    rq = _rqv_style_stat(log_return[0], W)[W:]
    fin = np.isfinite(rv) & np.isfinite(rq)
    assert fin.sum() > 0
    assert not np.allclose(rv[fin], rq[fin], atol=1e-6), "RESIDVOL degenerates to RQV"


def test_residvol_kernel_distinct_from_coskew():
    """Rewrite guard: RESIDVOL idioskew (residual skewness) is a different object
    from C405 COSKEW co-skewness vs market."""
    rng = np.random.default_rng(132)
    n_assets, n_bars = 4, 1200
    log_return = rng.standard_normal((n_assets, n_bars)) * 0.001
    market_return = log_return.mean(axis=0)
    W = R.RESIDVOL_W
    mm = R.compute_residvol_metrics(log_return, market_return, W)
    sk = mm["idioskew"][0, W:]
    ck = _coskew_style_stat(log_return[0], market_return, W)[W:]
    fin = np.isfinite(sk) & np.isfinite(ck)
    assert fin.sum() > 0
    assert not np.allclose(sk[fin], ck[fin], atol=1e-6), "RESIDVOL degenerates to COSKEW"


# ---------------------------------------------------------------- guard tests (rewrite guards)
def test_artifact_campaign_is_409():
    """Rewrite guard: every emitted artifact self-identifies campaign 409."""
    for part in ("verdict", "summary", "registry", "oos_sweep"):
        files = sorted((ROOT / "reports").glob(f"campaign409_{part}_*.json"))
        files = [f for f in files if ".full." not in f.name]
        if not files:
            continue
        obj = json.loads(files[-1].read_text())
        assert obj["campaign"] == 409, f"{part} artifact campaign != 409: {obj.get('campaign')}"


def test_mandate_contains_residvol():
    """Rewrite guard: the C409 mandate names RESIDVOL idiosyncratic/residual
    volatility (never prior families)."""
    p = sorted((ROOT / "reports").glob("campaign409_oos_sweep_*.json"))
    p = [f for f in p if ".full." not in f.name]
    if not p:
        return
    mandate = json.loads(p[-1].read_text())["mandate"]
    assert "RESIDVOL" in mandate, "mandate missing RESIDVOL"
    assert "IDIOSYNCRATIC" in mandate, "mandate missing IDIOSYNCRATIC"
    assert "RESIDUAL" in mandate, "mandate missing RESIDUAL"
    for bad in ("LEADLAG", "LEADER-FOLLOWER", "BETA", "BETAASYM", "COSKEW", "COKURT",
                "ASYMCURV", "TSCALE", "HILL",
                "RVQUART", "QUARTICITY", "KTREND", "CBREAK", "SPECFM", "MAGNET",
                "OUHALFLIFE", "CTES", "VTERM", "DDRUN", "XSKEW3", "XCOEX", "MINRV",
                "MADR", "BANDX", "PRROUGH", "HALFRANGE", "LMOM", "SEMICOV", "LVAC", "DSRV",
                "RSKEK", "DOMINANT", "SPECTRAL", "CENTROID", "ACOVK", "TIRV", "XSRANK",
                "RANK-PERSISTENCE"):
        assert bad not in mandate, f"mandate must not reference {bad} (prior campaign)"


def test_placebo_seed_is_20261273():
    assert R.PLACEBO_SEED == 20261273


def test_placebo_seed_unique_not_reserved():
    """Rewrite guard: C409 placebo seed 20261273 must not collide with reserved
    seeds 20261224–20261272 used by prior campaigns."""
    assert not (20261224 <= R.PLACEBO_SEED <= 20261272), "placebo seed must be outside 20261224-20261272"


# ---------------------------------------------------------------- real artifacts schema (if present)
def _find_latest(prefix: str):
    files = sorted((ROOT / "reports").glob(f"campaign409_{prefix}_*.json"))
    files = [f for f in files if ".full." not in f.name]
    return files[-1] if files else None


def test_artifacts_if_present_have_required_flags():
    p = _find_latest("verdict")
    if p is None:
        return
    v = json.loads(p.read_text())
    assert v["campaign"] == 409
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
    assert sw["config"]["residvol_params"]["window_W"] == 256


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
    test_residvol_matches_brute_force()
    test_residvol_defined_after_window_nan_before()
    test_residvol_non_finite_return_propagates()
    test_residvol_params()
    test_reference_config_matches_pre_registered_spec()
    test_phase_randomized_surrogate_same_marginal_deterministic()
    test_build_underlying_shapes_and_keys()
    test_build_scores_signals_lookbacks_causal()
    test_residvol_kernel_not_degenerate()
    test_residvol_kernel_distinct_from_rv()
    test_residvol_kernel_distinct_from_betaasym()
    test_residvol_kernel_distinct_from_dsrv()
    test_residvol_kernel_distinct_from_rqv()
    test_residvol_kernel_distinct_from_coskew()
    test_artifact_campaign_is_409()
    test_mandate_contains_residvol()
    test_placebo_seed_is_20261273()
    test_placebo_seed_unique_not_reserved()
    test_artifacts_if_present_have_required_flags()
    print("All C409 RESIDVOL runner tests passed")