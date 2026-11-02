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


def test_post_deployment_validation_remediation_preserves_gating():
    dep_path = Path("reports/post_deployment_validation_remediation_mt.json")
    gating_path = Path("reports/portfolio_gating_mt.json")
    if not dep_path.exists() or not gating_path.exists():
        pytest.skip("Missing artifacts")
    cert = json.loads(dep_path.read_text(encoding="utf-8"))
    gating = json.loads(gating_path.read_text(encoding="utf-8"))

    assert cert.get("real_data_only") is True
    assert cert.get("fabricated_data") is False
    assert cert.get("type") == "post_deployment_validation_remediation_mt"
    summary = cert.get("post_deployment_validation_summary") or {}
    assert summary.get("fail_closed") is True
    assert summary.get("no_auto_lift_of_blocks") is True
    assert summary.get("gate_thresholds_unchanged") is True
    assert summary.get("gating_preserved") is True
    assert summary.get("zero_blocked_capital_orders_fills") is True
    assert summary.get("only_pol_btc_4h_post_deploy_validated") is True

    g_res = gating.get("results_by_timeframe") or {}
    c_res = cert.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        g_r = g_res[tf]
        c_r = c_res[tf]
        eligible_g = set(g_r.get("eligible_pairs") or [])
        eligible_c = set(c_r.get("eligible_pairs") or [])
        assert eligible_c == eligible_g, f"{tf} eligible set drift"
        for pname in PAIRS_FOR_CHECK:
            cinfo = (c_r.get("pairs") or {}).get(pname) or {}
            assert cinfo.get("eligible_by_gating") is (pname in eligible_g)
            assert cinfo.get("post_deploy_validated") is (pname in eligible_g)
            assert cinfo.get("orders_allowed") is (pname in eligible_g)
            assert cinfo.get("fills_allowed") is (pname in eligible_g)
            if pname in eligible_g:
                assert cinfo.get("status") == "POST_DEPLOY_VALIDATED"
                assert cinfo.get("hard_blocked") is False
            else:
                assert cinfo.get("status") == "POST_DEPLOY_BLOCKED"
                assert cinfo.get("hard_blocked") is True
                assert float(cinfo.get("capital_usdt") or 0.0) == 0.0
                assert float(cinfo.get("allocation_usdt") or 0.0) == 0.0
                assert float(cinfo.get("position_limit_usdt") or 0.0) == 0.0
                rl = cinfo.get("rejection_log") or []
                assert isinstance(rl, list) and len(rl) >= 1
                br = cinfo.get("blocked_routes") or []
                assert isinstance(br, list) and len(br) >= 1
                assert any(entry.get("fail_closed") is True for entry in rl)
            prov = cinfo.get("provenance") or {}
            assert prov.get("real_data_only") is True
            assert prov.get("fabricated_data") is False
            gc = cinfo.get("gating_context") or {}
            assert gc.get("source") == "reports/portfolio_gating_mt.json"


def test_post_deployment_validation_remediation_summary_counts():
    dep_path = Path("reports/post_deployment_validation_remediation_mt.json")
    gating_path = Path("reports/portfolio_gating_mt.json")
    if not dep_path.exists() or not gating_path.exists():
        pytest.skip("Missing artifacts")
    cert = json.loads(dep_path.read_text(encoding="utf-8"))
    gating = json.loads(gating_path.read_text(encoding="utf-8"))
    g_res = gating.get("results_by_timeframe") or {}
    c_res = cert.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        eligible_g = set((g_res[tf] or {}).get("eligible_pairs") or [])
        eligible_c = set((c_res[tf] or {}).get("eligible_pairs") or [])
        assert eligible_c == eligible_g
    summary = cert.get("post_deployment_validation_summary") or {}
    assert summary.get("post_deployment_validation_hardened") is True
    assert summary.get("auto_remediation_hardened") is True
    assert summary.get("kill_switch_available") is True
    assert summary.get("rollback_capable") is True
