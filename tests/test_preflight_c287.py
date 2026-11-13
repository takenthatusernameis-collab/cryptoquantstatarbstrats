"""Tests for the C287 preflight script (fail-closed readiness gate).

The C287 preflight must exist, pin the exact dataset SHA256s, never log secret
values, and report ready:false with enumerated blockers when credentials,
connectivity, caches, or the pre-computed signal parquet are missing.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "preflight_c287.py"

EXPECTED_SHAS = {
    "SPOT_5M_SHA": "d15b0b183cf685a15dd34185baff22edf7ef3cc9c80c7d607bcd92f8da418c2f",
    "SPOT_5M_META_SHA": "e1a71f481cb4ad07881d132aba4ff7b47fc8194c69779701035efcf6e492ce4e",
    "VOLUME_SHA": "4365895387de4e542165fd331e39da40d455a3de24c7254eb67ba890053d193c",
    "VOLUME_META_SHA": "4d321584d3c687ad9956908c0179a1eae7d629c296c491e1e5ad1259a890c616",
    "VOLUME_PROVENANCE_SHA": "c7ff2f27ec5a668128e4856f809efde4922563dba87be0648be6d802c6d21c89",
}


def test_preflight_script_pins_dataset_shas() -> None:
    assert SCRIPT.exists(), f"missing C287 preflight script: {SCRIPT}"
    text = SCRIPT.read_text(encoding="utf-8")
    for name, sha in EXPECTED_SHAS.items():
        assert f'{name} = "{sha}"' in text, f"{name} must pin {sha}"
    assert "REST_BASE = \"https://testnet.binance.vision\"" in text
    assert "WS_HOST = \"stream.testnet.binance.vision\"" in text
    assert "BINANCE_TESTNET_API_KEY" in text
    assert "BINANCE_TESTNET_API_SECRET" in text


def test_preflight_emits_json_with_ready_and_blockers() -> None:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--json"],
        cwd=ROOT, capture_output=True, text=True, timeout=300,
    )
    result = json.loads(proc.stdout)
    assert result["campaign"] == "C287"
    assert isinstance(result["ready"], bool)
    assert isinstance(result["blockers"], list)
    assert result["real_data_only"] is True
    assert result["fabricated_data"] is False
    assert "preflight_c287.py" in result["script"]
    assert result["blocker_count"] == len(result["blockers"])
    # No secret values logged anywhere in output.
    out = proc.stdout + proc.stderr
    assert "BINANCE_TESTNET_API_KEY=" not in out
    assert "BINANCE_TESTNET_API_SECRET=" not in out


def test_preflight_blockers_enumerated_when_unready() -> None:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--json"],
        cwd=ROOT, capture_output=True, text=True, timeout=300,
    )
    result = json.loads(proc.stdout)
    if result["ready"] is not True:
        assert len(result["blockers"]) >= 1
        assert all(isinstance(b, str) and b for b in result["blockers"])
    # Cache checks must reflect verified real caches.
    checks = result["checks"]
    assert checks["spot_5m_cache"]["ok"] is True
    assert checks["volume_1h_cache"]["ok"] is True
    assert checks["spot_5m_real_flags"]["ok"] is True
    assert checks["volume_real_flags"]["ok"] is True
