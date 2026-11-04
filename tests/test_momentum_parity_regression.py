from __future__ import annotations

import numpy as np
import pandas as pd

from strategies.momentum import MomentumStrategy


def _make_df(n: int = 200) -> pd.DataFrame:
    rng = np.random.default_rng(123)
    price = 100 + np.cumsum(rng.normal(0, 1, n))
    return pd.DataFrame({"BTC": price})


def test_momentum_cached_vs_perbar_parity() -> None:
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
    strat_cached = MomentumStrategy(asset="BTC", n=10, m=20, enriched_diagnostics=ed)
    strat_perbar = MomentumStrategy(asset="BTC", n=10, m=20, enriched_diagnostics=None)
    import strategies.momentum as mom

    def _fake_target(p1, p2, pair_name=""):
        return {"gates": ed["gates"], "structural_breaks": ed["structural_breaks"], "provenance": {"fabricated_data": True}}

    orig = getattr(mom, "target_schema_diagnostics", None)
    try:
        mom.target_schema_diagnostics = _fake_target  # type: ignore
        sig_c = strat_cached.generate_signals(df)
        sig_p = strat_perbar.generate_signals(df)
    finally:
        if orig is not None:
            mom.target_schema_diagnostics = orig
    pd.testing.assert_series_equal(sig_c["enriched_gates_ok"], sig_p["enriched_gates_ok"])
    pd.testing.assert_series_equal(sig_c["long"], sig_p["long"])
    pd.testing.assert_series_equal(sig_c["short"], sig_p["short"])


def test_momentum_blocks_flagged_break() -> None:
    df = _make_df()
    ed = {
        "gates": {"eg_pass": True, "johansen_pass": True, "spread_mr_pass": True, "hl_bounds_pass": True,
                 "rolling_stable_ok": True, "leg_stationarity_ok": True, "no_structural_break": False, "all_pass": False},
        "structural_breaks": {"flagged": True},
    }
    strat = MomentumStrategy(asset="BTC", n=10, m=20, enriched_diagnostics=ed)
    sig = strat.generate_signals(df)
    assert (sig["long"] == False).all()
    assert (sig["short"] == False).all()
