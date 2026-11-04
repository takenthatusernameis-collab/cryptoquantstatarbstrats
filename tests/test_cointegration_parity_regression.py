"""Codified parity regression tests using shared helper."""

from __future__ import annotations

import numpy as np
import pandas as pd

from tests.cointegration_parity import assert_cached_vs_perbar_gate_parity_strict


def make_data(n: int = 250) -> pd.DataFrame:
    idx = pd.date_range("2024-01-01", periods=n, freq="h", tz="UTC")
    np.random.seed(123)
    eth = 2000 + np.cumsum(np.random.randn(n) * 1.0)
    btc = 30000 + 15.0 * (eth - 2000) + np.cumsum(np.random.randn(n) * 5.0)
    return pd.DataFrame({"BTC": btc, "ETH": eth}, index=idx)


def test_parity_structural_break_flagged_shared_helper():
    df = make_data()
    ed = {
        "gates": {
            "eg_pass": True,
            "johansen_pass": True,
            "spread_mr_pass": True,
            "hl_bounds_pass": True,
            "rolling_stable_ok": True,
            "leg_stationarity_ok": True,
            "no_structural_break": False,
            "all_pass": False,
        },
        "structural_breaks": {"flagged": True},
    }
    assert_cached_vs_perbar_gate_parity_strict(df, cached_diag=ed)


def test_parity_missing_structural_breaks_strict_shared_helper():
    df = make_data()
    ed = {
        "gates": {
            "eg_pass": True,
            "johansen_pass": True,
            "spread_mr_pass": True,
            "hl_bounds_pass": True,
            "rolling_stable_ok": True,
            "leg_stationarity_ok": True,
            "no_structural_break": True,
            "all_pass": True,
        },
        "structural_breaks": None,
    }
    assert_cached_vs_perbar_gate_parity_strict(df, cached_diag=ed)


def test_parity_gates_none_strict_shared_helper():
    df = make_data()
    ed = {
        "gates": None,
        "structural_breaks": {"flagged": False},
    }
    sig_cached, sig_perbar = assert_cached_vs_perbar_gate_parity_strict(df, cached_diag=ed)
    assert (sig_cached["enriched_gates_ok"] == 0.0).all()
    assert (sig_perbar["enriched_gates_ok"] == 0.0).all()


def test_parity_structural_break_flagged_none_strict_shared_helper():
    df = make_data()
    ed = {
        "gates": {
            "eg_pass": True,
            "johansen_pass": True,
            "spread_mr_pass": True,
            "hl_bounds_pass": True,
            "rolling_stable_ok": True,
            "leg_stationarity_ok": True,
            "no_structural_break": None,
        },
        "structural_breaks": {"flagged": None},
    }
    sig_cached, sig_perbar = assert_cached_vs_perbar_gate_parity_strict(df, cached_diag=ed)
    assert (sig_cached["enriched_gates_ok"] == 0.0).all()
    assert (sig_perbar["enriched_gates_ok"] == 0.0).all()
    assert not sig_cached["long"].any() and not sig_cached["short"].any()
    assert not sig_perbar["long"].any() and not sig_perbar["short"].any()


def test_parity_cost_grid_missing_in_strict_shared_helper():
    df = make_data()
    ed = {
        "gates": {
            "eg_pass": True,
            "johansen_pass": True,
            "spread_mr_pass": True,
            "hl_bounds_pass": True,
            "rolling_stable_ok": True,
            "leg_stationarity_ok": True,
            "no_structural_break": True,
            "all_pass": True,
        },
        "structural_breaks": {"flagged": False},
        "cost_stress": {},
        # cost_grid missing
    }
    # Should still be fine as long as gates are ok; parity must hold
    sig_cached, sig_perbar = assert_cached_vs_perbar_gate_parity_strict(df, cached_diag=ed)
    assert (sig_cached["enriched_gates_ok"] == 1.0).all()
    assert (sig_perbar["enriched_gates_ok"] == 1.0).all()


def test_parity_blocked_schema_preserved_shared_helper():
    df = make_data()
    ed = {
        "gates": {
            "eg_pass": False,
            "johansen_pass": True,
            "spread_mr_pass": True,
            "hl_bounds_pass": True,
            "rolling_stable_ok": True,
            "leg_stationarity_ok": True,
            "no_structural_break": True,
        },
        "structural_breaks": {"flagged": False},
        "blocked_routes": ["eg_fail"],
        "blocked_schema": {"code": "EG_FAIL"},
        "provenance": {"real_data_only": True, "fabricated_data": False},
    }
    fake = {
        "gates": dict(ed["gates"]),
        "structural_breaks": dict(ed["structural_breaks"]),
        "blocked_routes": list(ed["blocked_routes"]),
        "blocked_schema": dict(ed["blocked_schema"]),
        "provenance": dict(ed["provenance"]),
    }
    sig_cached, sig_perbar = assert_cached_vs_perbar_gate_parity_strict(
        df, cached_diag=ed, fake_target_diag=fake, check_provenance=True
    )
    assert (sig_cached["enriched_gates_ok"] == 0.0).all()
    assert (sig_perbar["enriched_gates_ok"] == 0.0).all()
    assert not sig_cached["long"].any() and not sig_cached["short"].any()
    assert not sig_perbar["long"].any() and not sig_perbar["short"].any()
