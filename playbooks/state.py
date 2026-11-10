"""Operational state management with persistence."""

import json
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


class OperationalState(str, Enum):
    """Operational states."""

    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    ERROR = "error"
    MAINTENANCE = "maintenance"


@dataclass
class StateTransition:
    """State transition record."""

    transition_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    from_state: OperationalState = OperationalState.STOPPED
    to_state: OperationalState = OperationalState.STOPPED
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    triggered_by: str = ""
    reason: str = ""
    metadata: Dict = field(default_factory=dict)


@dataclass
class OperationalStateSnapshot:
    """Complete operational state snapshot."""

    current_state: OperationalState = OperationalState.STOPPED
    previous_state: Optional[OperationalState] = None
    transitions: List[StateTransition] = field(default_factory=list)
    started_at: Optional[datetime] = None
    paused_at: Optional[datetime] = None
    last_error: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    version: int = 1


class StateManager:
    """Manage operational state with persistence."""

    def __init__(self, persistence_path: str = "/tmp/cryptoquant_state.json"):
        self.persistence_path = Path(persistence_path)
        self._state = OperationalStateSnapshot()
        self._lock = threading.RLock()
        self._callbacks: List[Callable[[OperationalState, OperationalState], None]] = []
        self._load()

    def _load(self) -> None:
        """Load state from persistence file."""
        if self.persistence_path.exists():
            try:
                with open(self.persistence_path, "r") as f:
                    data = json.load(f)
                self._state = self._deserialize(data)
            except Exception:
                # If load fails, start fresh
                self._state = OperationalStateSnapshot()

    def _save(self) -> None:
        """Save state to persistence file."""
        try:
            self.persistence_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.persistence_path, "w") as f:
                json.dump(self._serialize(), f, indent=2, default=str)
        except Exception:
            pass  # Best effort

    def _serialize(self) -> Dict:
        """Serialize state to dict."""
        return {
            "current_state": self._state.current_state.value,
            "previous_state": (
                self._state.previous_state.value
                if self._state.previous_state
                else None
            ),
            "transitions": [
                {
                    "transition_id": t.transition_id,
                    "from_state": t.from_state.value,
                    "to_state": t.to_state.value,
                    "timestamp": t.timestamp.isoformat(),
                    "triggered_by": t.triggered_by,
                    "reason": t.reason,
                    "metadata": t.metadata,
                }
                for t in self._state.transitions
            ],
            "started_at": (
                self._state.started_at.isoformat()
                if self._state.started_at
                else None
            ),
            "paused_at": (
                self._state.paused_at.isoformat()
                if self._state.paused_at
                else None
            ),
            "last_error": self._state.last_error,
            "metadata": self._state.metadata,
            "version": self._state.version,
        }

    def _deserialize(self, data: Dict) -> OperationalStateSnapshot:
        """Deserialize state from dict."""
        transitions = []
        for t in data.get("transitions", []):
            transitions.append(StateTransition(
                transition_id=t["transition_id"],
                from_state=OperationalState(t["from_state"]),
                to_state=OperationalState(t["to_state"]),
                timestamp=datetime.fromisoformat(t["timestamp"]),
                triggered_by=t["triggered_by"],
                reason=t["reason"],
                metadata=t["metadata"],
            ))

        return OperationalStateSnapshot(
            current_state=OperationalState(data["current_state"]),
            previous_state=(
                OperationalState(data["previous_state"])
                if data.get("previous_state")
                else None
            ),
            transitions=transitions,
            started_at=(
                datetime.fromisoformat(data["started_at"])
                if data.get("started_at")
                else None
            ),
            paused_at=(
                datetime.fromisoformat(data["paused_at"])
                if data.get("paused_at")
                else None
            ),
            last_error=data.get("last_error"),
            metadata=data.get("metadata", {}),
            version=data.get("version", 1),
        )

    def register_callback(
        self, callback: Callable[[OperationalState, OperationalState], None]
    ) -> None:
        """Register a state change callback."""
        with self._lock:
            self._callbacks.append(callback)

    def _transition(
        self, new_state: OperationalState, triggered_by: str, reason: str = ""
    ) -> bool:
        """Internal state transition."""
        with self._lock:
            if self._state.current_state == new_state:
                return False

            old_state = self._state.current_state
            transition = StateTransition(
                from_state=old_state,
                to_state=new_state,
                triggered_by=triggered_by,
                reason=reason,
            )

            self._state.previous_state = old_state
            self._state.current_state = new_state
            self._state.transitions.append(transition)

            # Update timestamps
            if new_state == OperationalState.RUNNING and not self._state.started_at:
                self._state.started_at = datetime.now(timezone.utc)
            elif new_state == OperationalState.PAUSED:
                self._state.paused_at = datetime.now(timezone.utc)
            elif new_state == OperationalState.ERROR:
                self._state.last_error = reason

            self._save()

            # Notify callbacks
            for callback in self._callbacks:
                try:
                    callback(old_state, new_state)
                except Exception:
                    pass

            return True

    def start(self, triggered_by: str = "operator", reason: str = "") -> bool:
        """Start operations."""
        if self._state.current_state not in {
            OperationalState.STOPPED,
            OperationalState.ERROR,
        }:
            return False
        return self._transition(OperationalState.RUNNING, triggered_by, reason)

    def stop(self, triggered_by: str = "operator", reason: str = "") -> bool:
        """Stop operations."""
        if self._state.current_state not in {
            OperationalState.RUNNING,
            OperationalState.PAUSED,
            OperationalState.ERROR,
        }:
            return False
        self._transition(OperationalState.STOPPING, triggered_by, reason)
        return self._transition(OperationalState.STOPPED, triggered_by, reason)

    def pause(self, triggered_by: str = "operator", reason: str = "") -> bool:
        """Pause operations."""
        if self._state.current_state != OperationalState.RUNNING:
            return False
        return self._transition(OperationalState.PAUSED, triggered_by, reason)

    def resume(self, triggered_by: str = "operator", reason: str = "") -> bool:
        """Resume operations."""
        if self._state.current_state != OperationalState.PAUSED:
            return False
        return self._transition(OperationalState.RUNNING, triggered_by, reason)

    def set_error(self, triggered_by: str = "system", reason: str = "") -> bool:
        """Set error state."""
        return self._transition(OperationalState.ERROR, triggered_by, reason)

    def set_maintenance(self, triggered_by: str = "operator", reason: str = "") -> bool:
        """Set maintenance state."""
        if self._state.current_state not in {
            OperationalState.STOPPED,
            OperationalState.RUNNING,
            OperationalState.PAUSED,
        }:
            return False
        return self._transition(OperationalState.MAINTENANCE, triggered_by, reason)

    def get_state(self) -> OperationalState:
        """Get current state."""
        with self._lock:
            return self._state.current_state

    def get_snapshot(self) -> OperationalStateSnapshot:
        """Get complete state snapshot."""
        with self._lock:
            return OperationalStateSnapshot(
                current_state=self._state.current_state,
                previous_state=self._state.previous_state,
                transitions=list(self._state.transitions),
                started_at=self._state.started_at,
                paused_at=self._state.paused_at,
                last_error=self._state.last_error,
                metadata=dict(self._state.metadata),
                version=self._state.version,
            )

    def is_running(self) -> bool:
        """Check if running."""
        return self.get_state() == OperationalState.RUNNING

    def is_paused(self) -> bool:
        """Check if paused."""
        return self.get_state() == OperationalState.PAUSED

    def is_stopped(self) -> bool:
        """Check if stopped."""
        return self.get_state() == OperationalState.STOPPED

    def can_trade(self) -> bool:
        """Check if trading is allowed."""
        return self.get_state() == OperationalState.RUNNING

    def clear_error(self, triggered_by: str = "operator") -> bool:
        """Clear error state."""
        if self._state.current_state != OperationalState.ERROR:
            return False
        self._state.last_error = None
        return self._transition(OperationalState.STOPPED, triggered_by, "Error cleared")

    def update_metadata(self, key: str, value: Any) -> None:
        """Update metadata."""
        with self._lock:
            self._state.metadata[key] = value
            self._save()

    def get_transitions(self, limit: Optional[int] = None) -> List[StateTransition]:
        """Get state transition history."""
        with self._lock:
            transitions = list(self._state.transitions)
            if limit:
                return transitions[-limit:]
            return transitions
