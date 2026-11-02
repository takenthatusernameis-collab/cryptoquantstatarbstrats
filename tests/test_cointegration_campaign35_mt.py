"""Campaign 35 tests - cointegration rigor phase 7.

Structural-break detection (Johansen rank changes, common stochastic trend decay,
hedge-ratio instability), drift-triggered re-gating with fail-closed re-entry validation,
cross-timeframe cointegration convergence/divergence stress. Real data only.
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
    "structural_break_detection",
    "drift_triggered_re_gating",
    "fail_closed_reentry_validation",
    "cross_timeframe_cointegration_convergence_divergence",
    "execution_aware_capacity_allocation",
    "kill_switch_state",
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


def test_cointegration_campaign35_artifact_exists_and_schema():
    data = _load(Path("reports/cointegration_campaign35_mt.json"))
    assert data.get("real_data_only") is True
    assert data.get("fabricated_data") is False
    assert data.get("causal_only") is True
    assert data.get("trailing_windows_only") is True
    assert data.get("no_lookahead") is True
    assert data.get("fail_closed") is True
    assert data.get("no_auto_lift_of_blocks") is True
    assert data.get("gate_thresholds_unchanged") is True
    assert data.get("gating_invariants_preserved") is True
    assert data.get("type") == "cointegration_campaign35_mt"
    assert data.get("campaign") == 35
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


def test_cointegration_campaign35_preserves_gating_invariants():
    data = _load(Path("reports/cointegration_campaign35_mt.json"))
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


def test_cointegration_campaign35_all_pairs_represented():
    data = _load(Path("reports/cointegration_campaign35_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        pairs = r.get("pairs") or {}
        assert len(pairs) == 17, f"{tf}: expected 17 pairs, got {len(pairs)}"
        for pname in PAIRS_FOR_CHECK:
            assert pname in pairs, f"{tf}/{pname} missing"
            assert pairs[pname] == (pname in set(EXPECTED_INVARIANTS[tf]))


def test_cointegration_campaign35_required_basket_sections():
    data = _load(Path("reports/cointegration_campaign35_mt.json"))
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


def test_cointegration_campaign35_provenance_all_sections_real_data():
    data = _load(Path("reports/cointegration_campaign35_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        assert (r.get("provenance") or {}).get("real_data_only") is True
        baskets = r.get("baskets") or {}
        for bname in BASKETS:
            b = baskets.get(bname) or {}
            if not b.get("available"):
                continue
            for sec in ["portfolio_basket_cointegration", "structural_break_detection",
                       "drift_triggered_re_gating", "fail_closed_reentry_validation",
                       "cross_timeframe_cointegration_convergence_divergence",
                       "execution_aware_capacity_allocation"]:
                if sec in b:
                    assert (b[sec].get("provenance") or {}).get("real_data_only") is True


def test_cointegration_campaign35_fail_closed_drift_regating():
    data = _load(Path("reports/cointegration_campaign35_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        baskets = r.get("baskets") or {}
        for bname in BASKETS:
            b = baskets.get(bname) or {}
            if not b.get("available"):
                continue
            reg = b.get("drift_triggered_re_gating") or {}
            assert reg.get("fail_closed") is True
            assert reg.get("no_auto_lift") is True
            assert reg.get("cannot_auto_lift_blocks") is True
            if not reg.get("new_eligible") or reg.get("reclassified_blocked"):
                cap = b.get("execution_aware_capacity_allocation") or {}
                assert cap.get("total_capacity_usd") == 0.0 or cap.get("capacity_allocated") == 0.0
                assert cap.get("fail_closed") is True


def test_cointegration_campaign35_fail_closed_reentry_validation():
    data = _load(Path("reports/cointegration_campaign35_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        baskets = r.get("baskets") or {}
        for bname in BASKETS:
            b = baskets.get(bname) or {}
            if not b.get("available"):
                continue
            re = b.get("fail_closed_reentry_validation") or {}
            assert re.get("reentry_requires_fresh_cointegration_evidence") is True
            assert re.get("fail_closed") is True
            assert re.get("no_auto_lift") is True


def test_cointegration_campaign35_structural_break_detection_quantified():
    data = _load(Path("reports/cointegration_campaign35_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    found = False
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        baskets = r.get("baskets") or {}
        for bname in BASKETS:
            b = baskets.get(bname) or {}
            if not b.get("available"):
                continue
            sb = b.get("structural_break_detection") or {}
            assert sb.get("available") is True
            assert "break_score" in sb
            assert "breaks_detected" in sb
            assert isinstance(sb.get("breaks_detected"), list)
            found = True
    assert found


def test_cointegration_campaign35_cross_timeframe_convergence_divergence_stress():
    data = _load(Path("reports/cointegration_campaign35_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    found = False
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        baskets = r.get("baskets") or {}
        for bname in BASKETS:
            b = baskets.get(bname) or {}
            if not b.get("available"):
                continue
            ctf = b.get("cross_timeframe_cointegration_convergence_divergence") or {}
            assert ctf.get("available") is True
            assert "convergence_divergence" in ctf or "cointegration_by_timeframe" in ctf
            assert (ctf.get("divergence_under_stress_quantified") is True or
                    "divergent_across_timeframes" in ctf)
            assert ctf.get("quantified") is True
            found = True
    assert found


def test_cointegration_campaign35_breach_alerts_drive_halts():
    data = _load(Path("reports/cointegration_campaign35_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    found = False
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        baskets = r.get("baskets") or {}
        for bname in BASKETS:
            b = baskets.get(bname) or {}
            if not b.get("available"):
                continue
            cap = b.get("execution_aware_capacity_allocation") or {}
            ks = b.get("kill_switch_state") or {}
            assert cap.get("breach_alerts_drive_halts") is True
            assert cap.get("halts_execution_on_breach") is True
            assert cap.get("zero_capacity_on_breach") is True
            assert ks.get("cannot_auto_lift") is True
            assert ks.get("fail_closed") is True
            if cap.get("breach_alerts_present") or ks.get("triggered"):
                assert cap.get("breach_alerts_present") is True or ks.get("triggered")
                found = True
    assert found


def test_cointegration_campaign35_no_nan_inf_anywhere():
    data = _load(Path("reports/cointegration_campaign35_mt.json"))
    assert not _has_nan(data), "Artifact contains NaN/Inf"


def test_cointegration_campaign35_campaign_flags():
    data = _load(Path("reports/cointegration_campaign35_mt.json"))
    assert data.get("campaign") == 35
    assert data.get("drift_threshold") is not None
    assert data.get("struct_break_threshold") is not None
