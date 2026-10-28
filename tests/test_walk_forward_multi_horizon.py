"""Tests for multi-horizon walk-forward (expanding vs rolling) reports."""

from __future__ import annotations

import contextlib
import io

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
    return str(price_path)


def test_expanding_vs_rolling_run_correctly():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    res_roll = engine.walk_forward_portfolio(
        w, data, train_period=40, test_period=10, mode="rolling"
    )
    res_exp = engine.walk_forward_portfolio(
        w, data, train_period=40, test_period=10, mode="expanding"
    )
    assert isinstance(res_roll, dict)
    assert isinstance(res_exp, dict)
    assert "results" in res_roll
    assert "results" in res_exp


def test_multi_horizon_return_correct_shape():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    res_roll = engine.walk_forward_portfolio(
        w, data, train_period=40, test_period=10, mode="rolling"
    )
    res_exp = engine.walk_forward_portfolio(
        w, data, train_period=40, test_period=10, mode="expanding"
    )
    wf_rep = generate_walk_forward_report(
        res_roll, multi_horizon={"rolling": res_roll, "expanding": res_exp}
    )
    assert "multi_horizon" in wf_rep
    mh = wf_rep["multi_horizon"]
    assert isinstance(mh, list)
    assert len(mh) == 2
    for row in mh:
        assert "mode" in row
        assert "mean_return" in row
        assert "oos_mean_return" in row
        assert "oos_is_ratio" in row
        assert "max_drawdown" in row


def test_multi_horizon_text_html_pdf_rendering(tmp_path):
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    res_roll = engine.walk_forward_portfolio(
        w, data, train_period=40, test_period=10, mode="rolling"
    )
    res_exp = engine.walk_forward_portfolio(
        w, data, train_period=40, test_period=10, mode="expanding"
    )
    wf_rep = generate_walk_forward_report(
        res_roll, multi_horizon={"rolling": res_roll, "expanding": res_exp}
    )
    text = generate_walk_forward_text_report(wf_rep)
    assert "Multi-Horizon Walk-Forward" in text
    html = generate_walk_forward_html_report(wf_rep)
    assert "Multi-Horizon Walk-Forward" in html
    out_pdf = tmp_path / "wf_mh.pdf"
    generate_walk_forward_pdf_report(wf_rep, str(out_pdf))
    assert out_pdf.exists() and out_pdf.stat().st_size > 0


def test_multi_horizon_backward_compat_when_absent():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    res = engine.walk_forward_portfolio(w, data, train_period=40, test_period=10)
    wf_rep = generate_walk_forward_report(res)
    assert "multi_horizon" not in wf_rep
    _ = walk_forward_report_to_dict(wf_rep)
    assert isinstance(generate_walk_forward_text_report(wf_rep), str)
    assert isinstance(generate_walk_forward_html_report(wf_rep), str)
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        generate_walk_forward_pdf_report(wf_rep, f"{td}/wf.pdf")


def test_multi_horizon_via_wf_result_key():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    res_roll = engine.walk_forward_portfolio(
        w, data, train_period=40, test_period=10, mode="rolling"
    )
    res_exp = engine.walk_forward_portfolio(
        w, data, train_period=40, test_period=10, mode="expanding"
    )
    res_roll["multi_horizon"] = {"rolling": res_roll, "expanding": res_exp}
    wf_rep = generate_walk_forward_report(res_roll)
    assert "multi_horizon" in wf_rep
    d = walk_forward_report_to_dict(wf_rep)
    assert "multi_horizon" in d
