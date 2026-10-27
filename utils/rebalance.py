"""
Periodic rebalancing utilities.
"""

from __future__ import annotations

from typing import Any, Callable

import pandas as pd


def generate_rebalance_dates(
    index: pd.DatetimeIndex | pd.Index,
    freq: str = "1W",
    offset: Any = None,
) -> pd.DatetimeIndex:
    """Generate rebalance dates from a price index."""
    if not isinstance(index, pd.DatetimeIndex):
        try:
            idx = pd.DatetimeIndex(index)
        except Exception:
            raise ValueError("index must be datetime-like")
    else:
        idx = index

    # Normalize deprecated lowercase weekly frequency to uppercase (pandas 2.x)
    if isinstance(freq, str):
        freq = freq.replace("w", "W")

    if len(idx) == 0:
        return pd.DatetimeIndex([])

    try:
        # Group by frequency to get period starts
        grouped = idx.to_series().groupby(pd.Grouper(freq=freq))
        rebalance_points = []
        for name, group in grouped:
            if len(group) == 0:
                continue
            rebalance_points.append(group.index[0])
        rebalance_points = sorted(set(rebalance_points))
        rebalance_points = [d for d in rebalance_points if d >= idx[0] and d <= idx[-1]]
        if len(rebalance_points) == 0:
            return pd.DatetimeIndex([idx[0]])
        if rebalance_points[0] != idx[0]:
            rebalance_points = [idx[0]] + [d for d in rebalance_points if d != idx[0]]
        return pd.DatetimeIndex(rebalance_points)
    except Exception:
        return pd.DatetimeIndex([idx[0]])


def create_rebalanced_weights(
    weights_func: Callable[..., Any] | pd.DataFrame | pd.Series,
    data: pd.DataFrame,
    freq: str = "1W",
    offset: Any = None,
) -> pd.DataFrame:
    """Create a weights DataFrame with periodic rebalancing (forward-filled)."""
    if isinstance(data, pd.DataFrame):
        idx = data.index
    else:
        idx = data.index if hasattr(data, "index") else None

    if isinstance(weights_func, pd.DataFrame):
        w = weights_func.copy()
        w = w.reindex(index=idx).ffill().fillna(0.0)
        if isinstance(data, pd.DataFrame) and hasattr(w, "columns"):
            w = w.reindex(columns=data.columns, fill_value=0.0)
        # Ensure weights only change on rebalance dates by snapping
        reb_dates = generate_rebalance_dates(idx, freq=freq, offset=offset)
        if len(reb_dates) > 0:
            result = w.copy()
            # For each rebalance date, take the weight value at that date and hold
            # Build by setting values only at rebalance points and ffill
            out = pd.DataFrame(0.0, index=idx, columns=result.columns)
            # Get target weights at rebalance dates
            reb_set = set(reb_dates)
            current = None
            for i, dt in enumerate(idx):
                if dt in reb_set or current is None:
                    # take current row as target
                    current = result.iloc[i].copy()
                out.iloc[i] = current.values
            out = out.ffill().fillna(0.0)
            return out
        return w.ffill().fillna(0.0)

    if isinstance(weights_func, pd.Series):
        w = weights_func.to_frame().T
        return create_rebalanced_weights(w, data, freq=freq, offset=offset)

    # Callable case - recompute at each rebalance
    reb_dates = generate_rebalance_dates(idx, freq=freq, offset=offset)
    if len(reb_dates) == 0:
        reb_dates = pd.DatetimeIndex([idx[0]]) if len(idx) > 0 else pd.DatetimeIndex([])

    if isinstance(data, pd.DataFrame):
        out = pd.DataFrame(0.0, index=idx, columns=data.columns)
    else:
        out = pd.DataFrame(0.0, index=idx)

    reb_set = set(reb_dates)
    current = None
    for i, dt in enumerate(idx):
        if dt in reb_set or current is None:
            try:
                try:
                    target = weights_func(data, reb_dates)
                except TypeError:
                    try:
                        target = weights_func(data.loc[:dt])
                    except Exception:
                        target = weights_func(data)
            except Exception:
                target = current
            if target is None:
                target_df = current
            elif isinstance(target, pd.Series):
                target_df = target.to_frame().T
            elif isinstance(target, pd.DataFrame):
                target_df = target.copy()
            else:
                target_df = current
            if target_df is not None and isinstance(data, pd.DataFrame):
                target_df = target_df.reindex(columns=data.columns, fill_value=0.0)
            current = target_df
        if current is not None and isinstance(current, pd.DataFrame):
            if len(current) == 1:
                out.iloc[i] = current.iloc[0].values
            else:
                try:
                    # take matching row or last
                    if dt in current.index:
                        out.iloc[i] = current.loc[dt].values
                    else:
                        out.iloc[i] = current.iloc[-1].values
                except Exception:
                    out.iloc[i] = current.iloc[-1].values
        elif current is not None and isinstance(current, pd.Series):
            out.iloc[i] = current.values
    out = out.ffill().fillna(0.0)
    return out


# Aliases
rebalance_weights = create_rebalanced_weights
generate_rebalance_schedule = generate_rebalance_dates
