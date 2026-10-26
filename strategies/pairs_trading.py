"""
Pairs Trading Strategy using Cointegration
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from strategies.base import PairStrategy


class CointegrationPairsStrategy(PairStrategy):
    """Pairs trading strategy based on cointegration testing."""

    def __init__(
        self,
        pair: tuple[str, str],
        lookback: int = 60,
        entry_threshold: float = 2.0,
        exit_threshold: float = 0.5,
        params: dict[str, Any] | None = None,
    ):
        super().__init__(
            f"coint_pairs_{pair[0]}_{pair[1]}", pair, params
        )
        self.lookback = lookback
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold

    def test_cointegration(self, price1: pd.Series, price2: pd.Series) -> tuple[float, float]:
        """Test for cointegration between two price series."""
        from statsmodels.tsa.stattools import coint

        score, pvalue, _ = coint(price1, price2)
        return float(score), float(pvalue)

    def calculate_spread(self, price1: pd.Series, price2: pd.Series) -> pd.Series:
        """Calculate the spread between cointegrated pairs via OLS."""
        from sklearn.linear_model import LinearRegression

        X = price2.values.reshape(-1, 1)
        y = price1.values
        reg = LinearRegression().fit(X, y)
        self.hedge_ratio = float(reg.coef_[0]) if reg.coef_[0] != 0 else 1.0
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

        signals["zscore"] = zscore
        signals["long"] = zscore < -self.entry_threshold
        signals["short"] = zscore > self.entry_threshold
        signals["exit"] = abs(zscore) < self.exit_threshold

        return signals

    def calculate_position_sizes(self, signals: pd.DataFrame) -> dict[str, float]:
        """Return position sizes for the pair based on latest signal."""
        asset1, asset2 = self.pair
        last = signals.iloc[-1] if len(signals) else pd.Series(dtype=float)
        long = bool(last.get("long", False))
        short = bool(last.get("short", False))
        if long:
            return {asset1: 1.0, asset2: -self.hedge_ratio}
        if short:
            return {asset1: -1.0, asset2: self.hedge_ratio}
        return {asset1: 0.0, asset2: 0.0}
