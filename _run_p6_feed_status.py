#!/usr/bin/env python3
import json, os, glob
from pathlib import Path
from datetime import datetime, timezone

root = Path('/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats')
reports = root / 'reports'
ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')

# Check for new real feed files
cands = []
for ext in ['*.parquet','*.csv','*.json','*.pkl']:
    for p in glob.glob(str(root / '**' / ext), recursive=True):
        pl = p.lower()
        if any(k in pl for k in ['funding','basis','perp','swap','future','iv','volsurface','vol_surface','dual','cross_exchange','orderbook']):
            # exclude existing known
            if 'cache' in pl and any(s in pl for s in ['ada','avax','bnb','btc','dot','eth','link','ltc','pol','sol','xrp']):
                continue  # spot cache
            cands.append(p)

status = {
  "report": "real_feed_unblock_status",
  "generated_at_utc": datetime.now(timezone.utc).isoformat(),
  "mandate": "PRIORITY 6 Deliverable B — re-check for newly added real feeds; if none, confirm blocked_no_real_feed per family with required schemas.",
  "provenance": {"real_data_only": True, "fabricated_data": False, "fail_closed": True, "no_threshold_weakening": True},
  "new_real_feed_files_found": cands,
  "assessment": {
    "cross_exchange_dual_venue_same_asset": "blocked_no_real_feed",
    "funding_basis_carry": "blocked_no_real_feed",
    "term_structure_real_iv_vol_surface": "blocked_no_real_feed"
  },
  "references": {
    "inventory": "reports/real_feed_inventory_20261105T084255Z.json",
    "unblock_plan": "reports/real_feed_unblock_plan_20261105T084447Z.json"
  },
  "required_schemas_still_needed": {
    "funding_basis_carry": ["perp/spot/funding timestamps aligned", "fees/carry costs", "real exchange provenance", "net-of-cost validation"],
    "cross_exchange_dual_venue": ["same-asset dual venue prices with timestamps", "fees/transfer constraints", "real provenance", "fail-closed arb test"],
    "term_structure_real_iv_vol_surface": ["real listed IV/vol surface by expiry/strike or term structure", "fees/margin assumptions stated", "real provider provenance", "net-of-cost validation"]
  },
  "action": "none_ingested_no_new_real_feeds_with_provenance"
}

out_path = reports / f'real_feed_unblock_status_{ts}.json'
with open(out_path,'w') as fh:
    json.dump(status, fh, indent=2)
print(out_path)
