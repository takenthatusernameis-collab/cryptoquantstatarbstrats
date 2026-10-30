#!/usr/bin/env python3
"""OOS real-market validation of cointegration pairs strategy beyond previous window."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backtest.engine import BacktestEngine
from backtest.sweep import run_parameter_sweep
from data.loader import DataLoader
from strategies.pairs_trading import CointegrationPairsStrategy


PAIRS = [("BTC", "ETH"), ("ETH", "SOL"), ("BTC", "SOL")]
SYMBOLS = ["BTC", "ETH", "SOL"]
START = "2026-04-01"
END = "2026-10-30"  # extended beyond 2026-10-28
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
        show_progress=True,
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
    print(
        "RESEARCH/DEMO ONLY: uses real public Binance spot candles. Results are not "
        "evidence of a trading edge and are not investment advice."
    )

    loader = DataLoader()
    data = loader.load_binance_data(SYMBOLS, START, END, interval=FREQ)
    data = loader.clean_data(data)
    print(
        f"Loaded {len(data)} hourly bars for {', '.join(SYMBOLS)} "
        f"({data.index.min().date()} -> {data.index.max().date()})"
    )

    grid = {
        "lookback": [60, 120],
        "entry_threshold": [2.0, 2.5],
        "cointegration_pvalue": [0.05, 0.10],
    }
    engine = BacktestEngine(initial_capital=100_000.0)

    results = {}
    for pair in PAIRS:
        print(f"\n=== Validating pair {pair[0]}/{pair[1]} ===")
        top, benchmark = run_for_pair(pair, data, grid, engine)
        replay = top.get("replay") or {}
        print("Top-ranked combo (out-of-sample walk-forward):")
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
        print(
            f"\nEqual-weighted buy-and-hold benchmark ({pair[0]}/{pair[1]}): "
            f"{benchmark['benchmark_total_return']:.4%}"
        )
        results["/".join(pair)] = {
            "pair": list(pair),
            "top_ranked": {k: v for k, v in top.items() if k != "replay"},
            "replay": replay,
            "benchmark_total_return": benchmark["benchmark_total_return"],
        }

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
        "pair": results["BTC/ETH"]["pair"],
        "top_ranked": results["BTC/ETH"]["top_ranked"],
        "replay": results["BTC/ETH"]["replay"],
        "benchmark_total_return": results["BTC/ETH"]["benchmark_total_return"],
        "oos_extended": True,
    }
    out_path = Path(__file__).resolve().parent.parent / "reports" / "pairs_real_market_oos.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, default=float), encoding="utf-8")
    print(f"\nWrote consolidated report to {out_path}")


if __name__ == "__main__":
    main()
