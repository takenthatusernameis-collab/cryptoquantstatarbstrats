#!/usr/bin/env python3
"""Build C273 promotion-ready evidence package from saved artifacts only."""
from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parents[1]
reports = root / 'reports'
ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')

ARTS = [
    ("oos", reports/"real_quote_volume_rqa_rte_over_white_diag_line_length_percentile_spread_shock_mr_costed_oos_20261112T050947Z.json", "1e4fd5983d29eb027336e77b2b3a5e7bda6fa6180494f0d836e5584cc298e1bf"),
    ("script", root/"scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_percentile_spread_shock_mr_costed_oos.py", "4d91581133c6ca5a8613c644f137f2c24bf5fefa0d1086d2d735d85d813a117e"),
    ("ingest", reports/"real_feed_ingest_attempt_20261112T051504Z.json", "dd704efab8d6c3650e5c872f0b8b3462185e960b136382ea260e139370d70446"),
    ("registry", reports/"strategy_edge_registry_20261112T051504Z.json", "7fb2ceeaccbb2c8499e5d8203479c7c9c309f41acd57ccc2c5e5685308b7c6b6"),
    ("summary", reports/"campaign273_execution_summary_20261112T051504Z.json", "d2694387c152b6659a041dd946fda79de415d9d1747bac447418c090cae153dd"),
    ("verification_script", root/"scripts/verify_c273_percentile_spread_edge.py", None),
    ("verification", reports/"campaign273_verification_20261112T051659Z.json", "42b3341d04e6c141fde5e0b88a8a2444a0b2c4a9270c56ce66149d21ca02c229"),
    ("robustness", reports/"campaign273_robustness_dossier_20261112T051659Z.json", "f7f51f9d84fe0f42207cfffe77e26e552ff8c10636017889fed706c029e716e6"),
    ("split_script", root/"scripts/run_c273_percentile_spread_split_decomposition.py", None),
    ("split_decomposition", reports/"campaign273_split_decomposition_20261112T052106Z.json", "2b4da1e685cee4eb8033e37d6a2844ba9639b7b3ba69b92c50ef7ea4a95a707d"),
    ("sensitivity_script", root/"scripts/run_c273_percentile_spread_param_sensitivity.py", "73832091f61282a3e1d2199284ba5af3fd79d1df66a1a512e9ea65a2c2252d98"),
    ("sensitivity", reports/"campaign273_param_sensitivity_20261112T052846Z.json", "15e4bf307b373c9c57a533dc69232d19855933ce8b7956d84e90b9f5d0e96b9d"),
]
EDGE_RULE = "oos_edge_proven=true IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. WF 720/168/168, cost grid [[0,0],[5,5],[10,10],[20,20],[40,40]], B&H same OOS windows."

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

manifest = []
hash_ok = True
for name, p, expected in ARTS:
    exists = p.exists()
    computed = sha(p) if exists else None
    ok = exists and (expected is None or computed == expected)
    if not ok:
        hash_ok = False
    manifest.append({"name": name, "path": str(p.relative_to(root)) if p.is_relative_to(root) else str(p), "exists": exists, "sha256": computed, "expected_sha256": expected, "hash_match_or_unpinned": ok})

oos = json.loads((reports/"real_quote_volume_rqa_rte_over_white_diag_line_length_percentile_spread_shock_mr_costed_oos_20261112T050947Z.json").read_text())
ver = json.loads((reports/"campaign273_verification_20261112T051659Z.json").read_text())
rob = json.loads((reports/"campaign273_robustness_dossier_20261112T051659Z.json").read_text())
split = json.loads((reports/"campaign273_split_decomposition_20261112T052106Z.json").read_text())
sens = json.loads((reports/"campaign273_param_sensitivity_20261112T052846Z.json").read_text())

fails = [r for r in sens['grid_results'] if not r['oos_edge_proven']]
baseline = next((r for r in sens['grid_results'] if r.get('is_baseline')), None)

