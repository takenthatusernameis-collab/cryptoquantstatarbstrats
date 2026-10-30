#!/usr/bin/env python3
"""Longer-horizon walk-forward sweeps on real data."""

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
END = "2026-10-30"
FREQ = "1h"


def main() -> None:
    print("Longer-horizon walk-forward...")
    loader = DataLoader()
    data = loader.load_binance_data(SYMBOLS, START, END, interval=FREQ)
    data = loader.clean_data(data)
    print(f"Loaded {len(data)} bars")

    grid = {
        "lookback": [60, 120],
        "entry_threshold": [2.0, 2.5],
        "cointegration_pvalue": [0.05, 0.10],
    }
    engine = BacktestEngine(initial_capital=100_000.0)

    results = {}
    for pair in PAIRS:
        print(f"Validating {pair[0]}/{pair[1]}...")
        rows = run_parameter_sweep(
            CointegrationPairsStrategy(pair=pair),
            data,
            grid,
            train_period=1000,
            test_period=200,
            fee_rate=0.001,
            slippage=0.0005,
            metric="calmar_ratio",
            engine=engine,
            mode="rolling",
            n_splits=6,
            replay_best=True,
            show_progress=False,
        )
        if rows:
            top = rows[0]
            results["/".join(pair)] = {
                "pair": list(pair),
                "top_ranked": {k: v for k, v in top.items() if k != "replay"},
                "replay": top.get("replay") or {},
                "oos_is_ratio": top.get("oos_is_ratio"),
                "oos_mean_return": top.get("oos_mean_return"),
            }
        else:
            results["/".join(pair)] = {"pair": list(pair), "error": "no results"}

    out = {
        "symbols": SYMBOLS,
        "start": START,
        "end": END,
        "freq": FREQ,
        "n_bars": int(len(data)),
        "grid": grid,
        "walk_forward": {
            "train_period": 1000,
            "test_period": 200,
            "mode": "rolling",
            "n_splits": 6,
            "metric": "calmar_ratio",
        },
        "pairs": results,
        "longer_horizon": True,
    }
    out_path = Path(__file__).resolve().parent.parent / "reports" / "pairs_real_market_longer_walkforward.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, default=float), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
