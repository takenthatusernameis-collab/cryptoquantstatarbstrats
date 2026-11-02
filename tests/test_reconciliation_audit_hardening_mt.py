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


def test_reconciliation_audit_hardening_preserves_gating():
    dep_path = Path("reports/reconciliation_audit_hardening_mt.json")
    gating_path = Path("reports/portfolio_gating_mt.json")
    if not dep_path.exists() or not gating_path.exists():
        pytest.skip("Missing artifacts")
    recon = json.loads(dep_path.read_text(encoding="utf-8"))
    gating = json.loads(gating_path.read_text(encoding="utf-8"))

    assert recon.get("real_data_only") is True
    assert recon.get("fabricated_data") is False
    assert recon.get("type") == "reconciliation_audit_hardening_mt"
    summary = recon.get("reconciliation_audit_summary") or {}
    assert summary.get("fail_closed") is True
    assert summary.get("no_auto_lift_of_blocks") is True
    assert summary.get("gate_thresholds_unchanged") is True
    assert summary.get("gating_preserved") is True
    assert summary.get("zero_blocked_capital_orders_fills") is True
    assert summary.get("only_pol_btc_4h_reconciliation_audit_ready") is True

    g_res = gating.get("results_by_timeframe") or {}
    r_res = recon.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        g_r = g_res[tf]
        r_r = r_res[tf]
        eligible_g = set(g_r.get("eligible_pairs") or [])
        eligible_r = set(r_r.get("eligible_pairs") or [])
        assert eligible_r == eligible_g, f"{tf} eligible set drift"
        for pname in PAIRS_FOR_CHECK:
            rinfo = (r_r.get("pairs") or {}).get(pname) or {}
            assert rinfo.get("eligible_by_gating") is (pname in eligible_g)
            assert rinfo.get("reconciliation_audit_ready") is (pname in eligible_g)
            assert rinfo.get("orders_allowed") is (pname in eligible_g)
            assert rinfo.get("fills_allowed") is (pname in eligible_g)
            if pname in eligible_g:
                assert rinfo.get("status") == "RECONCILIATION_AUDIT_READY"
                assert rinfo.get("hard_blocked") is False
            else:
                assert rinfo.get("status") == "RECONCILIATION_BLOCKED"
                assert rinfo.get("hard_blocked") is True
                assert float(rinfo.get("capital_usdt") or 0.0) == 0.0
                assert float(rinfo.get("allocation_usdt") or 0.0) == 0.0
                assert float(rinfo.get("position_limit_usdt") or 0.0) == 0.0
                rl = rinfo.get("rejection_log") or []
                assert isinstance(rl, list) and len(rl) >= 1
                br = rinfo.get("blocked_routes") or []
                assert isinstance(br, list) and len(br) >= 1
                assert any(entry.get("fail_closed") is True for entry in rl)
            prov = rinfo.get("provenance") or {}
            assert prov.get("real_data_only") is True
            assert prov.get("fabricated_data") is False


def test_reconciliation_audit_hardening_summary_counts():
    dep_path = Path("reports/reconciliation_audit_hardening_mt.json")
    gating_path = Path("reports/portfolio_gating_mt.json")
    if not dep_path.exists() or not gating_path.exists():
        pytest.skip("Missing artifacts")
    recon = json.loads(dep_path.read_text(encoding="utf-8"))
    gating = json.loads(gating_path.read_text(encoding="utf-8"))
    g_res = gating.get("results_by_timeframe") or {}
    r_res = recon.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        eligible_g = set((g_res[tf] or {}).get("eligible_pairs") or [])
        eligible_r = set((r_res[tf] or {}).get("eligible_pairs") or [])
        assert eligible_r == eligible_g
    summary = recon.get("reconciliation_audit_summary") or {}
    assert summary.get("reconciliation_hardened") is True
    assert summary.get("audit_hardened") is True
    assert summary.get("strict_tolerances_enforced") is True
    assert summary.get("auto_block_on_mismatch") is True
