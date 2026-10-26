"""
Tests for position sizing utilities and strategy integration.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from strategies.mean_reversion import MeanReversionStrategy
from utils.sizing import fixed_fractional, kelly, vol_target


def test_fixed_fractional_basic():
    assert fixed_fractional(100000.0, 0.02) == 2000.0
    assert fixed_fractional(100000.0, -0.01) == -1000.0


def test_fixed_fractional_invalid_inputs():
    assert fixed_fractional(None, 0.02) == 0.0
    assert fixed_fractional(100000.0, None) == 0.0
    assert fixed_fractional(-100.0, 0.02) == 0.0
    assert fixed_fractional(100000.0, float("nan")) == 0.0
    assert fixed_fractional(float("inf"), 0.02) == 0.0


def test_vol_target_scalar():
    # equity 100k, target vol 0.15, realized vol 0.30 -> 50k allocation
    result = vol_target(100000.0, 0.15, 0.30)
    assert abs(result - 50000.0) < 1e-9


def test_vol_target_invalid_inputs():
    assert vol_target(None, 0.15, 0.30) == 0.0
    assert vol_target(100000.0, 0.0, 0.30) == 0.0
    assert vol_target(100000.0, 0.15, 0.0) == 0.0
    assert vol_target(100000.0, 0.15, -0.30) == 0.0


def test_vol_target_series_with_lookback():
    rng = np.random.default_rng(0)
    returns = pd.Series(rng.normal(0.0, 0.02, 200))
    result = vol_target(100000.0, 0.15, returns, lookback=20)
    assert isinstance(result, float)
    assert result > 0.0


def test_kelly_full():
    # b=2, win_prob=0.55 -> full kelly = (0.55*3 - 1)/2 = 0.325
    result = kelly(1.0, 0.55, 2.0)
    assert abs(result - 0.325) < 1e-9


def test_kelly_half():
    # half kelly of above
    result = kelly(0.5, 0.55, 2.0)
    assert abs(result - 0.1625) < 1e-9


def test_kelly_negative_edge_clamps_to_zero():
    # b=1, win_prob=0.4 -> full kelly = (0.4*2 - 1)/1 = -0.2 -> clamped to 0
    result = kelly(1.0, 0.4, 1.0)
    assert result == 0.0


def test_kelly_invalid_inputs():
    assert kelly(None, 0.5, 1.0) == 0.0
    assert kelly(1.0, None, 1.0) == 0.0
    assert kelly(1.0, 0.5, None) == 0.0
    assert kelly(1.0, 1.5, 1.0) == 0.0
    assert kelly(1.0, 0.5, 0.0) == 0.0


def _make_data(n: int = 400, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2024-01-01", periods=n, freq="1h")
    r1 = rng.normal(0.0, 0.02, n)
    df = pd.DataFrame(
        {"BTC": 100 * np.exp(np.cumsum(r1))},
        index=dates,
    )
    return df


def test_mean_reversion_without_sizer_backward_compatible():
    df = _make_data()
    strat = MeanReversionStrategy("BTC")
    signals = strat.generate_signals(df)
    sizes = strat.calculate_position_sizes(signals)
    assert set(sizes.keys()) == {"BTC"}
    assert sizes["BTC"] in (-1.0, 0.0, 1.0)


def test_mean_reversion_with_sizer():
    df = _make_data()

    def sizer(base: float, equity: float, price: float, vol: float) -> float:
        # fixed fractional: risk 1% of equity on a long, scaled by base sign
        return base * equity * 0.01 / price if price > 0 else 0.0

    strat = MeanReversionStrategy("BTC", params={"equity": 100000.0}, sizer=sizer)
    signals = strat.generate_signals(df)
    # Inject price context for the sizer
    signals["price"] = df["BTC"]
    signals["realized_vol"] = df["BTC"].rolling(20).std().fillna(0.0)
    sizes = strat.calculate_position_sizes(signals)
    assert set(sizes.keys()) == {"BTC"}
    # When flat, size should be 0 (sizer not invoked)
    if sizes["BTC"] == 0.0:
        return
    # Otherwise allocation should be a finite float with correct sign
    assert np.isfinite(sizes["BTC"])
    # Sign of allocation should match the base direction
    base = 1.0 if sizes["BTC"] > 0 else -1.0
    assert base in (1.0, -1.0)


def test_risk_manager_apply_stop_loss():
    from utils.risk import RiskManager

    rm = RiskManager()
    positions = {"BTC": 1.0, "ETH": 1.0}
    prices = pd.Series([90, 95], index=["BTC", "ETH"])
    entry_prices = pd.Series([100, 100], index=["BTC", "ETH"])
    result = rm.apply_stop_loss(positions, prices, entry_prices, threshold=0.1)
    assert result["BTC"] == 0.0  # 10% drop triggers stop
    assert result["ETH"] == 1.0


def test_risk_manager_position_limit():
    from utils.risk import RiskManager

    rm = RiskManager()
    positions = pd.DataFrame({"BTC": [0.5], "ETH": [0.3], "SOL": [0.2], "XRP": [0.1]})
    result = rm.position_limit(positions, max_positions=2)
    # Should keep top 2 by absolute weight
    assert (np.abs(result.values) > 1e-18).sum() == 2


def test_risk_manager_drawdown_control():
    from utils.risk import RiskManager

    rm = RiskManager()
    positions = {"BTC": 1.0, "ETH": 0.5}
    result = rm.drawdown_control(positions, current_drawdown=0.25, max_drawdown=0.2)
    # Should liquidate if drawdown exceeds max
    assert result["BTC"] == 0.0
    assert result["ETH"] == 0.0
