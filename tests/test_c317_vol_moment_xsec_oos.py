"""Tests for C317 runner (scripts/run_c317_vol_moment_xsec_oos.py): the costed
out-of-sample cross-sectional REALIZED-VOLATILITY / HIGHER-MOMENT stat-arb over
1440 pre-registered configs on real USDT-M linear 5m perps.

These tests never fetch or fabricate market data. They exercise the runner's pure
functions on synthetic arrays (multiple-testing correction, single-leg cost model,
causal dollar-neutral cross-sectional positions, month-aligned walk-forward
splits, nan-aware trailing mean/max, and the five volatility/higher-moment signal
builders), and they validate the schema and flags of the emitted real-data
artifacts (verdict, registry, summary, binding constraint, sweep) produced by the
full run.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import run_c317_vol_moment_xsec_oos as R  # noqa: E402


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


# ---------------------------------------------------------------- single-leg costs
def test_cost_rate_symmetric_and_perp_heavy():
    assert R.cost_rate_bps(10, 5, "symmetric") == 15.0
    assert R.cost_rate_bps(10, 5, "perp_heavy") == 20.0
    for fee in R.FEES:
        for slip in R.SLIPS:
            assert R.cost_rate_bps(fee, slip, "perp_heavy") >= R.cost_rate_bps(fee, slip, "symmetric")


def test_cost_grid_is_real_and_nonzero():
    assert min(R.FEES) >= 1 and max(R.FEES) == 20
    assert min(R.SLIPS) >= 1 and max(R.SLIPS) == 10
    for fee in R.FEES:
        for slip in R.SLIPS:
            for cv in R.COST_VARIANTS:
                assert R.cost_rate_bps(fee, slip, cv) > 0


# ---------------------------------------------------------------- positions
def _score_matrix():
    return np.array([
        [0.9, 0.9, 0.1, 0.1, 0.9, 0.1],
        [0.8, 0.8, 0.2, 0.2, 0.8, 0.2],
        [-0.8, -0.8, -0.2, -0.2, -0.8, -0.2],
        [-0.9, -0.9, -0.1, -0.1, -0.9, -0.1],
    ])


def test_positions_dollar_neutral_and_causal():
    pos = R.xsec_positions(_score_matrix(), 0.25, 1)
    assert pos.shape == (4, 6)
    assert np.allclose(pos.sum(axis=0), 0.0)
    assert np.all(pos[:, 0] == 0.0)
    assert pos[0, 2] > 0 and pos[3, 2] < 0


def test_positions_hold_reduces_turnover():
    score = np.tile(np.array([[0.9], [0.8], [-0.8], [-0.9]]), (1, 12))
    pos1 = R.xsec_positions(score, 0.25, 1)
    pos6 = R.xsec_positions(score, 0.25, 6)
    turn1 = np.abs(np.diff(pos1, axis=1)).sum()
    turn6 = np.abs(np.diff(pos6, axis=1)).sum()
    assert turn6 <= turn1


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


# ---------------------------------------------------------------- trailing ops
def test_trailing_nanmean_warmup_nan_and_value():
    x = np.array([[1.0, 2.0, 3.0, 4.0, 5.0]])
    out = R.trailing_nanmean(x, 3)
    assert np.isnan(out[0, 0]) and np.isnan(out[0, 1])
    assert np.isclose(out[0, 2], 2.0)   # mean(1,2,3)
    assert np.isclose(out[0, 3], 3.0)   # mean(2,3,4)
    assert np.isclose(out[0, 4], 4.0)   # mean(3,4,5)


def test_trailing_nanmean_ignores_nan():
    x = np.array([[1.0, np.nan, 3.0, 4.0]])
    out = R.trailing_nanmean(x, 2)
    assert np.isnan(out[0, 0])
    assert np.isclose(out[0, 1], 1.0)   # window [1,nan] -> 1
    assert np.isclose(out[0, 2], 3.0)   # window [nan,3] -> 3
    assert np.isclose(out[0, 3], 3.5)   # window [3,4] -> 3.5


def test_trailing_nanmax_warmup_and_value():
    x = np.array([[1.0, 3.0, 2.0, 5.0, 4.0]])
    out = R.trailing_nanmax(x, 3)
    assert np.isnan(out[0, 0]) and np.isnan(out[0, 1])
    assert np.isclose(out[0, 2], 3.0)   # max(1,3,2)
    assert np.isclose(out[0, 3], 5.0)   # max(3,2,5)
    assert np.isclose(out[0, 4], 5.0)   # max(2,5,4)


def test_finite_or_nan_masks_nonfinite():
    x = np.array([[1.0, np.inf, -np.inf, np.nan, 5.0]])
    out = R.finite_or_nan(x)
    assert out[0, 0] == 1.0
    assert np.isnan(out[0, 1]) and np.isnan(out[0, 2]) and np.isnan(out[0, 3])
    assert out[0, 4] == 5.0


# ---------------------------------------------------------------- signal builders
def _bs():
    n_bars = 12
    t = np.arange(n_bars)
    lr = np.zeros((3, n_bars))
    lr[0] = 0.0001 * np.where(t % 2 == 0, 1.0, -1.0)   # low vol
    lr[1] = 0.01 * np.where(t % 2 == 0, 1.0, -1.0)     # high vol, large |min|
    lr[2] = 0.0                                         # zero vol (rv -> NaN, ok)
    return {"log_return": lr, "perp_close": np.ones((3, n_bars)) * 100.0}


def test_build_score_all_signals_shapes_and_warmup_nan():
    bs = _bs()
    for sig in R.SIGNALS:
        for L in R.LOOKBACKS:
            sc = R.build_score(bs, sig, L)
            assert sc.shape == (3, 12), (sig, L)
            # first L-1 bars must be NaN (full-window trailing, fail-closed)
            assert np.isnan(sc[:, :L - 1]).all(), (sig, L)


def test_build_score_rv_low_vol_higher_score():
    bs = _bs()
    sc = R.build_score(bs, "rv", 6)
    col = sc[:, 8]
    assert np.isfinite(col[0]) and np.isfinite(col[1])
    # high-vol asset1 -> more negative score than low-vol asset0
    assert col[1] < col[0]


def test_build_score_maxret_high_max_lower_score():
    bs = _bs()
    sc = R.build_score(bs, "maxret", 6)
    col = sc[:, 8]
    # score = -max; asset1 max=0.01 -> most negative
    assert col[1] < col[0]


def test_build_score_dsvol_large_downside_lower_score():
    bs = _bs()
    sc = R.build_score(bs, "dsvol", 6)
    col = sc[:, 8]
    # score = -downside_vol; asset1 has large negative returns -> most negative
    assert col[1] < col[0]


def test_build_score_ivol_high_deviation_lower_score():
    bs = _bs()
    sc = R.build_score(bs, "ivol", 6)
    col = sc[:, 8]
    # asset1 deviates most from xsec mean -> lowest idio-vol score
    assert col[1] < col[0]
    assert col[1] < col[2]


def test_build_score_skew_sign_convention():
    lr = np.array([
        [-0.001, -0.001, -0.001, 0.05],   # positive skew (rare large up)
        [0.001, 0.001, 0.001, -0.05],     # negative skew (rare large down)
    ])
    sc = R.build_score({"log_return": lr, "perp_close": np.ones((2, 4)) * 100.0}, "skew", 4)
    # score = -skew: positive-skew asset -> negative score; negative-skew -> positive
    assert sc[1, 3] > sc[0, 3]


# ---------------------------------------------------------------- grid size
def test_n_trials_is_1440_and_full_grid():
    assert R.N_TRIALS == 1440
    assert R.SIGNALS == ("rv", "ivol", "skew", "maxret", "dsvol")
    assert R.LOOKBACKS == (288, 1008, 2016)
    assert R.REBALANCES == (6, 12, 48)
    assert R.FEES == (1, 5, 10, 20)
    assert R.SLIPS == (1, 2, 5, 10)
    assert R.COST_VARIANTS == ("symmetric", "perp_heavy")


# ---------------------------------------------------------------- artifact schema
def _load(name):
    candidates = sorted(
        p for p in (ROOT / "reports").glob(f"campaign317_{name}_*.json")
        if not p.name.endswith(".full.json")
    )
    assert candidates, f"missing artifact campaign317_{name}_*.json"
    p = candidates[-1]
    return json.loads(p.read_text())


def test_artifacts_exist_with_real_data_flags():
    for name in ("oos_sweep", "tradable_edge_registry", "summary", "verdict", "binding_constraint"):
        obj = _load(name)
        assert obj.get("real_data_only") is True, name
        assert obj.get("fabricated_data") is False, name
        assert obj.get("executed_fills") is False, name
        assert obj.get("campaign") == 317, name


def test_verdict_binding_and_counts():
    v = _load("verdict")
    assert v["verdict"] in ("RETRACTED", "EDGE_PROVEN")
    assert v["edge_proven"] in (True, False)
    if not v["edge_proven"]:
        assert v["binding_constraint"] is not None
    assert v["n_deterministic_edge"] >= 0
    for key in ("oos_sweep_sha256", "registry_sha256", "summary_sha256"):
        assert isinstance(v[key], str) and len(v[key]) == 64


def test_sweep_has_all_1440_configs_and_gates():
    sw = _load("oos_sweep")
    assert sw["config"]["n_trials"] == 1440
    assert len(sw["results"]) == 1440
    for r in sw["results"]:
        for k in ("p_value", "p_holm", "p_bh", "holm_reject", "bh_reject",
                  "signal", "lookback", "rebalance", "fee_bps", "slippage_bps",
                  "cost_variant", "edge_proven"):
            assert k in r, (k, r)
    mt = sw["gates"]["multiple_testing"]
    assert mt["holm_alpha"] == 0.05 and mt["bh_alpha"] == 0.05
    assert mt["n_survive_both"] >= 0
    attr = sw["gates"]["attribution"]
    assert set(attr["shares"].keys()) == {"low_volatility", "lottery", "downside", "placebo_noise"}
    assert attr["dominant"] in ("low_volatility", "lottery", "downside", "placebo_noise")


def test_registry_and_binding_constraint_consistent_with_verdict():
    v = _load("verdict")
    reg = _load("tradable_edge_registry")
    bc = _load("binding_constraint")
    assert reg["verdict"] == v["verdict"]
    assert bc["binding_constraint"] == v["binding_constraint"]
    assert bc["verdict"] == v["verdict"]


def test_summary_reports_attribution_shares():
    s = _load("summary")
    cfg = s["config"]
    assert cfg["cost_variants"] == ["symmetric", "perp_heavy"]
    assert len(cfg["fee_bps"]) == 4 and len(cfg["slippage_bps"]) == 4
    assert cfg["signals"] == ["rv", "ivol", "skew", "maxret", "dsvol"]
    attr = s["gates"]["attribution"]
    assert "shares" in attr and "dominant_share" in attr and "attribution_ok" in attr