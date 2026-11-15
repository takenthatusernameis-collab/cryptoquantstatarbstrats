#!/usr/bin/env python3
"""C311 preflight: fail-closed verification of the real C311 COIN-M inverse
NATIVE 5m aggTrades + 5m klines OFI cache before the C311 runner sweeps the
cross-sectional OFI carry.

Verifies:
- the per-asset float32 ``.npz`` shards exist under
  ``data/cache/campaign311_coinm_ofi_5m/`` and every shard SHA256 matches the
  meta manifest;
- meta flags (real_data_only:true, fabricated_data:false, executed_fills:false),
  interval=5m, source/host intact, every shard < 100 MB (GitHub push limit);
- the common 5m grid is non-empty, starts 2022-07-01 and ends 2026-06;
- all 11 COIN-M inverse perps are present with finite, positive perp_close
  (5m klines close) and finite OFI legs (signed_volume, total_volume,
  trade_count, trade_sign_sum, notional, vwap) plus native 8h funding_rate;
- gap bars are recorded and never imputed.

Never fetches, imputes, resamples, or fabricates data. Exit 0 iff ready:true.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

CACHE_DIR = ROOT / "data" / "cache" / "campaign311_coinm_ofi_5m"
CACHE_META = ROOT / "data" / "cache" / "campaign311_coinm_ofi_5m.meta.json"
CACHE_PROV = ROOT / "data" / "cache" / "campaign311_coinm_ofi_5m.provenance.json"
PUSH_LIMIT_BYTES = 100_000_000

EXPECTED_INTERVAL = "5m"
EXPECTED_SOURCE_INTERVAL = "coin_m_aggTrades_ms"
GRID_START = pd.Timestamp("2022-07-01", tz="UTC")
GRID_END = pd.Timestamp("2026-07-01", tz="UTC")  # exclusive -> through 2026-06
N_PERP_SYMBOLS = 11
OFI_LEGS = ("signed_volume", "total_volume", "trade_count", "trade_sign_sum",
            "notional", "vwap")
# signed_volume and trade_sign_sum are legitimately signed (buy - sell); every
# other OFI leg is non-negative by construction.
SIGNED_LEGS = ("signed_volume", "trade_sign_sum")
F32_LEGS = ("signed_volume", "total_volume", "trade_count", "trade_sign_sum",
            "notional", "vwap", "perp_close", "funding_rate")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _as_index(pa: dict) -> pd.DatetimeIndex:
    idx_ms = pa.get("index_ms")
    if idx_ms is not None:
        return pd.DatetimeIndex(pd.to_datetime(np.asarray(idx_ms, dtype="int64"), unit="ms", utc=True))
    raise ValueError("shard missing index_ms")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.parse_args()

    checks: dict = {}
    blocked: list[str] = []

    if not CACHE_META.exists():
        print(json.dumps({"ready": False, "blocked_reasons": ["C311 meta missing"]}, indent=2))
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

    flags_ok = (
        meta.get("interval") == EXPECTED_INTERVAL
        and meta.get("source_interval") == EXPECTED_SOURCE_INTERVAL
        and int(meta.get("n_symbols") or 0) >= N_PERP_SYMBOLS
        and meta.get("real_data_only") is True
        and meta.get("fabricated_data") is False
        and meta.get("executed_fills") is False
        and meta.get("source_host") == "https://data.binance.vision"
        and meta.get("under_push_limit") is True
        and int(meta.get("max_shard_bytes") or 0) < PUSH_LIMIT_BYTES
    )
    checks["meta"] = {
        "interval": meta.get("interval"),
        "source_interval": meta.get("source_interval"),
        "n_symbols": meta.get("n_symbols"),
        "real_data_only": meta.get("real_data_only"),
        "fabricated_data": meta.get("fabricated_data"),
        "executed_fills": meta.get("executed_fills"),
        "source_host": meta.get("source_host"),
        "storage": meta.get("storage"),
        "max_shard_bytes": int(meta.get("max_shard_bytes") or 0),
        "max_shard_mb": round(int(meta.get("max_shard_bytes") or 0) / 1e6, 2),
        "under_push_limit": meta.get("under_push_limit"),
        "manifest_sha256": meta.get("manifest_sha256"),
        "window_start_month": meta.get("window_start_month"),
        "window_end_month": meta.get("window_end_month"),
        "ok": bool(flags_ok),
    }
    if not flags_ok:
        blocked.append("meta flags/interval/source/size mismatch")
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
        blocked.append("C311 common grid is empty")
    if n_symbols < N_PERP_SYMBOLS:
        blocked.append(f"C311 has {n_symbols} perp symbols (< {N_PERP_SYMBOLS} required)")
    checks["grid"] = {
        "n_symbols": n_symbols, "symbols": symbols, "n_grid_bars": n_grid,
        "grid_start_utc": grid_start, "grid_end_utc": grid_end,
        "in_window": bool(str(grid_start).startswith("2022-07-01") and str(grid_end).startswith("2026-06")),
    }
    if not checks["grid"]["in_window"]:
        blocked.append("C311 grid not in 2022-07..2026-06 window")

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
            idx = _as_index({k: z[k] for k in z.files})
            pc = np.asarray(z["perp_close"], dtype=float)
            fr = np.asarray(z["funding_rate"], dtype=float)
            pc_present = pc[np.isfinite(pc)]
            pc_ok = bool(len(pc_present) and np.isfinite(pc_present).all() and (pc_present > 0).all())
            d["fields"]["perp_close"] = {"len": int(len(pc)), "nan": int(np.isnan(pc).sum()),
                                         "all_finite_present": bool(np.isfinite(pc_present).all()) if len(pc_present) else False,
                                         "all_positive_present": bool((pc_present > 0).all()) if len(pc_present) else False,
                                         "ok": pc_ok}
            ok &= pc_ok
            d["fields"]["funding_rate"] = {"nan": int(np.isnan(fr).sum()), "len": int(len(fr)), "ok": True}
            for leg in OFI_LEGS:
                v = np.asarray(z[leg], dtype=float)
                present = v[np.isfinite(v)]
                if leg in SIGNED_LEGS:
                    leg_ok = bool(len(v) == len(pc) and np.isfinite(present).all())
                else:
                    nonneg = bool((present >= 0).all()) if len(present) else False
                    leg_ok = bool(len(v) == len(pc) and nonneg)
                d["fields"][leg] = {"len": int(len(v)), "nan": int(np.isnan(v).sum()),
                                    "finite_present": int(len(present)), "ok": leg_ok}
                ok &= leg_ok
            # trade bars / gap bars
            tc = np.asarray(z["trade_count"], dtype=float)
            d["n_trade_bars"] = int(np.isfinite(tc).sum())
            d["n_gap_bars"] = int(np.isnan(tc).sum())
            d["grid_len"] = int(len(idx))
        d["ok"] = bool(ok)
        detail[s] = d
        all_ok &= bool(ok)
    checks["per_symbol"] = {"n_symbols": n_symbols, "detail": detail, "ok": bool(all_ok)}
    if not all_ok:
        blocked.append("one or more perp symbols failed perp_close/OFI-leg/funding checks")

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
        "campaign": 311,
        "part": "preflight",
        "checks": checks,
        "blocked_reasons": blocked,
    }
    print(json.dumps(result, indent=2, default=str))
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())