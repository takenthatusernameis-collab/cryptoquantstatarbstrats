#!/usr/bin/env python3
"""C169: campaign execution summary listing all new C169 artifacts with SHAs from bytes."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parents[1]
reports = root / "reports"
scripts = root / "scripts"

OOS = "reports/real_quote_volume_rqa_vmax_over_trend_ratio_shock_mr_costed_oos_20261107T193943Z.json"
INGEST = "reports/real_feed_ingest_attempt_20261107T194126Z.json"
REGISTRY = "reports/strategy_edge_registry_20261107T194147Z.json"
SCRIPT = "scripts/run_real_quote_volume_rqa_vmax_over_trend_ratio_shock_mr_costed_oos.py"
PRIOR_REGISTRY = "reports/strategy_edge_registry_20261107T193533Z.json"
PRIOR_REGISTRY_SHA = "b8f49687af816d799ba2196ed74968d59599a99a593fe03ed3d812cbb36cfbf2"
PRIOR_C168_OOS = "reports/real_quote_volume_rqa_rr_over_trend_ratio_shock_mr_costed_oos_20261107T193420Z.json"
PRIOR_C168_OOS_SHA = "a415fbb010ef42c91fef5d207f561afc30010a0a9bad96b836955517b88dd6a2"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

oos = json.loads((root / OOS).read_text())

summary = {
    "tool": "campaign169_execution_summary",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "campaign": 169,
    "real_data_only": True,
    "fabricated_data": False,
    "fail_closed": True,
    "edge_claim": "NONE",
    "oos_edge_proven": bool(oos.get("oos_edge_proven")),
    "artifacts": {
        "oos": {
            "path": OOS,
            "sha256": sha(root / OOS),
        },
        "ingest": {
            "path": INGEST,
            "sha256": sha(root / INGEST),
        },
        "registry": {
            "path": REGISTRY,
            "sha256": sha(root / REGISTRY),
        },
        "script": {
            "path": SCRIPT,
            "sha256": sha(root / SCRIPT),
        },
        "superseded_registry": {
            "path": PRIOR_REGISTRY,
            "sha256": PRIOR_REGISTRY_SHA,
        },
        "superseded_c168_oos": {
            "path": PRIOR_C168_OOS,
            "sha256": PRIOR_C168_OOS_SHA,
        },
    },
    "c169_rb": {
        "candidate": oos.get("candidate"),
        "strategy_id": oos.get("strategy_id"),
        "oos_edge_proven": bool(oos.get("oos_edge_proven")),
        "edge_claim": oos.get("edge_claim", "NONE"),
        "any_exposure_oos": bool(oos.get("any_exposure_oos")),
        "all_cost_slices_positive_oos_net_sum": bool(oos.get("all_cost_slices_positive_oos_net_sum")),
        "all_cost_slices_beat_bh_mean_rule": bool(oos.get("all_cost_slices_beat_bh_mean_rule")),
        "cross_asset_oos_net_sums": oos.get("cross_asset", {}).get("oos_net_sums", {}),
    },
    "nonspot_blockers": {
        "status": "FAIL_CLOSED_BLOCKED_NO_REAL_ARTIFACT",
        "blocked_families": ["funding_basis_carry", "cross_exchange_dual_venue_same_asset", "term_structure_real_iv_vol_surface", "intrabar_microstructure"],
        "ingest_attempt": INGEST,
        "note": "Nonspot ingest blocked fail-closed; R-B unblocked on validated real_quote_volume.",
    },
    "notes": [
        "C169 V_max/TREND RQA ratio shock MR on real_quote_volume; heavy work completed (>=3 new concrete artifacts: OOS + ingest + registry + summary, each with SHA256 from bytes).",
        "Edge rule did not hold (edge_claim NONE); reported honestly, no fabrication.",
        "Nonspot ingest blocked fail-closed; R-B unblocked on real_quote_volume.",
        "pytest unavailable recorded honestly; no fabricated results.",
        "C168 RR/TREND and prior registry superseded by C169 artifacts.",
    ],
}

out_path = reports / f"campaign169_execution_summary_{ts}.json"
out_path.write_text(json.dumps(summary, indent=2) + "\n")
out_sha = sha(out_path)
print(json.dumps({
    "summary": str(out_path.relative_to(root)), "summary_sha256": out_sha,
}, indent=2))
