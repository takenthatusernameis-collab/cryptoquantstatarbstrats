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
    block_size: int | None = None,
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
        block_size: Optional positive integer. When set > 1 the bootstrap draws
            contiguous blocks (block bootstrap) instead of single draws, which
            preserves short-range serial dependence in the return series.
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
    block_size = int(block_size) if block_size and block_size > 0 else 1
    use_block = block_size > 1 and len(trades) > block_size
    if use_block:
        # Block bootstrap: resample contiguous blocks to preserve short-range
        # serial dependence in the return series. Each simulation draws
        # ceil(n/block_size) blocks and concatenates them to length n.
        n_blocks = int(np.ceil(len(trades) / float(block_size)))
        blocks = np.array(
            [trades[i : i + block_size] for i in range(0, len(trades) - block_size + 1, block_size)]
        )
        if len(blocks) == 0:
            blocks = trades.reshape(-1, 1)

    for _ in range(int(n_simulations)):
        if use_block:
            block_indices = rng.choice(len(blocks), size=n_blocks, replace=True)
            sim_trades = np.concatenate([blocks[i] for i in block_indices])[: len(trades)]
        elif method == "shuffle":
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
        "block_size": int(block_size) if (block_size and block_size > 0) else 1,
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


def permutation_test_distinguishability(
    trade_returns: Any,
    n_permutations: int = 2000,
    seed: int | None = None,
) -> dict[str, Any]:
    """Permutation test for whether a return series is distinguishable from zero.

    Under the null hypothesis the observed sequence carries no exploitable
    signal, so any permutation of the same returns is equally plausible. We
    compare the observed mean return against the distribution of permuted
    means and report a two-sided p-value. A small p-value rejects the null and
    supports that the observed mean is not a draw from a zero-signal process.

    Returns:
        Dictionary with observed mean, permutation mean/std, two-sided
        p-value, and the full permutation distribution of mean returns.
    """
    rng = np.random.default_rng(seed)
    if isinstance(trade_returns, pd.Series):
        trades = trade_returns.dropna().to_numpy(dtype=float)
    else:
        trades = np.asarray(trade_returns, dtype=float).ravel()
        trades = trades[~np.isnan(trades)]

    if len(trades) == 0:
        return {
            "observed_mean": 0.0,
            "permutation_mean": 0.0,
            "permutation_std": 0.0,
            "p_value": 1.0,
            "n_permutations": 0,
            "n_observations": 0,
            "note": "Empty input; cannot distinguish from zero.",
        }

    observed_mean = float(np.mean(trades))
    perm_means = np.empty(int(n_permutations), dtype=float)
    for i in range(int(n_permutations)):
        perm = rng.permutation(trades)
        perm_means[i] = float(np.mean(perm))

    perm_mean = float(np.mean(perm_means))
    perm_std = float(np.std(perm_means, ddof=0))
    # Two-sided p-value: fraction of permuted means at least as extreme as the
    # observed mean in either direction, plus one pseudo-count for stability.
    extreme = float(np.sum(np.abs(perm_means) >= abs(observed_mean)))
    p_value = float((extreme + 1.0) / (float(n_permutations) + 1.0))

    return {
        "observed_mean": observed_mean,
        "permutation_mean": perm_mean,
        "permutation_std": perm_std,
        "p_value": p_value,
        "n_permutations": int(n_permutations),
        "n_observations": int(len(trades)),
        "note": (
            "Two-sided permutation p-value for the observed mean return against "
            "the null of no exploitable signal. Lower p-value is more "
            "distinguishable from zero."
        ),
    }


