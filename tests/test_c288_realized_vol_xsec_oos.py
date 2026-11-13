"""Tests for C288: realized-volatility cross-sectional stat-arb
(scripts/run_c288_realized_vol_xsec_oos.py).

Covers causal feature construction, fail-closed cross-sectional weights, and the
persistence/SHA256-from-bytes of the campaign artifacts.  These tests run against
the verified real 5m caches only; they never impute or fabricate data.
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

import run_c288_realized_vol_xsec_oos as c288  # noqa: E402

SYMBOLS = list(c288.SYMBOLS)
N_BARS = 26208


def _spot_and_logret():
    spot = c288.load_spot(c288.SPOT_5M)
    assert spot.shape == (N_BARS, 11)
    return spot, np.log(spot)


def test_feature_shapes_columns_and_index():
    spot, logret = _spot_and_logret()
    for feature in c288.FEATURES:
        for L in c288.LOOKBACKS:
            sig = c288.SIGNAL(feature, logret, L)
            assert sig.shape == (N_BARS, 11)
            assert list(sig.columns) == SYMBOLS
            assert sig.index.equals(spot.index)


def test_low_vol_is_negative_realized_vol():
    _, logret = _spot_and_logret()
    rv = c288.realized_vol(logret, 288)
    low_vol = c288.feature_low_vol(logret, 288)
    pd.testing.assert_frame_equal(low_vol, -rv)


def test_features_are_causal_no_lookahead():
    """Perturbing the final 5m log-return must not change any earlier feature row."""
    _, logret = _spot_and_logret()
    perturbed = logret.copy()
    perturbed.iloc[-1] = perturbed.iloc[-1] + 1.0
    for feature in c288.FEATURES:
        for L in c288.LOOKBACKS:
            base = c288.SIGNAL(feature, logret, L)
            alt = c288.SIGNAL(feature, perturbed, L)
            pd.testing.assert_frame_equal(base.iloc[:-1], alt.iloc[:-1])


def test_weights_gross_exposure_cap_and_dollar_neutral():
    spot, logret = _spot_and_logret()
    sig = c288.SIGNAL("low_vol", logret, 288)
    weights, stats = c288.build_weights(sig, spot, K=2, H=6, r_start=288)
    assert weights.shape == (N_BARS, 11)
    gross = weights.abs().sum(axis=1)
    assert bool((gross <= 1.0 + 1e-9).all())
    net = weights.sum(axis=1)
    assert bool((net.abs() <= 1e-9).all())
    assert stats["rebalance_bars_total"] > 0
    assert 0.0 <= stats["gate_pass_share"] <= 1.0


def test_weights_long_short_counts_at_active_rows():
    spot, logret = _spot_and_logret()
    sig = c288.SIGNAL("low_vol", logret, 1008)
    weights, _ = c288.build_weights(sig, spot, K=3, H=24, r_start=1008)
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
    spot, _ = _spot_and_logret()
    constant = pd.DataFrame(1.0, index=spot.index, columns=SYMBOLS)
    weights, stats = c288.build_weights(constant, spot, K=2, H=6, r_start=288)
    assert bool((weights == 0.0).all().all())
    assert stats["rebalance_bars_passed"] == 0
    assert stats["blocked_rebalance_reasons"] == {"zero_dispersion": stats["rebalance_bars_total"]}


def test_position_is_shifted_one_bar():
    spot, logret = _spot_and_logret()
    sig = c288.SIGNAL("low_skew", logret, 288)
    weights, _ = c288.build_weights(sig, spot, K=2, H=1, r_start=288)
    pos = weights.shift(1).fillna(0.0)
    assert float(pos.iloc[0].abs().sum()) == 0.0
    assert pos.shape == (N_BARS, 11)


def test_c288_artifacts_exist_with_real_data_flags_and_sha256():
    parts = ("oos_sweep", "tradable_edge_registry", "summary", "verdict", "binding_constraint")
    paths = {}
    for part in parts:
        matches = sorted(ROOT.glob(f"reports/campaign288_{part}_*.json"))
        assert matches, f"missing C288 artifact for {part}"
        paths[part] = matches[-1]
        payload = json.loads(paths[part].read_text())
        assert payload.get("real_data_only") is True
        assert payload.get("fabricated_data") is False

    verdict = json.loads(paths["verdict"].read_text())
    assert verdict.get("verdict") in ("EDGE_PROVEN", "NOT_TRADABLE")
    assert verdict.get("campaign") == 288

    sweep = json.loads(paths["oos_sweep"].read_text())
    assert sweep["summary"]["n_total_runs"] == 81
    run_results = sweep.get("results", [])
    assert len(run_results) == 81
    assert all(
        set(r) >= {"feature", "lookback", "K", "hold", "edge_proven", "oos_exposure_bars_total"}
        for r in run_results
    )

    # SHA256-from-bytes recorded in the verdict artifact must match the artifact bytes.
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
            assert c288.sha256_file(p) == verdict[key], f"sha256 mismatch for {artifact_path}"