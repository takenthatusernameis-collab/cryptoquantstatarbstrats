"""
Statistical Arbitrage Strategy Base Classes
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import pandas as pd


class Strategy(ABC):
    """Base class for all statistical arbitrage strategies."""

    def __init__(self, name: str, params: dict[str, Any] | None = None):
        self.name = name
        self.params = params or {}
        self.positions: dict[str, float] = {}

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on market data."""
        ...

    @abstractmethod
    def calculate_position_sizes(self, signals: pd.DataFrame) -> dict[str, float]:
        """Calculate position sizes for each asset."""
        ...


class PairStrategy(Strategy):
    """Base class for pairs trading strategies."""

    def __init__(
        self,
        name: str,
        pair: tuple[str, str],
        params: dict[str, Any] | None = None,
    ):
        super().__init__(name, params)
        self.pair = pair
        self.hedge_ratio = 1.0

    def calculate_position_sizes(self, signals: pd.DataFrame) -> dict[str, float]:
        """Equal risk allocation between the two legs of the pair."""
        asset1, asset2 = self.pair
        last = signals.iloc[-1] if len(signals) else pd.Series(dtype=float)
        long = bool(last.get("long", False))
        short = bool(last.get("short", False))
        if long:
            return {asset1: 1.0, asset2: -self.hedge_ratio}
        if short:
            return {asset1: -1.0, asset2: self.hedge_ratio}
        return {asset1: 0.0, asset2: 0.0}