def tail_risk_metrics(
    trade_returns: Any,
    *,
    confidence_levels: tuple[float, ...] = (0.95, 0.99, 0.999),
    initial_equity: float = 1.0,
) -> dict[str, Any]:
    """Compute publication-grade tail risk metrics from a return series.

    For each confidence level reports VaR, CVaR (expected shortfall), and
    CDaR (conditional drawdown at risk). All risk figures are reported as
    positive magnitudes for readability; the underlying returns are negative
    in loss terms.

    Args:
        trade_returns: Iterable of per-period returns.
        confidence_levels: Confidence levels to evaluate (e.g. 0.95, 0.99, 0.999).
        initial_equity: Starting equity for drawdown-based metrics.

    Returns:
        Dictionary keyed by confidence level with VaR/CVaR/CDaR, plus the
        underlying return series summary.
    """
    if isinstance(trade_returns, pd.Series):
        trades = trade_returns.dropna().to_numpy(dtype=float)
    else:
        trades = np.asarray(trade_returns, dtype=float).ravel()
        trades = trades[~np.isnan(trades)]

    if trades.size == 0:
        return {
            "n_observations": 0,
            "note": "Empty input; tail metrics undefined.",
            "by_confidence": {},
        }

    equity = float(initial_equity) * np.cumprod(1.0 + trades)
    running_max = np.maximum.accumulate(equity)
    drawdown = equity / running_max - 1.0

    by_confidence: dict[str, Any] = {}
    for conf in confidence_levels:
        conf = float(conf)
        if not (0.0 < conf < 1.0):
            continue
        alpha = 1.0 - conf
        var = float(np.percentile(trades, alpha * 100.0))
        tail = trades[trades <= var]
        cvar = float(np.mean(tail)) if tail.size > 0 else var
        dd_var = float(np.percentile(drawdown, alpha * 100.0))
        dd_tail = drawdown[drawdown <= dd_var]
        cdar = float(np.mean(dd_tail)) if dd_tail.size > 0 else dd_var
        by_confidence[f"{int(conf * 100)}"] = {
            "confidence": conf,
            "var": abs(var),
            "cvar": abs(cvar),
            "cdar": abs(cdar),
            "n_tail": int(tail.size),
        }

    return {
        "n_observations": int(trades.size),
        "mean_return": float(np.mean(trades)),
        "std_return": float(np.std(trades, ddof=0)) if trades.size > 1 else 0.0,
        "min_return": float(np.min(trades)),
        "max_return": float(np.max(trades)),
        "final_equity": float(equity[-1]),
        "max_drawdown": abs(float(np.min(drawdown))),
        "by_confidence": by_confidence,
        "note": (
            "VaR/CVaR/CDaR reported as positive magnitudes. CVaR is the mean of "
            "returns at or below VaR; CDaR is the mean of drawdowns at or below "
            "the drawdown VaR threshold."
        ),
    }


def monte_carlo_analysis(
    returns: Any = None,
    equity_curve: Any = None,
    trade_returns: Any = None,
    n_simulations: int = 1000,
    method: str = "bootstrap",
    seed: int | None = None,
    periods_per_year: int = 252,
    ruin_threshold: float = 0.5,
    block_size: int | None = None,
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
            block_size=block_size,
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
                block_size=block_size,
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
                block_size=block_size,
                compute_risk_of_ruin=compute_risk_of_ruin,
            )
        return bootstrap_trade_returns(
            period_rets,
            n_simulations=n_simulations,
            method=method,
            seed=seed,
            ruin_threshold=ruin_threshold,
            block_size=block_size,
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
                block_size=block_size,
                compute_risk_of_ruin=compute_risk_of_ruin,
            )
        return bootstrap_trade_returns(
            r,
            n_simulations=n_simulations,
            method=method,
            seed=seed,
            ruin_threshold=ruin_threshold,
            block_size=block_size,
            compute_risk_of_ruin=compute_risk_of_ruin,
        )

    return bootstrap_trade_returns(
        [],
        n_simulations=n_simulations,
        method=method,
        seed=seed,
        ruin_threshold=ruin_threshold,
        block_size=block_size,
        compute_risk_of_ruin=compute_risk_of_ruin,
    )
