"""Cash reconciliation against exchange or paper ledger."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, List, Optional


@dataclass
class CashSnapshot:
    """Cash balance snapshot from a source."""

    source: str  # "exchange", "paper", "internal"
    currency: str
    available: Decimal
    locked: Decimal = Decimal("0")
    total: Optional[Decimal] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict = field(default_factory=dict)

    def __post_init__(self):
        if self.total is None:
            self.total = self.available + self.locked


@dataclass
class CashReconciliationResult:
    """Result of cash reconciliation."""

    currency: str
    exchange_cash: Optional[CashSnapshot] = None
    internal_cash: Optional[CashSnapshot] = None
    paper_cash: Optional[CashSnapshot] = None
    available_diff: Decimal = Decimal("0")
    total_diff: Decimal = Decimal("0")
    within_tolerance: bool = True
    tolerance: Decimal = Decimal("1e-2")
    details: Dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    check_id: str = field(default_factory=lambda: str(uuid.uuid4()))


class CashReconciler:
    """Reconcile cash balances between exchange, paper ledger, and internal state."""

    def __init__(self, tolerance: Decimal = Decimal("1e-2")):
        self.tolerance = tolerance
        self._exchange_cash: Dict[str, CashSnapshot] = {}
        self._internal_cash: Dict[str, CashSnapshot] = {}
        self._paper_cash: Dict[str, CashSnapshot] = {}

    def update_exchange_cash(self, snapshot: CashSnapshot) -> None:
        """Update exchange cash snapshot."""
        self._exchange_cash[snapshot.currency] = snapshot

    def update_internal_cash(self, snapshot: CashSnapshot) -> None:
        """Update internal cash snapshot."""
        self._internal_cash[snapshot.currency] = snapshot

    def update_paper_cash(self, snapshot: CashSnapshot) -> None:
        """Update paper cash snapshot."""
        self._paper_cash[snapshot.currency] = snapshot

    def reconcile_currency(self, currency: str) -> CashReconciliationResult:
        """Reconcile a single currency."""
        exchange = self._exchange_cash.get(currency)
        internal = self._internal_cash.get(currency)
        paper = self._paper_cash.get(currency)

        exchange_avail = exchange.available if exchange else Decimal("0")
        exchange_total = exchange.total if exchange else Decimal("0")
        internal_avail = internal.available if internal else Decimal("0")
        internal_total = internal.total if internal else Decimal("0")
        paper_avail = paper.available if paper else Decimal("0")
        paper_total = paper.total if paper else Decimal("0")

        reference_avail = exchange_avail if exchange else internal_avail
        reference_total = exchange_total if exchange else internal_total

        available_diff = abs(reference_avail - internal_avail)
        total_diff = abs(reference_total - internal_total)

        within_tolerance = (available_diff <= self.tolerance) and (total_diff <= self.tolerance)

        result = CashReconciliationResult(
            currency=currency,
            exchange_cash=exchange,
            internal_cash=internal,
            paper_cash=paper,
            available_diff=available_diff,
            total_diff=total_diff,
            within_tolerance=within_tolerance,
            tolerance=self.tolerance,
            details={
                "exchange_available": str(exchange_avail),
                "exchange_total": str(exchange_total),
                "internal_available": str(internal_avail),
                "internal_total": str(internal_total),
                "paper_available": str(paper_avail),
                "paper_total": str(paper_total),
                "reference_available": str(reference_avail),
                "reference_total": str(reference_total),
            },
        )
        return result

    def reconcile_all(self) -> List[CashReconciliationResult]:
        """Reconcile all known currencies."""
        all_currencies = set()
        all_currencies.update(self._exchange_cash.keys())
        all_currencies.update(self._internal_cash.keys())
        all_currencies.update(self._paper_cash.keys())

        return [self.reconcile_currency(currency) for currency in sorted(all_currencies)]

    def get_failed_reconciliations(self) -> List[CashReconciliationResult]:
        """Get only failed reconciliations."""
        return [r for r in self.reconcile_all() if not r.within_tolerance]

    def clear(self) -> None:
        """Clear all cash snapshots."""
        self._exchange_cash.clear()
        self._internal_cash.clear()
        self._paper_cash.clear()
