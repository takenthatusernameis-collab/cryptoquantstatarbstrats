"""Tests for reconciliation module."""

from decimal import Decimal

import pytest

from reconciliation import (
    CashSnapshot,
    EquitySnapshot,
    FillAuditRecord,
    PositionSnapshot,
    ReconciliationConfig,
    ReconciliationOrchestrator,
)
from reconciliation.lifecycle_audit import OrderState


class TestPositionReconciliation:
    """Test position reconciliation."""

    def test_position_reconciliation_match(self):
        """Test position reconciliation with matching positions."""
        from reconciliation.position import PositionReconciler

        reconciler = PositionReconciler(tolerance=Decimal("1e-6"))
        reconciler.update_internal_position(PositionSnapshot(
            source="internal", symbol="BTCUSDT", quantity=Decimal("1.0")
        ))
        reconciler.update_exchange_position(PositionSnapshot(
            source="exchange", symbol="BTCUSDT", quantity=Decimal("1.0")
        ))

        result = reconciler.reconcile_symbol("BTCUSDT")
        assert result.within_tolerance is True
        assert result.quantity_diff == Decimal("0")

    def test_position_reconciliation_mismatch(self):
        """Test position reconciliation with mismatched positions."""
        from reconciliation.position import PositionReconciler

        reconciler = PositionReconciler(tolerance=Decimal("1e-6"))
        reconciler.update_internal_position(PositionSnapshot(
            source="internal", symbol="BTCUSDT", quantity=Decimal("1.0")
        ))
        reconciler.update_exchange_position(PositionSnapshot(
            source="exchange", symbol="BTCUSDT", quantity=Decimal("1.5")
        ))

        result = reconciler.reconcile_symbol("BTCUSDT")
        assert result.within_tolerance is False
        assert result.quantity_diff == Decimal("0.5")

    def test_position_reconciliation_within_tolerance(self):
        """Test position reconciliation within tolerance."""
        from reconciliation.position import PositionReconciler

        reconciler = PositionReconciler(tolerance=Decimal("0.01"))
        reconciler.update_internal_position(PositionSnapshot(
            source="internal", symbol="BTCUSDT", quantity=Decimal("1.0")
        ))
        reconciler.update_exchange_position(PositionSnapshot(
            source="exchange", symbol="BTCUSDT", quantity=Decimal("1.005")
        ))

        result = reconciler.reconcile_symbol("BTCUSDT")
        assert result.within_tolerance is True


class TestCashReconciliation:
    """Test cash reconciliation."""

    def test_cash_reconciliation_match(self):
        """Test cash reconciliation with matching balances."""
        from reconciliation.cash import CashReconciler

        reconciler = CashReconciler(tolerance=Decimal("1e-2"))
        reconciler.update_internal_cash(CashSnapshot(
            source="internal", currency="USDT", available=Decimal("10000"), locked=Decimal("0")
        ))
        reconciler.update_exchange_cash(CashSnapshot(
            source="exchange", currency="USDT", available=Decimal("10000"), locked=Decimal("0")
        ))

        result = reconciler.reconcile_currency("USDT")
        assert result.within_tolerance is True
        assert result.available_diff == Decimal("0")

    def test_cash_reconciliation_mismatch(self):
        """Test cash reconciliation with mismatched balances."""
        from reconciliation.cash import CashReconciler

        reconciler = CashReconciler(tolerance=Decimal("1e-2"))
        reconciler.update_internal_cash(CashSnapshot(
            source="internal", currency="USDT", available=Decimal("10000"), locked=Decimal("0")
        ))
        reconciler.update_exchange_cash(CashSnapshot(
            source="exchange", currency="USDT", available=Decimal("10100"), locked=Decimal("0")
        ))

        result = reconciler.reconcile_currency("USDT")
        assert result.within_tolerance is False
        assert result.available_diff == Decimal("100")


class TestEquityReconciliation:
    """Test equity reconciliation."""

    def test_equity_reconciliation_match(self):
        """Test equity reconciliation with matching equity."""
        from reconciliation.equity import EquityReconciler

        reconciler = EquityReconciler(tolerance=Decimal("1e-4"))
        reconciler.update_internal_equity(EquitySnapshot(
            source="internal", total_equity=Decimal("100000")
        ))
        reconciler.update_exchange_equity(EquitySnapshot(
            source="exchange", total_equity=Decimal("100000")
        ))

        result = reconciler.reconcile()
        assert result.within_tolerance is True
        assert result.equity_diff == Decimal("0")


