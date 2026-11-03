"""Campaign 38 tests - cointegration rigor phase 10.

Cross-timeframe gate synchronization & portfolio-level regime-coupling stress
testing across 1h/4h/1d on real Binance cached data. Uses Campaign 37 baseline.
Quantifies cross-timeframe sync, portfolio regime coupling, adaptive recalibration,
portfolio-level fail-closed re-gating with basket blocking, cross-timeframe
predictive accuracy, and portfolio-level kill-switch halts with no auto-lift.
Real data only. Preserves gating invariants (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17).
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

REQUIRED_TIMEFRAME_SECTIONS = [
    "cross_timeframe_sync",
    "portfolio_regime_coupling",
    "adaptive_recalibration",
    "portfolio_fail_closed_regating",
    "cross_timeframe_prediction_accuracy",
    "basket_cointegration",
    "multi_asset_hedge_ratios",
    "portfolio_spreads",
    "execution_aware_capacity_allocation",
    "kill_switch_state",
    "breach_alerts",
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


def test_cointegration_campaign38_artifact_exists_and_schema():
    data = _load(Path("reports/cointegration_campaign38_mt.json"))
    assert data.get("type") == "cointegration_campaign38_mt"
    assert data.get("campaign") == 38
    assert data.get("real_data_only") is True
    assert data.get("fabricated_data") is False
    assert data.get("causal_only") is True
    assert data.get("trailing_windows_only") is True
    assert data.get("no_lookahead") is True
    assert data.get("fail_closed") is True
    assert data.get("no_auto_lift_of_blocks") is True
    assert data.get("gate_thresholds_unchanged") is True
    assert data.get("gating_invariants_preserved") is True
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
    c37 = data.get("campaign37_baseline") or {}
    assert c37.get("loaded") is True or Path("reports/cointegration_campaign37_mt.json").exists()


def test_cointegration_campaign38_preserves_gating_invariants():
    data = _load(Path("reports/cointegration_campaign38_mt.json"))
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


def test_cointegration_campaign38_all_pairs_represented():
    data = _load(Path("reports/cointegration_campaign38_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        pairs = r.get("pairs") or {}
        assert len(pairs) == 17
        for pname in PAIRS_FOR_CHECK:
            assert pname in pairs
            assert pairs[pname] == (pname in set(EXPECTED_INVARIANTS[tf]))


def test_cointegration_campaign38_required_sections():
    data = _load(Path("reports/cointegration_campaign38_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        for section in REQUIRED_TIMEFRAME_SECTIONS:
            assert section in r, f"{tf} missing {section}"
        for key in ["kill_switch_state", "execution_aware_capacity_allocation"]:
            sec = r.get(key) or {}
            if isinstance(sec, dict):
                prov = sec.get("provenance") or {}
                assert prov.get("real_data_only") is True
                assert prov.get("fabricated_data") is False


def test_cointegration_campaign38_cross_timeframe_sync_quantified():
    data = _load(Path("reports/cointegration_campaign38_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    found = False
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        cts = r.get("cross_timeframe_sync") or {}
        assert "matrices" in cts
        assert "per_pair_sync" in cts
        assert "global_sync_matrix" in cts
        pps = cts.get("per_pair_sync") or {}
        for pname in PAIRS_FOR_CHECK:
            p = pps.get(pname) or {}
            assert "sync_score" in p
            assert "co_occuring" in p
            assert "probabilities_by_timeframe" in p
            found = True
    assert found


def test_cointegration_campaign38_portfolio_regime_coupling_quantified():
    data = _load(Path("reports/cointegration_campaign38_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        prc = r.get("portfolio_regime_coupling") or {}
        assert "basket_correlation_structure" in prc
        assert "propagation_matrices" in prc
        # all baskets represented
        bcs = prc.get("basket_correlation_structure") or {}
        for b in BASKETS:
            assert b in bcs


def test_cointegration_campaign38_adaptive_recalibration_across_timeframes():
    data = _load(Path("reports/cointegration_campaign38_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        ar = r.get("adaptive_recalibration") or {}
        assert "threshold_schedules" in ar
        assert "per_pair_recalibration" in ar
        ppr = ar.get("per_pair_recalibration") or {}
        for pname in PAIRS_FOR_CHECK:
            p = ppr.get(pname) or {}
            if isinstance(p, dict) and p.get("available"):
                assert "adaptive_thresholds" in p
                at = p["adaptive_thresholds"]
                assert "eg_p_max" in at


def test_cointegration_campaign38_portfolio_fail_closed_basket_blocking_no_auto_lift():
    data = _load(Path("reports/cointegration_campaign38_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        pfr = r.get("portfolio_fail_closed_regating") or {}
        assert pfr.get("no_auto_lift") is True
        re = pfr.get("reentry_requirements") or {}
        assert re.get("requires_fresh_cointegration_evidence_across_all_timeframes") is True
        assert re.get("requires_regime_stability_confirmation") is True
        bb = pfr.get("basket_blocking") or {}
        for b in BASKETS:
            assert b in bb
            blk = bb[b]
            if blk.get("blocked"):
                assert blk.get("capacity") == 0.0
                assert blk.get("weight") == 0.0
                assert blk.get("fail_closed") is True
        ppr = pfr.get("per_pair_regating") or {}
        for pname in PAIRS_FOR_CHECK:
            pr = ppr.get(pname) or {}
            if pr.get("basket_blocked") or pr.get("predicted_breach"):
                assert pr.get("capacity") == 0.0
                assert pr.get("weight") == 0.0
                assert pr.get("fail_closed") is True
                assert pr.get("no_auto_lift") is True


def test_cointegration_campaign38_cross_timeframe_predictive_accuracy_precision_recall_f1():
    data = _load(Path("reports/cointegration_campaign38_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    found = False
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        cpa = r.get("cross_timeframe_prediction_accuracy") or {}
        pa = cpa.get("portfolio_accuracy") or {}
        for k in ["precision", "recall", "f1"]:
            assert k in pa
            v = pa[k]
            assert isinstance(v, (int, float)) and not math.isnan(v)
        ppa = cpa.get("per_pair_accuracy") or {}
        for pname in PAIRS_FOR_CHECK:
            p = ppa.get(pname) or {}
            assert isinstance(p, dict)
            for k in ["precision", "recall", "f1"]:
                assert k in p
            found = True
    assert found


def test_cointegration_campaign38_basket_cointegration_multi_asset_hedge_portfolio_spreads():
    data = _load(Path("reports/cointegration_campaign38_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        assert "basket_cointegration" in r
        assert "multi_asset_hedge_ratios" in r
        assert "portfolio_spreads" in r
        bc = r["basket_cointegration"]
        mah = r["multi_asset_hedge_ratios"]
        ps = r["portfolio_spreads"]
        for b in BASKETS:
            assert b in bc
            assert b in mah
            assert b in ps


def test_cointegration_campaign38_kill_switch_breach_alerts_drive_halts_no_auto_lift():
    data = _load(Path("reports/cointegration_campaign38_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        ks = r.get("kill_switch_state") or {}
        ea = r.get("execution_aware_capacity_allocation") or {}
        alerts = r.get("breach_alerts") or []
        assert ea.get("breach_alerts_drive_halts") is True
        assert ea.get("halt_execution_on_predicted_breach") is True
        assert ks.get("no_auto_lift") is True
        assert ks.get("cannot_auto_lift") is True
        re = ks.get("reentry_requirements") or {}
        assert re.get("fresh_cointegration_evidence_across_all_timeframes") is True
        assert re.get("regime_stability_confirmation") is True
        if ks.get("triggered"):
            assert isinstance(alerts, list) and len(alerts) > 0
            for a in alerts:
                assert a.get("fail_closed") is True
                assert a.get("no_auto_lift") is True
                assert a.get("action") == "halt_execution"
