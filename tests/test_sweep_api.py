"""
Tests for the `backtest.sweep` API module.
"""

from __future__ import annotations

import json

import pytest

from backtest.engine import BacktestEngine
from backtest.sweep import run_parameter_sweep
from data.loader import DataLoader
from strategies.mean_reversion import MeanReversionStrategy


def _make_data():
    loader = DataLoader()
    data = loader.load_data(["BTC"], "2024-01-01", "2024-01-10", freq="1h")
    return loader.clean_data(data)


def test_sweep_api_empty_grid():
    data = _make_data()
    with pytest.raises(ValueError):
        run_parameter_sweep(MeanReversionStrategy('BTC'), data, {}, 60, 20)


def test_sweep_api_single_combination():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100_000.0)
    rows = run_parameter_sweep(
        MeanReversionStrategy('BTC'),
        data,
        {"lookback": [20]},
        train_period=30,
        test_period=10,
        fee_rate=0.0,
        slippage=0.0,
        metric="calmar_ratio",
        engine=engine,
    )
    assert isinstance(rows, list)
    assert len(rows) == 1
    assert rows[0]["lookback"] == 20
    assert "oos_mean_return" in rows[0]
    assert "mean_max_drawdown" in rows[0]
    assert "oos_is_ratio" in rows[0]
    assert "oos_periods" in rows[0]
    assert "rank" in rows[0]


def test_sweep_api_ranking_order():
    data = _make_data()
    rows = run_parameter_sweep(
        MeanReversionStrategy('BTC'),
        data,
        {"lookback": [10, 30]},
        train_period=30,
        test_period=10,
        metric="calmar_ratio",
    )
    assert len(rows) == 2
    assert rows[0]["rank"] == 1
    assert rows[1]["rank"] == 2
    assert rows[0]["rank"] < rows[1]["rank"]


def test_sweep_api_invalid_metric():
    data = _make_data()
    with pytest.raises(ValueError):
        run_parameter_sweep(
            MeanReversionStrategy('BTC'), data, {"lookback": [20]}, 30, 10, metric="bad"
        )


def test_sweep_api_deterministic_output():
    data = _make_data()
    rows1 = run_parameter_sweep(
        MeanReversionStrategy('BTC'),
        data,
        {"lookback": [10, 20, 30]},
        train_period=30,
        test_period=10,
        metric="calmar_ratio",
    )
    rows2 = run_parameter_sweep(
        MeanReversionStrategy('BTC'),
        data,
        {"lookback": [10, 20, 30]},
        train_period=30,
        test_period=10,
        metric="calmar_ratio",
    )
    # Compare serialized forms (excluding any non-deterministic floats details)
    assert json.dumps(rows1, sort_keys=True) == json.dumps(rows2, sort_keys=True)
