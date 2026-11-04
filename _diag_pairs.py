#!/usr/bin/env python3
"""Diagnostic: why does run_pairs.py produce zero trades?"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import pandas as pd
from data.loader import DataLoader
from strategies.pairs_trading import CointegrationPairsStrategy
from utils.cointegration import comprehensive_cointegration_diagnostics, target_schema_diagnostics
from backtest.engine import BacktestEngine

ld = DataLoader()
data = ld.load_binance_data(["BTC", "ETH", "SOL"], "2026-04-01", "2026-10-28", interval="1h")
data = ld.clean_data(data)
print("data:", data.shape)

p1, p2 = data["BTC"], data["ETH"]

# 1. Engle-Granger on full sample
from statsmodels.tsa.stattools import coint
score, pval, _ = coint(p1, p2)
print(f"\n[1] Full-sample Engle-Granger coint p-value = {pval:.4f}")

# 2. Rolling coint p-value on trailing lookback windows (like the strategy)
lookback = 60
pv = []
for i in range(lookback - 1, len(data)):
    s1 = p1.iloc[i - lookback + 1 : i + 1]
    s2 = p2.iloc[i - lookback + 1 : i + 1]
    try:
        _, p, _ = coint(s1, s2)
        pv.append(p)
    except Exception:
        pv.append(np.nan)
pv = np.array(pv)
print(f"[2] Rolling 60-bar EG p-value: median={np.nanmedian(pv):.4f} mean={np.nanmean(pv):.4f} "
      f"frac<0.05={np.nanmean(pv <= 0.05):.3f} frac<0.10={np.nanmean(pv <= 0.10):.3f}")

# 3. Z-score distribution of the spread
strat = CointegrationPairsStrategy(pair=("BTC", "ETH"), lookback=lookback, entry_threshold=2.0)
spread = strat.calculate_spread(p1, p2)
spread_mean = spread.rolling(lookback, min_periods=lookback).mean()
spread_std = spread.rolling(lookback, min_periods=lookback).std()
z = (spread - spread_mean) / spread_std.where(spread_std > 0)
z = z.dropna()
print(f"\n[3] Z-score: mean={z.mean():.4f} std={z.std():.4f} "
      f"min={z.min():.3f} max={z.max():.3f}")
print(f"    frac |z|>2.0 = {(z.abs() > 2.0).mean():.4f}")
print(f"    frac z>2.0 = {(z > 2.0).mean():.4f}  frac z<-2.0 = {(z < -2.0).mean():.4f}")

# 4. Cached diagnostics gate for BTC/ETH
import json
pf = json.load(open("reports/portfolio_real.json"))
cd = pf.get("cointegration_diagnostics", {})
bte = cd.get("BTC/ETH", {})
print(f"\n[4] Cached BTC/ETH gates: {bte.get('gates')}")
print(f"     structural_breaks flagged: {bte.get('structural_breaks', {}).get('flagged')}")

# 5. Fresh target-schema diagnostics on trailing window (per-bar style)
diag = target_schema_diagnostics(p1.iloc[-lookback:], p2.iloc[-lookback:], pair_name="BTC/ETH")
print(f"\n[5] Fresh trailing-window target-schema gates: {diag.get('gates')}")
print(f"     structural_breaks: {diag.get('structural_breaks')}")

# 6. Run strategy WITHOUT enriched gates (default behaviour) and WITH, compare
for use_enriched in (False, True):
    s = CointegrationPairsStrategy(
        pair=("BTC", "ETH"), lookback=lookback, entry_threshold=2.0,
        use_enriched_gates=use_enriched, strict_enriched_gates=use_enriched,
    )
    sig = s.generate_signals(data)
    n_long = int(sig["long"].sum())
    n_short = int(sig["short"].sum())
    print(f"\n[6] use_enriched_gates={use_enriched}: long bars={n_long} short bars={n_short}")
    # count transitions (trades)
    pos = (sig["long"].astype(int) - sig["short"].astype(int))
    transitions = int((pos.diff().abs() > 0).sum())
    print(f"    position transitions (approx trades x2): {transitions}")

# 7. Full backtest without enriched gates
s = CointegrationPairsStrategy(pair=("BTC", "ETH"), lookback=lookback, entry_threshold=2.0,
                               use_enriched_gates=False, strict_enriched_gates=False)
eng = BacktestEngine(initial_capital=100_000.0)
res = eng.run(s, data, fee_rate=0.001, slippage=0.0005)
print(f"\n[7] Backtest (no enriched gates):")
print(f"    trades={res.get('n_trades')} total_return={res.get('total_return', 0):.4%} "
      f"sharpe={res.get('sharpe_ratio', 0):.4f} maxDD={res.get('max_drawdown', 0):.4%} "
      f"final_equity={res.get('final_equity', 0):,.2f}")