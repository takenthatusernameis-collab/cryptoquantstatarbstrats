"""Regime detection utilities."""

from __future__ import annotations

import pandas as pd


def rolling_volatility(series: pd.Series, window: int = 20) -> pd.Series:
    if window is None or window <= 1:
        window = 2
    return series.pct_change().rolling(window).std()


def volatility_regime(
    series: pd.Series, window: int = 20, n_regimes: int = 3, labels: list[str] | None = None
) -> pd.Series:
    vol = rolling_volatility(series, window)
    # quantile-based regimes
    q = vol.dropna()
    if q.empty:
        return pd.Series(index=series.index, dtype=object)
    try:
        bins = pd.qcut(vol, q=n_regimes, labels=False, duplicates="drop")
    except Exception:
        bins = pd.Series(0, index=series.index)
    if labels is not None and len(labels) == n_regimes:
        mapping = {i: labels[i] for i in range(n_regimes)}
        return bins.map(mapping)
    return bins


def trend_detection(series: pd.Series, short_window: int = 10, long_window: int = 50) -> pd.Series:
    if short_window is None or short_window <= 0:
        short_window = 1
    if long_window is None or long_window <= short_window:
        long_window = short_window + 1
    short_ma = series.rolling(short_window).mean()
    long_ma = series.rolling(long_window).mean()
    trend = pd.Series(0, index=series.index, dtype=int)
    trend[short_ma > long_ma] = 1
    trend[short_ma < long_ma] = -1
    return trend


def detect_regimes(
    data: pd.DataFrame, window: int = 20, trend_short: int = 10, trend_long: int = 50
) -> pd.DataFrame:
    out = pd.DataFrame(index=data.index)
    for col in data.columns:
        out[f"{col}_vol_regime"] = volatility_regime(data[col], window=window)
        out[f"{col}_trend"] = trend_detection(
            data[col], short_window=trend_short, long_window=trend_long
        )
    return out
