#!/usr/bin/env python3
"""Transaction-cost sensitivity sweep for a portfolio of cointegration pairs.

Uses real public Binance spot candles for BTC/ETH/SOL, constructs a combined
portfolio by aggregating weights from the top-ranked combos of each pair
(BTC/ETH, ETH/SOL, BTC/SOL) from walk-forward selection, runs cost-sensitivity
across a grid of (fee_rate, slippage), and writes a JSON-serializable artifact
to reports/cost_sensitivity_real_portfolio.json.

RESEARCH/DEMO ONLY: this is not investment advice.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

from backtest.engine import BacktestEngine
from backtest.sweep import run_parameter_sweep
from data.loader import DataLoader
from strategies.pairs_trading import CointegrationPairsStrategy

PAIRS = [("BTC", "ETH"), ("ETH", "SOL"), ("BTC", "SOL")]
SYMBOLS = ["BTC", "ETH", "SOL"]
START = "2026-04-01"
END = "2026-10-28"
FREQ = "1h"
COST_GRID = [
    (0.0, 0.0),
    (0.0005, 0.0),
    (0.001, 0.00025),
    (0.001, 0.0005),
    (0.002, 0.0005),
    (0.002, 0.001),
]
GRID = {
    "lookback": [60, 120],
    "entry_threshold": [2.0, 2.5],
    "cointegration_pvalue": [0.05, 0.10],
}


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

    engine = BacktestEngine(initial_capital=100_000.0)

    # Find top-ranked params for each pair
    top_params = {}
    for pair in PAIRS:
        print(f"\n=== Selecting top combo for {pair[0]}/{pair[1]} ===")
        rows = run_parameter_sweep(
            CointegrationPairsStrategy(pair=pair),
            data,
            GRID,
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
            k: top[k] for k in ("lookback", "entry_threshold", "cointegration_pvalue") if k in top
        }
        top_params["/".join(pair)] = params
        print(f"  Top: {params}")

    # Build combined portfolio weights by summing pair strategy weights
    # (equal allocation to each pair by construction of summing signals)
    combined_weights = pd.DataFrame(0.0, index=data.index, columns=SYMBOLS)
    for pair in PAIRS:
        strat = CointegrationPairsStrategy(pair=pair, **top_params["/".join(pair)])
        signals = strat.generate_signals(data)
        # Extract weights for the pair assets
        for asset in pair:
            if asset in signals.columns:
                combined_weights[asset] = combined_weights[asset].add(
                    signals[asset].reindex(data.index).fillna(0.0), fill_value=0.0
                )

    # Normalize to gross leverage of 1.0 (scale so |weights| sum appropriately)
    # For pairs each is market-neutral-ish; sum across pairs gives combined exposure
    # Keep as-is but ensure finite; engine will handle
    combined_weights = combined_weights.fillna(0.0)

    def eval_at_cost(fee_rate: float, slippage: float) -> dict:
        res = engine.run_portfolio(
            combined_weights,
            data,
            fee_rate=fee_rate,
            slippage=slippage,
        )
        return res

    results_rows = []
    base_res = None
    for fee_rate, slippage in COST_GRID:
        res = eval_at_cost(fee_rate, slippage)
        if fee_rate == 0.0 and slippage == 0.0:
            base_res = res
        row = {
            "fee_rate": float(fee_rate),
            "slippage": float(slippage),
            "total_return": float(res.get("total_return", 0.0)),
            "sharpe_ratio": float(res.get("sharpe_ratio", 0.0)),
            "max_drawdown": float(res.get("max_drawdown", 0.0)),
            "max_drawdown_duration": float(res.get("max_drawdown_duration", 0.0))
            if res.get("max_drawdown_duration") is not None
            else None,
            "calmar_ratio": float(res.get("calmar_ratio", 0.0)),
            "sortino_ratio": float(res.get("sortino_ratio", 0.0)),
            "var": float(res.get("var", 0.0)),
            "cvar": float(res.get("cvar", 0.0)),
            "final_equity": float(res.get("final_equity", engine.initial_capital)),
        }
        results_rows.append(row)
        print(
            f"  costs fee={fee_rate:.4f} slip={slippage:.4f} -> "
            f"total_return={row['total_return']:.4%} sharpe={row['sharpe_ratio']:.4f} "
            f"max_dd={row['max_drawdown']:.4%}"
        )

    out = {
        "type": "pairs_portfolio_cost_sensitivity",
        "symbols": SYMBOLS,
        "pairs": ["/".join(p) for p in PAIRS],
        "start": START,
        "end": END,
        "freq": FREQ,
        "n_bars": int(len(data)),
        "top_ranked_params": top_params,
        "grid": [{"fee_rate": f, "slippage": s} for f, s in COST_GRID],
        "rows": results_rows,
        "base": {
            "zero_cost_total_return": float(base_res.get("total_return", 0.0)) if base_res else 0.0,
            "zero_cost_final_equity": float(base_res.get("final_equity", engine.initial_capital))
            if base_res
            else float(engine.initial_capital),
        },
    }

    out_path = (
        Path(__file__).resolve().parent.parent / "reports" / "cost_sensitivity_real_portfolio.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, default=float), encoding="utf-8")
    print(f"\nWrote portfolio cost sensitivity to {out_path}")


if __name__ == "__main__":
    main()
