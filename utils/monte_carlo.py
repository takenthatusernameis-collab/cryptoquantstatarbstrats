"""
Monte Carlo robustness analysis for strategy equity curves.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from utils.metrics import max_drawdown, sharpe_ratio


def _to_series(x: Any) -> pd.Series:
    if isinstance(x, pd.Series):
        return x.copy()
    if isinstance(x, pd.DataFrame):
        # If single column, take it; else take first
        if x.shape[1] == 1:
            return x.iloc[:, 0].copy()
        # Try common names
        for name in ["equity_curve", "equity", "value"]:
            if name in x.columns:
                return x[name].copy()
        return x.iloc[:, 0].copy()
    arr = np.asarray(x)
    return pd.Series(arr)


def bootstrap_trade_returns(
    trade_returns: Any,
    n_simulations: int = 1000,
    method: str = "bootstrap",
    seed: int | None = None,
) -> dict[str, Any]:
    """Bootstrap or shuffle trade returns to simulate alternative sequences.

    Args:
        trade_returns: Iterable of per-trade returns.
        n_simulations: Number of Monte Carlo simulations.
        method: 'bootstrap' (resample with replacement) or 'shuffle'
            (permutation of the same trades).
        seed: Random seed for reproducibility.

    Returns:
        Dictionary with distribution statistics for final equity, max drawdown,
        and Sharpe ratio.
    """
    rng = np.random.default_rng(seed)

    if isinstance(trade_returns, pd.Series):
        trades = trade_returns.dropna().to_numpy()
    else:
        trades = np.asarray(trade_returns)
        trades = trades[~np.isnan(trades)]

    if len(trades) == 0:
        return {
            "n_simulations": int(n_simulations),
            "final_equity": {
                "mean": 0.0,
                "std": 0.0,
                "p5": 0.0,
                "p25": 0.0,
                "p50": 0.0,
                "p75": 0.0,
                "p95": 0.0,
            },
            "max_drawdown": {
                "mean": 0.0,
                "std": 0.0,
                "p5": 0.0,
                "p25": 0.0,
                "p50": 0.0,
                "p75": 0.0,
                "p95": 0.0,
            },
            "sharpe_ratio": {
                "mean": 0.0,
                "std": 0.0,
                "p5": 0.0,
                "p25": 0.0,
                "p50": 0.0,
                "p75": 0.0,
                "p95": 0.0,
            },
        }

    method = method.lower()
    final_equities: list[float] = []
    max_drawdowns: list[float] = []
    sharpes: list[float] = []

    initial_equity = 1.0
    for _ in range(int(n_simulations)):
        if method == "shuffle":
            sim_trades = rng.permutation(trades)
        else:  # bootstrap
            sim_trades = rng.choice(trades, size=len(trades), replace=True)

        equity_curve = initial_equity * np.cumprod(1.0 + sim_trades)
        final_equities.append(float(equity_curve[-1]))
        mdd = max_drawdown(equity_curve)
        max_drawdowns.append(float(abs(mdd)))
        sharpes.append(float(sharpe_ratio(sim_trades)))

    def _stats(arr: list[float]) -> dict[str, float]:
        a = np.asarray(arr)
        return {
            "mean": float(np.mean(a)),
            "std": float(np.std(a, ddof=0)),
            "p5": float(np.percentile(a, 5)),
            "p25": float(np.percentile(a, 25)),
            "p50": float(np.percentile(a, 50)),
            "p75": float(np.percentile(a, 75)),
            "p95": float(np.percentile(a, 95)),
        }

    return {
        "n_simulations": int(n_simulations),
        "method": method,
        "final_equity": _stats(final_equities),
        "max_drawdown": _stats(max_drawdowns),
        "sharpe_ratio": _stats(sharpes),
        "final_equities": final_equities,
        "max_drawdowns": max_drawdowns,
        "sharpes": sharpes,
    }


def monte_carlo_analysis(
    returns: Any = None,
    equity_curve: Any = None,
    trade_returns: Any = None,
    n_simulations: int = 1000,
    method: str = "bootstrap",
    seed: int | None = None,
    periods_per_year: int = 252,
) -> dict[str, Any]:
    """Run Monte Carlo analysis on returns/equity/trades.

    If trade_returns are provided, they are bootstrapped/shuffled directly.
    Otherwise, if equity_curve is provided, infer trade/period returns from it.
    Otherwise use the provided returns series.
    """
    if trade_returns is not None:
        return bootstrap_trade_returns(
            trade_returns, n_simulations=n_simulations, method=method, seed=seed
        )

    if equity_curve is not None:
        eq = _to_series(equity_curve).dropna()
        if len(eq) == 0:
            return bootstrap_trade_returns(
                [], n_simulations=n_simulations, method=method, seed=seed
            )
        # Compute period returns from equity curve
        period_rets = eq.pct_change().dropna()
        if len(period_rets) == 0:
            return bootstrap_trade_returns(
                [], n_simulations=n_simulations, method=method, seed=seed
            )
        return bootstrap_trade_returns(
            period_rets, n_simulations=n_simulations, method=method, seed=seed
        )

    if returns is not None:
        r = _to_series(returns).dropna()
        if len(r) == 0:
            return bootstrap_trade_returns(
                [], n_simulations=n_simulations, method=method, seed=seed
            )
        return bootstrap_trade_returns(r, n_simulations=n_simulations, method=method, seed=seed)

    return bootstrap_trade_returns([], n_simulations=n_simulations, method=method, seed=seed)
