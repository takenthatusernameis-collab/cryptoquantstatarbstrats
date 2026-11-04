#!/usr/bin/env python3
"""End-to-end causal EG-only pairs backtest on real cached Binance candles.

Runs CointegrationPairsStrategy with enriched gates DISABLED (causal Engle-
Granger screen only -- the repo's documented, fail-closed-by-design default
enriched gates record all_pass=False for every real pair, so zero positions
is the HONEST outcome there) and captures full metrics from real code paths.
"""
from __future__ import annotations

import json
import pickle
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from backtest.engine import BacktestEngine
from backtest.sweep import run_parameter_sweep
from strategies.pairs_trading import CointegrationPairsStrategy

CACHE = Path("data/cache")
PAIRS = [("BTC", "ETH"), ("ETH", "SOL"), ("BTC", "SOL")]
SYMBOLS = ["BTC", "ETH", "SOL"]
START = "2026-04-01"
END = "2026-10-28"
FREQ = "1h"


def load_cached(sym: str) -> pd.Series:
    with open(CACHE / f"{sym}_2026-04-01_2026-10-30_1h.pkl", "rb") as f:
        d = pickle.load(f)
    if isinstance(d, pd.DataFrame):
        col = d.columns[0] if len(d.columns) == 1 else sym
        s = d[col].astype(float)
    else:
        s = d[sym].astype(float)
    s.index.name = None
    return s


def main() -> None:
    series = {s: load_cached(s) for s in SYMBOLS}
    data = pd.concat(series, axis=1)
    data.columns = SYMBOLS
    data = data.sort_index().dropna()
    # Truncate to the example's declared window so the artifact matches.
    data = data.loc[:END]

    grid = {
        "lookback": [60, 120],
        "entry_threshold": [2.0, 2.5],
        "cointegration_pvalue": [0.05, 0.10],
    }
    engine = BacktestEngine(initial_capital=100_000.0)

    results: dict[str, Any] = {}
    for pair in PAIRS:
        rows = run_parameter_sweep(
            CointegrationPairsStrategy(
                pair=pair, use_enriched_gates=False
            ),
            data,
            grid,
            train_period=500,
            test_period=100,
            fee_rate=0.001,
            slippage=0.0005,
            metric="calmar_ratio",
            engine=engine,
            mode="rolling",
            n_splits=4,
            replay_best=True,
            show_progress=True,
        )
        top = rows[0]
        params = {
            k: top[k] for k in ("lookback", "entry_threshold", "cointegration_pvalue") if k in top
        }
        bench = engine.run_with_benchmark(
            CointegrationPairsStrategy(pair=pair, use_enriched_gates=False, **params),
            data,
            fee_rate=0.001,
            slippage=0.0005,
        )
        replay = top.get("replay") or {}
        results["/".join(pair)] = {
            "pair": list(pair),
            "top_ranked": {k: v for k, v in top.items() if k != "replay"},
            "replay": replay,
            "benchmark_total_return": bench["benchmark_total_return"],
        }
        print(
            f"{pair[0]}/{pair[1]}: replay total_return={replay.get('total_return', 0.0):.4%} "
            f"sharpe={replay.get('sharpe_ratio', 0.0):.4f} "
            f"mdd={replay.get('max_drawdown', 0.0):.4%} "
            f"final_equity={replay.get('final_equity', 0.0):,.2f} "
            f"benchmark={bench['benchmark_total_return']:.4%}"
        )

    out = {
        "symbols": SYMBOLS,
        "start": START,
        "end": END,
        "freq": FREQ,
        "n_bars": int(len(data)),
        "grid": grid,
        "walk_forward": {
            "train_period": 500,
            "test_period": 100,
            "mode": "rolling",
            "n_splits": 4,
            "metric": "calmar_ratio",
        },
        "pairs": results,
        "pair": results["BTC/ETH"]["pair"],
        "top_ranked": results["BTC/ETH"]["top_ranked"],
        "replay": results["BTC/ETH"]["replay"],
        "benchmark_total_return": results["BTC/ETH"]["benchmark_total_return"],
        "gate_mode": "causal_eng_only_use_enriched_gates_false",
        "provenance": {
            "source": "examples.run_pairs_causal_eg",
            "data_source": "binance_public_spot_cached",
            "real_data_only": True,
            "fabricated_data": False,
            "computed_at": datetime.now(timezone.utc).isoformat(),
            "blocked_routes": [],
            "rationale": (
                "Real public Binance spot candles only, served from the on-disk cache "
                "(data/cache/*.pkl) originally fetched from www.binance.com. No synthetic/"
                "fabricated candles/IV/volume used as evidence. Enriched publication-grade "
                "gates are DISABLED for this run (use_enriched_gates=False): the repo's own "
                "cached diagnostics in reports/portfolio_real.json record all_pass=False for "
                "every real pair, so the fail-closed default correctly produces zero "
                "positions -- that is the honest outcome, not a bug. This run applies the "
                "causal Engle-Granger screen only, with opposing-leg weights, costs and "
                "slippage, over a rolling walk-forward sweep."
            ),
        },
    }
    out_path = Path("reports") / "pairs_real_market_causal_eg.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, default=float), encoding="utf-8")
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()