"""Tests for C379 runner (scripts/run_c379_curv_xsec_oos.py): pure-function tests on
synthetic arrays (including a brute-force equality test for the vectorized CURV
curv_shape/curv_tilt kernels vs np.polyfit(s, y, 2)) plus schema/flag validation
of emitted real-data artifacts. No network, no fabricated market data."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import run_c379_curv_xsec_oos as R  # noqa: E402


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
    for pb in ("curv_shape_placebo", "curv_tilt_placebo"):
        assert pb in R.SIGNALS
    for real in ("curv_shape_dev", "curv_tilt_dev"):
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


# ---------------------------------------------------------------- CURV metric (brute-force equality vs np.polyfit)
def test_curv_matches_brute_force():
    """The vectorized curv_shape/curv_tilt kernels MUST equal the brute-force
    reference (np.polyfit(s, y, 2) normal-equation solution). curv_shape is
    compared strictly (maxdiff < 1e-12) everywhere; curv_tilt inherits the
    intrinsic conditioning floor of max(|b*W|, 1e-12) so it is compared
    strictly where |b*W| >= 1 (well-conditioned) and with relative tolerance
    rtol=1e-4/atol=1e-9 where |b*W| < 1 (clamped-denominator zone, where
    1-ulp b differences amplify past 1e-12)."""
    rng = np.random.default_rng(5)
    r = rng.standard_normal(700) * 0.001
    prices = 100.0 * np.exp(np.cumsum(r))
    fast = R.compute_curv_metrics(prices, R.CURV_W)
    brute = R._curv_bruteforce(prices, R.CURV_W)
    W = R.CURV_W
    s = np.arange(W, dtype=float)
    for key in ("curv_shape", "curv_tilt"):
        fv, fb = fast[key], brute[key]
        fin = np.isfinite(fv) & np.isfinite(fb)
        assert fin.sum() > 0, f"{key}: no finite overlapping points"
        assert np.array_equal(np.isnan(fv), np.isnan(fb)), f"{key}: NaN pattern mismatch"
    # curv_shape: strict brute-force equality everywhere
    fs, bs_ = fast["curv_shape"], brute["curv_shape"]
    fin_s = np.isfinite(fs) & np.isfinite(bs_)
    maxdiff_s = float(np.max(np.abs(fs[fin_s] - bs_[fin_s]))) if fin_s.sum() else 0.0
    assert maxdiff_s < 1e-12, f"curv_shape: maxdiff={maxdiff_s} >= 1e-12"
    # curv_tilt: zone-aware against normative per-window polyfit
    ft, bt = fast["curv_tilt"], brute["curv_tilt"]
    fin_t = np.isfinite(ft) & np.isfinite(bt)
    assert fin_t.sum() > 0, "curv_tilt: no finite overlapping points"
    for t in range(W - 1, len(prices)):
        if not fin_t[t]:
            continue
        y = np.log(prices[t - W + 1:t + 1])
        coef = np.polyfit(s, y, 2)  # [c, b, a]
        c, b = float(coef[0]), float(coef[1])
        shape = c * W * W
        tilt = shape / max(abs(b * W), 1e-12)
        assert np.isclose(fs[t], shape, rtol=1e-9, atol=1e-12)
        if abs(b * W) >= 1.0:
            assert np.isclose(ft[t], tilt, rtol=1e-9, atol=1e-12)
        else:
            assert np.isclose(ft[t], tilt, rtol=1e-4, atol=1e-9)


def test_curv_defined_after_window_nan_before():
    rng = np.random.default_rng(1)
    r = rng.standard_normal(2000) * 0.001
    prices = 100.0 * np.exp(np.cumsum(r))
    m = R.compute_curv_metrics(prices, R.CURV_W)
    W = R.CURV_W
    assert np.isnan(m["curv_shape"][:W - 1]).all()
    assert np.isnan(m["curv_tilt"][:W - 1]).all()
    assert np.isfinite(m["curv_shape"][W - 1:]).all()
    assert np.isfinite(m["curv_tilt"][W - 1:]).all()


def test_curv_non_positive_price_in_window_propagates():
    """A zero/negative price in the window -> NaN (log undefined / non-finite)."""
    prices = np.ones(600) * 100.0
    prices[300] = 0.0
    W = R.CURV_W
    m = R.compute_curv_metrics(prices, W)
    for t in range(300, 300 + W):
        assert np.isnan(m["curv_shape"][t]), f"curv_shape t={t} should be NaN"
        assert np.isnan(m["curv_tilt"][t]), f"curv_tilt t={t} should be NaN"
    for t in range(W - 1, 300):
        assert np.isfinite(m["curv_shape"][t])
        assert np.isfinite(m["curv_tilt"][t])
    for t in range(300 + W, 600):
        assert np.isfinite(m["curv_shape"][t])
        assert np.isfinite(m["curv_tilt"][t])


def test_curv_non_finite_price_propagates():
    """A non-finite price in the window -> NaN (log undefined / non-finite)."""
    prices = np.ones(600) * 100.0
    prices[300] = np.inf
    W = R.CURV_W
    m = R.compute_curv_metrics(prices, W)
    # window for bar t covers indices [t-W+1 .. t]; it contains index 300 iff
    # t in [300, 300+W-1]
    for t in range(300, min(300 + W, 600)):
        assert np.isnan(m["curv_shape"][t]), f"curv_shape t={t} should be NaN"
        assert np.isnan(m["curv_tilt"][t]), f"curv_tilt t={t} should be NaN"
    for t in range(W - 1, 300):
        assert np.isfinite(m["curv_shape"][t]), f"curv_shape t={t} should be finite"
        assert np.isfinite(m["curv_tilt"][t]), f"curv_tilt t={t} should be finite"
    for t in range(300 + W, 600):
        assert np.isfinite(m["curv_shape"][t])
        assert np.isfinite(m["curv_tilt"][t])


def test_curv_params():
    assert R.CURV_W == 256
    assert R.CURV_POLY_DEGREE == 2


def test_reference_config_matches_pre_registered_spec():
    assert R.ATTR_REPRESENTATIVES == {
        "curv_shape_dev": "curv_shape_dev",
        "curv_tilt_dev": "curv_tilt_dev",
    }
    assert R.PLACEBO_SEED == 20261243
    assert R.STABILITY_MIN_SIGN_CONSISTENCY == 0.70
    assert R.STABILITY_MIN_SHARPE_CORR == 0.50
    assert R.DOMINANT_SHARE_MIN == 0.50
    assert R.TRAIN_M == 12 and R.TEST_M == 3 and R.ROLL_M == 3
    assert R.CURV_W == 256
    assert R.SIGNALS[0] == "curv_shape_dev"


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
    assert set(series.keys()) == {"curv_shape", "curv_tilt"}
    for k in ("curv_shape", "curv_tilt"):
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


# ---------------------------------------------------------------- real artifacts schema (if present)
def _find_latest(prefix: str):
    files = sorted((ROOT / "reports").glob(f"campaign379_{prefix}_*.json"))
    files = [f for f in files if ".full." not in f.name]
    return files[-1] if files else None


def test_artifacts_if_present_have_required_flags():
    p = _find_latest("verdict")
    if p is None:
        return
    v = json.loads(p.read_text())
    assert v["campaign"] == 379
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
    assert sw["config"]["curv_params"]["W"] == 256


def test_cache_meta_curv_params_distinct():
    meta_path = ROOT / "data" / "cache" / "campaign379_curv_5m.meta.json"
    if not meta_path.exists():
        return
    meta = json.loads(meta_path.read_text())
    assert meta["campaign"] == 379
    assert meta["source_campaign"] == 312
    assert "curv_params" in meta
    assert meta["curv_params"]["window_W"] == 256
    for other in ("qspread_params", "rar_params", "lvac_params", "hill_params", "rskek_params",
                  "opte_params", "qatm_params", "dsrv_params", "ker_params",
                  "rqv_params", "bpv_params", "rmad_params", "gmd_params",
                  "rskrkt_params", "tirv_params", "rlrv_params", "signrun_params",
                  "acovk_params", "pslope_params", "vovr_params"):
        assert other not in meta


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
    test_curv_matches_brute_force()
    test_curv_defined_after_window_nan_before()
    test_curv_non_positive_price_in_window_propagates()
    test_curv_non_finite_price_propagates()
    test_curv_params()
    test_reference_config_matches_pre_registered_spec()
    test_phase_randomized_surrogate_same_marginal_deterministic()
    test_build_underlying_shapes_and_keys()
    test_build_scores_signals_lookbacks_causal()
    test_artifacts_if_present_have_required_flags()
    test_cache_meta_curv_params_distinct()
    print("All C379 runner tests passed")
