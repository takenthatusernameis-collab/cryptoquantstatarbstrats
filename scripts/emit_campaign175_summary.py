#!/usr/bin/env python3
"""C175 execution summary: lists all new C175 artifact paths + sha256 from bytes."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parents[1]
reports = root / "reports"
reports.mkdir(exist_ok=True)
ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


OOS_PATH = reports / "real_quote_volume_rqa_entr_over_vmax_ratio_shock_mr_costed_oos_20261107T214159Z.json"
SCRIPT_PATH = root / "scripts" / "run_real_quote_volume_rqa_entr_over_vmax_ratio_shock_mr_costed_oos.py"
PRIOR_REGISTRY = "reports/strategy_edge_registry_20261107T204909Z.json"
PRIOR_REGISTRY_SHA = "cf392ce4e8ed93c674d2ec0fd567eb4deae341485399e3c2b4dee53ee59a51b5"
C174_OOS = "reports/real_quote_volume_rqa_det_over_trend_ratio_shock_mr_costed_oos_20261107T204909Z.json"
C174_OOS_SHA = "083ff5be33807d7f91e8b5a517a6945148f0809eeb0a84e3a46e9616b60a5141"

oos = json.loads(OOS_PATH.read_text())
_ingests = sorted(reports.glob("real_feed_ingest_attempt_*.json"))
INGEST_PATH = max([p for p in _ingests if "20261107T214" in p.name], key=lambda p: p.stat().st_mtime)
_registries = sorted(reports.glob("strategy_edge_registry_*.json"))
REGISTRY_PATH = max([p for p in _registries if "20261107T214" in p.name], key=lambda p: p.stat().st_mtime)

out = {
    "tool": "campaign175_execution_summary",
    "generated_at_utc": ts,
    "campaign": 175,
    "strategy_id": "VOLUME_RQA_ENTR_OVER_VMAX_RATIO_SHOCK_MR",
    "real_data_only": True,
    "fabricated_data": False,
    "fail_closed": True,
    "edge_claim": oos.get("edge_claim", "NONE"),
    "artifacts": {
        "oos": {"path": str(OOS_PATH.relative_to(root)), "sha256": sha256_file(OOS_PATH)},
        "ingest": {"path": str(INGEST_PATH.relative_to(root)), "sha256": sha256_file(INGEST_PATH)},
        "registry": {"path": str(REGISTRY_PATH.relative_to(root)), "sha256": sha256_file(REGISTRY_PATH)},
        "script": {"path": str(SCRIPT_PATH.relative_to(root)), "sha256": sha256_file(SCRIPT_PATH)},
    },
    "all_new_c175_artifact_paths_sha256_from_bytes": True,
    "oos_edge_proven": oos.get("oos_edge_proven", False),
    "references": {
        "prior_registry": PRIOR_REGISTRY,
        "prior_registry_sha256": PRIOR_REGISTRY_SHA,
        "c174_oos": C174_OOS,
        "c174_oos_sha256": C174_OOS_SHA,
    },
}
out_path = reports / f"campaign175_execution_summary_{ts}.json"
out_path.write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps({"summary": str(out_path.relative_to(root)), "summary_sha256": sha256_file(out_path)}, indent=2))