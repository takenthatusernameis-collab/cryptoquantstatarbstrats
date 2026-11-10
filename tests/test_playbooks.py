"""Tests for playbooks module."""

import os
import tempfile

import pytest

from playbooks import (
    CheckStatus,
    DryRunConfig,
    DryRunPhase,
    DryRunStatus,
    DryRunStep,
    DryRunValidator,
    IncidentResponse,
    IncidentSeverity,
    IncidentStatus,
    IncidentType,
    OperationalState,
    PreflightCheck,
    PreflightChecker,
    StateManager,
)


class TestPreflightChecker:
    """Test preflight checker."""

    @pytest.mark.asyncio
    async def test_preflight_check_pass(self):
        """Test preflight check that passes."""
        async def check_fn():
            return CheckStatus.PASS

        check = PreflightCheck(
            name="test_check",
            description="Test check",
            check_fn=check_fn,
            critical=True,
        )
        checker = PreflightChecker([check])
        report = await checker.run()

        assert report.overall_status == CheckStatus.PASS
        assert report.passed_checks == 1
        assert report.failed_checks == 0

    @pytest.mark.asyncio
    async def test_preflight_check_fail(self):
        """Test preflight check that fails."""
        async def check_fn():
            return CheckStatus.FAIL

        check = PreflightCheck(
            name="test_check",
            description="Test check",
            check_fn=check_fn,
            critical=True,
        )
        checker = PreflightChecker([check])
        report = await checker.run()

        assert report.overall_status == CheckStatus.FAIL
        assert report.passed_checks == 0
        assert report.failed_checks == 1
        assert report.critical_failures == 1

    @pytest.mark.asyncio
    async def test_preflight_check_skip(self):
        """Test preflight check that is skipped."""
        async def check_fn():
            return CheckStatus.SKIP

        check = PreflightCheck(
            name="test_check",
            description="Test check",
            check_fn=check_fn,
            critical=True,
        )
        checker = PreflightChecker([check])
        report = await checker.run()

        assert report.overall_status == CheckStatus.PASS  # No critical failures
        assert report.skipped_checks == 1

    @pytest.mark.asyncio
    async def test_preflight_non_critical_fail(self):
        """Test preflight with non-critical failure."""
        async def check_fn():
            return CheckStatus.FAIL

        check = PreflightCheck(
            name="test_check",
            description="Test check",
            check_fn=check_fn,
            critical=False,
        )
        checker = PreflightChecker([check])
        report = await checker.run()

        # Non-critical failure doesn't fail overall
        assert report.overall_status == CheckStatus.PASS
        assert report.failed_checks == 1
        assert report.critical_failures == 0


