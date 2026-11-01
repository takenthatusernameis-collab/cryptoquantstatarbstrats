from __future__ import annotations

import json
from pathlib import Path

import pytest


def test_realtime_monitoring_preserves_gating():
    monitoring_path = Path("reports/realtime_monitoring_mt.json")
    gating_path = Path("reports/portfolio_gating_mt.json")
    if not monitoring_path.exists() or not gating_path.exists():
        pytest.skip("Missing artifacts")
    monitoring = json.loads(monitoring_path.read_text(encoding="utf-8"))
    gating = json.loads(gating_path.read_text(encoding="utf-8"))

    assert monitoring.get("real_data_only") is True
    assert monitoring.get("fabricated_data") is False
    assert monitoring.get("type") == "realtime_monitoring_mt"
    assert monitoring.get("monitoring_summary", {}).get("no_auto_lift_of_blocks") is True
    assert monitoring.get("monitoring_summary", {}).get("fail_closed") is True

    g_res = gating.get("results_by_timeframe") or {}
    m_res = monitoring.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        g_r = g_res[tf]
        m_r = m_res[tf]
        eligible_g = set(g_r.get("eligible_pairs") or [])
        eligible_m = set(m_r.get("eligible_pairs") or [])
        assert eligible_m == eligible_g
        for pname, minfo in (m_r.get("pairs") or {}).items():
            if pname in eligible_g:
                assert minfo.get("eligible") is True
                assert minfo.get("gate_respected") is True
                assert minfo.get("auto_lift_forbidden") is True
            else:
                assert minfo.get("eligible") is False
                assert minfo.get("gate_respected") is True
                assert minfo.get("auto_lift_forbidden") is True
                rl = minfo.get("rejection_log") or []
                assert isinstance(rl, list) and len(rl) >= 1
                br = minfo.get("blocked_routes") or []
                assert isinstance(br, list) and len(br) >= 1
            prov = minfo.get("provenance") or {}
            assert prov.get("real_data_only") is True
            gc = minfo.get("gating_context") or {}
            assert gc.get("source_gating") == "reports/portfolio_gating_mt.json"
            linked = gc.get("linked_artifacts") or []
            assert "reports/portfolio_gating_mt.json" in linked
