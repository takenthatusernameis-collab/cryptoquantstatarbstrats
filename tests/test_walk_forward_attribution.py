"""Tests for walk-forward attribution aggregation and reporting."""

from __future__ import annotations

import contextlib
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
    bench_path = tmp_path / "bench.csv"
    pd.DataFrame({"BTC": 0.6, "ETH": 0.4}, index=dates).to_csv(bench_path)
    factor_path = tmp_path / "factors.csv"
    pd.DataFrame({"mkt": rng.normal(0, 0.01, 120)}, index=dates).to_csv(factor_path)
    return str(price_path), str(bench_path), str(factor_path)


def test_walk_forward_aggregates_attribution_across_windows():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    # create benchmark weights aligned
    bench = pd.DataFrame({"BTC": 0.6, "ETH": 0.4}, index=data.index)
    # create factor returns
    rng = np.random.default_rng(123)
    factors = pd.DataFrame({"mkt": rng.normal(0, 0.01, len(data))}, index=data.index)
    res = engine.walk_forward_portfolio(
        w, data, train_period=40, test_period=10,
        benchmark_weights=bench, factor_returns=factors,
    )
    # aggregate report
    wf_rep = generate_walk_forward_report(res)
    assert "brinson" in wf_rep or "factor" in wf_rep
    # also check dict conversion
    d = walk_forward_report_to_dict(wf_rep)
    assert isinstance(d, dict)


def test_walk_forward_html_pdf_include_attribution_when_present(tmp_path):
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    bench = pd.DataFrame({"BTC": 0.6, "ETH": 0.4}, index=data.index)
    rng = np.random.default_rng(456)
    factors = pd.DataFrame({"mkt": rng.normal(0, 0.01, len(data))}, index=data.index)
    res = engine.walk_forward_portfolio(
        w, data, train_period=40, test_period=10,
        benchmark_weights=bench, factor_returns=factors,
    )
    wf_rep = generate_walk_forward_report(res)
    html = generate_walk_forward_html_report(wf_rep)
    assert "Attribution" in html
    out_pdf = tmp_path / "wf.pdf"
    generate_walk_forward_pdf_report(wf_rep, str(out_pdf))
    assert out_pdf.exists() or (tmp_path / "wf.html").exists()


def test_walk_forward_no_attribution_backward_compat():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    res = engine.walk_forward_portfolio(w, data, train_period=40, test_period=10)
    wf_rep = generate_walk_forward_report(res)
    # should not crash
    _ = walk_forward_report_to_dict(wf_rep)
    html = generate_walk_forward_html_report(wf_rep)
    assert isinstance(html, str)


def test_walk_forward_text_report_renders_attribution():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    bench = pd.DataFrame({"BTC": 0.6, "ETH": 0.4}, index=data.index)
    rng = np.random.default_rng(456)
    factors = pd.DataFrame({"mkt": rng.normal(0, 0.01, len(data))}, index=data.index)
    res = engine.walk_forward_portfolio(
        w, data, train_period=40, test_period=10,
        benchmark_weights=bench, factor_returns=factors,
    )
    wf_rep = generate_walk_forward_report(res)
    text = generate_walk_forward_text_report(wf_rep)
    assert "Walk-Forward Report" in text
    assert "Brinson" in text or "Allocation" in text
    assert "Factor" in text or "Alpha" in text


def test_walk_forward_cli_attribution_text(tmp_path):
    price, bench, factors = _make_cli_files(tmp_path)
    out = _run_cli(
        [
            "--walk-forward",
            "--strategy", "mean_reversion",
            "--asset", "BTC",
            "--data-source", "csv",
            "--data-csv", price,
            "--benchmark-weights-csv", bench,
            "--factor-returns-csv", factors,
            "--report", "attribution",
            "--output", "text",
            "--train-period", "40",
            "--test-period", "10",
        ]
    )
    assert "Brinson" in out
    assert "Allocation" in out or "allocation" in out.lower()
    assert "Selection" in out or "selection" in out.lower()
    assert "Interaction" in out or "interaction" in out.lower()
    assert "Factor" in out


def test_walk_forward_cli_attribution_json(tmp_path):
    price, bench, factors = _make_cli_files(tmp_path)
    out_path = tmp_path / "wf_attr.json"
    _run_cli(
        [
            "--walk-forward",
            "--strategy", "mean_reversion",
            "--asset", "BTC",
            "--data-source", "csv",
            "--data-csv", price,
            "--benchmark-weights-csv", bench,
            "--factor-returns-csv", factors,
            "--report", "attribution",
            "--output", "json",
            "--output-path", str(out_path),
            "--train-period", "40",
            "--test-period", "10",
        ]
    )
    payload = json.loads(out_path.read_text())
    assert isinstance(payload, dict)
    assert "brinson" in payload
    assert "factor" in payload
    assert payload["brinson"]["allocation_total"] is not None
    assert payload["brinson"]["summary"]


def test_walk_forward_cli_attribution_html(tmp_path):
    price, bench, factors = _make_cli_files(tmp_path)
    out_path = tmp_path / "wf_attr.html"
    _run_cli(
        [
            "--walk-forward",
            "--strategy", "mean_reversion",
            "--asset", "BTC",
            "--data-source", "csv",
            "--data-csv", price,
            "--benchmark-weights-csv", bench,
            "--factor-returns-csv", factors,
            "--report", "attribution",
            "--output", "html",
            "--output-path", str(out_path),
            "--train-period", "40",
            "--test-period", "10",
        ]
    )
    content = out_path.read_text()
    assert "<!DOCTYPE html>" in content
    assert "Attribution" in content
    assert "Brinson" in content
    assert "Factor" in content


def test_walk_forward_cli_attribution_pdf(tmp_path):
    price, bench, factors = _make_cli_files(tmp_path)
    out_path = tmp_path / "wf_attr.pdf"
    _run_cli(
        [
            "--walk-forward",
            "--strategy", "mean_reversion",
            "--asset", "BTC",
            "--data-source", "csv",
            "--data-csv", price,
            "--benchmark-weights-csv", bench,
            "--factor-returns-csv", factors,
            "--report", "attribution",
            "--output", "pdf",
            "--output-path", str(out_path),
            "--train-period", "40",
            "--test-period", "10",
        ]
    )
    assert out_path.exists() and out_path.stat().st_size > 0
    assert out_path.read_bytes()[:4] == b"%PDF"


def test_walk_forward_cli_attribution_no_inputs_backward_compat(tmp_path):
    price, _, _ = _make_cli_files(tmp_path)
    out = _run_cli(
        [
            "--walk-forward",
            "--strategy", "mean_reversion",
            "--asset", "BTC",
            "--data-source", "csv",
            "--data-csv", price,
            "--report", "attribution",
            "--output", "text",
            "--train-period", "40",
            "--test-period", "10",
        ]
    )
    assert "No attribution results" in out
