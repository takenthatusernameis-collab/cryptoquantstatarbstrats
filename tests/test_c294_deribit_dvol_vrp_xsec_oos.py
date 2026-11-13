"""Tests for C294: real implied-volatility (Deribit DVOL) variance-risk-premium /
BTC-vs-ETH relative-value cross-sectional stat-arb
(scripts/run_c294_deribit_dvol_vrp_xsec_oos.py).

Covers real DVOL/RV feature construction (causal iv-rv spread, IV z, cross-sectional
DVOL spread), the sign convention (higher score => long that asset), fail-closed
cross-sectional weights (pairwise long top-1 / short bottom-1), the one-bar position
shift, the PRIMARY real spot relative-value PnL and the DIAGNOSTIC variance-swap-proxy
leg (executed_fills=false), and the persistence/SHA256-from-bytes of the campaign
artifacts.  These tests run against the verified real ingested DVOL + Binance spot 1h
cache only; they never impute or fabricate data.
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

import run_c294_deribit_dvol_vrp_xsec_oos as c294  # noqa: E402

SYMBOLS = ["BTC", "ETH"]
K_EFF = 1  # 2-asset cross-section: long top-1 / short bottom-1


def _data():
    payload = c294.load_payload(c294.PKL)
    dvol = payload["dvol"].astype(float).sort_index()[SYMBOLS]
    spot = payload["spot_closes"].astype(float).sort_index()[SYMBOLS]
    feats = c294.build_features(dvol, spot)
    return payload, dvol, spot, feats


def test_universe_real_and_finite() -> None:
    payload, dvol, spot, _ = _data()
    n = len(dvol)
    assert dvol.shape == (n, 2)
    assert spot.shape == (n, 2)
    assert list(dvol.columns) == SYMBOLS
    assert dvol.index.equals(spot.index)
    assert int(dvol.isna().sum().sum()) == 0
    assert int(spot.isna().sum().sum()) == 0
    assert bool(np.isfinite(dvol.to_numpy(dtype=float)).all())
    assert bool(np.isfinite(spot.to_numpy(dtype=float)).all())
    assert bool((spot.to_numpy(dtype=float) > 0).all())
    assert payload["iv_definition"] == "deribit_dvol_index"
    # Exact 1h spacing (no gap-fill)
    diffs = dvol.index.to_series().diff().dropna()
    assert bool((diffs == pd.Timedelta(hours=1)).all())


def test_effective_k_for_two_asset_cross_section() -> None:
    assert c294.effective_k(2, 2) == 1
    assert c294.effective_k(5, 2) == 1


def test_feature_shapes_columns_and_index() -> None:
    _, dvol, _, feats = _data()
    for feature in c294.FEATURES:
        for L in c294.LOOKBACKS:
            sig = c294.SIGNAL(feature, feats, L)
            assert sig.shape == dvol.shape
            assert list(sig.columns) == SYMBOLS
            assert sig.index.equals(dvol.index)


def test_feature_sign_conventions() -> None:
    _, _, _, feats = _data()
    L = 24
    pd.testing.assert_frame_equal(c294.SIGNAL("iv_rv_spread", feats, L), c294.iv_rv_spread(feats, L))
    pd.testing.assert_frame_equal(c294.SIGNAL("iv_z", feats, L), c294.iv_z(feats, L))
    pd.testing.assert_frame_equal(c294.SIGNAL("dvol_x_spread", feats, L), c294.dvol_x_spread(feats, L))
    # dvol_x_spread is BTC=+z, ETH=-z
    x = c294.dvol_x_spread(feats, L)
    pd.testing.assert_series_equal(x["BTC"], -x["ETH"], check_names=False)


def test_features_are_causal_no_lookahead() -> None:
    """Perturbing the final input row must not change any feature row.

    Every feature applies shift(1), so the last input bar is never used by any
    output row.  This verifies no lookahead in the feature pipeline.
    """
    _, dvol, spot, feats = _data()
    pert_dvol = dvol.copy()
    pert_dvol.iloc[-1] = pert_dvol.iloc[-1] * 1.05
    pert_spot = spot.copy()
    pert_spot.iloc[-1] = pert_spot.iloc[-1] * 1.05
    pert_feats = c294.build_features(pert_dvol, pert_spot)
    for feature in c294.FEATURES:
        for L in c294.LOOKBACKS:
            base = c294.SIGNAL(feature, feats, L)
            alt = c294.SIGNAL(feature, pert_feats, L)
            pd.testing.assert_frame_equal(base, alt)


def test_wf_splits_185_and_min_periods() -> None:
    _, dvol, _, _ = _data()
    n = len(dvol)
    assert len(c294.wf_splits(n, 720, 168, 168)) == 185
    assert c294.min_periods_for(720) == 240
    assert c294.min_periods_for(24) == 8


def test_weights_gross_cap_and_dollar_neutral() -> None:
    _, dvol, _, feats = _data()
    sig = c294.SIGNAL("iv_z", feats, 24)
    weights, stats = c294.build_weights(sig, dvol, K_EFF, H=6, r_start=24)
    assert weights.shape == dvol.shape
    gross = weights.abs().sum(axis=1)
    assert bool((gross <= 1.0 + 1e-9).all())
    net = weights.sum(axis=1)
    assert bool((net.abs() <= 1e-9).all())
    assert stats["rebalance_bars_total"] > 0
    assert 0.0 <= stats["gate_pass_share"] <= 1.0


def test_weights_pairwise_long_short_one_each() -> None:
    _, dvol, _, feats = _data()
    sig = c294.SIGNAL("dvol_x_spread", feats, 24)
    weights, _ = c294.build_weights(sig, dvol, K_EFF, H=24, r_start=24)
    active = weights.abs().sum(axis=1) > 0
    assert bool(active.any())
    sub = weights.loc[active]
    for _, row in sub.iterrows():
        vals = row.to_numpy(dtype=float)
        assert int((vals > 0).sum()) == 1 and int((vals < 0).sum()) == 1
        assert bool((np.abs(vals[vals != 0]) == 0.5).all())


def test_fail_closed_zero_dispersion_blocks_all_weights() -> None:
    _, dvol, _, _ = _data()
    constant = pd.DataFrame(1.0, index=dvol.index, columns=dvol.columns)
    weights, stats = c294.build_weights(constant, dvol, K_EFF, H=6, r_start=24)
    assert bool((weights == 0.0).all().all())
    assert stats["rebalance_bars_passed"] == 0
    assert stats["blocked_rebalance_reasons"] == {"zero_dispersion": stats["rebalance_bars_total"]}


def test_position_is_shifted_one_bar() -> None:
    _, dvol, _, feats = _data()
    sig = c294.SIGNAL("iv_rv_spread", feats, 24)
    weights, _ = c294.build_weights(sig, dvol, K_EFF, H=1, r_start=24)
    pos = weights.shift(1).fillna(0.0)
    assert float(pos.iloc[0].abs().sum()) == 0.0
    assert pos.shape == dvol.shape


def test_variance_swap_proxy_returns_series() -> None:
    _, dvol, spot, feats = _data()
    sig = c294.SIGNAL("iv_rv_spread", feats, 24)
    weights, _ = c294.build_weights(sig, dvol, K_EFF, H=6, r_start=24)
    pos = weights.shift(1).fillna(0.0)
    logret = feats["logret"]
    payoff, entry_turn = c294.variance_swap_proxy(pos, dvol, logret, 6, c294.wf_splits(len(dvol), 720, 168, 168))
    assert payoff.shape == (len(pos),)
    assert entry_turn.shape == (len(pos),)
    assert payoff.index.equals(pos.index)
    # entry turnover is non-negative and finite
    assert bool(np.isfinite(entry_turn.to_numpy(dtype=float)).all())
    assert bool((entry_turn.to_numpy(dtype=float) >= 0).all())


def test_c294_artifacts_exist_with_real_data_flags_and_sha256() -> None:
    parts = ("oos_sweep", "tradable_edge_registry", "summary", "verdict", "binding_constraint")
    paths = {}
    for part in parts:
        matches = sorted(ROOT.glob(f"reports/campaign294_{part}_*.json"))
        assert matches, f"missing C294 artifact for {part}"
        paths[part] = matches[-1]
        payload = json.loads(paths[part].read_text())
        assert payload.get("real_data_only") is True
        assert payload.get("fabricated_data") is False

    verdict = json.loads(paths["verdict"].read_text())
    assert verdict.get("verdict") in ("EDGE_PROVEN", "NOT_TRADABLE")
    assert verdict.get("campaign") == 294

    sweep = json.loads(paths["oos_sweep"].read_text())
    assert sweep["config"]["total_runs"] == 27
    assert sweep["aggregate"]["n_total_runs"] == 27
    run_results = sweep.get("runs", [])
    assert len(run_results) == 27
    assert all(
        set(r) >= {"feature", "lookback", "hold", "edge_proven", "oos_exposure_bars_total", "spot_pnl_sum"}
        for r in run_results
    )
    # Variance-swap-proxy diagnostic must be explicitly labeled as not executed
    for r in run_results:
        vsp = r["variance_swap_proxy"]
        assert vsp["pnl_model"] == "variance_swap_proxy"
        assert vsp["executed_fills"] is False
        assert vsp["inputs"] == "real_dvol_iv+real_realized_vol"

    registry = json.loads(paths["tradable_edge_registry"].read_text())
    assert registry["oos_sweep_sha256"] == c294.sha256_file(paths["oos_sweep"])
    assert registry["sha256_from_bytes"] == c294.sha256_file(paths["oos_sweep"])

    assert verdict["oos_sweep_sha256"] == c294.sha256_file(paths["oos_sweep"])
    assert verdict["registry_sha256"] == c294.sha256_file(paths["tradable_edge_registry"])
    assert verdict["summary_sha256"] == c294.sha256_file(paths["summary"])
    if "binding_constraint_sha256" in verdict:
        assert verdict["binding_constraint_sha256"] == c294.sha256_file(paths["binding_constraint"])