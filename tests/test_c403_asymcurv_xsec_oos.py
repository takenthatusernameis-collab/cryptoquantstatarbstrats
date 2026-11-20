"""Tests for C403 runner (scripts/run_c403_asymcurv_xsec_oos.py): pure-function tests
on synthetic arrays (including a brute-force equality test for the vectorized ASYMCURV
conditional-skewness kernel vs the per-window reference) plus schema/flag validation of
emitted real-data artifacts. No network, no fabricated market data."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import run_c403_asymcurv_xsec_oos as R  # noqa: E402


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
    for pb in ("asym_curv_placebo", "skew_up_placebo", "skew_down_placebo"):
        assert pb in R.SIGNALS
    for real in ("asym_curv_dev", "skew_up_dev", "skew_down_dev"):
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


# ---------------------------------------------------------------- ASYMCURV metric (brute-force equality)
def test_asymcurv_matches_brute_force():
    """The vectorized ASYMCURV conditional-skewness kernel MUST equal the brute-force
    reference (per-window population skewness of {x:lagged>0} and {x:lagged<0},
    asym_curv = skew_up - skew_down). Compared strictly (maxdiff < 1e-12) with
    matching NaN patterns."""
    rng = np.random.default_rng(20261267)
    log_return = rng.standard_normal(4000) * 0.001
    fast = R.compute_asymcurv_metrics(log_return, R.ASYMCURV_W)
    brute = R._asymcurv_bruteforce(log_return, R.ASYMCURV_W)
    for key in ("skew_up", "skew_down", "asym_curv"):
        fv, fb = fast[key], brute[key]
        fin = np.isfinite(fv) & np.isfinite(fb)
        assert fin.sum() > 0, f"{key}: no finite overlapping points"
        assert np.array_equal(np.isnan(fv), np.isnan(fb)), f"{key}: NaN pattern mismatch"
        maxdiff = float(np.max(np.abs(fv[fin] - fb[fin]))) if fin.sum() else 0.0
        assert maxdiff < 1e-12, f"{key}: maxdiff={maxdiff} >= 1e-12"


def test_asymcurv_defined_after_window_nan_before():
    rng = np.random.default_rng(3)
    log_return = rng.standard_normal(4000) * 0.001
    m = R.compute_asymcurv_metrics(log_return, R.ASYMCURV_W)
    W = R.ASYMCURV_W
    for key in ("skew_up", "skew_down", "asym_curv"):
        assert np.isnan(m[key][:W]).all(), key
        assert np.isfinite(m[key][W:]).any(), key


def test_asymcurv_non_finite_return_propagates():
    """A non-finite return in the window -> NaN for all ASYMCURV outputs in affected bars."""
    rng = np.random.default_rng(9)
    log_return = rng.standard_normal(600) * 0.001
    log_return[300] = np.inf
    W = R.ASYMCURV_W
    m = R.compute_asymcurv_metrics(log_return, W)
    for t in range(300, min(300 + W, 600)):
        assert np.isnan(m["skew_up"][t]), f"skew_up t={t} should be NaN"
        assert np.isnan(m["skew_down"][t]), f"skew_down t={t} should be NaN"
        assert np.isnan(m["asym_curv"][t]), f"asym_curv t={t} should be NaN"
    for t in range(W, 300):
        assert np.isfinite(m["skew_up"][t]), f"skew_up t={t} should be finite"
    for t in range(300 + W, 600):
        assert np.isfinite(m["skew_up"][t]), f"skew_up t={t} should be finite"


def test_asymcurv_params():
    assert R.ASYMCURV_W == 256


def test_reference_config_matches_pre_registered_spec():
    assert R.ATTR_REPRESENTATIVES == {
        "asym_curv_dev": "asym_curv_dev",
        "skew_up_dev": "skew_up_dev",
        "skew_down_dev": "skew_down_dev",
    }
    assert R.PLACEBO_SEED == 20261267
    assert R.STABILITY_MIN_SIGN_CONSISTENCY == 0.70
    assert R.STABILITY_MIN_SHARPE_CORR == 0.50
    assert R.DOMINANT_SHARE_MIN == 0.50
    assert R.TRAIN_M == 12 and R.TEST_M == 3 and R.ROLL_M == 3
    assert R.ASYMCURV_W == 256
    assert R.SIGNALS[0] == "asym_curv_dev"


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
    assert set(series.keys()) == {"skew_up", "skew_down", "asym_curv"}
    for k in ("skew_up", "skew_down", "asym_curv"):
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
def test_asymcurv_kernel_not_degenerate():
    """Rewrite guard: ASYMCURV metrics are not degenerate (not allclose to 0 where defined)."""
    rng = np.random.default_rng(55)
    log_return = rng.standard_normal(1600) * 0.001
    W = R.ASYMCURV_W
    mm = R.compute_asymcurv_metrics(log_return, W)
    su = mm["skew_up"]
    sd = mm["skew_down"]
    ac = mm["asym_curv"]
    fin = np.isfinite(su) & np.isfinite(sd) & np.isfinite(ac)
    assert fin.sum() > 0
    for name, arr in (("skew_up", su), ("skew_down", sd), ("asym_curv", ac)):
        valid = arr[fin]
        assert not np.allclose(valid, 0.0, atol=1e-12), f"{name} collapses to 0"


def _rskek_stat(X, W):
    """Inline C361 RSKEK: unconditional population skewness of the full window."""
    n = len(X)
    out = np.full(n, np.nan)
    for t in range(W, n):
        Xw = X[t - W + 1:t + 1]
        if not np.isfinite(Xw).all():
            continue
        mu = float(np.mean(Xw))
        d = Xw - mu
        sigma2 = float(np.mean(d * d))
        if sigma2 <= 0:
            continue
        sigma = np.sqrt(sigma2)
        m3 = float(np.mean(d * d * d))
        out[t] = m3 / (sigma ** 3)
    return out


def _rkt_stat(X, W):
    """Inline C371 RKT: unconditional population excess kurtosis of the full window."""
    n = len(X)
    out = np.full(n, np.nan)
    for t in range(W, n):
        Xw = X[t - W + 1:t + 1]
        if not np.isfinite(Xw).all():
            continue
        mu = float(np.mean(Xw))
        d = Xw - mu
        sigma2 = float(np.mean(d * d))
        if sigma2 <= 0:
            continue
        sigma = np.sqrt(sigma2)
        m4 = float(np.mean(d ** 4))
        out[t] = m4 / (sigma ** 4) - 3.0
    return out


def _hill_single_style_stat(X, W, n_exceed=12):
    """Inline C362 Hill single-scale tail-index (n_exceed=12 only)."""
    n = len(X)
    out = np.full(n, np.nan)
    for t in range(W, n):
        Xw = X[t - W + 1:t + 1]
        if not np.isfinite(Xw).all():
            continue
        a = np.sort(np.abs(Xw))[::-1]
        if len(a) <= n_exceed:
            continue
        u = a[n_exceed]
        if u <= 0:
            continue
        top = a[:n_exceed]
        denom = float(np.sum(np.log(top / u)))
        if denom <= 0:
            continue
        out[t] = n_exceed / denom
    return out


def _xskew3_style_stat(X, W):
    """Inline C391 XSKEW3-style third-order lagged product (single-series proxy)."""
    n = len(X)
    out = np.full(n, np.nan)
    for t in range(W, n):
        Xw = X[t - W + 1:t + 1]
        if not np.isfinite(Xw).all() or len(Xw) < 3:
            continue
        x = Xw
        prod = x[2:] * x[1:-1] * x[:-2]
        if not np.isfinite(prod).all():
            continue
        out[t] = float(np.mean(prod))
    return out


def _semicov_style_stat(X, W, k=1):
    """Inline C380 SEMICOV-style signed-conditional lag covariance (k=1)."""
    n = len(X)
    out = np.full(n, np.nan)
    for t in range(W, n):
        Xw = X[t - W + 1:t + 1]
        if not np.isfinite(Xw).all() or len(Xw) <= k:
            continue
        rt = Xw[k:]
        rlm = Xw[:-k]
        neg = rlm < 0
        pos = rlm > 0
        if neg.sum() < 2 or pos.sum() < 2:
            continue
        def _cov(a, b):
            a = a - a.mean()
            b = b - b.mean()
            return float(np.mean(a * b))
        out[t] = _cov(rt[neg], rlm[neg]) - _cov(rt[pos], rlm[pos])
    return out


def _dsrv_style_stat(X, W):
    """Inline C364 DSRV-style downside/upside semivariance log-ratio."""
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


def test_asymcurv_kernel_distinct_from_rskek():
    """Rewrite guard: ASYMCURV conditional skewness is a different object from
    C361 RSKEK unconditional skewness of the full window."""
    rng = np.random.default_rng(123)
    log_return = rng.standard_normal(1200) * 0.001
    W = R.ASYMCURV_W
    mm = R.compute_asymcurv_metrics(log_return, W)
    ac = mm["asym_curv"][W:]
    rskek = _rskek_stat(log_return, W)[W:]
    fin = np.isfinite(ac) & np.isfinite(rskek)
    assert fin.sum() > 0
    assert not np.allclose(ac[fin], rskek[fin], atol=1e-6), "ASYMCURV degenerates to RSKEK"


def test_asymcurv_kernel_distinct_from_rkt():
    """Rewrite guard: ASYMCURV is a different object from C371 RKT excess kurtosis."""
    rng = np.random.default_rng(124)
    log_return = rng.standard_normal(1200) * 0.001
    W = R.ASYMCURV_W
    mm = R.compute_asymcurv_metrics(log_return, W)
    ac = mm["asym_curv"][W:]
    rkt = _rkt_stat(log_return, W)[W:]
    fin = np.isfinite(ac) & np.isfinite(rkt)
    assert fin.sum() > 0
    assert not np.allclose(ac[fin], rkt[fin], atol=1e-6), "ASYMCURV degenerates to RKT"


def test_asymcurv_kernel_distinct_from_hill_single():
    """Rewrite guard: ASYMCURV is a different object from C362 Hill single-scale
    tail-index (n_exceed=12)."""
    rng = np.random.default_rng(125)
    log_return = rng.standard_normal(1200) * 0.001
    W = R.ASYMCURV_W
    mm = R.compute_asymcurv_metrics(log_return, W)
    ac = mm["asym_curv"][W:]
    hill = _hill_single_style_stat(log_return, W)[W:]
    fin = np.isfinite(ac) & np.isfinite(hill)
    assert fin.sum() > 0
    assert not np.allclose(ac[fin], hill[fin], atol=1e-6), "ASYMCURV degenerates to Hill"


def test_asymcurv_kernel_distinct_from_xskew3():
    """Rewrite guard: ASYMCURV is a different object from C391 XSKEW3 lag-1 cross
    third-moment time-irreversibility."""
    rng = np.random.default_rng(126)
    log_return = rng.standard_normal(1200) * 0.001
    W = R.ASYMCURV_W
    mm = R.compute_asymcurv_metrics(log_return, W)
    ac = mm["asym_curv"][W:]
    xskew3 = _xskew3_style_stat(log_return, W)[W:]
    fin = np.isfinite(ac) & np.isfinite(xskew3)
    assert fin.sum() > 0
    assert not np.allclose(ac[fin], xskew3[fin], atol=1e-6), "ASYMCURV degenerates to XSKEW3"


def test_asymcurv_kernel_distinct_from_semicov():
    """Rewrite guard: ASYMCURV is a different object from C380 SEMICOV
    signed-conditional lag covariance."""
    rng = np.random.default_rng(127)
    log_return = rng.standard_normal(1200) * 0.001
    W = R.ASYMCURV_W
    mm = R.compute_asymcurv_metrics(log_return, W)
    ac = mm["asym_curv"][W:]
    semicov = _semicov_style_stat(log_return, W)[W:]
    fin = np.isfinite(ac) & np.isfinite(semicov)
    assert fin.sum() > 0
    assert not np.allclose(ac[fin], semicov[fin], atol=1e-6), "ASYMCURV degenerates to SEMICOV"


def test_asymcurv_kernel_distinct_from_dsrv():
    """Rewrite guard: ASYMCURV is a different object from C364 DSRV downside/upside
    semivariance log-ratio."""
    rng = np.random.default_rng(128)
    log_return = rng.standard_normal(1200) * 0.001
    W = R.ASYMCURV_W
    mm = R.compute_asymcurv_metrics(log_return, W)
    ac = mm["asym_curv"][W:]
    dsrv = _dsrv_style_stat(log_return, W)[W:]
    fin = np.isfinite(ac) & np.isfinite(dsrv)
    assert fin.sum() > 0
    assert not np.allclose(ac[fin], dsrv[fin], atol=1e-6), "ASYMCURV degenerates to DSRV"


# ---------------------------------------------------------------- guard tests (rewrite guards)
def test_artifact_campaign_is_403():
    """Rewrite guard: every emitted artifact self-identifies campaign 403."""
    for part in ("verdict", "summary", "registry", "oos_sweep"):
        files = sorted((ROOT / "reports").glob(f"campaign403_{part}_*.json"))
        files = [f for f in files if ".full." not in f.name]
        if not files:
            continue
        obj = json.loads(files[-1].read_text())
        assert obj["campaign"] == 403, f"{part} artifact campaign != 403: {obj.get('campaign')}"


def test_mandate_contains_asymcurv():
    """Rewrite guard: the C403 mandate names ASYMCURV conditional skewness
    (never TSCALE/HILL/RVQUART/KTREND/CBREAK/SPECFM/MAGNET/OUHALFLIFE/CTES/
    VTERM/DDRUN/XSKEW3/XCOEX/MINRV/MADR/BANDX/PRROUGH/HALFRANGE/LMOM/SEMICOV)."""
    p = sorted((ROOT / "reports").glob("campaign403_oos_sweep_*.json"))
    p = [f for f in p if ".full." not in f.name]
    if not p:
        return
    mandate = json.loads(p[-1].read_text())["mandate"]
    assert "ASYMCURV" in mandate, "mandate missing ASYMCURV"
    assert "CONDITIONAL" in mandate, "mandate missing CONDITIONAL"
    for bad in ("TSCALE", "HILL", "RVQUART", "QUARTICITY", "KTREND", "CBREAK", "SPECFM", "MAGNET",
                "OUHALFLIFE", "CTES", "VTERM", "DDRUN", "XSKEW3", "XCOEX", "MINRV", "MADR", "BANDX",
                "PRROUGH", "HALFRANGE", "LMOM", "KENDALL", "SPEARMAN", "SEMICOV"):
        assert bad not in mandate, f"mandate must not reference {bad} (prior campaign)"


def test_placebo_seed_is_20261267():
    assert R.PLACEBO_SEED == 20261267


def test_placebo_seed_unique_not_reserved():
    """Rewrite guard: C403 placebo seed 20261267 must not collide with reserved
    seeds 20261224–20261266 used by prior campaigns (20261266 = C402)."""
    assert not (20261224 <= R.PLACEBO_SEED <= 20261266), "placebo seed must be outside 20261224-20261266"


# ---------------------------------------------------------------- real artifacts schema (if present)
def _find_latest(prefix: str):
    files = sorted((ROOT / "reports").glob(f"campaign403_{prefix}_*.json"))
    files = [f for f in files if ".full." not in f.name]
    return files[-1] if files else None


def test_artifacts_if_present_have_required_flags():
    p = _find_latest("verdict")
    if p is None:
        return
    v = json.loads(p.read_text())
    assert v["campaign"] == 403
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
    assert sw["config"]["asymcurv_params"]["window_W"] == 256


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
    test_asymcurv_matches_brute_force()
    test_asymcurv_defined_after_window_nan_before()
    test_asymcurv_non_finite_return_propagates()
    test_asymcurv_params()
    test_reference_config_matches_pre_registered_spec()
    test_phase_randomized_surrogate_same_marginal_deterministic()
    test_build_underlying_shapes_and_keys()
    test_build_scores_signals_lookbacks_causal()
    test_asymcurv_kernel_not_degenerate()
    test_asymcurv_kernel_distinct_from_rskek()
    test_asymcurv_kernel_distinct_from_rkt()
    test_asymcurv_kernel_distinct_from_hill_single()
    test_asymcurv_kernel_distinct_from_xskew3()
    test_asymcurv_kernel_distinct_from_semicov()
    test_asymcurv_kernel_distinct_from_dsrv()
    test_artifact_campaign_is_403()
    test_mandate_contains_asymcurv()
    test_placebo_seed_is_20261267()
    test_placebo_seed_unique_not_reserved()
    test_artifacts_if_present_have_required_flags()
    print("All C403 ASYMCURV runner tests passed")
