from __future__ import annotations

import numpy as np
import pandas as pd

from backtest.engine import BacktestEngine
from backtest.execution import ExecutionSimulator


def test_vwap_fill_price_differs_from_market():
    sim = ExecutionSimulator(order_type="vwap", participation_rate=1.0, slippage_bps=0)
    r = sim.simulate_order(
        "vwap", "buy", 10.0, 100.0, bar_volume=1000.0,
        bar_high=110.0, bar_low=90.0)
    assert r["status"] == "filled"
    assert r["avg_price"] == (110.0 + 90.0 + 100.0) / 3.0


def test_twap_fill_price_differs_from_market():
    sim = ExecutionSimulator(order_type="twap", participation_rate=1.0, slippage_bps=0)
    r = sim.simulate_order(
        "twap", "buy", 10.0, 100.0, bar_volume=1000.0,
        bar_high=110.0, bar_low=90.0)
    assert r["status"] == "filled"
    assert r["avg_price"] == (110.0 + 90.0) / 2.0


def test_vwap_partial_fill_respects_participation():
    sim = ExecutionSimulator(order_type="vwap", participation_rate=0.05, slippage_bps=0)
    r = sim.simulate_order(
        "vwap", "buy", 100.0, 100.0, bar_volume=100.0,
        bar_high=110.0, bar_low=90.0)
    assert r["status"] == "partial"
    assert abs(r["filled_qty"]) == 5.0


def test_vwap_twap_differ_from_market_fill():
    data_price = 100.0
    sim_m = ExecutionSimulator(order_type="market", participation_rate=1.0, slippage_bps=0)
    sim_v = ExecutionSimulator(order_type="vwap", participation_rate=1.0, slippage_bps=0)
    sim_t = ExecutionSimulator(order_type="twap", participation_rate=1.0, slippage_bps=0)
    rm = sim_m.simulate_order(
        "market", "buy", 10.0, data_price, bar_volume=1000.0,
        bar_high=110.0, bar_low=95.0)
    rv = sim_v.simulate_order(
        "vwap", "buy", 10.0, data_price, bar_volume=1000.0,
        bar_high=110.0, bar_low=95.0)
    rt = sim_t.simulate_order(
        "twap", "buy", 10.0, data_price, bar_volume=1000.0,
        bar_high=110.0, bar_low=95.0)
    assert rm["avg_price"] != rv["avg_price"]
    assert rm["avg_price"] != rt["avg_price"]
    assert rv["avg_price"] != rt["avg_price"]


def _make_data(n: int = 200, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2024-01-01", periods=n, freq="1h")
    return pd.DataFrame(
        {"BTC": 100 * np.exp(np.cumsum(rng.normal(0.0, 0.02, n)))},
        index=dates,
    )


def test_engine_vwap_end_to_end():
    data = _make_data()
    weights = pd.DataFrame(1.0, index=data.index, columns=data.columns)
    engine = BacktestEngine(initial_capital=100_000.0)
    sim = ExecutionSimulator(order_type="vwap", slippage_bps=5)
    result = engine.run_portfolio(weights, data, execution_simulator=sim)
    assert "total_return" in result


def test_engine_twap_end_to_end():
    data = _make_data()
    weights = pd.DataFrame(1.0, index=data.index, columns=data.columns)
    engine = BacktestEngine(initial_capital=100_000.0)
    sim = ExecutionSimulator(order_type="twap", slippage_bps=5)
    result = engine.run_portfolio(weights, data, execution_simulator=sim)
    assert "total_return" in result
