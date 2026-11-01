#!/usr/bin/env python3
"""Out-of-sample re-validation on a different real Binance window (cached data only)."""

from __future__ import annotations

import json
import pickle
from pathlib import Path

import pandas as pd

from utils.cointegration import target_schema_diagnostics

PAIRS = [
    ("BTC", "ETH"),
    ("ETH", "SOL"),
    ("BTC", "SOL"),
    ("ADA", "ETH"),
    ("XRP", "BTC"),
    ("BNB", "ETH"),
    ("BTC", "BNB"),
    ("SOL", "BNB"),
    ("ADA", "BTC"),
    ("XRP", "ETH"),
    ("BNB", "BTC"),
    ("DOT", "BTC"),
    ("DOT", "ETH"),
    ("POL", "BTC"),
    ("AVAX", "BTC"),
    ("LINK", "BTC"),
    ("LTC", "BTC"),
]

SYMBOLS = sorted({s for pair in PAIRS for s in pair})
CACHE_DIR = Path("data/cache")
OUT_PATH = Path("reports/cointegration_diagnostics_oos.json")
# Use an earlier window from the cached series (first ~40% as OOS)
OOS_START_FRAC = 0.0
OOS_END_FRAC = 0.4


def load_symbol(symbol: str) -> pd.Series:
    path = CACHE_DIR / f"{symbol}_2026-04-01_2026-10-30_1h.pkl"
    if not path.exists():
        raise FileNotFoundError(f"Cache missing for {symbol}: {path}")
    with open(path, "rb") as fh:
        obj = pickle.load(fh)
    if isinstance(obj, pd.DataFrame):
        if symbol not in obj.columns:
            raise KeyError(f"{symbol} not a column in {path}; columns={list(obj.columns)}")
        series = obj[symbol].astype(float)
    else:
        series = obj.astype(float)
        series.name = symbol
    return series.sort_index()


def main() -> None:
    print(
        "RESEARCH/DEMO ONLY: uses real public Binance spot candles from cache. "
        "Not evidence of a trading edge; not investment advice."
    )
    print(f"Loading cached 1h candles for {len(SYMBOLS)} symbols (OOS window split).")
    series_full = {sym: load_symbol(sym) for sym in SYMBOLS}
    n = min(len(s) for s in series_full.values())
    start = int(n * OOS_START_FRAC)
    end = int(n * OOS_END_FRAC)
    series = {sym: series_full[sym].iloc[start:end] for sym in SYMBOLS}
    for sym in SYMBOLS:
        print(f"  {sym}: {len(series[sym])} bars "
              f"({series[sym].index.min().date()} -> {series[sym].index.max().date()})")

    diagnostics: dict[str, dict] = {}
    for base, quote in PAIRS:
        pname = f"{base}/{quote}"
        price1 = series[base]
        price2 = series[quote]
        diag = target_schema_diagnostics(
            price1, price2, pair_name=pname, source=str(OUT_PATH)
        )
        diagnostics[pname] = diag
        gates = diag["gates"]
        prov = diag["provenance"]
        print(
            f"  {pname}: status={diag['status']} "
            f"all_pass={gates['all_pass']} "
            f"eg={gates['eg_pass']} joh={gates['johansen_pass']} "
            f"spread_mr={gates['spread_mr_pass']} hl={gates['hl_bounds_pass']} "
            f"leg={gates['leg_stationarity_ok']} roll={gates['rolling_stable_ok']} "
            f"blocked_routes={len(prov['blocked_routes'])}"
        )

    n_pass = sum(1 for d in diagnostics.values() if d["gates"]["all_pass"])
    out = {
        "type": "cointegration_diagnostics_oos",
        "mandate": {"real_data_only": True, "fabricated_data": False},
        "real_data_only": True,
        "fabricated_data": False,
        "symbols": SYMBOLS,
        "oos_window": {
            "start_frac": OOS_START_FRAC,
            "end_frac": OOS_END_FRAC,
            "n_bars": end - start,
        },
        "source": "data/cache (real public Binance spot, www.binance.com) - different window",
        "n_pairs": len(PAIRS),
        "n_pass_all_gates": n_pass,
        "cointegration_diagnostics": diagnostics,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2, default=float), encoding="utf-8")
    print(f"\nWrote {len(PAIRS)} pair diagnostics ({n_pass} all-gates-pass) to {OUT_PATH}")


if __name__ == "__main__":
    main()
