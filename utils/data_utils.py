"""
Data processing and validation utilities.
"""

from __future__ import annotations

import pandas as pd


def fill_missing(data: pd.DataFrame, method: str = "ffill") -> pd.DataFrame:
    """Fill missing values in dataframe."""
    if method == "ffill":
        return data.fillna(method="ffill").fillna(method="bfill").fillna(0.0)
    elif method == "bfill":
        return data.fillna(method="bfill").fillna(method="ffill").fillna(0.0)
    elif method == "zero":
        return data.fillna(0.0)
    elif method == "mean":
        return data.fillna(data.mean())
    else:
        return data.fillna(method="ffill").fillna(0.0)


def remove_outliers(data: pd.DataFrame, threshold: float = 3.0) -> pd.DataFrame:
    """Remove outliers beyond threshold standard deviations."""
    result = data.copy()
    for col in result.columns:
        mean = result[col].mean()
        std = result[col].std()
        if std > 0:
            result = result[(result[col] - mean).abs() <= threshold * std]
    return result


def resample_data(data: pd.DataFrame, freq: str = "1D") -> pd.DataFrame:
    """Resample data to different frequency."""
    return data.resample(freq).last().dropna()


def compute_correlation(returns: pd.DataFrame, method: str = "pearson") -> pd.DataFrame:
    """Compute correlation matrix of returns."""
    return returns.corr(method=method)
