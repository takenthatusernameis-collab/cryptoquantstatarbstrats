"""
Reusable API for parameter grid search with walk-forward validation.
"""

from __future__ import annotations

import copy
import itertools
import sys
from concurrent.futures import ProcessPoolExecutor
from typing import Any, Callable, Dict, List, Mapping

import pandas as pd

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


def _evaluate_combo(
    payload: dict[str, Any],
) -> tuple[dict[str, Any], list[float]]:
    """Module-level worker: evaluate one parameter combo in a subprocess.

    Everything needed to run a walk-forward (strategy factory, params, data,
    engine config) is passed in as a plain dict so the function is picklable
    for ``ProcessPoolExecutor``. Returns the JSON-safe result row and the
    underlying OOS returns so callers can rank and checkpoint without
    re-running the sweep.
    """

    strategy = payload["strategy"]
    params = payload["params"]
    strategy_kwargs = payload.get("strategy_kwargs")
    data = payload["data"]
    train_period = int(payload["train_period"])
    test_period = int(payload["test_period"])
    fee_rate = float(payload["fee_rate"])
    slippage = float(payload["slippage"])
    mode = payload["mode"]
    anchor = payload.get("anchor")
    n_splits = payload.get("n_splits")

    strat = _build_strategy(strategy, params, strategy_kwargs)
    try:
        res = engine_walk_forward(
            strat,
            data,
            train_period=train_period,
            test_period=test_period,
            fee_rate=fee_rate,
            slippage=slippage,
            mode=mode,
            anchor=anchor,
            n_splits=n_splits,
        )
    except Exception:
        res = {}

    results_list = res.get("results", []) or []
    if n_splits is not None:
        results_list = results_list[:n_splits]
    oos_returns = [float((r or {}).get("total_return", 0.0)) for r in results_list]
    oos_mean = float(res.get("oos_mean_return", res.get("mean_return", 0.0)) or 0.0)
    mdds = [float((r or {}).get("max_drawdown", 0.0)) for r in results_list]
    mean_mdd = float(sum(mdds) / len(mdds)) if mdds else 0.0
    oos_is = float(res.get("oos_is_ratio", 0.0) or 0.0)

    row: dict[str, Any] = dict(params)
    row.update(
        {
            "oos_mean_return": oos_mean,
            "mean_max_drawdown": mean_mdd,
            "oos_is_ratio": oos_is,
            "oos_periods": len(results_list),
        }
    )
    return _to_json_safe(row), oos_returns


