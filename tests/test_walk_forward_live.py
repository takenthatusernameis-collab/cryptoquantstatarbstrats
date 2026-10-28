"""Tests for live/paper trading result attachment to walk-forward reports."""

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
    load_live_results_csv,
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


def _make_live_csv(tmp_path, schemes):
    path = tmp_path / "live_results.csv"
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "scheme",
                "live_mean_return",
                "live_max_drawdown",
                "live_total_return",
                "live_sharpe_ratio",
            ],
        )
        writer.writeheader()
        for scheme in schemes:
            writer.writerow(scheme)
    return str(path)


def _run_walk_forward():
    data = _make_data()
    engine = BacktestEngine(initial_capital=100000)
    w = pd.DataFrame(0.5, index=data.index, columns=data.columns)
    res = engine.walk_forward_portfolio(w, data, train_period=40, test_period=10)
    return res


def test_load_live_results_csv(tmp_path):
    schemes = [
        {
            "scheme": "BTC/ETH",
            "live_mean_return": "0.04",
            "live_max_drawdown": "0.10",
            "live_total_return": "0.12",
            "live_sharpe_ratio": "1.2",
        },
        {
            "scheme": "ETH/SOL",
            "live_mean_return": "0.03",
            "live_max_drawdown": "0.08",
        },
    ]
    path = _make_live_csv(tmp_path, schemes)
    loaded = load_live_results_csv(path)
    assert len(loaded) == 2
    assert loaded[0]["scheme"] == "BTC/ETH"
    assert loaded[0]["live_mean_return"] == 0.04
    assert loaded[0]["live_max_drawdown"] == 0.10
    assert loaded[0]["live_total_return"] == 0.12
    assert loaded[0]["live_sharpe_ratio"] == 1.2
    assert loaded[1]["scheme"] == "ETH/SOL"
    assert loaded[1]["live_total_return"] == 0.0
    assert loaded[1]["live_sharpe_ratio"] == 0.0


def test_generate_walk_forward_report_attaches_live_trading():
    res = _run_walk_forward()
    live_results = [
        {"scheme": "BTC/ETH", "live_mean_return": 0.04, "live_max_drawdown": 0.10},
        {"scheme": "ETH/SOL", "live_mean_return": 0.03, "live_max_drawdown": 0.08},
    ]
    wf_rep = generate_walk_forward_report(res, live_results=live_results)
    assert "live_trading" in wf_rep
    lt = wf_rep["live_trading"]
    assert isinstance(lt, dict)
    assert lt["scheme_count"] == 2
    assert len(lt["schemes"]) == 2
    for row in lt["schemes"]:
        assert "scheme" in row
        assert "oos_mean_return" in row
        assert "live_mean_return" in row
        assert "oos_max_drawdown" in row
        assert "live_max_drawdown" in row
    assert lt["schemes"][0]["scheme"] == "BTC/ETH"
    assert lt["schemes"][0]["live_mean_return"] == 0.04
    assert lt["schemes"][0]["oos_mean_return"] == lt["schemes"][1]["oos_mean_return"]


def test_live_trading_uses_wf_result_key():
    res = _run_walk_forward()
    live_results = {
        "schemes": [{"scheme": "X", "live_mean_return": 0.05, "live_max_drawdown": 0.05}]
    }
    wf_rep = generate_walk_forward_report(res, live_results=live_results)
    assert "live_trading" in wf_rep
    assert wf_rep["live_trading"]["scheme_count"] == 1


def test_walk_forward_text_report_renders_live_vs_wf():
    res = _run_walk_forward()
    live_results = [
        {"scheme": "BTC/ETH", "live_mean_return": 0.04, "live_max_drawdown": 0.10},
    ]
    wf_rep = generate_walk_forward_report(res, live_results=live_results)
    text = generate_walk_forward_text_report(wf_rep)
    assert "Live vs Walk-Forward" in text
    assert "BTC/ETH" in text
    assert "OOS Mean Return" in text or "oos_mean_return" in text


