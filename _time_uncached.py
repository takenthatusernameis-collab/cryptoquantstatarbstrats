#!/usr/bin/env python3
"""Time the uncached per-bar enriched-gate sweep path on real data."""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from backtest.engine import BacktestEngine
from backtest.sweep import run_parameter_sweep
from data.loader import DataLoader
from strategies.pairs_trading import CointegrationPairsStrategy

loader = DataLoader()
data, _ = loader.fetch_with_provenance(["BTC", "ETH", "SOL"], "2026-04-01", "2026-10-30", "1h", use_cache=True)

grid = {"lookback": [60], "entry_threshold": [2.0], "cointegration_pvalue": [0.05]}
engine = BacktestEngine(initial_capital=100_000.0)

t0 = time.monotonic()
rows = run_parameter_sweep(
    CointegrationPairsStrategy(pair=("BTC", "ETH"), use_enriched_gates=True, strict_enriched_gates=True),
    data, grid, train_period=500, test_period=100, fee_rate=0.001, slippage=0.0005,
    metric="calmar_ratio", engine=engine, mode="rolling", n_splits=4, replay_best=True, show_progress=True,
)
dt = time.monotonic() - t0
print(f"\nuncached sweep (1 combo, 4 splits) took {dt:.1f}s")
print("row:", rows[0].get("oos_mean_return"), "replay trades implied by total_return:", rows[0].get("replay", {}).get("total_return"))