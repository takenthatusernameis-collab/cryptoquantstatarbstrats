"""Tests for the C312 USDT-M LINEAR NATIVE 5m cross-sectional OFI carry runner
(scripts/run_c312_usdt_m_ofi_xsec_5m_oos.py).

These tests never fetch, impute, resample, or fabricate data. They verify the
pure statistical helpers (linear-settlement return, walk-forward splits, Holm and
Benjamini-Hochberg correction, one-sided p-value, cross-sectional positions), the
fail-closed per-shard C312 cache verification, and that the on-disk C312 artifacts
are present with real-data flags and SHA256-from-bytes integrity. They also assert
the edge rule is never relaxed across all 504 pre-registered configs and that the
verdict/registry/summary are internally consistent (a formal negative recorded with
a binding constraint if nothing survives Holm AND BH; no tradability claimed
otherwise).
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

import run_c312_usdt_m_ofi_xsec_5m_oos as c312  # noqa: E402


def _latest_ts(part: str) -> str:
    matches = sorted(ROOT.glob(f"reports/campaign312_{part}_*.json"))
    matches = [m for m in matches if ".full." not in m.name]
    assert matches, f"missing C312 artifact for {part}"
    return matches[-1].name.split(f"campaign312_{part}_")[1].split(".json")[0]


def _load_part(part: str) -> dict:
    ts = _latest_ts(part)
    return json.loads((ROOT / f"reports/campaign312_{part}_{ts}.json").read_text())


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------

def test_lin_ret_of_is_linear():
    entry = np.array([100.0, 100.0])
    exit_ = np.array([90.0, 110.0])
    r = c312.lin_ret_of(entry, exit_)
    assert np.allclose(r[0], (90.0 - 100.0) / 100.0), r
    assert np.allclose(r[1], (110.0 - 100.0) / 100.0), r
    assert r[0] < 0 and r[1] > 0


def test_wf_splits_fit_grid():
    n = 315_360  # ~5m common grid bars over 2023-01..2025-12
    splits = c312.wf_splits(n, c312.TRAIN, c312.TEST, c312.STEP)
    # independent recurrence check
    expected = []
    i = 0
    while i + c312.TRAIN + c312.TEST <= n:
        expected.append(i)
        i += c312.STEP
    assert len(splits) == len(expected)
    assert splits[0] == (0, c312.TRAIN, c312.TRAIN + c312.TEST)
    for tr_s, tr_e, te_e in splits:
        assert te_e <= n
        assert tr_e - tr_s == c312.TRAIN
        assert te_e - tr_e == c312.TEST
    # step spacing
    for a, b in zip(splits, splits[1:]):
        assert b[0] - a[0] == c312.STEP


def test_holm_adjust_known_values():
    p = np.array([0.01, 0.02, 0.03, 0.04])
    adj, reject = c312.holm_adjust(p)
    assert np.allclose(adj, [0.04, 0.06, 0.06, 0.06]), adj
    assert reject.tolist() == [True, False, False, False], reject
    assert np.all(adj >= p - 1e-12)
    assert np.all(adj <= 1.0)


def test_bh_adjust_known_values():
    p = np.array([0.01, 0.02, 0.03, 0.04])
    adj, reject = c312.bh_adjust(p)
    assert np.allclose(adj, [0.04, 0.04, 0.04, 0.04]), adj
    assert reject.tolist() == [True, True, True, True], reject
    assert np.all(adj >= p - 1e-12)
    assert np.all(adj <= 1.0)


def test_one_sided_p_direction():
    pos = np.array([0.1, 0.2, 0.15, 0.05, 0.3])
    neg = -pos
    assert c312.one_sided_p(pos) < 0.05
    assert c312.one_sided_p(neg) > 0.5
    assert c312.one_sided_p(np.array([0.1])) == 1.0


def test_xsec_positions_shifted_and_dollar_neutral():
    n_assets, n_bars = 10, 1200
    rng = np.random.default_rng(7)
    score = rng.standard_normal((n_assets, n_bars))
    gate = np.ones(n_bars, dtype=bool)
    for K in c312.K_VALUES:
        for H in c312.HOLDS:
            pos = c312.xsec_positions(score, K, H, gate)
            assert pos.shape == (n_assets, n_bars)
            assert bool((pos[:, 0] == 0.0).all()), "first bar flat"
            col_net = pos.sum(axis=0)
            col_gross = np.abs(pos).sum(axis=0)
            traded = col_gross > 0
            assert np.allclose(col_net[traded], 0.0, atol=1e-9), f"K={K} H={H} not dollar-neutral"
            assert np.allclose(col_gross[traded], 1.0, atol=1e-9), f"K={K} H={H} gross not 1.0"


def test_xsec_positions_flat_when_not_enough_assets():
    score = np.full((10, 50), np.nan)
    score[:4, :] = np.arange(4)[:, None]  # only 4 finite assets; need 2K=6 for K=3
    gate = np.ones(50, dtype=bool)
    pos = c312.xsec_positions(score, 3, 6, gate)
    assert bool((pos == 0).all())


# ---------------------------------------------------------------------------
# Fail-closed per-shard cache verification
# ---------------------------------------------------------------------------

def test_verify_cache_flags_and_shard_sha256():
    payload, meta, manifest_sha, meta_sha, prov_sha = c312.verify_cache()
    assert meta["real_data_only"] is True
    assert meta["fabricated_data"] is False
    assert meta["executed_fills"] is False
    assert meta["interval"] == "5m"
    assert meta["under_push_limit"] is True
    assert meta["max_shard_bytes"] < 100_000_000
    shard_sha = meta["shard_sha256"]
    assert len(shard_sha) >= 10
    for s, expected in shard_sha.items():
        sp = c312.CACHE_DIR / f"{s}.npz"
        assert sp.exists(), s
        assert hashlib.sha256(sp.read_bytes()).hexdigest() == expected, s
        assert sp.stat().st_size < 100_000_000
    # manifest sha is sha256 over the sorted shard map
    manifest = {s: shard_sha[s] for s in sorted(shard_sha)}
    assert manifest_sha == hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()
    assert manifest_sha == meta["manifest_sha256"]
    assert isinstance(payload, dict) and "per_asset" in payload
    assert len(payload["per_asset"]) >= 10
    assert prov_sha is not None


# ---------------------------------------------------------------------------
# Pre-registered grid size + edge rule never relaxed
# ---------------------------------------------------------------------------

def test_n_trials_pre_registered_504():
    assert c312.N_TRIALS == 504
    assert len(c312.SIGNALS) == 7
    assert len(c312.LOOKBACKS) == 4
    assert len(c312.K_VALUES) == 3
    assert len(c312.HOLDS) == 3
    assert len(c312.GATES) == 2
    assert c312.LOOKBACKS == (288, 1008, 2016, 4032)
    assert c312.HOLDS == (1, 6, 24)
    assert 7 * 4 * 3 * 3 * 2 == c312.N_TRIALS


def test_edge_rule_never_relaxed():
    sweep = _load_part("oos_sweep")
    results = sweep.get("results", [])
    assert len(results) == c312.N_TRIALS
    for r in results:
        exposure = r["oos_exposure_bars_total"] > 0
        expected_edge = bool(
            exposure
            and r["all_cost_slices_oos_net_positive"]
            and r["beats_bh_all_slices"]
            and r["beats_flat"]
        )
        assert r["edge_proven"] == expected_edge, f"edge rule mismatch for {r}"


# ---------------------------------------------------------------------------
# Verdict / registry / summary consistency
# ---------------------------------------------------------------------------

def test_verdict_registry_summary_consistent():
    verdict = _load_part("verdict")
    sweep = _load_part("oos_sweep")
    registry = _load_part("tradable_edge_registry")
    summary = _load_part("summary")

    assert verdict["campaign"] == 312
    assert verdict.get("executed_fills") is False
    assert verdict["real_data_only"] is True
    assert verdict["fabricated_data"] is False

    s = sweep["summary"]
    assert s["n_total_runs"] == c312.N_TRIALS
    assert s["n_survive_both"] == verdict["n_survive_both"]
    assert s["n_survive_holm"] == verdict["n_survive_holm"]
    assert s["n_survive_bh"] == verdict["n_survive_bh"]
    assert s["n_edge_proven_deterministic"] == verdict["n_deterministic_edge"]
    assert s["verdict"] == verdict["verdict"]
    assert s["binding_constraint"] == verdict["binding_constraint"]
    assert summary["verdict"] == verdict["verdict"]
    assert summary["binding_constraint"] == verdict["binding_constraint"]

    assert registry["n_tradable"] == verdict["n_survive_both"]
    assert len(registry["tradable_configs"]) == verdict["n_survive_both"]
    assert registry["verdict"] == verdict["verdict"]

    if verdict["n_survive_both"] == 0:
        assert verdict["verdict"] == "RETRACTED"
        assert verdict["edge_proven"] is False
        assert verdict["binding_constraint"] == "multiple_testing"
        assert registry["n_tradable"] == 0
        assert registry["tradable_configs"] == []


def test_c312_artifacts_flags_and_sha256_from_bytes():
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


def test_c312_binding_constraint_multiple_testing_when_no_survivors():
    binding = _load_part("binding_constraint")
    if binding["n_survive_both"] == 0:
        assert binding["binding_constraint"] == "multiple_testing"
        assert binding["n_survive_both"] == 0


def test_c312_sweep_is_bounded_under_100mb():
    ts = _latest_ts("oos_sweep")
    p = ROOT / f"reports/campaign312_oos_sweep_{ts}.json"
    assert p.stat().st_size < 100_000_000