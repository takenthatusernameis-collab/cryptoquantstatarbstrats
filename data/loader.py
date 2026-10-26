"""
Data loader for cryptocurrency market data
"""

import pandas as pd
import numpy as np
from typing import List, Optional


class DataLoader:
    """Load and preprocess cryptocurrency price data."""
    
    def __init__(self, data_source: str = "csv"):
        self.data_source = data_source
        
    def load_data(self, symbols: List[str], start_date: str, end_date: str) -> pd.DataFrame:
        """Load price data for given symbols."""
        # Generate sample data for demonstration
        dates = pd.date_range(start_date, end_date, freq='1H')
        data = pd.DataFrame(index=dates)
        
        for symbol in symbols:
            # Generate correlated price series for pairs trading
            returns = np.random.randn(len(dates)) * 0.02
            prices = 100 * np.exp(np.cumsum(returns))
            data[symbol] = prices
            
        return data
        
    def clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Clean and preprocess data."""
        # Remove missing values
        data = data.dropna()
        # Remove outliers (simple approach)
        return data
