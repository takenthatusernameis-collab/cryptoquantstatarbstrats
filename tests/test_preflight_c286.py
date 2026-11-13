"""Tests for the C286 preflight script.

The C286 preflight is the fail-closed gate that must pass before the 5m
execution-overlay campaign runs.  These tests keep it honest: the script must
exist, pin the exact dataset SHAs, and report ready=true on the verified caches.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "preflight_c286.py"

EXPECTED_SHAS = {
    "SPOT_5M_SHA": "d15b0b183cf685a15dd34185baff22edf7ef3cc9c80c7d607bcd92f8da418c2f",
    "SPOT_5M_META_SHA": "e1a71f481cb4ad07881d132aba4ff7b47fc8194c69779701035efcf6e492ce4e",
    "VOLUME_SHA": "4365895387de4e542165fd331e39da40d455a3de24c7254eb67ba890053d193c",
    "VOLUME_META_SHA": "4d321584d3c687ad9956908c0179a1eae7d629c296c491e1e5ad1259a890c616",
    "VOLUME_PROVENANCE_SHA": "c7ff2f27ec5a668128e4856f809efde4922563dba87be0648be6d802c6d21c89",
}


def test_preflight_script_pins_dataset_shas() -> None:
    assert SCRIPT.exists(), f"missing C286 preflight script: {SCRIPT}"
    text = SCRIPT.read_text(encoding="utf-8")
    for name, sha in EXPECTED_SHAS.items():
        assert f'{name} = "{sha}"' in text, f"{name} must pin {sha}"
    assert "EXPECTED_5M_SHAPE = (26208, 11)" in text
    assert "EXPECTED_WF_SPLITS = 151" in text
    assert "LOOKBACKS_1H = (168, 336, 720)" in text


def test_preflight_reports_ready_on_verified_caches() -> None:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert proc.returncode == 0, f"preflight failed: {proc.stdout}\n{proc.stderr}"
    result = json.loads(proc.stdout)
    assert result["ready"] is True
    assert result["blocked_reasons"] == []
    assert result["real_data_only"] is True
    assert result["fabricated_data"] is False
    checks = result["checks"]
    assert checks["spot_5m"]["ok"] is True
    assert checks["volume_1h"]["ok"] is True
    assert checks["causal_alignment_1h_to_5m"]["ok"] is True
    assert checks["walk_forward"]["n_splits"] == 151
    assert checks["walk_forward"]["ok"] is True