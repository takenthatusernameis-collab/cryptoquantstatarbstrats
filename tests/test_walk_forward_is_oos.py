"""Tests for in-sample vs out-of-sample walk-forward reporting."""

from __future__ import annotations

import contextlib
import io
import json

import numpy as np
import pandas as pd

from backtest.cli import main
from backtest.engine import BacktestEngine
from data.loader import DataLoader
from strategies.mean_reversion import MeanReversionStrategy
from utils.reporting import (
    generate_walk_forward_html_report,
    generate_walk_forward_pdf_report,
    generate_walk_forward_report,
    generate_walk_forward_text_report,
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


def test_walk_forward_portfolio_attaches_is_oos_per_window():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    res = engine.walk_forward_portfolio(w, data, train_period=40, test_period=10)
    results = res.get("results", [])
    assert len(results) > 0
    for r in results:
        assert "is_total_return" in r
        assert "is_sharpe_ratio" in r
        assert "is_max_drawdown" in r
        assert "oos_total_return" in r
        assert r["oos_total_return"] == r["total_return"]


def test_walk_forward_portfolio_is_oos_aggregates():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    res = engine.walk_forward_portfolio(w, data, train_period=40, test_period=10)
    assert "is_mean_return" in res
    assert "oos_mean_return" in res
    assert "oos_is_ratio" in res
    assert isinstance(res["is_mean_return"], float)
    assert isinstance(res["oos_mean_return"], float)
    assert isinstance(res["oos_is_ratio"], float)


def test_walk_forward_strategy_attaches_is_oos_per_window():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    strategy = MeanReversionStrategy(asset="BTC")
    res = engine.walk_forward(strategy, data, train_period=40, test_period=10)
    results = res.get("results", [])
    assert len(results) > 0
    for r in results:
        assert "is_total_return" in r
        assert "is_sharpe_ratio" in r
        assert "is_max_drawdown" in r
        assert "oos_total_return" in r
        assert r["oos_total_return"] == r["total_return"]
    assert "is_mean_return" in res
    assert "oos_mean_return" in res
    assert "oos_is_ratio" in res


def test_generate_walk_forward_report_includes_is_oos_columns():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    res = engine.walk_forward_portfolio(w, data, train_period=40, test_period=10)
    wf_rep = generate_walk_forward_report(res)
    summary = wf_rep["summary"]
    assert isinstance(summary, pd.DataFrame) and len(summary) > 0
    for col in ("is_total_return", "is_sharpe_ratio", "is_max_drawdown", "oos_total_return"):
        assert col in summary.columns, f"missing column {col}"
    assert "is_vs_oos" in wf_rep
    iso = wf_rep["is_vs_oos"]
    assert isinstance(iso, dict)
    for key in ("is_mean_return", "oos_mean_return", "oos_is_ratio"):
        assert key in iso, f"missing aggregate {key}"


def test_walk_forward_text_report_renders_is_oos():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    res = engine.walk_forward_portfolio(w, data, train_period=40, test_period=10)
    wf_rep = generate_walk_forward_report(res)
    text = generate_walk_forward_text_report(wf_rep)
    assert "Walk-Forward Report" in text
    assert "In-Sample vs Out-of-Sample" in text
    assert "Mean IS Return" in text
    assert "Mean OOS Return" in text
    assert "OOS/IS Ratio" in text


def test_walk_forward_html_report_renders_is_oos():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    res = engine.walk_forward_portfolio(w, data, train_period=40, test_period=10)
    wf_rep = generate_walk_forward_report(res)
    html = generate_walk_forward_html_report(wf_rep)
    assert "In-Sample vs Out-of-Sample" in html
    assert "Mean Return" in html
    assert "OOS/IS Ratio" in html


def test_walk_forward_pdf_report_renders_is_oos(tmp_path):
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    res = engine.walk_forward_portfolio(w, data, train_period=40, test_period=10)
    wf_rep = generate_walk_forward_report(res)
    out_pdf = tmp_path / "wf_is_oos.pdf"
    generate_walk_forward_pdf_report(wf_rep, str(out_pdf))
    assert out_pdf.exists() and out_pdf.stat().st_size > 0
    assert out_pdf.read_bytes()[:4] == b"%PDF"


def test_walk_forward_report_to_dict_includes_is_vs_oos():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    res = engine.walk_forward_portfolio(w, data, train_period=40, test_period=10)
    wf_rep = generate_walk_forward_report(res)
    d = walk_forward_report_to_dict(wf_rep)
    assert "is_vs_oos" in d
    iso = d["is_vs_oos"]
    assert isinstance(iso, dict)
    assert "is_mean_return" in iso
    assert "oos_mean_return" in iso
    assert "oos_is_ratio" in iso


def test_walk_forward_is_oos_backward_compat_when_absent():
    # Too little data for even one walk-forward window: engine takes the
    # early-return path whose single result has no IS keys.
    data = _make_data().iloc[:20]
    engine = BacktestEngine(initial_capital=100000)
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    res = engine.walk_forward_portfolio(w, data, train_period=40, test_period=10)
    results = res.get("results", [])
    assert len(results) == 1
    assert "is_total_return" not in results[0]
    wf_rep = generate_walk_forward_report(res)
    summary = wf_rep["summary"]
    assert "is_total_return" not in summary.columns
    assert "is_vs_oos" not in wf_rep
    # Report generators must not crash without IS data.
    _ = walk_forward_report_to_dict(wf_rep)
    assert isinstance(generate_walk_forward_text_report(wf_rep), str)
    assert isinstance(generate_walk_forward_html_report(wf_rep), str)


def test_walk_forward_cli_is_oos_text(tmp_path):
    price = _make_cli_files(tmp_path)
    out = _run_cli(
        [
            "--walk-forward",
            "--strategy", "mean_reversion",
            "--asset", "BTC",
            "--data-source", "csv",
            "--data-csv", price,
            "--output", "text",
            "--train-period", "40",
            "--test-period", "10",
        ]
    )
    assert "In-Sample vs Out-of-Sample" in out
    assert "Mean IS Return" in out
    assert "Mean OOS Return" in out
    assert "OOS/IS Ratio" in out


def test_walk_forward_cli_is_oos_json(tmp_path):
    price = _make_cli_files(tmp_path)
    out_path = tmp_path / "wf_is_oos.json"
    _run_cli(
        [
            "--walk-forward",
            "--strategy", "mean_reversion",
            "--asset", "BTC",
            "--data-source", "csv",
            "--data-csv", price,
            "--report", "attribution",
            "--output", "json",
            "--output-path", str(out_path),
            "--train-period", "40",
            "--test-period", "10",
        ]
    )
    payload = json.loads(out_path.read_text())
    assert isinstance(payload, dict)
    assert "is_vs_oos" in payload
    iso = payload["is_vs_oos"]
    assert "is_mean_return" in iso
    assert "oos_mean_return" in iso
    assert "oos_is_ratio" in iso
