"""Structured JSON logging for order lifecycle, risk, adapter probes, and microstructure."""


import json
import logging
import sys
import threading
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional


class LogEventType(str, Enum):
    """Types of log events."""

    ORDER_LIFECYCLE = "order_lifecycle"
    RISK_DECISION = "risk_decision"
    ADAPTER_PROBE = "adapter_probe"
    MICROSTRUCTURE_EVENT = "microstructure_event"
    RECONCILIATION = "reconciliation"
    PLAYBOOK = "playbook"
    HEALTH_CHECK = "health_check"


class OrderEventType(str, Enum):
    """Order lifecycle event types."""

    CREATED = "created"
    SUBMITTED = "submitted"
    ACKNOWLEDGED = "acknowledged"
    PARTIAL_FILL = "partial_fill"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"
    MODIFIED = "modified"


class RiskDecisionType(str, Enum):
    """Risk decision types."""

    POSITION_CHECK = "position_check"
    EXPOSURE_CHECK = "exposure_check"
    DRAWDOWN_CHECK = "drawdown_check"
    KILL_SWITCH = "kill_switch"
    CORRELATION_CHECK = "correlation_check"
    VAR_BREACH = "var_breach"


class AdapterProbeType(str, Enum):
    """Adapter probe types."""

    CONNECTIVITY = "connectivity"
    AUTHENTICATION = "authentication"
    RATE_LIMIT = "rate_limit"
    MARKET_DATA = "market_data"
    ACCOUNT_INFO = "account_info"
    ORDER_PLACEMENT = "order_placement"


class MicrostructureEventType(str, Enum):
    """Microstructure event types."""

    FILL = "fill"
    SLIPPAGE = "slippage"
    LATENCY = "latency"
    QUEUE_POSITION = "queue_position"
    PARTIAL_FILL = "partial_fill"
    REJECTION = "rejection"
    DEPTH_UPDATE = "depth_update"


@dataclass
class BaseLogEvent:
    """Base log event with common fields."""

    event_type: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    span_id: str = field(default_factory=lambda: str(uuid.uuid4())[:16])
    service: str = "cryptoquant"
    environment: str = "development"


@dataclass
class OrderLifecycleEvent(BaseLogEvent):
    """Order lifecycle log event."""

    event_type: str = LogEventType.ORDER_LIFECYCLE.value
    order_id: str = ""
    client_order_id: str = ""
    exchange_order_id: Optional[str] = None
    symbol: str = ""
    side: str = ""
    order_type: str = ""
    quantity: float = 0.0
    price: Optional[float] = None
    filled_quantity: float = 0.0
    avg_fill_price: Optional[float] = None
    status: str = ""
    event_subtype: OrderEventType = OrderEventType.CREATED
    exchange: str = ""
    latency_ms: Optional[float] = None
    error: Optional[str] = None


