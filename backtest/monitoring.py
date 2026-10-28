"""Real-time monitoring and alerting for paper trading sessions.

Tracks portfolio metrics (equity, drawdown, realized/unrealized PnL,
exposure) during a paper-trading session and emits alerts through
configurable channels (console, webhook, email) when thresholds are breached.
All external delivery (webhook/email) is best-effort and never raises.
"""

from __future__ import annotations

import json
import smtplib
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from email.message import EmailMessage
from typing import Any


@dataclass
class Alert:
    """A single alert emitted by the monitoring system."""

    alert_id: str
    level: str  # info, warning, error, critical
    message: str
    timestamp: str
    metric: str
    value: float
    threshold: float
    symbol: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "level": self.level,
            "message": self.message,
            "timestamp": self.timestamp,
            "metric": self.metric,
            "value": self.value,
            "threshold": self.threshold,
            "symbol": self.symbol,
            "metadata": dict(self.metadata),
        }


@dataclass
class AlertConfig:
    """Configuration for alert thresholds and delivery channels."""

    max_drawdown_pct: float | None = None
    max_daily_loss_pct: float | None = None
    min_pnl_pct: float | None = None
    max_gross_exposure_pct: float | None = None
    max_position_pct: float | None = None
    channels: list[str] = field(default_factory=lambda: ["console"])
    webhook_url: str | None = None
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    alert_email: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AlertConfig:
        return cls(
            max_drawdown_pct=_safe_float_opt(data.get("max_drawdown_pct")),
            max_daily_loss_pct=_safe_float_opt(data.get("max_daily_loss_pct")),
            min_pnl_pct=_safe_float_opt(data.get("min_pnl_pct")),
            max_gross_exposure_pct=_safe_float_opt(data.get("max_gross_exposure_pct")),
            max_position_pct=_safe_float_opt(data.get("max_position_pct")),
            channels=list(data.get("channels", ["console"])),
            webhook_url=data.get("webhook_url"),
            smtp_host=data.get("smtp_host"),
            smtp_port=_safe_int(data.get("smtp_port", 587), 587),
            smtp_user=data.get("smtp_user"),
            smtp_password=data.get("smtp_password"),
            alert_email=data.get("alert_email"),
        )


def _safe_float_opt(value: Any) -> float | None:
    if value is None:
        return None
    try:
        v = float(value)
    except (TypeError, ValueError):
        return None
    if v != v:  # NaN
        return None
    return v


def _safe_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


class AlertChannel:
    """Base class for alert delivery channels."""

    def send(self, alert: Alert) -> bool:
        """Send ``alert`` through this channel. Returns True on success."""
        raise NotImplementedError


class ConsoleAlertChannel(AlertChannel):
    """Write alerts to stdout."""

    def send(self, alert: Alert) -> bool:
        print(
            f"[ALERT] {alert.level.upper()} | {alert.timestamp} | {alert.metric} "
            f"={alert.value:.4f} (threshold {alert.threshold:.4f}) | {alert.message}"
        )
        return True


