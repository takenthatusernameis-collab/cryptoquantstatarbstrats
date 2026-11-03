from __future__ import annotations

import numpy as np
import pandas as pd

from utils.monte_carlo import bootstrap_trade_returns, monte_carlo_analysis


def test_bootstrap_trade_returns_basic():
    trades = [0.01, -0.005, 0.002, 0.01, -0.001]
    res = bootstrap_trade_returns(trades, n_simulations=100, seed=123)
    assert res["n_simulations"] == 100
    assert "final_equity" in res
    assert "max_drawdown" in res
    assert "sharpe_ratio" in res
    assert "mean" in res["final_equity"]


def test_bootstrap_trade_returns_shuffle():
    trades = [0.01, -0.005, 0.002]
    res = bootstrap_trade_returns(trades, n_simulations=50, method="shuffle", seed=42)
    assert res["method"] == "shuffle"
    assert isinstance(res["final_equity"]["mean"], float)


def test_bootstrap_trade_returns_empty():
    res = bootstrap_trade_returns([], n_simulations=10)
    assert res["final_equity"]["mean"] == 0.0
    assert res["max_drawdown"]["mean"] == 0.0
    assert res["sharpe_ratio"]["mean"] == 0.0


def test_monte_carlo_analysis_with_returns():
    rng = np.random.default_rng(0)
    returns = rng.normal(0.0005, 0.01, 252)
    res = monte_carlo_analysis(returns=returns, n_simulations=200, seed=7)
    assert res["n_simulations"] == 200
    assert res["final_equity"]["mean"] > 0


def test_monte_carlo_analysis_with_equity_curve():
    eq = pd.Series((1.0 + np.array([0.01, -0.002, 0.005, 0.003, -0.001])).cumprod())
    res = monte_carlo_analysis(equity_curve=eq, n_simulations=50, seed=9)
    assert "final_equity" in res


def test_monte_carlo_analysis_with_trade_returns():
    trades = pd.Series([0.002, -0.001, 0.003, -0.0005])
    res = monte_carlo_analysis(trade_returns=trades, n_simulations=30, seed=11)
    assert res["n_simulations"] == 30


def test_bootstrap_provenance_present_on_real_input():
    """Every Monte Carlo result carries real-data-only provenance."""
    trades = [0.01, -0.005, 0.002, 0.01, -0.001]
    res = bootstrap_trade_returns(trades, n_simulations=50, seed=123)
    prov = res.get("provenance") or {}
    assert prov.get("real_data_only") is True
    assert prov.get("fabricated_data") is False
    assert isinstance(prov.get("source"), str) and prov["source"]
    assert isinstance(prov.get("computed_at"), str) and prov["computed_at"]
    assert isinstance(prov.get("blocked_routes"), list)
    assert isinstance(prov.get("rationale"), str) and prov["rationale"]
    # On real input nothing is blocked.
    assert prov["blocked_routes"] == []


def test_bootstrap_empty_input_records_blocked_routes():
    """An empty/blocked input must NOT masquerade as computeable.

    The zeroed-out metrics are honest only because ``blocked_routes`` lists
    every affected metric family. This is fail-closed: a downstream artifact
    reading this result can see exactly what could not be computed.
    """
    res = bootstrap_trade_returns([], n_simulations=10)
    prov = res.get("provenance") or {}
    assert prov.get("real_data_only") is True
    assert prov.get("fabricated_data") is False
    assert prov.get("error") == "empty_input_no_real_returns"
    blocked = set(prov.get("blocked_routes", []))
    assert {"final_equity", "max_drawdown", "sharpe_ratio", "risk_of_ruin"} <= blocked


def test_monte_carlo_analysis_no_input_is_fail_closed_with_provenance():
    res = monte_carlo_analysis(n_simulations=10, seed=1)
    prov = res.get("provenance") or {}
    assert prov.get("real_data_only") is True
    assert prov.get("fabricated_data") is False
    assert prov.get("error") == "no_real_input_series"
    assert set(prov.get("blocked_routes", [])) >= {
        "final_equity",
        "max_drawdown",
        "sharpe_ratio",
        "risk_of_ruin",
    }


def test_permutation_test_provenance():
    from utils.monte_carlo import permutation_test_distinguishability

    res = permutation_test_distinguishability([0.01, -0.005, 0.002], n_permutations=50, seed=7)
    prov = res.get("provenance") or {}
    assert prov.get("real_data_only") is True
    assert prov.get("fabricated_data") is False
    assert isinstance(prov.get("source"), str) and prov["source"]
    assert prov["blocked_routes"] == []


def test_permutation_test_empty_input_records_blocked_routes():
    from utils.monte_carlo import permutation_test_distinguishability

    res = permutation_test_distinguishability([], n_permutations=10)
    prov = res.get("provenance") or {}
    assert prov.get("error") == "empty_input_no_real_returns"
    assert set(prov.get("blocked_routes", [])) >= {"observed_mean", "p_value"}


def test_tail_risk_provenance():
    from utils.monte_carlo import tail_risk_metrics

    res = tail_risk_metrics([0.01, -0.005, 0.002])
    prov = res.get("provenance") or {}
    assert prov.get("real_data_only") is True
    assert prov.get("fabricated_data") is False
    assert isinstance(prov.get("source"), str) and prov["source"]
    assert prov["blocked_routes"] == []


def test_tail_risk_empty_input_records_blocked_routes():
    from utils.monte_carlo import tail_risk_metrics

    res = tail_risk_metrics([])
    prov = res.get("provenance") or {}
    assert prov.get("error") == "empty_input_no_real_returns"
    assert set(prov.get("blocked_routes", [])) >= {"var", "cvar", "cdar"}
