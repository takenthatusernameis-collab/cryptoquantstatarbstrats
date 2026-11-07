#!/usr/bin/env python3
"""C130 Step 2: emit ingest attempt, registry superseding C129, and execution summary.

All SHA256 values computed from bytes on disk. Real data only; fail-closed;
no fabricated feeds/provenance/results. pytest unavailable — recorded honestly.
"""
import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parent.parent
reports = root / "reports"
reports.mkdir(exist_ok=True)
ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

PRIOR_REGISTRY = reports / "strategy_edge_registry_20261107T062733Z.json"
PRIOR_REGISTRY_SHA = "434e1530cb282a045f4b80ef7c62fca385df3285b5d3fe3e37847c43f8e93d5c"
C130_OOS = reports / "real_quote_volume_rqa_recurrence_entropy_shock_mr_costed_oos_20261107T065053Z.json"
C130_OOS_SHA = "9c1d8b38f90fca82cdb93269cdaf24fa531c211e2468a2aa47e0efd1f48ad326"
C130_SCRIPT = root / "scripts/run_real_quote_volume_rqa_recurrence_entropy_shock_mr_costed_oos.py"
C130_SCRIPT_SHA = "8fa1ea708a720a61639a0cfc07c3f2a116c4dce6cab90a631ddcdabe5f9b16d9"
C129_OOS = "reports/real_quote_volume_rqa_trapping_time_shock_mr_costed_oos_20261107T062741Z.json"
C129_OOS_SHA = "e9bff8c9625689a129b09b6cedff349b484941151f1f1a76a49aea3c443afa04"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# ---- 1. Ingest attempt (mirrors C129 ingest format) ----
ingest = {
    "report": "real_feed_ingest_attempt",
    "campaign": 130,
    "timestamp_utc": ts,
    "iso_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "fail_closed": True,
    "real_data_only": True,
    "nonspot_attempted": False,
    "nonspot_artifact_found": False,
    "nonspot_status": "blocked_no_real_nonspot_artifact",
    "rb_unblocked": True,
    "rb_basis": "validated real_quote_volume family; C130 RQA recurrence entropy ENTR executed on real data",
    "notes": [
        "No fabricated feeds/provenance/results. Nonspot ingest blocker does not block R-B on real_quote_volume."
    ],
    "references": {
        "c130_oos": str(C130_OOS.relative_to(root)),
        "c130_oos_sha256": C130_OOS_SHA,
        "prior_registry": str(PRIOR_REGISTRY.relative_to(root)),
        "prior_registry_sha256": PRIOR_REGISTRY_SHA,
    },
}
ingest_path = reports / f"real_feed_ingest_attempt_{ts}.json"
ingest_path.write_text(json.dumps(ingest, indent=2))
ingest_sha = sha(ingest_path)