class TestFillAudit:
    """Test fill audit."""

    def test_fill_audit_match(self):
        """Test fill audit with matching fills."""
        from reconciliation.fill_audit import FillAuditor

        auditor = FillAuditor()
        auditor.record_internal_fill(FillAuditRecord(
            client_order_id="order_1",
            exchange_order_id="exch_1",
            symbol="BTCUSDT",
            exchange="binance",
            side="buy",
            quantity=Decimal("0.001"),
            price=Decimal("50000"),
        ))
        auditor.record_exchange_fill(FillAuditRecord(
            client_order_id="order_1",
            exchange_order_id="exch_1",
            symbol="BTCUSDT",
            exchange="binance",
            side="buy",
            quantity=Decimal("0.001"),
            price=Decimal("50000"),
        ))

        result = auditor.audit()
        assert result.passed is True
        assert result.total_fills == 1
        assert result.matched_fills == 1

    def test_fill_audit_quantity_mismatch(self):
        """Test fill audit with quantity mismatch."""
        from reconciliation.fill_audit import FillAuditor

        auditor = FillAuditor()
        auditor.record_internal_fill(FillAuditRecord(
            client_order_id="order_1",
            exchange_order_id="exch_1",
            symbol="BTCUSDT",
            exchange="binance",
            side="buy",
            quantity=Decimal("0.001"),
            price=Decimal("50000"),
        ))
        auditor.record_exchange_fill(FillAuditRecord(
            client_order_id="order_1",
            exchange_order_id="exch_1",
            symbol="BTCUSDT",
            exchange="binance",
            side="buy",
            quantity=Decimal("0.002"),
            price=Decimal("50000"),
        ))

        result = auditor.audit(quantity_tolerance=Decimal("1e-8"))
        assert result.passed is False
        assert len(result.quantity_mismatches) == 1

    def test_fill_audit_unmatched(self):
        """Test fill audit with unmatched orders."""
        from reconciliation.fill_audit import FillAuditor

        auditor = FillAuditor()
        auditor.record_internal_fill(FillAuditRecord(
            client_order_id="order_1",
            exchange_order_id="exch_1",
            symbol="BTCUSDT",
            exchange="binance",
            side="buy",
            quantity=Decimal("0.001"),
            price=Decimal("50000"),
        ))
        # No exchange fill recorded

        result = auditor.audit()
        assert result.passed is False
        assert "order_1" in result.unmatched_client_orders


class TestLifecycleAudit:
    """Test lifecycle audit."""

    def test_lifecycle_audit_valid(self):
        """Test lifecycle audit with valid transitions."""
        from reconciliation.lifecycle_audit import LifecycleAuditor

        auditor = LifecycleAuditor()
        auditor.record_transition(
            order_id="order_1",
            client_order_id="client_1",
            from_state=OrderState.CREATED,
            to_state=OrderState.SUBMITTED,
            symbol="BTCUSDT",
            side="buy",
            order_type="limit",
            quantity=1.0,
        )
        auditor.record_transition(
            order_id="order_1",
            client_order_id="client_1",
            from_state=OrderState.SUBMITTED,
            to_state=OrderState.ACKNOWLEDGED,
            exchange_order_id="exch_1",
        )
        auditor.record_transition(
            order_id="order_1",
            client_order_id="client_1",
            from_state=OrderState.ACKNOWLEDGED,
            to_state=OrderState.FILLED,
            filled_quantity=1.0,
            avg_fill_price=50000.0,
        )

        result = auditor.audit()
        assert result.passed is True
        assert result.total_orders == 1
        assert result.valid_transitions == 3

    def test_lifecycle_audit_invalid_transition(self):
        """Test lifecycle audit with invalid transition."""
        from reconciliation.lifecycle_audit import LifecycleAuditor

        auditor = LifecycleAuditor()
        auditor.record_transition(
            order_id="order_1",
            client_order_id="client_1",
            from_state=OrderState.CREATED,
            to_state=OrderState.FILLED,  # Invalid: CREATED -> FILLED not allowed
        )

        result = auditor.audit()
        assert result.passed is False
        assert len(result.invalid_transitions) == 1

    def test_lifecycle_audit_orphan_order(self):
        """Test lifecycle audit with orphan order."""
        from reconciliation.lifecycle_audit import LifecycleAuditor

        auditor = LifecycleAuditor()
        auditor.record_transition(
            order_id="order_1",
            client_order_id="client_1",
            from_state=OrderState.CREATED,
            to_state=OrderState.SUBMITTED,
            # Never reaches terminal state
        )

        result = auditor.audit()
        assert result.passed is False
        assert "order_1" in result.orphan_orders


