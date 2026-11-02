"""Campaign 38 tests - cointegration rigor phase 10.

Cross-timeframe cointegration gate synchronization & portfolio-level regime-coupling
stress testing across 1h/4h/1d on real Binance cached data. Using Campaign 37 outputs,
builds cross-timeframe gate synchronization, portfolio-level regime-coupling, cross-timeframe
adaptive recalibration, portfolio-level fail-closed re-gating with basket blocking,
cross-timeframe predictive accuracy (precision/recall/F1), fail-closed re-gating on
cross-timeframe predicted breach with no auto-lift, portfolio-level kill-switch halts.
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
    "cross_timeframe_cointegration_gate_synchronization",
    "cross_timeframe_gate_synchronization_matrices",
    "portfolio_level_regime_coupling",
    "portfolio_level_regime_coupling_stress",
    "portfolio_level_regime_coupling_stress_matrices",
    "cross_timeframe_adaptive_gate_recalibration",
    "cross_timeframe_adaptive_recalibration_thresholds",
    "adaptive_threshold_schedules",
    "portfolio_level_fail_closed_regating",
    "portfolio_level_basket_blocking",
    "fail_closed_regime_transition_regating",
    "fail_closed_re_gating_cross_timeframe",
    "cross_timeframe_predictive_accuracy",
    "backtested_cross_timeframe_predictive_accuracy",
    "prediction_summary",
    "fail_closed_reentry_validation",
    "kill_switch_state",
    "breach_alerts",
    "execution_aware_capacity_allocation",
    "baskets",
]

REQUIRED_BASKET_SECTIONS = [
    "portfolio_basket_cointegration",
    "multi_asset_hedge_ratios",
    "portfolio_spreads",
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
        for key in [
            "kill_switch_state",
            "execution_aware_capacity_allocation",
            "prediction_summary",
        ]:
            sec = r.get(key) or {}
            if isinstance(sec, dict) and sec.get("available") is not False:
                prov = sec.get("provenance") or {}
                assert prov.get("real_data_only") is True
                assert prov.get("fabricated_data") is False


def test_cointegration_campaign38_cross_timeframe_sync_quantified():
    data = _load(Path("reports/cointegration_campaign38_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    found = False
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        sync = r.get("cross_timeframe_cointegration_gate_synchronization") or {}
        for pname in PAIRS_FOR_CHECK:
            s = sync.get(pname) or {}
            if isinstance(s, dict) and s.get("available"):
                assert "cross_timeframe_gate_failure_cooccurrence" in s
                assert "synchronization_score" in s
                found = True
    assert found


def test_cointegration_campaign38_portfolio_regime_coupling_quantified():
    data = _load(Path("reports/cointegration_campaign38_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        coupl = r.get("portfolio_level_regime_coupling_stress") or {}
        assert len(coupl) == 3
        for bname in BASKETS:
            assert bname in coupl
            b = coupl[bname]
            assert "mean_coupling" in b
            assert "propagation_risk" in b


def test_cointegration_campaign38_cross_timeframe_predictive_accuracy_precision_recall_f1():
    data = _load(Path("reports/cointegration_campaign38_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    found = False
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        pa = r.get("cross_timeframe_predictive_accuracy") or {}
        ps = r.get("prediction_summary") or {}
        if (
            pa.get("precision_mean") is not None
            or pa.get("recall_mean") is not None
            or pa.get("f1_mean") is not None
            or ps.get("precision_mean") is not None
        ):
            found = True
        for k in ["precision", "recall", "f1"]:
            if pa.get(k) is not None:
                v = pa[k]
                assert isinstance(v, (int, float)) and not math.isnan(v)
        for k in ["precision_mean", "recall_mean", "f1_mean"]:
            if pa.get(k) is not None:
                v = pa[k]
                assert isinstance(v, (int, float)) and not math.isnan(v)
    assert found


def test_cointegration_campaign38_fail_closed_cross_timeframe_regating_no_auto_lift():
    data = _load(Path("reports/cointegration_campaign38_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        rg = r.get("fail_closed_regime_transition_regating") or {}
        for pname in PAIRS_FOR_CHECK:
            g = rg.get(pname) or {}
            if not isinstance(g, dict) or not g.get("available"):
                continue
            assert g.get("fail_closed") is True
            assert g.get("no_auto_lift") is True
            assert g.get("cannot_auto_lift_blocks") is True
            assert "reclassified_blocked" in g
            assert "new_eligible" in g
            if not g.get("base_eligible"):
                assert g.get("new_eligible") is False


def test_cointegration_campaign38_basket_blocking_all_pairs():
    data = _load(Path("reports/cointegration_campaign38_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        pb = r.get("portfolio_level_basket_blocking") or {}
        assert len(pb) == 3
        for bname in BASKETS:
            assert bname in pb
            b = pb[bname]
            assert b.get("fail_closed") is True
            assert b.get("no_auto_lift") is True
            assert "entire_basket_blocked" in b
            assert "zero_capacity_weight_all_pairs_in_basket" in b


def test_cointegration_campaign38_reentry_requires_fresh_evidence_across_all_timeframes():
    data = _load(Path("reports/cointegration_campaign38_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        re = r.get("fail_closed_reentry_validation") or {}
        for pname in PAIRS_FOR_CHECK:
            reentry = re.get(pname) or {}
            if not isinstance(reentry, dict):
                continue
            assert reentry.get("reentry_requires_fresh_cointegration_evidence") is True
            assert reentry.get("reentry_requires_regime_stability_confirmation") is True
            assert (
                reentry.get("reentry_requires_fresh_cointegration_evidence_across_all_timeframes")
                is True
            )
            assert reentry.get("fail_closed") is True
            assert reentry.get("no_auto_lift") is True


def test_cointegration_campaign38_breach_alerts_drive_halts_cross_timeframe():
    data = _load(Path("reports/cointegration_campaign38_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    found = False
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        ks = r.get("kill_switch_state") or {}
        cap = r.get("execution_aware_capacity_allocation") or {}
        alerts = r.get("breach_alerts") or []
        assert ks.get("fail_closed") is True
        assert ks.get("cannot_auto_lift") is True
        assert ks.get("breach_alerts_drive_halts") is True
        if isinstance(cap, dict):
            assert cap.get("breach_alerts_drive_halts") is True
            assert cap.get("zero_capacity_on_breach") is True
            assert cap.get("fail_closed") is True
        if ks.get("triggered") or len(alerts) > 0 or (
            isinstance(cap, dict) and cap.get("breach_alerts_present")
        ):
            found = True
    assert found


def test_cointegration_campaign38_baskets_multi_asset_hedge_ratios_portfolio_spreads():
    data = _load(Path("reports/cointegration_campaign38_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        baskets = r.get("baskets") or {}
        assert len(baskets) == 3
        for bname in BASKETS:
            assert bname in baskets
            b = baskets[bname]
            for section in REQUIRED_BASKET_SECTIONS:
                assert section in b, f"{tf}/{bname} missing {section}"
            bc = b.get("portfolio_basket_cointegration") or {}
            if bc.get("available"):
                prov = bc.get("provenance") or {}
                assert prov.get("real_data_only") is True
                assert prov.get("fabricated_data") is False


def test_cointegration_campaign38_no_nan_inf_anywhere():
    data = _load(Path("reports/cointegration_campaign38_mt.json"))
    assert not _has_nan(data), "Artifact contains NaN/Inf"


def test_cointegration_campaign38_campaign_flags():
    data = _load(Path("reports/cointegration_campaign38_mt.json"))
    assert data.get("campaign") == 38
    assert data.get("type") == "cointegration_campaign38_mt"
