"""Tests for observability module."""

import pytest

from observability import (
    AdapterProbeLogger,
    Counter,
    DependencyStatus,
    Gauge,
    Histogram,
    LivenessProbe,
    MetricsCollector,
    MicrostructureEventLogger,
    OrderLifecycleLogger,
    PrometheusMetricsExporter,
    ReadinessProbe,
    RiskDecisionLogger,
    StructuredLogger,
    get_logger,
)
from observability.health import DependencyCheck
from observability.logging import (
    AdapterProbeEvent,
    AdapterProbeType,
    MicrostructureEvent,
    MicrostructureEventType,
    OrderEventType,
    OrderLifecycleEvent,
    RiskDecisionEvent,
    RiskDecisionType,
)


class TestStructuredLogger:
    """Test structured logger."""

    def test_logger_creation(self):
        """Test logger creation."""
        logger = StructuredLogger("test_logger", "development")
        assert logger.environment == "development"

    def test_trace_context(self):
        """Test trace context."""
        logger = StructuredLogger("test_logger")
        logger.set_trace_context("trace-123", "span-456")
        logger.clear_trace_context()

    def test_log_order_lifecycle(self):
        """Test logging order lifecycle event."""
        logger = StructuredLogger("test_logger")
        event = OrderLifecycleEvent(
            order_id="order_1",
            client_order_id="client_1",
            symbol="BTCUSDT",
            side="buy",
            order_type="limit",
            quantity=1.0,
            price=50000.0,
            status="created",
            event_subtype=OrderEventType.CREATED,
            exchange="binance",
        )
        logger.log_order_lifecycle(event)

    def test_log_risk_decision(self):
        """Test logging risk decision."""
        logger = StructuredLogger("test_logger")
        event = RiskDecisionEvent(
            decision_type=RiskDecisionType.POSITION_CHECK,
            allowed=True,
            reason="Within limits",
            current_value=0.5,
            limit_value=1.0,
            utilization_pct=50.0,
        )
        logger.log_risk_decision(event)

    def test_log_adapter_probe(self):
        """Test logging adapter probe."""
        logger = StructuredLogger("test_logger")
        event = AdapterProbeEvent(
            probe_type=AdapterProbeType.CONNECTIVITY,
            exchange="binance",
            success=True,
            latency_ms=10.0,
        )
        logger.log_adapter_probe(event)

    def test_log_microstructure(self):
        """Test logging microstructure event."""
        logger = StructuredLogger("test_logger")
        event = MicrostructureEvent(
            event_subtype=MicrostructureEventType.FILL,
            symbol="BTCUSDT",
            exchange="binance",
            order_id="order_1",
            client_order_id="client_1",
            quantity=0.001,
            price=50000.0,
        )
        logger.log_microstructure(event)


class TestSpecializedLoggers:
    """Test specialized loggers."""

    def test_order_lifecycle_logger(self):
        """Test order lifecycle logger."""
        logger = get_logger("test_order")
        order_logger = OrderLifecycleLogger(logger)

        order_logger.created(
            order_id="order_1",
            client_order_id="client_1",
            symbol="BTCUSDT",
            side="buy",
            order_type="limit",
            quantity=1.0,
            price=50000.0,
        )

        order_logger.submitted(
            order_id="order_1",
            client_order_id="client_1",
            symbol="BTCUSDT",
            side="buy",
        )

        order_logger.acknowledged(
            order_id="order_1",
            client_order_id="client_1",
            exchange_order_id="exch_1",
            symbol="BTCUSDT",
        )

        order_logger.filled(
            order_id="order_1",
            client_order_id="client_1",
            exchange_order_id="exch_1",
            symbol="BTCUSDT",
            filled_quantity=1.0,
            avg_fill_price=50000.0,
        )

        order_logger.cancelled(
            order_id="order_1",
            client_order_id="client_1",
            exchange_order_id="exch_1",
            symbol="BTCUSDT",
        )

        order_logger.rejected(
            order_id="order_1",
            client_order_id="client_1",
            symbol="BTCUSDT",
            error="Insufficient balance",
        )

    def test_risk_decision_logger(self):
        """Test risk decision logger."""
        logger = get_logger("test_risk")
        risk_logger = RiskDecisionLogger(logger)

        risk_logger.log_decision(
            decision_type=RiskDecisionType.POSITION_CHECK,
            allowed=True,
            reason="Within limits",
            current_value=0.5,
            limit_value=1.0,
        )

        risk_logger.log_decision(
            decision_type=RiskDecisionType.KILL_SWITCH,
            allowed=False,
            reason="Drawdown exceeded",
            current_value=0.15,
            limit_value=0.10,
        )

    def test_adapter_probe_logger(self):
        """Test adapter probe logger."""
        logger = get_logger("test_adapter")
        adapter_logger = AdapterProbeLogger(logger)

        adapter_logger.log_probe(
            probe_type=AdapterProbeType.CONNECTIVITY,
            exchange="binance",
            success=True,
            latency_ms=10.0,
        )

        adapter_logger.log_probe(
            probe_type=AdapterProbeType.ORDER_PLACEMENT,
            exchange="binance",
            success=False,
            latency_ms=100.0,
            error="Rate limit exceeded",
        )

    def test_microstructure_logger(self):
        """Test microstructure logger."""
        logger = get_logger("test_micro")
        micro_logger = MicrostructureEventLogger(logger)

        micro_logger.log_fill(
            symbol="BTCUSDT",
            exchange="binance",
            order_id="order_1",
            client_order_id="client_1",
            quantity=0.001,
            price=50000.0,
            expected_price=49990.0,
            latency_ms=5.0,
        )

        micro_logger.log_slippage(
            symbol="BTCUSDT",
            exchange="binance",
            order_id="order_1",
            client_order_id="client_1",
            expected_price=50000.0,
            actual_price=50010.0,
            quantity=0.001,
        )

        micro_logger.log_latency(
            symbol="BTCUSDT",
            exchange="binance",
            order_id="order_1",
            client_order_id="client_1",
            latency_ms=10.0,
        )

        micro_logger.log_rejection(
            symbol="BTCUSDT",
            exchange="binance",
            order_id="order_1",
            client_order_id="client_1",
            error="Insufficient balance",
        )


