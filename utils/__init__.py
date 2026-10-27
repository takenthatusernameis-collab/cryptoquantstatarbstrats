"""
Utility functions for data processing and strategy helpers
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Compute simple percentage returns."""
    return prices.pct_change().fillna(0.0)


def log_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Compute log returns."""
    return np.log(prices / prices.shift(1)).fillna(0.0)


def zscore(series: pd.Series, window: int) -> pd.Series:
    """Rolling z-score of a series."""
    mean = series.rolling(window).mean()
    std = series.rolling(window).std()
    return (series - mean) / std


def half_life(series: pd.Series) -> float:
    """Estimate mean-reversion half-life via AR(1) coefficient."""
    if len(series) < 2:
        return float("nan")
    y = series.diff().dropna().values
    x = series.shift(1).dropna().values
    if len(y) == 0 or np.std(x) == 0:
        return float("nan")
    beta = np.polyfit(x, y, 1)[0]
    if beta >= 0:
        return float("inf")
    return float(-np.log(2.0) / beta)


def clean_data(data: pd.DataFrame) -> pd.DataFrame:
    """Drop incomplete rows while preserving observed market prices exactly.

    Winsorizing price levels changes historical returns and can erase real
    market shocks. Use winsorize_data explicitly for features where clipping
    is methodologically justified; never apply it implicitly to prices.
    """
    return data.dropna().copy()


def winsorize_data(
    data: pd.DataFrame,
    lower_quantile: float = 0.001,
    upper_quantile: float = 0.999,
) -> pd.DataFrame:
    """Explicitly winsorize numeric columns for feature preprocessing."""
    if not 0.0 <= lower_quantile < upper_quantile <= 1.0:
        raise ValueError("Quantiles must satisfy 0 <= lower < upper <= 1.")
    result = data.copy()
    numeric = result.select_dtypes(include=[np.number]).columns
    if len(numeric) == 0:
        return result
    quantiles = result[numeric].quantile([lower_quantile, upper_quantile])
    for col in numeric:
        lo = quantiles.loc[lower_quantile, col]
        hi = quantiles.loc[upper_quantile, col]
        result[col] = result[col].clip(lower=lo, upper=hi)
    return result


def annualized_metrics(returns: pd.Series, periods: int = 252) -> dict[str, float]:
    """Compute annualized return, volatility, and Sharpe ratio."""
    if len(returns) == 0 or returns.std() == 0:
        return {"annual_return": 0.0, "annual_vol": 0.0, "sharpe": 0.0}
    ann_return = returns.mean() * periods
    ann_vol = returns.std() * np.sqrt(periods)
    sharpe = ann_return / ann_vol if ann_vol > 0 else 0.0
    return {
        "annual_return": float(ann_return),
        "annual_vol": float(ann_vol),
        "sharpe": float(sharpe),
    }
