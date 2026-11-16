"""Tests for C320 runner (scripts/run_c320_tod_seasonality_xsec_oos.py): the costed
out-of-sample cross-sectional INTRADAY TIME-OF-DAY / DAY-OF-WEEK SEASONALITY
mean-reversion stat-arb over 1440 pre-registered configs on real USDT-M linear 5m
perps.

These tests never fetch or fabricate market data. They exercise the runner's pure
functions on synthetic arrays (multiple-testing correction, single-leg cost model,
causal dollar-neutral cross-sectional positions, month-aligned walk-forward
splits, nan-aware trailing mean, bucket trailing stats, ewm baseline, and the five
seasonal signal builders), and they validate the schema and flags of the emitted
real-data artifacts (verdict, registry, summary, binding constraint, sweep)
produced by the full run.
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

import run_c320_tod_seasonality_xsec_oos as R  # noqa: E402


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


def test_finite_or_nan_masks_nonfinite():
    x = np.array([[1.0, np.inf, -np.inf, np.nan, 5.0]])
    out = R.finite_or_nan(x)
    assert out[0, 0] == 1.0
    assert np.isnan(out[0, 1]) and np.isnan(out[0, 2]) and np.isnan(out[0, 3])
    assert out[0, 4] == 5.0


# ---------------------------------------------------------------- seasonal signal builders
def _bs():
    """Synthetic 5m return panel over 14 days (2 weeks). grid starts at midnight;
    tod_idx = bar-of-day (0..287); dow_idx = dayofweek*288+tod (0..2015). A
    transient shock at the LAST bar makes asset0 seasonally rich (score<0) and
    asset2 seasonally cheap (score>0) at that bar's seasonal bucket."""
    n_bars = 288 * 42   # 42 days = 6 weeks: each dow+bar recurs 6x, each tod 42x
    t = np.arange(n_bars, dtype=float)
    tod_idx = (t % 288).astype(np.int64)
    dow = ((t // 288) % 7).astype(np.int64)
    dow_idx = (dow * 288 + tod_idx).astype(np.int64)
    r = np.zeros((3, n_bars))
    r[0, -1] = 0.05     # rich shock at last bar
    r[2, -1] = -0.05    # cheap shock at last bar
    return {"log_return": r, "tod_idx": tod_idx, "dow_idx": dow_idx}


def test_build_score_all_signals_shapes_and_warmup_nan():
    bs = _bs()
    for sig in R.SIGNALS:
        for L in (2, 5):
            sc = R.build_score(bs, sig, L)
            assert sc.shape == (3, 42 * 288), (sig, L)
            # warmup exists (first occurrences of each bucket are NaN)
            assert np.isnan(sc).any(), (sig, L)
            # last bar is past warmup for the signal-bearing assets (each
            # bucket recurs); zero-variance assets correctly yield NaN
            assert np.isfinite(sc[0, -1]) and np.isfinite(sc[2, -1]), (sig, L)


def test_build_score_cheap_long_rich_short():
    bs = _bs()
    L = 2
    for sig in R.SIGNALS:
        sc = R.build_score(bs, sig, L)
        col = sc[:, -1]
        assert np.isfinite(col[0]) and np.isfinite(col[2]), sig
        # asset0 rich (shock>0 -> score<0); asset2 cheap (shock<0 -> score>0)
        assert col[0] < 0.0 < col[2], (sig, col)


def test_tod_z_uses_dev_std_not_return_std():
    bs = _bs()
    sc_z = R.build_score(bs, "tod_z", 2)
    sc_rv = R.build_score(bs, "tod_rv", 2)
    # distinct signals: tod_z normalizes by dev std, tod_rv by return std
    assert not np.allclose(sc_z, sc_rv)


# ---------------------------------------------------------------- grid size
def test_n_trials_is_1440_and_full_grid():
    assert R.N_TRIALS == 1440
    assert R.SIGNALS == ("tod_dev", "tod_z", "dow_dev", "tod_rv", "tod_ewm")
    assert R.LOOKBACKS == (30, 60, 90)
    assert R.REBALANCES == (6, 12, 48)
    assert R.FEES == (1, 5, 10, 20)
    assert R.SLIPS == (1, 2, 5, 10)
    assert R.COST_VARIANTS == ("symmetric", "perp_heavy")


# ---------------------------------------------------------------- artifact schema
def _load(name):
    candidates = sorted(
        p for p in (ROOT / "reports").glob(f"campaign320_{name}_*.json")
        if not p.name.endswith(".full.json")
    )
    assert candidates, f"missing artifact campaign320_{name}_*.json"
    p = candidates[-1]
    return json.loads(p.read_text())


def test_artifacts_exist_with_real_data_flags():
    for name in ("oos_sweep", "tradable_edge_registry", "summary", "verdict", "binding_constraint"):
        obj = _load(name)
        assert obj.get("real_data_only") is True, name
        assert obj.get("fabricated_data") is False, name
        assert obj.get("executed_fills") is False, name
        assert obj.get("campaign") == 320, name


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
    assert set(attr["shares"].keys()) == {
        "tod_dev", "tod_z", "dow_dev", "tod_rv", "tod_ewm", "placebo_noise"}
    assert attr["dominant"] in ("tod_dev", "tod_z", "dow_dev", "tod_rv", "tod_ewm", "placebo_noise")


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
    assert cfg["signals"] == ["tod_dev", "tod_z", "dow_dev", "tod_rv", "tod_ewm"]
    attr = s["gates"]["attribution"]
    assert "shares" in attr and "dominant_share" in attr and "attribution_ok" in attr
