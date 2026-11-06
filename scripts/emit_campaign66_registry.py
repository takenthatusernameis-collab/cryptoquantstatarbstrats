#!/usr/bin/env python3
"""Emit Campaign 66 strategy_edge_registry superseding C65 registry (fail-closed)."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
SUPERSEDES = "reports/strategy_edge_registry_20261106T061455Z.json"


def run_pytest():
    cmd = [sys.executable, "-m", "pytest", "tests/", "-q"]
    p = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=1200)
    out = (p.stdout or "") + "\n" + (p.stderr or "")
    passed = failed = skipped = errors = 0
    m = re.search(r"(\d+)\s+passed", out)
    if m:
        passed = int(m.group(1))
    m = re.search(r"(\d+)\s+failed", out)
    if m:
        failed = int(m.group(1))
    m = re.search(r"(\d+)\s+skipped", out)
    if m:
        skipped = int(m.group(1))
    m = re.search(r"(\d+)\s+errors?", out)
    if m:
        errors = int(m.group(1))
    return {
        "command": " ".join(cmd),
        "returncode": p.returncode,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "errors": errors,
        "summary_tail": out.strip().splitlines()[-6:],
    }


def main():
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    pytest_res = run_pytest()

    c66_oos = sorted(REPORTS.glob("real_quote_volume_idr_interdecile_dispersion_shock_mr_costed_oos_*.json"))
    oos_art = str(c66_oos[-1].relative_to(ROOT)) if c66_oos else None
    status_art = None
    for p in sorted(REPORTS.glob("real_feed_unblock_status_*.json"), reverse=True):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
            if d.get("campaign") == 66:
                status_art = str(p.relative_to(ROOT))
                break
        except Exception:
            pass

    oos_data = {}
    if oos_art:
        try:
            oos_data = json.loads((ROOT / oos_art).read_text(encoding="utf-8"))
        except Exception:
            pass

    reg = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "campaign": 66,
        "supersedes": SUPERSEDES,
        "oos_edge_proven": bool(oos_data.get("oos_edge_proven", False)),
        "pytest_full_suite": pytest_res,
        "artifacts": [a for a in [oos_art, status_art] if a],
        "c66_hypothesis": "real_quote_volume Rolling Interdecile Range (IDR, P90-P10) dispersion shock MR (R-B, pre-stated; differs from C23/C40-C65)",
        "c66_oos_result": {
            "oos_edge_proven": oos_data.get("oos_edge_proven", False),
            "any_exposure": oos_data.get("any_exposure"),
            "aggregate_cost_grid": oos_data.get("aggregate_cost_grid"),
        },
        "blocked_families_substantive": [
            "funding_basis_carry",
            "cross_exchange_dual_venue_same_asset",
            "term_structure_real_iv_vol_surface",
            "intrabar_microstructure",
        ],
        "notes": "Fail-closed. Real data only. No proxies/fabrication/threshold weakening. C66 R-B on validated real_quote_volume (Rolling IDR P90-P10 rank-decile 80% spread, trimming 10% tails each side; distinct tail cutpoints from C62 IQR P75-P25 50% spread, distinct from C64 Range extremes, distinct from C61/C65 centered-L1 MAD/MeanAD magnitudes, C63 GMD pairwise, C48/C56 STD/CV L2, and all C23/C40-C65 moments/entropies/Hurst-SampEn/autocorr/corr/beta/level/ROC/cumulative/partition/imbalance); oos_edge_proven=false (pre-stated rule not met). Remaining families blocked_no_real_feed.",
    }
    out = REPORTS / f"strategy_edge_registry_{ts}.json"
    out.write_text(json.dumps(reg, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"wrote": str(out), "oos_edge_proven": reg["oos_edge_proven"], "pytest": {"rc": pytest_res["returncode"], "passed": pytest_res["passed"], "failed": pytest_res["failed"], "skipped": pytest_res["skipped"]}}))


if __name__ == "__main__":
    main()
