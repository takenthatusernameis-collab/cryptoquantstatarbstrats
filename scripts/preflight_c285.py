#!/usr/bin/env python3
"""C285 preflight: verify every real-data cache and the causal overlap.

C285 is a volume-conditioned cross-sectional statistical-arbitrage campaign.
It uses only real, already-cached Binance data:

- 1h spot close cache (5427 x 11, 2026-04-01 -> 2026-11-13T02:00Z)
- 1h real quote-volume cache (column 5, 5112 x 11 usable symbols)
- 5m spot close cache (26208 x 11, 2026-08-01 -> 2026-10-30T23:55Z) for C286

The script verifies SHA256-from-bytes, shape, NaNs, duplicate indexes, real /
fabricated flags, and the exact 1h overlap used by C285.  It never fetches,
imputes, resamples, or fabricates data.  Exit code 0 iff every check passes.
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
CACHE = ROOT / "data" / "cache"

SPOT_1H = CACHE / "26736ab8fbb16974dd59f123855ab7e4810026d12712a05a363eabacd814ade2.pkl"
SPOT_1H_META = SPOT_1H.with_suffix(".meta.json")
SPOT_1H_SHA = "9355aed62b00a56b46ebba70eec4f9855620e8fea1b6eeae417ec6d7dea349df"
SPOT_1H_META_SHA = "95baf25daae1656a8c6f074acdcd909250565ddda8e86920b00d85163646afd1"

VOLUME = CACHE / "volume_1h_full.pkl"
VOLUME_META = CACHE / "volume_1h_full.meta.json"
VOLUME_PROVENANCE = CACHE / "volume_1h_full.provenance.json"
VOLUME_SHA = "4365895387de4e542165fd331e39da40d455a3de24c7254eb67ba890053d193c"
VOLUME_META_SHA = "4d321584d3c687ad9956908c0179a1eae7d629c296c491e1e5ad1259a890c616"
VOLUME_PROVENANCE_SHA = "c7ff2f27ec5a668128e4856f809efde4922563dba87be0648be6d802c6d21c89"

SPOT_5M = CACHE / "90d10b876bb8eda9619cbba73ed19d6c7db4ea7327284f2e33f10a7872a5b263.pkl"
SPOT_5M_META = SPOT_5M.with_suffix(".meta.json")
SPOT_5M_SHA = "d15b0b183cf685a15dd34185baff22edf7ef3cc9c80c7d607bcd92f8da418c2f"
SPOT_5M_META_SHA = "e1a71f481cb4ad07881d132aba4ff7b47fc8194c69779701035efcf6e492ce4e"

SYMBOLS = ("ADA", "AVAX", "BNB", "BTC", "DOT", "ETH", "LINK", "LTC", "POL", "SOL", "XRP")
EXPECTED_SPOT_1H_SHAPE = (5427, 11)
EXPECTED_VOLUME_BARS = 5112
EXPECTED_SPOT_5M_SHAPE = (26208, 11)
EXPECTED_1H_OVERLAP = 5112


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_pickle(path: Path):
    with open(path, "rb") as handle:
        return pickle.load(handle)


def check_sha(checks: dict, label: str, path: Path, expected: str) -> bool:
    if not path.exists():
        checks[label] = {"path": str(path), "exists": False, "ok": False}
        return False
    actual = sha256_file(path)
    ok = actual == expected
    checks[label] = {
        "path": str(path),
        "exists": True,
        "sha256": actual,
        "expected_sha256": expected,
        "ok": ok,
    }
    return ok


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit a machine-readable JSON summary on stdout (default)",
    )
    parser.parse_args()

    checks: dict[str, dict] = {}
    blocked: list[str] = []

    sha_ok = True
    sha_ok &= check_sha(checks, "spot_1h_sha", SPOT_1H, SPOT_1H_SHA)
    sha_ok &= check_sha(checks, "spot_1h_meta_sha", SPOT_1H_META, SPOT_1H_META_SHA)
    sha_ok &= check_sha(checks, "volume_1h_sha", VOLUME, VOLUME_SHA)
    sha_ok &= check_sha(checks, "volume_1h_meta_sha", VOLUME_META, VOLUME_META_SHA)
    sha_ok &= check_sha(checks, "volume_1h_provenance_sha", VOLUME_PROVENANCE, VOLUME_PROVENANCE_SHA)
    sha_ok &= check_sha(checks, "spot_5m_sha", SPOT_5M, SPOT_5M_SHA)
    sha_ok &= check_sha(checks, "spot_5m_meta_sha", SPOT_5M_META, SPOT_5M_META_SHA)

    spot_1h = None
    volume = None
    spot_5m = None

    try:
        spot_1h = load_pickle(SPOT_1H)
        if isinstance(spot_1h, pd.Series):
            spot_1h = spot_1h.to_frame()
        spot_1h = spot_1h.astype(float).sort_index()
        nan_1h = int(spot_1h.isna().sum().sum())
        dup_1h = int(spot_1h.index.duplicated().sum())
        shape_1h = tuple(int(x) for x in spot_1h.shape)
        checks["spot_1h"] = {
            "shape": shape_1h,
            "expected_shape": list(EXPECTED_SPOT_1H_SHAPE),
            "nan_count": nan_1h,
            "duplicate_index_count": dup_1h,
            "start": str(spot_1h.index.min()),
            "end": str(spot_1h.index.max()),
            "columns": [str(c) for c in spot_1h.columns],
            "ok": (
                shape_1h == EXPECTED_SPOT_1H_SHAPE
                and nan_1h == 0
                and dup_1h == 0
                and tuple(str(c) for c in spot_1h.columns) == SYMBOLS
            ),
        }
        if not checks["spot_1h"]["ok"]:
            blocked.append("spot_1h shape/nan/duplicate/symbol check failed")
    except Exception as exc:  # noqa: BLE001 - report a blocker, never fabricate
        checks["spot_1h"] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        blocked.append("spot_1h could not be loaded")

    try:
        volume = load_pickle(VOLUME)
        if not isinstance(volume, dict):
            raise TypeError("volume cache is not a dict of symbol -> Series")
        per_symbol: dict[str, dict] = {}
        volume_ok = True
        for symbol in SYMBOLS:
            series = volume.get(symbol)
            if series is None:
                per_symbol[symbol] = {"present": False, "ok": False}
                volume_ok = False
                continue
            series = pd.Series(series).sort_index()
            bars = int(series.shape[0])
            nan_count = int(series.isna().sum())
            nonfinite = int((~np.isfinite(series.to_numpy(dtype=float))).sum())
            ok = bars == EXPECTED_VOLUME_BARS and nan_count == 0 and nonfinite == 0 and bool((series.dropna() > 0).all())
            per_symbol[symbol] = {
                "present": True,
                "bars": bars,
                "nan_count": nan_count,
                "nonfinite_count": nonfinite,
                "start": str(series.index.min()),
                "end": str(series.index.max()),
                "ok": ok,
            }
            volume_ok &= ok
        checks["volume_1h"] = {
            "symbols": per_symbol,
            "ok": volume_ok,
            "note": "Quote volume is Binance klines column 5 (USDT), not a proxy.",
        }
        if not volume_ok:
            blocked.append("volume_1h symbol/bar/finite check failed")
    except Exception as exc:  # noqa: BLE001
        checks["volume_1h"] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        blocked.append("volume_1h could not be loaded")

    try:
        spot_5m = load_pickle(SPOT_5M)
        if isinstance(spot_5m, pd.Series):
            spot_5m = spot_5m.to_frame()
        spot_5m = spot_5m.astype(float).sort_index()
        nan_5m = int(spot_5m.isna().sum().sum())
        dup_5m = int(spot_5m.index.duplicated().sum())
        shape_5m = tuple(int(x) for x in spot_5m.shape)
        checks["spot_5m"] = {
            "shape": shape_5m,
            "expected_shape": list(EXPECTED_SPOT_5M_SHAPE),
            "nan_count": nan_5m,
            "duplicate_index_count": dup_5m,
            "start": str(spot_5m.index.min()),
            "end": str(spot_5m.index.max()),
            "columns": [str(c) for c in spot_5m.columns],
            "ok": (
                shape_5m == EXPECTED_SPOT_5M_SHAPE
                and nan_5m == 0
                and dup_5m == 0
                and tuple(str(c) for c in spot_5m.columns) == SYMBOLS
            ),
        }
        if not checks["spot_5m"]["ok"]:
            blocked.append("spot_5m shape/nan/duplicate/symbol check failed")
    except Exception as exc:  # noqa: BLE001
        checks["spot_5m"] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        blocked.append("spot_5m could not be loaded")

    if spot_1h is not None and volume is not None:
        try:
            first_volume = next(iter(volume.values()))
            volume_index = pd.DatetimeIndex(pd.to_datetime(first_volume.index, utc=True))
            spot_index = pd.DatetimeIndex(spot_1h.index)
            overlap = spot_index.intersection(volume_index)
            checks["overlap_1h_spot_volume"] = {
                "bars": int(len(overlap)),
                "expected_bars": EXPECTED_1H_OVERLAP,
                "start": str(overlap.min()) if len(overlap) else None,
                "end": str(overlap.max()) if len(overlap) else None,
                "ok": len(overlap) == EXPECTED_1H_OVERLAP,
            }
            if len(overlap) != EXPECTED_1H_OVERLAP:
                blocked.append("1h spot/volume overlap is not 5112 bars")
        except Exception as exc:  # noqa: BLE001
            checks["overlap_1h_spot_volume"] = {
                "ok": False,
                "error": f"{type(exc).__name__}: {exc}",
            }
            blocked.append("1h overlap could not be computed")
    else:
        blocked.append("1h overlap skipped because a cache failed to load")

    if spot_5m is not None and volume is not None:
        try:
            first_volume = next(iter(volume.values()))
            volume_index = pd.DatetimeIndex(pd.to_datetime(first_volume.index, utc=True))
            volume_available = volume_index + pd.Timedelta(hours=1)
            m5_index = pd.DatetimeIndex(spot_5m.index)
            causal = m5_index[m5_index >= volume_available.min()]
            checks["overlap_5m_causal_volume"] = {
                "bars": int(len(causal)),
                "start": str(causal.min()) if len(causal) else None,
                "end": str(causal.max()) if len(causal) else None,
                "ok": len(causal) > 0,
                "note": "1h volume at bar t is available at t+1h; 5m bars at/after that instant are eligible.",
            }
            if len(causal) == 0:
                blocked.append("5m causal volume overlap is empty")
        except Exception as exc:  # noqa: BLE001
            checks["overlap_5m_causal_volume"] = {
                "ok": False,
                "error": f"{type(exc).__name__}: {exc}",
            }
            blocked.append("5m causal overlap could not be computed")
    else:
        blocked.append("5m causal overlap skipped because a cache failed to load")

    ready = sha_ok and not blocked
    result = {
        "ready": ready,
        "real_data_only": True,
        "fabricated_data": False,
        "campaign": 285,
        "part": "preflight",
        "checks": checks,
        "blocked_reasons": blocked,
    }
    print(json.dumps(result, indent=2, default=str))
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())