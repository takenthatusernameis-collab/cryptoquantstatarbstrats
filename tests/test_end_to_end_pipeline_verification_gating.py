from __future__ import annotations

import json
from pathlib import Path

import pytest


def test_end_to_end_pipeline_verification_preserves_gating():
    verification_path = Path("reports/end_to_end_pipeline_verification_mt.json")
    gating_path = Path("reports/portfolio_gating_mt.json")
    if not verification_path.exists() or not gating_path.exists():
        pytest.skip("Missing artifacts")
    verification = json.loads(verification_path.read_text(encoding="utf-8"))
    gating = json.loads(gating_path.read_text(encoding="utf-8"))

    assert verification.get("real_data_only") is True
    assert verification.get("fabricated_data") is False
    assert verification.get("type") == "end_to_end_pipeline_verification_mt"
    assert verification.get("verification_summary", {}).get("fail_closed") is True
    assert verification.get("verification_summary", {}).get("no_auto_lift_of_blocks") is True
    assert verification.get("verification_summary", {}).get("pipeline_end_to_end_verified") is True

    g_res = gating.get("results_by_timeframe") or {}
    v_res = verification.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        g_r = g_res[tf]
        v_r = v_res[tf]
        eligible_g = set(g_r.get("eligible_pairs") or [])
        eligible_v = set(v_r.get("eligible_pairs") or [])
        assert eligible_v == eligible_g
        for pname, vinfo in (v_r.get("pairs") or {}).items():
            assert vinfo.get("eligible") is (pname in eligible_g)
            assert vinfo.get("pipeline_consistent") is True
            assert vinfo.get("all_stages_respect_gating") is True
            assert vinfo.get("zeroed_when_blocked") is True
            if pname not in eligible_g:
                rl = vinfo.get("rejection_log") or []
                assert isinstance(rl, list) and len(rl) >= 1
                br = vinfo.get("blocked_routes") or []
                assert isinstance(br, list) and len(br) >= 1
            prov = vinfo.get("provenance") or {}
            assert prov.get("real_data_only") is True
            assert prov.get("fabricated_data") is False
            gc = vinfo.get("gating_context") or {}
            assert gc.get("source_gating") == "reports/portfolio_gating_mt.json"
            linked = gc.get("linked_artifacts") or []
            assert "reports/portfolio_gating_mt.json" in linked
            assert "reports/kill_switch_rules_mt.json" in linked