class TestReconciliationOrchestrator:
    """Test reconciliation orchestrator."""

    def test_full_reconciliation_pass(self):
        """Test full reconciliation with all checks passing."""
        config = ReconciliationConfig(
            position_tolerance=Decimal("1e-6"),
            cash_tolerance=Decimal("1e-2"),
            equity_tolerance=Decimal("1e-4"),
        )
        orchestrator = ReconciliationOrchestrator(config)

        # Add matching data
        orchestrator.update_internal_position(PositionSnapshot(
            source="internal", symbol="BTCUSDT", quantity=Decimal("1.0")
        ))
        orchestrator.update_exchange_position(PositionSnapshot(
            source="exchange", symbol="BTCUSDT", quantity=Decimal("1.0")
        ))

        orchestrator.update_internal_cash(CashSnapshot(
            source="internal", currency="USDT", available=Decimal("10000")
        ))
        orchestrator.update_exchange_cash(CashSnapshot(
            source="exchange", currency="USDT", available=Decimal("10000")
        ))

        orchestrator.update_internal_equity(EquitySnapshot(
            source="internal", total_equity=Decimal("100000")
        ))
        orchestrator.update_exchange_equity(EquitySnapshot(
            source="exchange", total_equity=Decimal("100000")
        ))

        # Add fills
        orchestrator.record_internal_fill(FillAuditRecord(
            client_order_id="order_1",
            exchange_order_id="exch_1",
            symbol="BTCUSDT",
            exchange="binance",
            side="buy",
            quantity=Decimal("0.001"),
            price=Decimal("50000"),
        ))
        orchestrator.record_exchange_fill(FillAuditRecord(
            client_order_id="order_1",
            exchange_order_id="exch_1",
            symbol="BTCUSDT",
            exchange="binance",
            side="buy",
            quantity=Decimal("0.001"),
            price=Decimal("50000"),
        ))
        orchestrator.link_fills("order_1", "exch_1")

        # Add lifecycle
        orchestrator.record_order_transition(
            order_id="order_1",
            client_order_id="order_1",
            from_state=OrderState.CREATED,
            to_state=OrderState.SUBMITTED,
            symbol="BTCUSDT",
            side="buy",
            order_type="limit",
            quantity=0.001,
        )
        orchestrator.record_order_transition(
            order_id="order_1",
            client_order_id="order_1",
            from_state=OrderState.SUBMITTED,
            to_state=OrderState.ACKNOWLEDGED,
            exchange_order_id="exch_1",
        )
        orchestrator.record_order_transition(
            order_id="order_1",
            client_order_id="order_1",
            from_state=OrderState.ACKNOWLEDGED,
            to_state=OrderState.FILLED,
            filled_quantity=0.001,
            avg_fill_price=50000.0,
        )

        result = orchestrator.run_reconciliation()
        assert result.overall_passed is True
        assert len(result.failed_checks) == 0

    def test_full_reconciliation_fail(self):
        """Test full reconciliation with mismatched positions."""
        config = ReconciliationConfig()
        orchestrator = ReconciliationOrchestrator(config)

        orchestrator.update_internal_position(PositionSnapshot(
            source="internal", symbol="BTCUSDT", quantity=Decimal("1.0")
        ))
        orchestrator.update_exchange_position(PositionSnapshot(
            source="exchange", symbol="BTCUSDT", quantity=Decimal("2.0")
        ))

        result = orchestrator.run_reconciliation()
        assert result.overall_passed is False
        assert "position" in result.failed_checks


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
