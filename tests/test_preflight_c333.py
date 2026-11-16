"""Tests for C333 preflight (scripts/preflight_c333.py): fail-closed verification
of the real C333 USDT-M intraday MICROSTRUCTURE NOISE & EFFECTIVE SPREAD
SEASONAL DISLOCATION feature cache.

Runs the real preflight as a subprocess and asserts ready:true, the pre-registered
NaN policy, provenance flags, and the microstructure schema. No network, no
fabricated data."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run_preflight() -> dict:
    out = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "preflight_c333.py"), "--json"],
        cwd=str(ROOT), capture_output=True, text=True,
    )
    assert out.returncode == 0, out.stderr + out.stdout
    return json.loads(out.stdout)


def test_preflight_ready_on_real_cache():
    d = _run_preflight()
    assert d["ready"] is True
    assert d["blocked_reasons"] == []
    assert d["campaign"] == 333
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
    assert meta["fields"] == ["index_ms", "perp_close", "log_return", "vwap", "notional",
                              "trade_count", "signed_volume", "funding_rate"]
    assert meta["source_campaign"] == 312
    assert meta["network_ingest"] is False and meta["resample"] is False
    assert meta["total_shard_mb"] < 100.0


def test_preflight_microstructure_nan_policy():
    d = _run_preflight()
    fi = d["checks"]["feature_integrity"]
    assert fi["ok"] is True
    assert fi["raw_nan_total"] == 0
    per = fi["per_shard"]
    for sym, rep in per.items():
        assert rep["log_return_all_finite"] is True, sym
        assert rep["log_return_first_zero"] is True, sym
        assert rep["vwap_all_finite"] is True, sym
        assert rep["vwap_all_positive"] is True, sym
        assert rep["notional_all_finite"] is True, sym
        assert rep["notional_all_nonneg"] is True, sym
        assert rep["trade_count_all_finite"] is True, sym
        assert rep["trade_count_all_nonneg"] is True, sym
        assert rep["signed_volume_all_finite"] is True, sym
        assert rep["funding_all_nan_control_only"] is True, sym


def test_preflight_provenance_present():
    prov = ROOT / "data" / "cache" / "campaign333_microstructure_noise_5m.provenance.json"
    assert prov.exists()
    meta = json.loads((ROOT / "data" / "cache" / "campaign333_microstructure_noise_5m.meta.json").read_text())
    assert meta["real_data_only"] is True
    assert meta["fabricated_data"] is False
    assert meta["network_ingest"] is False
    assert meta["resample"] is False