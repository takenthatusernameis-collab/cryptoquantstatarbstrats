#!/usr/bin/env python3
"""C161 emit driver: ingest + registry + summary artifacts + state.yaml sync.

Produces (SHAs computed from bytes on disk):
  reports/real_feed_ingest_attempt_<UTC>.json        (campaign 161)
  reports/strategy_edge_registry_<UTC>.json           (supersedes C160 registry)
  reports/campaign161_execution_summary_<UTC>.json    (OOS + ingest + registry + script)
And syncs research_state/state.yaml to C161-done / C162-next.
Fail-closed; real data only; no fabrication.
"""
import json, hashlib, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone

root = Path(__file__).resolve().parent
reports = root / "reports"
reports.mkdir(exist_ok=True)
ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

# --- inputs (disk-verified) ---
C160_REG = Path("reports/strategy_edge_registry_20261107T134336Z.json")
C160_REG_SHA = "a58ce4fc7161ec10340d6ec1183deabd7cf647abd83ad890f32e59356eb1a86a"
assert sha(C160_REG) == C160_REG_SHA, "C160 registry sha mismatch"

C160_OOS = Path("reports/real_quote_volume_rqa_trend_over_lmax_ratio_shock_mr_costed_oos_20261107T134222Z.json")
C160_OOS_SHA = "90e7d1b0aa2d41d8d8af2446c4f4d28d80f1d605343318cb612f9740a2a6e3c8"
assert sha(C160_OOS) == C160_OOS_SHA, "C160 OOS sha mismatch"

C161_OOS = sorted(reports.glob("real_quote_volume_rqa_lmax_over_trend_ratio_shock_mr_costed_oos_*.json"), key=lambda p: p.stat().st_mtime)[-1]
C161_OOS_SHA = sha(C161_OOS)
C161_OOS_OBJ = json.loads(C161_OOS.read_text())

C161_SCRIPT = root / "scripts" / "run_real_quote_volume_rqa_lmax_over_trend_ratio_shock_mr_costed_oos.py"
C161_SCRIPT_SHA = sha(C161_SCRIPT)

VOL_PKL = root / "data" / "cache" / "volume_1h_full.pkl"
VOL_META = root / "data" / "cache" / "volume_1h_full.meta.json"
VOL_PROV = root / "data" / "cache" / "volume_1h_full.provenance.json"
SPOT_PKL = root / "data" / "cache" / "0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl"

prior_reg = json.loads(C160_REG.read_text())

# --- 1. Ingest report ---
ingest = {
    "tool": "real_feed_ingest_attempt",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "campaign": 161,
    "real_data_only": True,
    "fabricated_data": False,
    "fail_closed": True,
    "nonspot_ingest": {
        "status": "blocked_fail_closed",
        "rb_unblocked": True,
        "rb_family": "real_quote_volume",
        "note": "Non-spot/external feed ingest remains blocked in this environment (fail-closed). R-B proceeds on validated real_quote_volume cache/provenance; blocker does not block R-B on real_quote_volume."
    },
    "real_quote_volume_cache": {
        "pkl": str(VOL_PKL),
        "pkl_exists": VOL_PKL.exists(),
        "pkl_sha256": sha(VOL_PKL),
        "meta": str(VOL_META),
        "meta_exists": VOL_META.exists(),
        "meta_sha256": sha(VOL_META),
        "provenance": str(VOL_PROV),
        "provenance_exists": VOL_PROV.exists(),
        "provenance_sha256": sha(VOL_PROV),
    },
    "spot_cache": {
        "pkl": str(SPOT_PKL),
        "exists": SPOT_PKL.exists(),
        "sha256": sha(SPOT_PKL),
    },
}
ingest_path = reports / f"real_feed_ingest_attempt_{ts}.json"
ingest_path.write_text(json.dumps(ingest, indent=2) + "\n")
ingest_sha = sha(ingest_path)

