"""Tests for C330 preflight (scripts/preflight_c330.py): fail-closed verification
of the real C330 USDT-M intraday RETURN-PATH DRAWDOWN / RUNUP / PATH-EFFICIENCY
feature cache.

Runs the real preflight as a subprocess and asserts ready:true, the pre-registered
NaN policy, provenance flags, and the genuinely-distinct path-field schema. No
network, no fabricated data."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run_preflight() -> dict:
    out = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "preflight_c330.py"), "--json"],
        cwd=str(ROOT), capture_output=True, text=True,
    )
    assert out.returncode == 0, out.stderr + out.stdout
    return json.loads(out.stdout)


def test_preflight_ready_on_real_cache():
    d = _run_preflight()
    assert d["ready"] is True
    assert d["blocked_reasons"] == []
    assert d["campaign"] == 330
    assert d["real_data_only"] is True
    assert d["fabricated_data"] is False
    assert d["executed_fills"] is False


def test_preflight_grid_and_shards():
    d = _run_preflight()
    grid = d["checks"]["grid"]
    assert grid["n_symbols"] == 10
    assert grid["n_grid_bars"] == 315648
    assert grid["grid_start_utc"].startswith("2023-01")
    assert grid["grid_end_utc"].startswith("2025-12")
    assert d["checks"]["shards"]["ok"] is True
    assert d["checks"]["shards"]["n_shards"] == 10
    meta = d["checks"]["meta"]
    assert meta["fields"] == ["index_ms", "perp_close", "log_return", "cumret",
                              "drawdown", "runup", "path_eff", "funding_rate"]
    assert meta["source_campaign"] == 312
    assert meta["network_ingest"] is False and meta["resample"] is False
    assert meta["total_shard_mb"] < 100.0


def test_preflight_path_nan_policy():
    d = _run_preflight()
    fi = d["checks"]["feature_integrity"]
    assert fi["ok"] is True
    assert fi["raw_nan_total_non_patheff"] == 0
    assert fi["path_eff_nan_total"] >= 0
    per = fi["per_shard"]
    for sym, rep in per.items():
        assert rep["log_return_all_finite"] is True, sym
        assert rep["cumret_all_finite"] is True, sym
        assert rep["drawdown_all_finite"] is True, sym
        assert rep["runup_all_finite"] is True, sym
        assert rep["drawdown_first_zero"] is True, sym
        assert rep["drawdown_nonpositive"] is True, sym
        assert rep["runup_nonnegative"] is True, sym
        assert rep["path_eff_in_unit_interval"] is True, sym
        assert rep["path_eff_nan_share"] < 0.001, sym
        assert rep["path_eff_nan_all_on_zero_return_bars"] is True, sym
        assert rep["funding_all_nan_control_only"] is True, sym


def test_preflight_provenance_present():
    prov = ROOT / "data" / "cache" / "campaign330_drawdown_5m.provenance.json"
    assert prov.exists()
    meta = json.loads((ROOT / "data" / "cache" / "campaign330_drawdown_5m.meta.json").read_text())
    assert meta["real_data_only"] is True
    assert meta["fabricated_data"] is False
    assert meta["network_ingest"] is False
    assert meta["resample"] is False