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


def test_capital_allocation_gating_preserves_gating():
    alloc_path = Path("reports/capital_allocation_gating_mt.json")
    gating_path = Path("reports/portfolio_gating_mt.json")
    if not alloc_path.exists() or not gating_path.exists():
        pytest.skip("Missing artifacts")
    allocation = json.loads(alloc_path.read_text(encoding="utf-8"))
    gating = json.loads(gating_path.read_text(encoding="utf-8"))

    assert allocation.get("real_data_only") is True
    assert allocation.get("fabricated_data") is False
    assert allocation.get("type") == "capital_allocation_gating_mt"
    summary = allocation.get("allocation_summary") or {}
    assert summary.get("fail_closed") is True
    assert summary.get("no_auto_lift_of_blocks") is True
    assert summary.get("gate_thresholds_unchanged") is True
    assert summary.get("proportional_to_gated_eligibility") is True
    assert summary.get("gating_preserved") is True

    g_res = gating.get("results_by_timeframe") or {}
    a_res = allocation.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        g_r = g_res[tf]
        a_r = a_res[tf]
        eligible_g = set(g_r.get("eligible_pairs") or [])
        eligible_a = set(a_r.get("eligible_pairs") or [])
        assert eligible_a == eligible_g, f"{tf} eligible set drift"
        for pname in PAIRS_FOR_CHECK:
            ainfo = (a_r.get("pairs") or {}).get(pname) or {}
            assert ainfo.get("eligible") is (pname in eligible_g)
            if pname in eligible_g:
                assert ainfo.get("status") == "allocated"
                assert float(ainfo.get("capital_allocated_usdt") or 0.0) >= 0.0
                assert ainfo.get("proportional_to_gated_eligibility") is True
            else:
                assert ainfo.get("status") == "blocked"
                assert float(ainfo.get("capital_allocated_usdt") or 0.0) == 0.0
                assert float(ainfo.get("allocation_usdt") or 0.0) == 0.0
                rl = ainfo.get("rejection_log") or []
                assert isinstance(rl, list) and len(rl) >= 1
                br = ainfo.get("blocked_routes") or []
                assert isinstance(br, list) and len(br) >= 1
                assert any(entry.get("fail_closed") is True for entry in rl)
            prov = ainfo.get("provenance") or {}
            assert prov.get("real_data_only") is True
            assert prov.get("fabricated_data") is False
            gc = ainfo.get("gating_context") or {}
            assert gc.get("source_gating") == "reports/portfolio_gating_mt.json"


def test_capital_allocation_gating_summary_counts():
    alloc_path = Path("reports/capital_allocation_gating_mt.json")
    if not alloc_path.exists():
        pytest.skip("Missing artifact")
    allocation = json.loads(alloc_path.read_text(encoding="utf-8"))
    summary = allocation.get("allocation_summary") or {}
    assert summary.get("total_pairs") == 17 * 3
    allocated = sum(
        1
        for tf in ("1h", "4h", "1d")
        for p in (
            (allocation.get("results_by_timeframe") or {}).get(tf, {}).get(
                "pairs", {}
            ).values()
        )
        if p.get("status") == "allocated"
    )
    blocked = sum(
        1
        for tf in ("1h", "4h", "1d")
        for p in (
            (allocation.get("results_by_timeframe") or {}).get(tf, {}).get(
                "pairs", {}
            ).values()
        )
        if p.get("status") == "blocked"
    )
    assert summary.get("allocated_pairs") == allocated
    assert summary.get("blocked_pairs") == blocked
    assert allocated + blocked == 17 * 3
