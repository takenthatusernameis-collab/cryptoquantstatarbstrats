from __future__ import annotations

import json
from pathlib import Path

import pytest


def test_operational_risk_controls_preserves_gating():
    risk_path = Path("reports/operational_risk_controls_mt.json")
    pretrade_path = Path("reports/pre_trade_enforcement_mt.json")
    guard_path = Path("reports/portfolio_guardrails_mt.json")
    gating_path = Path("reports/portfolio_gating_mt.json")
    if not risk_path.exists() or not gating_path.exists():
        pytest.skip("Missing artifacts")
    risk = json.loads(risk_path.read_text(encoding="utf-8"))
    pretrade = (
        json.loads(pretrade_path.read_text(encoding="utf-8"))
        if pretrade_path.exists()
        else {}
    )
    guard = (
        json.loads(guard_path.read_text(encoding="utf-8"))
        if guard_path.exists()
        else {}
    )
    gating = json.loads(gating_path.read_text(encoding="utf-8"))

    assert risk.get("real_data_only") is True
    assert risk.get("fabricated_data") is False
    assert risk.get("type") == "operational_risk_controls_mt"
    assert risk.get("operational_summary", {}).get("no_auto_lift_of_blocks") is True
    assert risk.get("operational_summary", {}).get("fail_closed") is True

    g_res = gating.get("results_by_timeframe") or {}
    r_res = risk.get("results_by_timeframe") or {}
    p_res = pretrade.get("results_by_timeframe") or {}
    gd_res = guard.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        g_r = g_res[tf]
        r_r = r_res[tf]
        eligible_g = set(g_r.get("eligible_pairs") or [])
        eligible_r = set(r_r.get("eligible_pairs") or [])
        assert eligible_r == eligible_g
        if p_res:
            eligible_p = set(p_res[tf].get("eligible_pairs") or [])
            assert eligible_p == eligible_g
        if gd_res:
            eligible_gd = set(gd_res[tf].get("eligible_pairs") or [])
            assert eligible_gd == eligible_g
        for pname, rinfo in (r_r.get("pairs") or {}).items():
            if pname in eligible_g:
                assert rinfo.get("enforcement_allowed") is True
                assert rinfo.get("pre_trade_checks_passed") is True
            else:
                assert rinfo.get("enforcement_allowed") is False
                assert rinfo.get("pre_trade_checks_passed") is False
                assert float(rinfo.get("position_limit_usdt", 1.0)) == 0.0
                rl = rinfo.get("rejection_log") or []
                assert isinstance(rl, list) and len(rl) >= 1
                br = rinfo.get("blocked_routes") or []
                assert isinstance(br, list) and len(br) >= 1
            prov = rinfo.get("provenance") or {}
            assert prov.get("real_data_only") is True
            gc = rinfo.get("gating_context") or {}
            assert gc.get("source_gating") == "reports/portfolio_gating_mt.json"
