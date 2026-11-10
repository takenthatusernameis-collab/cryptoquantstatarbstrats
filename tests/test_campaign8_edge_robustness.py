import hashlib
import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from examples.run_portfolio_real import PortfolioRiskController
from strategies.pairs_trading import CointegrationPairsStrategy, _evaluate_enriched_gates_strict

ROOT = Path(__file__).resolve().parents[1]
CACHE_PKL = ROOT / "data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl"
CACHE_META = (
    ROOT / "data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.meta.json"
)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_cached_spot_subset(cols=("BTC", "ETH"), n=240):
    if not CACHE_PKL.exists():
        pytest.skip("cached spot data unavailable")
    with open(CACHE_PKL, "rb") as f:
        df = pickle.load(f)
    df = df.sort_index()
    sub = df[list(cols)].dropna().iloc[:n].copy()
    if len(sub) < n:
        pytest.skip("insufficient cached rows for deterministic subset")
    return sub


def test_evaluate_enriched_gates_strict_fail_closed():
    # Missing/non-dict gates fail closed under strict
    assert _evaluate_enriched_gates_strict(None, None, True) is False
    assert _evaluate_enriched_gates_strict({}, {"flagged": False}, True) is False
    # Structural break blocks
    gates = {
        "eg_pass": True,
        "johansen_pass": True,
        "spread_mr_pass": True,
        "hl_bounds_pass": True,
        "rolling_stable_ok": True,
        "leg_stationarity_ok": True,
        "no_structural_break": True,
        "all_pass": True,
    }
    assert _evaluate_enriched_gates_strict(gates, {"flagged": True}, True) is False
    assert _evaluate_enriched_gates_strict(gates, {"flagged": None}, True) is False
    # Explicit False blocks
    g2 = dict(gates)
    g2["spread_mr_pass"] = False
    assert _evaluate_enriched_gates_strict(g2, {"flagged": False}, True) is False
    # All true + no break passes
    assert _evaluate_enriched_gates_strict(gates, {"flagged": False}, True) is True
    # Non-strict permissive fallback for missing structural breaks dict
    assert _evaluate_enriched_gates_strict(gates, None, False) is True


def test_cached_aggregate_diagnostics_applied_uniformly_on_real_subset():
    df = _load_cached_spot_subset(("BTC", "ETH"), n=300)
    # Cached/aggregate diagnostics are applied uniformly (not a causal per-bar refresh).
    # An all-pass aggregate payload yields enriched_ok=1.0 for all bars per evaluator.
    ed_pass = {
        "gates": {
            "eg_pass": True,
            "johansen_pass": True,
            "spread_mr_pass": True,
            "hl_bounds_pass": True,
            "rolling_stable_ok": True,
            "leg_stationarity_ok": True,
            "no_structural_break": True,
            "all_pass": True,
        },
        "structural_breaks": {"flagged": False},
    }
    strat = CointegrationPairsStrategy(
        pair=("BTC", "ETH"),
        lookback=60,
        entry_threshold=2.0,
        cointegration_pvalue=0.05,
        enriched_diagnostics=ed_pass,
        use_enriched_gates=True,
        strict_enriched_gates=True,
    )
    sig = strat.generate_signals(df)
    assert "enriched_gates_ok" in sig.columns
    assert (sig["enriched_gates_ok"].fillna(0.0) == 1.0).all()
    # A failing aggregate gate blocks uniformly (fail-closed outcome for that gate set).
    ed_fail = {
        "gates": {
            **ed_pass["gates"],
            "spread_mr_pass": False,
            "all_pass": False,
        },
        "structural_breaks": {"flagged": False},
    }
    strat_fail = CointegrationPairsStrategy(
        pair=("BTC", "ETH"),
        lookback=60,
        entry_threshold=2.0,
        cointegration_pvalue=0.05,
        enriched_diagnostics=ed_fail,
        use_enriched_gates=True,
        strict_enriched_gates=True,
    )
    sig_fail = strat_fail.generate_signals(df)
    assert int((sig_fail["BTC"].abs() > 1e-12).sum()) == 0
    assert int((sig_fail["ETH"].abs() > 1e-12).sum()) == 0


def test_uncached_strict_per_bar_blocks_when_gates_unassessable_or_failed():
    df = _load_cached_spot_subset(("BTC", "ETH"), n=180)
    strat = CointegrationPairsStrategy(
        pair=("BTC", "ETH"),
        lookback=60,
        entry_threshold=2.0,
        cointegration_pvalue=0.05,
        use_enriched_gates=True,
        strict_enriched_gates=True,
    )
    sig = strat.generate_signals(df)
    # Short trailing windows + strict gates: failed/unassessable gates block positions.
    assert "enriched_gates_ok" in sig.columns
    assert float(sig["enriched_gates_ok"].fillna(0.0).max()) in (0.0, 1.0)
    # Fail-closed expectation on this real subset/window: no traded exposure.
    assert int((sig["BTC"].abs() > 1e-12).sum()) == 0
    assert int((sig["ETH"].abs() > 1e-12).sum()) == 0


