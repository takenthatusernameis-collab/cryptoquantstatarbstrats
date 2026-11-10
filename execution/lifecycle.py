"""Campaign #6: Order lifecycle state machine.

This module provides a formal state machine for order lifecycle validation
covering submit/ack/partial/fill/cancel/replace/reject/timeout/retry semantics.
All transitions are explicit and validated. Any non-paper exchange interaction
must be explicitly labeled and proven; otherwise simulated and labeled.
"""

from __future__ import annotations

import math
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class LifecycleState(str, Enum):
    """Order lifecycle states."""
    CREATED = "created"
    SUBMITTED = "submitted"
    ACKNOWLEDGED = "acknowledged"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCEL_REQUESTED = "cancel_requested"
    CANCELED = "canceled"
    REPLACE_REQUESTED = "replace_requested"
    REPLACED = "replaced"
    REJECTED = "rejected"
    EXPIRED = "expired"
    TIMEOUT = "timeout"


class LifecycleEvent(str, Enum):
    """Events that trigger state transitions."""
    SUBMIT = "submit"
    ACKNOWLEDGE = "acknowledge"
    PARTIAL_FILL = "partial_fill"
    FILL = "fill"
    CANCEL_REQUEST = "cancel_request"
    CANCEL_ACKNOWLEDGE = "cancel_acknowledge"
    REPLACE_REQUEST = "replace_request"
    REPLACE_ACKNOWLEDGE = "replace_acknowledge"
    REJECT = "reject"
    EXPIRE = "expire"
    TIMEOUT = "timeout"
    RETRY = "retry"


# Valid state transitions: (from_state, event) -> to_state
VALID_TRANSITIONS: dict[tuple[LifecycleState, LifecycleEvent], LifecycleState] = {
    (LifecycleState.CREATED, LifecycleEvent.SUBMIT): LifecycleState.SUBMITTED,
    (LifecycleState.SUBMITTED, LifecycleEvent.ACKNOWLEDGE): LifecycleState.ACKNOWLEDGED,
    (LifecycleState.SUBMITTED, LifecycleEvent.REJECT): LifecycleState.REJECTED,
    (LifecycleState.SUBMITTED, LifecycleEvent.TIMEOUT): LifecycleState.TIMEOUT,
    (LifecycleState.ACKNOWLEDGED, LifecycleEvent.PARTIAL_FILL): LifecycleState.PARTIALLY_FILLED,
    (LifecycleState.ACKNOWLEDGED, LifecycleEvent.FILL): LifecycleState.FILLED,
    (LifecycleState.ACKNOWLEDGED, LifecycleEvent.CANCEL_REQUEST): LifecycleState.CANCEL_REQUESTED,
    (LifecycleState.ACKNOWLEDGED, LifecycleEvent.REPLACE_REQUEST): LifecycleState.REPLACE_REQUESTED,
    (LifecycleState.ACKNOWLEDGED, LifecycleEvent.REJECT): LifecycleState.REJECTED,
    (LifecycleState.ACKNOWLEDGED, LifecycleEvent.EXPIRE): LifecycleState.EXPIRED,
    (LifecycleState.PARTIALLY_FILLED, LifecycleEvent.PARTIAL_FILL): LifecycleState.PARTIALLY_FILLED,
    (LifecycleState.PARTIALLY_FILLED, LifecycleEvent.FILL): LifecycleState.FILLED,
    (LifecycleState.PARTIALLY_FILLED, LifecycleEvent.CANCEL_REQUEST): LifecycleState.CANCEL_REQUESTED,
    (LifecycleState.PARTIALLY_FILLED, LifecycleEvent.REPLACE_REQUEST): LifecycleState.REPLACE_REQUESTED,
    (LifecycleState.PARTIALLY_FILLED, LifecycleEvent.EXPIRE): LifecycleState.EXPIRED,
    (LifecycleState.CANCEL_REQUESTED, LifecycleEvent.CANCEL_ACKNOWLEDGE): LifecycleState.CANCELED,
    (LifecycleState.CANCEL_REQUESTED, LifecycleEvent.REJECT): LifecycleState.REJECTED,
    (LifecycleState.CANCEL_REQUESTED, LifecycleEvent.TIMEOUT): LifecycleState.TIMEOUT,
    (LifecycleState.REPLACE_REQUESTED, LifecycleEvent.REPLACE_ACKNOWLEDGE): LifecycleState.REPLACED,
    (LifecycleState.REPLACE_REQUESTED, LifecycleEvent.REJECT): LifecycleState.REJECTED,
    (LifecycleState.REPLACE_REQUESTED, LifecycleEvent.TIMEOUT): LifecycleState.TIMEOUT,
    (LifecycleState.TIMEOUT, LifecycleEvent.RETRY): LifecycleState.SUBMITTED,
    (LifecycleState.REJECTED, LifecycleEvent.RETRY): LifecycleState.SUBMITTED,
}


