#!/usr/bin/env python3
"""C309 preflight: fail-closed verification of the real C307 cache before the
C309 runner sweeps the premium-index & mark-perp-basis cross-sectional carry.

Verifies:
- the C307 pickle exists, SHA256-from-bytes matches meta, meta flags
  (real_data_only:true, fabricated_data:false, executed_fills:false),
  interval/source/host/format/push-limit intact;
- the Leg B common grid (11 COIN-M inverse perps) is non-empty, restricted to
  2022-07..2026-06, with all 11 symbols having finite perp_close/mark_close;
- premium_close_*, mark_close_*, perp_close_* are present and finite for all
  11 perps (mark_basis = mark_close/perp_close - 1 must be computable);
- funding_rate_*/funding_present_* present (control leg only, never the C309
  carry source).

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

CACHE = ROOT / "data" / "cache" / "campaign307_coinm_multiasset_term_structure_carry.pkl"
CACHE_META = ROOT / "data" / "cache" / "campaign307_coinm_multiasset_term_structure_carry.meta.json"
CACHE_PROV = ROOT / "data" / "cache" / "campaign307_coinm_multiasset_term_structure_carry.provenance.json"
PUSH_LIMIT_BYTES = 100_000_000

EXPECTED_INTERVAL = "1h"
EXPECTED_SOURCE_INTERVAL = "coin_m_klines_1h"
GRID_START = pd.Timestamp("2022-07-01", tz="UTC")
GRID_END = pd.Timestamp("2026-07-01", tz="UTC")  # exclusive end -> through 2026-06
N_PERP_SYMBOLS = 11


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
        print(json.dumps({"ready": False, "blocked_reasons": ["C307 pickle missing"]}, indent=2))
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
        and int(meta.get("n_perp_symbols") or 0) >= N_PERP_SYMBOLS
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
        "n_perp_symbols": meta.get("n_perp_symbols"),
        "real_data_only": meta.get("real_data_only"),
        "fabricated_data": meta.get("fabricated_data"),
        "executed_fills": meta.get("executed_fills"),
        "source_host": meta.get("source_host"),
        "cache_pkl_bytes": pkl_bytes,
        "cache_pkl_mb": round(pkl_bytes / 1e6, 2),
        "under_push_limit": bool(pkl_bytes < PUSH_LIMIT_BYTES),
        "sha256_from_bytes": meta.get("sha256_from_bytes"),
        "actual_sha256": pkl_sha,
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

    leg_b = payload.get("leg_b") or {}
    symbols = list(leg_b.get("symbols") or [])
    n_symbols = len(symbols)
    index = _as_index(leg_b) if "index" in leg_b else None
    n_bars = int(leg_b.get("n_bars") or 0)

    if index is None or n_bars == 0:
        blocked.append("Leg B common grid is empty")
    else:
        start_ok = index[0] >= GRID_START
        end_ok = index[-1] < GRID_END
        if not (start_ok and end_ok):
            blocked.append(f"Leg B grid outside 2022-07..2026-06: start={index[0]}, end={index[-1]}")
    checks["leg_b_grid"] = {
        "n_symbols": n_symbols,
        "symbols": symbols,
        "n_bars": n_bars,
        "window_start_utc": leg_b.get("window_start_utc"),
        "window_end_utc": leg_b.get("window_end_utc"),
        "start_utc": str(index[0]) if index is not None and len(index) else None,
        "end_utc": str(index[-1]) if index is not None and len(index) else None,
    }

    if n_symbols < N_PERP_SYMBOLS:
        blocked.append(f"Leg B has {n_symbols} perp symbols (< {N_PERP_SYMBOLS} required)")

    detail = {}
    all_ok = True
    for s in symbols:
        d = {"symbol": s, "fields": {}, "ok": True}
        ok = True
        for key, need_positive in (
            (f"perp_close_{s}", True),
            (f"mark_close_{s}", True),
            (f"premium_close_{s}", False),
        ):
            if key not in leg_b:
                d["fields"][key] = {"present": False, "ok": False}
                ok = False
                continue
            v = np.asarray(leg_b[key], dtype=float)
            present = v[~np.isnan(v)]
            finite = bool(np.isfinite(present).all()) if len(present) else False
            positive = bool((present > 0).all()) if (len(present) and need_positive) else True
            d["fields"][key] = {
                "present": True,
                "nan_count": int(np.isnan(v).sum()),
                "len": int(len(v)),
                "all_finite_present": finite,
                "all_positive_present": positive,
                "ok": bool(finite and positive and len(present) > 0),
            }
            ok &= d["fields"][key]["ok"]
        # mark_basis = mark_close/perp_close - 1 must be computable and finite
        pc_key = f"perp_close_{s}"
        mk_key = f"mark_close_{s}"
        basis_ok = False
        if pc_key in leg_b and mk_key in leg_b:
            pc = np.asarray(leg_b[pc_key], dtype=float)
            mk = np.asarray(leg_b[mk_key], dtype=float)
            basis = mk / pc - 1.0
            bp = basis[~np.isnan(basis)]
            basis_ok = bool(np.isfinite(bp).all() and len(bp) > 0)
            d["fields"]["mark_basis"] = {
                "nan_count": int(np.isnan(basis).sum()),
                "all_finite_present": bool(np.isfinite(bp).all()),
                "ok": basis_ok,
            }
        ok &= basis_ok
        for fk in (f"funding_rate_{s}", f"funding_present_{s}"):
            if fk in leg_b:
                fv = np.asarray(leg_b[fk], dtype=float)
                d["fields"][fk] = {"nan_count": int(np.isnan(fv).sum()), "len": int(len(fv)), "ok": True}
            else:
                d["fields"][fk] = {"present": False, "ok": False}
        d["ok"] = bool(ok)
        detail[s] = d
        all_ok &= bool(ok)
    checks["leg_b"] = {"n_symbols": n_symbols, "n_bars": n_bars, "detail": detail, "ok": bool(all_ok)}
    if not all_ok:
        blocked.append("one or more perp symbols failed premium/mark/perp/mark_basis checks")

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
        "campaign": 309,
        "part": "preflight",
        "checks": checks,
        "blocked_reasons": blocked,
    }
    print(json.dumps(result, indent=2, default=str))
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
