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


def risk_of_ruin(
    trade_returns: Any,
    ruin_threshold: float = 0.5,
    initial_equity: float = 1.0,
    n_simulations: int = 10000,
    method: str = "bootstrap",
    seed: int | None = None,
) -> float:
    """Estimate probability of ruin (equity falling below ruin_threshold).

    Returns probability (float between 0 and 1).
    """
    rng = np.random.default_rng(seed)

    if isinstance(trade_returns, pd.Series):
        trades = trade_returns.dropna().to_numpy()
    else:
        trades = np.asarray(trade_returns)
        trades = trades[~np.isnan(trades)]

    if len(trades) == 0:
        return 0.0

    method = method.lower()
    ruin_count = 0
    for _ in range(int(n_simulations)):
        if method == "shuffle":
            sim_trades = rng.permutation(trades)
        else:
            sim_trades = rng.choice(trades, size=len(trades), replace=True)

        equity_curve = initial_equity * np.cumprod(1.0 + sim_trades)
        if (
            np.min(equity_curve) < initial_equity * ruin_threshold
            or equity_curve[-1] < initial_equity * ruin_threshold
        ):
            ruin_count += 1

    return float(ruin_count / float(n_simulations))


def bootstrap_trade_returns(
    trade_returns: Any,
    n_simulations: int = 1000,
    method: str = "bootstrap",
    seed: int | None = None,
    ruin_threshold: float = 0.5,
    compute_risk_of_ruin: bool = True,
) -> dict[str, Any]:
    """Bootstrap or shuffle trade returns to simulate alternative sequences.

    Args:
        trade_returns: Iterable of per-trade returns.
        n_simulations: Number of Monte Carlo simulations.
        method: 'bootstrap' (resample with replacement) or 'shuffle'
            (permutation of the same trades).
        seed: Random seed for reproducibility.
        ruin_threshold: Threshold for risk-of-ruin calculation (fraction of initial equity).
        compute_risk_of_ruin: Whether to compute risk of ruin.

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
            "method": method.lower() if isinstance(method, str) else method,
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
                "ci95": [0.0, 0.0],
                "ci99": [0.0, 0.0],
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
            "risk_of_ruin": 0.0,
            "risk_of_ruin_threshold": float(ruin_threshold),
        }

    method = method.lower()
    final_equities: list[float] = []
    max_drawdowns: list[float] = []
    sharpes: list[float] = []
    ruin_count = 0

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
        if compute_risk_of_ruin:
            if (
                np.min(equity_curve) < initial_equity * ruin_threshold
                or equity_curve[-1] < initial_equity * ruin_threshold
            ):
                ruin_count += 1

    def _stats(arr: list[float]) -> dict[str, Any]:
        a = np.asarray(arr)
        stats = {
            "mean": float(np.mean(a)),
            "std": float(np.std(a, ddof=0)),
            "p5": float(np.percentile(a, 5)),
            "p25": float(np.percentile(a, 25)),
            "p50": float(np.percentile(a, 50)),
            "p75": float(np.percentile(a, 75)),
            "p95": float(np.percentile(a, 95)),
        }
        return stats

    mdd_stats = _stats(max_drawdowns)
    # Add percentile CI for drawdowns
    a_mdd = np.asarray(max_drawdowns)
    mdd_stats["ci95"] = [float(np.percentile(a_mdd, 2.5)), float(np.percentile(a_mdd, 97.5))]
    mdd_stats["ci99"] = [float(np.percentile(a_mdd, 0.5)), float(np.percentile(a_mdd, 99.5))]

    result = {
        "n_simulations": int(n_simulations),
        "method": method,
        "final_equity": _stats(final_equities),
        "max_drawdown": mdd_stats,
        "sharpe_ratio": _stats(sharpes),
        "final_equities": final_equities,
        "max_drawdowns": max_drawdowns,
        "sharpes": sharpes,
    }
    if compute_risk_of_ruin:
        result["risk_of_ruin"] = (
            float(ruin_count / float(n_simulations)) if n_simulations > 0 else 0.0
        )
        result["risk_of_ruin_threshold"] = float(ruin_threshold)
    else:
        result["risk_of_ruin"] = 0.0
        result["risk_of_ruin_threshold"] = float(ruin_threshold)
    return result


def monte_carlo_analysis(
    returns: Any = None,
    equity_curve: Any = None,
    trade_returns: Any = None,
    n_simulations: int = 1000,
    method: str = "bootstrap",
    seed: int | None = None,
    periods_per_year: int = 252,
    ruin_threshold: float = 0.5,
    compute_risk_of_ruin: bool = True,
) -> dict[str, Any]:
    """Run Monte Carlo analysis on returns/equity/trades.

    If trade_returns are provided, they are bootstrapped/shuffled directly.
    Otherwise, if equity_curve is provided, infer trade/period returns from it.
    Otherwise use the provided returns series.
    """
    if trade_returns is not None:
        return bootstrap_trade_returns(
            trade_returns,
            n_simulations=n_simulations,
            method=method,
            seed=seed,
            ruin_threshold=ruin_threshold,
            compute_risk_of_ruin=compute_risk_of_ruin,
        )

    if equity_curve is not None:
        eq = _to_series(equity_curve).dropna()
        if len(eq) == 0:
            return bootstrap_trade_returns(
                [],
                n_simulations=n_simulations,
                method=method,
                seed=seed,
                ruin_threshold=ruin_threshold,
                compute_risk_of_ruin=compute_risk_of_ruin,
            )
        # Compute period returns from equity curve
        period_rets = eq.pct_change().dropna()
        if len(period_rets) == 0:
            return bootstrap_trade_returns(
                [],
                n_simulations=n_simulations,
                method=method,
                seed=seed,
                ruin_threshold=ruin_threshold,
                compute_risk_of_ruin=compute_risk_of_ruin,
            )
        return bootstrap_trade_returns(
            period_rets,
            n_simulations=n_simulations,
            method=method,
            seed=seed,
            ruin_threshold=ruin_threshold,
            compute_risk_of_ruin=compute_risk_of_ruin,
        )

    if returns is not None:
        r = _to_series(returns).dropna()
        if len(r) == 0:
            return bootstrap_trade_returns(
                [],
                n_simulations=n_simulations,
                method=method,
                seed=seed,
                ruin_threshold=ruin_threshold,
                compute_risk_of_ruin=compute_risk_of_ruin,
            )
        return bootstrap_trade_returns(
            r,
            n_simulations=n_simulations,
            method=method,
            seed=seed,
            ruin_threshold=ruin_threshold,
            compute_risk_of_ruin=compute_risk_of_ruin,
        )

    return bootstrap_trade_returns(
        [],
        n_simulations=n_simulations,
        method=method,
        seed=seed,
        ruin_threshold=ruin_threshold,
        compute_risk_of_ruin=compute_risk_of_ruin,
    )
