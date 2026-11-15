"""Tests for C305 program closure (scripts/run_c305_program_closure_oos.py).

Runs the closure runner end-to-end and asserts: the runner exits 0 with
integrity_ok:true and n_mismatch_or_missing_or_error:0; the formal closure
report exists and carries real_data_only:true, fabricated_data:false,
executed_fills:false, reachable_real_data_cross_sectional_stat_arb_space
== CLOSED, edge_claim:NONE, oos_edge_proven:false, every C281B-C304 campaign
recorded as a formal negative (verdict NOT_TRADABLE, edge_proven:false,
n_edge_proven:0), and C287 cited as BLOCKED/decoupled; the integrity audit
reports zero mismatches across every campaign artifact + cache/meta/provenance
SHA256-from-bytes vs research_state/state.yaml; and state.yaml records the
closure report + integrity audit paths/SHA256s with latest_campaign_done:C305.

These tests never fetch market data, never fabricate data/fills, and never
re-run frozen C281B-C304 campaigns or retry C287.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
STATE = ROOT / "research_state" / "state.yaml"
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def latest(pattern: str) -> Path:
    matches = sorted(REPORTS.glob(pattern))
    assert matches, f"no artifact matching {pattern}"
    return matches[-1]


def walk_path_sha(node, out):
    if isinstance(node, dict):
        p = node.get("path")
        s = node.get("sha256")
        if isinstance(p, str) and isinstance(s, str) and (
            p.startswith("reports/") or p.startswith("data/cache/")
        ) and s and len(s) == 64 and all(c in "0123456789abcdef" for c in s):
            out.append((p, s))
        for v in node.values():
            walk_path_sha(v, out)
    elif isinstance(node, list):
        for v in node:
            walk_path_sha(v, out)


def _run_runner():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "run_c305_program_closure_oos.py"), "--json"],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout.strip())


def test_runner_exit_zero_integrity_ok():
    out = _run_runner()
    assert out.get("integrity_ok") is True
    assert out.get("n_mismatch_or_missing_or_error") == 0
    assert out.get("blocked_reasons") == []
    assert out.get("zero_tradable_edge_registry_confirmed") is True
    assert out.get("n_campaigns_audited") >= 1
    assert out.get("real_data_only") is True
    assert out.get("fabricated_data") is False
    assert out.get("executed_fills") is False


def test_closure_report_flags_and_scope():
    rep = json.loads(latest("program_closure_final_*.json").read_text(encoding="utf-8"))
    assert rep["artifact"] == "program_closure_final"
    assert rep["campaign"] == "C305"
    assert rep["path_b_recommended"] is True
    assert rep["reachable_real_data_cross_sectional_stat_arb_space"] == "CLOSED"
    assert rep["edge_claim"] == "NONE"
    assert rep["oos_edge_proven"] is False
    assert rep["n_tradable"] == 0
    assert rep["real_data_only"] is True
    assert rep["fabricated_data"] is False
    assert rep["executed_fills"] is False
    assert rep["c287"]["status"] == "BLOCKED"
    assert rep["c287"]["decoupled_from_economic_progress"] is True
    assert rep["c305_probe"]["path_b_recommended"] is True
    assert rep["c305_probe"]["genuinely_new_reachable_families"] == []


def test_closure_report_covers_all_campaigns_c281b_to_c304():
    rep = json.loads(latest("program_closure_final_*.json").read_text(encoding="utf-8"))
    labels = {c["campaign"] for c in rep["campaigns"]}
    expected = {
        "C281B", "C281C", "C282", "C283", "C284", "C285", "C286", "C288", "C289",
        "C290", "C291", "C292", "C293", "C294", "C295", "C296", "C297", "C298",
        "C299", "C300", "C301", "C302", "C303", "C304",
    }
    assert expected <= labels, f"missing campaigns: {expected - labels}"
    for c in rep["campaigns"]:
        assert c["frozen"] is True
        assert c["edge_claim"] == "NONE"
        assert c["oos_edge_proven"] is False
        assert c["real_data_only"] is True
        assert c["fabricated_data"] is False
        assert c["executed_fills"] is False


def test_integrity_audit_zero_mismatches():
    aud = json.loads(latest("program_closure_integrity_audit_*.json").read_text(encoding="utf-8"))
    assert aud["artifact"] == "program_closure_integrity_audit"
    assert aud["campaign"] == "C305"
    assert aud["integrity_ok"] is True
    assert aud["n_mismatch_or_missing_or_error"] == 0
    assert aud["n_references"] > 0
    assert aud["zero_tradable_edge_registry_confirmed"] is True
    assert aud["reachable_real_data_cross_sectional_stat_arb_space"] == "CLOSED"
    assert aud["real_data_only"] is True
    assert aud["fabricated_data"] is False
    assert aud["executed_fills"] is False
    assert isinstance(aud["campaign_rows"], list) and aud["campaign_rows"]
    for row in aud["campaign_rows"]:
        assert row["all_hashes_match"] is True
        assert row["any_errors"] is False


def test_integrity_audit_every_item_hash_matches_bytes():
    aud = json.loads(latest("program_closure_integrity_audit_*.json").read_text(encoding="utf-8"))
    for row in aud["campaign_rows"]:
        for it in row["items"]:
            assert it["exists"] is True
            assert it["sha256_match"] is True
            assert it["expected_sha256"] == it["actual_sha256"]
            assert it["errors"] == []
            p = ROOT / it["path"]
            assert p.exists()
            assert sha256_file(p) == it["expected_sha256"]


def test_closure_report_and_audit_sha_match_state_and_bytes():
    state = yaml.safe_load(STATE.read_text(encoding="utf-8"))
    js = latest("program_closure_integrity_audit_*.json")
    rep = latest("program_closure_final_*.json")
    actual_js = sha256_file(js)
    actual_rep = sha256_file(rep)

    recorded = {"json": None, "md": None, "closure_json": None, "closure_md": None}

    def walk(node):
        if isinstance(node, dict):
            p = node.get("path")
            s = node.get("sha256")
            if isinstance(p, str) and isinstance(s, str) and len(s) == 64:
                if p == str(js.relative_to(ROOT)):
                    recorded["json"] = s
                if p == str(rep.relative_to(ROOT)):
                    recorded["closure_json"] = s
            for v in node.values():
                if isinstance(v, (dict, list)):
                    walk(v)
        elif isinstance(node, list):
            for v in node:
                if isinstance(v, (dict, list)):
                    walk(v)

    walk(state)
    assert recorded["json"] == actual_js, "state.yaml must record the integrity audit path+sha256"
    assert recorded["closure_json"] == actual_rep, "state.yaml must record the closure report path+sha256"
    # companion .md files are named in state.yaml too (via the audit/closure blocks or latest_* entries)
    md_js = latest("program_closure_integrity_audit_*.md")
    md_rep = latest("program_closure_final_*.md")
    assert sha256_file(js) == actual_js
    assert sha256_file(rep) == actual_rep


def test_state_latest_campaign_c305_space_closed():
    state = yaml.safe_load(STATE.read_text(encoding="utf-8"))
    assert state["latest_campaign_done"] == "C305", state.get("latest_campaign_done")
    assert state["reachable_real_data_cross_sectional_stat_arb_space"] == "CLOSED"


def test_probe_evidence_recorded_matches_bytes():
    state = yaml.safe_load(STATE.read_text(encoding="utf-8"))
    pb = state["c305_reachability_probe"]
    assert sha256_file(Path("data/cache/campaign305_reachability_probe.json")) == pb["cache_sha256"]
    assert sha256_file(Path("reports/c305_reachability_probe_20261115T030618Z.json")) == pb["report_sha256"]
    assert sha256_file(Path("data/cache/campaign305_reachability_probe.provenance.json")) == pb["provenance_sha256"]
    assert pb["path_b_recommended"] is True
    assert pb["genuinely_new_reachable_families"] == []


def test_no_tradable_edge_any_campaign():
    aud = json.loads(latest("program_closure_integrity_audit_*.json").read_text(encoding="utf-8"))
    for row in aud["campaign_rows"]:
        assert row["verdicts"] == ["NOT_TRADABLE"], row
        for it in row["items"]:
            d = it.get("checks", {})
            assert d.get("edge_proven") is False, (row["campaign"], it["path"], d)
            assert d.get("n_edge_proven") == 0, (row["campaign"], it["path"], d)
            assert d.get("real_data_only") is True
            assert d.get("fabricated_data") is False
            assert d.get("executed_fills") is False
