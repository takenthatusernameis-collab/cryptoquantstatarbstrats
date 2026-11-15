"""Tests for C315 runner (scripts/run_c315_perp_momentum_reversal_oos.py): the
costed out-of-sample perp momentum / short-term reversal stat-arb over 3456
pre-registered configs on real USDT-M linear 5m perp closes.

These tests never fetch or fabricate market data. They exercise the runner's pure
functions on synthetic arrays (multiple-testing correction, single-leg cost model,
causal dollar-neutral cross-sectional positions, month-aligned walk-forward
splits, trailing-return + cross-sectional scores), and they validate the schema
and flags of the emitted real-data artifacts (verdict, registry, summary, binding
constraint, sweep) produced by the full run.
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

import run_c315_perp_momentum_reversal_oos as R  # noqa: E402


# ---------------------------------------------------------------- multiple testing
def test_holm_and_bh_reject_correctly():
    p = np.array([0.001, 0.01, 0.03, 0.2, 0.5])
    ph, rh = R.holm_adjust(p)
    pb, rb = R.bh_adjust(p)
    # Holm: sorted [0.001,0.01,0.03,...] * [5,4,3,...] => [0.005,0.04,0.09,...]
    assert np.isclose(ph[0], 0.005) and np.isclose(ph[1], 0.04)
    assert list(rh) == [True, True, False, False, False]
    # BH: [0.005,0.025,0.05,0.25,0.5]
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
    # symmetric: fee + slip per unit turnover
    assert R.cost_rate_bps(10, 5, "symmetric") == 15.0
    # perp_heavy: 1.5*fee + slip = 15 + 5 = 20
    assert R.cost_rate_bps(10, 5, "perp_heavy") == 20.0
    # perp_heavy always >= symmetric
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
    # dollar-neutral on every bar
    assert np.allclose(pos.sum(axis=0), 0.0)
    # causal: no position on the first bar (applied from next bar)
    assert np.all(pos[:, 0] == 0.0)
    # strongest positive names long, strongest negative short
    assert pos[0, 2] > 0 and pos[3, 2] < 0


def test_positions_dollar_neutral_on_equal_scores():
    # all-equal scores still split top/bottom by tie-break but stay dollar-neutral
    score = np.full((4, 5), 0.9)
    pos = R.xsec_positions(score, 0.25, 1)
    assert np.allclose(pos.sum(axis=0), 0.0)
    assert pos.shape == (4, 5)
    # causal: no position on the first bar
    assert np.all(pos[:, 0] == 0.0)


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


# ---------------------------------------------------------------- scores / returns
def test_cross_sectional_score_signs():
    mom = np.array([[0.01, -0.01, 0.02]])
    rev = np.array([[0.02, -0.02, -0.01]])
    assert np.allclose(R.cross_sectional_score(mom, rev, "xsec_mom"), mom)
    assert np.allclose(R.cross_sectional_score(mom, rev, "xsec_rev"), -rev)
    mmr = R.cross_sectional_score(mom, rev, "mom_minus_rev")
    assert mmr.shape == mom.shape


def test_trailing_return_causal_first_bars_nan():
    close = np.array([[1.0, 2.0, 4.0, 8.0, 16.0]])
    out = R.trailing_return(close, 2)
    assert np.isnan(out[0, 0]) and np.isnan(out[0, 1])
    # c[t]/c[t-2] - 1: t=2 -> 4/1-1=3, t=3 -> 8/2-1=3, t=4 -> 16/4-1=3
    assert np.isclose(out[0, 2], 3.0)
    assert np.isclose(out[0, 3], 3.0)
    assert np.isclose(out[0, 4], 3.0)


# ---------------------------------------------------------------- grid size
def test_n_trials_is_3456_and_full_grid():
    assert R.N_TRIALS == 3456
    assert R.SIGNALS == ("xsec_mom", "xsec_rev", "mom_minus_rev")
    assert R.MOM_LOOKBACKS == (288, 2016, 8640)
    assert R.REV_LOOKBACKS == (12, 72)
    assert R.REBALANCES == (6, 12, 48)
    assert R.FEES == (1, 5, 10, 20)
    assert R.SLIPS == (1, 2, 5, 10)
    assert R.SELECTIONS == (0.33, 0.25)
    assert R.COST_VARIANTS == ("symmetric", "perp_heavy")


# ---------------------------------------------------------------- artifact schema
def _load(name):
    # latest (lexicographically greatest timestamp) slim artifact, not the .full blob
    candidates = sorted(
        p for p in (ROOT / "reports").glob(f"campaign315_{name}_*.json")
        if not p.name.endswith(".full.json")
    )
    assert candidates, f"missing artifact campaign315_{name}_*.json"
    p = candidates[-1]
    return json.loads(p.read_text())


def test_artifacts_exist_with_real_data_flags():
    for name in ("oos_sweep", "tradable_edge_registry", "summary", "verdict", "binding_constraint"):
        obj = _load(name)
        assert obj.get("real_data_only") is True, name
        assert obj.get("fabricated_data") is False, name
        assert obj.get("executed_fills") is False, name
        assert obj.get("campaign") == 315, name


def test_verdict_binding_and_counts():
    v = _load("verdict")
    assert v["verdict"] in ("RETRACTED", "EDGE_PROVEN")
    assert v["edge_proven"] in (True, False)
    if not v["edge_proven"]:
        assert v["binding_constraint"] is not None
    assert v["n_deterministic_edge"] >= 0
    for key in ("oos_sweep_sha256", "registry_sha256", "summary_sha256"):
        assert isinstance(v[key], str) and len(v[key]) == 64


def test_sweep_has_all_3456_configs_and_gates():
    sw = _load("oos_sweep")
    assert sw["config"]["n_trials"] == 3456
    assert len(sw["results"]) == 3456
    for r in sw["results"]:
        for k in ("p_value", "p_holm", "p_bh", "holm_reject", "bh_reject",
                  "signal", "mom_lookback", "rev_lookback", "selection", "rebalance",
                  "fee_bps", "slippage_bps", "cost_variant", "edge_proven"):
            assert k in r, (k, r)
    mt = sw["gates"]["multiple_testing"]
    assert mt["holm_alpha"] == 0.05 and mt["bh_alpha"] == 0.05
    assert mt["n_survive_both"] >= 0
    attr = sw["gates"]["attribution"]
    assert set(attr["shares"].keys()) == {"momentum", "reversal", "placebo_noise"}
    assert attr["dominant"] in ("momentum", "reversal", "placebo_noise")


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
    attr = s["gates"]["attribution"]
    assert "shares" in attr and "dominant_share" in attr and "attribution_ok" in attr
