#!/usr/bin/env python3
"""Emit registry for campaign 267."""
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

root = Path(__file__).resolve().parents[1]
reports = root / "reports"

# Find the latest C267 OOS report
oos_files = list(reports.glob("real_quote_volume_rqa_rte_over_white_diag_line_length_root_mean_square_deviation_from_median_shock_mr_costed_oos_*.json"))
if not oos_files:
    raise SystemExit("No C267 OOS report found")
oos_path = max(oos_files, key=lambda p: p.stat().st_mtime)
print(f"Using OOS: {oos_path}")

with open(oos_path) as f:
    oos = json.load(f)

# Load prior registry
prior_registry = oos["artifacts"]["prior_registry"]
prior_path = root / prior_registry
with open(prior_path) as f:
    registry = json.load(f)

# Add C267 entry
entry = {
    "campaign": 267,
    "strategy_id": oos["strategy_id"],
    "family": "RQA WHITE_DIAG_LINE_LENGTH_ROOT_MEAN_SQUARE_DEVIATION_FROM_MEDIAN shock on volume dynamics",
    "oos_path": str(oos_path.relative_to(root)),
    "oos_sha256": hashlib.sha256(oos_path.read_bytes()).hexdigest(),
    "script_path": "scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_root_mean_square_deviation_from_median_shock_mr_costed_oos.py",
    "script_sha256": hashlib.sha256((root / "scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_root_mean_square_deviation_from_median_shock_mr_costed_oos.py").read_bytes()).hexdigest(),
    "oos_edge_proven": oos["oos_edge_proven"],
    "edge_claim": oos["edge_claim"],
    "pre_stated_distinctness": oos["pre_stated_distinctness"],
    "distinct_from": [
        "WHITE_DIAG_LINE_LENGTH_MAD_FROM_MEDIAN (C265, median absolute deviation from median)",
        "WHITE_DIAG_LINE_LENGTH_MEAN_ABSOLUTE_DEVIATION (C254, mean absolute deviation from mean)",
        "WHITE_DIAG_LINE_LENGTH_RELATIVE_MEAN_ABSOLUTE_DIFFERENCE (C266, pairwise relative)",
        "WHITE_DIAG_LINE_LENGTH_QUARTILE_COEFFICIENT_OF_DISPERSION (C264, QCD)",
        "C125-C265 prior RQA families",
    ],
    "ingest_path": f"reports/real_feed_ingest_attempt_{oos['generated_at_utc']}.json",
    "ingest_sha256": None,  # will be filled after ingest attempt
}

# Update registry
registry[f"c267"] = entry
registry["campaign_latest"] = 267
registry["generated_at_utc"] = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
registry["supersedes"] = prior_registry
registry["supersedes_sha256"] = oos["artifacts"]["prior_registry_sha256"]

out_path = reports / f"strategy_edge_registry_{registry['generated_at_utc']}.json"
out_path.write_text(json.dumps(registry, indent=2, default=str) + "\n")
print(f"Registry written: {out_path}")
print(f"SHA256: {hashlib.sha256(out_path.read_bytes()).hexdigest()}")