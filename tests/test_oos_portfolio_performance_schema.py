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


def test_oos_portfolio_performance_preserves_gating_and_schema():
    perf_path = Path("reports/oos_portfolio_performance_mt.json")
    gating_path = Path("reports/portfolio_gating_mt.json")
    exec_path = Path("reports/oos_portfolio_execution_mt.json")
    if not perf_path.exists() or not gating_path.exists() or not exec_path.exists():
        pytest.skip("Missing artifacts")
    perf = json.loads(perf_path.read_text(encoding="utf-8"))
    gating = json.loads(gating_path.read_text(encoding="utf-8"))
    execution = json.loads(exec_path.read_text(encoding="utf-8"))

    assert perf.get("real_data_only") is True
    assert perf.get("fabricated_data") is False
    assert perf.get("type") == "oos_portfolio_performance_mt"
    summary = perf.get("performance_summary") or {}
    assert summary.get("fail_closed") is True
    assert summary.get("no_auto_lift_of_blocks") is True
    assert summary.get("gate_thresholds_unchanged") is True
    assert summary.get("execution_realism_applied") is True
    assert summary.get("oos") is True
    assert summary.get("gating_preserved") is True

    g_res = gating.get("results_by_timeframe") or {}
    p_res = perf.get("results_by_timeframe") or {}
    e_res = execution.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        g_r = g_res[tf]
        p_r = p_res[tf]
        eligible_g = set(g_r.get("eligible_pairs") or [])
        for pname in PAIRS_FOR_CHECK:
            pinfo = (p_r.get("pairs") or {}).get(pname) or {}
            e_tf_res = e_res.get(tf) or {}
            einfo = (e_tf_res.get("pairs") or {}).get(pname) or {}
            assert pinfo.get("eligible") is (pname in eligible_g)
            assert pinfo.get("eligible") == einfo.get("eligible")
            if pname in eligible_g:
                assert pinfo.get("status") == "evaluated"
                assert isinstance(pinfo.get("bootstrap_ci"), dict)
                ci = pinfo.get("bootstrap_ci") or {}
                assert ci.get("n_sims") >= 2000
            else:
                assert pinfo.get("status") == "blocked"
                assert float(pinfo.get("total_return") or 0.0) == 0.0
                assert float(pinfo.get("sharpe") or 0.0) == 0.0
                assert float(pinfo.get("max_drawdown") or 0.0) == 0.0
                rl = pinfo.get("rejection_log") or []
                assert isinstance(rl, list) and len(rl) >= 1
                br = pinfo.get("blocked_routes") or []
                assert isinstance(br, list) and len(br) >= 1
                assert any(entry.get("fail_closed") is True for entry in rl)
                assert any(entry.get("metrics_zeroed") is True for entry in rl)
            prov = pinfo.get("provenance") or {}
            assert prov.get("real_data_only") is True
            assert prov.get("fabricated_data") is False
            gc = pinfo.get("gating_context") or {}
            assert gc.get("source_gating") == "reports/portfolio_gating_mt.json"
            linked = gc.get("linked_artifacts") or []
            assert "reports/portfolio_gating_mt.json" in linked
            assert "reports/oos_portfolio_execution_mt.json" in linked


def test_oos_portfolio_performance_summary_counts():
    perf_path = Path("reports/oos_portfolio_performance_mt.json")
    if not perf_path.exists():
        pytest.skip("Missing artifact")
    perf = json.loads(perf_path.read_text(encoding="utf-8"))
    summary = perf.get("performance_summary") or {}
    assert summary.get("total_pairs") == 17 * 3
    evaluated = 0
    blocked = 0
    for tf in ("1h", "4h", "1d"):
        pairs_tf = (perf.get("results_by_timeframe") or {}).get(tf, {}).get("pairs", {}) or {}
        for pinfo in pairs_tf.values():
            if pinfo.get("status") == "evaluated":
                evaluated += 1
            if pinfo.get("status") == "blocked":
                blocked += 1
    assert summary.get("evaluated_pairs") == evaluated
    assert summary.get("blocked_pairs") == blocked
    assert evaluated + blocked == 17 * 3
