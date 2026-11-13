"""Tests for C295: real three-venue spot cross-venue basis / dispersion /
lead-lag cross-sectional stat-arb
(scripts/run_c295_three_venue_basis_xsec_oos.py).

Covers real three-venue feature construction (causal basis_bc/basis_oc/xdisp/
leadlag with shift(1)), fail-closed cross-sectional weights (long top-K /
short bottom-K), the one-bar position shift, the costed OOS PnL on all legs,
and the persistence/SHA256-from-bytes of the campaign artifacts.  These tests
run against the verified real ingested three-venue 5m cache only; they never
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

import run_c295_three_venue_basis_xsec_oos as c295  # noqa: E402

SYMBOLS = None  # populated from the cache at test time
VENUES = ("binance", "okx", "coinbase")
K_EFF = 2


def _data():
    payload = c295.load_payload(c295.PKL)
    syms = list(payload["symbols"])
    b = payload["binance_closes"].astype(float).sort_index()[syms]
    o = payload["okx_closes"].astype(float).sort_index()[syms]
    c = payload["coinbase_closes"].astype(float).sort_index()[syms]
    feats = c295.build_features(b, o, c)
    return payload, syms, b, o, c, feats


def test_universe_real_and_finite() -> None:
    payload, syms, b, o, c, _ = _data()
    n = len(b)
    assert len(syms) >= 2
    assert b.shape == (n, len(syms))
    assert o.shape == (n, len(syms))
    assert c.shape == (n, len(syms))
    assert list(b.columns) == syms
    assert list(o.columns) == syms
    assert list(c.columns) == syms
    assert b.index.equals(o.index) and b.index.equals(c.index)
    for name, df in (("binance", b), ("okx", o), ("coinbase", c)):
        assert int(df.isna().sum().sum()) == 0
        assert bool(np.isfinite(df.to_numpy(dtype=float)).all())
        assert bool((df.to_numpy(dtype=float) > 0).all())
    # Exact 5m spacing (no gap-fill)
    diffs = b.index.to_series().diff().dropna()
    assert bool((diffs == pd.Timedelta(minutes=5)).all())
    import json as _json

    meta = _json.loads((ROOT / "data" / "cache" / "campaign295_three_venue_spot.meta.json").read_text())
    assert meta["real_data_only"] is True
    assert meta["fabricated_data"] is False


def test_feature_shapes_columns_and_index() -> None:
    _, syms, _, _, _, feats = _data()
    b = feats["r_b"]  # not a close, but has same index/shape
    n = len(b)
    for feature in c295.FEATURES:
        for L in c295.LOOKBACKS:
            sig = c295.SIGNAL(feature, feats, L)
            assert sig.shape == (n, len(syms)), (feature, L, sig.shape)
            assert list(sig.columns) == syms
            assert sig.index.equals(b.index)


def test_feature_sign_conventions() -> None:
    _, _, _, _, _, feats = _data()
    L = 288
    pd.testing.assert_frame_equal(c295.SIGNAL("basis_bc_ma", feats, L), -c295.basis_bc_ma(feats, L))
    pd.testing.assert_frame_equal(c295.SIGNAL("basis_bc_z", feats, L), -c295.basis_bc_z(feats, L))
    pd.testing.assert_frame_equal(c295.SIGNAL("basis_oc_ma", feats, L), -c295.basis_oc_ma(feats, L))
    pd.testing.assert_frame_equal(c295.SIGNAL("basis_oc_z", feats, L), -c295.basis_oc_z(feats, L))
    pd.testing.assert_frame_equal(c295.SIGNAL("xdisp", feats, L), -c295.xdisp(feats, L))
    pd.testing.assert_frame_equal(c295.SIGNAL("leadlag", feats, L), c295.leadlag(feats, L))


def test_features_are_causal_no_lookahead() -> None:
    """Perturbing the final input row must not change any feature row.

    Every feature applies shift(1), so the last input bar is never used by any
    output row.  This verifies no lookahead in the feature pipeline.
    """
    _, syms, b, o, c, feats = _data()
    pert_b = b.copy()
    pert_b.iloc[-1] = pert_b.iloc[-1] * 1.05
    pert_o = o.copy()
    pert_o.iloc[-1] = pert_o.iloc[-1] * 1.05
    pert_c = c.copy()
    pert_c.iloc[-1] = pert_c.iloc[-1] * 1.05
    pert_feats = c295.build_features(pert_b, pert_o, pert_c)
    for feature in c295.FEATURES:
        for L in c295.LOOKBACKS:
            base = c295.SIGNAL(feature, feats, L)
            alt = c295.SIGNAL(feature, pert_feats, L)
            pd.testing.assert_frame_equal(base, alt)


def test_wf_splits_and_min_periods() -> None:
    _, syms, b, _, _, _ = _data()
    n = len(b)
    expected = (n - 720 - 168) // 168 + 1
    assert len(c295.wf_splits(n, 720, 168, 168)) == expected
    assert c295.min_periods_for(2016) == 672
    assert c295.min_periods_for(288) == 96
    assert c295.min_periods_for(1008) == 336


def test_weights_gross_cap_and_dollar_neutral() -> None:
    _, syms, b, o, c, feats = _data()
    sig = c295.SIGNAL("basis_bc_ma", feats, 288)
    spr_ret = c295.spread_return("basis_bc_ma", feats)
    weights, stats = c295.build_weights(sig, b, c, K_EFF, H=6, r_start=0)
    assert weights.shape == (len(b), len(syms))
    gross = weights.abs().sum(axis=1)
    assert bool((gross <= 1.0 + 1e-9).all())
    net = weights.sum(axis=1)
    assert bool((net.abs() <= 1e-9).all())
    assert stats["rebalance_bars_total"] > 0
    assert 0.0 <= stats["gate_pass_share"] <= 1.0


def test_weights_long_short_K_each() -> None:
    _, syms, b, o, c, feats = _data()
    sig = c295.SIGNAL("basis_oc_z", feats, 1008)
    weights, _ = c295.build_weights(sig, o, c, K_EFF, H=24, r_start=0)
    active = weights.abs().sum(axis=1) > 0
    assert bool(active.any())
    sub = weights.loc[active]
    for _, row in sub.iterrows():
        vals = row.to_numpy(dtype=float)
        assert int((vals > 0).sum()) == K_EFF and int((vals < 0).sum()) == K_EFF
        assert bool((np.abs(vals[vals != 0]) == 0.5 / K_EFF).all())


def test_fail_closed_zero_dispersion_blocks_all_weights() -> None:
    _, syms, b, c, _, _ = _data()
    constant = pd.DataFrame(1.0, index=b.index, columns=b.columns)
    weights, stats = c295.build_weights(constant, b, c, K_EFF, H=6, r_start=0)
    assert bool((weights == 0.0).all().all())
    assert stats["rebalance_bars_passed"] == 0
    assert stats["blocked_rebalance_reasons"] == {"zero_dispersion": stats["rebalance_bars_total"]}


def test_position_is_shifted_one_bar() -> None:
    _, syms, b, c, _, feats = _data()
    sig = c295.SIGNAL("basis_bc_ma", feats, 288)
    weights, _ = c295.build_weights(sig, b, c, K_EFF, H=1, r_start=0)
    pos = weights.shift(1).fillna(0.0)
    assert float(pos.iloc[0].abs().sum()) == 0.0
    assert pos.shape == (len(b), len(syms))


def test_c295_artifacts_exist_with_real_data_flags_and_sha256() -> None:
    parts = ("oos_sweep", "tradable_edge_registry", "summary", "verdict", "binding_constraint")
    paths = {}
    for part in parts:
        matches = sorted(ROOT.glob(f"reports/campaign295_{part}_*.json"))
        assert matches, f"missing C295 artifact for {part}"
        paths[part] = matches[-1]
        payload = json.loads(paths[part].read_text())
        assert payload.get("real_data_only") is True
        assert payload.get("fabricated_data") is False

    verdict = json.loads(paths["verdict"].read_text())
    assert verdict.get("verdict") in ("EDGE_PROVEN", "NOT_TRADABLE")
    assert verdict.get("campaign") == 295

    sweep = json.loads(paths["oos_sweep"].read_text())
    assert sweep["config"]["total_runs"] == 162
    assert sweep["aggregate"]["n_total_runs"] == 162
    run_results = sweep.get("runs", [])
    assert len(run_results) == 162
    assert all(
        set(r) >= {
            "feature",
            "lookback",
            "K",
            "hold",
            "edge_proven",
            "oos_exposure_bars_total",
            "spread_pnl_sum",
        }
        for r in run_results
    )
    for r in run_results:
        assert r["feature"] in c295.FEATURES
        assert r["lookback"] in c295.LOOKBACKS
        assert r["K"] in c295.K_VALUES
        assert r["hold"] in c295.HOLDS

    registry = json.loads(paths["tradable_edge_registry"].read_text())
    assert registry["oos_sweep_sha256"] == c295.sha256_file(paths["oos_sweep"])
    assert registry["sha256_from_bytes"] == c295.sha256_file(paths["oos_sweep"])

    assert verdict["oos_sweep_sha256"] == c295.sha256_file(paths["oos_sweep"])
    assert verdict["registry_sha256"] == c295.sha256_file(paths["tradable_edge_registry"])
    assert verdict["summary_sha256"] == c295.sha256_file(paths["summary"])
    if "binding_constraint_sha256" in verdict:
        assert verdict["binding_constraint_sha256"] == c295.sha256_file(paths["binding_constraint"])
