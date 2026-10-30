#!/usr/bin/env python3
"""Measure ACTUAL current PortfolioRiskController.apply() + meta-selector output."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

from data.loader import DataLoader
from examples.run_portfolio_real import (
    PAIRS,
    SYMBOLS,
    PortfolioRiskController,
    regime_adaptive_meta_selector,
)
from strategies.pairs_trading import CointegrationPairsStrategy

START, END, FREQ = "2026-04-01", "2026-10-30", "1h"
top_params = json.loads((Path("reports/portfolio_real.json")).read_text())["top_ranked_pair_params"]
loader = DataLoader()
data = loader.load_binance_data(SYMBOLS, START, END, interval=FREQ)
data = loader.clean_data(data)

weights_by_strategy, pair_map = {}, {}
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

combined = regime_adaptive_meta_selector(
    weights_by_strategy, data
)
print(
    "after meta-selector: "
    f"gross max={combined.abs().sum(axis=1).max():.6f} "
    f"mean={combined.abs().sum(axis=1).mean():.6f}"
)
print(f"  meta-selector nonzero bars: {(combined.abs().sum(axis=1)>1e-9).sum()}/{len(combined)}")

returns = data.pct_change().fillna(0.0)
ctrl = PortfolioRiskController(
    max_gross_exposure=1.4,
    per_pair_cap=0.32,
    drawdown_circuit_breaker=-0.10,
    max_correlation_exposure=0.5,
    max_cvar_allocation=0.25,
)
out = ctrl.apply(combined, pair_map=pair_map, returns=returns)
gross = out.abs().sum(axis=1)
print(f"\nafter ACTUAL ctrl.apply: gross max={gross.max():.6f} mean={gross.mean():.6f}")
print(f"  nonzero bars: {(gross>1e-9).sum()}/{len(out)}")
print(f"  per-asset max: {out.abs().max().to_dict()}")
