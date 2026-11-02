"""Campaign 34 tests - cointegration rigor phase 6.

Fail-closed kill-switch / circuit-breaker execution halting (zero capacity/weight),
regime-transition stress amplification on multi-asset hedge-ratio stability across
volatility/trend regime switches, multi-regime basket cointegration walk-forward OOS
capacity/rebalancing robustness under stress regimes with monotonic fee x slippage
cost-stress grid per regime. Real data only. Preserves gating invariants
(1h 0/17, 4h 1/17 POL/BTC, 1d 0/17).
"""
from __future__ import annotations

import json
import math
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

SYMBOLS_FOR_CHECK = ["ADA", "AVAX", "BNB", "BTC", "DOT", "ETH", "LINK", "LTC", "POL", "SOL", "XRP"]

EXPECTED_INVARIANTS = {
    "1h": [],
    "4h": ["POL/BTC"],
    "1d": [],
}

BASKETS = ["core", "core_expanded", "full_universe"]

REQUIRED_BASKET_SECTIONS = [
    "portfolio_basket_cointegration",
    "regime_transition_stress_amplification",
    "kill_switch_circuit_breaker",
    "multi_regime_basket_cointegration_walk_forward_oos",
    "execution_aware_capacity_allocation",
]


def _has_nan(value) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, float):
        return math.isnan(value) or math.isinf(value)
    if isinstance(value, dict):
        return any(_has_nan(v) for v in value.values())
    if isinstance(value, (list, tuple)):
        return any(_has_nan(v) for v in value)
    return False


def _load(path: Path) -> dict:
    assert path.exists(), f"Missing {path}"
    return json.loads(path.read_text(encoding="utf-8"))


def test_cointegration_campaign34_artifact_exists_and_schema():
    data = _load(Path("reports/cointegration_campaign34_mt.json"))
    assert data.get("real_data_only") is True
    assert data.get("fabricated_data") is False
    assert data.get("causal_only") is True
    assert data.get("trailing_windows_only") is True
    assert data.get("no_lookahead") is True
    assert data.get("fail_closed") is True
    assert data.get("no_auto_lift_of_blocks") is True
    assert data.get("gate_thresholds_unchanged") is True
    assert data.get("gating_invariants_preserved") is True
    assert data.get("type") == "cointegration_campaign34_mt"
    assert data.get("campaign") == 34
    assert isinstance(data.get("pairs"), list)
    assert len(data["pairs"]) >= 17
    assert set(data.get("timeframes") or []) == {"1h", "4h", "1d"}
    assert set(data.get("symbols") or []) == set(SYMBOLS_FOR_CHECK)
    assert set(data.get("baskets") or []) == set(BASKETS)
    assert data.get("expected_invariants") == EXPECTED_INVARIANTS
    assert data.get("heavy_mandate") is True
    assert data.get("coasting_forbidden") is True
    assert not _has_nan(data), "Artifact contains NaN/Inf"
    prov = data.get("provenance") or {}
    assert prov.get("real_data_only") is True
    assert prov.get("fabricated_data") is False


def test_cointegration_campaign34_preserves_gating_invariants():
    data = _load(Path("reports/cointegration_campaign34_mt.json"))
    gating_path = Path("reports/portfolio_gating_mt.json")
    if not gating_path.exists():
        pytest.skip("Missing portfolio gating artifact")
    gating = _load(gating_path)
    g_res = gating.get("results_by_timeframe") or {}
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        g_r = g_res[tf]
        c_r = c_res[tf]
        eligible_g = set(g_r.get("eligible_pairs") or [])
        eligible_c = set(c_r.get("eligible_pairs_gating") or [])
        assert eligible_c == eligible_g, f"{tf} gating eligible set drift"
        assert eligible_c == set(EXPECTED_INVARIANTS[tf]), f"{tf} invariant drift"
        assert c_r.get("gating_invariants_preserved") is True
        assert c_r.get("n_pairs") == 17
        assert c_r.get("n_symbols") == 11


