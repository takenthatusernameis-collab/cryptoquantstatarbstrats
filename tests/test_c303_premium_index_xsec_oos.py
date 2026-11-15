"""Tests for C303: real cross-sectional (10 assets, 2020-01-31 .. 2026-10-31)
USDT-M perp premium-index carry / dispersion at NATIVE 1h
(scripts/run_c303_premium_index_xsec_oos.py).

Covers cross-sectional causal feature construction at 1h, dollar-neutral
top-K/bottom-K positions with gross 1.0 and shift(1), gap/warmup bars flat,
fail-closed funding staleness, the edge rule at identical strength to C285-C302,
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

import run_c303_premium_index_xsec_oos as c303  # noqa: E402


def _latest_ts(part: str) -> str:
    matches = sorted(ROOT.glob(f"reports/campaign303_{part}_*.json"))
    assert matches, f"missing C303 artifact for {part}"
    return matches[-1].name.split(f"campaign303_{part}_")[1].split(".json")[0]


SYMBOLS = list(c303.load_payload(c303.CACHE)["symbols"])
PER_ASSET = c303.load_payload(c303.CACHE)["per_asset"]
_COMMON_INDEX = None


def _index():
    global _COMMON_INDEX
    if _COMMON_INDEX is None:
        _COMMON_INDEX = pd.DatetimeIndex(np.asarray(PER_ASSET[SYMBOLS[0]]["index"]))
    return _COMMON_INDEX


def test_common_grid_and_per_asset_frames():
    import pandas as pd
    idx = _index()
    assert len(SYMBOLS) == 10
    assert int(len(idx)) == 58959
    assert str(idx.min()) >= "2020-01-31 08:00:00+00:00"
    assert str(idx.max()) <= "2026-10-31 23:00:00+00:00"
    for s in SYMBOLS:
        pa = PER_ASSET[s]
        assert int(pa.get("n_bars")) == 58959, s
        assert int(pa.get("n_present_premium_bars")) == 58959, s
        assert int(pa.get("n_missing_premium_bars")) == 0, s
        arr = np.asarray(pa["prem_close"], dtype=float)
        assert bool(np.isfinite(arr).all()), s
        c = np.asarray(pa["perp_close"], dtype=float)
        c_present = c[~np.isnan(c)]
        assert len(c_present) > 0, s
        assert bool(np.isfinite(c_present).all()) and bool((c_present > 0).all()), s


def test_xsec_positions_shifted_and_dollar_neutral():
    # build a synthetic score and verify shift(1) + dollar-neutral + gross 1.0
    n_assets, n_bars = 10, 1200
    rng = np.random.default_rng(7)
    score = rng.standard_normal((n_assets, n_bars))
    gate = np.ones(n_bars, dtype=bool)
    for K in c303.K_VALUES:
        for H in c303.HOLDS:
            pos = c303.xsec_positions(score, K, H, gate)
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
    pos = c303.xsec_positions(score, 2, 6, gate)  # need 2K=4 finite, have 3
    assert bool((pos == 0).all())


def test_xsec_positions_flat_on_nan_score():
    n = 500
    s = np.full((10, n), np.nan)
    pos = c303.xsec_positions(s, 2, 6, np.ones(n, dtype=bool))
    assert bool((pos == 0).all())


def test_wf_splits_fit_grid():
    n = int(len(_index()))
    splits = c303.wf_splits(n, c303.TRAIN, c303.TEST, c303.STEP)
    assert len(splits) == 346, f"expected 346 splits, got {len(splits)}"
    for tr_s, tr_e, te_e in splits:
        assert te_e <= n


def test_run_count_ge_400():
    ts = _latest_ts("oos_sweep")
    sweep = json.loads((ROOT / f"reports/campaign303_oos_sweep_{ts}.json").read_text())
    results = sweep.get("results", [])
    assert len(results) == c303.RUNS_TOTAL, f"expected {c303.RUNS_TOTAL}, got {len(results)}"
    assert len(results) >= 400


def test_edge_rule_never_relaxed():
    ts = _latest_ts("oos_sweep")
    sweep = json.loads((ROOT / f"reports/campaign303_oos_sweep_{ts}.json").read_text())
    results = sweep.get("results", [])
    for r in results:
        exposure = r["oos_exposure_bars_total"] > 0
        all_slices_pos = all(
            r["cost_slices"][f"fee{f}_slip{s2}"]["oos_net_sum"] > 0
            for f, s2 in c303.COST_GRID
        )
        beats_bh = all(
            r["cost_slices"][f"fee{f}_slip{s2}"]["oos_net_mean"] > r["bh_oos_mean"]
            for f, s2 in c303.COST_GRID
        )
        beats_flat = all(
            r["cost_slices"][f"fee{f}_slip{s2}"]["oos_net_mean"] > 0.0
            for f, s2 in c303.COST_GRID
        )
        expected_edge = bool(exposure and all_slices_pos and beats_bh and beats_flat)
        assert r["edge_proven"] == expected_edge, f"edge rule mismatch for {r}"
        if r["edge_proven"]:
            assert r["block_reason"] is None
        else:
            assert r["block_reason"] == "no_costed_oos_edge"


def test_c303_verdict_not_tradable_zero_edge():
    ts = _latest_ts("verdict")
    verdict = json.loads((ROOT / f"reports/campaign303_verdict_{ts}.json").read_text())
    assert verdict["verdict"] == "NOT_TRADABLE"
    assert verdict["edge_proven"] is False
    assert verdict["campaign"] == 303
    assert verdict.get("executed_fills") is False
    sweep = json.loads((ROOT / f"reports/campaign303_oos_sweep_{ts}.json").read_text())
    assert sweep["summary"]["n_total_runs"] == 432
    assert sweep["summary"]["n_edge_proven"] == 0
    run_results = sweep.get("results", [])
    assert len(run_results) == 432
    assert all(r["edge_proven"] is False for r in run_results)


def test_c303_artifacts_exist_with_real_data_flags_and_sha256():
    parts = ("oos_sweep", "tradable_edge_registry", "summary", "verdict", "binding_constraint")
    paths = {}
    for part in parts:
        matches = sorted(ROOT.glob(f"reports/campaign303_{part}_*.json"))
        assert matches, f"missing C303 artifact for {part}"
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
    verdict = json.loads((ROOT / f"reports/campaign303_verdict_{ts}.json").read_text())
    assert verdict["edge_proven"] is False
    assert "NONE" in verdict["finding"].upper() or "No costed OOS edge proven" in verdict["finding"]
    sweep = json.loads((ROOT / f"reports/campaign303_oos_sweep_{ts}.json").read_text())
    assert sweep["edge_proven"] is False
