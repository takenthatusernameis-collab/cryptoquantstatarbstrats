"""Schema checks for the sole workflow diagnostics ledger.

The ledger is written by ``.github/workflows/main.yml`` and is the only durable
record of completed scheduled runs.  These checks are intentionally
dependency-free so they run in the workflow's minimal controller-tests venv.
"""
from __future__ import annotations

import json
from pathlib import Path

LEDGER = Path("research_state/workflow_run_diagnostics.jsonl")
REQUIRED_KEYS = ("run_id", "workflow_name", "status", "run_started_at", "run_completed_at")


def test_workflow_diagnostics_ledger_schema() -> None:
    assert LEDGER.exists(), f"missing diagnostics ledger: {LEDGER}"
    rows = [json.loads(line) for line in LEDGER.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert rows, "diagnostics ledger is empty"
    for index, row in enumerate(rows):
        assert isinstance(row, dict), f"row {index} is not an object"
        for key in REQUIRED_KEYS:
            assert key in row, f"row {index} missing {key}"
        assert isinstance(row["run_id"], int), f"row {index} run_id must be int"
        assert isinstance(row["workflow_name"], str) and row["workflow_name"], (
            f"row {index} workflow_name must be non-empty"
        )
        assert isinstance(row["status"], str) and row["status"], (
            f"row {index} status must be non-empty"
        )
        assert isinstance(row["run_started_at"], str) and row["run_started_at"], (
            f"row {index} run_started_at must be non-empty"
        )
        assert isinstance(row["run_completed_at"], str) and row["run_completed_at"], (
            f"row {index} run_completed_at must be non-empty"
        )
        if "potential_errors" in row:
            assert isinstance(row["potential_errors"], list), (
                f"row {index} potential_errors must be a list"
            )