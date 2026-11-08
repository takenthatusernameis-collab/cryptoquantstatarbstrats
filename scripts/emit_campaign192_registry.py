#!/usr/bin/env python3
"""C192 strategy edge registry (superseding C191 registry).

Structurally consistent; includes prior registry + C192 artifact paths/SHAs/scripts.
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


OOS_PATH = reports / "real_quote_volume_rqa_lavg_over_tt_ratio_shock_mr_costed_oos_20261108T015314Z.json"
_ingests = sorted(reports.glob("real_feed_ingest_attempt_*.json"))
INGEST_PATH = max([p for p in _ingests if "20261108T015" in p.name], key=lambda p: p.stat().st_mtime)
SCRIPT_PATH = root / "scripts" / "run_real_quote_volume_rqa_lavg_over_tt_ratio_shock_mr_costed_oos.py"
PRIOR_REGISTRY = "reports/strategy_edge_registry_20261108T014412Z.json"
PRIOR_REGISTRY_SHA = "7d2e0861e67726b03924550d7be29a68154010d79d3c6c2fa1177077edc848e0"

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
    "campaign_latest": 192,
    "c191": None,
    "c192": {
        "campaign": 192,
        "strategy_id": "VOLUME_RQA_LAVG_OVER_TT_RATIO_SHOCK_MR",
        "family": "RQA LAVG/TT ratio shock on volume dynamics",
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
