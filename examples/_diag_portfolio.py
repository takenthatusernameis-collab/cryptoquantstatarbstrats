#!/usr/bin/env python3
"""Diagnostic: trace why portfolio weights collapse to ~1e-6 gross exposure."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd

from backtest.engine import BacktestEngine
from backtest.sweep import run_parameter_sweep
from data.loader import DataLoader
from strategies.pairs_trading import CointegrationPairsStrategy

PAIRS = [
    ("BTC", "ETH"), ("ETH", "SOL"), ("BTC", "SOL"),
    ("ADA", "ETH"), ("XRP", "BTC"), ("BNB", "ETH"),
    ("BTC", "BNB"), ("SOL", "BNB"), ("ADA", "BTC"), ("XRP", "ETH"),
]
SYMBOLS = sorted(set([s for p in PAIRS for s in p]))
START = "2026-04-01"
END = "2026-10-30"
FREQ = "1h"

loader = DataLoader()
data = loader.load_binance_data(SYMBOLS, START, END, interval=FREQ)
data = loader.clean_data(data)
print(f"Loaded {len(data)} bars; columns={list(data.columns)}")

engine = BacktestEngine(initial_capital=100_000.0)
grid_pairs = {
    "lookback": [60, 120],
    "entry_threshold": [2.0, 2.5],
    "cointegration_pvalue": [0.05, 0.10],
}

top_params = {}
for pair in PAIRS:
    pname = "/".join(pair)
    try:
        rows = run_parameter_sweep(
            CointegrationPairsStrategy(pair=pair), data, grid_pairs,
            train_period=500, test_period=100, fee_rate=0.001, slippage=0.0005,
            metric="calmar_ratio", engine=engine, mode="rolling", n_splits=4,
            replay_best=True, show_progress=False,
        )
        if not rows:
            print(f"  {pname}: no rows")
            continue
        top = rows[0]
        params = {k: top[k] for k in ("lookback", "entry_threshold", "cointegration_pvalue") if k in top}
        top_params[pname] = params
        print(f"  {pname}: {params}  oos_calmar={top.get('calmar_ratio')}")
    except Exception as e:
        print(f"  {pname}: failed {e!r}")

weights_by_strategy = {}
for pair in PAIRS:
    pname = "/".join(pair)
    if pname not in top_params:
        continue
    strat = CointegrationPairsStrategy(pair=pair, **top_params[pname])
    signals = strat.generate_signals(data)
    w = pd.DataFrame(0.0, index=data.index, columns=SYMBOLS)
    for asset in pair:
        if asset in signals.columns:
            w[asset] = signals[asset].reindex(data.index).fillna(0.0)
    gross = w.abs().sum(axis=1).replace(0.0, np.nan)
    print(f"  raw {pname}: gross_mean={gross.mean():.6f} gross_max={gross.max():.6f} nonzero={int((gross>0).sum())}")
    weights_by_strategy[pname] = w

# Reproduce regime_adaptive_meta_selector manually
from utils.regime import detect_regimes
from examples.run_portfolio_real import regime_adaptive_meta_selector, PortfolioRiskController

combined = regime_adaptive_meta_selector(weights_by_strategy, data, target_gross=1.0)
print(f"\nAfter meta-selector: gross_mean={combined.abs().sum(axis=1).mean():.6f} gross_max={combined.abs().sum(axis=1).max():.6f}")

returns = data.pct_change().fillna(0.0)
risk_ctrl = PortfolioRiskController(
    max_gross_exposure=1.4, per_pair_cap=0.32,
    drawdown_circuit_breaker=-0.10, max_correlation_exposure=0.5,
    max_cvar_allocation=0.25,
)
pair_map = {"/".join(p): list(p) for p in PAIRS if "/".join(p) in top_params}
corr_matrix = returns[SYMBOLS].corr().to_dict()
controlled = risk_ctrl.apply(combined, pair_map=pair_map, correlation_matrix=corr_matrix, returns=returns)
print(f"After risk controller: gross_mean={controlled.abs().sum(axis=1).mean():.6f} gross_max={controlled.abs().sum(axis=1).max():.6f}")