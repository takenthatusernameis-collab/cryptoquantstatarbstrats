"""The durable handoff state must point at a real, completed campaign.

This is a dependency-free consistency check for the fields the scheduled Kilo
workflow and the next agent rely on.  It deliberately does not parse YAML so it
can run in the minimal controller-tests venv.
"""
from __future__ import annotations

import re
from pathlib import Path

STATE = Path("research_state/state.yaml")
REQUIRED_KEYS = (
    "updated_at_utc",
    "active_initial_task",
    "latest_campaign_done",
    "next_campaign",
    "oos_edge_proven",
    "handoff:",
    "single_authoritative: true",
)
ARTIFACT_KINDS = ("oos_sweep", "tradable_edge_registry", "summary", "verdict")


def test_state_has_active_handoff_and_completed_campaign() -> None:
    assert STATE.exists(), f"missing state file: {STATE}"
    text = STATE.read_text(encoding="utf-8")
    for key in REQUIRED_KEYS:
        assert key in text, f"state.yaml missing {key}"

    match = re.search(r"^latest_campaign_done:\s*(C\d+)\s*$", text, re.MULTILINE)
    assert match, "state.yaml must record latest_campaign_done"
    latest = match.group(1)
    number = latest[1:]

    pattern = re.compile(
        rf"reports/campaign{number}_([a-z_]+)_[0-9TZ]+\.json"
    )
    referenced = {m.group(1) for m in pattern.finditer(text)}
    missing_kinds = [k for k in ARTIFACT_KINDS if k not in referenced]
    assert not missing_kinds, (
        f"state.yaml must reference {latest} artifacts of kinds {missing_kinds}"
    )
    for path in sorted({m.group(0) for m in pattern.finditer(text)}):
        assert Path(path).exists(), f"missing frozen {latest} artifact: {path}"


def test_handoff_forbids_duplicate_handoff_file() -> None:
    agents = Path("AGENTS.md")
    assert agents.exists(), "AGENTS.md is the single durable handoff"
    text = agents.read_text(encoding="utf-8")
    assert "HANDOFF.md" in text, "AGENTS.md must explicitly forbid HANDOFF.md"
    assert not Path("HANDOFF.md").exists(), "a duplicate handoff file must not exist"