"""Network-independent tests for momentum real-market validation path."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from backtest.engine import BacktestEngine
from backtest.sweep import run_parameter_sweep
from strategies.momentum import MomentumStrategy

REPLAY_KEYS = ("total_return", "sharpe_ratio", "max_drawdown", "calmar_ratio", "final_equity")


def _is_finite(value) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


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
    assert "cost_sensitivity_grid" in data
    assert "assets_results" in data and isinstance(data["assets_results"], dict)
    assert "provenance" in data
    for asset in data["assets"]:
        res = data["assets_results"][asset]
        assert "top_ranked" in res
        assert "replay" in res and isinstance(res["replay"], dict)
        for key in REPLAY_KEYS:
            assert key in res["replay"], f"{asset} replay missing {key}"
            assert _is_finite(res["replay"][key]), f"{asset} replay {key} not finite"
        assert "benchmark_total_return" in res
        assert _is_finite(res["benchmark_total_return"])
        assert "cost_sensitivity" in res and isinstance(res["cost_sensitivity"], list)
        assert res["cost_sensitivity"], f"{asset} cost_sensitivity grid must be non-empty"
        for point in res["cost_sensitivity"]:
            assert "fee_rate" in point and "slippage" in point
            for key in REPLAY_KEYS:
                assert key in point and _is_finite(point[key])
    # JSON-serializable structure
    json.dumps(data)


def test_momentum_real_market_provenance() -> None:
    p = Path("reports/momentum_real_market.json")
    data = json.loads(p.read_text())
    prov = data["provenance"]
    assert prov.get("real_data_only") is True
    assert prov.get("fabricated_data") is False
    assert isinstance(prov.get("blocked_routes"), list)
    assert prov.get("computed_at")
    assert prov.get("rationale")
