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


def test_live_production_deployment_preserves_gating():
    dep_path = Path("reports/live_production_deployment_mt.json")
    gating_path = Path("reports/portfolio_gating_mt.json")
    if not dep_path.exists() or not gating_path.exists():
        pytest.skip("Missing artifacts")
    deployment = json.loads(dep_path.read_text(encoding="utf-8"))
    gating = json.loads(gating_path.read_text(encoding="utf-8"))

    assert deployment.get("real_data_only") is True
    assert deployment.get("fabricated_data") is False
    assert deployment.get("type") == "live_production_deployment_mt"
    summary = deployment.get("deployment_summary") or {}
    assert summary.get("fail_closed") is True
    assert summary.get("no_auto_lift_of_blocks") is True
    assert summary.get("gate_thresholds_unchanged") is True
    assert summary.get("live_deployment_ready") is True
    assert summary.get("gating_preserved") is True

    g_res = gating.get("results_by_timeframe") or {}
    d_res = deployment.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        g_r = g_res[tf]
        d_r = d_res[tf]
        eligible_g = set(g_r.get("eligible_pairs") or [])
        eligible_d = set(d_r.get("eligible_pairs") or [])
        assert eligible_d == eligible_g, f"{tf} eligible set drift"
        for pname in PAIRS_FOR_CHECK:
            dinfo = (d_r.get("pairs") or {}).get(pname) or {}
            assert dinfo.get("eligible") is (pname in eligible_g)
            assert dinfo.get("orders_allowed") is (pname in eligible_g)
            assert dinfo.get("fills_allowed") is (pname in eligible_g)
            if pname in eligible_g:
                assert dinfo.get("status") == "deploy_ready"
                assert float(dinfo.get("capital_usdt") or 0.0) >= 0.0
                assert dinfo.get("live_deployment_bridge_ok") is True
                assert dinfo.get("kill_switch_respected") is True
                assert dinfo.get("post_trade_reconciliation_ok") is True
                assert dinfo.get("realtime_monitoring_ok") is True
                assert dinfo.get("portfolio_guardrails_ok") is True
            else:
                assert dinfo.get("status") == "blocked"
                assert float(dinfo.get("capital_usdt") or 0.0) == 0.0
                assert float(dinfo.get("allocation_usdt") or 0.0) == 0.0
                assert float(dinfo.get("position_limit_usdt") or 0.0) == 0.0
                rl = dinfo.get("rejection_log") or []
                assert isinstance(rl, list) and len(rl) >= 1
                br = dinfo.get("blocked_routes") or []
                assert isinstance(br, list) and len(br) >= 1
                assert any(entry.get("fail_closed") is True for entry in rl)
            prov = dinfo.get("provenance") or {}
            assert prov.get("real_data_only") is True
            assert prov.get("fabricated_data") is False
            gc = dinfo.get("gating_context") or {}
            assert gc.get("source_gating") == "reports/portfolio_gating_mt.json"
            linked = gc.get("linked_artifacts") or []
            assert "reports/portfolio_gating_mt.json" in linked


def test_live_production_deployment_summary_counts():
    dep_path = Path("reports/live_production_deployment_mt.json")
    if not dep_path.exists():
        pytest.skip("Missing artifact")
    deployment = json.loads(dep_path.read_text(encoding="utf-8"))
    summary = deployment.get("deployment_summary") or {}
    assert summary.get("total_pairs") == 17 * 3
    orders_allowed = sum(
        1
        for tf in ("1h", "4h", "1d")
        for p in (
            (deployment.get("results_by_timeframe") or {}).get(tf, {}).get(
                "pairs", {}
            ).values()
        )
        if p.get("orders_allowed") is True
    )
    orders_blocked = sum(
        1
        for tf in ("1h", "4h", "1d")
        for p in (
            (deployment.get("results_by_timeframe") or {}).get(tf, {}).get(
                "pairs", {}
            ).values()
        )
        if p.get("orders_allowed") is False
    )
    assert summary.get("orders_allowed_total") == orders_allowed
    assert summary.get("orders_blocked_total") == orders_blocked
    assert orders_allowed + orders_blocked == 17 * 3
