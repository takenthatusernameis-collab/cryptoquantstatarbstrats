"""Dry-run validation script that exercises full stack without live capital."""

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Awaitable, Callable, Dict, List, Optional


class DryRunPhase(str, Enum):
    """Dry-run phases."""

    PREFLIGHT = "preflight"
    CONFIG_VALIDATION = "config_validation"
    EXCHANGE_CONNECTIVITY = "exchange_connectivity"
    DATA_FEED = "data_feed"
    RISK_CHECKS = "risk_checks"
    ORDER_LIFECYCLE = "order_lifecycle"
    POSITION_MANAGEMENT = "position_management"
    RECONCILIATION = "reconciliation"
    METRICS_EMISSION = "metrics_emission"
    HEALTH_CHECKS = "health_checks"
    COMPLETE = "complete"


class DryRunStatus(str, Enum):
    """Dry-run status."""

    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class DryRunStep:
    """Individual dry-run step."""

    name: str
    phase: DryRunPhase
    description: str
    execute_fn: Callable[[], Awaitable[bool]]
    critical: bool = True
    timeout_seconds: float = 30.0


@dataclass
class DryRunStepResult:
    """Result of a dry-run step."""

    step_name: str
    phase: DryRunPhase
    status: DryRunStatus
    duration_ms: float
    error: Optional[str] = None
    details: Dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class DryRunConfig:
    """Dry-run configuration."""

    steps: List[DryRunStep] = field(default_factory=list)
    fail_fast: bool = True
    parallel_phases: bool = False
    max_total_duration_seconds: float = 300.0


@dataclass
class DryRunResult:
    """Complete dry-run result."""

    run_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    config: Optional[DryRunConfig] = None
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: Optional[datetime] = None
    step_results: List[DryRunStepResult] = field(default_factory=list)
    overall_status: DryRunStatus = DryRunStatus.PENDING
    total_duration_ms: float = 0.0
    passed_steps: int = 0
    failed_steps: int = 0
    skipped_steps: int = 0


