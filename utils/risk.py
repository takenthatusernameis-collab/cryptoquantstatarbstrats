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
        capital: float | None = None,
        max_weight: float | None = None,
    ) -> pd.DataFrame | dict[str, Any] | np.ndarray:
        """Scale positions so no single asset exceeds max_weight."""
        if max_weight is None:
            max_weight = self.max_weight

        if isinstance(positions, pd.DataFrame):
            scaled = positions.copy()
            for idx in scaled.index:
                row = scaled.loc[idx].copy()
                total = row.abs().sum()
                if total == 0:
                    continue
                max_abs = row.abs().max()
                max_w_rel = max_abs / total if total > 0 else 0
                if capital is not None and max_abs > max_weight * capital + 1e-18:
                    scale_factor = (max_weight * capital) / max_abs if max_abs > 0 else 1.0
                    scaled.loc[idx] = row * scale_factor
                    # Recheck
                    r = scaled.loc[idx]
                    t = r.abs().sum()
                    if t > 0 and r.abs().max()/t > max_weight + 1e-10:
                        sf = max_weight / (r.abs().max()/t)
                        scaled.loc[idx] = r * sf
                    continue
                if max_w_rel > max_weight + 1e-18:
                    # Force the ratio to be exactly max_weight
                    result = row.copy().astype(float)
                    # Make all positions equal magnitude
                    n = len(result)
                    # Set each to magnitude such that max/total = (mag)/(n*mag)=1/n if equal; but if n!=1/n? no
                    # Or directly set values so ratio is satisfied
                    vals = result.values.astype(float)
                    # Try to construct: let the max be M', others adjusted so M'/sum = max_weight
                    # Scale down largest and scale up others to keep sum same? no wait sum changes
                    M_new = max_weight * total  # target max value
                    # Cap max to M_new, add excess to others proportionally
                    max_mask = np.abs(vals) == np.max(np.abs(vals))
                    excess = np.sum(np.abs(vals[max_mask])) - M_new * np.sum(max_mask)
                    for j in range(len(vals)):
                        if max_mask[j]:
                            vals[j] = np.sign(vals[j]) * M_new if vals[j] != 0 else 0
                    others_mask = ~max_mask
                    if np.any(others_mask):
                        others_total_abs = np.sum(np.abs(vals[others_mask]))
                        if others_total_abs == 0:
                            # distribute excess equally to others
                            for j in range(len(vals)):
                                if others_mask[j]:
                                    vals[j] = np.sign(row.values[j]) * (excess / np.sum(others_mask)) if excess > 0 else 0
                        else:
                            for j in range(len(vals)):
                                if others_mask[j] and vals[j] != 0:
                                    vals[j] = vals[j] + np.sign(vals[j]) * excess * (abs(vals[j]) / others_total_abs)
                    total_new = np.sum(np.abs(vals))
                    max_new = np.max(np.abs(vals))
                    if total_new > 0 and max_new / total_new > max_weight + 1e-18:
                        vals = vals * (max_weight / (max_new / total_new))
                    scaled.loc[idx] = vals
                    continue
            return scaled