def engine_walk_forward(
    strategy: Any,
    data: Any,
    *,
    train_period: int,
    test_period: int,
    fee_rate: float,
    slippage: float,
    mode: str,
    anchor: Any,
    n_splits: int | None,
) -> dict[str, Any]:
    """Run a walk-forward on a freshly constructed engine (subprocess-safe)."""
    from backtest.engine import BacktestEngine

    engine = BacktestEngine(initial_capital=100_000.0)
    try:
        return engine.walk_forward(
            strategy,
            data,
            train_period=train_period,
            test_period=test_period,
            fee_rate=float(fee_rate),
            slippage=float(slippage),
            mode=mode,
            anchor=anchor,
            n_splits=n_splits,
        )
    except Exception:
        return {}


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
    mode: str = "rolling",
    n_splits: int | None = None,
    anchor: Any = None,
    replay_best: bool = False,
    parallel: bool = False,
    max_workers: int | None = None,
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

    Keyword-only args:
        parallel: When True and the grid has more than one combo, parameter
            combos are evaluated with a bounded ``ProcessPoolExecutor``
            (default ``min(4, os.cpu_count())`` workers, overridable via
            ``max_workers``). Submission order is deterministic, so the
            returned rows are reproducible across runs. Falls back to serial
            execution if the pool cannot start.
        max_workers: Optional cap on parallel workers.
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

    if mode not in ("rolling", "expanding"):
        raise ValueError(f"Invalid mode: {mode!r}; allowed: ('rolling', 'expanding')")
    if n_splits is not None:
        try:
            n_splits = int(n_splits)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"n_splits must be an integer > 0: {exc}") from exc
        if n_splits <= 0:
            raise ValueError(f"n_splits must be > 0, got {n_splits}")

    from backtest.engine import BacktestEngine, _resolve_anchor_index

    if anchor is not None:
        # Validate anchor up front so invalid values surface before any combo
        # is evaluated (walk_forward swallows per-combo errors).
        _resolve_anchor_index(anchor, data)
    if not isinstance(replay_best, bool):
        raise ValueError(f"replay_best must be a bool, got {type(replay_best).__name__}")

    if engine is None:
        engine = BacktestEngine(initial_capital=100_000.0)

    keys = list(grid.keys())
    values = [grid[k] if isinstance(grid[k], (list, tuple)) else [grid[k]] for k in keys]
    combos = list(itertools.product(*values)) if values else []
    total = len(combos)

    # Build the per-combo payload once. Order is deterministic (itertools.product
    # order over the grid keys), so results can be reassembled in submission
    # order whether run serially or in parallel.
    payloads: list[dict[str, Any]] = []
    for combo in combos:
        params = {k: combo[idx] for idx, k in enumerate(keys)}
        payloads.append(
            {
                "strategy": strategy,
                "params": params,
                "strategy_kwargs": strategy_kwargs,
                "data": data,
                "train_period": train_period,
                "test_period": test_period,
                "fee_rate": float(fee_rate),
                "slippage": float(slippage),
                "mode": mode,
                "anchor": anchor,
                "n_splits": n_splits,
            }
        )

    rows: List[Dict[str, Any]] = []
    oos_returns_by_row: List[List[float]] = []

    use_parallel = bool(parallel) and total > 1
    if use_parallel:
        import os

        workers = max_workers if (max_workers and max_workers > 0) else min(
            4, os.cpu_count() or 1
        )
        workers = int(workers)
        try:
            with ProcessPoolExecutor(max_workers=workers) as pool:
                # Submit in deterministic order; results are collected in the
                # same order so ranking is reproducible across runs.
                futures = [pool.submit(_evaluate_combo, p) for p in payloads]
                for i, fut in enumerate(futures, 1):
                    try:
                        row, oos_returns = fut.result()
                    except Exception:
                        row, oos_returns = {
                            **{k: payloads[i - 1]["params"][k] for k in keys},
                            "oos_mean_return": 0.0,
                            "mean_max_drawdown": 0.0,
                            "oos_is_ratio": 0.0,
                            "oos_periods": 0,
                        }, []
                    rows.append(row)
                    oos_returns_by_row.append(oos_returns)
                    if progress_callback is not None:
                        progress_callback(i, total, payloads[i - 1]["params"], row)
                    elif show_progress:
                        print(f"[sweep] {i}/{total} combos completed", file=sys.stderr)
        except Exception:
            # Fall back to serial execution if the pool cannot start (e.g. the
            # environment forbids forking). Determinism is preserved.
            use_parallel = False

    if not use_parallel:
        for i, payload in enumerate(payloads, 1):
            params = payload["params"]
            try:
                row, oos_returns = _evaluate_combo(payload)
            except Exception:
                row, oos_returns = {
                    **params,
                    "oos_mean_return": 0.0,
                    "mean_max_drawdown": 0.0,
                    "oos_is_ratio": 0.0,
                    "oos_periods": 0,
                }, []
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

    if replay_best and ranked:
        top = ranked[0]
        replay_params = {k: top.get(k) for k in keys}
        replay_strat = _build_strategy(strategy, replay_params, strategy_kwargs)
        run_result = engine.run(
            replay_strat, data, fee_rate=float(fee_rate), slippage=float(slippage)
        )
        equity_curve = run_result.get("equity_curve")
        if isinstance(equity_curve, pd.Series):
            equity_curve = equity_curve.to_numpy()
        elif not isinstance(equity_curve, (list, tuple)):
            equity_curve = [] if equity_curve is None else [equity_curve]
        final_equity = None
        if len(equity_curve):
            try:
                final_equity = float(engine.initial_capital) * float(equity_curve[-1])
            except (TypeError, ValueError, IndexError):
                final_equity = None
        replay_block = {
            "params": _to_json_safe(replay_params),
            "total_return": _to_json_safe(run_result.get("total_return")),
            "sharpe_ratio": _to_json_safe(run_result.get("sharpe_ratio")),
            "max_drawdown": _to_json_safe(run_result.get("max_drawdown")),
            "calmar_ratio": _to_json_safe(run_result.get("calmar_ratio")),
            "final_equity": _to_json_safe(final_equity),
        }
        top["replay"] = replay_block

    return ranked
