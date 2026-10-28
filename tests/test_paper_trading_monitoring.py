"""Tests for real-time monitoring and alerting for paper trading."""

from __future__ import annotations

import contextlib
import io
import json

from backtest.cli import main
from backtest.monitoring import (
    Alert,
    AlertConfig,
    ConsoleAlertChannel,
    EmailAlertChannel,
    PaperTradingMonitor,
    WebhookAlertChannel,
    load_alert_config,
)


def _run_cli(argv: list[str]) -> str:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = main(argv)
    assert code == 0
    return buf.getvalue()


def test_alert_emitted_on_drawdown_breach():
    monitor = PaperTradingMonitor(
        config=AlertConfig(max_drawdown_pct=0.1, channels=["console"]),
        initial_capital=100_000.0,
    )
    # Establish a peak, then drop 20% (breach of 10% limit).
    monitor.update(equity=100_000.0)
    alerts = monitor.update(equity=80_000.0)
    assert len(alerts) == 1
    alert = alerts[0]
    assert isinstance(alert, Alert)
    assert alert.level == "error"
    assert alert.metric == "drawdown"
    assert alert.value == 0.2
    assert alert.threshold == 0.1
    assert len(monitor.alerts) == 1


def test_no_alert_when_within_thresholds():
    monitor = PaperTradingMonitor(
        config=AlertConfig(max_drawdown_pct=0.5, channels=["console"]),
        initial_capital=100_000.0,
    )
    monitor.update(equity=100_000.0)
    alerts = monitor.update(equity=90_000.0)
    assert alerts == []
    assert monitor.alerts == []


def test_alert_emitted_on_pnl_threshold():
    monitor = PaperTradingMonitor(
        config=AlertConfig(min_pnl_pct=-0.05, channels=["console"]),
        initial_capital=100_000.0,
    )
    positions = {
        "BTC": {"quantity": 1.0, "avg_cost": 100.0, "last_price": 90.0,
                "realized_pnl": -1000.0, "unrealized_pnl": -1000.0}
    }
    alerts = monitor.update(equity=98_000.0, positions=positions)
    pnl_alerts = [a for a in alerts if a.metric == "pnl"]
    assert len(pnl_alerts) == 1
    assert pnl_alerts[0].level == "warning"


def test_alert_emitted_on_position_size_limit():
    monitor = PaperTradingMonitor(
        config=AlertConfig(max_position_pct=0.1, channels=["console"]),
        initial_capital=100_000.0,
    )
    positions = {
        "BTC": {"quantity": 2.0, "avg_cost": 60_000.0, "last_price": 60_000.0,
                "realized_pnl": 0.0, "unrealized_pnl": 0.0}
    }
    # 2 * 60000 = 120000 > 10% of 100000 -> breach
    alerts = monitor.update(equity=100_000.0, positions=positions)
    pos_alerts = [a for a in alerts if a.metric == "position_size"]
    assert len(pos_alerts) == 1
    assert pos_alerts[0].symbol == "BTC"
    assert pos_alerts[0].level == "warning"


def test_alert_emitted_on_gross_exposure_limit():
    monitor = PaperTradingMonitor(
        config=AlertConfig(max_gross_exposure_pct=0.5, channels=["console"]),
        initial_capital=100_000.0,
    )
    positions = {
        "BTC": {"quantity": 1.0, "avg_cost": 60_000.0, "last_price": 60_000.0,
                "realized_pnl": 0.0, "unrealized_pnl": 0.0},
        "ETH": {"quantity": 5.0, "avg_cost": 4_000.0, "last_price": 4_000.0,
                "realized_pnl": 0.0, "unrealized_pnl": 0.0},
    }
    # gross = 60000 + 20000 = 80000 = 80% > 50% limit
    alerts = monitor.update(equity=100_000.0, positions=positions)
    exp_alerts = [a for a in alerts if a.metric == "gross_exposure"]
    assert len(exp_alerts) == 1
    assert exp_alerts[0].level == "warning"


