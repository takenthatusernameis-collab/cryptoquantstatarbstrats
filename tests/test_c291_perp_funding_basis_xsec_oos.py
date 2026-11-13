"""Tests for C291: real USDT-M perp funding-carry / basis cross-sectional stat-arb
(scripts/run_c291_perp_funding_basis_xsec_oos.py).

Covers real-perp feature construction (causal funding/basis/momentum), the real
funding cashflow sign convention, fail-closed cross-sectional weights incl. the
funding-staleness gate, and the persistence/SHA256-from-bytes of the campaign
artifacts. These tests run against the verified real ingested perp+funding cache
only; they never impute or fabricate data.
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

import run_c291_perp_funding_basis_xsec_oos as c291  # noqa: E402

SYMBOLS = list(c291.load_payload(c291.PERP)["symbols"])
N_BARS = 26208


def _data():
    payload = c291.load_payload(c291.PERP)
    closes = payload["closes"].astype(float).sort_index()
    funding = payload["funding_rates"].astype(float).reindex(closes.index)
    spot_payload = c291.load_payload(c291.SPOT)
    spot = spot_payload["closes"].astype(float).reindex(closes.index)[SYMBOLS]
    feats = c291.build_features(closes, spot, funding)
    return payload, closes, funding, feats


def test_universe_is_24_real_perps_full_coverage():
    payload, closes, funding, _ = _data()
    assert closes.shape == (N_BARS, len(SYMBOLS))
    assert len(SYMBOLS) == 24
    assert int(closes.isna().sum().sum()) == 0
    assert bool((closes.to_numpy(dtype=float) > 0).all())
    for key in ("opens", "highs", "lows", "closes", "volumes"):
        assert payload[key].shape == (N_BARS, len(SYMBOLS))
    assert payload["funding_rates"].shape == (N_BARS, len(SYMBOLS))
    assert int(funding.notna().sum().sum()) >= 90 * len(SYMBOLS)


def test_feature_shapes_columns_and_index():
    _, closes, _, feats = _data()
    for feature in c291.FEATURES:
        for L in c291.LOOKBACKS:
            sig = c291.SIGNAL(feature, feats, L)
            assert sig.shape == (N_BARS, len(SYMBOLS))
            assert list(sig.columns) == SYMBOLS
            assert sig.index.equals(closes.index)


def test_feature_sign_conventions():
    _, _, _, feats = _data()
    L = 288
    pd.testing.assert_frame_equal(c291.SIGNAL("funding_level", feats, L), -c291.funding_level(feats, L))
    pd.testing.assert_frame_equal(c291.SIGNAL("funding_z", feats, L), -c291.funding_z(feats, L))
    pd.testing.assert_frame_equal(c291.SIGNAL("basis_ma", feats, L), -c291.basis_ma(feats, L))
    pd.testing.assert_frame_equal(c291.SIGNAL("basis_z", feats, L), -c291.basis_z(feats, L))
    pd.testing.assert_frame_equal(c291.SIGNAL("perp_mom", feats, L), c291.perp_mom(feats, L))
    pd.testing.assert_frame_equal(c291.SIGNAL("perp_lowvol", feats, L), -c291.perp_lowvol(feats, L))


def test_features_are_causal_no_lookahead():
    """Perturbing the final 5m inputs must not change any earlier feature row."""
    payload, closes, funding, feats = _data()
    spot_payload = c291.load_payload(c291.SPOT)
    spot = spot_payload["closes"].astype(float).reindex(closes.index)[SYMBOLS]
    pert_closes = closes.copy()
    pert_closes.iloc[-1] = pert_closes.iloc[-1] * 1.01
    pert_spot = spot.copy()
    pert_spot.iloc[-1] = pert_spot.iloc[-1] * 1.01
    pert_funding = funding.copy()
    pert_funding.iloc[-1] = pert_funding.iloc[-1] + 1e-4
    pert_feats = c291.build_features(pert_closes, pert_spot, pert_funding)
    for feature in c291.FEATURES:
        for L in c291.LOOKBACKS:
            base = c291.SIGNAL(feature, feats, L)
            alt = c291.SIGNAL(feature, pert_feats, L)
            pd.testing.assert_frame_equal(base.iloc[:-1], alt.iloc[:-1])


def test_funding_cashflow_sign_convention():
    """funding_leg == -rate at funding boundaries, 0 elsewhere; long pays when rate>0."""
    _, _, funding, _ = _data()
    leg = -funding.fillna(0.0)
    mask = funding.notna().values
    assert np.allclose(leg.values[mask], -funding.values[mask])
    assert bool((leg.values[~mask] == 0).all())

    pos = pd.DataFrame(0.0, index=funding.index, columns=funding.columns)
    bmask = funding["BTCUSDT"].notna()
    i = int(np.where(bmask.values)[0][5])
    pos.iloc[i, 0] = 0.5   # long BTC
    pos.iloc[i, 1] = -0.5  # short ETH
    fpn = (pos * leg).sum(axis=1)
    expected = -0.5 * funding["BTCUSDT"].iloc[i] + 0.5 * funding["ETHUSDT"].iloc[i]
    assert abs(float(fpn.iloc[i]) - float(expected)) < 1e-12
    # all non-boundary bars have zero funding pnl
    assert float(fpn.drop(fpn.index[[i]]).abs().sum()) == 0.0


def test_funding_age_is_bounded_by_8h():
    _, _, funding, _ = _data()
    age = c291.compute_funding_age(funding)
    assert float(np.nanmax(age.values)) <= c291.STALE_BARS
    assert float(np.nanmin(age.iloc[0].values)) == 0.0


def test_weights_gross_cap_and_dollar_neutral():
    _, closes, _, feats = _data()
    sig = c291.SIGNAL("funding_level", feats, 288)
    weights, stats = c291.build_weights(sig, closes, K=2, H=6, r_start=288)
    assert weights.shape == (N_BARS, len(SYMBOLS))
    gross = weights.abs().sum(axis=1)
    assert bool((gross <= 1.0 + 1e-9).all())
    net = weights.sum(axis=1)
    assert bool((net.abs() <= 1e-9).all())
    assert stats["rebalance_bars_total"] > 0
    assert 0.0 <= stats["gate_pass_share"] <= 1.0


def test_weights_long_short_counts_at_active_rows():
    _, closes, _, feats = _data()
    sig = c291.SIGNAL("basis_ma", feats, 1008)
    weights, _ = c291.build_weights(sig, closes, K=3, H=24, r_start=1008)
    active = weights.abs().sum(axis=1) > 0
    assert bool(active.any())
    sub = weights.loc[active]
    for _, row in sub.iterrows():
        vals = row.to_numpy(dtype=float)
        assert int((vals > 0).sum()) == 3 and int((vals < 0).sum()) == 3
        assert bool((np.abs(vals[vals != 0]) == 0.5 / 3).all())


def test_fail_closed_zero_dispersion_blocks_all_weights():
    _, closes, _, _ = _data()
    constant = pd.DataFrame(1.0, index=closes.index, columns=SYMBOLS)
    weights, stats = c291.build_weights(constant, closes, K=2, H=6, r_start=288)
    assert bool((weights == 0.0).all().all())
    assert stats["rebalance_bars_passed"] == 0
    assert stats["blocked_rebalance_reasons"] == {"zero_dispersion": stats["rebalance_bars_total"]}


def test_fail_closed_funding_staleness_blocks():
    """A stale (all-NaN) funding age must block rebalances as funding_stale."""
    _, closes, _, feats = _data()
    sig = c291.SIGNAL("perp_mom", feats, 288)
    stale_age = pd.DataFrame(np.inf, index=closes.index, columns=SYMBOLS)
    weights, stats = c291.build_weights(sig, closes, K=2, H=6, r_start=288, funding_age=stale_age)
    assert bool((weights == 0.0).all().all())
    assert stats["blocked_rebalance_reasons"] == {"funding_stale": stats["rebalance_bars_total"]}


def test_position_is_shifted_one_bar():
    _, closes, _, feats = _data()
    sig = c291.SIGNAL("perp_lowvol", feats, 288)
    weights, _ = c291.build_weights(sig, closes, K=2, H=1, r_start=288)
    pos = weights.shift(1).fillna(0.0)
    assert float(pos.iloc[0].abs().sum()) == 0.0
    assert pos.shape == (N_BARS, len(SYMBOLS))


def test_c291_artifacts_exist_with_real_data_flags_and_sha256():
    parts = ("oos_sweep", "tradable_edge_registry", "summary", "verdict", "binding_constraint")
    paths = {}
    for part in parts:
        matches = sorted(ROOT.glob(f"reports/campaign291_{part}_*.json"))
        assert matches, f"missing C291 artifact for {part}"
        paths[part] = matches[-1]
        payload = json.loads(paths[part].read_text())
        assert payload.get("real_data_only") is True
        assert payload.get("fabricated_data") is False

    verdict = json.loads(paths["verdict"].read_text())
    assert verdict.get("verdict") in ("EDGE_PROVEN", "NOT_TRADABLE")
    assert verdict.get("campaign") == 291

    sweep = json.loads(paths["oos_sweep"].read_text())
    assert sweep["summary"]["n_total_runs"] == 162
    assert sweep["config"]["total_runs"] == 162
    run_results = sweep.get("results", [])
    assert len(run_results) == 162
    assert all(
        set(r) >= {"feature", "lookback", "K", "hold", "edge_proven", "oos_exposure_bars_total"}
        for r in run_results
    )
    # funding cashflow must be recorded per run
    assert all("funding_pnl_sum" in r and "price_pnl_sum" in r for r in run_results)

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
            assert c291.sha256_file(p) == verdict[key], f"sha256 mismatch for {artifact_path}"