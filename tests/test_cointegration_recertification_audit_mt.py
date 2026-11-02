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


def test_cointegration_recertification_audit_preserves_gating():
    dep_path = Path("reports/cointegration_recertification_audit_mt.json")
    gating_path = Path("reports/portfolio_gating_mt.json")
    if not dep_path.exists() or not gating_path.exists():
        pytest.skip("Missing artifacts")
    cert = json.loads(dep_path.read_text(encoding="utf-8"))
    gating = json.loads(gating_path.read_text(encoding="utf-8"))

    assert cert.get("real_data_only") is True
    assert cert.get("fabricated_data") is False
    assert cert.get("type") == "cointegration_recertification_audit_mt"
    summary = cert.get("cointegration_recertification_summary") or {}
    assert summary.get("fail_closed") is True
    assert summary.get("no_auto_lift_of_blocks") is True
    assert summary.get("gate_thresholds_unchanged") is True
    assert summary.get("gating_preserved") is True
    assert summary.get("zero_blocked_capital_orders_fills") is True
    assert summary.get("only_pol_btc_4h_capital_preserved") is True
    assert summary.get("cointegration_is_law") is True
    assert summary.get("engle_granger_p_le_0_05") is True
    assert summary.get("johansen_checked") is True
    assert summary.get("spread_mean_reversion_required") is True
    assert summary.get("half_life_bounds_1_500") is True
    assert summary.get("rolling_stability_ge_0_6") is True
    assert summary.get("provenance_on_every_decision") is True

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
            assert cinfo.get("cointegration_recertified") is (pname in eligible_g)
            assert cinfo.get("orders_allowed") is (pname in eligible_g)
            assert cinfo.get("fills_allowed") is (pname in eligible_g)
            if pname in eligible_g:
                assert cinfo.get("status") == "COINTEGRATION_RECERTIFIED"
                assert cinfo.get("hard_blocked") is False
            else:
                assert cinfo.get("status") == "COINTEGRATION_RECERTIFICATION_BLOCKED"
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
            bd = cinfo.get("baseline_diff") or {}
            assert bd.get("baseline_source") == "reports/portfolio_gating_mt.json"
            assert bd.get("diff_against_baseline") is True
            assert bd.get("invariants_preserved") is True


def test_cointegration_recertification_audit_chain_linked():
    dep_path = Path("reports/cointegration_recertification_audit_mt.json")
    if not dep_path.exists():
        pytest.skip("Missing artifact")
    cert = json.loads(dep_path.read_text(encoding="utf-8"))
    assert cert.get("chain_linked") is True
    summary = cert.get("cointegration_recertification_summary") or {}
    assert summary.get("causal_only_trailing_windows") is True