def test_hedge_ratio_and_opposing_leg_weight_sanity_on_real_subset():
    df = _load_cached_spot_subset(("BTC", "ETH"), n=500)
    # Use non-strict cached permissive only to exercise weight construction math deterministically;
    # this is a math/shape sanity test, not an edge claim.
    ed = {
        "gates": {
            "eg_pass": True,
            "johansen_pass": True,
            "spread_mr_pass": True,
            "hl_bounds_pass": True,
            "rolling_stable_ok": True,
            "leg_stationarity_ok": True,
            "no_structural_break": True,
            "all_pass": True,
        },
        "structural_breaks": {"flagged": False},
    }
    strat = CointegrationPairsStrategy(
        pair=("BTC", "ETH"),
        lookback=60,
        entry_threshold=1.0,
        cointegration_pvalue=0.99,
        enriched_diagnostics=ed,
        use_enriched_gates=True,
        strict_enriched_gates=False,
    )
    sig = strat.generate_signals(df)
    hedge = strat.hedge_ratio_series.dropna()
    if len(hedge):
        assert np.isfinite(hedge.to_numpy()).all()
        assert (hedge > 0).all()
        assert (hedge >= 1e-6 - 1e-12).all() and (hedge <= 1e6 + 1e-12).all()
    # Opposing legs / no same-direction exposure
    prod = (sig["BTC"] * sig["ETH"]).fillna(0.0)
    assert (prod <= 1e-12).all()
    # When active, abs market-value normalized legs should sum to ~1 in abs value
    active = (sig["BTC"].abs() + sig["ETH"].abs()) > 1e-12
    if active.any():
        gross_leg = sig.loc[active, "BTC"].abs() + sig.loc[active, "ETH"].abs()
        assert np.allclose(gross_leg.to_numpy(), 1.0, atol=1e-6)


def test_portfolio_risk_controller_applies_declared_controls():
    idx = pd.date_range("2026-01-01", periods=50, freq="h", tz="UTC")
    cols = ["BTC", "ETH", "SOL"]
    w = pd.DataFrame(0.0, index=idx, columns=cols)
    w["BTC"] = 0.8
    w["ETH"] = 0.8
    w["SOL"] = 0.2
    pair_map = {"BTC/ETH": ["BTC", "ETH"]}
    rng = np.random.default_rng(0)
    rets = pd.DataFrame(rng.normal(0, 0.01, size=(len(idx), len(cols))), index=idx, columns=cols)
    # induce drawdown for breaker
    rets.iloc[10:15, :] = -0.05
    ctrl = PortfolioRiskController(
        max_gross_exposure=1.4,
        per_pair_cap=0.32,
        max_correlation_exposure=0.5,
        max_cvar_allocation=0.25,
        drawdown_circuit_breaker=-0.10,
    )
    corr = rets.corr().to_dict()
    out = ctrl.apply(w, pair_map=pair_map, correlation_matrix=corr, returns=rets)
    assert (out.abs().sum(axis=1) <= 1.4 + 1e-9).all()
    assert (out[["BTC", "ETH"]].abs().sum(axis=1) <= 0.32 + 1e-9).all()
    assert (out.abs().max(axis=1) <= 0.5 + 1e-9).all()
    # circuit breaker should zero from breach onward at some point given drawdown
    assert (out.iloc[-1].abs().sum() == 0.0) or (out.abs().sum(axis=1).min() == 0.0)


def test_campaign8_artifact_provenance_honesty_if_present():
    paths = sorted((ROOT / "reports").glob("campaign8_edge_robustness_*.json"))
    if not paths:
        pytest.skip("Campaign 8 artifact not yet produced in this run")
    p = paths[-1]
    data = json.loads(p.read_text())
    assert data.get("type") == "campaign8_edge_robustness"
    assert data.get("real_data_only") is True
    assert data.get("fabricated_data") is False
    prov = data.get("provenance") or {}
    assert prov.get("network_fetch_performed") is False
    assert prov.get("no_synthetic_fabricated_inputs") is True
    assert prov.get("cache_spot_pkl_sha256") == _sha256(CACHE_PKL)
    assert prov.get("cache_spot_meta_sha256") == _sha256(CACHE_META)
    expected_key = json.loads(CACHE_META.read_text())["cache_key"]
    assert prov.get("cache_spot_meta_content", {}).get("cache_key") == expected_key
    conclusion = data.get("conclusion") or {}
    assert conclusion.get("honest") is True
    assert conclusion.get("status") in {"edge", "no_edge", "insufficient_or_blocked"}
    assert conclusion.get("edge_claim") == (conclusion.get("status") == "edge")
    # Pairs and portfolio sections present with cost/OOS/replay evidence structure
    pairs = data.get("pairs") or {}
    assert set(pairs.keys()) >= {"BTC/ETH", "ETH/SOL", "BTC/SOL"}
    for _, block in pairs.items():
        assert isinstance(block.get("oos_by_cost"), list) and block["oos_by_cost"]
        assert isinstance(block.get("replay_by_cost"), list) and block["replay_by_cost"]
        assert "buy_and_hold_total_return" in block
        assert "enriched_gate_accounting" in block
    port = data.get("portfolio") or {}
    assert isinstance(port.get("portfolio_by_cost"), list) and port["portfolio_by_cost"]
    assert port.get("risk_controls", {}).get("max_gross_exposure") == 1.4
    assert port.get("risk_controls", {}).get("per_pair_cap") == 0.32
    assert port.get("risk_controls", {}).get("max_correlation_exposure") == 0.5
    assert port.get("risk_controls", {}).get("max_cvar_allocation") == 0.25
    assert port.get("risk_controls", {}).get("drawdown_circuit_breaker") == -0.10
