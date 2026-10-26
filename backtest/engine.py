"""
Backtesting framework for statistical arbitrage strategies
"""

import pandas as pd
import numpy as np
from typing import Dict, List
from strategies.base import Strategy


class BacktestEngine:
    """Backtesting engine for trading strategies."""
    
    def __init__(self, initial_capital: float = 100000):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions = {}
        self.trades = []
        self.equity_curve = []
        
    def run(self, strategy: Strategy, data: pd.DataFrame) -> Dict:
        """Run backtest for a given strategy."""
        signals = strategy.generate_signals(data)
        # Simple backtest logic
        returns = data.pct_change()
        portfolio_returns = returns.mean(axis=1) * 0.1  # Simple allocation
        cumulative_returns = (1 + portfolio_returns).cumprod()
        
        total_return = cumulative_returns.iloc[-1] - 1
        sharpe_ratio = portfolio_returns.mean() / portfolio_returns.std() * np.sqrt(252)
        max_drawdown = (cumulative_returns / cumulative_returns.cummax() - 1).min()
        
        return {
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'equity_curve': cumulative_returns
        }
