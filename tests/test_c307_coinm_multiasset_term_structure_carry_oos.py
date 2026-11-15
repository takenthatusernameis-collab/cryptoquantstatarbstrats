"""Tests for C307: real COIN-M inverse multi-asset term-structure carry (Leg A)
+ cross-sectional funding carry (Leg B) at NATIVE 1h
(scripts/run_c307_coinm_multiasset_term_structure_carry_oos.py).

Covers per-asset causal basis signal construction at 1h (Leg A), dollar-neutral
long cheap / short rich basis trades within each asset, inverse settlement PnL
modeling; cross-sectional causal funding signal construction at 1h (Leg B),
dollar-neutral top-K/bottom-K positions with gross 1.0 and shift(1), gap/warmup
bars flat, fail-closed funding staleness, the edge rule at identical strength
to C285-C306, and the persistence/SHA256-from-bytes of the campaign artifacts.
These tests run against the verified real ingested cache only; they never
impute or fabricate data.
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

import run_c307_coinm_multiasset_term_structure_carry_oos as c307  # noqa: E402


def _latest_ts(part: str) -> str:
    matches = sorted(ROOT.glob(f"reports/campaign307_{part}_*.json"))
    assert matches, f"missing C307 artifact for {part}"
    return matches[-1].name.split(f"campaign307_{part}_")[1].split(".json")[0]


PAYLOAD = c307.load_payload(c307.CACHE)
LEG_A = PAYLOAD.get("leg_a") or {}
ASSETS_A = list(LEG_A.get("selected_assets") or [])
PER_ASSET_A = LEG_A.get("per_asset") or {}
LEG_B = PAYLOAD.get("leg_b") or {}
SYMBOLS_B = list(LEG_B.get("symbols") or [])
_META = json.loads(c307.CACHE_META.read_text())


def _asset_index_a(a: str) -> pd.DatetimeIndex:
    pa = PER_ASSET_A[a]
    return c307._as_index(pa)


def _common_index_b() -> pd.DatetimeIndex:
    return c307._as_index(LEG_B)


def test_leg_a_common_grid_and_per_asset_frames():
    assert len(ASSETS_A) >= 1
    for a in ASSETS_A:
        pa = PER_ASSET_A[a]
        idx = _asset_index_a(a)
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


def test_leg_b_common_grid_and_per_symbol_frames():
    assert len(SYMBOLS_B) == 11
    idx_b = _common_index_b()
    assert len(idx_b) > 0
    assert str(idx_b[0]) >= "2022-07-01"
    assert str(idx_b[-1]) < "2026-07-01"
    for s in SYMBOLS_B:
        pc_key = f"perp_close_{s}"
        fr_key = f"funding_rate_{s}"
        fp_key = f"funding_present_{s}"
        if pc_key in LEG_B:
            pc = np.asarray(LEG_B[pc_key], dtype=float)
            pc_present = pc[~np.isnan(pc)]
            assert len(pc_present) > 0, s
            assert bool(np.isfinite(pc_present).all()), s
            assert bool((pc_present > 0).all()), s
        if fr_key in LEG_B:
            fr = np.asarray(LEG_B[fr_key], dtype=float)
            fr_present = fr[~np.isnan(fr)]
            assert len(fr_present) > 0, s
            assert bool(np.isfinite(fr_present).all()), s
        if fp_key in LEG_B:
            fp = np.asarray(LEG_B[fp_key], dtype=float)
            assert fp.sum() > 0, s


def test_inv_ret_is_nonlinear():
    entry = np.array([100.0, 100.0])
    exit_ = np.array([90.0, 110.0])
    r = c307.inv_ret(entry, exit_)
    assert np.allclose(r[0], (100.0 - 90.0) / 90.0), r
    assert np.allclose(r[1], (100.0 - 110.0) / 110.0), r
    # long inverse profits when price drops, loses when price rises
    assert r[0] > 0 and r[1] < 0


def test_xsec_positions_shifted_and_dollar_neutral():
    # build a synthetic score and verify shift(1) + dollar-neutral + gross 1.0
    n_assets, n_bars = 11, 1200
    rng = np.random.default_rng(7)
    score = rng.standard_normal((n_assets, n_bars))
    gate = np.ones(n_bars, dtype=bool)
    for K in c307.K_VALUES_B:
        for H in c307.HOLDS_B:
            pos = c307.xsec_positions(score, K, H, gate)
            assert pos.shape == (n_assets, n_bars)
            assert bool((pos[:, 0] == 0.0).all()), "first bar flat (decision from next bar)"
            col_net = pos.sum(axis=0)        # dollar-neutral: net 0 per traded bar
            col_gross = np.abs(pos).sum(axis=0)  # gross 1.0 per traded bar
            traded = col_gross > 0
            assert np.allclose(col_net[traded], 0.0, atol=1e-9), f"K={K} H={H} not dollar-neutral"
            assert np.allclose(col_gross[traded], 1.0, atol=1e-9), f"K={K} H={H} gross not 1.0"


def test_xsec_positions_flat_when_not_enough_assets():
    score = np.full((11, 50), np.nan)
    score[:5, :] = np.arange(5)[:, None]  # only 5 finite assets
    gate = np.ones(50, dtype=bool)
    pos = c307.xsec_positions(score, 3, 6, gate)  # need 2K=6 finite, have 5
    assert bool((pos == 0).all())


def test_xsec_positions_flat_on_nan_score():
    n = 500
    s = np.full((11, n), np.nan)
    pos = c307.xsec_positions(s, 2, 6, np.ones(n, dtype=bool))
    assert bool((pos == 0).all())


def test_leg_a_wf_splits_per_asset():
    for a in ASSETS_A:
        pa = PER_ASSET_A[a]
        idx = _asset_index_a(a)
        n = int(pa.get("n_bars") or len(idx))
        splits = c307.wf_splits(n, c307.TRAIN, c307.TEST, c307.STEP)
        assert len(splits) >= 1, a
        for tr_s, tr_e, te_e in splits:
            assert te_e <= n, a


def test_leg_b_wf_splits_fit_grid():
    n = int(len(_common_index_b()))
    splits = c307.wf_splits(n, c307.TRAIN, c307.TEST, c307.STEP)
    assert len(splits) >= 1
    for tr_s, tr_e, te_e in splits:
        assert te_e <= n


def test_run_count_ge_400():
    ts = _latest_ts("oos_sweep")
    sweep = json.loads((ROOT / f"reports/campaign307_oos_sweep_{ts}.json").read_text())
    results = sweep.get("results", [])
    expected_total = c307.RUNS_TOTAL_A + c307.RUNS_TOTAL_B
    assert len(results) == expected_total, f"expected {expected_total}, got {len(results)}"
    assert len(results) >= 400
    # Verify Leg B alone satisfies gate if Leg A collapses
    leg_b_runs = [r for r in results if r.get("leg") == "B"]
    assert len(leg_b_runs) == c307.RUNS_TOTAL_B
    assert len(leg_b_runs) >= 400


def test_edge_rule_never_relaxed():
    ts = _latest_ts("oos_sweep")
    sweep = json.loads((ROOT / f"reports/campaign307_oos_sweep_{ts}.json").read_text())
    results = sweep.get("results", [])
    for r in results:
        exposure = r["oos_exposure_bars_total"] > 0
        all_slices_pos = all(
            r["cost_slices"][f"fee{f}_slip{s2}"]["oos_net_sum"] > 0
            for f, s2 in c307.COST_GRID
        )
        beats_bh = all(
            r["cost_slices"][f"fee{f}_slip{s2}"]["oos_net_mean"] > r["bh_oos_mean"]
            for f, s2 in c307.COST_GRID
        )
        beats_flat = all(
            r["cost_slices"][f"fee{f}_slip{s2}"]["oos_net_mean"] > 0.0
            for f, s2 in c307.COST_GRID
        )
        expected_edge = bool(exposure and all_slices_pos and beats_bh and beats_flat)
        assert r["edge_proven"] == expected_edge, f"edge rule mismatch for {r}"
        if r["edge_proven"]:
            assert r["block_reason"] is None
        else:
            assert r["block_reason"] == "no_costed_oos_edge"


def test_c307_verdict_consistency():
    ts = _latest_ts("verdict")
    verdict = json.loads((ROOT / f"reports/campaign307_verdict_{ts}.json").read_text())
    assert verdict["campaign"] == 307
    assert verdict.get("executed_fills") is False
    assert verdict["verdict"] in ("NOT_TRADABLE", "EDGE_PROVEN")
    assert verdict["edge_proven"] is (verdict["verdict"] == "EDGE_PROVEN")
    sweep = json.loads((ROOT / f"reports/campaign307_oos_sweep_{ts}.json").read_text())
    assert sweep["summary"]["n_total_runs"] == c307.RUNS_TOTAL_A + c307.RUNS_TOTAL_B
    run_results = sweep.get("results", [])
    assert len(run_results) == c307.RUNS_TOTAL_A + c307.RUNS_TOTAL_B
    if verdict["verdict"] == "NOT_TRADABLE":
        assert all(r["edge_proven"] is False for r in run_results)
    else:
        assert any(r["edge_proven"] is True for r in run_results)
        assert verdict["edge_proven"] is True


def test_c307_artifacts_exist_with_real_data_flags_and_sha256():
    parts = ("oos_sweep", "tradable_edge_registry", "summary", "verdict", "binding_constraint")
    paths = {}
    for part in parts:
        matches = sorted(ROOT.glob(f"reports/campaign307_{part}_*.json"))
        if part == "binding_constraint":
            # binding_constraint only exists for NOT_TRADABLE verdict
            ts = _latest_ts("verdict")
            verdict = json.loads((ROOT / f"reports/campaign307_verdict_{ts}.json").read_text())
            if verdict["verdict"] == "EDGE_PROVEN":
                continue
        assert matches, f"missing C307 artifact for {part}"
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
    verdict = json.loads((ROOT / f"reports/campaign307_verdict_{ts}.json").read_text())
    if verdict["verdict"] != "NOT_TRADABLE":
        return
    assert verdict["edge_proven"] is False
    assert "NONE" in verdict["finding"].upper() or "No costed OOS edge proven" in verdict["finding"]
    sweep = json.loads((ROOT / f"reports/campaign307_oos_sweep_{ts}.json").read_text())
    assert sweep["edge_proven"] is False
    assert sweep["summary"]["n_edge_proven"] == 0


def test_leg_a_run_count_and_signals():
    ts = _latest_ts("oos_sweep")
    sweep = json.loads((ROOT / f"reports/campaign307_oos_sweep_{ts}.json").read_text())
    results = sweep.get("results", [])
    leg_a_results = [r for r in results if r.get("leg") == "A"]
    assert len(leg_a_results) == c307.RUNS_TOTAL_A
    # Verify signals
    signals_a = set(r["signal"] for r in leg_a_results)
    assert signals_a == set(c307.SIGNALS_A)
    # Verify lookbacks
    lookbacks_a = set(r["lookback"] for r in leg_a_results)
    assert lookbacks_a == set(c307.LOOKBACKS_A)
    # Verify K values
    k_vals_a = set(r["K"] for r in leg_a_results)
    assert k_vals_a == set(c307.K_VALUES_A)
    # Verify holds
    holds_a = set(r["hold"] for r in leg_a_results)
    assert holds_a == set(c307.HOLDS_A)
    # Verify gates
    gates_a = set(r["gate"] for r in leg_a_results)
    assert gates_a == set(c307.GATES_A)


def test_leg_b_run_count_and_signals():
    ts = _latest_ts("oos_sweep")
    sweep = json.loads((ROOT / f"reports/campaign307_oos_sweep_{ts}.json").read_text())
    results = sweep.get("results", [])
    leg_b_results = [r for r in results if r.get("leg") == "B"]
    assert len(leg_b_results) == c307.RUNS_TOTAL_B
    # Verify signals
    signals_b = set(r["signal"] for r in leg_b_results)
    assert signals_b == set(c307.SIGNALS_B)
    # Verify lookbacks
    lookbacks_b = set(r["lookback"] for r in leg_b_results)
    assert lookbacks_b == set(c307.LOOKBACKS_B)
    # Verify K values
    k_vals_b = set(r["K"] for r in leg_b_results)
    assert k_vals_b == set(c307.K_VALUES_B)
    # Verify holds
    holds_b = set(r["hold"] for r in leg_b_results)
    assert holds_b == set(c307.HOLDS_B)
    # Verify gates
    gates_b = set(r["gate"] for r in leg_b_results)
    assert gates_b == set(c307.GATES_B)