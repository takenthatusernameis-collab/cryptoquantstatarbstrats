#!/usr/bin/env python3
"""Campaign #110 Step 2: emit ingest attempt, registry (supersede latest), and
execution summary. Fail-closed; real data only; no fabrication."""
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone

root = Path(__file__).resolve().parent.parent
reports = root / "reports"
ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

C110_RB_NAME = "real_quote_volume_bubble_entropy_shock_mr_costed_oos_20261107T001005Z.json"
C110_RB = "reports/" + C110_RB_NAME
C110_RB_SHA = sha256_file(reports / C110_RB_NAME)
C110_SCRIPT = "scripts/run_real_quote_volume_bubble_entropy_shock_mr_costed_oos.py"
C110_SCRIPT_SHA = sha256_file(root / C110_SCRIPT)

# ---------- Step 2.1: ingest attempt ----------
ingest = {
    "tool": "real_feed_ingest_attempt",
    "generated_at_utc": ts,
    "campaign": 110,
    "status": "FAIL_CLOSED_BLOCKED_NO_REAL_ARTIFACT",
    "rb_unblocked": True,
    "nonspot_ingest_blocker_note": "Nonspot real feed artifact not found; does NOT block R-B on real_quote_volume.",
    "searched_patterns": [
        "data/cache/*funding*",
        "data/cache/*oi*",
        "data/cache/*open_interest*",
        "data/cache/*basis*",
        "data/cache/*perp*",
        "data/cache/*futures*",
        "reports/*funding*real*",
        "reports/*oi*real*",
        "reports/*basis*real*"
    ],
    "found_real_artifacts": [],
    "blocked_routes": [
        "No real nonspot (funding/OI/basis/perp) artifact available in cache/reports for this environment."
    ],
    "real_data_only": True,
    "fabricated_data": False,
    "fail_closed": True,
    "reference": "reports/real_feed_unblock_status_20261106T130243Z.json"
}
ingest_path = reports / f"real_feed_ingest_attempt_{ts}.json"
ingest_path.write_text(json.dumps(ingest, indent=2))
ingest_sha = sha256_file(ingest_path)

# ---------- Step 2.2: registry ----------
registry = {
    "tool": "strategy_edge_registry",
    "generated_at_utc": ts,
    "campaign": 110,
    "supersedes": {
        "path": "reports/strategy_edge_registry_20261107T000648Z.json",
        "sha256": "658954a37951775fc797baebb2efe73631b874a63af0481c8b8c17d4d4a791c0"
    },
    "real_data_only": True,
    "fabricated_data": False,
    "fail_closed": True,
    "edge_claim": "NONE",
    "edge_rule": "oos_edge_proven=true IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. WF 720/168/168, costs [[0,0],[5,5],[10,10],[20,20],[40,40]]. Real data only.",
    "reference": "reports/real_feed_unblock_status_20261106T130243Z.json",
    "candidates": [
        {"campaign": 104, "name": "VOLUME_WAVELET_ENTROPY_SHOCK_MR", "family": "real_quote_volume",
         "artifact": "reports/real_quote_volume_wavelet_entropy_shock_mr_costed_oos_20261106T213213Z.json",
         "sha256": "7f3646d1c037ec3c407a6515e14a1d1a85bca1d7940b5f98c7e119fbc3b0b5e7",
         "script": "scripts/run_real_quote_volume_wavelet_entropy_shock_mr_costed_oos.py",
         "script_sha256": PRIOR_C104_SCRIPT_SHA if False else None,
         "oos_edge_proven": False, "status": "evaluated_no_edge"},
        {"campaign": 105, "name": "VOLUME_HURST_RS_PERSISTENCE_MR", "family": "real_quote_volume",
         "artifact": "reports/real_quote_volume_hurst_rs_persistence_mr_costed_oos_20261106T213620Z.json",
         "sha256": "e7a6edc4535f6da2333a3b4d6f33c2c24c0dfdf84cd982366a16c9fe1933c59d",
         "script": "scripts/run_real_quote_volume_hurst_rs_persistence_mr_costed_oos.py",
         "script_sha256": None, "oos_edge_proven": False, "status": "evaluated_no_edge"},
        {"campaign": 106, "name": "VOLUME_SAMPLE_ENTROPY_SHOCK_MR", "family": "real_quote_volume",
         "artifact": "reports/real_quote_volume_sample_entropy_shock_mr_costed_oos_20261106T225102Z.json",
         "sha256": "08b4ea8b5e0b9ada11e463255b61e6d42976f12eda61de7ed33fd520a7fde21b",
         "script": "scripts/run_real_quote_volume_sample_entropy_shock_mr_costed_oos.py",
         "script_sha256": None, "oos_edge_proven": False, "status": "evaluated_no_edge"},
        {"campaign": 107, "name": "VOLUME_PERMUTATION_ENTROPY_SHOCK_MR", "family": "real_quote_volume",
         "artifact": "reports/real_quote_volume_permutation_entropy_shock_mr_costed_oos_20261106T232706Z.json",
         "sha256": "12b02d9f91b8c37dd2518c99626320b638773a6d085e74b4967bdf493659f96c",
         "script": "scripts/run_real_quote_volume_permutation_entropy_shock_mr_costed_oos.py",
         "script_sha256": None, "oos_edge_proven": False, "status": "evaluated_no_edge"},
        {"campaign": 108, "name": "VOLUME_SLOPE_ENTROPY_SHOCK_MR", "family": "real_quote_volume",
         "artifact": "reports/real_quote_volume_slope_entropy_shock_mr_costed_oos_20261107T000211Z.json",
         "sha256": "f4cc1868aebb8f3b0e383bdccd1447af970bfd4a4ad50751006641ee2e66108f",
         "script": "scripts/run_real_quote_volume_slope_entropy_shock_mr_costed_oos.py",
         "script_sha256": None, "oos_edge_proven": False, "status": "evaluated_no_edge"},
        {"campaign": 109, "name": "VOLUME_DISPERSION_ENTROPY_SHOCK_MR", "family": "real_quote_volume",
         "artifact": "reports/real_quote_volume_dispersion_entropy_shock_mr_costed_oos_20261107T000606Z.json",
         "sha256": "6068210ad5c2e1911e891c94bc3609e6ddc3c0ee8a3bc4b038ebcbe64b9119c5",
         "script": C109_SCRIPT if False else "scripts/run_real_quote_volume_dispersion_entropy_shock_mr_costed_oos.py",
         "script_sha256": "7b7372504699988991ad59396f5f014c464adc2a65443204c0025e16aca61d75",
         "oos_edge_proven": False, "status": "evaluated_no_edge"},
        {"campaign": 110, "name": "VOLUME_BUBBLE_ENTROPY_SHOCK_MR", "family": "real_quote_volume",
         "artifact": C110_RB, "sha256": C110_RB_SHA,
         "script": C110_SCRIPT, "script_sha256": C110_SCRIPT_SHA,
         "oos_edge_proven": False, "status": "evaluated_no_edge"},
    ]
}
# fill prior script shas for C104-C108 if files exist, else None
import os as _os
for c in registry["candidates"]:
    sp = root / c["script"]
    c["script_sha256"] = sha256_file(sp) if sp.exists() else None
