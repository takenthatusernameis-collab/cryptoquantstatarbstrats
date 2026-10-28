"""
Reusable API for parameter grid search with walk-forward validation.
"""

from __future__ import annotations

import itertools
from typing import Any, Dict, List, Mapping


def _compute_score(
    oos_mean_return: float, mean_max_drawdown: float, metric: str, oos_returns: List[float]
) -> float:
    if metric == "sharpe_ratio":
        std = 0.0
        try:
            import numpy as _np

            arr = _np.array(oos_returns or [], dtype=float)
            std = float(_np.std(arr, ddof=1)) if arr.size > 1 else 0.0
        except Exception:
            std = 0.0
        if std == 0.0:
            return float(oos_mean_return)
        return float(oos_mean_return) / float(std)
    elif metric == "total_return":
        return float(oos_mean_return)
    elif metric == "calmar_ratio":
        if mean_max_drawdown:
            return float(oos_mean_return) / abs(float(mean_max_drawdown))
        return float(oos_mean_return)
    else:
        raise ValueError(f"Invalid metric: {metric!r}")


def run_parameter_sweep(
    strategy: Any,
    data: Any,
    grid: Mapping[str, Any],
    train_period: int,
    test_period: int,
    fee_rate: float = 0.0,
    slippage: float = 0.0,
    metric: str = "calmar_ratio",
    engine: Any = None,
) -> List[Dict[str, Any]]:
    """
    Run a parameter grid search with walk-forward validation.

    Args:
        strategy: Strategy class/factory or instance to use; the caller is responsible
                  for instantiating strategies with parameter values if needed.
                  This API expects the caller to build strategy instances per combo
                  (see examples). Alternatively, if strategy is callable that takes
                  params, it can be used - but the function signature is generic.
        data: Prepared market data for backtesting.
        grid: Mapping of parameter name -> list of values (or single value).
        train_period: Training window length.
        test_period: Test window length.
        fee_rate: Transaction fee rate.
        slippage: Slippage rate.
        metric: Ranking metric: calmar_ratio | sharpe_ratio | total_return.
        engine: BacktestEngine instance; if None, a default is created.

    Returns:
        List of result rows (dicts) sorted by rank, with keys for params plus
        oos_mean_return, mean_max_drawdown, oos_is_ratio, oos_periods, rank.
    """
    if not isinstance(grid, dict) or not grid:
        raise ValueError("grid must be a non-empty dict mapping param names to value lists")

    if metric not in ("calmar_ratio", "sharpe_ratio", "total_return"):
        raise ValueError(f"Invalid metric: {metric!r}")

    from backtest.engine import BacktestEngine

    if engine is None:
        engine = BacktestEngine(initial_capital=100_000.0)

    keys = list(grid.keys())
    values = [grid[k] if isinstance(grid[k], list) else [grid[k]] for k in keys]
    combos = list(itertools.product(*values)) if values else []

    rows: List[Dict[str, Any]] = []
    for combo in combos:
        params = {k: combo[i] for i, k in enumerate(keys)}
        # Build strategy instance for this combo
        strat = strategy
        # If strategy is a class with params, try to instantiate
        if isinstance(strategy, type):
            try:
                strat = strategy(**params)
            except Exception:
                try:
                    # Fallback: try without params if constructor doesn't accept
                    strat = strategy()
                    for pk, pv in params.items():
                        if hasattr(strat, pk):
                            setattr(strat, pk, pv)
                except Exception:
                    strat = strategy
        else:
            # If it's an instance or callable, try to set attributes
            try:
                for pk, pv in params.items():
                    if hasattr(strat, pk):
                        setattr(strat, pk, pv)
            except Exception:
                pass

        try:
            res = engine.walk_forward(
                strat,
                data,
                train_period=int(train_period),
                test_period=int(test_period),
                fee_rate=float(fee_rate),
                slippage=float(slippage),
            )
        except Exception:
            res = {}

        results_list = res.get("results", []) or []
        oos_returns = [float((r or {}).get("total_return", 0.0)) for r in results_list]
        oos_mean = float(res.get("oos_mean_return", res.get("mean_return", 0.0)) or 0.0)
        mdds = [float((r or {}).get("max_drawdown", 0.0)) for r in results_list]
        mean_mdd = float(sum(mdds) / len(mdds)) if mdds else 0.0
        oos_is = float(res.get("oos_is_ratio", 0.0) or 0.0)

        row: Dict[str, Any] = dict(params)
        row.update(
            {
                "oos_mean_return": oos_mean,
                "mean_max_drawdown": mean_mdd,
                "oos_is_ratio": oos_is,
                "oos_periods": len(results_list),
                "oos_returns": oos_returns,
            }
        )
        rows.append(row)

    # Rank
    for r in rows:
        r["_score"] = _compute_score(
            r["oos_mean_return"], r["mean_max_drawdown"], metric, r.get("oos_returns", [])
        )
    rows.sort(key=lambda r: r["_score"], reverse=True)
    for i, r in enumerate(rows, 1):
        r["rank"] = i
        r.pop("_score", None)
        r.pop("oos_returns", None)

    return rows
