"""
Volatility Surface Strategy

Trades on implied-volatility surface signals based on IV percentile rank
relative to its rolling regime.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from strategies.base import Strategy


class VolatilitySurfaceStrategy(Strategy):
    """Strategy trading on implied volatility surface/regime signals.

    Long when IV is depressed relative to its rolling regime (e.g., low percentile rank),
    short when IV is elevated, and exits on reversion to mean.
    """

    def __init__(
        self,
        asset: str = "BTC",
        iv_column: str | None = None,
        lookback: int = 30,
        entry_percentile: float = 0.2,
        exit_percentile: float = 0.5,
        short_percentile: float = 0.8,
        params: dict[str, Any] | None = None,
    ):
        super().__init__(f"volatility_surface_{asset}", params)
        self.asset = asset
        self.iv_column = iv_column
        self.lookback = lookback
        self.entry_percentile = entry_percentile
        self.exit_percentile = exit_percentile
        self.short_percentile = short_percentile

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate long/short/exit signals based on IV percentile rank."""
        signals = pd.DataFrame(index=data.index)

        # Determine IV column
        iv_col = self.iv_column
        if iv_col is None:
            for candidate in ["iv", "implied_vol", "implied_volatility", "IV"]:
                if candidate in data.columns:
                    iv_col = candidate
                    break
        if iv_col is None:
            # Try to find any column with 'iv' in name
            for col in data.columns:
                if "iv" in str(col).lower():
                    iv_col = col
                    break

        if iv_col is not None and iv_col in data.columns:
            iv = data[iv_col].astype(float)
        elif self.asset in data.columns:
            # Fallback: use realized volatility proxy if no IV data
            price = data[self.asset].astype(float)
            returns = price.pct_change()
            iv = returns.rolling(self.lookback).std() * np.sqrt(252)
        else:
            iv = pd.Series(0.0, index=data.index)

        signals["iv"] = iv

        # Calculate rolling percentile rank
        def percentile_rank(series: pd.Series) -> float:
            if len(series) == 0:
                return 0.5
            current = series.iloc[-1]
            rank = (series < current).sum() / len(series)
            return float(rank)

        iv_percentile = iv.rolling(self.lookback).apply(percentile_rank, raw=False)
        signals["iv_percentile"] = iv_percentile
        signals["iv_mean"] = iv.rolling(self.lookback).mean()

        # Long when IV is depressed (low percentile rank)
        signals["long"] = iv_percentile < self.entry_percentile
        # Short when IV is elevated (high percentile rank)
        signals["short"] = iv_percentile > self.short_percentile
        # Exit on reversion toward mean
        signals["exit"] = iv_percentile >= self.exit_percentile

        return signals

    def calculate_position_sizes(self, signals: pd.DataFrame) -> dict[str, float]:
        """Calculate position sizes based on latest signal."""
        last = signals.iloc[-1] if len(signals) else pd.Series(dtype=float)
        long = bool(last.get("long", False))
        short = bool(last.get("short", False))
        exit_sig = bool(last.get("exit", False))

        # If exiting/reverting, flatten
        if exit_sig and not long and not short:
            return {self.asset: 0.0}

        if long and not short:
            return {self.asset: 1.0}
        if short and not long:
            return {self.asset: -1.0}
        return {self.asset: 0.0}
