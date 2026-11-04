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
    real_perbar: bool = False,
):
    """Assert cached enriched diagnostics produce identical gate outcomes
    to per-bar path under strict_enriched_gates=True.

    This helper is the single source of truth for parity checks and must
    be used by all tests comparing cached vs uncached paths.

    When ``real_perbar`` is True, the per-bar path is left to compute its
    own diagnostics from the supplied ``df`` (no monkeypatch). This is the
    integration mode used by the borderline-pair test, where the cached
    diagnostic is itself derived from the same real series and the two
    paths must still agree end-to-end. When False (the default), the
    per-bar path is driven by ``fake_target_diag`` (or a fallback built
    from ``cached_diag``) so the two paths receive identical inputs and
    only the evaluation logic is exercised.
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

    if real_perbar:
        # Integration mode: let the per-bar path compute its own diagnostics
        # from the real series. No monkeypatch -- the point is to verify the
        # cached diagnostic (itself derived from the same series) agrees
        # with the live per-bar computation.
        sig_perbar = strat_perbar.generate_signals(df)
    else:
        orig = pt.target_schema_diagnostics
        try:
            pt.target_schema_diagnostics = _fake_target
            sig_perbar = strat_perbar.generate_signals(df)
        finally:
            pt.target_schema_diagnostics = orig

    def _diverged(col: str) -> str:
        a = sig_cached[col].to_numpy()
        b = sig_perbar[col].to_numpy()
        if len(a) != len(b):
            return f"{col}: length differs (cached={len(a)}, per-bar={len(b)})"
        diff = a != b
        if diff.any():
            idx = diff.nonzero()[0]
            sample = idx[:5].tolist()
            return (
                f"{col}: {int(diff.sum())} bar(s) diverge at {sample} "
                f"(cached values {a[diff].tolist()[:5]}, "
                f"per-bar values {b[diff].tolist()[:5]})"
            )
        return ""

    problems: list[str] = []
    for col in ("enriched_gates_ok", "long", "short"):
        msg = _diverged(col)
        if msg:
            problems.append(msg)
    if not sig_cached["enriched_gates_ok"].notna().all():
        problems.append("cached enriched_gates_ok contains NaN in strict mode")
    if not sig_perbar["enriched_gates_ok"].notna().all():
        problems.append("per-bar enriched_gates_ok contains NaN in strict mode")
    if problems:
        raise AssertionError(
            "Cached vs per-bar gate parity failed under strict_enriched_gates=True. "
            + " | ".join(problems)
        )
    return sig_cached, sig_perbar