risks = [
    "Fragility flags from robustness dossier: some_assets_nonpositive_at_fee0; not_all_assets_positive_in_every_cost_slice (cross-asset edge positive but not uniform across all assets/cost slices).",
    "Split stability: fee0 cross-asset positive splits 16/24 (66.67%), 8/24 negative splits (min -12.116630665422184, max 27.10148575154885, mean 3.361829935125678); assets positive net at fee0 9/11.",
    f"Parameter sensitivity: 21/27 combos edge-positive overall, but 6/27 fail edge rule — all failures at W_RR=192 (ENTRY_Z 1.25 with EXIT_Z 0.25/0.5/0.75 and ENTRY_Z 1.5 with EXIT_Z 0.25/0.5/0.75) due to fee40/high-cost negativity and BH-beat failure (e.g. fee40 nets -23.068169522391372 and -44.7833781134085). Baseline W_RR=168/ENTRY_Z=1.5/EXIT_Z=0.5 reproduced.",
    "Evidence is real-cached-data OOS on fixed WF/cost framework; no live/refetched/synthetic validation and no out-of-sample beyond cached history.",
]

readiness = "READY_FOR_REVIEW"
reasons = []
if not hash_ok:
    readiness = "NOT_READY"; reasons.append("One or more required artifact hashes missing/mismatched.")
if not ver.get('verification_passed'):
    readiness = "NOT_READY"; reasons.append("Deterministic verification did not pass.")
if not split.get('replication_matches_c273'):
    readiness = "NOT_READY"; reasons.append("Split decomposition replication did not match C273.")
if sens.get('edge_positive_share', 0) < 0.7:
    readiness = "NOT_READY"; reasons.append("Parameter sensitivity share < 70%.")
if not reasons:
    reasons.append("All required artifacts present with matching/pinned hashes (where expected), verification passed, replication matched, and parameter sensitivity shows robust neighborhood (21/27 = 77.78%) with baseline reproduced. Risks/non-uniformities and W_RR=192 failures are explicitly documented for reviewer judgment.")

