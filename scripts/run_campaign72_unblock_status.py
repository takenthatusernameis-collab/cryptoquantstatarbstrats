#!/usr/bin/env python3
"""Campaign 72 unblock status (fail-closed, real data only). Delta vs C71."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from data.real_feed_loader import generate_unblock_status_report  # noqa: E402

if __name__ == "__main__":
    cache = ROOT / "data" / "cache"
    prior = "reports/real_feed_unblock_status_20261106T071417Z.json"
    path = generate_unblock_status_report(cache, campaign=72, reports_dir=str(ROOT / "reports"), prior_report=prior)
    print(path)
