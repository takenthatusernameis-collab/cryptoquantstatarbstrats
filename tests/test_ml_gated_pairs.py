from __future__ import annotations

import numpy as np
import pandas as pd

from strategies.ml_gated_pairs import MLGatedPairsStrategy
from utils.ml_gating import (
    FEATURE_NAMES,
    extract_persistence_features,
    gate_persistence,
    purged_walk_forward_indices,
    train_persistence_classifier,
)


def _synthetic_prices(n: int = 400, seed: int = 7) -> tuple[pd.Series, pd.Series]:
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2026-01-01", periods=n, freq="h", tz="UTC")
    x = 100 + np.cumsum(rng.normal(0, 0.5, n))
    # cointegrated-ish spread noise
    y = 0.5 * x + 50 + rng.normal(0, 0.3, n)
    return pd.Series(x, index=idx, name="A"), pd.Series(y, index=idx, name="B")


def test_extract_persistence_features_shape_and_causal():
    a, b = _synthetic_prices()
    feats = extract_persistence_features(a.iloc[:200], b.iloc[:200], lookback=120, min_obs=60)
    assert set(FEATURE_NAMES) == set(feats.keys())
    # same trailing window -> deterministic
    feats2 = extract_persistence_features(a.iloc[:200], b.iloc[:200], lookback=120, min_obs=60)
    assert feats["hedge_ratio"] == feats2["hedge_ratio"]


def test_purged_walk_forward_no_overlap_and_embargo():
    splits = purged_walk_forward_indices(200, train_size=60, test_size=20, step=20, embargo=10)
    assert splits
    for tr, te in splits:
        assert tr.max() < te.min()
        assert te.min() - tr.max() - 1 >= 10


def test_gate_persistence_fail_closed_no_model():
    a, b = _synthetic_prices()
    feats = extract_persistence_features(a.iloc[:200], b.iloc[:200], lookback=120, min_obs=60)
    res = gate_persistence(feats, None, threshold=0.5)
    assert res.allow is False
    assert "fail_closed" in res.reason


def test_train_persistence_classifier_insufficient_data():
    X = pd.DataFrame([{k: 0.0 for k in FEATURE_NAMES}] * 5)
    y = pd.Series([0, 1, 0, 1, 0])
    out = train_persistence_classifier(X, y, train_size=10, test_size=5, step=5, embargo=2)
    assert out["ok"] is False
    assert out["reason"] in {
        "insufficient_rows_after_dropna",
        "no_purged_splits",
        "no_valid_oos_predictions",
    }


def test_ml_gated_strategy_generates_expected_columns():
    a, b = _synthetic_prices()
    df = pd.DataFrame({"A": a, "B": b})
    strat = MLGatedPairsStrategy(pair=("A", "B"), lookback=60, ml_model=None)
    sig = strat.generate_signals(df)
    assert "A" in sig.columns and "B" in sig.columns
    assert "zscore" in sig.columns and "ml_allow" in sig.columns
    # no model => fail-closed, no entries expected
    assert float(sig["A"].abs().sum() + sig["B"].abs().sum()) == 0.0
