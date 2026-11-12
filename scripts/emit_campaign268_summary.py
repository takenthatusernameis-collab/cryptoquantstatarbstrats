#!/usr/bin/env python3
"""Emit summary for campaign 268."""
import json
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parents[1]
reports = root / "reports"

# Find the latest C268 OOS report
oos_files = list(reports.glob("real_quote_volume_rqa_rte_over_white_diag_line_length_standardized_moment_shock_mr_costed_oos_*.json"))
if not oos_files:
    raise SystemExit("No C268 OOS report found")
oos_path = max(oos_files, key=lambda p: p.stat().st_mtime)

with open(oos_path) as f:
    oos = json.load(f)

# Find registry
reg_files = list(reports.glob("strategy_edge_registry_*.json"))
reg_path = max(reg_files, key=lambda p: p.stat().st_mtime)
with open(reg_path) as f:
    registry = json.load(f)

# Find ingest attempt
ingest_files = list(reports.glob("real_feed_ingest_attempt_*.json"))
ingest_path = max(ingest_files, key=lambda p: p.stat().st_mtime)
with open(ingest_path) as f:
    ingest = json.load(f)

summary = {
    "campaign": 268,
    "strategy_id": oos["strategy_id"],
    "strategy_family": oos["strategy_family"],
    "generated_at_utc": oos["generated_at_utc"],
    "oos_edge_proven": oos["oos_edge_proven"],
    "edge_claim": oos["edge_claim"],
    "walk_forward": oos["walk_forward"],
    "cost_grid_bps": oos["cost_grid_bps"],
    "cross_asset_oos_net_sums": oos["cross_asset"]["oos_net_sums"],
    "any_exposure_oos": oos["any_exposure_oos"],
    "all_cost_slices_positive_oos_net_sum": oos["all_cost_slices_positive_oos_net_sum"],
    "all_cost_slices_beat_bh_mean_rule": oos["all_cost_slices_beat_bh_mean_rule"],
    "total_assets_tested": len([a for a in oos["per_asset"].values() if a.get("status") == "ok"]),
    "assets_insufficient": len([a for a in oos["per_asset"].values() if a.get("status") == "insufficient"]),
    "assets_feature_insufficient": len([a for a in oos["per_asset"].values() if a.get("status") == "feature_insufficient"]),
    "assets_no_splits": len([a for a in oos["per_asset"].values() if a.get("status") == "no_splits"]),
    "oos_report": str(oos_path.relative_to(root)),
    "oos_report_sha256": hashlib.sha256(oos_path.read_bytes()).hexdigest(),
    "registry": str(reg_path.relative_to(root)),
    "registry_sha256": hashlib.sha256(reg_path.read_bytes()).hexdigest(),
    "ingest_attempt": str(ingest_path.relative_to(root)),
    "ingest_attempt_sha256": hashlib.sha256(ingest_path.read_bytes()).hexdigest(),
    "script_path": "scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_standardized_moment_shock_mr_costed_oos.py",
    "script_sha256": hashlib.sha256((root / "scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_standardized_moment_shock_mr_costed_oos.py").read_bytes()).hexdigest(),
    "distinctness_grep_hits_nonself": oos["pre_stated_distinctness"]["grep_hits_nonself_at_run"],
    "prior_registry": oos["artifacts"]["prior_registry"],
    "prior_registry_sha256": oos["artifacts"]["prior_registry_sha256"],
    "edge_rule": oos["edge_rule"],
}

out_path = reports / f"campaign268_execution_summary_{oos['generated_at_utc']}.json"
out_path.write_text(json.dumps(summary, indent=2, default=str) + "\n")
print(f"Summary written: {out_path}")
print(f"SHA256: {hashlib.sha256(out_path.read_bytes()).hexdigest()}")
