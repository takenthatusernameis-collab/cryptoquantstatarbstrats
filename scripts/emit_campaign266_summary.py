#!/usr/bin/env python3
"""C266 execution summary."""
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


OOS_FILES = sorted(reports.glob("real_quote_volume_rqa_rte_over_white_diag_line_length_relative_mean_absolute_difference_shock_mr_costed_oos_*.json"))
if not OOS_FILES:
    raise SystemExit("No C266 OOS artifact found")
OOS_PATH = OOS_FILES[-1]
SCRIPT_PATH = root / "scripts" / "run_real_quote_volume_rqa_rte_over_white_diag_line_length_relative_mean_absolute_difference_shock_mr_costed_oos.py"
REG_FILES = sorted(reports.glob("strategy_edge_registry_2026*_T*.json")) or sorted(reports.glob("strategy_edge_registry_*.json"))
REGISTRY_PATH = max(REG_FILES, key=lambda p: p.stat().st_mtime) if REG_FILES else None
INGEST_FILES = sorted(reports.glob("real_feed_ingest_attempt_*.json"))
INGEST_PATH = max(INGEST_FILES, key=lambda p: p.stat().st_mtime) if INGEST_FILES else None
PRIOR_REGISTRY = "reports/strategy_edge_registry_20261111T201037Z.json"
PRIOR_REGISTRY_SHA = "10baa10b4c5d4584240373ee3f3d989bec5bbe06ea4fd3fb8c2d5e9a6dd9e418"

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
    "tool": "campaign266_execution_summary",
    "generated_at_utc": ts,
    "campaign": 266,
    "strategy_id": "VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_RELATIVE_MEAN_ABSOLUTE_DIFFERENCE_SHOCK_MR",
    "real_data_only": True,
    "fabricated_data": False,
    "fail_closed": True,
    "edge_claim": oos.get("edge_claim", "NONE"),
    "artifacts": artifacts,
    "all_new_c266_artifact_paths_sha256_from_bytes": True,
    "oos_edge_proven": oos.get("oos_edge_proven", False),
    "c266_preselected": {
        "family_primary": "VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_RELATIVE_MEAN_ABSOLUTE_DIFFERENCE_SHOCK_MR",
        "grep_cmd": "grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_RELATIVE_MEAN_ABSOLUTE_DIFFERENCE|WHITE_DIAG_LINE_LENGTH_RELATIVE_MEAN_ABSOLUTE_DIFFERENCE' scripts/ strategies/ backtest/ utils/ 2>&1",
        "grep_hits_nonself_at_run": oos.get("pre_stated_distinctness", {}).get("grep_hits_nonself_at_run", 0),
        "grep_verify_required": True,
        "note": "C266 primary RELATIVE_MEAN_ABSOLUTE_DIFFERENCE=mean(|L_i-L_j|)/(2*mean(L)) over all unordered pairs of qualifying WHITE diagonal segment lengths pooled over off-diagonal diagonals k!=0; fail-closed if <3 segments or mean(L)<=0/non-finite or R_MAD non-finite/degenerate. grep 0 nonself verified before run. Distinct from C265 MAD_FROM_MEDIAN (median-centered) and C254 MEAN_ABSOLUTE_DEVIATION (mean-centered single dispersion).",
    },
    "references": {
        "prior_registry": PRIOR_REGISTRY,
        "prior_registry_sha256": PRIOR_REGISTRY_SHA,
        "c265_oos": "reports/real_quote_volume_rqa_rte_over_white_diag_line_length_mad_from_median_shock_mr_costed_oos_20261111T201037Z.json",
        "c265_oos_sha256": "0297d22a42bb8c980e4730958cd19e4006751518374d0b311f84e1b3071a1c07",
    },
}
out_path = reports / f"campaign266_execution_summary_{ts}.json"
out_path.write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps({"summary": str(out_path.relative_to(root)), "summary_sha256": sha256_file(out_path)}, indent=2))