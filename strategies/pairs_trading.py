"""
Pairs Trading Strategy using Cointegration
"""

import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import coint
from strategies.base import PairStrategy


class CointegrationPairsStrategy(PairStrategy):
    """Pairs trading strategy based on cointegration testing."""
    
    def __init__(self, pair: tuple, lookback: int = 60, entry_threshold: float = 2.0,
                 exit_threshold: float = 0.5, params: dict = None):
        super().__init__(f"coint_pairs_{pair[0]}_{pair[1]}", pair, params)
        self.lookback = lookback
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold
        
    def test_cointegration(self, price1: pd.Series, price2: pd.Series):
        """Test for cointegration between two price series."""
        score, pvalue, _ = coint(price1, price2)
        return score, pvalue
        
    def calculate_spread(self, price1: pd.Series, price2: pd.Series):
        """Calculate the spread between cointegrated pairs."""
        # Simple linear regression for hedge ratio
        from sklearn.linear_model import LinearRegression
        X = price2.values.reshape(-1, 1)
        y = price1.values
        reg = LinearRegression().fit(X, y)
        self.hedge_ratio = reg.coef_[0]
        spread = price1 - self.hedge_ratio * price2
        return spread
        
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on spread z-score."""
        signals = pd.DataFrame(index=data.index)
        asset1, asset2 = self.pair
        
        spread = self.calculate_spread(data[asset1], data[asset2])
        spread_mean = spread.rolling(self.lookback).mean()
        spread_std = spread.rolling(self.lookback).std()
        zscore = (spread - spread_mean) / spread_std
        
        signals['zscore'] = zscore
        signals['long'] = zscore < -self.entry_threshold
        signals['short'] = zscore > self.entry_threshold
        signals['exit'] = abs(zscore) < self.exit_threshold
        
        return signals
