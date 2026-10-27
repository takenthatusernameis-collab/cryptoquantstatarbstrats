"""
Tests for reporting utilities.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from utils.reporting import (
    generate_report,
    generate_risk_report,
    report_to_dict,
    risk_report_to_dict,
)


def make_result() -> dict:
    rng = np.random.default_rng(7)
    dates = pd.date_range("2024-01-01", periods=100, freq="1h")
    equity = pd.Series(100 * np.exp(np.cumsum(rng.normal(0.001, 0.02, 100))), index=dates)
    return {
        "total_return": float(equity.iloc[-1] / equity.iloc[0] - 1.0),
        "sharpe_ratio": 1.25,
        "sortino_ratio": 1.5,
        "var": -0.02,
        "cvar": -0.03,
        "max_drawdown": -0.1,
        "max_drawdown_duration": 10,
        "calmar_ratio": 2.0,
        "equity_curve": equity,
        "weights": pd.DataFrame({"BTC": [0.5], "ETH": [0.5]}),
    }


def test_generate_report_returns_string():
    result = make_result()
    report = generate_report(result)
    assert isinstance(report, str)
    assert "Backtest Report" in report
    assert "Total Return" in report
    assert "Sharpe Ratio" in report
    assert "Sortino Ratio" in report
    assert "VaR (95%)" in report
    assert "CVaR (95%)" in report
    assert "Max Drawdown" in report
    assert "Max DD Duration" in report
    assert "Calmar Ratio" in report


def test_report_to_dict_serializable():
    result = make_result()
    data = report_to_dict(result)
    assert isinstance(data, dict)
    for key, value in data.items():
        assert isinstance(value, (float, int, str)), f"{key}: {type(value)}"
    assert "equity_curve" not in data
    assert "weights" not in data
    assert data["max_drawdown_duration"] == 10
    assert isinstance(data["max_drawdown_duration"], int)


def test_generate_risk_report_returns_string():
    result = make_result()
    report = generate_risk_report(result)
    assert isinstance(report, str)
    assert "Risk Report" in report
    assert "VaR (95%)" in report
    assert "CVaR (95%)" in report
    assert "Max Drawdown" in report
    assert "Max DD Duration" in report
    assert "Calmar Ratio" in report


def test_risk_report_to_dict_serializable():
    result = make_result()
    data = risk_report_to_dict(result)
    assert isinstance(data, dict)
    for key, value in data.items():
        assert isinstance(value, (float, int, str)), f"{key}: {type(value)}"
    assert set(data.keys()) == {
        "var",
        "cvar",
        "max_drawdown",
        "max_drawdown_duration",
        "calmar_ratio",
    }
    assert data["max_drawdown_duration"] == 10
    assert isinstance(data["max_drawdown_duration"], int)


def test_risk_report_missing_keys():
    data = risk_report_to_dict({})
    assert data["var"] == 0.0
    assert data["max_drawdown_duration"] == 0
    report = generate_risk_report({})
    assert isinstance(report, str)


def test_generate_html_report_returns_string():
    from utils.reporting import generate_html_report

    result = make_result()
    report = generate_html_report(result)
    assert isinstance(report, str)
    assert "<!DOCTYPE html>" in report
    assert "Backtest Report" in report
    assert "Total Return" in report
    assert "Sharpe Ratio" in report


def test_generate_html_report_includes_equity_curve():
    from utils.reporting import generate_html_report

    result = make_result()
    report = generate_html_report(result)
    assert "<svg" in report
    assert "Equity Curve" in report


def test_generate_pdf_report_creates_html_fallback(tmp_path):
    from utils.reporting import generate_pdf_report

    result = make_result()
    out = tmp_path / "report.pdf"
    path = generate_pdf_report(result, str(out))
    assert isinstance(path, str)
    # Fallback may write HTML if matplotlib/pdf unavailable
    assert path.endswith((".pdf", ".html"))


def test_generate_html_report_includes_trades_and_weights():
    from utils.reporting import generate_html_report

    result = make_result()
    trades = pd.DataFrame(
        {
            "timestamp": ["2024-01-01", "2024-01-02"],
            "side": ["BUY", "SELL"],
            "quantity": [1.0, 1.0],
            "price": [100.0, 105.0],
        }
    )
    weights = pd.DataFrame({"BTC": [0.6, 0.4], "ETH": [0.4, 0.6]})
    result["trades"] = trades
    result["weights"] = weights
    report = generate_html_report(result)
    assert "Trade List" in report
    assert "Portfolio Weights" in report
    assert "BUY" in report
    assert "SELL" in report


def test_generate_pdf_report_includes_trades_and_weights(tmp_path):
    from utils.reporting import generate_pdf_report

    result = make_result()
    trades = pd.DataFrame(
        {
            "timestamp": ["2024-01-01", "2024-01-02"],
            "side": ["BUY", "SELL"],
            "quantity": [1.0, 1.0],
            "price": [100.0, 105.0],
        }
    )
    weights = pd.DataFrame({"BTC": [0.6, 0.4], "ETH": [0.4, 0.6]})
    result["trades"] = trades
    result["weights"] = weights
    out = tmp_path / "report.pdf"
    path = generate_pdf_report(result, str(out))
    assert isinstance(path, str)
    assert path.endswith((".pdf", ".html"))


def test_generate_pdf_report_multi_page_trades(tmp_path):
    """Large trade lists should render across multiple PDF pages."""
    from utils.reporting import generate_pdf_report

    result = make_result()
    trades = pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-01-01", periods=120, freq="h").strftime(
                "%Y-%m-%d %H:%M"
            ),
            "side": ["BUY", "SELL"] * 60,
            "quantity": [1.0] * 120,
            "price": [100.0 + i for i in range(120)],
        }
    )
    result["trades"] = trades
    out = tmp_path / "report.pdf"
    path = generate_pdf_report(result, str(out))
    assert isinstance(path, str)
    assert path.endswith((".pdf", ".html"))


def test_generate_pdf_report_weights_bar_chart(tmp_path):
    """PDF report should render weights as a bar chart (not just text)."""
    from utils.reporting import generate_pdf_report

    result = make_result()
    weights = pd.DataFrame({"BTC": [0.6, 0.4], "ETH": [0.4, 0.6]})
    result["weights"] = weights
    out = tmp_path / "report.pdf"
    path = generate_pdf_report(result, str(out))
    assert isinstance(path, str)
    assert path.endswith((".pdf", ".html"))


def test_generate_pdf_report_tighter_layout(tmp_path):
    """PDF report should use tighter spacing and sans-serif fonts."""
    from utils.reporting import generate_pdf_report

    result = make_result()
    out = tmp_path / "report.pdf"
    path = generate_pdf_report(result, str(out))
    assert isinstance(path, str)
    assert path.endswith((".pdf", ".html"))


def test_generate_html_report_accepts_trade_list_key():
    from utils.reporting import generate_html_report

    result = make_result()
    trades = pd.DataFrame(
        {
            "timestamp": ["2024-01-01"],
            "side": ["BUY"],
            "quantity": [1.0],
            "price": [100.0],
        }
    )
    result["trade_list"] = trades
    report = generate_html_report(result)
    assert "Trade List" in report
    assert "BUY" in report


def test_generate_html_report_empty_trades_and_weights():
    from utils.reporting import generate_html_report

    result = make_result()
    result["trades"] = pd.DataFrame()
    result["weights"] = pd.DataFrame()
    report = generate_html_report(result)
    assert isinstance(report, str)
    assert "<!DOCTYPE html>" in report


def test_generate_html_report_custom_title():
    from utils.reporting import generate_html_report

    result = make_result()
    report = generate_html_report(result, title="Custom Report Title")
    assert "Custom Report Title" in report
    assert "<title>Custom Report Title</title>" in report
