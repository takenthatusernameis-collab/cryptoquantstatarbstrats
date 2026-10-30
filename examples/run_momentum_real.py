#!/usr/bin/env python3
"""Real-market validation of the single-asset MomentumStrategy.

Fetches public Binance spot candles (no API key required), runs a walk-forward
parameter sweep per asset (BTC, ETH, SOL) with replay_best=True, compares each
asset's top-ranked combo to an equal-weight buy-and-hold benchmark over the
same window, and consolidates results into reports/momentum_real_market.json.

This is a research/demonstration script. Its output is not evidence of a
trading edge and is not investment advice.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backtest.engine import BacktestEngine
from backtest.sweep import run_parameter_sweep
from data.loader import DataLoader
from strategies.momentum import MomentumStrategy

ASSETS = ["BTC", "ETH", "SOL"]
START = "2026-04-01"
END = "2026-10-28"
FREQ = "1h"
FEE_RATE = 0.001
SLIPPAGE = 0.0005
GRID = {
    "n": [5, 10, 20],
    "m": [20, 40, 60],
    "entry_threshold": [0.005, 0.01, 0.02],
}


def run_for_asset(asset: str, data, grid, engine: BacktestEngine):
    rows = run_parameter_sweep(
        MomentumStrategy(asset=asset),
        data,
        grid,
        train_period=500,
        test_period=100,
        fee_rate=FEE_RATE,
        slippage=SLIPPAGE,
        metric="calmar_ratio",
        engine=engine,
        mode="rolling",
        n_splits=4,
        replay_best=True,
        show_progress=True,
    )
    if not rows:
        raise RuntimeError(f"No sweep results for asset {asset}")
    top = rows[0]
    params = {k: top[k] for k in ("n", "m", "entry_threshold") if k in top}
    benchmark = engine.run_with_benchmark(
        MomentumStrategy(asset=asset, **params),
        data[[asset]],
        fee_rate=FEE_RATE,
        slippage=SLIPPAGE,
    )
    return top, benchmark


def main() -> None:
    print(
        "RESEARCH/DEMO ONLY: uses real public Binance spot candles. Results are not "
        "evidence of a trading edge and are not investment advice."
    )

    loader = DataLoader()
    data = loader.load_binance_data(ASSETS, START, END, interval=FREQ)
    data = loader.clean_data(data)
    print(
        f"Loaded {len(data)} hourly bars for {', '.join(ASSETS)} "
        f"({data.index.min().date()} -> {data.index.max().date()})"
    )

    engine = BacktestEngine(initial_capital=100_000.0)

    results = {}
    for asset in ASSETS:
        print(f"\n=== Validating momentum on {asset} ===")
        top, benchmark = run_for_asset(asset, data, GRID, engine)
        replay = top.get("replay") or {}
        print("Top-ranked combo (out-of-sample walk-forward):")
        print(f"  n={top['n']} m={top['m']} entry_threshold={top['entry_threshold']}")
        print(
            f"  OOS mean return={top['oos_mean_return']:.6f} "
            f"OOS/IS ratio={top['oos_is_ratio']:.4f} "
            f"OOS periods={top['oos_periods']}"
        )
        print("Replay over full dataset:")
        print(
            f"  total_return={replay.get('total_return', 0.0):.4%} "
            f"sharpe_ratio={replay.get('sharpe_ratio', 0.0):.4f} "
            f"max_drawdown={replay.get('max_drawdown', 0.0):.4%} "
            f"calmar_ratio={replay.get('calmar_ratio', 0.0):.4f} "
            f"final_equity={replay.get('final_equity', 0.0):,.2f}"
        )
        print(
            f"Equal-weighted buy-and-hold benchmark ({asset}): "
            f"{benchmark['benchmark_total_return']:.4%}"
        )
        results[asset] = {
            "asset": asset,
            "top_ranked": {k: v for k, v in top.items() if k != "replay"},
            "replay": replay,
            "benchmark_total_return": benchmark["benchmark_total_return"],
        }

    out = {
        "assets": ASSETS,
        "start": START,
        "end": END,
        "freq": FREQ,
        "n_bars": int(len(data)),
        "grid": GRID,
        "walk_forward": {
            "train_period": 500,
            "test_period": 100,
            "mode": "rolling",
            "n_splits": 4,
            "metric": "calmar_ratio",
        },
        "costs": {
            "fee_rate": FEE_RATE,
            "slippage": SLIPPAGE,
        },
        "assets_results": results,
    }
    out_path = Path(__file__).resolve().parent.parent / "reports" / "momentum_real_market.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, default=float), encoding="utf-8")
    print(f"\nWrote consolidated report to {out_path}")


if __name__ == "__main__":
    main()
