#!/usr/bin/env python3
"""C175 strategy edge registry (superseding C174 registry).

Structurally consistent; includes prior registry + C175 artifact paths/SHAs/scripts.
edge_claim:"NONE" unless rule holds.
"""
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
# newest campaign-175 ingest artifact (produced by run_real_feed_ingest_attempt_175.py)
_ingests = sorted(reports.glob("real_feed_ingest_attempt_*.json"))
INGEST_PATH = max([p for p in _ingests if "20261107T214" in p.name], key=lambda p: p.stat().st_mtime)
SCRIPT_PATH = root / "scripts" / "run_real_quote_volume_rqa_entr_over_vmax_ratio_shock_mr_costed_oos.py"
PRIOR_REGISTRY = "reports/strategy_edge_registry_20261107T204909Z.json"
PRIOR_REGISTRY_SHA = "cf392ce4e8ed93c674d2ec0fd567eb4deae341485399e3c2b4dee53ee59a51b5"

oos = json.loads(OOS_PATH.read_text())

out = {
    "tool": "strategy_edge_registry",
    "generated_at_utc": ts,
    "supersedes": PRIOR_REGISTRY,
    "supersedes_sha256": PRIOR_REGISTRY_SHA,
    "real_data_only": True,
    "fabricated_data": False,
    "fail_closed": True,
    "edge_claim": oos.get("edge_claim", "NONE"),
    "campaign_latest": 175,
    "c174": None,
    "c175": {
        "campaign": 175,
        "strategy_id": "VOLUME_RQA_ENTR_OVER_VMAX_RATIO_SHOCK_MR",
        "family": "RQA ENTR/V_max ratio shock on volume dynamics",
        "oos_path": str(OOS_PATH.relative_to(root)),
        "oos_sha256": sha256_file(OOS_PATH),
        "ingest_path": str(INGEST_PATH.relative_to(root)),
        "ingest_sha256": sha256_file(INGEST_PATH),
        "script_path": str(SCRIPT_PATH.relative_to(root)),
        "script_sha256": sha256_file(SCRIPT_PATH),
        "oos_edge_proven": oos.get("oos_edge_proven", False),
        "edge_claim": oos.get("edge_claim", "NONE"),
        "pre_stated_distinctness": oos.get("pre_stated_distinctness", {}),
    },
    "artifact_index": [],
}
out_path = reports / f"strategy_edge_registry_{ts}.json"
out_path.write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps({"registry": str(out_path.relative_to(root)), "registry_sha256": sha256_file(out_path)}, indent=2))