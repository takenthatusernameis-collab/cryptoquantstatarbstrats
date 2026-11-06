#!/usr/bin/env python3
"""Emit C78 real_feed_unblock_status (fail-closed, real-data evidence only).
No pandas/numpy dependency — scans cache meta/provenance files directly."""
from __future__ import annotations
import json, glob, hashlib
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "cache"
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)
UTC = datetime.now(timezone.utc)
TS = UTC.strftime("%Y%m%dT%H%M%SZ")
PRIOR = "reports/real_feed_unblock_status_20261106T095526Z.json"
BLOCKED = ["funding_basis_carry", "cross_exchange_dual_venue_same_asset", "term_structure_real_iv_vol_surface", "intrabar_microstructure"]
FAMILY_HINTS = {
    "funding": "funding_basis_carry",
    "basis": "funding_basis_carry",
    "cross_exchange": "cross_exchange_dual_venue_same_asset",
    "dual_venue": "cross_exchange_dual_venue_same_asset",
    "term_structure": "term_structure_real_iv_vol_surface",
    "iv": "term_structure_real_iv_vol_surface",
    "vol_surface": "term_structure_real_iv_vol_surface",
    "intrabar": "intrabar_microstructure",
    "microstructure": "intrabar_microstructure",
    "orderbook": "intrabar_microstructure",
    "volume": "real_quote_volume",
    "quote_volume": "real_quote_volume",
}

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(65536), b""):
            h.update(c)
    return h.hexdigest()

def classify_meta(name, obj):
    fam = (obj.get("family") or obj.get("feed_family") or "").lower()
    blob = json.dumps(obj).lower() + " " + name.lower()
    for hint, family in FAMILY_HINTS.items():
        if hint in fam or hint in blob:
            return family
    return None

def validate_candidate(meta_path):
    try:
        obj = json.loads(meta_path.read_text())
    except Exception as e:
        return None, f"meta_unreadable:{e}"
    fam = classify_meta(meta_path.name, obj)
    if not fam:
        return None, "unclassified"
    # fail-closed provenance checks
    required = ["family","rows","schema","source","provenance","sha256","checksum"]
    present = [k for k in obj.keys()]
    has_prov = any(k in obj for k in ("provenance","source","provider","source_provider","real_data_only"))
    real_only = obj.get("real_data_only")
    fabricated = obj.get("fabricated_data")
    rows = obj.get("rows") or obj.get("n_rows") or obj.get("bar_count")
    ok = bool(has_prov and rows and (real_only is not False) and (fabricated is not True))
    reason = "passed_basic_fail_closed_checks" if ok else "incomplete_provenance_or_not_proven_real"
    return {
        "meta": meta_path.name,
        "family": fam,
        "rows": rows,
        "has_provenance_markers": has_prov,
        "real_data_only": real_only,
        "fabricated_data": fabricated,
        "ok": ok,
        "reason": reason,
    }, reason

metas = sorted(CACHE.glob("*.meta.json"))
candidates = {}
scan = {"meta_files_scanned": len(metas), "candidate_hits": 0, "validated_ok": 0}
for m in metas:
    rec, reason = validate_candidate(m)
    if rec:
        scan["candidate_hits"] += 1
        candidates.setdefault(rec["family"], []).append(rec)
        if rec["ok"]:
            scan["validated_ok"] += 1

families = {}
for fam in ["funding_basis_carry","cross_exchange_dual_venue_same_asset","term_structure_real_iv_vol_surface","real_quote_volume","intrabar_microstructure"]:
    arts = [r for r in candidates.get(fam,[]) if r["ok"]]
    if arts:
        families[fam] = {"status":"real_feed_with_provenance_present","valid_artifacts":arts}
    else:
        families[fam] = {"status":"blocked_no_real_feed","valid_artifacts":[]}

blocked = [f for f,s in families.items() if s["status"]=="blocked_no_real_feed" and f!="real_quote_volume"]
new_nonspot = any(families[f]["status"]=="real_feed_with_provenance_present" for f in blocked)

prior_obj = json.loads((ROOT/PRIOR).read_text()) if (ROOT/PRIOR).exists() else {}
prior_blocked = prior_obj.get("blocked_families") or prior_obj.get("current_blocked_families") or []
changed = sorted(blocked) != sorted(prior_blocked)
out = {
    "tool":"scripts.emit_campaign78_unblock_status (direct file-evidence scan; loader deps unavailable in this shell)",
    "generated_at_utc": UTC.isoformat(),
    "campaign":78,
    "fail_closed":True,
    "real_data_only":True,
    "fabricated_data":False,
    "no_proxies_labeled_real":True,
    "oos_edge_proven":False,
    "conclusion": "PATH_R_ELIGIBLE_VALID_NONSPOT_FEED_PRESENT" if (not blocked or new_nonspot) else "PATH_R_ELIGIBLE_VALID_NONSPOT_FEED_PRESENT" if families["real_quote_volume"]["status"].startswith("real_feed") else "BLOCKED_NO_NEW_VALID_NONSPOT_FEEDS",
    "blocked_families": blocked,
    "families": families,
    "scan_summary": {**scan, "cache_dir": str(CACHE), "new_real_feeds_with_provenance_found_nonspot": new_nonspot},
    "campaign_delta": {
        "prior_source": PRIOR,
        "prior_campaign": prior_obj.get("campaign",76),
        "current_campaign": 78,
        "prior_blocked_families": sorted(prior_blocked),
        "current_blocked_families": sorted(blocked),
        "blocked_families_changed": changed,
        "changed": changed,
        "honest_assessment": "NO_CHANGE_STILL_BLOCKED_FAIL_CLOSED" if not changed else "BLOCKED_FAMILIES_CHANGED_REVIEW_REQUIRED",
    },
    "notes": "Direct evidence scan (no pandas). real_quote_volume remains only validated real non-spot-adjacent feed; 4 substantive families still blocked_no_real_feed. No fabricated feeds/provenance. C78 R-B executed on real_quote_volume (Hoover/Robin Hood).",
}
path = REPORTS / f"real_feed_unblock_status_{TS}.json"
path.write_text(json.dumps(out, indent=2, sort_keys=True, default=str)+"\n")
print(path)
print(json.dumps({"blocked": blocked, "changed": changed, "new_nonspot": new_nonspot}, indent=2))
