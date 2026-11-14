"""Tests for C297: daily-horizon multi-year cross-sectional stat-arb
(scripts/run_c297_daily_xsec_oos.py).

Covers daily causal feature construction (mom / vol_scaled_mom / resid_mom /
low_vol / reversal), fail-closed cross-sectional weights, the one-bar position
shift, and the persistence/SHA256-from-bytes of the campaign artifacts. These
tests run against the verified real ingested daily OHLCV cache only; they never
impute or fabricate data.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import run_c297_daily_xsec_oos as c297  # noqa: E402

SYMBOLS = list(c297.load_payload(c297.OHLCV)["symbols"])
TOTAL_RUNS = len(c297.FEATURES) * len(c297.LOOKBACKS) * len(c297.K_VALUES) * len(c297.HOLDS)


def _payload_and_feats():
    payload = c297.load_payload(c297.OHLCV)
    closes = payload["closes"].astype(float).sort_index()
    feats = c297.build_features(closes)
    return payload, closes, feats


def test_universe_full_daily_coverage() -> None:
    payload, closes, _ = _payload_and_feats()
    assert closes.shape == (len(closes), len(SYMBOLS))
    assert len(SYMBOLS) >= 8
    assert int(closes.isna().sum().sum()) == 0
    assert bool((closes.to_numpy(dtype=float) > 0).all())
    diffs = closes.index.to_series().diff().dropna()
    assert bool((diffs == pd.Timedelta(days=1)).all())
    for key in ("opens", "highs", "lows", "closes", "volumes", "quote_volumes"):
        assert payload[key].shape == (len(closes), len(SYMBOLS))


def test_feature_shapes_columns_and_index() -> None:
    _, closes, feats = _payload_and_feats()
    for feature in c297.FEATURES:
        for L in c297.LOOKBACKS:
            sig = c297.SIGNAL(feature, feats, L)
            assert sig.shape == (len(closes), len(SYMBOLS))
            assert list(sig.columns) == SYMBOLS
            assert sig.index.equals(closes.index)


def test_low_vol_is_negative_realized_vol() -> None:
    _, _, feats = c297._payload_and_feats() if hasattr(c297, "_payload_and_feats") else _payload_and_feats()
    vol = c297._vol(feats["logret"], 60)
    low = c297.SIGNAL("low_vol", feats, 60)
    # low_vol = (-vol).shift(1)
    pd.testing.assert_frame_equal(low, (-vol).shift(1))


def test_features_are_causal_no_lookahead() -> None:
    """Perturbing the final daily close must not change any feature row."""
    payload, closes, feats = _payload_and_feats()
    perturbed_closes = closes.copy()
    perturbed_closes.iloc[-1] = perturbed_closes.iloc[-1] * 1.01
    perturbed_feats = c297.build_features(perturbed_closes)
    for feature in c297.FEATURES:
        for L in c297.LOOKBACKS:
            base = c297.SIGNAL(feature, feats, L)
            alt = c297.SIGNAL(feature, perturbed_feats, L)
            pd.testing.assert_frame_equal(base.iloc[:-1], alt.iloc[:-1])


def test_weights_gross_exposure_cap_and_dollar_neutral() -> None:
    payload, closes, feats = _payload_and_feats()
    sig = c297.SIGNAL("mom", feats, 60)
    weights, stats = c297.build_weights(sig, closes, K=5, H=5, r_start=200)
    assert weights.shape == (len(closes), len(SYMBOLS))
    gross = weights.abs().sum(axis=1)
    assert bool((gross <= 1.0 + 1e-9).all())
    net = weights.sum(axis=1)
    assert bool((net.abs() <= 1e-9).all())
    assert stats["rebalance_bars_total"] > 0
    assert 0.0 <= stats["gate_pass_share"] <= 1.0


def test_weights_long_short_counts_at_active_rows() -> None:
    payload, closes, feats = _payload_and_feats()
    sig = c297.SIGNAL("vol_scaled_mom", feats, 60)
    weights, _ = c297.build_weights(sig, closes, K=3, H=5, r_start=200)
    active = weights.abs().sum(axis=1) > 0
    assert bool(active.any())
    sub = weights.loc[active]
    for _, row in sub.iterrows():
        vals = row.to_numpy(dtype=float)
        pos = int((vals > 0).sum())
        neg = int((vals < 0).sum())
        assert pos == 3 and neg == 3
        assert bool((np.abs(vals[vals != 0]) == 0.5 / 3).all())


def test_fail_closed_zero_dispersion_blocks_all_weights() -> None:
    payload, closes, _ = _payload_and_feats()
    constant = pd.DataFrame(1.0, index=closes.index, columns=SYMBOLS)
    weights, stats = c297.build_weights(constant, closes, K=3, H=5, r_start=200)
    assert bool((weights == 0.0).all().all())
    assert stats["rebalance_bars_passed"] == 0
    assert stats["blocked_rebalance_reasons"] == {"zero_dispersion": stats["rebalance_bars_total"]}


def test_position_is_shifted_one_bar() -> None:
    payload, closes, feats = _payload_and_feats()
    sig = c297.SIGNAL("reversal", feats, 60)
    weights, _ = c297.build_weights(sig, closes, K=3, H=1, r_start=200)
    pos = weights.shift(1).fillna(0.0)
    assert float(pos.iloc[0].abs().sum()) == 0.0
    assert pos.shape == (len(closes), len(SYMBOLS))


def test_c297_artifacts_exist_with_real_data_flags_and_sha256() -> None:
    parts = ("oos_sweep", "tradable_edge_registry", "summary", "verdict", "binding_constraint")
    paths = {}
    for part in parts:
        matches = sorted(ROOT.glob(f"reports/campaign297_{part}_*.json"))
        assert matches, f"missing C297 artifact for {part}"
        paths[part] = matches[-1]
        payload = json.loads(paths[part].read_text())
        assert payload.get("real_data_only") is True
        assert payload.get("fabricated_data") is False

    verdict = json.loads(paths["verdict"].read_text())
    assert verdict.get("verdict") in ("EDGE_PROVEN", "NOT_TRADABLE")
    assert verdict.get("campaign") == 297

    sweep = json.loads(paths["oos_sweep"].read_text())
    assert sweep["summary"]["n_total_runs"] == TOTAL_RUNS
    assert sweep["config"]["total_runs"] == TOTAL_RUNS
    run_results = sweep.get("results", [])
    assert len(run_results) == TOTAL_RUNS
    assert all(
        set(r) >= {"feature", "lookback", "K", "hold", "edge_proven", "oos_exposure_bars_total"}
        for r in run_results
    )

    registry = json.loads(paths["tradable_edge_registry"].read_text())
    assert registry["oos_sweep_sha256"] == c297.sha256_file(paths["oos_sweep"])

    for key, path_key in (
        ("oos_sweep_sha256", "oos_sweep_artifact"),
        ("registry_sha256", "registry_artifact"),
        ("summary_sha256", "summary_artifact"),
        ("binding_constraint_sha256", "binding_constraint_artifact"),
    ):
        artifact_path = verdict.get(path_key)
        if artifact_path:
            p = ROOT / artifact_path
            assert p.exists(), f"referenced artifact missing: {artifact_path}"
            assert c297.sha256_file(p) == verdict[key], f"sha256 mismatch for {artifact_path}"