"""Tests for C317 preflight (scripts/preflight_c317.py): fail-closed verification
of the real C317 USDT-M LINEAR NATIVE 5m cross-sectional REALIZED-VOLATILITY /
HIGHER-MOMENT feature cache before the C317 runner sweeps the costed OOS grid.

These tests never fetch, impute, resample, or fabricate data. They assert the
on-disk preflight result is ready:true with no blocked reasons, that the C317
shard schema/flags/SHA256-from-bytes/push-limit are intact, that the common 5m
grid is non-empty and inside 2023-01..2025-12, that all 10 symbols have finite
positive perp_close AND finite log_return on the common grid (log_return derived
from perp_close, r[0]=0), that the funding_rate leg is all-NaN (control only),
and that the preflight exits non-zero (fail-closed) when a gate value is falsified.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import preflight_c317 as pf  # noqa: E402


def _run_preflight():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "preflight_c317.py"), "--json"],
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
    assert meta["interval"] == "5m"
    assert meta["source_interval"] == "usdt_m_5m_klines_close"
    assert meta["source_campaign"] == 312
    assert meta["n_symbols"] is not None and int(meta["n_symbols"]) >= 10
    assert meta["real_data_only"] is True
    assert meta["fabricated_data"] is False
    assert meta["executed_fills"] is False
    assert meta["under_push_limit"] is True
    assert meta["max_shard_mb"] < 100.0
    assert meta["total_shard_mb"] < 100.0
    assert meta["storage"] == "per_asset_float32_npz_shards"
    assert meta["network_ingest"] is False
    assert meta["resample"] is False


def test_preflight_shard_integrity():
    out = _run_preflight()
    shards = out["checks"]["shards"]
    assert shards["ok"] is True
    assert shards["n_shards"] >= 10
    for s, d in shards["detail"].items():
        assert d["ok"], (s, d)
        assert d["under_push_limit"] is True
        assert d["sha_ok"] is True
    assert out["checks"]["manifest"]["ok"] is True


def test_preflight_grid_in_window():
    out = _run_preflight()
    grid = out["checks"]["grid"]
    assert grid["n_symbols"] == 10
    assert grid["n_grid_bars"] > 250_000  # ~315k 5m bars over 36 months
    assert grid["in_window"] is True
    assert str(grid["grid_start_utc"]).startswith("2023-01")
    assert str(grid["grid_end_utc"]).startswith("2025-12")


def test_preflight_per_symbol_fields():
    out = _run_preflight()
    per = out["checks"]["per_symbol"]
    assert per["ok"] is True
    assert per["n_symbols"] == 10
    detail = per["detail"]
    assert len(detail) == 10
    for s, d in detail.items():
        assert d["ok"], (s, d)
        assert d["fields"]["perp_close"]["ok"], (s, d)
        assert d["fields"]["perp_close"]["all_finite_present"] is True
        assert d["fields"]["perp_close"]["all_positive_present"] is True
        # causal log-return derived from perp_close: finite everywhere, r[0]=0
        assert d["fields"]["log_return"]["ok"], (s, d)
        assert d["fields"]["log_return"]["all_finite"] is True
        assert d["fields"]["log_return"]["first_is_zero"] is True
        # USDT-M funding is unreachable -> control-only, must be all-NaN
        assert d["fields"]["funding_rate"]["ok"], (s, d)
        assert d["fields"]["funding_rate"]["all_nan_control_only"] is True


def test_preflight_fails_closed_when_meta_flag_falsified(tmp_path, monkeypatch):
    import preflight_c317 as p

    real_meta = p.CACHE_META.read_text()
    fake_meta = tmp_path / "campaign317_vol_moment_5m.meta.json"
    fake_meta.write_text(real_meta.replace('"real_data_only": true', '"real_data_only": false'))
    monkeypatch.setattr(p, "CACHE_META", fake_meta)
    monkeypatch.setattr(sys, "argv", ["preflight_c317.py"])
    rc = p.main()
    assert rc != 0, "preflight must fail-closed on falsified real_data_only"


def test_preflight_fails_closed_when_shards_missing(tmp_path, monkeypatch):
    import preflight_c317 as p

    empty_dir = tmp_path / "campaign317_vol_moment_5m"
    empty_dir.mkdir()
    monkeypatch.setattr(p, "CACHE_DIR", empty_dir)
    monkeypatch.setattr(sys, "argv", ["preflight_c317.py"])
    rc = p.main()
    assert rc != 0, "preflight must fail-closed when shards are missing"