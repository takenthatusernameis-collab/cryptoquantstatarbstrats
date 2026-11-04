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


def test_live_go_live_authorization_final_preserves_gating():
    dep_path = Path("reports/live_go_live_authorization_final_mt.json")
    gating_path = Path("reports/portfolio_gating_mt.json")
    if not dep_path.exists() or not gating_path.exists():
        pytest.skip("Missing artifacts")
    cert = json.loads(dep_path.read_text(encoding="utf-8"))
    gating = json.loads(gating_path.read_text(encoding="utf-8"))

    assert cert.get("real_data_only") is True
    assert cert.get("fabricated_data") is False
    assert cert.get("type") == "live_go_live_authorization_final_mt"
    assert cert.get("causal_only") is True
    assert cert.get("no_lookahead") is True
    assert cert.get("fail_closed") is True
    assert cert.get("no_auto_lift_of_blocks") is True
    assert cert.get("no_threshold_weakening") is True
    summary = cert.get("go_live_authorization_summary") or {}
    assert summary.get("all_51_slots_assessed") is True
    assert summary.get("fail_closed") is True
    assert summary.get("no_auto_lift_of_blocks") is True
    assert summary.get("gate_thresholds_unchanged") is True
    assert summary.get("gating_preserved") is True
    assert summary.get("zero_blocked_capital_orders_fills") is True
    assert summary.get("only_pol_btc_4h_capital_preserved") is True
    assert summary.get("invariants_preserved") is True
    assert summary.get("kill_switch_verified") is True
    assert summary.get("risk_controls_verified") is True
    assert summary.get("pre_trade_enforcement_verified") is True
    assert summary.get("post_trade_reconciliation_ready") is True
    assert summary.get("reconciliation_audit_ready") is True
    assert summary.get("monitoring_alerting_ready") is True
    assert summary.get("incident_response_verified") is True
    assert summary.get("capital_preservation_verified") is True
    assert summary.get("live_continuity_verified") is True
    assert summary.get("campaign26_end_to_end_linked") is True
    assert summary.get("campaign26_live_operational_readiness_linked") is True

    go_live = cert.get("go_live_authorization") or {}
    assert go_live.get("fail_closed") is True
    assert go_live.get("scope_limited_to_eligible_only") is True
    assert go_live.get("zero_capital_on_blocked") is True
    assert go_live.get("authorized_pairs_timeframes") == [["POL/BTC", "4h"]]
    # Fail-closed provenance: must be a real, honest record, never a vacuous pass.
    go_live_provenance = go_live.get("provenance")
    assert isinstance(go_live_provenance, dict), (
        "go_live_authorization.provenance must be a dict with real-data "
        "provenance; got %r" % (go_live_provenance,)
    )
    assert go_live_provenance.get("real_data_only") is True
    assert go_live_provenance.get("fabricated_data") is False

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
            assert cinfo.get("go_live_authorized") is (pname in eligible_g)
            assert cinfo.get("orders_allowed") is (pname in eligible_g)
            assert cinfo.get("fills_allowed") is (pname in eligible_g)
            if pname in eligible_g:
                assert cinfo.get("status") == "GO_LIVE_AUTHORIZED"
                assert cinfo.get("hard_blocked") is False
                assert cinfo.get("capital_usdt") == 25000.0
                assert cinfo.get("allocation_usdt") == 25000.0
                assert cinfo.get("position_limit_usdt") == 30000.0
            else:
                assert cinfo.get("status") == "GO_LIVE_BLOCKED"
                assert cinfo.get("hard_blocked") is True
                assert float(cinfo.get("capital_usdt") or 0.0) == 0.0
                assert float(cinfo.get("allocation_usdt") or 0.0) == 0.0
                assert float(cinfo.get("position_limit_usdt") or 0.0) == 0.0
                assert cinfo.get("orders_allowed") is False
                assert cinfo.get("fills_allowed") is False
                rl = cinfo.get("rejection_log") or []
                assert isinstance(rl, list) and len(rl) >= 1
                br = cinfo.get("blocked_routes") or []
                assert isinstance(br, list) and len(br) >= 1
                assert any(entry.get("fail_closed") is True for entry in rl)
                assert any(
                    entry.get("auto_lift_attempt_blocked") is True for entry in rl
                )
            prov = cinfo.get("provenance") or {}
            assert prov.get("real_data_only") is True
            assert prov.get("fabricated_data") is False
            gc = cinfo.get("gating_context") or {}
            assert gc.get("source") == "reports/portfolio_gating_mt.json"
            bd = cinfo.get("baseline_diff") or {}
            assert bd.get("baseline_source") == "reports/portfolio_gating_mt.json"
            assert bd.get("diff_against_baseline") is True
            assert bd.get("invariants_preserved") is True


def test_live_go_live_authorization_final_chain_linked():
    dep_path = Path("reports/live_go_live_authorization_final_mt.json")
    if not dep_path.exists():
        pytest.skip("Missing artifact")
    cert = json.loads(dep_path.read_text(encoding="utf-8"))
    assert cert.get("chain_linked") is True
    prov = cert.get("provenance") or {}
    assert prov.get("generator") == "scripts/generate_campaign27_artifacts.py"
