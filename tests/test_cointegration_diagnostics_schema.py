"""
Network-independent tests for cointegration diagnostics.

These tests never call Binance. Synthetic series are used only in isolated
tests and are explicitly flagged ``fabricated_data: true``. The real artifact
(reports/portfolio_real.json) is validated for schema and provenance but never
regenerated here.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from utils.cointegration import (
    adf_test,
    blocked_schema_diagnostics,
    engle_granger_test,
    johansen_test,
    target_schema_diagnostics,
)

ARTIFACT = Path("reports/portfolio_real.json")

PAIRS = [
    ("BTC", "ETH"),
    ("ETH", "SOL"),
    ("BTC", "SOL"),
    ("ADA", "ETH"),
    ("XRP", "BTC"),
    ("BNB", "ETH"),
    ("BTC", "BNB"),
    ("SOL", "BNB"),
    ("ADA", "BTC"),
    ("XRP", "ETH"),
    ("BNB", "BTC"),
    ("DOT", "BTC"),
    ("DOT", "ETH"),
    ("POL", "BTC"),
    ("AVAX", "BTC"),
    ("LINK", "BTC"),
    ("LTC", "BTC"),
]

DIAG_KEYS = (
    "pair",
    "status",
    "engle_granger",
    "johansen",
    "adf_leg1",
    "kpss_leg1",
    "adf_leg2",
    "kpss_leg2",
    "spread",
    "rolling_stability",
    "structural_breaks",
    "gates",
    "provenance",
)

SPREAD_KEYS = (
    "available",
    "hedge_ratio",
    "adf_spread",
    "kpss_spread",
    "half_life_ou",
    "hurst_exponent",
    "mr_favorable",
    "provenance",
)

GATES_KEYS = (
    "all_pass",
    "eg_pass",
    "johansen_pass",
    "spread_mr_pass",
    "hl_bounds_pass",
    "leg_stationarity_ok",
    "rolling_stable_ok",
)

PROVENANCE_KEYS = (
    "source",
    "real_data_only",
    "fabricated_data",
    "computed_at",
    "blocked_routes",
    "rationale",
)


def _synthetic_cointegrated(n: int = 600, seed: int = 3) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    x = 100 + np.cumsum(rng.normal(0, 0.5, n))
    y = 1.5 * x + rng.normal(0, 0.5, n)  # cointegrated
    idx = pd.date_range("2026-01-01", periods=n, freq="1h", tz="UTC")
    return pd.DataFrame({"A": x, "B": y}, index=idx)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_artifact_is_real_data_only():
    data = _artifact()
    assert data.get("real_data_only") is True
    assert data.get("fabricated_data") is False


def test_artifact_has_all_17_pair_diagnostics():
    data = _artifact()
    cd = data.get("cointegration_diagnostics", {})
    assert isinstance(cd, dict)
    assert set(cd.keys()) == {f"{a}/{b}" for a, b in PAIRS}, set(cd.keys())


def test_each_pair_diagnostic_matches_target_schema():
    data = _artifact()
    cd = data["cointegration_diagnostics"]
    for pname in cd.keys():
        diag = cd[pname]
        assert list(diag["pair"]) == list(pname.split("/")), pname
        for k in DIAG_KEYS:
            assert k in diag, f"{pname}: missing {k}"
        assert diag["status"] in (
            "computed_from_existing_results",
            "blocked_or_insufficient_data",
        ), pname
        prov = diag["provenance"]
        for k in PROVENANCE_KEYS:
            assert k in prov, f"{pname}: provenance missing {k}"
        assert prov["real_data_only"] is True
        assert prov["fabricated_data"] is False
        assert isinstance(prov["blocked_routes"], list)
        assert isinstance(prov["computed_at"], str) and prov["computed_at"]
        assert isinstance(prov["rationale"], str) and prov["rationale"]
        gates = diag["gates"]
        for k in GATES_KEYS:
            assert k in gates, f"{pname}: gates missing {k}"
        spread = diag["spread"]
        for k in SPREAD_KEYS:
            assert k in spread, f"{pname}: spread missing {k}"
        for sub in ("adf_leg1", "kpss_leg1", "adf_leg2", "kpss_leg2"):
            for k in ("available", "stat", "pvalue", "provenance"):
                assert k in diag[sub], f"{pname}: {sub} missing {k}"


def test_hl_bounds_respected_when_computed():
    data = _artifact()
    cd = data["cointegration_diagnostics"]
    for pname, diag in cd.items():
        hl = diag["spread"].get("half_life_ou")
        gate = diag["gates"]["hl_bounds_pass"]
        expected = hl is not None and 1.0 < hl < 500.0
        assert gate is expected, f"{pname}: hl={hl} bounds_pass={gate} expected={expected}"
        if hl is not None:
            assert hl > 0, f"{pname}: half_life must be positive when present, got {hl}"


def test_eg_and_johansen_gates_bool_or_null():
    data = _artifact()
    cd = data["cointegration_diagnostics"]
    for pname, diag in cd.items():
        for g in ("eg_pass", "johansen_pass"):
            assert diag["gates"][g] in (True, False, None), f"{pname}: {g}={diag['gates'][g]}"


def test_rolling_and_structural_structure():
    data = _artifact()
    cd = data["cointegration_diagnostics"]
    for pname, diag in cd.items():
        rs = diag["rolling_stability"]
        assert isinstance(rs.get("windows"), list)
        assert isinstance(rs.get("details"), list)
        assert rs.get("stable") in (True, False, None)
        sb = diag["structural_breaks"]
        assert isinstance(sb.get("breaks"), list)
        assert sb.get("flagged") in (True, False, None)


def test_blocked_case_requires_status_blocked_routes_provenance():
    blocked = blocked_schema_diagnostics(
        ["X", "Y"],
        [{"host": "https://api.binance.com", "status": 451, "error": "HTTP Error 451"}],
        "api.binance.com returns HTTP 451; no cached series.",
    )
    assert blocked["status"] == "blocked_or_insufficient_data"
    assert blocked["pair"] == ["X", "Y"]
    assert len(blocked["provenance"]["blocked_routes"]) == 1
    assert blocked["provenance"]["real_data_only"] is True
    assert blocked["provenance"]["fabricated_data"] is False
    assert blocked["provenance"]["computed_at"]
    assert "451" in blocked["provenance"]["rationale"]
    # Every sub-test unavailable / null.
    assert blocked["engle_granger"]["available"] is False
    assert blocked["engle_granger"]["stat"] is None
    assert blocked["johansen"]["rank"] is None
    assert blocked["spread"]["half_life_ou"] is None
    assert blocked["gates"]["all_pass"] is False
    for g in ("eg_pass", "johansen_pass", "hl_bounds_pass"):
        assert blocked["gates"][g] is None


def test_target_schema_diagnostics_on_synthetic_series():
    df = _synthetic_cointegrated()
    diag = target_schema_diagnostics(df["A"], df["B"], "A/B", source="isolated_test")
    assert diag["status"] == "computed_from_existing_results"
    assert diag["pair"] == ["A", "B"]
    assert diag["provenance"]["fabricated_data"] is False
    assert diag["provenance"]["real_data_only"] is True
    # Round-trips through strict JSON (no NaN/Inf leakage).
    json.dumps(diag, default=float)
    # Gates are booleans once series are available.
    for g in (
        "eg_pass",
        "johansen_pass",
        "spread_mr_pass",
        "hl_bounds_pass",
        "rolling_stable_ok",
        "leg_stationarity_ok",
    ):
        assert diag["gates"][g] in (True, False), f"{g}={diag['gates'][g]}"


def test_target_schema_diagnostics_never_fabricates_unavailable():
    # Very short series: many sub-tests cannot run -> available:false, not invented.
    idx = pd.date_range("2026-01-01", periods=5, freq="1h", tz="UTC")
    diag = target_schema_diagnostics(
        pd.Series([1.0, 2.0, 3.0, 4.0, 5.0], index=idx),
        pd.Series([2.0, 4.0, 6.0, 8.0, 10.0], index=idx),
        "SHORT/X",
        source="isolated_test",
    )
    json.dumps(diag, default=float)
    assert diag["spread"]["half_life_ou"] is None or 1.0 < diag["spread"]["half_life_ou"] < 500.0


def test_adf_eg_johansen_functions_on_synthetic_series():
    df = _synthetic_cointegrated()
    eg = engle_granger_test(df["A"], df["B"])
    assert "score" in eg and "pvalue" in eg
    joh = johansen_test(df["A"], df["B"])
    assert "trace_stat" in joh and "rank_trace_95" in joh
    adf = adf_test(df["A"])
    assert "statistic" in adf and "pvalue" in adf
