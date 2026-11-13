"""Tests for the C288 preflight script.

The C288 preflight is the fail-closed gate that must pass before the
realized-volatility cross-sectional stat-arb campaign runs.  These tests keep it
honest: the script must exist, pin the exact dataset SHAs, and report ready=true
on the verified real 5m caches.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "preflight_c288.py"

EXPECTED_SHAS = {
    "SPOT_5M_SHA": "d15b0b183cf685a15dd34185baff22edf7ef3cc9c80c7d607bcd92f8da418c2f",
    "SPOT_5M_META_SHA": "e1a71f481cb4ad07881d132aba4ff7b47fc8194c69779701035efcf6e492ce4e",
}


def test_preflight_script_pins_dataset_shas() -> None:
    assert SCRIPT.exists(), f"missing C288 preflight script: {SCRIPT}"
    text = SCRIPT.read_text(encoding="utf-8")
    for name, sha in EXPECTED_SHAS.items():
        assert f'{name} = "{sha}"' in text, f"{name} must pin {sha}"
    assert "EXPECTED_5M_SHAPE = (26208, 11)" in text
    assert "EXPECTED_WF_SPLITS = 151" in text
    assert "LOOKBACKS_5M = (288, 1008, 2016)" in text


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
    assert checks["spot_5m"]["all_positive"] is True
    assert checks["walk_forward"]["n_splits"] == 151
    assert checks["walk_forward"]["ok"] is True
    assert checks["feature_warmup"]["ok"] is True