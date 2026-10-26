from __future__ import annotations

import numpy as np
import pandas as pd

from utils.regime import detect_regimes, trend_detection, volatility_regime


def test_volatility_regime_shape():
    rng = np.random.default_rng(0)
    s = pd.Series(100 + np.cumsum(rng.normal(0, 1, 100)))
    r = volatility_regime(s, window=10, n_regimes=3)
    assert len(r) == len(s)


def test_trend_detection_values():
    s = pd.Series([1.0, 2, 3, 4, 5, 6, 7, 8, 9, 10] * 10)
    t = trend_detection(s, short_window=3, long_window=8)
    assert set(t.unique()).issubset({-1, 0, 1})


def test_detect_regimes():
    df = pd.DataFrame({"a": np.arange(50, dtype=float), "b": np.arange(50, dtype=float) * 2})
    out = detect_regimes(df)
    assert "a_vol_regime" in out.columns
    assert "a_trend" in out.columns
