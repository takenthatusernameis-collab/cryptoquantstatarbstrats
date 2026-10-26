"""
Risk metrics utilities.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def sharpe_ratio(returns, risk_free_rate: float = 0.0, periods_per_year: int = 252) -> float:
    """Calculate Sharpe ratio."""
    if isinstance(returns, pd.Series):
        returns = returns.dropna()
    else:
        returns = np.asarray(returns)
        returns = returns[~np.isnan(returns)]

    if len(returns) == 0:
        return 0.0

    excess_returns = returns - risk_free_rate / periods_per_year
    mean_excess = np.mean(excess_returns)
    std = np.std(excess_returns, ddof=0)
    if std == 0:
        return 0.0
    return float(mean_excess / std * np.sqrt(periods_per_year))


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


def max_drawdown(equity_curve) -> float:
    """Compute maximum drawdown from equity curve."""
    if isinstance(equity_curve, pd.Series):
        equity = equity_curve
    else:
        equity = pd.Series(equity_curve)

    if len(equity) == 0:
        return 0.0

    running_max = equity.cummax()
    drawdown = equity / running_max - 1.0
    return float(drawdown.min())


def calmar_ratio(returns, equity_curve=None, periods_per_year: int = 252) -> float:
    """Calculate Calmar ratio (annualized return / max drawdown)."""
    if isinstance(returns, pd.Series):
        returns_clean = returns.dropna()
    else:
        returns_clean = np.asarray(returns)
        returns_clean = returns_clean[~np.isnan(returns_clean)]

    if len(returns_clean) == 0:
        return 0.0

    ann_return = float(np.mean(returns_clean) * periods_per_year)

    if equity_curve is not None:
        mdd = abs(max_drawdown(equity_curve))
    else:
        # Compute from cumulative returns if equity curve not provided
        cumret = (1.0 + returns_clean).cumprod()
        mdd = abs(max_drawdown(cumret))

    if mdd == 0:
        return 0.0

    return float(ann_return / mdd)


def beta(returns, market_returns, risk_free_rate: float = 0.0) -> float:
    """Calculate beta relative to market."""
    if isinstance(returns, pd.Series):
        returns = returns.dropna()
    else:
        returns = np.asarray(returns)
        returns = returns[~np.isnan(returns)]

    if isinstance(market_returns, pd.Series):
        market_returns = market_returns.dropna()
    else:
        market_returns = np.asarray(market_returns)
        market_returns = market_returns[~np.isnan(market_returns)]

    if len(returns) == 0 or len(market_returns) == 0:
        return 0.0

    # Align lengths
    min_len = min(len(returns), len(market_returns))
    returns = returns[-min_len:]
    market_returns = market_returns[-min_len:]

    excess_returns = returns - risk_free_rate / 252
    excess_market = market_returns - risk_free_rate / 252

    cov = np.cov(excess_returns, excess_market)[0, 1]
    var_market = np.var(excess_market)

    if var_market == 0:
        return 0.0

    return float(cov / var_market)


def information_ratio(returns, benchmark_returns) -> float:
    """Calculate information ratio."""
    if isinstance(returns, pd.Series):
        returns = returns.dropna()
    else:
        returns = np.asarray(returns)
        returns = returns[~np.isnan(returns)]

    if isinstance(benchmark_returns, pd.Series):
        benchmark_returns = benchmark_returns.dropna()
    else:
        benchmark_returns = np.asarray(benchmark_returns)
        benchmark_returns = benchmark_returns[~np.isnan(benchmark_returns)]

    if len(returns) == 0 or len(benchmark_returns) == 0:
        return 0.0

    min_len = min(len(returns), len(benchmark_returns))
    returns = returns[-min_len:]
    benchmark_returns = benchmark_returns[-min_len:]

    excess = returns - benchmark_returns
    mean_excess = np.mean(excess)
    tracking_error = np.std(excess, ddof=0)

    if tracking_error == 0:
        return 0.0

    return float(mean_excess / tracking_error * np.sqrt(252))


def alpha(returns, market_returns, risk_free_rate: float = 0.0,
           periods_per_year: int = 252) -> float:
    """Calculate Jensen's alpha (annualized)."""
    if isinstance(returns, pd.Series):
        returns = returns.dropna()
    else:
        returns = np.asarray(returns)
        returns = returns[~np.isnan(returns)]

    if isinstance(market_returns, pd.Series):
        market_returns = market_returns.dropna()
    else:
        market_returns = np.asarray(market_returns)
        market_returns = market_returns[~np.isnan(market_returns)]

    if len(returns) == 0 or len(market_returns) == 0:
        return 0.0

    min_len = min(len(returns), len(market_returns))
    returns = returns[-min_len:]
    market_returns = market_returns[-min_len:]

    b = beta(returns, market_returns, risk_free_rate)
    excess_returns = np.mean(returns) - risk_free_rate / periods_per_year
    excess_market = np.mean(market_returns) - risk_free_rate / periods_per_year
    alpha_daily = excess_returns - b * excess_market
    return float(alpha_daily * periods_per_year)


def tracking_error(returns, benchmark_returns, periods_per_year: int = 252) -> float:
    """Calculate annualized tracking error."""
    if isinstance(returns, pd.Series):
        returns = returns.dropna()
    else:
        returns = np.asarray(returns)
        returns = returns[~np.isnan(returns)]

    if isinstance(benchmark_returns, pd.Series):
        benchmark_returns = benchmark_returns.dropna()
    else:
        benchmark_returns = np.asarray(benchmark_returns)
        benchmark_returns = benchmark_returns[~np.isnan(benchmark_returns)]

    if len(returns) == 0 or len(benchmark_returns) == 0:
        return 0.0

    min_len = min(len(returns), len(benchmark_returns))
    returns = returns[-min_len:]
    benchmark_returns = benchmark_returns[-min_len:]

    excess = returns - benchmark_returns
    te = np.std(excess, ddof=0)
    if te == 0:
        return 0.0
    return float(te * np.sqrt(periods_per_year))


def win_rate(returns) -> float:
    """Calculate win rate (proportion of positive returns)."""
    if isinstance(returns, pd.Series):
        returns_clean = returns.dropna()
    else:
        returns_clean = np.asarray(returns)
        returns_clean = returns_clean[~np.isnan(returns_clean)]

    if len(returns_clean) == 0:
        return 0.0

    wins = np.sum(returns_clean > 0)
    return float(wins / len(returns_clean))


def profit_factor(returns) -> float:
    """Calculate profit factor (gross profit / gross loss)."""
    if isinstance(returns, pd.Series):
        returns_clean = returns.dropna()
    else:
        returns_clean = np.asarray(returns)
        returns_clean = returns_clean[~np.isnan(returns_clean)]

    if len(returns_clean) == 0:
        return 0.0

    gains = returns_clean[returns_clean > 0].sum()
    losses = returns_clean[returns_clean < 0].sum()

    if losses == 0:
        return float("inf") if gains > 0 else 0.0

    return float(abs(gains / losses))


def max_drawdown_percent(equity_curve) -> float:
    """Compute maximum drawdown as percentage (positive number)."""
    mdd = max_drawdown(equity_curve)
    return float(abs(mdd) * 100.0)