class WebhookAlertChannel(AlertChannel):
    """POST alert JSON to a webhook URL (best effort)."""

    def __init__(self, url: str | None) -> None:
        self.url = url

    def send(self, alert: Alert) -> bool:
        if not self.url:
            return False
        try:
            payload = json.dumps(alert.to_dict()).encode("utf-8")
            req = urllib.request.Request(
                self.url,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                resp.read()
            return True
        except (urllib.error.URLError, OSError, ValueError):
            return False


class EmailAlertChannel(AlertChannel):
    """Send alert email via SMTP (best effort)."""

    def __init__(self, config: AlertConfig) -> None:
        self.config = config

    def send(self, alert: Alert) -> bool:
        if not (self.config.smtp_host and self.config.alert_email):
            return False
        try:
            msg = EmailMessage()
            msg["Subject"] = f"[Paper Trading Alert] {alert.level.upper()}: {alert.metric}"
            msg["From"] = self.config.smtp_user or self.config.alert_email or ""
            msg["To"] = self.config.alert_email
            msg.set_content(
                f"{alert.timestamp}\n"
                f"Level: {alert.level}\n"
                f"Metric: {alert.metric}\n"
                f"Value: {alert.value:.4f}\n"
                f"Threshold: {alert.threshold:.4f}\n"
                f"Message: {alert.message}\n"
            )
            with smtplib.SMTP(
                self.config.smtp_host, self.config.smtp_port, timeout=5
            ) as smtp:
                smtp.starttls()
                if self.config.smtp_user and self.config.smtp_password:
                    smtp.login(self.config.smtp_user, self.config.smtp_password)
                smtp.send_message(msg)
            return True
        except (OSError, smtplib.SMTPException):
            return False


def load_alert_config(path: str) -> AlertConfig:
    """Load alert configuration from a JSON file.

    Returns a default :class:`AlertConfig` if the file cannot be read or
    parsed, so a missing config never blocks a paper-trading run.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return AlertConfig()
    if not isinstance(data, dict):
        return AlertConfig()
    return AlertConfig.from_dict(data)


class PaperTradingMonitor:
    """Track paper-trading metrics and emit alerts on threshold breaches."""

    def __init__(
        self,
        config: AlertConfig | None = None,
        initial_capital: float = 0.0,
        channels: list[AlertChannel] | None = None,
    ) -> None:
        self.config = config or AlertConfig()
        self.initial_capital = float(initial_capital)
        self.peak_equity = float(initial_capital)
        self.equity_history: list[dict[str, Any]] = []
        self.alerts: list[Alert] = []
        self._counter = 0
        self._channels = (
            list(channels) if channels is not None else self._build_channels()
        )

    def _build_channels(self) -> list[AlertChannel]:
        channels: list[AlertChannel] = []
        for name in self.config.channels:
            key = str(name).lower().strip()
            if key == "console":
                channels.append(ConsoleAlertChannel())
            elif key == "webhook":
                channels.append(WebhookAlertChannel(self.config.webhook_url))
            elif key == "email":
                channels.append(EmailAlertChannel(self.config))
        if not channels:
            channels.append(ConsoleAlertChannel())
        return channels

    def _emit(
        self,
        level: str,
        metric: str,
        value: float,
        threshold: float,
        message: str,
        symbol: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Alert:
        self._counter += 1
        alert = Alert(
            alert_id=f"alert-{self._counter}",
            level=level,
            message=message,
            timestamp=datetime.now(timezone.utc).isoformat(),
            metric=metric,
            value=float(value),
            threshold=float(threshold),
            symbol=symbol,
            metadata=dict(metadata or {}),
        )
        self.alerts.append(alert)
        for channel in self._channels:
            try:
                channel.send(alert)
            except Exception:
                pass
        return alert

    def get_drawdown(self, equity: float | None = None) -> float:
        """Return current drawdown as a fraction (0.0 = no drawdown)."""
        px = float(self.peak_equity)
        eq = float(equity if equity is not None else self._latest_equity())
        if px == 0.0:
            return 0.0
        dd = (px - eq) / px
        return dd if dd > 0.0 else 0.0

    def _latest_equity(self) -> float:
        if self.equity_history:
            return float(self.equity_history[-1].get("equity", 0.0))
        return self.initial_capital

    def update(
        self,
        equity: float,
        positions: dict[str, Any] | None = None,
        timestamp: str | None = None,
    ) -> list[Alert]:
        """Record a snapshot and evaluate all configured thresholds.

        Returns the list of alerts emitted by this update.
        """
        ts = timestamp or datetime.now(timezone.utc).isoformat()
        equity = float(equity)
        if equity > self.peak_equity:
            self.peak_equity = equity
        drawdown = self.get_drawdown(equity)
        self.equity_history.append(
            {"timestamp": ts, "equity": equity, "drawdown": drawdown}
        )

        emitted: list[Alert] = []
        total_realized = 0.0
        total_unrealized = 0.0
        gross_exposure = 0.0
        net_exposure = 0.0
        if positions:
            for sym, pos in positions.items():
                pos = pos or {}
                try:
                    qty = float(pos.get("quantity", 0.0) or 0.0)
                except (TypeError, ValueError):
                    qty = 0.0
                try:
                    price = float(
                        pos.get("last_price", pos.get("avg_cost", 0.0)) or 0.0
                    )
                except (TypeError, ValueError):
                    price = 0.0
                try:
                    realized = float(pos.get("realized_pnl", 0.0) or 0.0)
                except (TypeError, ValueError):
                    realized = 0.0
                try:
                    unrealized = float(pos.get("unrealized_pnl", 0.0) or 0.0)
                except (TypeError, ValueError):
                    unrealized = 0.0
                total_realized += realized
                total_unrealized += unrealized
                gross_exposure += abs(qty) * price
                net_exposure += qty * price
                if self.config.max_position_pct is not None and self.initial_capital > 0:
                    pct = abs(qty) * price / self.initial_capital
                    if pct >= self.config.max_position_pct:
                        emitted.append(
                            self._emit(
                                "warning",
                                "position_size",
                                pct,
                                self.config.max_position_pct,
                                (
                                    f"Position {sym} size {pct:.4%} exceeds limit "
                                    f"{self.config.max_position_pct:.4%}"
                                ),
                                symbol=str(sym),
                                metadata={"position_pct": pct},
                            )
                        )

        total_pnl = total_realized + total_unrealized
        pnl_pct = total_pnl / self.initial_capital if self.initial_capital > 0 else 0.0

        if self.config.max_drawdown_pct is not None and drawdown >= self.config.max_drawdown_pct:
            emitted.append(
                self._emit(
                    "error",
                    "drawdown",
                    drawdown,
                    self.config.max_drawdown_pct,
                    (
                        f"Drawdown {drawdown:.4%} exceeds limit "
                        f"{self.config.max_drawdown_pct:.4%}"
                    ),
                    metadata={"drawdown": drawdown, "equity": equity},
                )
            )

        if (
            self.config.min_pnl_pct is not None
            and (pnl_pct <= self.config.min_pnl_pct or total_pnl <= self.config.min_pnl_pct)
        ):
            emitted.append(
                self._emit(
                    "warning",
                    "pnl",
                    pnl_pct,
                    self.config.min_pnl_pct,
                    (
                        f"PnL {pnl_pct:.4%} at or below threshold "
                        f"{self.config.min_pnl_pct:.4%}"
                    ),
                    metadata={"pnl_pct": pnl_pct, "realized_pnl": total_realized,
                              "unrealized_pnl": total_unrealized},
                )
            )

        if (
            self.config.max_gross_exposure_pct is not None
            and self.initial_capital > 0
        ):
            exp_pct = gross_exposure / self.initial_capital
            if exp_pct >= self.config.max_gross_exposure_pct:
                emitted.append(
                    self._emit(
                        "warning",
                        "gross_exposure",
                        exp_pct,
                        self.config.max_gross_exposure_pct,
                        (
                            f"Gross exposure {exp_pct:.4%} exceeds limit "
                            f"{self.config.max_gross_exposure_pct:.4%}"
                        ),
                        metadata={"gross_exposure": gross_exposure},
                    )
                )

        return emitted

    def get_summary(self) -> dict[str, Any]:
        """Return a serializable summary of current monitoring state."""
        latest = self.equity_history[-1] if self.equity_history else {}
        return {
            "initial_capital": self.initial_capital,
            "peak_equity": self.peak_equity,
            "equity": float(latest.get("equity", self.initial_capital)),
            "drawdown": float(latest.get("drawdown", 0.0)),
            "total_alerts": len(self.alerts),
            "alerts": [a.to_dict() for a in self.alerts],
        }

    def to_dict(self) -> dict[str, Any]:
        return self.get_summary()
