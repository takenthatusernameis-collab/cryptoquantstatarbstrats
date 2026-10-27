"""
Tests for the stat-arb framework.
"""

from __future__ import annotations

import os
import sys
import tempfile

import numpy as np
import pandas as pd

from backtest.engine import BacktestEngine
from data.loader import DataLoader
from strategies.cross_exchange import CrossExchangeArb
from strategies.mean_reversion import MeanReversionStrategy
from strategies.momentum import MomentumStrategy
from strategies.pairs_trading import CointegrationPairsStrategy
from utils.metrics import cvar, max_drawdown_duration_from_curve, sortino_ratio, var


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


def test_dataloader_load_csv():
    df = make_data()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        df.to_csv(f.name)
        path = f.name
    try:
        loaded = DataLoader.load_csv(path)
        assert isinstance(loaded, pd.DataFrame)
        assert len(loaded) == len(df)
        assert set(["BTC", "ETH"]).issubset(set(loaded.columns))
    finally:
        os.unlink(path)


def test_clean_data_removes_nans():
    df = make_data()
    df.iloc[5, 0] = np.nan
    cleaned = DataLoader().clean_data(df)
    assert cleaned.isna().sum().sum() == 0


def test_clean_data_preserves_observed_price_extremes():
    data = pd.DataFrame({"BTC": [100.0, 100.1, 101.0, 10_000.0]})
    cleaned = DataLoader().clean_data(data)
    assert cleaned["BTC"].iloc[-1] == 10_000.0


def test_strategy_generate_signals():
    df = make_data()
    strat = CointegrationPairsStrategy(("BTC", "ETH"))
    signals = strat.generate_signals(df)
    assert "zscore" in signals.columns
    assert "long" in signals.columns
    assert "short" in signals.columns
    assert len(signals) == len(df)


def test_pairs_hedge_ratio_is_causal():
    data = make_data(n=300)
    strategy = CointegrationPairsStrategy(("BTC", "ETH"), lookback=30)
    original = strategy.calculate_spread(data["BTC"], data["ETH"])
    changed = data.copy()
    changed.loc[changed.index[-20:], "BTC"] *= 3.0
    altered = strategy.calculate_spread(changed["BTC"], changed["ETH"])
    cutoff = data.index[-20]
    pd.testing.assert_series_equal(
        original.loc[original.index < cutoff],
        altered.loc[altered.index < cutoff],
    )


def test_pairs_strategy_blocks_entries_when_cointegration_fails(monkeypatch):
    data = make_data(n=300)
    strategy = CointegrationPairsStrategy(
        ("BTC", "ETH"), lookback=30, cointegration_check_interval=15
    )
    monkeypatch.setattr(
        strategy, "test_cointegration", lambda price1, price2: (-1.0, 0.5)
    )
    signals = strategy.generate_signals(data)
    assert not signals["long"].any()
    assert not signals["short"].any()
    assert signals["cointegration_pvalue"].dropna().eq(0.5).all()


def test_engine_preserves_explicit_opposing_pair_weights():
    class ExplicitPairSignals:
        def generate_signals(self, data):
            return pd.DataFrame(
                {
                    "long": True,
                    "short": False,
                    "A": 0.5,
                    "B": -0.5,
                },
                index=data.index,
            )

    index = pd.date_range("2024-01-01", periods=4, freq="1h")
    data = pd.DataFrame(
        {
            "A": [100.0, 102.0, 101.0, 105.0],
            "B": [100.0, 99.0, 98.0, 97.0],
        },
        index=index,
    )
    result = BacktestEngine().run(ExplicitPairSignals(), data)
    weights = result["weights"]
    assert weights.iloc[0].abs().sum() == 0.0
    assert weights.iloc[1]["A"] > 0.0
    assert weights.iloc[1]["B"] < 0.0
    assert np.isclose(weights.iloc[1].abs().sum(), 1.0)


def test_engine_applies_close_based_signals_on_next_bar():
    class OneBarSignal:
        def generate_signals(self, data):
            signals = pd.DataFrame(index=data.index)
            signals["A"] = [1.0, 0.0, 0.0, 0.0]
            return signals

    index = pd.date_range("2024-01-01", periods=4, freq="1h")
    data = pd.DataFrame({"A": [100.0, 110.0, 121.0, 133.1]}, index=index)
    result = BacktestEngine().run(OneBarSignal(), data)
    assert result["weights"].iloc[0]["A"] == 0.0
    assert result["weights"].iloc[1]["A"] == 1.0
    # The target generated at the first close earns the following bar return.
    assert np.isclose(result["portfolio_returns"].iloc[1], 0.1)


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