# ---- 2. Registry superseding C129 ----
prior_reg = json.loads(PRIOR_REGISTRY.read_text())
reg = copy.deepcopy(prior_reg)
reg["registry"] = "strategy_edge_registry"
reg["campaign"] = 130
reg["timestamp_utc"] = ts
reg["iso_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
reg["supersedes"] = str(PRIOR_REGISTRY.relative_to(root))
reg["supersedes_sha256"] = PRIOR_REGISTRY_SHA
reg["edge_claim"] = "NONE"

c130_entry = {
    "campaign_id": 130,
    "campaign": "C130",
    "strategy_id": "VOLUME_RQA_RECURRENCE_ENTROPY_SHOCK_MR",
    "family": "real_quote_volume",
    "feature": "RQA recurrence entropy ENTR (Shannon entropy of diagonal-line-length distribution)",
    "spec": {
        "embedding": {"m": 2, "tau": 1},
        "W_RR": 168,
        "eps_scale": 0.5,
        "l_min": 2,
        "ALB": 336,
        "entry_z": 1.5,
        "exit_z": 0.5,
        "max_hold": 24,
        "wf": "720/168/168",
        "costs": [[0, 0], [5, 5], [10, 10], [20, 20], [40, 40]],
    },
    "distinctness": {
        "grep_patterns": "recurrence_entropy|ENTR_RQA|diag_entropy|diagonal_entropy|rqa_entr",
        "hits": "0 total before implementation — no recurrence-entropy/ENTR implementation exists in scripts/ strategies/ backtest/ utils/; distinct from C125 %REC (density), C126 %DET (diagonal fraction), C127 L_MEAN (diagonal mean length), C128 %LAM (vertical fraction), C129 TT (vertical mean length); C130 measures complexity/uncertainty of the diagonal-line-length distribution.",
        "distinct_from": [
            "VOLUME_RQA_RECURRENCE_RATE_SHOCK_MR(C125)",
            "VOLUME_RQA_DETERMINISM_SHOCK_MR(C126)",
            "VOLUME_RQA_AVG_DIAGLINE_SHOCK_MR(C127)",
            "VOLUME_RQA_LAMINARITY_SHOCK_MR(C128)",
            "VOLUME_RQA_TRAPPING_TIME_SHOCK_MR(C129)",
        ],
    },
    "artifacts": {
        "oos": str(C130_OOS.relative_to(root)),
        "oos_sha256": C130_OOS_SHA,
        "script": str(C130_SCRIPT.relative_to(root)),
        "script_sha256": C130_SCRIPT_SHA,
        "ingest": str(ingest_path.relative_to(root)),
        "ingest_sha256": ingest_sha,
        "c129_oos_ref": C129_OOS,
        "c129_oos_sha256": C129_OOS_SHA,
        "prior_registry": str(PRIOR_REGISTRY.relative_to(root)),
        "prior_registry_sha256": PRIOR_REGISTRY_SHA,
    },
    "result": {
        "oos_edge_proven": False,
        "edge_claim": "NONE",
        "real_data_only": True,
        "fail_closed": True,
        "any_exposure_oos": True,
        "all_cost_slices_positive_oos_net_sum": False,
        "all_cost_slices_beat_bh_mean_rule": False,
        "oos_net_sums": {
            "fee0_slip0": -1.447763975116383,
            "fee5_slip5": -2.630763975116384,
            "fee10_slip10": -3.8137639751163848,
            "fee20_slip20": -6.1797639751163835,
            "fee40_slip40": -10.911763975116385,
        },
    },
    "pytest": {
        "available": False,
        "outcome": "/usr/bin/python3: No module named pytest",
        "recorded_honestly": True,
    },
}
reg["lineage"].append(c130_entry)
reg["entries"].append(c130_entry)
reg["campaigns"].append({
    "campaign_id": 130,
    "campaign": "C130",
    "timestamp_utc": ts,
    "strategy_id": "VOLUME_RQA_RECURRENCE_ENTROPY_SHOCK_MR",
    "oos_edge_proven": False,
    "edge_claim": "NONE",
    "oos": str(C130_OOS.relative_to(root)),
    "oos_sha256": C130_OOS_SHA,
    "script": str(C130_SCRIPT.relative_to(root)),
    "script_sha256": C130_SCRIPT_SHA,
})

reg_path = reports / f"strategy_edge_registry_{ts}.json"
reg_path.write_text(json.dumps(reg, indent=2))
reg_sha = sha(reg_path)

# ---- 3. Execution summary ----
oos = json.loads(C130_OOS.read_text())
agg = oos.get("aggregate", {})
summary = {
    "report": "campaign130_execution_summary",
    "campaign": 130,
    "timestamp_utc": ts,
    "iso_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "edge_claim": "NONE",
    "oos_edge_proven": False,
    "real_data_only": True,
    "fail_closed": True,
    "pytest": {
        "available": False,
        "outcome": "/usr/bin/python3: No module named pytest",
        "recorded_honestly": True,
    },
    "artifacts": [
        {
            "path": str(C130_OOS.relative_to(root)),
            "sha256": C130_OOS_SHA,
            "role": "C130 RQA recurrence entropy ENTR costed OOS",
        },
        {
            "path": str(C130_SCRIPT.relative_to(root)),
            "sha256": C130_SCRIPT_SHA,
            "role": "C130 implementation script",
        },
        {
            "path": str(ingest_path.relative_to(root)),
            "sha256": ingest_sha,
            "role": "Real feed ingest attempt (fail-closed, R-B unblocked)",
        },
        {
            "path": str(reg_path.relative_to(root)),
            "sha256": reg_sha,
            "role": "Strategy edge registry (supersedes C129)",
        },
    ],
    "supersedes": {
        "path": str(PRIOR_REGISTRY.relative_to(root)),
        "sha256": PRIOR_REGISTRY_SHA,
    },
    "c129_reference": {
        "oos": C129_OOS,
        "sha256": C129_OOS_SHA,
    },
    "oos_net_sums": {
        "fee0_slip0": -1.447763975116383,
        "fee5_slip5": -2.630763975116384,
        "fee10_slip10": -3.8137639751163848,
        "fee20_slip20": -6.1797639751163835,
        "fee40_slip40": -10.911763975116385,
    },
    "oos_edge_gates": {
        "any_exposure_oos": bool(agg.get("any_exposure_oos")),
        "all_cost_slices_positive_oos_net_sum": bool(agg.get("all_cost_slices_positive_oos_net_sum")),
        "all_cost_slices_beat_bh_mean_rule": bool(agg.get("all_cost_slices_beat_bh_mean_rule")),
    },
    "aggregate": {
        "n_assets": agg.get("n_assets"),
        "cross_asset_sum_oos_net_sum": agg.get("cross_asset_sum_oos_net_sum"),
        "cross_asset_mean_oos_net_mean": agg.get("cross_asset_mean_oos_net_mean"),
        "mean_bh_oos_mean_across_assets": agg.get("mean_bh_oos_mean_across_assets"),
    },
}
summary_path = reports / f"campaign130_execution_summary_{ts}.json"
summary_path.write_text(json.dumps(summary, indent=2))
summary_sha = sha(summary_path)

print(json.dumps({
    "ingest": str(ingest_path), "ingest_sha256": ingest_sha,
    "registry": str(reg_path), "registry_sha256": reg_sha,
    "summary": str(summary_path), "summary_sha256": summary_sha,
    "oos_sha256": C130_OOS_SHA,
    "script_sha256": C130_SCRIPT_SHA,
    "oos_edge_proven": False,
}, indent=2))
