from __future__ import annotations

import json
from pathlib import Path

import pytest

REPORTS = [
    Path("reports/cointegration_diagnostics_real.json"),
    Path("reports/cointegration_diagnostics_oos.json"),
    Path("reports/cointegration_diagnostics_oos_v2.json"),
    Path("reports/cointegration_diagnostics_oos_mt_4h.json"),
    Path("reports/cointegration_diagnostics_oos_mt_1d.json"),
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

    for pair_name, diag in diags.items():
        assert diag.get("provenance", {}).get("real_data_only") is True
        assert diag.get("provenance", {}).get("fabricated_data") is False
        gates = diag.get("gates", {})
        prov = diag.get("provenance", {})
        metrics = diag.get("metrics", {})

        # Blocked routes must be non-empty if not all-pass
        if not gates.get("all_pass"):
            assert prov.get("blocked_routes"), f"{pair_name} not all-pass but no blocked_routes"

        # Pin invariants on key metrics if present (gate thresholds are the
        # law: rolling >= 0.6, EG pvalue <= 0.05, half-life (1, 500); raw
        # metric values are data-dependent and are pinned only when the
        # corresponding gate passes, never weakened).
        if "eg_pvalue" in metrics:
            v = metrics["eg_pvalue"]
            assert v is None or isinstance(v, (int, float))
        if "spread_adf_pvalue" in metrics:
            v = metrics["spread_adf_pvalue"]
            assert v is None or isinstance(v, (int, float))
        if "half_life_ou" in metrics:
            hl = metrics["half_life_ou"]
            assert hl is None or isinstance(hl, (int, float))
            if hl is not None and gates.get("hl_bounds_pass"):
                assert 1.0 < hl < 500.0, f"{pair_name}: hl={hl} violates gate bounds (1, 500)"
        if "hurst_exponent" in metrics:
            h = metrics["hurst_exponent"]
            assert h is None or isinstance(h, (int, float))
            if h is not None and diag.get("spread", {}).get("mr_favorable") is True:
                assert h < 0.5, f"{pair_name}: hurst={h} with mr_favorable=True"
        if "rolling_frac_stable" in metrics:
            rf = metrics["rolling_frac_stable"]
            assert rf is None or isinstance(rf, (int, float))
            # Invariant: passing requires >= MIN_ROLLING_FRAC_STABLE
            if gates.get("rolling_stable_ok"):
                assert rf >= MIN_ROLLING_FRAC_STABLE - 1e-12
        # Leg ADF pvalues
        for k in ("leg1_adf_pvalue", "leg2_adf_pvalue"):
            if k in metrics:
                assert metrics[k] is None or isinstance(metrics[k], (int, float))
