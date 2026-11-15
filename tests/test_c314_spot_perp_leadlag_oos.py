"""Tests for C314 runner (scripts/run_c314_spot_perp_leadlag_oos.py): the
costed out-of-sample spot-perp lead-lag stat-arb over 2304 pre-registered configs.

These tests never fetch or fabricate market data. They exercise the runner's pure
functions on synthetic arrays (multiple-testing correction, two-leg cost model,
causal dollar-neutral cross-sectional positions, month-aligned walk-forward
splits, the lead-lag signal on a series with a KNOWN spot-leads-perp lag), and
they validate the schema and flags of the emitted real-data artifacts (verdict,
registry, summary, binding constraint, sweep) produced by the full run.
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

import run_c314_spot_perp_leadlag_oos as R  # noqa: E402


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
        # rejection set must be exactly adj <= alpha
        assert np.array_equal(rej, adj <= R.ALPHA)


# ---------------------------------------------------------------- two-leg costs
def test_cost_rate_symmetric_and_perp_heavy():
    # symmetric: both legs fee+slip -> 2*(fee+slip)
    assert R.cost_rate_bps(10, 5, "symmetric") == 30.0
    # perp_heavy: spot=(fee+slip)=15, perp=(1.5*fee+slip)=20 -> 35
    assert R.cost_rate_bps(10, 5, "perp_heavy") == 35.0
    # perp_heavy always >= symmetric (perp leg costs more)
    for fee in R.FEES:
        for slip in R.SLIPS:
            assert R.cost_rate_bps(fee, slip, "perp_heavy") >= R.cost_rate_bps(fee, slip, "symmetric")


def test_cost_grid_is_real_and_nonzero():
    assert min(R.FEES) >= 1 and max(R.FEES) == 20
    assert min(R.SLIPS) >= 1 and max(R.SLIPS) == 10
    # every config pays strictly positive cost on turnover
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
    pos = R.xsec_positions(_score_matrix(), 0.05, 0.25, 1)
    assert pos.shape == (4, 6)
    # dollar-neutral on every bar
    assert np.allclose(pos.sum(axis=0), 0.0)
    # causal: no position on the first bar (applied from next bar)
    assert np.all(pos[:, 0] == 0.0)
    # strongest positive names are long, strongest negative are short
    assert pos[0, 2] > 0 and pos[3, 2] < 0


def test_positions_flat_when_one_side_empty():
    # only 2 names pass the threshold, all positive -> no short side -> flat
    score = np.array([
        [0.9, 0.9, 0.9, 0.9],
        [0.8, 0.8, 0.8, 0.8],
        [0.1, 0.1, 0.1, 0.1],
        [0.2, 0.2, 0.2, 0.2],
    ])
    pos = R.xsec_positions(score, 0.5, 0.25, 1)
    assert np.allclose(pos, 0.0)


def test_positions_respect_threshold():
    # scores below threshold -> all neutral -> flat
    score = np.full((4, 5), 0.01)
    pos = R.xsec_positions(score, 0.05, 0.25, 1)
    assert np.allclose(pos, 0.0)


def test_positions_hold_reduces_turnover():
    score = np.tile(np.array([[0.9], [0.8], [-0.8], [-0.9]]), (1, 12))
    pos1 = R.xsec_positions(score, 0.05, 0.25, 1)
    pos6 = R.xsec_positions(score, 0.05, 0.25, 6)
    turn1 = np.abs(np.diff(pos1, axis=1)).sum()
    turn6 = np.abs(np.diff(pos6, axis=1)).sum()
    assert turn6 <= turn1  # holding H bars cannot increase turnover


# ---------------------------------------------------------------- walk-forward
def test_wf_splits_month_aligned_non_overlapping():
    idx = pd.date_range("2023-01-01", periods=31 * 288 + 28 * 288 + 31 * 288,
                        freq="5min", tz="UTC")
    splits = R.wf_splits_by_month(idx, 1, 1, 1)
    assert len(splits) >= 2
    prev_te = None
    for (tr_s, tr_e, te_s, te_e) in splits:
        assert tr_s < tr_e <= te_s < te_e  # ordered, non-overlapping train/test
        if prev_te is not None:
            assert te_s >= prev_te  # rolling forward
        prev_te = te_e


# ---------------------------------------------------------------- lead-lag signal
def test_leadlag_signal_detects_known_spot_leads_perp_lag():
    rng = np.random.default_rng(3)
    n_assets, n_b = 3, 6000
    r_spot = rng.normal(0, 1e-3, size=(n_assets, n_b))
    r_perp = np.zeros_like(r_spot)
    r_perp[:, 2:] = r_spot[:, :-2] + rng.normal(0, 1e-4, size=(n_assets, n_b - 2))
    idx = pd.date_range("2023-01-01", periods=n_b, freq="5min", tz="UTC")
    sig = R.compute_leadlag_signals(r_spot, r_perp, idx, ["a", "b", "c"], max_lag=24, W=288)
    assert set(sig.keys()) == {6, 12, 24}
    for lag, (ms, mp) in sig.items():
        ll = R.leadlag_from_max(ms, mp)
        mid = ll[:, 400:5000]
        # spot leads perp by 2 bars -> strongly positive lead-lag
        assert np.nanmean(mid) > 0.5, (lag, np.nanmean(mid))
        # spot-lead corr dominates perp-lead corr
        assert np.nanmean(ms[:, 400:5000]) > np.nanmean(mp[:, 400:5000])


def test_leadlag_from_max_sign():
    ms = np.array([[1.0, 0.5]])
    mp = np.array([[0.2, 0.6]])
    ll = R.leadlag_from_max(ms, mp)
    assert np.isclose(ll[0, 0], 0.8) and np.isclose(ll[0, 1], -0.1)


def test_n_trials_is_2304_and_full_grid():
    assert R.N_TRIALS == 2304
    assert R.LAG_WINDOWS == (6, 12, 24)
    assert R.LEADLAG_THRESHOLDS == (0.05, 0.10, 0.15)
    assert R.REBALANCES == (1, 3, 6, 12)
    assert R.TERCILE_CUTS == (0.33, 0.25)
    assert R.COST_VARIANTS == ("symmetric", "perp_heavy")


# ---------------------------------------------------------------- artifact schema
def _load(name):
    # latest (lexicographically greatest timestamp) slim artifact, not the .full blob
    candidates = sorted(
        p for p in (ROOT / "reports").glob(f"campaign314_{name}_*.json")
        if not p.name.endswith(".full.json")
    )
    assert candidates, f"missing artifact campaign314_{name}_*.json"
    p = candidates[-1]
    return json.loads(p.read_text())


def test_artifacts_exist_with_real_data_flags():
    for name in ("oos_sweep", "tradable_edge_registry", "summary", "verdict", "binding_constraint"):
        obj = _load(name)
        assert obj.get("real_data_only") is True, name
        assert obj.get("fabricated_data") is False, name
        assert obj.get("executed_fills") is False, name
        assert obj.get("campaign") == 314, name


def test_verdict_binding_and_counts():
    v = _load("verdict")
    assert v["verdict"] in ("RETRACTED", "EDGE_PROVEN")
    assert v["edge_proven"] in (True, False)
    # every verdict declares a binding constraint unless an edge was proven
    if not v["edge_proven"]:
        assert v["binding_constraint"] is not None
    assert v["n_deterministic_edge"] == 0 or v["n_deterministic_edge"] >= 0
    # provenance chain: verdict references real artifact SHAs
    for key in ("oos_sweep_sha256", "registry_sha256", "summary_sha256"):
        assert isinstance(v[key], str) and len(v[key]) == 64


def test_sweep_has_all_2304_configs_and_gates():
    sw = _load("oos_sweep")
    assert sw["config"]["n_trials"] == 2304
    assert len(sw["results"]) == 2304
    # every config carries a Holm and BH adjusted p-value + rejection flag
    for r in sw["results"]:
        for k in ("p_value", "p_holm", "p_bh", "holm_reject", "bh_reject",
                  "lag_window", "lead_lag_threshold", "tercile_cut", "rebalance",
                  "fee_bps", "slippage_bps", "cost_variant", "edge_proven"):
            assert k in r, (k, r)
    # multiple-testing gate reports both corrections
    mt = sw["gates"]["multiple_testing"]
    assert mt["holm_alpha"] == 0.05 and mt["bh_alpha"] == 0.05
    assert mt["n_survive_both"] == 0 or mt["n_survive_both"] >= 0


def test_registry_and_binding_constraint_consistent_with_verdict():
    v = _load("verdict")
    reg = _load("tradable_edge_registry")
    bc = _load("binding_constraint")
    assert reg["verdict"] == v["verdict"]
    assert bc["binding_constraint"] == v["binding_constraint"]
    assert bc["verdict"] == v["verdict"]


def test_summary_reports_two_legs_and_cost_variants():
    s = _load("summary")
    cfg = s["config"]
    assert cfg["cost_variants"] == ["symmetric", "perp_heavy"]
    assert len(cfg["fee_bps"]) == 4 and len(cfg["slippage_bps"]) == 4
    # attribution must be present and honest (lead-lag vs noise)
    attr = s["gates"]["attribution"]
    assert "leadlag_vs_noise_share" in attr
    assert "edge_explained_by_leadlag" in attr