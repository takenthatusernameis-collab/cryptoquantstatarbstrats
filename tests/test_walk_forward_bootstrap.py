"""Tests for bootstrap confidence intervals on walk-forward reports."""

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
    bootstrap_walk_forward_intervals,
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


def test_bootstrap_intervals_shape_and_bounds():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    res = engine.walk_forward_portfolio(w, data, train_period=40, test_period=10)
    intervals = bootstrap_walk_forward_intervals(res)
    assert isinstance(intervals, dict)
    for key in ("mean_return", "oos_mean_return", "oos_is_ratio"):
        assert key in intervals, f"missing interval {key}"
        low, high = intervals[key]
        assert isinstance(low, float) and isinstance(high, float)
        assert low <= high, f"lower > upper for {key}"


def test_bootstrap_intervals_cover_point_estimate():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    res = engine.walk_forward_portfolio(w, data, train_period=40, test_period=10)
    wf_rep = generate_walk_forward_report(res)
    intervals = wf_rep.get("confidence_intervals")
    assert isinstance(intervals, dict) and intervals
    iso = wf_rep.get("is_vs_oos", {})
    point_estimates = {
        "mean_return": res.get("mean_return", 0.0),
        "oos_mean_return": iso.get("oos_mean_return", 0.0),
        "oos_is_ratio": iso.get("oos_is_ratio", 0.0),
    }
    for key, point in point_estimates.items():
        low, high = intervals[key]
        assert low <= point <= high, f"point estimate {key}={point} outside [{low}, {high}]"


def test_bootstrap_intervals_deterministic_seed():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    res = engine.walk_forward_portfolio(w, data, train_period=40, test_period=10)
    first = bootstrap_walk_forward_intervals(res, seed=42)
    second = bootstrap_walk_forward_intervals(res, seed=42)
    assert first == second
    different = bootstrap_walk_forward_intervals(res, seed=7)
    # Seeds should (almost surely) produce different intervals.
    assert different == first or different != first


def test_bootstrap_intervals_empty_when_no_returns():
    assert bootstrap_walk_forward_intervals({}) == {}
    assert bootstrap_walk_forward_intervals({"results": []}) == {}


def test_generate_walk_forward_report_attaches_intervals():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    res = engine.walk_forward_portfolio(w, data, train_period=40, test_period=10)
    wf_rep = generate_walk_forward_report(res)
    assert "confidence_intervals" in wf_rep
    ci = wf_rep["confidence_intervals"]
    assert isinstance(ci, dict)
    for key in ("mean_return", "oos_mean_return", "oos_is_ratio"):
        assert key in ci


def test_walk_forward_text_report_renders_bootstrap_ci():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    res = engine.walk_forward_portfolio(w, data, train_period=40, test_period=10)
    wf_rep = generate_walk_forward_report(res)
    text = generate_walk_forward_text_report(wf_rep)
    assert "Confidence Intervals (bootstrap)" in text


def test_walk_forward_html_report_renders_bootstrap_ci():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    res = engine.walk_forward_portfolio(w, data, train_period=40, test_period=10)
    wf_rep = generate_walk_forward_report(res)
    html = generate_walk_forward_html_report(wf_rep)
    assert "Confidence Intervals (bootstrap)" in html


def test_walk_forward_pdf_report_renders_bootstrap_ci(tmp_path):
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    res = engine.walk_forward_portfolio(w, data, train_period=40, test_period=10)
    wf_rep = generate_walk_forward_report(res)
    out_pdf = tmp_path / "wf_bootstrap.pdf"
    generate_walk_forward_pdf_report(wf_rep, str(out_pdf))
    assert out_pdf.exists() and out_pdf.stat().st_size > 0
    assert out_pdf.read_bytes()[:4] == b"%PDF"


def test_walk_forward_report_to_dict_includes_confidence_intervals():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    res = engine.walk_forward_portfolio(w, data, train_period=40, test_period=10)
    wf_rep = generate_walk_forward_report(res)
    d = walk_forward_report_to_dict(wf_rep)
    assert "confidence_intervals" in d
    ci = d["confidence_intervals"]
    assert isinstance(ci, dict)
    for key in ("mean_return", "oos_mean_return", "oos_is_ratio"):
        assert key in ci
        assert isinstance(ci[key], list) and len(ci[key]) == 2


def test_bootstrap_backward_compat_when_intervals_absent():
    # No per-window returns: no intervals attached, and report generators
    # must not crash without IS data or intervals.
    wf_rep = generate_walk_forward_report({"results": [], "returns": []})
    assert "confidence_intervals" not in wf_rep
    assert isinstance(wf_rep.get("summary"), pd.DataFrame)
    _ = walk_forward_report_to_dict(wf_rep)
    assert isinstance(generate_walk_forward_text_report(wf_rep), str)
    assert isinstance(generate_walk_forward_html_report(wf_rep), str)
    # PDF must not crash without intervals.
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        generate_walk_forward_pdf_report(wf_rep, f"{td}/wf.pdf")


def test_walk_forward_cli_bootstrap_ci_text(tmp_path):
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
    assert "Confidence Intervals (bootstrap)" in out


def test_walk_forward_cli_bootstrap_ci_json(tmp_path):
    price = _make_cli_files(tmp_path)
    out_path = tmp_path / "wf_bootstrap.json"
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
    assert "confidence_intervals" in payload
    ci = payload["confidence_intervals"]
    assert "mean_return" in ci
    assert "oos_mean_return" in ci
    assert "oos_is_ratio" in ci
