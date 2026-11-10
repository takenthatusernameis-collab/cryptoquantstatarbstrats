"""Fail-closed OMS primitives for Campaign #5 production bridge.

This module provides order intents, validation, idempotency/client-order IDs,
position/cash accounting, and strict state transitions. It does not fabricate
fills or exchange acknowledgements; execution is delegated to a broker that must
label paper/simulated fills honestly.
"""

from __future__ import annotations

import math
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class OrderStatus(str, Enum):
    NEW = "new"
    ACCEPTED = "accepted"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELED = "canceled"
    REPLACED = "replaced"
    REJECTED = "rejected"


class RejectReason(str, Enum):
    INVALID_INPUT = "invalid_input"
    DUPLICATE_CLIENT_ORDER_ID = "duplicate_client_order_id"
    RISK_REJECTED = "risk_rejected"
    INSUFFICIENT_CASH = "insufficient_cash"
    POSITION_LIMIT = "position_limit"
    NOT_FOUND = "not_found"
    UNSUPPORTED = "unsupported"
    BROKER_REJECTED = "broker_rejected"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _is_finite_number(value: Any) -> bool:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return False
    return math.isfinite(v)


@dataclass(frozen=True)
class OrderIntent:
    symbol: str
    side: str  # buy/sell
    quantity: float
    order_type: str = "market"  # market/limit
    limit_price: float | None = None
    client_order_id: str | None = None
    timestamp: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def normalized(self) -> "OrderIntent":
        symbol = str(self.symbol).strip().upper()
        side = str(self.side).strip().lower()
        order_type = str(self.order_type).strip().lower()
        coid = self.client_order_id
        if coid is None or str(coid).strip() == "":
            coid = f"coid-{uuid.uuid4().hex}"
        ts = self.timestamp or _utc_now_iso()
        limit_price = self.limit_price
        if limit_price is not None:
            limit_price = float(limit_price)
        return OrderIntent(
            symbol=symbol,
            side=side,
            quantity=float(self.quantity),
            order_type=order_type,
            limit_price=limit_price,
            client_order_id=str(coid),
            timestamp=ts,
            metadata=dict(self.metadata or {}),
        )

    def validate(self) -> None:
        intent = self.normalized()
        if not intent.symbol:
            raise ValueError("symbol is required")
        if intent.side not in {"buy", "sell"}:
            raise ValueError("side must be buy or sell")
        if intent.order_type not in {"market", "limit"}:
            raise ValueError("order_type must be market or limit")
        if not _is_finite_number(intent.quantity) or intent.quantity <= 0.0:
            raise ValueError("quantity must be a finite number > 0")
        if intent.order_type == "limit":
            lp = intent.limit_price
            if lp is None or not _is_finite_number(lp) or float(lp) <= 0.0:
                raise ValueError("limit_price must be a finite number > 0 for limit orders")
        else:
            if intent.limit_price is not None:
                lp = intent.limit_price
                if not _is_finite_number(lp) or float(lp) <= 0.0:
                    raise ValueError("limit_price, if provided for market orders, must be > 0")
        if not intent.client_order_id:
            raise ValueError("client_order_id is required")


@dataclass
class OrderRecord:
    order_id: str
    client_order_id: str
    symbol: str
    side: str
    quantity: float
    order_type: str
    limit_price: float | None
    status: OrderStatus
    created_at: str
    updated_at: str
    filled_quantity: float = 0.0
    avg_fill_price: float = 0.0
    cumulative_fee: float = 0.0
    reason: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    fills: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "order_id": self.order_id,
            "client_order_id": self.client_order_id,
            "symbol": self.symbol,
            "side": self.side,
            "quantity": self.quantity,
            "order_type": self.order_type,
            "limit_price": self.limit_price,
            "status": self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "filled_quantity": self.filled_quantity,
            "avg_fill_price": self.avg_fill_price,
            "cumulative_fee": self.cumulative_fee,
            "reason": self.reason,
            "metadata": dict(self.metadata),
            "fills": list(self.fills),
        }


@dataclass
class Position:
    symbol: str
    quantity: float = 0.0
    avg_cost: float = 0.0
    realized_pnl: float = 0.0

    @property
    def side(self) -> str:
        if self.quantity > 1e-12:
            return "long"
        if self.quantity < -1e-12:
            return "short"
        return "flat"


