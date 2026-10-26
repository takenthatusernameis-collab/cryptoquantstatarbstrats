"""
Position sizing and risk management utilities.

These helpers translate account equity and risk assumptions into capital
allocations (position sizes). They are intentionally pure: given an equity
value and a risk parameter they return a dollar allocation. Combine them with
the ``RiskManager`` in :mod:`utils.risk` to enforce per-asset caps.
"""

from __future__ import annotations

from typing import Any

import pandas as pd


def fixed_fractional(equity: float, risk_fraction: float) -> float:
    """Return the capital allocation for a fixed fractional position.

    A common money-management rule: risk a fixed fraction of equity on each
    trade. The returned value is the capital (in dollars) to allocate, which
    can be negative to represent a short position when ``risk_fraction`` is
    negative.

    Args:
        equity: Current account equity (must be non-negative).
        risk_fraction: Fraction of equity to allocate (e.g. ``0.02`` for
            2%). May be negative for short side.

    Returns:
        The allocated capital ``equity * risk_fraction`` or ``0.0`` when
        inputs are invalid (non-finite, negative equity, or non-finite risk).
    """
    if equity is None or risk_fraction is None:
        return 0.0
    try:
        eq = float(equity)
        rf = float(risk_fraction)
    except (TypeError, ValueError):
        return 0.0
    if eq < 0.0 or not _is_finite(eq) or not _is_finite(rf):
        return 0.0
    return eq * rf


def vol_target(
    equity: float,
    target_vol: float,
    realized_vol: float | pd.Series,
    lookback: int | None = None,
) -> float:
    """Return the capital allocation for volatility targeting.

    Scales the position so that the dollar exposure's volatility matches
    ``target_vol``. The allocation is ``equity * target_vol / realized_vol``
    when a positive realized volatility is available; otherwise ``0.0``.

    Args:
        equity: Current account equity (must be non-negative).
        target_vol: Desired annualized (or per-period) portfolio volatility
            as a fraction (e.g. ``0.15`` for 15%).
        realized_vol: Estimated volatility of the asset. May be a scalar or a
            pandas Series of historical returns; when a Series is provided and
            ``lookback`` is given, the rolling standard deviation over the
            last ``lookback`` observations is used.
        lookback: Window size used to compute realized volatility from a
            return Series. Ignored when ``realized_vol`` is a scalar.

    Returns:
        The allocated capital, or ``0.0`` when inputs are invalid.
    """
    if equity is None or target_vol is None or realized_vol is None:
        return 0.0
    try:
        eq = float(equity)
        tv = float(target_vol)
    except (TypeError, ValueError):
        return 0.0
    if eq < 0.0 or not _is_finite(eq) or not _is_finite(tv) or tv <= 0.0:
        return 0.0

    vol = _resolve_realized_vol(realized_vol, lookback)
    if vol is None or vol <= 0.0 or not _is_finite(vol):
        return 0.0
    return eq * tv / vol


def kelly(
    fractional_edge: float,
    win_prob: float,
    win_loss_ratio: float,
) -> float:
    """Return the Kelly criterion fraction of capital to risk.

    Computes the optimal bet fraction for a binary outcome where a win
    returns ``win_loss_ratio`` times the amount risked and a loss returns the
    full amount risked. The full-Kelly fraction is::

        f* = (win_prob * (win_loss_ratio + 1) - 1) / win_loss_ratio

    ``fractional_edge`` scales this to a fractional-Kelly allocation (e.g.
    ``0.5`` for half Kelly), a common risk-control practice. The result is
    clamped to ``>= 0`` so that negative edges (don't bet) map to ``0.0``.

    Args:
        fractional_edge: Fraction of full Kelly to apply (e.g. ``1.0`` for
            full Kelly, ``0.5`` for half Kelly).
        win_prob: Probability of a win, in ``[0, 1]``.
        win_loss_ratio: Ratio of win magnitude to loss magnitude (payoff
            ratio, ``b``). Must be positive.

    Returns:
        The Kelly fraction of capital to risk, clamped to ``>= 0``.
    """
    if fractional_edge is None or win_prob is None or win_loss_ratio is None:
        return 0.0
    try:
        fe = float(fractional_edge)
        wp = float(win_prob)
        b = float(win_loss_ratio)
    except (TypeError, ValueError):
        return 0.0
    if not (_is_finite(fe) and _is_finite(wp) and _is_finite(b)):
        return 0.0
    if wp < 0.0 or wp > 1.0 or b <= 0.0:
        return 0.0
    full_kelly = (wp * (b + 1.0) - 1.0) / b
    result = fe * full_kelly
    if result < 0.0:
        return 0.0
    return result


def _is_finite(value: Any) -> bool:
    """Return True when ``value`` is a real finite number."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return False
    return v == v and v not in (float("inf"), float("-inf"))


def _resolve_realized_vol(
    realized_vol: float | pd.Series, lookback: int | None
) -> float | None:
    """Resolve a scalar realized volatility from the given input."""
    if isinstance(realized_vol, pd.Series):
        series = realized_vol.dropna()
        if len(series) == 0:
            return None
        if lookback is not None and lookback > 0:
            window = series.rolling(int(lookback)).std()
            if len(window) == 0:
                return None
            last = window.iloc[-1]
        else:
            last = series.std()
        if last is None:
            return None
        try:
            return float(last)
        except (TypeError, ValueError):
            return None
    try:
        return float(realized_vol)
    except (TypeError, ValueError):
        return None
