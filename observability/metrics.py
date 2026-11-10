"""Prometheus-compatible metrics for fills, latency, slippage, rejections, and risk breaches."""


import threading
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Dict, List, Optional


class MetricType(str):
    """Metric types."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"


@dataclass
class MetricValue:
    """Metric value with labels."""
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class Metric(ABC):
    """Base metric class."""

    def __init__(self, name: str, description: str, labels: Optional[List[str]] = None):
        self.name = name
        self.description = description
        self.label_names = labels or []
        self._lock = threading.Lock()

    @abstractmethod
    def record(self, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """Record a metric value."""
        pass

    @abstractmethod
    def get_samples(self) -> List[MetricValue]:
        """Get all recorded samples."""
        pass

    def _make_key(self, labels: Optional[Dict[str, str]]) -> tuple:
        """Create a key from labels."""
        if not labels:
            return ()
        if self.label_names:
            return tuple(sorted((k, labels.get(k, "")) for k in self.label_names))
        return tuple(sorted(labels.items()))


class Counter(Metric):
    """Monotonically increasing counter."""

    def __init__(self, name: str, description: str, labels: Optional[List[str]] = None):
        super().__init__(name, description, labels)
        self._values: Dict[tuple, float] = defaultdict(float)

    def inc(self, value: float = 1.0, labels: Optional[Dict[str, str]] = None) -> None:
        """Increment counter."""
        with self._lock:
            key = self._make_key(labels)
            self._values[key] += value

    def record(self, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """Record counter value (alias for inc)."""
        self.inc(value, labels)

    def get(self, labels: Optional[Dict[str, str]] = None) -> float:
        """Get current counter value."""
        with self._lock:
            key = self._make_key(labels)
            return self._values.get(key, 0.0)

    def get_samples(self) -> List[MetricValue]:
        """Get all samples."""
        with self._lock:
            return [
                MetricValue(value=v, labels=dict(k))
                for k, v in self._values.items()
            ]


class Gauge(Metric):
    """Gauge that can go up and down."""

    def __init__(self, name: str, description: str, labels: Optional[List[str]] = None):
        super().__init__(name, description, labels)
        self._values: Dict[tuple, float] = {}

    def set(self, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """Set gauge value."""
        with self._lock:
            key = self._make_key(labels)
            self._values[key] = value

    def inc(self, value: float = 1.0, labels: Optional[Dict[str, str]] = None) -> None:
        """Increment gauge."""
        with self._lock:
            key = self._make_key(labels)
            self._values[key] = self._values.get(key, 0.0) + value

    def dec(self, value: float = 1.0, labels: Optional[Dict[str, str]] = None) -> None:
        """Decrement gauge."""
        self.inc(-value, labels)

    def record(self, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """Record gauge value (alias for set)."""
        self.set(value, labels)

    def get(self, labels: Optional[Dict[str, str]] = None) -> float:
        """Get current gauge value."""
        with self._lock:
            key = self._make_key(labels)
            return self._values.get(key, 0.0)

    def get_samples(self) -> List[MetricValue]:
        """Get all samples."""
        with self._lock:
            return [
                MetricValue(value=v, labels=dict(k))
                for k, v in self._values.items()
            ]


class Histogram(Metric):
    """Histogram for tracking distributions."""

    def __init__(
        self,
        name: str,
        description: str,
        labels: Optional[List[str]] = None,
        buckets: Optional[List[float]] = None,
    ):
        super().__init__(name, description, labels)
        self.buckets = buckets or [
            0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, float("inf")
        ]
        self._counts: Dict[tuple, Dict[float, int]] = defaultdict(lambda: defaultdict(int))
        self._sums: Dict[tuple, float] = defaultdict(float)
        self._count: Dict[tuple, int] = defaultdict(int)

    def observe(self, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """Observe a value."""
        with self._lock:
            key = self._make_key(labels)
            for bucket in self.buckets:
                if value <= bucket:
                    self._counts[key][bucket] += 1
            self._sums[key] += value
            self._count[key] += 1

    def record(self, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """Record histogram value (alias for observe)."""
        self.observe(value, labels)

    def get_count(self, labels: Optional[Dict[str, str]] = None) -> int:
        """Get total observation count."""
        with self._lock:
            key = self._make_key(labels)
            return self._count.get(key, 0)

    def get_sum(self, labels: Optional[Dict[str, str]] = None) -> float:
        """Get sum of observed values."""
        with self._lock:
            key = self._make_key(labels)
            return self._sums.get(key, 0.0)

    def get_bucket_count(self, bucket: float, labels: Optional[Dict[str, str]] = None) -> int:
        """Get count for a specific bucket."""
        with self._lock:
            key = self._make_key(labels)
            return self._counts[key].get(bucket, 0)

    def get_samples(self) -> List[MetricValue]:
        """Get all samples (returns count, sum, and bucket counts)."""
        with self._lock:
            samples = []
            for key in self._count.keys():
                labels = dict(key)
                samples.append(MetricValue(
                    value=self._count[key],
                    labels={**labels, "metric": "count"}
                ))
                samples.append(MetricValue(
                    value=self._sums[key],
                    labels={**labels, "metric": "sum"}
                ))
                for bucket, count in self._counts[key].items():
                    samples.append(MetricValue(
                        value=count,
                        labels={**labels, "metric": "bucket", "le": str(bucket)}
                    ))
            return samples


class MetricsCollector:
    """Central metrics collector with predefined metrics for the trading system."""

    def __init__(self, namespace: str = "cryptoquant"):
        self.namespace = namespace
        self._metrics: Dict[str, Metric] = {}
        self._lock = threading.Lock()

        # Define standard metrics
        self._init_standard_metrics()

    def _init_standard_metrics(self) -> None:
        """Initialize standard trading metrics."""
        ns = self.namespace

        # Fill metrics
        self._register(Counter(
            f"{ns}_fills_total",
            "Total number of fills",
            ["symbol", "exchange", "side"]
        ))
        self._register(Counter(
            f"{ns}_fill_quantity_total",
            "Total fill quantity",
            ["symbol", "exchange", "side"]
        ))
        self._register(Histogram(
            f"{ns}_fill_price",
            "Fill price distribution",
            ["symbol", "exchange"],
            buckets=[0.001, 0.01, 0.1, 1.0, 10.0, 100.0, 1000.0, 10000.0, 100000.0, float("inf")]
        ))
        self._register(Histogram(
            f"{ns}_fill_slippage_bps",
            "Fill slippage in basis points",
            ["symbol", "exchange", "side"],
            buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 25.0, 50.0, 100.0, float("inf")]
        ))

        # Latency metrics
        self._register(Histogram(
            f"{ns}_order_latency_ms",
            "Order submission latency in milliseconds",
            ["exchange", "operation"],
            buckets=[1, 5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000, float("inf")]
        ))
        self._register(Histogram(
            f"{ns}_adapter_latency_ms",
            "Adapter call latency in milliseconds",
            ["exchange", "probe_type"],
            buckets=[1, 5, 10, 25, 50, 100, 250, 500, 1000, float("inf")]
        ))

        # Rejection metrics
        self._register(Counter(
            f"{ns}_rejections_total",
            "Total number of order rejections",
            ["symbol", "exchange", "reason"]
        ))
        self._register(Counter(
            f"{ns}_order_errors_total",
            "Total number of order errors",
            ["symbol", "exchange", "error_type"]
        ))

        # Risk metrics
        self._register(Gauge(
            f"{ns}_position_size",
            "Current position size",
            ["symbol", "exchange"]
        ))
        self._register(Gauge(
            f"{ns}_gross_exposure",
            "Current gross exposure as fraction of capital",
            ["exchange"]
        ))
        self._register(Gauge(
            f"{ns}_net_exposure",
            "Current net exposure as fraction of capital",
            ["exchange"]
        ))
        self._register(Gauge(
            f"{ns}_drawdown_pct",
            "Current drawdown percentage",
            ["exchange"]
        ))
        self._register(Counter(
            f"{ns}_risk_breaches_total",
            "Total number of risk limit breaches",
            ["breach_type", "exchange"]
        ))
        self._register(Counter(
            f"{ns}_kill_switch_activations_total",
            "Total number of kill switch activations",
            ["exchange"]
        ))

        # Reconciliation metrics
        self._register(Gauge(
            f"{ns}_reconciliation_position_diff",
            "Position reconciliation difference",
            ["symbol", "exchange"]
        ))
        self._register(Gauge(
            f"{ns}_reconciliation_cash_diff",
            "Cash reconciliation difference",
            ["exchange"]
        ))
        self._register(Gauge(
            f"{ns}_reconciliation_equity_diff",
            "Equity reconciliation difference",
            ["exchange"]
        ))
        self._register(Counter(
            f"{ns}_reconciliation_failures_total",
            "Total number of reconciliation failures",
            ["check_type", "exchange"]
        ))

        # Adapter metrics
        self._register(Counter(
            f"{ns}_adapter_probes_total",
            "Total number of adapter probes",
            ["exchange", "probe_type", "success"]
        ))
        self._register(Gauge(
            f"{ns}_adapter_connected",
            "Adapter connection status (1=connected, 0=disconnected)",
            ["exchange"]
        ))

        # Order lifecycle metrics
        self._register(Counter(
            f"{ns}_order_events_total",
            "Total number of order lifecycle events",
            ["symbol", "exchange", "event_type", "status"]
        ))

        # Playbook metrics
        self._register(Counter(
            f"{ns}_playbook_executions_total",
            "Total number of playbook executions",
            ["playbook", "status"]
        ))
        self._register(Histogram(
            f"{ns}_playbook_duration_seconds",
            "Playbook execution duration in seconds",
            ["playbook"],
            buckets=[0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0, 300.0, float("inf")]
        ))

        # Health check metrics
        self._register(Gauge(
            f"{ns}_health_liveness",
            "Liveness health check status (1=healthy, 0=unhealthy)"
        ))
        self._register(Gauge(
            f"{ns}_health_readiness",
            "Readiness health check status (1=ready, 0=not ready)"
        ))
        self._register(Gauge(
            f"{ns}_dependency_status",
            "Dependency status (1=healthy, 0=unhealthy)",
            ["dependency"]
        ))

    def _register(self, metric: Metric) -> None:
        """Register a metric."""
        with self._lock:
            self._metrics[metric.name] = metric

    def create_counter(
        self, name: str, description: str = "", labels: Optional[List[str]] = None
    ) -> Counter:
        """Create and register an ad-hoc counter metric."""
        metric = Counter(name, description, labels)
        self._register(metric)
        return metric

    def create_gauge(
        self, name: str, description: str = "", labels: Optional[List[str]] = None
    ) -> Gauge:
        """Create and register an ad-hoc gauge metric."""
        metric = Gauge(name, description, labels)
        self._register(metric)
        return metric

    def create_histogram(
        self,
        name: str,
        description: str = "",
        labels: Optional[List[str]] = None,
        buckets: Optional[List[float]] = None,
    ) -> Histogram:
        """Create and register an ad-hoc histogram metric."""
        metric = Histogram(name, description, labels, buckets)
        self._register(metric)
        return metric

    def get(self, name: str) -> Optional[Metric]:
        """Get a metric by name."""
        with self._lock:
            return self._metrics.get(name)

    def counter(self, name: str) -> Counter:
        """Get or create a counter metric."""
        metric = self.get(name)
        if metric is None:
            return self.create_counter(name)
        if not isinstance(metric, Counter):
            raise TypeError(f"Metric {name} is not a Counter")
        return metric

    def gauge(self, name: str) -> Gauge:
        """Get or create a gauge metric."""
        metric = self.get(name)
        if metric is None:
            return self.create_gauge(name)
        if not isinstance(metric, Gauge):
            raise TypeError(f"Metric {name} is not a Gauge")
        return metric

    def histogram(self, name: str) -> Histogram:
        """Get or create a histogram metric."""
        metric = self.get(name)
        if metric is None:
            return self.create_histogram(name)
        if not isinstance(metric, Histogram):
            raise TypeError(f"Metric {name} is not a Histogram")
        return metric

    def get_all_samples(self) -> Dict[str, List[MetricValue]]:
        """Get all metric samples."""
        with self._lock:
            return {name: metric.get_samples() for name, metric in self._metrics.items()}


# Global metrics collector
_metrics_collector: Optional[MetricsCollector] = None
_collector_lock = threading.Lock()


def get_metrics(namespace: str = "cryptoquant") -> MetricsCollector:
    """Get or create the global metrics collector."""
    global _metrics_collector
    with _collector_lock:
        if _metrics_collector is None:
            _metrics_collector = MetricsCollector(namespace)
        return _metrics_collector


class PrometheusMetricsExporter:
    """Export metrics in Prometheus text format."""

    def __init__(self, collector: MetricsCollector):
        self.collector = collector

    def export(self) -> str:
        """Export all metrics in Prometheus format."""
        lines = []
        samples = self.collector.get_all_samples()

        # Group by metric name
        by_name: Dict[str, List[MetricValue]] = defaultdict(list)
        for metric_name, metric_samples in samples.items():
            for sample in metric_samples:
                by_name[metric_name].append(sample)

        for metric_name, metric_samples in sorted(by_name.items()):
            # Find the base metric to get description and type
            base_metric = self.collector.get(metric_name)
            if not base_metric:
                continue

            # Write HELP and TYPE
            lines.append(f"# HELP {metric_name} {base_metric.description}")
            if isinstance(base_metric, Counter):
                lines.append(f"# TYPE {metric_name} counter")
            elif isinstance(base_metric, Gauge):
                lines.append(f"# TYPE {metric_name} gauge")
            elif isinstance(base_metric, Histogram):
                lines.append(f"# TYPE {metric_name} histogram")
            else:
                lines.append(f"# TYPE {metric_name} untyped")

            # Write samples
            for sample in metric_samples:
                labels_str = ""
                if sample.labels:
                    label_parts = []
                    for k, v in sorted(sample.labels.items()):
                        # Escape label values
                        escaped_v = v.replace('"', '\\"').replace("\n", "\\n")
                        label_parts.append(f'{k}="{escaped_v}"')
                    labels_str = "{" + ",".join(label_parts) + "}"

                lines.append(f"{metric_name}{labels_str} {sample.value}")

        return "\n".join(lines) + "\n"

    def export_to_file(self, path: str) -> None:
        """Export metrics to file."""
        with open(path, "w") as f:
            f.write(self.export())


@contextmanager
def measure_latency(histogram: Histogram, labels: Optional[Dict[str, str]] = None):
    """Context manager to measure and record latency."""
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        histogram.observe(elapsed_ms, labels)
