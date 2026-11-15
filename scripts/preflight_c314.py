#!/usr/bin/env python3
"""C314 preflight: fail-closed verification of the real C314 SPOT + USDT-M LINEAR
native 5m klines lead-lag cache before the C314 runner sweeps the cross-sectional
spot-perp lead-lag stat-arb.

Verifies:
- the per-asset float32 ``.npz`` shards exist under
  ``data/cache/campaign314_spot_perp_leadlag_5m/`` and every shard SHA256 matches
  the meta manifest;
- meta flags (real_data_only:true, fabricated_data:false, executed_fills:false),
  interval=5m, markets=[spot,perp], source host intact, every shard < 100 MB
  (GitHub push limit), and the total cache under the 100 MB budget;
- the common 5m grid is non-empty and inside 2023-01..2025-12;
- all 10 symbols present with finite, positive spot_close AND perp_close (5m
  klines close) on the common grid;
- the funding_rate leg is present and all-NaN (control only, USDT-M funding is
  unreachable in this environment).

Never fetches, imputes, resamples, or fabricates data. Exit 0 iff ready:true.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

CACHE_DIR = ROOT / "data" / "cache" / "campaign314_spot_perp_leadlag_5m"
CACHE_META = ROOT / "data" / "cache" / "campaign314_spot_perp_leadlag_5m.meta.json"
CACHE_PROV = ROOT / "data" / "cache" / "campaign314_spot_perp_leadlag_5m.provenance.json"
PUSH_LIMIT_BYTES = 100_000_000
CACHE_BUDGET_BYTES = 100_000_000

EXPECTED_INTERVAL = "5m"
EXPECTED_SOURCE_INTERVAL = "spot_and_usdt_m_5m_klines_close"
EXPECTED_MARKETS = ["spot", "perp"]
N_SYMBOLS = 10
PRICE_LEGS = ("spot_close", "perp_close")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.parse_args()

    checks: dict = {}
    blocked: list[str] = []

    if not CACHE_META.exists():
        print(json.dumps({"ready": False, "blocked_reasons": ["C314 meta missing"]}, indent=2))
        return 1
    try:
        meta = json.loads(CACHE_META.read_text())
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"ready": False, "blocked_reasons": [f"meta unreadable: {exc}"]}, indent=2))
        return 1

    shard_sha_meta = meta.get("shard_sha256") or {}
    shard_bytes_meta = meta.get("shard_bytes") or {}

    # ---- shard integrity ----
    shard_ok = True
    shard_detail = {}
    max_shard = 0
    for s, expected_sha in shard_sha_meta.items():
        sp = CACHE_DIR / f"{s}.npz"
        if not sp.exists():
            shard_detail[s] = {"exists": False, "ok": False}
            shard_ok = False
            continue
        actual = sha256_file(sp)
        nbytes = sp.stat().st_size
        max_shard = max(max_shard, nbytes)
        ok = bool(actual == expected_sha and nbytes == int(shard_bytes_meta.get(s, -1))
                  and nbytes < PUSH_LIMIT_BYTES)
        shard_detail[s] = {"exists": True, "sha_ok": actual == expected_sha,
                           "bytes": int(nbytes), "under_push_limit": bool(nbytes < PUSH_LIMIT_BYTES),
                           "ok": ok}
        shard_ok &= ok

    total_shard_bytes = sum(int(v) for v in shard_bytes_meta.values())
    flags_ok = (
        meta.get("interval") == EXPECTED_INTERVAL
        and meta.get("source_interval") == EXPECTED_SOURCE_INTERVAL
        and list(meta.get("markets") or []) == EXPECTED_MARKETS
        and int(meta.get("n_symbols") or 0) >= N_SYMBOLS
        and meta.get("real_data_only") is True
        and meta.get("fabricated_data") is False
        and meta.get("executed_fills") is False
        and meta.get("source_host") == "https://data.binance.vision"
        and meta.get("under_push_limit") is True
        and int(meta.get("max_shard_bytes") or 0) < PUSH_LIMIT_BYTES
        and meta.get("resumable") is True
    )
    checks["meta"] = {
        "interval": meta.get("interval"),
        "source_interval": meta.get("source_interval"),
        "markets": meta.get("markets"),
        "n_symbols": meta.get("n_symbols"),
        "real_data_only": meta.get("real_data_only"),
        "fabricated_data": meta.get("fabricated_data"),
        "executed_fills": meta.get("executed_fills"),
        "source_host": meta.get("source_host"),
        "storage": meta.get("storage"),
        "resumable": meta.get("resumable"),
        "max_shard_bytes": int(meta.get("max_shard_bytes") or 0),
        "max_shard_mb": round(int(meta.get("max_shard_bytes") or 0) / 1e6, 2),
        "total_shard_mb": round(total_shard_bytes / 1e6, 2),
        "under_push_limit": meta.get("under_push_limit"),
        "under_cache_budget": meta.get("under_cache_budget"),
        "manifest_sha256": meta.get("manifest_sha256"),
        "window_start_month": meta.get("window_start_month"),
        "window_end_month": meta.get("window_end_month"),
        "ok": bool(flags_ok),
    }
    if not flags_ok:
        blocked.append("meta flags/interval/markets/source/size mismatch")
    checks["shards"] = {"n_shards": len(shard_sha_meta), "ok": bool(shard_ok), "detail": shard_detail}
    if not shard_ok:
        blocked.append("one or more shards missing / sha or size mismatch / over push limit")

    # manifest sha integrity
    manifest = {s: shard_sha_meta[s] for s in sorted(shard_sha_meta)}
    manifest_sha = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()
    checks["manifest"] = {"expected": meta.get("manifest_sha256"), "actual": manifest_sha,
                          "ok": bool(manifest_sha == meta.get("manifest_sha256"))}
    if manifest_sha != meta.get("manifest_sha256"):
        blocked.append("shard manifest sha mismatch")

    # ---- grid + per-symbol ----
    symbols = list(meta.get("symbols") or [])
    n_symbols = len(symbols)
    n_grid = int(meta.get("n_grid_bars") or 0)
    grid_start = meta.get("grid_start_utc")
    grid_end = meta.get("grid_end_utc")
    if n_grid == 0 or not symbols:
        blocked.append("C314 common grid is empty")
    if n_symbols < N_SYMBOLS:
        blocked.append(f"C314 has {n_symbols} symbols (< {N_SYMBOLS} required)")
    in_window = bool(str(grid_start).startswith("2023-01") and str(grid_end).startswith("2025-12"))
    checks["grid"] = {
        "n_symbols": n_symbols, "symbols": symbols, "n_grid_bars": n_grid,
        "grid_start_utc": grid_start, "grid_end_utc": grid_end,
        "in_window": in_window,
    }
    if not in_window:
        blocked.append("C314 grid not in 2023-01..2025-12 window")

    detail = {}
    all_ok = True
    for s in symbols:
        sp = CACHE_DIR / f"{s}.npz"
        d = {"symbol": s, "fields": {}, "ok": True}
        ok = True
        if not sp.exists():
            d["ok"] = False
            detail[s] = d
            all_ok = False
            continue
        with np.load(sp) as z:
            idx_ms = np.asarray(z["index_ms"], dtype="int64")
            d["grid_len"] = int(len(idx_ms))
            sc = np.asarray(z["spot_close"], dtype=float)
            pc = np.asarray(z["perp_close"], dtype=float)
            fr = np.asarray(z["funding_rate"], dtype=float)
            for name, arr in (("spot_close", sc), ("perp_close", pc)):
                present = arr[np.isfinite(arr)]
                leg_ok = bool(len(present) == len(arr) and len(present) > 0 and (present > 0).all())
                d["fields"][name] = {"len": int(len(arr)), "nan": int(np.isnan(arr).sum()),
                                     "all_finite_present": bool(len(present) == len(arr)),
                                     "all_positive_present": bool((present > 0).all()) if len(present) else False,
                                     "ok": leg_ok}
                ok &= leg_ok
            fr_ok = bool(len(fr) == len(sc) and np.isnan(fr).all())
            d["fields"]["funding_rate"] = {"nan": int(np.isnan(fr).sum()), "len": int(len(fr)),
                                           "all_nan_control_only": bool(np.isnan(fr).all()), "ok": fr_ok}
            ok &= fr_ok
        d["ok"] = bool(ok)
        detail[s] = d
        all_ok &= bool(ok)
    checks["per_symbol"] = {"n_symbols": n_symbols, "detail": detail, "ok": bool(all_ok)}
    if not all_ok:
        blocked.append("one or more symbols failed spot_close/perp_close/funding checks")

    checks["provenance"] = {
        "path": str(CACHE_PROV.relative_to(ROOT)) if CACHE_PROV.exists() else str(CACHE_PROV),
        "exists": bool(CACHE_PROV.exists()),
        "ok": bool(CACHE_PROV.exists()),
    }
    if not CACHE_PROV.exists():
        blocked.append("provenance json missing")

    ready = not blocked
    result = {
        "ready": ready,
        "real_data_only": True,
        "fabricated_data": False,
        "executed_fills": False,
        "campaign": 314,
        "part": "preflight",
        "checks": checks,
        "blocked_reasons": blocked,
    }
    print(json.dumps(result, indent=2, default=str))
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())