def test_single_asset_strategy_does_not_trade_other_input_columns():
    data = make_data()
    data["SOL"] = 100.0
    strategy = MeanReversionStrategy("BTC")
    signals = strategy.generate_signals(data)
    weights = BacktestEngine()._signals_to_weights(signals, data)
    assert weights["ETH"].abs().sum() == 0.0
    assert weights["SOL"].abs().sum() == 0.0


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


def test_momentum_generate_signals():
    df = make_data()
    strat = MomentumStrategy("BTC")
    signals = strat.generate_signals(df)
    assert "ma" in signals.columns
    assert "long" in signals.columns
    assert "short" in signals.columns
    assert len(signals) == len(df)


def test_momentum_position_sizes():
    df = make_data()
    strat = MomentumStrategy("BTC")
    signals = strat.generate_signals(df)
    sizes = strat.calculate_position_sizes(signals)
    assert set(sizes.keys()) == {"BTC"}
    assert sizes["BTC"] in (-1.0, 0.0, 1.0)


def test_momentum_backtest_runs():
    df = make_data()
    strat = MomentumStrategy("BTC")
    engine = BacktestEngine(initial_capital=100_000)
    result = engine.run(strat, df)
    assert "total_return" in result
    assert isinstance(result["total_return"], float)


def test_optimize_returns_non_empty_dataframe():
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from examples.optimize import optimize

    df = optimize()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_cross_exchange_generate_signals():
    df = make_cross_exchange_data()
    strat = CrossExchangeArb("BTC_Binance", "BTC_Coinbase")
    signals = strat.generate_signals(df)
    assert "spread" in signals.columns
    assert "long_a" in signals.columns
    assert "short_a" in signals.columns
    assert len(signals) == len(df)


def test_cross_exchange_position_persists_until_convergence():
    index = pd.date_range("2024-01-01", periods=6, freq="1h")
    data = pd.DataFrame(
        {
            "BTC_A": [98.0, 98.5, 99.2, 99.7, 100.3, 101.2],
            "BTC_B": [100.0] * 6,
        },
        index=index,
    )
    strategy = CrossExchangeArb(
        "BTC_A", "BTC_B", entry_threshold=0.01, exit_threshold=0.002, fee_rate=0.001
    )
    signals = strategy.generate_signals(data)
    assert signals.loc[index[0], "BTC_A"] > 0.0
    assert signals.loc[index[2], "BTC_A"] > 0.0  # still inside the holding band
    assert signals.loc[index[4], "BTC_A"] == 0.0  # spread crossed the exit band
    assert signals.loc[index[5], "BTC_A"] < 0.0  # later, a large opposite spread enters
    assert np.allclose(
        signals[["BTC_A", "BTC_B"]].abs().sum(axis=1).to_numpy(),
        [1.0, 1.0, 1.0, 1.0, 0.0, 1.0],
    )


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
    class AlwaysLong:
        def generate_signals(self, data):
            return pd.DataFrame({"BTC": 1.0}, index=data.index)

    df = make_data()[["BTC"]]
    engine = BacktestEngine(initial_capital=100_000)
    result_no_cost = engine.run(AlwaysLong(), df)
    result_with_cost = engine.run(
        AlwaysLong(), df, fee_rate=0.001, slippage=0.0005
    )
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


def test_risk_manager_max_position_size():
    """Test RiskManager.max_position_size scales positions."""
    from utils.risk import RiskManager

    rm = RiskManager(max_weight=0.2)
    positions = pd.DataFrame({"A": [0.6], "B": [0.4]})
    scaled = rm.max_position_size(positions, capital=100000)
    # Max position weight should be <= 0.2
    for _, row in scaled.iterrows():
        total = row.abs().sum()
        if total > 0:
            max_w = (row.abs().max() / total)
            assert max_w <= 0.2 + 1e-10


def test_metrics_basic():
    rng = np.random.default_rng(123)
    returns = rng.normal(0.001, 0.01, 1000)
    s = sortino_ratio(returns)
    v = var(returns, confidence=0.95)
    c = cvar(returns, confidence=0.95)
    assert isinstance(s, float)
    assert isinstance(v, float)
    assert isinstance(c, float)
    assert c <= v  # CVaR should be <= VaR (more negative for losses)


def test_metrics_max_drawdown_duration():
    equity = pd.Series([100, 110, 90, 80, 95, 120])
    duration = max_drawdown_duration_from_curve(equity)
    assert isinstance(duration, int)
    assert duration >= 0


def test_benchmark_basic():
    df = make_data()
    strat = CointegrationPairsStrategy(("BTC", "ETH"))
    engine = BacktestEngine(initial_capital=100_000)
    result = engine.run_with_benchmark(strat, df)
    assert "benchmark_total_return" in result
    assert "benchmark_equity_curve" in result
    assert len(result["benchmark_equity_curve"]) == len(df)
    assert "total_return" in result
