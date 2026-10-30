#!/usr/bin/env python3
"""Diagnostic: trace portfolio weight collapse in run_portfolio_real.py."""
from __future__ import annotations
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import numpy as np, pandas as pd
from backtest.engine import BacktestEngine
from data.loader import DataLoader
from strategies.pairs_trading import CointegrationPairsStrategy
from utils.regime import detect_regimes
from examples.run_portfolio_real import PortfolioRiskController, regime_adaptive_meta_selector, PAIRS, SYMBOLS

START, END, FREQ = "2026-04-01", "2026-10-30", "1h"
top_params = json.loads((Path("reports/portfolio_real.json")).read_text())["top_ranked_pair_params"]

loader = DataLoader()
data = loader.load_binance_data(SYMBOLS, START, END, interval=FREQ)
data = loader.clean_data(data)
print(f"data shape: {data.shape}")

weights_by_strategy, pair_map = {}, {}
for pair in PAIRS:
    pname = "/".join(pair)
    if pname not in top_params: continue
    strat = CointegrationPairsStrategy(pair=pair, **top_params[pname])
    signals = strat.generate_signals(data)
    w = pd.DataFrame(0.0, index=data.index, columns=SYMBOLS)
    for asset in pair:
        if asset in signals.columns:
            w[asset] = signals[asset].reindex(data.index).fillna(0.0)
    weights_by_strategy[pname] = w
    pair_map[pname] = list(pair)
    print(f"{pname}: raw gross max={w.abs().sum(axis=1).max():.4f} mean={w.abs().sum(axis=1).mean():.6f} nonzeros={(w.abs().sum(axis=1)>1e-9).sum()}/{len(w)}")

combined = regime_adaptive_meta_selector(weights_by_strategy, data)
print(f"\nafter meta-selector: gross max={combined.abs().sum(axis=1).max():.6f} mean={combined.abs().sum(axis=1).mean():.6f}")

returns = data.pct_change().fillna(0.0)
ctrl = PortfolioRiskController(max_gross_exposure=1.4, per_pair_cap=0.32, drawdown_circuit_breaker=-0.10,
                               max_correlation_exposure=0.5, max_cvar_allocation=0.25)

# Trace each control
w = combined.copy().fillna(0.0)
print(f"\n-- per_pair_cap --")
for pname, assets in pair_map.items():
    pa = [a for a in assets if a in w.columns]
    pair_abs = w[pa].abs().sum(axis=1)
    scale = (ctrl.per_pair_cap / pair_abs.replace(0, np.nan)).clip(upper=1.0).fillna(1.0)
    for a in pa: w[a] = w[a] * scale
print(f"after per_pair_cap: gross max={w.abs().sum(axis=1).max():.6f}")

print(f"\n-- correlation dampening (corr>0.65) --")
corr = returns[SYMBOLS].corr()
for c1 in w.columns:
    for c2 in w.columns:
        if c1 >= c2: continue
        c = corr.loc[c1, c2]
        if abs(c) > 0.65:
            w[c1] = w[c1]*0.7; w[c2] = w[c2]*0.7
print(f"after corr dampening: gross max={w.abs().sum(axis=1).max():.6f}")

print(f"\n-- max_correlation_exposure={ctrl.max_correlation_exposure} --")
asset_abs = w.abs()
scale = (ctrl.max_correlation_exposure / asset_abs.replace(0, np.nan)).clip(upper=1.0).fillna(1.0)
w = w.multiply(scale, axis=1)
print(f"after corr-exposure cap: gross max={w.abs().sum(axis=1).max():.6f} per-asset max={w.abs().max().max():.6f}")

print(f"\n-- CVaR cap (max={ctrl.max_cvar_allocation}) --")
cols = [c for c in w.columns if c in returns.columns]
rets = returns[cols].reindex(w.index).fillna(0.0)
from utils.portfolio_risk import portfolio_cvar
for it in range(6):
    port_rets = (w[cols].shift(1).fillna(0.0) * rets).sum(axis=1)
    cvar = float(portfolio_cvar(port_rets, confidence=0.95))
    print(f"  iter {it}: cvar={cvar:.8f} abs(cvar)={abs(cvar):.8f} <= cap? {abs(cvar) <= ctrl.max_cvar_allocation}")
    if not np.isfinite(cvar) or abs(cvar) <= ctrl.max_cvar_allocation:
        break
    w[cols] = w[cols] * (ctrl.max_cvar_allocation / abs(cvar))
print(f"after CVaR cap: gross max={w.abs().sum(axis=1).max():.6f}")

print(f"\n-- gross exposure cap (max={ctrl.max_gross_exposure}) --")
gross = w.abs().sum(axis=1)
scale_gross = (ctrl.max_gross_exposure / gross.replace(0, np.nan)).clip(upper=1.0).fillna(1.0)
print(f"  gross max before={gross.max():.8f} scale_gross max={scale_gross.max():.6f}")
w = w.multiply(scale_gross, axis=0)
print(f"after gross cap: gross max={w.abs().sum(axis=1).max():.8f} mean={w.abs().sum(axis=1).mean():.8f}")