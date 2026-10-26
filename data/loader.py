"""
Data loader for cryptocurrency market data
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from utils import clean_data as _clean_data


class DataLoader:
    """Load and preprocess cryptocurrency price data."""

    def __init__(self, data_source: str = "csv"):
        self.data_source = data_source

    @classmethod
    def load_csv(cls, path: str) -> pd.DataFrame:
        """Load data from a CSV file.

        Reads a CSV with a `timestamp` column + asset columns, parses
        timestamps, sets the index, and returns a DataFrame aligned with
        the engine's expected shape.
        """
        df = pd.read_csv(path)
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df = df.set_index("timestamp")
        elif "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
            df = df.set_index("date")
        elif "time" in df.columns:
            df["time"] = pd.to_datetime(df["time"])
            df = df.set_index("time")
        else:
            # Try to parse first column as datetime if it looks like it
            first_col = df.columns[0]
            try:
                df[first_col] = pd.to_datetime(df[first_col])
                df = df.set_index(first_col)
            except Exception:
                pass

        df = df.sort_index()
        return df

    def load_data(
        self,
        symbols: list[str],
        start_date: str,
        end_date: str,
        freq: str = "1h",
    ) -> pd.DataFrame:
        """Load price data for given symbols."""
        dates = pd.date_range(start_date, end_date, freq=freq)
        data = pd.DataFrame(index=dates)

        for symbol in symbols:
            # Generate correlated price series for demonstration.
            returns = np.random.randn(len(dates)) * 0.02
            prices = 100 * np.exp(np.cumsum(returns))
            data[symbol] = prices

        return data

    def clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Clean and preprocess data."""
        return _clean_data(data)