def test_cointegration_campaign34_all_pairs_represented():
    data = _load(Path("reports/cointegration_campaign34_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        pairs = r.get("pairs") or {}
        assert len(pairs) == 17, f"{tf}: expected 17 pairs, got {len(pairs)}"
        for pname in PAIRS_FOR_CHECK:
            assert pname in pairs, f"{tf}/{pname} missing"
            assert pairs[pname] == (pname in set(EXPECTED_INVARIANTS[tf]))


def test_cointegration_campaign34_required_basket_sections():
    data = _load(Path("reports/cointegration_campaign34_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        baskets = r.get("baskets") or {}
        assert len(baskets) == 3, f"{tf}: expected 3 baskets"
        for bname in BASKETS:
            assert bname in baskets, f"{tf}/{bname} missing"
            b = baskets[bname]
            for section in REQUIRED_BASKET_SECTIONS:
                assert section in b, f"{tf}/{bname} missing {section}"
                sec = b[section]
                assert isinstance(sec, dict), f"{tf}/{bname}/{section} not a dict"
                prov = sec.get("provenance") or {}
                assert prov.get("real_data_only") is True
                assert prov.get("fabricated_data") is False
                assert not _has_nan(sec), f"{tf}/{bname}/{section} contains NaN/Inf"


def test_cointegration_campaign34_provenance_all_sections_real_data():
    data = _load(Path("reports/cointegration_campaign34_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        baskets = r.get("baskets") or {}
        for bname in BASKETS:
            b = baskets[bname]
            if not b.get("available"):
                continue
            pbc = b.get("portfolio_basket_cointegration") or {}
            joh = pbc.get("johansen") or {}
            assert joh.get("available") is True
            assert joh.get("provenance", {}).get("real_data_only") is True
            rts = b.get("regime_transition_stress_amplification") or {}
            assert rts.get("provenance", {}).get("real_data_only") is True
            ks = b.get("kill_switch_circuit_breaker") or {}
            assert ks.get("fail_closed") is True
            assert ks.get("cannot_auto_lift") is True
            cap = b.get("execution_aware_capacity_allocation") or {}
            assert cap.get("provenance", {}).get("real_data_only") is True
            rb = b.get("multi_regime_basket_cointegration_walk_forward_oos") or {}
            assert rb.get("provenance", {}).get("real_data_only") is True


def test_cointegration_campaign34_fail_closed_kill_switch():
    data = _load(Path("reports/cointegration_campaign34_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        eligible_g = set(r.get("eligible_pairs_gating") or [])
        eligible_assets: set[str] = set()
        for pname in eligible_g:
            a, b = pname.split("/")
            eligible_assets.add(a)
            eligible_assets.add(b)
        baskets = r.get("baskets") or {}
        for bname in BASKETS:
            b = baskets[bname]
            if not b.get("available"):
                continue
            ks = b.get("kill_switch_circuit_breaker") or {}
            assert ks.get("fail_closed") is True
            assert ks.get("cannot_auto_lift") is True
            assert ks.get("zero_capacity_on_breach") is True
            assert ks.get("breach_alerts_driven_halting") is True
            cap = b.get("execution_aware_capacity_allocation") or {}
            assert cap.get("fail_closed") is True
            assert cap.get("blocked_pairs_zero_capacity") is True
            if ks.get("triggered") is True:
                assert cap.get("kill_switch_active") is True
                assert cap.get("execution_halted") is True
                assert cap.get("n_feasible_assets") == 0
                assert cap.get("total_capacity_notional") == 0.0
                assert cap.get("total_target_notional") == 0.0
                for asset, sym in (cap.get("per_symbol") or {}).items():
                    assert sym.get("feasible") is False
                    assert sym.get("allocated_weight") == 0
                alerts = cap.get("breach_alerts") or []
                halt_types = [a.get("alert_type") for a in alerts]
                assert "kill_switch_circuit_breaker_halt" in halt_types
            rb = b.get("multi_regime_basket_cointegration_walk_forward_oos") or {}
            if rb.get("available") is True:
                assert rb.get("fail_closed_gating") is True
                assert rb.get("multi_regime_stress_tested") is True


def test_cointegration_campaign34_cost_stress_monotonicity_per_regime():
    data = _load(Path("reports/cointegration_campaign34_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        baskets = r.get("baskets") or {}
        for bname in BASKETS:
            b = baskets[bname]
            if not b.get("available"):
                continue
            rb = b.get("multi_regime_basket_cointegration_walk_forward_oos") or {}
            if not rb.get("available"):
                continue
            grid = rb.get("cost_stress_grid") or []
            assert len(grid) >= 4, f"{tf}/{bname} cost grid too small"
            assert rb.get("cost_stress_monotonic") is True, (
                f"{tf}/{bname} cost stress not monotonic"
            )
            prev = None
            for entry in grid:
                assert "fee_bps" in entry and "slippage_bps" in entry
                assert "stressed_mean_return" in entry
                assert "total_cost_bps" in entry
                if prev is not None:
                    assert entry["total_cost_bps"] >= prev["total_cost_bps"]
                    assert entry["stressed_mean_return"] <= prev["stressed_mean_return"] + 1e-12
                prev = entry


def test_cointegration_campaign34_regime_transition_stress_amplification():
    data = _load(Path("reports/cointegration_campaign34_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        baskets = r.get("baskets") or {}
        for bname in BASKETS:
            b = baskets[bname]
            if not b.get("available"):
                continue
            rts = b.get("regime_transition_stress_amplification") or {}
            assert isinstance(rts, dict)
            assert rts.get("provenance", {}).get("real_data_only") is True
            assert rts.get("regime_transition_stress_amplified") is True
            assert rts.get("multi_asset_hedge_ratio_stability_across_switches") is True
            if rts.get("available") is True:
                assert rts.get("regime_switch_stress_quantified") is True
                assert isinstance(rts.get("n_transitions_analyzed"), int)
                assert isinstance(rts.get("n_transitions_with_degradation"), int)
                assert 0.0 <= rts.get("degradation_rate", 0.0) <= 1.0


def test_cointegration_campaign34_breach_alerts_drive_halts():
    data = _load(Path("reports/cointegration_campaign34_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        baskets = r.get("baskets") or {}
        for bname in BASKETS:
            b = baskets[bname]
            if not b.get("available"):
                continue
            cap = b.get("execution_aware_capacity_allocation") or {}
            assert isinstance(cap.get("breach_alerts"), list)
            assert isinstance(cap.get("breach_alerts_present"), bool)
            assert "breach_alert_threshold" in cap
            assert cap.get("zero_capacity_on_breach") is True
            for alert in cap.get("breach_alerts", []):
                assert "alert_type" in alert
                assert "severity" in alert


def test_cointegration_campaign34_no_nan_inf_anywhere():
    data = _load(Path("reports/cointegration_campaign34_mt.json"))
    assert not _has_nan(data), "Campaign 34 artifact contains NaN/Inf"
