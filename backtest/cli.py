"""
Command-line interface for running backtests and emitting reports.

Reuses :mod:`utils.reporting`` (``generate_report``, ``report_to_dict``,
``generate_risk_report``) to render either a human-readable text report or a
serializable JSON report from a backtest result.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Sequence

from backtest.engine import BacktestEngine
from data.loader import DataLoader
from strategies.mean_reversion import MeanReversionStrategy
from strategies.pairs_trading import CointegrationPairsStrategy
from utils.reporting import (
    generate_report,
    generate_risk_report,
    report_to_dict,
    risk_report_to_dict,
)

STRATEGIES = {
    "mean_reversion": MeanReversionStrategy,
    "pairs": CointegrationPairsStrategy,
}


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the backtest CLI."""
    parser = argparse.ArgumentParser(
        prog="cryptoquant",
        description="Run a statistical arbitrage backtest and emit a report.",
    )
    parser.add_argument(
        "--symbols",
        nargs="+",
        default=["BTC", "ETH", "SOL"],
        help="Asset symbols to load.",
    )
    parser.add_argument("--start", default="2024-01-01", help="Start date (YYYY-MM-DD).")
    parser.add_argument("--end", default="2024-02-01", help="End date (YYYY-MM-DD).")
    parser.add_argument("--freq", default="1h", help="Bar frequency.")
    parser.add_argument(
        "--strategy",
        choices=sorted(STRATEGIES),
        default="mean_reversion",
        help="Strategy to run.",
    )
    parser.add_argument(
        "--asset", default="BTC", help="Asset for the mean_reversion strategy."
    )
    parser.add_argument(
        "--pair",
        nargs=2,
        default=["BTC", "ETH"],
        help="Pair (asset1 asset2) for the pairs strategy.",
    )
    parser.add_argument(
        "--initial-capital", type=float, default=100_000.0, help="Starting capital."
    )
    parser.add_argument(
        "--fee-rate", type=float, default=0.0, help="Legacy linear fee rate."
    )
    parser.add_argument(
        "--slippage", type=float, default=0.0, help="Legacy slippage rate."
    )
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Report format (text or json).",
    )
    parser.add_argument(
        "--report",
        choices=["full", "risk"],
        default="full",
        help="Report kind (full backtest report or risk report).",
    )
    return parser


def _build_strategy(name: str, args: argparse.Namespace):
    if name == "mean_reversion":
        return MeanReversionStrategy(asset=args.asset)
    if name == "pairs":
        return CointegrationPairsStrategy(pair=tuple(args.pair))
    raise ValueError(f"Unknown strategy: {name}")


def main(argv: Sequence[str] | None = None) -> int:
    """Run a backtest and print a report. Returns the process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    loader = DataLoader()
    data = loader.load_data(args.symbols, args.start, args.end, freq=args.freq)
    data = loader.clean_data(data)

    strategy = _build_strategy(args.strategy, args)
    engine = BacktestEngine(initial_capital=args.initial_capital)
    result = engine.run(
        strategy,
        data,
        fee_rate=args.fee_rate,
        slippage=args.slippage,
    )

    if args.output == "json":
        payload = (
            risk_report_to_dict(result) if args.report == "risk" else report_to_dict(result)
        )
        print(json.dumps(payload, indent=2))
    else:
        print(
            generate_risk_report(result)
            if args.report == "risk"
            else generate_report(result)
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
