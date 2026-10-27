"""
Portfolio optimization utilities.

Helpers for constructing portfolio weights from a covariance matrix and
(expected) returns. All functions are pure: given a covariance matrix
(and, for mean-variance, expected returns) they return a weight vector.
They are intentionally decoupled from the backtest engine so they can be
used standalone or combined with :meth:`backtest.engine.BacktestEngine.run_portfolio`.

Supported schemes:

* :func:`equal_weight` - 1/n allocation.
* :func:`inverse_volatility` - weight inversely to asset volatility (diagonal of
  the covariance matrix).
* :func:`min_variance_weights` - analytic minimum-variance portfolio
  (``w ∝ Σ⁻¹ 1``, normalized to sum to one).
* :func:`mean_variance_weights` - mean-variance optimal portfolio
  (``w ∝ Σ⁻¹ μ / risk_aversion``, normalized to sum to one).
* :func:`risk_parity_weights` - risk parity via inverse-volatility weighting
  (each asset contributes roughly equal risk under the diagonal
  approximation).
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def _as_2d_array(cov_matrix: Any) -> np.ndarray:
    """Convert ``cov_matrix`` to a 2-D float ndarray, validating squareness."""
    if isinstance(cov_matrix, pd.DataFrame):
        cov_matrix = cov_matrix.values
    arr = np.asarray(cov_matrix, dtype=float)
    if arr.ndim == 1:
        # Treat a 1-D input as a diagonal covariance matrix.
        arr = np.diag(arr)
    if arr.ndim != 2 or arr.shape[0] != arr.shape[1]:
        raise ValueError("cov_matrix must be square")
    return arr


def _is_finite(value: Any) -> bool:
    """Return True when ``value`` is a real finite number."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return False
    return v == v and v not in (float("inf"), float("-inf"))


def _normalize_weights(weights: np.ndarray) -> np.ndarray:
    """Normalize a weight vector to sum to one (returning zeros on failure)."""
    total = float(np.sum(weights))
    if not _is_finite(total) or total == 0.0:
        return np.zeros_like(weights)
    return weights / total


def equal_weight(n: int) -> np.ndarray:
    """Equal weight allocation across ``n`` assets.

    Args:
        n: Number of assets. Must be a positive integer.

    Returns:
        A length-``n`` array where every entry is ``1/n``, or an empty array
        when ``n`` is not a positive integer.
    """
    if n is None:
        return np.array([], dtype=float)
    try:
        n_int = int(n)
    except (TypeError, ValueError):
        return np.array([], dtype=float)
    if n_int <= 0:
        return np.array([], dtype=float)
    return np.ones(n_int, dtype=float) / n_int


def inverse_volatility(cov_matrix: np.ndarray | pd.DataFrame) -> np.ndarray:
    """Inverse-volatility weighting.

    Weights are inversely proportional to asset volatility, estimated from the
    diagonal of the covariance matrix. Assets with non-positive variance fall
    back to equal weighting.

    Args:
        cov_matrix: Covariance matrix (square 2-D array or DataFrame).

    Returns:
        Normalized weight vector summing to one.
    """
    cov = _as_2d_array(cov_matrix)
    n = cov.shape[0]
    if n == 0:
        return np.array([], dtype=float)
    if n == 1:
        return np.array([1.0])
    vols = np.sqrt(np.diag(cov))
    if np.any(~np.isfinite(vols)) or np.any(vols <= 0):
        return equal_weight(n)
    inv_vols = 1.0 / vols
    return _normalize_weights(inv_vols)


def min_variance_weights(cov_matrix: np.ndarray | pd.DataFrame) -> np.ndarray:
    """Analytic minimum-variance portfolio weights.

    Solves ``w ∝ Σ⁻¹ 1`` subject to weights summing to one. Falls back to
    equal weights when the covariance matrix is singular, non-positive
    definite, or otherwise non-invertible.

    Args:
        cov_matrix: Covariance matrix (square 2-D array or DataFrame).

    Returns:
        Normalized weight vector summing to one.
    """
    cov = _as_2d_array(cov_matrix)
    n = cov.shape[0]
    if n == 0:
        return np.array([], dtype=float)
    if n == 1:
        if not _is_finite(cov[0, 0]) or cov[0, 0] <= 0:
            return np.array([1.0])
        return np.array([1.0])
    try:
        inv_cov = np.linalg.inv(cov)
        ones = np.ones(n)
        weights = inv_cov @ ones
        denom = float(ones @ inv_cov @ ones)
        if not _is_finite(denom) or denom == 0.0:
            return equal_weight(n)
        weights = weights / denom
        if np.any(~np.isfinite(weights)):
            return equal_weight(n)
        return _normalize_weights(weights)
    except np.linalg.LinAlgError:
        return equal_weight(n)


