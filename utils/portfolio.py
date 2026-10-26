"""
Portfolio optimization utilities.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def equal_weight(n: int) -> np.ndarray:
    """Equal weight allocation."""
    if n <= 0:
        return np.array([])
    return np.ones(n) / n


def risk_parity_weights(cov_matrix: np.ndarray | pd.DataFrame) -> np.ndarray:
    """Compute risk parity weights (inverse volatility weighting)."""
    if isinstance(cov_matrix, pd.DataFrame):
        cov_matrix = cov_matrix.values

    cov_matrix = np.asarray(cov_matrix)
    if cov_matrix.ndim != 2 or cov_matrix.shape[0] != cov_matrix.shape[1]:
        raise ValueError("cov_matrix must be square")

    n = cov_matrix.shape[0]
    if n == 0:
        return np.array([])

    # Use diagonal for volatility
    vols = np.sqrt(np.diag(cov_matrix))
    if np.any(vols <= 0):
        return equal_weight(n)

    inv_vols = 1.0 / vols
    weights = inv_vols / inv_vols.sum()
    return weights


def minimum_variance_weights(cov_matrix: np.ndarray | pd.DataFrame) -> np.ndarray:
    """Compute minimum variance portfolio weights."""
    if isinstance(cov_matrix, pd.DataFrame):
        cov_matrix = cov_matrix.values

    cov_matrix = np.asarray(cov_matrix)
    if cov_matrix.ndim != 2 or cov_matrix.shape[0] != cov_matrix.shape[1]:
        raise ValueError("cov_matrix must be square")

    n = cov_matrix.shape[0]
    if n == 0:
        return np.array([])
    if n == 1:
        return np.array([1.0])

    try:
        inv_cov = np.linalg.inv(cov_matrix)
        ones = np.ones(n)
        weights = inv_cov @ ones
        weights = weights / (ones @ inv_cov @ ones)
        return weights
    except Exception:
        return equal_weight(n)
