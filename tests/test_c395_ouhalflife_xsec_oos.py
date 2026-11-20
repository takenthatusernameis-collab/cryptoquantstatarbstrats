"""Tests for C394 runner (scripts/run_c394_ctes_xsec_oos.py): pure-function tests on
synthetic arrays (including a brute-force equality test for the vectorized CTES
kernels vs the per-window reference loop) plus schema/flag validation of emitted
real-data artifacts. No network, no fabricated market data."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import run_c394_ctes_xsec_oos as R  # noqa: E402


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
    for pb in ("ces_spread_placebo", "ces_asym_placebo"):
        assert pb in R.SIGNALS
    for real in ("ces_spread_dev", "ces_asym_dev"):
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


# ---------------------------------------------------------------- CTES metric (brute-force equality)
def test_ctes_matches_brute_force():
    """The vectorized ces_spread/ces_asym kernels MUST equal the brute-force
    reference (per-window conditional tail expectation). Compared strictly
    (maxdiff < 1e-12) with matching NaN patterns."""
    rng = np.random.default_rng(123)
    r = rng.standard_normal(900) * 0.001
    fast = R.compute_ctes_metrics(r, R.CTES_W, R.CTES_N_TAIL, R.CTES_EPS)
    brute = R._ctes_bruteforce(r, R.CTES_W, R.CTES_N_TAIL, R.CTES_EPS)
    for key in ("es_down", "es_up", "ces_spread", "ces_asym"):
        fv, fb = fast[key], brute[key]
        fin = np.isfinite(fv) & np.isfinite(fb)
        assert fin.sum() > 0, f"{key}: no finite overlapping points"
        assert np.array_equal(np.isnan(fv), np.isnan(fb)), f"{key}: NaN pattern mismatch"
    fs, bs_ = fast["ces_spread"], brute["ces_spread"]
    fin_s = np.isfinite(fs) & np.isfinite(bs_)
    maxdiff_s = float(np.max(np.abs(fs[fin_s] - bs_[fin_s]))) if fin_s.sum() else 0.0
    assert maxdiff_s < 1e-12, f"ces_spread: maxdiff={maxdiff_s} >= 1e-12"
    fa, ba = fast["ces_asym"], brute["ces_asym"]
    fin_a = np.isfinite(fa) & np.isfinite(ba)
    maxdiff_a = float(np.max(np.abs(fa[fin_a] - ba[fin_a]))) if fin_a.sum() else 0.0
    assert maxdiff_a < 1e-12, f"ces_asym: maxdiff={maxdiff_a} >= 1e-12"


def test_ctes_defined_after_window_nan_before():
    rng = np.random.default_rng(3)
    r = rng.standard_normal(2000) * 0.001
    m = R.compute_ctes_metrics(r, R.CTES_W, R.CTES_N_TAIL, R.CTES_EPS)
    W = R.CTES_W
    for key in ("es_down", "es_up", "ces_spread", "ces_asym"):
        assert np.isnan(m[key][:W]).all(), key
        assert np.isfinite(m[key][W:]).all(), key


def test_ctes_non_finite_return_propagates():
    """A non-finite return in the window -> NaN for all CTES outputs."""
    rng = np.random.default_rng(9)
    r = rng.standard_normal(600) * 0.001
    r[300] = np.inf
    W = R.CTES_W
    m = R.compute_ctes_metrics(r, W, R.CTES_N_TAIL, R.CTES_EPS)
    # r[300]=inf affects bars t where 300 in [t-W, t) => t in (300, 300+W]
    for t in range(301, min(301 + W, 600)):
        assert np.isnan(m["ces_spread"][t]), f"ces_spread t={t} should be NaN"
        assert np.isnan(m["ces_asym"][t]), f"ces_asym t={t} should be NaN"
    for t in range(W, 300):
        assert np.isfinite(m["ces_spread"][t])
        assert np.isfinite(m["ces_asym"][t])
    for t in range(300 + W + 1, 600):
        assert np.isfinite(m["ces_spread"][t])
        assert np.isfinite(m["ces_asym"][t])


def test_ctes_params():
    assert R.CTES_W == 256
    assert R.CTES_P == 0.10
    assert R.CTES_N_TAIL == 26
    assert R.CTES_EPS == 1e-12


def test_reference_config_matches_pre_registered_spec():
    assert R.ATTR_REPRESENTATIVES == {
        "ces_spread_dev": "ces_spread_dev",
        "ces_asym_dev": "ces_asym_dev",
    }
    assert R.PLACEBO_SEED == 20261258
    assert R.STABILITY_MIN_SIGN_CONSISTENCY == 0.70
    assert R.STABILITY_MIN_SHARPE_CORR == 0.50
    assert R.DOMINANT_SHARE_MIN == 0.50
    assert R.TRAIN_M == 12 and R.TEST_M == 3 and R.ROLL_M == 3
    assert R.CTES_W == 256
    assert R.SIGNALS[0] == "ces_spread_dev"


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
    assert set(series.keys()) == {"es_down", "es_up", "ces_spread", "ces_asym"}
    for k in ("es_down", "es_up", "ces_spread", "ces_asym"):
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
def test_ctes_kernel_distinct_from_degenerate():
    """Rewrite guard: CTES metrics are not degenerate (ces_spread not allclose to 0,
    ces_asym not allclose to 0 where defined)."""
    rng = np.random.default_rng(55)
    r = rng.standard_normal(800) * 0.001
    W = R.CTES_W
    mm = R.compute_ctes_metrics(r, W, R.CTES_N_TAIL, R.CTES_EPS)
    ces_spread = mm["ces_spread"]
    ces_asym = mm["ces_asym"]
    spread_valid = ces_spread[W:]
    asym_valid = ces_asym[W:]
    fin = np.isfinite(spread_valid) & np.isfinite(asym_valid)
    assert fin.sum() > 0
    assert not np.allclose(spread_valid[fin], 0.0, atol=1e-12), "ces_spread collapses to 0"
    assert not np.allclose(asym_valid[fin], 0.0, atol=1e-12), "ces_asym collapses to 0"


# ---------------------------------------------------------------- guard tests (rewrite guards)
def test_artifact_campaign_is_394():
    """Rewrite guard: every emitted artifact self-identifies campaign 394 (never 392/393)."""
    for part in ("verdict", "summary", "registry", "oos_sweep"):
        files = sorted((ROOT / "reports").glob(f"campaign394_{part}_*.json"))
        files = [f for f in files if ".full." not in f.name]
        if not files:
            continue
        obj = json.loads(files[-1].read_text())
        assert obj["campaign"] == 394, f"{part} artifact campaign != 394: {obj.get('campaign')}"


def test_mandate_contains_ctes_and_tail_expectation():
    """Rewrite guard: the C394 mandate names CTES and conditional tail expectation
    (never VTERM/semicov/xcoex/xskew3/ddrun/vterm)."""
    p = sorted((ROOT / "reports").glob("campaign394_oos_sweep_*.json"))
    p = [f for f in p if ".full." not in f.name]
    if not p:
        return
    mandate = json.loads(p[-1].read_text())["mandate"]
    assert "CTES" in mandate, "mandate missing CTES"
    assert "conditional tail" in mandate.lower(), "mandate missing conditional tail"
    assert "expectation" in mandate.lower(), "mandate missing expectation"
    assert "spread" in mandate.lower(), "mandate missing spread"
    assert "VTERM" not in mandate, "mandate must not reference VTERM"
    assert "semicov" not in mandate.lower(), "mandate must not reference semicov"
    assert "XCOEX" not in mandate, "mandate must not reference XCOEX"
    assert "XSKEW3" not in mandate, "mandate must not reference XSKEW3"
    assert "DDRUN" not in mandate, "mandate must not reference DDRUN"


def test_placebo_seed_is_20261258():
    assert R.PLACEBO_SEED == 20261258


# ---------------------------------------------------------------- real artifacts schema (if present)
def _find_latest(prefix: str):
    files = sorted((ROOT / "reports").glob(f"campaign394_{prefix}_*.json"))
    files = [f for f in files if ".full." not in f.name]
    return files[-1] if files else None


def test_artifacts_if_present_have_required_flags():
    p = _find_latest("verdict")
    if p is None:
        return
    v = json.loads(p.read_text())
    assert v["campaign"] == 394
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
    assert sw["config"]["ctes_params"]["window_W"] == 256
    assert sw["config"]["ctes_params"]["n_tail"] == 26
    assert sw["config"]["ctes_params"]["eps"] == 1e-12


def test_cache_meta_ctes_params_distinct():
    meta_path = ROOT / "data" / "cache" / "campaign394_ctes_5m.meta.json"
    if not meta_path.exists():
        return
    meta = json.loads(meta_path.read_text())
    assert meta["campaign"] == 394
    assert meta["source_campaign"] == 312
    assert "ces_params" in meta
    assert meta["ces_params"]["window_W"] == 256
    assert meta["ces_params"]["tail_p"] == 0.10
    assert meta["ces_params"]["n_tail"] == 26
    assert meta["ces_params"]["eps"] == 1e-12
    for other in ("vterm_params", "ddrun_params", "semicov_params", "qspread_params", "rar_params", "lvac_params",
                  "hill_params", "rskek_params", "opte_params", "qatm_params", "dsrv_params",
                  "ker_params", "rqv_params", "bpv_params", "rmad_params", "gmd_params",
                  "rskrkt_params", "tirv_params", "rlrv_params", "signrun_params",
                  "acovk_params", "pslope_params", "vovr_params", "curv_params",
                  "tailmem_params", "turningpt_params", "extpos_params", "prrough_params",
                  "halfrange_params", "bandx_params", "madr_params", "minrv_params",
                  "xcoex_params", "xskew3_params"):
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
    test_ctes_matches_brute_force()
    test_ctes_defined_after_window_nan_before()
    test_ctes_non_finite_return_propagates()
    test_ctes_params()
    test_reference_config_matches_pre_registered_spec()
    test_phase_randomized_surrogate_same_marginal_deterministic()
    test_build_underlying_shapes_and_keys()
    test_build_scores_signals_lookbacks_causal()
    test_ctes_kernel_distinct_from_degenerate()
    test_artifact_campaign_is_394()
    test_mandate_contains_ctes_and_tail_expectation()
    test_placebo_seed_is_20261258()
    test_artifacts_if_present_have_required_flags()
    test_cache_meta_ctes_params_distinct()
    print("All C394 runner tests passed")
