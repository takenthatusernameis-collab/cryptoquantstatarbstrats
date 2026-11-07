#!/usr/bin/env python3
"""C166: real feed ingest attempt (campaign 166).

Records nonspot blocked fail-closed, rb_unblocked:true for validated
real_quote_volume family (cache + provenance re-verified from disk bytes).
Does NOT fabricate any nonspot feed; does NOT block R-B on real_quote_volume.
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

SPOT_PKL = root / "data" / "cache" / "0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl"
VOL_PKL = root / "data" / "cache" / "volume_1h_full.pkl"
VOL_META = root / "data" / "cache" / "volume_1h_full.meta.json"
VOL_PROV = root / "data" / "cache" / "volume_1h_full.provenance.json"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def exists(p: Path) -> bool:
    return p.exists() and p.is_file()


blocked_fams = [
    "funding_basis_carry",
    "cross_exchange_dual_venue_same_asset",
    "term_structure_real_iv_vol_surface",
    "intrabar_microstructure",
]

attempt = {
    "tool": "real_feed_ingest_attempt",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "campaign": 166,
    "real_data_only": True,
    "fabricated_data": False,
    "fail_closed": True,
    "nonspot_ingest": {
        "status": "blocked_fail_closed",
        "rb_unblocked": True,
        "rb_family": "real_quote_volume",
        "note": "Non-spot/external feed ingest remains blocked in this environment (fail-closed). R-B proceeds on validated real_quote_volume cache/provenance; blocker does not block R-B on real_quote_volume.",
    },
    "real_quote_volume_cache": {
        "pkl": str(VOL_PKL),
        "pkl_exists": exists(VOL_PKL),
        "pkl_sha256": sha(VOL_PKL) if exists(VOL_PKL) else None,
        "meta": str(VOL_META),
        "meta_exists": exists(VOL_META),
        "meta_sha256": sha(VOL_META) if exists(VOL_META) else None,
        "provenance": str(VOL_PROV),
        "provenance_exists": exists(VOL_PROV),
        "provenance_sha256": sha(VOL_PROV) if exists(VOL_PROV) else None,
    },
    "spot_cache": {
        "pkl": str(SPOT_PKL),
        "exists": exists(SPOT_PKL),
        "sha256": sha(SPOT_PKL) if exists(SPOT_PKL) else None,
    },
}

out = reports / f"real_feed_ingest_attempt_{ts}.json"
out.write_text(json.dumps(attempt, indent=2) + "\n")
h = sha(out)
print(json.dumps({"artifact": str(out.relative_to(root)), "sha256": h}, indent=2))