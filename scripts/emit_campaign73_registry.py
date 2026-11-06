#!/usr/bin/env python3
"""Emit Campaign 73 strategy edge registry (fail-closed, supersedes C72)."""
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
    passed = failed = skipped = errors = 0
    for line in reversed(tail):
        if "passed" in line or "failed" in line or "error" in line:
            import re

            def grab(word):
                m = re.search(r"(\d+) " + word, line)
                return int(m.group(1)) if m else 0

            passed = grab("passed")
            failed = grab("failed")
            skipped = grab("skipped")
            errors = grab("error")
            break
    return {
        "command": " ".join(cmd),
        "returncode": p.returncode,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "errors": errors,
        "summary_tail": tail,
    }


def main():
    c73 = sorted(glob.glob(str(REPORTS / "real_quote_volume_peak_trough_drawdown_shock_mr_costed_oos_*.json")))
    c73_path = c73[-1] if c73 else None
    c73_obj = json.load(open(c73_path)) if c73_path else {}
    status = sorted(glob.glob(str(REPORTS / "real_feed_unblock_status_20261106T*.json")))
    status_path = [s for s in status if "081536" not in s.split("/")[-1]]
    status_path = (sorted(status_path)[-1] if status_path else (status[-1] if status else None))
    status_obj = json.load(open(status_path)) if status_path else {}

    pytest_res = run_pytest()
    blocked = status_obj.get("blocked_families") or status_obj.get("families_blocked") or [
        "funding_basis_carry",
        "cross_exchange_dual_venue_same_asset",
        "term_structure_real_iv_vol_surface",
        "intrabar_microstructure",
    ]
    oos = c73_obj.get("oos_edge_proven", False)
    out = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "campaign": 73,
        "supersedes": "reports/strategy_edge_registry_20261106T081541Z.json",
        "oos_edge_proven": bool(oos),
        "pytest_full_suite": pytest_res,
        "artifacts": [p for p in [c73_path and "reports/" + Path(c73_path).name, status_path and "reports/" + Path(status_path).name] if p],
        "c73_hypothesis": "real_quote_volume Rolling Volume Peak-to-Trough Drawdown Shock Mean Reversion (DD=(Peak-qvol)/Peak, Peak=rolling max W=48; zscore(DD,ZLB=168); fade d_z>=1.25 LONG / d_z<=-1.25 SHORT; exit |d_z|<0.25 or hold>=12; t->t+1; WF 720/168/168; cost grid 0-40bps; B&H benchmark). R-B, pre-stated; genuinely distinct from C23/C40-C72 (no moment/dispersion-magnitude/entropy/Hurst/autocorr/corr/beta/imbalance/level-breakout; first peak-to-trough drawdown transform on real_quote_volume; differs from C72 Bowley quartile asymmetry and C40 Fisher 3rd-moment skewness)",
        "c73_oos_result": {
            "oos_edge_proven": bool(oos),
            "any_exposure": c73_obj.get("any_exposure"),
            "all_costs_positive": c73_obj.get("all_costs_positive"),
            "beats_bh_rule": c73_obj.get("beats_bh_rule"),
            "aggregate": c73_obj.get("aggregate"),
        },
        "blocked_families_substantive": blocked,
        "notes": "Fail-closed. Real data only. No proxies/fabrication/threshold weakening. C73 R-B on validated real_quote_volume (peak-to-trough drawdown shock MR, W=48, ZLB=168, genuinely distinct from C23/C40-C72); oos_edge_proven=false unless pre-stated rule passes. Remaining families blocked_no_real_feed.",
    }
    out_path = REPORTS / f"strategy_edge_registry_{UTC}.json"
    out_path.write_text(json.dumps(out, indent=2, sort_keys=True, default=str) + "\n")
    print(out_path)
    print(json.dumps({"oos_edge_proven": out["oos_edge_proven"], "pytest_returncode": pytest_res["returncode"], "passed": pytest_res["passed"]}, indent=2))


if __name__ == "__main__":
    main()
