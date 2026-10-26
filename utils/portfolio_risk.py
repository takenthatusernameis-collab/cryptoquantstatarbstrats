"""
Portfolio-level risk metrics.

Utilities for measuring risk at the portfolio level from asset returns and
weights. All functions return floats (or, for marginal/component VaR, numpy
arrays) and degrade gracefully on empty or degenerate inputs.

Supported metrics:

* :func:`portfolio_var` - historical Value at Risk of the portfolio.
* :func:`portfolio_cvar` - historical Conditional VaR (expected shortfall).
* :func:`conditional_drawdown_at_risk` - average drawdown beyond the VaR
  threshold (CDaR).
* :func:`marginal_var` - per-asset marginal VaR (normal approximation).
* :func:`component_var` - per-asset component VaR (sums to portfolio VaR).
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import norm


def _as_1d_array(values: Any) -> np.ndarray:
    """Convert ``values`` to a 1-D float ndarray with NaNs dropped."""
    if isinstance(values, pd.Series):
        arr = values.dropna().to_numpy(dtype=float)
    else:
        arr = np.asarray(values, dtype=float).ravel()
        arr = arr[~np.isnan(arr)]
    return arr


def _portfolio_returns(
    returns: pd.DataFrame | pd.Series | np.ndarray, weights: np.ndarray | None
) -> np.ndarray:
    """Compute portfolio returns from asset returns and weights.

    When ``returns`` is already a 1-D series (e.g. pre-computed portfolio
    returns) it is returned as-is. Otherwise it is treated as an assets x
    time DataFrame and combined with ``weights``.
    """
    if isinstance(returns, pd.Series):
        return _as_1d_array(returns)
    arr = np.asarray(returns, dtype=float)
    if arr.ndim == 1:
        return _as_1d_array(arr)
    # time x assets -> combine with weights
    if weights is None:
        weights = np.ones(arr.shape[1]) / arr.shape[1]
    w = np.asarray(weights, dtype=float).ravel()
    if w.shape[0] != arr.shape[1]:
        raise ValueError("weights length must match number of assets in returns")
    port = arr @ w  # time series of portfolio returns
    return port[~np.isnan(port)]


def _is_finite(value: Any) -> bool:
    """Return True when ``value`` is a real finite number."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return False
    return v == v and v not in (float("inf"), float("-inf"))


def portfolio_var(
    returns: pd.DataFrame | pd.Series | np.ndarray,
    weights: np.ndarray | pd.Series | None = None,
    confidence: float = 0.95,
) -> float:
    """Historical Value at Risk of a portfolio.

    Computes portfolio returns (asset returns combined with ``weights``,
    or the series directly when already 1-D) and returns the
    ``(1 - confidence)`` percentile as a negative return figure.

    Args:
        returns: Asset returns (DataFrame assets x time) or pre-computed
            portfolio returns (Series/1-D array).
        weights: Per-asset weights. Ignored when ``returns`` is 1-D.
        confidence: Confidence level in ``(0, 1)``.

    Returns:
        Portfolio VaR as a negative return (or ``0.0`` on empty input).
    """
    try:
        conf = float(confidence)
    except (TypeError, ValueError):
        conf = 0.95
    if not _is_finite(conf) or conf <= 0.0 or conf >= 1.0:
        conf = 0.95

    w = None
    if weights is not None:
        w = np.asarray(weights, dtype=float).ravel()
        if w.shape[0] == 0 or np.any(~np.isfinite(w)):
            w = None

    port = _portfolio_returns(returns, w)
    if port.size == 0:
        return 0.0

    var_result = float(np.percentile(port, (1.0 - conf) * 100.0))
    return var_result if _is_finite(var_result) else 0.0


def portfolio_cvar(
    returns: pd.DataFrame | pd.Series | np.ndarray,
    weights: np.ndarray | pd.Series | None = None,
    confidence: float = 0.95,
) -> float:
    """Historical Conditional VaR (expected shortfall) of a portfolio.

    Returns the mean of portfolio returns at or below the VaR threshold.

    Args:
        returns: Asset returns (DataFrame assets x time) or pre-computed
            portfolio returns (Series/1-D array).
        weights: Per-asset weights. Ignored when ``returns`` is 1-D.
        confidence: Confidence level in ``(0, 1)``.

    Returns:
        Portfolio CVaR as a negative return (or ``0.0`` on empty input).
    """
    try:
        conf = float(confidence)
    except (TypeError, ValueError):
        conf = 0.95
    if not _is_finite(conf) or conf <= 0.0 or conf >= 1.0:
        conf = 0.95

    w = None
    if weights is not None:
        w = np.asarray(weights, dtype=float).ravel()
        if w.shape[0] == 0 or np.any(~np.isfinite(w)):
            w = None

    port = _portfolio_returns(returns, w)
    if port.size == 0:
        return 0.0

    var_threshold = float(np.percentile(port, (1.0 - conf) * 100.0))
    tail = port[port <= var_threshold]
    if tail.size == 0:
        return var_threshold
    cvar_result = float(np.mean(tail))
    return cvar_result if _is_finite(cvar_result) else 0.0


