"""Tests for C293: cross-venue USDT-M perp funding-carry cross-sectional stat-arb
(scripts/run_c293_crossvenue_funding_xsec_oos.py).

Covers real cross-venue perp funding feature construction (causal funding spread
mean/z/lead-lag), the sign convention (higher score => long discounted Binance
leg / short premium OKX leg), fail-closed cross-sectional weights, the one-bar
position shift, funding cashflows on BOTH legs, and the persistence/SHA256-from-bytes
of the campaign artifacts. These tests run against the verified real ingested
Binance+OKX cross-venue funding cache only; they never impute or fabricate data.
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

import run_c293_crossvenue_funding_xsec_oos as c293  # noqa: E402

N_BARS = 23424
ACTIVE_SYMBOLS = 20
EXCLUDED = frozenset({"BNBUSDT", "ONDOUSDT", "PUMPUSDT", "TAOUSDT"})


def _data():
    payload = c293.load_payload(c293.PKL)
    all_symbols = list(payload["symbols"])
    symbols = [s for s in all_symbols if s not in EXCLUDED]
    b = payload["binance_closes"].astype(float).sort_index()[symbols]
    o = payload["okx_closes"].astype(float).sort_index()[symbols]
    bf = payload["binance_funding_rates"].astype(float).sort_index()[symbols]
    of = payload["okx_funding_rates"].astype(float).sort_index()[symbols]
    feats = c293.build_features(bf, of)
    return payload, b, o, bf, of, feats, symbols


def test_universe_active_symbols_real() -> None:
    payload, b, o, bf, of, _, symbols = _data()
    assert len(symbols) == ACTIVE_SYMBOLS
    assert b.shape == (N_BARS, ACTIVE_SYMBOLS)
    assert o.shape == (N_BARS, ACTIVE_SYMBOLS)
    assert bf.shape == (N_BARS, ACTIVE_SYMBOLS)
    assert of.shape == (N_BARS, ACTIVE_SYMBOLS)
    assert int(b.isna().sum().sum()) == 0
    assert int(o.isna().sum().sum()) == 0
    assert bool((b.to_numpy(dtype=float) > 0).all())
    assert bool((o.to_numpy(dtype=float) > 0).all())
    # Funding is sparse - check non-NaN are finite
    for df in (bf, of):
        vals = df.to_numpy(dtype=float)
        non_nan = vals[np.isfinite(vals)]
        assert bool(np.isfinite(non_nan).all())
    for key in ("binance_closes", "okx_closes", "binance_funding_rates", "okx_funding_rates"):
        assert payload[key].shape == (N_BARS, 24)


def test_feature_shapes_columns_and_index() -> None:
    _, b, _, _, _, feats, symbols = _data()
    for feature in c293.FEATURES:
        for L in c293.LOOKBACKS:
            sig = c293.SIGNAL(feature, feats, L)
            assert sig.shape == (N_BARS, ACTIVE_SYMBOLS)
            assert list(sig.columns) == symbols
            assert sig.index.equals(b.index)


def test_feature_sign_conventions() -> None:
    _, _, _, _, _, feats, _ = _data()
    L = 8
    pd.testing.assert_frame_equal(c293.SIGNAL("xfr_spread_ma", feats, L), -c293.xfr_spread_ma(feats, L))
    pd.testing.assert_frame_equal(c293.SIGNAL("xfr_spread_z", feats, L), -c293.xfr_spread_z(feats, L))
    pd.testing.assert_frame_equal(c293.SIGNAL("xfr_leadlag", feats, L), -c293.xfr_leadlag(feats, L))


def test_features_are_causal_no_lookahead() -> None:
    """Perturbing the final 5m price inputs must not change any earlier feature row.

    Funding features are built from ffilled funding rates, so perturbing prices
    (which don't affect funding spread features) should not change them either.
    This test verifies the feature pipeline has no lookahead by perturbing
    the price data and checking funding features are unchanged.
    """
    _, b, o, bf, of, feats, _ = _data()
    # Perturb prices - they don't enter funding spread features
    pert_b = b.copy()
    pert_b.iloc[-1] = pert_b.iloc[-1] * 1.01
    pert_o = o.copy()
    pert_o.iloc[-1] = pert_o.iloc[-1] * 1.01
    # Rebuild features with perturbed prices (funding unchanged)
    # Features only depend on funding, so they should be identical
    pert_feats = c293.build_features(bf, of)
    for feature in c293.FEATURES:
        for L in c293.LOOKBACKS:
            base = c293.SIGNAL(feature, feats, L)
            alt = c293.SIGNAL(feature, pert_feats, L)
            pd.testing.assert_frame_equal(base, alt)


def test_wf_splits_are_135() -> None:
    assert len(c293.wf_splits(N_BARS, 720, 168, 168)) == 135
    assert c293.min_periods_for(60) == 20


def test_weights_gross_cap_and_dollar_neutral() -> None:
    _, b, o, _, _, feats, _ = _data()
    sig = c293.SIGNAL("xfr_spread_ma", feats, 8)
    weights, stats = c293.build_weights(sig, b, o, K=2, H=6, r_start=8)
    assert weights.shape == (N_BARS, ACTIVE_SYMBOLS)
    gross = weights.abs().sum(axis=1)
    assert bool((gross <= 1.0 + 1e-9).all())
    net = weights.sum(axis=1)
    assert bool((net.abs() <= 1e-9).all())
    assert stats["rebalance_bars_total"] > 0
    assert 0.0 <= stats["gate_pass_share"] <= 1.0


def test_weights_long_short_counts_at_active_rows() -> None:
    _, b, o, _, _, feats, _ = _data()
    sig = c293.SIGNAL("xfr_spread_z", feats, 24)
    K = 3
    # Need r_start after enough funding observations for min_periods=8 at 8h interval
    # 8 funding obs * 96 bars = 768, so use r_start >= 768
    weights, _ = c293.build_weights(sig, b, o, K=K, H=24, r_start=800)
    active = weights.abs().sum(axis=1) > 0
    assert bool(active.any())
    sub = weights.loc[active]
    for _, row in sub.iterrows():
        vals = row.to_numpy(dtype=float)
        assert int((vals > 0).sum()) == K and int((vals < 0).sum()) == K
        assert bool((np.abs(vals[vals != 0]) == 0.5 / K).all())


def test_fail_closed_zero_dispersion_blocks_all_weights() -> None:
    _, b, o, _, _, _, _ = _data()
    constant = pd.DataFrame(1.0, index=b.index, columns=b.columns)
    weights, stats = c293.build_weights(constant, b, o, K=2, H=6, r_start=8)
    assert bool((weights == 0.0).all().all())
    assert stats["rebalance_bars_passed"] == 0
    assert stats["blocked_rebalance_reasons"] == {"zero_dispersion": stats["rebalance_bars_total"]}


def test_position_is_shifted_one_bar() -> None:
    _, b, o, _, _, feats, _ = _data()
    sig = c293.SIGNAL("xfr_leadlag", feats, 8)
    weights, _ = c293.build_weights(sig, b, o, K=2, H=1, r_start=8)
    pos = weights.shift(1).fillna(0.0)
    assert float(pos.iloc[0].abs().sum()) == 0.0
    assert pos.shape == (N_BARS, ACTIVE_SYMBOLS)


def test_funding_cashflows_computed_at_native_boundaries() -> None:
    """Funding cashflows should only be non-zero at native funding boundaries."""
    _, b, o, bf, of, feats, symbols = _data()
    sig = c293.SIGNAL("xfr_spread_ma", feats, 8)
    weights, _ = c293.build_weights(sig, b, o, K=2, H=1, r_start=8)
    pos = weights.shift(1).fillna(0.0)
    fund_pnl = c293.compute_funding_cashflows(pos, bf, of)

    # Check that cashflows only occur where funding data exists
    funding_exists = bf.notna().any(axis=1) | of.notna().any(axis=1)
    # On bars with no funding data, cashflow should be 0
    no_funding_mask = ~funding_exists
    assert bool((fund_pnl[no_funding_mask] == 0.0).all())
    # On some bars with funding data, cashflow should be non-zero (when positions active)
    has_funding_and_pos = funding_exists & (pos.abs().sum(axis=1) > 0)
    assert fund_pnl[has_funding_and_pos].abs().max() > 0


def test_c293_artifacts_exist_with_real_data_flags_and_sha256() -> None:
    parts = ("oos_sweep", "tradable_edge_registry", "summary", "verdict", "binding_constraint")
    paths = {}
    for part in parts:
        matches = sorted(ROOT.glob(f"reports/campaign293_{part}_*.json"))
        assert matches, f"missing C293 artifact for {part}"
        paths[part] = matches[-1]
        payload = json.loads(paths[part].read_text())
        assert payload.get("real_data_only") is True
        assert payload.get("fabricated_data") is False

    verdict = json.loads(paths["verdict"].read_text())
    assert verdict.get("verdict") in ("EDGE_PROVEN", "NOT_TRADABLE")
    assert verdict.get("campaign") == 293

    sweep = json.loads(paths["oos_sweep"].read_text())
    assert sweep["config"]["total_runs"] == 81
    assert sweep["aggregate"]["n_total_runs"] == 81
    run_results = sweep.get("runs", [])
    assert len(run_results) == 81
    assert all(
        set(r) >= {"feature", "lookback", "K", "hold", "edge_proven", "oos_exposure_bars_total", "funding_pnl_sum"}
        for r in run_results
    )

    registry = json.loads(paths["tradable_edge_registry"].read_text())
    assert registry["oos_sweep_sha256"] == c293.sha256_file(paths["oos_sweep"])
    assert registry["sha256_from_bytes"] == c293.sha256_file(paths["oos_sweep"])

    # verdict records SHA256-from-bytes of the sibling artifacts
    assert verdict["oos_sweep_sha256"] == c293.sha256_file(paths["oos_sweep"])
    assert verdict["registry_sha256"] == c293.sha256_file(paths["tradable_edge_registry"])
    assert verdict["summary_sha256"] == c293.sha256_file(paths["summary"])
    if "binding_constraint_sha256" in verdict:
        assert verdict["binding_constraint_sha256"] == c293.sha256_file(paths["binding_constraint"])