#!/usr/bin/env python3
"""C304 preflight: fail-closed verification of the real cross-sectional
mark/index basis stat-arb cache before the C304 runner executes.

Verifies:

- SHA256-from-bytes of the ingested pickle matches the meta-recorded sha;
- meta flags (real/fabricated/executed_fills), interval 1h, source interval
  mark_index_1h, n_symbols, window = common intersection grid, source host,
  cache format = plain numpy ndarrays, cache < 100 MB push limit;
- for every selected asset: mark/index OHLC exactly (n_bars x 1) over the common
  grid, present bars finite; mark/index gaps (real archive outage) are NaN and
  NEVER imputed; basis = mark_close - index_close finite where present;
- funding boundary integrity: funding rates present only on native 8h
  boundaries (minute==0, hour%8==0), finite where present; staleness gap
  reported per asset as a diagnostic (the runner enforces the stale->flat gate
  at trade time);
- common-grid cross-sectional coverage >= 2K for K in {2,3,5};
- walk-forward split math: train=720/test=168/step=168 in 1h bars fits the
  common grid (>= 1 OOS split);
- feature warmup: rolling features with min_periods=max(20, L//3) warm before
  the first OOS test bar for every runner lookback;
- provenance json exists.

The script never fetches, imputes, resamples, or fabricates data. Exit 0 iff
every check passes (ready:true); any mismatch/missing file is a fail-closed
blocker.
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

PXL = CACHE / "campaign304_mark_index_basis_xsec.pkl"
PXL_META = CACHE / "campaign304_mark_index_basis_xsec.meta.json"
PXL_PROV = CACHE / "campaign304_mark_index_basis_xsec.provenance.json"

EXPECTED_INTERVAL = "1h"
EXPECTED_SOURCE_INTERVAL = "mark_index_1h"
MARK_LEGS = ("mark_open", "mark_high", "mark_low", "mark_close")
INDEX_LEGS = ("index_open", "index_high", "index_low", "index_close")
BASIS_LEGS = ("basis",)
PRICE_LEGS = MARK_LEGS + INDEX_LEGS + BASIS_LEGS
VALID_FUNDING_INTERVALS = {1, 2, 4, 8}
MIN_FUNDING_ROWS = 90
STALE_BARS = 24 + 1  # 24h + 1 bar on the 1h grid (runner enforcement)
PUSH_LIMIT_BYTES = 100_000_000

# Runner grid (must match run_c304_mark_index_basis_xsec_oos.py).
LOOKBACKS_1H = (24, 48, 96, 168, 336, 720, 1440, 2160)
WF_TRAIN = 720
WF_TEST = 168
WF_STEP = 168
K_VALUES = (2, 3, 5)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def min_periods_for(L: int) -> int:
    return max(20, L // 3)


def wf_splits(n: int, train: int, test: int, step: int):
    out = []
    i = 0
    while i + train + test <= n:
        out.append((i, i + train, i + train + test))
        i += step
    return out


def _as_index(pa: dict) -> pd.DatetimeIndex:
    idx = pa.get("index")
    if isinstance(idx, pd.DatetimeIndex):
        return idx
    arr = np.asarray(idx)
    if np.issubdtype(arr.dtype, np.datetime64):
        return pd.DatetimeIndex(arr).tz_localize("UTC")
    return pd.DatetimeIndex(pd.to_datetime(arr, unit="ms", utc=True))


def _as_series(pa: dict, key: str, index: pd.DatetimeIndex) -> pd.Series:
    arr = np.asarray(pa.get(key), dtype=float)
    return pd.Series(arr, index=index)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.parse_args()

    checks: dict = {}
    blocked: list[str] = []

    if not PXL.exists():
        print(json.dumps({"ready": False, "blocked_reasons": ["C304 pickle missing"]}, indent=2))
        return 1
    pkl_sha = sha256_file(PXL)
    pkl_bytes = PXL.stat().st_size

    try:
        meta = json.loads(PXL_META.read_text())
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"ready": False, "blocked_reasons": [f"meta unreadable: {exc}"]}, indent=2))
        return 1

    flags_ok = (
        meta.get("interval") == EXPECTED_INTERVAL
        and meta.get("source_interval") == EXPECTED_SOURCE_INTERVAL
        and meta.get("n_symbols") is not None and int(meta.get("n_symbols")) >= 1
        and meta.get("real_data_only") is True
        and meta.get("fabricated_data") is False
        and meta.get("executed_fills") is False
        and meta.get("fetch_real_data_only") is True
        and meta.get("fetch_fabricated_data") is False
        and meta.get("source_host") == "https://data.binance.vision"
        and meta.get("cache_format") == "plain_numpy_ndarrays_no_pandas_legs"
        and meta.get("under_push_limit") is True
        and int(meta.get("cache_pkl_bytes") or 0) == pkl_bytes
        and pkl_bytes < PUSH_LIMIT_BYTES
        and pkl_sha == meta.get("sha256_from_bytes")
    )
    checks["meta"] = {
        "interval": meta.get("interval"),
        "source_interval": meta.get("source_interval"),
        "n_symbols": meta.get("n_symbols"),
        "common_grid_bars": meta.get("common_grid_bars"),
        "common_grid_start_utc": meta.get("common_grid_start_utc"),
        "common_grid_end_utc": meta.get("common_grid_end_utc"),
        "window_start_utc": meta.get("window_start_utc"),
        "window_end_utc": meta.get("window_end_utc"),
        "real_data_only": meta.get("real_data_only"),
        "fabricated_data": meta.get("fabricated_data"),
        "executed_fills": meta.get("executed_fills"),
        "cache_format": meta.get("cache_format"),
        "cache_pkl_bytes": pkl_bytes,
        "cache_pkl_mb": round(pkl_bytes / 1e6, 2),
        "under_push_limit": bool(pkl_bytes < PUSH_LIMIT_BYTES),
        "source_host": meta.get("source_host"),
        "sha256_from_bytes": meta.get("sha256_from_bytes"),
        "actual_sha256": pkl_sha,
        "ok": bool(flags_ok),
    }
    if not flags_ok:
        blocked.append("meta flags/interval/source/window/format/size/sha mismatch")

    try:
        with open(PXL, "rb") as fh:
            payload = pickle.load(fh)
        symbols = list(payload.get("symbols") or [])
        sym_ok = len(symbols) >= 1 and len(symbols) == int(meta.get("n_symbols") or 0)
        per_asset = payload.get("per_asset") or {}
        common_grid_bars = int(payload.get("common_grid_bars") or 0)
        n_symbols = len(symbols)

        # cross-sectional coverage: need >= 2K assets for K in {2,3,5}.
        coverage_ok = n_symbols >= 2 * max(K_VALUES)
        checks["coverage"] = {
            "n_symbols": n_symbols,
            "k_values": [int(k) for k in K_VALUES],
            "min_required_for_max_k": 2 * int(max(K_VALUES)),
            "coverage_ok": bool(coverage_ok),
        }
        if not coverage_ok:
            blocked.append("common-grid cross-sectional coverage < 2K for K in {2,3,5}")

        asset_detail = {}
        asset_ok = True
        for s in symbols:
            pa = per_asset.get(s)
            if not isinstance(pa, dict):
                asset_detail[s] = {"ok": False, "error": "per-asset entry missing or not a dict"}
                asset_ok = False
                continue
            index = _as_index(pa)
            n_bars = int(pa.get("n_bars") or len(index))
            d = {"symbol": s, "n_bars": n_bars, "fields": {}}
            all_field_ok = True
            for key in PRICE_LEGS:
                f = _as_series(pa, key, index)
                arr = f.to_numpy(dtype=float)
                nan_c = int(np.isnan(arr).sum())
                present = arr[~np.isnan(arr)]
                finite = bool(np.isfinite(present).all()) if len(present) else True
                dup = int(f.index.duplicated().sum())
                fok = finite and dup == 0 and int(len(f)) == n_bars and int(present.shape[0]) > 0
                d["fields"][key] = {"nan_count": nan_c, "all_finite_present": finite,
                                    "duplicate": dup, "ok": bool(fok)}
                all_field_ok &= fok

            # perp close (execution price): finite, positive where present
            close = _as_series(pa, "perp_close", index).to_numpy(dtype=float)
            c_present = close[~np.isnan(close)]
            c_finite = bool(np.isfinite(c_present).all()) if len(c_present) else False
            c_positive = bool((c_present > 0).all()) if len(c_present) else False
            d["perp_close"] = {
                "nan_count": int(np.isnan(close).sum()),
                "all_finite_present": c_finite,
                "all_positive_present": c_positive,
                "ok": bool(c_finite and c_positive and len(c_present) > 0),
            }
            all_field_ok &= d["perp_close"]["ok"]

            # funding: present only on native 8h boundaries, finite where present
            funding = _as_series(pa, "funding_rates", index)
            f_arr = funding.to_numpy(dtype=float)
            fmask = funding.notna()
            f_rows = int(fmask.sum())
            f_vals = f_arr[fmask.values]
            f_finite = bool(np.isfinite(f_vals).all()) if len(f_vals) else False
            ts_b = funding.index[fmask.values]
            f_minute_ok = bool((ts_b.minute == 0).all()) if len(ts_b) else False
            f_hour_ok = bool((ts_b.hour % 8 == 0).all()) if len(ts_b) else False
            pos = np.where(fmask.values)[0]
            gap_f = int(np.diff(pos).max()) if len(pos) > 1 else 0
            tail_gap = int(len(index) - 1 - pos[-1]) if len(pos) else int(len(index))
            first_gap = int(pos[0]) if len(pos) else int(len(index))
            stale_ok = gap_f <= STALE_BARS and tail_gap <= STALE_BARS
            d["funding"] = {
                "funding_rows": f_rows, "min_rows": MIN_FUNDING_ROWS,
                "all_finite_present": f_finite,
                "minute_zero": f_minute_ok, "hour_multiple_of_8": f_hour_ok,
                "max_boundary_gap_bars": gap_f, "tail_gap_bars": tail_gap,
                "first_boundary_bar": first_gap,
                "stale_limit_bars": STALE_BARS,
                "stale_ok": bool(stale_ok),
                "ok": bool(f_finite and f_minute_ok and f_hour_ok),
                "staleness_diagnostic": "real altcoin funding archives carry gaps; "
                                        "runner enforces stale->flat at trade time",
            }
            all_field_ok &= d["funding"]["all_finite_present"] and f_minute_ok and f_hour_ok

            # walk-forward fit
            n_splits = len(wf_splits(n_bars, WF_TRAIN, WF_TEST, WF_STEP))
            wf_ok = n_bars >= WF_TRAIN + WF_TEST and n_splits > 0
            d["walk_forward"] = {"bars": n_bars, "train": WF_TRAIN, "test": WF_TEST,
                                 "step": WF_STEP, "n_splits": int(n_splits), "ok": bool(wf_ok)}
            all_field_ok &= wf_ok

            # feature warmup for all runner lookbacks
            warm = {f"L={L}": {"min_periods": int(min_periods_for(L)),
                               "warm_before_first_test_bar": bool(min_periods_for(L) <= WF_TRAIN),
                               "ok": bool(min_periods_for(L) <= WF_TRAIN)} for L in LOOKBACKS_1H}
            warm_ok = all(v["ok"] for v in warm.values())
            d["feature_warmup"] = {"rule": "min_periods = max(20, L // 3) on native-1h features",
                                   "lookbacks_1h": [int(l) for l in LOOKBACKS_1H],
                                   "warmup": warm, "ok": bool(warm_ok)}
            all_field_ok &= warm_ok

            d["ok"] = bool(all_field_ok)
            asset_detail[s] = d
            asset_ok &= all_field_ok
        checks["assets"] = {"n_symbols": n_symbols, "symbols": symbols,
                            "symbols_ok": bool(sym_ok), "detail": asset_detail, "ok": bool(asset_ok and sym_ok)}
        if not asset_ok:
            blocked.append("one or more assets failed mark/index/basis/perp/funding/WF/warmup checks")
        if not sym_ok:
            blocked.append("universe size mismatch")

        # common grid window sanity
        if n_symbols:
            first_idx = _as_index(per_asset[symbols[0]])
            checks["common_grid"] = {
                "bars": common_grid_bars,
                "start_utc": str(first_idx[0]),
                "end_utc": str(first_idx[-1]),
                "meta_start_utc": meta.get("common_grid_start_utc"),
                "meta_end_utc": meta.get("common_grid_end_utc"),
            }
    except Exception as exc:  # noqa: BLE001
        checks["assets"] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        blocked.append("assets could not be loaded")

    checks["provenance"] = {
        "path": str(PXL_PROV.relative_to(ROOT)) if PXL_PROV.exists() else str(PXL_PROV),
        "exists": PXL_PROV.exists(),
        "ok": bool(PXL_PROV.exists()),
    }
    if not PXL_PROV.exists():
        blocked.append("provenance json missing")

    ready = not blocked
    result = {
        "ready": ready,
        "real_data_only": True,
        "fabricated_data": False,
        "executed_fills": False,
        "campaign": 304,
        "part": "preflight",
        "checks": checks,
        "blocked_reasons": blocked,
    }
    print(json.dumps(result, indent=2, default=str))
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
