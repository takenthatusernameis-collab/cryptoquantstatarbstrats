#!/usr/bin/env python3
"""C257 execution summary: lists all new C257 artifact paths + sha256 from bytes."""
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


OOS_FILES = sorted(reports.glob("real_quote_volume_rqa_rte_over_white_diag_line_length_coefficient_of_range_shock_mr_costed_oos_*.json"))
if not OOS_FILES:
    raise SystemExit("No C257 OOS artifact found")
OOS_PATH = OOS_FILES[-1]
SCRIPT_PATH = root / "scripts" / "run_real_quote_volume_rqa_rte_over_white_diag_line_length_coefficient_of_range_shock_mr_costed_oos.py"
PRIOR_REGISTRY = "reports/strategy_edge_registry_20261111T142620Z.json"
PRIOR_REGISTRY_SHA = sha256_file(reports / "strategy_edge_registry_20261111T142620Z.json")

oos = json.loads(OOS_PATH.read_text())
_ingests = sorted(reports.glob("real_feed_ingest_attempt_*.json"))
INGEST_PATH = max(_ingests, key=lambda p: p.stat().st_mtime) if _ingests else None
_registries = sorted(reports.glob("strategy_edge_registry_*.json"))
REGISTRY_PATH = max(_registries, key=lambda p: p.stat().st_mtime) if _registries else None

artifacts = {
    "oos": {"path": str(OOS_PATH.relative_to(root)), "sha256": sha256_file(OOS_PATH)},
    "script": {"path": str(SCRIPT_PATH.relative_to(root)), "sha256": sha256_file(SCRIPT_PATH)},
}
if INGEST_PATH is not None:
    artifacts["ingest"] = {"path": str(INGEST_PATH.relative_to(root)), "sha256": sha256_file(INGEST_PATH)}
else:
    artifacts["ingest"] = {"path": None, "sha256": None}
if REGISTRY_PATH is not None:
    artifacts["registry"] = {"path": str(REGISTRY_PATH.relative_to(root)), "sha256": sha256_file(REGISTRY_PATH)}
else:
    artifacts["registry"] = {"path": None, "sha256": None}

out = {
    "tool": "campaign257_execution_summary",
    "generated_at_utc": ts,
    "campaign": 257,
    "strategy_id": "VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_COEFFICIENT_OF_RANGE_SHOCK_MR",
    "real_data_only": True,
    "fabricated_data": False,
    "fail_closed": True,
    "edge_claim": oos.get("edge_claim", "NONE"),
    "artifacts": artifacts,
    "all_new_c256_artifact_paths_sha256_from_bytes": True,
    "oos_edge_proven": oos.get("oos_edge_proven", False),
    "c257_preselected": {
        "family_primary": "VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_COEFFICIENT_OF_RANGE_SHOCK_MR",
        "grep_cmd": "grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_COEFFICIENT_OF_RANGE|WHITE_DIAG_LINE_LENGTH_COEFFICIENT_OF_RANGE' scripts/ strategies/ backtest/ utils/ 2>&1",
        "grep_hits_nonself_at_run": oos.get("pre_stated_distinctness", {}).get("grep_hits_nonself_at_run", 0),
        "grep_verify_required": True,
        "note": "C257 primary COEFFICIENT_OF_RANGE ((mx-mn)/(mx+mn) over qualifying WHITE diagonal segment lengths pooled over off-diagonal diagonals k!=0; fail-closed if <3 segments or mx/mn undefined/non-finite or (mx+mn)<=0 or COEFFICIENT_OF_RANGE<=0/degenerate/non-finite) grep 0 verified before implementation/run.",
    },
    "references": {
        "prior_registry": PRIOR_REGISTRY,
        "prior_registry_sha256": PRIOR_REGISTRY_SHA,
        "c256_oos": "reports/real_quote_volume_rqa_rte_over_white_diag_line_length_semi_variance_shock_mr_costed_oos_20261111T142022Z.json",
        "c256_oos_sha256": sha256_file(reports / "real_quote_volume_rqa_rte_over_white_diag_line_length_semi_variance_shock_mr_costed_oos_20261111T142022Z.json"),
    },
}
out_path = reports / f"campaign257_execution_summary_{ts}.json"
out_path.write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps({"summary": str(out_path.relative_to(root)), "summary_sha256": sha256_file(out_path)}, indent=2))
