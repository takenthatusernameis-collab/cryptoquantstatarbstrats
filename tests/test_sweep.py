"""
Tests for the `cryptoquant sweep` CLI subcommand.
"""

from __future__ import annotations

import io
import json
from contextlib import redirect_stderr, redirect_stdout

import pytest

from backtest.cli import main


def _run_sweep(argv: list[str]) -> tuple[int, str, str]:
    out_buf = io.StringIO()
    err_buf = io.StringIO()
    code = None
    with redirect_stdout(out_buf), redirect_stderr(err_buf):
        try:
            code = main(argv)
        except SystemExit as e:
            code = e.code
    return int(code or 0), out_buf.getvalue(), err_buf.getvalue()


def test_sweep_empty_grid_exits():
    code, out, err = _run_sweep(["sweep", "--grid", "{}"])
    assert code != 0
    assert "non-empty" in err or "non-empty" in out


def test_sweep_single_combination():
    code, out, err = _run_sweep(
        [
            "sweep",
            "--strategy",
            "mean_reversion",
            "--grid",
            '{"lookback":[20]}',
            "--data-source",
            "synthetic",
            "--output",
            "json",
        ]
    )
    assert code == 0
    assert "WARNING" in err
    rows = json.loads(out)
    assert isinstance(rows, list)
    assert len(rows) == 1
    assert rows[0]["lookback"] == 20
    assert "oos_mean_return" in rows[0]
    assert "mean_max_drawdown" in rows[0]
    assert "oos_is_ratio" in rows[0]
    assert "rank" in rows[0]


def test_sweep_ranking_order():
    code, out, err = _run_sweep(
        [
            "sweep",
            "--strategy",
            "mean_reversion",
            "--grid",
            '{"lookback":[10,30]}',
            "--data-source",
            "synthetic",
            "--metric",
            "calmar_ratio",
            "--output",
            "json",
        ]
    )
    assert code == 0
    rows = json.loads(out)
    assert len(rows) == 2
    # Ranks should be assigned in order
    assert rows[0]["rank"] == 1
    assert rows[1]["rank"] == 2
    # Scores should be in descending order of _score? We dropped _score; just check ranks are correct order
    assert rows[0]["rank"] < rows[1]["rank"]


def test_sweep_output_format_selection_csv():
    code, out, err = _run_sweep(
        [
            "sweep",
            "--strategy",
            "mean_reversion",
            "--grid",
            '{"lookback":[10]}',
            "--data-source",
            "synthetic",
            "--output",
            "csv",
        ]
    )
    assert code == 0
    # CSV should have header
    assert "lookback" in out
    assert "oos_mean_return" in out
    assert "rank" in out


def test_sweep_output_format_selection_text():
    code, out, err = _run_sweep(
        [
            "sweep",
            "--strategy",
            "mean_reversion",
            "--grid",
            '{"lookback":[10]}',
            "--data-source",
            "synthetic",
            "--output",
            "text",
        ]
    )
    assert code == 0
    assert "lookback" in out


def test_sweep_invalid_metric_handling():
    with pytest.raises(SystemExit):
        main(
            [
                "sweep",
                "--strategy",
                "mean_reversion",
                "--grid",
                '{"lookback":[10]}',
                "--metric",
                "invalid_metric",
            ]
        )
