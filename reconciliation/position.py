"""Position reconciliation against exchange or paper ledger."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional
from decimal import Decimal
import uuid


@dataclass
class PositionSnapshot:
    """Position snapshot from a source."""

    source: str  # "exchange", "paper", "internal"
    symbol: str
    quantity: Decimal
    avg_entry_price: Optional[Decimal] = None
    unrealized_pnl: Optional[Decimal] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict = field(default_factory=dict)


@dataclass
class PositionReconciliationResult:
    """Result of position reconciliation."""

    symbol: str
    exchange_position: Optional[PositionSnapshot] = None
    internal_position: Optional[PositionSnapshot] = None
    paper_position: Optional[PositionSnapshot] = None
    quantity_diff: Decimal = Decimal("0")
    within_tolerance: bool = True
    tolerance: Decimal = Decimal("1e-6")
    details: Dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    check_id: str = field(default_factory=lambda: str(uuid.uuid4()))


class PositionReconciler:
    """Reconcile positions between exchange, paper ledger, and internal state."""

    def __init__(self, tolerance: Decimal = Decimal("1e-6")):
        self.tolerance = tolerance
        self._exchange_positions: Dict[str, PositionSnapshot] = {}
        self._internal_positions: Dict[str, PositionSnapshot] = {}
        self._paper_positions: Dict[str, PositionSnapshot] = {}

    def update_exchange_position(self, snapshot: PositionSnapshot) -> None:
        """Update exchange position snapshot."""
        self._exchange_positions[snapshot.symbol] = snapshot

    def update_internal_position(self, snapshot: PositionSnapshot) -> None:
        """Update internal position snapshot."""
        self._internal_positions[snapshot.symbol] = snapshot

    def update_paper_position(self, snapshot: PositionSnapshot) -> None:
        """Update paper position snapshot."""
        self._paper_positions[snapshot.symbol] = snapshot

    def reconcile_symbol(self, symbol: str) -> PositionReconciliationResult:
        """Reconcile a single symbol."""
        exchange = self._exchange_positions.get(symbol)
        internal = self._internal_positions.get(symbol)
        paper = self._paper_positions.get(symbol)

        # Compare exchange vs internal
        exchange_qty = exchange.quantity if exchange else Decimal("0")
        internal_qty = internal.quantity if internal else Decimal("0")
        paper_qty = paper.quantity if paper else Decimal("0")

        # Use exchange as source of truth if available, otherwise internal
        reference = exchange_qty if exchange else internal_qty
        quantity_diff = abs(reference - internal_qty)
        within_tolerance = quantity_diff <= self.tolerance

        result = PositionReconciliationResult(
            symbol=symbol,
            exchange_position=exchange,
            internal_position=internal,
            paper_position=paper,
            quantity_diff=quantity_diff,
            within_tolerance=within_tolerance,
            tolerance=self.tolerance,
            details={
                "exchange_qty": str(exchange_qty),
                "internal_qty": str(internal_qty),
                "paper_qty": str(paper_qty),
                "reference_qty": str(reference),
            },
        )
        return result

    def reconcile_all(self) -> List[PositionReconciliationResult]:
        """Reconcile all known symbols."""
        all_symbols = set()
        all_symbols.update(self._exchange_positions.keys())
        all_symbols.update(self._internal_positions.keys())
        all_symbols.update(self._paper_positions.keys())

        return [self.reconcile_symbol(symbol) for symbol in sorted(all_symbols)]

    def get_failed_reconciliations(self) -> List[PositionReconciliationResult]:
        """Get only failed reconciliations."""
        return [r for r in self.reconcile_all() if not r.within_tolerance]

    def clear(self) -> None:
        """Clear all position snapshots."""
        self._exchange_positions.clear()
        self._internal_positions.clear()
        self._paper_positions.clear()