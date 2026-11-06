#!/usr/bin/env python3
import json, hashlib, subprocess, os
from pathlib import Path
from datetime import datetime, timezone

root = Path(__file__).resolve().parent
reports = root / 'reports'

# Get latest files
rb_c102 = 'reports/real_quote_volume_approximate_entropy_shock_mr_costed_oos_20261106T201839Z.json'
rb_c103 = max((p for p in reports.glob('real_quote_volume_spectral_entropy_shock_mr_costed_oos_*.json')), key=lambda p: p.stat().st_mtime)
ingest_c103 = max((p for p in reports.glob('real_feed_ingest_attempt_*.json')), key=lambda p: p.stat().st_mtime)

# pytest
r = subprocess.run(['.venv/bin/python', '-m', 'pytest', '-q'], cwd=root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
out = r.stdout.decode()
# Try to parse summary
passed = skipped = failed = None
# simple parse
for line in out.splitlines()[-15:]:
    if 'passed' in line or 'failed' in line or 'skipped' in line:
        pass
# fallback scan
import re
m = re.findall(r'(\d+) passed', out)
if m: passed = int(m[-1])
m = re.findall(r'(\d+) skipped', out)
if m: skipped = int(m[-1])
m = re.findall(r'(\d+) failed', out)
if m: failed = int(m[-1])
if failed is None: failed = 0
rc = r.returncode

ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
reg = {
  "tool": "strategy_edge_registry",
  "generated_at_utc": datetime.now(timezone.utc).isoformat(),
  "campaign": 103,
  "supersedes": "reports/strategy_edge_registry_20261106T202343Z.json",
  "supersedes_sha256": hashlib.sha256((root / 'reports/strategy_edge_registry_20261106T202343Z.json').read_bytes()).hexdigest(),
  "references": {
    "prior_unblock": "reports/real_feed_unblock_status_20261106T130243Z.json",
    "prior_unblock_sha256": hashlib.sha256((root / 'reports/real_feed_unblock_status_20261106T130243Z.json').read_bytes()).hexdigest(),
    "prior_registry": "reports/strategy_edge_registry_20261106T202343Z.json",
    "prior_registry_sha256": hashlib.sha256((root / 'reports/strategy_edge_registry_20261106T202343Z.json').read_bytes()).hexdigest(),
    "c102_rb": rb_c102,
    "c102_rb_sha256": hashlib.sha256((root / rb_c102).read_bytes()).hexdigest(),
    "c103_rb": str(rb_c103).replace(str(root)+'/',''),
    "c103_rb_sha256": hashlib.sha256(rb_c103.read_bytes()).hexdigest(),
  },
  "pytest": {
    "command": ".venv/bin/python -m pytest -q",
    "passed": passed,
    "skipped": skipped,
    "failed": failed,
    "returncode": rc,
  },
  "campaign103_r_b": {
    "artifact": str(rb_c103).replace(str(root)+'/',''),
    "sha256": hashlib.sha256(rb_c103.read_bytes()).hexdigest(),
    "candidate": "VOLUME_SPECTRAL_ENTROPY_SHOCK_MR (Spectral/PDS entropy of log-volume changes, periodogram normalized Shannon entropy over positive freqs, fade spectral-entropy shocks vs baseline)",
    "pre_stated_distinctness": "Grep-verified absent before impl: spectral_entropy|power_spectral.*entropy|psd.*entropy not present in prior real_quote_volume costed OOS reports/scripts. Distinct from ApEn/SampleEn/permutation/shannon/renyi block-frequency entropies, DFA(C101), Hurst/RS, Higuchi/Katz/Petrosian FD, LZ76, Hjorth/TKEO, ZCR(C100).",
    "oos_edge_proven": json.loads(rb_c103.read_text())['oos_edge_proven'],
    "aggregate": json.loads(rb_c103.read_text())['aggregate'],
    "fail_closed": True,
  },
  "nonspot_blockers": {
    "status": "FAIL_CLOSED_BLOCKED_NO_REAL_ARTIFACT",
    "blocked_families": ["funding_basis_carry", "cross_exchange_dual_venue_same_asset", "term_structure_real_iv_vol_surface", "intrabar_microstructure"],
    "validated_only_family": "real_quote_volume",
    "ingest_attempt": str(ingest_c103).replace(str(root)+'/',''),
    "ingest_attempt_sha256": hashlib.sha256(ingest_c103.read_bytes()).hexdigest(),
    "no_stale_cache_rescan": True,
  },
  "edge_rule_exact": "oos_edge_proven=true IFF OOS exposure>0 AND all cost slices OOS net sum>0 AND mean OOS net mean beats mean B&H OOS net mean on same WF windows; else false.",
  "overall_oos_edge_proven": False,
  "fail_closed": True,
  "real_data_only": True,
  "fabricated_data": False,
}

out = reports / f'strategy_edge_registry_{ts}.json'
out.write_text(json.dumps(reg, indent=2))
h = hashlib.sha256(out.read_bytes()).hexdigest()
print(json.dumps({"artifact": str(out), "sha256": h}, indent=2))
