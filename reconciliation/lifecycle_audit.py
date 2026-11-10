"""Order lifecycle state machine audit."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Set


class OrderState(str, Enum):
    """Valid order states."""

    CREATED = "created"
    SUBMITTED = "submitted"
    ACKNOWLEDGED = "acknowledged"
    PARTIAL_FILL = "partial_fill"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"
    MODIFIED = "modified"


# Valid state transitions
VALID_TRANSITIONS: Dict[OrderState, Set[OrderState]] = {
    OrderState.CREATED: {OrderState.SUBMITTED, OrderState.CANCELLED, OrderState.REJECTED},
    OrderState.SUBMITTED: {OrderState.ACKNOWLEDGED, OrderState.REJECTED, OrderState.CANCELLED},
    OrderState.ACKNOWLEDGED: {
        OrderState.PARTIAL_FILL,
        OrderState.FILLED,
        OrderState.CANCELLED,
        OrderState.EXPIRED,
        OrderState.MODIFIED,
    },
    OrderState.PARTIAL_FILL: {
        OrderState.PARTIAL_FILL,
        OrderState.FILLED,
        OrderState.CANCELLED,
        OrderState.EXPIRED,
    },
    OrderState.FILLED: set(),  # Terminal state
    OrderState.CANCELLED: set(),  # Terminal state
    OrderState.REJECTED: set(),  # Terminal state
    OrderState.EXPIRED: set(),  # Terminal state
    OrderState.MODIFIED: {
        OrderState.PARTIAL_FILL,
        OrderState.FILLED,
        OrderState.CANCELLED,
        OrderState.EXPIRED,
        OrderState.MODIFIED,
    },
}

TERMINAL_STATES = {
    OrderState.FILLED,
    OrderState.CANCELLED,
    OrderState.REJECTED,
    OrderState.EXPIRED,
}


@dataclass
class StateTransition:
    """Order state transition record."""

    transition_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    order_id: str = ""
    client_order_id: str = ""
    from_state: OrderState = OrderState.CREATED
    to_state: OrderState = OrderState.CREATED
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    valid: bool = True
    error: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


@dataclass
class OrderLifecycleRecord:
    """Complete order lifecycle record."""

    order_id: str
    client_order_id: str
    symbol: str
    side: str
    order_type: str
    quantity: float
    price: Optional[float] = None
    current_state: OrderState = OrderState.CREATED
    transitions: List[StateTransition] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    exchange_order_id: Optional[str] = None
    filled_quantity: float = 0.0
    avg_fill_price: Optional[float] = None
    error: Optional[str] = None


@dataclass
class LifecycleAuditResult:
    """Result of lifecycle audit."""

    total_orders: int = 0
    valid_transitions: int = 0
    invalid_transitions: List[Dict] = field(default_factory=list)
    orphan_orders: List[str] = field(default_factory=list)  # Orders stuck in non-terminal state
    terminal_without_fill: List[str] = field(
        default_factory=list
    )  # Cancelled/rejected without fill
    missing_initial_state: List[str] = field(default_factory=list)
    duplicate_transitions: List[str] = field(default_factory=list)
    passed: bool = True
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    audit_id: str = field(default_factory=lambda: str(uuid.uuid4()))


class LifecycleAuditor:
    """Audit order lifecycle state machine for validity."""

    def __init__(self):
        self._orders: Dict[str, OrderLifecycleRecord] = {}

    def record_transition(
        self,
        order_id: str,
        client_order_id: str,
        from_state: OrderState,
        to_state: OrderState,
        symbol: str = "",
        side: str = "",
        order_type: str = "",
        quantity: float = 0.0,
        price: Optional[float] = None,
        exchange_order_id: Optional[str] = None,
        filled_quantity: float = 0.0,
        avg_fill_price: Optional[float] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> StateTransition:
        """Record a state transition."""
        # Get or create order record
        if order_id not in self._orders:
            self._orders[order_id] = OrderLifecycleRecord(
                order_id=order_id,
                client_order_id=client_order_id,
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=price,
                exchange_order_id=exchange_order_id,
            )

        order = self._orders[order_id]

        # Validate transition
        valid = to_state in VALID_TRANSITIONS.get(from_state, set())
        transition_error = None
        if not valid:
            transition_error = (
                f"Invalid transition: {from_state.value} -> {to_state.value}"
            )

        transition = StateTransition(
            order_id=order_id,
            client_order_id=client_order_id,
            from_state=from_state,
            to_state=to_state,
            valid=valid,
            error=transition_error,
            metadata=metadata or {},
        )

        order.transitions.append(transition)
        order.current_state = to_state
        order.updated_at = datetime.now(timezone.utc)

        if exchange_order_id:
            order.exchange_order_id = exchange_order_id
        if filled_quantity > order.filled_quantity:
            order.filled_quantity = filled_quantity
        if avg_fill_price:
            order.avg_fill_price = avg_fill_price
        if error:
            order.error = error

        return transition

    def audit(self) -> LifecycleAuditResult:
        """Perform lifecycle audit."""
        result = LifecycleAuditResult()
        result.total_orders = len(self._orders)

        for order_id, order in self._orders.items():
            # Check for missing initial state
            if not order.transitions:
                result.missing_initial_state.append(order_id)
                result.passed = False
                continue

            # Check first state is CREATED
            first_transition = order.transitions[0]
            if first_transition.from_state != OrderState.CREATED:
                result.missing_initial_state.append(order_id)
                result.passed = False

            # Check each transition
            seen_transitions = set()

            for transition in order.transitions:
                # Check for duplicate transitions
                trans_key = (transition.from_state.value, transition.to_state.value)
                if trans_key in seen_transitions:
                    result.duplicate_transitions.append(f"{order_id}: {trans_key}")
                    result.passed = False
                seen_transitions.add(trans_key)

                # Validate transition
                if transition.valid:
                    result.valid_transitions += 1
                else:
                    result.invalid_transitions.append({
                        "order_id": order_id,
                        "client_order_id": order.client_order_id,
                        "from_state": transition.from_state.value,
                        "to_state": transition.to_state.value,
                        "error": transition.error,
                    })
                    result.passed = False


            # Check for orphan orders (stuck in non-terminal state)
            if order.current_state not in TERMINAL_STATES:
                result.orphan_orders.append(order_id)
                result.passed = False

            # Check terminal states without fills
            if order.current_state in {
                OrderState.CANCELLED,
                OrderState.REJECTED,
                OrderState.EXPIRED,
            }:
                if order.filled_quantity == 0:
                    result.terminal_without_fill.append(order_id)

        return result

    def get_order_record(self, order_id: str) -> Optional[OrderLifecycleRecord]:
        """Get order lifecycle record."""
        return self._orders.get(order_id)

    def get_all_orders(self) -> List[OrderLifecycleRecord]:
        """Get all order records."""
        return list(self._orders.values())

    def clear(self) -> None:
        """Clear all records."""
        self._orders.clear()
