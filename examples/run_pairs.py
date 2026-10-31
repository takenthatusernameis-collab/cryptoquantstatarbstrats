#!/usr/bin/env python3
"""Real-market validation of the cointegration pairs strategy.

This example fetches **public Binance spot candles** (no API key required) for
the requested pair, runs a walk-forward parameter sweep of
``CointegrationPairsStrategy``, replays the top-ranked combo over the full
dataset, and compares it against an equal-weighted buy-and-hold benchmark on
the same window.

RESEARCH/DEMO ONLY: this is not investment advice. A negative result against
the benchmark is a valid research outcome and should be reported as such.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backtest.engine import BacktestEngine
from backtest.sweep import run_parameter_sweep
from data.loader import DataLoader
from strategies.pairs_trading import CointegrationPairsStrategy


def main() -> None:
    print(
        "RESEARCH/DEMO ONLY: uses real public Binance spot candles. Results are not "
        "evidence of a trading edge and are not investment advice."
    )

    pair = ("BTC", "ETH")
    symbols = ["BTC", "ETH", "SOL"]
    start = "2026-04-01"
    end = "2026-10-28"
    freq = "1h"

    loader = DataLoader()
    data = loader.load_binance_data(symbols, start, end, interval=freq)
    data = loader.clean_data(data)
    print(
        f"Loaded {len(data)} hourly bars for {', '.join(symbols)} "
        f"({data.index.min().date()} -> {data.index.max().date()})"
    )

    grid = {
        "lookback": [60, 120],
        "entry_threshold": [2.0, 2.5],
        "cointegration_pvalue": [0.05, 0.10],
    }
    engine = BacktestEngine(initial_capital=100_000.0)

    rows = run_parameter_sweep(
        CointegrationPairsStrategy(pair=pair),
        data,
        grid,
        train_period=500,
        test_period=100,
        fee_rate=0.001,
        slippage=0.0005,
        metric="calmar_ratio",
        engine=engine,
        mode="rolling",
        n_splits=4,
        replay_best=True,
        show_progress=True,
    )

    top = rows[0]
    replay = top.get("replay") or {}
    print("\nTop-ranked combo (out-of-sample walk-forward):")
    print(
        f"  lookback={top['lookback']} entry_threshold={top['entry_threshold']} "
        f"cointegration_pvalue={top['cointegration_pvalue']}"
    )
    print(
        f"  OOS mean return={top['oos_mean_return']:.6f} "
        f"OOS/IS ratio={top['oos_is_ratio']:.4f} "
        f"OOS periods={top['oos_periods']}"
    )

    print("\nReplay over full dataset:")
    print(
        f"  total_return={replay.get('total_return', 0.0):.4%} "
        f"sharpe_ratio={replay.get('sharpe_ratio', 0.0):.4f} "
        f"max_drawdown={replay.get('max_drawdown', 0.0):.4%} "
        f"calmar_ratio={replay.get('calmar_ratio', 0.0):.4f} "
        f"final_equity={replay.get('final_equity', 0.0):,.2f}"
    )

    params = {
        k: v for k, v in top.items() if k in ("lookback", "entry_threshold", "cointegration_pvalue")
    }
    benchmark = engine.run_with_benchmark(
        CointegrationPairsStrategy(pair=pair, **params),
        data,
        fee_rate=0.001,
        slippage=0.0005,
    )
    print("\nEqual-weighted buy-and-hold benchmark (BTC/ETH/SOL):")
    print(f"  total_return={benchmark['benchmark_total_return']:.4%}")

    out = {
        "pair": list(pair),
        "symbols": symbols,
        "start": start,
        "end": end,
        "freq": freq,
        "n_bars": int(len(data)),
        "grid": grid,
        "walk_forward": {
            "train_period": 500,
            "test_period": 100,
            "mode": "rolling",
            "n_splits": 4,
            "metric": "calmar_ratio",
        },
        "top_ranked": {k: v for k, v in top.items() if k != "replay"},
        "replay": replay,
        "benchmark_total_return": benchmark["benchmark_total_return"],
    }
    out_path = Path(__file__).resolve().parent.parent / "reports" / "pairs_real_market.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, default=float), encoding="utf-8")
    print(f"\nWrote report to {out_path}")


if __name__ == "__main__":
    main()
