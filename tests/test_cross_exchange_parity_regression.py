from __future__ import annotations

import numpy as np
import pandas as pd

from strategies.cross_exchange import CrossExchangeArb


def _make_df(n: int = 200) -> pd.DataFrame:
    rng = np.random.default_rng(123)
    base = 100 + np.cumsum(rng.normal(0, 0.1, n))
    a = base + rng.normal(0, 0.001, n)
    b = base
    return pd.DataFrame({"EXA": a, "EXB": b})


def test_cross_exchange_cached_vs_perbar_parity() -> None:
    df = _make_df()
    ed = {
        "gates": {"eg_pass": True, "johansen_pass": True, "spread_mr_pass": True, "hl_bounds_pass": True,
                 "rolling_stable_ok": True, "leg_stationarity_ok": True, "no_structural_break": True, "all_pass": True},
        "structural_breaks": {"flagged": False},
    }
    strat_cached = CrossExchangeArb(exchange_a="EXA", exchange_b="EXB", enriched_diagnostics=ed)
    strat_perbar = CrossExchangeArb(exchange_a="EXA", exchange_b="EXB", enriched_diagnostics=None)
    import strategies.cross_exchange as ce

    def _fake_target(p1, p2, pair_name=""):
        return {"gates": ed["gates"], "structural_breaks": ed["structural_breaks"], "provenance": {"fabricated_data": True}}

    orig = getattr(ce, "target_schema_diagnostics", None)
    try:
        ce.target_schema_diagnostics = _fake_target  # type: ignore
        sig_c = strat_cached.generate_signals(df)
        sig_p = strat_perbar.generate_signals(df)
    finally:
        if orig is not None:
            ce.target_schema_diagnostics = orig
    pd.testing.assert_series_equal(sig_c["enriched_gates_ok"], sig_p["enriched_gates_ok"])
    pd.testing.assert_series_equal(sig_c["EXA"], sig_p["EXA"])
    pd.testing.assert_series_equal(sig_c["EXB"], sig_p["EXB"])


def test_cross_exchange_blocks_flagged() -> None:
    df = _make_df()
    ed = {"gates": {"eg_pass": True, "johansen_pass": True, "spread_mr_pass": True, "hl_bounds_pass": True,
                    "rolling_stable_ok": True, "leg_stationarity_ok": True, "no_structural_break": False, "all_pass": False},
          "structural_breaks": {"flagged": True}}
    strat = CrossExchangeArb(exchange_a="EXA", exchange_b="EXB", enriched_diagnostics=ed)
    sig = strat.generate_signals(df)
    assert (sig["EXA"] == 0.0).all()
    assert (sig["EXB"] == 0.0).all()
