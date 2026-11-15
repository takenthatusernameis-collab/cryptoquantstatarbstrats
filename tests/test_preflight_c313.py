"""Tests for C313 preflight (scripts/preflight_c313.py): fail-closed verification
of the real COIN-M inverse quarterly term-structure carry cache before the
C313 runner sweeps the cross-sectional term-structure carry.

These tests never fetch, impute, resample, or fabricate data. They assert the
on-disk preflight result is ready:true with no blocked reasons, that the C313
shard schema/flags/SHA256-from-bytes/push-limit are intact, that the common 1h
grid is non-empty and inside 2022-07..2026-06, that all 11 COIN-M inverse perps
have finite positive perp_close and finite front/next quarterly close + annualized
basis, that >= 2 quarterly contracts overlap the perp, and that the preflight
exits non-zero (fail-closed) when a gate value is falsified.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import preflight_c313 as pf  # noqa: E402


def _run_preflight():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "preflight_c313.py"), "--json"],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout.strip())


def test_preflight_exit_zero_ready_true():
    out = _run_preflight()
    assert out.get("ready") is True
    assert out.get("blocked_reasons") == []


def test_preflight_meta_schema_and_flags():
    out = _run_preflight()
    meta = out["checks"]["meta"]
    assert meta["interval"] == "1h"
    assert meta["source_interval"] == "coin_m_klines_1h"
    assert meta["n_symbols"] is not None and int(meta["n_symbols"]) >= 11
    assert meta["real_data_only"] is True
    assert meta["fabricated_data"] is False
    assert meta["executed_fills"] is False
    assert meta["under_push_limit"] is True
    assert meta["max_shard_mb"] < 100.0
    assert meta["storage"] == "per_asset_float32_npz_shards"
    assert meta["source_host"] == "https://data.binance.vision"
    assert meta["resumable"] is True
    assert meta["total_shard_mb"] < 100.0


def test_preflight_shard_integrity():
    out = _run_preflight()
    shards = out["checks"]["shards"]
    assert shards["ok"] is True
    assert shards["n_shards"] >= 11
    for s, d in shards["detail"].items():
        assert d["ok"], (s, d)
        assert d["under_push_limit"] is True
        assert d["sha_ok"] is True
    assert out["checks"]["manifest"]["ok"] is True


def test_preflight_grid_in_window():
    out = _run_preflight()
    grid = out["checks"]["grid"]
    assert grid["n_symbols"] >= 11
    assert grid["n_grid_bars"] > 20_000  # ~35k 1h bars over 48 months
    assert grid["in_window"] is True
    assert str(grid["window_start_month"]).startswith("2022-07")
    assert str(grid["window_end_month"]).startswith("2026-06")


def test_preflight_per_asset_finite_positive():
    out = _run_preflight()
    pa = out["checks"]["per_asset"]
    assert pa["ok"] is True
    assert pa["n_symbols"] >= 11
    for s, d in pa["detail"].items():
        assert d["ok"], (s, d)
        assert d["n_bars"] > 0
        pc = d["fields"]["perp_close"]
        assert pc["ok"] and pc["nan"] == 0
        for leg in ("front_close", "next_close", "front_basis", "next_basis",
                    "front_tte_hours", "next_tte_hours"):
            assert d["fields"][leg]["ok"], (s, leg, d["fields"][leg])


def test_preflight_walk_forward_fits():
    out = _run_preflight()
    wf = out["checks"]["walk_forward"]
    assert wf["ok"] is True
    assert wf["n_splits"] >= 10
    assert wf["train_hours"] == 365 * 24
    assert wf["test_hours"] == 90 * 24
    assert wf["step_hours"] == 90 * 24
    warm = out["checks"]["feature_warmup"]
    assert warm["ok"] is True


def test_preflight_provenance_and_manifest_files():
    out = _run_preflight()
    assert out["checks"]["provenance"]["ok"] is True
    assert out["checks"]["manifest_file"]["ok"] is True


def test_preflight_fail_closed_when_cache_missing(monkeypatch):
    """Cache missing -> ready:false, blocked_reasons non-empty, exit non-zero."""
    monkeypatch.setattr(pf, "CACHE_META", ROOT / "data" / "cache" /
                        "campaign313_coinm_quarterly_carry.MISSING.json")
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "preflight_c313.py"), "--json"],
        capture_output=True, text=True,
    )
    assert proc.returncode != 0
    out = json.loads(proc.stdout.strip())
    assert out.get("ready") is False
    assert "cache_missing" in out.get("blocked_reasons", [])
    assert out.get("real_data_only") is True
    assert out.get("fabricated_data") is False
    assert out.get("executed_fills") is False