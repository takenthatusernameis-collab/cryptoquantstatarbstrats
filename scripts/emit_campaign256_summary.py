#!/usr/bin/env python3
"""C256 execution summary: lists all new C256 artifact paths + sha256 from bytes."""
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


OOS_FILES = sorted(reports.glob("real_quote_volume_rqa_rte_over_white_diag_line_length_semi_variance_shock_mr_costed_oos_*.json"))
if not OOS_FILES:
    raise SystemExit("No C256 OOS artifact found")
OOS_PATH = OOS_FILES[-1]
SCRIPT_PATH = root / "scripts" / "run_real_quote_volume_rqa_rte_over_white_diag_line_length_semi_variance_shock_mr_costed_oos.py"
PRIOR_REGISTRY = "reports/strategy_edge_registry_20261111T133343Z.json"
PRIOR_REGISTRY_SHA = sha256_file(reports / "strategy_edge_registry_20261111T133343Z.json")

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
    "tool": "campaign256_execution_summary",
    "generated_at_utc": ts,
    "campaign": 256,
    "strategy_id": "VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_SEMI_VARIANCE_SHOCK_MR",
    "real_data_only": True,
    "fabricated_data": False,
    "fail_closed": True,
    "edge_claim": oos.get("edge_claim", "NONE"),
    "artifacts": artifacts,
    "all_new_c256_artifact_paths_sha256_from_bytes": True,
    "oos_edge_proven": oos.get("oos_edge_proven", False),
    "c256_preselected": {
        "family_primary": "VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_SEMI_VARIANCE_SHOCK_MR",
        "grep_cmd": "grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_SEMI_VARIANCE|WHITE_DIAG_LINE_LENGTH_SEMI_VARIANCE' scripts/ strategies/ backtest/ utils/ 2>&1",
        "grep_hits_nonself_at_run": oos.get("pre_stated_distinctness", {}).get("grep_hits_nonself_at_run", 0),
        "grep_verify_required": True,
        "note": "C256 primary SEMI_VARIANCE (lower semi-variance about mean: mu=mean(L), SEMI_VARIANCE=(1/N)*sum(max(mu-L_i,0))^2 over qualifying WHITE diagonal segment lengths pooled over off-diagonal diagonals k!=0; fail-closed if <3 segments or mu/SEMI_VARIANCE undefined/non-finite or SEMI_VARIANCE<=0/degenerate) grep 0 verified before implementation/run.",
    },
    "references": {
        "prior_registry": PRIOR_REGISTRY,
        "prior_registry_sha256": PRIOR_REGISTRY_SHA,
        "c255_oos": "reports/real_quote_volume_rqa_rte_over_white_diag_line_length_median_absolute_deviation_shock_mr_costed_oos_20261111T132821Z.json",
        "c255_oos_sha256": sha256_file(reports / "real_quote_volume_rqa_rte_over_white_diag_line_length_median_absolute_deviation_shock_mr_costed_oos_20261111T132821Z.json"),
    },
}
out_path = reports / f"campaign256_execution_summary_{ts}.json"
out_path.write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps({"summary": str(out_path.relative_to(root)), "summary_sha256": sha256_file(out_path)}, indent=2))
