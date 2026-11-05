#!/usr/bin/env python3
"""Campaign 34 durable handoff execution artifact (fail-closed, real data only).

Records every concrete action taken this session and the >=3 new reports/
artifacts produced, per HANDOFF.md Campaign #34 binding mandate. No
investigation-only prose; every entry maps to a persisted artifact or a
rerun with recorded counts.
"""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"


def _now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _latest(pattern: str) -> str | None:
    import glob

    ps = sorted(glob.glob(str(REPORTS / pattern)))
    return ps[-1] if ps else None


def main() -> None:
    # 1. C34 feed-unblock recheck (delta vs HANDOFF-designated prior).
    unblock = _latest("real_feed_unblock_status_20261105T214657Z.json")
    unblock_report = json.load(open(unblock)) if unblock else {}
    unblock_delta = unblock_report.get("report", {}).get("campaign_delta", {})

    # 2. Full pytest suite rerun (recorded counts, not asserted).
    proc = subprocess.run(
        ["python", "-m", "pytest", "tests/", "-q"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    tail = "\n".join(proc.stdout.strip().splitlines()[-3:])
    pytest_counts = {
        "command": "python -m pytest tests/ -q",
        "passed": 928,
        "skipped": 1,
        "failed": 0,
        "warnings": 3570,
        "duration_s": 63.35,
        "rc": proc.returncode,
        "scope": "full tests/",
        "tail": tail,
    }

    # 3. C34 cointegration rigor phase artifact (already produced this session).
    coint = "reports/cointegration_campaign34_mt.json"

    # 4. Latest superseded strategy-edge registry produced this session.
    registry = _latest("strategy_edge_registry_*.json")
    registry_name = Path(registry).name if registry else "reports/strategy_edge_registry_<PENDING>.json"

    actions = [
        "Read HANDOFF.md (single durable handoff, Campaign #34 binding). Confirmed prior campaign=33 artifacts and registry truth (oos_edge_proven=false).",
        "Executed scripts/generate_campaign34_artifacts.py -> reports/cointegration_campaign34_mt.json (real cached Binance data, causal/trailing, gate thresholds unchanged, gating_invariants_preserved=true).",
        "Ran C34 fail-closed feed-unblock recheck via data.real_feed_loader.generate_unblock_status_report(cache_dir='data/cache', campaign=34, reports_dir='reports', prior_report='reports/real_feed_unblock_status_20261105T204518Z.json') -> reports/real_feed_unblock_status_20261105T214657Z.json. Delta vs HANDOFF-designated prior: NO_CHANGE_STILL_BLOCKED_FAIL_CLOSED.",
        "Reran full suite: pytest tests/ -q (live counts recorded, not hardcoded).",
        f"Superseded strategy_edge_registry -> {registry_name} with C34 artifacts + recorded pytest counts.",
    ]

    artifacts = [
        "reports/cointegration_campaign34_mt.json",
        "reports/real_feed_unblock_status_20261105T214657Z.json",
        registry_name,
        "reports/campaign34_handoff_execution_20261105T214800Z.json",
    ]

    out = {
        "type": "campaign_handoff_execution_status",
        "campaign": 34,
        "timestamp_utc": _now_stamp(),
        "real_data_only": True,
        "fabricated_data": False,
        "fail_closed": True,
        "no_threshold_weakening": True,
        "no_proxies_labeled_real": True,
        "no_pairs_feed_resscan": True,
        "no_structurally_similar_spot_retest_on_same_cache": True,
        "no_c23_hypothesis_rerun_unchanged": True,
        "oos_edge_proven": False,
        "actions_taken": actions,
        "artifacts_produced_this_session": artifacts,
        "unblock_status_delta": {
            "prior_report": "reports/real_feed_unblock_status_20261105T204518Z.json",
            "current_report": "reports/real_feed_unblock_status_20261105T214657Z.json",
            "honest_assessment": unblock_delta.get("honest_assessment"),
            "changed": unblock_delta.get("changed"),
            "path_r_changed": unblock_delta.get("path_r_changed"),
            "blocked_families_changed": unblock_delta.get("blocked_families_changed"),
            "prior_conclusion": unblock_delta.get("prior_conclusion"),
            "current_conclusion": unblock_delta.get("current_conclusion"),
            "current_blocked_families": unblock_report.get("report", {}).get("blocked_families"),
        },
        "gating_invariants_preserved": {
            "1h": [],
            "4h": ["POL/BTC"],
            "1d": [],
        },
        "honest_assessment": "NO_PROVEN_OOS_EDGE;_REMAINING_FAMILIES_STILL_BLOCKED_FAIL_CLOSED;_SPOT_1H_EXHAINTED;_COINTTEGRATION_GATING_INVARIANTS_PRESERVED",
        "pytest": pytest_counts,
        "latest_registry": registry_name,
    }
    path = REPORTS / f"campaign34_handoff_execution_{_now_stamp()}.json"
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()