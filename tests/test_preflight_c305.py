"""Tests for C305 preflight (scripts/preflight_c305.py): fail-closed
verification of the program-closure evidence before the C305 runner executes.

These tests never fetch market data and never fabricate data. They assert the
on-disk preflight result is ready:true with no blocked reasons, that the C305
probe cache/report/provenance SHA256-from-bytes match research_state/state.yaml,
that path_b_recommended is true with genuinely_new_reachable_families empty,
and that the preflight exits non-zero (fail-closed) when a gate is falsified.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "research_state" / "state.yaml"
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import preflight_c305 as pf  # noqa: E402


def _run_preflight():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "preflight_c305.py"), "--json"],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout.strip())


def test_preflight_exit_zero_ready_true():
    out = _run_preflight()
    assert out.get("ready") is True
    assert out.get("blocked_reasons") == []
    assert out.get("real_data_only") is True
    assert out.get("fabricated_data") is False
    assert out.get("executed_fills") is False


def test_preflight_probe_evidence_sha_matches_state_and_bytes():
    out = _run_preflight()
    state = yaml.safe_load(STATE.read_text(encoding="utf-8"))
    pb = state["c305_reachability_probe"]
    for label, path, expected_key in (
        ("cache", pf.CACHE, "cache_sha256"),
        ("provenance", pf.CACHE_PROV, "provenance_sha256"),
    ):
        actual = pf.sha256_file(path)
        assert actual == pb[expected_key], (label, actual, pb[expected_key])
    # probe report sha == cache sha (same bytes written twice)
    assert pf.sha256_file(pf.PROBE_REPORT) == pb["report_sha256"] == pb["cache_sha256"]


def test_preflight_path_b_and_genuinely_new_empty():
    out = _run_preflight()
    state = yaml.safe_load(STATE.read_text(encoding="utf-8"))
    pb = state["c305_reachability_probe"]
    assert pb["path_b_recommended"] is True
    assert pb["genuinely_new_reachable_families"] == []
    probe = json.loads(pf.PROBE_REPORT.read_text(encoding="utf-8"))
    assert probe["path_b_recommended"] is True
    assert probe["genuinely_new_reachable_families"] == []


def test_preflight_reachable_space_closed():
    out = _run_preflight()
    state = yaml.safe_load(STATE.read_text(encoding="utf-8"))
    assert state["reachable_real_data_cross_sectional_stat_arb_space"] == "CLOSED"


def test_preflight_fail_closed_when_probe_cache_missing(tmp_path, monkeypatch):
    fake_cache = tmp_path / "campaign305_reachability_probe_missing.json"
    assert not fake_cache.exists()
    monkeypatch.setattr(pf, "CACHE", fake_cache)
    monkeypatch.setattr(sys, "argv", ["preflight_c305.py"])
    rc = pf.main()
    assert rc != 0, "preflight must fail-closed when probe cache is missing"


def test_preflight_fail_closed_when_path_b_false_proper(tmp_path, monkeypatch):
    import preflight_c305 as p

    fake_report = tmp_path / "c305_fake.json"
    real_report = p.PROBE_REPORT.read_text(encoding="utf-8")
    fake_report.write_text(real_report.replace('"path_b_recommended": true', '"path_b_recommended": false'))
    monkeypatch.setattr(p, "PROBE_REPORT", fake_report)
    monkeypatch.setattr(sys, "argv", ["preflight_c305.py"])
    rc = p.main()
    assert rc != 0, "preflight must fail-closed when path_b_recommended is false"
