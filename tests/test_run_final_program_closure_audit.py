"""Tests for scripts/run_final_program_closure_audit.py.

Final program-closure audit over all campaign verdicts C281B–C318 (NOT the stale
C305 generators). These tests never run campaigns, never retry C287, and never
fabricate data. They assert the audit exits 0, emits
reports/program_closure_final_<TS>.json with reachable_space CLOSED,
edge_proven false, binding_constraint multiple_testing, zero errors, and that
the recorded artifact SHA256-from-bytes matches a re-serialization of the
report without the artifact key.
"""
from __future__ import annotations

import glob
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_final_program_closure_audit.py"


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _latest_closure_report() -> Path:
    files = glob.glob(str(ROOT / "reports" / "program_closure_final_*.json"))
    assert files, "no program_closure_final_*.json artifact found"
    return Path(sorted(files)[-1])


def _report_body_sha(report: dict) -> str:
    body = {k: v for k, v in report.items() if k != "artifact"}
    return _sha256_bytes((json.dumps(body, indent=2, sort_keys=False) + "\n").encode("utf-8"))


def test_closure_audit_exits_zero():
    proc = subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr + proc.stdout


def test_closure_report_is_terminal_negative():
    report_path = _latest_closure_report()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["analysis"] == "final_program_closure_audit"
    assert report["reachable_space"] == "CLOSED"
    assert report["edge_proven"] is False
    assert report["binding_constraint"] == "multiple_testing"
    assert report["zero_tradable_costed_oos_edge"] is True
    assert report["all_verdicts_formal_negative_or_closure"] is True
    assert report["all_resolved_edge_proven_false_or_closure"] is True
    assert report["no_holm_bh_survivors_both"] is True
    assert report["n_survive_both_total"] == 0
    assert report["genuinely_new_families_tested"] > 0
    assert report["total_configs_recorded"] >= 15000
    assert report["errors"] == []
    assert report["campaign_range"] == "C281B-C318"
    assert report["source_host"] == "https://data.binance.vision"
    assert report["blocked_routes"] == {
        "binance_testnet_rest": 451,
        "fapi": 451,
        "bybit": 403,
    }
    assert report["missing_env_credentials"] is True
    assert "externally blocked" in report["c287"]
    assert set(report["stale_closures_not_reused"]) == {
        "scripts/run_c305_program_closure_oos.py",
        "scripts/run_program_closure_integrity_audit.py",
    }


def test_closure_report_self_sha_matches_bytes():
    report_path = _latest_closure_report()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    art = report["artifact"]
    assert Path(art["path"]).name == report_path.name
    assert art["sha256"] == _report_body_sha(report)
    for campaign in report["campaigns"]:
        for atype, art_entry in campaign["artifacts"].items():
            if art_entry["path"] is None:
                assert art_entry["sha_ok"] is None
                continue
            assert art_entry["sha_ok"] is True, (
                f"C{campaign['campaign']} {atype} SHA mismatch: {art_entry['path']}"
            )
            assert _sha256_bytes((ROOT / art_entry["path"]).read_bytes()) == art_entry["sha_computed"]