def mean_variance_weights(
    cov_matrix: np.ndarray | pd.DataFrame,
    expected_returns: np.ndarray | pd.Series | pd.DataFrame | None = None,
    risk_aversion: float = 1.0,
) -> np.ndarray:
    """Mean-variance optimal portfolio weights.

    Computes the unconstrained mean-variance optimum ``w ∝ Σ⁻¹ μ / risk_aversion``
    and normalizes so weights sum to one. When ``expected_returns`` is not
    provided (or is degenerate) this reduces to the minimum-variance
    portfolio.

    Args:
        cov_matrix: Covariance matrix (square 2-D array or DataFrame).
        expected_returns: Expected returns per asset, aligned with the rows of
            ``cov_matrix``. When omitted, non-finite, or zero-norm, falls back
            to minimum-variance weights.
        risk_aversion: Risk-aversion coefficient. Must be positive and finite;
            non-positive or non-finite values fall back to ``1.0``.

    Returns:
        Normalized weight vector summing to one.
    """
    cov = _as_2d_array(cov_matrix)
    n = cov.shape[0]
    if n == 0:
        return np.array([], dtype=float)
    if n == 1:
        return np.array([1.0])

    try:
        ra = float(risk_aversion)
    except (TypeError, ValueError):
        ra = 1.0
    if not _is_finite(ra) or ra <= 0.0:
        ra = 1.0

    mu = None
    if expected_returns is not None:
        if isinstance(expected_returns, (pd.DataFrame, pd.Series)):
            mu = np.asarray(expected_returns.values, dtype=float).ravel()
        else:
            mu = np.asarray(expected_returns, dtype=float).ravel()
        if mu.shape[0] != n or np.any(~np.isfinite(mu)) or np.all(mu == 0.0):
            mu = None

    try:
        inv_cov = np.linalg.inv(cov)
        ones = np.ones(n)
        if mu is None:
            weights = inv_cov @ ones
            denom = float(ones @ inv_cov @ ones)
        else:
            weights = (1.0 / ra) * (inv_cov @ mu)
            denom = float(np.sum(weights))
        if not _is_finite(denom) or denom == 0.0:
            return equal_weight(n)
        weights = weights / denom
        if np.any(~np.isfinite(weights)):
            return equal_weight(n)
        return _normalize_weights(weights)
    except np.linalg.LinAlgError:
        return equal_weight(n)


def risk_parity_weights(cov_matrix: np.ndarray | pd.DataFrame) -> np.ndarray:
    """Risk parity weights via inverse-volatility weighting.

    Under the diagonal approximation each asset's risk contribution is
    proportional to its volatility, so inverse-volatility weighting equalizes
    risk contributions. See :func:`inverse_volatility`.

    Args:
        cov_matrix: Covariance matrix (square 2-D array or DataFrame).

    Returns:
        Normalized weight vector summing to one.
    """
    return inverse_volatility(cov_matrix)


def make_equal_weight_optimizer():
    """Return an optimizer callable for walk-forward reoptimization.

    The returned callable accepts ``train_data`` and returns a weights
    DataFrame aligned to ``train_data`` columns (equal weight).
    """

    def _optimizer(train_data: pd.DataFrame | pd.Series):
        if isinstance(train_data, pd.Series):
            n = len(train_data)
            cols = list(train_data.index)
            w = equal_weight(n)
            s = pd.Series(w, index=cols)
            return s.to_frame().T
        if isinstance(train_data, pd.DataFrame):
            cols = list(train_data.columns)
            n = len(cols)
            w = equal_weight(n)
            idx = [train_data.index[0]] if len(train_data.index) > 0 else [0]
            return pd.DataFrame([w], columns=cols, index=idx)
        return pd.DataFrame()

    return _optimizer


def make_inverse_volatility_optimizer(lookback: int | None = None):
    """Return an inverse-volatility optimizer callable.

    Computes returns on ``train_data``, builds covariance matrix,
    and returns weights via :func:`inverse_volatility`.
    """

    def _optimizer(train_data: pd.DataFrame | pd.Series):
        if isinstance(train_data, pd.Series):
            train_data = train_data.to_frame()
        if not isinstance(train_data, pd.DataFrame) or train_data.empty:
            return pd.DataFrame()
        try:
            returns = train_data.pct_change().dropna(how="all")
            if returns.empty:
                returns = train_data
            cov = returns.cov()
            w = inverse_volatility(cov)
            cols = list(train_data.columns)
            if len(w) != len(cols):
                # align by columns order
                cov_aligned = cov.reindex(index=cols, columns=cols).fillna(0.0)
                w = inverse_volatility(cov_aligned)
            idx = [train_data.index[0]] if len(train_data.index) > 0 else [0]
            return pd.DataFrame(
                [np.asarray(w, dtype=float).ravel()[: len(cols)]],
                columns=cols,
                index=idx,
            )
        except Exception:
            cols = list(train_data.columns)
            idx = [train_data.index[0]] if len(train_data.index) > 0 else [0]
            return pd.DataFrame([equal_weight(len(cols))], columns=cols, index=idx)

    return _optimizer


