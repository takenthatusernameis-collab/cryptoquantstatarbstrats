"""Tests for walk-forward report comparison dashboard."""

from __future__ import annotations

import contextlib
import io
import json

import pandas as pd

from backtest.cli import main
from backtest.engine import BacktestEngine
from data.loader import DataLoader
from utils.reporting import (
    compare_walk_forward_reports,
    generate_walk_forward_comparison_html,
    generate_walk_forward_report,
    walk_forward_report_to_dict,
)


def _make_data():
    loader = DataLoader()
    data = loader.load_data(["BTC", "ETH"], "2024-01-01", "2024-04-01", freq="1d")
    return loader.clean_data(data)


def _run_walk_forward():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    res = engine.walk_forward_portfolio(w, data, train_period=40, test_period=10)
    return res


def test_compare_walk_forward_reports_aggregation():
    res = _run_walk_forward()
    wf_rep1 = generate_walk_forward_report(res)
    wf_rep2 = generate_walk_forward_report(
        res, benchmarks=[{"name": "BM1", "mean_return": 0.02, "max_drawdown": 0.05}]
    )
    comparison = compare_walk_forward_reports([wf_rep1, wf_rep2])
    assert isinstance(comparison, dict)
    assert "reports" in comparison
    assert len(comparison["reports"]) == 2
    r0 = comparison["reports"][0]
    assert "oos_mean_return" in r0 or "mean_return" in r0
    assert "total_windows" in r0


def test_compare_walk_forward_reports_html_rendering():
    res = _run_walk_forward()
    wf_rep1 = generate_walk_forward_report(res)
    wf_rep2 = generate_walk_forward_report(res)
    comparison = compare_walk_forward_reports([wf_rep1, wf_rep2])
    html = generate_walk_forward_comparison_html(comparison)
    assert isinstance(html, str)
    assert "html" in html.lower() or "<table" in html


def test_compare_walk_forward_reports_missing_fields_backward_compat():
    comparison = compare_walk_forward_reports([{}, {"name": "x"}])
    assert isinstance(comparison, dict)
    assert "reports" in comparison
    assert len(comparison["reports"]) == 2


def test_compare_walk_forward_reports_with_benchmarks_deltas():
    res = _run_walk_forward()
    wf_rep = generate_walk_forward_report(
        res, benchmarks=[{"name": "BuyAndHold", "mean_return": 0.04, "max_drawdown": 0.10}]
    )
    comparison = compare_walk_forward_reports([wf_rep])
    assert isinstance(comparison, dict)
    assert "benchmarks" in comparison


def _run_cli(argv: list[str]) -> str:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = main(argv)
    assert code == 0
    return buf.getvalue()


def test_walk_forward_cli_compare_integration(tmp_path):
    res = _run_walk_forward()
    wf_rep1 = generate_walk_forward_report(res)
    wf_rep2 = generate_walk_forward_report(res)
    p1 = tmp_path / "wf1.json"
    p2 = tmp_path / "wf2.json"
    p1.write_text(json.dumps(walk_forward_report_to_dict(wf_rep1), default=float))
    p2.write_text(json.dumps(walk_forward_report_to_dict(wf_rep2), default=float))
    out_path = tmp_path / "compare.html"
    _run_cli(
        [
            "--wf-compare",
            "--report-path",
            str(p1),
            "--report-path",
            str(p2),
            "--output-path",
            str(out_path),
        ]
    )
    assert out_path.exists()
    content = out_path.read_text()
    assert "html" in content.lower() or "<table" in content
    assert "Report" in content