@dataclass
class AccountState:
    initial_cash: float
    cash: float
    positions: dict[str, Position] = field(default_factory=dict)
    realized_pnl: float = 0.0
    fees_paid: float = 0.0

    @classmethod
    def with_cash(cls, cash: float) -> "AccountState":
        if not _is_finite_number(cash) or cash < 0.0:
            raise ValueError("initial cash must be finite and >= 0")
        c = float(cash)
        return cls(initial_cash=c, cash=c)

    def mark_to_market(self, prices: dict[str, float] | None = None) -> dict[str, Any]:
        prices = prices or {}
        equity = float(self.cash)
        gross = 0.0
        net = 0.0
        unrealized = 0.0
        pos_out: dict[str, Any] = {}
        for sym, pos in self.positions.items():
            px = prices.get(sym)
            if px is None or not _is_finite_number(px):
                px = pos.avg_cost
            px = float(px)
            mv = pos.quantity * px
            equity += mv
            gross += abs(mv)
            net += mv
            upnl = pos.quantity * (px - pos.avg_cost) if abs(pos.quantity) > 1e-12 else 0.0
            unrealized += upnl
            pos_out[sym] = {
                "symbol": sym,
                "quantity": pos.quantity,
                "avg_cost": pos.avg_cost,
                "side": pos.side,
                "last_price": px,
                "market_value": mv,
                "unrealized_pnl": upnl,
                "realized_pnl": pos.realized_pnl,
            }
        return {
            "cash": self.cash,
            "equity": equity,
            "gross_exposure": gross,
            "net_exposure": net,
            "unrealized_pnl": unrealized,
            "realized_pnl": self.realized_pnl,
            "fees_paid": self.fees_paid,
            "positions": pos_out,
        }

    def apply_paper_fill(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        fee: float = 0.0,
    ) -> None:
        """Apply a *paper/simulated* fill to accounting. Never an exchange fill."""
        symbol = str(symbol).strip().upper()
        side = str(side).strip().lower()
        if side not in {"buy", "sell"}:
            raise ValueError("side must be buy or sell")
        if not all(_is_finite_number(x) and float(x) > 0.0 for x in (quantity, price)):
            raise ValueError("quantity and price must be finite and > 0")
        if not _is_finite_number(fee) or float(fee) < 0.0:
            raise ValueError("fee must be finite and >= 0")
        qty = float(quantity)
        px = float(price)
        fee = float(fee)
        signed = qty if side == "buy" else -qty
        notional = signed * px
        self.cash -= notional
        self.cash -= fee
        self.fees_paid += fee
        pos = self.positions.setdefault(symbol, Position(symbol=symbol))
        prev_qty = pos.quantity
        prev_avg = pos.avg_cost
        new_qty = prev_qty + signed
        realized = 0.0
        if abs(prev_qty) < 1e-12:
            pos.avg_cost = px
        elif prev_qty * signed > 0:
            # increasing same direction
            total = abs(prev_qty) + abs(signed)
            if total > 0:
                pos.avg_cost = (abs(prev_qty) * prev_avg + abs(signed) * px) / total
        else:
            # reducing or flipping
            closing = min(abs(prev_qty), abs(signed))
            if prev_qty > 0:
                realized = closing * (px - prev_avg)
            else:
                realized = closing * (prev_avg - px)
            pos.realized_pnl += realized
            self.realized_pnl += realized
            if abs(new_qty) < 1e-12:
                pos.avg_cost = 0.0
            elif prev_qty * new_qty < 0:
                # flipped direction; remaining opened at fill price
                pos.avg_cost = px
            # else reduced, avg cost unchanged
        pos.quantity = new_qty
        if abs(pos.quantity) < 1e-12:
            pos.quantity = 0.0
            pos.avg_cost = 0.0


