"""Campaign 31 tests - cointegration rigor phase 3.

Cross-timeframe cointegration convergence/divergence, regime-conditioned
cointegration persistence (BTC vol/trend regimes), and execution-aware
walk-forward OOS pairs with transaction-cost stress (real data only).
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

EXPECTED_INVARIANTS = {
    "1h": [],
    "4h": ["POL/BTC"],
    "1d": [],
}

REQUIRED_SECTIONS = [
    "regime_conditioned_cointegration_persistence",
    "execution_aware_oos_cost_stress",
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


def test_cointegration_campaign31_artifact_exists_and_schema():
    p = Path("reports/cointegration_campaign31_mt.json")
    assert p.exists(), "Missing reports/cointegration_campaign31_mt.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data.get("real_data_only") is True
    assert data.get("fabricated_data") is False
    assert data.get("causal_only") is True
    assert data.get("trailing_windows_only") is True
    assert data.get("no_lookahead") is True
    assert data.get("fail_closed") is True
    assert data.get("no_auto_lift_of_blocks") is True
    assert data.get("gate_thresholds_unchanged") is True
    assert data.get("gating_invariants_preserved") is True
    assert data.get("type") == "cointegration_campaign31_mt"
    assert data.get("campaign") == 31
    assert isinstance(data.get("pairs"), list)
    assert len(data["pairs"]) >= 17
    assert set(data.get("timeframes") or []) == {"1h", "4h", "1d"}
    assert data.get("expected_invariants") == EXPECTED_INVARIANTS
    assert data.get("heavy_mandate") is True
    assert data.get("coasting_forbidden") is True
    assert not _has_nan(data), "Artifact contains NaN/Inf"
    prov = data.get("provenance") or {}
    assert prov.get("real_data_only") is True
    assert prov.get("fabricated_data") is False
    assert "cross_timeframe_regime_agreement" in data


def test_cointegration_campaign31_preserves_gating_invariants():
    p = Path("reports/cointegration_campaign31_mt.json")
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
        assert eligible_c == set(EXPECTED_INVARIANTS[tf]), f"{tf} invariant drift"
        assert c_r.get("gating_invariants_preserved") is True
        assert c_r.get("n_pairs") == 17


def test_cointegration_campaign31_required_sections_present():
    p = Path("reports/cointegration_campaign31_mt.json")
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
            assert pname in pairs, f"{tf}/{pname} missing"
            pr = pairs[pname]
            assert pr.get("pair") == pname
            assert pr.get("timeframe") == tf
            assert pr.get("real_data_only") is True
            assert pr.get("fabricated_data") is False
            assert pr.get("causal_only") is True
            assert pr.get("trailing_windows_only") is True
            assert pr.get("hard_blocked") == (
                pname not in set(EXPECTED_INVARIANTS[tf])
            )
            assert pr.get("eligible_by_gating") == (
                pname in set(EXPECTED_INVARIANTS[tf])
            )
            for section in REQUIRED_SECTIONS:
                assert section in pr, f"{tf}/{pname} missing {section}"
                sec = pr[section]
                assert isinstance(sec, dict)
                prov = sec.get("provenance") or {}
                assert prov.get("real_data_only") is True
                assert prov.get("fabricated_data") is False
                assert not _has_nan(sec), f"{tf}/{pname}/{section} contains NaN/Inf"
            assert isinstance(pr.get("provenance"), dict)
            pair_prov = pr.get("provenance") or {}
            assert pair_prov.get("real_data_only") is True
            assert pair_prov.get("fabricated_data") is False


def test_cointegration_campaign31_fail_closed_gating():
    p = Path("reports/cointegration_campaign31_mt.json")
    if not p.exists():
        pytest.skip("Missing artifact")
    data = json.loads(p.read_text(encoding="utf-8"))
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        for pname, pr in (c_res[tf].get("pairs") or {}).items():
            cost = pr.get("execution_aware_oos_cost_stress") or {}
            assert cost.get("fail_closed_gating") is True
            if cost.get("robustness_pass") is True:
                assert pr.get("eligible_by_gating") is True, (
                    f"{tf}/{pname} execution-robust despite gating block"
                )
            assert cost.get("execution_aware_robust") == (
                cost.get("robustness_pass") is True and pr.get("eligible_by_gating") is True
            )
            assert pr.get("hard_blocked") == (not pr.get("eligible_by_gating"))


def test_cointegration_campaign31_regime_conditioned_persistence_schema():
    p = Path("reports/cointegration_campaign31_mt.json")
    if not p.exists():
        pytest.skip("Missing artifact")
    data = json.loads(p.read_text(encoding="utf-8"))
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        for pname, pr in (c_res[tf].get("pairs") or {}).items():
            reg = pr.get("regime_conditioned_cointegration_persistence") or {}
            if reg.get("available") is True:
                assert isinstance(reg.get("n_regimes_tested"), int)
                assert reg.get("n_regimes_tested") >= 0
                assert 0.0 <= reg.get("persistence_rate", 0.0) <= 1.0
                assert isinstance(reg.get("regime_conditioned_persistent"), bool)
                assert isinstance(reg.get("results_by_regime"), dict)


def test_cointegration_campaign31_execution_aware_cost_stress_schema():
    p = Path("reports/cointegration_campaign31_mt.json")
    if not p.exists():
        pytest.skip("Missing artifact")
    data = json.loads(p.read_text(encoding="utf-8"))
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        for pname, pr in (c_res[tf].get("pairs") or {}).items():
            cost = pr.get("execution_aware_oos_cost_stress") or {}
            if cost.get("available") is True:
                assert isinstance(cost.get("cost_stress_grid"), list)
                assert len(cost.get("cost_stress_grid")) >= 4
                assert isinstance(cost.get("cost_stress_monotonic"), bool)
                # Cost stress must be monotonic (higher costs never improve returns)
                grid = cost.get("cost_stress_grid") or []
                if len(grid) >= 2:
                    for i in range(1, len(grid)):
                        assert grid[i].get("stressed_mean_return", 0) <= grid[i - 1].get(
                            "stressed_mean_return", 0
                        ) + 1e-12, f"{tf}/{pname} cost stress not monotonic"
                assert isinstance(cost.get("robustness_pass"), bool)


def test_cointegration_campaign31_cross_timeframe_agreement():
    p = Path("reports/cointegration_campaign31_mt.json")
    if not p.exists():
        pytest.skip("Missing artifact")
    data = json.loads(p.read_text(encoding="utf-8"))
    ct = data.get("cross_timeframe_regime_agreement") or {}
    assert ct.get("available") is True
    assert isinstance(ct.get("overall_regime_agreement"), (int, float))
    assert isinstance(ct.get("per_pair"), dict)
    assert len(ct.get("per_pair")) >= 17
    for pname in PAIRS_FOR_CHECK:
        assert pname in ct["per_pair"]
        pp = ct["per_pair"][pname]
        assert "regime_agreement" in pp
        assert "convergent" in pp
        assert "divergent" in pp
        assert isinstance(pp.get("scores_by_tf"), dict)
    prov = ct.get("provenance") or {}
    assert prov.get("real_data_only") is True
    assert prov.get("fabricated_data") is False