pkg = {
    "generated_at_utc": ts,
    "campaign": 273,
    "strategy_id": oos.get('strategy_id'),
    "strategy_family": oos.get('strategy_family'),
    "edge_claim": oos.get('edge_claim'),
    "oos_edge_proven": oos.get('oos_edge_proven'),
    "edge_rule": EDGE_RULE,
    "edge_rule_compliance": {
        "oos_edge_proven": oos.get('oos_edge_proven'),
        "any_exposure_oos": oos.get('any_exposure_oos'),
        "all_cost_slices_positive_oos_net_sum": oos.get('all_cost_slices_positive_oos_net_sum'),
        "all_cost_slices_beat_bh_mean_rule": oos.get('all_cost_slices_beat_bh_mean_rule'),
        "compliant_with_saved_flags": bool(oos.get('oos_edge_proven') and oos.get('any_exposure_oos') and oos.get('all_cost_slices_positive_oos_net_sum') and oos.get('all_cost_slices_beat_bh_mean_rule')),
    },
    "baseline_metrics": {
        "walk_forward": oos.get('walk_forward'),
        "cost_grid_bps": oos.get('cost_grid_bps'),
        "cross_asset_oos_net_sums": oos.get('cross_asset',{}).get('oos_net_sums'),
        "distinctness_grep_hits_nonself_at_run": oos.get('pre_stated_distinctness',{}).get('grep_hits_nonself_at_run'),
    },
    "verification": {
        "verification_passed": ver.get('verification_passed'),
        "artifact": "reports/campaign273_verification_20261112T051659Z.json",
        "sha256": "42b3341d04e6c141fde5e0b88a8a2444a0b2c4a9270c56ce66149d21ca02c229",
    },
    "robustness_dossier": {
        "assessment": rob.get('assessment'),
        "fragility_flags": rob.get('fragility_flags'),
        "artifact": "reports/campaign273_robustness_dossier_20261112T051659Z.json",
        "sha256": "f7f51f9d84fe0f42207cfffe77e26e552ff8c10636017889fed706c029e716e6",
    },
    "split_stability": {
        "replication_matches_c273": split.get('replication_matches_c273'),
        "replication_diffs_recomputed_minus_reported": split.get('replication_diffs_recomputed_minus_reported'),
        "n_splits_per_asset": split.get('n_splits_per_asset'),
        "cross_asset_split_stats_fee0": split.get('cross_asset_split_stats',{}).get('fee0_slip0'),
        "stability_assessment": split.get('stability_assessment'),
        "artifact": "reports/campaign273_split_decomposition_20261112T052106Z.json",
        "sha256": "2b4da1e685cee4eb8033e37d6a2844ba9639b7b3ba69b92c50ef7ea4a95a707d",
    },
    "parameter_sensitivity": {
        "sensitivity_assessment": sens.get('sensitivity_assessment'),
        "total_combos": sens.get('total_combos'),
        "edge_positive_combos": sens.get('edge_positive_combos'),
        "edge_positive_share": sens.get('edge_positive_share'),
        "combos_all_cost_slices_positive": sens.get('combos_all_cost_slices_positive'),
        "baseline_reproduced_in_grid": sens.get('baseline_reproduced_in_grid'),
        "grid_spec": sens.get('grid_spec'),
        "failing_combos_count": len(fails),
        "failing_combos_summary": [{"params": r.get('params'), "fee40_slip40": r.get('cross_asset_oos_net_sums',{}).get('fee40_slip40'), "all_cost_slices_positive_oos_net_sum": r.get('all_cost_slices_positive_oos_net_sum'), "all_cost_slices_beat_bh_mean_rule": r.get('all_cost_slices_beat_bh_mean_rule')} for r in fails],
        "artifact": "reports/campaign273_param_sensitivity_20261112T052846Z.json",
        "sha256": "15e4bf307b373c9c57a533dc69232d19855933ce8b7956d84e90b9f5d0e96b9d",
    },
    "artifact_manifest": manifest,
    "risks_and_caveats": risks,
    "promotion_readiness": readiness,
    "promotion_readiness_reasons": reasons,
    "provenance": {"real_data_only": True, "fabricated_data": False, "network_refetch": False, "basis": "saved C273 artifacts on cached real data only"},
    "builder_script": str(Path(__file__).relative_to(root)),
}

json_path = reports/f"campaign273_promotion_evidence_package_{ts}.json"
md_path = reports/f"campaign273_promotion_evidence_package_{ts}.md"

