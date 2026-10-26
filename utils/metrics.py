"""
Risk metrics utilities.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def sortino_ratio(returns, risk_free_rate: float = 0.0, periods_per_year: int = 252) -> float:
    """Calculate Sortino ratio using downside deviation (only negative returns)."""
    if isinstance(returns, pd.Series):
        returns = returns.dropna()
    else:
        returns = np.asarray(returns)
        returns = returns[~np.isnan(returns)]

    if len(returns) == 0:
        return 0.0

    excess_returns = returns - risk_free_rate / periods_per_year
    mean_excess = np.mean(excess_returns)

    # Downside deviation: only negative excess returns
    downside_returns = excess_returns[excess_returns < 0]
    if len(downside_returns) == 0:
        return 0.0

    downside_deviation = np.sqrt(np.mean(downside_returns**2))
    if downside_deviation == 0:
        return 0.0

    return float(mean_excess / downside_deviation * np.sqrt(periods_per_year))


def var(returns, confidence: float = 0.95) -> float:
    """Historical Value at Risk."""
    if isinstance(returns, pd.Series):
        returns = returns.dropna()
    else:
        returns = np.asarray(returns)
        returns = returns[~np.isnan(returns)]

    if len(returns) == 0:
        return 0.0

    # VaR is the loss at the confidence level - typically reported as positive number
    # or negative return; check convention - historical VaR is the percentile
    var_result = np.percentile(returns, (1 - confidence) * 100)
    return float(var_result)


def cvar(returns, confidence: float = 0.95) -> float:
    """Conditional VaR (expected shortfall)."""
    if isinstance(returns, pd.Series):
        returns = returns.dropna()
    else:
        returns = np.asarray(returns)
        returns = returns[~np.isnan(returns)]

    if len(returns) == 0:
        return 0.0

    var_threshold = np.percentile(returns, (1 - confidence) * 100)
    tail_returns = returns[returns <= var_threshold]
    if len(tail_returns) == 0:
        return float(var_threshold)

    return float(np.mean(tail_returns))


def max_drawdown_duration_from_curve(equity_curve) -> int:
    """Compute max drawdown duration from equity curve."""
    if isinstance(equity_curve, pd.Series):
        equity = equity_curve
    else:
        equity = pd.Series(equity_curve)

    if len(equity) == 0:
        return 0

    running_max = equity.cummax()
    drawdown = equity / running_max - 1.0

    max_dd_duration = 0
    in_drawdown = False
    dd_start = 0
    for i in range(len(drawdown)):
        if drawdown.iloc[i] < 0:
            if not in_drawdown:
                in_drawdown = True
                dd_start = i
        else:
            if in_drawdown:
                dd_duration = i - dd_start
                if dd_duration > max_dd_duration:
                    max_dd_duration = dd_duration
                in_drawdown = False
    if in_drawdown:
        dd_duration = len(drawdown) - dd_start
        if dd_duration > max_dd_duration:
            max_dd_duration = dd_duration

    return int(max_dd_duration)
