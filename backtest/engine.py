"""
Backtesting framework for statistical arbitrage strategies
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from strategies.base import Strategy
from utils.metrics import cvar, sharpe_ratio, sortino_ratio, var


class BacktestEngine:
    """Backtesting engine for trading strategies."""

    def __init__(self, initial_capital: float = 100000.0):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions: dict[str, float] = {}
        self.trades: list[dict[str, Any]] = []
        self.equity_curve: list[float] = []

    def run(
        self,
        strategy: Strategy,
        data: pd.DataFrame,
        fee_rate: float = 0.0,
        slippage: float = 0.0,
        risk_manager: Any = None,
    ) -> dict[str, Any]:
        """Run backtest for a given strategy."""
        signals = strategy.generate_signals(data)
        returns = data.pct_change().fillna(0.0)

        # Determine per-asset weights from signals.
        weights = pd.DataFrame(0.0, index=data.index, columns=data.columns)

        # Explicit per-asset weight columns (e.g. cross-exchange legs).
        weight_cols = [c for c in data.columns if c in signals.columns]
        if weight_cols:
            for asset in weight_cols:
                weights[asset] = signals[asset].reindex(data.index).fillna(0.0)

        if "long" in signals.columns and "short" in signals.columns:
            long_mask = signals["long"].fillna(False).reindex(
                data.index, fill_value=False
            )
            short_mask = signals["short"].fillna(False).reindex(
                data.index, fill_value=False
            )
            for asset in data.columns:
                weights.loc[long_mask, asset] = 1.0
                weights.loc[short_mask, asset] = -1.0

        if "exit" in signals.columns:
            exit_mask = signals["exit"].fillna(False).reindex(
                data.index, fill_value=False
            )
            weights.loc[exit_mask, :] = 0.0

        # Equal-weight across active positions to stay fully invested.
        active = weights.abs().sum(axis=1).replace(0.0, np.nan)
        weights = weights.div(active, axis=0).fillna(0.0)

        # Apply risk management if provided
        if risk_manager is not None:
            try:
                weights = risk_manager.max_position_size(weights, self.capital)
            except Exception:
                pass

        portfolio_returns = (weights * returns).sum(axis=1)

        # Apply transaction costs: fees and slippage on turnover
        turnover = weights.diff().abs().sum(axis=1).fillna(0.0)
        cost = turnover * (fee_rate + slippage)
        portfolio_returns = portfolio_returns - cost

        cumulative_returns = (1.0 + portfolio_returns).cumprod()

        total_return = float(cumulative_returns.iloc[-1] - 1.0)
        sharpe = sharpe_ratio(portfolio_returns)
        running_max = cumulative_returns.cummax()
        drawdown = cumulative_returns / running_max - 1.0
        max_drawdown = float(drawdown.min())

        # Compute max drawdown duration
        max_dd_duration = 0
        if len(drawdown) > 0:
            in_drawdown = False
            dd_start = 0
            for i in range(len(drawdown)):
                if drawdown.iloc[i] < 0:
                    if not in_drawdown:
                        in_drawdown = True
                        dd_start = i
                else:
                    if in_drawdown:
                        dd_duration = i - dd_start
                        if dd_duration > max_dd_duration:
                            max_dd_duration = dd_duration
                        in_drawdown = False
            if in_drawdown:
                dd_duration = len(drawdown) - dd_start
                if dd_duration > max_dd_duration:
                    max_dd_duration = dd_duration

        # Compute Calmar ratio
        if max_drawdown < 0:
            calmar_ratio = total_return / abs(max_drawdown)
        else:
            calmar_ratio = 0.0

        # Compute advanced risk metrics
        sortino = sortino_ratio(portfolio_returns)
        var_95 = var(portfolio_returns, confidence=0.95)
        cvar_95 = cvar(portfolio_returns, confidence=0.95)

        self.equity_curve = [float(x) for x in cumulative_returns]
        self.positions = weights.iloc[-1].to_dict() if len(weights) else {}

        result = {
            "total_return": total_return,
            "sharpe_ratio": sharpe,
            "max_drawdown": max_drawdown,
            "max_drawdown_duration": int(max_dd_duration),
            "calmar_ratio": float(calmar_ratio),
            "sortino_ratio": float(sortino),
            "var": float(var_95),
            "cvar": float(cvar_95),
            "equity_curve": cumulative_returns,
            "weights": weights,
        }
        return result

    def run_with_benchmark(
        self,
        strategy: Strategy,
        data: pd.DataFrame,
        fee_rate: float = 0.0,
        slippage: float = 0.0,
        risk_manager: Any = None,
    ) -> dict[str, Any]:
        """Run backtest and include an equal-weighted buy-and-hold benchmark."""
        result = self.run(
            strategy, data, fee_rate=fee_rate, slippage=slippage, risk_manager=risk_manager
        )
        returns = data.pct_change().fillna(0.0)
        n = data.shape[1]
        if n == 0:
            bench_returns = pd.Series(0.0, index=data.index)
        else:
            bench_weights = pd.DataFrame(
                1.0 / n, index=data.index, columns=data.columns
            )
            bench_returns = (bench_weights * returns).sum(axis=1)
            turnover = bench_weights.diff().abs().sum(axis=1).fillna(0.0)
            # Initial entry turnover
            turnover.iloc[0] = float(bench_weights.iloc[0].abs().sum())
            cost = turnover * (fee_rate + slippage)
            bench_returns = bench_returns - cost

        bench_equity = (1.0 + bench_returns).cumprod()
        bench_total_return = float(bench_equity.iloc[-1] - 1.0) if len(bench_equity) else 0.0

        result["benchmark_total_return"] = bench_total_return
        result["benchmark_equity_curve"] = bench_equity
        return result

    def walk_forward(
        self,
        strategy: Strategy,
        data: pd.DataFrame,
        train_period: int = 252,
        test_period: int = 63,
        fee_rate: float = 0.0,
        slippage: float = 0.0,
    ) -> dict[str, Any]:
        """Perform walk-forward validation."""
        results = []
        total = len(data)
        i = 0
        while i + train_period + test_period <= total:
            train_data = data.iloc[i : i + train_period]
            test_data = data.iloc[i + train_period : i + train_period + test_period]
            # Train the strategy if it has a fit method
            if hasattr(strategy, "fit"):
                try:
                    strategy.fit(train_data)
                except Exception:
                    pass
            # Run on test data
            result = self.run(strategy, test_data, fee_rate=fee_rate, slippage=slippage)
            results.append(result)
            i += test_period

        if not results:
            # If not enough data for walk-forward, run on all data
            result = self.run(strategy, data, fee_rate=fee_rate, slippage=slippage)
            return {
                "returns": [result["total_return"]],
                "results": [result],
            }

        returns_list = [r["total_return"] for r in results]
        return {
            "returns": returns_list,
            "results": results,
        }
