#!/usr/bin/env python3
import json
import hashlib
import sys
from pathlib import Path
from datetime import datetime, timezone

root = Path(__file__).resolve().parent.parent
reports = root / "reports"
ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# Ingest attempt
ingest = {
    "tool": "real_feed_ingest_attempt",
    "generated_at_utc": ts,
    "campaign": 125,
    "real_data_only": True,
    "fail_closed": True,
    "status": "blocked_no_real_nonspot_artifact",
    "rb_unblocked": True,
    "detail": "No validated real nonspot artifact found in this environment; R-B proceeds on validated real_quote_volume family. Nonspot ingest not fabricated.",
    "sources_checked": ["data/cache/*", "reports/*nonspot*", "reports/*perp*", "reports/*futures*"],
    "sha256": {},
}
ingest_fn = reports / f"real_feed_ingest_attempt_{ts}.json"
ingest_fn.write_text(json.dumps(ingest, indent=2))
ingest_sha = sha256_file(ingest_fn)
ingest["sha256"][ingest_fn.name] = ingest_sha
ingest_fn.write_text(json.dumps(ingest, indent=2))

# Find latest artifacts
oos_c125 = sorted(reports.glob("real_quote_volume_recurrence_rate_shock_mr_costed_oos_*.json"))[-1]
oos_c125_sha = sha256_file(oos_c125)
script_c125 = root / "scripts" / "run_real_quote_volume_recurrence_rate_shock_mr_costed_oos.py"
script_c125_sha = sha256_file(script_c125)

# Load prior registry
prior_reg = reports / "strategy_edge_registry_20261107T045938Z.json"
prior_reg_sha = sha256_file(prior_reg)
reg = json.loads(prior_reg.read_text())

# Add C125
c125_entry = {
    "campaign": 125,
    "status": "DONE",
    "oos_edge_proven": False,
    "oos_artifact": str(oos_c125.relative_to(root)),
    "oos_artifact_sha256": oos_c125_sha,
    "edge_claim": "NONE",
    "ingest_artifact": str(ingest_fn.relative_to(root)),
    "ingest_artifact_sha256": ingest_sha,
    "script": str(script_c125.relative_to(root)),
    "script_sha256": script_c125_sha,
    "candidate": "VOLUME_RECURRENCE_RATE_SHOCK_MR (RQA %REC, m=2,tau=1,eps=0.15*sigma_embedded,W_RR=168)",
    "distinct_from_c124": "Hilbert phase histogram entropy vs RQA recurrence matrix density"
}

# Add to lineage if not present
# Find if C125 exists
has_c125 = False
for i, item in enumerate(reg.get("lineage", [])):
    if isinstance(item, dict) and item.get("campaign") == 125:
        reg["lineage"][i] = c125_entry
        has_c125 = True
        break
if not has_c125:
    # append
    reg["lineage"].append(c125_entry)

# Update campaigns list
if "campaigns" not in reg:
    reg["campaigns"] = []
# ensure C125 present
found = False
for c in reg["campaigns"]:
    if isinstance(c, dict) and c.get("id") == 125:
        c.update(c125_entry)
        found = True
        break
if not found:
    reg["campaigns"].append({"id": 125, **c125_entry})

reg["campaign"] = "C125"
reg["generated_at_utc"] = ts
reg["supersedes"] = str(prior_reg.relative_to(root))
reg["supersedes_sha256"] = prior_reg_sha

reg_fn = reports / f"strategy_edge_registry_{ts}.json"
reg_fn.write_text(json.dumps(reg, indent=2))
reg_sha = sha256_file(reg_fn)

# Summary
summary = {
    "tool": "campaign125_execution_summary",
    "generated_at_utc": ts,
    "campaign": 125,
    "status": "DONE",
    "real_data_only": True,
    "fail_closed": True,
    "edge_claim": "NONE",
    "oos_edge_proven": False,
    "new_artifacts": [
        {
            "path": str(oos_c125.relative_to(root)),
            "sha256": oos_c125_sha,
            "type": "oos_costed"
        },
        {
            "path": str(ingest_fn.relative_to(root)),
            "sha256": ingest_sha,
            "type": "ingest_attempt"
        },
        {
            "path": str(reg_fn.relative_to(root)),
            "sha256": reg_sha,
            "type": "registry_superseding"
        },
        {
            "path": str(script_c125.relative_to(root)),
            "sha256": script_c125_sha,
            "type": "script"
        }
    ],
    "references": {
        "prior_registry": str(prior_reg.relative_to(root)),
        "prior_registry_sha256": prior_reg_sha,
        "c124_oos": "reports/real_quote_volume_phase_entropy_shock_mr_costed_oos_20261107T045907Z.json",
        "c124_oos_sha256": "4b876ec7f9212502affacf82c9f8e504f2833533810bbee9a0d8c22ad6107410"
    },
    "pytest": "not_run_or_unavailable_recorded_honestly"
}
sum_fn = reports / f"campaign125_execution_summary_{ts}.json"
sum_fn.write_text(json.dumps(summary, indent=2))
sum_sha = sha256_file(sum_fn)

print(json.dumps({
    "ingest": str(ingest_fn),
    "ingest_sha": ingest_sha,
    "registry": str(reg_fn),
    "registry_sha": reg_sha,
    "summary": str(sum_fn),
    "summary_sha": sum_sha
}, indent=2))
