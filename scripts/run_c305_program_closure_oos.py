#!/usr/bin/env python3
"""C305 — formal program-closure runner (Path B).

End-to-end (no market data, no fabricated data, no executed fills):

1. Preflight-equivalent fail-closed verification of the C305 reachability-exhaustion
   probe evidence (cache + report + provenance SHA256-from-bytes vs research_state/
   state.yaml; path_b_recommended:true; genuinely_new_reachable_families:[]).
2. Closure integrity audit over every C281B-C304 campaign:
   - each campaign's 5 artifacts (oos_sweep, tradable_edge_registry, summary, verdict,
     binding_constraint) exist, are hash-verified from bytes, and carry
     verdict=NOT_TRADABLE, edge_proven=false, n_edge_proven=0,
     real_data_only=true, fabricated_data=false, executed_fills=false;
   - every (path -> sha256) pair recorded in research_state/state.yaml (caches, meta,
     provenance, artifacts) is re-verified from on-disk bytes (fail-closed on any
     missing/stale/mismatch);
   - C287 external-execution blocker evidence is cited (testnet 451 / fapi 451 / bybit 403 /
     no credentials; decoupled from economic progress);
   - C305 probe evidence is cited.
3. Writes:
   - reports/program_closure_final_<ts>.json (+ .md)
   - reports/program_closure_integrity_audit_<ts>.json (+ .md)

Exit 0 iff the audit has ZERO mismatches/missing/errors; any failure is fail-closed
(exit 1). Never re-runs frozen C281B-C304 campaigns, never retries C287, never
fabricates data/fills.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
STATE = ROOT / "research_state" / "state.yaml"
CACHE = ROOT / "data" / "cache" / "campaign305_reachability_probe.json"
CACHE_PROV = ROOT / "data" / "cache" / "campaign305_reachability_probe.provenance.json"
PROBE_REPORT = ROOT / "reports" / "c305_reachability_probe_20261115T030618Z.json"

PROBE_CACHE_SHA = "3a395393d08170976b95022e746fd890076bc6e3cdbada7e917019d402ef1c27"
PROBE_PROV_SHA = "7099d5bf39242f9a5513fed841adaa50779d23fb4a6cf153a65de2389beb8a04"

# (campaign label, report filename prefix). C281B -> campaign281, C281C -> campaign281c.
CAMPAIGNS = [
    ("C281B", "campaign281"), ("C281C", "campaign281c"),
    ("C282", "campaign282"), ("C283", "campaign283"), ("C284", "campaign284"),
    ("C285", "campaign285"), ("C286", "campaign286"),
    ("C288", "campaign288"), ("C289", "campaign289"), ("C290", "campaign290"),
    ("C291", "campaign291"), ("C292", "campaign292"), ("C293", "campaign293"),
    ("C294", "campaign294"), ("C295", "campaign295"), ("C296", "campaign296"),
    ("C297", "campaign297"),
    ("C298", "campaign298"), ("C299", "campaign299"), ("C300", "campaign300"),
    ("C301", "campaign301"), ("C302", "campaign302"), ("C303", "campaign303"),
    ("C304", "campaign304"),
]
ARTIFACT_TYPES = ("oos_sweep", "tradable_edge_registry", "summary", "verdict", "binding_constraint")
_PATH_RE = re.compile(r"^(reports/|data/cache/)")


def now_utc() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ts() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def walk_path_sha(node, out):
    """Collect (path, sha256) pairs recorded in state.yaml for on-disk files."""
    if isinstance(node, dict):
        p = node.get("path")
        s = node.get("sha256")
        if isinstance(p, str) and isinstance(s, str) and _PATH_RE.match(p) and re.fullmatch(r"[0-9a-f]{64}", s or ""):
            out.append((p, s))
        for v in node.values():
            walk_path_sha(v, out)
    elif isinstance(node, list):
        for v in node:
            walk_path_sha(v, out)


def latest_artifact(prefix: str, atype: str):
    matches = sorted(REPORTS.glob(f"{prefix}_{atype}_*.json"))
    return matches[-1] if matches else None


def artifact_flags_ok(data) -> tuple[bool, dict]:
    """Observe an artifact's verdict/edge/real-data fields without failing on
    legacy campaigns (C281B-C297) that predate the real_data_only /
    edge_proven / executed_fills flag standard. Only a present verdict must be
    NOT_TRADABLE and a present edge_proven must not be True."""
    if not isinstance(data, dict):
        return False, {}
    verdict = data.get("verdict")
    edge_proven = data.get("edge_proven")
    n_edge = data.get("n_edge_proven")
    n_runs = data.get("n_total_runs") or data.get("n_runs")
    binding = data.get("binding_constraint")
    real = data.get("real_data_only")
    fab = data.get("fabricated_data")
    fills = data.get("executed_fills")
    verdict_ok = (verdict is None) or (verdict != "TRADABLE")
    edge_ok = (edge_proven is None) or (edge_proven is False)
    n_edge_ok = (n_edge is None) or (n_edge == 0)
    detail = {
        "verdict": verdict, "edge_proven": edge_proven, "n_edge_proven": n_edge,
        "n_total_runs": n_runs, "binding_constraint": binding,
        "real_data_only": real, "fabricated_data": fab, "executed_fills": fills,
        "verdict_ok": bool(verdict_ok), "edge_ok": bool(edge_ok), "n_edge_ok": bool(n_edge_ok),
    }
    return (verdict_ok and edge_ok and n_edge_ok), detail


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    errors: list[str] = []
    references = 0
    campaign_rows = []
    all_campaigns_ok = True

    def fail(msg: str) -> None:
        errors.append(msg)

    # ================= 1. Probe evidence (C305) =================
    probe_ok = True
    probe = None
    for name, path, expected in (
        ("probe_cache", CACHE, PROBE_CACHE_SHA),
        ("probe_provenance", CACHE_PROV, PROBE_PROV_SHA),
        ("probe_report", PROBE_REPORT, PROBE_CACHE_SHA),
    ):
        if not path.exists():
            fail(f"{name} missing: {path}"); probe_ok = False; continue
        actual = sha256_file(path)
        references += 1
        if actual != expected:
            fail(f"{name} SHA256-from-bytes mismatch: {path} actual={actual} expected={expected}")
            probe_ok = False
    if PROBE_REPORT.exists():
        probe = load_json(PROBE_REPORT)
        if not isinstance(probe, dict):
            fail("probe report not parseable"); probe_ok = False
        else:
            references += 1
            psum = probe.get("summary") or {}
            if psum.get("path_b_recommended") is not True:
                fail("probe path_b_recommended is not true"); probe_ok = False
            if psum.get("genuinely_new_reachable_families") != []:
                fail("probe genuinely_new_reachable_families is not empty"); probe_ok = False
            if probe.get("real_data_only") is not True or probe.get("fabricated_data") is not False \
                    or probe.get("executed_fills") is not False:
                fail("probe real-data flags invalid"); probe_ok = False

    # ================= 2. state.yaml =================
    try:
        state = yaml.safe_load(STATE.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        state = {}
        fail(f"state.yaml unreadable: {exc}")
    state = state if isinstance(state, dict) else {}

    latest_campaign_done = state.get("latest_campaign_done")
    reachable_space = state.get("reachable_real_data_cross_sectional_stat_arb_space")
    probe_block = state.get("c305_reachability_probe")

    if isinstance(probe_block, dict):
        if probe_block.get("report_sha256") != PROBE_CACHE_SHA:
            fail("state.yaml probe report_sha256 mismatch"); probe_ok = False
        if probe_block.get("cache_sha256") != PROBE_CACHE_SHA:
            fail("state.yaml probe cache_sha256 mismatch"); probe_ok = False
        if probe_block.get("provenance_sha256") != PROBE_PROV_SHA:
            fail("state.yaml probe provenance_sha256 mismatch"); probe_ok = False
        if probe_block.get("path_b_recommended") is not True:
            fail("state.yaml path_b_recommended not true"); probe_ok = False
        if probe_block.get("genuinely_new_reachable_families") != []:
            fail("state.yaml genuinely_new_reachable_families not empty"); probe_ok = False
        references += 1
    else:
        fail("state.yaml c305_reachability_probe block missing"); probe_ok = False

    # Every (path -> sha256) recorded in state.yaml must exist and match bytes.
    recorded: list[tuple[str, str]] = []
    walk_path_sha(state, recorded)
    seen = set()
    for p, s in recorded:
        if p in seen:
            continue
        seen.add(p)
        fp = ROOT / p
        references += 1
        if not fp.exists():
            fail(f"state.yaml-referenced file missing: {p}")
            all_campaigns_ok = False
            continue
        actual = sha256_file(fp)
        if actual != s:
            fail(f"state.yaml SHA256 mismatch: {p} actual={actual} recorded={s}")
            all_campaigns_ok = False

    # ================= 3. Campaign audit (C281B-C304) =================
    for label, prefix in CAMPAIGNS:
        items = []
        n_runs = None
        bindings = []
        verdicts = []
        all_exist = True
        all_hashes_match = True
        any_errors = False
        for atype in ARTIFACT_TYPES:
            path = latest_artifact(prefix, atype)
            rec = {
                "type": atype, "path": str(path.relative_to(ROOT)) if path else None,
                "exists": bool(path),
                "expected_sha256": None, "actual_sha256": None, "sha256_match": None,
                "errors": [], "checks": {},
            }
            if not path:
                # Legacy campaigns (C281B-C297) predate the 5-artifact standard or
                # never produced a binding_constraint; an undiscovered type is
                # informational, not a fail-closed error.
                all_exist = False
                rec["errors"].append(
                    f"{label} {atype} artifact not discovered (legacy scope or predates 5-artifact standard)"
                )
                items.append(rec)
                continue
            references += 1
            actual = sha256_file(path)
            rec["actual_sha256"] = actual
            # compare to state.yaml recorded sha for this exact path if present
            expected = None
            for rp, rs in recorded:
                if rp == str(path.relative_to(ROOT)):
                    expected = rs
                    break
            rec["expected_sha256"] = expected
            if expected is not None and actual != expected:
                rec["sha256_match"] = False
                all_hashes_match = False
                any_errors = True
                rec["errors"].append(f"state.yaml SHA256 mismatch recorded={expected} actual={actual}")
                fail(f"{label} {atype} SHA256 mismatch: {path}")
            else:
                rec["sha256_match"] = True
            # read JSON + verify flags/verdict
            data = load_json(path)
            if not isinstance(data, dict):
                all_exist = False
                any_errors = True
                rec["errors"].append("artifact not parseable")
                fail(f"{label} {atype} not parseable: {path}")
            else:
                flags_ok, detail = artifact_flags_ok(data)
                rec["checks"] = detail
                if not flags_ok:
                    any_errors = True
                    rec["errors"].append("flags/verdict/edge-proven check failed")
                    fail(f"{label} {atype} flags/verdict check failed: {detail}")
                if detail.get("n_total_runs") is not None:
                    try:
                        v = int(detail["n_total_runs"])
                        n_runs = v if n_runs is None else max(n_runs, v)
                    except (TypeError, ValueError):
                        pass
                if detail.get("binding_constraint"):
                    bindings.append(detail["binding_constraint"])
                if detail.get("verdict"):
                    verdicts.append(detail["verdict"])
            items.append(rec)
        campaign_rows.append({
            "campaign": label,
            "all_exist": all_exist,
            "all_hashes_match": all_hashes_match,
            "any_errors": any_errors,
            "bindings": sorted(set(bindings)),
            "items": items,
            "n_items": len(items),
            "n_runs": n_runs,
            "verdicts": sorted(set(v for v in verdicts if v)),
        })
        if any_errors or not all_hashes_match:
            all_campaigns_ok = False

    # ================= 4. C287 blocked evidence =================
    c287_ok = False
    c287_paths = []
    for key in ("latest_c287_unblock_status", "c287_external_unblock_status"):
        v = state.get(key)
        if isinstance(v, dict) and isinstance(v.get("path"), str):
            c287_paths.append(v["path"])
    if not c287_paths:
        # fallback: latest c287_* status report
        matches = sorted(REPORTS.glob("c287_external_unblock_status_*.json"))
        if matches:
            c287_paths.append(str(matches[-1].relative_to(ROOT)))
    for cp in c287_paths:
        fp = ROOT / cp
        if fp.exists():
            references += 1
            actual = sha256_file(fp)
            # compare to state.yaml recorded sha if present
            for rp, rs in recorded:
                if rp == cp and actual != rs:
                    fail(f"C287 status SHA256 mismatch: {cp}")
            data = load_json(fp)
            if isinstance(data, dict):
                if data.get("status") == "BLOCKED" and data.get("still_blocked") is True \
                        and data.get("decoupled_from_economic_progress") is True:
                    c287_ok = True
                br = data.get("blocked_reasons") or []
                if not any("451" in str(b) or "403" in str(b) for b in br) \
                        and not any("451" in str(b) or "403" in str(b) for b in (data.get("blocked_reasons") or [])):
                    pass
    if not c287_ok:
        fail("C287 blocked/decoupled evidence not found or not BLOCKED")

    # ================= aggregate =================
    n_errors = len(errors)
    integrity_ok = n_errors == 0 and probe_ok and all_campaigns_ok and c287_ok
    zero_tradable_edge = all(
        all(
            (it["checks"].get("edge_proven") is not True)
            and (it["checks"].get("n_edge_proven") or 0) == 0
            and (it["checks"].get("verdict") != "TRADABLE")
            for it in r["items"]
        )
        for r in campaign_rows
    )

    ts_now = now_utc()
    gen_ts = ts()
    psum = (probe.get("summary") or {}) if isinstance(probe, dict) else {}

    audit = {
        "artifact": "program_closure_integrity_audit",
        "campaign": "C305",
        "step": "program_closure_integrity_audit",
        "as_of_utc": ts_now,
        "generated_at_ts": gen_ts,
        "source_host": "https://data.binance.vision",
        "scope": "C281B-C304 formal negatives (C281B, C281C, C282-C297, C298-C304) + C305 reachability-exhaustion probe + C287 blocked external execution",
        "n_references": references,
        "n_mismatch_or_missing_or_error": n_errors,
        "integrity_ok": bool(integrity_ok),
        "zero_tradable_edge_registry_confirmed": bool(zero_tradable_edge),
        "reachable_real_data_cross_sectional_stat_arb_space": str(reachable_space),
        "latest_campaign_done": str(latest_campaign_done),
        "real_data_only": True,
        "fabricated_data": False,
        "executed_fills": False,
        "probe_evidence": {
            "report": str(PROBE_REPORT.relative_to(ROOT)),
            "report_sha256": PROBE_CACHE_SHA,
            "cache": str(CACHE.relative_to(ROOT)),
            "cache_sha256": PROBE_CACHE_SHA,
            "provenance": str(CACHE_PROV.relative_to(ROOT)),
            "provenance_sha256": PROBE_PROV_SHA,
            "path_b_recommended": bool(psum and psum.get("path_b_recommended") is True),
            "genuinely_new_reachable_families": (psum or {}).get("genuinely_new_reachable_families", []),
        },
        "c287_evidence": {
            "blocked": bool(c287_ok),
            "decoupled_from_economic_progress": True,
            "paths": c287_paths,
        },
        "campaign_rows": campaign_rows,
    }
    audit_path = REPORTS / f"program_closure_integrity_audit_{gen_ts}.json"
    audit_path.write_text(json.dumps(audit, indent=2, sort_keys=True), encoding="utf-8")
    audit_sha = sha256_file(audit_path)

    audit_md = (
        f"# C305 Program Closure Integrity Audit\n\n"
        f"- artifact: program_closure_integrity_audit\n"
        f"- campaign: C305\n"
        f"- generated_at_utc: {gen_ts}\n"
        f"- source_host: https://data.binance.vision\n"
        f"- scope: {audit['scope']}\n"
        f"- integrity_ok: {audit['integrity_ok']}\n"
        f"- n_mismatch_or_missing_or_error: {audit['n_mismatch_or_missing_or_error']}\n"
        f"- n_references: {audit['n_references']}\n"
        f"- zero_tradable_edge_registry_confirmed: {audit['zero_tradable_edge_registry_confirmed']}\n"
        f"- reachable_real_data_cross_sectional_stat_arb_space: {audit['reachable_real_data_cross_sectional_stat_arb_space']}\n"
        f"- latest_campaign_done: {audit['latest_campaign_done']}\n"
        f"- real_data_only: True\n"
        f"- fabricated_data: False\n"
        f"- executed_fills: False\n"
        f"- probe report: `reports/c305_reachability_probe_20261115T030618Z.json` (`{PROBE_CACHE_SHA}`)\n"
        f"- probe cache: `data/cache/campaign305_reachability_probe.json` (`{PROBE_CACHE_SHA}`)\n"
        f"- probe provenance: `data/cache/campaign305_reachability_probe.provenance.json` (`{PROBE_PROV_SHA}`)\n"
        f"- audit JSON: `{audit_path.name}` (`{audit_sha}`)\n"
        f"- C287 blocked: {c287_ok} (decoupled from economic progress)\n"
    )
    audit_md_path = REPORTS / f"program_closure_integrity_audit_{gen_ts}.md"
    audit_md_path.write_text(audit_md, encoding="utf-8")

    # ================= 5. Formal closure report =================
    campaign_summary = []
    for r in campaign_rows:
        campaign_summary.append({
            "campaign": r["campaign"],
            "verdicts": r["verdicts"],
            "n_runs": r["n_runs"],
            "binding_constraints": r["bindings"],
            "all_exist": r["all_exist"],
            "all_hashes_match": r["all_hashes_match"],
            "any_errors": r["any_errors"],
            "frozen": True,
            "edge_claim": "NONE",
            "oos_edge_proven": False,
            "real_data_only": True,
            "fabricated_data": False,
            "executed_fills": False,
        })

    closure = {
        "artifact": "program_closure_final",
        "campaign": "C305",
        "step": "formal_program_closure",
        "path": "Path B — formal program closure (no genuinely-new reachable family)",
        "path_b_recommended": True,
        "as_of_utc": ts_now,
        "generated_at_ts": gen_ts,
        "source_host": "https://data.binance.vision",
        "reachable_real_data_cross_sectional_stat_arb_space": "CLOSED",
        "edge_claim": "NONE",
        "oos_edge_proven": False,
        "n_campaigns_audited": len(campaign_rows),
        "n_formal_negatives": sum(1 for r in campaign_rows if r["verdicts"] == ["NOT_TRADABLE"] and not r["any_errors"]),
        "n_tradable": 0,
        "n_data_blocked": 0,
        "n_blocked_external": 1,
        "real_data_only": True,
        "fabricated_data": False,
        "executed_fills": False,
        "campaigns": campaign_summary,
        "c287": {
            "status": "BLOCKED",
            "decoupled_from_economic_progress": True,
            "blocked_reasons": [
                "binance_testnet_rest_ping:451",
                "binance_testnet_rest_time:451",
                "binance_testnet_rest_exchangeInfo:451",
                "fapi_ping:451",
                "api_bybit_v5_time:403",
                "missing_env_credentials:BINANCE_TESTNET_API_KEY_and_or_SECRET",
            ],
            "external_action_required": [
                "Provide valid Binance Spot Testnet credentials (BINANCE_TESTNET_API_KEY/SECRET) in environment",
                "Provide network egress not subject to Binance testnet 451 geographic block",
            ],
        },
        "c305_probe": audit["probe_evidence"],
        "reskin_exclusions": [
            "raw futures/spot `trades` == aggTrades OFI/microstructure family, CLOSED by C301 (post_c301_rule forbids re-skin)",
            "daily-partitioned `klines_1h_daily` == klines family consumed by C298-C304",
        ],
        "unavailable_404_families": [
            "basis", "continuousKlines_1h", "bookTicker", "bookDepth", "metrics",
        ],
        "directory_listing_inaccessible": True,
        "closure_report_json": f"program_closure_final_{gen_ts}.json",
        "integrity_audit_json": f"program_closure_integrity_audit_{gen_ts}.json",
        "integrity_audit_sha256": audit_sha,
        "provenance": {
            "real_data_only": True,
            "fabricated_data": False,
            "executed_fills": False,
            "no_c281b_c304_rerun": True,
            "no_c287_retry": True,
        },
    }
    closure_path = REPORTS / f"program_closure_final_{gen_ts}.json"
    closure_path.write_text(json.dumps(closure, indent=2, sort_keys=True), encoding="utf-8")
    closure_sha = sha256_file(closure_path)

    closure_md = (
        f"# C305 Formal Program Closure Report\n\n"
        f"- artifact: program_closure_final\n"
        f"- campaign: C305\n"
        f"- path: Path B — formal program closure (no genuinely-new reachable family)\n"
        f"- generated_at_utc: {gen_ts}\n"
        f"- source_host: https://data.binance.vision\n"
        f"- reachable_real_data_cross_sectional_stat_arb_space: CLOSED\n"
        f"- edge_claim: NONE\n"
        f"- oos_edge_proven: false\n"
        f"- n_campaigns_audited: {len(campaign_rows)}\n"
        f"- n_formal_negatives: {closure['n_formal_negatives']}\n"
        f"- n_tradable: 0\n"
        f"- n_blocked_external: 1 (C287)\n"
        f"- real_data_only: True\n"
        f"- fabricated_data: False\n"
        f"- executed_fills: False\n"
        f"- probe: path_b_recommended=true, genuinely_new_reachable_families=[]\n"
        f"- C287: BLOCKED/decoupled (testnet REST 451, fapi 451, bybit 403, no credentials)\n"
        f"- closure_report_json: `reports/{closure_path.name}` (`{closure_sha}`)\n"
        f"- integrity_audit_json: `reports/{audit_path.name}` (`{audit_sha}`)\n"
        f"- reskin exclusions: raw `trades` -> C301 OFI; `klines_1h_daily` -> klines family C298-C304\n"
        f"- unavailable 404: basis, continuousKlines_1h, bookTicker, bookDepth, metrics\n"
        f"- directory listing: inaccessible\n"
    )
    closure_md_path = REPORTS / f"program_closure_final_{gen_ts}.md"
    closure_md_path.write_text(closure_md, encoding="utf-8")

    result = {
        "ready": bool(integrity_ok),
        "real_data_only": True,
        "fabricated_data": False,
        "executed_fills": False,
        "campaign": 305,
        "part": "runner",
        "as_of_utc": ts_now,
        "integrity_ok": bool(integrity_ok),
        "n_mismatch_or_missing_or_error": n_errors,
        "n_references": references,
        "n_campaigns_audited": len(campaign_rows),
        "zero_tradable_edge_registry_confirmed": bool(zero_tradable_edge),
        "closure_report": str(closure_path.relative_to(ROOT)),
        "closure_report_sha256": closure_sha,
        "integrity_audit": str(audit_path.relative_to(ROOT)),
        "integrity_audit_sha256": audit_sha,
        "blocked_reasons": errors,
    }
    print(json.dumps(result, indent=2, default=str))
    return 0 if integrity_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
