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
    """Remove NaNs and clip extreme outliers."""
    data = data.dropna()
    # Winsorize at 0.1% on each side to avoid extreme outliers.
    quantiles = data.quantile([0.001, 0.999])
    for col in data.columns:
        lo, hi = quantiles.loc[0.001, col], quantiles.loc[0.999, col]
        data[col] = data[col].clip(lower=lo, upper=hi)
    return data


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
