#!/usr/bin/env python3
"""Regime/period robustness analysis on real Binance spot data.

Splits the window into subperiods and reports stability for top configs.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backtest.engine import BacktestEngine
from data.loader import DataLoader
from strategies.mean_reversion import MeanReversionStrategy
from strategies.pairs_trading import CointegrationPairsStrategy

SYMBOLS = ["BTC", "ETH", "SOL"]
START = "2026-04-01"
END = "2026-10-28"
FREQ = "1h"


def split_periods(df: pd.DataFrame):
    # Split into roughly equal thirds
    n = len(df)
    thirds = [
        (0, n // 3),
        (n // 3, 2 * n // 3),
        (2 * n // 3, n),
    ]
    periods = []
    for i, (s, e) in enumerate(thirds):
        periods.append(
            {
                "name": f"period_{i + 1}",
                "start_idx": int(s),
                "end_idx": int(e),
                "start_date": str(df.index[s].date()) if s < len(df) else None,
                "end_date": str(df.index[min(e - 1, len(df) - 1)].date()) if e > 0 else None,
            }
        )
    return periods


def main() -> None:
    print(
        "RESEARCH/DEMO ONLY: uses real public Binance spot candles. Results are not "
        "evidence of a trading edge and are not investment advice."
    )

    loader = DataLoader()
    data = loader.load_binance_data(SYMBOLS, START, END, interval=FREQ)
    data = loader.clean_data(data)
    print(f"Loaded {len(data)} hourly bars")

    periods = split_periods(data)
    engine = BacktestEngine(initial_capital=100_000.0)

    out = {
        "symbols": SYMBOLS,
        "start": START,
        "end": END,
        "freq": FREQ,
        "n_bars": int(len(data)),
        "periods": periods,
        "pairs": {},
        "mean_reversion": {},
    }

    # BTC/ETH as example
    try:
        pair = ("BTC", "ETH")
        strat = CointegrationPairsStrategy(
            pair=pair,
            lookback=120,
            entry_threshold=2.5,
            cointegration_pvalue=0.05,
        )
        for p in periods:
            sub = data.iloc[p["start_idx"] : p["end_idx"]]
            if len(sub) < 100:
                continue
            try:
                res = engine.run(strat, sub, fee_rate=0.001, slippage=0.0005)
                bench = engine.run_with_benchmark(strat, sub, fee_rate=0.001, slippage=0.0005)
                out["pairs"][f"{pair[0]}/{pair[1]}_{p['name']}"] = {
                    "pair": list(pair),
                    "period": p["name"],
                    "total_return": res["total_return"],
                    "sharpe_ratio": res["sharpe_ratio"],
                    "max_drawdown": res["max_drawdown"],
                    "calmar_ratio": res["calmar_ratio"],
                    "benchmark_total_return": bench["benchmark_total_return"],
                }
            except Exception as e:
                out["pairs"][f"{pair[0]}/{pair[1]}_{p['name']}"] = {"error": str(e)}
    except Exception as e:
        out["pairs"]["error"] = str(e)

    # Mean reversion
    try:
        for asset in ["BTC"]:
            strat = MeanReversionStrategy(asset=asset, lookback=120, entry_threshold=1.5)
            for p in periods:
                sub = data.iloc[p["start_idx"] : p["end_idx"]]
                if len(sub) < 100:
                    continue
                try:
                    res = engine.run(strat, sub[[asset]], fee_rate=0.001, slippage=0.0005)
                    bench = engine.run_with_benchmark(
                        strat,
                        sub[[asset]],
                        fee_rate=0.001,
                        slippage=0.0005,
                    )
                    out["mean_reversion"][f"{asset}_{p['name']}"] = {
                        "asset": asset,
                        "period": p["name"],
                        "total_return": res["total_return"],
                        "sharpe_ratio": res["sharpe_ratio"],
                        "max_drawdown": res["max_drawdown"],
                        "calmar_ratio": res["calmar_ratio"],
                        "benchmark_total_return": bench["benchmark_total_return"],
                    }
                except Exception as e:
                    out["mean_reversion"][f"{asset}_{p['name']}"] = {"error": str(e)}
    except Exception as e:
        out["mean_reversion"]["error"] = str(e)

    out_path = Path(__file__).resolve().parent.parent / "reports" / "regime_robustness_real.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, default=float), encoding="utf-8")
    print(f"Wrote report to {out_path}")


if __name__ == "__main__":
    main()
