from __future__ import annotations

from backtest.execution import ExecutionSimulator, LimitOrderBookExecution


def test_lob_single_level_fill():
    sim = ExecutionSimulator(participation_rate=1.0, lob_depth_levels=1, lob_market_impact_bps=0)
    r = sim.simulate_order("lob", "buy", 10.0, 100.0, bar_volume=1000.0)
    assert r["status"] == "filled"
    assert abs(r["filled_qty"]) == 10.0


def test_lob_multi_level_walk_with_market_impact():
    sim = ExecutionSimulator(participation_rate=1.0, lob_depth_levels=3, lob_market_impact_bps=10)
    r_buy = sim.simulate_order("lob", "buy", 10.0, 100.0, bar_volume=1000.0)
    r_sell = sim.simulate_order("lob", "sell", 10.0, 100.0, bar_volume=1000.0)
    # Buy walks ask side -> price up; sell walks bid side -> price down
    assert r_buy["avg_price"] > 100.0
    assert r_sell["avg_price"] < 100.0


def test_lob_partial_fill_when_depth_insufficient():
    sim = ExecutionSimulator(participation_rate=0.1, lob_depth_levels=1, lob_market_impact_bps=5)
    # With low participation and limited depth, may get partial fill
    r = sim.simulate_order("lob", "buy", 100.0, 100.0, bar_volume=10.0)
    assert r["status"] in ("partial", "filled")
    # If depth insufficient relative to order, partial expected
    if abs(r["filled_qty"]) < 100.0:
        assert r["status"] == "partial"


def test_lob_price_impact_direction():
    sim = ExecutionSimulator(participation_rate=1.0, lob_depth_levels=2, lob_market_impact_bps=5)
    r_buy = sim.simulate_order("lob", "buy", 5.0, 50.0, bar_volume=100.0)
    r_sell = sim.simulate_order("lob", "sell", 5.0, 50.0, bar_volume=100.0)
    assert r_buy["avg_price"] > 50.0  # buy pushes price up
    assert r_sell["avg_price"] < 50.0  # sell pushes price down


def test_lob_class_instantiation():
    lob = LimitOrderBookExecution(depth_levels=5, market_impact_bps=10, slippage_bps=2)
    assert lob.depth_levels == 5
    assert lob.market_impact_bps == 10
    assert lob.slippage_bps == 2
