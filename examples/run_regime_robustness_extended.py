#!/usr/bin/env python3
"""Regime/period robustness analysis on real Binance spot data with cost stress."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
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

COST_STRESS = [
    (0.0, 0.0),
    (0.001, 0.0005),
    (0.002, 0.001),
]


def split_periods(df: pd.DataFrame):
    n = len(df)
    thirds = [
        (0, n // 3),
        (n // 3, 2 * n // 3),
        (2 * n // 3, n),
    ]
    periods = []
    for i, (s, e) in enumerate(thirds):
        periods.append({
            "name": f"period_{i + 1}",
            "start_idx": int(s),
            "end_idx": int(e),
            "start_date": str(df.index[s].date()) if s < len(df) else None,
            "end_date": str(df.index[min(e - 1, len(df) - 1)].date()) if e > 0 else None,
        })
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
        "cost_stress": {
            "grid": [{"fee_rate": f, "slippage": s} for f, s in COST_STRESS],
            "pairs": {},
            "mean_reversion": {},
        },
    }

    # Pairs: use top configs from existing reports
    pairs_configs = [
        (("BTC", "ETH"), {"lookback": 120, "entry_threshold": 2.5, "cointegration_pvalue": 0.05}),
        (("ETH", "SOL"), {"lookback": 120, "entry_threshold": 2.5, "cointegration_pvalue": 0.05}),
        (("BTC", "SOL"), {"lookback": 120, "entry_threshold": 2.0, "cointegration_pvalue": 0.1}),
    ]
    for pair, pparams in pairs_configs:
        strat = CointegrationPairsStrategy(pair=pair, **pparams)
        for p in periods:
            sub = data.iloc[p["start_idx"]:p["end_idx"]]
            if len(sub) < 100:
                continue
            try:
                bench = engine.run_with_benchmark(strat, sub, fee_rate=0.001, slippage=0.0005)
                base = {
                    "pair": list(pair),
                    "period": p["name"],
                    "params": pparams,
                    "benchmark_total_return": bench["benchmark_total_return"],
                }
                slices = []
                for fee_rate, slippage in COST_STRESS:
                    res = engine.run(strat, sub, fee_rate=fee_rate, slippage=slippage)
                    slices.append({
                        "fee_rate": fee_rate,
                        "slippage": slippage,
                        "total_return": res["total_return"],
                        "sharpe_ratio": res["sharpe_ratio"],
                        "max_drawdown": res["max_drawdown"],
                        "calmar_ratio": res["calmar_ratio"],
                    })
                base["cost_stress_slices"] = slices
                out["pairs"][f"{pair[0]}/{pair[1]}_{p['name']}"] = base
                out["cost_stress"]["pairs"][f"{pair[0]}/{pair[1]}_{p['name']}"] = base
            except Exception as e:
                err = {"pair": list(pair), "period": p["name"], "error": str(e)}
                out["pairs"][f"{pair[0]}/{pair[1]}_{p['name']}"] = err
                out["cost_stress"]["pairs"][f"{pair[0]}/{pair[1]}_{p['name']}"] = err

    # Mean reversion: use top configs
    mr_configs = [
        ("BTC", {"lookback": 120, "entry_threshold": 1.5}),
        ("ETH", {"lookback": 50, "entry_threshold": 2.0}),
        ("SOL", {"lookback": 50, "entry_threshold": 2.0}),
    ]
    for asset, mparams in mr_configs:
        strat = MeanReversionStrategy(asset=asset, **mparams)
        for p in periods:
            sub = data.iloc[p["start_idx"]:p["end_idx"]]
            if len(sub) < 100:
                continue
            try:
                bench = engine.run_with_benchmark(strat, sub[[asset]], fee_rate=0.001, slippage=0.0005)
                base = {
                    "asset": asset,
                    "period": p["name"],
                    "params": mparams,
                    "benchmark_total_return": bench["benchmark_total_return"],
                }
                slices = []
                for fee_rate, slippage in COST_STRESS:
                    res = engine.run(strat, sub[[asset]], fee_rate=fee_rate, slippage=slippage)
                    slices.append({
                        "fee_rate": fee_rate,
                        "slippage": slippage,
                        "total_return": res["total_return"],
                        "sharpe_ratio": res["sharpe_ratio"],
                        "max_drawdown": res["max_drawdown"],
                        "calmar_ratio": res["calmar_ratio"],
                    })
                base["cost_stress_slices"] = slices
                out["mean_reversion"][f"{asset}_{p['name']}"] = base
                out["cost_stress"]["mean_reversion"][f"{asset}_{p['name']}"] = base
            except Exception as e:
                err = {"asset": asset, "period": p["name"], "error": str(e)}
                out["mean_reversion"][f"{asset}_{p['name']}"] = err
                out["cost_stress"]["mean_reversion"][f"{asset}_{p['name']}"] = err

    out_path = Path(__file__).resolve().parent.parent / "reports" / "regime_robustness_real.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, default=float), encoding="utf-8")
    print(f"Wrote extended report to {out_path}")


if __name__ == "__main__":
    main()
