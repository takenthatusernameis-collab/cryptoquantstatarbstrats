"""Tests for the repository's CI-facing bootstrap and controller helpers.

These tests use only the Python standard library so they also run in the
workflow's minimal ``controller-tests`` virtualenv (pytest + numpy + requests).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFY_ENV = ROOT / "scripts" / "verify_env.py"
PREFLIGHT_C285 = ROOT / "scripts" / "preflight_c285.py"


def test_verify_env_json_schema() -> None:
    proc = subprocess.run(
        [sys.executable, str(VERIFY_ENV), "--json"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode in (0, 1), proc.stderr
    payload = json.loads(proc.stdout)
    assert isinstance(payload.get("ready"), bool)
    assert isinstance(payload.get("missing"), list)
    assert isinstance(payload.get("versions"), dict)


def test_preflight_c285_is_ready() -> None:
    proc = subprocess.run(
        [sys.executable, str(PREFLIGHT_C285), "--json"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    payload = json.loads(proc.stdout)
    assert payload["ready"] is True
    assert payload["real_data_only"] is True
    assert payload["fabricated_data"] is False
    assert payload["checks"]["spot_1h_sha"]["sha256"] == (
        "9355aed62b00a56b46ebba70eec4f9855620e8fea1b6eeae417ec6d7dea349df"
    )
    assert payload["checks"]["volume_1h_sha"]["sha256"] == (
        "4365895387de4e542165fd331e39da40d455a3de24c7254eb67ba890053d193c"
    )
    assert payload["checks"]["spot_5m_sha"]["sha256"] == (
        "d15b0b183cf685a15dd34185baff22edf7ef3cc9c80c7d607bcd92f8da418c2f"
    )
