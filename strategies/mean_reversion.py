"""
Mean Reversion Strategy using rolling z-score or Bollinger Bands
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from strategies.base import Strategy
from utils import zscore


class MeanReversionStrategy(Strategy):
    """Mean-reversion strategy on a single asset's price.

    Longs when the price drops below the lower Bollinger Band (z-score < -entry)
    and shorts when it rises above the upper band (z-score > entry). Exits when
    the z-score reverts toward the mean.
    """

    def __init__(
        self,
        asset: str,
        lookback: int = 30,
        entry_threshold: float = 2.0,
        exit_threshold: float = 0.5,
        params: dict[str, Any] | None = None,
    ):
        super().__init__(
            f"mean_reversion_{asset}", params
        )
        self.asset = asset
        self.lookback = lookback
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate long/short/exit signals based on rolling z-score."""
        signals = pd.DataFrame(index=data.index)
        price = data[self.asset]
        z = zscore(price, self.lookback)

        signals["zscore"] = z
        signals["long"] = z < -self.entry_threshold
        signals["short"] = z > self.entry_threshold
        signals["exit"] = abs(z) < self.exit_threshold

        return signals

    def calculate_position_sizes(self, signals: pd.DataFrame) -> dict[str, float]:
        """Return per-asset weight for the latest signal."""
        last = signals.iloc[-1] if len(signals) else pd.Series(dtype=float)
        long = bool(last.get("long", False))
        short = bool(last.get("short", False))
        if long:
            return {self.asset: 1.0}
        if short:
            return {self.asset: -1.0}
        return {self.asset: 0.0}
