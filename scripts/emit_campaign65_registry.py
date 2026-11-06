#!/usr/bin/env python3
"""Emit Campaign 65 strategy_edge_registry superseding C64 registry (fail-closed)."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
SUPERSEDES = "reports/strategy_edge_registry_20261106T053524Z.json"


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

    c65_oos = sorted(REPORTS.glob("real_quote_volume_meanad_mean_centered_l1_dispersion_shock_mr_costed_oos_*.json"))
    oos_art = str(c65_oos[-1].relative_to(ROOT)) if c65_oos else None
    status_art = None
    for p in sorted(REPORTS.glob("real_feed_unblock_status_*.json"), reverse=True):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
            if d.get("campaign") == 65:
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
        "campaign": 65,
        "supersedes": SUPERSEDES,
        "oos_edge_proven": bool(oos_data.get("oos_edge_proven", False)),
        "pytest_full_suite": pytest_res,
        "artifacts": [a for a in [oos_art, status_art] if a],
        "c65_hypothesis": "real_quote_volume Rolling MeanAD mean(|x-mean(x)|) mean-centered L1 dispersion shock MR (R-B, pre-stated; differs from C23/C40-C64)",
        "c65_oos_result": {
            "oos_edge_proven": oos_data.get("oos_edge_proven", False),
            "n_assets_tested": oos_data.get("n_assets_tested"),
            "n_assets_with_exposure": oos_data.get("n_assets_with_exposure"),
            "n_oos_edge_proven": oos_data.get("n_oos_edge_proven"),
        },
        "blocked_families_substantive": [
            "funding_basis_carry",
            "cross_exchange_dual_venue_same_asset",
            "term_structure_real_iv_vol_surface",
            "intrabar_microstructure",
        ],
        "notes": "Fail-closed. Real data only. No proxies/fabrication/threshold weakening. C65 R-B on validated real_quote_volume (Rolling MeanAD mean(|x-mean(x)|) mean-centered L1 dispersion shock MR; distinct from C61 MAD median-centered L1, C63 GMD pairwise dispersion, C64 Range max-min extremes, C62 IQR rank quartile spread, C48 STD/L2 mean-based, C56 CV relative ratio, C49/C50 higher moments, C57/C58/C60 entropies, C59 Hurst fractal scaling, C51 autocorr, C52-C55 correlations/beta, and all C23/C40-C64 level/ROC/cumulative/partition/imbalance transforms); oos_edge_proven=false unless pre-stated rule passes. Remaining families blocked_no_real_feed.",
    }
    out = REPORTS / f"strategy_edge_registry_{ts}.json"
    out.write_text(json.dumps(reg, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"wrote": str(out), "oos_edge_proven": reg["oos_edge_proven"], "pytest": pytest_res}))


if __name__ == "__main__":
    main()
