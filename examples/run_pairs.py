#!/usr/bin/env python3
"""Synthetic demonstration of the pairs API; not evidence of a trading edge."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backtest.engine import BacktestEngine
from data.loader import DataLoader
from strategies.pairs_trading import CointegrationPairsStrategy


def main() -> None:
    print(
        "DEMO ONLY: this example uses synthetic prices and must not be interpreted "
        "as evidence of real-market performance."
    )
    loader = DataLoader()
    data = loader.load_data(["BTC", "ETH"], "2024-01-01", "2024-02-01", freq="1h")
    data = loader.clean_data(data)

    strategy = CointegrationPairsStrategy(
        pair=("BTC", "ETH"),
        lookback=60,
        entry_threshold=2.0,
        exit_threshold=0.5,
    )

    engine = BacktestEngine(initial_capital=100_000)
    result = engine.run(strategy, data)

    print("Backtest results")
    print("---------------")
    print(f"Total return:    {result['total_return']:.4%}")
    print(f"Sharpe ratio:    {result['sharpe_ratio']:.4f}")
    print(f"Max drawdown:    {result['max_drawdown']:.4%}")


if __name__ == "__main__":
    main()
