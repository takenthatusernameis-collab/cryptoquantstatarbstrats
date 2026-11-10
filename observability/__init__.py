"""Observability module for structured logging, metrics, and health checks."""

from .logging import (
    StructuredLogger,
    get_logger,
    configure_logging,
    OrderLifecycleLogger,
    RiskDecisionLogger,
    AdapterProbeLogger,
    MicrostructureEventLogger,
)
from .metrics import (
    MetricsCollector,
    get_metrics,
    PrometheusMetricsExporter,
    Counter,
    Histogram,
    Gauge,
)
from .health import (
    HealthCheckServer,
    LivenessProbe,
    ReadinessProbe,
    DependencyStatus,
    start_health_server,
)

__all__ = [
    "StructuredLogger",
    "get_logger",
    "configure_logging",
    "OrderLifecycleLogger",
    "RiskDecisionLogger",
    "AdapterProbeLogger",
    "MicrostructureEventLogger",
    "MetricsCollector",
    "get_metrics",
    "PrometheusMetricsExporter",
    "Counter",
    "Histogram",
    "Gauge",
    "HealthCheckServer",
    "LivenessProbe",
    "ReadinessProbe",
    "DependencyStatus",
    "start_health_server",
]