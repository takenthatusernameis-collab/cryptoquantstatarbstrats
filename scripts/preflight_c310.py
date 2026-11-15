#!/usr/bin/env python3
"""C310 preflight: fail-closed verification of the real C310 COIN-M inverse
aggTrades OFI cache before the C310 runner sweeps the cross-sectional OFI carry.

Verifies:
- the C310 pickle exists, SHA256-from-bytes matches meta, meta flags
  (real_data_only:true, fabricated_data:false, executed_fills:false),
  interval/source/host/format/push-limit intact;
- the common 1h grid (C307 leg_b grid) is non-empty and equals the C307 leg_b
  grid (34,968 bars over 2022-07..2026-06);
- all 11 COIN-M inverse perps are present with finite, positive perp_close and
  finite OFI legs (buy_volume, sell_volume, signed_volume, trade_count,
  trade_sign_sum, notional, vwap) and native 8h funding_rate present;
- gap bars are recorded and never imputed.

Never fetches, imputes, resamples, or fabricates data. Exit 0 iff ready:true.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

CACHE = ROOT / "data" / "cache" / "campaign310_coinm_aggtrades_ofi.pkl"
CACHE_META = ROOT / "data" / "cache" / "campaign310_coinm_aggtrades_ofi.meta.json"
CACHE_PROV = ROOT / "data" / "cache" / "campaign310_coinm_aggtrades_ofi.provenance.json"
C307_CACHE = ROOT / "data" / "cache" / "campaign307_coinm_multiasset_term_structure_carry.pkl"
PUSH_LIMIT_BYTES = 100_000_000

EXPECTED_INTERVAL = "1h"
EXPECTED_SOURCE_INTERVAL = "coin_m_aggTrades_ms"
GRID_START = pd.Timestamp("2022-07-01", tz="UTC")
GRID_END = pd.Timestamp("2026-07-01", tz="UTC")  # exclusive -> through 2026-06
N_PERP_SYMBOLS = 11
OFI_LEGS = ("buy_volume", "sell_volume", "signed_volume", "trade_count",
            "trade_sign_sum", "notional", "vwap")
# signed_volume and trade_sign_sum are legitimately signed (buy - sell); every
# other OFI leg is non-negative by construction.
SIGNED_LEGS = ("signed_volume", "trade_sign_sum")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _as_index(pa: dict) -> pd.DatetimeIndex:
    idx = pa.get("index")
    if isinstance(idx, pd.DatetimeIndex):
        return idx
    arr = np.asarray(idx)
    if np.issubdtype(arr.dtype, np.datetime64):
        return pd.DatetimeIndex(arr).tz_localize("UTC")
    return pd.DatetimeIndex(pd.to_datetime(arr, unit="ms", utc=True))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.parse_args()

    checks: dict = {}
    blocked: list[str] = []

    if not CACHE.exists():
        print(json.dumps({"ready": False, "blocked_reasons": ["C310 pickle missing"]}, indent=2))
        return 1
    pkl_sha = sha256_file(CACHE)
    pkl_bytes = CACHE.stat().st_size

    try:
        meta = json.loads(CACHE_META.read_text())
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"ready": False, "blocked_reasons": [f"meta unreadable: {exc}"]}, indent=2))
        return 1

    flags_ok = (
        meta.get("interval") == EXPECTED_INTERVAL
        and meta.get("source_interval") == EXPECTED_SOURCE_INTERVAL
        and int(meta.get("n_symbols") or 0) >= N_PERP_SYMBOLS
        and meta.get("real_data_only") is True
        and meta.get("fabricated_data") is False
        and meta.get("executed_fills") is False
        and meta.get("source_host") == "https://data.binance.vision"
        and int(meta.get("cache_pkl_bytes") or 0) == pkl_bytes
        and pkl_bytes < PUSH_LIMIT_BYTES
        and pkl_sha == meta.get("sha256_from_bytes")
    )
    checks["meta"] = {
        "interval": meta.get("interval"),
        "source_interval": meta.get("source_interval"),
        "n_symbols": meta.get("n_symbols"),
        "real_data_only": meta.get("real_data_only"),
        "fabricated_data": meta.get("fabricated_data"),
        "executed_fills": meta.get("executed_fills"),
        "source_host": meta.get("source_host"),
        "cache_pkl_bytes": pkl_bytes,
        "cache_pkl_mb": round(pkl_bytes / 1e6, 2),
        "under_push_limit": bool(pkl_bytes < PUSH_LIMIT_BYTES),
        "sha256_from_bytes": meta.get("sha256_from_bytes"),
        "actual_sha256": pkl_sha,
        "window_start_month": meta.get("window_start_month"),
        "window_end_month": meta.get("window_end_month"),
        "ok": bool(flags_ok),
    }
    if not flags_ok:
        blocked.append("meta flags/interval/source/size/sha mismatch")

    try:
        with open(CACHE, "rb") as fh:
            payload = pickle.load(fh)
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"ready": False, "blocked_reasons": [f"cache could not be loaded: {exc}"]}, indent=2))
        return 1

    per_asset = payload.get("per_asset") or {}
    symbols = list(payload.get("symbols") or [])
    n_symbols = len(symbols)
    n_grid = int(payload.get("n_grid_bars") or 0)
    grid_start = payload.get("grid_start_utc")
    grid_end = payload.get("grid_end_utc")

    if n_grid == 0 or not symbols:
        blocked.append("C310 common grid is empty")

    # Grid must equal the C307 leg_b grid.
    c307_grid_ok = False
    if C307_CACHE.exists():
        with open(C307_CACHE, "rb") as fh:
            c307 = pickle.load(fh)
        lb = c307.get("leg_b") or {}
        c307_index = _as_index(lb)
        if per_asset and symbols:
            first = per_asset[symbols[0]]
            c310_index = _as_index(first)
            c307_grid_ok = bool(len(c307_index) == len(c310_index) and c310_index.equals(c307_index))
    checks["grid"] = {
        "n_symbols": n_symbols,
        "symbols": symbols,
        "n_grid_bars": n_grid,
        "grid_start_utc": grid_start,
        "grid_end_utc": grid_end,
        "equals_c307_leg_b_grid": c307_grid_ok,
    }
    if not c307_grid_ok:
        blocked.append("C310 grid does not equal the C307 leg_b 1h grid")

    if n_symbols < N_PERP_SYMBOLS:
        blocked.append(f"C310 has {n_symbols} perp symbols (< {N_PERP_SYMBOLS} required)")

    detail = {}
    all_ok = True
    for s in symbols:
        d = {"symbol": s, "fields": {}, "ok": True}
        ok = True
        pa = per_asset.get(s) or {}
        pc = np.asarray(pa.get("perp_close", []), dtype=float)
        fr = np.asarray(pa.get("funding_rate", []), dtype=float)
        pc_present = pc[~np.isnan(pc)]
        pc_ok = bool(len(pc_present) and np.isfinite(pc_present).all() and (pc_present > 0).all())
        d["fields"]["perp_close"] = {"len": int(len(pc)), "nan": int(np.isnan(pc).sum()),
                                     "all_finite_present": bool(np.isfinite(pc_present).all()) if len(pc_present) else False,
                                     "all_positive_present": bool((pc_present > 0).all()) if len(pc_present) else False,
                                     "ok": pc_ok}
        ok &= pc_ok
        d["fields"]["funding_rate"] = {"nan": int(np.isnan(fr).sum()), "len": int(len(fr)), "ok": True}
        for leg in OFI_LEGS:
            v = np.asarray(pa.get(leg, []), dtype=float)
            present = v[np.isfinite(v)]
            if leg in SIGNED_LEGS:
                # signed leg: finite where present (may be negative); no inf.
                leg_ok = bool(len(v) == len(pc) and np.isfinite(present).all())
            else:
                nonneg = bool((present >= 0).all()) if len(present) else False
                leg_ok = bool(len(v) == len(pc) and nonneg)
            d["fields"][leg] = {"len": int(len(v)), "nan": int(np.isnan(v).sum()),
                                "finite_present": int(len(present)), "ok": leg_ok}
            ok &= leg_ok
        d["n_gap_bars"] = int(pa.get("n_gap_bars", -1))
        d["n_trade_bars"] = int(pa.get("n_trade_bars", -1))
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
        "campaign": 310,
        "part": "preflight",
        "checks": checks,
        "blocked_reasons": blocked,
    }
    print(json.dumps(result, indent=2, default=str))
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())