from __future__ import annotations

import json
from pathlib import Path

import pytest

PAIRS_FOR_CHECK = [
    "BTC/ETH",
    "ETH/SOL",
    "BTC/SOL",
    "ADA/ETH",
    "XRP/BTC",
    "BNB/ETH",
    "BTC/BNB",
    "SOL/BNB",
    "ADA/BTC",
    "XRP/ETH",
    "BNB/BTC",
    "DOT/BTC",
    "DOT/ETH",
    "POL/BTC",
    "AVAX/BTC",
    "LINK/BTC",
    "LTC/BTC",
]


def test_oos_portfolio_execution_preserves_gating():
    exec_path = Path("reports/oos_portfolio_execution_mt.json")
    gating_path = Path("reports/portfolio_gating_mt.json")
    if not exec_path.exists() or not gating_path.exists():
        pytest.skip("Missing artifacts")
    execution = json.loads(exec_path.read_text(encoding="utf-8"))
    gating = json.loads(gating_path.read_text(encoding="utf-8"))

    assert execution.get("real_data_only") is True
    assert execution.get("fabricated_data") is False
    assert execution.get("type") == "oos_portfolio_execution_mt"
    summary = execution.get("execution_summary") or {}
    assert summary.get("fail_closed") is True
    assert summary.get("no_auto_lift_of_blocks") is True
    assert summary.get("gate_thresholds_unchanged") is True
    assert summary.get("execution_realism_applied") is True
    assert summary.get("gating_preserved") is True

    g_res = gating.get("results_by_timeframe") or {}
    e_res = execution.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        g_r = g_res[tf]
        e_r = e_res[tf]
        eligible_g = set(g_r.get("eligible_pairs") or [])
        eligible_e = set(e_r.get("eligible_pairs") or [])
        assert eligible_e == eligible_g, f"{tf} eligible set drift"
        for pname in PAIRS_FOR_CHECK:
            einfo = (e_r.get("pairs") or {}).get(pname) or {}
            assert einfo.get("eligible") is (pname in eligible_g)
            assert einfo.get("orders_allowed") is (pname in eligible_g)
            assert einfo.get("fills_allowed") is (pname in eligible_g)
            if pname in eligible_g:
                assert einfo.get("status") == "execute"
                assert float(einfo.get("allocation_usdt") or 0.0) >= 0.0
                assert einfo.get("pre_trade_enforcement_ok") is True
            else:
                assert einfo.get("status") == "block"
                assert float(einfo.get("allocation_usdt") or 0.0) == 0.0
                assert float(einfo.get("position_limit_usdt") or 0.0) == 0.0
                assert float(einfo.get("capacity_usdt") or 0.0) == 0.0
                rl = einfo.get("rejection_log") or []
                assert isinstance(rl, list) and len(rl) >= 1
                br = einfo.get("blocked_routes") or []
                assert isinstance(br, list) and len(br) >= 1
                assert any(entry.get("fail_closed") is True for entry in rl)
            prov = einfo.get("provenance") or {}
            assert prov.get("real_data_only") is True
            assert prov.get("fabricated_data") is False
            gc = einfo.get("gating_context") or {}
            assert gc.get("source_gating") == "reports/portfolio_gating_mt.json"
            linked = gc.get("linked_artifacts") or []
            assert "reports/portfolio_gating_mt.json" in linked
            assert "reports/oos_cointegration_validation_mt.json" in linked


def test_oos_portfolio_execution_summary_counts():
    exec_path = Path("reports/oos_portfolio_execution_mt.json")
    if not exec_path.exists():
        pytest.skip("Missing artifact")
    execution = json.loads(exec_path.read_text(encoding="utf-8"))
    summary = execution.get("execution_summary") or {}
    assert summary.get("total_pairs") == 17 * 3
    orders_allowed = sum(
        1
        for tf in ("1h", "4h", "1d")
        for p in (execution.get("results_by_timeframe") or {}).get(tf, {}).get("pairs", {}).values()
        if p.get("orders_allowed") is True
    )
    orders_blocked = sum(
        1
        for tf in ("1h", "4h", "1d")
        for p in (execution.get("results_by_timeframe") or {}).get(tf, {}).get("pairs", {}).values()
        if p.get("orders_allowed") is False
    )
    assert summary.get("orders_allowed_total") == orders_allowed
    assert summary.get("orders_blocked_total") == orders_blocked
    assert orders_allowed + orders_blocked == 17 * 3