@dataclass
class RiskDecisionEvent(BaseLogEvent):
    """Risk decision log event."""

    event_type: str = LogEventType.RISK_DECISION.value
    decision_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    decision_type: RiskDecisionType = RiskDecisionType.POSITION_CHECK
    allowed: bool = True
    reason: str = ""
    current_value: float = 0.0
    limit_value: float = 0.0
    utilization_pct: float = 0.0
    affected_symbols: list = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AdapterProbeEvent(BaseLogEvent):
    """Adapter probe log event."""

    event_type: str = LogEventType.ADAPTER_PROBE.value
    probe_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    probe_type: AdapterProbeType = AdapterProbeType.CONNECTIVITY
    exchange: str = ""
    success: bool = True
    latency_ms: float = 0.0
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MicrostructureEvent(BaseLogEvent):
    """Microstructure event log."""

    event_type: str = LogEventType.MICROSTRUCTURE_EVENT.value
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_subtype: MicrostructureEventType = MicrostructureEventType.FILL
    symbol: str = ""
    exchange: str = ""
    order_id: str = ""
    client_order_id: str = ""
    quantity: float = 0.0
    price: float = 0.0
    expected_price: Optional[float] = None
    slippage_bps: Optional[float] = None
    latency_ms: Optional[float] = None
    queue_position: Optional[int] = None
    depth_level: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class JSONFormatter(logging.Formatter):
    """JSON log formatter with structured fields."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in {
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs",
                "message", "msg", "name", "pathname", "process",
                "processName", "relativeCreated", "thread", "threadName",
                "exc_info", "exc_text", "stack_info", "getMessage"
            }:
                log_data[key] = value

        return json.dumps(log_data, default=str)


class StructuredLogger:
    """Structured logger with typed event methods."""

    def __init__(self, name: str, environment: str = "development"):
        self.logger = logging.getLogger(name)
        self.environment = environment
        self._trace_context: Dict[str, str] = {}

    def set_trace_context(self, trace_id: str, span_id: str) -> None:
        """Set trace context for correlation."""
        self._trace_context = {"trace_id": trace_id, "span_id": span_id}

    def clear_trace_context(self) -> None:
        """Clear trace context."""
        self._trace_context = {}

    def _log_event(self, event: BaseLogEvent, level: int = logging.INFO) -> None:
        """Log a structured event."""
        event.environment = self.environment
        extra = asdict(event)
        self.logger.log(level, event.event_type, extra=extra)

    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self.logger.info(message, extra=kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self.logger.warning(message, extra=kwargs)

    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        self.logger.error(message, extra=kwargs)

    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self.logger.debug(message, extra=kwargs)

    def log_order_lifecycle(self, event: OrderLifecycleEvent) -> None:
        """Log order lifecycle event."""
        self._log_event(event)

    def log_risk_decision(self, event: RiskDecisionEvent) -> None:
        """Log risk decision event."""
        self._log_event(event, level=logging.WARNING if not event.allowed else logging.INFO)

    def log_adapter_probe(self, event: AdapterProbeEvent) -> None:
        """Log adapter probe event."""
        level = logging.ERROR if not event.success else logging.INFO
        self._log_event(event, level=level)

    def log_microstructure(self, event: MicrostructureEvent) -> None:
        """Log microstructure event."""
        self._log_event(event)

    def log_reconciliation(self, event: BaseLogEvent) -> None:
        """Log reconciliation event."""
        self._log_event(event)

    def log_playbook(self, event: BaseLogEvent) -> None:
        """Log playbook event."""
        self._log_event(event)

    def log_health_check(self, event: BaseLogEvent) -> None:
        """Log health check event."""
        self._log_event(event)


# Global logger registry
_loggers: Dict[str, StructuredLogger] = {}
_logger_lock = threading.Lock()


def get_logger(name: str, environment: str = "development") -> StructuredLogger:
    """Get or create a structured logger."""
    with _logger_lock:
        if name not in _loggers:
            _loggers[name] = StructuredLogger(name, environment)
        return _loggers[name]


def configure_logging(
    level: str = "INFO",
    format_type: str = "json",
    output: str = "stdout",
    environment: str = "development",
) -> None:
    """Configure global logging."""
    log_level = getattr(logging, level.upper(), logging.INFO)

    handler: logging.Handler
    if output == "stdout":
        handler = logging.StreamHandler(sys.stdout)
    elif output == "stderr":
        handler = logging.StreamHandler(sys.stderr)
    else:
        handler = logging.FileHandler(output)

    if format_type == "json":
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s %(name)s %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%S%z",
            )
        )

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers = [handler]

    # Update all existing loggers
    for logger in _loggers.values():
        logger.environment = environment


class OrderLifecycleLogger:
    """Specialized logger for order lifecycle events."""

    def __init__(self, logger: StructuredLogger):
        self.logger = logger

    def created(
        self,
        order_id: str,
        client_order_id: str,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        exchange: str = "binance",
    ) -> None:
        event = OrderLifecycleEvent(
            order_id=order_id,
            client_order_id=client_order_id,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            status="created",
            event_subtype=OrderEventType.CREATED,
            exchange=exchange,
        )
        self.logger.log_order_lifecycle(event)

    def submitted(
        self,
        order_id: str,
        client_order_id: str,
        symbol: str,
        side: str,
        exchange: str = "binance",
        latency_ms: Optional[float] = None,
    ) -> None:
        event = OrderLifecycleEvent(
            order_id=order_id,
            client_order_id=client_order_id,
            symbol=symbol,
            side=side,
            order_type="",
            quantity=0,
            status="submitted",
            event_subtype=OrderEventType.SUBMITTED,
            exchange=exchange,
            latency_ms=latency_ms,
        )
        self.logger.log_order_lifecycle(event)

    def acknowledged(
        self,
        order_id: str,
        client_order_id: str,
        exchange_order_id: str,
        symbol: str,
        exchange: str = "binance",
        latency_ms: Optional[float] = None,
    ) -> None:
        event = OrderLifecycleEvent(
            order_id=order_id,
            client_order_id=client_order_id,
            exchange_order_id=exchange_order_id,
            symbol=symbol,
            side="",
            order_type="",
            quantity=0,
            status="acknowledged",
            event_subtype=OrderEventType.ACKNOWLEDGED,
            exchange=exchange,
            latency_ms=latency_ms,
        )
        self.logger.log_order_lifecycle(event)

    def partial_fill(
        self,
        order_id: str,
        client_order_id: str,
        exchange_order_id: str,
        symbol: str,
        filled_quantity: float,
        avg_fill_price: float,
        exchange: str = "binance",
    ) -> None:
        event = OrderLifecycleEvent(
            order_id=order_id,
            client_order_id=client_order_id,
            exchange_order_id=exchange_order_id,
            symbol=symbol,
            side="",
            order_type="",
            quantity=0,
            filled_quantity=filled_quantity,
            avg_fill_price=avg_fill_price,
            status="partial_fill",
            event_subtype=OrderEventType.PARTIAL_FILL,
            exchange=exchange,
        )
        self.logger.log_order_lifecycle(event)

    def filled(
        self,
        order_id: str,
        client_order_id: str,
        exchange_order_id: str,
        symbol: str,
        filled_quantity: float,
        avg_fill_price: float,
        exchange: str = "binance",
    ) -> None:
        event = OrderLifecycleEvent(
            order_id=order_id,
            client_order_id=client_order_id,
            exchange_order_id=exchange_order_id,
            symbol=symbol,
            side="",
            order_type="",
            quantity=0,
            filled_quantity=filled_quantity,
            avg_fill_price=avg_fill_price,
            status="filled",
            event_subtype=OrderEventType.FILLED,
            exchange=exchange,
        )
        self.logger.log_order_lifecycle(event)

    def cancelled(
        self,
        order_id: str,
        client_order_id: str,
        exchange_order_id: Optional[str],
        symbol: str,
        exchange: str = "binance",
        reason: Optional[str] = None,
    ) -> None:
        event = OrderLifecycleEvent(
            order_id=order_id,
            client_order_id=client_order_id,
            exchange_order_id=exchange_order_id,
            symbol=symbol,
            side="",
            order_type="",
            quantity=0,
            status="cancelled",
            event_subtype=OrderEventType.CANCELLED,
            exchange=exchange,
            error=reason,
        )
        self.logger.log_order_lifecycle(event)

    def rejected(
        self,
        order_id: str,
        client_order_id: str,
        symbol: str,
        error: str,
        exchange: str = "binance",
    ) -> None:
        event = OrderLifecycleEvent(
            order_id=order_id,
            client_order_id=client_order_id,
            symbol=symbol,
            side="",
            order_type="",
            quantity=0,
            status="rejected",
            event_subtype=OrderEventType.REJECTED,
            exchange=exchange,
            error=error,
        )
        self.logger.log_order_lifecycle(event)


class RiskDecisionLogger:
    """Specialized logger for risk decisions."""

    def __init__(self, logger: StructuredLogger):
        self.logger = logger

    def log_decision(
        self,
        decision_type: RiskDecisionType,
        allowed: bool,
        reason: str,
        current_value: float,
        limit_value: float,
        affected_symbols: Optional[list] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        utilization = (current_value / limit_value * 100) if limit_value > 0 else 0
        event = RiskDecisionEvent(
            decision_type=decision_type,
            allowed=allowed,
            reason=reason,
            current_value=current_value,
            limit_value=limit_value,
            utilization_pct=utilization,
            affected_symbols=affected_symbols or [],
            metadata=metadata or {},
        )
        self.logger.log_risk_decision(event)


class AdapterProbeLogger:
    """Specialized logger for adapter probes."""

    def __init__(self, logger: StructuredLogger):
        self.logger = logger

    def log_probe(
        self,
        probe_type: AdapterProbeType,
        exchange: str,
        success: bool,
        latency_ms: float,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        event = AdapterProbeEvent(
            probe_type=probe_type,
            exchange=exchange,
            success=success,
            latency_ms=latency_ms,
            error=error,
            metadata=metadata or {},
        )
        self.logger.log_adapter_probe(event)


class MicrostructureEventLogger:
    """Specialized logger for microstructure events."""

    def __init__(self, logger: StructuredLogger):
        self.logger = logger

    def log_fill(
        self,
        symbol: str,
        exchange: str,
        order_id: str,
        client_order_id: str,
        quantity: float,
        price: float,
        expected_price: Optional[float] = None,
        latency_ms: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        slippage_bps = None
        if expected_price and expected_price > 0:
            slippage_bps = ((price - expected_price) / expected_price) * 10000

        event = MicrostructureEvent(
            event_subtype=MicrostructureEventType.FILL,
            symbol=symbol,
            exchange=exchange,
            order_id=order_id,
            client_order_id=client_order_id,
            quantity=quantity,
            price=price,
            expected_price=expected_price,
            slippage_bps=slippage_bps,
            latency_ms=latency_ms,
            metadata=metadata or {},
        )
        self.logger.log_microstructure(event)

    def log_slippage(
        self,
        symbol: str,
        exchange: str,
        order_id: str,
        client_order_id: str,
        expected_price: float,
        actual_price: float,
        quantity: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        slippage_bps = ((actual_price - expected_price) / expected_price) * 10000
        event = MicrostructureEvent(
            event_subtype=MicrostructureEventType.SLIPPAGE,
            symbol=symbol,
            exchange=exchange,
            order_id=order_id,
            client_order_id=client_order_id,
            quantity=quantity,
            price=actual_price,
            expected_price=expected_price,
            slippage_bps=slippage_bps,
            metadata=metadata or {},
        )
        self.logger.log_microstructure(event)

    def log_latency(
        self,
        symbol: str,
        exchange: str,
        order_id: str,
        client_order_id: str,
        latency_ms: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        event = MicrostructureEvent(
            event_subtype=MicrostructureEventType.LATENCY,
            symbol=symbol,
            exchange=exchange,
            order_id=order_id,
            client_order_id=client_order_id,
            quantity=0,
            price=0,
            latency_ms=latency_ms,
            metadata=metadata or {},
        )
        self.logger.log_microstructure(event)

    def log_rejection(
        self,
        symbol: str,
        exchange: str,
        order_id: str,
        client_order_id: str,
        error: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        event = MicrostructureEvent(
            event_subtype=MicrostructureEventType.REJECTION,
            symbol=symbol,
            exchange=exchange,
            order_id=order_id,
            client_order_id=client_order_id,
            quantity=0,
            price=0,
            metadata={"error": error, **(metadata or {})},
        )
        self.logger.log_microstructure(event)
