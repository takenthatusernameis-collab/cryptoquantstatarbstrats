"""Production bridge package: OMS primitives, paper broker, risk dashboard, exchange adapter, lifecycle, microstructure.

Campaign #5 - Production bridge (paper/testnet path, OMS primitives, risk dashboard).
Campaign #6 - Live/testnet execution validation (adapter, lifecycle, microstructure).

All modules are fail-closed: invalid inputs are rejected explicitly and never
silently coerced into fabricated fills or order books. Paper fills are always
labeled ``simulated_fills: true`` and are never presented as real exchange fills.
"""

from __future__ import annotations

from execution.adapter import (
    AdapterMode,
    CapabilityProbe,
    ExchangeAdapter,
    ExchangeCredentials,
    Fill,
    OrderAck,
    OrderSide,
    OrderType,
    OrderUpdate,
    PaperExchangeAdapter,
    SimulatedTestnetAdapter,
    create_adapter_from_env,
)
from execution.adapter import (
    OrderIntent as AdapterOrderIntent,
)
from execution.adapter import (
    OrderStatus as AdapterOrderStatus,
)
from execution.adapter import (
    RejectReason as AdapterRejectReason,
)
from execution.lifecycle import (
    ACTIVE_STATES,
    TERMINAL_STATES,
    VALID_TRANSITIONS,
    LifecycleEvent,
    LifecycleHarness,
    LifecycleState,
    LifecycleTransition,
    LifecycleValidator,
    OrderLifecycle,
    create_test_lifecycle_scenarios,
)
from execution.microstructure import (
    DataGapHandler,
    LatencySample,
    LatencySimulator,
    MicrostructureConfig,
    MicrostructurePaperBroker,
    PaperFillResult,
    QueueSimulator,
    SlippageImpactModel,
    create_microstructure_broker_from_env,
)
from execution.oms import (
    OMS,
    AccountState,
    OrderIntent,
    OrderRecord,
    OrderStatus,
    RejectReason,
)
from execution.paper_broker import PaperBroker, PaperFill
from execution.risk import (
    Breach,
    KillSwitch,
    RiskConfig,
    RiskDashboard,
    RiskEvent,
    StaleDataGuard,
)

__all__ = [
    # Campaign #5 (existing)
    "AccountState",
    "Breach",
    "KillSwitch",
    "OMS",
    "OrderIntent",
    "OrderRecord",
    "OrderStatus",
    "PaperBroker",
    "PaperFill",
    "RejectReason",
    "RiskConfig",
    "RiskDashboard",
    "RiskEvent",
    "StaleDataGuard",
    # Campaign #6 - Adapter
    "AdapterMode",
    "OrderSide",
    "OrderType",
    "AdapterOrderStatus",
    "AdapterRejectReason",
    "CapabilityProbe",
    "ExchangeCredentials",
    "AdapterOrderIntent",
    "OrderAck",
    "Fill",
    "OrderUpdate",
    "ExchangeAdapter",
    "PaperExchangeAdapter",
    "SimulatedTestnetAdapter",
    "create_adapter_from_env",
    # Campaign #6 - Lifecycle
    "LifecycleState",
    "LifecycleEvent",
    "LifecycleTransition",
    "OrderLifecycle",
    "LifecycleValidator",
    "LifecycleHarness",
    "VALID_TRANSITIONS",
    "TERMINAL_STATES",
    "ACTIVE_STATES",
    "create_test_lifecycle_scenarios",
    # Campaign #6 - Microstructure
    "MicrostructureConfig",
    "LatencySample",
    "LatencySimulator",
    "SlippageImpactModel",
    "QueueSimulator",
    "DataGapHandler",
    "PaperFillResult",
    "MicrostructurePaperBroker",
    "create_microstructure_broker_from_env",
]
