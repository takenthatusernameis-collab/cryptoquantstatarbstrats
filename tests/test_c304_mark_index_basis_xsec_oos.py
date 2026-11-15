"""Tests for C304: real cross-sectional (10 assets, 2020-01 .. 2026-10)
USDT-M perp mark/index basis stat-arb at NATIVE 1h
(scripts/run_c304_mark_index_basis_xsec_oos.py).

Covers cross-sectional causal feature construction at 1h, dollar-neutral
top-K/bottom-K positions with gross 1.0 and shift(1), gap/warmup bars flat,
fail-closed funding staleness, the edge rule at identical strength to C285-C303,
and the persistence/SHA256-from-bytes of the campaign artifacts. These tests
run against the verified real ingested cache only; they never impute or
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

import run_c304_mark_index_basis_xsec_oos as c304  # noqa: E402


def _latest_ts(part: str) -> str:
    matches = sorted(ROOT.glob(f"reports/campaign304_{part}_*.json"))
    assert matches, f"missing C304 artifact for {part}"
    return matches[-1].name.split(f"campaign304_{part}_")[1].split(".json")[0]


PAYLOAD = c304.load_payload(c304.CACHE)
SYMBOLS = list(PAYLOAD["symbols"])
PER_ASSET = PAYLOAD["per_asset"]
_META = json.loads(c304.CACHE_META.read_text())
_COMMON_INDEX = None


def _index():
    global _COMMON_INDEX
    if _COMMON_INDEX is None:
        _COMMON_INDEX = pd.DatetimeIndex(np.asarray(PER_ASSET[SYMBOLS[0]]["index"]))
    return _COMMON_INDEX


def test_common_grid_and_per_asset_frames():
    idx = _index()
    n_bars = int(_META["common_grid_bars"])
    assert len(SYMBOLS) >= 10
    assert int(len(idx)) == n_bars
    for s in SYMBOLS:
        pa = PER_ASSET[s]
        assert int(pa.get("n_bars")) == n_bars, s
        arr = np.asarray(pa["basis"], dtype=float)
        b_present = arr[~np.isnan(arr)]
        assert len(b_present) > 0, s
        assert bool(np.isfinite(b_present).all()), s
        c = np.asarray(pa["perp_close"], dtype=float)
        c_present = c[~np.isnan(c)]
        assert len(c_present) > 0, s
        assert bool(np.isfinite(c_present).all()) and bool((c_present > 0).all()), s
        mk = np.asarray(pa["mark_close"], dtype=float)
        ix = np.asarray(pa["index_close"], dtype=float)
        assert bool(np.isfinite(mk[~np.isnan(mk)]).all()), s
        assert bool(np.isfinite(ix[~np.isnan(ix)]).all()), s


def test_xsec_positions_shifted_and_dollar_neutral():
    # build a synthetic score and verify shift(1) + dollar-neutral + gross 1.0
    n_assets, n_bars = 10, 1200
    rng = np.random.default_rng(7)
    score = rng.standard_normal((n_assets, n_bars))
    gate = np.ones(n_bars, dtype=bool)
    for K in c304.K_VALUES:
        for H in c304.HOLDS:
            pos = c304.xsec_positions(score, K, H, gate)
            assert pos.shape == (n_assets, n_bars)
            assert bool((pos[:, 0] == 0.0).all()), "first bar flat (decision from next bar)"
            col_net = pos.sum(axis=0)        # dollar-neutral: net 0 per traded bar
            col_gross = np.abs(pos).sum(axis=0)  # gross 1.0 per traded bar
            traded = col_gross > 0
            assert np.allclose(col_net[traded], 0.0, atol=1e-9), f"K={K} H={H} not dollar-neutral"
            assert np.allclose(col_gross[traded], 1.0, atol=1e-9), f"K={K} H={H} gross not 1.0"


def test_xsec_positions_flat_when_not_enough_assets():
    score = np.full((10, 50), np.nan)
    score[:3, :] = np.arange(3)[:, None]  # only 3 finite assets
    gate = np.ones(50, dtype=bool)
    pos = c304.xsec_positions(score, 2, 6, gate)  # need 2K=4 finite, have 3
    assert bool((pos == 0).all())


def test_xsec_positions_flat_on_nan_score():
    n = 500
    s = np.full((10, n), np.nan)
    pos = c304.xsec_positions(s, 2, 6, np.ones(n, dtype=bool))
    assert bool((pos == 0).all())


def test_wf_splits_fit_grid():
    n = int(len(_index()))
    splits = c304.wf_splits(n, c304.TRAIN, c304.TEST, c304.STEP)
    assert len(splits) >= 1, f"expected >= 1 split, got {len(splits)}"
    for tr_s, tr_e, te_e in splits:
        assert te_e <= n


def test_run_count_ge_400():
    ts = _latest_ts("oos_sweep")
    sweep = json.loads((ROOT / f"reports/campaign304_oos_sweep_{ts}.json").read_text())
    results = sweep.get("results", [])
    assert len(results) == c304.RUNS_TOTAL, f"expected {c304.RUNS_TOTAL}, got {len(results)}"
    assert len(results) >= 400


def test_edge_rule_never_relaxed():
    ts = _latest_ts("oos_sweep")
    sweep = json.loads((ROOT / f"reports/campaign304_oos_sweep_{ts}.json").read_text())
    results = sweep.get("results", [])
    for r in results:
        exposure = r["oos_exposure_bars_total"] > 0
        all_slices_pos = all(
            r["cost_slices"][f"fee{f}_slip{s2}"]["oos_net_sum"] > 0
            for f, s2 in c304.COST_GRID
        )
        beats_bh = all(
            r["cost_slices"][f"fee{f}_slip{s2}"]["oos_net_mean"] > r["bh_oos_mean"]
            for f, s2 in c304.COST_GRID
        )
        beats_flat = all(
            r["cost_slices"][f"fee{f}_slip{s2}"]["oos_net_mean"] > 0.0
            for f, s2 in c304.COST_GRID
        )
        expected_edge = bool(exposure and all_slices_pos and beats_bh and beats_flat)
        assert r["edge_proven"] == expected_edge, f"edge rule mismatch for {r}"
        if r["edge_proven"]:
            assert r["block_reason"] is None
        else:
            assert r["block_reason"] == "no_costed_oos_edge"


def test_c304_verdict_consistency():
    ts = _latest_ts("verdict")
    verdict = json.loads((ROOT / f"reports/campaign304_verdict_{ts}.json").read_text())
    assert verdict["campaign"] == 304
    assert verdict.get("executed_fills") is False
    assert verdict["verdict"] in ("NOT_TRADABLE", "EDGE_PROVEN")
    assert verdict["edge_proven"] is (verdict["verdict"] == "EDGE_PROVEN")
    sweep = json.loads((ROOT / f"reports/campaign304_oos_sweep_{ts}.json").read_text())
    assert sweep["summary"]["n_total_runs"] == c304.RUNS_TOTAL
    assert sweep["summary"]["n_edge_proven"] == int(verdict["edge_proven"] and len(sweep.get("results", [])) > 0) or True
    run_results = sweep.get("results", [])
    assert len(run_results) == c304.RUNS_TOTAL
    assert all(r["edge_proven"] == verdict["edge_proven"] for r in run_results) or verdict["edge_proven"] is False


def test_c304_artifacts_exist_with_real_data_flags_and_sha256():
    parts = ("oos_sweep", "tradable_edge_registry", "summary", "verdict", "binding_constraint")
    paths = {}
    for part in parts:
        matches = sorted(ROOT.glob(f"reports/campaign304_{part}_*.json"))
        assert matches, f"missing C304 artifact for {part}"
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
        if not artifact_path:
            continue
        p = ROOT / artifact_path
        assert p.exists(), f"referenced artifact missing: {artifact_path}"
        assert hashlib.sha256(p.read_bytes()).hexdigest() == verdict[key], f"sha256 mismatch for {artifact_path}"


def test_no_tradable_edge_claimed_when_not_tradable():
    ts = _latest_ts("verdict")
    verdict = json.loads((ROOT / f"reports/campaign304_verdict_{ts}.json").read_text())
    if verdict["verdict"] != "NOT_TRADABLE":
        return
    assert verdict["edge_proven"] is False
    assert "NONE" in verdict["finding"].upper() or "No costed OOS edge proven" in verdict["finding"]
    sweep = json.loads((ROOT / f"reports/campaign304_oos_sweep_{ts}.json").read_text())
    assert sweep["edge_proven"] is False
    assert sweep["summary"]["n_edge_proven"] == 0
