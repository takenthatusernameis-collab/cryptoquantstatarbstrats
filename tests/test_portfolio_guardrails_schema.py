from __future__ import annotations

import json
from pathlib import Path

import pytest


def test_portfolio_guardrails_preserves_gating_and_schema():
    guard_path = Path("reports/portfolio_guardrails_mt.json")
    pretrade_path = Path("reports/pre_trade_enforcement_mt.json")
    risk_path = Path("reports/operational_risk_controls_mt.json")
    gating_path = Path("reports/portfolio_gating_mt.json")
    if not guard_path.exists() or not pretrade_path.exists() or not gating_path.exists():
        pytest.skip("Missing artifacts")
    guard = json.loads(guard_path.read_text(encoding="utf-8"))
    pretrade = json.loads(pretrade_path.read_text(encoding="utf-8"))
    risk = json.loads(risk_path.read_text(encoding="utf-8")) if risk_path.exists() else {}
    gating = json.loads(gating_path.read_text(encoding="utf-8"))

    assert guard.get("real_data_only") is True
    assert guard.get("fabricated_data") is False
    assert guard.get("type") == "portfolio_guardrails_mt"
    assert guard.get("guardrail_summary", {}).get("no_auto_lift_blocks") is True
    assert guard.get("guardrail_summary", {}).get("fail_closed") is True

    g_res = gating.get("results_by_timeframe") or {}
    gd_res = guard.get("results_by_timeframe") or {}
    p_res = pretrade.get("results_by_timeframe") or {}
    r_res = risk.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        g_r = g_res[tf]
        gd_r = gd_res[tf]
        p_r = p_res[tf]
        eligible_g = set(g_r.get("eligible_pairs") or [])
        eligible_gd = set(gd_r.get("eligible_pairs") or [])
        eligible_p = set(p_r.get("eligible_pairs") or [])
        assert eligible_gd == eligible_g
        assert eligible_p == eligible_g
        if r_res:
            eligible_r = set(r_res[tf].get("eligible_pairs") or [])
            assert eligible_r == eligible_g
        g_inv = gd_r.get("guardrail_invariants") or {}
        assert g_inv.get("cointegration_gated") is True
        assert g_inv.get("respect_gating") is True
        assert g_inv.get("fail_closed") is True
        assert g_inv.get("no_auto_lift_of_blocks") is True
        p_inv = p_r.get("enforcement_invariants") or {}
        assert p_inv.get("cointegration_gated") is True
        assert p_inv.get("fail_closed") is True
        assert p_inv.get("no_auto_lift_of_blocks") is True
        for pname, ginfo in (gd_r.get("pairs") or {}).items():
            if pname not in eligible_g:
                assert ginfo.get("eligible") is False
                assert ginfo.get("risk_budget_allocated") is False
                br = ginfo.get("blocked_routes") or []
                assert isinstance(br, list) and len(br) >= 1
                rules = ginfo.get("guardrail_rules") or []
                assert isinstance(rules, list) and len(rules) >= 1
            else:
                assert ginfo.get("eligible") is True
            prov = ginfo.get("provenance") or {}
            assert prov.get("real_data_only") is True
