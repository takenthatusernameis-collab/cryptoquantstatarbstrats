"""Network-independent test for pairs transaction-cost sensitivity logic."""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from backtest.engine import BacktestEngine
from strategies.pairs_trading import CointegrationPairsStrategy


def _make_cointegrated_pair(n: int = 2000) -> pd.DataFrame:
    rng = np.random.default_rng(7)
    idx = pd.date_range("2026-01-01", periods=n, freq="h")
    x = 100.0 + np.cumsum(rng.normal(0.0, 0.001, n))
    noise = rng.normal(0.0, 0.0005, n)
    y = 1.5 * x + 50.0 + np.cumsum(noise)
    df = pd.DataFrame({"BTC": x, "ETH": y}, index=idx)
    df = df - df.rolling(50).mean()
    df = df / (df.rolling(50).std() + 1e-12) * 10 + 100
    return df


def test_pairs_cost_sensitivity_replay_over_grid() -> None:
    data = _make_cointegrated_pair(2000)
    engine = BacktestEngine(initial_capital=100_000.0)
    pair = ("BTC", "ETH")
    strat = CointegrationPairsStrategy(pair=pair, lookback=120, entry_threshold=2.5, cointegration_pvalue=0.05)

    grid = [
        {"fee_rate": 0.0, "slippage": 0.0},
        {"fee_rate": 0.001, "slippage": 0.0005},
        {"fee_rate": 0.002, "slippage": 0.001},
    ]
    rows = []
    for cfg in grid:
        res = engine.run(strat, data, fee_rate=cfg["fee_rate"], slippage=cfg["slippage"])
        eq = res.get("equity_curve")
        if isinstance(eq, pd.Series):
            final_equity = float(engine.initial_capital) * float(eq.iloc[-1])
        elif hasattr(eq, "__len__") and len(eq):
            final_equity = float(engine.initial_capital) * float(eq[-1])
        else:
            final_equity = None
        rows.append(
            {
                "fee_rate": cfg["fee_rate"],
                "slippage": cfg["slippage"],
                "replay": {
                    "total_return": res["total_return"],
                    "sharpe_ratio": res["sharpe_ratio"],
                    "max_drawdown": res["max_drawdown"],
                    "final_equity": final_equity,
                },
            }
        )
    payload = {"pair": list(pair), "cost_sensitivity": {"rows": rows}}
    json.dumps(payload)  # serializable
