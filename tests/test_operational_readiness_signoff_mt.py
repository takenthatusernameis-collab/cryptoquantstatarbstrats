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


def test_operational_readiness_signoff_preserves_gating():
    dep_path = Path("reports/operational_readiness_signoff_mt.json")
    gating_path = Path("reports/portfolio_gating_mt.json")
    if not dep_path.exists() or not gating_path.exists():
        pytest.skip("Missing artifacts")
    signoff = json.loads(dep_path.read_text(encoding="utf-8"))
    gating = json.loads(gating_path.read_text(encoding="utf-8"))

    assert signoff.get("real_data_only") is True
    assert signoff.get("fabricated_data") is False
    assert signoff.get("type") == "operational_readiness_signoff_mt"
    summary = signoff.get("signoff_summary") or {}
    assert summary.get("fail_closed") is True
    assert summary.get("no_auto_lift_of_blocks") is True
    assert summary.get("gate_thresholds_unchanged") is True
    assert summary.get("gating_preserved") is True
    assert summary.get("zero_blocked_capital_orders_fills") is True
    assert summary.get("only_pol_btc_4h_ready") is True

    g_res = gating.get("results_by_timeframe") or {}
    s_res = signoff.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        g_r = g_res[tf]
        s_r = s_res[tf]
        eligible_g = set(g_r.get("eligible_pairs") or [])
        eligible_s = set(s_r.get("eligible_pairs") or [])
        assert eligible_s == eligible_g, f"{tf} eligible set drift"
        for pname in PAIRS_FOR_CHECK:
            sinfo = (s_r.get("pairs") or {}).get(pname) or {}
            assert sinfo.get("eligible_by_gating") is (pname in eligible_g)
            assert sinfo.get("operationally_ready") is (pname in eligible_g)
            assert sinfo.get("orders_allowed") is (pname in eligible_g)
            assert sinfo.get("fills_allowed") is (pname in eligible_g)
            if pname in eligible_g:
                assert sinfo.get("signoff") == "OPERATIONALLY_READY"
                assert float(sinfo.get("capital_usdt") or 0.0) >= 0.0
                assert sinfo.get("all_checks_pass") is True
            else:
                assert sinfo.get("signoff") == "NOT_READY_BLOCKED"
                assert float(sinfo.get("capital_usdt") or 0.0) == 0.0
                assert float(sinfo.get("allocation_usdt") or 0.0) == 0.0
                assert float(sinfo.get("position_limit_usdt") or 0.0) == 0.0
                rl = sinfo.get("rejection_log") or []
                assert isinstance(rl, list) and len(rl) >= 1
                br = sinfo.get("blocked_routes") or []
                assert isinstance(br, list) and len(br) >= 1
                assert any(entry.get("fail_closed") is True for entry in rl)
            prov = sinfo.get("provenance") or {}
            assert prov.get("real_data_only") is True
            assert prov.get("fabricated_data") is False
            gc = sinfo.get("gating_context") or {}
            assert gc.get("source_gating") == "reports/portfolio_gating_mt.json"
            linked = gc.get("linked_artifacts") or []
            assert "reports/portfolio_gating_mt.json" in linked


def test_operational_readiness_signoff_summary_counts():
    dep_path = Path("reports/operational_readiness_signoff_mt.json")
    if not dep_path.exists():
        pytest.skip("Missing artifact")
    signoff = json.loads(dep_path.read_text(encoding="utf-8"))
    summary = signoff.get("signoff_summary") or {}
    assert summary.get("total_pairs_by_tf") == 17 * 3
    ready_total = sum(
        1
        for tf in ("1h", "4h", "1d")
        for p in (signoff.get("results_by_timeframe") or {}).get(tf, {}).get("pairs", {}).values()
        if p.get("operationally_ready") is True
    )
    not_ready_total = sum(
        1
        for tf in ("1h", "4h", "1d")
        for p in (signoff.get("results_by_timeframe") or {}).get(tf, {}).get("pairs", {}).values()
        if p.get("operationally_ready") is False
    )
    assert summary.get("operationally_ready_total") == ready_total
    assert summary.get("not_ready_blocked_total") == not_ready_total
    assert ready_total + not_ready_total == 17 * 3
    assert ready_total == 1
