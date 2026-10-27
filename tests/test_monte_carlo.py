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
