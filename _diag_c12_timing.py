#!/usr/bin/env python3
"""Temporary timing probe for Campaign #12 cadence calibration."""
from __future__ import annotations

import pickle
import sys
import time
import warnings
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils.cointegration import target_schema_diagnostics

ROOT = Path(__file__).resolve().parent
df = pickle.load(open(ROOT / "data/cache/90d10b876bb8eda9619cbba73ed19d6c7db4ea7327284f2e33f10a7872a5b263.pkl", "rb")).sort_index()
al = pd.concat([df["BTC"], df["ETH"]], axis=1).dropna()
p1 = al.iloc[:, 0]
p2 = al.iloc[:, 1]
print("aligned rows", len(al), flush=True)

for n in [120, 240, 720, 2000, 5000]:
    s1 = p1.iloc[-n:]
    s2 = p2.iloc[-n:]
    t = time.time()
    d = target_schema_diagnostics(s1, s2, "BTC/ETH")
    dt = time.time() - t
    g = d.get("gates", {})
    keys = ["eg_pass", "johansen_pass", "spread_mr_pass", "hl_bounds_pass",
            "leg_stationarity_ok", "rolling_stable_ok", "no_structural_break"]
    print(f"n={n}: {dt:.2f}s all_pass={g.get('all_pass')} gates={ {k: g.get(k) for k in keys} }", flush=True)