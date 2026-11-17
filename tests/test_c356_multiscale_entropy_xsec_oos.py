"""Tests for C356 runner (scripts/run_c356_multiscale_entropy_xsec_oos.py): pure-function
tests on synthetic arrays (including a brute-force equality test for the vectorized
Multiscale Entropy kernel) plus schema/flag validation of emitted real-data artifacts.
No network, no fabricated market data."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import run_c356_multiscale_entropy_xsec_oos as R  # noqa: E402


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
    for pb in ("mse_slope_placebo", "mse_area_placebo"):
        assert pb in R.SIGNALS
    for real in ("mse_slope_dev", "mse_area_dev"):
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


# ---------------------------------------------------------------- multiscale entropy kernel
def test_mse_matches_brute_force():
    # The vectorized sliding-window MSE kernel MUST equal the brute-force
    # reference (per-window explicit coarse-graining over tau, per-scale np.mean,
    # explicit SampEn double loop over i,j with Chebyshev distance).
    rng = np.random.default_rng(5)
    for n in (200, 320, 500):
        r = rng.standard_normal(n) * 0.003
        fast = R.compute_mse_metrics(r)
        brute = R._mse_bruteforce(r, R.MSE_W)
        for key in ("mse_slope", "mse_area"):
            vf, vb = fast[key], brute[key]
            fin = np.isfinite(vf) & np.isfinite(vb)
            assert fin.sum() > 0, key
            assert np.array_equal(np.isnan(vf), np.isnan(vb)), key
            assert np.allclose(vf[fin], vb[fin], rtol=1e-9, atol=1e-9), key


def test_mse_defined_after_window_nan_before():
    rng = np.random.default_rng(1)
    r = rng.standard_normal(2000) * 0.001
    m = R.compute_mse_metrics(r)
    W = R.MSE_W
    for key in ("mse_slope", "mse_area"):
        assert np.isnan(m[key][:W]).all(), key
        fin_share = float(np.isfinite(m[key][W:]).mean())
        assert fin_share > 0.10, (key, fin_share)


def test_mse_nan_in_window_propagates():
    rng = np.random.default_rng(0)
    r = rng.standard_normal(600) * 0.001
    r[300] = np.nan
    W = R.MSE_W
    m = R.compute_mse_metrics(r)
    for key in ("mse_slope", "mse_area"):
        # windows covering the NaN bar must be NaN
        for t in range(300, 300 + W):
            assert np.isnan(m[key][t]), f"{key} t={t} should be NaN"
        # windows before the NaN: at least some finite (MSE needs >=3 finite scales,
        # stricter than single-scale SampEn)
        pre = m[key][W:300]
        assert float(np.isfinite(pre).mean()) > 0.05, key
        # windows after the NaN+W: at least some finite again
        post = m[key][300 + W:]
        assert float(np.isfinite(post).mean()) > 0.05, key


def test_mse_constant_series_all_nan():
    # constant returns -> std=0 -> NaN
    r = np.full(400, 0.25)
    m = R.compute_mse_metrics(r)
    for key in ("mse_slope", "mse_area"):
        assert not np.isfinite(m[key]).any(), key


def test_mse_single_window_matches_manual():
    # explicit manual computation for one window, sanity check mse_slope/mse_area
    rng = np.random.default_rng(9)
    # one series of length W+1: window i=0 -> t=W-1 (NaN, t<W), window i=1 -> t=W (valid)
    w2 = rng.standard_normal(R.MSE_W + 1) * 0.002
    win = w2[1:R.MSE_W + 1]  # trailing W returns ending at bar t=W
    # manual per-window MSE on this window
    sampen_per_tau = []
    valid_taus = []
    for tau in R.MSE_TAUS:
        N_tau = R.MSE_W // tau
        if N_tau < R.MSE_M + 1:
            continue
        y = np.array([win[k * tau:(k + 1) * tau].mean() for k in range(N_tau)])
        y_std = float(y.std())
        if not (y_std > 0 and np.isfinite(y_std)):
            continue
        z = (y - y.mean()) / y_std
        se = R._sampen_single_window(z, R.MSE_M, R.MSE_R)
        if np.isfinite(se):
            sampen_per_tau.append(se)
            valid_taus.append(tau)
    if len(sampen_per_tau) >= 3:
        x = np.log(np.array(valid_taus, dtype=float))
        yv = np.array(sampen_per_tau, dtype=float)
        x_mean = x.mean(); y_mean = yv.mean()
        sxx = float(((x - x_mean) ** 2).sum())
        sxy = float(((x - x_mean) * (yv - y_mean)).sum())
        expected_slope = sxy / sxx if sxx > 0 else float("nan")
        expected_area = 0.0
        for k in range(len(valid_taus) - 1):
            expected_area += (sampen_per_tau[k] + sampen_per_tau[k + 1]) / 2 * (valid_taus[k + 1] - valid_taus[k])
    else:
        expected_slope = float("nan")
        expected_area = float("nan")
    fast2 = R.compute_mse_metrics(w2)
    # bar t=W (index R.MSE_W) is the first valid bar (window i=1 of w2)
    for key, exp in (("mse_slope", expected_slope), ("mse_area", expected_area)):
        if np.isnan(exp):
            assert np.isnan(fast2[key][R.MSE_W]), key
        else:
            assert np.isclose(fast2[key][R.MSE_W], exp, rtol=1e-9, atol=1e-9), key


# ---------------------------------------------------------------- pre-registered spec constants
def test_reference_config_matches_pre_registered_spec():
    assert R.ATTR_REPRESENTATIVES == {"mse_slope_dev": "mse_slope_dev", "mse_area_dev": "mse_area_dev"}
    assert R.PLACEBO_SEED == 20261222
    assert R.STABILITY_MIN_SIGN_CONSISTENCY == 0.70
    assert R.STABILITY_MIN_SHARPE_CORR == 0.50
    assert R.DOMINANT_SHARE_MIN == 0.50
    assert R.TRAIN_M == 12 and R.TEST_M == 3 and R.ROLL_M == 3
    assert R.MSE_W == 64
    assert tuple(R.MSE_TAUS) == (1, 2, 4, 8, 16, 32)
    assert R.MSE_M == 2
    assert R.MSE_R == 0.25


# ---------------------------------------------------------------- phase-randomized surrogate
def test_phase_randomized_surrogate_same_marginal_deterministic():
    rng = np.random.default_rng(0)
    x = rng.standard_normal(500) * 3.0 + 5.0
    s1 = R._phase_randomized_surrogate(x, R.PLACEBO_SEED)
    s2 = R._phase_randomized_surrogate(x, R.PLACEBO_SEED)
    assert np.array_equal(s1, s2)
    assert np.isclose(np.sort(s1), np.sort(x), equal_nan=True).all()


# ---------------------------------------------------------------- build_underlying / build_scores
def _synthetic_bs(n_assets=3, n_days=8, seed=1):
    rng = np.random.default_rng(seed)
    T = R.TOD_BARS_PER_DAY
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
    assert set(series.keys()) == {"mse_slope", "mse_area"}
    for k in ("mse_slope", "mse_area"):
        assert series[k].shape == (bs["n_assets"], bs["n_bars"])


def test_build_scores_signals_lookbacks_causal():
    bs = _synthetic_bs()
    series = R.build_underlying(bs)
    scores = R.build_scores(series, bs["bucket"])
    for sig in R.SIGNALS:
        for L in R.LOOKBACKS:
            assert (sig, L) in scores
            assert scores[(sig, L)].shape == (bs["n_assets"], bs["n_bars"])
    # causal: first bar of every score series is NaN
    for key, sc in scores.items():
        assert np.isnan(sc[:, 0]).all(), key


# ---------------------------------------------------------------- real artifacts schema (if present)
def _find_latest(prefix: str):
    files = sorted((ROOT / "reports").glob(f"campaign356_{prefix}_*.json"))
    files = [f for f in files if ".full." not in f.name]
    return files[-1] if files else None


def test_artifacts_if_present_have_required_flags():
    p = _find_latest("verdict")
    if p is None:
        return
    v = json.loads(p.read_text())
    assert v["campaign"] == 356
    assert v["real_data_only"] is True and v["fabricated_data"] is False
    assert v["executed_fills"] is False
    assert v["verdict"] in ("EDGE_PROVEN", "RETRACTED")
    assert isinstance(v["edge_proven"], bool)
    for k in ("oos_sweep_sha256", "registry_sha256", "summary_sha256"):
        assert isinstance(v[k], str) and len(v[k]) == 64
    reg = json.loads((ROOT / v["registry_artifact"]).read_text())
    assert reg["real_data_only"] is True and reg["fabricated_data"] is False
    sw = json.loads((ROOT / v["oos_sweep_artifact"]).read_text())
    assert sw["real_data_only"] is True and sw["fabricated_data"] is False
    assert sw["config"]["placebo_seed"] == R.PLACEBO_SEED
    assert sw["config"]["mse_params"]["W"] == 64
    assert list(sw["config"]["mse_params"]["coarse_grain_scales"]) == [1, 2, 4, 8, 16, 32]
    n_total = int(sw["summary"]["n_total_runs"])
    if n_total > 0:  # full sweep artifact (smoke/partial runs report 0)
        assert n_total == R.N_TRIALS
        assert sw["config"]["n_trials"] == R.N_TRIALS


def test_cache_meta_mse_params_distinct():
    meta_path = ROOT / "data" / "cache" / "campaign356_multiscale_entropy_5m.meta.json"
    if not meta_path.exists():
        return
    meta = json.loads(meta_path.read_text())
    assert meta["campaign"] == 356
    assert meta["source_campaign"] == 312
    spp = meta["mse_params"]
    assert spp["window_W"] == 64
    assert list(spp["coarse_grain_scales"]) == [1, 2, 4, 8, 16, 32]
    assert spp["embedding_dimension_m"] == 2
    assert spp["tolerance_r"] == 0.25
