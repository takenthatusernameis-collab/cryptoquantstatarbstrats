#!/usr/bin/env python3
"""Campaign 51 fail-closed real-feed unblock status (delta vs C50)."""
from __future__ import annotations
import json, sys
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from data.real_feed_loader import generate_unblock_status_report

def main():
    cache = ROOT / 'data' / 'cache'
    reports = ROOT / 'reports'
    prior = 'reports/real_feed_unblock_status_20261106T023842Z.json'
    ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    report = generate_unblock_status_report(cache, campaign=51, reports_dir=str(reports), prior_report=prior)
    out = reports / f'real_feed_unblock_status_{ts}.json'
    out.write_text(json.dumps(report, indent=2, default=str) + '\n', encoding='utf-8')
    delta = report.get('campaign_delta') or {}
    print(json.dumps({'wrote': str(out), 'path_r_triggered': report.get('path_r_triggered'),
                      'delta_changed': delta.get('changed')}))

if __name__ == '__main__':
    main()
