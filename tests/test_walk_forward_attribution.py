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
    walk_forward_report_to_dict,
)


def _make_data():
    loader = DataLoader()
    data = loader.load_data(["BTC", "ETH"], "2024-01-01", "2024-04-01", freq="1d")
    return loader.clean_data(data)


def test_walk_forward_aggregates_attribution_across_windows():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    # create benchmark weights aligned
    bench = pd.DataFrame({"BTC": 0.6, "ETH": 0.4}, index=data.index)
    # create factor returns
    rng = np.random.default_rng(123)
    factors = pd.DataFrame({"mkt": rng.normal(0, 0.01, len(data))}, index=data.index)
    res = engine.walk_forward_portfolio(w, data, train_period=40, test_period=10, benchmark_weights=bench, factor_returns=factors)
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
    res = engine.walk_forward_portfolio(w, data, train_period=40, test_period=10, benchmark_weights=bench, factor_returns=factors)
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
