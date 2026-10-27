"""
Tests for VolatilitySurfaceStrategy.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from backtest.engine import BacktestEngine
from strategies.volatility_surface import VolatilitySurfaceStrategy


def make_data_with_iv(n: int = 200, seed: int = 123) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2024-01-01", periods=n, freq="1h")
    # Create price series
    r = rng.normal(0.0, 0.01, n)
    price = 100 * np.exp(np.cumsum(r))
    # Create IV series that varies
    iv = 0.3 + 0.1 * np.sin(np.linspace(0, 4 * np.pi, n)) + rng.normal(0, 0.02, n)
    iv = np.clip(iv, 0.1, 0.8)
    df = pd.DataFrame(
        {
            "BTC": price,
            "iv": iv,
        },
        index=dates,
    )
    return df


def test_volatility_surface_generate_signals():
    df = make_data_with_iv()
    strat = VolatilitySurfaceStrategy(asset="BTC")
    signals = strat.generate_signals(df)
    assert "iv" in signals.columns
    assert "iv_percentile" in signals.columns
    assert "iv_mean" in signals.columns
    assert "long" in signals.columns
    assert "short" in signals.columns
    assert "exit" in signals.columns
    assert len(signals) == len(df)


def test_volatility_surface_position_sizes():
    df = make_data_with_iv()
    strat = VolatilitySurfaceStrategy(asset="BTC")
    signals = strat.generate_signals(df)
    sizes = strat.calculate_position_sizes(signals)
    assert set(sizes.keys()) == {"BTC"}
    assert sizes["BTC"] in (-1.0, 0.0, 1.0)


def test_volatility_surface_backtest_runs():
    df = make_data_with_iv()
    strat = VolatilitySurfaceStrategy(asset="BTC")
    engine = BacktestEngine(initial_capital=100_000)
    result = engine.run(strat, df)
    assert "total_return" in result
    assert isinstance(result["total_return"], float)
