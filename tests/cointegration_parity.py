"""Shared parity assertions for cached vs per-bar cointegration gate evaluation.

Codified to prevent regression drift across tests. All parity violations
are explicit and unmissable.
"""

from __future__ import annotations

from typing import Any

import pandas as pd


def assert_cached_vs_perbar_gate_parity_strict(
    df: pd.DataFrame,
    pair: tuple[str, str] = ("BTC", "ETH"),
    lookback: int = 60,
    cached_diag: dict[str, Any] | None = None,
    fake_target_diag: dict[str, Any] | None = None,
):
    """Assert cached enriched diagnostics produce identical gate outcomes
    to per-bar path under strict_enriched_gates=True.

    This helper is the single source of truth for parity checks and must
    be used by all tests comparing cached vs uncached paths.
    """
    import strategies.pairs_trading as pt
    from strategies.pairs_trading import CointegrationPairsStrategy

    strat_cached = CointegrationPairsStrategy(
        pair,
        lookback=lookback,
        enriched_diagnostics=cached_diag,
        use_enriched_gates=True,
        strict_enriched_gates=True,
    )
    strat_perbar = CointegrationPairsStrategy(
        pair,
        lookback=lookback,
        enriched_diagnostics=None,
        use_enriched_gates=True,
        strict_enriched_gates=True,
    )
    sig_cached = strat_cached.generate_signals(df)

    def _fake_target(p1, p2, pair_name=""):
        if fake_target_diag is not None:
            return fake_target_diag
        # Fallback to cached diag if not provided
        if cached_diag is not None:
            return {
                "gates": cached_diag.get("gates", {}),
                "structural_breaks": cached_diag.get("structural_breaks", {}),
                "provenance": {"fabricated_data": True},
            }
        raise AssertionError("fake_target_diag required for per-bar parity test")

    orig = pt.target_schema_diagnostics
    try:
        pt.target_schema_diagnostics = _fake_target
        sig_perbar = strat_perbar.generate_signals(df)
    finally:
        pt.target_schema_diagnostics = orig

    assert (sig_cached["enriched_gates_ok"] == sig_perbar["enriched_gates_ok"]).all(), (
        "Cached vs per-bar gate parity failed under strict_enriched_gates=True"
    )
    assert (sig_cached["long"] == sig_perbar["long"]).all()
    assert (sig_cached["short"] == sig_perbar["short"]).all()
    assert (sig_cached["enriched_gates_ok"].notna().all() and sig_perbar["enriched_gates_ok"].notna().all()), (
        "Parity failure: enriched_gates_ok contains NaN in strict mode"
    )
    return sig_cached, sig_perbar
