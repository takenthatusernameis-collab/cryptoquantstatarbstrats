"""
Tests for TermStructureStrategy.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from backtest.engine import BacktestEngine
from strategies.term_structure import TermStructureStrategy


def make_term_structure_data(n: int = 200, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2024-01-01", periods=n, freq="1h")
    r = rng.normal(0.0, 0.01, n)
    price = 100 * np.exp(np.cumsum(r))
    # Near-term IV oscillates faster; far-term IV is smoother -> spread varies.
    t = np.arange(n, dtype=float)
    iv_30d = 0.3 + 0.05 * np.sin(t / 5.0) + rng.normal(0, 0.01, n)
    iv_90d = 0.3 + 0.02 * np.sin(t / 12.0) + rng.normal(0, 0.005, n)
    iv_30d = np.clip(iv_30d, 0.1, 0.9)
    iv_90d = np.clip(iv_90d, 0.1, 0.9)
    return pd.DataFrame(
        {
            "BTC": price,
            "iv_30d": iv_30d,
            "iv_90d": iv_90d,
        },
        index=dates,
    )


def test_term_structure_generate_signals():
    df = make_term_structure_data()
    strat = TermStructureStrategy(asset="BTC")
    signals = strat.generate_signals(df)
    assert "spread" in signals.columns
    assert "spread_mean" in signals.columns
    assert "spread_std" in signals.columns
    assert "spread_zscore" in signals.columns
    assert "long_spread" in signals.columns
    assert "short_spread" in signals.columns
    assert "exit" in signals.columns
    assert "BTC" in signals.columns
    assert len(signals) == len(df)


def test_term_structure_position_sizes():
    df = make_term_structure_data()
    strat = TermStructureStrategy(asset="BTC")
    signals = strat.generate_signals(df)
    sizes = strat.calculate_position_sizes(signals)
    assert set(sizes.keys()) == {"BTC"}
    assert sizes["BTC"] in (-1.0, 0.0, 1.0)


def test_term_structure_backtest_runs():
    df = make_term_structure_data()
    strat = TermStructureStrategy(asset="BTC")
    engine = BacktestEngine(initial_capital=100_000)
    result = engine.run(strat, df)
    assert "total_return" in result
    assert isinstance(result["total_return"], float)
    assert "BTC" in result["weights"].columns


def test_term_structure_missing_columns_raises():
    df = pd.DataFrame(
        {"BTC": [100.0, 101.0, 102.0]},
        index=pd.date_range("2024-01-01", periods=3, freq="1h"),
    )
    strat = TermStructureStrategy(asset="BTC")
    try:
        strat.generate_signals(df)
    except ValueError as exc:
        assert "implied-volatility" in str(exc).lower() or "iv" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError when IV columns are missing")


def test_term_structure_custom_tenors():
    df = make_term_structure_data()
    df = df.rename(columns={"iv_30d": "iv_1m", "iv_90d": "iv_3m"})
    strat = TermStructureStrategy(
        asset="BTC", near_tenor="iv_1m", far_tenor="iv_3m"
    )
    signals = strat.generate_signals(df)
    assert "spread_zscore" in signals.columns
    assert "BTC" in signals.columns
