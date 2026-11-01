from __future__ import annotations

import json
from pathlib import Path

import pytest


def test_order_routing_schema_and_invariants():
    route_path = Path("reports/order_routing_realism_mt.json")
    if not route_path.exists():
        pytest.skip(f"Missing {route_path}")
    data = json.loads(route_path.read_text(encoding="utf-8"))

    assert data.get("real_data_only") is True
    assert data.get("fabricated_data") is False
    assert data.get("type") == "order_routing_realism_mt"
    assert "results_by_timeframe" in data
    assert "assumptions" in data
    ass = data["assumptions"]
    assert ass.get("fail_closed") is True
    assert ass.get("only_gated_eligible_feasible") is True
    assert ass.get("partial_fills") is True
    assert "latency_assumptions" in ass
    assert "reject_replace" in ass

    inv = data.get("routing_invariant") or {}
    assert inv.get("fail_closed") is True
    assert inv.get("only_gated_eligible_feasible") is True
    assert inv.get("blocked_pairs_have_rejection_log") is True

    for tf in ["1h", "4h", "1d"]:
        assert tf in data["results_by_timeframe"]
        r = data["results_by_timeframe"][tf]
        assert "pairs" in r
        pairs = r["pairs"]
        for pname, pinfo in pairs.items():
            assert "routing_blocked_by_gating" in pinfo
            assert "feasible" in pinfo
            assert "rejection_log" in pinfo
            assert "blocked_routes" in pinfo
            assert "maker_taker_model" in pinfo
            assert "queue_latency" in pinfo
            assert "partial_fill_model" in pinfo
            assert "reject_replace" in pinfo
            prov = pinfo.get("provenance") or {}
            assert prov.get("real_data_only") is True
            assert prov.get("fail_closed") is True
            if pinfo.get("routing_blocked_by_gating") is True:
                assert pinfo.get("feasible") is False
                rl = pinfo.get("rejection_log") or []
                assert isinstance(rl, list) and len(rl) >= 1
                reason = rl[0].get("reason") or ""
                block_reason = rl[0].get("block_reason") == "gating"
                is_routed_reject = reason == "route_rejected_by_cointegration_gating"
                assert block_reason or is_routed_reject
            else:
                assert pinfo.get("feasible") is True


def test_order_routing_only_gated_eligible_feasible_against_portfolio_gating():
    route_path = Path("reports/order_routing_realism_mt.json")
    gating_path = Path("reports/portfolio_gating_mt.json")
    if not route_path.exists() or not gating_path.exists():
        pytest.skip("Missing routing or gating artifacts")
    routing = json.loads(route_path.read_text(encoding="utf-8"))
    gating = json.loads(gating_path.read_text(encoding="utf-8"))

    g_results = gating.get("results_by_timeframe") or {}
    r_results = routing.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        g_r = g_results.get(tf) or {}
        r_r = r_results.get(tf) or {}
        eligible_g = set(g_r.get("eligible_pairs") or [])
        for pname, pinfo in (r_r.get("pairs") or {}).items():
            if pinfo.get("feasible") is True:
                assert pname in eligible_g
                assert pinfo.get("routing_blocked_by_gating") is False
            if pinfo.get("routing_blocked_by_gating") is True:
                assert pname not in eligible_g
