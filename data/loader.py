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
