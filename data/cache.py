"""Disk + in-memory cache for real Binance market data.

Provides a transparent caching wrapper around ``DataLoader.load_binance_data``
so that repeated multi-timeframe / multi-symbol fetches during a campaign do
not hammer the public REST endpoints.  All data provenance (host, attempt
counts, errors) is retained in the cache metadata so audits stay honest.
"""

from __future__ import annotations

import hashlib
import json
import os
import pickle
import threading
from pathlib import Path
from typing import Any

import pandas as pd


_CACHE_DIR = Path(os.environ.get("BINANCE_DATA_CACHE_DIR", "data/cache"))
_CACHE_DIR.mkdir(parents=True, exist_ok=True)

_lock = threading.Lock()
_memory_cache: dict[str, tuple[pd.DataFrame, dict[str, Any]]] = {}


def _cache_key(symbols: list[str], start_date: str, end_date: str, interval: str, quote_asset: str) -> str:
    raw = json.dumps(
        {
            "symbols": sorted(set(symbols)),
            "start": start_date,
            "end": end_date,
            "interval": interval,
            "quote": quote_asset,
        },
        sort_keys=True,
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _cache_path(key: str) -> Path:
    return _CACHE_DIR / f"{key}.pkl"


def _meta_path(key: str) -> Path:
    return _CACHE_DIR / f"{key}.meta.json"


def load_cached(
    loader: Any,
    symbols: list[str],
    start_date: str,
    end_date: str,
    interval: str = "1h",
    quote_asset: str = "USDT",
    *,
    use_cache: bool = True,
    write_cache: bool = True,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Load real Binance data, consulting the cache first.

    Returns ``(data, provenance)`` where ``provenance`` records cache hits,
    fetch attempts, hosts tried, and errors so the campaign can prove it never
    fabricated data.
    """
    key = _cache_key(symbols, start_date, end_date, interval, quote_asset)
    provenance: dict[str, Any] = {
        "cache_key": key,
        "symbols": list(symbols),
        "start": start_date,
        "end": end_date,
        "interval": interval,
        "quote_asset": quote_asset,
        "cache_hit": False,
        "fetch_attempts": [],
        "hosts_tried": [],
        "errors": [],
    }

    if use_cache:
        with _lock:
            if key in _memory_cache:
                data, meta = _memory_cache[key]
                provenance["cache_hit"] = True
                provenance["memory_cache"] = True
                provenance.update({k: v for k, v in meta.items() if k.startswith("fetch_")})
                return data.copy(), provenance
            parquet_path = _cache_path(key)
            meta_path = _meta_path(key)
            if parquet_path.exists() and meta_path.exists():
                try:
                    with open(parquet_path, "rb") as fh:
                        data = pickle.load(fh)
                    meta = json.loads(meta_path.read_text(encoding="utf-8"))
                    provenance["cache_hit"] = True
                    provenance["disk_cache"] = True
                    provenance.update({k: v for k, v in meta.items() if k.startswith("fetch_")})
                    _memory_cache[key] = (data.copy(), meta)
                    return data.copy(), provenance
                except Exception as exc:
                    provenance["errors"].append(f"cache_read_failed: {exc}")

    # Cold fetch through the loader.
    try:
        data = loader.load_binance_data(
            symbols, start_date, end_date, interval=interval, quote_asset=quote_asset
        )
    except Exception as exc:
        provenance["errors"].append(f"loader_exception: {str(exc)[:120]}")
        raise

    provenance["fetch_attempts"].append(
        {"symbols": list(symbols), "interval": interval, "success": True, "rows": int(len(data))}
    )

    if write_cache:
        try:
            with _lock:
                parquet_path = _cache_path(key)
                meta_path = _meta_path(key)
                with open(parquet_path, "wb") as fh:
                    pickle.dump(data, fh)
                meta_path.write_text(
                    json.dumps(
                        {
                            "cache_key": key,
                            "symbols": list(symbols),
                            "start": start_date,
                            "end": end_date,
                            "interval": interval,
                            "quote_asset": quote_asset,
                            "fetch_success": True,
                            "rows": int(len(data)),
                            "columns": list(data.columns),
                        },
                        indent=2,
                    ),
                    encoding="utf-8",
                )
                _memory_cache[key] = (data.copy(), provenance)
        except Exception as exc:
            provenance["errors"].append(f"cache_write_failed: {str(exc)[:120]}")

    return data.copy(), provenance


def cache_info() -> dict[str, Any]:
    """Return summary of on-disk cache contents (for provenance blocks)."""
    entries: list[dict[str, Any]] = []
    try:
        for p in sorted(_CACHE_DIR.glob("*.meta.json")):
            try:
                meta = json.loads(p.read_text(encoding="utf-8"))
                entries.append(meta)
            except Exception:
                continue
    except Exception:
        pass
    return {
        "cache_dir": str(_CACHE_DIR),
        "entries": entries,
        "in_memory_keys": len(_memory_cache),
    }


def clear_cache() -> None:
    """Remove all cached data.  Research-only helper; never called by default."""
    with _lock:
        _memory_cache.clear()
        for p in _CACHE_DIR.glob("*"):
            try:
                p.unlink()
            except Exception:
                pass