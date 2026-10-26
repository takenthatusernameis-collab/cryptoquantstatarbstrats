"""
Command-line interface for running backtests and emitting reports.

Reuses :mod:`utils.reporting`` (``generate_report``, ``report_to_dict``,
``generate_risk_report``) to render either a human-readable text report or a
serializable JSON report from a backtest result. Also supports loading
backtest parameters from a YAML/TOML/JSON config file and writing reports to a
file via ``--output-path``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

from backtest.config import load_config
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
        "--config",
        help="Path to a YAML/TOML/JSON config file specifying backtest parameters.",
    )
    parser.add_argument(
        "--symbols",
        nargs="+",
        default=None,
        help="Asset symbols to load.",
    )
    parser.add_argument("--start", default=None, help="Start date (YYYY-MM-DD).")
    parser.add_argument("--end", default=None, help="End date (YYYY-MM-DD).")
    parser.add_argument("--freq", default=None, help="Bar frequency.")
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
        default=None,
        help="Pair (asset1 asset2) for the pairs strategy.",
    )
    parser.add_argument(
        "--initial-capital",
        type=float,
        default=100_000.0,
        help="Starting capital.",
    )
    parser.add_argument(
        "--fee-rate", type=float, default=None, help="Legacy linear fee rate."
    )
    parser.add_argument(
        "--slippage", type=float, default=None, help="Legacy slippage rate."
    )
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Report format (text or json).",
    )
    parser.add_argument(
        "--output-path",
        default=None,
        help="Write the report to this file instead of stdout.",
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
        asset = getattr(args, "asset", None) or "BTC"
        return MeanReversionStrategy(asset=asset)
    if name == "pairs":
        pair = getattr(args, "pair", None) or ["BTC", "ETH"]
        return CointegrationPairsStrategy(pair=tuple(pair))
    raise ValueError(f"Unknown strategy: {name}")


def _apply_config(args: argparse.Namespace, parser: argparse.ArgumentParser) -> argparse.Namespace:
    config_path = getattr(args, "config", None)
    if not config_path:
        return args

    cfg = load_config(config_path)

    def _get(cfg: dict[str, Any], *keys: str) -> Any:
        for k in keys:
            if k in cfg and cfg[k] is not None:
                return cfg[k]
        return None

    # Config fills in values the user did not explicitly override on the CLI.
    # An argument is treated as "not overridden" when it is None or still at its
    # parser default, so config-driven runs work without CLI flags while an
    # explicitly passed CLI flag always wins.
    mappings = [
        ("symbols", ("symbols",)),
        ("start", ("start", "start_date")),
        ("end", ("end", "end_date")),
        ("freq", ("freq", "frequency")),
        ("strategy", ("strategy",)),
        ("asset", ("asset",)),
        ("pair", ("pair", "pairs")),
        ("initial_capital", ("initial_capital", "initialCapital", "capital")),
        ("fee_rate", ("fee_rate", "feeRate", "fee")),
        ("slippage", ("slippage",)),
        ("output", ("output", "format")),
        ("report", ("report", "report_type")),
        ("output_path", ("output_path", "outputPath", "output_file")),
    ]

    for attr, keys in mappings:
        config_value = _get(cfg, *keys)
        if config_value is None:
            continue
        current = getattr(args, attr, None)
        parser_default = parser.get_default(attr)
        if current is None or current == parser_default:
            if attr == "pair" and config_value is not None:
                config_value = list(config_value)
            setattr(args, attr, config_value)

    return args


def main(argv: Sequence[str] | None = None) -> int:
    """Run a backtest and print a report. Returns the process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    args = _apply_config(args, parser)

    # Apply defaults if still missing
    if args.symbols is None:
        args.symbols = ["BTC", "ETH", "SOL"]
    if args.start is None:
        args.start = "2024-01-01"
    if args.end is None:
        args.end = "2024-02-01"
    if args.freq is None:
        args.freq = "1h"
    if args.strategy is None:
        args.strategy = "mean_reversion"
    if args.asset is None:
        args.asset = "BTC"
    if args.pair is None:
        args.pair = ["BTC", "ETH"]
    if args.initial_capital is None:
        args.initial_capital = 100_000.0
    if args.fee_rate is None:
        args.fee_rate = 0.0
    if args.slippage is None:
        args.slippage = 0.0
    if args.output is None:
        args.output = "text"
    if args.report is None:
        args.report = "full"

    loader = DataLoader()
    data = loader.load_data(args.symbols, args.start, args.end, freq=args.freq)
    data = loader.clean_data(data)

    strategy = _build_strategy(args.strategy, args)
    engine = BacktestEngine(initial_capital=float(args.initial_capital))
    result = engine.run(
        strategy,
        data,
        fee_rate=float(args.fee_rate),
        slippage=float(args.slippage),
    )

    if args.output == "json":
        payload = (
            risk_report_to_dict(result) if args.report == "risk" else report_to_dict(result)
        )
        content = json.dumps(payload, indent=2)
    else:
        content = (
            generate_risk_report(result)
            if args.report == "risk"
            else generate_report(result)
        )

    output_path = getattr(args, "output_path", None)
    if output_path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    else:
        print(content)
    return 0


if __name__ == "__main__":
    sys.exit(main())
