"""
Causal rolling-hedge-ratio pairs trading strategy.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from strategies.base import PairStrategy


class CointegrationPairsStrategy(PairStrategy):
    """Pairs strategy using a rolling OLS hedge ratio and spread z-score.

    The hedge ratio at each timestamp uses only observations in the trailing
    lookback window. Explicit per-asset weights are emitted so the backtest
    engine can preserve the opposing legs instead of applying one generic
    long/short flag to both assets.
    """

    def __init__(
        self,
        pair: tuple[str, str],
        lookback: int = 60,
        entry_threshold: float = 2.0,
        exit_threshold: float = 0.5,
        params: dict[str, Any] | None = None,
    ):
        if len(pair) != 2 or pair[0] == pair[1]:
            raise ValueError("pair must contain two distinct asset names.")
        if lookback < 2:
            raise ValueError("lookback must be at least 2.")
        if entry_threshold <= 0 or exit_threshold < 0 or exit_threshold >= entry_threshold:
            raise ValueError(
                "Thresholds must satisfy entry_threshold > exit_threshold >= 0."
            )
        super().__init__(f"coint_pairs_{pair[0]}_{pair[1]}", pair, params)
        self.lookback = int(lookback)
        self.entry_threshold = float(entry_threshold)
        self.exit_threshold = float(exit_threshold)
        self.hedge_ratio_series = pd.Series(dtype=float)

    def test_cointegration(
        self, price1: pd.Series, price2: pd.Series
    ) -> tuple[float, float]:
        """Test cointegration on the explicitly supplied sample only."""
        from statsmodels.tsa.stattools import coint

        aligned = pd.concat([price1, price2], axis=1).dropna()
        if len(aligned) < 3:
            raise ValueError("At least three aligned observations are required.")
        score, pvalue, _ = coint(aligned.iloc[:, 0], aligned.iloc[:, 1])
        return float(score), float(pvalue)

    def calculate_spread(self, price1: pd.Series, price2: pd.Series) -> pd.Series:
        """Return a spread built from a causal rolling hedge ratio."""
        aligned = pd.concat([price1, price2], axis=1)
        aligned.columns = ["price1", "price2"]
        price1_aligned = aligned["price1"].astype(float)
        price2_aligned = aligned["price2"].astype(float)

        rolling_cov = price2_aligned.rolling(
            self.lookback, min_periods=self.lookback
        ).cov(price1_aligned)
        rolling_var = price2_aligned.rolling(
            self.lookback, min_periods=self.lookback
        ).var()
        hedge_ratio = rolling_cov.div(rolling_var.where(rolling_var > 0))
        hedge_ratio = hedge_ratio.replace([np.inf, -np.inf], np.nan)
        # This long/short pairs implementation is intended for positively
        # related legs; a non-positive hedge ratio would create same-direction
        # exposures rather than a spread hedge.
        hedge_ratio = hedge_ratio.where(hedge_ratio > 0)
        self.hedge_ratio_series = hedge_ratio
        valid = hedge_ratio.dropna()
        self.hedge_ratio = float(valid.iloc[-1]) if not valid.empty else 1.0

        return price1_aligned - hedge_ratio * price2_aligned

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate stateful spread signals and opposing, gross-normalized legs."""
        asset1, asset2 = self.pair
        missing = [asset for asset in self.pair if asset not in data.columns]
        if missing:
            raise ValueError(f"Pair assets missing from data: {missing}")

        price1 = data[asset1].astype(float)
        price2 = data[asset2].astype(float)
        spread = self.calculate_spread(price1, price2)
        spread_mean = spread.rolling(self.lookback, min_periods=self.lookback).mean()
        spread_std = spread.rolling(self.lookback, min_periods=self.lookback).std()
        zscore = spread.sub(spread_mean).div(spread_std.where(spread_std > 0))

        # Maintain the position between entry and exit thresholds; a new
        # opposite entry flips the spread position.
        state = 0
        position = np.zeros(len(data), dtype=float)
        z_values = zscore.to_numpy(dtype=float)
        for i, z_value in enumerate(z_values):
            if not np.isfinite(z_value):
                state = 0
            elif state == 1:
                if z_value >= self.entry_threshold:
                    state = -1
                elif z_value >= -self.exit_threshold:
                    state = 0
            elif state == -1:
                if z_value <= -self.entry_threshold:
                    state = 1
                elif z_value <= self.exit_threshold:
                    state = 0
            elif z_value <= -self.entry_threshold:
                state = 1
            elif z_value >= self.entry_threshold:
                state = -1
            position[i] = state

        signals = pd.DataFrame(index=data.index)
        signals["spread"] = spread
        signals["zscore"] = zscore
        signals["long"] = position > 0
        signals["short"] = position < 0
        signals["exit"] = position == 0

        # Backtest weights represent dollar exposure. Scale each leg by its
        # market value so the absolute weights sum to one before engine
        # normalization, preserving the rolling hedge ratio's relative sizing.
        beta = self.hedge_ratio_series.reindex(data.index)
        gross_value = price1.abs() + beta.abs() * price2.abs()
        valid = (
            (position != 0)
            & beta.notna().to_numpy()
            & np.isfinite(gross_value.to_numpy())
            & (gross_value.to_numpy() > 0)
        )
        leg1 = pd.Series(0.0, index=data.index, dtype=float)
        leg2 = pd.Series(0.0, index=data.index, dtype=float)
        direction = pd.Series(position, index=data.index)
        leg1.loc[valid] = (
            direction.loc[valid] * price1.loc[valid] / gross_value.loc[valid]
        )
        leg2.loc[valid] = (
            -direction.loc[valid] * beta.loc[valid] * price2.loc[valid]
            / gross_value.loc[valid]
        )
        signals[asset1] = leg1
        signals[asset2] = leg2
        return signals

    def calculate_position_sizes(self, signals: pd.DataFrame) -> dict[str, float]:
        """Return the latest explicit per-asset weights."""
        asset1, asset2 = self.pair
        if signals.empty:
            return {asset1: 0.0, asset2: 0.0}
        last = signals.iloc[-1]
        return {
            asset1: float(last.get(asset1, 0.0)),
            asset2: float(last.get(asset2, 0.0)),
        }
