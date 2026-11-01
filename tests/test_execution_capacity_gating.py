from __future__ import annotations

import json
from pathlib import Path

import pytest


def test_execution_capacity_gating_schema_and_invariants():
    cap_path = Path("reports/execution_capacity_mt.json")
    if not cap_path.exists():
        pytest.skip(f"Missing {cap_path}")
    data = json.loads(cap_path.read_text(encoding="utf-8"))

    assert data.get("real_data_only") is True
    assert data.get("fabricated_data") is False
    assert data.get("type") == "execution_capacity_mt"
    assert "results_by_timeframe" in data
    assert "assumptions" in data
    ass = data["assumptions"]
    assert ass.get("capacity_never_lifts_gating") is True
    assert ass.get("fail_closed") is True

    for tf in ["1h", "4h", "1d"]:
        assert tf in data["results_by_timeframe"]
        r = data["results_by_timeframe"][tf]
        assert "pairs" in r
        pairs = r["pairs"]
        for pname, pinfo in pairs.items():
            assert "capacity_blocked_by_gating" in pinfo
            assert "allocation_usdt" in pinfo
            assert "capacity_limits" in pinfo
            assert "rejection_log" in pinfo
            prov = pinfo.get("provenance") or {}
            assert prov.get("real_data_only") is True
            if pinfo.get("capacity_blocked_by_gating") is True:
                assert float(pinfo.get("allocation_usdt", 0.0)) == 0.0
                assert pinfo.get("feasible") is False
                rl = pinfo.get("rejection_log") or []
                assert isinstance(rl, list) and len(rl) >= 1
                reason = rl[0].get("reason") or ""
                block = rl[0].get("block_reason") == "gating"
                valid = block or reason in (
                    "order_blocked_by_cointegration_gating",
                    "route_rejected_by_cointegration_gating",
                )
                assert valid


def test_execution_capacity_gating_matches_portfolio_gating():
    cap_path = Path("reports/execution_capacity_mt.json")
    gating_path = Path("reports/portfolio_gating_mt.json")
    if not cap_path.exists() or not gating_path.exists():
        pytest.skip("Missing capacity or gating artifacts")
    cap = json.loads(cap_path.read_text(encoding="utf-8"))
    gating = json.loads(gating_path.read_text(encoding="utf-8"))

    g_results = gating.get("results_by_timeframe") or {}
    c_results = cap.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        g_r = g_results.get(tf) or {}
        c_r = c_results.get(tf) or {}
        eligible_g = set(g_r.get("eligible_pairs") or [])
        eligible_c = set(c_r.get("eligible_pairs") or [])
        assert eligible_c.issubset(eligible_g)
        for pname, pinfo in (c_r.get("pairs") or {}).items():
            if pinfo.get("capacity_blocked_by_gating"):
                assert pname not in eligible_g
                assert pname not in eligible_c