def conditional_drawdown_at_risk(
    equity_curve: pd.Series | pd.DataFrame | np.ndarray,
    confidence: float = 0.95,
) -> float:
    """Conditional Drawdown at Risk (CDaR).

    Computes the drawdown series from the equity curve, takes the VaR of
    drawdowns at ``confidence``, and returns the mean of drawdowns at or
    beyond that threshold as a positive magnitude.

    Args:
        equity_curve: Portfolio equity curve over time.
        confidence: Confidence level in ``(0, 1)``.

    Returns:
        CDaR as a positive drawdown magnitude (or ``0.0`` on empty input).
    """
    try:
        conf = float(confidence)
    except (TypeError, ValueError):
        conf = 0.95
    if not _is_finite(conf) or conf <= 0.0 or conf >= 1.0:
        conf = 0.95

    if isinstance(equity_curve, pd.DataFrame):
        equity = equity_curve.iloc[:, 0]
    elif isinstance(equity_curve, pd.Series):
        equity = equity_curve
    else:
        equity = pd.Series(np.asarray(equity_curve, dtype=float).ravel())

    equity = equity.dropna()
    if equity.size == 0:
        return 0.0

    running_max = equity.cummax()
    drawdown = equity / running_max - 1.0
    dd = drawdown.to_numpy(dtype=float)
    dd = dd[~np.isnan(dd)]
    if dd.size == 0:
        return 0.0

    # Drawdowns are negative; VaR of drawdowns (a negative threshold).
    var_threshold = float(np.percentile(dd, (1.0 - conf) * 100.0))
    tail = dd[dd <= var_threshold]
    if tail.size == 0:
        return abs(var_threshold) if _is_finite(var_threshold) else 0.0
    cdar = float(np.mean(tail))
    return abs(cdar) if _is_finite(cdar) else 0.0


def marginal_var(
    returns: pd.DataFrame | np.ndarray,
    weights: np.ndarray | pd.Series | None = None,
    confidence: float = 0.95,
) -> np.ndarray:
    """Per-asset marginal VaR (normal approximation).

    Under the normal approximation::

        VaR_p = z_alpha * sigma_p
        MVaR_i = d VaR_p / d w_i = z_alpha * (Sigma w)_i / sigma_p

    Returns a per-asset array; when portfolio volatility is zero or the
    covariance is degenerate, returns zeros.

    Args:
        returns: Asset returns (DataFrame assets x time or 2-D array).
        weights: Per-asset weights. Defaults to equal weights.
        confidence: Confidence level in ``(0, 1)``.

    Returns:
        1-D array of marginal VaR per asset (same length as number of assets).
    """
    try:
        conf = float(confidence)
    except (TypeError, ValueError):
        conf = 0.95
    if not _is_finite(conf) or conf <= 0.0 or conf >= 1.0:
        conf = 0.95

    if isinstance(returns, pd.DataFrame):
        arr = returns.to_numpy(dtype=float)
    else:
        arr = np.asarray(returns, dtype=float)
    if arr.ndim != 2:
        return np.array([])
    n_assets = arr.shape[0]
    if n_assets == 0:
        return np.array([])

    if weights is None:
        w = np.ones(n_assets) / n_assets
    else:
        w = np.asarray(weights, dtype=float).ravel()
        if w.shape[0] != n_assets or np.any(~np.isfinite(w)):
            w = np.ones(n_assets) / n_assets

    # Drop NaN columns/time observations pairwise via covariance.
    clean = pd.DataFrame(arr.T)
    clean = clean.dropna(axis=1)
    if clean.shape[1] == 0:
        return np.zeros(n_assets)
    cov = clean.cov().to_numpy(dtype=float)

    z = norm.ppf(conf)
    try:
        sigma_vec = cov @ w
        port_var = float(w @ sigma_vec)
        if not _is_finite(port_var) or port_var <= 0.0:
            return np.zeros(n_assets)
        port_vol = np.sqrt(port_var)
        mvar = z * sigma_vec / port_vol
        mvar = np.where(np.isfinite(mvar), mvar, 0.0)
        return mvar
    except np.linalg.LinAlgError:
        return np.zeros(n_assets)


def component_var(
    returns: pd.DataFrame | np.ndarray,
    weights: np.ndarray | pd.Series | None = None,
    confidence: float = 0.95,
) -> np.ndarray:
    """Per-asset component VaR.

    Component VaR_i = w_i * MVaR_i, so the components sum to portfolio VaR
    under the normal approximation.

    Args:
        returns: Asset returns (DataFrame assets x time or 2-D array).
        weights: Per-asset weights. Defaults to equal weights.
        confidence: Confidence level in ``(0, 1)``.

    Returns:
        1-D array of component VaR per asset.
    """
    if isinstance(returns, pd.DataFrame):
        arr = returns.to_numpy(dtype=float)
    else:
        arr = np.asarray(returns, dtype=float)
    if arr.ndim != 2 or arr.shape[0] == 0:
        return np.array([])
    n_assets = arr.shape[0]

    if weights is None:
        w = np.ones(n_assets) / n_assets
    else:
        w = np.asarray(weights, dtype=float).ravel()
        if w.shape[0] != n_assets or np.any(~np.isfinite(w)):
            w = np.ones(n_assets) / n_assets

    mvar = marginal_var(arr, w, confidence=confidence)
    cvar_comp = w * mvar
    return np.where(np.isfinite(cvar_comp), cvar_comp, 0.0)
