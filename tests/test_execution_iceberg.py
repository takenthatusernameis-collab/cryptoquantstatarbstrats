from __future__ import annotations

from backtest.execution import ExecutionSimulator, IcebergExecution


def test_iceberg_partial_replenishment():
    sim = ExecutionSimulator(participation_rate=0.1, iceberg_visible_qty=10.0)
    # Large order with limited volume - should result in partial fill
    r = sim.simulate_order("iceberg", "buy", 100.0, 100.0, bar_volume=50.0)
    # With participation 0.1 and vol 50, max fill = 5.0
    assert abs(r["filled_qty"]) == 5.0
    assert r["status"] == "partial"


def test_iceberg_full_fill():
    sim = ExecutionSimulator(participation_rate=1.0, iceberg_visible_qty=10.0)
    r = sim.simulate_order("iceberg", "buy", 10.0, 100.0, bar_volume=1000.0)
    assert r["status"] == "filled"
    assert abs(r["filled_qty"]) == 10.0


def test_iceberg_min_fill_constraints():
    sim = ExecutionSimulator(participation_rate=0.01, iceberg_visible_qty=5.0, iceberg_min_fill=2.0)
    # Max fill would be 1.0 with low participation - below min_fill, should be unfilled
    r = sim.simulate_order("iceberg", "buy", 100.0, 100.0, bar_volume=100.0)
    # participation 0.01 * 100 = 1.0 < min_fill 2.0 and not completing order
    assert r["status"] == "unfilled"
    assert r["filled_qty"] == 0.0


def test_iceberg_price_offset_application():
    sim = ExecutionSimulator(participation_rate=1.0, iceberg_price_offset_bps=10)
    r = sim.simulate_order("iceberg", "buy", 5.0, 100.0, bar_volume=1000.0)
    # Base price 100, +10bps = 100.1
    assert r["avg_price"] > 100.0
    assert abs(r["avg_price"] - 100.1) < 1e-6


def test_iceberg_with_absolute_price_offset():
    sim = ExecutionSimulator(participation_rate=1.0, iceberg_price_offset_absolute=0.5)
    r = sim.simulate_order("iceberg", "buy", 5.0, 100.0, bar_volume=1000.0)
    assert abs(r["avg_price"] - 100.5) < 1e-6


def test_iceberg_class_instantiation():
    ice = IcebergExecution(visible_qty=10, min_fill=1, price_offset_bps=5)
    assert ice.visible_qty == 10
    assert ice.min_fill == 1
    assert ice.price_offset_bps == 5
