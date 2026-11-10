"""Equity reconciliation against exchange or paper ledger."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Optional


@dataclass
class EquitySnapshot:
    """Equity snapshot from a source."""

    source: str  # "exchange", "paper", "internal"
    total_equity: Decimal
    unrealized_pnl: Decimal = Decimal("0")
    realized_pnl: Decimal = Decimal("0")
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict = field(default_factory=dict)


@dataclass
class EquityReconciliationResult:
    """Result of equity reconciliation."""

    exchange_equity: Optional[EquitySnapshot] = None
    internal_equity: Optional[EquitySnapshot] = None
    paper_equity: Optional[EquitySnapshot] = None
    equity_diff: Decimal = Decimal("0")
    within_tolerance: bool = True
    tolerance: Decimal = Decimal("1e-4")
    details: Dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    check_id: str = field(default_factory=lambda: str(uuid.uuid4()))


class EquityReconciler:
    """Reconcile equity between exchange, paper ledger, and internal state."""

    def __init__(self, tolerance: Decimal = Decimal("1e-4")):
        self.tolerance = tolerance
        self._exchange_equity: Optional[EquitySnapshot] = None
        self._internal_equity: Optional[EquitySnapshot] = None
        self._paper_equity: Optional[EquitySnapshot] = None

    def update_exchange_equity(self, snapshot: EquitySnapshot) -> None:
        """Update exchange equity snapshot."""
        self._exchange_equity = snapshot

    def update_internal_equity(self, snapshot: EquitySnapshot) -> None:
        """Update internal equity snapshot."""
        self._internal_equity = snapshot

    def update_paper_equity(self, snapshot: EquitySnapshot) -> None:
        """Update paper equity snapshot."""
        self._paper_equity = snapshot

    def reconcile(self) -> EquityReconciliationResult:
        """Reconcile equity."""
        exchange = self._exchange_equity
        internal = self._internal_equity
        paper = self._paper_equity

        exchange_eq = exchange.total_equity if exchange else Decimal("0")
        internal_eq = internal.total_equity if internal else Decimal("0")
        paper_eq = paper.total_equity if paper else Decimal("0")

        reference = exchange_eq if exchange else internal_eq
        equity_diff = abs(reference - internal_eq)
        within_tolerance = equity_diff <= self.tolerance

        result = EquityReconciliationResult(
            exchange_equity=exchange,
            internal_equity=internal,
            paper_equity=paper,
            equity_diff=equity_diff,
            within_tolerance=within_tolerance,
            tolerance=self.tolerance,
            details={
                "exchange_equity": str(exchange_eq),
                "internal_equity": str(internal_eq),
                "paper_equity": str(paper_eq),
                "reference_equity": str(reference),
            },
        )
        return result

    def clear(self) -> None:
        """Clear all equity snapshots."""
        self._exchange_equity = None
        self._internal_equity = None
        self._paper_equity = None