def test_console_channel_emits_alert(capsys):
    channel = ConsoleAlertChannel()
    alert = Alert(
        alert_id="1", level="warning", message="test", timestamp="2024-01-01",
        metric="drawdown", value=0.2, threshold=0.1,
    )
    channel.send(alert)
    captured = capsys.readouterr()
    assert "[ALERT]" in captured.out
    assert "drawdown" in captured.out


def test_webhook_channel_best_effort_no_network():
    channel = WebhookAlertChannel(url="http://127.0.0.1:1/webhook")
    alert = Alert(
        alert_id="1", level="info", message="test", timestamp="2024-01-01",
        metric="drawdown", value=0.2, threshold=0.1,
    )
    # No server listening; must not raise.
    assert channel.send(alert) is False

    null_channel = WebhookAlertChannel(url=None)
    assert null_channel.send(alert) is False


def test_email_channel_best_effort_no_smtp():
    config = AlertConfig(smtp_host="127.0.0.1", smtp_port=1, alert_email="a@b.com")
    channel = EmailAlertChannel(config)
    alert = Alert(
        alert_id="1", level="info", message="test", timestamp="2024-01-01",
        metric="drawdown", value=0.2, threshold=0.1,
    )
    assert channel.send(alert) is False

    no_host = EmailAlertChannel(AlertConfig())
    assert no_host.send(alert) is False


def test_load_alert_config_from_json(tmp_path):
    cfg_path = tmp_path / "alerts.json"
    cfg_path.write_text(
        json.dumps(
            {
                "max_drawdown_pct": 0.2,
                "channels": ["console", "webhook"],
                "webhook_url": "http://example.com/hook",
                "smtp_port": 25,
            }
        )
    )
    config = load_alert_config(str(cfg_path))
    assert config.max_drawdown_pct == 0.2
    assert config.channels == ["console", "webhook"]
    assert config.webhook_url == "http://example.com/hook"
    assert config.smtp_port == 25


def test_load_alert_config_missing_file_backward_compat(tmp_path):
    missing = tmp_path / "does_not_exist.json"
    config = load_alert_config(str(missing))
    assert isinstance(config, AlertConfig)
    assert config.max_drawdown_pct is None
    assert config.channels == ["console"]


def test_load_alert_config_invalid_json_backward_compat(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{not valid json")
    config = load_alert_config(str(bad))
    assert isinstance(config, AlertConfig)


def test_monitor_peak_equity_and_drawdown_tracking():
    monitor = PaperTradingMonitor(
        config=AlertConfig(channels=["console"]),
        initial_capital=100_000.0,
    )
    monitor.update(equity=110_000.0)  # new peak
    assert monitor.peak_equity == 110_000.0
    assert monitor.get_drawdown() == 0.0
    monitor.update(equity=90_000.0)  # drawdown from 110k peak
    assert monitor.get_drawdown() > 0.0
    assert len(monitor.equity_history) == 2


def test_monitor_summary_is_serializable():
    monitor = PaperTradingMonitor(
        config=AlertConfig(max_drawdown_pct=0.1, channels=["console"]),
        initial_capital=100_000.0,
    )
    monitor.update(equity=95_000.0)
    summary = monitor.get_summary()
    assert "initial_capital" in summary
    assert "peak_equity" in summary
    assert "equity" in summary
    assert "drawdown" in summary
    assert "total_alerts" in summary
    assert "alerts" in summary
    json.dumps(summary)  # must be JSON-serializable


def test_paper_trade_cli_with_monitor(tmp_path):
    out = tmp_path / "paper_monitor.json"
    cfg = tmp_path / "alerts.json"
    cfg.write_text(json.dumps({"max_drawdown_pct": 0.01}))
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
            "--fee-rate",
            "0.001",
            "--slippage",
            "0.0005",
            "--monitor",
            "--alert-config",
            str(cfg),
            "--output-path",
            str(out),
        ]
    )
    assert out.exists()
    data = json.loads(out.read_text())
    assert "monitoring" in data
    assert "total_alerts" in data["monitoring"]
    assert isinstance(data["monitoring"]["alerts"], list)
