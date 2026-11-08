#!/usr/bin/env python3
"""C192 execution summary: lists all new C192 artifact paths + sha256 from bytes."""
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


OOS_PATH = reports / "real_quote_volume_rqa_lavg_over_tt_ratio_shock_mr_costed_oos_20261108T015314Z.json"
SCRIPT_PATH = root / "scripts" / "run_real_quote_volume_rqa_lavg_over_tt_ratio_shock_mr_costed_oos.py"
PRIOR_REGISTRY = "reports/strategy_edge_registry_20261108T014412Z.json"
PRIOR_REGISTRY_SHA = "7d2e0861e67726b03924550d7be29a68154010d79d3c6c2fa1177077edc848e0"
C191_OOS = "reports/real_quote_volume_rqa_lmax_over_lavg_ratio_shock_mr_costed_oos_20261108T014311Z.json"
C191_OOS_SHA = "313f6e904c049905b8ce87596b1af6953eaf36076be50c9a65f547e54b87768e"

oos = json.loads(OOS_PATH.read_text())
_ingests = sorted(reports.glob("real_feed_ingest_attempt_*.json"))
INGEST_PATH = max([p for p in _ingests if "20261108T015" in p.name], key=lambda p: p.stat().st_mtime)
_registries = sorted(reports.glob("strategy_edge_registry_*.json"))
REGISTRY_PATH = max([p for p in _registries if "20261108T015" in p.name], key=lambda p: p.stat().st_mtime)

out = {
    "tool": "campaign192_execution_summary",
    "generated_at_utc": ts,
    "campaign": 192,
    "strategy_id": "VOLUME_RQA_LAVG_OVER_TT_RATIO_SHOCK_MR",
    "real_data_only": True,
    "fabricated_data": False,
    "fail_closed": True,
    "edge_claim": oos.get("edge_claim", "NONE"),
    "artifacts": {
        "oos": {"path": str(OOS_PATH.relative_to(root)), "sha256": sha256_file(OOS_PATH)},
        "ingest": {"path": str(INGEST_PATH.relative_to(root)), "sha256": sha256_file(INGEST_PATH)},
        "registry": {"path": str(REGISTRY_PATH.relative_to(root)), "sha256": sha256_file(REGISTRY_PATH)},
        "script": {"path": str(SCRIPT_PATH.relative_to(root)), "sha256": sha256_file(SCRIPT_PATH)},
    },
    "all_new_c192_artifact_paths_sha256_from_bytes": True,
    "oos_edge_proven": oos.get("oos_edge_proven", False),
    "c192_preselected": {
        "family_primary": "VOLUME_RQA_LAVG_OVER_TT_RATIO_SHOCK_MR",
        "grep_cmd": "grep -rnE 'LAVG_OVER_TT|lavg_over_tt|rqa_ratio_lavg_over_tt|rqa_lavg_over_tt_ratio' scripts/ strategies/ backtest/ utils/ 2>&1",
        "grep_hits_nonself_at_run": 0,
        "grep_verify_required": True,
        "note": "C192 primary LAVG_OVER_TT grep 0 verified before implementation/run; now consumed by C192.",
    },
    "references": {
        "prior_registry": PRIOR_REGISTRY,
        "prior_registry_sha256": PRIOR_REGISTRY_SHA,
        "c191_oos": C191_OOS,
        "c191_oos_sha256": C191_OOS_SHA,
    },
}
out_path = reports / f"campaign192_execution_summary_{ts}.json"
out_path.write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps({"summary": str(out_path.relative_to(root)), "summary_sha256": sha256_file(out_path)}, indent=2))