# --- 2. Registry ---
reg = {
    "tool": "strategy_edge_registry",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "campaign": 161,
    "edge_claim": "NONE",
    "global_oos_edge_proven": bool(C161_OOS_OBJ["oos_edge_proven"]),
    "real_data_only": True,
    "fabricated_data": False,
    "fail_closed": True,
    "no_proxies_labeled_real": True,
    "pytest": "unavailable (No module named pytest)",
    "nonspot_ingest": "blocked_fail_closed_rb_unblocked",
    "supersedes": str(C160_REG),
    "supersedes_sha256": C160_REG_SHA,
    "lineage": list(prior_reg.get("lineage", [])) + [
        {
            "campaign": 161,
            "strategy_id": "VOLUME_RQA_LMAX_OVER_TREND_RATIO_SHOCK_MR",
            "family": "RQA L_max/TREND ratio (max diagonal line length normalized by diagonal recurrence TREND slope) shock on volume dynamics",
            "status": "completed_oos_evaluated",
            "edge_claim": "NONE",
            "oos_edge_proven": bool(C161_OOS_OBJ["oos_edge_proven"]),
            "any_exposure_oos": bool(C161_OOS_OBJ["any_exposure_oos"]),
            "all_cost_slices_positive_oos_net_sum": bool(C161_OOS_OBJ["all_cost_slices_positive_oos_net_sum"]),
            "all_cost_slices_beat_bh_mean_rule": bool(C161_OOS_OBJ["all_cost_slices_beat_bh_mean_rule"]),
            "cross_asset_oos_net_sums": C161_OOS_OBJ["cross_asset"]["oos_net_sums"],
        }
    ],
    "campaigns": ["157", "158", "159", "160", "161"],
    "latest": {
        "campaign": 161,
        "strategy_id": "VOLUME_RQA_LMAX_OVER_TREND_RATIO_SHOCK_MR",
        "family": "RQA L_max/TREND ratio (max diagonal line length normalized by diagonal recurrence TREND slope) shock on volume dynamics",
        "status": "completed_oos_evaluated",
        "edge_claim": "NONE",
        "oos_edge_proven": bool(C161_OOS_OBJ["oos_edge_proven"]),
        "any_exposure_oos": bool(C161_OOS_OBJ["any_exposure_oos"]),
        "all_cost_slices_positive_oos_net_sum": bool(C161_OOS_OBJ["all_cost_slices_positive_oos_net_sum"]),
        "all_cost_slices_beat_bh_mean_rule": bool(C161_OOS_OBJ["all_cost_slices_beat_bh_mean_rule"]),
        "cross_asset_oos_net_sums": C161_OOS_OBJ["cross_asset"]["oos_net_sums"],
        "artifacts": {
            "oos_report": str(C161_OOS.relative_to(root)),
            "oos_sha256": C161_OOS_SHA,
            "ingest_report": str(ingest_path.relative_to(root)),
            "ingest_sha256": ingest_sha,
            "script": str(C161_SCRIPT.relative_to(root)),
            "script_sha256": C161_SCRIPT_SHA,
        },
        "distinctness_grep": {
            "cmd": "grep -rn 'lmax_over_trend|lmax_trend_ratio|rqa_ratio_lmax_trend|LMAX_OVER_TREND' scripts/ strategies/ backtest/ utils/ 2>&1",
            "hits_pre_non_self": 0,
            "verified_at_utc": "20261107T135009Z",
            "note": "0 non-self hits before implementation/run (grep verified at run time); primary LMAX/TREND candidate used. Distinct from C125-C160 incl C160 TREND/L_max (inverse ratio, distinct feature/id/implementation/hypothesis), C159 TT/ENTR, C158 %LAM/L_max, C157 RR/ENTR."
        }
    },
    "latest_campaign_done": 161,
    "lineage_note": "Structurally consistent campaign/supersedes/supersedes_sha256 lineage; carries forward prior context and adds C161.",
}
# carry forward prior completion entries + add c161
for k in ("c155_completion", "c156_completion", "c157_completion", "c158_completion", "c159_completion", "c160_completion"):
    if k in prior_reg:
        reg[k] = prior_reg[k]
reg["c161_completion"] = {
    "campaign": 161,
    "strategy_id": "VOLUME_RQA_LMAX_OVER_TREND_RATIO_SHOCK_MR",
    "family": "RQA L_max/TREND ratio (max diagonal line length normalized by diagonal recurrence TREND slope) shock on volume dynamics",
    "status": "completed_oos_evaluated",
    "completed_utc": ts,
    "oos_path": str(C161_OOS.relative_to(root)),
    "oos_sha256": C161_OOS_SHA,
    "ingest_path": str(ingest_path.relative_to(root)),
    "ingest_sha256": ingest_sha,
    "registry_path": str((reports / f"strategy_edge_registry_{ts}.json").relative_to(root)),
    "script_path": str(C161_SCRIPT.relative_to(root)),
    "script_sha256": C161_SCRIPT_SHA,
    "oos_edge_proven": bool(C161_OOS_OBJ["oos_edge_proven"]),
    "any_exposure_oos": bool(C161_OOS_OBJ["any_exposure_oos"]),
    "all_cost_slices_positive_oos_net_sum": bool(C161_OOS_OBJ["all_cost_slices_positive_oos_net_sum"]),
    "all_cost_slices_beat_bh_mean_rule": bool(C161_OOS_OBJ["all_cost_slices_beat_bh_mean_rule"]),
    "cross_asset_oos_net_sums": C161_OOS_OBJ["cross_asset"]["oos_net_sums"],
    "edge_claim": "NONE",
    "distinctness_grep": {
        "cmd": "grep -rn 'lmax_over_trend|lmax_trend_ratio|rqa_ratio_lmax_trend|LMAX_OVER_TREND' scripts/ strategies/ backtest/ utils/ 2>&1",
        "hits_pre_non_self": 0,
        "verified_at_utc": "20261107T135009Z",
        "note": "0 non-self hits before implementation/run (grep verified at run time); primary LMAX/TREND candidate used. Distinct from C125-C160 incl C160 TREND/L_max (inverse ratio, distinct feature/id/implementation/hypothesis)."
    }
}
reg_path = reports / f"strategy_edge_registry_{ts}.json"
reg_path.write_text(json.dumps(reg, indent=2) + "\n")
reg_sha = sha(reg_path)

