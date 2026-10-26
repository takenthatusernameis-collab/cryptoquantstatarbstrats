"""
Risk management utilities.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


class RiskManager:
    """Risk manager for position sizing and risk controls."""

    def __init__(self, max_weight: float = 0.2):
        self.max_weight = max_weight

    def _scale_row(self, vals: np.ndarray, max_weight: float) -> np.ndarray:
        vals = vals.astype(float).copy()
        total = float(np.abs(vals).sum())
        if total == 0:
            return vals
        max_abs = float(np.abs(vals).max())
        if max_abs / total <= max_weight + 1e-12:
            return vals
        # If capping cannot be satisfied by scaling (e.g. too few assets),
        # zero out positions.
        if len(vals) < 2 or max_weight < 1.0 / len(vals) - 1e-12:
            return np.zeros_like(vals)
        max_mask = np.abs(vals) == max_abs
        # Scale up non-max assets so max becomes at most max_weight of total.
        others_sum = float(np.abs(vals[~max_mask]).sum())
        required_others = max_abs * (1.0 - max_weight) / max_weight
        if others_sum > 0:
            factor = required_others / others_sum
            vals[~max_mask] = vals[~max_mask] * factor
        else:
            cnt = int(np.sum(~max_mask))
            if cnt > 0:
                vals[~max_mask] = np.sign(vals[~max_mask] + 1e-30) * (required_others / cnt)
        return vals

    def max_position_size(
        self,
        positions: pd.DataFrame | dict[str, Any] | np.ndarray,
        capital: float | None = None,
        max_weight: float | None = None,
    ) -> pd.DataFrame | dict[str, Any] | np.ndarray:
        """Scale positions so no single asset exceeds max_weight (by weight)."""
        if max_weight is None:
            max_weight = self.max_weight

        if isinstance(positions, pd.DataFrame):
            scaled = positions.copy().astype(float)
            for idx in scaled.index:
                scaled.loc[idx] = self._scale_row(scaled.loc[idx].values, max_weight)
            return scaled

        if isinstance(positions, dict):
            vals = np.array(list(positions.values()), dtype=float)
            new_vals = self._scale_row(vals, max_weight)
            return {k: float(v) for k, v in zip(positions.keys(), new_vals)}

        arr = np.asarray(positions, dtype=float).copy()
        if arr.ndim == 1:
            arr = self._scale_row(arr, max_weight)
        elif arr.ndim == 2:
            for i in range(arr.shape[0]):
                arr[i] = self._scale_row(arr[i], max_weight)
        return arr

    def stop_loss(
        self,
        prices: pd.Series | np.ndarray,
        entry_prices: pd.Series | np.ndarray,
        threshold: float = 0.1,
    ) -> pd.Series | np.ndarray:
        """Return boolean mask of assets breaching stop-loss threshold."""
        p = pd.Series(prices) if not isinstance(prices, pd.Series) else prices
        e = pd.Series(entry_prices) if not isinstance(entry_prices, pd.Series) else entry_prices
        breach = (e - p) / e.replace(0, np.nan) >= threshold
        return breach.fillna(False).astype(bool)
