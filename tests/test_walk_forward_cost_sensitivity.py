"""Tests for cost-model sensitivity sweeps on walk-forward reports."""

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
    sweep_cost_sensitivity,
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


def _walk_forward_fn(engine, data, weights, train_period, test_period):
    def fn(fee_rate: float, slippage: float) -> dict:
        return engine.walk_forward_portfolio(
            weights,
            data,
            train_period=train_period,
            test_period=test_period,
            fee_rate=fee_rate,
            slippage=slippage,
        )

    return fn


def test_sweep_cost_sensitivity_runs_across_grid():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    fn = _walk_forward_fn(engine, data, w, train_period=40, test_period=10)
    cost_grid = [(0.0, 0.0), (0.001, 0.0), (0.0, 0.001), (0.001, 0.001)]
    sweep = sweep_cost_sensitivity(fn, cost_grid)
    assert len(sweep) == len(cost_grid)


def test_sweep_cost_sensitivity_row_keys_and_shape():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    fn = _walk_forward_fn(engine, data, w, train_period=40, test_period=10)
    cost_grid = [(0.0, 0.0), (0.002, 0.001)]
    sweep = sweep_cost_sensitivity(fn, cost_grid)
    assert len(sweep) == 2
    for row, (fee, slip) in zip(sweep, cost_grid):
        assert set(row.keys()) >= {
            "fee_rate",
            "slippage",
            "mean_return",
            "oos_mean_return",
            "oos_is_ratio",
            "max_drawdown",
        }
        assert row["fee_rate"] == fee
        assert row["slippage"] == slip
        assert isinstance(row["mean_return"], float)
        assert isinstance(row["oos_mean_return"], float)
        assert isinstance(row["oos_is_ratio"], float)
        assert isinstance(row["max_drawdown"], float)


def test_sweep_cost_sensitivity_higher_costs_reduce_oos_return():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    fn = _walk_forward_fn(engine, data, w, train_period=40, test_period=10)
    cost_grid = [(0.0, 0.0), (0.005, 0.005)]
    sweep = sweep_cost_sensitivity(fn, cost_grid)
    free = sweep[0]
    costly = sweep[-1]
    # Higher transaction costs should not improve the OOS mean return.
    assert costly["oos_mean_return"] <= free["oos_mean_return"] + 1e-9


def test_sweep_cost_sensitivity_identifies_best_worst():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    fn = _walk_forward_fn(engine, data, w, train_period=40, test_period=10)
    cost_grid = [(0.0, 0.0), (0.001, 0.0), (0.0, 0.001), (0.001, 0.001)]
    sweep = sweep_cost_sensitivity(fn, cost_grid)
    valid = [r for r in sweep if isinstance(r, dict)]
    best = max(valid, key=lambda r: r.get("oos_mean_return", 0.0))
    worst = min(valid, key=lambda r: r.get("oos_mean_return", 0.0))
    assert best["oos_mean_return"] >= worst["oos_mean_return"]
    # The zero-cost config should be the best (or tied for best).
    assert best == sweep[0] or best["oos_mean_return"] == sweep[0]["oos_mean_return"]


def test_generate_walk_forward_report_attaches_cost_sensitivity():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    res = engine.walk_forward_portfolio(w, data, train_period=40, test_period=10)
    fn = _walk_forward_fn(engine, data, w, train_period=40, test_period=10)
    cost_grid = [(0.0, 0.0), (0.001, 0.001)]
    sweep = sweep_cost_sensitivity(fn, cost_grid)
    res["cost_sensitivity"] = sweep
    wf_rep = generate_walk_forward_report(res)
    assert "cost_sensitivity" in wf_rep
    cs = wf_rep["cost_sensitivity"]
    assert isinstance(cs, list) and len(cs) == 2
    for row in cs:
        assert "fee_rate" in row
        assert "slippage" in row
        assert "oos_mean_return" in row
        assert "result" not in row  # internal result stripped for serialization


def test_walk_forward_text_report_renders_cost_sensitivity():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    res = engine.walk_forward_portfolio(w, data, train_period=40, test_period=10)
    fn = _walk_forward_fn(engine, data, w, train_period=40, test_period=10)
    sweep = sweep_cost_sensitivity(fn, [(0.0, 0.0), (0.001, 0.001)])
    res["cost_sensitivity"] = sweep
    wf_rep = generate_walk_forward_report(res)
    text = generate_walk_forward_text_report(wf_rep)
    assert "Walk-Forward Report" in text
    assert "Cost-Model Sensitivity" in text
    assert "Fee Rate" not in text  # text uses raw column names
    assert "Best OOS return" in text
    assert "Worst OOS return" in text


