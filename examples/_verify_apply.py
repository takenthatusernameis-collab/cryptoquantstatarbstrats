#!/usr/bin/env python3
"""Verify the fixed PortfolioRiskController.apply() on real data."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pandas as pd

from data.loader import DataLoader
from examples.run_portfolio_real import PAIRS, SYMBOLS, PortfolioRiskController
from strategies.pairs_trading import CointegrationPairsStrategy
from utils.regime import detect_regimes

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

# Reproduce meta-selector from the real script


def regime_adaptive_meta_selector(weights_by_strategy, data):
    regimes = detect_regimes(data)
    vol_regime = trend_regime = None
    for col in regimes.columns:
        if col.endswith("_vol_regime") and col.startswith("BTC_"):
            vol_regime = regimes[col]
        if col.endswith("_trend") and col.startswith("BTC_"):
            trend_regime = regimes[col]
    combined = pd.DataFrame(
        0.0,
        index=data.index,
        columns=list(
            set(data.columns) | set([c for w in weights_by_strategy.values() for c in w.columns])
        ),
    )
    if len(weights_by_strategy) == 0:
        return combined
    high_vol = None
    try:
        if vol_regime is not None:
            unique = [u for u in vol_regime.dropna().unique()]
            high_vol = max(unique) if unique else None
    except Exception:
        high_vol = None
    for k, w in weights_by_strategy.items():
        w_aligned = w.reindex(index=data.index, columns=combined.columns).fillna(0.0)
        w_adj = w_aligned.copy()
        if high_vol is not None and vol_regime is not None:
            mask_high = (vol_regime == high_vol).reindex(index=data.index).fillna(False)
            w_adj.loc[mask_high] = w_adj.loc[mask_high] * 0.4
        if trend_regime is not None:
            mask_down = (trend_regime == -1).reindex(index=data.index).fillna(False)
            w_adj.loc[mask_down] = w_adj.loc[mask_down] * 0.7
        combined = combined.add(w_adj, fill_value=0.0)
    n = len(weights_by_strategy)
    return combined / n if n > 0 else combined


returns = data.pct_change().fillna(0.0)
combined = regime_adaptive_meta_selector(weights_by_strategy, data)
corr_matrix = returns[SYMBOLS].corr().to_dict()
ctrl = PortfolioRiskController(
    max_gross_exposure=1.4,
    per_pair_cap=0.32,
    drawdown_circuit_breaker=-0.10,
    max_correlation_exposure=0.5,
    max_cvar_allocation=0.25,
)
out = ctrl.apply(combined, pair_map=pair_map, correlation_matrix=corr_matrix, returns=returns)
gross = out.abs().sum(axis=1)
print(
    "FIXED apply(): "
    f"gross max={gross.max():.6f} mean={gross.mean():.6f} "
    f"per-asset max={out.abs().max().max():.6f}"
)
print(f"  nonzero bars={(gross > 1e-9).sum()}/{len(out)}")
print("  PASS" if gross.max() > 0.01 else "  FAIL")
