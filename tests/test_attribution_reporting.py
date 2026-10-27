"""Tests for attribution reporting through utils.reporting and CLI."""

from __future__ import annotations

import json

import pandas as pd

from utils.reporting import (
    attribution_report_to_dict,
    generate_attribution_report,
)


def _make_result():
    dates = pd.date_range("2024-01-01", periods=10, freq="1h")
    summary = pd.DataFrame(
        [
            {"asset": "BTC", "allocation": 0.01, "selection": 0.02, "interaction": 0.005, "total": 0.035},
            {"asset": "ETH", "allocation": -0.005, "selection": 0.01, "interaction": -0.002, "total": 0.003},
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
