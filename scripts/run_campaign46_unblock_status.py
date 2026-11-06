#!/usr/bin/env python3
"""Campaign 46 real-feed unblock status (fail-closed)."""
from __future__ import annotations
import json, sys
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from data.real_feed_loader import generate_unblock_status_report  # noqa: E402

CACHE_DIR = ROOT / "data" / "cache"
REPORTS_DIR = ROOT / "reports"
PRIOR = REPORTS_DIR / "real_feed_unblock_status_20261106T014124Z.json"

def main():
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    rep = generate_unblock_status_report(CACHE_DIR, campaign=46, reports_dir=str(REPORTS_DIR), prior_report=str(PRIOR) if PRIOR.exists() else None)
    rep["computed_at_stamp"] = ts
    rep["campaign"] = 46
    out = REPORTS_DIR / f"real_feed_unblock_status_{ts}.json"
    out.write_text(json.dumps(rep, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"wrote": str(out), "path_r_triggered": rep.get("path_r_triggered"), "blocked_families": rep.get("blocked_families"), "delta_vs_prior": rep.get("delta_vs_prior")}, indent=2))

if __name__ == "__main__":
    main()
