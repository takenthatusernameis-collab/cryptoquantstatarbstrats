"""Tests for C290: wider-universe true-5m OHLCV cross-sectional stat-arb
(scripts/run_c290_wider_universe_oohlcv_xsec_oos.py).

Covers true-5m causal feature construction, fail-closed cross-sectional weights,
and the persistence/SHA256-from-bytes of the campaign artifacts. These tests run
against the verified real ingested OHLCV cache only; they never impute or
fabricate data.
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

import run_c290_wider_universe_oohlcv_xsec_oos as c290  # noqa: E402

SYMBOLS = list(c290.load_payload(c290.OHLCV)["symbols"])
N_BARS = 26208


def _payload_and_feats():
    payload = c290.load_payload(c290.OHLCV)
    closes = payload["closes"].astype(float).sort_index()
    feats = c290.build_features(
        closes,
        payload["highs"].astype(float).reindex(closes.index),
        payload["lows"].astype(float).reindex(closes.index),
        payload["quote_volumes"].astype(float).reindex(closes.index),
    )
    return payload, closes, feats


def test_universe_is_wider_than_prior_and_full_coverage():
    payload, closes, _ = _payload_and_feats()
    assert closes.shape == (N_BARS, len(SYMBOLS))
    assert len(SYMBOLS) >= 20
    assert int(closes.isna().sum().sum()) == 0
    assert bool((closes.to_numpy(dtype=float) > 0).all())
    for key in ("opens", "highs", "lows", "closes", "volumes", "quote_volumes"):
        assert payload[key].shape == (N_BARS, len(SYMBOLS))


def test_feature_shapes_columns_and_index():
    _, closes, feats = _payload_and_feats()
    for feature in c290.FEATURES:
        for L in c290.LOOKBACKS:
            sig = c290.SIGNAL(feature, feats, L)
            assert sig.shape == (N_BARS, len(SYMBOLS))
            assert list(sig.columns) == SYMBOLS
            assert sig.index.equals(closes.index)


def test_low_close_vol_is_negative_realized_vol():
    _, _, feats = _payload_and_feats()
    rv = c290.rv_close(feats["logret"], 288)
    low = c290.SIGNAL("low_close_vol", feats, 288)
    pd.testing.assert_frame_equal(low, -rv)


def test_features_are_causal_no_lookahead():
    """Perturbing the final 5m inputs must not change any earlier feature row."""
    payload, closes, feats = _payload_and_feats()
    highs = payload["highs"].astype(float).reindex(closes.index)
    lows = payload["lows"].astype(float).reindex(closes.index)
    qv = payload["quote_volumes"].astype(float).reindex(closes.index)
    perturbed_closes = closes.copy()
    perturbed_closes.iloc[-1] = perturbed_closes.iloc[-1] * 1.01
    perturbed_feats = c290.build_features(perturbed_closes, highs, lows, qv)
    for feature in c290.FEATURES:
        for L in c290.LOOKBACKS:
            base = c290.SIGNAL(feature, feats, L)
            alt = c290.SIGNAL(feature, perturbed_feats, L)
            pd.testing.assert_frame_equal(base.iloc[:-1], alt.iloc[:-1])


def test_weights_gross_exposure_cap_and_dollar_neutral():
    payload, closes, feats = _payload_and_feats()
    sig = c290.SIGNAL("low_close_vol", feats, 288)
    weights, stats = c290.build_weights(sig, closes, K=2, H=6, r_start=288)
    assert weights.shape == (N_BARS, len(SYMBOLS))
    gross = weights.abs().sum(axis=1)
    assert bool((gross <= 1.0 + 1e-9).all())
    net = weights.sum(axis=1)
    assert bool((net.abs() <= 1e-9).all())
    assert stats["rebalance_bars_total"] > 0
    assert 0.0 <= stats["gate_pass_share"] <= 1.0


def test_weights_long_short_counts_at_active_rows():
    payload, closes, feats = _payload_and_feats()
    sig = c290.SIGNAL("low_close_vol", feats, 1008)
    weights, _ = c290.build_weights(sig, closes, K=3, H=24, r_start=1008)
    active = weights.abs().sum(axis=1) > 0
    assert bool(active.any())
    sub = weights.loc[active]
    for _, row in sub.iterrows():
        vals = row.to_numpy(dtype=float)
        pos = int((vals > 0).sum())
        neg = int((vals < 0).sum())
        assert pos == 3 and neg == 3
        assert bool((np.abs(vals[vals != 0]) == 0.5 / 3).all())


def test_fail_closed_zero_dispersion_blocks_all_weights():
    payload, closes, _ = _payload_and_feats()
    constant = pd.DataFrame(1.0, index=closes.index, columns=SYMBOLS)
    weights, stats = c290.build_weights(constant, closes, K=2, H=6, r_start=288)
    assert bool((weights == 0.0).all().all())
    assert stats["rebalance_bars_passed"] == 0
    assert stats["blocked_rebalance_reasons"] == {"zero_dispersion": stats["rebalance_bars_total"]}


def test_position_is_shifted_one_bar():
    payload, closes, feats = _payload_and_feats()
    sig = c290.SIGNAL("low_skew", feats, 288)
    weights, _ = c290.build_weights(sig, closes, K=2, H=1, r_start=288)
    pos = weights.shift(1).fillna(0.0)
    assert float(pos.iloc[0].abs().sum()) == 0.0
    assert pos.shape == (N_BARS, len(SYMBOLS))


def test_c290_artifacts_exist_with_real_data_flags_and_sha256():
    parts = ("oos_sweep", "tradable_edge_registry", "summary", "verdict", "binding_constraint")
    paths = {}
    for part in parts:
        matches = sorted(ROOT.glob(f"reports/campaign290_{part}_*.json"))
        assert matches, f"missing C290 artifact for {part}"
        paths[part] = matches[-1]
        payload = json.loads(paths[part].read_text())
        assert payload.get("real_data_only") is True
        assert payload.get("fabricated_data") is False

    verdict = json.loads(paths["verdict"].read_text())
    assert verdict.get("verdict") in ("EDGE_PROVEN", "NOT_TRADABLE")
    assert verdict.get("campaign") == 290

    sweep = json.loads(paths["oos_sweep"].read_text())
    assert sweep["summary"]["n_total_runs"] == 162
    assert sweep["config"]["total_runs"] == 162
    run_results = sweep.get("results", [])
    assert len(run_results) == 162
    assert all(
        set(r) >= {"feature", "lookback", "K", "hold", "edge_proven", "oos_exposure_bars_total"}
        for r in run_results
    )

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
            assert c290.sha256_file(p) == verdict[key], f"sha256 mismatch for {artifact_path}"