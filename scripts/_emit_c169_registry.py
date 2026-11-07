#!/usr/bin/env python3
"""C169: emit strategy_edge_registry superseding C168 registry (b8f49687...).

Reads the emitted C168 OOS report, C169 OOS report, C169 ingest report and
C169 script; computes SHAs from bytes. Structurally consistent with C168
registry. edge_claim NONE unless the fail-closed edge rule holds.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parents[1]
reports = root / "reports"
scripts = root / "scripts"

PRIOR_REGISTRY = "reports/strategy_edge_registry_20261107T193533Z.json"
PRIOR_REGISTRY_SHA = "b8f49687af816d799ba2196ed74968d59599a99a593fe03ed3d812cbb36cfbf2"
PRIOR_C168_OOS = "reports/real_quote_volume_rqa_rr_over_trend_ratio_shock_mr_costed_oos_20261107T193420Z.json"
PRIOR_C168_OOS_SHA = "a415fbb010ef42c91fef5d207f561afc30010a0a9bad96b836955517b88dd6a2"

C169_OOS = "reports/real_quote_volume_rqa_vmax_over_trend_ratio_shock_mr_costed_oos_20261107T193943Z.json"
C169_INGEST = "reports/real_feed_ingest_attempt_20261107T194126Z.json"
C169_SCRIPT = "scripts/run_real_quote_volume_rqa_vmax_over_trend_ratio_shock_mr_costed_oos.py"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load(p: Path):
    return json.loads(p.read_text())


ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

c168_oos = load(root / PRIOR_C168_OOS)
c169_oos = load(root / C169_OOS)
c169_ingest = load(root / C169_INGEST)

c169_script_sha = sha(root / C169_SCRIPT)

c169_oos_sha = sha(root / C169_OOS)
c169_ingest_sha = sha(root / C169_INGEST)


def oos_block(label, path, sha256, obj):
    return {
        "path": path,
        "sha256": sha256,
        "oos_edge_proven": bool(obj.get("oos_edge_proven")),
        "edge_claim": obj.get("edge_claim", "NONE"),
        "any_exposure_oos": bool(obj.get("any_exposure_oos")),
        "all_cost_slices_positive_oos_net_sum": bool(obj.get("all_cost_slices_positive_oos_net_sum")),
        "all_cost_slices_beat_bh_mean_rule": bool(obj.get("all_cost_slices_beat_bh_mean_rule")),
        "cross_asset_oos_net_sums": obj.get("cross_asset", {}).get("oos_net_sums", {}),
    }


registry = {
    "tool": "strategy_edge_registry",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "campaign": 169,
    "real_data_only": True,
    "fabricated_data": False,
    "fail_closed": True,
    "edge_claim": "NONE",
    "global_oos_edge_proven": bool(c169_oos.get("oos_edge_proven")),
    "supersedes": {
        "path": PRIOR_REGISTRY,
        "sha256": PRIOR_REGISTRY_SHA,
    },
    "references": {
        "c168_oos": {
            "path": PRIOR_C168_OOS,
            "sha256": PRIOR_C168_OOS_SHA,
        }
    },
    "c168_oos": oos_block("c168_oos", PRIOR_C168_OOS, PRIOR_C168_OOS_SHA, c168_oos),
    "c169_oos": oos_block("c169_oos", C169_OOS, c169_oos_sha, c169_oos),
    "c169_ingest": {
        "path": C169_INGEST,
        "sha256": c169_ingest_sha,
    },
    "c169_script": {
        "path": C169_SCRIPT,
        "sha256": c169_script_sha,
    },
    "lineage_note": "C169 V_max/TREND RQA ratio shock MR evaluated fail-closed on real_quote_volume OOS WF 720/168/168, costs [[0,0],[5,5],[10,10],[20,20],[40,40]]. No edge proven; edge_claim NONE. Supersedes C168 registry b8f49687.",
}

out_path = reports / f"strategy_edge_registry_{ts}.json"
out_path.write_text(json.dumps(registry, indent=2) + "\n")
out_sha = sha(out_path)
print(json.dumps({
    "registry": str(out_path.relative_to(root)), "registry_sha256": out_sha,
    "c169_oos_sha256": c169_oos_sha, "c169_ingest_sha256": c169_ingest_sha,
    "c169_script_sha256": c169_script_sha,
    "global_oos_edge_proven": registry["global_oos_edge_proven"],
}, indent=2))
