"""
Cross-Exchange Arbitrage Strategy
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from strategies.base import Strategy


class CrossExchangeArb(Strategy):
    """Trade a relative-price spread between one asset on two venues.

    Positions persist until the spread converges to the exit band or a
    sufficiently large opposite-side spread appears. Weights are explicit
    and gross-normalized, and the entry threshold is never reduced by fees.
    """

    def __init__(
        self,
        exchange_a: str,
        exchange_b: str,
        entry_threshold: float = 0.01,
        exit_threshold: float = 0.002,
        fee_rate: float = 0.001,
        params: dict[str, Any] | None = None,
    ):
        if exchange_a == exchange_b:
            raise ValueError("The two exchange price columns must be distinct.")
        if entry_threshold <= 0 or exit_threshold < 0 or exit_threshold >= entry_threshold:
            raise ValueError(
                "Thresholds must satisfy entry_threshold > exit_threshold >= 0."
            )
        if fee_rate < 0:
            raise ValueError("fee_rate must be non-negative.")
        super().__init__(f"cross_exchange_{exchange_a}_{exchange_b}", params)
        self.exchange_a = exchange_a
        self.exchange_b = exchange_b
        self.entry_threshold = float(entry_threshold)
        self.exit_threshold = float(exit_threshold)
        self.fee_rate = float(fee_rate)

    def _spread(self, data: pd.DataFrame) -> pd.Series:
        """Relative spread between the two exchange price feeds."""
        denominator = data[self.exchange_b].replace(0.0, float("nan"))
        return (data[self.exchange_a] - data[self.exchange_b]) / denominator

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate persistent, explicit per-venue target weights."""
        missing = [
            name for name in (self.exchange_a, self.exchange_b)
            if name not in data.columns
        ]
        if missing:
            raise ValueError(f"Exchange price columns missing from data: {missing}")

        spread = self._spread(data)
        # A two-leg round trip has four fills (open/close on both venues).
        # Require a gross spread larger than the estimated round-trip fees.
        required_entry = max(self.entry_threshold, 4.0 * self.fee_rate)

        state = 0
        position = np.zeros(len(data), dtype=float)
        for i, value in enumerate(spread.to_numpy(dtype=float)):
            if not np.isfinite(value):
                state = 0
            elif state == 1:
                if value >= required_entry:
                    state = -1
                elif value >= -self.exit_threshold:
                    state = 0
            elif state == -1:
                if value <= -required_entry:
                    state = 1
                elif value <= self.exit_threshold:
                    state = 0
            elif value <= -required_entry:
                state = 1
            elif value >= required_entry:
                state = -1
            position[i] = state

        signals = pd.DataFrame(index=data.index)
        signals["spread"] = spread
        signals["long_a"] = position > 0
        signals["short_a"] = position < 0
        signals["exit"] = position == 0
        signals[self.exchange_a] = position * 0.5
        signals[self.exchange_b] = -position * 0.5
        return signals

    def calculate_position_sizes(self, signals: pd.DataFrame) -> dict[str, float]:
        """Return per-venue weights for the latest signal."""
        if signals.empty:
            return {self.exchange_a: 0.0, self.exchange_b: 0.0}
        last = signals.iloc[-1]
        return {
            self.exchange_a: float(last.get(self.exchange_a, 0.0)),
            self.exchange_b: float(last.get(self.exchange_b, 0.0)),
        }