md = []
md.append(f"# C273 Promotion Evidence Package ({ts})")
md.append("")
md.append(f"- Strategy: `{pkg['strategy_id']}`")
md.append(f"- Edge claim: **{pkg['edge_claim']}** | `oos_edge_proven={pkg['oos_edge_proven']}` | Readiness: **{pkg['promotion_readiness']}**")
md.append(f"- Edge rule: {EDGE_RULE}")
md.append("")
md.append("## Baseline (real cached data, WF 720/168/168, costs [[0,0],[5,5],[10,10],[20,20],[40,40]])")
md.append(f"- Cross-asset OOS net sums: {json.dumps(pkg['baseline_metrics']['cross_asset_oos_net_sums'])}")
md.append(f"- Distinctness grep hits (non-self): {pkg['baseline_metrics']['distinctness_grep_hits_nonself_at_run']}")
md.append(f"- Compliance flags: {json.dumps(pkg['edge_rule_compliance'])}")
md.append("")
md.append("## Verification / Replication")
md.append(f"- Deterministic verification passed: **{pkg['verification']['verification_passed']}** (`{pkg['verification']['artifact']}`, sha256 `{pkg['verification']['sha256']}`)")
md.append(f"- Split-decomposition replication matches C273: **{pkg['split_stability']['replication_matches_c273']}** (diffs: {json.dumps(pkg['split_stability']['replication_diffs_recomputed_minus_reported'])}, `{pkg['split_stability']['artifact']}`, sha256 `{pkg['split_stability']['sha256']}`)")
md.append("")
md.append("## Stability / Sensitivity")
md.append(f"- Robustness dossier: {pkg['robustness_dossier']['assessment']} | flags: {json.dumps(pkg['robustness_dossier']['fragility_flags'])}")
ss = pkg['split_stability']['stability_assessment'] or {}
md.append(f"- Split stats (fee0): positive {ss.get('fee0_positive_splits')}/{ss.get('fee0_total_splits')} ({ss.get('fee0_positive_split_share')}), assets positive net fee0 {ss.get('assets_positive_net_fee0')}/{ss.get('assets_total_ok')}, cross-asset positive all cost slices recomputed={ss.get('cross_asset_positive_all_cost_slices_recomputed')}")
ps = pkg['parameter_sensitivity']
md.append(f"- Parameter sensitivity: **{ps['sensitivity_assessment']}** — edge-positive {ps['edge_positive_combos']}/{ps['total_combos']} ({ps['edge_positive_share']}), all-cost-positive {ps['combos_all_cost_slices_positive']}/{ps['total_combos']}, baseline reproduced={ps['baseline_reproduced_in_grid']}")
md.append(f"- Failing combos ({ps['failing_combos_count']}), all at W_RR=192: {json.dumps(ps['failing_combos_summary'])}")
md.append("")
md.append("## Risks and Caveats")
for r in risks:
    md.append(f"- {r}")
md.append("")
md.append("## Artifact Manifest (SHA256 from bytes)")
for m in manifest:
    md.append(f"- `{m['name']}`: `{m['path']}` — sha256 `{m['sha256']}` (expected `{m['expected_sha256']}`, ok={m['hash_match_or_unpinned']})")
md.append("")
md.append("## Promotion Readiness")
md.append(f"- **{pkg['promotion_readiness']}**")
for r in reasons:
    md.append(f"- {r}")
md.append("")
md.append("## Reproduction (real cached data only, no refetch)")
md.append("- Core run: `python3 scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_percentile_spread_shock_mr_costed_oos.py`")
md.append("- Verification: `python3 scripts/verify_c273_percentile_spread_edge.py`")
md.append("- Split decomposition: `python3 scripts/run_c273_percentile_spread_split_decomposition.py`")
md.append("- Param sensitivity: `python3 scripts/run_c273_percentile_spread_param_sensitivity.py`")
md.append("- Package build: `python3 scripts/build_c273_promotion_evidence_package.py`")

md_text = "\n".join(md) + "\n"
json_path.write_text(json.dumps(pkg, indent=2) + "\n")
md_path.write_text(md_text)

# append self-hashes into json by rewriting
pkg['package_artifacts'] = {
    'json': {"path": str(json_path.relative_to(root)), "sha256": sha(json_path)},
    'md': {"path": str(md_path.relative_to(root)), "sha256": sha(md_path)},
    'builder_script_sha256': sha(Path(__file__)),
}
# include builder in manifest view
pkg['artifact_manifest'].append({"name": "builder_script", "path": str(Path(__file__).relative_to(root)), "exists": True, "sha256": sha(Path(__file__)), "expected_sha256": None, "hash_match_or_unpinned": True})
json_path.write_text(json.dumps(pkg, indent=2) + "\n")

print(json.dumps({
    "package_json": str(json_path.relative_to(root)), "package_json_sha256": sha(json_path),
    "package_md": str(md_path.relative_to(root)), "package_md_sha256": sha(md_path),
    "builder_script_sha256": sha(Path(__file__)),
    "promotion_readiness": pkg['promotion_readiness'],
    "promotion_readiness_reasons": reasons,
}, indent=2))
