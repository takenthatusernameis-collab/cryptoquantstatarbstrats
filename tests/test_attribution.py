"""
Tests for performance attribution and factor decomposition utilities
(``utils.attribution``: ``brinson_attribution`` and ``factor_attribution``).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from utils.attribution import brinson_attribution, factor_attribution


def _make_returns(n: int = 60, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2024-01-01", periods=n, freq="1h")
    return pd.DataFrame(
        {
            "BTC": rng.normal(0.0005, 0.01, n),
            "ETH": rng.normal(0.0003, 0.012, n),
            "SOL": rng.normal(0.0004, 0.015, n),
        },
        index=dates,
    )


def test_brinson_basic_decomposition_identity():
    """Allocation + selection + interaction must reconcile to active return."""
    returns = _make_returns()
    w_p = pd.DataFrame(
        {"BTC": 0.5, "ETH": 0.3, "SOL": 0.2},
        index=returns.index,
    )
    w_b = pd.DataFrame(
        {"BTC": 1.0 / 3.0, "ETH": 1.0 / 3.0, "SOL": 1.0 / 3.0},
        index=returns.index,
    )
    res = brinson_attribution(returns, w_p, w_b, returns)

    active = res["total_active_return"]
    implied = res["allocation_total"] + res["selection_total"] + res["interaction_total"]
    pd.testing.assert_series_equal(active.round(8), implied.round(8))

    # Portfolio return vs benchmark return reconcile.
    port_ret = res["portfolio_return"]
    bench_ret = res["benchmark_return"]
    assert np.allclose((port_ret - bench_ret).values, active.values)

    assert set(res.keys()) >= {
        "allocation",
        "selection",
        "interaction",
        "allocation_total",
        "selection_total",
        "interaction_total",
        "total_active_return",
        "portfolio_return",
        "benchmark_return",
        "summary",
    }


def test_brinson_zero_effects_when_portfolio_equals_benchmark():
    """When weights and returns match the benchmark, all effects vanish."""
    returns = _make_returns()
    w = pd.DataFrame(
        {"BTC": 0.5, "ETH": 0.3, "SOL": 0.2},
        index=returns.index,
    )
    res = brinson_attribution(returns, w, w, returns)

    assert (res["allocation"].abs().sum().sum() < 1e-9)
    assert (res["selection"].abs().sum().sum() < 1e-9)
    assert (res["interaction"].abs().sum().sum() < 1e-9)
    assert (res["allocation_total"].abs() < 1e-9).all()
    assert (res["selection_total"].abs() < 1e-9).all()
    assert (res["interaction_total"].abs() < 1e-9).all()
    assert (res["total_active_return"].abs() < 1e-9).all()


def test_brinson_summary_has_expected_columns():
    returns = _make_returns()
    w_p = pd.DataFrame(
        {"BTC": 0.4, "ETH": 0.35, "SOL": 0.25},
        index=returns.index,
    )
    w_b = pd.DataFrame(
        {"BTC": 1.0 / 3.0, "ETH": 1.0 / 3.0, "SOL": 1.0 / 3.0},
        index=returns.index,
    )
    res = brinson_attribution(returns, w_p, w_b, returns)
    summary = res["summary"]
    assert isinstance(summary, pd.DataFrame)
    assert list(summary.columns) == ["asset", "allocation", "selection", "interaction", "total"]
    assert set(summary["asset"]) == {"BTC", "ETH", "SOL"}


def test_brinson_empty_inputs():
    empty = pd.DataFrame(dtype=float)
    res = brinson_attribution(empty, empty, empty, empty)
    assert res["allocation"].empty
    assert res["selection"].empty
    assert res["interaction"].empty
    assert res["summary"].empty


def test_brinson_aligns_mismatched_indices():
    """Inputs with different dates/columns are aligned on the inner join."""
    dates1 = pd.date_range("2024-01-01", periods=10, freq="1h")
    dates2 = pd.date_range("2024-01-01 02:00", periods=10, freq="1h")  # offset by 2h
    r1 = pd.DataFrame({"BTC": np.arange(10, dtype=float) * 0.001}, index=dates1)
    r2 = pd.DataFrame({"BTC": np.arange(10, dtype=float) * 0.001}, index=dates2)
    w1 = pd.DataFrame({"BTC": 1.0}, index=dates1)
    w2 = pd.DataFrame({"BTC": 0.5}, index=dates2)
    res = brinson_attribution(r1, w1, w2, r2)
    # Should align on the overlapping 8 periods.
    assert len(res["portfolio_return"]) == 8
    assert len(res["benchmark_return"]) == 8


def test_brinson_only_allocation_effect():
    """Same returns, different weights -> pure allocation effect (selection ~ 0)."""
    n = 30
    dates = pd.date_range("2024-01-01", periods=n, freq="1h")
    rng = np.random.default_rng(1)
    r = pd.DataFrame(
        {
            "BTC": rng.normal(0.0005, 0.01, n),
            "ETH": rng.normal(0.0003, 0.01, n),
        },
        index=dates,
    )
    w_p = pd.DataFrame({"BTC": 1.0, "ETH": 0.0}, index=dates)
    w_b = pd.DataFrame({"BTC": 0.0, "ETH": 1.0}, index=dates)
    res = brinson_attribution(r, w_p, w_b, r)
    # Selection uses w_b * (r_p - r_b); with r_p == r_b it is zero.
    assert (res["selection"].abs().sum().sum() < 1e-9)
    # Total active return should be nonzero generally (BTC vs ETH differ).
    assert abs(float(res["total_active_return"].sum())) > 0


def test_factor_basic_recovery():
    """OLS recovers known alpha/beta when returns = alpha + beta * factor exactly."""
    n = 200
    rng = np.random.default_rng(3)
    dates = pd.date_range("2024-01-01", periods=n, freq="1h")
    f = rng.normal(0.0, 0.01, n)
    alpha = 0.0005
    beta = 0.6
    r = alpha + beta * f  # exact, zero residual
    r_series = pd.Series(r, index=dates, name="portfolio")
    f_df = pd.DataFrame({"mkt": f}, index=dates)

    res = factor_attribution(r_series, f_df)
    assert abs(res["alpha"] - alpha) < 1e-6
    assert abs(res["beta"]["mkt"] - beta) < 1e-6
    assert abs(res["r_squared"] - 1.0) < 1e-6
    assert res["n_obs"] == n


def test_factor_single_factor_capm_like():
    """Regressing a series on itself yields beta ~ 1, alpha ~ 0, r2 ~ 1."""
    n = 150
    rng = np.random.default_rng(5)
    dates = pd.date_range("2024-01-01", periods=n, freq="1h")
    r = pd.Series(rng.normal(0.0004, 0.01, n), index=dates, name="r")
    f_df = pd.DataFrame({"r": r.values}, index=dates)
    res = factor_attribution(r, f_df)
    assert abs(res["beta"]["r"] - 1.0) < 1e-6
    assert abs(res["alpha"]) < 1e-6
    assert abs(res["r_squared"] - 1.0) < 1e-6


def test_factor_multi_factor():
    n = 300
    rng = np.random.default_rng(9)
    dates = pd.date_range("2024-01-01", periods=n, freq="1h")
    f1 = rng.normal(0.0, 0.01, n)
    f2 = rng.normal(0.0, 0.008, n)
    alpha = 0.0002
    r = alpha + 0.5 * f1 + (-0.3) * f2 + rng.normal(0, 0.001, n)  # small noise
    r_series = pd.Series(r, index=dates, name="portfolio")
    f_df = pd.DataFrame({"f1": f1, "f2": f2}, index=dates)
    res = factor_attribution(r_series, f_df)
    assert res["n_obs"] == n
    assert 0.0 <= res["r_squared"] <= 1.0
    assert "f1" in res["beta"] and "f2" in res["beta"]
    assert abs(res["beta"]["f1"] - 0.5) < 0.05
    assert abs(res["beta"]["f2"] - (-0.3)) < 0.05


def test_factor_no_factors_alpha_equals_mean():
    n = 100
    rng = np.random.default_rng(11)
    dates = pd.date_range("2024-01-01", periods=n, freq="1h")
    r = pd.Series(rng.normal(0.001, 0.01, n), index=dates, name="portfolio")
    f_df = pd.DataFrame(index=dates)  # no factor columns
    res = factor_attribution(r, f_df)
    assert abs(res["alpha"] - float(r.mean())) < 1e-9
    assert res["r_squared"] == 0.0
    assert res["beta"].empty
    assert res["n_obs"] == n


def test_factor_empty_input():
    r = pd.Series(dtype=float)
    f = pd.DataFrame(dtype=float)
    res = factor_attribution(r, f)
    assert res["n_obs"] == 0
    assert res["r_squared"] == 0.0
    assert res["alpha"] == 0.0
    assert res["beta"].empty


def test_factor_aligns_mismatched_indices():
    dates1 = pd.date_range("2024-01-01", periods=20, freq="1h")
    dates2 = pd.date_range("2024-01-01 01:00", periods=20, freq="1h")
    r = pd.Series(np.arange(20, dtype=float) * 0.001, index=dates1, name="r")
    f = pd.DataFrame({"f": np.arange(20, dtype=float) * 0.001}, index=dates2)
    res = factor_attribution(r, f)
    # Overlap is 19 periods (dates1[1:] == dates2[:19]).
    assert res["n_obs"] == 19


def test_factor_returns_series_and_dataframe_inputs():
    n = 50
    rng = np.random.default_rng(13)
    dates = pd.date_range("2024-01-01", periods=n, freq="1h")
    r_arr = rng.normal(0.0005, 0.01, n)
    f_arr = rng.normal(0.0, 0.01, n)
    # list / array inputs should be coerced without error; align index with factor.
    res = factor_attribution(
        pd.Series(r_arr.tolist(), index=dates, name="portfolio"),
        pd.DataFrame({"f": f_arr}, index=dates),
    )
    assert res["n_obs"] == n


def test_brinson_integration_via_engine_benchmark_weights():
    """Engine attaches brinson attribution when benchmark_weights is passed."""
    from backtest.engine import BacktestEngine
    from strategies.mean_reversion import MeanReversionStrategy

    rng = np.random.default_rng(21)
    dates = pd.date_range("2024-01-01", periods=120, freq="1h")
    price = 100 * np.exp(np.cumsum(rng.normal(0.0002, 0.01, 120)))
    data = pd.DataFrame({"BTC": price, "ETH": price * 0.9}, index=dates)
    strat = MeanReversionStrategy(asset="BTC")
    engine = BacktestEngine(initial_capital=100_000.0)
    w_b = pd.DataFrame({"BTC": 0.5, "ETH": 0.5}, index=data.index)
    result = engine.run(
        strat,
        data,
        benchmark_weights=w_b,
    )
    assert "brinson" in result
    brinson = result["brinson"]
    assert "allocation_total" in brinson
    assert "selection_total" in brinson
    assert "summary" in brinson


def test_factor_integration_via_engine_factor_returns():
    """Engine attaches factor attribution when factor_returns is passed."""
    from backtest.engine import BacktestEngine
    from strategies.mean_reversion import MeanReversionStrategy

    rng = np.random.default_rng(22)
    dates = pd.date_range("2024-01-01", periods=120, freq="1h")
    price = 100 * np.exp(np.cumsum(rng.normal(0.0002, 0.01, 120)))
    data = pd.DataFrame({"BTC": price}, index=dates)
    strat = MeanReversionStrategy(asset="BTC")
    engine = BacktestEngine(initial_capital=100_000.0)
    factor = pd.DataFrame({"mkt": data.pct_change().fillna(0.0)["BTC"]}, index=dates)
    result = engine.run(strat, data, factor_returns=factor)
    assert "factor" in result
    factor_res = result["factor"]
    assert "alpha" in factor_res
    assert "beta" in factor_res
    assert "r_squared" in factor_res
    assert "n_obs" in factor_res
