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
