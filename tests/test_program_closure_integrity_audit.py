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
    for c in ["C281B", "C282", "C285", "C286", "C287", "C288", "C289", "C290", "C291", "C292", "C293", "C294", "C295", "C296"]:
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
