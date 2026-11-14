"""Tests for C287 external-unblock status artifact (fail-closed)."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def latest() -> Path:
    matches = sorted(REPORTS.glob("c287_external_unblock_status_*.json"))
    assert matches, "no c287_external_unblock_status artifact found"
    return matches[-1]


def test_c287_unblock_status_schema_fail_closed():
    path = latest()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["artifact"] == "c287_external_unblock_status"
    assert data["campaign"] == "C287"
    assert data["real_data_only"] is True
    assert data["fabricated_data"] is False
    assert data["decoupled_from_economic_progress"] is True
    assert isinstance(data["status"], str)
    assert isinstance(data["still_blocked"], bool)
    assert isinstance(data["http_probes"], list) and data["http_probes"]
    assert isinstance(data["ws_probes"], list) and data["ws_probes"]
    assert isinstance(data["blocked_reasons"], list)
    assert "credentials" in data
    assert "BINANCE_TESTNET_API_KEY_present" in data["credentials"]
    assert "BINANCE_TESTNET_API_SECRET_present" in data["credentials"]
    # no secrets leaked
    text = path.read_text(encoding="utf-8")
    assert "BINANCE_TESTNET_API_KEY=" not in text
    assert "BINANCE_TESTNET_API_SECRET=" not in text
    # probed expected blocked candidates
    names = {p["name"] for p in data["http_probes"]}
    for n in ["binance_testnet_rest_ping", "fapi_ping", "api_bybit_v5_time", "deribit_public_time"]:
        assert n in names
    # if still blocked, external action documented
    if data["still_blocked"]:
        assert data["status"] == "BLOCKED"
        assert data["external_action_required"]
        assert data["blocked_reasons"]


def test_c287_unblock_status_sha_matches_recorded_file_bytes():
    """The artifact's recorded sha256 must equal recomputation from file bytes."""
    path = latest()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert sha256_file(path) == data["sha256"], "sha256 must match file bytes"
    assert data["real_data_only"] is True
    assert data["fabricated_data"] is False
    assert data["still_blocked"] is True
    assert data["status"] == "BLOCKED"
    # blocked routes must include the known geographic/credential blockers
    reasons = " ".join(data["blocked_reasons"])
    assert "451" in reasons
    assert "missing_env_credentials" in reasons


def test_c287_unblock_status_referenced_by_closure_audit():
    """The latest C287 external-unblock artifact must be referenced (and
    hash-verified) inside the latest program closure-integrity audit."""
    unblock = latest()
    unblock_sha = sha256_file(unblock)
    audit_matches = sorted((ROOT / "reports").glob("program_closure_integrity_audit_*.json"))
    assert audit_matches, "no closure-integrity audit found to cross-reference"
    audit = json.loads(audit_matches[-1].read_text(encoding="utf-8"))
    c287_rows = [r for r in audit["campaign_rows"] if r["campaign"] == "C287"]
    assert c287_rows, "C287 must be audited in closure-integrity audit"
    found = False
    for row in c287_rows:
        for it in row["items"]:
            if it["path"] == str(unblock.relative_to(ROOT)):
                assert it["sha256_match"] is True
                assert it["expected_sha256"] == unblock_sha
                assert it["errors"] == []
                found = True
    assert found, "latest c287_external_unblock_status artifact must be hash-verified in audit"
