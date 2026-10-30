#!/usr/bin/env python3
"""Real-data paper-trading simulation on public Binance spot candles.

Runs a simple paper-trading loop for the top-ranked pairs combos from
reports/pairs_real_market.json using DataLoader.load_binance_data() (no
API key), records fills/slippage/fees/equity curve/drawdown, and produces
reports/paper_trading_real.json (JSON-serializable).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd

from backtest.engine import BacktestEngine
from backtest.execution import ExecutionSimulator
from backtest.paper_report import build_paper_trading_report
from data.loader import DataLoader
from strategies.pairs_trading import CointegrationPairsStrategy


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
    print(
        f"Loaded {len(data)} hourly bars for {', '.join(SYMBOLS)} "
        f"({data.index.min().date()} -> {data.index.max().date()})"
    )

    # Top-ranked params from reports/pairs_real_market.json
    top_params = {
        ("BTC", "ETH"): {"lookback": 120, "entry_threshold": 2.5, "cointegration_pvalue": 0.05},
        ("ETH", "SOL"): {"lookback": 120, "entry_threshold": 2.5, "cointegration_pvalue": 0.05},
        ("BTC", "SOL"): {"lookback": 120, "entry_threshold": 2.0, "cointegration_pvalue": 0.1},
    }

    engine = BacktestEngine(initial_capital=100_000.0)
    sim = ExecutionSimulator(participation_rate=0.1, slippage_bps=SLIPPAGE * 10000.0)

    all_fills = []
    order_counter = 0
    equity_curve = []
    realized_pnl_total = 0.0

    # Run paper trading simulation per pair (simple stepwise simulation)
    for pair in PAIRS:
        strat = CointegrationPairsStrategy(pair=pair, **top_params[pair])
        signals = strat.generate_signals(data)
        pair_fills = []
        for ts in data.index:
            # For pairs, we get weights per asset
            try:
                w_a = float(signals.loc[ts, pair[0]]) if pair[0] in signals.columns else 0.0
                w_b = float(signals.loc[ts, pair[1]]) if pair[1] in signals.columns else 0.0
            except Exception:
                w_a, w_b = 0.0, 0.0
            # Simple discrete fill when weights change significantly (mock)
            if abs(w_a) > 1e-12:
                side = "buy" if w_a > 0 else "sell"
                qty = abs(w_a) * 10000.0  # notional scaling for paper
                price = float(data.loc[ts, pair[0]])
                order_counter += 1
                res = sim.simulate_order(
                    "market",
                    side,
                    qty,
                    price,
                    bar_volume=0.0,
                    order_id=order_counter,
                    symbol=pair[0],
                    timestamp=str(ts),
                    fee_rate=FEE_RATE,
                )
                fee = abs(res["filled_qty"]) * price * FEE_RATE
                f = {
                    "order_id": order_counter,
                    "pair": f"{pair[0]}/{pair[1]}",
                    "symbol": pair[0],
                    "side": side,
                    "quantity": res["filled_qty"],
                    "price": res["avg_price"],
                    "fee": fee,
                    "timestamp": str(ts),
                    "status": res["status"],
                    "slippage_bps": SLIPPAGE * 10000.0,
                }
                pair_fills.append(f)
                all_fills.append(f)
                realized_pnl_total -= fee
            if abs(w_b) > 1e-12:
                side = "buy" if w_b > 0 else "sell"
                qty = abs(w_b) * 10000.0
                price = float(data.loc[ts, pair[1]])
                order_counter += 1
                res = sim.simulate_order(
                    "market",
                    side,
                    qty,
                    price,
                    bar_volume=0.0,
                    order_id=order_counter,
                    symbol=pair[1],
                    timestamp=str(ts),
                    fee_rate=FEE_RATE,
                )
                fee = abs(res["filled_qty"]) * price * FEE_RATE
                f = {
                    "order_id": order_counter,
                    "pair": f"{pair[0]}/{pair[1]}",
                    "symbol": pair[1],
                    "side": side,
                    "quantity": res["filled_qty"],
                    "price": res["avg_price"],
                    "fee": fee,
                    "timestamp": str(ts),
                    "status": res["status"],
                    "slippage_bps": SLIPPAGE * 10000.0,
                }
                pair_fills.append(f)
                all_fills.append(f)
                realized_pnl_total -= fee
        equity_curve.append(
            {"timestamp": str(data.index[-1]), "equity": sim.get_portfolio_value(engine.initial_capital)}
        )

    # Compute drawdown
    eq_vals = []
    for ec in equity_curve:
        try:
            eq_vals.append(float(ec["equity"]))
        except Exception:
            pass
    if not eq_vals:
        eq_vals = [float(engine.initial_capital)]
    peak = eq_vals[0]
    max_dd = 0.0
    for v in eq_vals:
        if v > peak:
            peak = v
        dd = (v - peak) / peak if peak > 0 else 0.0
        if dd < max_dd:
            max_dd = dd

    summary = {
        "initial_capital": float(engine.initial_capital),
        "realized_pnl": float(realized_pnl_total),
        "num_fills": len(all_fills),
        "portfolio_value": float(sim.get_portfolio_value(engine.initial_capital)),
        "equity_curve_summary": {
            "start_equity": eq_vals[0],
            "end_equity": eq_vals[-1],
            "max_equity": max(eq_vals) if eq_vals else eq_vals[0],
            "min_equity": min(eq_vals) if eq_vals else eq_vals[0],
            "max_drawdown": float(max_dd),
        },
        "fills": all_fills,
        "positions": {
            k: {
                "quantity": v.quantity,
                "avg_cost": v.avg_cost,
                "unrealized_pnl": v.unrealized_pnl,
            }
            for k, v in sim.get_positions().items()
        },
        "risk_metrics": sim.get_risk_metrics(),
    }

    report = build_paper_trading_report(
        session_summary=summary,
        fills=all_fills,
        equity_curve=equity_curve,
        positions=summary.get("positions"),
        metadata={
            "initial_capital": float(engine.initial_capital),
            "symbols": SYMBOLS,
            "pairs": ["/".join(p) for p in PAIRS],
            "start": START,
            "end": END,
            "freq": FREQ,
            "fee_rate": FEE_RATE,
            "slippage": SLIPPAGE,
            "data_source": "binance_public",
        },
    )
    # Ensure required fields
    report["equity_curve_summary"] = summary["equity_curve_summary"]
    report["session_summary"]["equity_curve_summary"] = summary["equity_curve_summary"]
    report["fees"] = {"total_fees": float(-realized_pnl_total) if realized_pnl_total < 0 else 0.0}
    report["slippage"] = {"slippage_bps": SLIPPAGE * 10000.0}
    report["drawdown"] = {"max_drawdown": float(max_dd)}

    out_path = Path(__file__).resolve().parent.parent / "reports" / "paper_trading_real.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, default=float), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
