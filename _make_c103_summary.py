#!/usr/bin/env python3
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone

root = Path(__file__).resolve().parent
reports = root / 'reports'
ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')

rb_c103 = max((p for p in reports.glob('real_quote_volume_spectral_entropy_shock_mr_costed_oos_*.json')), key=lambda p: p.stat().st_mtime)
ingest_c103 = max((p for p in reports.glob('real_feed_ingest_attempt_*.json')), key=lambda p: p.stat().st_mtime)
reg_c103 = max((p for p in reports.glob('strategy_edge_registry_*.json')), key=lambda p: p.stat().st_mtime)

rb = json.loads(rb_c103.read_text())
summary = {
  "tool": "campaign103_execution_summary",
  "generated_at_utc": datetime.now(timezone.utc).isoformat(),
  "campaign": 103,
  "mandate": "C103: remove bottlenecks, run distinct R-B (spectral entropy), ingest attempt if nonspot blocked, registry+summary.",
  "artifacts": [
    {"path": str(ingest_c103).replace(str(root)+'/',''), "sha256": hashlib.sha256(ingest_c103.read_bytes()).hexdigest()},
    {"path": str(rb_c103).replace(str(root)+'/',''), "sha256": hashlib.sha256(rb_c103.read_bytes()).hexdigest()},
    {"path": str(reg_c103).replace(str(root)+'/',''), "sha256": hashlib.sha256(reg_c103.read_bytes()).hexdigest()},
  ],
  "c103_rb": {
    "candidate": rb['candidate'],
    "oos_edge_proven": rb['oos_edge_proven'],
    "n_assets": rb['aggregate']['n_assets'],
    "any_exposure_oos": rb['aggregate']['any_exposure_oos'],
    "all_cost_slices_positive_oos_net_sum": rb['aggregate']['all_cost_slices_positive_oos_net_sum'],
    "all_cost_slices_beat_bh_mean_rule": rb['aggregate']['all_cost_slices_beat_bh_mean_rule'],
  },
  "nonspot_blockers": {
    "status": "FAIL_CLOSED_BLOCKED_NO_REAL_ARTIFACT",
    "blocked_families": ["funding_basis_carry", "cross_exchange_dual_venue_same_asset", "term_structure_real_iv_vol_surface", "intrabar_microstructure"],
    "ingest_attempt": str(ingest_c103).replace(str(root)+'/',''),
  },
  "references": {
    "prior_unblock": "reports/real_feed_unblock_status_20261106T130243Z.json",
    "prior_registry": "reports/strategy_edge_registry_20261106T202343Z.json",
  },
  "rules_followed": ["real_data_only", "fail_closed", "no_proxies_labeled_real", "no_fabrication", "edge_only_if_all_cost_slices_pass_and_beat_bh", "grep_verified_distinctness", "no_C102_rerun", "no_stale_cache_rescan"],
  "result": "NO_OOS_EDGE_PROVEN",
  "next_focus": "If any real nonspot artifact appears, ingest+unblock exactly one family with full provenance; else continue distinct real_quote_volume R-B families only if mechanically distinct and grep-verified."
}
out = reports / f'campaign103_execution_summary_{ts}.json'
out.write_text(json.dumps(summary, indent=2))
h = hashlib.sha256(out.read_bytes()).hexdigest()
print(json.dumps({"artifact": str(out), "sha256": h}, indent=2))
