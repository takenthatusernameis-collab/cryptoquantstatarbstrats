#!/usr/bin/env python3
"""Diagnostic: compare enriched-gates modes on real cached data."""
from __future__ import annotations
import sys
import pickle
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from strategies.pairs_trading import CointegrationPairsStrategy

CACHE = Path("data/cache")

def load_cached(sym, start="2026-04-01", end="2026-10-30", freq="1h"):
    p = CACHE / f"{sym}_{start}_{end}_{freq}.pkl"
    with open(p, "rb") as f:
        d = pickle.load(f)
    if isinstance(d, pd.DataFrame):
        col = d.columns[0] if len(d.columns) == 1 else sym
        s = d[col].astype(float)
        s.index.name = None
        return s
    return d if isinstance(d, pd.Series) else None

def main():
    syms = ["BTC", "ETH", "SOL"]
    series = {}
    for s in syms:
        series[s] = load_cached(s)
    data = pd.concat(series, axis=1)
    data.columns = syms
    data = data.sort_index().dropna()
    print(f"data shape: {data.shape}")

    pair = ("BTC", "ETH")
    lb, ent, cp = 60, 2.0, 0.05

    # Mode A: enriched gates OFF (fast, no per-bar diagnostics)
    sA = CointegrationPairsStrategy(pair=pair, lookback=lb, entry_threshold=ent, cointegration_pvalue=cp, use_enriched_gates=False)
    sigA = sA.generate_signals(data)
    print("\n[use_enriched_gates=False] long=%d short=%d enriched_ok==1=%d/%d" % (
        int(sigA["long"].sum()), int(sigA["short"].sum()),
        int((sigA["enriched_gates_ok"] == 1).sum()), len(sigA)))

    # Mode B: cached all-pass diagnostics (fast, no per-bar diagnostics)
    ed = {"gates": {"eg_pass": True, "johansen_pass": True, "spread_mr_pass": True,
                    "hl_bounds_pass": True, "rolling_stable_ok": True,
                    "leg_stationarity_ok": True, "no_structural_break": True, "all_pass": True},
          "structural_breaks": {"flagged": False}}
    sB = CointegrationPairsStrategy(pair=pair, lookback=lb, entry_threshold=ent, cointegration_pvalue=cp, enriched_diagnostics=ed)
    sigB = sB.generate_signals(data)
    print("[cached all-pass diag] long=%d short=%d enriched_ok==1=%d/%d" % (
        int(sigB["long"].sum()), int(sigB["short"].sum()),
        int((sigB["enriched_gates_ok"] == 1).sum()), len(sigB)))

    # Mode C: default (per-bar diagnostics, slow) - only on a short tail
    tail = data.tail(2000)
    sC = CointegrationPairsStrategy(pair=pair, lookback=lb, entry_threshold=ent, cointegration_pvalue=cp)
    sigC = sC.generate_signals(tail)
    print("[default per-bar, tail 2000] long=%d short=%d enriched_ok==1=%d/%d" % (
        int(sigC["long"].sum()), int(sigC["short"].sum()),
        int((sigC["enriched_gates_ok"] == 1).sum()), len(sigC)))

if __name__ == "__main__":
    main()