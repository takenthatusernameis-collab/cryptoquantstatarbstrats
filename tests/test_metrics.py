from __future__ import annotations

import numpy as np
import pandas as pd

from utils.metrics import cvar, max_drawdown_duration_from_curve, sharpe_ratio, sortino_ratio, var


def test_sharpe_ratio_zero_std():
    returns = np.zeros(10)
    assert sharpe_ratio(returns) == 0.0


def test_sharpe_ratio_basic():
    rng = np.random.default_rng(0)
    r = rng.normal(0.001, 0.01, 252)
    val = sharpe_ratio(r)
    assert isinstance(val, float)


def test_sharpe_ratio_series():
    s = pd.Series([0.01, -0.005, 0.002, 0.0])
    assert isinstance(sharpe_ratio(s), float)


def test_sharpe_ratio_empty():
    assert sharpe_ratio([]) == 0.0
    assert sharpe_ratio(pd.Series([], dtype=float)) == 0.0


def test_sortino_ratio_basic():
    returns = np.array([0.01, -0.002, 0.015, -0.001, 0.02])
    val = sortino_ratio(returns)
    assert isinstance(val, float)
    assert val != 0.0


def test_sortino_ratio_all_positive():
    returns = np.array([0.01, 0.02, 0.005])
    val = sortino_ratio(returns)
    assert isinstance(val, float)


def test_sortino_ratio_empty():
    assert sortino_ratio([]) == 0.0
    assert sortino_ratio(pd.Series([], dtype=float)) == 0.0


def test_sortino_ratio_series():
    s = pd.Series([0.01, -0.005, 0.002])
    assert isinstance(sortino_ratio(s), float)


def test_var_basic():
    returns = np.array([-0.02, -0.01, 0.0, 0.01, 0.02])
    val = var(returns, confidence=0.95)
    assert isinstance(val, float)


def test_var_empty():
    assert var([]) == 0.0
    assert var(pd.Series([], dtype=float)) == 0.0


def test_var_series():
    s = pd.Series([-0.03, -0.01, 0.01, 0.02])
    assert isinstance(var(s, confidence=0.95), float)


def test_cvar_basic():
    returns = np.array([-0.05, -0.02, -0.01, 0.0, 0.01, 0.02])
    val = cvar(returns, confidence=0.95)
    assert isinstance(val, float)


def test_cvar_empty():
    assert cvar([]) == 0.0
    assert cvar(pd.Series([], dtype=float)) == 0.0


def test_cvar_series():
    s = pd.Series([-0.04, -0.02, 0.01, 0.03])
    assert isinstance(cvar(s, confidence=0.95), float)


def test_max_drawdown_duration_from_curve_basic():
    equity = pd.Series([100, 110, 105, 95, 100, 120])
    duration = max_drawdown_duration_from_curve(equity)
    assert isinstance(duration, int)
    assert duration >= 0


def test_max_drawdown_duration_from_curve_no_drawdown():
    equity = pd.Series([100, 110, 120, 130])
    duration = max_drawdown_duration_from_curve(equity)
    assert duration == 0


def test_max_drawdown_duration_from_curve_empty():
    duration = max_drawdown_duration_from_curve([])
    assert duration == 0
    assert max_drawdown_duration_from_curve(pd.Series([], dtype=float)) == 0


def test_max_drawdown_duration_from_curve_list():
    equity = [100, 90, 80, 90]
    duration = max_drawdown_duration_from_curve(equity)
    assert isinstance(duration, int)


def test_alpha_basic():
    from utils.metrics import alpha

    returns = np.array([0.01, 0.02, -0.01, 0.015])
    market_returns = np.array([0.008, 0.015, -0.005, 0.01])
    val = alpha(returns, market_returns)
    assert isinstance(val, float)


def test_tracking_error_basic():
    from utils.metrics import tracking_error

    returns = np.array([0.01, 0.02, -0.01])
    benchmark_returns = np.array([0.008, 0.015, -0.005])
    val = tracking_error(returns, benchmark_returns)
    assert isinstance(val, float)
    assert val >= 0


def test_win_rate_basic():
    from utils.metrics import win_rate

    returns = np.array([0.01, -0.005, 0.02, -0.001, 0.015])
    assert win_rate(returns) == 0.6


def test_profit_factor_basic():
    from utils.metrics import profit_factor

    returns = np.array([0.02, -0.01, 0.01, -0.005])
    pf = profit_factor(returns)
    assert isinstance(pf, float)
    assert pf > 0


def test_max_drawdown_percent_basic():
    from utils.metrics import max_drawdown_percent

    equity = pd.Series([100, 110, 90, 95])
    val = max_drawdown_percent(equity)
    assert isinstance(val, float)
    assert val > 0
