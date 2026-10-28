"""Tests for the strategy benchmark registry dashboard."""

from __future__ import annotations

import contextlib
import csv
import io

from backtest.cli import main
from utils.reporting import (
    aggregate_benchmark_registry,
    generate_benchmark_dashboard_html,
)


def _make_benchmarks_csv(tmp_path, benchmarks):
    path = tmp_path / "benchmarks.csv"
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["name", "mean_return", "max_drawdown", "total_return", "sharpe_ratio"],
        )
        writer.writeheader()
        for benchmark in benchmarks:
            writer.writerow(benchmark)
    return str(path)


def _run_cli(argv: list[str]) -> str:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = main(argv)
    assert code == 0
    return buf.getvalue()


def test_aggregate_benchmark_registry_list_input():
    benchmarks = [
        {"name": "BuyAndHold", "mean_return": 0.04, "max_drawdown": 0.10, "sharpe_ratio": 0.8},
        {"name": "Momentum", "mean_return": 0.06, "max_drawdown": 0.15, "sharpe_ratio": 1.1},
        {"name": "MeanReversion", "mean_return": 0.02, "max_drawdown": 0.08, "sharpe_ratio": 0.6},
    ]
    agg = aggregate_benchmark_registry(benchmarks)
    assert agg["count"] == 3
    assert agg["mean_return"] == (0.04 + 0.06 + 0.02) / 3
    assert agg["mean_drawdown"] == (0.10 + 0.15 + 0.08) / 3
    assert len(agg["benchmarks"]) == 3
    assert agg["benchmarks"][0]["name"] == "BuyAndHold"
    assert agg["benchmarks"][0]["mean_return"] == 0.04


def test_aggregate_benchmark_registry_dict_input():
    benchmarks = {
        "benchmarks": [
            {"name": "BuyAndHold", "mean_return": 0.04, "max_drawdown": 0.10},
            {"name": "Momentum", "mean_return": 0.06, "max_drawdown": 0.15},
        ]
    }
    agg = aggregate_benchmark_registry(benchmarks)
    assert agg["count"] == 2
    assert agg["mean_return"] == 0.05
    assert agg["mean_drawdown"] == 0.125


def test_aggregate_benchmark_registry_single_dict_input():
    benchmarks = {"name": "BuyAndHold", "mean_return": 0.04, "max_drawdown": 0.10}
    agg = aggregate_benchmark_registry(benchmarks)
    assert agg["count"] == 1
    assert agg["mean_return"] == 0.04


def test_aggregate_benchmark_registry_empty_and_none():
    assert aggregate_benchmark_registry([])["count"] == 0
    assert aggregate_benchmark_registry(None)["count"] == 0
    assert aggregate_benchmark_registry({})["count"] == 0
    agg = aggregate_benchmark_registry(None)
    assert agg["mean_return"] == 0.0
    assert agg["mean_drawdown"] == 0.0


def test_aggregate_benchmark_registry_optional_fields_default():
    benchmarks = [{"name": "OnlyName"}]
    agg = aggregate_benchmark_registry(benchmarks)
    assert agg["count"] == 1
    assert agg["benchmarks"][0]["mean_return"] == 0.0
    assert agg["benchmarks"][0]["max_drawdown"] == 0.0
    assert agg["benchmarks"][0]["total_return"] == 0.0
    assert agg["benchmarks"][0]["sharpe_ratio"] == 0.0


def test_generate_benchmark_dashboard_html_rendering():
    benchmarks = [
        {"name": "BuyAndHold", "mean_return": 0.04, "max_drawdown": 0.10, "sharpe_ratio": 0.8},
        {"name": "Momentum", "mean_return": 0.06, "max_drawdown": 0.15, "sharpe_ratio": 1.1},
    ]
    html = generate_benchmark_dashboard_html(benchmarks)
    assert isinstance(html, str)
    assert "<!DOCTYPE html>" in html
    assert "Benchmark Registry Dashboard" in html
    assert "BuyAndHold" in html
    assert "Momentum" in html
    assert "4.0000%" in html
    assert "<table" in html
    assert "<th>Mean Return</th>" in html


def test_generate_benchmark_dashboard_html_empty():
    html = generate_benchmark_dashboard_html([])
    assert isinstance(html, str)
    assert "Count: 0" in html
    assert "<table" in html


def test_generate_benchmark_dashboard_html_none():
    html = generate_benchmark_dashboard_html(None)
    assert isinstance(html, str)
    assert "Count: 0" in html


def test_generate_benchmark_dashboard_html_missing_fields():
    benchmarks = [{"name": "Partial"}]
    html = generate_benchmark_dashboard_html(benchmarks)
    assert "Partial" in html
    assert "<table" in html


def test_generate_benchmark_dashboard_html_dict_input():
    benchmarks = {
        "benchmarks": [
            {"name": "BuyAndHold", "mean_return": 0.04, "max_drawdown": 0.10},
            {"name": "Momentum", "mean_return": 0.06, "max_drawdown": 0.15},
        ]
    }
    html = generate_benchmark_dashboard_html(benchmarks)
    assert "BuyAndHold" in html
    assert "Momentum" in html
    assert "Count: 2" in html


def test_benchmark_dashboard_cli_integration(tmp_path):
    benchmarks = [
        {
            "name": "BuyAndHold",
            "mean_return": "0.04",
            "max_drawdown": "0.10",
            "sharpe_ratio": "0.8",
        },
        {
            "name": "Momentum",
            "mean_return": "0.06",
            "max_drawdown": "0.15",
            "sharpe_ratio": "1.1",
        },
    ]
    csv_path = _make_benchmarks_csv(tmp_path, benchmarks)
    out_path = tmp_path / "benchmark_dashboard.html"
    output = _run_cli(
        ["benchmarks-dashboard", "--benchmarks-csv", csv_path, "--output", str(out_path)]
    )
    assert out_path.exists()
    content = out_path.read_text()
    assert "<!DOCTYPE html>" in content
    assert "Benchmark Registry Dashboard" in content
    assert "BuyAndHold" in content
    assert "Momentum" in content
    # stdout should be empty when writing to a file.
    assert output.strip() == ""


def test_benchmark_dashboard_cli_prints_html_when_no_output(tmp_path):
    benchmarks = [
        {"name": "BuyAndHold", "mean_return": "0.04", "max_drawdown": "0.10"},
    ]
    csv_path = _make_benchmarks_csv(tmp_path, benchmarks)
    output = _run_cli(["benchmarks-dashboard", "--benchmarks-csv", csv_path])
    assert "Benchmark Registry Dashboard" in output
    assert "BuyAndHold" in output


def test_benchmark_dashboard_cli_backward_compat_empty_csv(tmp_path):
    csv_path = _make_benchmarks_csv(tmp_path, [])
    out_path = tmp_path / "benchmark_dashboard_empty.html"
    _run_cli(
        ["benchmarks-dashboard", "--benchmarks-csv", csv_path, "--output", str(out_path)]
    )
    assert out_path.exists()
    content = out_path.read_text()
    assert "Count: 0" in content
