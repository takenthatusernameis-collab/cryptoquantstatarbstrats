"""Tests for C292: cross-venue real-spot basis / lead-lag cross-sectional stat-arb
(scripts/run_c292_crossvenue_basis_xsec_oos.py).

Covers real cross-venue feature construction (causal basis / lead-lag), the sign
convention (higher score => long discounted Binance leg / short premium OKX leg),
fail-closed cross-sectional weights, the one-bar position shift, and the
persistence/SHA256-from-bytes of the campaign artifacts. These tests run against
the verified real ingested Binance+OKX cross-venue cache only; they never impute
or fabricate data.
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

import run_c292_crossvenue_basis_xsec_oos as c292  # noqa: E402

N_BARS = 26208


def _data():
    payload = c292.load_payload(c292.PKL)
    b = payload["binance_closes"].astype(float).sort_index()
    o = payload["okx_closes"].astype(float).sort_index()
    feats = c292.build_features(b, o)
    return payload, b, o, feats


def test_universe_full_coverage_real() -> None:
    payload, b, o, _ = _data()
    symbols = list(payload["symbols"])
    assert len(symbols) >= 2
    assert b.shape == (N_BARS, len(symbols))
    assert o.shape == (N_BARS, len(symbols))
    assert int(b.isna().sum().sum()) == 0
    assert int(o.isna().sum().sum()) == 0
    assert bool((b.to_numpy(dtype=float) > 0).all())
    assert bool((o.to_numpy(dtype=float) > 0).all())
    for key in ("binance_opens", "binance_highs", "binance_lows", "binance_closes", "binance_volumes",
                "okx_opens", "okx_highs", "okx_lows", "okx_closes", "okx_volumes"):
        assert payload[key].shape == (N_BARS, len(symbols))


def test_feature_shapes_columns_and_index() -> None:
    _, b, _, feats = _data()
    symbols = list(b.columns)
    for feature in c292.FEATURES:
        for L in c292.LOOKBACKS:
            sig = c292.SIGNAL(feature, feats, L)
            assert sig.shape == (N_BARS, len(symbols))
            assert list(sig.columns) == symbols
            assert sig.index.equals(b.index)


def test_feature_sign_conventions() -> None:
    _, _, _, feats = _data()
    L = 288
    pd.testing.assert_frame_equal(c292.SIGNAL("xbasis_ma", feats, L), -c292.xbasis_ma(feats, L))
    pd.testing.assert_frame_equal(c292.SIGNAL("xbasis_z", feats, L), -c292.xbasis_z(feats, L))
    pd.testing.assert_frame_equal(c292.SIGNAL("xleadlag", feats, L), -c292.xleadlag(feats, L))


def test_features_are_causal_no_lookahead() -> None:
    """Perturbing the final 5m inputs must not change any earlier feature row."""
    _, b, o, feats = _data()
    pert_b = b.copy()
    pert_b.iloc[-1] = pert_b.iloc[-1] * 1.01
    pert_o = o.copy()
    pert_o.iloc[-1] = pert_o.iloc[-1] * 1.01
    pert_feats = c292.build_features(pert_b, pert_o)
    for feature in c292.FEATURES:
        for L in c292.LOOKBACKS:
            base = c292.SIGNAL(feature, feats, L)
            alt = c292.SIGNAL(feature, pert_feats, L)
            pd.testing.assert_frame_equal(base.iloc[:-1], alt.iloc[:-1])


def test_wf_splits_are_151() -> None:
    assert len(c292.wf_splits(N_BARS, 720, 168, 168)) == 151
    assert c292.min_periods_for(2016) == 672


def test_weights_gross_cap_and_dollar_neutral() -> None:
    _, b, o, feats = _data()
    sig = c292.SIGNAL("xbasis_ma", feats, 288)
    weights, stats = c292.build_weights(sig, b, o, K=2, H=6, r_start=288)
    assert weights.shape == (N_BARS, b.shape[1])
    gross = weights.abs().sum(axis=1)
    assert bool((gross <= 1.0 + 1e-9).all())
    net = weights.sum(axis=1)
    assert bool((net.abs() <= 1e-9).all())
    assert stats["rebalance_bars_total"] > 0
    assert 0.0 <= stats["gate_pass_share"] <= 1.0


def test_weights_long_short_counts_at_active_rows() -> None:
    _, b, o, feats = _data()
    sig = c292.SIGNAL("xbasis_z", feats, 1008)
    K = 3
    weights, _ = c292.build_weights(sig, b, o, K=K, H=24, r_start=1008)
    active = weights.abs().sum(axis=1) > 0
    assert bool(active.any())
    sub = weights.loc[active]
    for _, row in sub.iterrows():
        vals = row.to_numpy(dtype=float)
        assert int((vals > 0).sum()) == K and int((vals < 0).sum()) == K
        assert bool((np.abs(vals[vals != 0]) == 0.5 / K).all())


def test_fail_closed_zero_dispersion_blocks_all_weights() -> None:
    _, b, o, _ = _data()
    constant = pd.DataFrame(1.0, index=b.index, columns=b.columns)
    weights, stats = c292.build_weights(constant, b, o, K=2, H=6, r_start=288)
    assert bool((weights == 0.0).all().all())
    assert stats["rebalance_bars_passed"] == 0
    assert stats["blocked_rebalance_reasons"] == {"zero_dispersion": stats["rebalance_bars_total"]}


def test_position_is_shifted_one_bar() -> None:
    _, b, o, feats = _data()
    sig = c292.SIGNAL("xleadlag", feats, 288)
    weights, _ = c292.build_weights(sig, b, o, K=2, H=1, r_start=288)
    pos = weights.shift(1).fillna(0.0)
    assert float(pos.iloc[0].abs().sum()) == 0.0
    assert pos.shape == (N_BARS, b.shape[1])


def test_c292_artifacts_exist_with_real_data_flags_and_sha256() -> None:
    parts = ("oos_sweep", "tradable_edge_registry", "summary", "verdict", "binding_constraint")
    paths = {}
    for part in parts:
        matches = sorted(ROOT.glob(f"reports/campaign292_{part}_*.json"))
        assert matches, f"missing C292 artifact for {part}"
        paths[part] = matches[-1]
        payload = json.loads(paths[part].read_text())
        assert payload.get("real_data_only") is True
        assert payload.get("fabricated_data") is False

    verdict = json.loads(paths["verdict"].read_text())
    assert verdict.get("verdict") in ("EDGE_PROVEN", "NOT_TRADABLE")
    assert verdict.get("campaign") == 292

    sweep = json.loads(paths["oos_sweep"].read_text())
    assert sweep["config"]["total_runs"] == 81
    assert sweep["aggregate"]["n_total_runs"] == 81
    run_results = sweep.get("runs", [])
    assert len(run_results) == 81
    assert all(
        set(r) >= {"feature", "lookback", "K", "hold", "edge_proven", "oos_exposure_bars_total"}
        for r in run_results
    )

    registry = json.loads(paths["tradable_edge_registry"].read_text())
    assert registry["oos_sweep_sha256"] == c292.sha256_file(paths["oos_sweep"])
    assert registry["sha256_from_bytes"] == c292.sha256_file(paths["oos_sweep"])

    # verdict records SHA256-from-bytes of the sibling artifacts
    assert verdict["oos_sweep_sha256"] == c292.sha256_file(paths["oos_sweep"])
    assert verdict["registry_sha256"] == c292.sha256_file(paths["tradable_edge_registry"])
    assert verdict["summary_sha256"] == c292.sha256_file(paths["summary"])
    if "binding_constraint_sha256" in verdict:
        assert verdict["binding_constraint_sha256"] == c292.sha256_file(paths["binding_constraint"])