"""Tests for program closure-integrity audit artifacts (C281B–C296)."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def latest(pattern: str) -> Path:
    matches = sorted(REPORTS.glob(pattern))
    assert matches, f"no artifact matching {pattern}"
    return matches[-1]


def test_closure_integrity_audit_json_schema_and_hashes():
    path = latest("program_closure_integrity_audit_*.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["artifact"] == "program_closure_integrity_audit"
    assert data["real_data_only"] is True
    assert data["fabricated_data"] is False
    assert data["integrity_ok"] is True
    assert data["n_mismatch_or_missing_or_error"] == 0
    assert data["n_references"] > 0
    assert data["zero_tradable_edge_registry_confirmed"] is True
    assert data["reachable_real_data_cross_sectional_stat_arb_space"] == "CLOSED"
    assert isinstance(data["campaign_rows"], list) and data["campaign_rows"]
    # every referenced item hash-verified
    for row in data["campaign_rows"]:
        for it in row["items"]:
            assert it["exists"] is True
            assert it["sha256_match"] is True
            assert it["expected_sha256"] == it["actual_sha256"]
            assert it["errors"] == []
            p = ROOT / it["path"]
            assert p.exists()
            assert sha256_file(p) == it["expected_sha256"]
    # core campaigns present (normalize C281B naming variants)
    campaigns = {r["campaign"] for r in data["campaign_rows"]}
    normalized = set()
    for c in campaigns:
        if c in ("C281", "281B"):
            normalized.add("C281B")
        elif c in ("281C", "C281C"):
            normalized.add("C281C")
        else:
            normalized.add(c)
    for c in ["C281B", "C282", "C285", "C286", "C287", "C288", "C289", "C290", "C291", "C292", "C293", "C294", "C295", "C296", "C297"]:
        assert c in normalized, f"missing campaign in audit: {c}"


def test_closure_integrity_audit_md_exists_and_consistent():
    md = latest("program_closure_integrity_audit_*.md")
    js = latest("program_closure_integrity_audit_*.json")
    # timestamps should align by suffix
    assert md.stem.replace("program_closure_integrity_audit_", "") == js.stem.replace("program_closure_integrity_audit_", "")
    text = md.read_text(encoding="utf-8")
    data = json.loads(js.read_text(encoding="utf-8"))
    assert f"integrity_ok: {data['integrity_ok']}" in text
    assert "real_data_only: True" in text
    assert "fabricated_data: False" in text
    assert "C296" in text
    assert "C297" in text


def test_closure_integrity_audit_sha_matches_recorded_file_bytes():
    """The audit JSON's own SHA256-from-bytes must equal the value recorded in
    the companion .md (written after the json), and must match recomputation
    from file bytes. The md's own SHA256 cannot be embedded in the md without
    becoming self-referential, so it is recorded in the authoritative handoff
    (research_state/state.yaml) and verified there."""
    import yaml

    js = latest("program_closure_integrity_audit_*.json")
    md = latest("program_closure_integrity_audit_*.md")
    data = json.loads(js.read_text(encoding="utf-8"))
    actual = sha256_file(js)
    md_text = md.read_text(encoding="utf-8")
    assert f"`{js.name}` (`{actual}`)" in md_text, "md must record json path+sha"
    assert f"n_references: {data['n_references']}" in md_text
    assert f"n_issues: {data['n_mismatch_or_missing_or_error']}" in md_text
    assert f"`{md.name}`" in md_text, "md must name itself in the artifacts block"

    state = yaml.safe_load((ROOT / "research_state" / "state.yaml").read_text(encoding="utf-8"))
    recorded = {"json": None, "md": None}

    def walk(node):
        if isinstance(node, dict):
            p = node.get("path")
            if isinstance(p, str) and (p.startswith("reports/") or p.startswith("data/")):
                rel = p
                if rel == str(js.relative_to(ROOT)):
                    s = node.get("sha256")
                    if isinstance(s, str) and len(s) == 64:
                        recorded["json"] = s
                if rel == str(md.relative_to(ROOT)):
                    s = node.get("sha256")
                    if isinstance(s, str) and len(s) == 64:
                        recorded["md"] = s
            for v in node.values():
                if isinstance(v, (dict, list)):
                    walk(v)
        elif isinstance(node, list):
            for v in node:
                if isinstance(v, (dict, list)):
                    walk(v)

    walk(state)
    assert recorded["json"] == actual, "state.yaml must record the audit json sha256"
    assert recorded["md"] == sha256_file(md), "state.yaml must record the audit md sha256"


def test_closure_integrity_audit_covers_c281b_through_c297():
    """Audit scope must span the full closed range C281B..C297 (intraday + daily)."""
    js = latest("program_closure_integrity_audit_*.json")
    data = json.loads(js.read_text(encoding="utf-8"))
    assert "C281B" in data["scope"]
    assert "C297" in data["scope"]
    campaigns = {r["campaign"] for r in data["campaign_rows"]}
    for c in ["C281B", "C281C", "C282", "C283", "C284", "C285", "C286", "C287",
              "C288", "C289", "C290", "C291", "C292", "C293", "C294", "C295",
              "C296", "C297"]:
        assert c in campaigns, f"missing campaign in audit: {c}"
    # every campaign row must be error-free and hash-verified
    for row in data["campaign_rows"]:
        assert row["all_hashes_match"] is True
        assert row["all_exist"] is True
        assert row["any_errors"] is False
