"""Tests for C400 runner (scripts/run_c400_ktrend_xsec_oos.py): pure-function tests on
synthetic arrays (including a brute-force equality test for the vectorized KTREND
Kendall tau / Spearman rho kernels vs the per-window reference) plus schema/flag
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

import run_c400_ktrend_xsec_oos as R  # noqa: E402


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
    for pb in ("ktrend_tau_placebo", "ktrend_rho_placebo"):
        assert pb in R.SIGNALS
    for real in ("ktrend_tau_dev", "ktrend_rho_dev"):
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


# ---------------------------------------------------------------- KTREND metric (brute-force equality)
def test_ktrend_matches_brute_force():
    """The vectorized KTREND Kendall tau / Spearman rho kernels MUST equal the
    brute-force reference (per-window scipy.stats.kendalltau/spearmanr against
    bar index 1..W). Compared strictly (maxdiff < 1e-12) with matching NaN patterns."""
    rng = np.random.default_rng(20261264)
    log_return = rng.standard_normal(4000) * 0.001
    fast = R.compute_ktrend_metrics(log_return, R.KTREND_W)
    brute = R._ktrend_bruteforce(log_return, R.KTREND_W)
    for key in ("ktrend_tau", "ktrend_rho"):
        fv, fb = fast[key], brute[key]
        fin = np.isfinite(fv) & np.isfinite(fb)
        assert fin.sum() > 0, f"{key}: no finite overlapping points"
        assert np.array_equal(np.isnan(fv), np.isnan(fb)), f"{key}: NaN pattern mismatch"
        maxdiff = float(np.max(np.abs(fv[fin] - fb[fin]))) if fin.sum() else 0.0
        assert maxdiff < 1e-12, f"{key}: maxdiff={maxdiff} >= 1e-12"


def test_ktrend_perfect_monotonic_trend():
    """A perfect monotonic trend yields tau/rho = +/-1 (KTREND detects ordinal
    concordance), showing the kernel is a genuine rank-based trend detector."""
    W = R.KTREND_W
    inc = np.arange(1, W + 1, dtype=float)
    dec = inc[::-1]
    m_inc = R.compute_ktrend_metrics(np.concatenate([np.zeros(W - 1), inc]), W)
    m_dec = R.compute_ktrend_metrics(np.concatenate([np.zeros(W - 1), dec]), W)
    assert np.isclose(m_inc["ktrend_tau"][W - 1], 1.0, atol=1e-12)
    assert np.isclose(m_inc["ktrend_rho"][W - 1], 1.0, atol=1e-12)
    assert np.isclose(m_dec["ktrend_tau"][W - 1], -1.0, atol=1e-12)
    assert np.isclose(m_dec["ktrend_rho"][W - 1], -1.0, atol=1e-12)


def test_ktrend_defined_after_window_nan_before():
    rng = np.random.default_rng(3)
    log_return = rng.standard_normal(4000) * 0.001
    m = R.compute_ktrend_metrics(log_return, R.KTREND_W)
    W = R.KTREND_W
    for key in ("ktrend_tau", "ktrend_rho"):
        assert np.isnan(m[key][:W]).all(), key
        assert np.isfinite(m[key][W:]).any(), key


def test_ktrend_non_finite_return_propagates():
    """A non-finite return in the window -> NaN for all KTREND outputs in affected bars."""
    rng = np.random.default_rng(9)
    log_return = rng.standard_normal(600) * 0.001
    log_return[300] = np.inf
    W = R.KTREND_W
    m = R.compute_ktrend_metrics(log_return, W)
    for t in range(300, min(300 + W, 600)):
        assert np.isnan(m["ktrend_tau"][t]), f"ktrend_tau t={t} should be NaN"
        assert np.isnan(m["ktrend_rho"][t]), f"ktrend_rho t={t} should be NaN"
    for t in range(W, 300):
        assert np.isfinite(m["ktrend_tau"][t]), f"ktrend_tau t={t} should be finite"
    for t in range(300 + W, 600):
        assert np.isfinite(m["ktrend_tau"][t]), f"ktrend_tau t={t} should be finite"


def test_ktrend_params():
    assert R.KTREND_W == 256


def test_ktrend_constant_returns_edge_case():
    """Constant returns -> sigma=0 -> NaN (matches brute force)."""
    log_return = np.ones(600) * 0.001
    fast = R.compute_ktrend_metrics(log_return, R.KTREND_W)
    brute = R._ktrend_bruteforce(log_return, R.KTREND_W)
    for key in ("ktrend_tau", "ktrend_rho"):
        fv, fb = fast[key], brute[key]
        assert np.array_equal(np.isnan(fv), np.isnan(fb)), key
        fin = np.isfinite(fv) & np.isfinite(fb)
        maxdiff = float(np.max(np.abs(fv[fin] - fb[fin]))) if fin.sum() else 0.0
        assert maxdiff < 1e-12, f"{key}: maxdiff={maxdiff} >= 1e-12"


def test_reference_config_matches_pre_registered_spec():
    assert R.ATTR_REPRESENTATIVES == {
        "ktrend_tau_dev": "ktrend_tau_dev",
        "ktrend_rho_dev": "ktrend_rho_dev",
    }
    assert R.PLACEBO_SEED == 20261264
    assert R.STABILITY_MIN_SIGN_CONSISTENCY == 0.70
    assert R.STABILITY_MIN_SHARPE_CORR == 0.50
    assert R.DOMINANT_SHARE_MIN == 0.50
    assert R.TRAIN_M == 12 and R.TEST_M == 3 and R.ROLL_M == 3
    assert R.KTREND_W == 256
    assert R.SIGNALS[0] == "ktrend_tau_dev"


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
    assert set(series.keys()) == {"ktrend_tau", "ktrend_rho"}
    for k in ("ktrend_tau", "ktrend_rho"):
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
def test_ktrend_kernel_not_degenerate():
    """Rewrite guard: KTREND metrics are not degenerate (not allclose to 0 where defined)."""
    rng = np.random.default_rng(55)
    log_return = rng.standard_normal(1600) * 0.001
    W = R.KTREND_W
    mm = R.compute_ktrend_metrics(log_return, W)
    tau = mm["ktrend_tau"]
    rho = mm["ktrend_rho"]
    tau_valid = tau[W:]
    rho_valid = rho[W:]
    fin = np.isfinite(tau_valid) & np.isfinite(rho_valid)
    assert fin.sum() > 0
    assert not np.allclose(tau_valid[fin], 0.0, atol=1e-12), "Kendall tau collapses to 0"
    assert not np.allclose(rho_valid[fin], 0.0, atol=1e-12), "Spearman rho collapses to 0"


def test_ktrend_kernel_distinct_from_cbreak():
    """Rewrite guard: KTREND tau/rho is a different object from a CBREAK-style
    CUSUM-break statistic on the same random data (different kernels -> different values)."""
    rng = np.random.default_rng(123)
    log_return = rng.standard_normal(1200) * 0.001
    W = R.KTREND_W
    mm = R.compute_ktrend_metrics(log_return, W)
    # inline CBREAK CUSUM stat for distinctness comparison
    X = log_return
    n = len(X)
    cbreak_stat = np.full(n, np.nan)
    for t in range(W, n):
        Xw = X[t - W + 1:t + 1]
        if not np.isfinite(Xw).all():
            continue
        m = float(np.mean(Xw))
        s = float(np.std(Xw, ddof=0))
        if not np.isfinite(s) or s <= 0:
            continue
        S = np.cumsum(Xw - m)
        cbreak_stat[t] = float(np.max(np.abs(S))) / (s * np.sqrt(W))
    tau = mm["ktrend_tau"][W:]
    cb = cbreak_stat[W:]
    fin = np.isfinite(tau) & np.isfinite(cb)
    assert fin.sum() > 0
    assert not np.allclose(tau[fin], cb[fin], atol=1e-6), "KTREND tau degenerates to CBREAK stat"


# ---------------------------------------------------------------- guard tests (rewrite guards)
def test_artifact_campaign_is_400():
    """Rewrite guard: every emitted artifact self-identifies campaign 400 (never 399/400)."""
    for part in ("verdict", "summary", "registry", "oos_sweep"):
        files = sorted((ROOT / "reports").glob(f"campaign400_{part}_*.json"))
        files = [f for f in files if ".full." not in f.name]
        if not files:
            continue
        obj = json.loads(files[-1].read_text())
        assert obj["campaign"] == 400, f"{part} artifact campaign != 400: {obj.get('campaign')}"


def test_mandate_contains_ktrend():
    """Rewrite guard: the C400 mandate names KTREND Kendall tau / Spearman rho
    (never CBREAK/SPECFM/MAGNET/OUHALFLIFE/CTES/VTERM/DDRUN/XSKEW3/XCOEX/MINRV/MADR/BANDX/PRROUGH/HALFRANGE)."""
    p = sorted((ROOT / "reports").glob("campaign400_oos_sweep_*.json"))
    p = [f for f in p if ".full." not in f.name]
    if not p:
        return
    mandate = json.loads(p[-1].read_text())["mandate"]
    assert "KTREND" in mandate, "mandate missing KTREND"
    assert "KENDALL" in mandate, "mandate missing KENDALL"
    assert "SPEARMAN" in mandate, "mandate missing SPEARMAN"
    for bad in ("CBREAK", "SPECFM", "MAGNET", "OUHALFLIFE", "CTES", "VTERM",
                "DDRUN", "XSKEW3", "XCOEX", "MINRV", "MADR", "BANDX",
                "PRROUGH", "HALFRANGE", "LMOM"):
        assert bad not in mandate, f"mandate must not reference {bad} (prior campaign)"


def test_placebo_seed_is_20261264():
    assert R.PLACEBO_SEED == 20261264


def test_placebo_seed_unique_not_reserved():
    """Rewrite guard: C400 placebo seed 20261264 must not collide with reserved
    seeds 20261224–20261263 used by prior campaigns."""
    assert not (20261224 <= R.PLACEBO_SEED <= 20261263), "placebo seed must be outside 20261224-20261263"


# ---------------------------------------------------------------- real artifacts schema (if present)
def _find_latest(prefix: str):
    files = sorted((ROOT / "reports").glob(f"campaign400_{prefix}_*.json"))
    files = [f for f in files if ".full." not in f.name]
    return files[-1] if files else None


def test_artifacts_if_present_have_required_flags():
    p = _find_latest("verdict")
    if p is None:
        return
    v = json.loads(p.read_text())
    assert v["campaign"] == 400
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
    assert sw["config"]["ktrend_params"]["window_W"] == 256


def test_cache_meta_ktrend_params_distinct():
    meta_path = ROOT / "data" / "cache" / "campaign400_ktrend_5m.meta.json"
    if not meta_path.exists():
        return
    meta = json.loads(meta_path.read_text())
    assert meta["campaign"] == 400
    assert meta["source_campaign"] == 312
    assert "ktrend_params" in meta
    assert meta["ktrend_params"]["window_W"] == 256
    for other in ("cbreak_params", "specfm_params", "magnet_params", "ces_params",
                  "vterm_params", "ddrun_params", "semicov_params", "qspread_params",
                  "rar_params", "lvac_params", "hill_params", "rskek_params",
                  "opte_params", "qatm_params", "dsrv_params", "ker_params",
                  "rqv_params", "bpv_params", "rmad_params", "gmd_params",
                  "rskrkt_params", "tirv_params", "rlrv_params", "signrun_params",
                  "acovk_params", "pslope_params", "vovr_params", "curv_params",
                  "tailmem_params", "turningpt_params", "extpos_params",
                  "prrough_params", "halfrange_params", "bandx_params",
                  "madr_params", "minrv_params", "xcoex_params", "xskew3_params",
                  "ou_params", "ou_halflife_params", "lmom_params"):
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
    test_ktrend_matches_brute_force()
    test_ktrend_perfect_monotonic_trend()
    test_ktrend_defined_after_window_nan_before()
    test_ktrend_non_finite_return_propagates()
    test_ktrend_params()
    test_ktrend_constant_returns_edge_case()
    test_reference_config_matches_pre_registered_spec()
    test_phase_randomized_surrogate_same_marginal_deterministic()
    test_build_underlying_shapes_and_keys()
    test_build_scores_signals_lookbacks_causal()
    test_ktrend_kernel_not_degenerate()
    test_ktrend_kernel_distinct_from_cbreak()
    test_artifact_campaign_is_400()
    test_mandate_contains_ktrend()
    test_placebo_seed_is_20261264()
    test_placebo_seed_unique_not_reserved()
    test_artifacts_if_present_have_required_flags()
    test_cache_meta_ktrend_params_distinct()
    print("All C400 KTREND runner tests passed")
