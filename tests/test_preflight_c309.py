"""Tests for C309 preflight (scripts/preflight_c309.py): fail-closed
verification of the real C307 cache before the C309 runner sweeps the
premium-index & mark-perp-basis cross-sectional carry.

These tests never fetch, impute, resample, or fabricate data. They assert the
on-disk preflight result is ready:true with no blocked reasons, that the C307
cache schema/flags/SHA256-from-bytes/push-limit are intact, that the common
grid (11 COIN-M inverse perps) is within 2022-07..2026-06, that
premium_close_*/mark_close_*/perp_close_* are present and finite for all 11
perps with mark_basis = mark_close/perp_close - 1 computable, and that the
preflight exits non-zero (fail-closed) when a gate value is falsified.
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

import preflight_c309 as pf  # noqa: E402


def _run_preflight():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "preflight_c309.py"), "--json"],
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
    assert meta["n_perp_symbols"] is not None and int(meta["n_perp_symbols"]) >= 11
    assert meta["real_data_only"] is True
    assert meta["fabricated_data"] is False
    assert meta["executed_fills"] is False
    assert meta["under_push_limit"] is True
    assert meta["cache_pkl_mb"] < 100.0
    assert meta["sha256_from_bytes"] == meta["actual_sha256"]
    assert meta["source_host"] == "https://data.binance.vision"


def test_preflight_leg_b_grid_nonempty_and_in_window():
    out = _run_preflight()
    grid = out["checks"]["leg_b_grid"]
    assert grid["n_symbols"] == 11
    assert grid["n_bars"] > 0
    assert str(grid["start_utc"]).startswith("2022-07-01")
    assert str(grid["end_utc"]).startswith("2026-06")
    assert grid["n_bars"] == 34968


def test_preflight_leg_b_per_symbol_premium_mark_perp_finite():
    out = _run_preflight()
    leg_b = out["checks"]["leg_b"]
    assert leg_b["ok"] is True
    assert leg_b["n_symbols"] == 11
    detail = leg_b["detail"]
    assert len(detail) == 11
    for s, d in detail.items():
        assert d["ok"], (s, d)
        assert d["fields"][f"perp_close_{s}"]["ok"], (s, d)
        assert d["fields"][f"mark_close_{s}"]["ok"], (s, d)
        assert d["fields"][f"premium_close_{s}"]["ok"], (s, d)
        assert d["fields"]["mark_basis"]["ok"], (s, d)
        assert d["fields"][f"funding_rate_{s}"]["ok"], (s, d)
        assert d["fields"][f"funding_present_{s}"]["ok"], (s, d)


def test_preflight_fails_closed_when_meta_flag_falsified(tmp_path, monkeypatch):
    import preflight_c309 as p

    real_meta = p.CACHE_META.read_text()
    fake_meta = tmp_path / "campaign307_coinm_multiasset_term_structure_carry.meta.json"
    fake_meta.write_text(real_meta.replace('"real_data_only": true', '"real_data_only": false'))
    monkeypatch.setattr(p, "CACHE_META", fake_meta)
    monkeypatch.setattr(sys, "argv", ["preflight_c309.py"])
    rc = p.main()
    assert rc != 0, "preflight must fail-closed on falsified real_data_only"
