from __future__ import annotations

import numpy as np
import pandas as pd

from backtest.engine import BacktestEngine
from strategies.mean_reversion import MeanReversionStrategy


def _make_data(n=120, seed=1):
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2024-01-01", periods=n, freq="h")
    rets = rng.normal(0, 0.01, size=(n, 2))
    prices = 100 * np.exp(np.cumsum(rets, axis=0))
    return pd.DataFrame(prices, index=dates, columns=["BTC", "ETH"])


def _make_flat_data(n=120):
    dates = pd.date_range("2024-01-01", periods=n, freq="h")
    return pd.DataFrame({"BTC": 100.0, "ETH": 200.0}, index=dates)


def _make_trending_data(n=120):
    dates = pd.date_range("2024-01-01", periods=n, freq="h")
    t = np.arange(n, dtype=float)
    return pd.DataFrame(
        {"BTC": 100 + 0.5 * t, "ETH": 200 + 1.0 * t}, index=dates
    )


def _make_vol_split_data(n=200):
    """Low volatility first half, high volatility second half."""
    dates = pd.date_range("2024-01-01", periods=n, freq="h")
    rng = np.random.default_rng(7)
    rets = np.zeros((n, 2))
    rets[: n // 2] = rng.normal(0, 0.0001, size=(n // 2, 2))
    rets[n // 2 :] = rng.normal(0, 0.05, size=(n // 2, 2))
    prices = 100 * np.exp(np.cumsum(rets, axis=0))
    return pd.DataFrame(prices, index=dates, columns=["BTC", "ETH"])


def test_regime_disabled_is_noop():
    """No regime params -> unchanged results (backward compatible)."""
    engine = BacktestEngine(initial_capital=100_000.0)
    data = _make_data()
    strategy = MeanReversionStrategy(asset="BTC")
    result = engine.run(strategy, data)
    assert "total_return" in result
    assert result["weights"].abs().sum().sum() > 0


def test_regime_signal_bool_series_gates_weights():
    """Boolean Series regime_signal zeroes weights where False."""
    engine = BacktestEngine(initial_capital=100_000.0)
    data = _make_data()
    strategy = MeanReversionStrategy(asset="BTC")
    baseline = engine.run(strategy, data)["weights"]

    regime_signal = pd.Series(True, index=data.index)
    regime_signal.iloc[len(data) // 2 :] = False

    result = engine.run(strategy, data, regime_signal=regime_signal)
    gated = result["weights"]

    split = len(data) // 2
    pd.testing.assert_frame_equal(baseline.iloc[:split], gated.iloc[:split])
    assert (gated.iloc[split:] == 0.0).all().all()


def test_regime_signal_scalar_false_zeroes_all():
    """Scalar False regime_signal zeroes every weight."""
    engine = BacktestEngine(initial_capital=100_000.0)
    data = _make_data()
    strategy = MeanReversionStrategy(asset="BTC")
    result = engine.run(strategy, data, regime_signal=False)
    assert (result["weights"] == 0.0).all().all()
    assert result["total_return"] == 0.0


def test_regime_signal_dataframe_gates_weights():
    """DataFrame regime_signal gates via any(axis=1) mask."""
    engine = BacktestEngine(initial_capital=100_000.0)
    data = _make_data()
    strategy = MeanReversionStrategy(asset="BTC")
    baseline = engine.run(strategy, data)["weights"]

    regime_signal = pd.DataFrame(
        {"BTC": True, "ETH": True}, index=data.index
    )
    regime_signal.iloc[len(data) // 2 :, :] = False

    result = engine.run(strategy, data, regime_signal=regime_signal)
    gated = result["weights"]

    split = len(data) // 2
    pd.testing.assert_frame_equal(baseline.iloc[:split], gated.iloc[:split])
    assert (gated.iloc[split:] == 0.0).all().all()


def test_regime_mode_trend_flat_data_zeroes_weights():
    """regime_mode='trend' on flat (no-trend) data zeroes pre-computed weights."""
    engine = BacktestEngine(initial_capital=100_000.0)
    data = _make_flat_data()
    weights = pd.DataFrame(1.0, index=data.index, columns=data.columns)
    result = engine.run_portfolio(weights, data, regime_mode="trend", regime_lookback=10)
    assert (result["weights"] == 0.0).all().all()


def test_regime_mode_trend_trending_data_preserves_weights():
    """regime_mode='trend' on trending data preserves pre-computed weights."""
    engine = BacktestEngine(initial_capital=100_000.0)
    data = _make_trending_data()
    weights = pd.DataFrame(1.0, index=data.index, columns=data.columns)
    result = engine.run_portfolio(weights, data, regime_mode="trend", regime_lookback=10)
    gated = result["weights"]
    # Trending data has trend != 0 after warmup -> weights preserved after warmup
    assert gated.iloc[20:].abs().sum().sum() > 0


def test_run_portfolio_regime_signal():
    """run_portfolio with regime_signal gates pre-computed weights."""
    engine = BacktestEngine(initial_capital=100_000.0)
    data = _make_data()
    weights = pd.DataFrame(1.0, index=data.index, columns=data.columns)

    result = engine.run_portfolio(weights, data)
    assert (result["weights"] == 1.0).all().all()

    regime_signal = pd.Series(False, index=data.index)
    result_gated = engine.run_portfolio(weights, data, regime_signal=regime_signal)
    assert (result_gated["weights"] == 0.0).all().all()
    assert result_gated["total_return"] == 0.0


def test_walk_forward_regime_mode():
    """walk_forward with regime_mode runs end-to-end."""
    engine = BacktestEngine(initial_capital=100_000.0)
    data = _make_data(n=200)
    strategy = MeanReversionStrategy(asset="BTC")
    result = engine.walk_forward(
        strategy,
        data,
        train_period=60,
        test_period=20,
        regime_mode="trend",
        regime_lookback=10,
    )
    assert "returns" in result
    assert "results" in result
    assert len(result["returns"]) > 0


def test_walk_forward_portfolio_regime_signal():
    """walk_forward_portfolio with regime_signal runs end-to-end."""
    engine = BacktestEngine(initial_capital=100_000.0)
    data = _make_data(n=200)
    weights = pd.DataFrame(1.0, index=data.index, columns=data.columns)
    regime_signal = pd.Series(True, index=data.index)
    result = engine.walk_forward_portfolio(
        weights,
        data,
        train_period=60,
        test_period=20,
        regime_signal=regime_signal,
    )
    assert "returns" in result
    assert "results" in result


def test_regime_backward_compatibility_defaults():
    """Calling run with explicit None regime args matches legacy behavior."""
    engine = BacktestEngine(initial_capital=100_000.0)
    data = _make_data()
    strategy = MeanReversionStrategy(asset="BTC")
    r1 = engine.run(strategy, data)
    r2 = engine.run(
        strategy,
        data,
        regime_signal=None,
        regime_mode=None,
        regime_lookback=None,
    )
    pd.testing.assert_frame_equal(r1["weights"], r2["weights"])
    assert r1["total_return"] == r2["total_return"]


def test_regime_vol_mode_low_vol_gates_weights():
    """regime_vol_mode='low_vol' reduces weights in high-volatility periods."""
    engine = BacktestEngine(initial_capital=100_000.0)
    data = _make_vol_split_data()
    weights = pd.DataFrame(1.0, index=data.index, columns=data.columns)

    result_full = engine.run_portfolio(weights, data)
    assert (result_full["weights"] == 1.0).all().all()

    result_gated = engine.run_portfolio(
        weights, data, regime_vol_mode="low_vol", regime_lookback=10
    )
    gated = result_gated["weights"]
    split = len(data) // 2
    low_vol_weight = gated.iloc[:split].abs().sum().sum()
    high_vol_weight = gated.iloc[split:].abs().sum().sum()
    assert low_vol_weight > 0.0
    assert high_vol_weight < low_vol_weight


def test_regime_vol_mode_combined_with_trend():
    """regime_vol_mode='low_vol' combined with regime_mode='trend' runs end-to-end."""
    engine = BacktestEngine(initial_capital=100_000.0)
    data = _make_vol_split_data()
    weights = pd.DataFrame(1.0, index=data.index, columns=data.columns)

    result = engine.run_portfolio(
        weights,
        data,
        regime_mode="trend",
        regime_vol_mode="low_vol",
        regime_lookback=10,
    )
    assert "total_return" in result
    assert (result["weights"] <= 1.0).all().all()
    assert (result["weights"] >= -1.0).all().all()


def test_regime_vol_mode_none_backward_compatible():
    """regime_vol_mode=None matches no regime params (backward compatible)."""
    engine = BacktestEngine(initial_capital=100_000.0)
    data = _make_vol_split_data()
    strategy = MeanReversionStrategy(asset="BTC")
    r1 = engine.run(strategy, data)
    r2 = engine.run(
        strategy,
        data,
        regime_signal=None,
        regime_mode=None,
        regime_lookback=None,
        regime_vol_mode=None,
    )
    pd.testing.assert_frame_equal(r1["weights"], r2["weights"])
    assert r1["total_return"] == r2["total_return"]
