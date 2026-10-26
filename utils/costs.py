"""
Transaction cost modeling for backtesting.

Costs are expressed as a fraction of capital to subtract from each period's
portfolio return. Built-in models:

* :class:`FixedCostModel` - linear cost in turnover (fees + slippage). This
  matches the legacy ``fee_rate`` / ``slippage`` behavior of the engine.
* :class:`SquareRootImpactCostModel` - adds a square-root market-impact term,
  which better captures the nonlinear cost of large or frequent rebalancing.

Pass a model to :meth:`backtest.engine.BacktestEngine.run` via the
``cost_model`` argument to override the legacy ``fee_rate`` / ``slippage``
parameters. When no model is supplied the engine falls back to the legacy
behavior, so existing callers are unaffected.
"""

from __future__ import annotations

import math
from typing import Any

import pandas as pd


class CostModel:
    """Base class for transaction cost models.

    Subclasses translate a per-period turnover (the sum of absolute weight
    changes across assets) into a cost fraction of capital. The base class is
    intentionally not abstract so it can be used as a type hint; calling
    :meth:`compute_cost` on the base directly raises ``NotImplementedError``.
    """

    def compute_cost(self, turnover: float, capital: float | None = None) -> float:
        """Return the cost for a single period as a fraction of capital."""
        raise NotImplementedError

    def compute_cost_series(
        self, turnover: pd.Series, capital: float | None = None
    ) -> pd.Series:
        """Apply :meth:`compute_cost` element-wise over a turnover series."""
        if not isinstance(turnover, pd.Series):
            turnover = pd.Series(turnover)
        return pd.Series(
            [self.compute_cost(float(t), capital) for t in turnover.values],
            index=turnover.index,
        )

    def __repr__(self) -> str:
        return f"{type(self).__name__}()"


def _is_finite(value: Any) -> bool:
    """Return True when ``value`` is a real finite number."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return False
    return v == v and v not in (float("inf"), float("-inf"))


class FixedCostModel(CostModel):
    """Linear cost model: ``cost = turnover * (fee_rate + slippage)``."""

    def __init__(self, fee_rate: float = 0.0, slippage: float = 0.0):
        self.fee_rate = float(fee_rate)
        self.slippage = float(slippage)

    def compute_cost(self, turnover: float, capital: float | None = None) -> float:
        if turnover is None:
            return 0.0
        try:
            t = float(turnover)
        except (TypeError, ValueError):
            return 0.0
        if not _is_finite(t) or t < 0.0:
            return 0.0
        return t * (self.fee_rate + self.slippage)

    def __repr__(self) -> str:
        return (
            f"FixedCostModel(fee_rate={self.fee_rate}, slippage={self.slippage})"
        )


class SquareRootImpactCostModel(CostModel):
    """Cost model with linear fees plus square-root market impact.

    The cost for a period is::

        cost = fee_rate * turnover + impact_coeff * sqrt(turnover)

    The square-root term captures the empirical regularity that market impact
    grows sub-linearly with participation / order size. The model is flat when
    turnover is zero (no trades, no costs) and grows faster than linearly for
    small rebalancing activity, which penalizes churn more realistically than a
    purely linear model.
    """

    def __init__(self, fee_rate: float = 0.001, impact_coeff: float = 0.05):
        self.fee_rate = float(fee_rate)
        self.impact_coeff = float(impact_coeff)

    def compute_cost(self, turnover: float, capital: float | None = None) -> float:
        if turnover is None:
            return 0.0
        try:
            t = float(turnover)
        except (TypeError, ValueError):
            return 0.0
        if not _is_finite(t) or t < 0.0:
            return 0.0
        impact = self.impact_coeff * math.sqrt(t)
        return self.fee_rate * t + impact

    def __repr__(self) -> str:
        return (
            "SquareRootImpactCostModel("
            f"fee_rate={self.fee_rate}, impact_coeff={self.impact_coeff})"
        )
