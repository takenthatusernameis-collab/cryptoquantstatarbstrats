#!/usr/bin/env python3
import json, subprocess
from pathlib import Path
from datetime import datetime, timezone

root = Path('/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats')
reports = root / 'reports'
ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')

# Run tests
env = dict(**os.environ) if False else None
cmd = "PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages /home/runner/work/_temp/kilo-home/.local/bin/pytest -q"
res = subprocess.run(cmd, shell=True, cwd=str(root), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out = res.stdout.decode()
err = res.stderr.decode()
# parse
passed=skipped=failed=0
for line in out.splitlines():
    if 'passed' in line or 'failed' in line or 'skipped' in line:
        # crude parse
        pass
# try to extract
import re
m = re.search(r'(\d+)\s+passed', out)
if m: passed = int(m.group(1))
m = re.search(r'(\d+)\s+skipped', out)
if m: skipped = int(m.group(1))
m = re.search(r'(\d+)\s+failed', out)
if m: failed = int(m.group(1))

# load previous registry
prev = reports / 'strategy_edge_registry_20261105T084647Z.json'
with open(prev) as fh:
    reg = json.load(fh)

# update
reg_new = dict(reg)
reg_new['report'] = 'strategy_edge_registry'
reg_new['supersedes'] = prev.name
reg_new['generated_at_utc'] = datetime.now(timezone.utc).isoformat()
reg_new['mandate'] = "PRIORITY 6 Deliverable C — superseding registry: adds Deliverable A (Donchian breakout + vol-filter, real cached spot, net-of-cost WF IS/OOS) + Deliverable B feed status; fail-closed, real data only, no threshold weakening."
reg_new['pytest'] = {
  "command": cmd,
  "passed": passed,
  "skipped": skipped,
  "warnings": None,
  "failed": failed,
  "duration_s": None,
  "scope": "full tests/",
  "note": "rerun on P6 with env deps on PYTHONPATH"
}
# new artifacts
reg_new['new_artifacts_this_session'] = [
  "reports/spot_breakout_volfilter_costed_oos_20261105T093626Z.json",
  "reports/real_feed_unblock_status_20261105T093642Z.json"
]
# add family
fam_break = {
  "family": "donchian_breakout_volfilter",
  "data_status": "real_cached_verified",
  "diagnostic_evidence": [
    {
      "artifact": "reports/spot_breakout_volfilter_costed_oos_20261105T093626Z.json",
      "key_metrics": {
        "assets": 11,
        "bars": 5112,
        "window": "2026-04-01..2026-10-30",
        "interval": "1h",
        "walk_forward": {"mode": "rolling", "train_bars": 720, "test_bars": 168, "step_bars": 168},
        "cost_grid_bps_fee_slippage": [[0,0],[5,0],[0,5],[5,5],[10,0],[0,10],[10,10],[20,0],[0,20],[20,20]],
        "n_oos_edge_proven": 0,
        "n_assets_all_slices_oos_net_positive": 0,
        "n_assets_all_slices_beat_benchmark": 0,
        "aggregate_oos_edge_proven_fail_closed": False,
        "family": "donchian_breakout_volfilter"
      }
    }
  ],
  "strategy_honors_fail_closed": {"verified": True, "method": "report sets oos_edge_proven=false, real_data_only=true, fabricated_data=false, fail_closed=true, no_threshold_weakening=true"},
  "actionable_next_step": "NO PROVEN NET-OF-COST OOS EDGE on real cached spot 1h for this pre-stated family. Do not claim edge; do not tune in-sample. Deprioritize until new real data/structure exists."
}
# append if not present
fam_names = [f['family'] for f in reg_new.get('families',[])]
if 'donchian_breakout_volfilter' not in fam_names:
    reg_new['families'].append(fam_break)
else:
    for i,f in enumerate(reg_new['families']):
        if f['family']=='donchian_breakout_volfilter':
            reg_new['families'][i]=fam_break
            break
# ensure feed status updated
reg_new['real_feed_status']['feed_unblock_status_artifact'] = 'reports/real_feed_unblock_status_20261105T093642Z.json'

out_path = reports / f'strategy_edge_registry_{ts}.json'
with open(out_path,'w') as fh:
    json.dump(reg_new, fh, indent=2)
print(out_path, passed, skipped, failed)
