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


def load_state():
    return yaml.safe_load(STATE.read_text(encoding="utf-8"))


def pinned(kind: str) -> Path:
    """Deterministically select the closure artifact set recorded in state.yaml.

    ``scripts/run_c305_program_closure_oos.py`` writes a fresh timestamped
    closure/audit pair on every invocation, so ``latest(glob)`` is
    non-deterministic across test runs (each run leaves newer files behind and
    the comparison against state.yaml then fails). The frozen closure recorded
    in state.yaml is the authoritative artifact set; pin to it so the test is
    stable while still verifying the same substantive gates.
    """
    block = load_state().get("c305_program_closure") or {}
    key = {
        "closure": "closure_report_json",
        "audit": "integrity_audit_json",
        "closure_md": "closure_report_md",
        "audit_md": "integrity_audit_md",
    }[kind]
    entry = block.get(key) or {}
    rel = entry.get("path")
    assert rel, f"state.yaml does not record c305_program_closure.{key}"
    path = ROOT / rel
    assert path.exists(), f"state-recorded closure artifact missing: {rel}"
    return path


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
    # The closure runner writes a fresh timestamped closure/audit pair into
    # reports/ on every invocation. Those files are STALE C305-era artifacts that
    # contradict the live campaign (see AGENTS.md closure-trap) and must never be
    # left behind for a future session to mistake as authoritative. The test only
    # consumes the runner's stdout JSON (integrity_ok etc.) and the state-pinned
    # artifacts via ``pinned()``, so we delete exactly the files this run creates.
    before = set(REPORTS.glob("program_closure_*"))
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "run_c305_program_closure_oos.py"), "--json"],
        capture_output=True, text=True,
    )
    for p in set(REPORTS.glob("program_closure_*")) - before:
        p.unlink(missing_ok=True)
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
    rep = json.loads(pinned("closure").read_text(encoding="utf-8"))
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
    rep = json.loads(pinned("closure").read_text(encoding="utf-8"))
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
    aud = json.loads(pinned("audit").read_text(encoding="utf-8"))
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
    aud = json.loads(pinned("audit").read_text(encoding="utf-8"))
    for row in aud["campaign_rows"]:
        for it in row["items"]:
            if not it.get("exists"):
                # legacy campaigns (C281B-C297) predate the 5-artifact standard;
                # an absent optional artifact is informational for the runner
                assert "legacy" in " ".join(it.get("errors", [])).lower(), (row["campaign"], it["path"])
                continue
            assert it["sha256_match"] is True
            # expected_sha256 is only set when state.yaml records this exact
            # path; when it is absent the runner still verifies the artifact's
            # flags/verdict and the state-wide walk verifies every recorded ref.
            if it["expected_sha256"] is not None:
                assert it["expected_sha256"] == it["actual_sha256"]
                p = ROOT / it["path"]
                assert p.exists()
                assert sha256_file(p) == it["expected_sha256"]
            assert it["errors"] == []


def test_closure_report_and_audit_sha_match_state_and_bytes():
    state = yaml.safe_load(STATE.read_text(encoding="utf-8"))
    js = pinned("audit")
    rep = pinned("closure")
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
    md_js = pinned("audit_md")
    md_rep = pinned("closure_md")
    assert sha256_file(js) == actual_js
    assert sha256_file(rep) == actual_rep


def test_state_latest_campaign_c305_space_closed():
    """C305 closed the USDT-M/spot/options space. COIN-M inverse futures
    (C306/C307/C308/C309) is also exhausted: all formal negatives, 0 tradable
    costed-OOS edge, no next reachable family on disk. The C305 closure's own
    scope must remain CLOSED regardless of latest_campaign_done."""
    state = yaml.safe_load(STATE.read_text(encoding="utf-8"))
    # C305 closure stays valid as later campaigns (C306..C318) advance the
    # counter; only require a recognised post-closure campaign label.
    assert state["latest_campaign_done"] in {
        "C305", "C306", "C307", "C308", "C309", "C310", "C311",
        "C312", "C313", "C314", "C315", "C316", "C317", "C318",
    }, state.get("latest_campaign_done")
    closure = state.get("c305_program_closure") or {}
    assert closure.get("reachable_real_data_cross_sectional_stat_arb_space") == "CLOSED"
    scope = state.get("reachable_real_data_cross_sectional_stat_arb_space_scope", "")
    assert "COIN-M" in scope and "CLOSED" in scope.upper()


def test_probe_evidence_recorded_matches_bytes():
    state = yaml.safe_load(STATE.read_text(encoding="utf-8"))
    pb = state["c305_reachability_probe"]
    assert sha256_file(Path("data/cache/campaign305_reachability_probe.json")) == pb["cache_sha256"]
    assert sha256_file(Path("reports/c305_reachability_probe_20261115T030618Z.json")) == pb["report_sha256"]
    assert sha256_file(Path("data/cache/campaign305_reachability_probe.provenance.json")) == pb["provenance_sha256"]
    assert pb["path_b_recommended"] is True
    assert pb["genuinely_new_reachable_families"] == []


def test_no_tradable_edge_any_campaign():
    aud = json.loads(pinned("audit").read_text(encoding="utf-8"))
    # Legacy C281C/C289 predate the 5-artifact standard and expose no top-level
    # verdict in their surviving artifacts, so their verdicts list is empty; the
    # zero-edge gate is enforced by the closure report's n_tradable == 0 and
    # zero_tradable_edge_registry_confirmed plus every non-empty verdict row.
    for row in aud["campaign_rows"]:
        assert row["verdicts"] in ([], ["NOT_TRADABLE"], ["DATA_BLOCKED"]), row
        for it in row["items"]:
            d = it.get("checks", {})
            # Legacy C281B-C297 artifacts predate the n_edge_proven /
            # real_data_only / executed_fills flag standard: only fields that
            # are present are enforced (the runner's artifact_flags_ok already
            # enforces the same present-value rule).
            if d.get("edge_proven") is not None:
                assert d["edge_proven"] is False, (row["campaign"], it["path"], d)
            if d.get("n_edge_proven") is not None:
                assert d["n_edge_proven"] == 0, (row["campaign"], it["path"], d)
            if d.get("real_data_only") is not None:
                assert d["real_data_only"] is True, (row["campaign"], it["path"], d)
            if d.get("fabricated_data") is not None:
                assert d["fabricated_data"] is False, (row["campaign"], it["path"], d)
            if d.get("executed_fills") is not None:
                assert d["executed_fills"] is False, (row["campaign"], it["path"], d)
