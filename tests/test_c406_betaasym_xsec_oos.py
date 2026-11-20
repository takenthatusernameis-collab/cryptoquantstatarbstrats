"""Tests for C406 runner (scripts/run_c406_betaasym_xsec_oos.py): pure-function tests
on synthetic arrays (including a brute-force equality test for the vectorized
BETAASYM market-beta level & upside/downside beta asymmetry kernel vs the
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

import run_c406_betaasym_xsec_oos as R  # noqa: E402


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
    for pb in ("beta_asym_placebo", "beta_level_placebo"):
        assert pb in R.SIGNALS
    for real in ("beta_asym_dev", "beta_level_dev"):
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


# ---------------------------------------------------------------- BETAASYM metric (brute-force equality)
def test_betaasym_matches_brute_force():
    """The vectorized BETAASYM kernel MUST equal the brute-force reference
    (per-window loop with explicit market series and conditional masks). Compared
    with maxdiff < 1e-12 with matching NaN patterns."""
    rng = np.random.default_rng(20261270)
    log_return = rng.standard_normal(4000) * 0.001
    market = rng.standard_normal(4000) * 0.001
    fast = R.compute_betaasym_metrics(log_return, market, R.BETAASYM_W)
    brute = R._betaasym_bruteforce(log_return, market, R.BETAASYM_W)
    for key in ("beta_level", "beta_up", "beta_down", "beta_asym"):
        fv, fb = fast[key], brute[key]
        fin = np.isfinite(fv) & np.isfinite(fb)
        assert fin.sum() > 0, f"{key}: no finite overlapping points"
        assert np.array_equal(np.isnan(fv), np.isnan(fb)), f"{key}: NaN pattern mismatch"
        maxdiff = float(np.max(np.abs(fv[fin] - fb[fin]))) if fin.sum() else 0.0
        assert maxdiff < 1e-12, f"{key}: maxdiff={maxdiff} >= 1e-12"


def test_betaasym_defined_after_window_nan_before():
    rng = np.random.default_rng(3)
    log_return = rng.standard_normal(4000) * 0.001
    market = rng.standard_normal(4000) * 0.001
    m = R.compute_betaasym_metrics(log_return, market, R.BETAASYM_W)
    W = R.BETAASYM_W
    for key in ("beta_level", "beta_up", "beta_down", "beta_asym"):
        assert np.isnan(m[key][:W]).all(), key
        assert np.isfinite(m[key][W:]).any(), key


def test_betaasym_non_finite_return_propagates():
    """A non-finite return in the asset window -> NaN for all BETAASYM outputs
    in affected bars (market stays finite)."""
    rng = np.random.default_rng(9)
    log_return = rng.standard_normal(600) * 0.001
    market = rng.standard_normal(600) * 0.001
    log_return[300] = np.inf
    W = R.BETAASYM_W
    m = R.compute_betaasym_metrics(log_return, market, W)
    for t in range(300, min(300 + W, 600)):
        assert np.isnan(m["beta_level"][t]), f"beta_level t={t} should be NaN"
        assert np.isnan(m["beta_asym"][t]), f"beta_asym t={t} should be NaN"
    for t in range(W, 300):
        assert np.isfinite(m["beta_level"][t]), f"beta_level t={t} should be finite"


def test_betaasym_params():
    assert R.BETAASYM_W == 256


def test_reference_config_matches_pre_registered_spec():
    assert R.ATTR_REPRESENTATIVES == {
        "beta_asym_dev": "beta_asym_dev",
        "beta_level_dev": "beta_level_dev",
    }
    assert R.PLACEBO_SEED == 20261270
    assert R.STABILITY_MIN_SIGN_CONSISTENCY == 0.70
    assert R.STABILITY_MIN_SHARPE_CORR == 0.50
    assert R.DOMINANT_SHARE_MIN == 0.50
    assert R.TRAIN_M == 12 and R.TEST_M == 3 and R.ROLL_M == 3
    assert R.BETAASYM_W == 256
    assert R.SIGNALS[0] == "beta_asym_dev"


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
    assert set(series.keys()) == {"beta_level", "beta_up", "beta_down", "beta_asym"}
    for k in ("beta_level", "beta_up", "beta_down", "beta_asym"):
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
def test_betaasym_kernel_not_degenerate():
    """Rewrite guard: BETAASYM metrics are not degenerate (not allclose to 0 where defined)."""
    rng = np.random.default_rng(55)
    log_return = rng.standard_normal(1600) * 0.001
    market = rng.standard_normal(1600) * 0.001
    W = R.BETAASYM_W
    mm = R.compute_betaasym_metrics(log_return, market, W)
    dp = mm["beta_asym"]
    bl = mm["beta_level"]
    fin = np.isfinite(dp) & np.isfinite(bl)
    assert fin.sum() > 0
    for name, arr in (("beta_asym", dp), ("beta_level", bl)):
        valid = arr[fin]
        assert not np.allclose(valid, 0.0, atol=1e-12), f"{name} collapses to 0"


def _third_moment_style_stat(log_return, market, W):
    """Inline third/fourth co-moment style co-skewness = mean((X-mu_X)(M-mu_M)^2)/(sig_X*sig_M^2)."""
    n = len(log_return)
    out = np.full(n, np.nan)
    for t in range(W, n):
        Xw = log_return[t - W + 1:t + 1]
        Mw = market[t - W + 1:t + 1]
        if not (np.isfinite(Xw).all() and np.isfinite(Mw).all()):
            continue
        mu_X = Xw.mean(); mu_M = Mw.mean()
        sig_X = Xw.std(); sig_M = Mw.std()
        if not (sig_X > 0 and sig_M > 0):
            continue
        dX = Xw - mu_X; dM = Mw - mu_M
        out[t] = (dX * dM * dM).mean() / (sig_X * sig_M * sig_M)
    return out


def _semicov_style_stat(X, W):
    """Inline C380 SEMICOV signed-conditional lag covariance for k in {1,2,4}:
    mean over k of [cov(r_t, r_{t-k}|r_{t-k}<0) - cov(r_t, r_{t-k}|r_{t-k}>0)]."""
    n = len(X)
    out = np.full(n, np.nan)
    for t in range(W, n):
        Xw = X[t - W + 1:t + 1]
        if not np.isfinite(Xw).all():
            continue
        vals = []
        for k in (1, 2, 4):
            a = Xw[k:]
            b = Xw[:-k]
            mask_pos = b > 0
            mask_neg = b < 0
            if int(mask_pos.sum()) < 3 or int(mask_neg.sum()) < 3:
                vals.append(np.nan); continue
            ap, bp = a[mask_pos], b[mask_pos]
            cov_pos = ((ap - ap.mean()) * (bp - bp.mean())).mean()
            an, bn = a[mask_neg], b[mask_neg]
            cov_neg = ((an - an.mean()) * (bn - bn.mean())).mean()
            vals.append(cov_neg - cov_pos)
        if all(np.isfinite(v) for v in vals):
            out[t] = float(np.mean(vals))
    return out


def _lvac_style_stat(X, W):
    """Inline C360 LVAC mean of corr(r, |r|_k) over k in {1..5}."""
    n = len(X)
    out = np.full(n, np.nan)
    for t in range(W, n):
        Xw = X[t - W + 1:t + 1]
        if not np.isfinite(Xw).all():
            continue
        absX = np.abs(Xw)
        vals = []
        for k in (1, 2, 3, 4, 5):
            a = Xw[k:]; b = absX[:-k]
            if a.std() <= 0 or b.std() <= 0:
                vals.append(np.nan); continue
            vals.append(np.corrcoef(a, b)[0, 1])
        if all(np.isfinite(v) for v in vals):
            out[t] = float(np.mean(vals))
    return out


def _dsrv_style_stat(X, W):
    """Inline C364 DSRV asymmetry log(rv_down/rv_up)."""
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


def _acovk_style_stat(X, W):
    """Inline C375 ACOVK sum of autocovariances gamma_k for k in {1,2,4,8}."""
    n = len(X)
    out = np.full(n, np.nan)
    for t in range(W, n):
        Xw = X[t - W + 1:t + 1]
        if not np.isfinite(Xw).all():
            continue
        total = 0.0
        ok = True
        for k in (1, 2, 4, 8):
            a = Xw[k:]; b = Xw[:-k]
            if len(a) < 3 or a.std() <= 0 or b.std() <= 0:
                ok = False; break
            total += float(((a - a.mean()) * (b - b.mean())).mean())
        if ok:
            out[t] = total
    return out


def test_betaasym_kernel_distinct_from_third_moment():
    """Rewrite guard: BETAASYM beta_asym is a different object from the
    third/fourth co-moment family (third co-moment, not second-moment beta)."""
    rng = np.random.default_rng(123)
    log_return = rng.standard_normal(1200) * 0.001
    market = rng.standard_normal(1200) * 0.001
    W = R.BETAASYM_W
    mm = R.compute_betaasym_metrics(log_return, market, W)
    dp = mm["beta_asym"][W:]
    third_moment = _third_moment_style_stat(log_return, market, W)[W:]
    fin = np.isfinite(dp) & np.isfinite(third_moment)
    assert fin.sum() > 0
    assert not np.allclose(dp[fin], third_moment[fin], atol=1e-6), "BETAASYM degenerates to third-moment co-moment"


def test_betaasym_kernel_distinct_from_semicov():
    """Rewrite guard: BETAASYM beta_asym is a different object from C380 SEMICOV
    signed-conditional lag covariance."""
    rng = np.random.default_rng(124)
    log_return = rng.standard_normal(1200) * 0.001
    market = rng.standard_normal(1200) * 0.001
    W = R.BETAASYM_W
    mm = R.compute_betaasym_metrics(log_return, market, W)
    dp = mm["beta_asym"][W:]
    semicov = _semicov_style_stat(log_return, W)[W:]
    fin = np.isfinite(dp) & np.isfinite(semicov)
    assert fin.sum() > 0
    assert not np.allclose(dp[fin], semicov[fin], atol=1e-6), "BETAASYM degenerates to SEMICOV"


def test_betaasym_kernel_distinct_from_lvac():
    """Rewrite guard: BETAASYM beta_asym is a different object from C360 LVAC
    leverage corr(r, |r|_k)."""
    rng = np.random.default_rng(125)
    log_return = rng.standard_normal(1200) * 0.001
    market = rng.standard_normal(1200) * 0.001
    W = R.BETAASYM_W
    mm = R.compute_betaasym_metrics(log_return, market, W)
    dp = mm["beta_asym"][W:]
    lvac = _lvac_style_stat(log_return, W)[W:]
    fin = np.isfinite(dp) & np.isfinite(lvac)
    assert fin.sum() > 0
    assert not np.allclose(dp[fin], lvac[fin], atol=1e-6), "BETAASYM degenerates to LVAC"


def test_betaasym_kernel_distinct_from_dsrv():
    """Rewrite guard: BETAASYM beta_asym is a different object from C364 DSRV
    downside/upside semivariance log-ratio."""
    rng = np.random.default_rng(126)
    log_return = rng.standard_normal(1200) * 0.001
    market = rng.standard_normal(1200) * 0.001
    W = R.BETAASYM_W
    mm = R.compute_betaasym_metrics(log_return, market, W)
    dp = mm["beta_asym"][W:]
    dsrv = _dsrv_style_stat(log_return, W)[W:]
    fin = np.isfinite(dp) & np.isfinite(dsrv)
    assert fin.sum() > 0
    assert not np.allclose(dp[fin], dsrv[fin], atol=1e-6), "BETAASYM degenerates to DSRV"


def test_betaasym_kernel_distinct_from_acovk():
    """Rewrite guard: BETAASYM beta_asym is a different object from C375 ACOVK
    unconditional autocovariance profile."""
    rng = np.random.default_rng(127)
    log_return = rng.standard_normal(1200) * 0.001
    market = rng.standard_normal(1200) * 0.001
    W = R.BETAASYM_W
    mm = R.compute_betaasym_metrics(log_return, market, W)
    dp = mm["beta_asym"][W:]
    acovk = _acovk_style_stat(log_return, W)[W:]
    fin = np.isfinite(dp) & np.isfinite(acovk)
    assert fin.sum() > 0
    assert not np.allclose(dp[fin], acovk[fin], atol=1e-6), "BETAASYM degenerates to ACOVK"


# ---------------------------------------------------------------- guard tests (rewrite guards)
def test_artifact_campaign_is_406():
    """Rewrite guard: every emitted artifact self-identifies campaign 406."""
    for part in ("verdict", "summary", "registry", "oos_sweep"):
        files = sorted((ROOT / "reports").glob(f"campaign406_{part}_*.json"))
        files = [f for f in files if ".full." not in f.name]
        if not files:
            continue
        obj = json.loads(files[-1].read_text())
        assert obj["campaign"] == 406, f"{part} artifact campaign != 406: {obj.get('campaign')}"


def test_mandate_contains_betaasym():
    """Rewrite guard: the C406 mandate names BETAASYM market-beta level &
    upside/downside beta asymmetry vs equal-weight market (never prior
    higher-co-moment or tail families)."""
    p = sorted((ROOT / "reports").glob("campaign406_oos_sweep_*.json"))
    p = [f for f in p if ".full." not in f.name]
    if not p:
        return
    mandate = json.loads(p[-1].read_text())["mandate"]
    assert "BETAASYM" in mandate, "mandate missing BETAASYM"
    assert "EQUAL-WEIGHT MARKET" in mandate, "mandate missing EQUAL-WEIGHT MARKET"
    assert "BETA" in mandate, "mandate missing BETA"
    for bad in ("ASYMCURV", "TSCALE", "HILL",
                "RVQUART", "QUARTICITY", "KTREND", "CBREAK", "SPECFM", "MAGNET",
                "OUHALFLIFE", "CTES", "VTERM", "DDRUN", "XSKEW3", "XCOEX", "MINRV",
                "MADR", "BANDX", "PRROUGH", "HALFRANGE", "LMOM", "KENDALL", "SPEARMAN",
                "SEMICOV", "LVAC", "DSRV", "RSKEK", "DOMINANT", "SPECTRAL", "CENTROID"):
        assert bad not in mandate, f"mandate must not reference {bad} (prior campaign)"


def test_placebo_seed_is_20261270():
    assert R.PLACEBO_SEED == 20261270


def test_placebo_seed_unique_not_reserved():
    """Rewrite guard: C406 placebo seed 20261270 must not collide with reserved
    seeds 20261224–20261268 used by prior campaigns."""
    assert not (20261224 <= R.PLACEBO_SEED <= 20261268), "placebo seed must be outside 20261224-20261268"


# ---------------------------------------------------------------- real artifacts schema (if present)
def _find_latest(prefix: str):
    files = sorted((ROOT / "reports").glob(f"campaign406_{prefix}_*.json"))
    files = [f for f in files if ".full." not in f.name]
    return files[-1] if files else None


def test_artifacts_if_present_have_required_flags():
    p = _find_latest("verdict")
    if p is None:
        return
    v = json.loads(p.read_text())
    assert v["campaign"] == 406
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
    assert sw["config"]["betaasym_params"]["window_W"] == 256


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
    test_betaasym_matches_brute_force()
    test_betaasym_defined_after_window_nan_before()
    test_betaasym_non_finite_return_propagates()
    test_betaasym_params()
    test_reference_config_matches_pre_registered_spec()
    test_phase_randomized_surrogate_same_marginal_deterministic()
    test_build_underlying_shapes_and_keys()
    test_build_scores_signals_lookbacks_causal()
    test_betaasym_kernel_not_degenerate()
    test_betaasym_kernel_distinct_from_third_moment()
    test_betaasym_kernel_distinct_from_semicov()
    test_betaasym_kernel_distinct_from_lvac()
    test_betaasym_kernel_distinct_from_dsrv()
    test_betaasym_kernel_distinct_from_acovk()
    test_artifact_campaign_is_406()
    test_mandate_contains_betaasym()
    test_placebo_seed_is_20261270()
    test_placebo_seed_unique_not_reserved()
    test_artifacts_if_present_have_required_flags()
    print("All C406 BETAASYM runner tests passed")
