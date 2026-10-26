"""
Cross-Exchange Arbitrage Strategy
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from strategies.base import Strategy


class CrossExchangeArb(Strategy):
    """Cross-exchange arbitrage on a single asset quoted on two exchanges.

    Signals when the absolute spread between the two price feeds exceeds the
    entry threshold minus estimated round-trip transaction fees, and exits
    when the spread reverts below the exit threshold.
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
        super().__init__(
            f"cross_exchange_{exchange_a}_{exchange_b}", params
        )
        self.exchange_a = exchange_a
        self.exchange_b = exchange_b
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold
        self.fee_rate = fee_rate

    def _spread(self, data: pd.DataFrame) -> pd.Series:
        """Relative spread between the two exchange price feeds."""
        return (data[self.exchange_a] - data[self.exchange_b]) / data[
            self.exchange_b
        ].replace(0.0, float("nan"))

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate per-exchange weight signals from the spread."""
        signals = pd.DataFrame(index=data.index)
        spread = self._spread(data)
        signals["spread"] = spread

        net_entry = self.entry_threshold - 2 * self.fee_rate
        net_exit = self.exit_threshold - 2 * self.fee_rate

        # Long the cheaper exchange, short the expensive one.
        long_a = spread < -net_entry
        short_a = spread > net_entry

        signals["long_a"] = long_a
        signals["short_a"] = short_a
        signals["exit"] = abs(spread) < net_exit

        # Per-exchange weights (consumed by the engine when columns match).
        signals[self.exchange_a] = 0.0
        signals[self.exchange_b] = 0.0
        signals.loc[long_a, self.exchange_a] = 1.0
        signals.loc[long_a, self.exchange_b] = -1.0
        signals.loc[short_a, self.exchange_a] = -1.0
        signals.loc[short_a, self.exchange_b] = 1.0
        signals.loc[signals["exit"], [self.exchange_a, self.exchange_b]] = 0.0

        return signals

    def calculate_position_sizes(self, signals: pd.DataFrame) -> dict[str, float]:
        """Return per-exchange weights for the latest signal."""
        last = signals.iloc[-1] if len(signals) else pd.Series(dtype=float)
        long_a = bool(last.get("long_a", False))
        short_a = bool(last.get("short_a", False))
        if long_a:
            return {self.exchange_a: 1.0, self.exchange_b: -1.0}
        if short_a:
            return {self.exchange_a: -1.0, self.exchange_b: 1.0}
        return {self.exchange_a: 0.0, self.exchange_b: 0.0}
