"""Tests for advanced paper-trading features."""

from __future__ import annotations

import contextlib
import io
import json

from backtest.cli import main
from backtest.execution import ExecutionSimulator, Order


def _run_cli(argv: list[str]) -> str:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = main(argv)
    assert code == 0
    return buf.getvalue()


def test_order_management_create_and_cancel():
    sim = ExecutionSimulator()
    order = sim.create_order("BTC", "buy", 1.0, order_type="limit", limit_price=50000)
    assert isinstance(order, Order)
    assert order.symbol == "BTC"
    assert order.side == "buy"
    assert order.status == "open"
    assert sim.get_order(order.order_id) is not None
    open_orders = sim.get_open_orders()
    assert len(open_orders) == 1
    cancelled = sim.cancel_order(order.order_id)
    assert cancelled
    assert sim.get_order(order.order_id).status == "cancelled"


def test_order_submission_updates_position():
    sim = ExecutionSimulator(participation_rate=1.0, slippage_bps=0.0)
    order = sim.create_order("ETH", "buy", 2.0)
    res = sim.submit_order(order, price=50.0, bar_volume=100.0)
    assert res["status"] in ("filled", "partial")
    pos = sim.get_position("ETH")
    assert pos is not None
    assert pos.quantity != 0


def test_position_tracking_and_risk_metrics():
    sim = ExecutionSimulator(participation_rate=1.0)
    sim.simulate_order("market", "buy", 1.0, 100.0, bar_volume=1000.0, symbol="BTC")
    sim.simulate_order("market", "sell", 0.5, 110.0, bar_volume=1000.0, symbol="ETH")
    positions = sim.get_positions()
    assert isinstance(positions, dict)
    metrics = sim.get_risk_metrics()
    assert "num_positions" in metrics
    assert "gross_exposure" in metrics
    assert "net_exposure" in metrics
    assert "realized_pnl" in metrics
    assert "unrealized_pnl" in metrics


def test_paper_trade_cli_with_advanced_options(tmp_path):
    out = tmp_path / "paper_adv.json"
    _run_cli(
        [
            "paper-trade",
            "--symbols",
            "BTC",
            "--data-source",
            "synthetic",
            "--strategy",
            "mean_reversion",
            "--start",
            "2024-01-01",
            "--end",
            "2024-01-02",
            "--freq",
            "1h",
            "--initial-capital",
            "50000",
            "--fee-rate",
            "0.001",
            "--slippage",
            "0.0005",
            "--max-position",
            "0.1",
            "--position-sizing",
            "fixed",
            "--output-path",
            str(out),
        ]
    )
    assert out.exists()
    data = json.loads(out.read_text())
    assert "fills" in data
    assert "positions" in data
    assert "risk_metrics" in data
    assert "portfolio_value" in data
