#!/usr/bin/env python3
"""Multi-timeframe (4h/1d) out-of-sample style rolling cointegration stability
on cached real Binance 1h data (causal/trailing only)."""

from __future__ import annotations

import json
import pickle
from datetime import datetime, timezone
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


def load_symbol_1h(symbol: str) -> pd.Series:
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


def resample_causal(series_1h: pd.Series, rule: str) -> pd.Series:
    """Causal trailing resample - use last value of completed bar, no lookahead."""
    # For close prices, resample last is causal
    resampled = series_1h.resample(rule).last()
    resampled = resampled.dropna()
    return resampled


def run_for_timeframe(timeframe: str, rule: str, out_path: Path) -> dict:
    print(
        "RESEARCH/DEMO ONLY: uses real public Binance spot candles from cache (resampled). "
        "Not evidence of a trading edge; not investment advice."
    )
    print(f"Loading cached 1h candles for {len(SYMBOLS)} symbols, resampling to {timeframe}.")
    series_1h = {sym: load_symbol_1h(sym) for sym in SYMBOLS}
    series = {sym: resample_causal(series_1h[sym], rule) for sym in SYMBOLS}
    for sym in SYMBOLS:
        print(
            f"  {sym} ({timeframe}): {len(series[sym])} bars "
            f"({series[sym].index.min().date()} -> {series[sym].index.max().date()})"
        )

    diagnostics: dict[str, dict] = {}
    for base, quote in PAIRS:
        pname = f"{base}/{quote}"
        price1 = series[base]
        price2 = series[quote]
        diag = target_schema_diagnostics(
            price1, price2, pair_name=pname, source=str(out_path)
        )
        # Add timeframe to provenance
        if "provenance" in diag:
            diag["provenance"]["timeframe"] = timeframe
        diagnostics[pname] = diag
        gates = diag["gates"]
        prov = diag["provenance"]
        print(
            f"  {pname} [{timeframe}]: status={diag['status']} "
            f"all_pass={gates['all_pass']} "
            f"eg={gates['eg_pass']} joh={gates['johansen_pass']} "
            f"spread_mr={gates['spread_mr_pass']} hl={gates['hl_bounds_pass']} "
            f"leg={gates['leg_stationarity_ok']} roll={gates['rolling_stable_ok']} "
            f"blocked_routes={len(prov.get('blocked_routes', []))}"
        )

    n_pass = sum(1 for d in diagnostics.values() if d["gates"]["all_pass"])
    out = {
        "type": "cointegration_diagnostics_oos_mt",
        "mandate": {"real_data_only": True, "fabricated_data": False},
        "real_data_only": True,
        "fabricated_data": False,
        "timeframe": timeframe,
        "symbols": SYMBOLS,
        "source": "data/cache (real public Binance spot 1h resampled, www.binance.com)",
        "n_pairs": len(PAIRS),
        "n_pass_all_gates": n_pass,
        "cointegration_diagnostics": diagnostics,
        "computed_at": datetime.now(tz=timezone.utc).isoformat(),
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, default=float), encoding="utf-8")
    print(
        f"\nWrote {len(PAIRS)} pair diagnostics "
        f"({n_pass} all-gates-pass) [{timeframe}] to {out_path}"
    )
    return out


def main() -> None:
    run_for_timeframe("4h", "4h", Path("reports/cointegration_diagnostics_oos_mt_4h.json"))
    run_for_timeframe("1d", "D", Path("reports/cointegration_diagnostics_oos_mt_1d.json"))


if __name__ == "__main__":
    main()
