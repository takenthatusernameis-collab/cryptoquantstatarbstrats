"""
Enhanced tests for the `backtest.sweep` API module.

Covers the strategy factory pattern, input validation errors, JSON
serializability of returned rows, and the progress callback.
"""

from __future__ import annotations

import json

import numpy as np
import pytest

from backtest.engine import BacktestEngine
from backtest.sweep import run_parameter_sweep
from data.loader import DataLoader
from strategies.mean_reversion import MeanReversionStrategy


def _make_data():
    loader = DataLoader()
    data = loader.load_data(["BTC"], "2024-01-01", "2024-01-10", freq="1h")
    return loader.clean_data(data)


def _base_kwargs():
    return dict(
        fee_rate=0.0,
        slippage=0.0,
    )


def test_sweep_factory_pattern_returns_rows():
    data = _make_data()
    calls = []

    def factory(combo):
        calls.append(dict(combo))
        return MeanReversionStrategy(
            "BTC",
            lookback=int(combo.get("lookback", 30)),
            entry_threshold=float(combo.get("entry_threshold", 2.0)),
        )

    engine = BacktestEngine(initial_capital=100_000.0)
    rows = run_parameter_sweep(
        factory,
        data,
        {"lookback": [20, 30], "entry_threshold": [1.5, 2.0]},
        train_period=30,
        test_period=10,
        engine=engine,
        **_base_kwargs(),
    )
    assert len(rows) == 4
    assert len(calls) == 4
    # Every row carries the params and the standard metric keys.
    for r in rows:
        assert "lookback" in r and "entry_threshold" in r
        assert "oos_mean_return" in r
        assert "mean_max_drawdown" in r
        assert "oos_is_ratio" in r
        assert "oos_periods" in r
        assert "rank" in r
        assert "oos_returns" not in r
    # Ranks are 1..4 in order.
    assert [r["rank"] for r in rows] == [1, 2, 3, 4]


def test_sweep_instance_not_mutated():
    data = _make_data()
    template = MeanReversionStrategy("BTC", lookback=30, entry_threshold=2.0)
    engine = BacktestEngine(initial_capital=100_000.0)
    run_parameter_sweep(
        template,
        data,
        {"lookback": [999], "entry_threshold": [7.7]},
        train_period=30,
        test_period=10,
        engine=engine,
        **_base_kwargs(),
    )
    # The caller's instance must be left untouched.
    assert template.lookback == 30
    assert template.entry_threshold == 2.0


def test_sweep_strategy_kwargs_merged():
    data = _make_data()

    class TrackingStrategy(MeanReversionStrategy):
        def __init__(self, asset, lookback=30, entry_threshold=2.0, tag="default"):
            super().__init__(asset, lookback=lookback, entry_threshold=entry_threshold)
            self.tag = tag

    engine = BacktestEngine(initial_capital=100_000.0)
    rows = run_parameter_sweep(
        TrackingStrategy,
        data,
        {"lookback": [20]},
        train_period=30,
        test_period=10,
        engine=engine,
        strategy_kwargs={"tag": "sweep_run", "asset": "BTC"},
        **_base_kwargs(),
    )
    assert len(rows) == 1
    assert rows[0]["lookback"] == 20


def test_sweep_validation_bad_train_period():
    data = _make_data()
    with pytest.raises(ValueError, match="train_period"):
        run_parameter_sweep(
            MeanReversionStrategy("BTC"),
            data,
            {"lookback": [20]},
            train_period=0,
            test_period=10,
            **_base_kwargs(),
        )
    with pytest.raises(ValueError, match="train_period"):
        run_parameter_sweep(
            MeanReversionStrategy("BTC"),
            data,
            {"lookback": [20]},
            train_period=-5,
            test_period=10,
            **_base_kwargs(),
        )


def test_sweep_validation_bad_test_period():
    data = _make_data()
    with pytest.raises(ValueError, match="test_period"):
        run_parameter_sweep(
            MeanReversionStrategy("BTC"),
            data,
            {"lookback": [20]},
            train_period=30,
            test_period=0,
            **_base_kwargs(),
        )


def test_sweep_validation_invalid_metric():
    data = _make_data()
    with pytest.raises(ValueError, match="Invalid metric"):
        run_parameter_sweep(
            MeanReversionStrategy("BTC"),
            data,
            {"lookback": [20]},
            train_period=30,
            test_period=10,
            metric="bad_metric",
            **_base_kwargs(),
        )


def test_sweep_validation_empty_grid():
    data = _make_data()
    with pytest.raises(ValueError, match="non-empty"):
        run_parameter_sweep(
            MeanReversionStrategy("BTC"),
            data,
            {},
            train_period=30,
            test_period=10,
            **_base_kwargs(),
        )


