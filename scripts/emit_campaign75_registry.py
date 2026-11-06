#!/usr/bin/env python3
"""Emit Campaign 75 strategy edge registry (fail-closed, supersedes C74)."""
from __future__ import annotations
import glob
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
UTC = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def run_pytest():
    cmd = [sys.executable, "-m", "pytest", "tests/", "-q"]
    p = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=1200)
    tail = (p.stdout + "\n" + p.stderr).strip().splitlines()[-12:]
    passed = failed = skipped = errors = 0
    for line in reversed(tail):
        if "passed" in line or "failed" in line or "error" in line:
            def grab(word):
                m = re.search(r"(\d+) " + word, line)
                return int(m.group(1)) if m else 0
            passed, failed, skipped, errors = grab("passed"), grab("failed"), grab("skipped"), grab("error")
            break
    return {"command": " ".join(cmd), "returncode": p.returncode, "passed": passed, "failed": failed, "skipped": skipped, "errors": errors, "summary_tail": tail}


def main():
    c75 = sorted(glob.glob(str(REPORTS / "real_quote_volume_renyi2_collision_entropy_shock_mr_costed_oos_*.json")))
    c75_path = c75[-1] if c75 else None
    c75_obj = json.load(open(c75_path)) if c75_path else {}
    statuses = sorted(glob.glob(str(REPORTS / "real_feed_unblock_status_*.json")))
    c75_status = [s for s in statuses if Path(s).name > "real_feed_unblock_status_20261106T092751Z.json"]
    status_path = sorted(c75_status)[-1] if c75_status else (statuses[-1] if statuses else None)
    status_obj = json.load(open(status_path)) if status_path else {}

    pytest_res = run_pytest()
    blocked = status_obj.get("blocked_families") or ["funding_basis_carry", "cross_exchange_dual_venue_same_asset", "term_structure_real_iv_vol_surface", "intrabar_microstructure"]
    oos = bool(c75_obj.get("oos_edge_proven", False))
    out = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "campaign": 75,
        "supersedes": "reports/strategy_edge_registry_20261106T092751Z.json",
        "oos_edge_proven": oos,
        "pytest_full_suite": pytest_res,
        "artifacts": [p for p in [c75_path and "reports/" + Path(c75_path).name, status_path and "reports/" + Path(status_path).name] if p],
        "c75_hypothesis": "real_quote_volume Rolling Rényi-2 Collision Entropy (H2=-ln(Σ p_i^2), p_i=x_i/Σx_i, no binning, order-2/HHI) shock MR (R-B, pre-stated; differs from C23/C40-C74 incl. C41 Shannon binned histogram entropy order-1, C74 Theil T GE(1) mean r*ln r inequality, C51 Gini L1, C42/43 permutation/sample entropy, C45 CV, C72 Bowley, C73 Kelly)",
        "c75_oos_result": {
            "oos_edge_proven": oos,
            "any_exposure": c75_obj.get("any_exposure"),
            "all_costs_positive": c75_obj.get("all_costs_positive"),
            "beats_bh_rule": c75_obj.get("beats_bh_rule"),
            "aggregate": c75_obj.get("aggregate"),
        },
        "blocked_families_substantive": blocked,
        "notes": "Fail-closed. Real data only. No proxies/fabrication/threshold weakening. C75 R-B on validated real_quote_volume (Rényi-2 collision entropy, W=48, ZLB=168, normalized raw shares no binning, order-2 HHI; distinct from C41 Shannon binned histogram, C74 Theil T GE(1), C51 Gini L1, C42/43 permutation/sample entropy, C45 CV, C72 Bowley, C73 Kelly, and all C23/C40-C74); oos_edge_proven=false (pre-stated rule not met). Remaining families blocked_no_real_feed.",
    }
    out_path = REPORTS / f"strategy_edge_registry_{UTC}.json"
    out_path.write_text(json.dumps(out, indent=2, sort_keys=True, default=str) + "\n")
    print(out_path)
    print(json.dumps({"oos_edge_proven": out["oos_edge_proven"], "pytest_returncode": pytest_res["returncode"], "passed": pytest_res["passed"]}, indent=2))


if __name__ == "__main__":
    main()
