"""
Reusable API for parameter grid search with walk-forward validation.
"""

from __future__ import annotations

import copy
import itertools
import sys
from typing import Any, Callable, Dict, List, Mapping

_ALLOWED_METRICS = ("calmar_ratio", "sharpe_ratio", "total_return")


def _to_json_safe(value: Any) -> Any:
    """Recursively convert numpy scalars/arrays to JSON-native Python types."""
    import numpy as _np

    if isinstance(value, _np.generic):
        return _to_json_safe(value.item())
    if isinstance(value, _np.ndarray):
        return [_to_json_safe(v) for v in value.tolist()]
    if isinstance(value, Mapping):
        return {str(k): _to_json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_json_safe(v) for v in value]
    if isinstance(value, bool):
        return bool(value)
    if isinstance(value, int):
        return int(value)
    if isinstance(value, float):
        return float(value)
    return value


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


def _build_strategy(
    strategy: Any, params: Dict[str, Any], strategy_kwargs: Dict[str, Any] | None
) -> Any:
    """Build a fresh strategy instance for a single parameter combo.

    Supports three forms of ``strategy``:

    * a callable factory (not a class): ``factory(params) -> Strategy``. A fresh
      instance is returned for every combo, so callers never see mutated state.
    * a class: instantiated with ``strategy_kwargs`` merged with ``params``.
    * an instance: deep-copied, then ``params`` are applied as attributes, so the
      caller's original object is never mutated.
    """
    kwargs = dict(strategy_kwargs or {})

    # Callable factory (not a class): fresh instance per combo.
    if callable(strategy) and not isinstance(strategy, type):
        try:
            return strategy(params)
        except TypeError:
            return strategy(**{**kwargs, **params})

    # Class: instantiate per combo.
    if isinstance(strategy, type):
        merged = {**kwargs, **params}
        try:
            return strategy(**merged)
        except TypeError:
            pass
        try:
            return strategy(**kwargs)
        except TypeError:
            pass
        try:
            return strategy()
        except TypeError:
            pass

    # Instance: avoid mutating the caller's object.
    try:
        instance = copy.deepcopy(strategy)
    except Exception:
        instance = strategy
    for pk, pv in params.items():
        if hasattr(instance, pk):
            setattr(instance, pk, pv)
    return instance


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
    *,
    strategy_kwargs: Dict[str, Any] | None = None,
    progress_callback: Callable[
        [int, int, Dict[str, Any], Dict[str, Any]], None
    ] | None = None,
    show_progress: bool = False,
) -> List[Dict[str, Any]]:
    """
    Run a parameter grid search with walk-forward validation.

    Args:
        strategy: Strategy class, instance, or callable factory
                  ``factory(combo) -> Strategy`` used to build a fresh instance
                  per parameter combo. When an instance is passed it is
                  deep-copied before parameters are applied, so the caller's
                  object is never mutated.
        data: Prepared market data for backtesting.
        grid: Mapping of parameter name -> list of values (or single value).
        train_period: Training window length (must be > 0).
        test_period: Test window length (must be > 0).
        fee_rate: Transaction fee rate.
        slippage: Slippage rate.
        metric: Ranking metric: calmar_ratio | sharpe_ratio | total_return.
        engine: BacktestEngine instance; if None, a default is created.
        strategy_kwargs: Extra kwargs merged into class construction.
        progress_callback: Optional ``callback(completed, total, current_combo, row)``
            invoked after each combo.
        show_progress: If True and no callback is given, print a one-line
            progress note to stderr after each combo.

    Returns:
        List of result rows (dicts) sorted by rank, with keys for params plus
        oos_mean_return, mean_max_drawdown, oos_is_ratio, oos_periods, rank.
        All values are JSON-serializable native Python types; ``oos_returns`` is
        never included in the returned rows.
    """
    if not isinstance(grid, Mapping) or len(grid) == 0:
        raise ValueError("grid must be a non-empty mapping of param names to value lists")

    empty_keys = [
        k
        for k, v in grid.items()
        if v is None or (isinstance(v, (list, tuple)) and len(v) == 0)
    ]
    if empty_keys:
        raise ValueError(
            f"grid values must be non-empty; empty for: {empty_keys!r}"
        )

    try:
        train_period = int(train_period)
        test_period = int(test_period)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"train_period and test_period must be integers > 0: {exc}"
        ) from exc
    if train_period <= 0:
        raise ValueError(f"train_period must be > 0, got {train_period}")
    if test_period <= 0:
        raise ValueError(f"test_period must be > 0, got {test_period}")

    if metric not in _ALLOWED_METRICS:
        raise ValueError(
            f"Invalid metric: {metric!r}; allowed: {_ALLOWED_METRICS}"
        )

    from backtest.engine import BacktestEngine

    if engine is None:
        engine = BacktestEngine(initial_capital=100_000.0)

    keys = list(grid.keys())
    values = [grid[k] if isinstance(grid[k], (list, tuple)) else [grid[k]] for k in keys]
    combos = list(itertools.product(*values)) if values else []
    total = len(combos)

    rows: List[Dict[str, Any]] = []
    oos_returns_by_row: List[List[float]] = []
    for i, combo in enumerate(combos, 1):
        params = {k: combo[idx] for idx, k in enumerate(keys)}
        strat = _build_strategy(strategy, params, strategy_kwargs)

        try:
            res = engine.walk_forward(
                strat,
                data,
                train_period=train_period,
                test_period=test_period,
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
            }
        )
        row = _to_json_safe(row)

        rows.append(row)
        oos_returns_by_row.append(oos_returns)

        if progress_callback is not None:
            progress_callback(i, total, params, row)
        elif show_progress:
            print(f"[sweep] {i}/{total} combos completed", file=sys.stderr)

    # Rank
    for r, oos_returns in zip(rows, oos_returns_by_row):
        r["_score"] = _compute_score(
            r["oos_mean_return"], r["mean_max_drawdown"], metric, oos_returns
        )
    order = sorted(range(len(rows)), key=lambda idx: rows[idx]["_score"], reverse=True)
    ranked = [rows[idx] for idx in order]
    for i, r in enumerate(ranked, 1):
        r["rank"] = i
        r.pop("_score", None)

    return ranked
