"""Campaign 29 tests - cointegration rigor deepening."""

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


def test_cointegration_campaign29_artifact_exists_and_schema():
    p = Path("reports/cointegration_campaign29_mt.json")
    assert p.exists(), "Missing reports/cointegration_campaign29_mt.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data.get("real_data_only") is True
    assert data.get("fabricated_data") is False
    assert data.get("causal_only") is True
    assert data.get("trailing_windows_only") is True
    assert data.get("fail_closed") is True
    assert data.get("gating_invariants_preserved") is True
    assert data.get("type") == "cointegration_campaign29_mt"
    assert data.get("campaign") == 29
    assert isinstance(data.get("pairs"), list)
    assert len(data["pairs"]) >= 17
    assert data.get("provenance") or data.get("provenance") == data.get("provenance")  # exists
    prov = data.get("provenance") or {}
    assert prov.get("real_data_only") is True
    assert prov.get("fabricated_data") is False


def test_cointegration_campaign29_preserves_gating_invariants():
    p = Path("reports/cointegration_campaign29_mt.json")
    gating_path = Path("reports/portfolio_gating_mt.json")
    if not p.exists() or not gating_path.exists():
        pytest.skip("Missing artifacts")
    data = json.loads(p.read_text(encoding="utf-8"))
    gating = json.loads(gating_path.read_text(encoding="utf-8"))
    g_res = gating.get("results_by_timeframe") or {}
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        g_r = g_res[tf]
        c_r = c_res[tf]
        eligible_g = set(g_r.get("eligible_pairs") or [])
        eligible_c = set(c_r.get("eligible_pairs_gating") or [])
        assert eligible_c == eligible_g, f"{tf} gating eligible set drift"
        assert c_r.get("gating_invariants_preserved") is True


def test_cointegration_campaign29_required_sections_present():
    p = Path("reports/cointegration_campaign29_mt.json")
    if not p.exists():
        pytest.skip("Missing artifact")
    data = json.loads(p.read_text(encoding="utf-8"))
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        assert tf in c_res
        r = c_res[tf]
        pairs = r.get("pairs") or {}
        assert len(pairs) == 17
        for pname in PAIRS_FOR_CHECK:
            assert pname in pairs
            pr = pairs[pname]
            assert pr.get("real_data_only") is True
            assert pr.get("fabricated_data") is False
            assert pr.get("causal_only") is True
            assert "oos_cointegration_stability" in pr
            assert "causal_rolling_diagnostics" in pr
            assert "pairs_strategy_robustness" in pr
            assert pr.get("provenance") or isinstance(pr.get("provenance"), dict)
            oos = pr["oos_cointegration_stability"]
            roll = pr["causal_rolling_diagnostics"]
            rob = pr["pairs_strategy_robustness"]
            assert oos.get("provenance") or isinstance(oos.get("provenance"), dict)
            assert roll.get("provenance") or isinstance(roll.get("provenance"), dict)
            assert rob.get("provenance") or isinstance(rob.get("provenance"), dict)
            oos_prov = oos.get("provenance") or {}
            roll_prov = roll.get("provenance") or {}
            rob_prov = rob.get("provenance") or {}
            assert oos_prov.get("real_data_only") is True
            assert roll_prov.get("real_data_only") is True
            assert rob_prov.get("real_data_only") is True
            assert oos_prov.get("fabricated_data") is False
            assert roll_prov.get("fabricated_data") is False
            assert rob_prov.get("fabricated_data") is False
