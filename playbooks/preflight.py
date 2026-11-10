"""Preflight checklist automation."""

import asyncio
import socket
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, List, Optional
import uuid


class CheckStatus(str, Enum):
    """Preflight check status."""

    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"
    ERROR = "error"


@dataclass
class PreflightCheck:
    """Individual preflight check definition."""

    name: str
    description: str
    check_fn: Callable[[], Awaitable[CheckStatus]]
    critical: bool = True
    timeout_seconds: float = 10.0
    metadata: Dict = field(default_factory=dict)


@dataclass
class PreflightResult:
    """Result of a preflight check."""

    check_name: str
    status: CheckStatus
    latency_ms: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    error: Optional[str] = None
    details: Dict = field(default_factory=dict)


@dataclass
class PreflightReport:
    """Complete preflight report."""

    run_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    results: List[PreflightResult] = field(default_factory=list)
    overall_status: CheckStatus = CheckStatus.PASS
    critical_failures: int = 0
    total_checks: int = 0
    passed_checks: int = 0
    failed_checks: int = 0
    skipped_checks: int = 0
    duration_ms: float = 0.0


class PreflightChecker:
    """Automated preflight checklist."""

    def __init__(self, checks: Optional[List[PreflightCheck]] = None):
        self.checks = checks or []
        self._default_checks()

    def _default_checks(self) -> None:
        """Add default preflight checks."""
        self.checks.extend([
            PreflightCheck(
                name="network_reachability",
                description="Verify network connectivity to exchange endpoints",
                check_fn=self._check_network_reachability,
                critical=True,
                timeout_seconds=10.0,
            ),
            PreflightCheck(
                name="credential_presence",
                description="Verify required API credentials are present",
                check_fn=self._check_credential_presence,
                critical=True,
                timeout_seconds=2.0,
            ),
            PreflightCheck(
                name="risk_config_validation",
                description="Validate risk configuration parameters",
                check_fn=self._check_risk_config,
                critical=True,
                timeout_seconds=2.0,
            ),
            PreflightCheck(
                name="exchange_capability_probe",
                description="Probe exchange API capabilities",
                check_fn=self._check_exchange_capability,
                critical=True,
                timeout_seconds=15.0,
            ),
            PreflightCheck(
                name="data_feed_validation",
                description="Validate market data feed availability",
                check_fn=self._check_data_feed,
                critical=True,
                timeout_seconds=10.0,
            ),
        ])

    async def _check_network_reachability(self) -> CheckStatus:
        """Check network reachability to exchange endpoints."""
        endpoints = [
            ("api.binance.com", 443),
            ("www.binance.com", 443),
            ("testnet.binance.vision", 443),
        ]

        for host, port in endpoints:
            try:
                sock = socket.create_connection((host, port), timeout=5)
                sock.close()
            except (socket.timeout, socket.error, OSError):
                return CheckStatus.FAIL
        return CheckStatus.PASS

    async def _check_credential_presence(self) -> CheckStatus:
        """Check if required credentials are present in environment."""
        import os
        required = ["BINANCE_API_KEY", "BINANCE_API_SECRET"]
        for var in required:
            if not os.getenv(var):
                return CheckStatus.FAIL
        return CheckStatus.PASS

    async def _check_risk_config(self) -> CheckStatus:
        """Validate risk configuration."""
        # This would integrate with config module
        # For now, just check if config can be loaded
        try:
            from config import load_config
            config = load_config()
            # Basic validation
            if config.risk.max_gross_exposure <= 0:
                return CheckStatus.FAIL
            if config.risk.max_position_size <= 0 or config.risk.max_position_size > 1:
                return CheckStatus.FAIL
            return CheckStatus.PASS
        except Exception:
            return CheckStatus.FAIL

    async def _check_exchange_capability(self) -> CheckStatus:
        """Probe exchange API capabilities."""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.binance.com/api/v3/ping",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    if resp.status == 200:
                        return CheckStatus.PASS
        except Exception:
            pass
        return CheckStatus.FAIL

    async def _check_data_feed(self) -> CheckStatus:
        """Validate market data feed."""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=1",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data and len(data) > 0:
                            return CheckStatus.PASS
        except Exception:
            pass
        return CheckStatus.FAIL

    def add_check(self, check: PreflightCheck) -> None:
        """Add a custom preflight check."""
        self.checks.append(check)

    def remove_check(self, name: str) -> bool:
        """Remove a check by name."""
        for i, check in enumerate(self.checks):
            if check.name == name:
                self.checks.pop(i)
                return True
        return False

    async def run(self) -> PreflightReport:
        """Run all preflight checks."""
        import time
        start = time.perf_counter()

        report = PreflightReport()
        report.total_checks = len(self.checks)

        for check in self.checks:
            check_start = time.perf_counter()
            try:
                status = await asyncio.wait_for(check.check_fn(), timeout=check.timeout_seconds)
            except asyncio.TimeoutError:
                status = CheckStatus.ERROR
            except Exception as e:
                status = CheckStatus.ERROR

            latency_ms = (time.perf_counter() - check_start) * 1000
            result = PreflightResult(
                check_name=check.name,
                status=status,
                latency_ms=latency_ms,
            )
            report.results.append(result)

            if status == CheckStatus.PASS:
                report.passed_checks += 1
            elif status == CheckStatus.FAIL:
                report.failed_checks += 1
                if check.critical:
                    report.critical_failures += 1
            elif status == CheckStatus.SKIP:
                report.skipped_checks += 1

        # Determine overall status
        if report.critical_failures > 0:
            report.overall_status = CheckStatus.FAIL
        elif report.failed_checks > 0:
            report.overall_status = CheckStatus.FAIL
        else:
            report.overall_status = CheckStatus.PASS

        report.duration_ms = (time.perf_counter() - start) * 1000
        return report

    def run_sync(self) -> PreflightReport:
        """Run preflight checks synchronously."""
        return asyncio.run(self.run())