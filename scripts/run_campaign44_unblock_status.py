#!/usr/bin/env python3
"""Campaign 44 feed-unblock recheck (fail-closed, delta vs prior)."""
from __future__ import annotations

import glob
import json
from datetime import datetime, timezone
from pathlib import Path

from data.real_feed_loader import generate_unblock_status_report

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
CACHE = ROOT / "data" / "cache"


def _now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _latest(pattern: str) -> str | None:
    ps = sorted(glob.glob(str(REPORTS / pattern)))
    return ps[-1] if ps else None


def main() -> None:
    prior = _latest("real_feed_unblock_status_*.json")
    stamp = _now_stamp()
    out_path = REPORTS / f"real_feed_unblock_status_{stamp}.json"

    report = generate_unblock_status_report(
        CACHE,
        campaign=44,
        reports_dir=REPORTS,
        prior_report=prior,
    )

    envelope = {
        "type": "real_feed_unblock_status_campaign44",
        "campaign": 44,
        "mandate": "cryptoquantstatarbstrats - Campaign 44 fail-closed feed-unblock "
        "recheck with delta vs prior. Real data only. No proxies labeled real. "
        "No fabricated feeds/provenance.",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "computed_at_stamp": stamp,
        "real_data_only": True,
        "fabricated_data": False,
        "fail_closed": True,
        "no_threshold_weakening": True,
        "no_auto_lift_of_blocks": True,
        "prior_report": prior,
        "report": report,
    }
    out_path.write_text(
        json.dumps(envelope, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Wrote {out_path}")
    print(
        "campaign_delta.honest_assessment="
        f"{report.get('campaign_delta', {}).get('honest_assessment')}"
    )
    print("changed=", report.get("campaign_delta", {}).get("changed"))


if __name__ == "__main__":
    main()
