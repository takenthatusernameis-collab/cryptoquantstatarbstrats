#!/usr/bin/env python3
"""Recompute per-pair cointegration diagnostics on real cached Binance data.

Loads real public Binance spot candles (2026-04-01 to 2026-10-30, 1h) from
``data/cache/`` (no network required) and runs ``target_schema_diagnostics``
for all 17 pairs in ``reports/portfolio_real.json``. Persists full gates +
``blocked_routes[]`` + rationale + provenance per pair to
``reports/cointegration_diagnostics_real.json``.

Real data only. Never fabricates. Honest blocking: pairs that do not pass all
enriched gates are marked ``blocked_or_insufficient_data`` with non-empty
``blocked_routes`` and full rationale.
"""

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
START = "2026-04-01"
END = "2026-10-30"
FREQ = "1h"
CACHE_DIR = Path("data/cache")
OUT_PATH = Path("reports/cointegration_diagnostics_real.json")


def load_symbol(symbol: str) -> pd.Series:
    """Load a single symbol's cached 1h close series (stored as a Series)."""
    path = CACHE_DIR / f"{symbol}_{START}_{END}_{FREQ}.pkl"
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
    print(f"Loading cached 1h candles ({START} -> {END}, {FREQ}) for {len(SYMBOLS)} symbols.")
    series = {sym: load_symbol(sym) for sym in SYMBOLS}
    for sym in SYMBOLS:
        print(f"  {sym}: {len(series[sym])} bars "
              f"({series[sym].index.min().date()} -> {series[sym].index.max().date()})")

    diagnostics: dict[str, dict] = {}
    for base, quote in PAIRS:
        pname = f"{base}/{quote}"
        price1 = series[base]
        price2 = series[quote]
        diag = target_schema_diagnostics(
            price1, price2, pair_name=pname, source="reports/cointegration_diagnostics_real.json"
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
        "type": "cointegration_diagnostics_real",
        "mandate": {"real_data_only": True, "fabricated_data": False},
        "real_data_only": True,
        "fabricated_data": False,
        "symbols": SYMBOLS,
        "start": START,
        "end": END,
        "freq": FREQ,
        "source": "data/cache (real public Binance spot, www.binance.com)",
        "n_pairs": len(PAIRS),
        "n_pass_all_gates": n_pass,
        "cointegration_diagnostics": diagnostics,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2, default=float), encoding="utf-8")
    print(f"\nWrote {len(PAIRS)} pair diagnostics ({n_pass} all-gates-pass) to {OUT_PATH}")


if __name__ == "__main__":
    main()
