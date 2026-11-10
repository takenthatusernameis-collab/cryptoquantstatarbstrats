"""Health check endpoints (liveness/readiness) with dependency status."""

import asyncio
import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, List, Optional
from aiohttp import web
import threading


class DependencyStatus(str, Enum):
    """Dependency health status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class DependencyCheck:
    """Dependency health check definition."""

    name: str
    check_fn: Callable[[], Awaitable[DependencyStatus]]
    critical: bool = True
    timeout_seconds: float = 5.0
    description: str = ""


@dataclass
class HealthCheckResult:
    """Result of a health check."""

    name: str
    status: DependencyStatus
    latency_ms: float
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    details: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


class HealthProbe(ABC):
    """Abstract health probe."""

    @abstractmethod
    async def check(self) -> HealthCheckResult:
        """Perform health check."""
        pass


class LivenessProbe(HealthProbe):
    """Liveness probe - indicates if process is alive."""

    def __init__(self, name: str = "liveness"):
        self.name = name
        self._start_time = time.time()

    async def check(self) -> HealthCheckResult:
        """Check liveness - always healthy if process is running."""
        start = time.perf_counter()
        uptime = time.time() - self._start_time
        return HealthCheckResult(
            name=self.name,
            status=DependencyStatus.HEALTHY,
            latency_ms=(time.perf_counter() - start) * 1000,
            details={"uptime_seconds": uptime},
        )


class ReadinessProbe(HealthProbe):
    """Readiness probe - indicates if service can handle requests."""

    def __init__(
        self,
        name: str = "readiness",
        dependencies: Optional[List[DependencyCheck]] = None,
    ):
        self.name = name
        self.dependencies = dependencies or []

    async def check(self) -> HealthCheckResult:
        """Check readiness by verifying all dependencies."""
        start = time.perf_counter()
        results = {}
        overall_status = DependencyStatus.HEALTHY

        for dep in self.dependencies:
            try:
                # Run with timeout
                status = await asyncio.wait_for(dep.check_fn(), timeout=dep.timeout_seconds)
                results[dep.name] = {
                    "status": status.value,
                    "critical": dep.critical,
                    "description": dep.description,
                }
                if status == DependencyStatus.UNHEALTHY:
                    if dep.critical:
                        overall_status = DependencyStatus.UNHEALTHY
                    elif overall_status == DependencyStatus.HEALTHY:
                        overall_status = DependencyStatus.DEGRADED
                elif status == DependencyStatus.DEGRADED and overall_status == DependencyStatus.HEALTHY:
                    overall_status = DependencyStatus.DEGRADED
            except asyncio.TimeoutError:
                results[dep.name] = {
                    "status": DependencyStatus.UNHEALTHY.value,
                    "critical": dep.critical,
                    "description": dep.description,
                    "error": f"Timeout after {dep.timeout_seconds}s",
                }
                if dep.critical:
                    overall_status = DependencyStatus.UNHEALTHY
                elif overall_status == DependencyStatus.HEALTHY:
                    overall_status = DependencyStatus.DEGRADED
            except Exception as e:
                results[dep.name] = {
                    "status": DependencyStatus.UNHEALTHY.value,
                    "critical": dep.critical,
                    "description": dep.description,
                    "error": str(e),
                }
                if dep.critical:
                    overall_status = DependencyStatus.UNHEALTHY
                elif overall_status == DependencyStatus.HEALTHY:
                    overall_status = DependencyStatus.DEGRADED

        return HealthCheckResult(
            name=self.name,
            status=overall_status,
            latency_ms=(time.perf_counter() - start) * 1000,
            details={"dependencies": results},
        )


class HealthCheckServer:
    """HTTP server for health check endpoints."""

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 8080,
        liveness_path: str = "/health/live",
        readiness_path: str = "/health/ready",
        liveness_probe: Optional[LivenessProbe] = None,
        readiness_probe: Optional[ReadinessProbe] = None,
    ):
        self.host = host
        self.port = port
        self.liveness_path = liveness_path
        self.readiness_path = readiness_path
        self.liveness_probe = liveness_probe or LivenessProbe()
        self.readiness_probe = readiness_probe or ReadinessProbe()
        self._app: Optional[web.Application] = None
        self._runner: Optional[web.AppRunner] = None
        self._site: Optional[web.TCPSite] = None

    def _create_app(self) -> web.Application:
        """Create aiohttp application."""
        app = web.Application()

        async def liveness_handler(request: web.Request) -> web.Response:
            result = await self.liveness_probe.check()
            status_code = 200 if result.status == DependencyStatus.HEALTHY else 503
            return web.json_response(
                {
                    "status": result.status.value,
                    "timestamp": result.timestamp,
                    "latency_ms": result.latency_ms,
                    "details": result.details,
                },
                status=status_code,
            )

        async def readiness_handler(request: web.Request) -> web.Response:
            result = await self.readiness_probe.check()
            status_code = 200 if result.status == DependencyStatus.HEALTHY else 503
            return web.json_response(
                {
                    "status": result.status.value,
                    "timestamp": result.timestamp,
                    "latency_ms": result.latency_ms,
                    "details": result.details,
                },
                status=status_code,
            )

        app.router.add_get(self.liveness_path, liveness_handler)
        app.router.add_get(self.readiness_path, readiness_handler)
        return app

    async def start(self) -> None:
        """Start the health check server."""
        self._app = self._create_app()
        self._runner = web.AppRunner(self._app)
        await self._runner.setup()
        self._site = web.TCPSite(self._runner, self.host, self.port)
        await self._site.start()

    async def stop(self) -> None:
        """Stop the health check server."""
        if self._site:
            await self._site.stop()
        if self._runner:
            await self._runner.cleanup()


# Sync wrapper for running in background thread
class HealthCheckServerThread:
    """Health check server running in a background thread."""

    def __init__(self, server: HealthCheckServer):
        self.server = server
        self._thread: Optional[threading.Thread] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._started = threading.Event()
        self._error: Optional[Exception] = None

    def start(self) -> None:
        """Start server in background thread."""
        def run_server():
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            try:
                self._loop.run_until_complete(self.server.start())
                self._started.set()
                self._loop.run_forever()
            except Exception as e:
                self._error = e
                self._started.set()
            finally:
                self._loop.close()

        self._thread = threading.Thread(target=run_server, daemon=True)
        self._thread.start()
        self._started.wait(timeout=10)
        if self._error:
            raise self._error

    def stop(self) -> None:
        """Stop the server."""
        if self._loop:
            async def stop_server():
                await self.server.stop()
                self._loop.stop()

            asyncio.run_coroutine_threadsafe(stop_server(), self._loop)
        if self._thread:
            self._thread.join(timeout=5)


def start_health_server(
    host: str = "0.0.0.0",
    port: int = 8080,
    liveness_path: str = "/health/live",
    readiness_path: str = "/health/ready",
    dependencies: Optional[List[DependencyCheck]] = None,
) -> HealthCheckServerThread:
    """Start health check server in background thread."""
    liveness = LivenessProbe()
    readiness = ReadinessProbe(dependencies=dependencies)
    server = HealthCheckServer(
        host=host,
        port=port,
        liveness_path=liveness_path,
        readiness_path=readiness_path,
        liveness_probe=liveness,
        readiness_probe=readiness,
    )
    thread_server = HealthCheckServerThread(server)
    thread_server.start()
    return thread_server