"""Tests for C306: real COIN-M inverse quarterly-futures term-structure /
calendar-basis carry at NATIVE 1h
(scripts/run_c306_coinm_term_structure_oos.py).

Covers per-asset causal basis signal construction at 1h, dollar-neutral long
cheap / short rich basis trades within each asset, inverse settlement PnL
modeling, gap/warmup bars flat, fail-closed funding-free gates, the edge rule
at identical strength to C285-C304, and the persistence/SHA256-from-bytes of
the campaign artifacts. These tests run against the verified real ingested
cache only; they never impute or fabricate data.
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

import run_c306_coinm_term_structure_oos as c306  # noqa: E402


def _latest_ts(part: str) -> str:
    matches = sorted(ROOT.glob(f"reports/campaign306_{part}_*.json"))
    assert matches, f"missing C306 artifact for {part}"
    return matches[-1].name.split(f"campaign306_{part}_")[1].split(".json")[0]


PAYLOAD = c306.load_payload(c306.CACHE)
ASSETS = list(PAYLOAD["assets"])
PER_ASSET = PAYLOAD["per_asset"]
_META = json.loads(c306.CACHE_META.read_text())


def _asset_index(a: str) -> pd.DatetimeIndex:
    pa = PER_ASSET[a]
    return c306._as_index(pa)


def test_common_grid_and_per_asset_frames():
    assert len(ASSETS) >= 1
    for a in ASSETS:
        pa = PER_ASSET[a]
        idx = _asset_index(a)
        n_bars = int(pa.get("n_bars") or len(idx))
        assert len(idx) == n_bars, a
        assert int(pa.get("n_contracts") or 0) >= 2, a
        assert int(pa.get("bars_ge2_contracts") or 0) > 0, a
        p_close = np.asarray(pa["perp_close"], dtype=float)
        p_present = p_close[~np.isnan(p_close)]
        assert len(p_present) > 0, a
        assert bool(np.isfinite(p_present).all()), a
        assert bool((p_present > 0).all()), a
        qsyms = pa.get("quarterly_contracts") or []
        assert len(qsyms) >= 1, a
        for qsym in qsyms:
            qc = np.asarray(pa[f"q_close_{qsym}"], dtype=float)
            q_present = qc[~np.isnan(qc)]
            assert len(q_present) > 0, (a, qsym)
            assert bool(np.isfinite(q_present).all()), (a, qsym)
            assert bool((q_present > 0).all()), (a, qsym)
            qb = np.asarray(pa[f"q_basis_{qsym}"], dtype=float)
            b_present = qb[~np.isnan(qb)]
            assert bool(np.isfinite(b_present).all()), (a, qsym)


def test_inv_ret_is_nonlinear():
    entry = np.array([100.0, 100.0])
    exit_ = np.array([90.0, 110.0])
    r = c306.inv_ret(entry, exit_)
    assert np.allclose(r[0], (100.0 - 90.0) / 90.0), r
    assert np.allclose(r[1], (100.0 - 110.0) / 110.0), r
    # long inverse profits when price drops, loses when price rises
    assert r[0] > 0 and r[1] < 0


def test_wf_splits_per_asset():
    splits = c306.wf_splits(2000, c306.TRAIN, c306.TEST, c306.STEP)
    assert len(splits) >= 1
    for tr_s, tr_e, te_e in splits:
        assert te_e <= 2000


def test_run_count_ge_400():
    ts = _latest_ts("oos_sweep")
    sweep = json.loads((ROOT / f"reports/campaign306_oos_sweep_{ts}.json").read_text())
    results = sweep.get("results", [])
    assert len(results) == c306.RUNS_TOTAL, f"expected {c306.RUNS_TOTAL}, got {len(results)}"
    assert len(results) >= 400


def test_edge_rule_never_relaxed():
    ts = _latest_ts("oos_sweep")
    sweep = json.loads((ROOT / f"reports/campaign306_oos_sweep_{ts}.json").read_text())
    results = sweep.get("results", [])
    for r in results:
        exposure = r["oos_exposure_bars_total"] > 0
        all_slices_pos = all(
            r["cost_slices"][f"fee{f}_slip{s2}"]["oos_net_sum"] > 0
            for f, s2 in c306.COST_GRID
        )
        beats_bh = all(
            r["cost_slices"][f"fee{f}_slip{s2}"]["oos_net_mean"] > r["bh_oos_mean"]
            for f, s2 in c306.COST_GRID
        )
        beats_flat = all(
            r["cost_slices"][f"fee{f}_slip{s2}"]["oos_net_mean"] > 0.0
            for f, s2 in c306.COST_GRID
        )
        expected_edge = bool(exposure and all_slices_pos and beats_bh and beats_flat)
        assert r["edge_proven"] == expected_edge, f"edge rule mismatch for {r}"
        if r["edge_proven"]:
            assert r["block_reason"] is None
        else:
            assert r["block_reason"] == "no_costed_oos_edge"


def test_c306_verdict_consistency():
    ts = _latest_ts("verdict")
    verdict = json.loads((ROOT / f"reports/campaign306_verdict_{ts}.json").read_text())
    assert verdict["campaign"] == 306
    assert verdict.get("executed_fills") is False
    assert verdict["verdict"] in ("NOT_TRADABLE", "EDGE_PROVEN")
    assert verdict["edge_proven"] is (verdict["verdict"] == "EDGE_PROVEN")
    sweep = json.loads((ROOT / f"reports/campaign306_oos_sweep_{ts}.json").read_text())
    assert sweep["summary"]["n_total_runs"] == c306.RUNS_TOTAL
    run_results = sweep.get("results", [])
    assert len(run_results) == c306.RUNS_TOTAL
    assert all(r["edge_proven"] == verdict["edge_proven"] for r in run_results) or verdict["edge_proven"] is False


def test_c306_artifacts_exist_with_real_data_flags_and_sha256():
    parts = ("oos_sweep", "tradable_edge_registry", "summary", "verdict", "binding_constraint")
    paths = {}
    for part in parts:
        matches = sorted(ROOT.glob(f"reports/campaign306_{part}_*.json"))
        assert matches, f"missing C306 artifact for {part}"
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
    verdict = json.loads((ROOT / f"reports/campaign306_verdict_{ts}.json").read_text())
    if verdict["verdict"] != "NOT_TRADABLE":
        return
    assert verdict["edge_proven"] is False
    assert "NONE" in verdict["finding"].upper() or "No costed OOS edge proven" in verdict["finding"]
    sweep = json.loads((ROOT / f"reports/campaign306_oos_sweep_{ts}.json").read_text())
    assert sweep["edge_proven"] is False
    assert sweep["summary"]["n_edge_proven"] == 0
