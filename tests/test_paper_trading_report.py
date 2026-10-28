"""Tests for paper-trading session reporting and artifact persistence."""

from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path

from backtest.cli import main
from backtest.paper_report import (
    build_paper_trading_report,
    generate_paper_trading_report_html,
    generate_paper_trading_report_text,
    load_paper_trading_artifacts,
    paper_report_to_dict,
    save_paper_trading_artifacts,
)


def _run_cli(argv: list[str]) -> str:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = main(argv)
    assert code == 0
    return buf.getvalue()


def test_build_paper_trading_report_basic():
    report = build_paper_trading_report(
        session_summary={
            "initial_capital": 100000.0,
            "fills": [{"symbol": "BTC", "side": "buy", "quantity": 1.0, "price": 50000.0}],
            "realized_pnl": -10.0,
            "num_fills": 1,
        },
        fills=[{"symbol": "BTC", "side": "buy", "quantity": 1.0, "price": 50000.0}],
        equity_curve=[{"timestamp": "2024-01-01T00:00:00", "equity": 99990.0}],
        positions={"BTC": {"quantity": 1.0, "avg_cost": 50000.0, "unrealized_pnl": 0.0}},
        monitoring={"alerts": [{"alert_id": "a1", "level": "info"}], "total_alerts": 1},
    )
    assert isinstance(report, dict)
    assert "session_summary" in report
    assert "fills" in report
    assert "equity_curve" in report
    assert "positions" in report
    assert "monitoring" in report
    text = generate_paper_trading_report_text(report)
    assert "Paper Trading Report" in text
    html = generate_paper_trading_report_html(report)
    assert "<html" in html


def test_artifact_persistence_and_load(tmp_path):
    report = build_paper_trading_report(
        session_summary={"initial_capital": 50000.0},
        fills=[{"order_id": 1, "symbol": "ETH"}],
        equity_curve=[{"timestamp": "2024-01-01", "equity": 50000.0}],
        monitoring={"alerts": []},
    )
    saved = save_paper_trading_artifacts(report, tmp_path)
    assert "report" in saved
    assert Path(saved["report"]).exists()
    loaded = load_paper_trading_artifacts(tmp_path)
    assert isinstance(loaded, dict)
    assert "fills" in loaded


def test_paper_report_missing_data_backward_compat(tmp_path):
    # Load from empty dir should not crash
    loaded = load_paper_trading_artifacts(tmp_path)
    assert isinstance(loaded, dict)
    # Build with missing data
    report = build_paper_trading_report()
    d = paper_report_to_dict(report)
    assert isinstance(d, dict)


def test_cli_paper_trade_persists_artifacts_and_paper_report_subcommand(tmp_path):
    out = tmp_path / "paper.json"
    ad = tmp_path / "artifacts"
    ad.mkdir()
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
            "100000",
            "--output-path",
            str(out),
            "--artifact-dir",
            str(ad),
            "--monitor",
        ]
    )
    assert out.exists()
    assert (ad / "paper_trading_report.json").exists()
    assert (ad / "paper_trading_fills.json").exists()
    assert (ad / "paper_trading_alerts.json").exists()
    assert (ad / "paper_trading_equity_curve.json").exists()

    text_out = _run_cli(["paper-report", "--artifact-dir", str(ad), "--format", "text"])
    assert "Paper Trading Report" in text_out
    html_out = _run_cli(["paper-report", "--artifact-dir", str(ad), "--format", "html"])
    assert "<html" in html_out
    json_out = _run_cli(["paper-report", "--artifact-dir", str(ad), "--format", "json"])
    data = json.loads(json_out)
    assert isinstance(data, dict)
