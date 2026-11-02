"""Campaign 30 tests - cointegration rigor phase 2.

Johansen rank stability, structural-break discipline, half-life
mean-reversion favorability bands, walk-forward out-of-sample pairs
execution robustness (real data only). Preserves gating invariants
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

EXPECTED_INVARIANTS = {
    "1h": [],
    "4h": ["POL/BTC"],
    "1d": [],
}

REQUIRED_SECTIONS = [
    "johansen_rank_stability",
    "structural_break_discipline",
    "half_life_favorability_bands",
    "walk_forward_oos_pairs_robustness",
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


def test_cointegration_campaign30_artifact_exists_and_schema():
    p = Path("reports/cointegration_campaign30_mt.json")
    assert p.exists(), "Missing reports/cointegration_campaign30_mt.json"
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
    assert data.get("type") == "cointegration_campaign30_mt"
    assert data.get("campaign") == 30
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


def test_cointegration_campaign30_preserves_gating_invariants():
    p = Path("reports/cointegration_campaign30_mt.json")
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


def test_cointegration_campaign30_required_sections_present():
    p = Path("reports/cointegration_campaign30_mt.json")
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
            assert pr.get("provenance") or isinstance(pr.get("provenance"), dict)
            pair_prov = pr.get("provenance") or {}
            assert pair_prov.get("real_data_only") is True
            assert pair_prov.get("fabricated_data") is False


def test_cointegration_campaign30_fail_closed_gating():
    p = Path("reports/cointegration_campaign30_mt.json")
    if not p.exists():
        pytest.skip("Missing artifact")
    data = json.loads(p.read_text(encoding="utf-8"))
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        for pname, pr in (c_res[tf].get("pairs") or {}).items():
            wf = pr.get("walk_forward_oos_pairs_robustness") or {}
            assert wf.get("fail_closed_gating") is True
            # Fail-closed: OOS robustness requires gating eligibility.
            if wf.get("robustness_pass") is True:
                assert pr.get("eligible_by_gating") is True, (
                    f"{tf}/{pname} OOS-robust despite gating block"
                )
            # Only gated-eligible pairs may be feasible/robust.
            assert wf.get("oos_robust") == (
                wf.get("robustness_pass") is True and pr.get("eligible_by_gating") is True
            )
            assert pr.get("hard_blocked") == (not pr.get("eligible_by_gating"))


def test_cointegration_campaign30_johansen_rank_stability_schema():
    p = Path("reports/cointegration_campaign30_mt.json")
    if not p.exists():
        pytest.skip("Missing artifact")
    data = json.loads(p.read_text(encoding="utf-8"))
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        for pname, pr in (c_res[tf].get("pairs") or {}).items():
            j = pr.get("johansen_rank_stability") or {}
            if j.get("available") is True:
                assert isinstance(j.get("n_windows"), int)
                assert j.get("n_windows") >= 1
                assert isinstance(j.get("modal_rank_trace"), int)
                assert isinstance(j.get("modal_rank_maxeig"), int)
                assert 0.0 <= j.get("frac_windows_modal_rank_trace", 0.0) <= 1.0
                assert 0.0 <= j.get("frac_windows_rank_ge_1_trace", 0.0) <= 1.0
                assert isinstance(j.get("rank_trace_stable"), bool)
                assert isinstance(j.get("rank_maxeig_stable"), bool)


def test_cointegration_campaign30_structural_break_discipline_schema():
    p = Path("reports/cointegration_campaign30_mt.json")
    if not p.exists():
        pytest.skip("Missing artifact")
    data = json.loads(p.read_text(encoding="utf-8"))
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        for pname, pr in (c_res[tf].get("pairs") or {}).items():
            sb = pr.get("structural_break_discipline") or {}
            assert isinstance(sb.get("half_sample_has_break"), bool)
            assert isinstance(sb.get("no_hidden_regime_shift"), bool)
            assert isinstance(sb.get("discipline_pass"), bool)
            assert isinstance(sb.get("break_dates"), list)
            assert isinstance(sb.get("n_breaks_detected"), int)


def test_cointegration_campaign30_half_life_favorability_bands_schema():
    p = Path("reports/cointegration_campaign30_mt.json")
    if not p.exists():
        pytest.skip("Missing artifact")
    data = json.loads(p.read_text(encoding="utf-8"))
    c_res = data.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        for pname, pr in (c_res[tf].get("pairs") or {}).items():
            hl = pr.get("half_life_favorability_bands") or {}
            if hl.get("available") is True:
                assert hl.get("band_low") == 1.0
                assert hl.get("band_high") == 500.0
                assert 0.0 <= hl.get("frac_windows_hl_in_bands", 0.0) <= 1.0
                assert 0.0 <= hl.get("frac_windows_mean_reversion_favorable", 0.0) <= 1.0
                assert isinstance(hl.get("favorability_band_pass"), bool)
