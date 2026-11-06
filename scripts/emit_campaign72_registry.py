#!/usr/bin/env python3
"""Emit Campaign 72 strategy edge registry (fail-closed, supersedes C71)."""
from __future__ import annotations
import glob
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
UTC = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

def run_pytest():
    cmd = [sys.executable, "-m", "pytest", "tests/", "-q"]
    p = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=900)
    tail = (p.stdout + "\n" + p.stderr).strip().splitlines()[-12:]
    # parse summary line like "928 passed, 1 skipped, 3587 warnings in 31.15s"
    passed = failed = skipped = errors = 0
    for line in reversed(tail):
        if "passed" in line or "failed" in line or "error" in line:
            import re
            def grab(word):
                m = re.search(r"(\d+) " + word, line)
                return int(m.group(1)) if m else 0
            passed = grab("passed"); failed = grab("failed"); skipped = grab("skipped"); errors = grab("error")
            break
    return {"command": " ".join(cmd), "returncode": p.returncode, "passed": passed, "failed": failed, "skipped": skipped, "errors": errors, "summary_tail": tail}

def main():
    # find C72 OOS artifact
    c72 = sorted(glob.glob(str(REPORTS / "real_quote_volume_bowley_quartile_skewness_shock_mr_costed_oos_*.json")))
    c72_path = c72[-1] if c72 else None
    c72_obj = json.load(open(c72_path)) if c72_path else {}
    status = sorted(glob.glob(str(REPORTS / "real_feed_unblock_status_20261106T*.json")))
    # pick the latest (C72 run will produce one)
    status_path = [s for s in status if "071417" not in s.split("/")[-1]]
    status_path = (sorted(status_path)[-1] if status_path else (status[-1] if status else None))
    status_obj = json.load(open(status_path)) if status_path else {}

    pytest_res = run_pytest()
    blocked = status_obj.get("blocked_families") or status_obj.get("families_blocked") or ["funding_basis_carry","cross_exchange_dual_venue_same_asset","term_structure_real_iv_vol_surface","intrabar_microstructure"]
    oos = c72_obj.get("oos_edge_proven", False)
    out = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "campaign": 72,
        "supersedes": "reports/strategy_edge_registry_20261106T071418Z.json",
        "oos_edge_proven": bool(oos),
        "pytest_full_suite": pytest_res,
        "artifacts": [p for p in [c72_path and "reports/"+Path(c72_path).name, status_path and "reports/"+Path(status_path).name] if p],
        "c72_hypothesis": "real_quote_volume Rolling Bowley (Quartile/Galton) Skewness (P75+P25-2*P50)/(P75-P25), rank/quartile asymmetry bounded [-1,1], shock MR (R-B, pre-stated; differs from C23/C40-C71 incl. C40 Fisher moment skewness & C62/C70/C71 dispersion magnitudes)",
        "c72_oos_result": {
            "oos_edge_proven": bool(oos),
            "any_exposure": c72_obj.get("any_exposure"),
            "all_costs_positive": c72_obj.get("all_costs_positive"),
            "beats_bh_rule": c72_obj.get("beats_bh_rule"),
            "aggregate": c72_obj.get("aggregate"),
        },
        "blocked_families_substantive": blocked,
        "notes": "Fail-closed. Real data only. No proxies/fabrication/threshold weakening. C72 R-B on validated real_quote_volume (Bowley quartile/Galton skewness, W=48, ZLB=168, rank/quartile asymmetry direction; distinct from C40 Fisher 3rd-moment skewness and from C62/C70/C71/C66 dispersion magnitudes — asymmetry coefficient vs spread size — and all C23/C40-C71); oos_edge_proven=false (pre-stated rule not met). Remaining families blocked_no_real_feed.",
    }
    out_path = REPORTS / f"strategy_edge_registry_{UTC}.json"
    out_path.write_text(json.dumps(out, indent=2, sort_keys=True, default=str) + "\n")
    print(out_path)
    print(json.dumps({"oos_edge_proven": out["oos_edge_proven"], "pytest_returncode": pytest_res["returncode"], "passed": pytest_res["passed"]}, indent=2))

if __name__ == "__main__":
    main()
