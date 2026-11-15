"""Tests for C308 preflight (scripts/preflight_c308.py): fail-closed
verification of the real C307 cache before the C308 runner validates the
C307 edge.

These tests never fetch, impute, resample, or fabricate data. They assert the
on-disk preflight result is ready:true with no blocked reasons, that the C307
cache schema/flags/SHA256-from-bytes/push-limit are intact, that the common
funding grid (Leg B) has required properties, that the 44 C307 edge configs are
reproducible from the cache, and that the preflight exits non-zero (fail-closed)
when a gate value is falsified.
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

import preflight_c308 as pf  # noqa: E402


def _run_preflight():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "preflight_c308.py"), "--json"],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout.strip())


def test_preflight_exit_zero_ready_true():
    out = _run_preflight()
    assert out.get("ready") is True
    assert out.get("blocked_reasons") == []


def test_preflight_cache_schema_and_flags():
    out = _run_preflight()
    meta = out["checks"]["meta"]
    assert meta["interval"] == "1h"
    assert meta["source_interval"] == "coin_m_klines_1h"
    assert meta["n_assets"] is not None and int(meta["n_assets"]) >= 1
    assert meta["real_data_only"] is True
    assert meta["fabricated_data"] is False
    assert meta["executed_fills"] is False
    assert meta["cache_format"] == "plain_numpy_ndarrays_no_pandas_legs"
    assert meta["under_push_limit"] is True
    assert meta["cache_pkl_mb"] < 100.0
    assert meta["sha256_from_bytes"] == meta["actual_sha256"]
    assert meta["source_host"] == "https://data.binance.vision"


def test_preflight_leg_b_grid_nonempty_and_in_window():
    out = _run_preflight()
    grid = out["checks"]["leg_b_grid"]
    assert grid["ok"] is True
    assert grid["n_symbols"] == 11
    assert grid["n_bars"] > 0
    assert grid["window_start_utc"] >= "2022-07-01"
    assert grid["window_end_utc"] < "2026-07-01"
    assert grid["n_bars"] == 34968


def test_preflight_leg_b_per_symbol_frames_present_finite():
    out = _run_preflight()
    leg_b = out["checks"]["leg_b"]
    assert leg_b["ok"] is True
    assert leg_b["n_symbols"] == 11
    assert leg_b["n_assets_with_funding"] >= 10  # need 2*K=10 for K=5
    detail = leg_b["detail"]
    assert len(detail) == 11
    for s, d in detail.items():
        assert d["ok"], (s, d)
        assert d["fields"][f"perp_close_{s}"]["ok"], (s, d)
        assert d["fields"][f"funding_rate_{s}"]["ok"], (s, d)
        assert d["fields"][f"funding_present_{s}"]["ok"], (s, d)


def test_preflight_leg_b_reproducibility_44_edge():
    out = _run_preflight()
    repro = out["checks"]["leg_b_reproducibility"]
    assert repro["ok"] is True
    assert repro["n_runs"] == 432
    assert repro["n_edge_proven"] == 44
    assert set(repro["edge_signals"]) <= {"fund_level", "fund_z", "fund_sign"}
    assert set(repro["edge_lookbacks"]) <= {720, 1440}
    assert set(repro["edge_K"]) <= {2, 3, 5}
    assert set(repro["edge_holds"]) <= {1, 6, 24}
    assert set(repro["edge_gates"]) <= {"off"}


def test_preflight_c307_artifact_set_present():
    out = _run_preflight()
    arts = out["checks"]["c307_artifacts"]
    assert arts["ok"] is True
    for part in ("oos_sweep", "tradable_edge_registry", "summary", "verdict"):
        d = arts["detail"][part]
        assert d["exists"] is True, part
        assert d["latest"] is not None, part
        assert d["real_data_only"] is True, part
        assert d["fabricated_data"] is False, part
        assert d["executed_fills"] is False, part
        assert d["flags_ok"] is True, part


def test_preflight_provenance_present():
    out = _run_preflight()
    prov = out["checks"]["provenance"]
    assert prov["exists"] is True
    assert prov["ok"] is True


def test_preflight_fails_closed_when_meta_flag_falsified(tmp_path, monkeypatch):
    """A falsified real_data_only flag must make the preflight fail-closed."""
    import preflight_c308 as p

    real_meta = p.CACHE_META.read_text()
    fake_meta = tmp_path / "campaign307_coinm_multiasset_term_structure_carry.meta.json"
    fake_meta.write_text(real_meta.replace('"real_data_only": true', '"real_data_only": false'))
    monkeypatch.setattr(p, "CACHE_META", fake_meta)
    monkeypatch.setattr(sys, "argv", ["preflight_c308.py"])
    rc = p.main()
    assert rc != 0, "preflight must fail-closed on falsified real_data_only"