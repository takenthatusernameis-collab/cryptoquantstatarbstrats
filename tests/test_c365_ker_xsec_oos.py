"""Tests for C365 runner (scripts/run_c365_ker_xsec_oos.py): pure-function tests on
synthetic arrays (including a brute-force equality test for the vectorized KER
kernel) plus schema/flag validation of emitted real-data artifacts. No network,
no fabricated market data."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import run_c365_ker_xsec_oos as R  # noqa: E402


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
    for pb in ("ker_er_placebo", "ker_signed_placebo"):
        assert pb in R.SIGNALS
    for real in ("ker_er_dev", "ker_signed_dev"):
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


# ---------------------------------------------------------------- KER metric
def test_ker_matches_brute_force():
    """The vectorized KER kernel MUST equal the brute-force reference."""
    rng = np.random.default_rng(5)
    c = 100.0 * np.cumprod(1.0 + rng.standard_normal(700) * 0.0003)
    fast = R.compute_ker_metrics(c, R.KER_W)
    brute = R._ker_bruteforce(c, R.KER_W)
    W = R.KER_W
    for key in ("net_disp", "path_len", "ker_er", "ker_signed"):
        fv, fb = fast[key], brute[key]
        fin = np.isfinite(fv) & np.isfinite(fb)
        assert fin.sum() > 0, f"{key}: no finite overlapping points"
        assert np.array_equal(np.isnan(fv), np.isnan(fb)), f"{key}: NaN pattern mismatch"
        assert np.allclose(fv[fin], fb[fin], rtol=1e-9, atol=1e-9), f"{key}: value mismatch"
    # explicit primitives
    assert np.allclose(fast["net_disp"][W:], np.abs(c[W:] - c[:-W]), rtol=1e-9, atol=1e-9)
    pl = np.empty(len(c) - W)
    for t in range(W, len(c)):
        pl[t - W] = sum(abs(c[i] - c[i - 1]) for i in range(t - W + 1, t + 1))
    assert np.allclose(fast["path_len"][W:], pl, rtol=1e-9, atol=1e-9)
    assert np.allclose(fast["ker_er"][W:], fast["net_disp"][W:] / fast["path_len"][W:], rtol=1e-9, atol=1e-9)


def test_ker_defined_after_window_nan_before():
    rng = np.random.default_rng(1)
    c = 100.0 * np.exp(np.cumsum(rng.standard_normal(2000) * 0.001))
    m = R.compute_ker_metrics(c, R.KER_W)
    W = R.KER_W
    assert np.isnan(m["net_disp"][:W]).all()
    assert np.isnan(m["path_len"][:W]).all()
    assert np.isnan(m["ker_er"][:W]).all()
    assert np.isnan(m["ker_signed"][:W]).all()
    assert np.isfinite(m["net_disp"][W:]).all()
    assert np.isfinite(m["path_len"][W:]).all()
    assert np.isfinite(m["ker_er"][W:]).all()
    assert np.isfinite(m["ker_signed"][W:]).all()


def test_ker_nan_in_window_propagates():
    rng = np.random.default_rng(0)
    c = 100.0 * np.exp(np.cumsum(rng.standard_normal(1200) * 0.001))
    c[500] = np.nan
    W = R.KER_W
    m = R.compute_ker_metrics(c, W)
    for t in range(500, 500 + W + 1):
        assert np.isnan(m["ker_er"][t]), f"ker_er t={t} should be NaN"
        assert np.isnan(m["ker_signed"][t]), f"ker_signed t={t} should be NaN"
    for t in range(W, 500):
        assert np.isfinite(m["ker_er"][t]), f"ker_er t={t} should be finite"
    for t in range(500 + W + 1, 1200):
        assert np.isfinite(m["ker_er"][t]), f"ker_er t={t} should be finite"


def test_ker_flat_price_path_len_zero_nan():
    """Flat price: path_len=0 -> ker_er/ker_signed NaN; net_disp=0."""
    c = np.full(600, 50.0)
    m = R.compute_ker_metrics(c, R.KER_W)
    W = R.KER_W
    assert (m["net_disp"][W:] == 0.0).all()
    assert (m["path_len"][W:] == 0.0).all()
    assert np.isnan(m["ker_er"][W:]).all()
    assert np.isnan(m["ker_signed"][W:]).all()


def test_ker_params():
    assert R.KER_W == 256


def test_reference_config_matches_pre_registered_spec():
    assert R.ATTR_REPRESENTATIVES == {
        "ker_er_dev": "ker_er_dev",
        "ker_signed_dev": "ker_signed_dev",
    }
    assert R.PLACEBO_SEED == 20261229
    assert R.STABILITY_MIN_SIGN_CONSISTENCY == 0.70
    assert R.STABILITY_MIN_SHARPE_CORR == 0.50
    assert R.DOMINANT_SHARE_MIN == 0.50
    assert R.TRAIN_M == 12 and R.TEST_M == 3 and R.ROLL_M == 3
    assert R.KER_W == 256
    assert R.SIGNALS[0] == "ker_er_dev"


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
    assert set(series.keys()) == {"net_disp", "path_len", "ker_er", "ker_signed"}
    for k in ("net_disp", "path_len", "ker_er", "ker_signed"):
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
    files = sorted((ROOT / "reports").glob(f"campaign365_{prefix}_*.json"))
    files = [f for f in files if ".full." not in f.name]
    return files[-1] if files else None


def test_artifacts_if_present_have_required_flags():
    p = _find_latest("verdict")
    if p is None:
        return
    v = json.loads(p.read_text())
    assert v["campaign"] == 365
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
    assert sw["config"]["ker_params"]["W"] == 256


def test_cache_meta_ker_params_distinct():
    meta_path = ROOT / "data" / "cache" / "campaign365_ker_5m.meta.json"
    if not meta_path.exists():
        return
    meta = json.loads(meta_path.read_text())
    assert meta["campaign"] == 365
    assert meta["source_campaign"] == 312
    assert "ker_params" in meta
    assert meta["ker_params"]["window_W"] == 256
    assert "lvac_params" not in meta
    assert "hill_params" not in meta
    assert "rskek_params" not in meta
    assert "opte_params" not in meta
    assert "qatm_params" not in meta
    assert "dsrv_params" not in meta


if __name__ == "__main__":
    test_holm_and_bh_reject_correctly()
    test_holm_and_bh_monotone_and_bounded()
    test_n_trials_matches_pre_registered_grid_product()
    test_cost_rate_taker_and_maker_blend()
    test_positions_dollar_neutral_and_causal()
    test_positions_hold_reduces_turnover()
    test_positions_nan_asset_gets_zero_weight()
    test_wf_splits_month_aligned_non_overlapping()
    test_ker_matches_brute_force()
    test_ker_defined_after_window_nan_before()
    test_ker_nan_in_window_propagates()
    test_ker_flat_price_path_len_zero_nan()
    test_ker_params()
    test_reference_config_matches_pre_registered_spec()
    test_phase_randomized_surrogate_same_marginal_deterministic()
    test_build_underlying_shapes_and_keys()
    test_build_scores_signals_lookbacks_causal()
    test_artifacts_if_present_have_required_flags()
    test_cache_meta_ker_params_distinct()
    print("All tests passed")
