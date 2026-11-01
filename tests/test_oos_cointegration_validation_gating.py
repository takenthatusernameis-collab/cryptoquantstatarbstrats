from __future__ import annotations

import json
from pathlib import Path

import pytest


def test_oos_cointegration_validation_preserves_gating():
    oos_path = Path("reports/oos_cointegration_validation_mt.json")
    gating_path = Path("reports/portfolio_gating_mt.json")
    if not oos_path.exists() or not gating_path.exists():
        pytest.skip("Missing artifacts")
    oos = json.loads(oos_path.read_text(encoding="utf-8"))
    gating = json.loads(gating_path.read_text(encoding="utf-8"))

    assert oos.get("real_data_only") is True
    assert oos.get("fabricated_data") is False
    assert oos.get("type") == "oos_cointegration_validation_mt"
    assert oos.get("validation_summary", {}).get("fail_closed") is True
    assert oos.get("validation_summary", {}).get("no_auto_lift_of_blocks") is True
    assert oos.get("validation_summary", {}).get("gate_thresholds_unchanged") is True
    assert oos.get("validation_summary", {}).get("oos_only") is True
    assert oos.get("validation_summary", {}).get("causal") is True

    g_res = gating.get("results_by_timeframe") or {}
    o_res = oos.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        g_r = g_res[tf]
        o_r = o_res[tf]
        eligible_g = set(g_r.get("eligible_pairs") or [])
        eligible_o = set(o_r.get("eligible_pairs") or [])
        assert eligible_o == eligible_g, f"{tf} eligible set drift"
        assert o_r["n_eligible"] == len(eligible_g)
        assert o_r["n_blocked"] == len(PAIRS_FOR_CHECK()) - len(eligible_g)
        for pname, oinfo in (o_r.get("pairs") or {}).items():
            assert oinfo.get("eligible") is (pname in eligible_g)
            assert oinfo.get("status") in ("pass", "block")
            assert oinfo.get("all_pass") is (oinfo.get("status") == "pass")
            # Fail-closed: a blocked pair must never be an OOS pass.
            if not eligible_g:
                assert oinfo.get("status") == "block"
            if pname not in eligible_g:
                rl = oinfo.get("rejection_log") or []
                assert isinstance(rl, list) and len(rl) >= 1
                br = oinfo.get("blocked_routes") or []
                assert isinstance(br, list) and len(br) >= 1
                assert any(
                    entry.get("fail_closed") is True for entry in rl
                )
            prov = oinfo.get("provenance") or {}
            assert prov.get("real_data_only") is True
            assert prov.get("fabricated_data") is False
            assert prov.get("causal") is True
            assert prov.get("fail_closed") is True
            gc = oinfo.get("gating_context") or {}
            assert gc.get("source_gating") == "reports/portfolio_gating_mt.json"
            linked = gc.get("linked_artifacts") or []
            assert "reports/portfolio_gating_mt.json" in linked


def PAIRS_FOR_CHECK():
    return [
        "BTC/ETH", "ETH/SOL", "BTC/SOL", "ADA/ETH", "XRP/BTC", "BNB/ETH",
        "BTC/BNB", "SOL/BNB", "ADA/BTC", "XRP/ETH", "BNB/BTC", "DOT/BTC",
        "DOT/ETH", "POL/BTC", "AVAX/BTC", "LINK/BTC", "LTC/BTC",
    ]


def test_oos_cointegration_validation_summary_counts():
    oos_path = Path("reports/oos_cointegration_validation_mt.json")
    if not oos_path.exists():
        pytest.skip("Missing artifact")
    oos = json.loads(oos_path.read_text(encoding="utf-8"))
    summary = oos.get("validation_summary") or {}
    assert summary.get("total_pairs") == 17 * 3
    n_pass = sum(
        1
        for tf in ("1h", "4h", "1d")
        for p in (oos.get("results_by_timeframe") or {}).get(tf, {}).get("pairs", {}).values()
        if p.get("status") == "pass"
    )
    n_block = sum(
        1
        for tf in ("1h", "4h", "1d")
        for p in (oos.get("results_by_timeframe") or {}).get(tf, {}).get("pairs", {}).values()
        if p.get("status") == "block"
    )
    assert summary.get("oos_pass_pairs") == n_pass
    assert summary.get("oos_block_pairs") == n_block
    assert n_pass + n_block == 17 * 3
