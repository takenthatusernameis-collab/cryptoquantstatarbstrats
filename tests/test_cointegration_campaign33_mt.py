"""Campaign 33 tests - cointegration rigor phase 5.

Portfolio-level cointegration regime-transition stress (volatility/trend
regime-switch stress), tightened execution-aware capacity allocation with real
Binance quote-volume liquidity constraints and participation-cap breach alerts
(fail-closed), and basket cointegration walk-forward OOS capacity/rebalancing
robustness with a monotonic fee x slippage cost-stress grid (real data only).
Preserves gating invariants (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17).
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
    "regime_conditioned_spread",
    "regime_transition_stress",
    "regime_conditioned_portfolio_rebalancing",
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


def test_cointegration_campaign33_artifact_exists_and_schema():
    data = _load(Path("reports/cointegration_campaign33_mt.json"))
    assert data.get("real_data_only") is True
    assert data.get("fabricated_data") is False
    assert data.get("causal_only") is True
    assert data.get("trailing_windows_only") is True
    assert data.get("no_lookahead") is True
    assert data.get("fail_closed") is True
    assert data.get("no_auto_lift_of_blocks") is True
    assert data.get("gate_thresholds_unchanged") is True
    assert data.get("gating_invariants_preserved") is True
    assert data.get("type") == "cointegration_campaign33_mt"
    assert data.get("campaign") == 33
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


def test_cointegration_campaign33_preserves_gating_invariants():
    data = _load(Path("reports/cointegration_campaign33_mt.json"))
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


def test_cointegration_campaign33_all_pairs_represented():
    data = _load(Path("reports/cointegration_campaign33_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        pairs = r.get("pairs") or {}
        assert len(pairs) == 17, f"{tf}: expected 17 pairs, got {len(pairs)}"
        for pname in PAIRS_FOR_CHECK:
            assert pname in pairs, f"{tf}/{pname} missing"
            assert pairs[pname] == (pname in set(EXPECTED_INVARIANTS[tf]))


def test_cointegration_campaign33_required_basket_sections():
    data = _load(Path("reports/cointegration_campaign33_mt.json"))
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


def test_cointegration_campaign33_provenance_all_sections_real_data():
    data = _load(Path("reports/cointegration_campaign33_mt.json"))
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
            cst = pbc.get("common_stochastic_trend") or {}
            assert cst.get("provenance", {}).get("real_data_only") is True
            cap = b.get("execution_aware_capacity_allocation") or {}
            assert cap.get("provenance", {}).get("real_data_only") is True
            rb = b.get("regime_conditioned_portfolio_rebalancing") or {}
            assert rb.get("provenance", {}).get("real_data_only") is True
            rts = b.get("regime_transition_stress") or {}
            assert rts.get("provenance", {}).get("real_data_only") is True


def test_cointegration_campaign33_fail_closed_gating_and_capacity():
    data = _load(Path("reports/cointegration_campaign33_mt.json"))
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
            cap = b.get("execution_aware_capacity_allocation") or {}
            assert cap.get("fail_closed") is True
            assert cap.get("blocked_pairs_zero_capacity") is True
            assert cap.get("real_liquidity_constraints") is True
            assert cap.get("eligible_assets") == sorted(list(eligible_assets)), (
                f"{tf}/{bname} eligible_assets drift"
            )
            n_feasible = cap.get("n_feasible_assets", 0)
            assert 0 <= n_feasible <= len(eligible_assets), (
                f"{tf}/{bname} n_feasible {n_feasible} exceeds eligible assets"
            )
            per_symbol = cap.get("per_symbol") or {}
            for asset, sym in per_symbol.items():
                in_eligible = asset in eligible_assets
                if not in_eligible:
                    assert sym.get("feasible") is False, (
                        f"{tf}/{bname}/{asset} feasible despite gating block"
                    )
                    assert sym.get("allocated_weight") == 0, (
                        f"{tf}/{bname}/{asset} non-zero weight despite gating block"
                    )
                    assert "pair_gating_blocked_zero_capacity" in (sym.get("blocked_reason") or [])
            rb = b.get("regime_conditioned_portfolio_rebalancing") or {}
            if rb.get("available") is True:
                assert rb.get("fail_closed_gating") is True
                assert rb.get("execution_aware_robust") == (
                    rb.get("robustness_pass") is True
                    and rb.get("eligible_by_gating") is True
                )


def test_cointegration_campaign33_cost_stress_monotonicity():
    data = _load(Path("reports/cointegration_campaign33_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        baskets = r.get("baskets") or {}
        for bname in BASKETS:
            b = baskets[bname]
            if not b.get("available"):
                continue
            rb = b.get("regime_conditioned_portfolio_rebalancing") or {}
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
                    assert entry["stressed_mean_return"] <= prev["stressed_mean_return"] + 1e-12, (
                        f"{tf}/{bname} cost stress not monotonic: {prev} -> {entry}"
                    )
                prev = entry


def test_cointegration_campaign33_basket_cointegration_structure():
    data = _load(Path("reports/cointegration_campaign33_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        baskets = r.get("baskets") or {}
        for bname in BASKETS:
            b = baskets[bname]
            if not b.get("available"):
                continue
            pbc = b.get("portfolio_basket_cointegration") or {}
            assert pbc.get("basket") == bname
            assert isinstance(pbc.get("n_assets"), int) and pbc["n_assets"] >= 2
            joh = pbc.get("johansen") or {}
            assert isinstance(joh.get("rank_trace_95"), int)
            assert isinstance(joh.get("rank_maxeig_95"), int)
            assert isinstance(joh.get("cointegrated"), bool)
            cst = pbc.get("common_stochastic_trend") or {}
            assert isinstance(cst.get("evidence"), bool)
            assert isinstance(cst.get("rank_trace_95"), int)
            assert 0.0 <= cst.get("frac_windows_rank_ge_1", 0.0) <= 1.0
            roll = pbc.get("rolling_rank_stability") or {}
            if roll.get("available") is True:
                assert isinstance(roll.get("rank_stable"), bool)
                assert isinstance(roll.get("n_windows"), int) and roll["n_windows"] >= 1


def test_cointegration_campaign33_regime_transition_stress():
    data = _load(Path("reports/cointegration_campaign33_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        baskets = r.get("baskets") or {}
        for bname in BASKETS:
            b = baskets[bname]
            if not b.get("available"):
                continue
            rts = b.get("regime_transition_stress") or {}
            assert isinstance(rts, dict)
            assert rts.get("provenance", {}).get("real_data_only") is True
            if rts.get("available") is True:
                assert rts.get("regime_switch_stress_quantified") is True
                assert isinstance(rts.get("n_transitions_analyzed"), int)
                assert isinstance(rts.get("n_transitions_with_degradation"), int)
                assert 0.0 <= rts.get("degradation_rate", 0.0) <= 1.0


def test_cointegration_campaign33_breach_alerts():
    data = _load(Path("reports/cointegration_campaign33_mt.json"))
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
            for alert in cap.get("breach_alerts", []):
                assert "alert_type" in alert
                assert "severity" in alert
                assert "utilization" in alert


def test_cointegration_campaign33_no_nan_inf_anywhere():
    data = _load(Path("reports/cointegration_campaign33_mt.json"))
    assert not _has_nan(data), "Campaign 33 artifact contains NaN/Inf"