def test_walk_forward_html_report_renders_live_vs_wf():
    res = _run_walk_forward()
    live_results = [
        {"scheme": "BTC/ETH", "live_mean_return": 0.04, "live_max_drawdown": 0.10},
    ]
    wf_rep = generate_walk_forward_report(res, live_results=live_results)
    html = generate_walk_forward_html_report(wf_rep)
    assert "Live vs Walk-Forward" in html
    assert "BTC/ETH" in html


def test_walk_forward_pdf_report_renders_live_vs_wf(tmp_path):
    res = _run_walk_forward()
    live_results = [
        {"scheme": "BTC/ETH", "live_mean_return": 0.04, "live_max_drawdown": 0.10},
    ]
    wf_rep = generate_walk_forward_report(res, live_results=live_results)
    out_pdf = tmp_path / "wf_live.pdf"
    generate_walk_forward_pdf_report(wf_rep, str(out_pdf))
    assert out_pdf.exists() and out_pdf.stat().st_size > 0
    assert out_pdf.read_bytes()[:4] == b"%PDF"


def test_walk_forward_report_to_dict_includes_live_trading():
    res = _run_walk_forward()
    live_results = [
        {"scheme": "BTC/ETH", "live_mean_return": 0.04, "live_max_drawdown": 0.10},
    ]
    wf_rep = generate_walk_forward_report(res, live_results=live_results)
    d = walk_forward_report_to_dict(wf_rep)
    assert "live_trading" in d
    lt = d["live_trading"]
    assert isinstance(lt, dict)
    assert "schemes" in lt
    assert lt["scheme_count"] == 1
    assert lt["schemes"][0]["scheme"] == "BTC/ETH"
    assert lt["schemes"][0]["live_mean_return"] == 0.04
    assert isinstance(lt["oos_mean_return"], float)
    assert isinstance(lt["live_mean_return"], float)


def test_live_trading_backward_compat_when_absent():
    res = _run_walk_forward()
    wf_rep = generate_walk_forward_report(res)
    assert "live_trading" not in wf_rep
    assert isinstance(wf_rep.get("summary"), pd.DataFrame)
    _ = walk_forward_report_to_dict(wf_rep)
    assert isinstance(generate_walk_forward_text_report(wf_rep), str)
    assert isinstance(generate_walk_forward_html_report(wf_rep), str)
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        generate_walk_forward_pdf_report(wf_rep, f"{td}/wf_live.pdf")


def test_walk_forward_cli_live_trading_text(tmp_path):
    price = _make_cli_files(tmp_path)
    live = _make_live_csv(
        tmp_path,
        [
            {
                "scheme": "BTC/ETH",
                "live_mean_return": "0.04",
                "live_max_drawdown": "0.10",
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
            "--live-results-csv", live,
            "--output", "text",
            "--train-period", "40",
            "--test-period", "10",
        ]
    )
    assert "Live vs Walk-Forward" in out
    assert "BTC/ETH" in out


def test_walk_forward_cli_live_trading_json(tmp_path):
    price = _make_cli_files(tmp_path)
    live = _make_live_csv(
        tmp_path,
        [
            {
                "scheme": "BTC/ETH",
                "live_mean_return": "0.04",
                "live_max_drawdown": "0.10",
            }
        ],
    )
    out_path = tmp_path / "wf_live.json"
    _run_cli(
        [
            "--walk-forward",
            "--strategy", "mean_reversion",
            "--asset", "BTC",
            "--data-source", "csv",
            "--data-csv", price,
            "--live-results-csv", live,
            "--report", "attribution",
            "--output", "json",
            "--output-path", str(out_path),
            "--train-period", "40",
            "--test-period", "10",
        ]
    )
    payload = json.loads(out_path.read_text())
    assert isinstance(payload, dict)
    assert "live_trading" in payload
    lt = payload["live_trading"]
    assert lt["scheme_count"] == 1
    assert lt["schemes"][0]["scheme"] == "BTC/ETH"
    assert lt["schemes"][0]["live_mean_return"] == 0.04
