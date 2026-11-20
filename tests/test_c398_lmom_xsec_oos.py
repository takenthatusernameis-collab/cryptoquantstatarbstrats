"""Tests for C398 runner (scripts/run_c398_lmom_xsec_oos.py): pure-function tests on
synthetic arrays (including a brute-force equality test for the vectorized LMOM
L-skewness/L-kurtosis kernels vs the per-window reference) plus schema/flag
validation of emitted real-data artifacts. No network, no fabricated market data."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import run_c398_lmom_xsec_oos as R  # noqa: E402


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
    for pb in ("lmom_skew_placebo", "lmom_kurt_placebo"):
        assert pb in R.SIGNALS
    for real in ("lmom_skew_dev", "lmom_kurt_dev"):
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


# ---------------------------------------------------------------- LMOM metric (brute-force equality)
def test_lmom_matches_brute_force():
    """The vectorized LMOM L-skewness/L-kurtosis kernels MUST equal the brute-force
    reference (per-window probability-weighted moments over sorted returns).
    Compared strictly (maxdiff < 1e-12) with matching NaN patterns."""
    rng = np.random.default_rng(20261262)
    log_return = rng.standard_normal(4000) * 0.001
    fast = R.compute_lmom_metrics(log_return, R.LMOM_W)
    brute = R._lmom_bruteforce(log_return, R.LMOM_W)
    for key in ("lmom_skew", "lmom_kurt"):
        fv, fb = fast[key], brute[key]
        fin = np.isfinite(fv) & np.isfinite(fb)
        assert fin.sum() > 0, f"{key}: no finite overlapping points"
        assert np.array_equal(np.isnan(fv), np.isnan(fb)), f"{key}: NaN pattern mismatch"
        maxdiff = float(np.max(np.abs(fv[fin] - fb[fin]))) if fin.sum() else 0.0
        assert maxdiff < 1e-12, f"{key}: maxdiff={maxdiff} >= 1e-12"


def test_lmom_defined_after_window_nan_before():
    rng = np.random.default_rng(3)
    log_return = rng.standard_normal(4000) * 0.001
    m = R.compute_lmom_metrics(log_return, R.LMOM_W)
    W = R.LMOM_W
    for key in ("lmom_skew", "lmom_kurt"):
        assert np.isnan(m[key][:W]).all(), key
        assert np.isfinite(m[key][W:]).any(), key


def test_lmom_non_finite_return_propagates():
    """A non-finite return in the window -> NaN for all LMOM outputs in affected bars."""
    rng = np.random.default_rng(9)
    log_return = rng.standard_normal(600) * 0.001
    log_return[300] = np.inf
    W = R.LMOM_W
    m = R.compute_lmom_metrics(log_return, W)
    for t in range(300, min(300 + W, 600)):
        assert np.isnan(m["lmom_skew"][t]), f"lmom_skew t={t} should be NaN"
        assert np.isnan(m["lmom_kurt"][t]), f"lmom_kurt t={t} should be NaN"
    for t in range(W, 300):
        assert np.isfinite(m["lmom_skew"][t]), f"lmom_skew t={t} should be finite"
    for t in range(300 + W, 600):
        assert np.isfinite(m["lmom_skew"][t]), f"lmom_skew t={t} should be finite"


def test_lmom_params():
    assert R.LMOM_W == 256


def test_lmom_constant_returns_edge_case():
    """Constant returns -> all order statistics equal -> beta_r all equal -> lambda_2=0 -> NaN (matches brute force)."""
    log_return = np.ones(600) * 0.001
    fast = R.compute_lmom_metrics(log_return, R.LMOM_W)
    brute = R._lmom_bruteforce(log_return, R.LMOM_W)
    for key in ("lmom_skew", "lmom_kurt"):
        fv, fb = fast[key], brute[key]
        fin = np.isfinite(fv) & np.isfinite(fb)
        assert np.array_equal(np.isnan(fv), np.isnan(fb)), key
        maxdiff = float(np.max(np.abs(fv[fin] - fb[fin]))) if fin.sum() else 0.0
        assert maxdiff < 1e-12, f"{key}: maxdiff={maxdiff} >= 1e-12"


def test_reference_config_matches_pre_registered_spec():
    assert R.ATTR_REPRESENTATIVES == {
        "lmom_skew_dev": "lmom_skew_dev",
        "lmom_kurt_dev": "lmom_kurt_dev",
    }
    assert R.PLACEBO_SEED == 20261262
    assert R.STABILITY_MIN_SIGN_CONSISTENCY == 0.70
    assert R.STABILITY_MIN_SHARPE_CORR == 0.50
    assert R.DOMINANT_SHARE_MIN == 0.50
    assert R.TRAIN_M == 12 and R.TEST_M == 3 and R.ROLL_M == 3
    assert R.LMOM_W == 256
    assert R.SIGNALS[0] == "lmom_skew_dev"


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
    assert set(series.keys()) == {"lmom_skew", "lmom_kurt"}
    for k in ("lmom_skew", "lmom_kurt"):
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
def test_lmom_kernel_not_degenerate():
    """Rewrite guard: LMOM metrics are not degenerate (not allclose to 0/1 where defined)."""
    rng = np.random.default_rng(55)
    log_return = rng.standard_normal(1600) * 0.001
    W = R.LMOM_W
    mm = R.compute_lmom_metrics(log_return, W)
    skew = mm["lmom_skew"]
    kurt = mm["lmom_kurt"]
    skew_valid = skew[W:]
    kurt_valid = kurt[W:]
    fin = np.isfinite(skew_valid) & np.isfinite(kurt_valid)
    assert fin.sum() > 0
    assert not np.allclose(skew_valid[fin], 0.0, atol=1e-12), "L-skewness collapses to 0"
    assert not np.allclose(kurt_valid[fin], 0.0, atol=1e-12), "L-kurtosis collapses to 0"


# ---------------------------------------------------------------- guard tests (rewrite guards)
def test_artifact_campaign_is_398():
    """Rewrite guard: every emitted artifact self-identifies campaign 398 (never 397/399)."""
    for part in ("verdict", "summary", "registry", "oos_sweep"):
        files = sorted((ROOT / "reports").glob(f"campaign398_{part}_*.json"))
        files = [f for f in files if ".full." not in f.name]
        if not files:
            continue
        obj = json.loads(files[-1].read_text())
        assert obj["campaign"] == 398, f"{part} artifact campaign != 398: {obj.get('campaign')}"


def test_mandate_contains_lmom():
    """Rewrite guard: the C398 mandate names LMOM L-moment skewness/kurtosis (never SPECFM/MAGNET/OUHALFLIFE/CTES/VTERM/DDRUN/XSKEW3/XCOEX/MINRV/MADR/BANDX/PRROUGH/HALFRANGE)."""
    p = sorted((ROOT / "reports").glob("campaign398_oos_sweep_*.json"))
    p = [f for f in p if ".full." not in f.name]
    if not p:
        return
    mandate = json.loads(p[-1].read_text())["mandate"]
    assert "LMOM" in mandate, "mandate missing LMOM"
    assert "L-MOMENT" in mandate, "mandate missing L-MOMENT"
    assert "SPECFM" not in mandate, "mandate must not reference SPECFM (prior campaign C397)"
    assert "MAGNET" not in mandate, "mandate must not reference MAGNET (prior campaign C396)"
    assert "OUHALFLIFE" not in mandate, "mandate must not reference OUHALFLIFE (prior campaign C395)"
    assert "CTES" not in mandate, "mandate must not reference CTES (prior campaign C394)"
    assert "VTERM" not in mandate, "mandate must not reference VTERM (prior campaign C393)"
    assert "DDRUN" not in mandate, "mandate must not reference DDRUN (prior campaign C392)"
    assert "XSKEW3" not in mandate, "mandate must not reference XSKEW3 (prior campaign C391)"
    assert "XCOEX" not in mandate, "mandate must not reference XCOEX (prior campaign C390)"
    assert "MINRV" not in mandate, "mandate must not reference MINRV (prior campaign C389)"
    assert "MADR" not in mandate, "mandate must not reference MADR (prior campaign C388)"
    assert "BANDX" not in mandate, "mandate must not reference BANDX (prior campaign C387)"
    assert "PRROUGH" not in mandate, "mandate must not reference PRROUGH (prior campaign C386)"
    assert "HALFRANGE" not in mandate, "mandate must not reference HALFRANGE (prior campaign C385)"


def test_placebo_seed_is_20261262():
    assert R.PLACEBO_SEED == 20261262


def test_placebo_seed_unique_not_reserved():
    """Rewrite guard: C398 placebo seed 20261262 must not collide with reserved
    seeds 20261224–20261261 used by prior campaigns."""
    assert not (20261224 <= R.PLACEBO_SEED <= 20261261), "placebo seed must be outside 20261224-20261261"


# ---------------------------------------------------------------- real artifacts schema (if present)
def _find_latest(prefix: str):
    files = sorted((ROOT / "reports").glob(f"campaign398_{prefix}_*.json"))
    files = [f for f in files if ".full." not in f.name]
    return files[-1] if files else None


def test_artifacts_if_present_have_required_flags():
    p = _find_latest("verdict")
    if p is None:
        return
    v = json.loads(p.read_text())
    assert v["campaign"] == 398
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
    assert sw["config"]["lmom_params"]["window_W"] == 256


def test_cache_meta_lmom_params_distinct():
    meta_path = ROOT / "data" / "cache" / "campaign398_lmom_5m.meta.json"
    if not meta_path.exists():
        return
    meta = json.loads(meta_path.read_text())
    assert meta["campaign"] == 398
    assert meta["source_campaign"] == 312
    assert "lmom_params" in meta
    assert meta["lmom_params"]["window_W"] == 256
    for other in ("specfm_params", "magnet_params", "ces_params", "vterm_params",
                  "ddrun_params", "semicov_params", "qspread_params", "rar_params",
                  "lvac_params", "hill_params", "rskek_params", "opte_params",
                  "qatm_params", "dsrv_params", "ker_params", "rqv_params",
                  "bpv_params", "rmad_params", "gmd_params", "rskrkt_params",
                  "tirv_params", "rlrv_params", "signrun_params", "acovk_params",
                  "pslope_params", "vovr_params", "curv_params", "tailmem_params",
                  "turningpt_params", "extpos_params", "prrough_params",
                  "halfrange_params", "bandx_params", "madr_params", "minrv_params",
                  "xcoex_params", "xskew3_params", "ou_params", "ou_halflife_params"):
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
    test_lmom_matches_brute_force()
    test_lmom_defined_after_window_nan_before()
    test_lmom_non_finite_return_propagates()
    test_lmom_params()
    test_lmom_constant_returns_edge_case()
    test_reference_config_matches_pre_registered_spec()
    test_phase_randomized_surrogate_same_marginal_deterministic()
    test_build_underlying_shapes_and_keys()
    test_build_scores_signals_lookbacks_causal()
    test_lmom_kernel_not_degenerate()
    test_artifact_campaign_is_398()
    test_mandate_contains_lmom()
    test_placebo_seed_is_20261262()
    test_placebo_seed_unique_not_reserved()
    test_artifacts_if_present_have_required_flags()
    test_cache_meta_lmom_params_distinct()
    print("All C398 LMOM runner tests passed")