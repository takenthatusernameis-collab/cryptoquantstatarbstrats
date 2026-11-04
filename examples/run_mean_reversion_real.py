#!/usr/bin/env python3
"""Real-market validation of the single-asset MeanReversionStrategy.

Fetches public Binance spot candles (no API key required), runs a walk-forward
parameter sweep per asset (BTC, ETH, SOL) with replay_best=True, compares each
asset's top-ranked combo to an equal-weight buy-and-hold benchmark over the
same window, sweeps a transaction-cost sensitivity grid, and consolidates
results into reports/mean_reversion_real_market.json with full provenance
(real_data_only: true, fabricated_data: false).

This is a research/demonstration script. Its output is not evidence of a
trading edge and is not investment advice.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backtest.engine import BacktestEngine
from backtest.sweep import run_parameter_sweep
from data.loader import DataLoader
from strategies.mean_reversion import MeanReversionStrategy

ASSETS = ["BTC", "ETH", "SOL"]
START = "2026-04-01"
END = "2026-10-28"
FREQ = "1h"
FEE_RATE = 0.001
SLIPPAGE = 0.0005
GRID = {
    "lookback": [20, 30, 50, 120],
    "entry_threshold": [1.5, 2.0, 2.5],
}
COST_FEES = [0.0, 0.001, 0.002]
COST_SLIPPAGES = [0.0, 0.0005, 0.001]


def run_for_asset(asset: str, data, grid, engine: BacktestEngine):
    rows = run_parameter_sweep(
        MeanReversionStrategy(asset=asset),
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
    params = {k: top[k] for k in ("lookback", "entry_threshold") if k in top}
    benchmark = engine.run_with_benchmark(
        MeanReversionStrategy(asset=asset, **params),
        data[[asset]],
        fee_rate=FEE_RATE,
        slippage=SLIPPAGE,
    )
    return top, benchmark, params


def cost_sensitivity_grid(asset: str, params: dict, data, engine: BacktestEngine):
    grid = []
    for fee in COST_FEES:
        for slip in COST_SLIPPAGES:
            result = engine.run(
                MeanReversionStrategy(asset=asset, **params),
                data[[asset]],
                fee_rate=fee,
                slippage=slip,
            )
            grid.append(
                {
                    "fee_rate": fee,
                    "slippage": slip,
                    "total_return": float(result.get("total_return", 0.0)),
                    "sharpe_ratio": float(result.get("sharpe_ratio", 0.0)),
                    "max_drawdown": float(result.get("max_drawdown", 0.0)),
                    "calmar_ratio": float(result.get("calmar_ratio", 0.0)),
                    "final_equity": float(result.get("final_equity", 0.0)),
                }
            )
    return grid


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
    provenance = {
        "source": "examples.run_mean_reversion_real",
        "data_source": "binance_public_spot",
        "real_data_only": True,
        "fabricated_data": False,
        "computed_at": datetime.now(timezone.utc).isoformat(),
        "blocked_routes": [],
        "rationale": (
            "All candles fetched from public Binance spot klines (www.binance.com); "
            "no synthetic/fabricated candles/IV/volume used as evidence."
        ),
    }

    results = {}
    for asset in ASSETS:
        print(f"\n=== Validating mean reversion on {asset} ===")
        top, benchmark, params = run_for_asset(asset, data, GRID, engine)
        replay = top.get("replay") or {}
        print("Top-ranked combo (out-of-sample walk-forward):")
        print(f"  lookback={top['lookback']} entry_threshold={top['entry_threshold']}")
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
        cost_grid = cost_sensitivity_grid(asset, params, data, engine)
        print(
            f"Cost sensitivity: {len(cost_grid)} fee x slippage points "
            f"(fees={COST_FEES}, slippages={COST_SLIPPAGES})"
        )
        results[asset] = {
            "asset": asset,
            "top_ranked": {k: v for k, v in top.items() if k != "replay"},
            "replay": replay,
            "benchmark_total_return": benchmark["benchmark_total_return"],
            "cost_sensitivity": cost_grid,
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
        "cost_sensitivity_grid": {
            "fee_rates": COST_FEES,
            "slippages": COST_SLIPPAGES,
        },
        "assets_results": results,
        "provenance": provenance,
    }
    out_path = (
        Path(__file__).resolve().parent.parent / "reports" / "mean_reversion_real_market.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, default=float), encoding="utf-8")
    print(f"\nWrote consolidated report to {out_path}")


if __name__ == "__main__":
    main()
