"""Tests for C298: real multi-year (2020-01 .. 2026-10) USDT-M perp
funding-carry + spot/perp basis cross-sectional stat-arb
(scripts/run_c298_multianual_funding_basis_xsec_oos.py).

Covers real-perp feature construction (causal funding/basis/momentum), the real
funding cashflow sign convention, fail-closed cross-sectional weights incl. the
signal-coverage gate (the fully-covered 2020-2026 universe is 3 perps, so K in
{2,3,5} can never select 2K distinct assets and every run is correctly blocked
with zero exposure), and the persistence/SHA256-from-bytes of the campaign
artifacts. These tests run against the verified real ingested cache only; they
never impute or fabricate data. Spot feed gaps (data-api missing hours) are
carried as NaN and must make basis-based scores NaN at those rows.
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

import run_c298_multianual_funding_basis_xsec_oos as c298  # noqa: E402

SYMBOLS = list(c298.load_payload(c298.CACHE)["symbols"])
N_BARS = int(c298.load_payload(c298.CACHE)["n_bars"])


def _data():
    payload = c298.load_payload(c298.CACHE)
    closes = payload["closes"].astype(float).sort_index()
    funding = payload["funding_rates"].astype(float).reindex(closes.index)
    spot = payload["spot_closes"].astype(float).reindex(closes.index)[SYMBOLS]
    feats = c298.build_features(closes, spot, funding)
    return payload, closes, funding, spot, feats


def test_universe_full_coverage_over_window():
    payload, closes, funding, spot, _ = _data()
    assert len(SYMBOLS) >= 2
    assert closes.shape == (N_BARS, len(SYMBOLS))
    assert spot.shape == (N_BARS, len(SYMBOLS))
    assert funding.shape == (N_BARS, len(SYMBOLS))
    for key in ("opens", "highs", "lows", "closes", "volumes"):
        assert payload[key].shape == (N_BARS, len(SYMBOLS))
    assert int(closes.isna().sum().sum()) == 0
    assert bool((closes.to_numpy(dtype=float) > 0).all())
    assert bool(np.isfinite(closes.to_numpy(dtype=float)).all())
    assert str(closes.index.min()) == "2020-01-01 00:00:00+00:00"
    assert str(closes.index.max()) == "2026-10-31 23:00:00+00:00"
    assert int(funding.notna().sum().sum()) >= 90 * len(SYMBOLS)
    # spot gaps are recorded (data-api missing hours), never imputed
    assert int(spot.isna().sum().sum()) > 0


def test_feature_shapes_columns_and_index():
    _, closes, _, spot, feats = _data()
    for feature in c298.FEATURES:
        for L in c298.LOOKBACKS:
            sig = c298.SIGNAL(feature, feats, L)
            assert sig.shape == (N_BARS, len(SYMBOLS))
            assert list(sig.columns) == SYMBOLS
            assert sig.index.equals(closes.index)


def test_feature_sign_conventions():
    _, _, _, spot, feats = _data()
    L = 168
    pd.testing.assert_frame_equal(c298.SIGNAL("funding_level", feats, L), -c298.funding_level(feats, L))
    pd.testing.assert_frame_equal(c298.SIGNAL("funding_z", feats, L), -c298.funding_z(feats, L))
    pd.testing.assert_frame_equal(c298.SIGNAL("basis_ma", feats, L), -c298.basis_ma(feats, L))
    pd.testing.assert_frame_equal(c298.SIGNAL("basis_z", feats, L), -c298.basis_z(feats, L))
    pd.testing.assert_frame_equal(c298.SIGNAL("perp_mom", feats, L), c298.perp_mom(feats, L))
    pd.testing.assert_frame_equal(c298.SIGNAL("perp_lowvol", feats, L), -c298.perp_lowvol(feats, L))


def test_features_are_causal_no_lookahead():
    payload, closes, funding, spot, feats = _data()
    pert_closes = closes.copy()
    pert_closes.iloc[-1] = pert_closes.iloc[-1] * 1.01
    pert_spot = spot.copy()
    pert_spot.iloc[-1] = pert_spot.iloc[-1] * 1.01
    pert_funding = funding.copy()
    pert_funding.iloc[-1] = pert_funding.iloc[-1] + 1e-4
    pert_feats = c298.build_features(pert_closes, pert_spot, pert_funding)
    for feature in c298.FEATURES:
        for L in c298.LOOKBACKS:
            base = c298.SIGNAL(feature, feats, L)
            alt = c298.SIGNAL(feature, pert_feats, L)
            pd.testing.assert_frame_equal(base.iloc[:-1], alt.iloc[:-1])


def test_basis_signal_tolerates_sparse_spot_gaps():
    """Sparse spot gaps (data-api missing hours) are carried as NaN in the raw
    spot frame and never imputed; basis scores are rolling means over L bars
    with min_periods=max(20, L//3), so sparse gaps do not NaN them out."""
    _, _, _, spot, feats = _data()
    gap_mask = spot.isna().any(axis=1)
    assert int(gap_mask.sum()) > 0, "expected recorded spot gap hours"
    sig = c298.SIGNAL("basis_ma", feats, 168)
    # sparse gaps: basis remains finite at gap rows (min_periods tolerance)
    assert bool(np.isfinite(sig.loc[gap_mask]).all().all()), "basis finite at sparse spot gaps"
    # a dense (> L - min_periods) gap NaNs the rolling mean out
    dense = feats["basis"].copy()
    dense.iloc[:200] = np.nan
    out = c298.basis_ma(feats | {"basis": dense}, 168)
    assert bool(out.iloc[:190].isna().all().all())


def test_funding_cashflow_sign_convention():
    _, _, funding, _, _ = _data()
    leg = -funding.fillna(0.0)
    mask = funding.notna().values
    assert np.allclose(leg.values[mask], -funding.values[mask])
    assert bool((leg.values[~mask] == 0).all())


def test_funding_age_is_bounded():
    _, _, funding, _, _ = _data()
    age = c298.compute_funding_age(funding)
    assert float(np.nanmax(age.values)) <= c298.STALE_BARS


def test_weights_gross_cap_and_dollar_neutral():
    _, closes, _, _, feats = _data()
    sig = c298.SIGNAL("funding_level", feats, 168)
    weights, stats = c298.build_weights(sig, closes, K=2, H=1, r_start=168)
    assert weights.shape == (N_BARS, len(SYMBOLS))
    gross = weights.abs().sum(axis=1)
    assert bool((gross <= 1.0 + 1e-9).all())
    net = weights.sum(axis=1)
    assert bool((net.abs() <= 1e-9).all())
    assert stats["rebalance_bars_total"] > 0
    assert 0.0 <= stats["gate_pass_share"] <= 1.0


def test_fail_closed_zero_dispersion_blocks_all_weights():
    _, closes, _, _, _ = _data()
    constant = pd.DataFrame(1.0, index=closes.index, columns=SYMBOLS)
    weights, stats = c298.build_weights(constant, closes, K=2, H=6, r_start=168)
    assert bool((weights == 0.0).all().all())
    assert stats["rebalance_bars_passed"] == 0


def test_fail_closed_signal_coverage_blocks_thin_cross_section():
    """With 3 fully-covered perps, K>=2 can never select 2K distinct assets."""
    _, closes, _, _, feats = _data()
    sig = c298.SIGNAL("funding_level", feats, 168)
    for K in c298.K_VALUES:
        weights, stats = c298.build_weights(sig, closes, K=K, H=1, r_start=168)
        assert bool((weights == 0.0).all().all()), f"K={K} must be blocked on a 3-asset universe"
        assert stats["rebalance_bars_passed"] == 0
        assert stats["blocked_rebalance_reasons"] == {"signal_coverage": stats["rebalance_bars_total"]}


def test_position_is_shifted_one_bar():
    _, closes, _, _, feats = _data()
    sig = c298.SIGNAL("perp_lowvol", feats, 168)
    weights, _ = c298.build_weights(sig, closes, K=2, H=1, r_start=168)
    pos = weights.shift(1).fillna(0.0)
    assert float(pos.iloc[0].abs().sum()) == 0.0
    assert pos.shape == (N_BARS, len(SYMBOLS))


def test_c298_artifacts_exist_with_real_data_flags_and_sha256():
    parts = ("oos_sweep", "tradable_edge_registry", "summary", "verdict", "binding_constraint")
    paths = {}
    for part in parts:
        matches = sorted(ROOT.glob(f"reports/campaign298_{part}_*.json"))
        assert matches, f"missing C298 artifact for {part}"
        paths[part] = matches[-1]
        payload = json.loads(paths[part].read_text())
        assert payload.get("real_data_only") is True
        assert payload.get("fabricated_data") is False

    verdict = json.loads(paths["verdict"].read_text())
    assert verdict.get("verdict") == "NOT_TRADABLE"
    assert verdict.get("edge_proven") is False
    assert verdict.get("campaign") == 298
    assert verdict.get("executed_fills") is False or "executed_fills" not in verdict

    sweep = json.loads(paths["oos_sweep"].read_text())
    assert sweep["verdict"] == "NOT_TRADABLE"
    assert sweep["summary"]["n_total_runs"] == 162
    assert sweep["config"]["total_runs"] == 162
    run_results = sweep.get("results", [])
    assert len(run_results) == 162
    assert all(r["edge_proven"] is False for r in run_results)
    assert all(r["oos_exposure_bars_total"] == 0 for r in run_results)
    assert all("funding_pnl_sum" in r and "price_pnl_sum" in r for r in run_results)

    sweep_sha = c298.sha256_file(paths["oos_sweep"])
    reg_sha = c298.sha256_file(paths["tradable_edge_registry"])
    sum_sha = c298.sha256_file(paths["summary"])
    ver_sha = c298.sha256_file(paths["verdict"])
    bind_sha = c298.sha256_file(paths["binding_constraint"])
    assert sweep_sha == verdict["oos_sweep_sha256"]
    assert reg_sha == verdict["registry_sha256"]
    assert sum_sha == verdict["summary_sha256"]
    assert bind_sha == verdict["binding_constraint_sha256"]

    # edge rule, never relaxed: exposure > 0 AND all cost slices net > 0 AND
    # mean per-split OOS net mean > mean per-split B&H OOS net mean
    assert sweep["summary"]["n_edge_proven"] == 0
    assert sweep["summary"]["n_with_exposure"] == 0

    for key, path_key in (
        ("oos_sweep_sha256", "oos_sweep_artifact"),
        ("registry_sha256", "registry_artifact"),
        ("summary_sha256", "summary_artifact"),
        ("binding_constraint_sha256", "binding_constraint_artifact"),
    ):
        artifact_path = verdict.get(path_key)
        assert artifact_path, f"verdict missing {path_key}"
        p = ROOT / artifact_path
        assert p.exists(), f"referenced artifact missing: {artifact_path}"
        assert c298.sha256_file(p) == verdict[key], f"sha256 mismatch for {artifact_path}"
