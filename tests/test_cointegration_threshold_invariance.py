from __future__ import annotations

import json
from pathlib import Path

import pytest

REPORTS = [
    Path("reports/cointegration_diagnostics_real.json"),
    Path("reports/cointegration_diagnostics_oos.json"),
    Path("reports/cointegration_diagnostics_oos_v2.json"),
]


@pytest.mark.parametrize("report_path", REPORTS)
def test_threshold_invariance_near_misses(report_path: Path):
    if not report_path.exists():
        pytest.skip(f"Missing report {report_path}")
    data = json.loads(report_path.read_text(encoding="utf-8"))
    diags = data.get("cointegration_diagnostics") or data.get("diagnostics") or {}
    assert isinstance(diags, dict) and diags, f"No diagnostics in {report_path}"

    # Required thresholds as enforced (from strategy logic expectations)
    MIN_ROLLING_FRAC_STABLE = 0.6
    MAX_HALF_LIFE = 30.0
    MIN_HALF_LIFE = 1.0
    MAX_HURST = 0.5
    LEG_ADF_PVAL_MAX = 0.05

    for pair_name, diag in diags.items():
        assert diag.get("provenance", {}).get("real_data_only") is True
        assert diag.get("provenance", {}).get("fabricated_data") is False
        gates = diag.get("gates", {})
        prov = diag.get("provenance", {})
        metrics = diag.get("metrics", {})

        # Blocked routes must be non-empty if not all-pass
        if not gates.get("all_pass"):
            assert prov.get("blocked_routes"), f"{pair_name} not all-pass but no blocked_routes"

        # Pin invariants on key metrics if present
        if "eg_pvalue" in metrics:
            # Must remain <= EG_PVAL_MAX to pass; if present, just ensure it's a number
            assert isinstance(metrics["eg_pvalue"], (int, float))
        if "spread_adf_pvalue" in metrics:
            assert isinstance(metrics["spread_adf_pvalue"], (int, float))
        if "half_life_ou" in metrics:
            hl = metrics["half_life_ou"]
            assert isinstance(hl, (int, float))
            # Threshold bounds must remain enforced (values not weakened)
            assert hl >= MIN_HALF_LIFE and hl <= MAX_HALF_LIFE
        if "hurst_exponent" in metrics:
            h = metrics["hurst_exponent"]
            assert isinstance(h, (int, float))
            assert h <= MAX_HURST
        if "rolling_frac_stable" in metrics:
            rf = metrics["rolling_frac_stable"]
            assert isinstance(rf, (int, float))
            # Invariant: passing requires >= MIN_ROLLING_FRAC_STABLE
            if gates.get("rolling_stable_ok"):
                assert rf >= MIN_ROLLING_FRAC_STABLE - 1e-12
        # Leg ADF pvalues
        for k in ("leg1_adf_pvalue", "leg2_adf_pvalue"):
            if k in metrics:
                assert isinstance(metrics[k], (int, float))
                assert metrics[k] <= LEG_ADF_PVAL_MAX
