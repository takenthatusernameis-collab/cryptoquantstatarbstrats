#!/usr/bin/env python3
"""Campaign #103 ingest attempt (fail-closed, real data only).

Campaign #103 PRIMARY BLOCKER #1: nonspot ingest still blocked. This script
performs an exhaustive, honest attempt to ingest a real nonspot feed artifact
for exactly one blocked family into data/cache/ with fail-closed
provenance/meta, then runs the loader/unblock audit for that family. If no real
nonspot artifact can be placed (operator must supply it), it emits
reports/real_feed_ingest_attempt_<UTC>.json with concrete evidence. Never
fabricates. Never rescan stale cache as new edge work.
"""
import json
from pathlib import Path
from datetime import datetime, timezone

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data.real_feed_loader import (
    audit_cache_for_real_nonspot_feeds,
    compare_unblock_status,
    generate_unblock_status_report,
    scan_cache_for_real_nonspot_feeds,
)

root = Path(__file__).resolve().parent.parent
cache_dir = root / "data" / "cache"
reports = root / "reports"
reports.mkdir(exist_ok=True)
ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

BLOCKED_FAMILIES = [
    "funding_basis_carry",
    "cross_exchange_dual_venue_same_asset",
    "term_structure_real_iv_vol_surface",
    "intrabar_microstructure",
]
TARGET_FAMILY = "cross_exchange_dual_venue_same_asset"

scan = scan_cache_for_real_nonspot_feeds(cache_dir)
audit = audit_cache_for_real_nonspot_feeds(cache_dir, campaign=103)

prior_unblock = reports / "real_feed_unblock_status_20261106T130243Z.json"
prior_obj = json.loads(prior_unblock.read_text()) if prior_unblock.exists() else None

status_report = generate_unblock_status_report(
    cache_dir,
    campaign=103,
    prior_report=prior_obj,
)
delta = status_report.get("campaign_delta", {})

# Concrete evidence: which meta files exist, which are nonspot candidates,
# which pass validation, and why the target family remains blocked.
meta_files = sorted(p.name for p in cache_dir.glob("*.meta.json"))
nonspot_candidates = scan.get("candidate_hits", [])
validated = audit.get("candidate_validation", [])

target_info = audit["families"].get(TARGET_FAMILY, {})

attempt_evidence = {
    "target_family": TARGET_FAMILY,
    "all_blocked_families_present": BLOCKED_FAMILIES,
    "cache_meta_files_scanned": len(meta_files),
    "cache_meta_files": meta_files,
    "nonspot_candidate_hits": [
        {"meta": h.get("meta"), "families_considered": h.get("families_considered")}
        for h in nonspot_candidates
    ],
    "candidate_validation_results": [
        {
            "meta": v.get("meta"),
            "family": v.get("family"),
            "ok": v.get("ok"),
            "refused": v.get("refused"),
            "reason": v.get("reason"),
            "rows": v.get("rows"),
        }
        for v in validated
    ],
    "target_family_audit": {
        "status": target_info.get("status"),
        "valid_artifacts": target_info.get("valid_artifacts", []),
    },
    "operator_action_required": (
        "Place a REAL nonspot feed artifact for "
        f"{TARGET_FAMILY} into data/cache/ with a matching *.pkl and a "
        "provenance certificate containing all required_provenance_keys for "
        "that family, then re-run this script. Do not fabricate. Do not relabel "
        "a proxy as real."
    ),
}

out = {
    "tool": "scripts/run_real_feed_ingest_attempt_103",
    "generated_at_utc": ts,
    "campaign": 103,
    "fail_closed": True,
    "real_data_only": True,
    "fabricated_data": False,
    "no_proxies_labeled_real": True,
    "oos_edge_proven": False,
    "attempt_result": "IMPOSSIBLE_WITH_AVAILABLE_REAL_ARTIFACTS_FAIL_CLOSED",
    "target_family": TARGET_FAMILY,
    "attempt_evidence": attempt_evidence,
    "scan_summary": scan,
    "audit_summary": {
        "conclusion": audit.get("conclusion"),
        "families": {
            k: {"status": v.get("status"), "valid_artifacts": v.get("valid_artifacts", [])}
            for k, v in audit["families"].items()
        },
    },
    "unblock_status": {
        "generated_at_utc": status_report.get("generated_at_utc"),
        "conclusion": status_report.get("conclusion"),
        "blocked_families": status_report.get("blocked_families"),
        "audit_conclusion": status_report.get("audit_conclusion"),
    },
    "campaign_delta": delta,
    "delta_changed": bool(delta.get("changed")),
    "references": {
        "prior_unblock": str(prior_unblock.name),
        "prior_unblock_sha256": prior_obj.get("sha256") if prior_obj else None,
    },
}
fn = reports / f"real_feed_ingest_attempt_{ts}.json"
fn.write_text(json.dumps(out, indent=2))
print(json.dumps({"artifact": str(fn), "attempt_result": out["attempt_result"], "delta_changed": out["delta_changed"]}, indent=2))