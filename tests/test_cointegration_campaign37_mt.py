"""Campaign 37 tests - cointegration rigor phase 9.

Regime-transition prediction & adaptive gate recalibration across 1h/4h/1d on real
Binance cached data. Using Campaign 36 baseline, predicts impending cointegration
gate failure, does adaptive recalibration, proactive de-risking, backtested predictive
accuracy (precision/recall/F1), fail-closed re-gating on predicted breach with no
auto-lift, breach alerts drive halts. Real data only. Preserves gating invariants
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

REQUIRED_TIMEFRAME_SECTIONS = [
    "regime_transition_prediction",
    "regime_transition_probability_matrices",
    "gate_failure_lead_time_estimation",
    "gate_failure_lead_time_distributions",
    "adaptive_gate_recalibration",
    "adaptive_threshold_schedules",
    "proactive_de_risking",
    "proactive_capacity_weight_zeroing",
    "backtested_predictive_accuracy",
    "prediction_summary",
    "fail_closed_regime_transition_regating",
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


def test_cointegration_campaign37_artifact_exists_and_schema():
    data = _load(Path("reports/cointegration_campaign37_mt.json"))
    assert data.get("type") == "cointegration_campaign37_mt"
    assert data.get("campaign") == 37
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
    c36 = data.get("campaign36_baseline") or {}
    assert c36.get("loaded") is True or Path("reports/cointegration_campaign36_mt.json").exists()


def test_cointegration_campaign37_preserves_gating_invariants():
    data = _load(Path("reports/cointegration_campaign37_mt.json"))
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


def test_cointegration_campaign37_all_pairs_represented():
    data = _load(Path("reports/cointegration_campaign37_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        pairs = r.get("pairs") or {}
        assert len(pairs) == 17
        for pname in PAIRS_FOR_CHECK:
            assert pname in pairs
            assert pairs[pname] == (pname in set(EXPECTED_INVARIANTS[tf]))


def test_cointegration_campaign37_required_sections():
    data = _load(Path("reports/cointegration_campaign37_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        for section in REQUIRED_TIMEFRAME_SECTIONS:
            assert section in r, f"{tf} missing {section}"
        # check provenance on key sections
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


def test_cointegration_campaign37_regime_transition_probability_quantified():
    data = _load(Path("reports/cointegration_campaign37_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    found = False
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        preds = r.get("regime_transition_prediction") or {}
        for pname in PAIRS_FOR_CHECK:
            p = preds.get(pname) or {}
            if p.get("available"):
                assert "regime_transition_probability" in p
                v = p["regime_transition_probability"]
                assert v is None or (
                    isinstance(v, (int, float)) and not math.isnan(v) and 0.0 <= float(v) <= 1.0
                )
                found = True
    assert found


def test_cointegration_campaign37_gate_failure_lead_time_quantified():
    data = _load(Path("reports/cointegration_campaign37_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    found = False
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        glt = r.get("gate_failure_lead_time_estimation") or {}
        for pname in PAIRS_FOR_CHECK:
            g = glt.get(pname) or {}
            if isinstance(g, dict) and g.get("available") is not False:
                assert "mean_lead_time_bars" in g or "n_failures_observed" in g
                found = True
    assert found


def test_cointegration_campaign37_predictive_accuracy_precision_recall_f1():
    data = _load(Path("reports/cointegration_campaign37_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    found = False
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        pa_all = r.get("backtested_predictive_accuracy") or {}
        ps = r.get("prediction_summary") or {}
        ppa = ps.get("portfolio_predictive_accuracy") or {}
        if (
            ppa.get("precision_mean") is not None
            or ppa.get("recall_mean") is not None
            or ppa.get("f1_mean") is not None
        ):
            found = True
        for pname in PAIRS_FOR_CHECK:
            pa = pa_all.get(pname) or {}
            if isinstance(pa, dict) and pa.get("available"):
                for k in ["precision", "recall", "f1"]:
                    assert k in pa
                    v = pa[k]
                    assert isinstance(v, (int, float)) and not math.isnan(v)
                found = True
    assert found


def test_cointegration_campaign37_adaptive_recalibration_and_proactive_derisking():
    data = _load(Path("reports/cointegration_campaign37_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        recal = r.get("adaptive_gate_recalibration") or {}
        derisk = r.get("proactive_de_risking") or {}
        r.get("adaptive_threshold_schedules") or {}
        pz = r.get("proactive_capacity_weight_zeroing") or {}
        for pname in PAIRS_FOR_CHECK:
            rc = recal.get(pname) or {}
            if isinstance(rc, dict) and rc.get("available"):
                assert "adaptive_thresholds" in rc
                at = rc["adaptive_thresholds"]
                assert "eg_p_max" in at and "half_life_min" in at
            dd = derisk.get(pname) or {}
            if isinstance(dd, dict) and dd.get("available"):
                assert "capacity_factor" in dd
                assert "weight_factor" in dd
                assert dd.get("fail_closed") is True
            assert pname in pz


def test_cointegration_campaign37_fail_closed_regime_transition_regating_no_auto_lift():
    data = _load(Path("reports/cointegration_campaign37_mt.json"))
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
            assert "base_eligible" in g
            if not g.get("base_eligible"):
                assert g.get("new_eligible") is False
            if g.get("base_eligible") and not g.get("new_eligible"):
                cap = r.get("execution_aware_capacity_allocation") or {}
                per_pair = cap.get("per_pair") or {}
                pp = per_pair.get(pname) or {}
                if pp.get("available") is not False and isinstance(pp, dict):
                    ok_block = (
                        pp.get("allocated_weight") == 0.0
                        or pp.get("zero_capacity_on_block") is True
                    )
                    assert ok_block


def test_cointegration_campaign37_reentry_requires_fresh_evidence_and_regime_stability():
    data = _load(Path("reports/cointegration_campaign37_mt.json"))
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
            assert reentry.get("fail_closed") is True
            assert reentry.get("no_auto_lift") is True


def test_cointegration_campaign37_breach_alerts_drive_halts():
    data = _load(Path("reports/cointegration_campaign37_mt.json"))
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
        cap_has = isinstance(cap, dict) and cap.get("breach_alerts_present")
        if ks.get("triggered") or len(alerts) > 0 or cap_has:
            found = True
    assert found


def test_cointegration_campaign37_baskets_multi_asset_hedge_ratios_portfolio_spreads():
    data = _load(Path("reports/cointegration_campaign37_mt.json"))
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


def test_cointegration_campaign37_no_nan_inf_anywhere():
    data = _load(Path("reports/cointegration_campaign37_mt.json"))
    assert not _has_nan(data), "Artifact contains NaN/Inf"


def test_cointegration_campaign37_campaign_flags():
    data = _load(Path("reports/cointegration_campaign37_mt.json"))
    assert data.get("campaign") == 37
    assert data.get("type") == "cointegration_campaign37_mt"