def test_sweep_validation_empty_grid_value():
    data = _make_data()
    with pytest.raises(ValueError, match="empty for"):
        run_parameter_sweep(
            MeanReversionStrategy("BTC"),
            data,
            {"lookback": []},
            train_period=30,
            test_period=10,
            **_base_kwargs(),
        )


def test_sweep_rows_json_serializable_with_numpy_params():
    data = _make_data()
    # Grid values supplied as numpy scalars; returned rows must be native types.
    engine = BacktestEngine(initial_capital=100_000.0)
    rows = run_parameter_sweep(
        MeanReversionStrategy("BTC"),
        data,
        {"lookback": [np.int64(20), np.int64(30)]},
        train_period=30,
        test_period=10,
        engine=engine,
        **_base_kwargs(),
    )
    assert len(rows) == 2
    for r in rows:
        assert isinstance(r["lookback"], int) and not isinstance(r["lookback"], np.integer)
        assert isinstance(r["oos_mean_return"], float)
    # Must round-trip through JSON without a custom default.
    json.dumps(rows, sort_keys=True)


def test_sweep_progress_callback_invoked():
    data = _make_data()
    events = []

    def callback(completed, total, current_combo, row):
        events.append((completed, total, dict(current_combo), dict(row)))

    engine = BacktestEngine(initial_capital=100_000.0)
    rows = run_parameter_sweep(
        MeanReversionStrategy("BTC"),
        data,
        {"lookback": [10, 20, 30]},
        train_period=30,
        test_period=10,
        engine=engine,
        progress_callback=callback,
        **_base_kwargs(),
    )
    assert len(rows) == 3
    assert len(events) == 3
    assert events[0][0] == 1 and events[0][1] == 3
    assert events[-1][0] == 3 and events[-1][1] == 3
    # current_combo carries the params for that combo.
    assert events[0][2]["lookback"] in (10, 20, 30)
    # row carries the metric keys (no rank yet at callback time).
    assert "oos_mean_return" in events[0][3]
    assert "oos_returns" not in events[0][3]


def test_sweep_expanding_mode_runs():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100_000.0)
    rows = run_parameter_sweep(
        MeanReversionStrategy("BTC"),
        data,
        {"lookback": [20]},
        train_period=30,
        test_period=10,
        engine=engine,
        mode="expanding",
        **_base_kwargs(),
    )
    assert len(rows) == 1
    assert rows[0]["oos_periods"] >= 1


def test_sweep_rolling_mode_default():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100_000.0)
    rows = run_parameter_sweep(
        MeanReversionStrategy("BTC"),
        data,
        {"lookback": [20]},
        train_period=30,
        test_period=10,
        engine=engine,
        **_base_kwargs(),
    )
    assert len(rows) == 1


def test_sweep_n_splits_caps_windows():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100_000.0)
    full = run_parameter_sweep(
        MeanReversionStrategy("BTC"),
        data,
        {"lookback": [20]},
        train_period=30,
        test_period=10,
        engine=engine,
        **_base_kwargs(),
    )
    capped = run_parameter_sweep(
        MeanReversionStrategy("BTC"),
        data,
        {"lookback": [20]},
        train_period=30,
        test_period=10,
        engine=engine,
        n_splits=1,
        **_base_kwargs(),
    )
    assert capped[0]["oos_periods"] <= full[0]["oos_periods"]
    assert capped[0]["oos_periods"] == 1


def test_sweep_validation_bad_mode():
    data = _make_data()
    with pytest.raises(ValueError, match="Invalid mode"):
        run_parameter_sweep(
            MeanReversionStrategy("BTC"),
            data,
            {"lookback": [20]},
            train_period=30,
            test_period=10,
            mode="bogus",
            **_base_kwargs(),
        )


def test_sweep_validation_bad_n_splits():
    data = _make_data()
    with pytest.raises(ValueError, match="n_splits"):
        run_parameter_sweep(
            MeanReversionStrategy("BTC"),
            data,
            {"lookback": [20]},
            train_period=30,
            test_period=10,
            n_splits=0,
            **_base_kwargs(),
        )
def test_sweep_deterministic_output():
    data = _make_data()
    rows1 = run_parameter_sweep(
        MeanReversionStrategy("BTC"),
        data,
        {"lookback": [10, 20, 30]},
        train_period=30,
        test_period=10,
        **_base_kwargs(),
    )
    rows2 = run_parameter_sweep(
        MeanReversionStrategy("BTC"),
        data,
        {"lookback": [10, 20, 30]},
        train_period=30,
        test_period=10,
        **_base_kwargs(),
    )
    assert json.dumps(rows1, sort_keys=True) == json.dumps(rows2, sort_keys=True)
