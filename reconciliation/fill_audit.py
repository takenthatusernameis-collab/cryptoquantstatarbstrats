"""Fill audit trail with client_order_id ↔ exchange_order_id linkage."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional
from decimal import Decimal
import uuid


@dataclass
class FillAuditRecord:
    """Single fill audit record."""

    fill_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    client_order_id: str = ""
    exchange_order_id: Optional[str] = None
    symbol: str = ""
    exchange: str = ""
    side: str = ""  # "buy" or "sell"
    quantity: Decimal = Decimal("0")
    price: Decimal = Decimal("0")
    fee: Decimal = Decimal("0")
    fee_currency: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    liquidity: str = ""  # "maker" or "taker"
    metadata: Dict = field(default_factory=dict)


@dataclass
class FillAuditResult:
    """Result of fill audit."""

    total_fills: int = 0
    matched_fills: int = 0
    unmatched_client_orders: List[str] = field(default_factory=list)
    unmatched_exchange_orders: List[str] = field(default_factory=list)
    quantity_mismatches: List[Dict] = field(default_factory=list)
    price_mismatches: List[Dict] = field(default_factory=list)
    duplicate_fills: List[str] = field(default_factory=list)
    missing_fills: List[str] = field(default_factory=list)
    passed: bool = True
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    audit_id: str = field(default_factory=lambda: str(uuid.uuid4()))


class FillAuditor:
    """Audit fill records for completeness and correctness."""

    def __init__(self):
        self._internal_fills: Dict[str, FillAuditRecord] = {}  # keyed by client_order_id
        self._exchange_fills: Dict[str, FillAuditRecord] = {}  # keyed by exchange_order_id
        self._fill_sequence: List[FillAuditRecord] = []

    def record_internal_fill(self, record: FillAuditRecord) -> None:
        """Record a fill from internal system."""
        self._internal_fills[record.client_order_id] = record
        self._fill_sequence.append(record)

    def record_exchange_fill(self, record: FillAuditRecord) -> None:
        """Record a fill from exchange."""
        if record.exchange_order_id:
            self._exchange_fills[record.exchange_order_id] = record

    def link_fills(self, client_order_id: str, exchange_order_id: str) -> bool:
        """Link internal and exchange fill records."""
        if client_order_id in self._internal_fills:
            self._internal_fills[client_order_id].exchange_order_id = exchange_order_id
            return True
        return False

    def audit(self, quantity_tolerance: Decimal = Decimal("1e-8"), price_tolerance: Decimal = Decimal("1e-8")) -> FillAuditResult:
        """Perform fill audit."""
        result = FillAuditResult()
        result.total_fills = len(self._fill_sequence)

        matched_client_ids = set()
        matched_exchange_ids = set()
        seen_client_ids = set()
        seen_exchange_ids = set()

        for fill in self._fill_sequence:
            # Check for duplicate client_order_ids
            if fill.client_order_id in seen_client_ids:
                result.duplicate_fills.append(fill.client_order_id)
                result.passed = False
            seen_client_ids.add(fill.client_order_id)

            # Check linkage
            if fill.exchange_order_id:
                if fill.exchange_order_id in self._exchange_fills:
                    exchange_fill = self._exchange_fills[fill.exchange_order_id]
                    matched_client_ids.add(fill.client_order_id)
                    matched_exchange_ids.add(fill.exchange_order_id)

                    # Check quantity match
                    if abs(fill.quantity - exchange_fill.quantity) > quantity_tolerance:
                        result.quantity_mismatches.append({
                            "client_order_id": fill.client_order_id,
                            "exchange_order_id": fill.exchange_order_id,
                            "internal_qty": str(fill.quantity),
                            "exchange_qty": str(exchange_fill.quantity),
                            "diff": str(abs(fill.quantity - exchange_fill.quantity)),
                        })
                        result.passed = False

                    # Check price match
                    if abs(fill.price - exchange_fill.price) > price_tolerance:
                        result.price_mismatches.append({
                            "client_order_id": fill.client_order_id,
                            "exchange_order_id": fill.exchange_order_id,
                            "internal_price": str(fill.price),
                            "exchange_price": str(exchange_fill.price),
                            "diff": str(abs(fill.price - exchange_fill.price)),
                        })
                        result.passed = False
                else:
                    result.unmatched_exchange_orders.append(fill.exchange_order_id)
                    result.passed = False
            else:
                result.unmatched_client_orders.append(fill.client_order_id)
                result.passed = False

        # Check for exchange fills without internal records
        for exchange_id, exchange_fill in self._exchange_fills.items():
            if exchange_id not in matched_exchange_ids:
                result.unmatched_exchange_orders.append(exchange_id)
                result.passed = False

        result.matched_fills = len(matched_client_ids)
        return result

    def get_audit_trail(self) -> List[FillAuditRecord]:
        """Get complete audit trail."""
        return list(self._fill_sequence)

    def clear(self) -> None:
        """Clear all records."""
        self._internal_fills.clear()
        self._exchange_fills.clear()
        self._fill_sequence.clear()