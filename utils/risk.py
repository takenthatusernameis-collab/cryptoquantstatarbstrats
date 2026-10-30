"""
Risk management utilities.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


class DrawdownCircuitBreaker:
    """Circuit breaker that forces full de-risking when trailing drawdown breaches threshold.

    The engine calls ``breached(current_drawdown)`` per bar. When True, the engine
    zeroes all subsequent weights. The breaker stays tripped once triggered.
    """

    def __init__(self, max_drawdown: float = -0.15):
        if not isinstance(max_drawdown, (int, float)):
            raise ValueError("max_drawdown must be a number")
        self.max_drawdown = float(max_drawdown)
        self.tripped = False

    def breached(self, current_drawdown: float) -> bool:
        """Return True when the trailing drawdown breaches the threshold.

        ``current_drawdown`` is expected as a negative fraction (e.g. -0.15).
        """
        try:
            dd = float(current_drawdown)
        except (TypeError, ValueError):
            return False
        if not np.isfinite(dd):
            return False
        if dd <= self.max_drawdown:
            self.tripped = True
            return True
        return False


class RiskManager:
    """Risk manager for position sizing and risk controls."""

    def __init__(self, max_weight: float = 0.2, stop_loss_threshold: float | None = None):
        self.max_weight = max_weight
        self.stop_loss_threshold = stop_loss_threshold

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

    def apply_stop_loss(
        self,
        positions: pd.DataFrame | dict[str, Any] | np.ndarray,
        prices: pd.Series | np.ndarray,
        entry_prices: pd.Series | np.ndarray,
        threshold: float | None = None,
    ) -> pd.DataFrame | dict[str, Any] | np.ndarray:
        """Close positions that breach stop-loss."""
        if threshold is None and self.stop_loss_threshold is not None:
            threshold = self.stop_loss_threshold
        elif threshold is None:
            threshold = 0.1

        breach = self.stop_loss(prices, entry_prices, threshold)

        if isinstance(positions, pd.DataFrame):
            result = positions.copy().astype(float)
            if isinstance(breach, pd.Series):
                breach_series = breach
            else:
                breach_arr = np.asarray(breach)
                breach_series = pd.Series(breach_arr, index=result.columns)
            for col in result.columns:
                if col in breach_series.index and bool(breach_series[col]):
                    result[col] = 0.0
            return result

        if isinstance(positions, dict):
            result = dict(positions)
            if isinstance(breach, pd.Series):
                breach_series = breach
            else:
                breach_arr = np.asarray(breach)
                keys = list(positions.keys())
                breach_series = pd.Series(breach_arr, index=keys[: len(breach_arr)])
            for k in result:
                if k in breach_series.index and bool(breach_series[k]):
                    result[k] = 0.0
            return result

        arr = np.asarray(positions, dtype=float).copy()
        breach_arr = np.asarray(breach)
        if arr.ndim == 1:
            if len(breach_arr) == len(arr):
                arr[breach_arr] = 0.0
        elif arr.ndim == 2:
            if len(breach_arr) == arr.shape[1]:
                for i in range(arr.shape[0]):
                    arr[i, breach_arr] = 0.0
        return arr

    def position_limit(
        self,
        positions: pd.DataFrame | dict[str, Any] | np.ndarray,
        max_positions: int = 10,
    ) -> pd.DataFrame | dict[str, Any] | np.ndarray:
        """Limit number of concurrent positions to max_positions (by absolute weight)."""
        if isinstance(positions, pd.DataFrame):
            result = positions.copy().astype(float)
            for idx in result.index:
                row = result.loc[idx].values.copy()
                abs_vals = np.abs(row)
                active = np.where(abs_vals > 1e-18)[0]
                if len(active) > max_positions:
                    # Keep top N by absolute weight
                    sorted_idx = active[np.argsort(abs_vals[active])[::-1]]
                    to_close = sorted_idx[max_positions:]
                    for i in to_close:
                        row[i] = 0.0
                    result.loc[idx] = row
            return result

        if isinstance(positions, dict):
            result = dict(positions)
            abs_vals = {k: abs(v) for k, v in result.items()}
            if sum(1 for v in abs_vals.values() if v > 1e-18) > max_positions:
                sorted_items = sorted(abs_vals.items(), key=lambda x: x[1], reverse=True)
                to_keep = set([k for k, _ in sorted_items[:max_positions]])
                for k in result:
                    if k not in to_keep and abs_vals.get(k, 0) > 1e-18:
                        result[k] = 0.0
            return result

        arr = np.asarray(positions, dtype=float).copy()
        if arr.ndim == 1:
            abs_vals = np.abs(arr)
            active = np.where(abs_vals > 1e-18)[0]
            if len(active) > max_positions:
                sorted_idx = active[np.argsort(abs_vals[active])[::-1]]
                to_close = sorted_idx[max_positions:]
                arr[to_close] = 0.0
        elif arr.ndim == 2:
            for i in range(arr.shape[0]):
                arr[i] = self.position_limit(arr[i], max_positions)
        return arr


    def drawdown_control(
        self,
        positions: pd.DataFrame | dict[str, Any] | np.ndarray,
        current_drawdown: float,
        max_drawdown: float = 0.2,
    ) -> pd.DataFrame | dict[str, Any] | np.ndarray:
        """Scale or reduce positions if current drawdown exceeds threshold."""
        if current_drawdown >= max_drawdown:
            # Liquidate positions if drawdown exceeds max
            if isinstance(positions, pd.DataFrame):
                return positions.copy().astype(float) * 0.0
            if isinstance(positions, dict):
                return {k: 0.0 for k in positions}
            arr = np.asarray(positions, dtype=float).copy()
            return arr * 0.0
        elif current_drawdown > max_drawdown * 0.5:
            # Scale down positions proportionally
            scale = 1.0 - (current_drawdown - max_drawdown * 0.5) / (max_drawdown * 0.5)
            scale = max(0.0, min(1.0, scale))
            if isinstance(positions, pd.DataFrame):
                return positions.copy().astype(float) * scale
            if isinstance(positions, dict):
                return {k: float(v) * scale for k, v in positions.items()}
            arr = np.asarray(positions, dtype=float).copy()
            return arr * scale
        return positions
