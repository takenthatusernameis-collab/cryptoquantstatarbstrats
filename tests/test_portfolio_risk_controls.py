"""Network-independent unit tests for portfolio risk controls and meta-selector.

These tests cover the logic that lives inside ``examples/run_portfolio_real.py``
(``PortfolioRiskController`` and ``regime_adaptive_meta_selector``) which had no
direct unit-test coverage. They are deliberately network-independent: they use
synthetic DataFrames so the campaign can keep expanding without depending on
Binance reachability.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from examples.run_portfolio_real import (
    PortfolioRiskController,
    regime_adaptive_meta_selector,
)


def _prices(n: int = 60, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2026-01-01", periods=n, freq="h")
    cols = ["BTC", "ETH", "SOL"]
    data = 100.0 * np.cumprod(1.0 + rng.normal(0.0, 0.01, size=(n, len(cols))), axis=0)
    return pd.DataFrame(data, index=idx, columns=cols)


def test_per_pair_cap_is_enforced():
    data = _prices()
    w = pd.DataFrame(0.0, index=data.index, columns=data.columns)
    w["BTC"] = 0.9
    w["ETH"] = 0.9
    pair_map = {"BTC/ETH": ["BTC", "ETH"]}
    ctrl = PortfolioRiskController(max_gross_exposure=10.0, per_pair_cap=0.32)
    out = ctrl.apply(w, pair_map=pair_map)
    pair_abs = out[["BTC", "ETH"]].abs().sum(axis=1)
    assert (pair_abs <= 0.32 + 1e-9).all()


def test_max_gross_exposure_is_enforced():
    data = _prices()
    w = pd.DataFrame(0.0, index=data.index, columns=data.columns)
    w["BTC"] = 2.0
    w["ETH"] = 2.0
    ctrl = PortfolioRiskController(max_gross_exposure=1.4, per_pair_cap=10.0)
    out = ctrl.apply(w)
    gross = out.abs().sum(axis=1)
    assert (gross <= 1.4 + 1e-9).all()


def test_max_correlation_exposure_is_enforced():
    data = _prices()
    w = pd.DataFrame(0.0, index=data.index, columns=data.columns)
    w["BTC"] = 2.0
    w["ETH"] = 0.0
    w["SOL"] = 0.0
    ctrl = PortfolioRiskController(
        max_gross_exposure=10.0, per_pair_cap=10.0, max_correlation_exposure=0.5
    )
    out = ctrl.apply(w)
    asset_abs = out.abs()
    assert (asset_abs.max() <= 0.5 + 1e-9).all()


def test_max_correlation_exposure_disabled_when_zero():
    data = _prices()
    w = pd.DataFrame(0.0, index=data.index, columns=data.columns)
    w["BTC"] = 2.0
    ctrl = PortfolioRiskController(
        max_gross_exposure=10.0, per_pair_cap=10.0, max_correlation_exposure=0.0
    )
    out = ctrl.apply(w)
    assert float(out["BTC"].abs().max()) > 1.0


def test_max_cvar_allocation_reduces_weights_when_breached():
    data = _prices()
    w = pd.DataFrame(0.0, index=data.index, columns=data.columns)
    w["BTC"] = 5.0
    ctrl = PortfolioRiskController(
        max_gross_exposure=10.0,
        per_pair_cap=10.0,
        max_correlation_exposure=0.0,
        max_cvar_allocation=1e-4,
    )
    out = ctrl.apply(w, returns=data)
    # CVaR cap should have scaled the single-asset weight down.
    assert float(out["BTC"].abs().max()) < 5.0


def test_max_cvar_allocation_no_op_when_within_cap():
    data = _prices()
    w = pd.DataFrame(0.0, index=data.index, columns=data.columns)
    w["BTC"] = 0.01
    ctrl = PortfolioRiskController(
        max_gross_exposure=10.0,
        per_pair_cap=10.0,
        max_correlation_exposure=0.0,
        max_cvar_allocation=1.0,
    )
    out = ctrl.apply(w, returns=data)
    assert float(out["BTC"].abs().max()) == pytest.approx(0.01)


def test_regime_adaptive_meta_selector_de_risks_in_high_vol():
    data = _prices(n=120)
    # Two strategies with identical weights; high-vol bars should be scaled down.
    w = pd.DataFrame(0.5, index=data.index, columns=["BTC", "ETH"])
    combined = regime_adaptive_meta_selector({"s1": w, "s2": w}, data)
    # Each strategy is normalized to unit gross (0.5+0.5=1.0 -> unchanged),
    # then summed and rescaled to target gross = 1.0. With two active
    # strategies the base weight per asset is 0.5 before regime adjustment.
    base = 0.5
    regimes = regime_adaptive_meta_selector.__globals__["detect_regimes"](data)
    vol_col = next(c for c in regimes.columns if c.startswith("BTC") and c.endswith("_vol_regime"))
    next(c for c in regimes.columns if c.startswith("BTC") and c.endswith("_trend"))
    high_vol = regimes[vol_col].max()
    mask_high = regimes[vol_col] == high_vol
    if mask_high.any():
        scaled = combined.loc[mask_high, "BTC"].mean()
        assert scaled < base
        # Non-high-vol bars carry only trend scaling (downtrend 0.6 / uptrend 1.1),
        # so their mean is bounded strictly below the base weight.
        non_high = combined.loc[~mask_high, "BTC"].mean()
        assert non_high <= base + 1e-12


def test_regime_adaptive_meta_selector_preserves_signal_magnitude():
    data = _prices(n=120)
    w = pd.DataFrame(0.5, index=data.index, columns=["BTC", "ETH"])
    combined = regime_adaptive_meta_selector({"s1": w}, data)
    # Single strategy: normalized gross = 1.0, rescaled to target gross = 1.0,
    # so base weight per asset is 0.5 before regime adjustment. The invariant
    # is that the book does NOT collapse to ~1/n strategies: gross exposure
    # stays near the target (1.0) rather than falling to ~0.
    gross = combined.abs().sum(axis=1)
    assert gross.max() >= 0.5
    assert gross.mean() > 0.1
    # Unadjusted bars (neither high-vol nor trend) keep weight 0.5.
    regimes = regime_adaptive_meta_selector.__globals__["detect_regimes"](data)
    vol_col = next(c for c in regimes.columns if c.startswith("BTC") and c.endswith("_vol_regime"))
    trend_col = next(c for c in regimes.columns if c.startswith("BTC") and c.endswith("_trend"))
    high_vol = regimes[vol_col].max()
    unadjusted = (regimes[vol_col] != high_vol) & (regimes[trend_col] == 0)
    if unadjusted.any():
        assert combined.loc[unadjusted, "BTC"].abs().max() == pytest.approx(0.5, abs=1e-9)


def test_regime_adaptive_meta_selector_empty_input_returns_zeros():
    data = _prices()
    combined = regime_adaptive_meta_selector({}, data)
    assert combined.shape[0] == len(data)
    assert (combined == 0.0).all().all()


def test_regime_adaptive_meta_selector_downtrend_de_risk():
    data = _prices(n=120)
    w = pd.DataFrame(0.5, index=data.index, columns=["BTC", "ETH"])
    combined = regime_adaptive_meta_selector({"s1": w}, data)
    regimes = regime_adaptive_meta_selector.__globals__["detect_regimes"](data)
    trend_col = next(c for c in regimes.columns if c.startswith("BTC") and c.endswith("_trend"))
    mask_down = regimes[trend_col] == -1
    if mask_down.any():
        base = 0.5
        scaled = combined.loc[mask_down, "BTC"].mean()
        assert scaled <= base + 1e-12