TERMINAL_STATES = {
    LifecycleState.FILLED,
    LifecycleState.CANCELED,
    LifecycleState.REPLACED,
    LifecycleState.REJECTED,
    LifecycleState.EXPIRED,
    LifecycleState.TIMEOUT,
}

ACTIVE_STATES = {
    LifecycleState.SUBMITTED,
    LifecycleState.ACKNOWLEDGED,
    LifecycleState.PARTIALLY_FILLED,
    LifecycleState.CANCEL_REQUESTED,
    LifecycleState.REPLACE_REQUESTED,
}


@dataclass
class LifecycleTransition:
    """Record of a state transition."""
    from_state: LifecycleState
    event: LifecycleEvent
    to_state: LifecycleState
    timestamp_utc: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "from_state": self.from_state.value,
            "event": self.event.value,
            "to_state": self.to_state.value,
            "timestamp_utc": self.timestamp_utc,
            "metadata": dict(self.metadata),
        }


@dataclass
class OrderLifecycle:
    """Order lifecycle tracker with explicit state machine."""
    client_order_id: str
    symbol: str
    side: str
    order_type: str
    quantity: float
    limit_price: float | None = None
    exchange_order_id: str | None = None
    state: LifecycleState = LifecycleState.CREATED
    filled_quantity: float = 0.0
    avg_fill_price: float = 0.0
    cumulative_fee: float = 0.0
    reject_reason: str | None = None
    reject_message: str | None = None
    transitions: list[LifecycleTransition] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    simulated: bool = True
    real_exchange_interaction: bool = False
    execution_environment: str = "paper"

    def __post_init__(self) -> None:
        pass

    def _record_transition(
        self,
        from_state: LifecycleState,
        event: LifecycleEvent,
        to_state: LifecycleState,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.transitions.append(LifecycleTransition(
            from_state=from_state,
            event=event,
            to_state=to_state,
            timestamp_utc=_utc_now_iso(),
            metadata=metadata or {},
        ))
        self.state = to_state

    def can_transition(self, event: LifecycleEvent) -> bool:
        return (self.state, event) in VALID_TRANSITIONS

    def transition(self, event: LifecycleEvent, **metadata: Any) -> LifecycleState:
        """Apply a state transition, validating against the state machine."""
        key = (self.state, event)
        if key not in VALID_TRANSITIONS:
            raise ValueError(
                f"Invalid transition: {self.state.value} --{event.value}--> ? "
                f"(valid from {self.state.value}: {[e.value for (s, e) in VALID_TRANSITIONS if s == self.state]})"
            )
        to_state = VALID_TRANSITIONS[key]
        self._record_transition(self.state, event, to_state, metadata)
        return to_state

    def submit(self, exchange_order_id: str | None = None) -> LifecycleState:
        self.exchange_order_id = exchange_order_id or f"exch-{uuid.uuid4().hex[:12]}"
        return self.transition(LifecycleEvent.SUBMIT, exchange_order_id=self.exchange_order_id)

    def acknowledge(self, exchange_order_id: str | None = None) -> LifecycleState:
        if exchange_order_id:
            self.exchange_order_id = exchange_order_id
        return self.transition(LifecycleEvent.ACKNOWLEDGE)

    def partial_fill(
        self,
        fill_qty: float,
        fill_price: float,
        fee: float = 0.0,
        trade_id: str | None = None,
    ) -> LifecycleState:
        if not (0 < fill_qty <= self.quantity - self.filled_quantity + 1e-12):
            raise ValueError("fill_qty exceeds remaining quantity")
        if not (fill_price > 0 and math.isfinite(fill_price)):
            raise ValueError("fill_price must be positive and finite")
        if not (fee >= 0 and math.isfinite(fee)):
            raise ValueError("fee must be non-negative and finite")

        self.filled_quantity += fill_qty
        prev_notional = self.avg_fill_price * (self.filled_quantity - fill_qty)
        self.avg_fill_price = (prev_notional + fill_qty * fill_price) / self.filled_quantity
        self.cumulative_fee += fee

        if self.filled_quantity >= self.quantity - 1e-9:
            return self.transition(
                LifecycleEvent.FILL,
                fill_qty=fill_qty,
                fill_price=fill_price,
                fee=fee,
                trade_id=trade_id,
            )
        return self.transition(
            LifecycleEvent.PARTIAL_FILL,
            fill_qty=fill_qty,
            fill_price=fill_price,
            fee=fee,
            trade_id=trade_id,
        )

    def fill(
        self,
        fill_qty: float,
        fill_price: float,
        fee: float = 0.0,
        trade_id: str | None = None,
    ) -> LifecycleState:
        return self.partial_fill(fill_qty, fill_price, fee, trade_id)

    def request_cancel(self) -> LifecycleState:
        return self.transition(LifecycleEvent.CANCEL_REQUEST)

    def acknowledge_cancel(self) -> LifecycleState:
        return self.transition(LifecycleEvent.CANCEL_ACKNOWLEDGE)

    def request_replace(self, new_client_order_id: str | None = None) -> LifecycleState:
        return self.transition(LifecycleEvent.REPLACE_REQUEST, new_client_order_id=new_client_order_id)

    def acknowledge_replace(self) -> LifecycleState:
        return self.transition(LifecycleEvent.REPLACE_ACKNOWLEDGE)

    def reject(self, reason: str, message: str | None = None) -> LifecycleState:
        self.reject_reason = reason
        self.reject_message = message
        return self.transition(LifecycleEvent.REJECT, reason=reason, message=message)

    def expire(self) -> LifecycleState:
        return self.transition(LifecycleEvent.EXPIRE)

    def timeout(self) -> LifecycleState:
        return self.transition(LifecycleEvent.TIMEOUT)

    def retry(self) -> LifecycleState:
        return self.transition(LifecycleEvent.RETRY)

    def is_terminal(self) -> bool:
        return self.state in TERMINAL_STATES

    def is_active(self) -> bool:
        return self.state in ACTIVE_STATES

    def to_dict(self) -> dict[str, Any]:
        return {
            "client_order_id": self.client_order_id,
            "exchange_order_id": self.exchange_order_id,
            "symbol": self.symbol,
            "side": self.side,
            "order_type": self.order_type,
            "quantity": self.quantity,
            "limit_price": self.limit_price,
            "state": self.state.value,
            "filled_quantity": self.filled_quantity,
            "avg_fill_price": self.avg_fill_price,
            "cumulative_fee": self.cumulative_fee,
            "reject_reason": self.reject_reason,
            "reject_message": self.reject_message,
            "transitions": [t.to_dict() for t in self.transitions],
            "metadata": dict(self.metadata),
            "simulated": self.simulated,
            "real_exchange_interaction": self.real_exchange_interaction,
            "execution_environment": self.execution_environment,
        }


class LifecycleValidator:
    """Validates order lifecycle sequences against the state machine."""

    def __init__(self, strict: bool = True):
        self.strict = strict

    def validate_sequence(self, transitions: list[LifecycleTransition]) -> tuple[bool, list[str]]:
        """Validate a sequence of transitions."""
        errors: list[str] = []
        if not transitions:
            return True, errors

        # First transition should be from CREATED
        if transitions[0].from_state != LifecycleState.CREATED:
            errors.append(f"First transition must be from CREATED, got {transitions[0].from_state.value}")

        current_state = LifecycleState.CREATED
        for i, t in enumerate(transitions):
            if t.from_state != current_state:
                errors.append(
                    f"Transition {i}: from_state {t.from_state.value} != expected {current_state.value}"
                )
            key = (t.from_state, t.event)
            if key not in VALID_TRANSITIONS:
                errors.append(
                    f"Transition {i}: invalid transition {t.from_state.value} --{t.event.value}-->"
                )
            else:
                expected_to = VALID_TRANSITIONS[key]
                if t.to_state != expected_to:
                    errors.append(
                        f"Transition {i}: to_state {t.to_state.value} != expected {expected_to.value}"
                    )
            current_state = t.to_state

        return len(errors) == 0, errors

    def validate_lifecycle(self, lifecycle: OrderLifecycle) -> tuple[bool, list[str]]:
        """Validate an OrderLifecycle object."""
        return self.validate_sequence(lifecycle.transitions)


class LifecycleHarness:
    """Test harness for exercising order lifecycle scenarios."""

    def __init__(
        self,
        *,
        simulated: bool = True,
        real_exchange_interaction: bool = False,
        execution_environment: str = "paper",
    ):
        self.simulated = simulated
        self.real_exchange_interaction = real_exchange_interaction
        self.execution_environment = execution_environment
        self.lifecycles: dict[str, OrderLifecycle] = {}

    def create_order(
        self,
        client_order_id: str,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        limit_price: float | None = None,
    ) -> OrderLifecycle:
        lifecycle = OrderLifecycle(
            client_order_id=client_order_id,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            limit_price=limit_price,
            simulated=self.simulated,
            real_exchange_interaction=self.real_exchange_interaction,
            execution_environment=self.execution_environment,
        )
        self.lifecycles[client_order_id] = lifecycle
        return lifecycle

    def get(self, client_order_id: str) -> OrderLifecycle | None:
        return self.lifecycles.get(client_order_id)

    def run_full_lifecycle_market(self, client_order_id: str, market_price: float) -> OrderLifecycle:
        """Run complete market order lifecycle: submit -> ack -> fill."""
        lifecycle = self.get(client_order_id)
        if lifecycle is None:
            raise KeyError(f"Unknown client_order_id: {client_order_id}")
        lifecycle.submit()
        lifecycle.acknowledge()
        lifecycle.fill(lifecycle.quantity, market_price)
        return lifecycle

    def run_full_lifecycle_limit(
        self,
        client_order_id: str,
        market_price: float,
        *,
        crosses: bool = True,
    ) -> OrderLifecycle:
        """Run complete limit order lifecycle."""
        lifecycle = self.get(client_order_id)
        if lifecycle is None:
            raise KeyError(f"Unknown client_order_id: {client_order_id}")
        lifecycle.submit()
        lifecycle.acknowledge()
        if crosses:
            lifecycle.fill(lifecycle.quantity, market_price)
        else:
            lifecycle.expire()
        return lifecycle

    def run_partial_fill_then_complete(
        self,
        client_order_id: str,
        partial_qty: float,
        partial_price: float,
        final_price: float,
    ) -> OrderLifecycle:
        """Run partial fill then complete fill lifecycle."""
        lifecycle = self.get(client_order_id)
        if lifecycle is None:
            raise KeyError(f"Unknown client_order_id: {client_order_id}")
        lifecycle.submit()
        lifecycle.acknowledge()
        lifecycle.partial_fill(partial_qty, partial_price)
        lifecycle.fill(lifecycle.quantity - lifecycle.filled_quantity, final_price)
        return lifecycle

    def run_cancel_before_fill(self, client_order_id: str) -> OrderLifecycle:
        """Run cancel before fill lifecycle."""
        lifecycle = self.get(client_order_id)
        if lifecycle is None:
            raise KeyError(f"Unknown client_order_id: {client_order_id}")
        lifecycle.submit()
        lifecycle.acknowledge()
        lifecycle.request_cancel()
        lifecycle.acknowledge_cancel()
        return lifecycle

    def run_cancel_after_partial(self, client_order_id: str, partial_qty: float, partial_price: float) -> OrderLifecycle:
        """Run partial fill then cancel."""
        lifecycle = self.get(client_order_id)
        if lifecycle is None:
            raise KeyError(f"Unknown client_order_id: {client_order_id}")
        lifecycle.submit()
        lifecycle.acknowledge()
        lifecycle.partial_fill(partial_qty, partial_price)
        lifecycle.request_cancel()
        lifecycle.acknowledge_cancel()
        return lifecycle

    def run_replace(self, client_order_id: str, new_client_order_id: str) -> OrderLifecycle:
        """Run replace lifecycle."""
        lifecycle = self.get(client_order_id)
        if lifecycle is None:
            raise KeyError(f"Unknown client_order_id: {client_order_id}")
        lifecycle.submit()
        lifecycle.acknowledge()
        lifecycle.request_replace(new_client_order_id)
        lifecycle.acknowledge_replace()
        return lifecycle

    def run_reject(self, client_order_id: str, reason: str, message: str | None = None) -> OrderLifecycle:
        """Run reject lifecycle."""
        lifecycle = self.get(client_order_id)
        if lifecycle is None:
            raise KeyError(f"Unknown client_order_id: {client_order_id}")
        lifecycle.submit()
        lifecycle.reject(reason, message)
        return lifecycle

    def run_timeout_retry(self, client_order_id: str) -> OrderLifecycle:
        """Run timeout then retry lifecycle."""
        lifecycle = self.get(client_order_id)
        if lifecycle is None:
            raise KeyError(f"Unknown client_order_id: {client_order_id}")
        lifecycle.submit()
        lifecycle.timeout()
        lifecycle.retry()
        lifecycle.acknowledge()
        return lifecycle

    def export_all(self) -> list[dict[str, Any]]:
        return [lc.to_dict() for lc in self.lifecycles.values()]


def create_test_lifecycle_scenarios() -> dict[str, list[LifecycleTransition]]:
    """Create canonical lifecycle scenarios for testing."""
    scenarios = {}

    # Market order: submit -> ack -> fill
    scenarios["market_fill"] = [
        LifecycleTransition(LifecycleState.CREATED, LifecycleEvent.SUBMIT, LifecycleState.SUBMITTED, _utc_now_iso()),
        LifecycleTransition(LifecycleState.SUBMITTED, LifecycleEvent.ACKNOWLEDGE, LifecycleState.ACKNOWLEDGED, _utc_now_iso()),
        LifecycleTransition(LifecycleState.ACKNOWLEDGED, LifecycleEvent.FILL, LifecycleState.FILLED, _utc_now_iso()),
    ]

    # Limit order crosses: submit -> ack -> fill
    scenarios["limit_cross_fill"] = [
        LifecycleTransition(LifecycleState.CREATED, LifecycleEvent.SUBMIT, LifecycleState.SUBMITTED, _utc_now_iso()),
        LifecycleTransition(LifecycleState.SUBMITTED, LifecycleEvent.ACKNOWLEDGE, LifecycleState.ACKNOWLEDGED, _utc_now_iso()),
        LifecycleTransition(LifecycleState.ACKNOWLEDGED, LifecycleEvent.FILL, LifecycleState.FILLED, _utc_now_iso()),
    ]

    # Limit order expires: submit -> ack -> expire
    scenarios["limit_expire"] = [
        LifecycleTransition(LifecycleState.CREATED, LifecycleEvent.SUBMIT, LifecycleState.SUBMITTED, _utc_now_iso()),
        LifecycleTransition(LifecycleState.SUBMITTED, LifecycleEvent.ACKNOWLEDGE, LifecycleState.ACKNOWLEDGED, _utc_now_iso()),
        LifecycleTransition(LifecycleState.ACKNOWLEDGED, LifecycleEvent.EXPIRE, LifecycleState.EXPIRED, _utc_now_iso()),
    ]

    # Partial then full fill
    scenarios["partial_then_full"] = [
        LifecycleTransition(LifecycleState.CREATED, LifecycleEvent.SUBMIT, LifecycleState.SUBMITTED, _utc_now_iso()),
        LifecycleTransition(LifecycleState.SUBMITTED, LifecycleEvent.ACKNOWLEDGE, LifecycleState.ACKNOWLEDGED, _utc_now_iso()),
        LifecycleTransition(LifecycleState.ACKNOWLEDGED, LifecycleEvent.PARTIAL_FILL, LifecycleState.PARTIALLY_FILLED, _utc_now_iso()),
        LifecycleTransition(LifecycleState.PARTIALLY_FILLED, LifecycleEvent.FILL, LifecycleState.FILLED, _utc_now_iso()),
    ]

    # Cancel before fill
    scenarios["cancel_before_fill"] = [
        LifecycleTransition(LifecycleState.CREATED, LifecycleEvent.SUBMIT, LifecycleState.SUBMITTED, _utc_now_iso()),
        LifecycleTransition(LifecycleState.SUBMITTED, LifecycleEvent.ACKNOWLEDGE, LifecycleState.ACKNOWLEDGED, _utc_now_iso()),
        LifecycleTransition(LifecycleState.ACKNOWLEDGED, LifecycleEvent.CANCEL_REQUEST, LifecycleState.CANCEL_REQUESTED, _utc_now_iso()),
        LifecycleTransition(LifecycleState.CANCEL_REQUESTED, LifecycleEvent.CANCEL_ACKNOWLEDGE, LifecycleState.CANCELED, _utc_now_iso()),
    ]

    # Cancel after partial fill
    scenarios["cancel_after_partial"] = [
        LifecycleTransition(LifecycleState.CREATED, LifecycleEvent.SUBMIT, LifecycleState.SUBMITTED, _utc_now_iso()),
        LifecycleTransition(LifecycleState.SUBMITTED, LifecycleEvent.ACKNOWLEDGE, LifecycleState.ACKNOWLEDGED, _utc_now_iso()),
        LifecycleTransition(LifecycleState.ACKNOWLEDGED, LifecycleEvent.PARTIAL_FILL, LifecycleState.PARTIALLY_FILLED, _utc_now_iso()),
        LifecycleTransition(LifecycleState.PARTIALLY_FILLED, LifecycleEvent.CANCEL_REQUEST, LifecycleState.CANCEL_REQUESTED, _utc_now_iso()),
        LifecycleTransition(LifecycleState.CANCEL_REQUESTED, LifecycleEvent.CANCEL_ACKNOWLEDGE, LifecycleState.CANCELED, _utc_now_iso()),
    ]

    # Replace order
    scenarios["replace_order"] = [
        LifecycleTransition(LifecycleState.CREATED, LifecycleEvent.SUBMIT, LifecycleState.SUBMITTED, _utc_now_iso()),
        LifecycleTransition(LifecycleState.SUBMITTED, LifecycleEvent.ACKNOWLEDGE, LifecycleState.ACKNOWLEDGED, _utc_now_iso()),
        LifecycleTransition(LifecycleState.ACKNOWLEDGED, LifecycleEvent.REPLACE_REQUEST, LifecycleState.REPLACE_REQUESTED, _utc_now_iso()),
        LifecycleTransition(LifecycleState.REPLACE_REQUESTED, LifecycleEvent.REPLACE_ACKNOWLEDGE, LifecycleState.REPLACED, _utc_now_iso()),
    ]

    # Reject
    scenarios["reject"] = [
        LifecycleTransition(LifecycleState.CREATED, LifecycleEvent.SUBMIT, LifecycleState.SUBMITTED, _utc_now_iso()),
        LifecycleTransition(LifecycleState.SUBMITTED, LifecycleEvent.REJECT, LifecycleState.REJECTED, _utc_now_iso()),
    ]

    # Timeout then retry
    scenarios["timeout_retry"] = [
        LifecycleTransition(LifecycleState.CREATED, LifecycleEvent.SUBMIT, LifecycleState.SUBMITTED, _utc_now_iso()),
        LifecycleTransition(LifecycleState.SUBMITTED, LifecycleEvent.TIMEOUT, LifecycleState.TIMEOUT, _utc_now_iso()),
        LifecycleTransition(LifecycleState.TIMEOUT, LifecycleEvent.RETRY, LifecycleState.SUBMITTED, _utc_now_iso()),
        LifecycleTransition(LifecycleState.SUBMITTED, LifecycleEvent.ACKNOWLEDGE, LifecycleState.ACKNOWLEDGED, _utc_now_iso()),
    ]

    return scenarios
