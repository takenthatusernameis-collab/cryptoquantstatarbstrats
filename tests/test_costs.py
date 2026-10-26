"""
Tests for transaction cost models.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from backtest.engine import BacktestEngine
from strategies.mean_reversion import MeanReversionStrategy
from utils.costs import FixedCostModel, SquareRootImpactCostModel


def test_fixed_cost_model_basic():
    model = FixedCostModel(fee_rate=0.001, slippage=0.0005)
    assert model.compute_cost(0.0) == 0.0
    assert model.compute_cost(1.0) == 0.0015
    assert model.compute_cost(2.0) == 0.003


def test_fixed_cost_model_invalid_inputs():
    model = FixedCostModel()
    assert model.compute_cost(None) == 0.0
    assert model.compute_cost(float("nan")) == 0.0
    assert model.compute_cost(-0.5) == 0.0
    assert model.compute_cost(float("inf")) == 0.0


def test_fixed_cost_model_series():
    model = FixedCostModel(fee_rate=0.001, slippage=0.0)
    series = pd.Series([0.0, 0.5, 1.0, 2.0])
    result = model.compute_cost_series(series)
    assert isinstance(result, pd.Series)
    assert len(result) == len(series)
    assert result.iloc[0] == 0.0
    assert result.iloc[2] == 0.001


def test_square_root_impact_basic():
    model = SquareRootImpactCostModel(fee_rate=0.0, impact_coeff=0.05)
    # fee_rate=0 so cost = 0.05 * sqrt(turnover)
    assert model.compute_cost(0.0) == 0.0
    assert abs(model.compute_cost(1.0) - 0.05) < 1e-12
    assert abs(model.compute_cost(4.0) - 0.10) < 1e-12


def test_square_root_impact_with_fees():
    model = SquareRootImpactCostModel(fee_rate=0.001, impact_coeff=0.05)
    cost = model.compute_cost(1.0)
    expected = 0.001 * 1.0 + 0.05 * math.sqrt(1.0)
    assert abs(cost - expected) < 1e-12


def test_square_root_impact_invalid_inputs():
    model = SquareRootImpactCostModel()
    assert model.compute_cost(None) == 0.0
    assert model.compute_cost(float("nan")) == 0.0
    assert model.compute_cost(-0.5) == 0.0


def test_cost_model_repr():
    assert "FixedCostModel" in repr(FixedCostModel())
    assert "SquareRootImpactCostModel" in repr(SquareRootImpactCostModel())


def test_engine_cost_model_reduces_returns():
    rng = np.random.default_rng(42)
    n = 300
    dates = pd.date_range("2024-01-01", periods=n, freq="1h")
    df = pd.DataFrame(
        {"BTC": 100 * np.exp(np.cumsum(rng.normal(0.0, 0.02, n)))},
        index=dates,
    )
    strat = MeanReversionStrategy("BTC")
    engine = BacktestEngine(initial_capital=100_000)

    result_no_cost = engine.run(strat, df)
    result_with_cost = engine.run(
        strat, df, cost_model=FixedCostModel(fee_rate=0.001, slippage=0.0005)
    )
    assert result_with_cost["total_return"] <= result_no_cost["total_return"]


def test_engine_cost_model_backward_compatible():
    """Legacy fee_rate/slippage params still work without cost_model."""
    rng = np.random.default_rng(42)
    n = 300
    dates = pd.date_range("2024-01-01", periods=n, freq="1h")
    df = pd.DataFrame(
        {"BTC": 100 * np.exp(np.cumsum(rng.normal(0.0, 0.02, n)))},
        index=dates,
    )
    strat = MeanReversionStrategy("BTC")
    engine = BacktestEngine(initial_capital=100_000)

    result_legacy = engine.run(strat, df, fee_rate=0.001, slippage=0.0005)
    result_model = engine.run(
        strat, df, cost_model=FixedCostModel(fee_rate=0.001, slippage=0.0005)
    )
    assert abs(result_legacy["total_return"] - result_model["total_return"]) < 1e-12


def test_engine_cost_model_walk_forward():
    rng = np.random.default_rng(42)
    n = 600
    dates = pd.date_range("2024-01-01", periods=n, freq="1h")
    df = pd.DataFrame(
        {"BTC": 100 * np.exp(np.cumsum(rng.normal(0.0, 0.02, n)))},
        index=dates,
    )
    strat = MeanReversionStrategy("BTC")
    engine = BacktestEngine(initial_capital=100_000)

    wf = engine.walk_forward(
        strat,
        df,
        train_period=200,
        test_period=50,
        cost_model=FixedCostModel(fee_rate=0.001, slippage=0.0005),
    )
    assert isinstance(wf, dict)
    assert "returns" in wf
    assert isinstance(wf["returns"], list)
    assert len(wf["returns"]) > 0


def test_engine_cost_model_with_benchmark():
    rng = np.random.default_rng(42)
    n = 300
    dates = pd.date_range("2024-01-01", periods=n, freq="1h")
    df = pd.DataFrame(
        {"BTC": 100 * np.exp(np.cumsum(rng.normal(0.0, 0.02, n)))},
        index=dates,
    )
    strat = MeanReversionStrategy("BTC")
    engine = BacktestEngine(initial_capital=100_000)

    result = engine.run_with_benchmark(
        strat, df, cost_model=FixedCostModel(fee_rate=0.001, slippage=0.0005)
    )
    assert "benchmark_total_return" in result
    assert "benchmark_equity_curve" in result
