"""Tests for paper-trading execution integration."""

from __future__ import annotations

import contextlib
import io
import json

import numpy as np
import pandas as pd

from backtest.cli import main
from backtest.execution import ExecutionSimulator


def _run_cli(argv: list[str]) -> str:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = main(argv)
    assert code == 0
    return buf.getvalue()


def test_execution_simulator_emits_fill_records_with_metadata():
    sim = ExecutionSimulator(participation_rate=0.1)
    res = sim.simulate_order(
        "market",
        "buy",
        1.0,
        100.0,
        bar_volume=10.0,
        order_id=1,
        symbol="BTC",
        timestamp="2024-01-01T00:00:00",
        fee_rate=0.001,
    )
    assert isinstance(res, dict)
    assert "filled_qty" in res
    assert "avg_price" in res
    assert "status" in res
    fills = sim.fills()
    assert len(fills) == 1
    f = fills[0]
    for key in ["order_id", "symbol", "side", "timestamp", "fee_rate", "order_type"]:
        assert key in f
    assert f["order_id"] == 1
    assert f["symbol"] == "BTC"
    assert f["side"] == "buy"
    assert "fee" in f


def test_paper_trading_pnl_summary():
    sim = ExecutionSimulator(participation_rate=1.0, slippage_bps=0.0)
    sim.simulate_order(
        "market",
        "buy",
        2.0,
        50.0,
        bar_volume=100.0,
        order_id=10,
        symbol="ETH",
        timestamp="2024-01-01T01:00:00",
        fee_rate=0.001,
    )
    fills = sim.fills()
    assert len(fills) == 1
    fee = fills[0].get("fee", 0.0)
    # fee should be qty * price * fee_rate
    assert abs(fee - 2.0 * 50.0 * 0.001) < 1e-9


def test_paper_trading_missing_data_backward_compat():
    sim = ExecutionSimulator()
    # Old style call without metadata
    res = sim.simulate_order("market", "buy", 1.0, 100.0)
    assert isinstance(res, dict)
    fills = sim.fills()
    # Should still record something for backward compat
    assert isinstance(fills, list)


def test_paper_trade_cli_integration_synthetic(tmp_path):
    out = tmp_path / "paper.json"
    content = _run_cli(
        [
            "paper-trade",
            "--symbols",
            "BTC",
            "ETH",
            "--data-source",
            "synthetic",
            "--strategy",
            "mean_reversion",
            "--start",
            "2024-01-01",
            "--end",
            "2024-01-03",
            "--freq",
            "1h",
            "--initial-capital",
            "100000",
            "--fee-rate",
            "0.001",
            "--slippage",
            "0.0005",
            "--output-path",
            str(out),
        ]
    )
    # Should either write to file or print; file should exist
    assert out.exists()
    data = json.loads(out.read_text())
    assert "fills" in data
    assert "realized_pnl" in data
    assert "num_fills" in data
    assert "initial_capital" in data
    assert isinstance(data["fills"], list)
