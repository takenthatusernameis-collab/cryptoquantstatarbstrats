#!/usr/bin/env python3
"""Parameter optimization harness for strategies."""

from __future__ import annotations

import itertools
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

from backtest.engine import BacktestEngine
from data.loader import DataLoader
from strategies.mean_reversion import MeanReversionStrategy
from strategies.momentum import MomentumStrategy


def run_backtest(strategy, data: pd.DataFrame) -> dict[str, float]:
    engine = BacktestEngine(initial_capital=100_000)
    result = engine.run(strategy, data)
    return {
        "total_return": result["total_return"],
        "sharpe_ratio": result["sharpe_ratio"],
        "max_drawdown": result["max_drawdown"],
        "calmar_ratio": result["calmar_ratio"],
    }


def optimize() -> pd.DataFrame:
    loader = DataLoader()
    data = loader.load_data(["BTC"], "2024-01-01", "2024-02-01", freq="1h")
    data = loader.clean_data(data)

    results: list[dict[str, Any]] = []

    # Grid search for MomentumStrategy
    for window, threshold in itertools.product([10, 20], [0.005, 0.01, 0.02]):
        strat = MomentumStrategy("BTC", n=window // 2 or 5, m=window, entry_threshold=threshold)
        try:
            metrics = run_backtest(strat, data)
            results.append(
                {"strategy": "momentum", "window": window, "threshold": threshold, **metrics}
            )
        except Exception:
            continue

    # Grid search for MeanReversionStrategy
    for z_window, entry_threshold in itertools.product([20, 30], [1.5, 2.0]):
        strat = MeanReversionStrategy("BTC", lookback=z_window, entry_threshold=entry_threshold)
        try:
            metrics = run_backtest(strat, data)
            results.append(
                {
                    "strategy": "mean_reversion",
                    "z_window": z_window,
                    "entry_threshold": entry_threshold,
                    **metrics,
                }
            )
        except Exception:
            continue

    df = pd.DataFrame(results)
    if df.empty:
        return df
    df_sorted = df.sort_values("calmar_ratio", ascending=False)
    return df_sorted.head(5)


def main() -> None:
    result_df = optimize()
    print(result_df.to_string(index=False))


if __name__ == "__main__":
    main()
