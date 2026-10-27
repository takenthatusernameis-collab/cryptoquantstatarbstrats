"""
Tests for the backtest CLI and volume-tied partial fills.

Covers the CLI text/JSON output (reusing ``utils.reporting``) and the
engine's volume-tied partial-fill behavior executed through the same
``run``/``run_portfolio`` path the CLI uses.
"""

from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from backtest.cli import build_parser, main
from backtest.engine import BacktestEngine
from backtest.execution import ExecutionSimulator


def _make_data(n: int = 200, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2024-01-01", periods=n, freq="1h")
    return pd.DataFrame(
        {"BTC": 100 * np.exp(np.cumsum(rng.normal(0.0, 0.02, n)))},
        index=dates,
    )


def _run_cli(argv: list[str]) -> str:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = main(argv)
    assert code == 0
    return buf.getvalue()


def test_cli_parser_defaults():
    parser = build_parser()
    ns = parser.parse_args([])
    assert ns.strategy == "mean_reversion"
    assert ns.output == "text"
    assert ns.report == "full"
    assert ns.asset == "BTC"
    assert ns.initial_capital == 100_000.0


def test_cli_text_output_contains_report_sections():
    out = _run_cli(["--strategy", "mean_reversion", "--asset", "BTC"])
    assert "Backtest Report" in out
    assert "Total Return" in out
    assert "Sharpe Ratio" in out
    assert "Sortino Ratio" in out
    assert "VaR (95%)" in out
    assert "CVaR (95%)" in out
    assert "Max Drawdown" in out
    assert "Calmar Ratio" in out


def test_cli_json_output_is_serializable():
    out = _run_cli(
        ["--strategy", "pairs", "--pair", "BTC", "ETH", "--output", "json"]
    )
    payload = json.loads(out)
    assert isinstance(payload, dict)
    for key, value in payload.items():
        assert isinstance(value, (float, int, str)), f"{key}: {type(value)}"
    assert "total_return" in payload
    assert "sharpe_ratio" in payload
    assert "max_drawdown" in payload
    assert "equity_curve" not in payload
    assert "weights" not in payload


def test_cli_risk_report():
    out = _run_cli(
        ["--strategy", "mean_reversion", "--asset", "BTC", "--report", "risk"]
    )
    assert "Risk Report" in out
    assert "VaR (95%)" in out
    assert "Max Drawdown" in out


def test_cli_invalid_strategy_exits():
    with pytest.raises(SystemExit):
        main(["--strategy", "not_a_strategy"])


def test_cli_pairs_strategy_runs():
    out = _run_cli(["--strategy", "pairs", "--pair", "BTC", "ETH", "--output", "json"])
    payload = json.loads(out)
    assert "total_return" in payload


def test_cli_term_structure_strategy_runs():
    out = _run_cli(["--strategy", "term_structure", "--output", "json"])
    payload = json.loads(out)
    assert "total_return" in payload


def test_cli_term_structure_strategy_config_override(tmp_path):
    import yaml

    data = _make_data(n=50)
    df = data.copy()
    df["iv_30d"] = 0.5 + 0.01 * np.arange(len(df))
    df["iv_90d"] = 0.6 + 0.005 * np.arange(len(df))
    path = tmp_path / "term.csv"
    df.to_csv(path)

    cfg_path = tmp_path / "config.yaml"
    cfg_path.write_text(
        yaml.safe_dump(
            {
                "strategy": "term_structure",
                "symbols": ["BTC"],
                "start": "2024-01-01",
                "end": "2024-01-03",
                "freq": "1h",
                "near_tenor": "iv_30d",
                "far_tenor": "iv_90d",
                "lookback": 10,
                "entry_threshold": 1.5,
                "exit_threshold": 0.3,
                "asset": "BTC",
                "output": "json",
            }
        )
    )
    out = _run_cli(["--config", str(cfg_path)])
    payload = json.loads(out)
    assert "total_return" in payload


def _volume_frame(index: pd.Index, volume: float) -> pd.DataFrame:
    return pd.DataFrame({"BTC": float(volume)}, index=index)


def test_volume_tied_partial_fills_reduce_return():
    data = _make_data(n=150)
    weights = pd.DataFrame(1.0, index=data.index, columns=data.columns)

    # Tiny bar volume relative to the order size forces heavy partial fills.
    low_vol = _volume_frame(data.index, volume=1.0)
    sim_low = ExecutionSimulator(participation_rate=0.01, slippage_bps=0)
    low = BacktestEngine(initial_capital=100_000.0).run_portfolio(
        weights, data, execution_simulator=sim_low, volume=low_vol
    )

    # Large bar volume means no participation cap binds -> full fills.
    high_vol = _volume_frame(data.index, volume=1_000_000.0)
    sim_high = ExecutionSimulator(participation_rate=0.01, slippage_bps=0)
    high = BacktestEngine(initial_capital=100_000.0).run_portfolio(
        weights, data, execution_simulator=sim_high, volume=high_vol
    )

    # Partial fills leave the position under-filled vs the target, so with
    # zero slippage the low-volume run should not outperform the full-fill run.
    assert low["total_return"] <= high["total_return"] + 1e-9
    assert any(f["status"] == "partial" for f in sim_low.fills())
    assert all(f["status"] != "partial" for f in sim_high.fills())


def test_volume_absent_matches_full_fill_behavior():
    """Without a volume DataFrame the engine behaves as before (full fills)."""
    data = _make_data(n=100)
    weights = pd.DataFrame(1.0, index=data.index, columns=data.columns)

    sim = ExecutionSimulator(participation_rate=0.01, slippage_bps=0)
    with_vol = BacktestEngine(initial_capital=100_000.0).run_portfolio(
        weights, data, execution_simulator=sim, volume=_volume_frame(data.index, 1_000_000.0)
    )
    without_vol = BacktestEngine(initial_capital=100_000.0).run_portfolio(
        weights, data, execution_simulator=sim
    )
    assert abs(with_vol["total_return"] - without_vol["total_return"]) < 1e-9


def test_cli_vwap_order_type_runs():
    out = _run_cli(
        [
            "--strategy", "mean_reversion", "--asset", "BTC",
            "--execution-simulator", "--order-type", "vwap",
        ]
    )
    assert "Backtest Report" in out


def test_cli_twap_order_type_runs():
    out = _run_cli(
        [
            "--strategy", "mean_reversion", "--asset", "BTC",
            "--execution-simulator", "--order-type", "twap",
        ]
    )
    assert "Backtest Report" in out


def _write_csv(tmp_path: Path, name: str, index: pd.Index, values: dict[str, float]) -> str:
    df = pd.DataFrame(values, index=index)
    path = tmp_path / name
    df.to_csv(path)
    return str(path)


def test_cli_high_low_csv_drives_vwap_fills(tmp_path):
    data = _make_data(n=50)
    high = _write_csv(tmp_path, "high.csv", data.index, {"BTC": 120.0})
    low = _write_csv(tmp_path, "low.csv", data.index, {"BTC": 80.0})
    out = _run_cli(
        [
            "--strategy", "mean_reversion", "--asset", "BTC",
            "--execution-simulator", "--order-type", "vwap",
            "--high-csv", high, "--low-csv", low,
        ]
    )
    assert "Backtest Report" in out


def test_cli_config_drives_vwap_and_ohlc(tmp_path):
    import yaml

    data = _make_data(n=50)
    high = _write_csv(tmp_path, "high.csv", data.index, {"BTC": 120.0})
    low = _write_csv(tmp_path, "low.csv", data.index, {"BTC": 80.0})
    cfg_path = tmp_path / "config.yaml"
    cfg_path.write_text(
        yaml.safe_dump(
            {
                "strategy": "mean_reversion",
                "asset": "BTC",
                "execution_simulator": True,
                "order_type": "vwap",
                "high_csv": high,
                "low_csv": low,
                "output": "json",
            }
        )
    )
    out = _run_cli(["--config", str(cfg_path)])
    payload = json.loads(out)
    assert "total_return" in payload


def test_cli_html_title_appears(tmp_path):
    out_path = tmp_path / "report.html"
    _run_cli(
        [
            "--strategy",
            "mean_reversion",
            "--asset",
            "BTC",
            "--output",
            "html",
            "--title",
            "My Custom Title",
            "--output-path",
            str(out_path),
        ]
    )
    content = out_path.read_text()
    assert "My Custom Title" in content
    assert "<!DOCTYPE html>" in content


def test_cli_title_default_in_html():
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = main(
            ["--strategy", "mean_reversion", "--asset", "BTC", "--output", "html"]
        )
    assert code == 0
    assert "Backtest Report" in buf.getvalue()


def test_cli_benchmark_flag_parses():
    parser = build_parser()
    ns = parser.parse_args(["--benchmark"])
    assert ns.benchmark is True
    ns_off = parser.parse_args([])
    assert ns_off.benchmark is False


def test_cli_html_includes_benchmark_line(tmp_path):
    out_path = tmp_path / "report_bench.html"
    _run_cli(
        [
            "--strategy",
            "mean_reversion",
            "--asset",
            "BTC",
            "--output",
            "html",
            "--benchmark",
            "--output-path",
            str(out_path),
        ]
    )
    content = out_path.read_text()
    assert "<!DOCTYPE html>" in content
    # Benchmark equity polyline (green, dashed) rendered into the SVG.
    assert "#2ca02c" in content


def test_cli_rebalance_benchmark_flag_parses():
    parser = build_parser()
    ns = parser.parse_args(["--rebalance-benchmark"])
    assert ns.rebalance_benchmark is True


def test_cli_walk_forward_report_flag_parses():
    parser = build_parser()
    ns = parser.parse_args(["--walk-forward-report"])
    assert ns.walk_forward_report is True


def test_cli_walk_forward_report_artifacts(tmp_path):
    _run_cli(
        [
            "--symbols",
            "BTC",
            "ETH",
            "--start",
            "2024-01-01",
            "--end",
            "2024-01-05",
            "--freq",
            "1h",
            "--walk-forward",
            "--walk-forward-report",
            "--artifact-dir",
            str(tmp_path),
        ]
    )
    files = list(tmp_path.glob("walk_forward*"))
    assert len(files) >= 1
    names = [f.name for f in files]
    assert any(n.endswith(".csv") for n in names)
    assert any(n.endswith(".html") for n in names) or any(n.endswith(".pdf") for n in names)
