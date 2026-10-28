"""
Tests for walk-forward ``anchor`` validation and threading.

Covers the engine methods (``walk_forward`` / ``walk_forward_portfolio``),
the sweep API (``run_parameter_sweep``), and the CLI (``--anchor``).
"""

from __future__ import annotations

import contextlib
import io

import pandas as pd
import pytest

from backtest.cli import main
from backtest.engine import BacktestEngine
from backtest.sweep import run_parameter_sweep
from data.loader import DataLoader
from strategies.mean_reversion import MeanReversionStrategy


def _make_data() -> pd.DataFrame:
    loader = DataLoader()
    data = loader.load_data(["BTC", "ETH"], "2024-01-01", "2024-01-11", freq="1h")
    return loader.clean_data(data)


def _engine() -> BacktestEngine:
    return BacktestEngine(initial_capital=100_000.0)


def test_walk_forward_anchor_none_returns_windows():
    data = _make_data()
    engine = _engine()
    res = engine.walk_forward(
        MeanReversionStrategy(asset="BTC"), data, train_period=100, test_period=40
    )
    assert len(res.get("results", [])) == 3


def test_walk_forward_anchor_int_shifts_windows():
    data = _make_data()
    engine = _engine()
    # Anchor at row 40 drops the first window (needs train+test <= remaining).
    res = engine.walk_forward(
        MeanReversionStrategy(asset="BTC"),
        data,
        train_period=100,
        test_period=40,
        anchor=40,
    )
    assert len(res.get("results", [])) == 2


def test_walk_forward_anchor_timestamp_valid():
    data = _make_data()
    engine = _engine()
    res = engine.walk_forward(
        MeanReversionStrategy(asset="BTC"),
        data,
        train_period=100,
        test_period=40,
        anchor="2024-01-01 04:00:00",
    )
    assert len(res.get("results", [])) == 3


def test_walk_forward_anchor_negative_clamped_to_origin():
    data = _make_data()
    engine = _engine()
    res = engine.walk_forward(
        MeanReversionStrategy(asset="BTC"),
        data,
        train_period=100,
        test_period=40,
        anchor=-5,
    )
    assert len(res.get("results", [])) == 3


def test_walk_forward_anchor_bool_raises():
    data = _make_data()
    engine = _engine()
    with pytest.raises(ValueError):
        engine.walk_forward(
            MeanReversionStrategy(asset="BTC"),
            data,
            train_period=100,
            test_period=40,
            anchor=True,
        )


def test_walk_forward_anchor_unparseable_string_raises():
    data = _make_data()
    engine = _engine()
    with pytest.raises(ValueError):
        engine.walk_forward(
            MeanReversionStrategy(asset="BTC"),
            data,
            train_period=100,
            test_period=40,
            anchor="not-a-date",
        )


def test_walk_forward_anchor_float_nonintegral_raises():
    data = _make_data()
    engine = _engine()
    with pytest.raises(ValueError):
        engine.walk_forward(
            MeanReversionStrategy(asset="BTC"),
            data,
            train_period=100,
            test_period=40,
            anchor=2.5,
        )


def test_walk_forward_portfolio_anchor_validation():
    data = _make_data()
    engine = _engine()
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    # Valid anchor works.
    res = engine.walk_forward_portfolio(
        w, data, train_period=100, test_period=40, anchor=40
    )
    assert len(res.get("results", [])) == 2
    # Invalid anchor raises.
    with pytest.raises(ValueError):
        engine.walk_forward_portfolio(
            w, data, train_period=100, test_period=40, anchor="not-a-date"
        )
    with pytest.raises(ValueError):
        engine.walk_forward_portfolio(
            w, data, train_period=100, test_period=40, anchor=True
        )


def test_sweep_invalid_anchor_raises():
    data = _make_data()
    with pytest.raises(ValueError):
        run_parameter_sweep(
            MeanReversionStrategy(asset="BTC"),
            data,
            {"lookback": [20]},
            train_period=100,
            test_period=40,
            fee_rate=0.0,
            slippage=0.0,
            metric="calmar_ratio",
            anchor="not-a-date",
        )
    with pytest.raises(ValueError):
        run_parameter_sweep(
            MeanReversionStrategy(asset="BTC"),
            data,
            {"lookback": [20]},
            train_period=100,
            test_period=40,
            fee_rate=0.0,
            slippage=0.0,
            metric="calmar_ratio",
            anchor=True,
        )


def test_sweep_valid_anchor_returns_rows():
    data = _make_data()
    rows = run_parameter_sweep(
        MeanReversionStrategy(asset="BTC"),
        data,
        {"lookback": [20]},
        train_period=100,
        test_period=40,
        fee_rate=0.0,
        slippage=0.0,
        metric="calmar_ratio",
        anchor="2024-01-01",
    )
    assert isinstance(rows, list)
    assert len(rows) == 1


def _run_cli(argv: list[str]) -> int:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = main(argv)
    return int(code or 0)


def test_walk_forward_cli_anchor_valid_exits_zero():
    code = _run_cli(
        [
            "--walk-forward",
            "--strategy",
            "mean_reversion",
            "--asset",
            "BTC",
            "--data-source",
            "synthetic",
            "--train-period",
            "100",
            "--test-period",
            "40",
            "--anchor",
            "2024-01-05",
        ]
    )
    assert code == 0


def test_walk_forward_cli_anchor_invalid_raises():
    with pytest.raises(ValueError):
        main(
            [
                "--walk-forward",
                "--strategy",
                "mean_reversion",
                "--asset",
                "BTC",
                "--data-source",
                "synthetic",
                "--train-period",
                "100",
                "--test-period",
                "40",
                "--anchor",
                "not-a-date",
            ]
        )
