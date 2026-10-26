"""
Tests for portfolio-level risk metrics in utils/portfolio_risk.py.

Covers portfolio VaR/CVaR, conditional drawdown at risk (CDaR), and
marginal/component VaR, including edge cases (NaN, empty, single asset,
degenerate covariance).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from scipy.stats import norm

from utils.portfolio_risk import (
    component_var,
    conditional_drawdown_at_risk,
    marginal_var,
    portfolio_cvar,
    portfolio_var,
)


def _make_returns() -> pd.DataFrame:
    rng = np.random.default_rng(7)
    n = 200
    r1 = rng.normal(0.001, 0.02, n)
    r2 = 0.5 * r1 + rng.normal(0.0, 0.015, n)
    return pd.DataFrame({"A": r1, "B": r2})


def test_portfolio_var_basic_dataframe():
    returns = _make_returns()
    weights = np.array([0.5, 0.5])
    val = portfolio_var(returns, weights, confidence=0.95)
    assert isinstance(val, float)
    # VaR is a loss percentile; with these returns it should be <= 0.
    assert val <= 0.0


def test_portfolio_var_series_already_portfolio_returns():
    port_returns = pd.Series(np.array([-0.02, -0.01, 0.0, 0.01, 0.02]))
    val = portfolio_var(port_returns, confidence=0.95)
    assert isinstance(val, float)
    # 5% percentile of 5 sorted values via linear interpolation = -0.018.
    assert abs(val - (-0.018)) < 1e-9


def test_portfolio_cvar_basic():
    returns = _make_returns()
    weights = np.array([0.5, 0.5])
    val = portfolio_cvar(returns, weights, confidence=0.95)
    assert isinstance(val, float)
    assert val <= 0.0


def test_portfolio_cvar_tail_is_at_most_var():
    port_returns = pd.Series(np.array([-0.02, -0.01, 0.0, 0.01, 0.02]))
    v = portfolio_var(port_returns, confidence=0.95)
    c = portfolio_cvar(port_returns, confidence=0.95)
    # CVaR (mean of tail) is at most VaR (more negative or equal).
    assert abs(c - (-0.02)) < 1e-9
    assert c <= v


def test_portfolio_var_empty():
    assert portfolio_var(pd.DataFrame(), np.array([])) == 0.0
    assert portfolio_var(pd.Series([], dtype=float)) == 0.0
    assert portfolio_var(np.array([])) == 0.0


def test_portfolio_var_single_asset():
    returns = pd.Series(np.array([-0.02, -0.01, 0.0, 0.01, 0.02]))
    val = portfolio_var(returns, confidence=0.95)
    assert isinstance(val, float)


def test_portfolio_var_invalid_confidence_defaults():
    returns = pd.Series(np.array([-0.02, -0.01, 0.0, 0.01, 0.02]))
    v_default = portfolio_var(returns)
    assert portfolio_var(returns, confidence=0.0) == v_default
    assert portfolio_var(returns, confidence=1.0) == v_default
    assert portfolio_var(returns, confidence=float("nan")) == v_default


def test_portfolio_var_nan_weights():
    returns = _make_returns()
    val = portfolio_var(returns, np.array([np.nan, np.nan]))
    assert isinstance(val, float)


def test_conditional_drawdown_at_risk_basic():
    equity = pd.Series([100.0, 110.0, 105.0, 90.0, 95.0, 100.0])
    cdar = conditional_drawdown_at_risk(equity, confidence=0.95)
    assert isinstance(cdar, float)
    assert cdar >= 0.0


def test_conditional_drawdown_at_risk_no_drawdown_is_zero():
    equity = pd.Series([100.0, 110.0, 120.0, 130.0])
    assert conditional_drawdown_at_risk(equity, confidence=0.95) == 0.0


def test_conditional_drawdown_at_risk_empty():
    assert conditional_drawdown_at_risk(pd.Series([], dtype=float)) == 0.0
    assert conditional_drawdown_at_risk(np.array([])) == 0.0


def test_conditional_drawdown_at_risk_invalid_confidence_defaults():
    equity = pd.Series([100.0, 110.0, 90.0, 95.0])
    v_default = conditional_drawdown_at_risk(equity)
    assert conditional_drawdown_at_risk(equity, confidence=0.0) == v_default
    assert conditional_drawdown_at_risk(equity, confidence=1.0) == v_default


def test_marginal_var_basic():
    rng = np.random.default_rng(3)
    n = 300
    r1 = rng.normal(0.001, 0.02, n)
    r2 = rng.normal(0.0, 0.015, n)
    returns = pd.DataFrame({"A": r1, "B": r2}).to_numpy().T  # assets x time
    weights = np.array([0.5, 0.5])
    mvar = marginal_var(returns, weights, confidence=0.95)
    assert isinstance(mvar, np.ndarray)
    assert mvar.shape == (2,)
    assert np.all(np.isfinite(mvar))


def test_marginal_var_component_var_relationship():
    rng = np.random.default_rng(3)
    n = 300
    r1 = rng.normal(0.001, 0.02, n)
    r2 = rng.normal(0.0, 0.015, n)
    returns = pd.DataFrame({"A": r1, "B": r2}).to_numpy().T
    weights = np.array([0.5, 0.5])
    mvar = marginal_var(returns, weights, confidence=0.95)
    cvar_comp = component_var(returns, weights, confidence=0.95)
    assert cvar_comp.shape == (2,)
    assert np.allclose(cvar_comp, weights * mvar)


def test_marginal_var_component_var_sum_equals_parametric_var():
    rng = np.random.default_rng(3)
    n = 300
    r1 = rng.normal(0.001, 0.02, n)
    r2 = rng.normal(0.0, 0.015, n)
    returns = pd.DataFrame({"A": r1, "B": r2}).to_numpy().T
    weights = np.array([0.5, 0.5])
    cvar_comp = component_var(returns, weights, confidence=0.95)
    clean = pd.DataFrame(returns.T).dropna(axis=1)
    cov = clean.cov().to_numpy(dtype=float)
    port_vol = np.sqrt(float(weights @ cov @ weights))
    z = norm.ppf(0.95)
    expected = z * port_vol
    assert abs(cvar_comp.sum() - expected) < 1e-9


def test_marginal_var_empty_and_degenerate():
    assert marginal_var(np.zeros((0, 10))).size == 0
    # Zero variance -> zeros
    returns = np.zeros((2, 100))
    mvar = marginal_var(returns, np.array([0.5, 0.5]))
    assert np.allclose(mvar, [0.0, 0.0])


def test_component_var_empty():
    assert component_var(np.zeros((0, 10))).size == 0


def test_portfolio_var_weights_length_mismatch_raises():
    returns = _make_returns().to_numpy().T
    with pytest.raises(ValueError):
        portfolio_var(returns, np.array([0.5, 0.5, 0.5]))
