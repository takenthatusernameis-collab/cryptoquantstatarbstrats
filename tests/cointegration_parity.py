"""Shared parity assertions for cached vs per-bar cointegration gate evaluation.

Codified to prevent regression drift across tests. All parity violations
are explicit and unmissable.
"""

from __future__ import annotations

from typing import Any

import pandas as pd


def _diag_field_diverged(
    cached: dict[str, Any] | None,
    perbar: dict[str, Any] | None,
    pair: tuple[str, str],
    field: str,
) -> list[str]:
    """Compare one gate-determining field between cached and per-bar diagnostics.

    Returns a list of actionable messages (empty when the field agrees).
    Missing/None inputs are reported as diverged so a test that forgets to
    supply one of the two diagnostics fails loudly instead of silently
    comparing nothing.
    """
    problems: list[str] = []
    if cached is None or perbar is None:
        problems.append(
            f"{field}: one of cached/perbar diagnostics is missing "
            f"(cached={cached is not None}, perbar={perbar is not None})"
        )
        return problems
    a = cached.get(field)
    b = perbar.get(field)
    if a is None and b is None:
        return problems
    if a is None or b is None:
        problems.append(
            f"{field}: cached={a!r} vs per-bar={b!r} (one side missing)"
        )
        return problems
    if isinstance(a, dict) and isinstance(b, dict):
        for key in set(a.keys()) | set(b.keys()):
            av = a.get(key)
            bv = b.get(key)
            if av != bv:
                problems.append(
                    f"{field}.{key}: cached={av!r} vs per-bar={bv!r}"
                )
        return problems
    if a != b:
        problems.append(f"{field}: cached={a!r} vs per-bar={b!r}")
    return problems


def assert_cached_vs_perbar_gate_parity_strict(
    df: pd.DataFrame,
    pair: tuple[str, str] = ("BTC", "ETH"),
    lookback: int = 60,
    cached_diag: dict[str, Any] | None = None,
    fake_target_diag: dict[str, Any] | None = None,
    real_perbar: bool = False,
    check_input_parity: bool = True,
    check_provenance: bool = False,
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

    Input-parity enforcement (``check_input_parity=True``, always on when
    a per-bar fake is supplied and ``real_perbar`` is False): the cached
    and per-bar diagnostics must agree on the gate-determining fields
    (``gates``, ``structural_breaks``) before any output comparison is
    meaningful. A test that feeds *different* gates to the two paths and
    then asserts parity is comparing apples to oranges -- this helper
    fails loudly in that case, naming the pair and the diverged field.

    When ``check_provenance=True`` the helper additionally asserts that
    ``blocked_routes`` and ``provenance`` agree between the two inputs.
    This is opt-in because the fallback fake (used when only
    ``cached_diag`` is supplied) intentionally marks itself
    ``fabricated_data: True``; callers that want provenance parity must
    supply an explicit ``fake_target_diag`` that mirrors the cached
    provenance.
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
        perbar_diag = None
    else:
        perbar_diag = (
            fake_target_diag
            if fake_target_diag is not None
            else _fake_target(None, None, "/".join(pair))
        )
        orig = pt.target_schema_diagnostics
        try:
            pt.target_schema_diagnostics = _fake_target
            sig_perbar = strat_perbar.generate_signals(df)
        finally:
            pt.target_schema_diagnostics = orig

    # --- Input-parity enforcement (gate-determining fields, always on when
    # a per-bar fake is supplied and not in real_perbar integration mode).
    if (not real_perbar) and check_input_parity and cached_diag is not None:
        problems: list[str] = []
        problems.extend(_diag_field_diverged(cached_diag, perbar_diag, pair, "gates"))
        problems.extend(
            _diag_field_diverged(cached_diag, perbar_diag, pair, "structural_breaks")
        )
        if check_provenance:
            problems.extend(
                _diag_field_diverged(cached_diag, perbar_diag, pair, "blocked_routes")
            )
            problems.extend(
                _diag_field_diverged(cached_diag, perbar_diag, pair, "provenance")
            )
        if problems:
            raise AssertionError(
                f"Cached vs per-bar input parity failed for pair {pair}: "
                + " | ".join(problems)
            )

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
