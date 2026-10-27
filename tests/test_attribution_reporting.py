"""Tests for attribution reporting through utils.reporting and the CLI."""

from __future__ import annotations

import contextlib
import io
import json

import numpy as np
import pandas as pd

from backtest.cli import main
from utils.reporting import (
    attribution_report_to_dict,
    generate_attribution_report,
    generate_html_report,
    generate_pdf_report,
)


def _make_result():
    dates = pd.date_range("2024-01-01", periods=10, freq="1h")
    summary = pd.DataFrame(
        [
            {"asset": "BTC", "allocation": 0.01, "selection": 0.02,
             "interaction": 0.005, "total": 0.035},
            {"asset": "ETH", "allocation": -0.005, "selection": 0.01,
             "interaction": -0.002, "total": 0.003},
        ]
    )
    brinson = {
        "allocation_total": pd.Series([0.005], index=dates[:1]),
        "selection_total": pd.Series([0.03], index=dates[:1]),
        "interaction_total": pd.Series([0.003], index=dates[:1]),
        "portfolio_return": pd.Series([0.05], index=dates[:1]),
        "benchmark_return": pd.Series([0.02], index=dates[:1]),
        "summary": summary,
    }
    factor = {
        "alpha": 0.001,
        "alpha_annualized": 0.252,
        "beta": pd.Series({"mkt": 0.8}),
        "r_squared": 0.6,
        "n_obs": 10,
    }
    return {"brinson": brinson, "factor": factor}


def test_text_report_renders_effects():
    result = _make_result()
    text = generate_attribution_report(result)
    assert "Allocation" in text or "allocation" in text.lower()
    assert "Selection" in text or "selection" in text.lower()
    assert "Interaction" in text or "interaction" in text.lower()
    assert "BTC" in text


def test_json_dict_serializable():
    result = _make_result()
    d = attribution_report_to_dict(result)
    json.dumps(d)
    assert "brinson" in d
    assert "factor" in d
    assert d["brinson"]["allocation_total"] is not None


def test_backward_compat_no_attribution():
    text = generate_attribution_report({})
    assert "No attribution results" in text
    d = attribution_report_to_dict({})
    assert d == {}


def test_html_includes_attribution_when_inputs_present():
    result = _make_result()
    html = generate_html_report(result)
    assert "Attribution" in html
    assert "Brinson" in html
    assert "Factor" in html


def test_pdf_includes_attribution_when_inputs_present(tmp_path):
    result = _make_result()
    out = tmp_path / "attr.pdf"
    generate_pdf_report(result, str(out))
    # File should be created (matplotlib may write PDF or fallback to HTML)
    assert out.exists() or (tmp_path / "attr.html").exists()


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


def _run_cli(argv: list[str]) -> str:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = main(argv)
    assert code == 0
    return buf.getvalue()


def test_cli_attribution_text_renders_effects(tmp_path):
    price, bench, factors = _make_cli_files(tmp_path)
    out = _run_cli(
        [
            "--strategy",
            "mean_reversion",
            "--asset",
            "BTC",
            "--data-source",
            "csv",
            "--data-csv",
            price,
            "--benchmark-weights-csv",
            bench,
            "--factor-returns-csv",
            factors,
            "--report",
            "attribution",
            "--output",
            "text",
        ]
    )
    assert "Brinson Attribution" in out
    assert "Allocation" in out or "allocation" in out.lower()
    assert "Selection" in out or "selection" in out.lower()
    assert "Interaction" in out or "interaction" in out.lower()
    assert "Factor Attribution" in out


def test_cli_attribution_json_serializable(tmp_path):
    price, bench, factors = _make_cli_files(tmp_path)
    out = _run_cli(
        [
            "--strategy",
            "mean_reversion",
            "--asset",
            "BTC",
            "--data-source",
            "csv",
            "--data-csv",
            price,
            "--benchmark-weights-csv",
            bench,
            "--factor-returns-csv",
            factors,
            "--report",
            "attribution",
            "--output",
            "json",
        ]
    )
    payload = json.loads(out)
    assert isinstance(payload, dict)
    assert "brinson" in payload
    assert "factor" in payload
    assert payload["brinson"]["allocation_total"] is not None
    assert payload["brinson"]["summary"]


def test_cli_attribution_html_includes_breakdown(tmp_path):
    price, bench, factors = _make_cli_files(tmp_path)
    out_path = tmp_path / "attr.html"
    argv = [
        "--strategy",
        "mean_reversion",
        "--asset",
        "BTC",
        "--data-source",
        "csv",
        "--data-csv",
        price,
        "--benchmark-weights-csv",
        bench,
        "--factor-returns-csv",
        factors,
        "--report",
        "attribution",
        "--output",
        "html",
        "--output-path",
        str(out_path),
    ]
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = main(argv)
    assert code == 0
    content = out_path.read_text()
    assert "<!DOCTYPE html>" in content
    assert "Attribution" in content
    assert "Brinson" in content
    assert "Factor" in content


def test_cli_attribution_pdf_written(tmp_path):
    price, bench, factors = _make_cli_files(tmp_path)
    out_path = tmp_path / "attr.pdf"
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = main(
            [
                "--strategy",
                "mean_reversion",
                "--asset",
                "BTC",
                "--data-source",
                "csv",
                "--data-csv",
                price,
                "--benchmark-weights-csv",
                bench,
                "--factor-returns-csv",
                factors,
                "--report",
                "attribution",
                "--output",
                "pdf",
                "--output-path",
                str(out_path),
            ]
        )
    assert code == 0
    assert out_path.exists() and out_path.stat().st_size > 0
    assert out_path.read_bytes()[:4] == b"%PDF"


def test_cli_attribution_no_inputs_backward_compat(tmp_path):
    price, _, _ = _make_cli_files(tmp_path)
    out = _run_cli(
        [
            "--strategy",
            "mean_reversion",
            "--asset",
            "BTC",
            "--data-source",
            "csv",
            "--data-csv",
            price,
            "--report",
            "attribution",
            "--output",
            "text",
        ]
    )
    assert "No attribution results" in out


def test_cli_attribution_full_includes_attribution(tmp_path):
    price, bench, factors = _make_cli_files(tmp_path)
    out = _run_cli(
        [
            "--strategy",
            "mean_reversion",
            "--asset",
            "BTC",
            "--data-source",
            "csv",
            "--data-csv",
            price,
            "--benchmark-weights-csv",
            bench,
            "--factor-returns-csv",
            factors,
            "--report",
            "full",
            "--output",
            "text",
        ]
    )
    assert "Backtest Report" in out
    assert "Attribution" in out
    assert "Brinson" in out
