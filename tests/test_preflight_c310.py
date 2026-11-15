"""Tests for C310 preflight (scripts/preflight_c310.py): fail-closed
verification of the real C310 COIN-M inverse aggTrades OFI cache before the
C310 runner sweeps the cross-sectional OFI carry.

These tests never fetch, impute, resample, or fabricate data. They assert the
on-disk preflight result is ready:true with no blocked reasons, that the C310
cache schema/flags/SHA256-from-bytes/push-limit are intact, that the common 1h
grid equals the C307 leg_b grid (34,968 bars over 2022-07..2026-06), that all
11 COIN-M inverse perps have finite positive perp_close and finite OFI legs,
and that the preflight exits non-zero (fail-closed) when a gate value is
falsified.
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

import preflight_c310 as pf  # noqa: E402


def _run_preflight():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "preflight_c310.py"), "--json"],
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
    assert meta["source_interval"] == "coin_m_aggTrades_ms"
    assert meta["n_symbols"] is not None and int(meta["n_symbols"]) >= 11
    assert meta["real_data_only"] is True
    assert meta["fabricated_data"] is False
    assert meta["executed_fills"] is False
    assert meta["under_push_limit"] is True
    assert meta["cache_pkl_mb"] < 100.0
    assert meta["sha256_from_bytes"] == meta["actual_sha256"]
    assert meta["source_host"] == "https://data.binance.vision"


def test_preflight_grid_equals_c307_and_in_window():
    out = _run_preflight()
    grid = out["checks"]["grid"]
    assert grid["n_symbols"] == 11
    assert grid["n_grid_bars"] == 34968
    assert grid["equals_c307_leg_b_grid"] is True
    assert str(grid["grid_start_utc"]).startswith("2022-07-01")
    assert str(grid["grid_end_utc"]).startswith("2026-06")


def test_preflight_per_symbol_perp_close_and_ofi_legs_finite():
    out = _run_preflight()
    per = out["checks"]["per_symbol"]
    assert per["ok"] is True
    assert per["n_symbols"] == 11
    detail = per["detail"]
    assert len(detail) == 11
    for s, d in detail.items():
        assert d["ok"], (s, d)
        assert d["fields"]["perp_close"]["ok"], (s, d)
        for leg in ("buy_volume", "sell_volume", "signed_volume", "trade_count",
                    "trade_sign_sum", "notional", "vwap"):
            assert d["fields"][leg]["ok"], (s, leg, d)
        assert d["fields"]["funding_rate"]["ok"], (s, d)
        assert d["n_gap_bars"] >= 0
        assert d["n_trade_bars"] > 0


def test_preflight_fails_closed_when_meta_flag_falsified(tmp_path, monkeypatch):
    import preflight_c310 as p

    real_meta = p.CACHE_META.read_text()
    fake_meta = tmp_path / "campaign310_coinm_aggtrades_ofi.meta.json"
    fake_meta.write_text(real_meta.replace('"real_data_only": true', '"real_data_only": false'))
    monkeypatch.setattr(p, "CACHE_META", fake_meta)
    monkeypatch.setattr(sys, "argv", ["preflight_c310.py"])
    rc = p.main()
    assert rc != 0, "preflight must fail-closed on falsified real_data_only"