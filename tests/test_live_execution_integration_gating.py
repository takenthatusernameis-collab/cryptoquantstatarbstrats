from __future__ import annotations

import json
from pathlib import Path

import pytest


def test_live_execution_integration_preserves_gating():
    integration_path = Path("reports/live_execution_integration_mt.json")
    gating_path = Path("reports/portfolio_gating_mt.json")
    if not integration_path.exists() or not gating_path.exists():
        pytest.skip("Missing artifacts")
    integration = json.loads(integration_path.read_text(encoding="utf-8"))
    gating = json.loads(gating_path.read_text(encoding="utf-8"))

    assert integration.get("real_data_only") is True
    assert integration.get("fabricated_data") is False
    assert integration.get("type") == "live_execution_integration_mt"
    assert integration.get("integration_summary", {}).get("no_auto_lift_of_blocks") is True
    assert integration.get("integration_summary", {}).get("fail_closed") is True

    g_res = gating.get("results_by_timeframe") or {}
    i_res = integration.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        g_r = g_res[tf]
        i_r = i_res[tf]
        eligible_g = set(g_r.get("eligible_pairs") or [])
        eligible_i = set(i_r.get("eligible_pairs") or [])
        assert eligible_i == eligible_g
        for pname, iinfo in (i_r.get("pairs") or {}).items():
            if pname in eligible_g:
                assert iinfo.get("integration_allowed") is True
                assert iinfo.get("orders_allowed") is True
                assert iinfo.get("fills_allowed") is True
                assert iinfo.get("eligible") is True
            else:
                assert iinfo.get("integration_allowed") is False
                assert iinfo.get("orders_allowed") is False
                assert iinfo.get("fills_allowed") is False
                assert iinfo.get("eligible") is False
                assert float(iinfo.get("allocation_usdt", -1.0)) == 0.0
                rl = iinfo.get("rejection_log") or []
                assert isinstance(rl, list) and len(rl) >= 1
                br = iinfo.get("blocked_routes") or []
                assert isinstance(br, list) and len(br) >= 1
            prov = iinfo.get("provenance") or {}
            assert prov.get("real_data_only") is True
            gc = iinfo.get("gating_context") or {}
            assert gc.get("source_gating") == "reports/portfolio_gating_mt.json"
            linked = gc.get("linked_artifacts") or []
            assert "reports/portfolio_gating_mt.json" in linked
