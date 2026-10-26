"""
Tests for portfolio optimization utilities in utils/optimization.py.

Covers equal weighting, inverse-volatility weighting, minimum-variance,
mean-variance, and risk-parity weights, including edge cases (NaN, empty,
single asset, non-square covariance).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from utils.optimization import (
    equal_weight,
    inverse_volatility,
    mean_variance_weights,
    min_variance_weights,
    risk_parity_weights,
)


def test_equal_weight_basic():
    w = equal_weight(4)
    assert w.shape == (4,)
    assert np.allclose(w, 0.25)
    assert abs(w.sum() - 1.0) < 1e-12


def test_equal_weight_single_asset():
    w = equal_weight(1)
    assert np.allclose(w, [1.0])


def test_equal_weight_edge_cases():
    assert equal_weight(0).size == 0
    assert equal_weight(-3).size == 0
    assert equal_weight(None).size == 0
    assert equal_weight("not_an_int").size == 0


def test_inverse_volatility_basic():
    cov = np.diag([0.04, 0.01, 0.16])  # vols 0.2, 0.1, 0.4
    w = inverse_volatility(cov)
    # inverse vol: 5, 10, 2.5 -> normalized: 5/17.5, 10/17.5, 2.5/17.5
    expected = np.array([5.0, 10.0, 2.5]) / 17.5
    assert np.allclose(w, expected)
    assert abs(w.sum() - 1.0) < 1e-12


def test_inverse_volatility_dataframe():
    cov = pd.DataFrame(np.diag([0.04, 0.01]), columns=["A", "B"], index=["A", "B"])
    w = inverse_volatility(cov)
    expected = np.array([1.0 / 3.0, 2.0 / 3.0])  # vol 0.2 vs 0.1
    assert np.allclose(w, expected)


def test_inverse_volatility_single_asset():
    w = inverse_volatility(np.array([[0.04]]))
    assert np.allclose(w, [1.0])


def test_inverse_volatility_empty():
    w = inverse_volatility(np.zeros((0, 0)))
    assert w.size == 0


def test_inverse_volatility_non_positive_vol_falls_back_to_equal():
    # Zero variance on one asset -> fall back to equal weight
    cov = np.diag([0.0, 0.04])
    w = inverse_volatility(cov)
    assert np.allclose(w, [0.5, 0.5])


def test_inverse_volatility_nan_falls_back_to_equal():
    cov = np.diag([np.nan, 0.04])
    w = inverse_volatility(cov)
    assert np.allclose(w, [0.5, 0.5])


def test_inverse_volatility_non_square_raises():
    with pytest.raises(ValueError):
        inverse_volatility(np.zeros((2, 3)))


def test_min_variance_weights_basic():
    cov = np.diag([0.04, 0.01])  # vol 0.2, 0.1
    w = min_variance_weights(cov)
    # inv_cov = diag(25, 100); ones -> [25, 100]; denom 125 -> [0.2, 0.8]
    expected = np.array([0.2, 0.8])
    assert np.allclose(w, expected)
    assert abs(w.sum() - 1.0) < 1e-12


def test_min_variance_weights_single_asset():
    w = min_variance_weights(np.array([[0.04]]))
    assert np.allclose(w, [1.0])


def test_min_variance_weights_empty():
    w = min_variance_weights(np.zeros((0, 0)))
    assert w.size == 0


def test_min_variance_weights_singular_falls_back_to_equal():
    cov = np.ones((2, 2))  # singular (perfectly correlated)
    w = min_variance_weights(cov)
    assert np.allclose(w, [0.5, 0.5])


def test_mean_variance_weights_basic():
    cov = np.diag([0.04, 0.01])
    mu = np.array([0.1, 0.05])
    w = mean_variance_weights(cov, mu, risk_aversion=1.0)
    # inv_cov = diag(25, 100); Sigma^-1 mu = [2.5, 5.0]; /1 -> [2.5, 5.0]; normalize -> [1/3, 2/3]
    expected = np.array([1.0 / 3.0, 2.0 / 3.0])
    assert np.allclose(w, expected)
    assert abs(w.sum() - 1.0) < 1e-12


def test_mean_variance_weights_risk_aversion_scales():
    cov = np.diag([0.04, 0.01])
    mu = np.array([0.1, 0.05])
    w_ra1 = mean_variance_weights(cov, mu, risk_aversion=1.0)
    w_ra2 = mean_variance_weights(cov, mu, risk_aversion=2.0)
    # Both normalize to sum 1, so identical for this diagonal case (direction preserved)
    assert np.allclose(w_ra1, w_ra2)


def test_mean_variance_weights_no_expected_returns_falls_back_to_min_var():
    cov = np.diag([0.04, 0.01])
    w = mean_variance_weights(cov, None)
    expected = min_variance_weights(cov)
    assert np.allclose(w, expected)


def test_mean_variance_weights_single_asset():
    w = mean_variance_weights(np.array([[0.04]]), np.array([0.1]))
    assert np.allclose(w, [1.0])


def test_mean_variance_weights_empty():
    w = mean_variance_weights(np.zeros((0, 0)), np.array([]))
    assert w.size == 0


def test_mean_variance_weights_invalid_risk_aversion_defaults():
    cov = np.diag([0.04, 0.01])
    mu = np.array([0.1, 0.05])
    w = mean_variance_weights(cov, mu, risk_aversion=0.0)
    assert np.allclose(w, mean_variance_weights(cov, mu, risk_aversion=1.0))
    w = mean_variance_weights(cov, mu, risk_aversion=float("nan"))
    assert np.allclose(w, mean_variance_weights(cov, mu, risk_aversion=1.0))


def test_mean_variance_weights_degenerate_mu_falls_back_to_min_var():
    cov = np.diag([0.04, 0.01])
    mu = np.array([0.0, 0.0])
    w = mean_variance_weights(cov, mu)
    assert np.allclose(w, min_variance_weights(cov))


def test_mean_variance_weights_non_square_raises():
    with pytest.raises(ValueError):
        mean_variance_weights(np.zeros((2, 3)), np.array([0.1, 0.2]))


def test_risk_parity_weights_matches_inverse_volatility():
    cov = np.diag([0.04, 0.01, 0.16])
    assert np.allclose(risk_parity_weights(cov), inverse_volatility(cov))


def test_risk_parity_weights_edge_cases():
    assert risk_parity_weights(np.zeros((0, 0))).size == 0
    assert np.allclose(risk_parity_weights(np.array([[0.04]])), [1.0])
