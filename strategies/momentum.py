"""
Momentum Strategy
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from strategies.base import Strategy


class MomentumStrategy(Strategy):
    """Momentum strategy on a single asset.

    Long when close > close.shift(n).rolling(m).mean() * (1 + entry_threshold),
    short when below * (1 - entry_threshold), exit on crossover of that mean.
    """

    def __init__(
        self,
        asset: str,
        n: int = 10,
        m: int = 20,
        entry_threshold: float = 0.01,
        params: dict[str, Any] | None = None,
    ):
        super().__init__(f"momentum_{asset}", params)
        self.asset = asset
        self.n = n
        self.m = m
        self.entry_threshold = entry_threshold

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        signals = pd.DataFrame(index=data.index)
        price = data[self.asset]
        shifted = price.shift(self.n)
        ma = shifted.rolling(self.m).mean()
        signals["ma"] = ma
        signals["long"] = price > ma * (1 + self.entry_threshold)
        signals["short"] = price < ma * (1 - self.entry_threshold)
        signals["exit"] = abs(price - ma) / ma < self.entry_threshold * 0.5
        # Explicit asset weights prevent this single-asset strategy from
        # applying its generic long/short flags to every input column.
        signals[self.asset] = (
            signals["long"].astype(float) - signals["short"].astype(float)
        )
        return signals

    def calculate_position_sizes(self, signals: pd.DataFrame) -> dict[str, float]:
        last = signals.iloc[-1] if len(signals) else pd.Series(dtype=float)
        long = bool(last.get("long", False))
        short = bool(last.get("short", False))
        if long and not short:
            return {self.asset: 1.0}
        if short and not long:
            return {self.asset: -1.0}
        return {self.asset: 0.0}
