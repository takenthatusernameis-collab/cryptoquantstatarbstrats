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

    def max_position_size(
        self,
        positions: pd.DataFrame | dict[str, Any] | np.ndarray,
        capital: float,
        max_weight: float | None = None,
    ) -> pd.DataFrame | dict[str, Any] | np.ndarray:
        """Scale positions so no single asset exceeds max_weight of capital."""
        if max_weight is None:
            max_weight = self.max_weight

        if isinstance(positions, pd.DataFrame):
            scaled = positions.copy()
            for idx in scaled.index:
                row = scaled.loc[idx].copy()
                total = row.abs().sum()
                if total == 0:
                    continue
                # If any position's weight exceeds max_weight, scale so max position is exactly max_weight of total
                max_w = row.abs().max() / total if total > 0 else 0
                if max_w > max_weight + 1e-18:
                    # Scale factor so that max position becomes max_weight of total
                    scale_factor = max_weight * total / row.abs().max()
                    scaled.loc[idx] = row * scale_factor
            return scaled
        elif isinstance(positions, dict):
            scaled = dict(positions)
            total = sum(abs(v) for v in scaled.values())
            if total == 0:
                return scaled
            max_w = max(abs(v) for v in scaled.values()) / total if total > 0 else 0
            if max_w > max_weight + 1e-18:
                scale_factor = max_weight * total / max(abs(v) for v in scaled.values())
                for k in scaled:
                    scaled[k] = scaled[k] * scale_factor
            return scaled
        elif isinstance(positions, np.ndarray):
            scaled = positions.copy().astype(float)
            if scaled.ndim == 1:
                total = np.sum(np.abs(scaled))
                if total == 0:
                    return scaled
                max_w = np.max(np.abs(scaled)) / total if total > 0 else 0
                if max_w > max_weight + 1e-18:
                    scale_factor = max_weight * total / np.max(np.abs(scaled))
                    scaled = scaled * scale_factor
                return scaled
            elif scaled.ndim == 2:
                for i in range(scaled.shape[0]):
                    row = scaled[i].copy()
                    total = np.sum(np.abs(row))
                    if total == 0:
                        continue
                    max_w = np.max(np.abs(row)) / total if total > 0 else 0
                    if max_w > max_weight + 1e-18:
                        scale_factor = max_weight * total / np.max(np.abs(row))
                        scaled[i] = row * scale_factor
                return scaled
            return scaled
        else:
            return positions

    def stop_loss(
        self,
        prices: pd.Series | pd.DataFrame,
        entry_prices: pd.Series | pd.DataFrame,
        threshold: float,
    ) -> pd.Series | pd.DataFrame | np.ndarray:
        """Return a boolean mask of assets breaching the stop."""
        if isinstance(prices, pd.DataFrame) and isinstance(entry_prices, pd.DataFrame):
            # Compute drawdown from entry
            drawdown = (prices - entry_prices) / entry_prices
            # Stop loss triggered if drawdown < -threshold (price dropped more than threshold)
            breach = drawdown < -threshold
            return breach
        elif isinstance(prices, pd.Series) and isinstance(entry_prices, pd.Series):
            drawdown = (prices - entry_prices) / entry_prices
            breach = drawdown < -threshold
            return breach
        elif isinstance(prices, np.ndarray) and isinstance(entry_prices, np.ndarray):
            drawdown = (prices - entry_prices) / entry_prices
            breach = drawdown < -threshold
            return breach
        else:
            # Try to coerce
            try:
                prices_s = pd.Series(prices) if not isinstance(prices, pd.Series) else prices
                entry_s = (
                    pd.Series(entry_prices)
                    if not isinstance(entry_prices, pd.Series)
                    else entry_prices
                )
                drawdown = (prices_s - entry_s) / entry_s
                return drawdown < -threshold
            except Exception:
                return np.array([False])
