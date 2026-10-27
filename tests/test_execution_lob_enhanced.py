from __future__ import annotations

from backtest.execution import ExecutionSimulator, LimitOrderBookExecution


def _sim(sim_kwargs: dict, **order_kwargs) -> dict:
    sim = ExecutionSimulator(**sim_kwargs)
    return sim.simulate_order("lob", **order_kwargs)


def test_lob_per_level_liquidity_enforcement():
    # Two levels of 5.0 each fill a 10.0 order exactly across 2 levels.
    r = _sim(
        {"lob_level_liquidity": [5.0, 5.0, 5.0], "lob_depth_levels": 3,
         "lob_market_impact_bps": 0},
        side="buy", quantity=10.0, price=100.0,
    )
    assert r["status"] == "filled"
    assert abs(r["filled_qty"]) == 10.0
    assert r["remaining_qty"] == 0.0


def test_lob_multi_level_consumption_with_impact_per_level():
    # 100 bps impact per walked level: 1 level walked -> +1%, 2 levels -> +2%.
    r1 = _sim(
        {"lob_level_liquidity": [10.0, 10.0], "lob_depth_levels": 2,
         "lob_market_impact_bps": 100},
        side="buy", quantity=10.0, price=100.0,
    )
    assert r1["status"] == "filled"
    assert abs(r1["filled_qty"]) == 10.0
    assert abs(r1["avg_price"] - 101.0) < 1e-9

    r2 = _sim(
        {"lob_level_liquidity": [10.0, 10.0], "lob_depth_levels": 2,
         "lob_market_impact_bps": 100},
        side="buy", quantity=20.0, price=100.0,
    )
    assert r2["status"] == "filled"
    assert abs(r2["filled_qty"]) == 20.0
    assert abs(r2["avg_price"] - 102.0) < 1e-9


def test_lob_insufficient_liquidity_partial_fill():
    # Total book liquidity 6.0 < order 10.0 -> partial fill.
    r = _sim(
        {"lob_level_liquidity": [2.0, 2.0, 2.0], "lob_depth_levels": 3,
         "lob_market_impact_bps": 0},
        side="buy", quantity=10.0, price=100.0,
    )
    assert r["status"] == "partial"
    assert abs(r["filled_qty"]) == 6.0
    assert abs(r["remaining_qty"]) == 4.0


def test_lob_queue_position_reduces_first_level_fill():
    # queue_position=0.5 -> only half of first level fillable.
    r = _sim(
        {"lob_level_liquidity": [10.0], "lob_depth_levels": 1,
         "lob_queue_position": 0.5, "lob_market_impact_bps": 0},
        side="buy", quantity=10.0, price=100.0,
    )
    assert r["status"] == "partial"
    assert abs(r["filled_qty"]) == 5.0


def test_lob_queue_position_full_blocks_first_level():
    # queue_position=1.0 -> nothing fillable at first level.
    r = _sim(
        {"lob_level_liquidity": [10.0], "lob_depth_levels": 1,
         "lob_queue_position": 1.0, "lob_market_impact_bps": 0},
        side="buy", quantity=10.0, price=100.0,
    )
    assert r["status"] == "partial"
    assert abs(r["filled_qty"]) == 0.0


def test_lob_queue_position_and_level_liquidity_combined():
    # queue_position halves first level; remaining fills from second level.
    r = _sim(
        {"lob_level_liquidity": [10.0, 10.0], "lob_depth_levels": 2,
         "lob_queue_position": 0.5, "lob_market_impact_bps": 0},
        side="buy", quantity=15.0, price=100.0,
    )
    assert r["status"] == "filled"
    assert abs(r["filled_qty"]) == 15.0


def test_lob_level_liquidity_ignores_volume_cap():
    # Explicit level liquidity takes precedence even with zero bar volume.
    r = _sim(
        {"lob_level_liquidity": [10.0], "lob_depth_levels": 1,
         "lob_market_impact_bps": 0},
        side="buy", quantity=10.0, price=100.0, bar_volume=0.0,
    )
    assert r["status"] == "filled"
    assert abs(r["filled_qty"]) == 10.0


def test_lob_empty_level_liquidity_partial():
    # No liquidity at any level -> nothing fills.
    r = _sim(
        {"lob_level_liquidity": [], "lob_depth_levels": 3,
         "lob_market_impact_bps": 0},
        side="buy", quantity=10.0, price=100.0,
    )
    assert r["status"] == "partial"
    assert abs(r["filled_qty"]) == 0.0


def test_lob_backward_compat_without_level_liquidity():
    # No level_liquidity -> volume-proxy logic unchanged.
    r = _sim(
        {"participation_rate": 1.0, "lob_depth_levels": 1,
         "lob_market_impact_bps": 0},
        side="buy", quantity=10.0, price=100.0, bar_volume=1000.0,
    )
    assert r["status"] == "filled"
    assert abs(r["filled_qty"]) == 10.0


def test_lob_queue_position_validation_clamped():
    # Negative queue_position clamps to 0.0 (no penalty).
    sim_neg = ExecutionSimulator(
        lob_level_liquidity=[10.0], lob_depth_levels=1,
        lob_queue_position=-0.5, lob_market_impact_bps=0,
    )
    assert sim_neg._lob.queue_position == 0.0
    r_neg = sim_neg.simulate_order("lob", "buy", 10.0, 100.0)
    assert abs(r_neg["filled_qty"]) == 10.0

    # queue_position > 1 clamps to 1.0 (fully blocked at first level).
    sim_high = ExecutionSimulator(
        lob_level_liquidity=[10.0], lob_depth_levels=1,
        lob_queue_position=1.5, lob_market_impact_bps=0,
    )
    assert sim_high._lob.queue_position == 1.0
    r_high = sim_high.simulate_order("lob", "buy", 10.0, 100.0)
    assert abs(r_high["filled_qty"]) == 0.0


def test_lob_limit_order_book_execution_fields():
    lob = LimitOrderBookExecution(
        depth_levels=4, market_impact_bps=7, slippage_bps=1,
        participation_rate=0.5, level_liquidity=[1.0, 2.0],
        queue_position=0.25,
    )
    assert lob.level_liquidity == [1.0, 2.0]
    assert lob.queue_position == 0.25
