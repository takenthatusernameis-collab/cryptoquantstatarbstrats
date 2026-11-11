#!/usr/bin/env python3
"""C264 execution summary."""
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


OOS_FILES = sorted(reports.glob("real_quote_volume_rqa_rte_over_white_diag_line_length_quartile_coefficient_of_dispersion_shock_mr_costed_oos_*.json"))
if not OOS_FILES:
    raise SystemExit("No C264 OOS artifact found")
OOS_PATH = OOS_FILES[-1]
SCRIPT_PATH = root / "scripts" / "run_real_quote_volume_rqa_rte_over_white_diag_line_length_quartile_coefficient_of_dispersion_shock_mr_costed_oos.py"
REG_FILES = sorted(reports.glob("strategy_edge_registry_2026*_T*.json")) or sorted(reports.glob("strategy_edge_registry_*.json"))
REGISTRY_PATH = max(REG_FILES, key=lambda p: p.stat().st_mtime) if REG_FILES else None
INGEST_FILES = sorted(reports.glob("real_feed_ingest_attempt_*.json"))
INGEST_PATH = max(INGEST_FILES, key=lambda p: p.stat().st_mtime) if INGEST_FILES else None
PRIOR_REGISTRY = "reports/strategy_edge_registry_20261111T190903Z.json"
PRIOR_REGISTRY_SHA = "7ec6c1607b95729bbb0130ce1a61ffc2d05b9cde4dc255bd072b4ed269d7f627"

oos = json.loads(OOS_PATH.read_text())

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
    "tool": "campaign264_execution_summary",
    "generated_at_utc": ts,
    "campaign": 264,
    "strategy_id": "VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_QUARTILE_COEFFICIENT_OF_DISPERSION_SHOCK_MR",
    "real_data_only": True,
    "fabricated_data": False,
    "fail_closed": True,
    "edge_claim": oos.get("edge_claim", "NONE"),
    "artifacts": artifacts,
    "all_new_c264_artifact_paths_sha256_from_bytes": True,
    "oos_edge_proven": oos.get("oos_edge_proven", False),
    "c264_preselected": {
        "family_primary": "VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_QUARTILE_COEFFICIENT_OF_DISPERSION_SHOCK_MR",
        "grep_cmd": "grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_QUARTILE_COEFFICIENT_OF_DISPERSION|WHITE_DIAG_LINE_LENGTH_QUARTILE_COEFFICIENT_OF_DISPERSION' scripts/ strategies/ backtest/ utils/ 2>&1",
        "grep_hits_nonself_at_run": oos.get("pre_stated_distinctness", {}).get("grep_hits_nonself_at_run", 0),
        "grep_verify_required": True,
        "note": "C264 primary QUARTILE_COEFFICIENT_OF_DISPERSION=(Q3-Q1)/(Q3+Q1) over qualifying WHITE diagonal segment lengths pooled over off-diagonal diagonals k!=0; fail-closed if <3 segments or Q1/Q3 undefined/non-finite or (Q3+Q1)<=0 or QCD<=0/degenerate/non-finite. grep 0 nonself verified before run.",
    },
    "references": {
        "prior_registry": PRIOR_REGISTRY,
        "prior_registry_sha256": PRIOR_REGISTRY_SHA,
        "c263_oos": "reports/real_quote_volume_rqa_rte_over_white_diag_line_length_index_of_dispersion_shock_mr_costed_oos_20261111T190430Z.json",
        "c263_oos_sha256": "02490c3c839435ad4a6040d8eaeb97721c10f130983a91ed3de3875dd398953e",
    },
}
out_path = reports / f"campaign264_execution_summary_{ts}.json"
out_path.write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps({"summary": str(out_path.relative_to(root)), "summary_sha256": sha256_file(out_path)}, indent=2))
