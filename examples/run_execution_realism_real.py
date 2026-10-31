#!/usr/bin/env python3
"""Execution realism on real-data paper trading with VWAP/TWAP/LOB.

Compares naive fills vs VWAP, TWAP, and Limit Order Book (LOB) execution
models on real Binance spot data using top-ranked pairs combos; produces
reports/execution_realism_real.json (JSON-serializable).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backtest.execution import ExecutionSimulator
from data.loader import DataLoader
from strategies.pairs_trading import CointegrationPairsStrategy

PAIRS = [("BTC", "ETH"), ("ETH", "SOL"), ("BTC", "SOL")]
SYMBOLS = ["BTC", "ETH", "SOL"]
START = "2026-04-01"
END = "2026-10-28"
FREQ = "1h"
FEE_RATE = 0.001


def run_exec_model(order_type: str, lob_config: dict | None = None):
    loader = DataLoader()
    data = loader.load_binance_data(SYMBOLS, START, END, interval=FREQ)
    data = loader.clean_data(data)

    top_params = {
        ("BTC", "ETH"): {"lookback": 120, "entry_threshold": 2.5, "cointegration_pvalue": 0.05},
        ("ETH", "SOL"): {"lookback": 120, "entry_threshold": 2.5, "cointegration_pvalue": 0.05},
        ("BTC", "SOL"): {"lookback": 120, "entry_threshold": 2.0, "cointegration_pvalue": 0.1},
    }

    sim = ExecutionSimulator(participation_rate=0.1, slippage_bps=5.0)
    if lob_config:
        sim.lob_depth_levels = lob_config.get("depth_levels", 3)
        sim.lob_market_impact_bps = lob_config.get("market_impact_bps", 5.0)
        sim.lob_slippage_bps = lob_config.get("slippage_bps", 0.0)
        from backtest.execution import LimitOrderBookExecution

        sim._lob = LimitOrderBookExecution(
            depth_levels=sim.lob_depth_levels,
            market_impact_bps=sim.lob_market_impact_bps,
            slippage_bps=sim.lob_slippage_bps,
            participation_rate=sim.participation_rate,
            level_liquidity=lob_config.get("level_liquidity"),
            queue_position=lob_config.get("queue_position", 0.0),
        )

    total_fees = 0.0
    total_slippage_cost = 0.0
    fills = 0
    for pair in PAIRS:
        strat = CointegrationPairsStrategy(pair=pair, **top_params[pair])
        signals = strat.generate_signals(data)
        for ts in data.index[:200]:  # sample for efficiency but real data
            try:
                w_a = float(signals.loc[ts, pair[0]]) if pair[0] in signals.columns else 0.0
                w_b = float(signals.loc[ts, pair[1]]) if pair[1] in signals.columns else 0.0
            except Exception:
                continue
            for sym, w in [(pair[0], w_a), (pair[1], w_b)]:
                if abs(w) < 1e-12:
                    continue
                side = "buy" if w > 0 else "sell"
                qty = abs(w) * 1000.0
                price = float(data.loc[ts, sym])
                try:
                    vol = float(data[sym].pct_change().abs().rolling(20).mean().iloc[-1]) * 1e6
                except Exception:
                    vol = 1000.0
                res = sim.simulate_order(
                    order_type,
                    side,
                    qty,
                    price,
                    bar_volume=vol,
                    bar_high=price * 1.001,
                    bar_low=price * 0.999,
                    order_id=fills + 1,
                    symbol=sym,
                    timestamp=str(ts),
                    fee_rate=FEE_RATE,
                )
                if res.get("status") in ("filled", "partial"):
                    fills += 1
                    fee = abs(res.get("filled_qty", 0.0)) * price * FEE_RATE
                    total_fees += fee
                    avg_price = res.get("avg_price", price)
                    if side == "buy":
                        total_slippage_cost += abs(avg_price - price) * abs(
                            res.get("filled_qty", 0.0)
                        )
                    else:
                        total_slippage_cost += abs(price - avg_price) * abs(
                            res.get("filled_qty", 0.0)
                        )

    return {
        "order_type": order_type,
        "fills": fills,
        "total_fees": float(total_fees),
        "total_slippage_cost": float(total_slippage_cost),
        "avg_slippage_cost_per_fill": float(total_slippage_cost / fills) if fills > 0 else 0.0,
    }


def main() -> None:
    print(
        "RESEARCH/DEMO ONLY: uses real public Binance spot candles. Results are not "
        "evidence of a trading edge and are not investment advice."
    )

    results = {
        "symbols": SYMBOLS,
        "pairs": ["/".join(p) for p in PAIRS],
        "start": START,
        "end": END,
        "freq": FREQ,
        "fee_rate": FEE_RATE,
        "data_source": "binance_public",
        "models": {},
    }

    # Naive/market baseline
    results["models"]["naive_market"] = run_exec_model("market")

    # VWAP and TWAP
    results["models"]["vwap"] = run_exec_model("vwap")
    results["models"]["twap"] = run_exec_model("twap")

    # LOB with different depths
    results["models"]["lob_depth3"] = run_exec_model(
        "lob", {"depth_levels": 3, "market_impact_bps": 5.0}
    )
    results["models"]["lob_depth5"] = run_exec_model(
        "lob", {"depth_levels": 5, "market_impact_bps": 3.0}
    )
    results["models"]["lob_with_levels"] = run_exec_model(
        "lob",
        {
            "depth_levels": 3,
            "market_impact_bps": 5.0,
            "level_liquidity": [10.0, 20.0, 30.0],
            "queue_position": 0.2,
        },
    )

    # Impact quantification vs naive
    naive_slip = results["models"]["naive_market"]["avg_slippage_cost_per_fill"]
    for k in results["models"]:
        if k == "naive_market":
            results["models"][k]["vs_naive_slippage_ratio"] = 1.0
        else:
            m = results["models"][k]
            m["vs_naive_slippage_ratio"] = (
                float(m["avg_slippage_cost_per_fill"] / naive_slip) if naive_slip > 0 else None
            )

    out_path = Path(__file__).resolve().parent.parent / "reports" / "execution_realism_real.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2, default=float), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
