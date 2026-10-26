from __future__ import annotations

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
