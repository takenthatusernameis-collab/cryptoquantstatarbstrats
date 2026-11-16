"""Tests for C319 runner (scripts/run_c319_cointegration_pairs_oos.py): the costed
out-of-sample cross-sectional COINTEGRATION / PAIRS mean-reversion stat-arb over
3456 pre-registered configs on real USDT-M linear 5m perps.

These tests never fetch or fabricate market data. They exercise the runner's pure
functions on synthetic arrays (multiple-testing correction, beta-hedged single-leg
cost model, causal mean-reversion position with deadband, nan-aware trailing mean,
causal shift, month-aligned walk-forward splits, all-pairs construction, rolling
cointegration precompute, top-N pair selection), and they validate the schema and
flags of the emitted real-data artifacts (verdict, registry, summary, binding
constraint, sweep) produced by the run.
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

import run_c319_cointegration_pairs_oos as R  # noqa: E402


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
def test_meanrev_position_deadband_and_full():
    # exit=0.5, entry=2.0 -> inside deadband zero, full at |z|>=2, ramp between
    z = np.array([[0.0, 0.3, 0.5, 1.0, 2.0, 3.0, -2.5, -1.0, -0.2]])
    pos = R.meanrev_position(z, 2.0, 0.5)
    assert np.isclose(pos[0, 0], 0.0)      # z=0 -> 0
    assert np.isclose(pos[0, 1], 0.0)      # |z|=0.3 < exit -> 0
    assert np.isclose(pos[0, 2], 0.0)      # |z|=0.5 == exit -> 0
    assert pos[0, 3] < 0.0                 # z=1.0 -> short (negative)
    assert np.isclose(pos[0, 4], -1.0)     # z=2.0 -> full short
    assert np.isclose(pos[0, 5], -1.0)     # z=3.0 -> clipped full short
    assert np.isclose(pos[0, 6], 1.0)      # z=-2.5 -> full long
    assert pos[0, 7] > 0.0                 # z=-1.0 -> long
    assert np.isclose(pos[0, 8], 0.0)      # |z|=0.2 < exit -> 0


def test_meanrev_position_nan_collapse_to_zero():
    z = np.array([[np.nan, 1.0, np.nan]])
    pos = R.meanrev_position(z, 2.0, 0.5)
    assert np.isclose(pos[0, 0], 0.0)
    assert np.isfinite(pos).all()


# ---------------------------------------------------------------- causal shift
def test_causal_shifts_right_by_one():
    x = np.array([[1.0, 2.0, 3.0, 4.0]])
    y = R.causal(x)
    assert np.isnan(y[0, 0])
    assert np.isclose(y[0, 1], 1.0)
    assert np.isclose(y[0, 3], 3.0)


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


# ---------------------------------------------------------------- trailing mean
def test_trailing_mean_warmup_nan_and_value():
    x = np.array([[1.0, 2.0, 3.0, 4.0, 5.0]])
    out = R.trailing_mean(x, 3)
    assert np.isnan(out[0, 0]) and np.isnan(out[0, 1])
    assert np.isclose(out[0, 2], 2.0)   # mean(1,2,3)
    assert np.isclose(out[0, 3], 3.0)   # mean(2,3,4)
    assert np.isclose(out[0, 4], 4.0)   # mean(3,4,5)


# ---------------------------------------------------------------- pairs + precompute
def _fake_bs(n_assets=4, n_bars=40):
    rng = np.random.default_rng(11)
    t = np.arange(n_bars)
    log_price = np.cumsum(rng.normal(0, 0.01, size=(n_assets, n_bars)), axis=1) + 10.0
    log_return = np.zeros((n_assets, n_bars))
    log_return[:, 1:] = log_price[:, 1:] - log_price[:, :-1]
    return {"symbols": [f"S{i}" for i in range(n_assets)], "n_assets": n_assets,
            "log_price": log_price, "log_return": log_return}


def test_build_pairs_all_unordered_pairs():
    bs = _fake_bs(n_assets=10, n_bars=20)
    pr = R.build_pairs(bs)
    assert pr["n_pairs"] == 45
    assert pr["logPa"].shape == (45, 20)
    assert pr["pairs"][0] == ("S0", "S1")
    assert pr["pairs"][-1] == ("S8", "S9")


def test_precompute_L_shapes_and_warmup_nan():
    bs = _fake_bs(n_assets=4, n_bars=40)
    pr = R.build_pairs(bs)
    L = 10
    d = R.precompute_L(pr, L)
    for key in ("beta", "beta_prev", "z", "r2", "spr_ret", "inv"):
        assert d[key].shape == (6, 40), key
    # rolling stats warmup: first L-1 bars must be NaN for beta / z / r2
    assert np.isnan(d["beta"][:, :L - 1]).all()
    assert np.isnan(d["z"][:, :L - 1]).all()
    # spr_ret uses causal beta -> first bar NaN (beta_prev[0] = NaN)
    assert np.isnan(d["spr_ret"][:, 0]).all()
    # inv is finite (0 where beta_prev NaN) -> no NaN
    assert np.isfinite(d["inv"]).all()


def test_top15_mask_selects_n_per_segment():
    rng = np.random.default_rng(3)
    r2 = rng.uniform(0, 1, size=(45, 60))
    mask = R.top15_mask(r2, H=10)
    assert mask.shape == (45, 60)
    # each 10-bar segment should have exactly 15 True per column
    for t in (0, 5, 10, 25, 59):
        assert mask[:, t].sum() == 15


def test_top15_mask_prefers_highest_r2():
    r2 = np.zeros((45, 20))
    r2[7, 0] = 0.99   # pair 7 has highest R2 in first segment
    mask = R.top15_mask(r2, H=20)
    assert mask[7, 0] is np.True_ or bool(mask[7, 0]) is True


# ---------------------------------------------------------------- grid size
def test_n_trials_is_3456_and_full_grid():
    assert R.N_TRIALS == 3456
    assert R.LOOKBACKS == (1008, 2016, 4032)
    assert R.ENTRY_Z == (1.5, 2.0, 2.5)
    assert R.EXIT_Z == (0.5, 1.0)
    assert R.HOLD_BARS == (6, 12, 48)
    assert R.FEES == (1, 5, 10, 20)
    assert R.SLIPS == (1, 2, 5, 10)
    assert R.COST_VARIANTS == ("symmetric", "perp_heavy")
    assert R.PAIRSETS == ("all45", "top15")


# ---------------------------------------------------------------- artifact schema
def _load(name):
    candidates = sorted(
        p for p in (ROOT / "reports").glob(f"campaign319_{name}_*.json")
        if not p.name.endswith(".full.json")
    )
    assert candidates, f"missing artifact campaign319_{name}_*.json"
    p = candidates[-1]
    return json.loads(p.read_text())


def test_artifacts_exist_with_real_data_flags():
    for name in ("oos_sweep", "tradable_edge_registry", "summary", "verdict", "binding_constraint"):
        obj = _load(name)
        assert obj.get("real_data_only") is True, name
        assert obj.get("fabricated_data") is False, name
        assert obj.get("executed_fills") is False, name
        assert obj.get("campaign") == 319, name


def test_verdict_binding_and_counts():
    v = _load("verdict")
    assert v["verdict"] in ("RETRACTED", "EDGE_PROVEN")
    assert v["edge_proven"] in (True, False)
    if not v["edge_proven"]:
        assert v["binding_constraint"] is not None
    assert v["n_deterministic_edge"] >= 0
    for key in ("oos_sweep_sha256", "registry_sha256", "summary_sha256"):
        assert isinstance(v[key], str) and len(v[key]) == 64


def test_sweep_has_declared_grid_and_gates():
    sw = _load("oos_sweep")
    assert sw["config"]["n_trials"] == 3456
    results = sw["results"]
    # smoke runs produce 1 result; the full sweep produces 3456
    assert len(results) in (1, 3456), len(results)
    for r in results:
        for k in ("p_value", "p_holm", "p_bh", "holm_reject", "bh_reject",
                  "cointegration_lookback", "entry_z", "exit_z", "hold_bars", "pairset",
                  "fee_bps", "slippage_bps", "cost_variant", "edge_proven", "exposure"):
            assert k in r, (k, r)
    mt = sw["gates"]["multiple_testing"]
    assert mt["holm_alpha"] == 0.05 and mt["bh_alpha"] == 0.05
    assert mt["n_survive_both"] >= 0
    attr = sw["gates"]["attribution"]
    assert set(attr["shares"].keys()) == set(R.ATTR_BUCKETS)
    assert attr["dominant"] in R.ATTR_BUCKETS


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
    assert cfg["cointegration_lookbacks_bars"] == [1008, 2016, 4032]
    assert cfg["entry_z"] == [1.5, 2.0, 2.5]
    assert cfg["exit_z"] == [0.5, 1.0]
    attr = s["gates"]["attribution"]
    assert "shares" in attr and "dominant_share" in attr and "attribution_ok" in attr