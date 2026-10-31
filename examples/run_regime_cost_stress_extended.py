#!/usr/bin/env python3
"""Extended regime/cost-stress slices across pairs/regimes."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backtest.engine import BacktestEngine
from data.loader import DataLoader
from strategies.pairs_trading import CointegrationPairsStrategy

PAIRS = [
    ("BTC", "ETH"),
    ("ETH", "SOL"),
    ("BTC", "SOL"),
    ("ADA", "ETH"),
    ("XRP", "BTC"),
    ("BNB", "ETH"),
]
SYMBOLS = ["BTC", "ETH", "SOL", "ADA", "XRP", "BNB"]
START = "2026-04-01"
END = "2026-10-30"
FREQ = "1h"


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
        ("ADA", "ETH"): {"lookback": 120, "entry_threshold": 2.5, "cointegration_pvalue": 0.05},
        ("XRP", "BTC"): {"lookback": 120, "entry_threshold": 2.5, "cointegration_pvalue": 0.05},
        ("BNB", "ETH"): {"lookback": 120, "entry_threshold": 2.0, "cointegration_pvalue": 0.05},
    }

    fee_slip_grid = [
        (0.0, 0.0),
        (0.0005, 0.00025),
        (0.001, 0.0005),
        (0.002, 0.001),
    ]

    engine = BacktestEngine(initial_capital=100_000.0)
    cost_stress = {}
    for pair in PAIRS:
        cost_stress["/".join(pair)] = {}
        for fee, slip in fee_slip_grid:
            try:
                res = engine.run(
                    CointegrationPairsStrategy(
                        pair=pair,
                        **top_params.get(
                            pair,
                            {"lookback": 120, "entry_threshold": 2.5, "cointegration_pvalue": 0.05},
                        ),
                    ),
                    data,
                    fee_rate=fee,
                    slippage=slip,
                )
                cost_stress["/".join(pair)][f"fee_{fee}_slip_{slip}"] = {
                    "total_return": res.get("total_return"),
                    "sharpe_ratio": res.get("sharpe_ratio"),
                    "max_drawdown": res.get("max_drawdown"),
                    "calmar_ratio": res.get("calmar_ratio"),
                    "final_equity": res.get("final_equity"),
                }
            except Exception as e:
                cost_stress["/".join(pair)][f"fee_{fee}_slip_{slip}"] = {"error": str(e)}

    # regime slices
    n = len(data)
    regimes = {
        "full": (data.index[0], data.index[-1]),
        "early": (data.index[0], data.index[n // 2]),
        "late": (data.index[n // 2], data.index[-1]),
    }
    regime_results = {}
    for regime_name, (start_ts, end_ts) in regimes.items():
        regime_results[regime_name] = {}
        mask = (data.index >= start_ts) & (data.index <= end_ts)
        dreg = data.loc[mask]
        for pair in PAIRS[:3]:
            try:
                res = engine.run(
                    CointegrationPairsStrategy(
                        pair=pair,
                        **top_params.get(
                            pair,
                            {"lookback": 120, "entry_threshold": 2.5, "cointegration_pvalue": 0.05},
                        ),
                    ),
                    dreg,
                    fee_rate=0.001,
                    slippage=0.0005,
                )
                regime_results[regime_name]["/".join(pair)] = {
                    "total_return": res.get("total_return"),
                    "sharpe_ratio": res.get("sharpe_ratio"),
                    "max_drawdown": res.get("max_drawdown"),
                    "calmar_ratio": res.get("calmar_ratio"),
                }
            except Exception as e:
                regime_results[regime_name]["/".join(pair)] = {"error": str(e)}

    out = {
        "symbols": SYMBOLS,
        "pairs": ["/".join(p) for p in PAIRS],
        "start": START,
        "end": END,
        "freq": FREQ,
        "data_source": "binance_public",
        "oos_extended": True,
        "wider_universe": True,
        "cost_stress": cost_stress,
        "regime_slices": regime_results,
    }
    out_path = (
        Path(__file__).resolve().parent.parent / "reports" / "regime_cost_stress_extended.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, default=float), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
