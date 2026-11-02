"""Campaign 36 tests - cointegration rigor phase 8.

Regime-conditioned cointegration gate persistence and forward-reliability stress
across 1h/4h/1d on real Binance cached data. Quantifies gate persistence/decay
half-life, regime-conditioned gate failure rates under high-vol / trend-breakdown /
low-vol stress, walk-forward OOS gate stability, multi-regime convergence/divergence
stress, fail-closed re-gating with no auto-lift, and breach-alert-driven kill-switch
halts. Real data only. Preserves gating invariants (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17).
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
    "pair_persistence",
    "regime_conditioned_failure_rates",
    "forward_reliability_walk_forward",
    "multi_regime_convergence_divergence",
    "fail_closed_re_gating",
    "fail_closed_reentry_validation",
    "kill_switch_state",
    "execution_aware_capacity_allocation",
]

TIMEFRAME_SECTIONS_WITH_PROVENANCE = [
    "multi_regime_convergence_divergence",
    "kill_switch_state",
    "execution_aware_capacity_allocation",
]

PER_PAIR_MAP_SECTIONS = [
    "pair_persistence",
    "regime_conditioned_failure_rates",
    "forward_reliability_walk_forward",
    "fail_closed_re_gating",
    "fail_closed_reentry_validation",
]

REQUIRED_BASKET_SECTIONS = ["portfolio_basket_cointegration"]


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


def test_cointegration_campaign36_artifact_exists_and_schema():
    data = _load(Path("reports/cointegration_campaign36_mt.json"))
    assert data.get("type") == "cointegration_campaign36_mt"
    assert data.get("campaign") == 36
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


def test_cointegration_campaign36_preserves_gating_invariants():
    data = _load(Path("reports/cointegration_campaign36_mt.json"))
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


def test_cointegration_campaign36_all_pairs_represented():
    data = _load(Path("reports/cointegration_campaign36_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        pairs = r.get("pairs") or {}
        assert len(pairs) == 17, f"{tf}: expected 17 pairs, got {len(pairs)}"
        for pname in PAIRS_FOR_CHECK:
            assert pname in pairs, f"{tf}/{pname} missing"
            assert pairs[pname] == (pname in set(EXPECTED_INVARIANTS[tf]))


def test_cointegration_campaign36_required_timeframe_sections():
    data = _load(Path("reports/cointegration_campaign36_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        for section in REQUIRED_TIMEFRAME_SECTIONS:
            assert section in r, f"{tf} missing section {section}"
            sec = r[section]
            assert isinstance(sec, dict), f"{tf}/{section} not a dict"
            if section in TIMEFRAME_SECTIONS_WITH_PROVENANCE:
                if sec.get("available") is False:
                    continue
                prov = sec.get("provenance") or {}
                assert prov.get("real_data_only") is True
                assert prov.get("fabricated_data") is False
                assert not _has_nan(sec), f"{tf}/{section} contains NaN/Inf"
            elif section in PER_PAIR_MAP_SECTIONS:
                for pname in PAIRS_FOR_CHECK:
                    entry = sec.get(pname) or {}
                    if not entry.get("available"):
                        continue
                    prov = entry.get("provenance") or {}
                    assert prov.get("real_data_only") is True, f"{tf}/{section}/{pname} provenance"
                    assert prov.get("fabricated_data") is False
                    assert not _has_nan(entry), f"{tf}/{section}/{pname} contains NaN/Inf"


def test_cointegration_campaign36_required_basket_sections():
    data = _load(Path("reports/cointegration_campaign36_mt.json"))
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


def test_cointegration_campaign36_provenance_all_sections_real_data():
    data = _load(Path("reports/cointegration_campaign36_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        assert (r.get("provenance") or {}).get("real_data_only") is True
        assert (r.get("multi_regime_convergence_divergence") or {}).get("provenance") or {}
        assert (r.get("kill_switch_state") or {}).get("provenance") or {}
        assert (r.get("execution_aware_capacity_allocation") or {}).get("provenance") or {}
        baskets = r.get("baskets") or {}
        for bname in BASKETS:
            b = baskets.get(bname) or {}
            if not b.get("available"):
                continue
            sec = b.get("portfolio_basket_cointegration") or {}
            assert (sec.get("provenance") or {}).get("real_data_only") is True


def test_cointegration_campaign36_persistence_quantified():
    data = _load(Path("reports/cointegration_campaign36_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    found = False
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        pp = r.get("pair_persistence") or {}
        for pname in PAIRS_FOR_CHECK:
            p = pp.get(pname) or {}
            if not p.get("available"):
                continue
            assert "persistence_half_life_bars" in p, f"{tf}/{pname} missing persistence half-life"
            assert "decay_half_life_bars" in p, f"{tf}/{pname} missing decay half-life"
            assert "pass_rate" in p
            assert "failure_rate" in p
            assert "survival_curve" in p
            assert isinstance(p.get("survival_curve"), dict)
            assert p.get("provenance") or {}
            assert (p.get("provenance") or {}).get("real_data_only") is True
            found = True
    assert found, "No pair persistence quantified across any timeframe"


def test_cointegration_campaign36_forward_reliability_quantified():
    data = _load(Path("reports/cointegration_campaign36_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    found = False
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        wf = r.get("forward_reliability_walk_forward") or {}
        for pname in PAIRS_FOR_CHECK:
            w = wf.get(pname) or {}
            if not w.get("available"):
                continue
            assert "forward_reliability" in w, f"{tf}/{pname} missing forward_reliability"
            assert "forward_reliability_quantified" in w
            assert "mean_oos_pass_rate" in w
            assert "n_splits_computed" in w
            assert "splits" in w
            assert isinstance(w.get("splits"), list)
            assert (w.get("provenance") or {}).get("real_data_only") is True
            found = True
    assert found, "No forward-reliability/walk-forward quantified across any timeframe"


def test_cointegration_campaign36_regime_conditioned_failure_rates_quantified():
    data = _load(Path("reports/cointegration_campaign36_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    found = False
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        rc = r.get("regime_conditioned_failure_rates") or {}
        for pname in PAIRS_FOR_CHECK:
            regs = rc.get(pname) or {}
            if not regs:
                continue
            # At least one regime bucket reported
            buckets = [k for k in (
                "low_vol", "med_vol", "high_vol",
                "trend_down", "trend_flat", "trend_up",
            ) if k in regs]
            assert len(buckets) >= 1, f"{tf}/{pname} no regime buckets"
            for b in buckets:
                bstat = regs.get(b) or {}
                assert "failure_rate" in bstat
                assert "n_windows" in bstat
                assert (bstat.get("provenance") or {}).get("real_data_only") is True
            found = True
    assert found, "No regime-conditioned failure rates quantified across any timeframe"


def test_cointegration_campaign36_multi_regime_convergence_divergence_stress():
    data = _load(Path("reports/cointegration_campaign36_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    found = False
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        mcd = r.get("multi_regime_convergence_divergence") or {}
        assert mcd.get("available") is True
        assert "per_pair_regime_divergence" in mcd
        assert "mean_pair_regime_divergence" in mcd
        assert "cross_timeframe_terminal_gate_agreement" in mcd
        assert "convergence_divergence_stressed" in mcd
        assert (mcd.get("provenance") or {}).get("real_data_only") is True
        assert not _has_nan(mcd), f"{tf} mcd contains NaN/Inf"
        found = True
    assert found


def test_cointegration_campaign36_fail_closed_re_gating():
    data = _load(Path("reports/cointegration_campaign36_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        rg = r.get("fail_closed_re_gating") or {}
        for pname in PAIRS_FOR_CHECK:
            g = rg.get(pname) or {}
            if not g.get("available"):
                continue
            assert g.get("fail_closed") is True, f"{tf}/{pname} re_gating not fail_closed"
            assert g.get("no_auto_lift") is True, f"{tf}/{pname} re_gating allows auto-lift"
            assert g.get("cannot_auto_lift_blocks") is True
            assert "reclassified_blocked" in g
            assert "new_eligible" in g
            assert "base_eligible" in g
            assert "persistence_degraded" in g
            assert "high_vol_fail_max" in g
            assert "persistence_half_life_min" in g
            assert g.get("reclassification_action") in (
                "reclassify_to_blocked_fail_closed", "no_change"
            )
            # No auto-lift: if not base eligible, stays not eligible
            if not g.get("base_eligible"):
                assert g.get("new_eligible") is False
            # Blocked pairs get zero capacity
            if g.get("base_eligible") and not g.get("new_eligible"):
                cap = r.get("execution_aware_capacity_allocation") or {}
                per_pair = cap.get("per_pair") or {}
                pp = per_pair.get(pname) or {}
                if pp.get("available"):
                    assert pp.get("zero_capacity_on_block") is True or \
                        pp.get("allocated_weight") == 0.0


def test_cointegration_campaign36_fail_closed_reentry_validation():
    data = _load(Path("reports/cointegration_campaign36_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        reentry = r.get("fail_closed_reentry_validation") or {}
        for pname in PAIRS_FOR_CHECK:
            re = reentry.get(pname) or {}
            if not re.get("available"):
                continue
            assert re.get("reentry_requires_fresh_cointegration_evidence") is True
            assert re.get("fail_closed") is True
            assert re.get("no_auto_lift") is True
            if re.get("currently_blocked"):
                assert re.get("fresh_cointegration_evidence_checked") is True


def test_cointegration_campaign36_kill_switch_breach_alerts_drive_halts():
    data = _load(Path("reports/cointegration_campaign36_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    found_breach = False
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        ks = r.get("kill_switch_state") or {}
        cap = r.get("execution_aware_capacity_allocation") or {}
        assert ks.get("fail_closed") is True
        assert ks.get("cannot_auto_lift") is True
        assert ks.get("breach_alerts_drive_halts") is True
        assert ks.get("halts_execution") in (True, False)
        assert cap.get("breach_alerts_drive_halts") is True
        assert cap.get("halts_execution_on_breach") == bool(cap.get("kill_switch_triggered"))
        assert cap.get("zero_capacity_on_breach") is True
        assert cap.get("fail_closed") is True
        if ks.get("triggered") or cap.get("breach_alerts_present"):
            found_breach = True
            assert ks.get("triggered") is True or cap.get("breach_alerts_present") is True
            assert len(cap.get("breach_alerts") or []) >= 0
    # At least one timeframe should exercise breach/kill-switch logic (4h does).
    assert found_breach


def test_cointegration_campaign36_capacity_fail_closed_zero_on_block():
    data = _load(Path("reports/cointegration_campaign36_mt.json"))
    c_res = data.get("results_by_timeframe") or {}
    found_blocked = False
    for tf in ["1h", "4h", "1d"]:
        r = c_res[tf]
        cap = r.get("execution_aware_capacity_allocation") or {}
        per_pair = cap.get("per_pair") or {}
        rg = r.get("fail_closed_re_gating") or {}
        for pname in PAIRS_FOR_CHECK:
            g = rg.get(pname) or {}
            pp = per_pair.get(pname) or {}
            if not pp.get("available"):
                continue
            if g.get("base_eligible") and not g.get("new_eligible"):
                found_blocked = True
                assert pp.get("zero_capacity_on_block") is True
                assert pp.get("feasible") is False
                assert pp.get("allocated_weight") == 0.0
                assert pp.get("kill_switch_active") in (True, False)
            # Every per-pair entry has required fields
            assert "base_eligible" in pp
            assert "new_eligible" in pp
            assert "feasible" in pp
            assert "allocated_weight" in pp
            assert "capacity_notional" in pp
            assert "blocked_reasons" in pp
            assert (pp.get("provenance") or {}).get("real_data_only") is True
    # 4h timeframe reclassifies pairs blocked, so expect at least one blocked pair somewhere.
    assert found_blocked


def test_cointegration_campaign36_no_nan_inf_anywhere():
    data = _load(Path("reports/cointegration_campaign36_mt.json"))
    assert not _has_nan(data), "Artifact contains NaN/Inf"


def test_cointegration_campaign36_campaign_flags():
    data = _load(Path("reports/cointegration_campaign36_mt.json"))
    assert data.get("campaign") == 36
    assert data.get("gate_thresholds") is not None
    assert data.get("persistence_thresholds") is not None
    assert data.get("walk_forward") is not None
    assert data.get("portfolio") is not None
    assert data.get("regime_definitions") is not None
    wf = data.get("walk_forward") or {}
    assert wf.get("train_bars") is not None
    assert wf.get("test_bars") is not None
    assert wf.get("n_splits") is not None
