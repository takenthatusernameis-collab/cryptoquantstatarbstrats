from __future__ import annotations

import json
from pathlib import Path

import pytest


def test_position_sizing_enforcement_schema():
    sizing_path = Path("reports/position_sizing_enforcement_mt.json")
    gating_path = Path("reports/portfolio_gating_mt.json")
    if not sizing_path.exists() or not gating_path.exists():
        pytest.skip("Missing artifacts")
    sizing = json.loads(sizing_path.read_text(encoding="utf-8"))
    gating = json.loads(gating_path.read_text(encoding="utf-8"))

    assert sizing.get("real_data_only") is True
    assert sizing.get("fabricated_data") is False
    assert sizing.get("type") == "position_sizing_enforcement_mt"
    assert sizing.get("sizing_summary", {}).get("fail_closed") is True
    assert sizing.get("sizing_summary", {}).get("no_auto_lift_blocks") is True

    g_res = gating.get("results_by_timeframe") or {}
    s_res = sizing.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        g_r = g_res[tf]
        s_r = s_res[tf]
        eligible_g = set(g_r.get("eligible_pairs") or [])
        eligible_s = set(s_r.get("eligible_pairs") or [])
        assert eligible_s == eligible_g
        for pname, sinfo in (s_r.get("pairs") or {}).items():
            assert sinfo.get("sizing_enforced") is True
            if pname in eligible_g:
                assert sinfo.get("eligible") is True
                assert sinfo.get("position_increase_allowed") is True
                assert float(sinfo.get("position_size_usdt", 0.0)) >= 0.0
            else:
                assert sinfo.get("eligible") is False
                assert float(sinfo.get("position_size_usdt", -1.0)) == 0.0
                assert float(sinfo.get("max_position_limit_usdt", -1.0)) == 0.0
                assert sinfo.get("position_increase_allowed") is False
                rl = sinfo.get("rejection_log") or []
                assert isinstance(rl, list) and len(rl) >= 1
                br = sinfo.get("blocked_routes") or []
                assert isinstance(br, list) and len(br) >= 1
            prov = sinfo.get("provenance") or {}
            assert prov.get("real_data_only") is True
            gc = sinfo.get("gating_context") or {}
            assert gc.get("source_gating") == "reports/portfolio_gating_mt.json"
