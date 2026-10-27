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
from datetime import datetime
from importlib.metadata import version as _pkg_version
from pathlib import Path
from typing import Any, Sequence

import pandas as pd

from backtest.config import ConfigValidationError, load_config, validate_config
from backtest.engine import BacktestEngine
from backtest.execution import ExecutionSimulator
from data.loader import DataLoader
from strategies.mean_reversion import MeanReversionStrategy
from strategies.pairs_trading import CointegrationPairsStrategy
from strategies.term_structure import TermStructureStrategy
from utils.monte_carlo import monte_carlo_analysis
from utils.optimization import get_optimizer
from utils.rebalance import create_rebalanced_weights

STRATEGIES = {
    "mean_reversion": MeanReversionStrategy,
    "pairs": CointegrationPairsStrategy,
    "term_structure": TermStructureStrategy,
}


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the backtest CLI."""
    parser = argparse.ArgumentParser(
        prog="cryptoquant",
        description="Run a statistical arbitrage backtest and emit a report.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {_pkg_version('cryptoquantstatarbstrats')}",
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
    parser.add_argument("--freq", default=None, help="Bar frequency / Binance kline interval.")
    parser.add_argument(
        "--data-source",
        choices=["binance", "csv", "synthetic"],
        default=None,
        help="Price source. Defaults to public Binance spot candles; synthetic is demo-only.",
    )
    parser.add_argument(
        "--data-csv",
        default=None,
        help="CSV with timestamp/index plus price columns (required for --data-source csv).",
    )
    parser.add_argument(
        "--strategy",
        choices=sorted(STRATEGIES),
        default="mean_reversion",
        help="Strategy to run.",
    )
    parser.add_argument("--asset", default="BTC", help="Asset for the mean_reversion strategy.")
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
    parser.add_argument("--fee-rate", type=float, default=None, help="Legacy linear fee rate.")
    parser.add_argument("--slippage", type=float, default=None, help="Legacy slippage rate.")
    parser.add_argument(
        "--output",
        choices=["text", "json", "html", "pdf"],
        default="text",
        help="Report format (text or json).",
    )
    parser.add_argument(
        "--output-path",
        default=None,
        help="Write the report to this file instead of stdout.",
    )
    parser.add_argument(
        "--artifact-dir",
        default=None,
        help="Directory to persist timestamped report artifacts (html/pdf/json/txt).",
    )
    parser.add_argument(
        "--title",
        default=None,
        help="Custom title for HTML/PDF reports.",
    )
    parser.add_argument(
        "--report",
        choices=["full", "risk", "attribution"],
        default="full",
        help="Report kind (full backtest report or risk report).",
    )
    parser.add_argument(
        "--benchmark",
        action="store_true",
        default=False,
        help="Include an equal-weighted buy-and-hold benchmark in reports.",
    )
    parser.add_argument(
        "--rebalance-benchmark",
        "--rebalance_benchmark",
        action="store_true",
        default=False,
        dest="rebalance_benchmark",
        help="Also compute benchmark for portfolio/walk-forward paths.",
    )
    parser.add_argument(
        "--walk-forward",
        action="store_true",
        default=False,
        help="Run walk-forward validation.",
    )
    parser.add_argument(
        "--walk-forward-report",
        dest="walk_forward_report",
        action="store_true",
        default=False,
        help="Generate walk-forward report artifacts.",
    )
    parser.add_argument(
        "--walk_forward_report",
        dest="walk_forward_report",
        action="store_true",
        default=False,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--train-period",
        type=int,
        default=None,
        help="Walk-forward train period.",
    )
    parser.add_argument(
        "--test-period",
        type=int,
        default=None,
        help="Walk-forward test period.",
    )
    parser.add_argument(
        "--rebalance-frequency",
        "--rebalance_freq",
        default=None,
        help="Rebalance frequency (e.g. 1d, 1w, 1m).",
    )
    parser.add_argument(
        "--rebalance-offset",
        default=None,
        help="Optional rebalance offset.",
    )
    parser.add_argument(
        "--volume-csv",
        default=None,
        help="Path to CSV with per-asset bar volume (timestamp/index + asset columns).",
    )
    parser.add_argument(
        "--high-csv",
        default=None,
        help="Path to CSV with per-asset bar highs (timestamp/index + asset columns).",
    )
    parser.add_argument(
        "--low-csv",
        default=None,
        help="Path to CSV with per-asset bar lows (timestamp/index + asset columns).",
    )
    parser.add_argument(
        "--benchmark-weights-csv",
        default=None,
        help=("Path to CSV with benchmark weights (timestamp/index + asset "
              "columns) for Brinson attribution."),
    )
    parser.add_argument(
        "--factor-returns-csv",
        default=None,
        help=("Path to CSV with factor returns (timestamp/index + factor "
              "columns) for factor attribution."),
    )
    parser.add_argument(
        "--execution-simulator",
        action="store_true",
        help="Enable execution simulation path (for VWAP/TWAP/participation).",
    )
    parser.add_argument(
        "--order-type",
        choices=["market", "limit", "vwap", "twap"],
        default=None,
        help="Order type for execution simulator.",
    )
    parser.add_argument(
        "--participation-rate",
        type=float,
        default=None,
        help="Max fraction of bar volume to fill per order.",
    )
    parser.add_argument(
        "--slippage-bps",
        type=float,
        default=None,
        help="Slippage in basis points for execution simulator.",
    )
    parser.add_argument(
        "--regime-mode",
        default=None,
        help="Regime mode for regime-aware gating (e.g. trend/volatility).",
    )
    parser.add_argument(
        "--regime-lookback",
        type=int,
        default=None,
        help="Lookback window for regime detection.",
    )
    parser.add_argument(
        "--regime-vol-mode",
        default=None,
        help="Volatility-based regime gating (e.g. low_vol).",
    )
    parser.add_argument(
        "--reoptimize",
        action="store_true",
        default=False,
        help="Reoptimize portfolio weights on each walk-forward train window.",
    )
    parser.add_argument(
        "--optimizer",
        default=None,
        help=(
            "Optimizer name for walk-forward reoptimization (e.g. equal_weight, "
            "inverse_volatility, risk_parity, min_variance, mean_variance)."
        ),
    )
    parser.add_argument(
        "--monte-carlo",
        type=int,
        default=None,
        dest="monte_carlo",
        help="Run Monte Carlo bootstrap analysis with N simulations.",
    )
    parser.add_argument(
        "--monte-carlo-method",
        choices=["bootstrap", "shuffle"],
        default="bootstrap",
        dest="monte_carlo_method",
        help="Monte Carlo resampling method.",
    )
    parser.add_argument(
        "--monte-carlo-seed",
        type=int,
        default=None,
        dest="monte_carlo_seed",
        help="Random seed for Monte Carlo analysis.",
    )
    parser.add_argument(
        "--near-tenor",
        default=None,
        help="Near tenor IV column name for term_structure.",
    )
    parser.add_argument(
        "--far-tenor",
        default=None,
        help="Far tenor IV column name for term_structure.",
    )
    parser.add_argument(
        "--lookback",
        type=int,
        default=None,
        help="Lookback window for term_structure z-score.",
    )
    parser.add_argument(
        "--entry-threshold",
        type=float,
        default=None,
        help="Entry threshold for term_structure.",
    )
    parser.add_argument(
        "--exit-threshold",
        type=float,
        default=None,
        help="Exit threshold for term_structure.",
    )
    return parser


def _build_strategy(name: str, args: argparse.Namespace):
    if name == "mean_reversion":
        asset = getattr(args, "asset", None) or "BTC"
        return MeanReversionStrategy(asset=asset)
    if name == "pairs":
        pair = getattr(args, "pair", None) or ["BTC", "ETH"]
        return CointegrationPairsStrategy(pair=tuple(pair))
    if name == "term_structure":
        asset = getattr(args, "asset", None) or "BTC"
        near_tenor = getattr(args, "near_tenor", None) or "iv_30d"
        far_tenor = getattr(args, "far_tenor", None) or "iv_90d"
        lookback = getattr(args, "lookback", None) or 30
        entry_threshold = getattr(args, "entry_threshold", None) or 2.0
        exit_threshold = getattr(args, "exit_threshold", None) or 0.5
        return TermStructureStrategy(
            asset=asset,
            near_tenor=near_tenor,
            far_tenor=far_tenor,
            lookback=int(lookback),
            entry_threshold=float(entry_threshold),
            exit_threshold=float(exit_threshold),
        )
    raise ValueError(f"Unknown strategy: {name}")


def _apply_config(args: argparse.Namespace, parser: argparse.ArgumentParser) -> argparse.Namespace:
    config_path = getattr(args, "config", None)
    if not config_path:
        return args

    cfg = load_config(config_path)
    try:
        validate_config(cfg)
    except ConfigValidationError as exc:
        parser.error(f"Invalid config {config_path}: {exc}")
    args = _apply_config_from_dict(args, parser, cfg)
    return args


def _apply_config_from_dict(
    args: argparse.Namespace, parser: argparse.ArgumentParser, cfg: dict[str, Any]
) -> argparse.Namespace:

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
        ("data_source", ("data_source", "dataSource")),
        ("data_csv", ("data_csv", "data_path", "price_csv")),
        ("strategy", ("strategy",)),
        ("asset", ("asset",)),
        ("pair", ("pair", "pairs")),
        ("initial_capital", ("initial_capital", "initialCapital", "capital")),
        ("fee_rate", ("fee_rate", "feeRate", "fee")),
        ("slippage", ("slippage",)),
        ("output", ("output", "format")),
        ("report", ("report", "report_type")),
        ("output_path", ("output_path", "outputPath", "output_file")),
        ("artifact_dir", ("artifact_dir", "artifactDir", "artifact_directory")),
        ("rebalance_frequency", ("rebalance_frequency", "rebalance_freq", "rebal_freq")),
        ("rebalance_offset", ("rebalance_offset", "offset")),
        ("volume_csv", ("volume_csv", "volume", "volume_path")),
        ("high_csv", ("high_csv", "high", "high_path")),
        ("low_csv", ("low_csv", "low", "low_path")),
        ("benchmark_weights_csv", ("benchmark_weights_csv", "benchmark_weights",
                                   "benchmark_weights_path")),
        ("factor_returns_csv", ("factor_returns_csv", "factor_returns", "factor_returns_path")),
        ("execution_simulator", ("execution_simulator", "use_execution_simulator")),
        ("order_type", ("order_type",)),
        ("participation_rate", ("participation_rate",)),
        ("slippage_bps", ("slippage_bps",)),
        ("regime_mode", ("regime_mode", "regimeMode")),
        ("regime_lookback", ("regime_lookback", "regimeLookback")),
        ("regime_vol_mode", ("regime_vol_mode", "regimeVolMode")),
        ("benchmark", ("benchmark",)),
        ("rebalance_benchmark", ("rebalance_benchmark", "rebalanceBenchmark")),
        ("walk_forward_report", ("walk_forward_report", "walkForwardReport")),
        ("walk_forward", ("walk_forward",)),
        ("train_period", ("train_period", "trainPeriod")),
        ("test_period", ("test_period", "testPeriod")),
        ("reoptimize", ("reoptimize", "reOptimize", "reoptimize_portfolio")),
        ("optimizer", ("optimizer", "opt", "optimization", "optimizer_name")),
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

    # Also apply term structure specific params if present
    for attr, keys in [
        ("near_tenor", ("near_tenor", "nearTenor")),
        ("far_tenor", ("far_tenor", "farTenor")),
        ("lookback", ("lookback",)),
        ("entry_threshold", ("entry_threshold", "entryThreshold")),
        ("exit_threshold", ("exit_threshold", "exitThreshold")),
    ]:
        config_value = _get(cfg, *keys)
        if config_value is None:
            continue
        current = getattr(args, attr, None)
        parser_default = parser.get_default(attr)
        if current is None or current == parser_default:
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
    if args.data_source is None:
        args.data_source = "binance"
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
    if args.data_source == "binance":
        data = loader.load_binance_data(
            args.symbols, args.start, args.end, interval=args.freq
        )
    elif args.data_source == "synthetic":
        print(
            "WARNING: using synthetic demonstration prices; results are not evidence "
            "of real-market performance.",
            file=sys.stderr,
        )
        data = loader.load_data(args.symbols, args.start, args.end, freq=args.freq)
    elif args.data_source == "csv":
        if not args.data_csv:
            raise ValueError("--data-source csv requires --data-csv PATH.")
        data = DataLoader.load_csv(args.data_csv)
    else:
        raise ValueError(f"Unsupported data source: {args.data_source!r}")
    data = loader.clean_data(data)

    if args.strategy == "term_structure":
        if not isinstance(data, pd.DataFrame):
            data = pd.DataFrame(data)
        if "iv_30d" not in data.columns or "iv_90d" not in data.columns:
            raise ValueError(
                "The term_structure strategy requires real iv_30d and iv_90d "
                "columns in --data-csv. Synthetic implied-volatility columns are "
                "not generated automatically."
            )

    volume_df = None
    high_df = None
    low_df = None
    vol_path = getattr(args, "volume_csv", None)
    if vol_path:
        try:
            volume_df = DataLoader.load_csv(vol_path)
            volume_df = loader.clean_data(volume_df)
            volume_df = volume_df.reindex(index=data.index).ffill().fillna(0.0)
            if isinstance(data, pd.DataFrame):
                volume_df = volume_df.reindex(columns=data.columns, fill_value=0.0)
        except Exception:
            volume_df = None
    high_path = getattr(args, "high_csv", None)
    if high_path:
        try:
            high_df = DataLoader.load_csv(high_path)
            high_df = loader.clean_data(high_df)
            high_df = high_df.reindex(index=data.index).ffill()
            if isinstance(data, pd.DataFrame):
                high_df = high_df.reindex(columns=data.columns)
        except Exception:
            high_df = None
    low_path = getattr(args, "low_csv", None)
    if low_path:
        try:
            low_df = DataLoader.load_csv(low_path)
            low_df = loader.clean_data(low_df)
            low_df = low_df.reindex(index=data.index).ffill()
            if isinstance(data, pd.DataFrame):
                low_df = low_df.reindex(columns=data.columns)
        except Exception:
            low_df = None

    # Benchmark weights (for Brinson attribution): asset columns aligned to data.
    benchmark_weights_df = None
    bw_path = getattr(args, "benchmark_weights_csv", None)
    if bw_path:
        try:
            benchmark_weights_df = DataLoader.load_csv(bw_path)
            benchmark_weights_df = loader.clean_data(benchmark_weights_df)
            benchmark_weights_df = benchmark_weights_df.reindex(
                index=data.index).ffill().fillna(0.0)
            if isinstance(data, pd.DataFrame):
                benchmark_weights_df = benchmark_weights_df.reindex(
                    columns=data.columns, fill_value=0.0)
        except Exception:
            benchmark_weights_df = None

    # Factor returns (for factor attribution): factor columns kept as-is.
    factor_returns_df = None
    fr_path = getattr(args, "factor_returns_csv", None)
    if fr_path:
        try:
            factor_returns_df = DataLoader.load_csv(fr_path)
            factor_returns_df = loader.clean_data(factor_returns_df)
            factor_returns_df = factor_returns_df.reindex(index=data.index).ffill().fillna(0.0)
        except Exception:
            factor_returns_df = None

    exec_sim = None
    use_exec = getattr(args, "execution_simulator", False)
    order_type = getattr(args, "order_type", None)
    part_rate = getattr(args, "participation_rate", None)
    slip_bps = getattr(args, "slippage_bps", None)
    if use_exec or order_type or part_rate is not None or slip_bps is not None:
        if part_rate is None:
            part_rate = 0.1
        if slip_bps is None:
            slip_bps = 0.0
        exec_sim = ExecutionSimulator(
            participation_rate=float(part_rate),
            slippage_bps=float(slip_bps),
            order_type=str(order_type) if order_type is not None else "market",
        )

    strategy = _build_strategy(args.strategy, args)
    engine = BacktestEngine(initial_capital=float(args.initial_capital))
    rebalance_freq = getattr(args, "rebalance_frequency", None)
    walk_forward = getattr(args, "walk_forward", False) or getattr(
        args, "walk_forward_report", False
    )
    train_period = getattr(args, "train_period", None)
    test_period = getattr(args, "test_period", None)
    regime_mode = getattr(args, "regime_mode", None)
    regime_lookback = getattr(args, "regime_lookback", None)
    regime_vol_mode = getattr(args, "regime_vol_mode", None)
    if train_period is None:
        train_period = 60
    if test_period is None:
        test_period = 20
    if walk_forward:
        reopt = bool(getattr(args, "reoptimize", False))
        opt_name = getattr(args, "optimizer", None)
        opt_fn = get_optimizer(opt_name) if opt_name else None
        if rebalance_freq or reopt:
            signals = strategy.generate_signals(data)
            weights = pd.DataFrame(0.0, index=data.index, columns=data.columns)
            weight_cols = [c for c in data.columns if c in signals.columns]
            if weight_cols:
                for asset in weight_cols:
                    weights[asset] = signals[asset].reindex(data.index).fillna(0.0)
            if "long" in signals.columns and "short" in signals.columns:
                import numpy as _np

                long_mask = signals["long"].fillna(False).reindex(data.index, fill_value=False)
                short_mask = signals["short"].fillna(False).reindex(data.index, fill_value=False)
                for asset in data.columns:
                    weights.loc[long_mask, asset] = 1.0
                    weights.loc[short_mask, asset] = -1.0
            if "exit" in signals.columns:
                exit_mask = signals["exit"].fillna(False).reindex(data.index, fill_value=False)
                weights.loc[exit_mask, :] = 0.0
            active = weights.abs().sum(axis=1).replace(0.0, _np.nan)
            weights = weights.div(active, axis=0).fillna(0.0)
            if rebalance_freq:
                reb_offset = getattr(args, "rebalance_offset", None)
                weights = create_rebalanced_weights(
                    weights, data, freq=rebalance_freq, offset=reb_offset
                )
            result = engine.walk_forward_portfolio(
                weights,
                data,
                train_period=int(train_period),
                test_period=int(test_period),
                fee_rate=float(args.fee_rate),
                slippage=float(args.slippage),
                execution_simulator=exec_sim,
                volume=volume_df,
                high=high_df,
                low=low_df,
                reoptimize=reopt,
                optimizer=opt_fn,
                regime_mode=regime_mode,
                regime_lookback=regime_lookback,
                regime_vol_mode=regime_vol_mode,
                benchmark_weights=benchmark_weights_df,
                factor_returns=factor_returns_df,
            )
        else:
            result = engine.walk_forward(
                strategy,
                data,
                train_period=int(train_period),
                test_period=int(test_period),
                fee_rate=float(args.fee_rate),
                slippage=float(args.slippage),
                execution_simulator=exec_sim,
                volume=volume_df,
                high=high_df,
                low=low_df,
                regime_mode=regime_mode,
                regime_lookback=regime_lookback,
                regime_vol_mode=regime_vol_mode,
                benchmark_weights=benchmark_weights_df,
                factor_returns=factor_returns_df,
            )
    elif rebalance_freq:
        signals = strategy.generate_signals(data)
        weights = pd.DataFrame(0.0, index=data.index, columns=data.columns)
        weight_cols = [c for c in data.columns if c in signals.columns]
        if weight_cols:
            for asset in weight_cols:
                weights[asset] = signals[asset].reindex(data.index).fillna(0.0)
        if "long" in signals.columns and "short" in signals.columns:
            import numpy as _np

            long_mask = signals["long"].fillna(False).reindex(data.index, fill_value=False)
            short_mask = signals["short"].fillna(False).reindex(data.index, fill_value=False)
            for asset in data.columns:
                weights.loc[long_mask, asset] = 1.0
                weights.loc[short_mask, asset] = -1.0
        if "exit" in signals.columns:
            exit_mask = signals["exit"].fillna(False).reindex(data.index, fill_value=False)
            weights.loc[exit_mask, :] = 0.0
        active = weights.abs().sum(axis=1).replace(0.0, _np.nan)
        weights = weights.div(active, axis=0).fillna(0.0)
        reb_offset = getattr(args, "rebalance_offset", None)
        weights = create_rebalanced_weights(weights, data, freq=rebalance_freq, offset=reb_offset)
        result = engine.run_portfolio(
            weights,
            data,
            fee_rate=float(args.fee_rate),
            slippage=float(args.slippage),
            execution_simulator=exec_sim,
            volume=volume_df,
            high=high_df,
            low=low_df,
            regime_mode=regime_mode,
            regime_lookback=regime_lookback,
            regime_vol_mode=regime_vol_mode,
            benchmark_weights=benchmark_weights_df,
            factor_returns=factor_returns_df,
        )
    else:
        result = engine.run(
            strategy,
            data,
            fee_rate=float(args.fee_rate),
            slippage=float(args.slippage),
            execution_simulator=exec_sim,
            volume=volume_df,
            high=high_df,
            low=low_df,
            regime_mode=regime_mode,
            regime_lookback=regime_lookback,
            regime_vol_mode=regime_vol_mode,
            benchmark_weights=benchmark_weights_df,
            factor_returns=factor_returns_df,
        )

    if getattr(args, "benchmark", False) or getattr(args, "rebalance_benchmark", False):
        # Equal-weighted buy-and-hold benchmark over the same data window.
        bench_returns = data.pct_change().fillna(0.0)
        n_assets = data.shape[1]
        if n_assets > 0:
            bench_weights = pd.DataFrame(1.0 / n_assets, index=data.index, columns=data.columns)
            bench_series = (bench_weights * bench_returns).sum(axis=1)
            bench_equity = (1.0 + bench_series).cumprod()
            result["benchmark_equity_curve"] = bench_equity
            result["benchmark_total_return"] = (
                float(bench_equity.iloc[-1] - 1.0) if len(bench_equity) else 0.0
            )

    if getattr(args, "walk_forward_report", False):
        try:
            from utils.reporting import (
                generate_walk_forward_html_report,
                generate_walk_forward_pdf_report,
                generate_walk_forward_report,
            )

            wf_rep = generate_walk_forward_report(result)
            artifact_dir = getattr(args, "artifact_dir", None)
            out_path_base = getattr(args, "output_path", None)
            out_path_base = None if out_path_base is None else str(out_path_base)
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if artifact_dir:
                Path(artifact_dir).mkdir(parents=True, exist_ok=True)
                base_path = Path(artifact_dir) / f"walk_forward_{stamp}"
            elif out_path_base:
                pp = Path(out_path_base)
                base_path = pp.parent / f"walk_forward_{pp.stem}_{stamp}"
            else:
                Path("reports").mkdir(parents=True, exist_ok=True)
                base_path = Path("reports") / f"walk_forward_{stamp}"
            try:
                import pandas as _pd

                if isinstance(wf_rep.get("summary"), _pd.DataFrame):
                    (base_path.parent / f"{base_path.name}.csv").write_text(
                        wf_rep["summary"].to_csv(index=False)
                    )
            except Exception:
                pass
            try:
                html_p = base_path.with_suffix(".html")
                Path(html_p).write_text(generate_walk_forward_html_report(wf_rep))
            except Exception:
                pass
            try:
                generate_walk_forward_pdf_report(wf_rep, str(base_path.with_suffix(".pdf")))
            except Exception:
                pass
        except Exception:
            pass

    # Monte Carlo analysis if requested
    monte_carlo_n = getattr(args, "monte_carlo", None)
    if monte_carlo_n:
        try:
            mc_method = getattr(args, "monte_carlo_method", "bootstrap")
            mc_seed = getattr(args, "monte_carlo_seed", None)
            mc_res = monte_carlo_analysis(
                returns=result.get("portfolio_returns"),
                equity_curve=result.get("equity_curve"),
                trade_returns=None,
                n_simulations=int(monte_carlo_n),
                method=mc_method,
                seed=mc_seed,
            )
            print("\n=== Monte Carlo Robustness Analysis ===")
            print(f"Simulations: {mc_res.get('n_simulations')} (method={mc_res.get('method')})")
            fe = mc_res.get("final_equity", {})
            mdd = mc_res.get("max_drawdown", {})
            print(
                "Final Equity: "
                f"mean={fe.get('mean', 0):.3f} "
                f"p5={fe.get('p5', 0):.3f} "
                f"p50={fe.get('p50', 0):.3f} "
                f"p95={fe.get('p95', 0):.3f}"
            )
            print(
                "Max Drawdown:  "
                f"mean={mdd.get('mean', 0):.3f} "
                f"p5={mdd.get('p5', 0):.3f} "
                f"p50={mdd.get('p50', 0):.3f} "
                f"p95={mdd.get('p95', 0):.3f}"
            )
            if isinstance(mdd.get("ci95"), (list, tuple)):
                ci95 = mdd["ci95"]
                print(f"Max Drawdown CI (95%): [{ci95[0]:.3f}, {ci95[1]:.3f}]")
            if mc_res.get("risk_of_ruin") is not None:
                ror = mc_res.get("risk_of_ruin", 0.0)
                thr = mc_res.get("risk_of_ruin_threshold", 0.5)
                print(f"Risk of Ruin (below {thr:.2f}x): {ror:.2%}")
            # Optionally write MC report to artifact dir if requested
            artifact_dir = getattr(args, "artifact_dir", None)
            if artifact_dir:
                try:
                    Path(artifact_dir).mkdir(parents=True, exist_ok=True)
                    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    mc_path = Path(artifact_dir) / f"monte_carlo_{stamp}.json"
                    mc_path.write_text(json.dumps(mc_res, indent=2, default=float))
                except Exception:
                    pass
        except Exception as exc:
            print(f"Monte Carlo analysis failed: {exc}", file=sys.stderr)

    # Emit the requested report (text / json / html / pdf) for the chosen report
    # kind (full / risk / attribution). Attribution results produced by the
    # engine (brinson / factor) are surfaced automatically when benchmark
    # weights / factor returns were provided via --benchmark-weights-csv /
    # --factor-returns-csv.
    from utils.reporting import (
        attribution_report_to_dict,
        generate_attribution_report,
        generate_html_report,
        generate_pdf_report,
        generate_report,
        generate_risk_report,
        report_to_dict,
        risk_report_to_dict,
    )

    report_kind = getattr(args, "report", "full") or "full"
    output_format = getattr(args, "output", "text") or "text"
    output_path = getattr(args, "output_path", None)
    title = getattr(args, "title", None) or "Backtest Report"

    if report_kind == "attribution":
        text = generate_attribution_report(result)
        data = attribution_report_to_dict(result)
    elif report_kind == "risk":
        text = generate_risk_report(result)
        data = risk_report_to_dict(result)
    else:
        text = generate_report(result)
        data = report_to_dict(result)

    def _emit(content: str, path: str | None) -> None:
        if path is not None:
            Path(path).write_text(content)
        else:
            print(content)

    if output_format == "json":
        _emit(json.dumps(data, indent=2, default=float), output_path)
    elif output_format == "html":
        _emit(generate_html_report(result, title=title), output_path)
    elif output_format == "pdf":
        if output_path is None:
            Path("reports").mkdir(parents=True, exist_ok=True)
            output_path = str(
                Path("reports") / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            )
        generate_pdf_report(result, str(output_path), title=title)
        print(f"PDF report written to {output_path}")
    else:
        _emit(text, output_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
