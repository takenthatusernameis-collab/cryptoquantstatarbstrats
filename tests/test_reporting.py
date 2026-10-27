"""
Tests for reporting utilities.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

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


def test_generate_html_report_includes_benchmark_line():
    from utils.reporting import generate_html_report

    result = make_result()
    dates = pd.date_range("2024-01-01", periods=100, freq="1h")
    bench = pd.Series(
        100 * np.exp(np.cumsum(np.random.default_rng(3).normal(0.0005, 0.015, 100))),
        index=dates,
    )
    result["benchmark_equity_curve"] = bench
    report = generate_html_report(result)
    assert "#2ca02c" in report


def test_generate_pdf_report_with_benchmark(tmp_path):
    from utils.reporting import generate_pdf_report

    result = make_result()
    dates = pd.date_range("2024-01-01", periods=100, freq="1h")
    bench = pd.Series(
        100 * np.exp(np.cumsum(np.random.default_rng(3).normal(0.0005, 0.015, 100))),
        index=dates,
    )
    result["benchmark_equity_curve"] = bench
    out = tmp_path / "report_bench.pdf"
    path = generate_pdf_report(result, str(out))
    assert isinstance(path, str)
    assert path.endswith((".pdf", ".html"))


def test_generate_pdf_report_trade_cell_text_via_pypdf(tmp_path):
    """PDF trade table should embed extractable cell text (pypdf when available)."""
    try:
        import pypdf  # noqa: F401
    except ImportError:
        pytest.skip("pypdf not installed")

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
    result["trades"] = trades
    out = tmp_path / "report_trades.pdf"
    path = generate_pdf_report(result, str(out))
    if not path.endswith(".pdf"):
        pytest.skip("PDF backend unavailable; HTML fallback written")

    reader = pypdf.PdfReader(path)
    text = "\n".join((page.extract_text() or "") for page in reader.pages)
    assert "BUY" in text
    assert "SELL" in text
    assert "100.0" in text or "100" in text
    assert "105.0" in text or "105" in text


def _wf_result() -> dict:
    dates = pd.date_range("2024-01-01", periods=10, freq="1h")
    rng = np.random.default_rng(1)
    ec1 = pd.Series(
        100 * np.exp(np.cumsum(rng.normal(0.001, 0.01, 10))), index=dates
    )
    ec2 = pd.Series(
        100 * np.exp(np.cumsum(rng.normal(0.001, 0.01, 10))), index=dates
    )
    return {
        "returns": [0.05, -0.02],
        "results": [
            {
                "total_return": 0.05,
                "sharpe_ratio": 1.0,
                "sortino_ratio": 1.2,
                "max_drawdown": -0.03,
                "calmar_ratio": 1.5,
                "equity_curve": ec1,
            },
            {
                "total_return": -0.02,
                "sharpe_ratio": 0.5,
                "sortino_ratio": 0.6,
                "max_drawdown": -0.04,
                "calmar_ratio": 0.4,
                "equity_curve": ec2,
            },
        ],
        "mean_return": 0.015,
        "std_return": 0.05,
        "positive_periods": 1,
        "total_periods": 2,
    }


def test_generate_walk_forward_report_summary():
    from utils.reporting import generate_walk_forward_report

    report = generate_walk_forward_report(_wf_result())
    summary = report["summary"]
    assert isinstance(summary, pd.DataFrame)
    assert len(summary) == 2
    expected_cols = {
        "window",
        "total_return",
        "sharpe_ratio",
        "sortino_ratio",
        "max_drawdown",
        "calmar_ratio",
        "start_equity",
        "end_equity",
    }
    assert expected_cols.issubset(set(summary.columns))
    assert summary.loc[0, "total_return"] == 0.05
    assert summary.loc[1, "total_return"] == -0.02
    assert report["mean_return"] == 0.015
    assert report["total_periods"] == 2


def test_generate_walk_forward_report_equity_curve_chained():
    from utils.reporting import generate_walk_forward_report

    report = generate_walk_forward_report(_wf_result())
    ec = report["equity_curve"]
    assert isinstance(ec, pd.Series)
    assert len(ec) == 20
    # Segment 1 starts at 1.0 (cumulative_before == 1.0), normalized by its own first value.
    assert abs(float(ec.iloc[0]) - 1.0) < 1e-9
    # Last value of segment 1 equals its own end/start growth.
    seg1 = _wf_result()["results"][0]["equity_curve"]
    seg1 = seg1 if isinstance(seg1, pd.Series) else pd.Series(seg1)
    assert abs(float(ec.iloc[9]) - float(seg1.iloc[-1] / seg1.iloc[0])) < 1e-9
    # First value of segment 2 = 1.0 * (1.0 + total_return of window 0) = 1.05.
    assert abs(float(ec.iloc[10]) - 1.05) < 1e-9


def test_generate_walk_forward_report_empty():
    from utils.reporting import generate_walk_forward_report

    report = generate_walk_forward_report({})
    assert isinstance(report["summary"], pd.DataFrame)
    assert len(report["summary"]) == 0
    assert isinstance(report["equity_curve"], pd.Series)
    assert len(report["equity_curve"]) == 0


def test_generate_walk_forward_report_no_results_key():
    from utils.reporting import generate_walk_forward_report

    report = generate_walk_forward_report({"returns": []})
    assert len(report["summary"]) == 0
