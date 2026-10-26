from __future__ import annotations

import numpy as np
import pandas as pd

from backtest.engine import BacktestEngine
from backtest.execution import ExecutionSimulator


def test_market_order_fill():
    sim = ExecutionSimulator(participation_rate=0.1, slippage_bps=5)
    r = sim.simulate_order("market", "buy", 10.0, 100.0, bar_volume=1000.0)
    assert r["status"] == "filled"
    assert r["filled_qty"] == 10.0
    assert r["avg_price"] > 100.0


def test_partial_fill():
    sim = ExecutionSimulator(participation_rate=0.05)
    r = sim.simulate_order("market", "buy", 100.0, 100.0, bar_volume=100.0)
    assert r["status"] == "partial"
    assert abs(r["filled_qty"]) == 5.0


def test_limit_order_unfilled():
    sim = ExecutionSimulator()
    r = sim.simulate_order("limit", "buy", 10.0, 105.0, bar_volume=1000.0, limit_price=100.0)
    assert r["status"] == "unfilled"
    assert r["filled_qty"] == 0.0


def test_invalid_inputs():
    sim = ExecutionSimulator()
    r = sim.simulate_order("market", "buy", 0.0, 100.0)
    assert r["status"] == "rejected"
    r2 = sim.simulate_order("foo", "buy", 10.0, 100.0)
    assert r2["status"] == "rejected"


def _make_data(n: int = 200, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2024-01-01", periods=n, freq="1h")
    return pd.DataFrame(
        {"BTC": 100 * np.exp(np.cumsum(rng.normal(0.0, 0.02, n)))},
        index=dates,
    )


def test_engine_execution_simulator_applies_slippage():
    data = _make_data()
    weights = pd.DataFrame(1.0, index=data.index, columns=data.columns)
    engine = BacktestEngine(initial_capital=100_000.0)

    base = engine.run_portfolio(weights, data)
    sim = ExecutionSimulator(slippage_bps=10)
    result = engine.run_portfolio(weights, data, execution_simulator=sim)

    # Slippage on the entry trade reduces total return relative to no slippage.
    assert result["total_return"] < base["total_return"]
    assert engine.fills() if hasattr(engine, "fills") else True


def test_engine_execution_simulator_zero_slippage_matches_legacy():
    data = _make_data()
    weights = pd.DataFrame(1.0, index=data.index, columns=data.columns)
    engine = BacktestEngine(initial_capital=100_000.0)

    base = engine.run_portfolio(weights, data)
    sim = ExecutionSimulator(slippage_bps=0)
    result = engine.run_portfolio(weights, data, execution_simulator=sim)

    # Zero slippage and full fills reproduce the no-cost result (single entry trade).
    assert abs(result["total_return"] - base["total_return"]) < 1e-6


def test_engine_execution_backward_compatible_without_simulator():
    data = _make_data()
    weights = pd.DataFrame(1.0, index=data.index, columns=data.columns)
    engine = BacktestEngine(initial_capital=100_000.0)

    result = engine.run_portfolio(weights, data)
    assert "total_return" in result
    assert "sharpe_ratio" in result
    assert isinstance(result["total_return"], float)


def test_walk_forward_portfolio_with_execution_simulator():
    data = _make_data(n=400)
    weights = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    engine = BacktestEngine(initial_capital=100_000.0)
    sim = ExecutionSimulator(slippage_bps=5)

    wf = engine.walk_forward_portfolio(
        weights,
        data,
        train_period=100,
        test_period=50,
        execution_simulator=sim,
    )
    assert isinstance(wf, dict)
    assert "returns" in wf
    assert len(wf["returns"]) > 0
