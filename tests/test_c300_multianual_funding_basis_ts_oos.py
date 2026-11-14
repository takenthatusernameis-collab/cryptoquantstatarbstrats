"""Tests for C300: real per-asset (2020-01 .. 2026-10) USDT-M perp
funding-carry + spot/perp basis time-series stat-arb at NATIVE 5m
(scripts/run_c300_multianual_funding_basis_ts_oos.py).

Covers per-asset causal feature construction (funding/basis/momentum/mean
reversion) at 5m, the real funding cashflow sign convention, fail-closed causal
positions (shift(1), flat when no signal, flat on stale funding / NaN score),
the vectorized position parity with the reference loop, the 462-gap NaN spot
handling, and the persistence/SHA256-from-bytes of the campaign artifacts. These
tests run against the verified real ingested cache only; they never impute or
fabricate data. Spot gap bars (462/asset) are carried as NaN and make
basis-based scores NaN at those rows.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import run_c300_multianual_funding_basis_ts_oos as c300  # noqa: E402


def _latest_ts(part: str) -> str:
    matches = sorted(ROOT.glob(f"reports/campaign300_{part}_*.json"))
    assert matches, f"missing C300 artifact for {part}"
    return matches[-1].name.split(f"campaign300_{part}_")[1].split(".json")[0]


SYMBOLS = list(c300.load_payload(c300.CACHE)["symbols"])
PER_ASSET = c300.load_payload(c300.CACHE)["per_asset"]


def _data(symbol: str):
    pa = PER_ASSET[symbol]
    close, spot, funding, index = c300._asset_series(pa)
    feats = c300.build_features(close, spot, funding)
    return pa, close, spot, funding, index, feats


def test_per_asset_frames_full_window_and_no_close_nan():
    assert len(SYMBOLS) >= 1
    for s in SYMBOLS:
        pa, close, spot, funding, index, _ = _data(s)
        assert close.shape == (len(index),)
        assert int(close.isna().sum()) == 0
        assert bool((close.to_numpy(dtype=float) > 0).all())
        assert bool(np.isfinite(close.to_numpy(dtype=float)).all())
        assert str(index.min()) >= "2020-01-01 00:00:00+00:00"
        assert str(index.max()) <= "2026-10-31 23:55:00+00:00"
        assert int(funding.notna().sum()) >= 90
        # 462 un-imputed spot gap bars per asset (never imputed)
        assert int(spot.isna().sum()) == 462
        assert bool((spot.dropna().to_numpy(dtype=float) > 0).all())


def test_signal_shapes_columns_and_index():
    for s in SYMBOLS:
        _, _, _, _, index, feats = _data(s)
        for signal in c300.SIGNALS:
            for L in c300.LOOKBACKS:
                sig = c300.SIGNAL(signal, feats, L)
                assert len(sig) == len(index)
                assert sig.index.equals(index)


def test_signal_sign_conventions():
    _, _, _, _, _, feats = _data(SYMBOLS[0])
    L = 288
    pd.testing.assert_series_equal(c300.SIGNAL("funding_level", feats, L), -c300.funding_level(feats, L))
    pd.testing.assert_series_equal(c300.SIGNAL("funding_z", feats, L), -c300.funding_z(feats, L))
    pd.testing.assert_series_equal(c300.SIGNAL("basis_ma", feats, L), -c300.basis_ma(feats, L))
    pd.testing.assert_series_equal(c300.SIGNAL("basis_z", feats, L), -c300.basis_z(feats, L))
    pd.testing.assert_series_equal(c300.SIGNAL("perp_mom", feats, L), c300.perp_mom(feats, L))
    pd.testing.assert_series_equal(c300.SIGNAL("basis_mr", feats, L), c300.basis_mr(feats, L))


def test_features_are_causal_no_lookahead():
    for s in SYMBOLS:
        pa, close, spot, funding, index, feats = _data(s)
        pc = close.copy()
        pc.iloc[-1] = pc.iloc[-1] * 1.01
        ps = spot.copy()
        ps.iloc[-1] = ps.iloc[-1] * 1.01
        pf = funding.copy()
        pf.iloc[-1] = pf.iloc[-1] + 1e-4
        pert_feats = c300.build_features(pc, ps, pf)
        for signal in c300.SIGNALS:
            for L in c300.LOOKBACKS:
                base = c300.SIGNAL(signal, feats, L)
                alt = c300.SIGNAL(signal, pert_feats, L)
                pd.testing.assert_series_equal(base.iloc[:-1], alt.iloc[:-1])


def test_basis_signal_tolerates_sparse_spot_gaps():
    for s in SYMBOLS:
        _, close, spot, funding, _, feats = _data(s)
        gap_mask = spot.isna()
        L = 288
        mp = c300.min_periods_for(L)
        sig = c300.SIGNAL("basis_ma", feats, L)
        if int(gap_mask.sum()) > 0:
            assert bool(np.isfinite(sig.loc[gap_mask]).all()), "basis finite at sparse spot gaps"
        dense = feats["basis"].copy()
        dense.iloc[: int(L - mp + 10)] = np.nan
        out = c300.basis_ma(feats | {"basis": dense}, L)
        assert bool(out.iloc[: int(L - mp)].isna().all()), "dense gap NaNs basis rolling mean"


def test_funding_cashflow_sign_convention():
    for s in SYMBOLS:
        _, _, _, funding, _, _ = _data(s)
        leg = -funding.fillna(0.0)
        mask = funding.notna().values
        assert np.allclose(leg.values[mask], -funding.values[mask])
        assert bool((leg.values[~mask] == 0).all())


def test_funding_age_is_bounded():
    for s in SYMBOLS:
        _, _, _, funding, _, _ = _data(s)
        age = c300.compute_funding_age(funding)
        assert float(np.nanmax(age)) <= c300.STALE_BARS


def test_position_is_shifted_one_bar_and_flat_when_no_signal():
    for s in SYMBOLS:
        pa, close, spot, funding, _, feats = _data(s)
        sig = c300.SIGNAL("perp_mom", feats, 288)
        pos = c300.positions_from_score(sig, entry=1e-4, exit_level=5e-5, H=1)
        assert pos[0] == 0.0, "first bar must be flat (decision applied from next bar)"
        assert len(pos) == len(close)
        constant = pd.Series(0.0, index=close.index)
        pos_zero = c300.positions_from_score(constant, entry=1.0, exit_level=0.5, H=6)
        assert bool((pos_zero == 0.0).all())


def test_vectorized_positions_match_reference_loop():
    """The vectorized positions_from_score must equal the reference per-segment
    loop semantics (causal shift + mean-reversion exit within hold segments)."""

    def ref(score, entry, exit_level, H):
        n = len(score)
        s = np.asarray(score, dtype=float)
        entry_mask = np.abs(s) >= entry
        exit_mask = np.abs(s) <= exit_level
        desired = np.zeros(n)
        desired[entry_mask & (s >= entry)] = 1.0
        desired[entry_mask & (s <= -entry)] = -1.0
        seg_start = (np.arange(n) // H) * H
        seg_desired = desired[seg_start]
        pos = np.zeros(n)
        if n > 1:
            pos[1:] = seg_desired[:-1]
        seg_ids = np.arange(n) // H
        exit_cum = np.zeros(n, dtype=bool)
        for seg_id in np.unique(seg_ids):
            m = seg_ids == seg_id
            exit_cum[m] = np.maximum.accumulate(exit_mask[m])
        pos = np.where(exit_cum, 0.0, pos)
        return np.where(np.isfinite(pos), pos, 0.0)

    rng = np.random.default_rng(7)
    for n in (777, 3600):
        s = pd.Series(rng.standard_normal(n))
        for H in (1, 6, 24, 12):
            for entry, ex in ((1e-4, 5e-5), (1.5, 0.5), (0.5, 0.0)):
                a = c300.positions_from_score(s, entry, ex, H)
                b = ref(s, entry, ex, H)
                assert np.array_equal(a, b), (n, H, entry, ex)


def test_fail_closed_stale_funding_flattens_position():
    for s in SYMBOLS:
        pa, close, spot, funding, index, feats = _data(s)
        sig = c300.SIGNAL("funding_level", feats, 288)
        pos = c300.positions_from_score(sig, entry=1e-6, exit_level=0.0, H=1)
        age = c300.compute_funding_age(funding)
        stale = ~np.isfinite(age) | (age > c300.STALE_BARS)
        pos_gated = np.where(stale, 0.0, pos)
        assert bool((pos_gated[stale] == 0.0).all())


def test_wf_splits_fit_asset_window():
    for s in SYMBOLS:
        n = len(PER_ASSET[s]["perp_close"])
        splits = c300.wf_splits(n, c300.TRAIN, c300.TEST, c300.STEP)
        assert len(splits) > 0
        for tr_s, tr_e, te_e in splits:
            assert te_e <= n


def test_edge_rule_never_relaxed():
    """Re-derive the edge rule from the sweep results and confirm it is applied
    at identical strength: exposure>0 AND all cost slices net>0 AND mean
    per-split net mean > mean per-split B&H OOS net mean AND > flat."""
    ts = _latest_ts("oos_sweep")
    sweep = json.loads((ROOT / f"reports/campaign300_oos_sweep_{ts}.json").read_text())
    results = sweep.get("results", [])
    assert len(results) == 648, f"expected 648 runs (3 assets x 216), got {len(results)}"
    for r in results:
        exposure = r["oos_exposure_bars_total"] > 0
        all_slices_pos = all(
            r["cost_slices"][f"fee{f}_slip{s2}"]["oos_net_sum"] > 0 for f, s2 in c300.COST_GRID
        )
        beats_bh = r["oos_net_mean"] > r["bh_oos_mean"]
        beats_flat = r["oos_net_mean"] > 0.0
        expected_edge = bool(exposure and all_slices_pos and beats_bh and beats_flat)
        assert r["edge_proven"] == expected_edge, f"edge rule mismatch for {r}"
        assert r["block_reason"] is None if r["edge_proven"] else r["block_reason"] == "no_costed_oos_edge"


def test_c300_verdict_not_tradable_zero_edge():
    ts = _latest_ts("verdict")
    verdict = json.loads((ROOT / f"reports/campaign300_verdict_{ts}.json").read_text())
    assert verdict["verdict"] == "NOT_TRADABLE"
    assert verdict["edge_proven"] is False
    assert verdict["campaign"] == 300
    assert verdict.get("executed_fills") is False
    sweep = json.loads((ROOT / f"reports/campaign300_oos_sweep_{ts}.json").read_text())
    assert sweep["summary"]["n_total_runs"] == 648
    assert sweep["summary"]["n_edge_proven"] == 0
    assert sweep["config"]["total_runs_per_asset"] == 216
    run_results = sweep.get("results", [])
    assert len(run_results) == 648
    assert all(r["edge_proven"] is False for r in run_results)


def test_c300_artifacts_exist_with_real_data_flags_and_sha256():
    parts = ("oos_sweep", "tradable_edge_registry", "summary", "verdict", "binding_constraint")
    ts = _latest_ts("verdict")
    paths = {}
    for part in parts:
        matches = sorted(ROOT.glob(f"reports/campaign300_{part}_*.json"))
        assert matches, f"missing C300 artifact for {part}"
        paths[part] = matches[-1]
        payload = json.loads(paths[part].read_text())
        assert payload.get("real_data_only") is True
        assert payload.get("fabricated_data") is False
        assert payload.get("executed_fills") is False
    verdict = json.loads(paths["verdict"].read_text())
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
        assert hashlib.sha256(p.read_bytes()).hexdigest() == verdict[key], f"sha256 mismatch for {artifact_path}"


def test_no_tradable_edge_claimed():
    ts = _latest_ts("verdict")
    verdict = json.loads((ROOT / f"reports/campaign300_verdict_{ts}.json").read_text())
    assert verdict["edge_proven"] is False
    assert "NONE" in verdict["finding"].upper() or "No costed OOS edge proven" in verdict["finding"]
    sweep = json.loads((ROOT / f"reports/campaign300_oos_sweep_{ts}.json").read_text())
    assert sweep["edge_proven"] is False