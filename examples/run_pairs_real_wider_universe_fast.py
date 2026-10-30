#!/usr/bin/env python3
"""Wider universe real-market validation (2+ additional pairs/assets)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backtest.engine import BacktestEngine
from backtest.sweep import run_parameter_sweep
from data.loader import DataLoader
from strategies.pairs_trading import CointegrationPairsStrategy

PAIRS = [("BTC", "ETH"), ("ETH", "SOL"), ("BTC", "SOL"), ("ADA", "ETH"), ("XRP", "BTC"), ("BNB", "ETH")]
SYMBOLS = ["BTC", "ETH", "SOL", "ADA", "XRP", "BNB"]
START = "2026-04-01"
END = "2026-10-30"
FREQ = "1h"


def run_for_pair(pair: tuple[str, str], data, grid, engine: BacktestEngine):
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
        show_progress=False,
    )
    if not rows:
        raise RuntimeError(f"No sweep results for pair {pair}")
    top = rows[0]
    params = {
        k: top[k]
        for k in ("lookback", "entry_threshold", "cointegration_pvalue")
        if k in top
    }
    benchmark = engine.run_with_benchmark(
        CointegrationPairsStrategy(pair=pair, **params),
        data,
        fee_rate=0.001,
        slippage=0.0005,
    )
    return top, benchmark


def main() -> None:
    print("Starting wider universe validation...")
    loader = DataLoader()
    try:
        data = loader.load_binance_data(SYMBOLS, START, END, interval=FREQ)
        data = loader.clean_data(data)
        print(f"Loaded {len(data)} bars")
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    grid = {
        "lookback": [60, 120],
        "entry_threshold": [2.0, 2.5],
        "cointegration_pvalue": [0.05, 0.10],
    }
    engine = BacktestEngine(initial_capital=100_000.0)

    results = {}
    for pair in PAIRS:
        print(f"Validating {pair[0]}/{pair[1]}...")
        try:
            top, benchmark = run_for_pair(pair, data, grid, engine)
            replay = top.get("replay") or {}
            results["/".join(pair)] = {
                "pair": list(pair),
                "top_ranked": {k: v for k, v in top.items() if k != "replay"},
                "replay": replay,
                "benchmark_total_return": benchmark["benchmark_total_return"],
            }
            print(f"  done: {pair[0]}/{pair[1]}")
        except Exception as e:
            print(f"  Failed for {pair}: {e}")
            results["/".join(pair)] = {"pair": list(pair), "error": str(e)}

    out = {
        "symbols": SYMBOLS,
        "start": START,
        "end": END,
        "freq": FREQ,
        "n_bars": int(len(data)),
        "grid": grid,
        "walk_forward": {
            "train_period": 500,
            "test_period": 100,
            "mode": "rolling",
            "n_splits": 4,
            "metric": "calmar_ratio",
        },
        "pairs": results,
        "wider_universe": True,
    }
    out_path = Path(__file__).resolve().parent.parent / "reports" / "pairs_real_market_wider_universe.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, default=float), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