def test_walk_forward_html_report_renders_cost_sensitivity():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    res = engine.walk_forward_portfolio(w, data, train_period=40, test_period=10)
    fn = _walk_forward_fn(engine, data, w, train_period=40, test_period=10)
    sweep = sweep_cost_sensitivity(fn, [(0.0, 0.0), (0.001, 0.001)])
    res["cost_sensitivity"] = sweep
    wf_rep = generate_walk_forward_report(res)
    html = generate_walk_forward_html_report(wf_rep)
    assert "Cost-Model Sensitivity" in html
    assert "Fee Rate" in html
    assert "Best OOS return" in html
    assert "Worst OOS return" in html


def test_walk_forward_pdf_report_renders_cost_sensitivity(tmp_path):
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    res = engine.walk_forward_portfolio(w, data, train_period=40, test_period=10)
    fn = _walk_forward_fn(engine, data, w, train_period=40, test_period=10)
    sweep = sweep_cost_sensitivity(fn, [(0.0, 0.0), (0.001, 0.001)])
    res["cost_sensitivity"] = sweep
    wf_rep = generate_walk_forward_report(res)
    out_pdf = tmp_path / "wf_cost_sensitivity.pdf"
    generate_walk_forward_pdf_report(wf_rep, str(out_pdf))
    assert out_pdf.exists() and out_pdf.stat().st_size > 0
    assert out_pdf.read_bytes()[:4] == b"%PDF"


def test_walk_forward_report_to_dict_includes_cost_sensitivity():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    res = engine.walk_forward_portfolio(w, data, train_period=40, test_period=10)
    fn = _walk_forward_fn(engine, data, w, train_period=40, test_period=10)
    sweep = sweep_cost_sensitivity(fn, [(0.0, 0.0), (0.001, 0.001)])
    res["cost_sensitivity"] = sweep
    wf_rep = generate_walk_forward_report(res)
    d = walk_forward_report_to_dict(wf_rep)
    assert "cost_sensitivity" in d
    cs = d["cost_sensitivity"]
    assert isinstance(cs, list) and len(cs) == 2
    for row in cs:
        assert "result" not in row
        assert isinstance(row["fee_rate"], float)
        assert isinstance(row["slippage"], float)


def test_cost_sensitivity_backward_compat_when_absent():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    res = engine.walk_forward_portfolio(w, data, train_period=40, test_period=10)
    wf_rep = generate_walk_forward_report(res)
    assert "cost_sensitivity" not in wf_rep
    # Report generators must not crash without cost-sensitivity data.
    _ = walk_forward_report_to_dict(wf_rep)
    assert isinstance(generate_walk_forward_text_report(wf_rep), str)
    assert isinstance(generate_walk_forward_html_report(wf_rep), str)
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        generate_walk_forward_pdf_report(wf_rep, f"{td}/wf.pdf")


def test_sweep_cost_sensitivity_backward_compat_empty_grid():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    fn = _walk_forward_fn(engine, data, w, train_period=40, test_period=10)
    sweep = sweep_cost_sensitivity(fn, [])
    assert sweep == []


def test_sweep_cost_sensitivity_skips_failing_configs():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)

    def fn(fee_rate: float, slippage: float) -> dict:
        if fee_rate > 0:
            raise RuntimeError("simulated failure")
        return engine.walk_forward_portfolio(
            w, data, train_period=40, test_period=10,
            fee_rate=fee_rate, slippage=slippage,
        )

    sweep = sweep_cost_sensitivity(fn, [(0.0, 0.0), (0.001, 0.0), (0.002, 0.0)])
    assert len(sweep) == 1
    assert sweep[0]["fee_rate"] == 0.0


def test_walk_forward_cli_cost_sensitivity_text(tmp_path):
    # The CLI walks forward with a single cost config; cost sensitivity is an
    # opt-in sweep attached to the report. Verify the CLI still renders a
    # walk-forward report (backward compatible) and does not crash.
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
    assert "Walk-Forward Report" in out


def test_walk_forward_cli_cost_sensitivity_json(tmp_path):
    price = _make_cli_files(tmp_path)
    out_path = tmp_path / "wf_cost.json"
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