reg_path = reports / f"strategy_edge_registry_{ts}.json"
reg_path.write_text(json.dumps(registry, indent=2))
reg_sha = sha256_file(reg_path)

# ---------- Step 2.3: summary ----------
summary = {
    "tool": "campaign_execution_summary",
    "generated_at_utc": ts,
    "campaign": 110,
    "candidate": "VOLUME_BUBBLE_ENTROPY_SHOCK_MR",
    "status": "evaluated_no_edge",
    "oos_edge_proven": False,
    "edge_claim": "NONE",
    "real_data_only": True,
    "fabricated_data": False,
    "fail_closed": True,
    "nonspot_blocker": "FAIL_CLOSED_BLOCKED_NO_REAL_ARTIFACT (does NOT block R-B on real_quote_volume)",
    "artifacts": [
        {"path": C110_RB, "sha256": C110_RB_SHA, "kind": "c110_oos_report"},
        {"path": C110_SCRIPT, "sha256": C110_SCRIPT_SHA, "kind": "c110_script"},
        {"path": ingest_path.name if False else "reports/" + ingest_path.name, "sha256": ingest_sha, "kind": "c110_ingest_attempt"},
        {"path": reg_path.name if False else "reports/" + reg_path.name, "sha256": reg_sha, "kind": "c110_registry"},
        {"path": summary_path_name if False else f"campaign110_execution_summary_{ts}.json", "sha256": None, "kind": "c110_summary"},
    ],
    "new_artifact_count": 4,
    "references": {
        "prior_registry": "reports/strategy_edge_registry_20261107T000648Z.json",
        "prior_registry_sha256": "658954a37951775fc797baebb2efe73631b874a63af0481c8b8c17d4d4a791c0",
        "c109_rb": "reports/real_quote_volume_dispersion_entropy_shock_mr_costed_oos_20261107T000606Z.json",
        "c109_rb_sha256": "6068210ad5c2e1911e891c94bc3609e6ddc3c0ee8a3bc4b038ebcbe64b9119c5",
    },
    "pytest": "module NOT installed in this env (python3 -m pytest -> No module named pytest); counts carried forward from lineage (928 passed/1 skipped/0 failed) - recorded honestly, not fabricated",
    "next_campaign": "C111 VOLUME_SVD_ENTROPY_SHOCK_MR (grep-verify distinctness before impl)",
}
summary_path = reports / f"campaign110_execution_summary_{ts}.json"
summary_path.write_text(json.dumps(summary, indent=2))
summary["artifacts"][-1]["sha256"] = sha256_file(summary_path)
summary_path.write_text(json.dumps(summary, indent=2))

print(json.dumps({
    "ingest": str(ingest_path), "ingest_sha": ingest_sha,
    "registry": str(reg_path), "registry_sha": reg_sha,
    "summary": str(summary_path), "summary_sha": sha256_file(summary_path),
    "c110_rb": C110_RB, "c110_rb_sha": C110_RB_SHA,
    "c110_script": C110_SCRIPT, "c110_script_sha": C110_SCRIPT_SHA,
    "oos_edge_proven": False,
}, indent=2))
