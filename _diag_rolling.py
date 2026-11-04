"""Fast rolling-cointegration stability sweep on cached real data.

The full ``rolling_cointegration_stability`` re-runs an Engle-Granger test per
window, which is slow. This diagnostic subsamples the window/step grid and
reports frac_significant so the gate threshold can be calibrated honestly on
real data. Never fabricates.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from data.cache import load_cached
from data.loader import DataLoader
from utils.cointegration import _to_clean_pair
from statsmodels.tsa.stattools import coint


def _fast_rolling(p1: pd.Series, p2: pd.Series, window: int, step: int) -> dict:
    a, b = _to_clean_pair(p1, p2)
    if len(a) < window * 1.5:
        return {"n_windows": 0, "frac_significant": 0.0, "reason": "insufficient_data"}
    pvalues = []
    for start in range(0, len(a) - window + 1, step):
        try:
            _, pv, _ = coint(a.values[start : start + window], b.values[start : start + window])
            if np.isfinite(pv):
                pvalues.append(float(pv))
        except Exception:
            continue
    if not pvalues:
        return {"n_windows": 0, "frac_significant": 0.0}
    frac = float(np.mean([pv < 0.05 for pv in pvalues]))
    return {"n_windows": len(pvalues), "frac_significant": frac}


def main() -> int:
    loader = DataLoader()
    data, prov = load_cached(loader, ["BTC", "ETH", "POL"], "2026-04-01", "2026-10-28", "1h")
    print(f"loaded {data.shape[0]} bars; cache_hit={prov.get('cache_hit')}")

    pairs = [("BTC", "ETH"), ("POL", "BTC")]
    windows = [60, 120, 240, 360, 500, 720, 1000, 1500]
    steps = [1, 6, 12, 24, 48, 72, 120, 168]
    for a, b in pairs:
        print(f"\n=== {a}/{b} (raw prices) ===")
        for w in windows:
            best = None
            for step in steps:
                r = _fast_rolling(data[a], data[b], w, step)
                if r["n_windows"] == 0:
                    continue
                if best is None or r["frac_significant"] > best[1]:
                    best = (step, r["frac_significant"], r["n_windows"])
            if best:
                print(f"  w={w:5d} best_step={best[0]:4d} frac={best[1]:.3f} nwin={best[2]}")
            else:
                print(f"  w={w:5d} insufficient_data")
        print(f"  --- {a}/{b} (log prices) ---")
        lp, lq = np.log(data[a]), np.log(data[b])
        for w in windows:
            best = None
            for step in steps:
                r = _fast_rolling(lp, lq, w, step)
                if r["n_windows"] == 0:
                    continue
                if best is None or r["frac_significant"] > best[1]:
                    best = (step, r["frac_significant"], r["n_windows"])
            if best:
                print(f"  w={w:5d} best_step={best[0]:4d} frac={best[1]:.3f} nwin={best[2]}")
            else:
                print(f"  w={w:5d} insufficient_data")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())