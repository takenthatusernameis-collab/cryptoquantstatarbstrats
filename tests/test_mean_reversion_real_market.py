"""Network-independent tests for mean-reversion real-market validation path."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from backtest.engine import BacktestEngine
from backtest.sweep import run_parameter_sweep
from strategies.mean_reversion import MeanReversionStrategy


def _make_ohlc(n: int = 1500) -> pd.DataFrame:
    rng = np.random.default_rng(123)
    idx = pd.date_range("2026-04-01", periods=n, freq="h")
    price = 100.0 + np.cumsum(rng.normal(0.0, 0.001, n))
    return pd.DataFrame({"BTC": price}, index=idx)


def test_mean_reversion_walk_forward_with_replay_and_benchmark(tmp_path: Path) -> None:
    data = _make_ohlc(1500)
    engine = BacktestEngine(initial_capital=100_000.0)
    grid = {"lookback": [20, 30], "entry_threshold": [1.5, 2.0]}

    rows = run_parameter_sweep(
        MeanReversionStrategy(asset="BTC"),
        data,
        grid,
        train_period=300,
        test_period=100,
        fee_rate=0.001,
        slippage=0.0005,
        metric="calmar_ratio",
        engine=engine,
        mode="rolling",
        n_splits=3,
        replay_best=True,
        show_progress=False,
    )
    assert rows
    top = rows[0]
    assert "replay" in top
    replay = top["replay"]
    for key in ("total_return", "sharpe_ratio", "max_drawdown", "calmar_ratio", "final_equity"):
        assert key in replay

    benchmark = engine.run_with_benchmark(
        MeanReversionStrategy(asset="BTC", **{k: top[k] for k in ("lookback", "entry_threshold")}),
        data[["BTC"]],
        fee_rate=0.001,
        slippage=0.0005,
    )
    assert "benchmark_total_return" in benchmark

    # Ensure results are JSON serializable like the example script
    out = {
        "assets": ["BTC"],
        "assets_results": {
            "BTC": {
                "asset": "BTC",
                "top_ranked": {k: v for k, v in top.items() if k != "replay"},
                "replay": replay,
                "benchmark_total_return": benchmark["benchmark_total_return"],
            }
        },
    }
    json.dumps(out)  # should not raise
