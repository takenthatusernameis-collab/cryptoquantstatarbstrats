"""Tests for the C308 C307-edge-validation runner
(scripts/run_c308_c307_edge_validation_oos.py).

These tests never fetch, impute, resample, or fabricate data. They verify the
pure statistical helpers (inverse-settlement return, walk-forward splits, Holm
and Benjamini-Hochberg correction, one-sided p-value, cross-sectional
positions), the fail-closed C307 cache verification, the edge rule that is never
relaxed, and that the on-disk C308 artifacts are present with real-data flags and
SHA256-from-bytes integrity. They also assert the C308 verdict is internally
consistent with the emitted registry and sweep (the C307 edge was RETRACTED:
0 configs survive Holm+BH over 612; binding constraint multiple_testing).
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import run_c308_c307_edge_validation_oos as c308  # noqa: E402


def _latest_ts(part: str) -> str:
    matches = sorted(ROOT.glob(f"reports/campaign308_{part}_*.json"))
    assert matches, f"missing C308 artifact for {part}"
    return matches[-1].name.split(f"campaign308_{part}_")[1].split(".json")[0]


def _load_part(part: str) -> dict:
    ts = _latest_ts(part)
    return json.loads((ROOT / f"reports/campaign308_{part}_{ts}.json").read_text())


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------

def test_inv_coin_ret_is_nonlinear():
    entry = np.array([100.0, 100.0])
    exit_ = np.array([90.0, 110.0])
    r = c308.inv_coin_ret(entry, exit_)
    assert np.allclose(r[0], (1.0 / 100.0) - (1.0 / 90.0)), r
    assert np.allclose(r[1], (1.0 / 100.0) - (1.0 / 110.0)), r
    # long inverse-settlement return: 1/entry - 1/exit; loses when price drops,
    # gains when price rises.
    assert r[0] < 0 and r[1] > 0


def test_wf_splits_fit_grid():
    n = 34968  # C307 Leg B common funding grid bars
    splits = c308.wf_splits(n, c308.TRAIN, c308.TEST, c308.STEP)
    assert len(splits) == 203
    for tr_s, tr_e, te_e in splits:
        assert te_e <= n
        assert tr_e - tr_s == c308.TRAIN
        assert te_e - tr_e == c308.TEST


def test_holm_adjust_known_values():
    p = np.array([0.01, 0.02, 0.03, 0.04])
    adj, reject = c308.holm_adjust(p)
    assert np.allclose(adj, [0.04, 0.06, 0.06, 0.06]), adj
    assert reject.tolist() == [True, False, False, False], reject
    # adjusted p-values are always >= raw and <= 1
    assert np.all(adj >= p - 1e-12)
    assert np.all(adj <= 1.0)


def test_bh_adjust_known_values():
    p = np.array([0.01, 0.02, 0.03, 0.04])
    adj, reject = c308.bh_adjust(p)
    assert np.allclose(adj, [0.04, 0.04, 0.04, 0.04]), adj
    assert reject.tolist() == [True, True, True, True], reject
    assert np.all(adj >= p - 1e-12)
    assert np.all(adj <= 1.0)


def test_one_sided_p_direction():
    pos = np.array([0.1, 0.2, 0.15, 0.05, 0.3])
    neg = -pos
    assert c308.one_sided_p(pos) < 0.05
    assert c308.one_sided_p(neg) > 0.5
    # degenerate inputs are safe
    assert c308.one_sided_p(np.array([0.1])) == 1.0


def test_xsec_positions_shifted_and_dollar_neutral():
    n_assets, n_bars = 11, 1200
    rng = np.random.default_rng(7)
    score = rng.standard_normal((n_assets, n_bars))
    gate = np.ones(n_bars, dtype=bool)
    for K in c308.K_VALUES_B:
        for H in c308.HOLDS_B:
            pos = c308.xsec_positions(score, K, H, gate)
            assert pos.shape == (n_assets, n_bars)
            assert bool((pos[:, 0] == 0.0).all()), "first bar flat (decision from next bar)"
            col_net = pos.sum(axis=0)
            col_gross = np.abs(pos).sum(axis=0)
            traded = col_gross > 0
            assert np.allclose(col_net[traded], 0.0, atol=1e-9), f"K={K} H={H} not dollar-neutral"
            assert np.allclose(col_gross[traded], 1.0, atol=1e-9), f"K={K} H={H} gross not 1.0"


def test_xsec_positions_flat_when_not_enough_assets():
    score = np.full((11, 50), np.nan)
    score[:5, :] = np.arange(5)[:, None]  # only 5 finite assets; need 2K=6 for K=3
    gate = np.ones(50, dtype=bool)
    pos = c308.xsec_positions(score, 3, 6, gate)
    assert bool((pos == 0).all())


def test_xsec_positions_flat_on_nan_score():
    n = 500
    s = np.full((11, n), np.nan)
    pos = c308.xsec_positions(s, 2, 6, np.ones(n, dtype=bool))
    assert bool((pos == 0).all())


# ---------------------------------------------------------------------------
# Fail-closed cache verification
# ---------------------------------------------------------------------------

def test_verify_cache_flags_and_sha256():
    payload, meta, cache_sha, meta_sha, prov_sha = c308.verify_cache()
    assert cache_sha == meta["sha256_from_bytes"]
    assert cache_sha == hashlib.sha256(c308.CACHE.read_bytes()).hexdigest()
    assert meta["real_data_only"] is True
    assert meta["fabricated_data"] is False
    assert meta["executed_fills"] is False
    assert int(meta["cache_pkl_bytes"]) == c308.CACHE.stat().st_size
    assert c308.CACHE.stat().st_size < 100_000_000
    assert isinstance(payload, dict) and "leg_b" in payload
    assert prov_sha is not None


# ---------------------------------------------------------------------------
# Edge rule never relaxed + verdict/registry consistency
# ---------------------------------------------------------------------------

def test_edge_rule_never_relaxed():
    sweep = _load_part("oos_sweep")
    results = sweep.get("results", [])
    assert len(results) == c308.N_TRIALS
    for r in results:
        exposure = r["oos_exposure_bars_total"] > 0
        expected_edge = bool(
            exposure
            and r["all_cost_slices_oos_net_positive"]
            and r["beats_bh_all_slices"]
            and r["beats_flat"]
        )
        assert r["edge_proven"] == expected_edge, f"edge rule mismatch for {r}"


def test_c308_verdict_retracted_consistent():
    verdict = _load_part("verdict")
    sweep = _load_part("oos_sweep")
    registry = _load_part("tradable_edge_registry")
    summary = _load_part("summary")

    assert verdict["campaign"] == 308
    assert verdict.get("executed_fills") is False
    assert verdict["real_data_only"] is True
    assert verdict["fabricated_data"] is False

    # C307 edge retracted: 0 survive Holm AND BH over the 612 pre-registered configs.
    assert verdict["n_survive_both"] == 0
    assert verdict["n_survive_holm"] == 0
    assert verdict["edge_proven"] is False
    assert verdict["verdict"] == "RETRACTED"
    assert verdict["binding_constraint"] == "multiple_testing"

    # registry claims no tradable edge
    assert registry["n_tradable"] == 0
    assert registry["tradable_configs"] == []
    assert registry["verdict"] == "RETRACTED"

    # summary matches sweep totals
    s = sweep["summary"]
    assert s["n_total_runs"] == c308.N_TRIALS
    assert s["n_leg_a_runs"] + s["n_leg_b_runs"] == c308.N_TRIALS
    assert s["n_survive_both"] == 0
    assert s["verdict"] == "RETRACTED"
    assert summary["verdict"] == "RETRACTED"
    assert summary["binding_constraint"] == "multiple_testing"


def test_c308_artifacts_flags_and_sha256_from_bytes():
    parts = ("oos_sweep", "tradable_edge_registry", "summary", "verdict", "binding_constraint")
    for part in parts:
        payload = _load_part(part)
        assert payload.get("real_data_only") is True, part
        assert payload.get("fabricated_data") is False, part
        assert payload.get("executed_fills") is False, part

    verdict = _load_part("verdict")
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


def test_c308_attribution_edge_not_explained_by_funding():
    binding = _load_part("binding_constraint")
    # Fail-closed validation rule: convexity (not funding carry) dominates, so the
    # edge is not attributable to funding carry.
    assert binding["binding_constraint"] == "multiple_testing"
    assert binding["n_survive_both"] == 0
    assert binding["edge_explained_by_funding"] is False
    assert binding["aggregate_conv_share"] > binding["aggregate_fund_share"]