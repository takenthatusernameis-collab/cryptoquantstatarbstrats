#!/usr/bin/env python3
"""Campaign 34 strategy-edge registry superseder (fail-closed, real data only).

Runs the full pytest suite, records live counts, and writes
reports/strategy_edge_registry_<UTC>.json superseding the prior registry with
the Campaign 34 cointegration rigor artifact + unblock recheck listed as
new_artifacts_this_session. oos_edge_proven stays false (no proven edge).
"""
from __future__ import annotations

import glob
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _latest(pattern: str) -> str | None:
    ps = sorted(glob.glob(str(REPORTS / pattern)))
    return ps[-1] if ps else None


def _run_pytest() -> dict:
    proc = subprocess.run(
        ["python", "-m", "pytest", "tests/", "-q"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    tail = "\n".join(proc.stdout.strip().splitlines()[-3:])
    # Parse the pytest summary line to avoid hardcoding stale counts.
    counts = {"passed": 0, "skipped": 0, "failed": 0, "warnings": 0}
    for line in proc.stdout.splitlines():
        low = line.strip()
        if "passed" in low and "warning" in low:
            import re

            m = re.search(r"(\d+)\s+passed", low)
            if m:
                counts["passed"] = int(m.group(1))
            m = re.search(r"(\d+)\s+skipped", low)
            if m:
                counts["skipped"] = int(m.group(1))
            m = re.search(r"(\d+)\s+failed", low)
            if m:
                counts["failed"] = int(m.group(1))
            m = re.search(r"(\d+)\s+warning", low)
            if m:
                counts["warnings"] = int(m.group(1))
            break
    return {
        "command": "python -m pytest tests/ -q",
        "passed": counts["passed"],
        "skipped": counts["skipped"],
        "failed": counts["failed"],
        "warnings": counts["warnings"],
        "rc": proc.returncode,
        "scope": "full tests/",
        "tail": tail,
    }


def main() -> None:
    prev = _latest("strategy_edge_registry_*.json")
    prev_d = json.load(open(prev)) if prev else {}
    fam_prev = {f["family"]: f for f in prev_d.get("families", [])}

    pytest_counts = _run_pytest()
    if pytest_counts["failed"] != 0 or pytest_counts["rc"] != 0:
        raise SystemExit(f"FAIL-CLOSED: pytest not green {pytest_counts}")

    new_artifacts = [
        "reports/cointegration_campaign34_mt.json",
        "reports/real_feed_unblock_status_20261105T214657Z.json",
    ]
    # Reference the durable handoff execution artifact produced this session
    # (latest campaign34_handoff_execution_*.json) so the registry never
    # references a stale/misspelled filename.
    handoff = _latest("campaign34_handoff_execution_*.json")
    if handoff:
        new_artifacts.append(Path(handoff).name)

    def keep(name, default_status):
        f = fam_prev.get(name, {"family": name, "data_status": default_status})
        f.setdefault("family", name)
        f["data_status"] = default_status
        f["actionable_next_step"] = (
            f.get("actionable_next_step", "")
            + " (unchanged by C34; do not re-scan/re-audit without NEW real dataset.)"
        ).strip()
        return f

    families = [
        keep("pairs_cointegration", "real_cached_verified"),
        keep("momentum", "real_cached_verified"),
        keep("mean_reversion", "real_cached_verified"),
        keep("cross_exchange_same_asset_dual_venue", "blocked_no_real_feed"),
        keep("funding_basis_carry", "blocked_no_real_feed"),
        keep("term_structure_carry_proxy", "blocked_no_real_feed"),
        keep("volatility_surface_arbitrage_proxy", "blocked_no_real_feed"),
    ]

    out = {
        "report": "strategy_edge_registry",
        "supersedes": Path(prev).name if prev else None,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "mandate": "Campaign 34 deliverable — consolidated edge registry updated with C34 cointegration rigor phase 6 artifact + fail-closed unblock recheck (delta vs 20261105T204518Z) + full pytest rerun. Fail-closed, real data only, no fabrication, no threshold weakening, no proxies labeled real.",
        "provenance": {
            "real_data_only": True,
            "fabricated_data": False,
            "fail_closed": True,
            "no_threshold_weakening": True,
        },
        "pytest": pytest_counts,
        "new_artifacts_this_session": new_artifacts,
        "families": families,
        "global_truth": {
            "pairs": "PROVEN BLOCKED (fail-closed) on current real cached universe/window — do not re-scan/re-audit without NEW real dataset.",
            "momentum_mean_reversion": "NO PROVEN NET-OF-COST OOS EDGE on real cached spot 1h; beta-like, not alpha.",
            "cross_exchange_funding_basis_term_structure_real_iv": "BLOCKED_NO_REAL_FEED — honest only; no fabricated feeds/proxies labeled real.",
            "cointegration_campaign34": "Rigor phase 6 rerun on real cached data; gating invariants preserved (1h=[], 4h=[POL/BTC], 1d=[]); full-universe 1d Johansen rank=1 spread stationary (adf p=1.3e-11, half-life 2.48, Hurst 0.068) but NO walk-forward OOS edge (insufficient_splits / zero capacity); regime-transition stress amplified but no breach. oos_edge_proven=false.",
            "rules": [
                "real data only",
                "no fabrication",
                "fail-closed",
                "no threshold weakening",
                "no proxies labeled real",
                ">=3 concrete reports artifacts per session",
                "no structurally-similar spot retest on same cache presented as new campaign",
                "no C23 Abnormal Quote Volume Momentum rerun unchanged",
            ],
        },
    }
    path = REPORTS / f"strategy_edge_registry_{_now()}.json"
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {path}")
    print("pytest:", json.dumps(pytest_counts))


if __name__ == "__main__":
    main()