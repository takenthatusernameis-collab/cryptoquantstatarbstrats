from __future__ import annotations

import numpy as np
import pandas as pd

from utils.metrics import sharpe_ratio


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
