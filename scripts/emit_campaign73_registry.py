#!/usr/bin/env python3
"""Emit Campaign 73 strategy edge registry (fail-closed, supersedes C72)."""
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
    p = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=900)
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
    c73 = sorted(glob.glob(str(REPORTS / "real_quote_volume_kelly_decile_skewness_shock_mr_costed_oos_*.json")))
    c73_path = c73[-1] if c73 else None
    c73_obj = json.load(open(c73_path)) if c73_path else {}
    statuses = sorted(glob.glob(str(REPORTS / "real_feed_unblock_status_*.json")))
    c73_status = [s for s in statuses if Path(s).name > "real_feed_unblock_status_20261106T081536Z.json"]
    status_path = sorted(c73_status)[-1] if c73_status else (statuses[-1] if statuses else None)
    status_obj = json.load(open(status_path)) if status_path else {}

    pytest_res = run_pytest()
    blocked = status_obj.get("blocked_families") or ["funding_basis_carry", "cross_exchange_dual_venue_same_asset", "term_structure_real_iv_vol_surface", "intrabar_microstructure"]
    oos = bool(c73_obj.get("oos_edge_proven", False))
    out = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "campaign": 73,
        "supersedes": "reports/strategy_edge_registry_20261106T081541Z.json",
        "oos_edge_proven": oos,
        "pytest_full_suite": pytest_res,
        "artifacts": [p for p in [c73_path and "reports/" + Path(c73_path).name, status_path and "reports/" + Path(status_path).name] if p],
        "c73_hypothesis": "real_quote_volume Rolling Kelly (Decile) Skewness (P90+P10-2*P50)/(P90-P10), rank/decile asymmetry bounded [-1,1], shock MR (R-B, pre-stated; differs from C23/C40-C72 incl. C66 IDR magnitude same decile cutpoints, C72 Bowley quartile asymmetry, C40 Fisher moment skewness)",
        "c73_oos_result": {
            "oos_edge_proven": oos,
            "any_exposure": c73_obj.get("any_exposure"),
            "all_costs_positive": c73_obj.get("all_costs_positive"),
            "beats_bh_rule": c73_obj.get("beats_bh_rule"),
            "aggregate": c73_obj.get("aggregate"),
        },
        "blocked_families_substantive": blocked,
        "notes": "Fail-closed. Real data only. No proxies/fabrication/threshold weakening. C73 R-B on validated real_quote_volume (Kelly decile skewness, W=48, ZLB=168, rank/decile asymmetry direction; distinct from C66 IDR P90-P10 dispersion magnitude on same decile cutpoints — asymmetry ratio vs magnitude — distinct from C72 Bowley quartile asymmetry (P25/P75) — decile vs quartile tail sensitivity — distinct from C40 Fisher 3rd-moment skewness and all C23/C40-C72); oos_edge_proven=false (pre-stated rule not met). Remaining families blocked_no_real_feed.",
    }
    out_path = REPORTS / f"strategy_edge_registry_{UTC}.json"
    out_path.write_text(json.dumps(out, indent=2, sort_keys=True, default=str) + "\n")
    print(out_path)
    print(json.dumps({"oos_edge_proven": out["oos_edge_proven"], "pytest_returncode": pytest_res["returncode"], "passed": pytest_res["passed"]}, indent=2))


if __name__ == "__main__":
    main()
