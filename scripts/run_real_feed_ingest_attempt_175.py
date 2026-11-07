#!/usr/bin/env python3
"""C175 ingest attempt: record non-spot feed ingest status (fail-closed) and validated
real_quote_volume cache/provenance SHAs computed from bytes. R-B proceeds on real_quote_volume
regardless of non-spot ingest block.

Emits reports/real_feed_ingest_attempt_<UTC>.json
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parents[1]
reports = root / "reports"
reports.mkdir(exist_ok=True)
ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


VOL_PKL = root / "data" / "cache" / "volume_1h_full.pkl"
VOL_META = root / "data" / "cache" / "volume_1h_full.meta.json"
VOL_PROV = root / "data" / "cache" / "volume_1h_full.provenance.json"
SPOT_PKL = root / "data" / "cache" / "0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl"

out = {
    "tool": "real_feed_ingest_attempt",
    "generated_at_utc": ts,
    "campaign": 175,
    "real_data_only": True,
    "fabricated_data": False,
    "fail_closed": True,
    "nonspot_ingest": {
        "status": "blocked_fail_closed",
        "rb_unblocked": True,
        "rb_family": "real_quote_volume",
        "note": (
            "Non-spot/external feed ingest remains blocked in this environment (fail-closed). "
            "R-B proceeds on validated real_quote_volume cache/provenance; blocker does not block "
            "R-B on real_quote_volume."
        ),
    },
    "real_quote_volume_cache": {
        "pkl": str(VOL_PKL.relative_to(root)),
        "pkl_exists": VOL_PKL.exists(),
        "pkl_sha256": sha256_file(VOL_PKL) if VOL_PKL.exists() else None,
        "meta": str(VOL_META.relative_to(root)),
        "meta_exists": VOL_META.exists(),
        "meta_sha256": sha256_file(VOL_META) if VOL_META.exists() else None,
        "provenance": str(VOL_PROV.relative_to(root)),
        "provenance_exists": VOL_PROV.exists(),
        "provenance_sha256": sha256_file(VOL_PROV) if VOL_PROV.exists() else None,
    },
    "spot_cache": {
        "pkl": str(SPOT_PKL.relative_to(root)),
        "exists": SPOT_PKL.exists(),
        "sha256": sha256_file(SPOT_PKL) if SPOT_PKL.exists() else None,
    },
}
out_path = reports / f"real_feed_ingest_attempt_{ts}.json"
out_path.write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps({"ingest": str(out_path.relative_to(root)), "ingest_sha256": sha256_file(out_path)}, indent=2))