"""Campaign #5 risk controls and dashboard.

Fail-closed by design: missing/invalid inputs, stale data, or breaches produce
explicit deny/breach events and kill-switch actions where configured. Controls do
not fabricate market data or fills.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _finite(x: Any) -> bool:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return False
    return math.isfinite(v)


@dataclass
class RiskConfig:
    max_notional_per_order: float = 25_000.0
    max_position_notional_per_symbol: float = 50_000.0
    max_gross_exposure: float = 100_000.0
    max_net_exposure: float = 100_000.0
    max_symbol_concentration: float = 0.60  # fraction of gross
    max_turnover_notional: float = 500_000.0
    max_cost_bps: float = 100.0
    max_drawdown_fraction: float = 0.20
    stale_data_seconds: float = 3600.0 * 6
    require_market_price: bool = True
    fail_closed_on_missing_data: bool = True
    allow_historical_replay: bool = False
    replay_timestamp_skew_seconds: float = 3600.0 * 24 * 7


@dataclass
class Breach:
    code: str
    message: str
    severity: str = "high"
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
            "details": dict(self.details),
        }


@dataclass
class RiskEvent:
    timestamp_utc: str
    event_type: str
    allowed: bool
    reason: str | None = None
    breaches: list[Breach] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp_utc": self.timestamp_utc,
            "event_type": self.event_type,
            "allowed": self.allowed,
            "reason": self.reason,
            "breaches": [b.to_dict() for b in self.breaches],
            "context": dict(self.context),
        }


class KillSwitch:
    def __init__(self, active: bool = False, reason: str | None = None):
        self.active = bool(active)
        self.reason = reason
        self.history: list[dict[str, Any]] = []

    def trip(self, reason: str, details: dict[str, Any] | None = None) -> None:
        self.active = True
        self.reason = reason
        self.history.append(
            {
                "timestamp_utc": _utc_now_iso(),
                "action": "trip",
                "reason": reason,
                "details": details or {},
            }
        )

    def reset(self, reason: str = "manual_reset") -> None:
        self.active = False
        self.history.append(
            {
                "timestamp_utc": _utc_now_iso(),
                "action": "reset",
                "reason": reason,
                "previous_reason": self.reason,
            }
        )
        self.reason = None

    def to_dict(self) -> dict[str, Any]:
        return {"active": self.active, "reason": self.reason, "history": list(self.history)}


class StaleDataGuard:
    def __init__(self, max_age_seconds: float):
        if not _finite(max_age_seconds) or float(max_age_seconds) <= 0:
            raise ValueError("max_age_seconds must be finite and > 0")
        self.max_age_seconds = float(max_age_seconds)

    @staticmethod
    def _parse_utc(data_timestamp_utc: str) -> datetime:
        ts = datetime.fromisoformat(str(data_timestamp_utc).replace("Z", "+00:00"))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        else:
            ts = ts.astimezone(timezone.utc)
        return ts

    def is_stale(
        self,
        data_timestamp_utc: str | None,
        now_utc: datetime | None = None,
        *,
        allow_historical_replay: bool = False,
    ) -> tuple[bool, str | None]:
        """Check timestamp freshness.

        Fail-closed by default: missing/invalid/future timestamps are stale.
        For bounded historical replay (paper backfill using real cached data),
        callers may pass ``now_utc`` equal to the processed bar timestamp and
        ``allow_historical_replay=True``; this only suppresses wall-clock age
        staleness, never missing/invalid timestamp failures.
        """
        if not data_timestamp_utc:
            return True, "missing_data_timestamp"
        try:
            ts = self._parse_utc(data_timestamp_utc)
        except Exception as exc:
            return True, f"invalid_data_timestamp:{exc}"
        if allow_historical_replay and now_utc is not None:
            try:
                now = now_utc if now_utc.tzinfo else now_utc.replace(tzinfo=timezone.utc)
                # In replay mode the bar timestamp is authoritative; allow small skew.
                age = abs((now.astimezone(timezone.utc) - ts).total_seconds())
                if age > self.max_age_seconds:
                    return True, f"replay_timestamp_skew_seconds:{age}"
                return False, None
            except Exception as exc:
                return True, f"invalid_replay_clock:{exc}"
        now = now_utc or datetime.now(timezone.utc)
        age = (now - ts).total_seconds()
        if age < 0:
            # future timestamps treated as stale/suspicious
            return True, f"future_data_timestamp_age_seconds:{age}"
        if age > self.max_age_seconds:
            return True, f"stale_data_age_seconds:{age}"
        return False, None


class RiskDashboard:
    def __init__(self, config: RiskConfig | None = None, kill_switch: KillSwitch | None = None):
        self.config = config or RiskConfig()
        self.kill_switch = kill_switch or KillSwitch()
        self.events: list[RiskEvent] = []
        self.turnover_notional = 0.0
        self.peak_equity: float | None = None
        self.current_drawdown = 0.0

    def _deny(
        self, event_type: str, breaches: list[Breach], context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        reason = breaches[0].code if breaches else "risk_denied"
        ev = RiskEvent(
            timestamp_utc=_utc_now_iso(),
            event_type=event_type,
            allowed=False,
            reason=reason,
            breaches=breaches,
            context=context or {},
        )
        self.events.append(ev)
        return ev.to_dict()

    def _allow(self, event_type: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        ev = RiskEvent(
            timestamp_utc=_utc_now_iso(), event_type=event_type, allowed=True, context=context or {}
        )
        self.events.append(ev)
        return ev.to_dict()

    def update_drawdown(self, equity: float) -> None:
        if not _finite(equity):
            return
        eq = float(equity)
        if self.peak_equity is None or eq > self.peak_equity:
            self.peak_equity = eq
        if self.peak_equity and self.peak_equity > 0:
            self.current_drawdown = max(0.0, (self.peak_equity - eq) / self.peak_equity)
        if self.current_drawdown > self.config.max_drawdown_fraction:
            self.kill_switch.trip(
                "drawdown_kill_switch",
                {
                    "drawdown": self.current_drawdown,
                    "max_drawdown_fraction": self.config.max_drawdown_fraction,
                },
            )

    def pre_trade_check(
        self,
        order: dict[str, Any],
        *,
        market_price: float | None = None,
        portfolio_state: dict[str, Any] | None = None,
        data_timestamp_utc: str | None = None,
        now_utc: datetime | None = None,
    ) -> dict[str, Any]:
        breaches: list[Breach] = []
        ctx = {
            "order": dict(order),
            "market_price": market_price,
            "data_timestamp_utc": data_timestamp_utc,
            "replay_mode": bool(self.config.allow_historical_replay),
        }
        if self.kill_switch.active:
            return self._deny(
                "pre_trade",
                [
                    Breach(
                        "kill_switch_active",
                        "kill switch is active",
                        details={"reason": self.kill_switch.reason},
                    )
                ],
                ctx,
            )
        stale_guard = StaleDataGuard(
            self.config.replay_timestamp_skew_seconds
            if self.config.allow_historical_replay
            else self.config.stale_data_seconds
        )
        stale, stale_reason = stale_guard.is_stale(
            data_timestamp_utc,
            now_utc=now_utc,
            allow_historical_replay=self.config.allow_historical_replay,
        )
        if stale and self.config.fail_closed_on_missing_data:
            return self._deny(
                "pre_trade",
                [
                    Breach(
                        "stale_or_missing_data",
                        "market/data timestamp stale or missing (fail-closed)",
                        details={"reason": stale_reason},
                    )
                ],
                ctx,
            )
        symbol = str(order.get("symbol", "")).upper()
        side = str(order.get("side", "")).lower()
        qty = order.get("quantity")
        if not symbol or side not in {"buy", "sell"}:
            return self._deny(
                "pre_trade",
                [Breach("invalid_order", "invalid order fields", details={"order": order})],
                ctx,
            )
        if not _finite(qty):
            return self._deny(
                "pre_trade",
                [Breach("invalid_order", "quantity not finite", details={"order": order})],
                ctx,
            )
        qty_f = float(qty)  # type: ignore[arg-type]
        if qty_f <= 0:
            return self._deny(
                "pre_trade",
                [Breach("invalid_order", "quantity must be positive", details={"order": order})],
                ctx,
            )
        px = market_price
        if (px is None or not _finite(px) or float(px) <= 0) and _finite(order.get("limit_price")):
            lp = order.get("limit_price")
            if lp is not None and _finite(lp):
                px = float(lp)
        if self.config.require_market_price and (px is None or not _finite(px) or float(px) <= 0):
            return self._deny(
                "pre_trade",
                [
                    Breach(
                        "missing_market_price",
                        "market price required (fail-closed)",
                        details={"symbol": symbol},
                    )
                ],
                ctx,
            )
        if px is None or not _finite(px) or float(px) <= 0:
            px = 0.0
        px_f = float(px)
        qty_f = float(qty) if qty is not None and _finite(qty) else 0.0
        notional = abs(qty_f * px_f)
        ctx["notional"] = notional
        if notional > self.config.max_notional_per_order:
            breaches.append(
                Breach(
                    "max_notional_per_order",
                    "order notional exceeds limit",
                    details={"notional": notional, "limit": self.config.max_notional_per_order},
                )
            )
        pstate = dict(portfolio_state or {})
        gross = float(pstate.get("gross_exposure", 0.0) or 0.0)
        net = float(pstate.get("net_exposure", 0.0) or 0.0)
        equity = float(pstate.get("equity", pstate.get("cash", 0.0)) or 0.0)
        positions = dict(pstate.get("positions") or {})
        sym_pos = dict(positions.get(symbol) or {})
        sym_notional = abs(float(sym_pos.get("market_value", 0.0) or 0.0)) + notional
        projected_gross = gross + notional
        signed = notional if side == "buy" else -notional
        projected_net_abs = abs(net + signed)
        if sym_notional > self.config.max_position_notional_per_symbol:
            breaches.append(
                Breach(
                    "max_position_notional_per_symbol",
                    "symbol position notional exceeds limit",
                    details={
                        "symbol": symbol,
                        "projected": sym_notional,
                        "limit": self.config.max_position_notional_per_symbol,
                    },
                )
            )
        if projected_gross > self.config.max_gross_exposure:
            breaches.append(
                Breach(
                    "max_gross_exposure",
                    "gross exposure exceeds limit",
                    details={
                        "projected_gross": projected_gross,
                        "limit": self.config.max_gross_exposure,
                    },
                )
            )
        if projected_net_abs > self.config.max_net_exposure:
            breaches.append(
                Breach(
                    "max_net_exposure",
                    "net exposure exceeds limit",
                    details={
                        "projected_net_abs": projected_net_abs,
                        "limit": self.config.max_net_exposure,
                    },
                )
            )
        if (
            projected_gross > 0
            and (sym_notional / projected_gross) > self.config.max_symbol_concentration
        ):
            # Single-asset bounded paper sessions: concentration is not meaningful when
            # only one projected symbol is exposed; keep check for multi-asset exposure.
            active_symbols = {
                s
                for s in positions.keys()
                if abs(float(dict(positions.get(s) or {}).get("market_value", 0.0) or 0.0)) > 1e-9
            } | {symbol}
            if len(active_symbols) > 1:
                breaches.append(
                    Breach(
                        "max_symbol_concentration",
                        "symbol concentration exceeds limit",
                        details={
                            "symbol": symbol,
                            "concentration": sym_notional / projected_gross,
                            "limit": self.config.max_symbol_concentration,
                        },
                    )
                )
        if self.turnover_notional + notional > self.config.max_turnover_notional:
            breaches.append(
                Breach(
                    "max_turnover_notional",
                    "turnover/cost budget exceeded",
                    details={
                        "projected_turnover": self.turnover_notional + notional,
                        "limit": self.config.max_turnover_notional,
                    },
                )
            )
        fee_rate = float(order.get("fee_rate", 0.001) or 0.001)
        slippage_bps = float(order.get("slippage_bps", 5.0) or 5.0)
        est_cost_bps = (fee_rate * 10000.0) + slippage_bps
        if est_cost_bps > self.config.max_cost_bps:
            breaches.append(
                Breach(
                    "max_cost_bps",
                    "estimated cost exceeds budget",
                    details={"estimated_cost_bps": est_cost_bps, "limit": self.config.max_cost_bps},
                )
            )
        self.update_drawdown(equity)
        if self.kill_switch.active:
            breaches.append(
                Breach(
                    "drawdown_kill_switch",
                    "drawdown kill switch tripped",
                    details={"drawdown": self.current_drawdown},
                )
            )
        if breaches:
            return self._deny("pre_trade", breaches, ctx)
        self.turnover_notional += notional
        return self._allow("pre_trade", {**ctx, "portfolio_state": pstate})

    def runtime_state(self, portfolio_state: dict[str, Any] | None = None) -> dict[str, Any]:
        pstate = dict(portfolio_state or {})
        equity = float(pstate.get("equity", pstate.get("cash", 0.0)) or 0.0)
        self.update_drawdown(equity)
        breaches = []
        if self.kill_switch.active:
            breaches.append(
                Breach(
                    "kill_switch_active",
                    "kill switch active",
                    details={"reason": self.kill_switch.reason},
                )
            )
        return {
            "timestamp_utc": _utc_now_iso(),
            "kill_switch": self.kill_switch.to_dict(),
            "drawdown": self.current_drawdown,
            "peak_equity": self.peak_equity,
            "turnover_notional": self.turnover_notional,
            "config": {
                "max_notional_per_order": self.config.max_notional_per_order,
                "max_position_notional_per_symbol": self.config.max_position_notional_per_symbol,
                "max_gross_exposure": self.config.max_gross_exposure,
                "max_net_exposure": self.config.max_net_exposure,
                "max_symbol_concentration": self.config.max_symbol_concentration,
                "max_turnover_notional": self.config.max_turnover_notional,
                "max_cost_bps": self.config.max_cost_bps,
                "max_drawdown_fraction": self.config.max_drawdown_fraction,
                "stale_data_seconds": self.config.stale_data_seconds,
                "require_market_price": self.config.require_market_price,
                "fail_closed_on_missing_data": self.config.fail_closed_on_missing_data,
                "allow_historical_replay": self.config.allow_historical_replay,
                "replay_timestamp_skew_seconds": self.config.replay_timestamp_skew_seconds,
            },
            "portfolio_state": pstate,
            "breaches": [b.to_dict() for b in breaches],
            "events_count": len(self.events),
            "recent_events": [e.to_dict() for e in self.events[-20:]],
            "status": "halted" if self.kill_switch.active else "ok",
        }
