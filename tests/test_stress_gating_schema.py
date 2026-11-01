from __future__ import annotations

import json
from pathlib import Path

import pytest


def test_stress_gating_schema():
    stress_path = Path("reports/stress_gating_mt.json")
    gating_path = Path("reports/portfolio_gating_mt.json")
    if not stress_path.exists() or not gating_path.exists():
        pytest.skip("Missing artifacts")
    stress = json.loads(stress_path.read_text(encoding="utf-8"))
    gating = json.loads(gating_path.read_text(encoding="utf-8"))

    assert stress.get("real_data_only") is True
    assert stress.get("fabricated_data") is False
    assert stress.get("type") == "stress_gating_mt"
    assert stress.get("stress_summary", {}).get("fail_closed") is True
    assert stress.get("stress_summary", {}).get("no_auto_lift_of_blocks") is True
    assert stress.get("stress_summary", {}).get("gate_thresholds_unchanged") is True
    assert stress.get("stress_summary", {}).get("stress_gating_verified") is True

    g_res = gating.get("results_by_timeframe") or {}
    s_res = stress.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        g_r = g_res[tf]
        s_r = s_res[tf]
        eligible_g = set(g_r.get("eligible_pairs") or [])
        eligible_s = set(s_r.get("eligible_pairs") or [])
        assert eligible_s == eligible_g
        for pname, sinfo in (s_r.get("pairs") or {}).items():
            assert sinfo.get("eligible") is (pname in eligible_g)
            assert sinfo.get("stress_passed") is True
            assert sinfo.get("gate_held_under_stress") is True
            assert sinfo.get("no_auto_lift_of_blocks") is True
            assert sinfo.get("fail_closed") is True
            if pname not in eligible_g:
                rl = sinfo.get("rejection_log") or []
                assert isinstance(rl, list) and len(rl) >= 1
                br = sinfo.get("blocked_routes") or []
                assert isinstance(br, list) and len(br) >= 1
            prov = sinfo.get("provenance") or {}
            assert prov.get("real_data_only") is True
            assert prov.get("fabricated_data") is False
            gc = sinfo.get("gating_context") or {}
            assert gc.get("source_gating") == "reports/portfolio_gating_mt.json"
            linked = gc.get("linked_artifacts") or []
            assert "reports/portfolio_gating_mt.json" in linked
            assert "reports/kill_switch_rules_mt.json" in linked