class TestMetrics:
    """Test metrics collection."""

    def test_counter(self):
        """Test counter metric."""
        counter = Counter("test_counter", "Test counter", ["label1"])
        counter.inc(1, {"label1": "value1"})
        counter.inc(2, {"label1": "value2"})
        assert counter.get({"label1": "value1"}) == 1
        assert counter.get({"label1": "value2"}) == 2

    def test_gauge(self):
        """Test gauge metric."""
        gauge = Gauge("test_gauge", "Test gauge", ["label1"])
        gauge.set(10, {"label1": "value1"})
        gauge.inc(5, {"label1": "value1"})
        gauge.dec(2, {"label1": "value1"})
        assert gauge.get({"label1": "value1"}) == 13

    def test_histogram(self):
        """Test histogram metric."""
        histogram = Histogram("test_histogram", "Test histogram", ["label1"], buckets=[1, 5, 10, float("inf")])
        histogram.observe(2, {"label1": "value1"})
        histogram.observe(7, {"label1": "value1"})
        assert histogram.get_count({"label1": "value1"}) == 2
        assert histogram.get_sum({"label1": "value1"}) == 9

    def test_metrics_collector(self):
        """Test metrics collector."""
        collector = MetricsCollector("test")
        fills_counter = collector.counter("test_fills_total")
        fills_counter.inc(1, {"symbol": "BTCUSDT", "exchange": "binance", "side": "buy"})

        position_gauge = collector.gauge("test_position_size")
        position_gauge.set(1.0, {"symbol": "BTCUSDT", "exchange": "binance"})

        latency_histogram = collector.histogram("test_order_latency_ms")
        latency_histogram.observe(10.0, {"exchange": "binance", "operation": "submit"})

    def test_prometheus_exporter(self):
        """Test Prometheus exporter."""
        collector = MetricsCollector("test")
        collector.counter("test_counter").inc(1, {"label": "value"})

        exporter = PrometheusMetricsExporter(collector)
        output = exporter.export()
        assert "test_counter" in output
        assert 'label="value"' in output


class TestHealthChecks:
    """Test health checks."""

    @pytest.mark.asyncio
    async def test_liveness_probe(self):
        """Test liveness probe."""
        probe = LivenessProbe()
        result = await probe.check()
        assert result.status == DependencyStatus.HEALTHY
        assert result.name == "liveness"
        assert "uptime_seconds" in result.details

    async def test_readiness_probe_no_deps(self):
        """Test readiness probe with no dependencies."""
        probe = ReadinessProbe()
        result = await probe.check()
        assert result.status == DependencyStatus.HEALTHY
        assert result.name == "readiness"

    async def test_readiness_probe_with_deps(self):
        """Test readiness probe with dependencies."""
        async def healthy_check():
            return DependencyStatus.HEALTHY

        async def unhealthy_check():
            return DependencyStatus.UNHEALTHY

        probe = ReadinessProbe(dependencies=[
            DependencyCheck("healthy_dep", healthy_check, critical=True),
            DependencyCheck("unhealthy_dep", unhealthy_check, critical=False),
        ])
        result = await probe.check()
        assert result.status == DependencyStatus.DEGRADED
        assert "dependencies" in result.details

    async def test_readiness_probe_critical_failure(self):
        """Test readiness probe with critical dependency failure."""
        async def unhealthy_check():
            return DependencyStatus.UNHEALTHY

        probe = ReadinessProbe(dependencies=[
            DependencyCheck("critical_dep", unhealthy_check, critical=True),
        ])
        result = await probe.check()
        assert result.status == DependencyStatus.UNHEALTHY


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
