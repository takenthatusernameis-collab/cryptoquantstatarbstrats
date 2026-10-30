#!/usr/bin/env python3
"""Transaction-cost sensitivity sweep for the cointegration pairs strategy.

Uses real public Binance spot candles for BTC/ETH, runs the top-ranked combo
from the walk-forward sweep across a grid of (fee_rate, slippage) cost
assumptions, and records how total_return / sharpe_ratio / max_drawdown change
as costs rise. Results are appended to reports/cost_sensitivity_real.json under a
``cost_sensitivity`` block.

RESEARCH/DEMO ONLY: this is not investment advice. A result showing the strategy
stays unprofitable across realistic costs is a valid research outcome.
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
from utils.reporting import sweep_cost_sensitivity

PAIR = ("ETH", "SOL")
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
    grid = {
        "lookback": [60, 120],
        "entry_threshold": [2.0, 2.5],
        "cointegration_pvalue": [0.05, 0.10],
    }

    rows = run_parameter_sweep(
        CointegrationPairsStrategy(pair=PAIR),
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
    params = {
        k: top[k]
        for k in ("lookback", "entry_threshold", "cointegration_pvalue")
        if k in top
    }
    print(
        f"Top-ranked combo: lookback={params.get('lookback')} "
        f"entry_threshold={params.get('entry_threshold')} "
        f"cointegration_pvalue={params.get('cointegration_pvalue')}"
    )

    strat = CointegrationPairsStrategy(pair=PAIR, **params)

    def wf_fn(fee_rate: float, slippage: float) -> dict:
        return engine.walk_forward(
            strat,
            data,
            train_period=500,
            test_period=100,
            fee_rate=fee_rate,
            slippage=slippage,
            mode="rolling",
            n_splits=4,
        )

    sweep = sweep_cost_sensitivity(wf_fn, COST_GRID)

    # Replay the top-ranked combo at each cost config to report full-dataset
    # metrics (total_return / sharpe / max_drawdown / final_equity).
    # Only scalar metrics are kept: the engine also returns equity_curve,
    # weights, portfolio_returns, and returns (Series/DataFrame) which are not
    # JSON-serializable and are not needed for this report. final_equity is
    # derived from the equity curve (initial_capital * last equity multiple),
    # matching the replay block produced by backtest.sweep.
    SCALAR_KEYS = (
        "total_return",
        "sharpe_ratio",
        "max_drawdown",
        "max_drawdown_duration",
        "calmar_ratio",
        "sortino_ratio",
        "var",
        "cvar",
    )
    for row in sweep:
        replay = engine.run(
            strat,
            data,
            fee_rate=row["fee_rate"],
            slippage=row["slippage"],
        )
        replay_block = {
            "params": dict(params),
            **{k: replay.get(k) for k in SCALAR_KEYS if k in replay},
        }
        equity_curve = replay.get("equity_curve")
        try:
            replay_block["final_equity"] = float(
                engine.initial_capital
            ) * float(equity_curve.iloc[-1])
        except Exception:
            replay_block["final_equity"] = None
        row["replay"] = replay_block
        print(
            f"  costs fee={row['fee_rate']:.4f} slip={row['slippage']:.4f} -> "
            f"OOS return={row['oos_mean_return']:.6f} "
            f"replay total_return={row['replay']['total_return']:.4%}"
        )

    out_path = (
        Path(__file__).resolve().parent.parent / "reports" / "cost_sensitivity_real.json"
    )
    clean_rows = []
    for row in sweep:
        clean = {k: v for k, v in row.items() if k != "result"}
        clean_rows.append(clean)
    report = {
        "pair": list(PAIR),
        "symbols": SYMBOLS,
        "start": START,
        "end": END,
        "freq": FREQ,
        "cost_sensitivity": {
            "pair": list(PAIR),
            "grid": [{"fee_rate": f, "slippage": s} for f, s in COST_GRID],
            "rows": clean_rows,
        },
    }
    out_path.write_text(
        json.dumps(report, indent=2, default=float), encoding="utf-8"
    )
    print(f"\nAppended cost sensitivity to {out_path}")


if __name__ == "__main__":
    main()