def make_risk_parity_optimizer(lookback: int | None = None):
    """Return a risk-parity optimizer callable (inverse-volatility approximation)."""

    def _optimizer(train_data: pd.DataFrame | pd.Series):
        if isinstance(train_data, pd.Series):
            train_data = train_data.to_frame()
        if not isinstance(train_data, pd.DataFrame) or train_data.empty:
            return pd.DataFrame()
        try:
            returns = train_data.pct_change().dropna(how="all")
            if returns.empty:
                returns = train_data
            cov = returns.cov()
            w = risk_parity_weights(cov)
            cols = list(train_data.columns)
            if len(w) != len(cols):
                cov_aligned = cov.reindex(index=cols, columns=cols).fillna(0.0)
                w = risk_parity_weights(cov_aligned)
            idx = [train_data.index[0]] if len(train_data.index) > 0 else [0]
            return pd.DataFrame(
                [np.asarray(w, dtype=float).ravel()[: len(cols)]],
                columns=cols,
                index=idx,
            )
        except Exception:
            cols = list(train_data.columns)
            idx = [train_data.index[0]] if len(train_data.index) > 0 else [0]
            return pd.DataFrame([equal_weight(len(cols))], columns=cols, index=idx)

    return _optimizer


def make_min_variance_optimizer(lookback: int | None = None):
    """Return a minimum-variance optimizer callable."""

    def _optimizer(train_data: pd.DataFrame | pd.Series):
        if isinstance(train_data, pd.Series):
            train_data = train_data.to_frame()
        if not isinstance(train_data, pd.DataFrame) or train_data.empty:
            return pd.DataFrame()
        try:
            returns = train_data.pct_change().dropna(how="all")
            if returns.empty:
                returns = train_data
            cov = returns.cov()
            w = min_variance_weights(cov)
            cols = list(train_data.columns)
            if len(w) != len(cols):
                cov_aligned = cov.reindex(index=cols, columns=cols).fillna(0.0)
                w = min_variance_weights(cov_aligned)
            idx = [train_data.index[0]] if len(train_data.index) > 0 else [0]
            return pd.DataFrame(
                [np.asarray(w, dtype=float).ravel()[: len(cols)]],
                columns=cols,
                index=idx,
            )
        except Exception:
            cols = list(train_data.columns)
            idx = [train_data.index[0]] if len(train_data.index) > 0 else [0]
            return pd.DataFrame([equal_weight(len(cols))], columns=cols, index=idx)

    return _optimizer


def make_mean_variance_optimizer(
    expected_returns: Any = None,
    risk_aversion: float = 1.0,
    lookback: int | None = None,
):
    """Return a mean-variance optimizer callable."""

    def _optimizer(train_data: pd.DataFrame | pd.Series):
        if isinstance(train_data, pd.Series):
            train_data = train_data.to_frame()
        if not isinstance(train_data, pd.DataFrame) or train_data.empty:
            return pd.DataFrame()
        try:
            returns = train_data.pct_change().dropna(how="all")
            if returns.empty:
                returns = train_data
            cov = returns.cov()
            mu = expected_returns
            if mu is None:
                try:
                    mu = returns.mean()
                except Exception:
                    mu = None
            w = mean_variance_weights(cov, expected_returns=mu, risk_aversion=risk_aversion)
            cols = list(train_data.columns)
            if len(w) != len(cols):
                try:
                    mu2 = mu
                    if isinstance(mu2, (pd.Series, pd.DataFrame)):
                        mu2 = pd.Series(mu2).reindex(cols).fillna(0.0)
                    cov2 = cov.reindex(index=cols, columns=cols).fillna(0.0)
                    w = mean_variance_weights(
                        cov2, expected_returns=mu2, risk_aversion=risk_aversion
                    )
                except Exception:
                    pass
            idx = [train_data.index[0]] if len(train_data.index) > 0 else [0]
            w_arr: np.ndarray = np.asarray(w, dtype=float).ravel()
            if len(w_arr) < len(cols):
                w_arr = np.pad(w_arr, (0, len(cols) - len(w_arr)))
            return pd.DataFrame([w_arr[:len(cols)]], columns=cols, index=idx)
        except Exception:
            cols = list(train_data.columns)
            idx = [train_data.index[0]] if len(train_data.index) > 0 else [0]
            return pd.DataFrame([equal_weight(len(cols))], columns=cols, index=idx)

    return _optimizer


OPTIMIZERS = {
    "equal": make_equal_weight_optimizer,
    "equal_weight": make_equal_weight_optimizer,
    "1/n": make_equal_weight_optimizer,
    "inverse_vol": make_inverse_volatility_optimizer,
    "inverse_volatility": make_inverse_volatility_optimizer,
    "iv": make_inverse_volatility_optimizer,
    "risk_parity": make_risk_parity_optimizer,
    "min_variance": make_min_variance_optimizer,
    "minimum_variance": make_min_variance_optimizer,
    "mean_variance": make_mean_variance_optimizer,
    "mv": make_mean_variance_optimizer,
}


def get_optimizer(name: str, **kwargs: Any):
    """Get an optimizer callable by name."""
    if name is None:
        return None
    key = str(name).strip().lower().replace("-", "_")
    if key in OPTIMIZERS:
        factory = OPTIMIZERS[key]
        try:
            return factory(**kwargs)
        except TypeError:
            return factory()
    raise ValueError(f"Unknown optimizer: {name}")
