"""Cached vs per-bar parity regression for mean reversion strategy."""
from __future__ import annotations

import numpy as np
import pandas as pd

from strategies.mean_reversion import MeanReversionStrategy
from tests.cointegration_parity import assert_cached_vs_perbar_gate_parity_strict


def _make_df(n: int = 200) -> pd.DataFrame:
    rng = np.random.default_rng(123)
    price = 100 + np.cumsum(rng.normal(0, 1, n))
    return pd.DataFrame({"BTC": price})


def test_mean_reversion_cached_vs_perbar_gates_pass() -> None:
    df = _make_df()
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
    }
    strat_cached = MeanReversionStrategy(asset="BTC", lookback=30, enriched_diagnostics=ed)
    strat_perbar = MeanReversionStrategy(asset="BTC", lookback=30, enriched_diagnostics=None)
    import strategies.mean_reversion as mr

    def _fake_target(p1, p2, pair_name=""):
        return {"gates": ed["gates"], "structural_breaks": ed["structural_breaks"], "provenance": {"fabricated_data": True}}

    orig = getattr(mr, "target_schema_diagnostics", None)
    try:
        mr.target_schema_diagnostics = _fake_target  # type: ignore
        sig_c = strat_cached.generate_signals(df)
        sig_p = strat_perbar.generate_signals(df)
    finally:
        if orig is not None:
            mr.target_schema_diagnostics = orig
    pd.testing.assert_series_equal(sig_c["enriched_gates_ok"], sig_p["enriched_gates_ok"])
    pd.testing.assert_series_equal(sig_c["long"], sig_p["long"])
    pd.testing.assert_series_equal(sig_c["short"], sig_p["short"])


def test_mean_reversion_blocks_on_structural_break_flagged() -> None:
    df = _make_df()
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
    strat = MeanReversionStrategy(asset="BTC", lookback=30, enriched_diagnostics=ed, strict_enriched_gates=True)
    sig = strat.generate_signals(df)
    assert (sig["long"] == False).all()
    assert (sig["short"] == False).all()


def test_mean_reversion_blocks_missing_gates_strict() -> None:
    df = _make_df()
    ed = {"gates": {}, "structural_breaks": {"flagged": False}}
    strat = MeanReversionStrategy(asset="BTC", lookback=30, enriched_diagnostics=ed, strict_enriched_gates=True)
    sig = strat.generate_signals(df)
    assert (sig["enriched_gates_ok"] == 0.0).all()
