from __future__ import annotations

import json
from pathlib import Path

import pytest


def test_drift_monitor_schema_and_invariants():
    drift_path = Path("reports/drift_monitor_mt.json")
    gating_path = Path("reports/portfolio_gating_mt.json")
    alerts_path = Path("reports/alerting_rules_mt.json")
    if not drift_path.exists() or not gating_path.exists() or not alerts_path.exists():
        pytest.skip("Missing artifacts")
    drift = json.loads(drift_path.read_text(encoding="utf-8"))
    gating = json.loads(gating_path.read_text(encoding="utf-8"))
    alerts = json.loads(alerts_path.read_text(encoding="utf-8"))

    assert drift.get("real_data_only") is True
    assert drift.get("fabricated_data") is False
    assert drift.get("type") == "drift_monitor_mt"
    assert drift.get("monitor_summary", {}).get("auto_lift_blocks") is False
    assert drift.get("monitor_summary", {}).get("drift_never_lifts_gating") is True

    g_res = gating.get("results_by_timeframe") or {}
    d_res = drift.get("results_by_timeframe") or {}
    a_res = alerts.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        g_r = g_res[tf]
        d_r = d_res[tf]
        a_r = a_res[tf]
        eligible_g = set(g_r.get("eligible_pairs") or [])
        for pname, dinfo in (d_r.get("pairs") or {}).items():
            assert dinfo.get("auto_lift_blocks") is False
            prov = dinfo.get("provenance") or {}
            assert prov.get("real_data_only") is True
            gc = dinfo.get("gating_context") or {}
            assert gc.get("source_gating") == "reports/portfolio_gating_mt.json"
            if pname in eligible_g:
                assert dinfo.get("drift_alerts") == []
            else:
                br = dinfo.get("blocked_routes") or []
                assert isinstance(br, list) and len(br) >= 1

        for pname, ainfo in (a_r.get("pairs") or {}).items():
            prov = ainfo.get("provenance") or {}
            assert prov.get("real_data_only") is True
            gc = ainfo.get("gating_context") or {}
            assert gc.get("source_gating") == "reports/portfolio_gating_mt.json"
            if pname not in eligible_g:
                assert ainfo.get("eligible") is False
                br = ainfo.get("blocked_routes") or []
                assert isinstance(br, list) and len(br) >= 1
                # alerts must not suggest allocation to blocked pairs
            rules = ainfo.get("alert_rules") or []
            assert isinstance(rules, list) and len(rules) >= 1
