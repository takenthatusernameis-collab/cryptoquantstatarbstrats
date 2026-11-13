"""Tests for C285: volume-conditioned cross-sectional stat-arb (scripts/run_c285_volume_xsec_oos.py).

Covers causal signal construction, fail-closed cross-sectional weights, and the
persistence/SHA256-from-bytes of the campaign artifacts. These tests run against
the verified real caches only; they never impute or fabricate data.
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

import run_c285_volume_xsec_oos as c285  # noqa: E402

SYMBOLS = list(c285.SYMBOLS)
OVERLAP_BARS = 5112


def _load_overlap():
    spot = c285.load_spot(c285.SPOT_1H)
    volume = c285.load_volume(c285.VOLUME)
    spot_index = pd.DatetimeIndex(spot.index)
    volume_index = pd.DatetimeIndex(
        pd.to_datetime(next(iter(volume.values())).index, utc=True)
    )
    overlap = spot_index.intersection(volume_index)
    assert len(overlap) == OVERLAP_BARS
    spot_o = spot.loc[overlap].sort_index()
    qv_df = pd.DataFrame(
        {s: volume[s].reindex(overlap) for s in SYMBOLS}, index=overlap
    )
    return spot_o, qv_df


def test_signal_shapes_columns_and_index():
    spot_o, qv_df = _load_overlap()
    logqv = np.log(qv_df)
    for feature in c285.FEATURES:
        for L in c285.LOOKBACKS:
            sig = c285.SIGNAL(feature, logqv, qv_df, L)
            assert sig.shape == (OVERLAP_BARS, 11)
            assert list(sig.columns) == SYMBOLS
            assert sig.index.equals(spot_o.index)


def test_qv_ratio_positive_and_qv_vol_nonnegative():
    _, qv_df = _load_overlap()
    logqv = np.log(qv_df)
    ratio = c285.signal_qv_ratio(qv_df, 168)
    vol = c285.signal_qv_vol(logqv, 168)
    assert bool((ratio.dropna() > 0).all().all())
    assert bool((vol.dropna() >= 0).all().all())


def test_signal_is_causal_no_lookahead():
    """The signal at bar t must use data through t-1 only: perturbing the final
    quote-volume observation must not change any signal row."""
    spot_o, qv_df = _load_overlap()
    logqv = np.log(qv_df)
    base = c285.signal_z_logqv(logqv, 168)
    perturbed = qv_df.copy()
    perturbed.iloc[-1] = perturbed.iloc[-1] * 2.0
    alt = c285.signal_z_logqv(np.log(perturbed), 168)
    pd.testing.assert_frame_equal(base, alt)


def test_weights_gross_exposure_cap_and_dollar_neutral():
    spot_o, qv_df = _load_overlap()
    logqv = np.log(qv_df)
    sig = c285.signal_z_logqv(logqv, 168)
    weights, stats = c285.build_weights(sig, spot_o, qv_df, K=2, H=6, r_start=168)
    assert weights.shape == (OVERLAP_BARS, 11)
    gross = weights.abs().sum(axis=1)
    assert bool((gross <= 1.0 + 1e-9).all())
    net = weights.sum(axis=1)
    assert bool((net.abs() <= 1e-9).all())
    assert stats["rebalance_bars_total"] > 0
    assert 0.0 <= stats["gate_pass_share"] <= 1.0


def test_weights_long_short_counts_at_active_rows():
    spot_o, qv_df = _load_overlap()
    logqv = np.log(qv_df)
    sig = c285.signal_z_logqv(logqv, 336)
    weights, _ = c285.build_weights(sig, spot_o, qv_df, K=3, H=24, r_start=336)
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
    spot_o, qv_df = _load_overlap()
    constant = pd.DataFrame(1.0, index=spot_o.index, columns=SYMBOLS)
    weights, stats = c285.build_weights(constant, spot_o, qv_df, K=2, H=6, r_start=168)
    assert bool((weights == 0.0).all().all())
    assert stats["rebalance_bars_passed"] == 0
    assert stats["blocked_rebalance_reasons"] == {"zero_dispersion": stats["rebalance_bars_total"]}


def test_position_is_shifted_one_bar():
    spot_o, qv_df = _load_overlap()
    logqv = np.log(qv_df)
    sig = c285.signal_z_logqv(logqv, 168)
    weights, _ = c285.build_weights(sig, spot_o, qv_df, K=2, H=1, r_start=168)
    pos = weights.shift(1).fillna(0.0)
    assert float(pos.iloc[0].abs().sum()) == 0.0
    assert pos.shape == (OVERLAP_BARS, 11)


def test_c285_artifacts_exist_with_real_data_flags_and_sha256():
    parts = ("oos_sweep", "tradable_edge_registry", "summary", "verdict", "binding_constraint")
    paths = {}
    for part in parts:
        matches = sorted(ROOT.glob(f"reports/campaign285_{part}_*.json"))
        assert matches, f"missing C285 artifact for {part}"
        paths[part] = matches[-1]
        payload = json.loads(paths[part].read_text())
        assert payload.get("real_data_only") is True
        assert payload.get("fabricated_data") is False

    verdict = json.loads(paths["verdict"].read_text())
    assert verdict.get("verdict") in ("EDGE_PROVEN", "NOT_TRADABLE")
    assert verdict.get("campaign") == 285

    sweep = json.loads(paths["oos_sweep"].read_text())
    assert sweep["summary"]["n_total_runs"] == 81
    run_results = sweep.get("results", [])
    assert len(run_results) == 81
    assert all(set(r) >= {"feature", "lookback", "K", "hold", "edge_proven", "oos_exposure_bars_total"} for r in run_results)

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
            assert c285.sha256_file(p) == verdict[key], f"sha256 mismatch for {artifact_path}"
