"""Network-independent tests for momentum real-market validation path."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from backtest.engine import BacktestEngine
from backtest.sweep import run_parameter_sweep
from strategies.momentum import MomentumStrategy


def _make_ohlc(n: int = 1500) -> pd.DataFrame:
    rng = np.random.default_rng(123)
    idx = pd.date_range("2026-04-01", periods=n, freq="h")
    price = 100.0 + np.cumsum(rng.normal(0.0, 0.001, n))
    return pd.DataFrame({"BTC": price}, index=idx)


def test_momentum_walk_forward_with_replay_and_benchmark(tmp_path: Path) -> None:
    data = _make_ohlc(1500)
    engine = BacktestEngine(initial_capital=100_000.0)
    grid = {"n": [5, 10], "m": [20, 30], "entry_threshold": [0.005, 0.01]}

    rows = run_parameter_sweep(
        MomentumStrategy(asset="BTC"),
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
        MomentumStrategy(
            asset="BTC",
            n=top["n"],
            m=top["m"],
            entry_threshold=top["entry_threshold"],
        ),
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


def test_momentum_real_market_artifact_exists() -> None:
    p = Path("reports/momentum_real_market.json")
    assert p.exists()
    data = json.loads(p.read_text())
    assert data.get("assets") == ["BTC", "ETH", "SOL"]
    assert "grid" in data and isinstance(data["grid"], dict)
    assert "walk_forward" in data and isinstance(data["walk_forward"], dict)
    assert "costs" in data and isinstance(data["costs"], dict)
    assert "assets_results" in data and isinstance(data["assets_results"], dict)
    for asset in data["assets"]:
        res = data["assets_results"][asset]
        assert "top_ranked" in res
        assert "replay" in res and isinstance(res["replay"], dict)
        assert "benchmark_total_return" in res
    # JSON-serializable structure
    json.dumps(data)
