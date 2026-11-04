from __future__ import annotations

import numpy as np
import pandas as pd

from strategies.term_structure import TermStructureStrategy


def _make_df(n: int = 200) -> pd.DataFrame:
    rng = np.random.default_rng(123)
    iv30 = 0.5 + np.cumsum(rng.normal(0, 0.01, n))
    iv90 = iv30 + 0.05 + rng.normal(0, 0.01, n)
    return pd.DataFrame({"iv_30d": iv30, "iv_90d": iv90})


def test_term_structure_cached_vs_perbar_parity() -> None:
    df = _make_df()
    ed = {
        "gates": {"eg_pass": True, "johansen_pass": True, "spread_mr_pass": True, "hl_bounds_pass": True,
                 "rolling_stable_ok": True, "leg_stationarity_ok": True, "no_structural_break": True, "all_pass": True},
        "structural_breaks": {"flagged": False},
    }
    strat_cached = TermStructureStrategy(asset="BTC", near_tenor="iv_30d", far_tenor="iv_90d", lookback=30, enriched_diagnostics=ed)
    strat_perbar = TermStructureStrategy(asset="BTC", near_tenor="iv_30d", far_tenor="iv_90d", lookback=30, enriched_diagnostics=None)
    import strategies.term_structure as ts

    def _fake_target(p1, p2, pair_name=""):
        return {"gates": ed["gates"], "structural_breaks": ed["structural_breaks"], "provenance": {"fabricated_data": True}}

    orig = getattr(ts, "target_schema_diagnostics", None)
    try:
        ts.target_schema_diagnostics = _fake_target  # type: ignore
        sig_c = strat_cached.generate_signals(df)
        sig_p = strat_perbar.generate_signals(df)
    finally:
        if orig is not None:
            ts.target_schema_diagnostics = orig
    pd.testing.assert_series_equal(sig_c["enriched_gates_ok"], sig_p["enriched_gates_ok"])
    pd.testing.assert_series_equal(sig_c["long_spread"], sig_p["long_spread"])
    pd.testing.assert_series_equal(sig_c["short_spread"], sig_p["short_spread"])


def test_term_structure_blocks_missing_gates() -> None:
    df = _make_df()
    ed = {"gates": {}, "structural_breaks": {"flagged": False}}
    strat = TermStructureStrategy(asset="BTC", near_tenor="iv_30d", far_tenor="iv_90d", lookback=30, enriched_diagnostics=ed)
    sig = strat.generate_signals(df)
    assert (sig["enriched_gates_ok"] == 0.0).all()
    assert (sig["long_spread"] == False).all()
    assert (sig["short_spread"] == False).all()
