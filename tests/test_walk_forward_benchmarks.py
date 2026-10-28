"""Tests for strategy benchmark registry attachment to walk-forward reports."""

from __future__ import annotations

import contextlib
import csv
import io
import json

import numpy as np
import pandas as pd

from backtest.cli import main
from backtest.engine import BacktestEngine
from data.loader import DataLoader
from utils.reporting import (
    generate_walk_forward_html_report,
    generate_walk_forward_pdf_report,
    generate_walk_forward_report,
    generate_walk_forward_text_report,
    load_benchmarks_csv,
    walk_forward_report_to_dict,
)


def _make_data():
    loader = DataLoader()
    data = loader.load_data(["BTC", "ETH"], "2024-01-01", "2024-04-01", freq="1d")
    return loader.clean_data(data)


def _run_cli(argv: list[str]) -> str:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = main(argv)
    assert code == 0
    return buf.getvalue()


def _make_cli_files(tmp_path):
    rng = np.random.default_rng(7)
    dates = pd.date_range("2024-01-01", periods=120, freq="1h")
    data = pd.DataFrame(
        {
            "BTC": 100 * np.exp(np.cumsum(rng.normal(0, 0.02, 120))),
            "ETH": 100 * np.exp(np.cumsum(rng.normal(0, 0.02, 120))),
        },
        index=dates,
    )
    price_path = tmp_path / "prices.csv"
    data.to_csv(price_path)
    return str(price_path)


def _make_benchmarks_csv(tmp_path, benchmarks):
    path = tmp_path / "benchmarks.csv"
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "name",
                "mean_return",
                "max_drawdown",
                "total_return",
                "sharpe_ratio",
            ],
        )
        writer.writeheader()
        for benchmark in benchmarks:
            writer.writerow(benchmark)
    return str(path)


def _run_walk_forward():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    res = engine.walk_forward_portfolio(w, data, train_period=40, test_period=10)
    return res


def test_load_benchmarks_csv(tmp_path):
    benchmarks = [
        {
            "name": "BuyAndHold",
            "mean_return": "0.04",
            "max_drawdown": "0.10",
            "total_return": "0.12",
            "sharpe_ratio": "1.2",
        },
        {
            "name": "Momentum",
            "mean_return": "0.03",
            "max_drawdown": "0.08",
        },
    ]
    path = _make_benchmarks_csv(tmp_path, benchmarks)
    loaded = load_benchmarks_csv(path)
    assert len(loaded) == 2
    assert loaded[0]["name"] == "BuyAndHold"
    assert loaded[0]["mean_return"] == 0.04
    assert loaded[0]["max_drawdown"] == 0.10
    assert loaded[0]["total_return"] == 0.12
    assert loaded[0]["sharpe_ratio"] == 1.2
    assert loaded[1]["name"] == "Momentum"
    assert loaded[1]["total_return"] == 0.0
    assert loaded[1]["sharpe_ratio"] == 0.0


def test_generate_walk_forward_report_attaches_benchmarks():
    res = _run_walk_forward()
    benchmarks = [
        {"name": "BuyAndHold", "mean_return": 0.04, "max_drawdown": 0.10},
        {"name": "Momentum", "mean_return": 0.03, "max_drawdown": 0.08},
    ]
    wf_rep = generate_walk_forward_report(res, benchmarks=benchmarks)
    assert "benchmarks" in wf_rep
    bm = wf_rep["benchmarks"]
    assert isinstance(bm, dict)
    assert bm["benchmark_count"] == 2
    assert len(bm["benchmarks"]) == 2
    for row in bm["benchmarks"]:
        assert "name" in row
        assert "wf_oos_mean_return" in row
        assert "benchmark_mean_return" in row
        assert "wf_oos_max_drawdown" in row
        assert "benchmark_max_drawdown" in row
    assert bm["benchmarks"][0]["name"] == "BuyAndHold"
    assert bm["benchmarks"][0]["benchmark_mean_return"] == 0.04
    assert bm["wf_oos_mean_return"] == bm["benchmarks"][0]["wf_oos_mean_return"]


def test_benchmarks_uses_wf_result_key():
    res = _run_walk_forward()
    benchmarks = {
        "benchmarks": [
            {"name": "X", "mean_return": 0.05, "max_drawdown": 0.05}
        ]
    }
    wf_rep = generate_walk_forward_report(res, benchmarks=benchmarks)
    assert "benchmarks" in wf_rep
    assert wf_rep["benchmarks"]["benchmark_count"] == 1


