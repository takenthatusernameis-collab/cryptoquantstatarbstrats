from __future__ import annotations

import json
from pathlib import Path

import pytest


def test_execution_realism_mt_schema_and_provenance():
    exec_path = Path("reports/execution_realism_mt.json")
    gating_path = Path("reports/portfolio_gating_mt.json")
    if not exec_path.exists():
        pytest.skip(f"Missing {exec_path}")
    data = json.loads(exec_path.read_text(encoding="utf-8"))
    assert data.get("real_data_only") is True
    assert data.get("fabricated_data") is False
    assert data.get("type") == "execution_realism_mt"
    assert "results_by_timeframe" in data
    assert "assumptions" in data
    ass = data["assumptions"]
    assert ass.get("partial_fills") is True
    assert "latency_assumptions" in ass
    assert "rejection_logic" in ass
    assert "borrow_fee_realism" in ass
    # provenance links
    pl = data.get("provenance_links") or {}
    if gating_path.exists():
        assert pl.get("portfolio_gating_mt") == str(gating_path)

    for tf in ["1h", "4h", "1d"]:
        assert tf in data["results_by_timeframe"]
        r = data["results_by_timeframe"][tf]
        assert "pairs" in r
        pairs = r["pairs"]
        for pname, pinfo in pairs.items():
            assert "execution_blocked_by_gating" in pinfo
            assert "fills" in pinfo
            assert "implementation_shortfall_components" in pinfo
            assert "rejection_log" in pinfo
            assert "tick_lot_applied" in pinfo
            prov = pinfo.get("provenance") or {}
            assert prov.get("real_data_only") is True
            if pinfo.get("execution_blocked_by_gating") is True:
                assert pinfo.get("fills_count", 0) == 0
                assert len(pinfo.get("fills") or []) == 0


def test_turnover_slippage_mt_schema():
    path = Path("reports/turnover_slippage_mt.json")
    gating_path = Path("reports/portfolio_gating_mt.json")
    wf_path = Path("reports/portfolio_walkforward_mt.json")
    if not path.exists():
        pytest.skip(f"Missing {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data.get("real_data_only") is True
    assert data.get("fabricated_data") is False
    assert data.get("type") == "turnover_slippage_mt"
    pl = data.get("provenance_links") or {}
    if gating_path.exists():
        assert pl.get("portfolio_gating_mt") == str(gating_path)
    if wf_path.exists():
        assert pl.get("portfolio_walkforward_mt") == str(wf_path)
    for tf in ["1h", "4h", "1d"]:
        r = data["results_by_timeframe"][tf]
        assert "turnover_daily" in r
        assert "turnover_rolling" in r
        assert "pairs" in r
        assert r.get("linked_to_portfolio_walkforward_mt") is True


def test_execution_stress_grid_mt_schema_and_monotonicity():
    path = Path("reports/execution_stress_grid_mt.json")
    gating_path = Path("reports/portfolio_gating_mt.json")
    if not path.exists():
        pytest.skip(f"Missing {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data.get("real_data_only") is True
    assert data.get("fabricated_data") is False
    assert data.get("type") == "execution_stress_grid_mt"
    assert data.get("monotonicity_enforced") is True
    assert "grids" in data
    pl = data.get("provenance_links") or {}
    if gating_path.exists():
        assert pl.get("portfolio_gating_mt") == str(gating_path)
    for tf in ["1h", "4h", "1d"]:
        r = data["results_by_timeframe"][tf]
        assert "pairs" in r
        for pname, pinfo in r["pairs"].items():
            if pinfo.get("eligible") is True:
                assert pinfo.get("execution_blocked_by_gating") is False
                assert pinfo.get("monotonicity_ok") is True
                assert len(pinfo.get("grid_cells") or []) > 0
            else:
                assert pinfo.get("execution_blocked_by_gating") is True
                assert pinfo.get("breakeven_analysis", {}).get("re_gated_honestly") is True
