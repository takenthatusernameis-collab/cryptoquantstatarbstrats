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


def test_continuous_monitoring_hardening_preserves_gating():
    dep_path = Path("reports/continuous_monitoring_hardening_mt.json")
    gating_path = Path("reports/portfolio_gating_mt.json")
    if not dep_path.exists() or not gating_path.exists():
        pytest.skip("Missing artifacts")
    mon = json.loads(dep_path.read_text(encoding="utf-8"))
    gating = json.loads(gating_path.read_text(encoding="utf-8"))

    assert mon.get("real_data_only") is True
    assert mon.get("fabricated_data") is False
    assert mon.get("type") == "continuous_monitoring_hardening_mt"
    summary = mon.get("monitoring_hardening_summary") or {}
    assert summary.get("fail_closed") is True
    assert summary.get("no_auto_lift_of_blocks") is True
    assert summary.get("gate_thresholds_unchanged") is True
    assert summary.get("gating_preserved") is True
    assert summary.get("zero_blocked_capital_orders_fills") is True
    assert summary.get("only_pol_btc_4h_monitoring_eligible") is True

    g_res = gating.get("results_by_timeframe") or {}
    m_res = mon.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        g_r = g_res[tf]
        m_r = m_res[tf]
        eligible_g = set(g_r.get("eligible_pairs") or [])
        eligible_m = set(m_r.get("eligible_pairs") or [])
        assert eligible_m == eligible_g, f"{tf} eligible set drift"
        for pname in PAIRS_FOR_CHECK:
            minfo = (m_r.get("pairs") or {}).get(pname) or {}
            assert minfo.get("eligible_by_gating") is (pname in eligible_g)
            assert minfo.get("monitoring_eligible") is (pname in eligible_g)
            assert minfo.get("orders_allowed") is (pname in eligible_g)
            assert minfo.get("fills_allowed") is (pname in eligible_g)
            if pname in eligible_g:
                assert minfo.get("status") == "MONITORING_ELIGIBLE"
                assert minfo.get("monitoring_blocked") is False
            else:
                assert minfo.get("status") == "MONITORING_BLOCKED"
                assert minfo.get("monitoring_blocked") is True
                assert float(minfo.get("capital_usdt") or 0.0) == 0.0
                rl = minfo.get("rejection_log") or []
                assert isinstance(rl, list) and len(rl) >= 1
                br = minfo.get("blocked_routes") or []
                assert isinstance(br, list) and len(br) >= 1
                assert any(entry.get("fail_closed") is True for entry in rl)
            prov = minfo.get("provenance") or {}
            assert prov.get("real_data_only") is True
            assert prov.get("fabricated_data") is False


def test_continuous_monitoring_hardening_summary_counts():
    dep_path = Path("reports/continuous_monitoring_hardening_mt.json")
    gating_path = Path("reports/portfolio_gating_mt.json")
    if not dep_path.exists() or not gating_path.exists():
        pytest.skip("Missing artifacts")
    mon = json.loads(dep_path.read_text(encoding="utf-8"))
    gating = json.loads(gating_path.read_text(encoding="utf-8"))
    g_res = gating.get("results_by_timeframe") or {}
    m_res = mon.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        eligible_g = set((g_res[tf] or {}).get("eligible_pairs") or [])
        eligible_m = set((m_res[tf] or {}).get("eligible_pairs") or [])
        assert eligible_m == eligible_g
    summary = mon.get("monitoring_hardening_summary") or {}
    assert summary.get("drift_detection_enforced") is True
    assert summary.get("alerting_slas_enforced") is True
    assert summary.get("reconciliation_tolerances_enforced") is True
    assert summary.get("kill_switch_latency_bounded") is True
    assert summary.get("monitoring_chain_hardened") is True
