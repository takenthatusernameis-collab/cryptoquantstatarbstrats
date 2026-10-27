"""
Term Structure / Calendar Spread Strategy

Trades mean-reversion between near-term and long-term implied volatility
(or realized volatility spread). When the spread between far and near
tenors widens beyond a threshold relative to its rolling z-score, take a
spread trade expecting convergence; flatten on reversion.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from strategies.base import Strategy
from utils import zscore


class TermStructureStrategy(Strategy):
    """Mean-reversion strategy on the volatility term-structure spread.

    The strategy computes the spread between a far-tenor IV column and a
    near-tenor IV column (e.g. ``iv_90d`` minus ``iv_30d``). When the
    z-score of that spread exceeds ``entry_threshold`` (widening), a
    spread trade is taken expecting convergence: short the far tenor and
    long the near tenor (expressed as a negative weight on the underlying).
    When the spread collapses below ``-entry_threshold``, the opposite
    trade is taken. Positions are flattened when the z-score reverts
    inside ``exit_threshold``.

    The strategy emits a per-asset weight column named after ``asset`` so
    that auxiliary IV columns in the data are not treated as tradable
    assets by the engine (consistent with ``CrossExchangeArb``).
    """

    def __init__(
        self,
        asset: str = "BTC",
        near_tenor: str = "iv_30d",
        far_tenor: str = "iv_90d",
        lookback: int = 30,
        entry_threshold: float = 2.0,
        exit_threshold: float = 0.5,
        params: dict[str, Any] | None = None,
    ):
        super().__init__(f"term_structure_{asset}", params)
        self.asset = asset
        self.near_tenor = near_tenor
        self.far_tenor = far_tenor
        self.lookback = lookback
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold

    def _resolve_iv_columns(self, data: pd.DataFrame) -> tuple[str, str]:
        """Resolve near/far IV column names, falling back to alternatives."""
        near = self.near_tenor
        far = self.far_tenor

        # Exact matches first.
        if near in data.columns and far in data.columns:
            return near, far

        # Try case-insensitive exact matches.
        lower_map = {str(c).lower(): c for c in data.columns}
        if near.lower() in lower_map and far.lower() in lower_map:
            return lower_map[near.lower()], lower_map[far.lower()]

        # Fall back to any IV-like columns when the requested ones are absent.
        iv_cols = [c for c in data.columns if "iv" in str(c).lower()]
        if len(iv_cols) >= 2:
            if near in iv_cols and far in iv_cols:
                return near, far
            return iv_cols[0], iv_cols[1]

        raise ValueError(
            "TermStructureStrategy requires at least two implied-volatility "
            f"columns (e.g. '{self.near_tenor}' and '{self.far_tenor}'). "
            f"Available columns: {list(data.columns)}"
        )

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate spread, z-score, and directional weight signals."""
        signals = pd.DataFrame(index=data.index)
        near_col, far_col = self._resolve_iv_columns(data)

        near_iv = data[near_col].astype(float)
        far_iv = data[far_col].astype(float)
        spread = far_iv - near_iv

        signals["spread"] = spread
        signals["spread_mean"] = spread.rolling(self.lookback).mean()
        signals["spread_std"] = spread.rolling(self.lookback).std()
        signals["spread_zscore"] = zscore(spread, self.lookback)

        # Directional booleans (named distinctly from the generic "long"/"short"
        # so the engine does not apply them to every data column).
        signals["long_spread"] = signals["spread_zscore"] < -self.entry_threshold
        signals["short_spread"] = signals["spread_zscore"] > self.entry_threshold
        signals["exit"] = signals["spread_zscore"].abs() < self.exit_threshold

        # Per-asset weight column consumed by the engine. The spread trade
        # is dollar-neutral expressed on the underlying: widen -> short,
        # narrow -> long, revert -> flat.
        weight = pd.Series(0.0, index=data.index, dtype=float)
        weight[signals["short_spread"]] = -1.0
        weight[signals["long_spread"]] = 1.0
        signals[self.asset] = weight

        return signals

    def calculate_position_sizes(self, signals: pd.DataFrame) -> dict[str, float]:
        """Return per-asset weight for the latest spread signal."""
        last = signals.iloc[-1] if len(signals) else pd.Series(dtype=float)
        long = bool(last.get("long_spread", False))
        short = bool(last.get("short_spread", False))
        exit_sig = bool(last.get("exit", False))

        if exit_sig and not long and not short:
            return {self.asset: 0.0}
        if long:
            return {self.asset: 1.0}
        if short:
            return {self.asset: -1.0}
        return {self.asset: 0.0}
