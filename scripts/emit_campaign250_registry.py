#!/usr/bin/env python3
"""C250 strategy edge registry (superseding C249 registry).

Structurally consistent; includes prior registry + C250 artifact paths/SHAs/scripts.
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


OOS_PATH = reports / "real_quote_volume_rqa_rte_over_white_diag_line_length_yule_k_shock_mr_costed_oos_20261111T103421Z.json"
SCRIPT_PATH = root / "scripts" / "run_real_quote_volume_rqa_rte_over_white_diag_line_length_yule_k_shock_mr_costed_oos.py"
PRIOR_REGISTRY = "reports/strategy_edge_registry_20261110T170949Z.json"
PRIOR_REGISTRY_SHA = sha256_file(reports / "strategy_edge_registry_20261110T170949Z.json")

oos = json.loads(OOS_PATH.read_text())
_ingests = sorted(reports.glob("real_feed_ingest_attempt_*.json"))
INGEST_PATH = max(_ingests, key=lambda p: p.stat().st_mtime) if _ingests else None

c250_entry = {
    "campaign": 250,
    "strategy_id": "VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_YULE_K_SHOCK_MR",
    "family": "RQA RTE / WHITE_DIAG_LINE_LENGTH_YULE_K ratio shock on volume dynamics",
    "oos_path": str(OOS_PATH.relative_to(root)),
    "oos_sha256": sha256_file(OOS_PATH),
    "script_path": str(SCRIPT_PATH.relative_to(root)),
    "script_sha256": sha256_file(SCRIPT_PATH),
    "oos_edge_proven": oos.get("oos_edge_proven", False),
    "edge_claim": oos.get("edge_claim", "NONE"),
    "pre_stated_distinctness": oos.get("pre_stated_distinctness", {}),
}
if INGEST_PATH is not None:
    c250_entry["ingest_path"] = str(INGEST_PATH.relative_to(root))
    c250_entry["ingest_sha256"] = sha256_file(INGEST_PATH)
else:
    c250_entry["ingest_path"] = None
    c250_entry["ingest_sha256"] = None
    c250_entry["ingest_note"] = "C250 OOS script consumes cached spot+volume data only; no separate ingest artifact produced by this campaign."

out = {
    "tool": "strategy_edge_registry",
    "generated_at_utc": ts,
    "supersedes": PRIOR_REGISTRY,
    "supersedes_sha256": PRIOR_REGISTRY_SHA,
    "real_data_only": True,
    "fabricated_data": False,
    "fail_closed": True,
    "edge_claim": oos.get("edge_claim", "NONE"),
    "campaign_latest": 250,
    "c249": None,
    "c250": c250_entry,
    "artifact_index": [],
}
out_path = reports / f"strategy_edge_registry_{ts}.json"
out_path.write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps({"registry": str(out_path.relative_to(root)), "registry_sha256": sha256_file(out_path)}, indent=2))
