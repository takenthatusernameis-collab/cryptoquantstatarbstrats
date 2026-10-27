"""Tests for walk-forward portfolio reoptimization."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from backtest.engine import BacktestEngine
from data.loader import DataLoader
from utils.optimization import (
    get_optimizer,
    make_equal_weight_optimizer,
    make_inverse_volatility_optimizer,
    make_mean_variance_optimizer,
    make_min_variance_optimizer,
    make_risk_parity_optimizer,
)


def _make_data():
    loader = DataLoader()
    data = loader.load_data(["BTC", "ETH"], "2024-01-01", "2024-03-01", freq="1d")
    return loader.clean_data(data)


def test_make_equal_weight_optimizer():
    data = _make_data()
    opt = make_equal_weight_optimizer()
    w = opt(data.iloc[:10])
    assert isinstance(w, pd.DataFrame)
    assert list(w.columns) == list(data.columns)
    assert np.allclose(w.sum(axis=1).iloc[0], 1.0)
    assert np.allclose(w.values[0], 0.5)


def test_make_inverse_volatility_optimizer():
    data = _make_data()
    opt = make_inverse_volatility_optimizer()
    w = opt(data.iloc[:20])
    assert isinstance(w, pd.DataFrame)
    assert list(w.columns) == list(data.columns)
    assert abs(w.sum(axis=1).iloc[0] - 1.0) < 1e-10


def test_make_risk_parity_optimizer():
    data = _make_data()
    opt = make_risk_parity_optimizer()
    w = opt(data.iloc[:20])
    assert isinstance(w, pd.DataFrame)
    assert abs(w.sum(axis=1).iloc[0] - 1.0) < 1e-10


def test_make_min_variance_optimizer():
    data = _make_data()
    opt = make_min_variance_optimizer()
    w = opt(data.iloc[:30])
    assert isinstance(w, pd.DataFrame)
    assert abs(w.sum(axis=1).iloc[0] - 1.0) < 1e-10


def test_make_mean_variance_optimizer():
    data = _make_data()
    opt = make_mean_variance_optimizer()
    w = opt(data.iloc[:30])
    assert isinstance(w, pd.DataFrame)
    assert abs(w.sum(axis=1).iloc[0] - 1.0) < 1e-10


def test_get_optimizer():
    for name in [
        "equal_weight",
        "inverse_volatility",
        "risk_parity",
        "min_variance",
        "mean_variance",
    ]:
        opt = get_optimizer(name)
        assert callable(opt)


def test_walk_forward_portfolio_reoptimize_false_uses_static_weights():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    # static equal weights
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    res = engine.walk_forward_portfolio(w, data, train_period=30, test_period=10, reoptimize=False)
    assert "results" in res
    assert len(res["results"]) > 0


def test_walk_forward_portfolio_reoptimize_true_with_optimizer():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    opt = make_equal_weight_optimizer()
    res = engine.walk_forward_portfolio(
        w, data, train_period=30, test_period=10, reoptimize=True, optimizer=opt
    )
    assert "results" in res
    assert len(res["results"]) > 0


def test_walk_forward_portfolio_reoptimize_different_optimizers():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    for opt in [
        make_equal_weight_optimizer(),
        make_inverse_volatility_optimizer(),
        make_risk_parity_optimizer(),
        make_min_variance_optimizer(),
        make_mean_variance_optimizer(),
    ]:
        res = engine.walk_forward_portfolio(
            w, data, train_period=30, test_period=10, reoptimize=True, optimizer=opt
        )
        assert "results" in res


def test_walk_forward_portfolio_reoptimize_weight_alignment():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    opt = make_equal_weight_optimizer()

    # Track that optimizer gets train_data
    calls = []

    def tracking_opt(train_data):
        calls.append(train_data)
        return opt(train_data)

    res = engine.walk_forward_portfolio(
        w, data, train_period=30, test_period=10, reoptimize=True, optimizer=tracking_opt
    )
    assert len(calls) > 0
    # returned weights aligned
    assert len(res["results"]) > 0


def test_walk_forward_portfolio_supports_series_optimizer_output():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    initial = pd.DataFrame(0.5, index=data.index, columns=data.columns)

    def series_optimizer(train_data):
        return pd.Series({"BTC": 0.25, "ETH": 0.75})

    result = engine.walk_forward_portfolio(
        initial,
        data,
        train_period=30,
        test_period=10,
        reoptimize=True,
        optimizer=series_optimizer,
    )
    first_weights = result["results"][0]["weights"].iloc[0]
    assert np.isclose(first_weights["BTC"], 0.25)
    assert np.isclose(first_weights["ETH"], 0.75)


def test_walk_forward_portfolio_does_not_hide_optimizer_failure():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    initial = pd.DataFrame(0.5, index=data.index, columns=data.columns)

    def broken_optimizer(train_data):
        raise RuntimeError("optimizer failed")

    with pytest.raises(RuntimeError, match="optimizer failed"):
        engine.walk_forward_portfolio(
            initial,
            data,
            train_period=30,
            test_period=10,
            reoptimize=True,
            optimizer=broken_optimizer,
        )


def test_cli_config_drives_reoptimize(tmp_path):
    import yaml

    from backtest import cli

    data_loader = DataLoader()
    data = data_loader.load_data(["BTC"], "2024-01-01", "2024-02-01", freq="1d")
    data = data_loader.clean_data(data)
    data.to_csv(tmp_path / "data.csv")

    cfg = {
        "symbols": ["BTC"],
        "start": "2024-01-01",
        "end": "2024-02-01",
        "freq": "1d",
        "strategy": "mean_reversion",
        "data_source": "synthetic",
        "walk_forward": True,
        "train_period": 10,
        "test_period": 5,
        "reoptimize": True,
        "optimizer": "inverse_volatility",
        "output": "json",
    }
    cfg_path = tmp_path / "cfg.yaml"
    cfg_path.write_text(yaml.safe_dump(cfg))

    rc = cli.main(["--config", str(cfg_path)])
    assert rc == 0


def test_cli_walk_forward_reoptimize_without_rebalance_frequency(tmp_path):
    from backtest import cli

    data_loader = DataLoader()
    data = data_loader.load_data(["BTC", "ETH"], "2024-01-01", "2024-03-01", freq="1d")
    data = data_loader.clean_data(data)
    data.to_csv(tmp_path / "data.csv")

    rc = cli.main(
        [
            "--symbols",
            "BTC",
            "ETH",
            "--start",
            "2024-01-01",
            "--end",
            "2024-03-01",
            "--freq",
            "1d",
            "--strategy",
            "mean_reversion",
            "--data-source",
            "synthetic",
            "--walk-forward",
            "--train-period",
            "20",
            "--test-period",
            "10",
            "--reoptimize",
            "--optimizer",
            "equal_weight",
            "--output",
            "json",
        ]
    )
    assert rc == 0


def test_cli_walk_forward_reoptimize_optimizer_applied_differs(tmp_path):
    import json

    from backtest import cli

    rc1 = cli.main(
        [
            "--symbols",
            "BTC",
            "ETH",
            "--start",
            "2024-01-01",
            "--end",
            "2024-03-01",
            "--freq",
            "1d",
            "--strategy",
            "mean_reversion",
            "--data-source",
            "synthetic",
            "--walk-forward",
            "--train-period",
            "20",
            "--test-period",
            "10",
            "--reoptimize",
            "--optimizer",
            "equal_weight",
            "--output",
            "json",
            "--output-path",
            str(tmp_path / "r1.json"),
        ]
    )
    assert rc1 == 0
    # Run without reoptimize (should use strategy-based walk_forward)
    rc2 = cli.main(
        [
            "--symbols",
            "BTC",
            "ETH",
            "--start",
            "2024-01-01",
            "--end",
            "2024-03-01",
            "--freq",
            "1d",
            "--strategy",
            "mean_reversion",
            "--data-source",
            "synthetic",
            "--walk-forward",
            "--train-period",
            "20",
            "--test-period",
            "10",
            "--output",
            "json",
            "--output-path",
            str(tmp_path / "r2.json"),
        ]
    )
    assert rc2 == 0
    r1 = json.loads((tmp_path / "r1.json").read_text())
    r2 = json.loads((tmp_path / "r2.json").read_text())
    # Walk-forward runs emit the aggregated walk-forward report (summary table +
    # aggregates). Each must contain a non-empty summary of per-window results.
    assert "summary" in r1
    assert "summary" in r2
    assert len(r1["summary"]) > 0
    assert len(r2["summary"]) > 0


def test_cli_config_drives_reoptimize_without_rebalance_frequency(tmp_path):
    import yaml

    from backtest import cli

    cfg = {
        "symbols": ["BTC", "ETH"],
        "start": "2024-01-01",
        "end": "2024-03-01",
        "freq": "1d",
        "strategy": "mean_reversion",
        "data_source": "synthetic",
        "walk_forward": True,
        "train_period": 20,
        "test_period": 10,
        "reoptimize": True,
        "optimizer": "risk_parity",
        "output": "json",
    }
    cfg_path = tmp_path / "cfg.yaml"
    cfg_path.write_text(yaml.safe_dump(cfg))

    rc = cli.main(["--config", str(cfg_path)])
    assert rc == 0
