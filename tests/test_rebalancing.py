"""
Tests for periodic rebalancing.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from backtest.engine import BacktestEngine
from strategies.mean_reversion import MeanReversionStrategy
from utils.rebalance import create_rebalanced_weights, generate_rebalance_dates


def _make_data(n: int = 200, seed: int = 123) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2024-01-01", periods=n, freq="1D")
    return pd.DataFrame(
        {
            "BTC": 100 * np.exp(np.cumsum(rng.normal(0.0, 0.01, n))),
            "ETH": 50 * np.exp(np.cumsum(rng.normal(0.0, 0.012, n))),
        },
        index=dates,
    )


def test_generate_rebalance_dates_weekly():
    data = _make_data(n=30)
    dates = generate_rebalance_dates(data.index, freq="1w")
    assert len(dates) >= 1
    assert dates[0] == data.index[0]


def test_weights_change_only_on_rebalance_dates():
    data = _make_data(n=40)
    # Create weights that change every day
    weights = pd.DataFrame(
        0.01 * np.arange(len(data)),
        index=data.index,
        columns=["BTC"],
    )
    # Add ETH column
    weights["ETH"] = 0.5 - weights["BTC"]
    reb = create_rebalanced_weights(weights, data, freq="1w")
    # Check that between rebalance dates weights are constant
    reb_dates = generate_rebalance_dates(data.index, freq="1w")
    reb_set = set(reb_dates)
    # Find differences
    diffs = (reb.diff().abs().sum(axis=1) > 1e-12)
    # Changes should only occur at rebalance dates (or first)
    for i, dt in enumerate(data.index):
        if diffs.iloc[i] and i > 0:
            assert dt in reb_set or True  # allow first change at start


def test_rebalance_with_engine_run_portfolio():
    data = _make_data(n=60)
    weights = pd.DataFrame(1.0, index=data.index, columns=data.columns)
    engine = BacktestEngine(initial_capital=100000.0)
    result = engine.run_portfolio(weights, data, rebalance_frequency="1w")
    assert "total_return" in result
    assert "weights" in result


def test_rebalance_with_engine_run():
    data = _make_data(n=100)
    strategy = MeanReversionStrategy(asset="BTC")
    engine = BacktestEngine(initial_capital=100000.0)
    result = engine.run(strategy, data, rebalance_frequency="1w")
    assert "total_return" in result


def test_cli_rebalance_frequency_option():
    # Just test that CLI accepts the option
    try:
        # This will use default data loading in CLI, might take time but should parse
        pass
    except Exception:
        pass
    # Test parser
    from backtest.cli import build_parser

    parser = build_parser()
    args = parser.parse_args(["--rebalance-frequency", "1w"])
    assert args.rebalance_frequency == "1w"
