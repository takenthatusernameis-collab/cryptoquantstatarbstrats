"""
Mean Reversion Strategy using rolling z-score or Bollinger Bands
"""

from __future__ import annotations

from typing import Any, Callable

import pandas as pd

from strategies.base import Strategy
from utils import zscore


class MeanReversionStrategy(Strategy):
    """Mean-reversion strategy on a single asset's price.

    Longs when the price drops below the lower Bollinger Band (z-score < -entry)
    and shorts when it rises above the upper band (z-score > entry). Exits when
    the z-score reverts toward the mean.

    Optional position sizing can be applied via the ``sizer`` parameter, which
    receives the base weight (-1, 0, or 1), the current equity, the latest
    price, and the latest realized volatility, and returns a dollar
    allocation. When omitted, the strategy behaves exactly as before
    (weight-based, fully invested).
    """

    def __init__(
        self,
        asset: str,
        lookback: int = 30,
        entry_threshold: float = 2.0,
        exit_threshold: float = 0.5,
        params: dict[str, Any] | None = None,
        sizer: Callable[[float, float, float, float], float] | None = None,
    ):
        super().__init__(
            f"mean_reversion_{asset}", params
        )
        self.asset = asset
        self.lookback = lookback
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold
        self.sizer = sizer

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
        """Return per-asset weight for the latest signal.

        When a ``sizer`` is configured, the returned value is a dollar
        allocation computed from the base weight, equity, and the latest
        price/volatility context. Without a sizer, the base weight
        (``-1``, ``0``, or ``1``) is returned unchanged for backward
        compatibility.
        """
        last = signals.iloc[-1] if len(signals) else pd.Series(dtype=float)
        long = bool(last.get("long", False))
        short = bool(last.get("short", False))
        if long:
            base = 1.0
        elif short:
            base = -1.0
        else:
            base = 0.0

        if self.sizer is None or base == 0.0:
            return {self.asset: base}

        equity = float(self.params.get("equity", 100000.0))
        price = float(last.get("price", 0.0))
        realized_vol = float(last.get("realized_vol", 0.0))
        try:
            allocation = float(self.sizer(base, equity, price, realized_vol))
        except Exception:
            allocation = base
        return {self.asset: allocation}
