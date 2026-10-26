#!/usr/bin/env python3
"""Comparative backtest harness for multiple stat-arb strategies."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

from backtest.engine import BacktestEngine
from data.loader import DataLoader
from strategies.cross_exchange import CrossExchangeArb
from strategies.mean_reversion import MeanReversionStrategy
from strategies.momentum import MomentumStrategy
from strategies.pairs_trading import CointegrationPairsStrategy
from utils.risk import RiskManager


def run_backtest(strategy, data: pd.DataFrame, risk_manager: Any = None) -> dict[str, float]:
    engine = BacktestEngine(initial_capital=100_000)
    result = engine.run(strategy, data, risk_manager=risk_manager)
    return {
        "total_return": result["total_return"],
        "sharpe_ratio": result["sharpe_ratio"],
        "sortino_ratio": result["sortino_ratio"],
        "var": result["var"],
        "cvar": result["cvar"],
        "max_drawdown": result["max_drawdown"],
        "max_drawdown_duration": result["max_drawdown_duration"],
        "calmar_ratio": result["calmar_ratio"],
    }


def main() -> None:
    loader = DataLoader()
    start, end = "2024-01-01", "2024-02-01"

    # Single-asset data for mean reversion.
    single = loader.load_data(["BTC", "ETH", "SOL"], start, end, freq="1h")
    single = loader.clean_data(single)

    # Cross-exchange data: same asset quoted on two venues.
    cross = loader.load_data(["BTC_Binance", "BTC_Coinbase"], start, end, freq="1h")
    cross = loader.clean_data(cross)

    risk_manager = RiskManager(max_weight=0.25)

    strategies = [
        ("Cointegration Pairs (BTC-ETH)", CointegrationPairsStrategy(("BTC", "ETH")), single),
        ("Mean Reversion (BTC)", MeanReversionStrategy("BTC"), single),
        ("Mean Reversion (ETH)", MeanReversionStrategy("ETH"), single),
        ("Mean Reversion (SOL)", MeanReversionStrategy("SOL"), single),
        ("Momentum (BTC)", MomentumStrategy("BTC"), single),
        ("Cross-Exchange (BTC)", CrossExchangeArb("BTC_Binance", "BTC_Coinbase"), cross),
    ]

    rows: list[dict[str, Any]] = []
    for name, strategy, data in strategies:
        metrics = run_backtest(strategy, data, risk_manager=risk_manager)
        rows.append({"Strategy": name, **metrics})

    df = pd.DataFrame(rows)
    print("Strategy Comparison")
    print("------------------")
    print(
        df.to_string(
            index=False,
            formatters={
                "total_return": "{:.4%}".format,
                "sharpe_ratio": "{:.4f}".format,
                "sortino_ratio": "{:.4f}".format,
                "var": "{:.4%}".format,
                "cvar": "{:.4%}".format,
                "max_drawdown": "{:.4%}".format,
                "max_drawdown_duration": "{:.0f}".format,
                "calmar_ratio": "{:.4f}".format,
            },
        )
    )


if __name__ == "__main__":
    main()
