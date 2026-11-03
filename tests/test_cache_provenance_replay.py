"""Regression tests for cache provenance parity (blocked routes never masked).

A cache HIT must report the same blocked routes, errors, and fetch provenance
as the original cold fetch.  A hit that silently drops ``blocked_routes`` is
exactly the "cache masks failures" failure mode this campaign forbids.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pandas as pd

from data import cache as cache_mod
from data.cache import load_cached


class _FakeLoader:
    """Stand-in loader whose cold fetch records a blocked host in provenance."""

    def __init__(self, blocked_host: str = "https://api.binance.com"):
        self.blocked_host = blocked_host
        self.last_fetch_provenance: dict = {}

    def load_binance_data(self, symbols, start_date, end_date, interval="1h", quote_asset="USDT"):
        idx = pd.date_range("2024-01-01", periods=4, freq="1h", tz="UTC")
        data = pd.DataFrame({"BTC": [100.0, 101.0, 102.0, 103.0]}, index=idx)
        self.last_fetch_provenance = {
            "blocked_hosts": [self.blocked_host],
            "blocked_routes": [self.blocked_host],
            "per_symbol": {s: {"status": "ok", "bars": 4} for s in symbols},
        }
        return data


def _isolated_cache(monkeypatch):
    """Point the cache module at a private temp dir so tests never touch the
    shared ``data/cache`` directory (which holds committed real-data artifacts
    that must not be wiped)."""
    tmp = Path(tempfile.mkdtemp(prefix="coint_cache_test_"))
    monkeypatch.setattr(cache_mod, "_CACHE_DIR", tmp)
    monkeypatch.setenv("BINANCE_DATA_CACHE_DIR", str(tmp))
    cache_mod._memory_cache.clear()
    return tmp


def test_memory_cache_hit_preserves_blocked_routes(monkeypatch):
    _isolated_cache(monkeypatch)
    loader = _FakeLoader()
    data, prov_cold = load_cached(
        loader, ["BTC"], "2024-01-01", "2024-01-01", interval="1h", use_cache=True
    )
    assert prov_cold["blocked_routes"] == ["https://api.binance.com"]

    # Second call must hit the in-memory cache and STILL report blocked routes.
    data2, prov_mem = load_cached(
        loader, ["BTC"], "2024-01-01", "2024-01-01", interval="1h", use_cache=True
    )
    assert prov_mem["cache_hit"] is True
    assert prov_mem.get("memory_cache") is True
    assert prov_mem["blocked_routes"] == ["https://api.binance.com"], (
        "memory-cache HIT must replay the cold-fetch blocked routes, not mask them"
    )
    assert prov_mem.get("blocked_hosts") == ["https://api.binance.com"]


def test_disk_cache_hit_preserves_blocked_routes(monkeypatch):
    _isolated_cache(monkeypatch)
    loader = _FakeLoader()
    load_cached(
        loader, ["BTC"], "2024-01-01", "2024-01-01", interval="1h", use_cache=True
    )
    # Evict memory cache so the next read comes from disk only.
    cache_mod._memory_cache.clear()
    data, prov_disk = load_cached(
        loader, ["BTC"], "2024-01-01", "2024-01-01", interval="1h", use_cache=True
    )
    assert prov_disk["cache_hit"] is True
    assert prov_disk.get("disk_cache") is True
    assert prov_disk["blocked_routes"] == ["https://api.binance.com"]
    assert prov_disk.get("blocked_hosts") == ["https://api.binance.com"]


def test_cache_meta_persists_blocked_routes_on_disk(monkeypatch):
    _isolated_cache(monkeypatch)
    loader = _FakeLoader()
    load_cached(
        loader, ["BTC"], "2024-01-01", "2024-01-01", interval="1h", use_cache=True
    )
    meta_files = list(cache_mod._CACHE_DIR.glob("*.meta.json"))
    assert len(meta_files) == 1
    meta = json.loads(meta_files[0].read_text(encoding="utf-8"))
    assert meta.get("fetch_blocked_routes") == ["https://api.binance.com"]
    assert meta.get("fetch_blocked_hosts") == ["https://api.binance.com"]
    assert meta.get("fetch_real_data_only") is True
    assert meta.get("fetch_fabricated_data") is False


def test_cache_key_invariant_for_symbol_order(monkeypatch):
    _isolated_cache(monkeypatch)
    loader = _FakeLoader()
    _, prov_a = load_cached(
        loader, ["BTC", "ETH"], "2024-01-01", "2024-01-01", interval="1h", use_cache=False
    )
    assert prov_a["cache_hit"] is False
    # Same request, reordered symbols -> must hit the same cache entry.
    _, prov_b = load_cached(
        loader, ["ETH", "BTC"], "2024-01-01", "2024-01-01", interval="1h", use_cache=True
    )
    assert prov_b["cache_hit"] is True, (
        "symbol order must not change the cache key"
    )
