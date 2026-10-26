"""
Tests for the stat-arb framework.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from backtest.engine import BacktestEngine
from data.loader import DataLoader
from strategies.cross_exchange import CrossExchangeArb
from strategies.mean_reversion import MeanReversionStrategy
from strategies.pairs_trading import CointegrationPairsStrategy


def make_data(n: int = 500, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2024-01-01", periods=n, freq="1h")
    r1 = rng.normal(0.0, 0.02, n)
    r2 = 0.6 * r1 + rng.normal(0.0, 0.015, n)
    df = pd.DataFrame(
        {
            "BTC": 100 * np.exp(np.cumsum(r1)),
            "ETH": 100 * np.exp(np.cumsum(r2)),
        },
        index=dates,
    )
    return df


def make_cross_exchange_data(n: int = 500, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2024-01-01", periods=n, freq="1h")
    base = 100 * np.exp(np.cumsum(rng.normal(0.0, 0.02, n)))
    spread = rng.normal(0.0, 0.005, n)
    df = pd.DataFrame(
        {
            "BTC_Binance": base,
            "BTC_Coinbase": base * (1.0 + spread),
        },
        index=dates,
    )
    return df


def test_dataloader_loads_data():
    loader = DataLoader()
    df = loader.load_data(["BTC", "ETH"], "2024-01-01", "2024-01-02", freq="1h")
    assert df.shape[1] == 2
    assert df.isna().sum().sum() == 0


def test_clean_data_removes_nans():
    df = make_data()
    df.iloc[5, 0] = np.nan
    cleaned = DataLoader().clean_data(df)
    assert cleaned.isna().sum().sum() == 0


def test_strategy_generate_signals():
    df = make_data()
    strat = CointegrationPairsStrategy(("BTC", "ETH"))
    signals = strat.generate_signals(df)
    assert "zscore" in signals.columns
    assert "long" in signals.columns
    assert "short" in signals.columns
    assert len(signals) == len(df)


def test_backtest_engine_runs():
    df = make_data()
    strat = CointegrationPairsStrategy(("BTC", "ETH"))
    engine = BacktestEngine(initial_capital=100_000)
    result = engine.run(strat, df)
    assert "total_return" in result
    assert "sharpe_ratio" in result
    assert "max_drawdown" in result
    assert isinstance(result["total_return"], float)


def test_pair_strategy_position_sizes():
    df = make_data()
    strat = CointegrationPairsStrategy(("BTC", "ETH"))
    signals = strat.generate_signals(df)
    sizes = strat.calculate_position_sizes(signals)
    assert set(sizes.keys()) == {"BTC", "ETH"}


def test_mean_reversion_generate_signals():
    df = make_data()
    strat = MeanReversionStrategy("BTC")
    signals = strat.generate_signals(df)
    assert "zscore" in signals.columns
    assert "long" in signals.columns
    assert "short" in signals.columns
    assert "exit" in signals.columns
    assert len(signals) == len(df)


def test_mean_reversion_position_sizes():
    df = make_data()
    strat = MeanReversionStrategy("BTC")
    signals = strat.generate_signals(df)
    sizes = strat.calculate_position_sizes(signals)
    assert set(sizes.keys()) == {"BTC"}
    assert sizes["BTC"] in (-1.0, 0.0, 1.0)


def test_mean_reversion_backtest_runs():
    df = make_data()
    strat = MeanReversionStrategy("BTC")
    engine = BacktestEngine(initial_capital=100_000)
    result = engine.run(strat, df)
    assert "total_return" in result
    assert isinstance(result["total_return"], float)


def test_cross_exchange_generate_signals():
    df = make_cross_exchange_data()
    strat = CrossExchangeArb("BTC_Binance", "BTC_Coinbase")
    signals = strat.generate_signals(df)
    assert "spread" in signals.columns
    assert "long_a" in signals.columns
    assert "short_a" in signals.columns
    assert len(signals) == len(df)


def test_cross_exchange_position_sizes():
    df = make_cross_exchange_data()
    strat = CrossExchangeArb("BTC_Binance", "BTC_Coinbase")
    signals = strat.generate_signals(df)
    sizes = strat.calculate_position_sizes(signals)
    assert set(sizes.keys()) == {"BTC_Binance", "BTC_Coinbase"}
    assert sizes["BTC_Binance"] in (-1.0, 0.0, 1.0)
    assert sizes["BTC_Coinbase"] in (-1.0, 0.0, 1.0)
    assert sizes["BTC_Binance"] + sizes["BTC_Coinbase"] == 0.0


def test_cross_exchange_backtest_runs():
    df = make_cross_exchange_data()
    strat = CrossExchangeArb("BTC_Binance", "BTC_Coinbase")
    engine = BacktestEngine(initial_capital=100_000)
    result = engine.run(strat, df)
    assert "total_return" in result
    assert isinstance(result["total_return"], float)


def test_transaction_costs_reduce_returns():
    df = make_data()
    strat = CointegrationPairsStrategy(("BTC", "ETH"))
    engine = BacktestEngine(initial_capital=100_000)
    result_no_cost = engine.run(strat, df)
    result_with_cost = engine.run(strat, df, fee_rate=0.001, slippage=0.0005)
    assert result_with_cost["total_return"] < result_no_cost["total_return"]


def test_walk_forward_returns_dict():
    df = make_data(n=1000)
    strat = CointegrationPairsStrategy(("BTC", "ETH"))
    engine = BacktestEngine(initial_capital=100_000)
    wf_result = engine.walk_forward(strat, df, train_period=200, test_period=50)
    assert isinstance(wf_result, dict)
    assert "returns" in wf_result
    assert isinstance(wf_result["returns"], list)
    assert len(wf_result["returns"]) > 0
    assert "results" in wf_result