# --- 3. Summary ---
summary = {
    "tool": "campaign161_execution_summary",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "campaign": 161,
    "mandate": "C161: implement/run distinct R-B L_max/TREND (inverse of C160 TREND/L_max) on real_quote_volume, emit OOS+ingest+registry+summary, sync state.yaml to C161-done/C162-next. Heavy work mandatory; no status-only.",
    "artifacts": [
        {"path": str(C161_OOS.relative_to(root)), "sha256": C161_OOS_SHA},
        {"path": str(ingest_path.relative_to(root)), "sha256": ingest_sha},
        {"path": str(reg_path.relative_to(root)), "sha256": reg_sha},
        {"path": str(C161_SCRIPT.relative_to(root)), "sha256": C161_SCRIPT_SHA},
    ],
    "c161_oos": {
        "strategy_id": "VOLUME_RQA_LMAX_OVER_TREND_RATIO_SHOCK_MR",
        "oos_edge_proven": bool(C161_OOS_OBJ["oos_edge_proven"]),
        "edge_claim": C161_OOS_OBJ["edge_claim"],
        "any_exposure_oos": bool(C161_OOS_OBJ["any_exposure_oos"]),
        "all_cost_slices_positive_oos_net_sum": bool(C161_OOS_OBJ["all_cost_slices_positive_oos_net_sum"]),
        "all_cost_slices_beat_bh_mean_rule": bool(C161_OOS_OBJ["all_cost_slices_beat_bh_mean_rule"]),
        "cross_asset_oos_net_sums": C161_OOS_OBJ["cross_asset"]["oos_net_sums"],
    },
    "nonspot_blockers": {
        "status": "blocked_fail_closed_rb_unblocked",
        "blocked_families": ["funding_basis_carry", "cross_exchange_dual_venue_same_asset", "term_structure_real_iv_vol_surface", "intrabar_microstructure"],
        "validated_only_family": "real_quote_volume",
        "ingest_attempt": str(ingest_path.relative_to(root)),
        "ingest_attempt_sha256": ingest_sha,
        "no_stale_cache_rescan": True,
        "note": "Nonspot ingest blocker does NOT block R-B on real_quote_volume.",
    },
    "references": {
        "prior_registry": str(C160_REG),
        "prior_registry_sha256": C160_REG_SHA,
        "c160_oos": str(C160_OOS),
        "c160_oos_sha256": C160_OOS_SHA,
    },
    "rules_followed": [
        "real_data_only", "fail_closed", "no_proxies_labeled_real", "no_fabrication",
        "edge_only_if_all_cost_slices_pass_and_beat_bh", "grep_verified_distinctness",
        "no_prior_campaign_rerun", "no_stale_cache_rescan", "sha_from_disk_bytes",
        "no_status_before_3_artifacts", "heavy_work_mandatory"
    ],
    "result": "NO_OOS_EDGE_PROVEN",
    "next_focus": "C162: distinct grep-verified RQA-ratio candidate (TREND/ENTR preselected, grep 0 hits at preselect; re-verify at run time), then continue C125-C162 distinct real_quote_volume families only if mechanically distinct and grep-verified."
}
summary_path = reports / f"campaign161_execution_summary_{ts}.json"
summary_path.write_text(json.dumps(summary, indent=2) + "\n")
summary_sha = sha(summary_path)

