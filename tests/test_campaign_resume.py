"""The durable handoff state must point at a real, completed campaign.

This is a dependency-free consistency check for the fields the scheduled Kilo
workflow and the next agent rely on.  It deliberately does not parse YAML so it
can run in the minimal controller-tests venv.
"""
from __future__ import annotations

from pathlib import Path

STATE = Path("research_state/state.yaml")
C284_ARTIFACTS = (
    "reports/campaign284_oos_sweep_20261113T061220Z.json",
    "reports/campaign284_tradable_edge_registry_20261113T061220Z.json",
    "reports/campaign284_summary_20261113T061220Z.json",
    "reports/campaign284_verdict_20261113T061220Z.json",
    "reports/campaign284_binding_constraint_20261113T061220Z.json",
)


def test_state_has_active_handoff_and_completed_campaign() -> None:
    assert STATE.exists(), f"missing state file: {STATE}"
    text = STATE.read_text(encoding="utf-8")
    for key in (
        "updated_at_utc",
        "active_initial_task",
        "latest_campaign_done",
        "next_campaign",
        "oos_edge_proven",
        "handoff:",
        "single_authoritative: true",
    ):
        assert key in text, f"state.yaml missing {key}"

    assert "C284" in text, "state.yaml must record C284 as the latest completed campaign"
    for path in C284_ARTIFACTS:
        assert Path(path).exists(), f"missing frozen C284 artifact: {path}"


def test_handoff_forbids_duplicate_handoff_file() -> None:
    agents = Path("AGENTS.md")
    assert agents.exists(), "AGENTS.md is the single durable handoff"
    text = agents.read_text(encoding="utf-8")
    assert "HANDOFF.md" in text, "AGENTS.md must explicitly forbid HANDOFF.md"
    assert not Path("HANDOFF.md").exists(), "a duplicate handoff file must not exist"