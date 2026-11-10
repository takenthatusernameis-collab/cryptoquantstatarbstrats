"""Reconciliation orchestrator combining all reconciliation checks."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional

from .cash import CashReconciler, CashReconciliationResult, CashSnapshot
from .equity import EquityReconciler, EquityReconciliationResult, EquitySnapshot
from .fill_audit import FillAuditor, FillAuditRecord, FillAuditResult
from .lifecycle_audit import (
    LifecycleAuditor,
    LifecycleAuditResult,
    OrderState,
)
from .position import PositionReconciler, PositionReconciliationResult, PositionSnapshot


@dataclass
class ReconciliationConfig:
    """Configuration for reconciliation orchestrator."""

    position_tolerance: Decimal = Decimal("1e-6")
    cash_tolerance: Decimal = Decimal("1e-2")
    equity_tolerance: Decimal = Decimal("1e-4")
    fill_quantity_tolerance: Decimal = Decimal("1e-8")
    fill_price_tolerance: Decimal = Decimal("1e-8")
    enabled_checks: List[str] = field(default_factory=lambda: [
        "position",
        "cash",
        "equity",
        "fill_audit",
        "lifecycle_audit",
    ])
    interval_seconds: int = 60


@dataclass
class ReconciliationResult:
    """Combined reconciliation result."""

    check_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    position_results: List[PositionReconciliationResult] = field(default_factory=list)
    cash_results: List[CashReconciliationResult] = field(default_factory=list)
    equity_result: Optional[EquityReconciliationResult] = None
    fill_audit_result: Optional[FillAuditResult] = None
    lifecycle_audit_result: Optional[LifecycleAuditResult] = None
    overall_passed: bool = True
    failed_checks: List[str] = field(default_factory=list)
    duration_ms: float = 0.0


class ReconciliationOrchestrator:
    """Orchestrate all reconciliation checks."""

    def __init__(self, config: Optional[ReconciliationConfig] = None):
        self.config = config or ReconciliationConfig()
        self.position_reconciler = PositionReconciler(tolerance=self.config.position_tolerance)
        self.cash_reconciler = CashReconciler(tolerance=self.config.cash_tolerance)
        self.equity_reconciler = EquityReconciler(tolerance=self.config.equity_tolerance)
        self.fill_auditor = FillAuditor()
        self.lifecycle_auditor = LifecycleAuditor()

    def run_reconciliation(self) -> ReconciliationResult:
        """Run all enabled reconciliation checks."""
        import time
        start = time.perf_counter()

        result = ReconciliationResult()

        if "position" in self.config.enabled_checks:
            result.position_results = self.position_reconciler.reconcile_all()
            failed = [r for r in result.position_results if not r.within_tolerance]
            if failed:
                result.overall_passed = False
                result.failed_checks.append("position")

        if "cash" in self.config.enabled_checks:
            result.cash_results = self.cash_reconciler.reconcile_all()
            failed = [r for r in result.cash_results if not r.within_tolerance]
            if failed:
                result.overall_passed = False
                result.failed_checks.append("cash")

        if "equity" in self.config.enabled_checks:
            result.equity_result = self.equity_reconciler.reconcile()
            if result.equity_result and not result.equity_result.within_tolerance:
                result.overall_passed = False
                result.failed_checks.append("equity")

        if "fill_audit" in self.config.enabled_checks:
            result.fill_audit_result = self.fill_auditor.audit(
                quantity_tolerance=self.config.fill_quantity_tolerance,
                price_tolerance=self.config.fill_price_tolerance,
            )
            if result.fill_audit_result and not result.fill_audit_result.passed:
                result.overall_passed = False
                result.failed_checks.append("fill_audit")

        if "lifecycle_audit" in self.config.enabled_checks:
            result.lifecycle_audit_result = self.lifecycle_auditor.audit()
            if result.lifecycle_audit_result and not result.lifecycle_audit_result.passed:
                result.overall_passed = False
                result.failed_checks.append("lifecycle_audit")

        result.duration_ms = (time.perf_counter() - start) * 1000
        return result

    # Convenience methods for updating data
    def update_exchange_position(self, snapshot: PositionSnapshot) -> None:
        self.position_reconciler.update_exchange_position(snapshot)

    def update_internal_position(self, snapshot: PositionSnapshot) -> None:
        self.position_reconciler.update_internal_position(snapshot)

    def update_paper_position(self, snapshot: PositionSnapshot) -> None:
        self.position_reconciler.update_paper_position(snapshot)

    def update_exchange_cash(self, snapshot: CashSnapshot) -> None:
        self.cash_reconciler.update_exchange_cash(snapshot)

    def update_internal_cash(self, snapshot: CashSnapshot) -> None:
        self.cash_reconciler.update_internal_cash(snapshot)

    def update_paper_cash(self, snapshot: CashSnapshot) -> None:
        self.cash_reconciler.update_paper_cash(snapshot)

    def update_exchange_equity(self, snapshot: EquitySnapshot) -> None:
        self.equity_reconciler.update_exchange_equity(snapshot)

    def update_internal_equity(self, snapshot: EquitySnapshot) -> None:
        self.equity_reconciler.update_internal_equity(snapshot)

    def update_paper_equity(self, snapshot: EquitySnapshot) -> None:
        self.equity_reconciler.update_paper_equity(snapshot)

    def record_internal_fill(self, record: FillAuditRecord) -> None:
        self.fill_auditor.record_internal_fill(record)

    def record_exchange_fill(self, record: FillAuditRecord) -> None:
        self.fill_auditor.record_exchange_fill(record)

    def link_fills(self, client_order_id: str, exchange_order_id: str) -> bool:
        return self.fill_auditor.link_fills(client_order_id, exchange_order_id)

    def record_order_transition(
        self,
        order_id: str,
        client_order_id: str,
        from_state: OrderState,
        to_state: OrderState,
        **kwargs,
    ) -> None:
        self.lifecycle_auditor.record_transition(
            order_id, client_order_id, from_state, to_state, **kwargs
        )

    def clear_all(self) -> None:
        """Clear all reconciliation data."""
        self.position_reconciler.clear()
        self.cash_reconciler.clear()
        self.equity_reconciler.clear()
        self.fill_auditor.clear()
        self.lifecycle_auditor.clear()
