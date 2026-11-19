"""Tests for C393 runner (scripts/run_c393_vterm_xsec_oos.py): pure-function tests on
synthetic arrays (including a brute-force equality test for the vectorized VTERM
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

import run_c393_vterm_xsec_oos as R  # noqa: E402


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
    for pb in ("vterm_level_placebo", "vterm_ratio_placebo"):
        assert pb in R.SIGNALS
    for real in ("vterm_level_dev", "vterm_ratio_dev"):
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


# ---------------------------------------------------------------- VTERM metric (brute-force equality)
def test_vterm_matches_brute_force():
    """The vectorized vterm_level/vterm_ratio kernels MUST equal the brute-force
    reference (per-window front/back realized variance ratio). Compared strictly
    (maxdiff < 1e-12) with matching NaN patterns."""
    rng = np.random.default_rng(123)
    r = rng.standard_normal(900) * 0.001
    fast = R.compute_vterm_metrics(r, R.VTERM_W, R.VTERM_SPLIT, R.VTERM_EPS)
    brute = R._vterm_bruteforce(r, R.VTERM_W, R.VTERM_SPLIT, R.VTERM_EPS)
    for key in ("vterm_level", "vterm_ratio"):
        fv, fb = fast[key], brute[key]
        fin = np.isfinite(fv) & np.isfinite(fb)
        assert fin.sum() > 0, f"{key}: no finite overlapping points"
        assert np.array_equal(np.isnan(fv), np.isnan(fb)), f"{key}: NaN pattern mismatch"
    fs, bs_ = fast["vterm_level"], brute["vterm_level"]
    fin_s = np.isfinite(fs) & np.isfinite(bs_)
    maxdiff_s = float(np.max(np.abs(fs[fin_s] - bs_[fin_s]))) if fin_s.sum() else 0.0
    assert maxdiff_s < 1e-12, f"vterm_level: maxdiff={maxdiff_s} >= 1e-12"
    fc, bc = fast["vterm_ratio"], brute["vterm_ratio"]
    fin_c = np.isfinite(fc) & np.isfinite(bc)
    maxdiff_c = float(np.max(np.abs(fc[fin_c] - bc[fin_c]))) if fin_c.sum() else 0.0
    assert maxdiff_c < 1e-12, f"vterm_ratio: maxdiff={maxdiff_c} >= 1e-12"


def test_vterm_defined_after_window_nan_before():
    rng = np.random.default_rng(3)
    r = rng.standard_normal(2000) * 0.001
    m = R.compute_vterm_metrics(r, R.VTERM_W, R.VTERM_SPLIT, R.VTERM_EPS)
    W = R.VTERM_W
    for key in ("vterm_level", "vterm_ratio"):
        assert np.isnan(m[key][:W]).all(), key
        assert np.isfinite(m[key][W:]).all(), key


def test_vterm_non_finite_return_propagates():
    """A non-finite return in the window -> NaN for all VTERM outputs."""
    rng = np.random.default_rng(9)
    r = rng.standard_normal(600) * 0.001
    r[300] = np.inf
    W = R.VTERM_W
    m = R.compute_vterm_metrics(r, W, R.VTERM_SPLIT, R.VTERM_EPS)
    # r[300]=inf affects bars t where 300 in [t-W, t) => t in (300, 300+W]
    for t in range(301, min(301 + W, 600)):
        assert np.isnan(m["vterm_level"][t]), f"vterm_level t={t} should be NaN"
        assert np.isnan(m["vterm_ratio"][t]), f"vterm_ratio t={t} should be NaN"
    for t in range(W, 300):
        assert np.isfinite(m["vterm_level"][t])
        assert np.isfinite(m["vterm_ratio"][t])
    for t in range(300 + W + 1, 600):
        assert np.isfinite(m["vterm_level"][t])
        assert np.isfinite(m["vterm_ratio"][t])


def test_vterm_flat_window_nan():
    """A flat return window -> NaN for vterm_ratio (rv_front+rv_back=0 -> denom<=eps)."""
    r = np.zeros(600)
    W = R.VTERM_W
    m = R.compute_vterm_metrics(r, W, R.VTERM_SPLIT, R.VTERM_EPS)
    for t in range(W, 600):
        assert np.isnan(m["vterm_ratio"][t]), f"vterm_ratio t={t} flat window NaN"


def test_vterm_params():
    assert R.VTERM_W == 256
    assert R.VTERM_SPLIT == 128
    assert R.VTERM_EPS == 1e-12


def test_reference_config_matches_pre_registered_spec():
    assert R.ATTR_REPRESENTATIVES == {
        "vterm_level_dev": "vterm_level_dev",
        "vterm_ratio_dev": "vterm_ratio_dev",
    }
    assert R.PLACEBO_SEED == 20261257
    assert R.STABILITY_MIN_SIGN_CONSISTENCY == 0.70
    assert R.STABILITY_MIN_SHARPE_CORR == 0.50
    assert R.DOMINANT_SHARE_MIN == 0.50
    assert R.TRAIN_M == 12 and R.TEST_M == 3 and R.ROLL_M == 3
    assert R.VTERM_W == 256
    assert R.SIGNALS[0] == "vterm_level_dev"


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
    assert set(series.keys()) == {"vterm_level", "vterm_ratio"}
    for k in ("vterm_level", "vterm_ratio"):
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
def test_vterm_kernel_distinct_from_rv_and_degenerate_ratio():
    """Rewrite guard: VTERM metrics are not clones of RV and vterm_ratio is not
    degenerate (not allclose to 0 or 1 where defined)."""
    rng = np.random.default_rng(55)
    r = rng.standard_normal(800) * 0.001
    W = R.VTERM_W
    mm = R.compute_vterm_metrics(r, W, R.VTERM_SPLIT, R.VTERM_EPS)
    vterm_level = mm["vterm_level"]
    vterm_ratio = mm["vterm_ratio"]
    # recompute rv aligned to bars t>=W over returns r[t-W:t]
    wv = sliding_window_view(r, W)[:, :]  # (n-W+1, W), window j = r[j:j+W], bar t=j+W
    rv = (wv * wv).sum(axis=1)                       # length n-W+1, aligned to bars t>=W
    # align: rv[j] -> bar t=j+W
    level_valid = vterm_level[W:]
    ratio_valid = vterm_ratio[W:]
    rv_aligned = rv[1:len(level_valid) + 1]  # rv[j] for j=1.. corresponds to bar W+1..; skip j=0 (bar W)
    # simpler: compare at overlapping finite points
    fin = np.isfinite(level_valid) & np.isfinite(ratio_valid)
    # rv aligned to same bars: bar t -> rv[t-W] (window r[t-W:t])
    rv_for_bars = rv[:len(level_valid)]  # rv[j] -> bar j+W, so rv[0]->bar W, rv[1]->bar W+1...
    fin2 = fin & np.isfinite(rv_for_bars)
    assert fin2.sum() > 0
    assert not np.allclose(level_valid[fin2], rv_for_bars[fin2], atol=1e-12), "vterm_level collapses to rv"
    assert not np.allclose(ratio_valid[fin2], 0.0, atol=1e-12), "vterm_ratio collapses to 0"
    assert not np.allclose(ratio_valid[fin2], 1.0, atol=1e-12), "vterm_ratio collapses to 1.0"


# ---------------------------------------------------------------- guard tests (rewrite guards)
def test_artifact_campaign_is_393():
    """Rewrite guard: every emitted artifact self-identifies campaign 393 (never 388/390/391/392)."""
    for part in ("verdict", "summary", "registry", "oos_sweep"):
        files = sorted((ROOT / "reports").glob(f"campaign393_{part}_*.json"))
        files = [f for f in files if ".full." not in f.name]
        if not files:
            continue
        obj = json.loads(files[-1].read_text())
        assert obj["campaign"] == 393, f"{part} artifact campaign != 393: {obj.get('campaign')}"


def test_mandate_contains_vterm_and_term_structure():
    """Rewrite guard: the C393 mandate names VTERM and term structure
    (never DDRUN/semicov/xcoex/xskew3/ddrun)."""
    p = sorted((ROOT / "reports").glob("campaign393_oos_sweep_*.json"))
    p = [f for f in p if ".full." not in f.name]
    if not p:
        return
    mandate = json.loads(p[-1].read_text())["mandate"]
    assert "VTERM" in mandate, "mandate missing VTERM"
    assert "term structure" in mandate.lower(), "mandate missing term structure"
    assert "front" in mandate.lower(), "mandate missing front"
    assert "back" in mandate.lower(), "mandate missing back"
    assert "DDRUN" not in mandate, "mandate must not reference DDRUN"
    assert "semicov" not in mandate.lower(), "mandate must not reference semicov"
    assert "XCOEX" not in mandate, "mandate must not reference XCOEX"
    assert "XSKEW3" not in mandate, "mandate must not reference XSKEW3"


def test_placebo_seed_is_20261257():
    assert R.PLACEBO_SEED == 20261257


# ---------------------------------------------------------------- real artifacts schema (if present)
def _find_latest(prefix: str):
    files = sorted((ROOT / "reports").glob(f"campaign393_{prefix}_*.json"))
    files = [f for f in files if ".full." not in f.name]
    return files[-1] if files else None


def test_artifacts_if_present_have_required_flags():
    p = _find_latest("verdict")
    if p is None:
        return
    v = json.loads(p.read_text())
    assert v["campaign"] == 393
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
    assert sw["config"]["vterm_params"]["window_W"] == 256
    assert sw["config"]["vterm_params"]["eps"] == 1e-12


def test_cache_meta_vterm_params_distinct():
    meta_path = ROOT / "data" / "cache" / "campaign393_vterm_5m.meta.json"
    if not meta_path.exists():
        return
    meta = json.loads(meta_path.read_text())
    assert meta["campaign"] == 393
    assert meta["source_campaign"] == 312
    assert "vterm_params" in meta
    assert meta["vterm_params"]["window_W"] == 256
    assert meta["vterm_params"]["split"] == 128
    assert meta["vterm_params"]["eps"] == 1e-12
    for other in ("ddrun_params", "semicov_params", "qspread_params", "rar_params", "lvac_params",
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
    test_vterm_matches_brute_force()
    test_vterm_defined_after_window_nan_before()
    test_vterm_non_finite_return_propagates()
    test_vterm_flat_window_nan()
    test_vterm_params()
    test_reference_config_matches_pre_registered_spec()
    test_phase_randomized_surrogate_same_marginal_deterministic()
    test_build_underlying_shapes_and_keys()
    test_build_scores_signals_lookbacks_causal()
    test_vterm_kernel_distinct_from_rv_and_degenerate_ratio()
    test_artifact_campaign_is_393()
    test_mandate_contains_vterm_and_term_structure()
    test_placebo_seed_is_20261257()
    test_artifacts_if_present_have_required_flags()
    test_cache_meta_vterm_params_distinct()
    print("All C393 runner tests passed")