class OMS:
    """Fail-closed OMS with idempotency and strict validation.

    The OMS manages intent lifecycle and accounting hooks. Fill simulation is
    performed by a broker; paper fills must be explicitly labeled by the broker.
    """

    def __init__(self, account: AccountState):
        self.account = account
        self.orders: dict[str, OrderRecord] = {}
        self._client_index: dict[str, str] = {}
        self._seq = 0
        self.events: list[dict[str, Any]] = []

    def _next_order_id(self) -> str:
        self._seq += 1
        return f"ord-{self._seq}"

    def _record_event(self, event_type: str, payload: dict[str, Any]) -> None:
        self.events.append(
            {
                "type": event_type,
                "timestamp_utc": _utc_now_iso(),
                **payload,
            }
        )

    def submit(
        self,
        intent: OrderIntent,
        *,
        broker: Any = None,
        market_price: float | None = None,
        risk_decision: dict[str, Any] | None = None,
    ) -> OrderRecord:
        try:
            norm = intent.normalized()
            norm.validate()
        except Exception as exc:
            rec = self._reject(intent, RejectReason.INVALID_INPUT, str(exc))
            return rec

        coid = norm.client_order_id or ""
        if coid in self._client_index:
            existing_id = self._client_index[coid]
            existing = self.orders[existing_id]
            self._record_event(
                "duplicate_client_order_id",
                {"client_order_id": coid, "order_id": existing_id, "status": existing.status.value},
            )
            return existing

        if risk_decision is not None and not risk_decision.get("allowed", False):
            rec = self._new_record(norm, OrderStatus.REJECTED)
            rec.reason = str(risk_decision.get("reason") or RejectReason.RISK_REJECTED.value)
            self.orders[rec.order_id] = rec
            self._client_index[rec.client_order_id] = rec.order_id
            self._record_event(
                "order_rejected_risk",
                {"order": rec.to_dict(), "risk_decision": risk_decision},
            )
            return rec

        rec = self._new_record(norm, OrderStatus.ACCEPTED)
        self.orders[rec.order_id] = rec
        self._client_index[rec.client_order_id] = rec.order_id
        self._record_event("order_accepted", {"order": rec.to_dict()})

        if broker is not None:
            try:
                fills = broker.execute(rec.to_dict(), market_price=market_price)
            except Exception as exc:
                rec.status = OrderStatus.REJECTED
                rec.reason = f"{RejectReason.BROKER_REJECTED.value}:{exc}"
                rec.updated_at = _utc_now_iso()
                self._record_event(
                    "order_broker_rejected",
                    {"order": rec.to_dict(), "error": str(exc)},
                )
                return rec
            self._apply_broker_fills(rec, fills)
        return rec

    def _new_record(self, intent: OrderIntent, status: OrderStatus) -> OrderRecord:
        now = _utc_now_iso()
        oid = self._next_order_id()
        return OrderRecord(
            order_id=oid,
            client_order_id=intent.client_order_id or f"coid-{oid}",
            symbol=intent.symbol,
            side=intent.side,
            quantity=float(intent.quantity),
            order_type=intent.order_type,
            limit_price=float(intent.limit_price) if intent.limit_price is not None else None,
            status=status,
            created_at=now,
            updated_at=now,
            metadata=dict(intent.metadata or {}),
        )

    def _reject(self, intent: OrderIntent, reason: RejectReason, detail: str) -> OrderRecord:
        try:
            norm = intent.normalized()
            rec = self._new_record(norm, OrderStatus.REJECTED)
        except Exception:
            now = _utc_now_iso()
            rec = OrderRecord(
                order_id=self._next_order_id(),
                client_order_id=str(
                    getattr(intent, "client_order_id", None) or f"coid-{uuid.uuid4().hex}"
                ),
                symbol=str(getattr(intent, "symbol", "")).upper(),
                side=str(getattr(intent, "side", "")).lower(),
                quantity=float(getattr(intent, "quantity", 0.0) or 0.0),
                order_type=str(getattr(intent, "order_type", "market")).lower(),
                limit_price=getattr(intent, "limit_price", None),
                status=OrderStatus.REJECTED,
                created_at=now,
                updated_at=now,
            )
        rec.reason = f"{reason.value}:{detail}"
        self.orders[rec.order_id] = rec
        if rec.client_order_id:
            self._client_index.setdefault(rec.client_order_id, rec.order_id)
        self._record_event("order_rejected", {"order": rec.to_dict()})
        return rec

    def _apply_broker_fills(self, rec: OrderRecord, fills: list[dict[str, Any]] | None) -> None:
        fills = list(fills or [])
        for fill in fills:
            self.apply_fill(rec.order_id, fill)
        if not fills and rec.status == OrderStatus.ACCEPTED:
            # Broker returned no fills (e.g. limit not crossed in paper mode) - keep accepted.
            rec.updated_at = _utc_now_iso()

    def apply_fill(self, order_id: str, fill: dict[str, Any]) -> OrderRecord:
        rec = self.orders.get(order_id)
        if rec is None:
            raise KeyError(f"unknown order_id: {order_id}")
        if rec.status in {OrderStatus.CANCELED, OrderStatus.REJECTED}:
            raise ValueError(f"cannot apply fill to {rec.status.value} order")
        # Fail-closed: paper/simulated fills must be labeled.
        if fill.get("simulated_fill") is not True and fill.get("paper") is not True:
            raise ValueError(
                "fill must be explicitly labeled simulated_fill/paper; "
                "real exchange fills are not accepted by Campaign #5 paper OMS"
            )
        qty = float(fill["quantity"])
        px = float(fill["price"])
        fee = float(fill.get("fee", 0.0) or 0.0)
        if not all(_is_finite_number(x) for x in (qty, px, fee)) or qty <= 0 or px <= 0 or fee < 0:
            raise ValueError("invalid fill quantity/price/fee")
        if rec.filled_quantity + qty > rec.quantity + 1e-9:
            raise ValueError("fill exceeds remaining order quantity")
        side = str(fill.get("side") or rec.side).lower()
        symbol = str(fill.get("symbol") or rec.symbol).upper()
        self.account.apply_paper_fill(symbol, side, qty, px, fee)
        prev_notional = rec.avg_fill_price * rec.filled_quantity
        rec.filled_quantity += qty
        rec.avg_fill_price = (
            (prev_notional + qty * px) / rec.filled_quantity if rec.filled_quantity > 0 else 0.0
        )
        rec.cumulative_fee += fee
        fill_out = dict(fill)
        fill_out.setdefault("order_id", rec.order_id)
        fill_out.setdefault("client_order_id", rec.client_order_id)
        fill_out.setdefault("symbol", symbol)
        fill_out.setdefault("side", side)
        fill_out.setdefault("timestamp_utc", _utc_now_iso())
        fill_out["simulated_fill"] = True
        fill_out["real_exchange_fill"] = False
        rec.fills.append(fill_out)
        rec.status = (
            OrderStatus.FILLED
            if rec.filled_quantity >= rec.quantity - 1e-9
            else OrderStatus.PARTIALLY_FILLED
        )
        rec.updated_at = _utc_now_iso()
        self._record_event("order_fill_applied", {"order_id": rec.order_id, "fill": fill_out})
        return rec

    def cancel(self, order_id: str, reason: str = "cancel_requested") -> OrderRecord:
        rec = self.orders.get(order_id)
        if rec is None:
            raise KeyError(f"unknown order_id: {order_id}")
        if rec.status in {OrderStatus.FILLED, OrderStatus.CANCELED, OrderStatus.REJECTED}:
            raise ValueError(f"cannot cancel {rec.status.value} order")
        rec.status = OrderStatus.CANCELED
        rec.reason = reason
        rec.updated_at = _utc_now_iso()
        self._record_event("order_canceled", {"order_id": rec.order_id, "reason": reason})
        return rec

    def replace(
        self,
        order_id: str,
        new_intent: OrderIntent,
        *,
        broker: Any = None,
        market_price: float | None = None,
    ) -> OrderRecord:
        """Cancel/replace semantics where supported (paper). Implemented as cancel + new intent."""
        old = self.cancel(order_id, reason="replace_requested")
        replacement = self.submit(new_intent, broker=broker, market_price=market_price)
        old.status = OrderStatus.REPLACED
        old.metadata["replaced_by_order_id"] = replacement.order_id
        old.updated_at = _utc_now_iso()
        replacement.metadata["replaces_order_id"] = order_id
        self._record_event(
            "order_replaced",
            {"old_order_id": order_id, "new_order_id": replacement.order_id},
        )
        return replacement

    def get(self, order_id: str) -> OrderRecord | None:
        return self.orders.get(order_id)

    def by_client_order_id(self, client_order_id: str) -> OrderRecord | None:
        oid = self._client_index.get(str(client_order_id))
        return self.orders.get(oid) if oid else None

    def snapshot(self, prices: dict[str, float] | None = None) -> dict[str, Any]:
        return {
            "account": self.account.mark_to_market(prices),
            "orders": [o.to_dict() for o in self.orders.values()],
            "events_count": len(self.events),
        }
