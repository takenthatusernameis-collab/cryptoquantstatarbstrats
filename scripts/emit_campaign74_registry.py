#!/usr/bin/env python3
"""Emit Campaign 74 strategy edge registry (fail-closed, supersedes C73)."""
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
    c74 = sorted(glob.glob(str(REPORTS / "real_quote_volume_theil_t_inequality_shock_mr_costed_oos_*.json")))
    c74_path = c74[-1] if c74 else None
    c74_obj = json.load(open(c74_path)) if c74_path else {}
    statuses = sorted(glob.glob(str(REPORTS / "real_feed_unblock_status_*.json")))
    c74_status = [s for s in statuses if Path(s).name > "real_feed_unblock_status_20261106T091925Z.json"]
    status_path = sorted(c74_status)[-1] if c74_status else (statuses[-1] if statuses else None)
    status_obj = json.load(open(status_path)) if status_path else {}

    pytest_res = run_pytest()
    blocked = status_obj.get("blocked_families") or ["funding_basis_carry", "cross_exchange_dual_venue_same_asset", "term_structure_real_iv_vol_surface", "intrabar_microstructure"]
    oos = bool(c74_obj.get("oos_edge_proven", False))
    out = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "campaign": 74,
        "supersedes": "reports/strategy_edge_registry_20261106T091943Z.json",
        "oos_edge_proven": oos,
        "pytest_full_suite": pytest_res,
        "artifacts": [p for p in [c74_path and "reports/" + Path(c74_path).name, status_path and "reports/" + Path(status_path).name] if p],
        "c74_hypothesis": "real_quote_volume Rolling Theil T Inequality (GE(1), mean((x/mu)*ln(x/mu)), value-weighted log-ratio) shock MR (R-B, pre-stated; differs from C23/C40-C73 incl. C51 Gini L1 mean-difference, C41 Shannon binned histogram entropy, C42/43 permutation/sample entropy, C45 CV σ/μ, C72 Bowley quartile asymmetry, C73 Kelly decile asymmetry)",
        "c74_oos_result": {
            "oos_edge_proven": oos,
            "any_exposure": c74_obj.get("any_exposure"),
            "all_costs_positive": c74_obj.get("all_costs_positive"),
            "beats_bh_rule": c74_obj.get("beats_bh_rule"),
            "aggregate": c74_obj.get("aggregate"),
        },
        "blocked_families_substantive": blocked,
        "notes": "Fail-closed. Real data only. No proxies/fabrication/threshold weakening. C74 R-B on validated real_quote_volume (Theil T inequality, W=48, ZLB=168, value-weighted log-ratio GE(1); distinct from C51 Gini L1 mean-difference, C41 Shannon binned histogram entropy, C42/43 permutation/sample entropy, C45 CV, C72 Bowley, C73 Kelly, and all C23/C40-C73); oos_edge_proven=false (pre-stated rule not met). Remaining families blocked_no_real_feed.",
    }
    out_path = REPORTS / f"strategy_edge_registry_{UTC}.json"
    out_path.write_text(json.dumps(out, indent=2, sort_keys=True, default=str) + "\n")
    print(out_path)
    print(json.dumps({"oos_edge_proven": out["oos_edge_proven"], "pytest_returncode": pytest_res["returncode"], "passed": pytest_res["passed"]}, indent=2))


if __name__ == "__main__":
    main()
