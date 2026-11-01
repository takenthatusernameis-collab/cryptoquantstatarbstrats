from __future__ import annotations

import json
from pathlib import Path

import pytest


def test_walkforward_gate_stability_schema():
    wf_path = Path("reports/walkforward_gate_stability_mt.json")
    gating_path = Path("reports/portfolio_gating_mt.json")
    oos_path = Path("reports/oos_cointegration_validation_mt.json")
    if not wf_path.exists() or not gating_path.exists() or not oos_path.exists():
        pytest.skip("Missing artifacts")
    wf = json.loads(wf_path.read_text(encoding="utf-8"))
    gating = json.loads(gating_path.read_text(encoding="utf-8"))

    assert wf.get("real_data_only") is True
    assert wf.get("fabricated_data") is False
    assert wf.get("type") == "walkforward_gate_stability_mt"
    assert wf.get("stability_summary", {}).get("fail_closed") is True
    assert wf.get("stability_summary", {}).get("no_auto_lift_of_blocks") is True
    assert wf.get("stability_summary", {}).get("gate_thresholds_unchanged") is True
    assert wf.get("stability_summary", {}).get("causal") is True
    assert wf.get("stability_summary", {}).get("trailing_windows_only") is True

    g_res = gating.get("results_by_timeframe") or {}
    w_res = wf.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        g_r = g_res[tf]
        w_r = w_res[tf]
        eligible_g = set(g_r.get("eligible_pairs") or [])
        eligible_w = set(w_r.get("eligible_pairs") or [])
        assert eligible_w == eligible_g, f"{tf} eligible set drift"
        assert w_r["n_eligible"] == len(eligible_g)
        assert w_r["n_blocked"] == 17 - len(eligible_g)
        for pname, winfo in (w_r.get("pairs") or {}).items():
            assert winfo.get("eligible") is (pname in eligible_g)
            assert winfo.get("status") in ("stable", "unstable")
            assert winfo.get("gate_stability_ok") is (winfo.get("status") == "stable")
            assert isinstance(winfo.get("n_windows"), int)
            assert winfo.get("n_windows") >= 1
            assert isinstance(winfo.get("window_decisions"), list)
            assert len(winfo.get("window_decisions") or []) == winfo.get("n_windows")
            for wdec in winfo.get("window_decisions") or []:
                assert wdec.get("all_pass") in (True, False)
                assert isinstance(wdec.get("blocked_routes"), list)
            # Fail-closed / no auto-lift: IS blocked -> every OOS window blocked.
            if pname not in eligible_g:
                rl = winfo.get("rejection_log") or []
                assert isinstance(rl, list) and len(rl) >= 1
                assert any(entry.get("fail_closed") is True for entry in rl)
            prov = winfo.get("provenance") or {}
            assert prov.get("real_data_only") is True
            assert prov.get("fabricated_data") is False
            assert prov.get("causal") is True
            assert prov.get("fail_closed") is True
            gc = winfo.get("gating_context") or {}
            assert gc.get("source_gating") == "reports/portfolio_gating_mt.json"
            linked = gc.get("linked_artifacts") or []
            assert "reports/portfolio_gating_mt.json" in linked
            assert "reports/oos_cointegration_validation_mt.json" in linked


def test_walkforward_gate_stability_summary_counts():
    wf_path = Path("reports/walkforward_gate_stability_mt.json")
    if not wf_path.exists():
        pytest.skip("Missing artifact")
    wf = json.loads(wf_path.read_text(encoding="utf-8"))
    summary = wf.get("stability_summary") or {}
    assert summary.get("total_pairs") == 17 * 3
    n_stable = sum(
        1
        for tf in ("1h", "4h", "1d")
        for p in (wf.get("results_by_timeframe") or {}).get(tf, {}).get("pairs", {}).values()
        if p.get("gate_stability_ok") is True
    )
    n_unstable = sum(
        1
        for tf in ("1h", "4h", "1d")
        for p in (wf.get("results_by_timeframe") or {}).get(tf, {}).get("pairs", {}).values()
        if p.get("gate_stability_ok") is False
    )
    assert summary.get("stable_pairs") == n_stable
    assert summary.get("unstable_pairs") == n_unstable
    assert n_stable + n_unstable == 17 * 3
