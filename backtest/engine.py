"""
Backtesting framework for statistical arbitrage strategies
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from strategies.base import Strategy


class BacktestEngine:
    """Backtesting engine for trading strategies."""

    def __init__(self, initial_capital: float = 100000.0):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions: dict[str, float] = {}
        self.trades: list[dict[str, Any]] = []
        self.equity_curve: list[float] = []

    def run(self, strategy: Strategy, data: pd.DataFrame) -> dict[str, Any]:
        """Run backtest for a given strategy."""
        signals = strategy.generate_signals(data)
        returns = data.pct_change().fillna(0.0)

        # Determine per-asset weights from signals.
        weights = pd.DataFrame(0.0, index=data.index, columns=data.columns)

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

        portfolio_returns = (weights * returns).sum(axis=1)
        cumulative_returns = (1.0 + portfolio_returns).cumprod()

        total_return = float(cumulative_returns.iloc[-1] - 1.0)
        mean_ret = float(portfolio_returns.mean())
        std_ret = float(portfolio_returns.std())
        sharpe_ratio = (mean_ret / std_ret * np.sqrt(252)) if std_ret > 0 else 0.0
        running_max = cumulative_returns.cummax()
        drawdown = cumulative_returns / running_max - 1.0
        max_drawdown = float(drawdown.min())

        self.equity_curve = [float(x) for x in cumulative_returns]
        self.positions = weights.iloc[-1].to_dict() if len(weights) else {}

        return {
            "total_return": total_return,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown,
            "equity_curve": cumulative_returns,
            "weights": weights,
        }
