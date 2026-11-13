"""Tests for C296: Deribit options term-structure / skew data-blocked closure.

C296 probes the Deribit public API for a deep historical per-strike mark IV /
implied-volatility time series (term-structure / skew stat-arb). No such feed is
reachable: per-strike mark_iv is a current snapshot only
(get_book_summary_by_currency), DVOL is 30-day ATM only (C294 closed), and the
per-instrument tradingview / last-trades endpoints return price or trades with no
IV field. The family is therefore formally closed as data_blocked and the
reachable real-data cross-sectional stat-arb space is declared closed.

These tests assert the probe + closure artifact schema/evidence and that every
probed endpoint is recorded with `yields_deep_per_strike_iv_history: false`. They
never fabricate or proxy per-strike IV.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
TS = "20261113T224349Z"


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_report(name: str) -> dict:
    return json.loads((REPORTS / name).read_text())


def _probe_artifact() -> dict:
    name = f"campaign296_deribit_per_strike_iv_reachability_{TS}.json"
    path = REPORTS / name
    assert path.exists(), f"missing C296 probe artifact: {path}"
    data = _load_report(name)
    assert data.get("campaign") == 296
    assert data.get("part") == "deribit_per_strike_iv_reachability_probe"
    assert data.get("real_data_only") is True
    assert data.get("fabricated_data") is False
    assert data.get("source_host") == "https://www.deribit.com"
    assert int(data.get("n_probes", 0)) > 0
    assert int(data.get("n_instruments_probed", 0)) > 0
    conclusion = data.get("conclusion", {})
    assert conclusion.get("deep_historical_per_strike_mark_iv_reachable") is False
    assert conclusion.get("per_strike_iv_time_series_available") is False
    assert conclusion.get("per_strike_mark_iv_snapshot_only") is True
    assert conclusion.get("dvol_30d_atm_only_c294_closed") is True
    assert conclusion.get("any_probe_yields_iv_history") is False
    assert conclusion.get("options_term_structure_skew_family") == "data_blocked"
    assert conclusion.get("reachable_cross_sectional_stat_arb_space") == "closed"
    assert isinstance(conclusion.get("reason"), str) and len(conclusion["reason"]) > 0
    probes = data.get("probes", [])
    assert len(probes) == data.get("n_probes")
    for p in probes:
        assert isinstance(p.get("endpoint"), str) and p["endpoint"].startswith("/")
        assert isinstance(p.get("params"), str)
        assert p.get("yields_deep_per_strike_iv_history") is False
    return data


def _artifact(kind: str) -> dict:
    name = f"campaign296_{kind}_{TS}.json"
    path = REPORTS / name
    assert path.exists(), f"missing C296 {kind} artifact: {path}"
    data = _load_report(name)
    assert data.get("campaign") == 296
    assert data.get("part") == kind
    assert data.get("real_data_only") is True
    assert data.get("fabricated_data") is False
    assert data.get("verdict") == "DATA_BLOCKED"
    assert data.get("edge_proven") is False
    if "edge_claim" in data:
        assert data.get("edge_claim") == "NONE"
    assert data.get("family") == "options_term_structure_skew"
    assert data.get("family_verdict") == "data_blocked"
    assert data.get("reachable_cross_sectional_stat_arb_space") == "closed"
    assert isinstance(data.get("explanation"), str) and len(data["explanation"]) > 0
    # cross-references the probe artifact by filename + sha
    probe_name = f"campaign296_deribit_per_strike_iv_reachability_{TS}.json"
    assert data.get("probe_artifact") == probe_name
    assert data.get("probe_artifact_sha256") == _sha256_file(REPORTS / probe_name)
    return data


def test_probe_artifact_real_data_only_and_no_per_strike_iv_history() -> None:
    _probe_artifact()


def test_closure_artifacts_exist_data_blocked_and_cross_reference_probe() -> None:
    for kind in ("oos_sweep", "tradable_edge_registry", "summary", "verdict"):
        _artifact(kind)


def test_summary_and_verdict_cross_reference_each_other() -> None:
    summary = _artifact("summary")
    verdict = _artifact("verdict")
    oos_name = f"campaign296_oos_sweep_{TS}.json"
    reg_name = f"campaign296_tradable_edge_registry_{TS}.json"
    summ_name = f"campaign296_summary_{TS}.json"
    oos_sha = _sha256_file(REPORTS / oos_name)
    reg_sha = _sha256_file(REPORTS / reg_name)
    summ_sha = _sha256_file(REPORTS / summ_name)
    # summary references oos + registry with correct SHAs
    assert summary.get("oos_sweep") == oos_name
    assert summary.get("oos_sweep_sha256") == oos_sha
    assert summary.get("registry") == reg_name
    assert summary.get("registry_sha256") == reg_sha
    # verdict references oos + registry + summary with correct SHAs
    assert verdict.get("oos_sweep") == oos_name
    assert verdict.get("oos_sweep_sha256") == oos_sha
    assert verdict.get("registry") == reg_name
    assert verdict.get("registry_sha256") == reg_sha
    assert verdict.get("summary") == summ_name
    assert verdict.get("summary_sha256") == summ_sha
    assert verdict.get("edge_claim") == "NONE"
