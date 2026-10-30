#!/usr/bin/env python3
"""Monte Carlo robustness on real-data returns.

Uses real public Binance spot candles and top-ranked pairs combos, computes
returns, runs bootstrap/shuffle Monte Carlo resampling via utils.monte_carlo,
and produces reports/monte_carlo_real.json (JSON-serializable) with confidence
intervals for total return, Sharpe, max drawdown.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd

from backtest.engine import BacktestEngine
from data.loader import DataLoader
from strategies.pairs_trading import CointegrationPairsStrategy
from utils.monte_carlo import monte_carlo_analysis


PAIRS = [("BTC", "ETH"), ("ETH", "SOL"), ("BTC", "SOL")]
SYMBOLS = ["BTC", "ETH", "SOL"]
START = "2026-04-01"
END = "2026-10-28"
FREQ = "1h"
FEE_RATE = 0.001
SLIPPAGE = 0.0005


def main() -> None:
    print(
        "RESEARCH/DEMO ONLY: uses real public Binance spot candles. Results are not "
        "evidence of a trading edge and are not investment advice."
    )

    loader = DataLoader()
    data = loader.load_binance_data(SYMBOLS, START, END, interval=FREQ)
    data = loader.clean_data(data)

    top_params = {
        ("BTC", "ETH"): {"lookback": 120, "entry_threshold": 2.5, "cointegration_pvalue": 0.05},
        ("ETH", "SOL"): {"lookback": 120, "entry_threshold": 2.5, "cointegration_pvalue": 0.05},
        ("BTC", "SOL"): {"lookback": 120, "entry_threshold": 2.0, "cointegration_pvalue": 0.1},
    }

    engine = BacktestEngine(initial_capital=100_000.0)
    results = {
        "symbols": SYMBOLS,
        "pairs": ["/".join(p) for p in PAIRS],
        "start": START,
        "end": END,
        "freq": FREQ,
        "fee_rate": FEE_RATE,
        "slippage": SLIPPAGE,
        "data_source": "binance_public",
        "monte_carlo": {},
    }

    all_portfolio_returns = []
    for pair in PAIRS:
        strat = CointegrationPairsStrategy(pair=pair, **top_params[pair])
        res = engine.run(strat, data, fee_rate=FEE_RATE, slippage=SLIPPAGE)
        rets = res.get("portfolio_returns")
        if rets is not None:
            try:
                all_portfolio_returns.append(pd.Series(rets).fillna(0.0))
            except Exception:
                pass
        # Per-pair MC
        pair_mc_boot = monte_carlo_analysis(
            equity_curve=res.get("equity_curve"),
            n_simulations=1000,
            method="bootstrap",
            seed=12345,
        )
        pair_mc_shuffle = monte_carlo_analysis(
            equity_curve=res.get("equity_curve"),
            n_simulations=1000,
            method="shuffle",
            seed=12345,
        )
        results["monte_carlo"]["/".join(pair)] = {
            "bootstrap": pair_mc_boot,
            "shuffle": pair_mc_shuffle,
            "confidence_intervals": {
                "total_return": {
                    "p5": float((pair_mc_boot["final_equity"]["p5"] - 1.0)),
                    "p50": float((pair_mc_boot["final_equity"]["p50"] - 1.0)),
                    "p95": float((pair_mc_boot["final_equity"]["p95"] - 1.0)),
                },
                "sharpe_ratio": {
                    "p5": pair_mc_boot["sharpe_ratio"]["p5"],
                    "p50": pair_mc_boot["sharpe_ratio"]["p50"],
                    "p95": pair_mc_boot["sharpe_ratio"]["p95"],
                },
                "max_drawdown": {
                    "p5": pair_mc_boot["max_drawdown"]["p5"],
                    "p50": pair_mc_boot["max_drawdown"]["p50"],
                    "p95": pair_mc_boot["max_drawdown"]["p95"],
                    "ci95": pair_mc_boot["max_drawdown"]["ci95"],
                    "ci99": pair_mc_boot["max_drawdown"]["ci99"],
                },
            },
        }

    # Portfolio-level MC if we have returns
    if all_portfolio_returns:
        try:
            port_rets = sum(all_portfolio_returns) / len(all_portfolio_returns)
            port_mc_boot = monte_carlo_analysis(
                returns=port_rets,
                n_simulations=2000,
                method="bootstrap",
                seed=54321,
            )
            port_mc_shuffle = monte_carlo_analysis(
                returns=port_rets,
                n_simulations=2000,
                method="shuffle",
                seed=54321,
            )
            results["monte_carlo"]["portfolio"] = {
                "bootstrap": port_mc_boot,
                "shuffle": port_mc_shuffle,
                "confidence_intervals": {
                    "total_return": {
                        "p5": float((port_mc_boot["final_equity"]["p5"] - 1.0)),
                        "p50": float((port_mc_boot["final_equity"]["p50"] - 1.0)),
                        "p95": float((port_mc_boot["final_equity"]["p95"] - 1.0)),
                    },
                    "sharpe_ratio": {
                        "p5": port_mc_boot["sharpe_ratio"]["p5"],
                        "p50": port_mc_boot["sharpe_ratio"]["p50"],
                        "p95": port_mc_boot["sharpe_ratio"]["p95"],
                    },
                    "max_drawdown": {
                        "p5": port_mc_boot["max_drawdown"]["p5"],
                        "p50": port_mc_boot["max_drawdown"]["p50"],
                        "p95": port_mc_boot["max_drawdown"]["p95"],
                        "ci95": port_mc_boot["max_drawdown"]["ci95"],
                        "ci99": port_mc_boot["max_drawdown"]["ci99"],
                    },
                },
            }
        except Exception as e:
            results["monte_carlo"]["portfolio"] = {"error": str(e)}

    out_path = Path(__file__).resolve().parent.parent / "reports" / "monte_carlo_real.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2, default=float), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