class TestStateManager:
    """Test state manager."""

    def test_state_manager_initial_state(self):
        """Test initial state is STOPPED."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            path = f.name
        try:
            manager = StateManager(path)
            assert manager.get_state() == OperationalState.STOPPED
            assert manager.is_stopped()
        finally:
            os.unlink(path)

    def test_state_transitions(self):
        """Test state transitions."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            path = f.name
        try:
            manager = StateManager(path)

            # Start
            assert manager.start("test")
            assert manager.get_state() == OperationalState.RUNNING
            assert manager.is_running()
            assert manager.can_trade()

            # Pause
            assert manager.pause("test")
            assert manager.get_state() == OperationalState.PAUSED
            assert manager.is_paused()
            assert not manager.can_trade()

            # Resume
            assert manager.resume("test")
            assert manager.get_state() == OperationalState.RUNNING
            assert manager.can_trade()

            # Stop
            assert manager.stop("test")
            assert manager.get_state() == OperationalState.STOPPED
            assert manager.is_stopped()
        finally:
            os.unlink(path)

    def test_state_persistence(self):
        """Test state persistence across restarts."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            path = f.name
        try:
            manager = StateManager(path)
            manager.start("test")
            manager.pause("test")

            # Create new manager with same path
            manager2 = StateManager(path)
            assert manager2.get_state() == OperationalState.PAUSED
        finally:
            os.unlink(path)

    def test_state_callbacks(self):
        """Test state change callbacks."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            path = f.name
        try:
            manager = StateManager(path)
            transitions = []

            def callback(old_state, new_state):
                transitions.append((old_state, new_state))

            manager.register_callback(callback)
            manager.start("test")
            manager.pause("test")

            assert len(transitions) == 2
            assert transitions[0] == (OperationalState.STOPPED, OperationalState.RUNNING)
            assert transitions[1] == (OperationalState.RUNNING, OperationalState.PAUSED)
        finally:
            os.unlink(path)

    def test_invalid_transitions(self):
        """Test invalid state transitions are rejected."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            path = f.name
        try:
            manager = StateManager(path)

            # Can't pause from STOPPED
            assert not manager.pause("test")
            assert manager.get_state() == OperationalState.STOPPED

            # Can't resume from STOPPED
            assert not manager.resume("test")
            assert manager.get_state() == OperationalState.STOPPED

            # Start then try to start again
            manager.start("test")
            assert not manager.start("test")
        finally:
            os.unlink(path)


class TestIncidentResponse:
    """Test incident response."""

    def test_create_incident(self):
        """Test creating an incident."""
        response = IncidentResponse()
        incident = response.create_incident(
            incident_type=IncidentType.RISK_BREACH,
            severity=IncidentSeverity.HIGH,
            title="Risk limit exceeded",
            description="Position size exceeds limit",
        )

        assert incident.incident_type == IncidentType.RISK_BREACH
        assert incident.severity == IncidentSeverity.HIGH
        assert incident.status == IncidentStatus.OPEN
        assert incident.title == "Risk limit exceeded"

    def test_acknowledge_incident(self):
        """Test acknowledging an incident."""
        response = IncidentResponse()
        incident = response.create_incident(
            incident_type=IncidentType.MANUAL,
            severity=IncidentSeverity.LOW,
            title="Test",
            description="Test",
        )

        assert response.acknowledge_incident(incident.incident_id, "operator")
        updated = response.get_incident(incident.incident_id)
        assert updated.status == IncidentStatus.ACKNOWLEDGED
        assert updated.acknowledged_by == "operator"

    def test_resolve_incident(self):
        """Test resolving an incident."""
        response = IncidentResponse()
        incident = response.create_incident(
            incident_type=IncidentType.MANUAL,
            severity=IncidentSeverity.LOW,
            title="Test",
            description="Test",
        )

        response.acknowledge_incident(incident.incident_id, "operator")
        assert response.resolve_incident(incident.incident_id, "operator", "Fixed")
        updated = response.get_incident(incident.incident_id)
        assert updated.status == IncidentStatus.RESOLVED
        assert updated.resolved_by == "operator"

    def test_get_incidents(self):
        """Test getting incidents."""
        response = IncidentResponse()
        inc1 = response.create_incident(
            IncidentType.MANUAL, IncidentSeverity.LOW, "Test 1", "Desc 1"
        )
        inc2 = response.create_incident(
            IncidentType.MANUAL, IncidentSeverity.HIGH, "Test 2", "Desc 2"
        )

        open_incidents = response.get_open_incidents()
        assert len(open_incidents) == 2

        response.resolve_incident(inc1.incident_id, "operator")
        open_incidents = response.get_open_incidents()
        assert len(open_incidents) == 1
        assert open_incidents[0].incident_id == inc2.incident_id


class TestDryRunValidator:
    """Test dry-run validator."""

    @pytest.mark.asyncio
    async def test_dry_run_pass(self):
        """Test dry-run with all steps passing."""
        async def passing_step():
            return True

        config = DryRunConfig(steps=[
            DryRunStep("step1", DryRunPhase.PREFLIGHT, "Step 1", passing_step),
            DryRunStep("step2", DryRunPhase.CONFIG_VALIDATION, "Step 2", passing_step),
        ])
        validator = DryRunValidator(config)
        result = await validator.run()

        assert result.overall_status == DryRunStatus.PASSED
        assert result.passed_steps == 2
        assert result.failed_steps == 0

    @pytest.mark.asyncio
    async def test_dry_run_fail(self):
        """Test dry-run with failing step."""
        async def failing_step():
            return False

        config = DryRunConfig(steps=[
            DryRunStep("step1", DryRunPhase.PREFLIGHT, "Step 1", failing_step, critical=True),
        ], fail_fast=True)
        validator = DryRunValidator(config)
        result = await validator.run()

        assert result.overall_status == DryRunStatus.FAILED
        assert result.failed_steps == 1

    @pytest.mark.asyncio
    async def test_dry_run_non_critical_fail(self):
        """Test dry-run with non-critical failure."""
        async def failing_step():
            return False

        async def passing_step():
            return True

        config = DryRunConfig(steps=[
            DryRunStep("step1", DryRunPhase.PREFLIGHT, "Step 1", failing_step, critical=False),
            DryRunStep("step2", DryRunPhase.CONFIG_VALIDATION, "Step 2", passing_step),
        ], fail_fast=True)
        validator = DryRunValidator(config)
        result = await validator.run()

        # Non-critical failure doesn't stop execution with fail_fast
        assert result.failed_steps == 1
        assert result.passed_steps == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
