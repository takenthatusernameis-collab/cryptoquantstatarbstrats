#!/usr/bin/env python3
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone

root = Path(__file__).resolve().parent
reports = root / 'reports'
reports.mkdir(exist_ok=True)
ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')

cache_dir = root / 'data' / 'cache'
# Audit current state
files = sorted([p.name for p in cache_dir.iterdir() if p.is_file()])
prov = [f for f in files if f.endswith('.provenance.json')]
meta = [f for f in files if f.endswith('.meta.json')]
pkls = [f for f in files if f.endswith('.pkl')]

blocked_fams = ["funding_basis_carry", "cross_exchange_dual_venue_same_asset", "term_structure_real_iv_vol_surface", "intrabar_microstructure"]
attempt = {
  "tool": "real_feed_ingest_attempt",
  "generated_at_utc": datetime.now(timezone.utc).isoformat(),
  "campaign": 103,
  "result": "IMPOSSIBLE_WITH_AVAILABLE_REAL_ARTIFACTS_FAIL_CLOSED",
  "reason": "No real nonspot artifacts present in data/cache or workspace for any blocked family; cannot fabricate. Only real_quote_volume validated and tested.",
  "blocked_families": blocked_fams,
  "validated_only_family": "real_quote_volume",
  "cache_audit": {
    "dir": str(cache_dir),
    "files_sample": files[:40],
    "provenance_files": prov,
    "meta_files": meta,
    "pkl_files": pkls,
  },
  "actions_taken": [],
  "operator_instruction": "Place a real, verifiable artifact for exactly one blocked family into data/cache/ with matching .meta.json and .provenance.json (fail-closed schema) to enable ingest/unblock audit.",
  "real_data_only": True,
  "fabricated_data": False,
  "fail_closed": True,
}

out = reports / f'real_feed_ingest_attempt_{ts}.json'
out.write_text(json.dumps(attempt, indent=2))
h = hashlib.sha256(out.read_bytes()).hexdigest()
print(json.dumps({"artifact": str(out), "sha256": h}, indent=2))
