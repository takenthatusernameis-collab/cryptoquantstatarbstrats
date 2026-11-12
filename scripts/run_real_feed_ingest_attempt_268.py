#!/usr/bin/env python3
"""C268 ingest attempt: non-spot blocked fail-closed (no network). Records paths/sha256s for spot+volume caches."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cache_dir = root / "data" / "cache"
reports = root / "reports"
reports.mkdir(exist_ok=True)
ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

CACHES = [
    ("spot_pkl", cache_dir / "0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl"),
    ("spot_meta", cache_dir / "0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.meta.json"),
    ("volume_pkl", cache_dir / "volume_1h_full.pkl"),
    ("volume_meta", cache_dir / "volume_1h_full.meta.json"),
    ("volume_provenance", cache_dir / "volume_1h_full.provenance.json"),
]


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    verified = []
    for label, p in CACHES:
        if not p.exists():
            raise SystemExit(f"FATAL: required cache missing: {p}")
        verified.append({"label": label, "path": str(p.relative_to(root)), "sha256": sha256_file(p)})
    out = {
        "generated_at_utc": ts,
        "campaign": 268,
        "real_data_only": True,
        "fabricated_data": False,
        "nonspot_ingest": "blocked_fail_closed_rb_unblocked",
        "network_refetch": False,
        "caches_verified": verified,
    }
    out_path = reports / f"real_feed_ingest_attempt_{ts}.json"
    out_path.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({"ingest": str(out_path.relative_to(root)), "ingest_sha256": sha256_file(out_path)}, indent=2))


if __name__ == "__main__":
    main()
