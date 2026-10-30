#!/usr/bin/env python3
"""Trace PortfolioRiskController step-by-step to find the real bottleneck."""

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
from utils.portfolio_risk import portfolio_cvar

PAIRS = [
    ("BTC", "ETH"), ("ETH", "SOL"), ("BTC", "SOL"),
    ("ADA", "ETH"), ("XRP", "BTC"), ("BNB", "ETH"),
    ("BTC", "BNB"), ("SOL", "BNB"), ("ADA", "BTC"), ("XRP", "ETH"),
]
SYMBOLS = sorted(set([s for p in PAIRS for s in p]))
START = "2026-04-01"
END = "2026-10-30"

loader = DataLoader()
data = loader.load_binance_data(SYMBOLS, START, END, interval="1h")
data = loader.clean_data(data)
print(f"Loaded {len(data)} bars")

engine = BacktestEngine(initial_capital=100_000.0)
grid_pairs = {"lookback": [60, 120], "entry_threshold": [2.0, 2.5], "cointegration_pvalue": [0.05, 0.10]}

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
            continue
        top = rows[0]
        top_params[pname] = {k: top[k] for k in ("lookback", "entry_threshold", "cointegration_pvalue") if k in top}
    except Exception as e:
        print(f"  {pname}: failed {e!r}")

weights_by_strategy = {}
pair_map = {}
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
    weights_by_strategy[pname] = w
    pair_map[pname] = list(pair)

from examples.run_portfolio_real import regime_adaptive_meta_selector
combined = regime_adaptive_meta_selector(weights_by_strategy, data, target_gross=1.0)
returns = data.pct_change().fillna(0.0)
corr_matrix = returns[SYMBOLS].corr().to_dict()

# Manual step-by-step risk controller
from examples.run_portfolio_real import PortfolioRiskController

# Step 1: pair caps
w = combined.copy().fillna(0.0)
for pair_name, assets in pair_map.items():
    pair_assets = [a for a in assets if a in w.columns]
    if not pair_assets:
        continue
    pair_abs = w[pair_assets].abs().sum(axis=1)
    scale = (0.32 / pair_abs.replace(0, np.nan)).clip(upper=1.0).fillna(1.0)
    for a in pair_assets:
        w[a] = w[a] * scale
print(f"After per_pair_cap=0.32: gross_mean={w.abs().sum(axis=1).mean():.6f}")

# Step 2: correlation redundancy
redundancy = pd.Series(1.0, index=w.columns, dtype=float)
for c1 in w.columns:
    c1m = corr_matrix.get(c1)
    if not isinstance(c1m, dict):
        continue
    hits = 0
    for c2 in w.columns:
        if c1 == c2:
            continue
        corr = c1m.get(c2)
        if corr is not None and abs(float(corr)) > 0.65:
            hits += 1
    if hits > 0:
        redundancy[c1] = 1.0 / (1.0 + 0.10 * hits)
print(f"  redundancy factors: {redundancy.to_dict()}")
w = w.multiply(redundancy, axis=1)
print(f"After correlation redundancy: gross_mean={w.abs().sum(axis=1).mean():.6f}")

# Step 3: max_correlation_exposure
asset_abs = w.abs()
scale = (0.5 / asset_abs.replace(0, np.nan)).clip(upper=1.0).fillna(1.0)
w = w.multiply(scale, axis=0)
print(f"After max_corr_exp=0.5: gross_mean={w.abs().sum(axis=1).mean():.6f}")

# Step 4: CVaR loop
cols = [c for c in w.columns if c in returns.columns]
rets = returns[cols].reindex(w.index).fillna(0.0)
for i in range(6):
    port_rets = (w[cols].shift(1).fillna(0.0) * rets).sum(axis=1)
    cvar = float(portfolio_cvar(port_rets, confidence=0.95))
    print(f"  CVaR iter {i}: cvar={cvar:.6f} gross_mean={w[cols].abs().sum(axis=1).mean():.6f}")
    if not np.isfinite(cvar) or abs(cvar) <= 0.25:
        break
    w[cols] = w[cols] * (0.25 / abs(cvar))
print(f"After CVaR loop: gross_mean={w.abs().sum(axis=1).mean():.6f}")

# Step 5: gross exposure
gross = w.abs().sum(axis=1)
scale_gross = (1.4 / gross.replace(0, np.nan)).clip(upper=1.0).fillna(1.0)
w = w.multiply(scale_gross, axis=0)
print(f"After gross cap=1.4: gross_mean={w.abs().sum(axis=1).mean():.6f}")

print(f"\nCVaR of the returns themselves (per-asset):")
for c in SYMBOLS:
    print(f"  {c}: cvar95={portfolio_cvar(returns[c], 0.95):.6f}")