def test_walk_forward_text_report_renders_benchmarks():
    res = _run_walk_forward()
    benchmarks = [
        {"name": "BuyAndHold", "mean_return": 0.04, "max_drawdown": 0.10},
    ]
    wf_rep = generate_walk_forward_report(res, benchmarks=benchmarks)
    text = generate_walk_forward_text_report(wf_rep)
    assert "Strategy Benchmarks" in text
    assert "BuyAndHold" in text
    assert "bench_mean_return" in text


def test_walk_forward_html_report_renders_benchmarks():
    res = _run_walk_forward()
    benchmarks = [
        {"name": "BuyAndHold", "mean_return": 0.04, "max_drawdown": 0.10},
    ]
    wf_rep = generate_walk_forward_report(res, benchmarks=benchmarks)
    html = generate_walk_forward_html_report(wf_rep)
    assert "Strategy Benchmarks" in html
    assert "BuyAndHold" in html


def test_walk_forward_pdf_report_renders_benchmarks(tmp_path):
    res = _run_walk_forward()
    benchmarks = [
        {"name": "BuyAndHold", "mean_return": 0.04, "max_drawdown": 0.10},
    ]
    wf_rep = generate_walk_forward_report(res, benchmarks=benchmarks)
    out_pdf = tmp_path / "wf_benchmarks.pdf"
    generate_walk_forward_pdf_report(wf_rep, str(out_pdf))
    assert out_pdf.exists() and out_pdf.stat().st_size > 0
    assert out_pdf.read_bytes()[:4] == b"%PDF"


def test_walk_forward_report_to_dict_includes_benchmarks():
    res = _run_walk_forward()
    benchmarks = [
        {"name": "BuyAndHold", "mean_return": 0.04, "max_drawdown": 0.10},
    ]
    wf_rep = generate_walk_forward_report(res, benchmarks=benchmarks)
    d = walk_forward_report_to_dict(wf_rep)
    assert "benchmarks" in d
    bm = d["benchmarks"]
    assert isinstance(bm, dict)
    assert "benchmarks" in bm
    assert bm["benchmark_count"] == 1
    assert bm["benchmarks"][0]["name"] == "BuyAndHold"
    assert bm["benchmarks"][0]["benchmark_mean_return"] == 0.04
    assert isinstance(bm["benchmarks"][0]["benchmark_mean_return"], float)
    assert isinstance(bm["wf_oos_mean_return"], float)


def test_benchmarks_backward_compat_when_absent():
    res = _run_walk_forward()
    wf_rep = generate_walk_forward_report(res)
    assert "benchmarks" not in wf_rep
    assert isinstance(wf_rep.get("summary"), pd.DataFrame)
    _ = walk_forward_report_to_dict(wf_rep)
    assert isinstance(generate_walk_forward_text_report(wf_rep), str)
    assert isinstance(generate_walk_forward_html_report(wf_rep), str)
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        generate_walk_forward_pdf_report(wf_rep, f"{td}/wf_benchmarks.pdf")


def test_walk_forward_cli_benchmarks_text(tmp_path):
    price = _make_cli_files(tmp_path)
    benchmarks = _make_benchmarks_csv(
        tmp_path,
        [
            {
                "name": "BuyAndHold",
                "mean_return": "0.04",
                "max_drawdown": "0.10",
            }
        ],
    )
    out = _run_cli(
        [
            "--walk-forward",
            "--strategy", "mean_reversion",
            "--asset", "BTC",
            "--data-source", "csv",
            "--data-csv", price,
            "--benchmarks-csv", benchmarks,
            "--output", "text",
            "--train-period", "40",
            "--test-period", "10",
        ]
    )
    assert "Strategy Benchmarks" in out
    assert "BuyAndHold" in out


def test_walk_forward_cli_benchmarks_json(tmp_path):
    price = _make_cli_files(tmp_path)
    benchmarks = _make_benchmarks_csv(
        tmp_path,
        [
            {
                "name": "BuyAndHold",
                "mean_return": "0.04",
                "max_drawdown": "0.10",
            }
        ],
    )
    out_path = tmp_path / "wf_benchmarks.json"
    _run_cli(
        [
            "--walk-forward",
            "--strategy", "mean_reversion",
            "--asset", "BTC",
            "--data-source", "csv",
            "--data-csv", price,
            "--benchmarks-csv", benchmarks,
            "--report", "attribution",
            "--output", "json",
            "--output-path", str(out_path),
            "--train-period", "40",
            "--test-period", "10",
        ]
    )
    payload = json.loads(out_path.read_text())
    assert isinstance(payload, dict)
    assert "benchmarks" in payload
    bm = payload["benchmarks"]
    assert bm["benchmark_count"] == 1
    assert bm["benchmarks"][0]["name"] == "BuyAndHold"
    assert bm["benchmarks"][0]["benchmark_mean_return"] == 0.04
