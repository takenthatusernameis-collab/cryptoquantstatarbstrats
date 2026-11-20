"""Tests for C404 runner (scripts/run_c404_domfreq_xsec_oos.py): pure-function tests
on synthetic arrays (including a brute-force equality test for the vectorized DOMFREQ
dominant-spectral-frequency / spectral-centroid kernel vs the per-window reference)
plus schema/flag validation of emitted real-data artifacts. No network, no fabricated
market data."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import run_c404_domfreq_xsec_oos as R  # noqa: E402


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
    for pb in ("dom_period_placebo", "spec_centroid_placebo"):
        assert pb in R.SIGNALS
    for real in ("dom_period_dev", "spec_centroid_dev"):
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


# ---------------------------------------------------------------- DOMFREQ metric (brute-force equality)
def test_domfreq_matches_brute_force():
    """The vectorized DOMFREQ dominant-spectral-frequency kernel MUST equal the
    brute-force reference (per-window detrended rfft argmax + spectral centroid).
    Compared with maxdiff < 1e-9 (FFT round-off) with matching NaN patterns."""
    rng = np.random.default_rng(20261268)
    log_return = rng.standard_normal(4000) * 0.001
    fast = R.compute_domfreq_metrics(log_return, R.DOMFREQ_W)
    brute = R._domfreq_bruteforce(log_return, R.DOMFREQ_W)
    for key in ("dom_period", "spec_centroid"):
        fv, fb = fast[key], brute[key]
        fin = np.isfinite(fv) & np.isfinite(fb)
        assert fin.sum() > 0, f"{key}: no finite overlapping points"
        assert np.array_equal(np.isnan(fv), np.isnan(fb)), f"{key}: NaN pattern mismatch"
        maxdiff = float(np.max(np.abs(fv[fin] - fb[fin]))) if fin.sum() else 0.0
        assert maxdiff < 1e-9, f"{key}: maxdiff={maxdiff} >= 1e-9"


def test_domfreq_defined_after_window_nan_before():
    rng = np.random.default_rng(3)
    log_return = rng.standard_normal(4000) * 0.001
    m = R.compute_domfreq_metrics(log_return, R.DOMFREQ_W)
    W = R.DOMFREQ_W
    for key in ("dom_period", "spec_centroid"):
        assert np.isnan(m[key][:W]).all(), key
        assert np.isfinite(m[key][W:]).any(), key


def test_domfreq_non_finite_return_propagates():
    """A non-finite return in the window -> NaN for all DOMFREQ outputs in affected bars."""
    rng = np.random.default_rng(9)
    log_return = rng.standard_normal(600) * 0.001
    log_return[300] = np.inf
    W = R.DOMFREQ_W
    m = R.compute_domfreq_metrics(log_return, W)
    for t in range(300, min(300 + W, 600)):
        assert np.isnan(m["dom_period"][t]), f"dom_period t={t} should be NaN"
        assert np.isnan(m["spec_centroid"][t]), f"spec_centroid t={t} should be NaN"
    for t in range(W, 300):
        assert np.isfinite(m["dom_period"][t]), f"dom_period t={t} should be finite"
    for t in range(300 + W, 600):
        assert np.isfinite(m["dom_period"][t]), f"dom_period t={t} should be finite"


def test_domfreq_params():
    assert R.DOMFREQ_W == 256


def test_reference_config_matches_pre_registered_spec():
    assert R.ATTR_REPRESENTATIVES == {
        "dom_period_dev": "dom_period_dev",
        "spec_centroid_dev": "spec_centroid_dev",
    }
    assert R.PLACEBO_SEED == 20261268
    assert R.STABILITY_MIN_SIGN_CONSISTENCY == 0.70
    assert R.STABILITY_MIN_SHARPE_CORR == 0.50
    assert R.DOMINANT_SHARE_MIN == 0.50
    assert R.TRAIN_M == 12 and R.TEST_M == 3 and R.ROLL_M == 3
    assert R.DOMFREQ_W == 256
    assert R.SIGNALS[0] == "dom_period_dev"


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
    assert set(series.keys()) == {"dom_period", "spec_centroid"}
    for k in ("dom_period", "spec_centroid"):
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
def test_domfreq_kernel_not_degenerate():
    """Rewrite guard: DOMFREQ metrics are not degenerate (not allclose to 0 where defined)."""
    rng = np.random.default_rng(55)
    log_return = rng.standard_normal(1600) * 0.001
    W = R.DOMFREQ_W
    mm = R.compute_domfreq_metrics(log_return, W)
    dp = mm["dom_period"]
    sc = mm["spec_centroid"]
    fin = np.isfinite(dp) & np.isfinite(sc)
    assert fin.sum() > 0
    for name, arr in (("dom_period", dp), ("spec_centroid", sc)):
        valid = arr[fin]
        assert not np.allclose(valid, 0.0, atol=1e-12), f"{name} collapses to 0"


def _specfm_style_stat(X, W):
    """Inline C397 SPECFM spectral flatness = geometric_mean(P)/arithmetic_mean(P)
    on the detrended trailing window (no peak location, no centroid)."""
    n = len(X)
    out = np.full(n, np.nan)
    for t in range(W, n):
        Xw = X[t - W + 1:t + 1]
        if not np.isfinite(Xw).all():
            continue
        Y = Xw - Xw.mean()
        F = np.fft.rfft(Y)
        P = np.abs(F[1:]) ** 2          # DC excluded
        s = float(P.sum())
        if s <= 0 or not np.isfinite(s):
            continue
        p = P / s
        nz = p > 0
        gm = float(np.exp(np.mean(np.log(p[nz]))))
        am = float(np.mean(p))
        out[t] = gm / am if am > 0 else np.nan
    return out


def _vovr_style_stat(X, W):
    """Inline C378 VOVR: cross-sub-block RV dispersion = std(block_RV)/mean(block_RV)
    over 16 non-overlapping 16-bar blocks."""
    n = len(X)
    out = np.full(n, np.nan)
    n_blocks = 16
    block_len = W // n_blocks
    for t in range(W, n):
        Xw = X[t - W + 1:t + 1]
        if not np.isfinite(Xw).all():
            continue
        rv_blocks = []
        for b in range(n_blocks):
            seg = Xw[b * block_len:(b + 1) * block_len]
            rv_blocks.append(float(np.sum(seg ** 2)))
        rv_blocks = np.array(rv_blocks, dtype=float)
        mean_rv = float(rv_blocks.mean())
        if mean_rv <= 0 or not np.isfinite(mean_rv):
            continue
        out[t] = float(rv_blocks.std()) / mean_rv
    return out


def test_domfreq_kernel_distinct_from_specfm():
    """Rewrite guard: DOMFREQ dom_period is a different object from C397 SPECFM
    spectral flatness (no peak location, no centroid)."""
    rng = np.random.default_rng(123)
    log_return = rng.standard_normal(1200) * 0.001
    W = R.DOMFREQ_W
    mm = R.compute_domfreq_metrics(log_return, W)
    dp = mm["dom_period"][W:]
    specfm = _specfm_style_stat(log_return, W)[W:]
    fin = np.isfinite(dp) & np.isfinite(specfm)
    assert fin.sum() > 0
    assert not np.allclose(dp[fin], specfm[fin], atol=1e-6), "DOMFREQ degenerates to SPECFM"


def test_domfreq_centroid_distinct_from_specfm():
    """Rewrite guard: spec_centroid is also distinct from C397 SPECFM flatness."""
    rng = np.random.default_rng(124)
    log_return = rng.standard_normal(1200) * 0.001
    W = R.DOMFREQ_W
    mm = R.compute_domfreq_metrics(log_return, W)
    sc = mm["spec_centroid"][W:]
    specfm = _specfm_style_stat(log_return, W)[W:]
    fin = np.isfinite(sc) & np.isfinite(specfm)
    assert fin.sum() > 0
    assert not np.allclose(sc[fin], specfm[fin], atol=1e-6), "spec_centroid degenerates to SPECFM"


def test_domfreq_kernel_distinct_from_vovr():
    """Rewrite guard: DOMFREQ dom_period is a different object from C378 VOVR
    cross-sub-block RV dispersion."""
    rng = np.random.default_rng(125)
    log_return = rng.standard_normal(1200) * 0.001
    W = R.DOMFREQ_W
    mm = R.compute_domfreq_metrics(log_return, W)
    dp = mm["dom_period"][W:]
    vovr = _vovr_style_stat(log_return, W)[W:]
    fin = np.isfinite(dp) & np.isfinite(vovr)
    assert fin.sum() > 0
    assert not np.allclose(dp[fin], vovr[fin], atol=1e-6), "DOMFREQ degenerates to VOVR"


# ---------------------------------------------------------------- guard tests (rewrite guards)
def test_artifact_campaign_is_404():
    """Rewrite guard: every emitted artifact self-identifies campaign 404."""
    for part in ("verdict", "summary", "registry", "oos_sweep"):
        files = sorted((ROOT / "reports").glob(f"campaign404_{part}_*.json"))
        files = [f for f in files if ".full." not in f.name]
        if not files:
            continue
        obj = json.loads(files[-1].read_text())
        assert obj["campaign"] == 404, f"{part} artifact campaign != 404: {obj.get('campaign')}"


def test_mandate_contains_domfreq():
    """Rewrite guard: the C404 mandate names DOMFREQ dominant spectral frequency
    (never ASYMCURV/SKEW/TSCALE/HILL/RVQUART/KTREND/CBREAK/SPECFM/MAGNET/
    OUHALFLIFE/CTES/VTERM/DDRUN/XSKEW3/XCOEX/MINRV/MADR/BANDX/PRROUGH/
    HALFRANGE/LMOM/SEMICOV/VOVR)."""
    p = sorted((ROOT / "reports").glob("campaign404_oos_sweep_*.json"))
    p = [f for f in p if ".full." not in f.name]
    if not p:
        return
    mandate = json.loads(p[-1].read_text())["mandate"]
    assert "DOMFREQ" in mandate, "mandate missing DOMFREQ"
    assert "DOMINANT" in mandate, "mandate missing DOMINANT"
    assert "SPECTRAL" in mandate, "mandate missing SPECTRAL"
    for bad in ("ASYMCURV", "SKEW", "TSCALE", "HILL", "RVQUART", "QUARTICITY", "KTREND",
                "CBREAK", "SPECFM", "MAGNET", "OUHALFLIFE", "CTES", "VTERM", "DDRUN",
                "XSKEW3", "XCOEX", "MINRV", "MADR", "BANDX", "PRROUGH", "HALFRANGE",
                "LMOM", "KENDALL", "SPEARMAN", "SEMICOV", "VOVR"):
        assert bad not in mandate, f"mandate must not reference {bad} (prior campaign)"


def test_placebo_seed_is_20261268():
    assert R.PLACEBO_SEED == 20261268


def test_placebo_seed_unique_not_reserved():
    """Rewrite guard: C404 placebo seed 20261268 must not collide with reserved
    seeds 20261224–20261267 used by prior campaigns (20261267 = C403)."""
    assert not (20261224 <= R.PLACEBO_SEED <= 20261267), "placebo seed must be outside 20261224-20261267"


# ---------------------------------------------------------------- real artifacts schema (if present)
def _find_latest(prefix: str):
    files = sorted((ROOT / "reports").glob(f"campaign404_{prefix}_*.json"))
    files = [f for f in files if ".full." not in f.name]
    return files[-1] if files else None


def test_artifacts_if_present_have_required_flags():
    p = _find_latest("verdict")
    if p is None:
        return
    v = json.loads(p.read_text())
    assert v["campaign"] == 404
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
    assert sw["config"]["domfreq_params"]["window_W"] == 256


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
    test_domfreq_matches_brute_force()
    test_domfreq_defined_after_window_nan_before()
    test_domfreq_non_finite_return_propagates()
    test_domfreq_params()
    test_reference_config_matches_pre_registered_spec()
    test_phase_randomized_surrogate_same_marginal_deterministic()
    test_build_underlying_shapes_and_keys()
    test_build_scores_signals_lookbacks_causal()
    test_domfreq_kernel_not_degenerate()
    test_domfreq_kernel_distinct_from_specfm()
    test_domfreq_centroid_distinct_from_specfm()
    test_domfreq_kernel_distinct_from_vovr()
    test_artifact_campaign_is_404()
    test_mandate_contains_domfreq()
    test_placebo_seed_is_20261268()
    test_placebo_seed_unique_not_reserved()
    test_artifacts_if_present_have_required_flags()
    print("All C404 DOMFREQ runner tests passed")