class DryRunValidator:
    """Dry-run validation for full stack without live capital."""

    def __init__(self, config: Optional[DryRunConfig] = None):
        if config is None:
            self.config = DryRunConfig()
            self._default_steps()
        else:
            self.config = config
            if not self.config.steps:
                self._default_steps()

    def _default_steps(self) -> None:
        """Add default dry-run steps."""
        self.config.steps = [
            DryRunStep(
                name="preflight_checks",
                phase=DryRunPhase.PREFLIGHT,
                description="Run preflight checklist",
                execute_fn=self._run_preflight,
                critical=True,
            ),
            DryRunStep(
                name="config_validation",
                phase=DryRunPhase.CONFIG_VALIDATION,
                description="Validate configuration schemas",
                execute_fn=self._validate_config,
                critical=True,
            ),
            DryRunStep(
                name="exchange_connectivity",
                phase=DryRunPhase.EXCHANGE_CONNECTIVITY,
                description="Test exchange API connectivity",
                execute_fn=self._test_exchange_connectivity,
                critical=True,
            ),
            DryRunStep(
                name="data_feed",
                phase=DryRunPhase.DATA_FEED,
                description="Validate market data feed",
                execute_fn=self._test_data_feed,
                critical=True,
            ),
            DryRunStep(
                name="risk_checks",
                phase=DryRunPhase.RISK_CHECKS,
                description="Test risk management checks",
                execute_fn=self._test_risk_checks,
                critical=True,
            ),
            DryRunStep(
                name="order_lifecycle",
                phase=DryRunPhase.ORDER_LIFECYCLE,
                description="Test order lifecycle (paper)",
                execute_fn=self._test_order_lifecycle,
                critical=True,
            ),
            DryRunStep(
                name="position_management",
                phase=DryRunPhase.POSITION_MANAGEMENT,
                description="Test position management",
                execute_fn=self._test_position_management,
                critical=True,
            ),
            DryRunStep(
                name="reconciliation",
                phase=DryRunPhase.RECONCILIATION,
                description="Test reconciliation checks",
                execute_fn=self._test_reconciliation,
                critical=False,
            ),
            DryRunStep(
                name="metrics_emission",
                phase=DryRunPhase.METRICS_EMISSION,
                description="Test metrics emission",
                execute_fn=self._test_metrics,
                critical=False,
            ),
            DryRunStep(
                name="health_checks",
                phase=DryRunPhase.HEALTH_CHECKS,
                description="Test health check endpoints",
                execute_fn=self._test_health_checks,
                critical=False,
            ),
        ]

    async def _run_preflight(self) -> bool:
        """Run preflight checks."""
        from playbooks.preflight import PreflightChecker
        checker = PreflightChecker()
        report = await checker.run()
        return report.overall_status.value == "pass"

    async def _validate_config(self) -> bool:
        """Validate configuration."""
        try:
            from config import load_config
            load_config()
            return True
        except Exception:
            return False

    async def _test_exchange_connectivity(self) -> bool:
        """Test exchange connectivity."""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.binance.com/api/v3/ping",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    return resp.status == 200
        except Exception:
            return False

    async def _test_data_feed(self) -> bool:
        """Test data feed."""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=1",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return len(data) > 0
        except Exception:
            return False

    async def _test_risk_checks(self) -> bool:
        """Test risk management checks."""
        try:
            from config import load_config
            config = load_config()
            # Test that risk limits are enforced
            assert config.risk.max_gross_exposure > 0
            assert 0 < config.risk.max_position_size <= 1
            assert config.risk.max_drawdown_pct > 0
            return True
        except Exception:
            return False

    async def _test_order_lifecycle(self) -> bool:
        """Test order lifecycle with paper broker."""
        try:
            from execution.oms import OrderManagementSystem
            from execution.paper_broker import PaperBroker
            from execution.risk import RiskManager

            broker = PaperBroker()
            oms = OrderManagementSystem(broker)
            RiskManager()

            # Create and submit a test order
            order_id = oms.create_order(
                symbol="BTCUSDT",
                side="buy",
                quantity=0.001,
                order_type="limit",
                price=50000.0,
            )

            # Check order was created
            order = oms.get_order(order_id)
            if not order:
                return False

            # Cancel the order
            cancelled = oms.cancel_order(order_id)
            return cancelled

        except Exception:
            return False

    async def _test_position_management(self) -> bool:
        """Test position management."""
        try:
            from execution.paper_broker import PaperBroker
            broker = PaperBroker(initial_balance=100000.0)

            # Check initial positions
            positions = broker.get_positions()
            assert "BTCUSDT" in positions or len(positions) == 0

            return True
        except Exception:
            return False

    async def _test_reconciliation(self) -> bool:
        """Test reconciliation."""
        try:
            from decimal import Decimal

            from reconciliation import ReconciliationConfig, ReconciliationOrchestrator
            from reconciliation.position import PositionSnapshot

            config = ReconciliationConfig()
            orchestrator = ReconciliationOrchestrator(config)

            # Add test positions
            orchestrator.update_internal_position(PositionSnapshot(
                source="internal",
                symbol="BTCUSDT",
                quantity=Decimal("1.0"),
            ))
            orchestrator.update_exchange_position(PositionSnapshot(
                source="exchange",
                symbol="BTCUSDT",
                quantity=Decimal("1.0"),
            ))

            result = orchestrator.run_reconciliation()
            return result.overall_passed
        except Exception:
            return False

    async def _test_metrics(self) -> bool:
        """Test metrics emission."""
        try:
            from observability.metrics import get_metrics
            metrics = get_metrics()
            counter = metrics.counter("cryptoquant_fills_total")
            counter.inc(1, {"symbol": "BTCUSDT", "exchange": "binance", "side": "buy"})
            return True
        except Exception:
            return False

    async def _test_health_checks(self) -> bool:
        """Test health checks."""
        try:
            from observability.health import LivenessProbe
            probe = LivenessProbe()
            result = await probe.check()
            return result.status.value == "healthy"
        except Exception:
            return False

    def add_step(self, step: DryRunStep) -> None:
        """Add a custom dry-run step."""
        self.config.steps.append(step)

    async def run(self) -> DryRunResult:
        """Run dry-run validation."""
        result = DryRunResult(config=self.config)
        start_time = time.perf_counter()

        # Group steps by phase
        phases: Dict[DryRunPhase, List[DryRunStep]] = {}
        for step in self.config.steps:
            phases.setdefault(step.phase, []).append(step)

        for phase in DryRunPhase:
            if phase not in phases:
                continue

            steps = phases[phase]

            if self.config.parallel_phases and len(steps) > 1:
                # Run steps in parallel
                tasks = [self._run_step(step) for step in steps]
                step_results = await asyncio.gather(*tasks, return_exceptions=True)

                for i, step_result in enumerate(step_results):
                    if isinstance(step_result, Exception):
                        step_result = DryRunStepResult(
                            step_name=steps[i].name,
                            phase=phase,
                            status=DryRunStatus.FAILED,
                            duration_ms=0,
                            error=str(step_result),
                        )
                    result.step_results.append(step_result)
            else:
                # Run steps sequentially
                for step in steps:
                    step_result = await self._run_step(step)
                    result.step_results.append(step_result)

                    # Fail fast
                    if self.config.fail_fast and step_result.status == DryRunStatus.FAILED and step.critical:
                        break

        result.end_time = datetime.now(timezone.utc)
        result.total_duration_ms = (time.perf_counter() - start_time) * 1000
        result.passed_steps = sum(1 for r in result.step_results if r.status == DryRunStatus.PASSED)
        result.failed_steps = sum(1 for r in result.step_results if r.status == DryRunStatus.FAILED)
        result.skipped_steps = sum(1 for r in result.step_results if r.status == DryRunStatus.SKIPPED)

        if result.failed_steps == 0:
            result.overall_status = DryRunStatus.PASSED
        else:
            result.overall_status = DryRunStatus.FAILED

        return result

    async def _run_step(self, step: DryRunStep) -> DryRunStepResult:
        """Run a single dry-run step."""
        step_start = time.perf_counter()
        try:
            success = await asyncio.wait_for(step.execute_fn(), timeout=step.timeout_seconds)
            duration_ms = (time.perf_counter() - step_start) * 1000

            if success:
                return DryRunStepResult(
                    step_name=step.name,
                    phase=step.phase,
                    status=DryRunStatus.PASSED,
                    duration_ms=duration_ms,
                )
            else:
                return DryRunStepResult(
                    step_name=step.name,
                    phase=step.phase,
                    status=DryRunStatus.FAILED,
                    duration_ms=duration_ms,
                    error="Step returned False",
                )
        except asyncio.TimeoutError:
            duration_ms = (time.perf_counter() - step_start) * 1000
            return DryRunStepResult(
                step_name=step.name,
                phase=step.phase,
                status=DryRunStatus.FAILED,
                duration_ms=duration_ms,
                error=f"Timeout after {step.timeout_seconds}s",
            )
        except Exception as e:
            duration_ms = (time.perf_counter() - step_start) * 1000
            return DryRunStepResult(
                step_name=step.name,
                phase=step.phase,
                status=DryRunStatus.FAILED,
                duration_ms=duration_ms,
                error=str(e),
            )

    def run_sync(self) -> DryRunResult:
        """Run dry-run synchronously."""
        return asyncio.run(self.run())
