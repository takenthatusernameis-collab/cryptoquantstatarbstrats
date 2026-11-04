"""Cross-strategy parity lock: every stat-arb strategy shares the same fail-closed
enriched-gate contract.

This is the single source of truth for the cross-strategy gate contract. It must
be satisfied by ``mean_reversion``, ``momentum``, ``term_structure``,
``volatility_surface``, ``cross_exchange`` and ``CointegrationPairsStrategy``:

* Defaults: ``use_enriched_gates=True`` and ``strict_enriched_gates=True``.
* Supplied ``enriched_diagnostics`` with missing/None gates blocks entries under
  strict mode (no ``or True`` / ``is None -> True`` coercion).
* Supplied ``structural_breaks.flagged is True`` blocks entries.
* Supplied ``structural_breaks`` is None/missing and strict blocks entries.
* Cached diagnostics vs per-bar diagnostics produce identical gate decisions
  (parity) via ``tests.cointegration_parity.assert_cached_vs_perbar_gate_parity_strict``
  where the shared helper applies, and an equivalent cached/per-bar comparison
  for the single-asset strategies.

No bespoke parity assertions outside these patterns.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from strategies.cross_exchange import CrossExchangeArb
from strategies.mean_reversion import MeanReversionStrategy
from strategies.momentum import MomentumStrategy
from strategies.term_structure import TermStructureStrategy
from strategies.volatility_surface import VolatilitySurfaceStrategy
from tests.cointegration_parity import assert_cached_vs_perbar_gate_parity_strict

GATE_KEYS = (
    "eg_pass",
    "johansen_pass",
    "spread_mr_pass",
    "hl_bounds_pass",
    "rolling_stable_ok",
    "leg_stationarity_ok",
    "no_structural_break",
    "all_pass",
)

ALL_PASS_DIAG = {
    "gates": {key: True for key in GATE_KEYS},
    "structural_breaks": {"flagged": False},
}

EMPTY_GATES_DIAG = {
    "gates": {},
    "structural_breaks": {"flagged": False},
}

FLAGGED_DIAG = {
    "gates": {key: True for key in GATE_KEYS},
    "structural_breaks": {"flagged": True},
}

SB_NONE_DIAG = {
    "gates": {key: True for key in GATE_KEYS},
    "structural_breaks": None,
}


def _ohlc_df(n: int = 200) -> pd.DataFrame:
    rng = np.random.default_rng(7)
    price = 100.0 + np.cumsum(rng.normal(0.0, 0.5, n))
    return pd.DataFrame({"BTC": price}, index=pd.date_range("2026-04-01", periods=n, freq="h"))


def _pairs_df(n: int = 200) -> pd.DataFrame:
    rng = np.random.default_rng(7)
    btc = 100.0 + np.cumsum(rng.normal(0.0, 0.5, n))
    eth = 3000.0 + np.cumsum(rng.normal(0.0, 15.0, n))
    idx = pd.date_range("2026-04-01", periods=n, freq="h")
    return pd.DataFrame({"BTC": btc, "ETH": eth}, index=idx)


def _ce_df(n: int = 200) -> pd.DataFrame:
    rng = np.random.default_rng(7)
    base = 100.0 + np.cumsum(rng.normal(0.0, 0.1, n))
    idx = pd.date_range("2026-04-01", periods=n, freq="h")
    return pd.DataFrame({"EXA": base + rng.normal(0, 0.001, n), "EXB": base}, index=idx)


def _ts_df(n: int = 400) -> pd.DataFrame:
    rng = np.random.default_rng(7)
    idx = pd.date_range("2026-04-01", periods=n, freq="h")
    near = 0.20 + np.cumsum(rng.normal(0.0, 0.0005, n))
    far = near + 0.02 + np.cumsum(rng.normal(0.0, 0.0002, n))
    frame = pd.DataFrame(
        {"BTC": 100.0 + np.cumsum(rng.normal(0, 0.5, n)), "iv_30d": near, "iv_90d": far},
        index=idx,
    )
    return frame


_STRATEGY_CASES = [
    ("mean_reversion", MeanReversionStrategy, dict(asset="BTC"), _ohlc_df()),
    ("momentum", MomentumStrategy, dict(asset="BTC"), _ohlc_df()),
    (
        "term_structure",
        TermStructureStrategy,
        dict(asset="BTC", near_tenor="iv_30d", far_tenor="iv_90d"),
        _ts_df(),
    ),
    ("volatility_surface", VolatilitySurfaceStrategy, dict(asset="BTC"), _ohlc_df()),
    ("cross_exchange", CrossExchangeArb, dict(exchange_a="EXA", exchange_b="EXB"), _ce_df()),
]


def _positions_zero(strat, sig) -> bool:
    sizes = strat.calculate_position_sizes(sig)
    return all(float(v) == 0.0 for v in sizes.values())


def test_all_strategies_default_to_strict_enriched_gates() -> None:
    for name, cls, kwargs, _data in _STRATEGY_CASES:
        strat = cls(**kwargs)
        assert strat.use_enriched_gates is True, name
        assert strat.strict_enriched_gates is True, name


def test_fail_closed_missing_gates_block_strict() -> None:
    for name, cls, kwargs, data in _STRATEGY_CASES:
        strat = cls(**kwargs, enriched_diagnostics=EMPTY_GATES_DIAG, strict_enriched_gates=True)
        sig = strat.generate_signals(data)
        gated_ok = (sig["enriched_gates_ok"] == 0.0).all()
        assert gated_ok, f"{name}: enriched_gates_ok not blocked by missing gates"
        assert _positions_zero(strat, sig), f"{name}: positions not blocked by missing gates"


def test_fail_closed_flagged_structural_break_blocks() -> None:
    for name, cls, kwargs, data in _STRATEGY_CASES:
        strat = cls(**kwargs, enriched_diagnostics=FLAGGED_DIAG, strict_enriched_gates=True)
        sig = strat.generate_signals(data)
        gated_ok = (sig["enriched_gates_ok"] == 0.0).all()
        assert gated_ok, f"{name}: enriched_gates_ok not blocked by flagged break"
        assert _positions_zero(strat, sig), f"{name}: positions not blocked by flagged break"


def test_fail_closed_structural_breaks_none_blocks_strict() -> None:
    for name, cls, kwargs, data in _STRATEGY_CASES:
        strat = cls(**kwargs, enriched_diagnostics=SB_NONE_DIAG, strict_enriched_gates=True)
        sig = strat.generate_signals(data)
        gated_ok = (sig["enriched_gates_ok"] == 0.0).all()
        assert gated_ok, f"{name}: gates not blocked when structural_breaks None under strict"
        assert _positions_zero(strat, sig), f"{name}: positions not blocked when structural_breaks None under strict"


def test_gate_none_coercion_is_fail_closed() -> None:
    # A non-all_pass gate explicitly set to None must block under strict (no None -> True coercion).
    diag = {
        "gates": {key: True for key in GATE_KEYS},
        "structural_breaks": {"flagged": False},
    }
    diag["gates"]["eg_pass"] = None
    for name, cls, kwargs, data in _STRATEGY_CASES:
        strat = cls(**kwargs, enriched_diagnostics=diag, strict_enriched_gates=True)
        sig = strat.generate_signals(data)
        gated_ok = (sig["enriched_gates_ok"] == 0.0).all()
        assert gated_ok, f"{name}: None gate coerced to pass under strict"
        assert _positions_zero(strat, sig), f"{name}: positions not blocked for None gate under strict"


def test_cached_vs_perbar_gate_parity_all_strategies() -> None:
    # Supplying diagnostics identical to the per-bar _build_diagnostics output
    # (all gates pass, no structural break) must yield identical signals to the
    # per-bar path (enriched_diagnostics=None) for every strategy.
    for name, cls, kwargs, data in _STRATEGY_CASES:
        strat_cached = cls(**kwargs, enriched_diagnostics=ALL_PASS_DIAG, strict_enriched_gates=True)
        strat_perbar = cls(**kwargs, enriched_diagnostics=None, strict_enriched_gates=True)
        sig_cached = strat_cached.generate_signals(data)
        sig_perbar = strat_perbar.generate_signals(data)
        pd.testing.assert_series_equal(
            sig_cached["enriched_gates_ok"],
            sig_perbar["enriched_gates_ok"],
            check_names=False,
        )
        weight_cols = [c for c in sig_cached.columns if c not in ("enriched_gates_ok",)]
        for c in weight_cols:
            if c in sig_perbar.columns:
                pd.testing.assert_series_equal(sig_cached[c], sig_perbar[c], check_names=False)


def test_pairs_parity_lock_via_shared_helper() -> None:
    df = _pairs_df()
    cached_diag = {
        "gates": {key: True for key in GATE_KEYS},
        "structural_breaks": {"flagged": False},
        "provenance": {"source": "tests", "real_data_only": True, "fabricated_data": False},
        "blocked_routes": [],
    }
    assert_cached_vs_perbar_gate_parity_strict(
        df,
        pair=("BTC", "ETH"),
        lookback=60,
        cached_diag=cached_diag,
        real_perbar=False,
    )
