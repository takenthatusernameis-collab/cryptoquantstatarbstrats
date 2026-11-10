"""Utility wrapper for Campaign #5 risk dashboard artifact construction.

This module provides a thin, explicit helper to build the machine-readable
``risk_dashboard.json`` payload from a runtime OMS/paper session. It does not
fabricate market data, fills, or breaches.
"""

from __future__ import annotations

from typing import Any

from execution.risk import RiskDashboard


def build_risk_dashboard_artifact(
    dashboard: RiskDashboard,
    *,
    campaign: str,
    generated_at_utc: str,
    environment: dict[str, Any],
    data_sources: list[dict[str, Any]] | dict[str, Any],
    portfolio_state: dict[str, Any] | None = None,
    blocked_routes: list[dict[str, Any]] | None = None,
    limitations: list[str] | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    state = dashboard.runtime_state(portfolio_state)
    artifact = {
        "campaign": campaign,
        "generated_at_utc": generated_at_utc,
        "status": state.get("status", "ok"),
        "environment": dict(environment),
        "data_sources": data_sources,
        "blocked_routes": list(blocked_routes or []),
        "risk_state": state,
        "events": [e.to_dict() for e in dashboard.events],
        "breaches": [b for b in state.get("breaches", [])],
        "limitations": list(limitations or []),
        "notes": [
            "Risk controls are fail-closed on missing/invalid/stale inputs where configured.",
            (
                "This dashboard reports paper/runtime state only; "
                "it does not claim real exchange risk coverage."
            ),
        ],
    }
    if extra:
        artifact.update(extra)
    return artifact
