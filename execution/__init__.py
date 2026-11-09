"""Production bridge package: OMS primitives, paper broker, risk dashboard.

Campaign #5 - Production bridge (paper/testnet path, OMS primitives, risk dashboard).

All modules are fail-closed: invalid inputs are rejected explicitly and never
silently coerced into fabricated fills or order books. Paper fills are always
labeled ``simulated_fills: true`` and are never presented as real exchange fills.
"""

from __future__ import annotations

from execution.oms import (
    AccountState,
    OrderIntent,
    OrderRecord,
    OrderStatus,
    OMS,
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
]