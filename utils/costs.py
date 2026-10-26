"""
Transaction cost modeling for backtesting.

Costs are expressed as a fraction of capital to subtract from each period's
portfolio return. Built-in models:

* :class:`FixedCostModel` - linear cost in turnover (fees + slippage). This
  matches the legacy ``fee_rate`` / ``slippage`` behavior of the engine.
* :class:`LinearCostModel` - alias for :class:`FixedCostModel`.
* :class:`SquareRootImpactCostModel` - adds a square-root market-impact term,
  which better captures the nonlinear cost of large or frequent rebalancing.
* :class:`ProportionalCostModel` - simple proportional cost model.
* :class:`VolumeSlippageCostModel` - volume-based slippage approximation.
* :class:`TransactionCostModel` - flexible configurable cost model.

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


# Alias for compatibility
LinearCostModel = FixedCostModel
ProportionalCostModel = FixedCostModel


class TransactionCostModel(CostModel):
    """Flexible configurable cost model.

    Combines a proportional fee with optional fixed cost per trade and
    slippage components. ``fixed_cost`` is treated as a fraction of capital
    if applied per rebalance event (when turnover > 0).
    """

    def __init__(
        self,
        commission: float = 0.0,
        slippage: float = 0.0,
        fixed_cost: float = 0.0,
        impact: float = 0.0,
    ) -> None:
        self.commission = float(commission)
        self.slippage = float(slippage)
        self.fixed_cost = float(fixed_cost)
        self.impact = float(impact)

    def compute_cost(self, turnover: float, capital: float | None = None) -> float:
        if turnover is None:
            return 0.0
        try:
            t = float(turnover)
        except (TypeError, ValueError):
            return 0.0
        if not _is_finite(t) or t < 0.0:
            return 0.0
        cost = t * (self.commission + self.slippage)
        if t > 0.0 and self.fixed_cost != 0.0:
            cost += self.fixed_cost
        if self.impact != 0.0 and t > 0.0:
            cost += self.impact * math.sqrt(t)
        return cost

    def __repr__(self) -> str:
        return (
            "TransactionCostModel("
            f"commission={self.commission}, slippage={self.slippage}, "
            f"fixed_cost={self.fixed_cost}, impact={self.impact})"
        )


class VolumeSlippageCostModel(CostModel):
    """Volume-based slippage approximation.

    Models slippage as proportional to turnover (as a proxy for market
    impact relative to volume) with a configurable coefficient.
    """

    def __init__(self, slippage_coeff: float = 0.001, fee_rate: float = 0.0):
        self.slippage_coeff = float(slippage_coeff)
        self.fee_rate = float(fee_rate)

    def compute_cost(self, turnover: float, capital: float | None = None) -> float:
        if turnover is None:
            return 0.0
        try:
            t = float(turnover)
        except (TypeError, ValueError):
            return 0.0
        if not _is_finite(t) or t < 0.0:
            return 0.0
        slippage_cost = self.slippage_coeff * t * math.sqrt(t + 1e-18)
        return self.fee_rate * t + slippage_cost

    def __repr__(self) -> str:
        return (
            "VolumeSlippageCostModel("
            f"slippage_coeff={self.slippage_coeff}, fee_rate={self.fee_rate})"
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
