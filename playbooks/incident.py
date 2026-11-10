"""Incident response runbook with kill-switch activation, position flattening, and alert escalation."""

import asyncio
import os
import threading
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Awaitable, Callable, Dict, List, Optional


class IncidentType(str, Enum):
    """Incident types."""

    RISK_BREACH = "risk_breach"
    CONNECTIVITY_LOSS = "connectivity_loss"
    EXCHANGE_ERROR = "exchange_error"
    DATA_FEED_FAILURE = "data_feed_failure"
    POSITION_DISCREPANCY = "position_discrepancy"
    KILL_SWITCH = "kill_switch"
    MANUAL = "manual"
    UNKNOWN = "unknown"


class IncidentSeverity(str, Enum):
    """Incident severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(str, Enum):
    """Incident status."""

    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    MITIGATING = "mitigating"
    RESOLVED = "resolved"
    CLOSED = "closed"


@dataclass
class IncidentRecord:
    """Incident record."""

    incident_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    incident_type: IncidentType = IncidentType.UNKNOWN
    severity: IncidentSeverity = IncidentSeverity.MEDIUM
    status: IncidentStatus = IncidentStatus.OPEN
    title: str = ""
    description: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    resolved_by: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    actions_taken: List[Dict] = field(default_factory=list)


@dataclass
class KillSwitchResult:
    """Result of kill switch activation."""

    activated: bool = False
    activation_time: Optional[datetime] = None
    positions_flattened: int = 0
    orders_cancelled: int = 0
    error: Optional[str] = None
    details: Dict = field(default_factory=dict)


class IncidentResponse:
    """Incident response runbook."""

    def __init__(
        self,
        kill_switch_grace_seconds: int = 30,
        position_flatten_timeout_seconds: int = 300,
        alert_webhook_url: Optional[str] = None,
    ):
        self.kill_switch_grace_seconds = kill_switch_grace_seconds
        self.position_flatten_timeout_seconds = position_flatten_timeout_seconds
        self.alert_webhook_url = alert_webhook_url or os.getenv("ALERT_WEBHOOK_URL")
        self._incidents: Dict[str, IncidentRecord] = {}
        self._lock = threading.RLock()
        self._kill_switch_activated = False
        self._callbacks: List[Callable[[IncidentRecord], None]] = []

    def register_callback(self, callback: Callable[[IncidentRecord], None]) -> None:
        """Register incident callback."""
        with self._lock:
            self._callbacks.append(callback)

    def create_incident(
        self,
        incident_type: IncidentType,
        severity: IncidentSeverity,
        title: str,
        description: str,
        metadata: Optional[Dict] = None,
    ) -> IncidentRecord:
        """Create a new incident."""
        incident = IncidentRecord(
            incident_type=incident_type,
            severity=severity,
            title=title,
            description=description,
            metadata=metadata or {},
        )

        with self._lock:
            self._incidents[incident.incident_id] = incident

        self._notify_callbacks(incident)
        self._send_alert(incident)
        return incident

    def acknowledge_incident(self, incident_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an incident."""
        with self._lock:
            incident = self._incidents.get(incident_id)
            if not incident:
                return False

            incident.status = IncidentStatus.ACKNOWLEDGED
            incident.acknowledged_at = datetime.now(timezone.utc)
            incident.acknowledged_by = acknowledged_by
            incident.actions_taken.append({
                "action": "acknowledged",
                "by": acknowledged_by,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

        self._notify_callbacks(incident)
        return True

    def resolve_incident(self, incident_id: str, resolved_by: str, resolution: str = "") -> bool:
        """Resolve an incident."""
        with self._lock:
            incident = self._incidents.get(incident_id)
            if not incident:
                return False

            incident.status = IncidentStatus.RESOLVED
            incident.resolved_at = datetime.now(timezone.utc)
            incident.resolved_by = resolved_by
            incident.actions_taken.append({
                "action": "resolved",
                "by": resolved_by,
                "resolution": resolution,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

        self._notify_callbacks(incident)
        return True

    def close_incident(self, incident_id: str) -> bool:
        """Close an incident."""
        with self._lock:
            incident = self._incidents.get(incident_id)
            if not incident:
                return False

            incident.status = IncidentStatus.CLOSED
            incident.closed_at = datetime.now(timezone.utc)
            incident.actions_taken.append({
                "action": "closed",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

        return True

    def get_incident(self, incident_id: str) -> Optional[IncidentRecord]:
        """Get incident by ID."""
        with self._lock:
            return self._incidents.get(incident_id)

    def get_open_incidents(self) -> List[IncidentRecord]:
        """Get all open incidents."""
        with self._lock:
            return [
                i for i in self._incidents.values()
                if i.status in {IncidentStatus.OPEN, IncidentStatus.ACKNOWLEDGED, IncidentStatus.MITIGATING}
            ]

    def get_all_incidents(self) -> List[IncidentRecord]:
        """Get all incidents."""
        with self._lock:
            return list(self._incidents.values())

    def _notify_callbacks(self, incident: IncidentRecord) -> None:
        """Notify registered callbacks."""
        for callback in self._callbacks:
            try:
                callback(incident)
            except Exception:
                pass

    def _send_alert(self, incident: IncidentRecord) -> None:
        """Send alert via webhook."""
        if not self.alert_webhook_url:
            return

        try:
            import requests
            payload = {
                "incident_id": incident.incident_id,
                "type": incident.incident_type.value,
                "severity": incident.severity.value,
                "title": incident.title,
                "description": incident.description,
                "timestamp": incident.created_at.isoformat(),
            }
            requests.post(self.alert_webhook_url, json=payload, timeout=5)
        except Exception:
            pass  # Best effort

    async def activate_kill_switch(
        self,
        flatten_positions_fn: Callable[[], Awaitable[int]],
        cancel_orders_fn: Callable[[], Awaitable[int]],
        reason: str = "Manual kill switch activation",
    ) -> KillSwitchResult:
        """Activate kill switch - flatten positions and cancel orders."""
        if self._kill_switch_activated:
            return KillSwitchResult(
                activated=False,
                error="Kill switch already activated",
            )

        self._kill_switch_activated = True
        start_time = datetime.now(timezone.utc)

        result = KillSwitchResult(
            activated=True,
            activation_time=start_time,
        )

        try:
            # Grace period
            await asyncio.sleep(self.kill_switch_grace_seconds)

            # Flatten positions
            try:
                positions_flattened = await asyncio.wait_for(
                    flatten_positions_fn(),
                    timeout=self.position_flatten_timeout_seconds,
                )
                result.positions_flattened = positions_flattened
            except asyncio.TimeoutError:
                result.error = "Position flattening timeout"
                result.details["flatten_timeout"] = True

            # Cancel orders
            try:
                orders_cancelled = await cancel_orders_fn()
                result.orders_cancelled = orders_cancelled
            except Exception as e:
                result.details["cancel_error"] = str(e)

        except Exception as e:
            result.error = str(e)

        # Record incident
        self.create_incident(
            IncidentType.KILL_SWITCH,
            IncidentSeverity.CRITICAL,
            "Kill Switch Activated",
            reason,
            {"result": asdict(result)},
        )

        return result

    def reset_kill_switch(self) -> bool:
        """Reset kill switch (requires manual intervention)."""
        if not self._kill_switch_activated:
            return False
        self._kill_switch_activated = False
        return True

    def is_kill_switch_active(self) -> bool:
        """Check if kill switch is active."""
        return self._kill_switch_activated