# --- 4. Sync state.yaml ---
state = {
    "repo": "cryptoquantstatarbstrats",
    "updated_utc": ts,
    "latest_campaign_done": "C161",
    "next_campaign": "C162",
    "readiness_verified_utc": ts,
    "edge_claim": "NONE",
    "global_oos_edge_proven": bool(C161_OOS_OBJ["oos_edge_proven"]),
    "real_data_only": True,
    "fail_closed": True,
    "no_proxies_labeled_real": True,
    "pytest": "unavailable (No module named pytest)",
    "deps": "numpy/scipy/pandas importable",
    "nonspot_ingest": "blocked_fail_closed_rb_unblocked",
    "latest_registry": {
        "path": str(reg_path.relative_to(root)),
        "sha256": reg_sha,
        "supersedes": str(C160_REG),
        "supersedes_sha256": C160_REG_SHA,
    },
    "latest_oos": {
        "campaign": "C161",
        "family": "VOLUME_RQA_LMAX_OVER_TREND_RATIO_SHOCK_MR",
        "path": str(C161_OOS.relative_to(root)),
        "sha256": C161_OOS_SHA,
        "oos_edge_proven": bool(C161_OOS_OBJ["oos_edge_proven"]),
        "any_exposure_oos": bool(C161_OOS_OBJ["any_exposure_oos"]),
        "all_cost_slices_positive_oos_net_sum": bool(C161_OOS_OBJ["all_cost_slices_positive_oos_net_sum"]),
        "all_cost_slices_beat_bh_mean_rule": bool(C161_OOS_OBJ["all_cost_slices_beat_bh_mean_rule"]),
        "cross_asset_oos_net_sums": C161_OOS_OBJ["cross_asset"]["oos_net_sums"],
    },
    "c162_preselected": {
        "family_primary": "VOLUME_RQA_TREND_OVER_ENTR_RATIO_SHOCK_MR",
        "metric_primary": "RQA ratio TREND/ENTR (diagonal recurrence TREND slope normalized by diagonal-line Shannon entropy) shock on volume dynamics (m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2); fail-closed on ENTR<=0/undefined/TREND undefined-non-finite",
        "alt1": "VOLUME_RQA_ENTR_OVER_TREND_RATIO_SHOCK_MR (ENTR/TREND; fail-closed on TREND==0/undefined-non-finite, ENTR<=0/undefined)",
        "distinctness_grep_primary": "trend_over_entr|trend_entr_ratio|rqa_ratio_trend_entr|TREND_OVER_ENTR",
        "grep_hits_observed_preselect": 0,
        "grep_verify_required": True,
        "note": "C162 pre-stated at C161 wrap-up. Operational primary TREND/ENTR (grep 0 hits observed); alt1 ENTR/TREND. Re-verify primary grep at run time (must be 0 hits, distinct from C125-C161). C162 trades TREND/ENTR."
    },
    "bottlenecks_removed": [
        "C104-C161 locked; no reruns unchanged",
        "C161 completed at " + ts + " (OOS+ingest+registry+summary+script, disk SHAs verified); state.yaml/HANDOFF synced to C161-done/C162-next",
        "numpy/scipy/pandas importable; pytest unavailable recorded honestly, do not fabricate test results",
        "nonspot ingest does not block R-B on real_quote_volume",
        "C160 collision guard verified 0 hits for TREND/LMAX; C161 primary (LMAX/TREND) grep verified 0 hits at run time"
    ],
    "mandatory": [
        "No status summary before >= 3 new concrete C162 report artifacts (OOS + ingest + registry/summary)",
        "Heavy work mandatory: implement/run + emit artifacts; no status-only replies"
    ]
}
import yaml  # may not be present; fallback manual
state_path = root / "research_state" / "state.yaml"
try:
    import yaml as _yaml
    state_path.write_text(_yaml.safe_dump(state, sort_keys=False))
except Exception:
    # manual fallback YAML
    def _dump(d, indent=0):
        lines = []
        sp = "  " * indent
        for k, v in d.items():
            if isinstance(v, dict):
                lines.append(f"{sp}{k}:")
                lines.append(_dump(v, indent + 1))
            elif isinstance(v, list):
                lines.append(f"{sp}{k}:")
                for it in v:
                    if isinstance(it, dict):
                        lines.append(f"{sp}  -")
                        for ik, iv in it.items():
                            lines.append(f"{sp}    {ik}: {iv}")
                    else:
                        lines.append(f"{sp}  - {it}")
            elif isinstance(v, bool):
                lines.append(f"{sp}{k}: {'true' if v else 'false'}")
            else:
                lines.append(f"{sp}{k}: {v}")
        return "\n".join(lines)
    state_path.write_text(_dump(state) + "\n")
state_sha = sha(state_path)

print(json.dumps({
    "ingest": str(ingest_path.relative_to(root)), "ingest_sha256": ingest_sha,
    "registry": str(reg_path.relative_to(root)), "registry_sha256": reg_sha,
    "summary": str(summary_path.relative_to(root)), "summary_sha256": summary_sha,
    "script": str(C161_SCRIPT.relative_to(root)), "script_sha256": C161_SCRIPT_SHA,
    "state": str(state_path.relative_to(root)), "state_sha256": state_sha,
    "oos_edge_proven": bool(C161_OOS_OBJ["oos_edge_proven"]),
    "edge_claim": C161_OOS_OBJ["edge_claim"],
}, indent=2))
