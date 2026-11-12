#!/usr/bin/env python3
"""Emit registry for campaign 271."""
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

root = Path(__file__).resolve().parents[1]
reports = root / "reports"

# Find the latest C271 OOS report
oos_files = list(reports.glob("real_quote_volume_rqa_rte_over_white_diag_line_length_skewness_about_mean_shock_mr_costed_oos_*.json"))
if not oos_files:
    raise SystemExit("No C271 OOS report found")
oos_path = max(oos_files, key=lambda p: p.stat().st_mtime)
print(f"Using OOS: {oos_path}")

with open(oos_path) as f:
    oos = json.load(f)

# Load prior registry (C270)
prior_registry = "reports/strategy_edge_registry_20261112T031436Z.json"
prior_path = root / prior_registry
with open(prior_path) as f:
    registry = json.load(f)

# Add C271 entry
entry = {
    "campaign": 271,
    "strategy_id": oos["strategy_id"],
    "family": "RQA WHITE_DIAG_LINE_LENGTH_SKEWNESS_ABOUT_MEAN shock on volume dynamics",
    "oos_path": str(oos_path.relative_to(root)),
    "oos_sha256": hashlib.sha256(oos_path.read_bytes()).hexdigest(),
    "script_path": "scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_skewness_about_mean_shock_mr_costed_oos.py",
    "script_sha256": hashlib.sha256((root / "scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_skewness_about_mean_shock_mr_costed_oos.py").read_bytes()).hexdigest(),
    "oos_edge_proven": oos["oos_edge_proven"],
    "edge_claim": oos["edge_claim"],
    "pre_stated_distinctness": oos["pre_stated_distinctness"],
    "distinct_from": [
        "WHITE_DIAG_LINE_LENGTH_COEFFICIENT_OF_VARIATION (C270)",
        "WHITE_DIAG_LINE_LENGTH_PEARSON_MODE_SKEW (C269)",
        "WHITE_DIAG_LINE_LENGTH_STANDARDIZED_MOMENT (C268)",
        "WHITE_DIAG_LINE_LENGTH_ROOT_MEAN_SQUARE_DEVIATION_FROM_MEDIAN (C267)",
        "WHITE_DIAG_LINE_LENGTH_RELATIVE_MEAN_ABSOLUTE_DIFFERENCE (C266)",
        "WHITE_DIAG_LINE_LENGTH_MAD_FROM_MEDIAN (C265)",
        "WHITE_DIAG_LINE_LENGTH_SKEWNESS (C230, 3rd central moment about the mean)",
        "WHITE_DIAG_LINE_LENGTH_KURTOSIS (C231, 4th central moment)",
        "C125-C269 prior RQA families",
    ],
    "ingest_path": f"reports/real_feed_ingest_attempt_{oos['generated_at_utc']}.json",
    "ingest_sha256": None,
}

# Find matching ingest attempt by timestamp
ingest_files = list(reports.glob(f"real_feed_ingest_attempt_{oos['generated_at_utc']}.json"))
if ingest_files:
    entry["ingest_sha256"] = hashlib.sha256(ingest_files[0].read_bytes()).hexdigest()

# Update registry
registry["c271"] = entry
registry["campaign_latest"] = 271
registry["generated_at_utc"] = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
registry["supersedes"] = prior_registry
registry["supersedes_sha256"] = oos["artifacts"]["prior_registry_sha256"]

out_path = reports / f"strategy_edge_registry_{registry['generated_at_utc']}.json"
out_path.write_text(json.dumps(registry, indent=2, default=str) + "\n")
print(f"Registry written: {out_path}")
print(f"SHA256: {hashlib.sha256(out_path.read_bytes()).hexdigest()}")
