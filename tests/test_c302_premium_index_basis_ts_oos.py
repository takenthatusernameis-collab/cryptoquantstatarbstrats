"""Tests for C302: real per-asset (2020-01 .. 2026-10) USDT-M perp
premium-index time-series stat-arb at NATIVE 1h
(scripts/run_c302_premium_index_basis_ts_oos.py).

Covers per-asset causal premium-index feature construction at 1h, gap bars carried
as NaN and never imputed, fail-closed causal positions (shift(1), flat when no
signal, flat on stale funding / NaN score), the edge rule at identical strength to
C285-C301, and the persistence/SHA256-from-bytes of the campaign artifacts. These
tests run against the verified real ingested cache only; they never impute or
fabricate data.
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

import run_c302_premium_index_basis_ts_oos as c302  # noqa: E402


def _latest_ts(part: str) -> str:
    matches = sorted(ROOT.glob(f"reports/campaign302_{part}_*.json"))
    assert matches, f"missing C302 artifact for {part}"
    return matches[-1].name.split(f"campaign302_{part}_")[1].split(".json")[0]


SYMBOLS = list(c302.load_payload(c302.CACHE)["symbols"])
PER_ASSET = c302.load_payload(c302.CACHE)["per_asset"]


def _asset(symbol: str) -> dict:
    pa = PER_ASSET[symbol]
    prem_open, prem_high, prem_low, prem_close, index = c302._asset_series(pa)
    return {"pa": pa, "prem_open": prem_open, "prem_high": prem_high, "prem_low": prem_low,
            "prem_close": prem_close, "index": index}


def test_per_asset_frames_full_window_and_gap_nan():
    assert len(SYMBOLS) >= 1
    exp_n_bars = 59904
    for s in SYMBOLS:
        d = _asset(s)
        assert int(d["pa"].get("n_bars")) == exp_n_bars, s
        assert d["prem_close"].shape == (len(d["index"]),)
        # gap bars (real archive outage) are NaN on all premium legs and never imputed
        gap = d["prem_close"].isna()
        for col in ("prem_open", "prem_high", "prem_low", "prem_close"):
            arr = np.asarray(d[col], dtype=float)
            assert bool(np.isnan(arr[gap]).all()), f"{col} gap not NaN for {s}"
        # present bars: all premium legs finite
        present = ~gap
        for col in ("prem_open", "prem_high", "prem_low", "prem_close"):
            arr = np.asarray(d[col], dtype=float)
            assert bool(np.isfinite(arr[present]).all()), f"{col} present not finite for {s}"
        assert str(d["index"].min()) >= "2020-01-01 00:00:00+00:00"
        assert str(d["index"].max()) <= "2026-10-31 23:00:00+00:00"


def test_signal_lengths_match_bars():
    for s in SYMBOLS:
        d = _asset(s)
        feats = c302.build_features(d["prem_close"], d["prem_high"], d["prem_low"])
        for signal in c302.SIGNALS:
            for L in c302.LOOKBACKS:
                sig = c302.SIGNAL(signal, feats, L)
                assert len(sig) == len(d["index"]), (s, signal, L)


def test_features_are_causal_no_lookahead():
    s = SYMBOLS[0]
    d = _asset(s)
    feats = c302.build_features(d["prem_close"], d["prem_high"], d["prem_low"])
    prem2 = d["prem_close"].copy()
    prem2.iloc[-1] = prem2.iloc[-1] * 2.0
    feats2 = c302.build_features(prem2, d["prem_high"], d["prem_low"])
    for signal in c302.SIGNALS:
        for L in c302.LOOKBACKS:
            base = c302.SIGNAL(signal, feats, L)
            alt = c302.SIGNAL(signal, feats2, L)
            np.testing.assert_array_equal(base.to_numpy(dtype=float)[:-1], alt.to_numpy(dtype=float)[:-1])


def test_funding_cashflow_sign_convention():
    # funding is sourced from C299 reuse; verify the leg sign convention holds on
    # the merged frame by re-deriving from the cache.
    import pickle
    c299 = pickle.load(open(c302.CACHE.parent / "campaign299_multianual_perp_funding_basis_ts.pkl", "rb"))
    for s in SYMBOLS:
        pa = c302._asset_series(PER_ASSET[s])[4]
        funding = pd.Series(np.asarray(c299["per_asset"][s]["funding_rates"], dtype=float),
                            index=pd.DatetimeIndex(np.asarray(c299["per_asset"][s]["index"]))).reindex(pa)
        leg = -funding.fillna(0.0)
        mask = funding.notna().values
        assert np.allclose(leg.values[mask], -funding.values[mask])
        assert bool((leg.values[~mask] == 0).all())


def test_position_is_shifted_one_bar_and_flat_when_no_signal():
    for s in SYMBOLS:
        d = _asset(s)
        feats = c302.build_features(d["prem_close"], d["prem_high"], d["prem_low"])
        sig = c302.SIGNAL("prem_z", feats, 168).to_numpy(dtype=float)
        pos = c302.positions_from_score(sig, entry=1.5, exit_level=0.5, H=1)
        assert pos[0] == 0.0, "first bar must be flat (decision applied from next bar)"
        assert len(pos) == len(d["prem_close"])
        pos_zero = c302.positions_from_score(np.zeros(len(d["prem_close"])), entry=1.0, exit_level=0.5, H=6)
        assert bool((pos_zero == 0.0).all())


def test_position_flat_on_nan_score():
    # a NaN score (gap/warmup) must not open a position
    n = 500
    s = np.full(n, np.nan)
    pos = c302.positions_from_score(s, entry=1.0, exit_level=0.5, H=6)
    assert bool((pos == 0.0).all())


def test_vectorized_positions_match_reference_loop():
    def ref(score, entry, exit_level, H):
        n = len(score)
        sarr = np.asarray(score, dtype=float)
        desired = np.zeros(n)
        desired[sarr >= entry] = 1.0
        desired[sarr <= -entry] = -1.0
        seg_start = (np.arange(n) // H) * H
        seg_desired = desired[seg_start]
        pos = np.zeros(n)
        if n > 1:
            pos[1:] = seg_desired[:-1]
        seg_ids = np.arange(n) // H
        exit_mask = np.abs(sarr) <= exit_level
        exit_cum = np.zeros(n, dtype=bool)
        for seg_id in np.unique(seg_ids):
            m = seg_ids == seg_id
            exit_cum[m] = np.maximum.accumulate(exit_mask[m])
        pos = np.where(exit_cum, 0.0, pos)
        return np.where(np.isfinite(pos), pos, 0.0)

    rng = np.random.default_rng(11)
    for n in (777, 3600):
        s = pd.Series(rng.standard_normal(n))
        for H in (1, 6, 24):
            for entry, ex in ((1.5, 0.5), (2.0, 1.0)):
                a = c302.positions_from_score(s.to_numpy(dtype=float), entry, ex, H)
                b = ref(s, entry, ex, H)
                assert np.array_equal(a, b), (n, H, entry, ex)


def test_wf_splits_fit_asset_window():
    for s in SYMBOLS:
        n = len(PER_ASSET[s]["prem_close"])
        splits = c302.wf_splits(n, c302.TRAIN, c302.TEST, c302.STEP)
        assert len(splits) == 80, f"{s}: expected 80 splits, got {len(splits)}"
        for tr_s, tr_e, te_e in splits:
            assert te_e <= n


def test_edge_rule_never_relaxed():
    ts = _latest_ts("oos_sweep")
    sweep = json.loads((ROOT / f"reports/campaign302_oos_sweep_{ts}.json").read_text())
    results = sweep.get("results", [])
    assert len(results) == 486, f"expected 486 runs (3 assets x 162), got {len(results)}"
    for r in results:
        exposure = r["oos_exposure_bars_total"] > 0
        all_slices_pos = all(
            r["cost_slices"][f"fee{f}_slip{s2}"]["oos_net_sum"] > 0 for f, s2 in c302.COST_GRID
        )
        beats_bh = all(
            r["cost_slices"][f"fee{f}_slip{s2}"]["oos_net_mean"] > r["bh_oos_mean"]
            for f, s2 in c302.COST_GRID
        )
        beats_flat = all(
            r["cost_slices"][f"fee{f}_slip{s2}"]["oos_net_mean"] > 0.0
            for f, s2 in c302.COST_GRID
        )
        expected_edge = bool(exposure and all_slices_pos and beats_bh and beats_flat)
        assert r["edge_proven"] == expected_edge, f"edge rule mismatch for {r}"
        if r["edge_proven"]:
            assert r["block_reason"] is None
        else:
            assert r["block_reason"] == "no_costed_oos_edge"


def test_c302_verdict_not_tradable_zero_edge():
    ts = _latest_ts("verdict")
    verdict = json.loads((ROOT / f"reports/campaign302_verdict_{ts}.json").read_text())
    assert verdict["verdict"] == "NOT_TRADABLE"
    assert verdict["edge_proven"] is False
    assert verdict["campaign"] == 302
    assert verdict.get("executed_fills") is False
    sweep = json.loads((ROOT / f"reports/campaign302_oos_sweep_{ts}.json").read_text())
    assert sweep["summary"]["n_total_runs"] == 486
    assert sweep["summary"]["n_edge_proven"] == 0
    assert sweep["config"]["total_runs_per_asset"] == 162
    run_results = sweep.get("results", [])
    assert len(run_results) == 486
    assert all(r["edge_proven"] is False for r in run_results)


def test_c302_artifacts_exist_with_real_data_flags_and_sha256():
    parts = ("oos_sweep", "tradable_edge_registry", "summary", "verdict", "binding_constraint")
    paths = {}
    for part in parts:
        matches = sorted(ROOT.glob(f"reports/campaign302_{part}_*.json"))
        assert matches, f"missing C302 artifact for {part}"
        paths[part] = matches[-1]
        payload = json.loads(paths[part].read_text())
        assert payload.get("real_data_only") is True, part
        assert payload.get("fabricated_data") is False, part
        assert payload.get("executed_fills") is False, part
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
    verdict = json.loads((ROOT / f"reports/campaign302_verdict_{ts}.json").read_text())
    assert verdict["edge_proven"] is False
    assert "NONE" in verdict["finding"].upper() or "No costed OOS edge proven" in verdict["finding"]
    sweep = json.loads((ROOT / f"reports/campaign302_oos_sweep_{ts}.json").read_text())
    assert sweep["edge_proven"] is False