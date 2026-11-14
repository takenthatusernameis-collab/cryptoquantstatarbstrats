#!/usr/bin/env python3
"""C302 preflight: fail-closed verification of the real 2020-01 .. 2026-10
USDT-M perp premiumIndexKlines-derived 1h premium-index feature cache before the
C302 per-asset premium-index time-series campaign runs.

Verifies:

- SHA256-from-bytes of the ingested pickle matches the meta-recorded sha;
- meta flags (real/fabricated), interval 1h, source interval premiumIndex_1h,
  n_symbols, window (2020-01-01 .. 2026-10-31 23:00), source host, C299 reuse
  cache sha, cache format = plain numpy ndarrays, cache < 100 MB push limit;
- for every selected asset: premium OHLC exactly (n_bars x 1) over the C299 1h
  index, zero NaN, all finite; funding_rates present only on native 8h boundaries
  (>= 90 finite rows, stale gap <= 24h + 1 bar on the 1h grid); perp_close zero
  NaN / positive / finite (the real execution price);
- walk-forward split math: train=2160/test=720/step=720 in 1h bars fits each
  asset's window (>= 1 OOS split);
- feature warmup: rolling features with min_periods=max(20, L//3) warm before
  the first OOS test bar for every lookback L in {168, 720, 2160};
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

PXL = CACHE / "campaign302_premium_index_basis.pkl"
PXL_META = CACHE / "campaign302_premium_index_basis.meta.json"
PXL_PROV = CACHE / "campaign302_premium_index_basis.provenance.json"
C299_CACHE = CACHE / "campaign299_multianual_perp_funding_basis_ts.pkl"

EXPECTED_INTERVAL = "1h"
EXPECTED_SOURCE_INTERVAL = "premiumIndex_1h"
WINDOW_START = "2020-01-01T00:00:00Z"
WINDOW_END = "2026-10-31T23:00:00Z"
PREMIUM_LEGS = ("prem_open", "prem_high", "prem_low", "prem_close")
VALID_FUNDING_INTERVALS = {1, 2, 4, 8}
MIN_FUNDING_ROWS = 90
STALE_BARS = 24 + 1  # 24h + 1 bar on the 1h grid
MIN_BARS = 2160 + 720  # train + one test
PUSH_LIMIT_BYTES = 100_000_000

LOOKBACKS_1H = (168, 720, 2160)
WF_TRAIN = 2160
WF_TEST = 720
WF_STEP = 720


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
        print(json.dumps({"ready": False, "blocked_reasons": ["C302 premium-index pickle missing"]}, indent=2))
        return 1
    pkl_sha = sha256_file(PXL)
    pkl_bytes = PXL.stat().st_size

    try:
        meta = json.loads(PXL_META.read_text())
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"ready": False, "blocked_reasons": [f"meta unreadable: {exc}"]}, indent=2))
        return 1

    # C299 reuse cache must exist and match recorded sha.
    c299_sha = sha256_file(C299_CACHE) if C299_CACHE.exists() else None

    flags_ok = (
        meta.get("interval") == EXPECTED_INTERVAL
        and meta.get("source_interval") == EXPECTED_SOURCE_INTERVAL
        and meta.get("n_symbols") is not None and int(meta.get("n_symbols")) >= 1
        and meta.get("window_start_utc") == WINDOW_START
        and meta.get("window_end_utc") == WINDOW_END
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
        and meta.get("c299_cache_sha256") == c299_sha
    )
    checks["meta"] = {
        "interval": meta.get("interval"),
        "source_interval": meta.get("source_interval"),
        "n_symbols": meta.get("n_symbols"),
        "total_bars": meta.get("total_bars"),
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
        "c299_cache_sha256": meta.get("c299_cache_sha256"),
        "c299_cache_actual_sha256": c299_sha,
        "sha256_from_bytes": meta.get("sha256_from_bytes"),
        "actual_sha256": pkl_sha,
        "ok": bool(flags_ok),
    }
    if not flags_ok:
        blocked.append("meta flags/interval/source/window/host/format/size/sha/C299-reuse mismatch")

    try:
        with open(PXL, "rb") as fh:
            payload = pickle.load(fh)
        symbols = list(payload.get("symbols") or [])
        sym_ok = len(symbols) >= 1 and len(symbols) == int(meta.get("n_symbols") or 0)
        per_asset = payload.get("per_asset") or {}
        c299 = pickle.load(open(C299_CACHE, "rb")) if C299_CACHE.exists() else {"per_asset": {}}
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
            # premium OHLC: exact C299 index; present bars finite; gap bars (real
            # archive outage, e.g. 2021-07-01) are NaN and NEVER imputed.
            for key in PREMIUM_LEGS:
                f = _as_series(pa, key, index)
                arr = f.to_numpy(dtype=float)
                nan_c = int(np.isnan(arr).sum())
                present = arr[~np.isnan(arr)]
                finite = bool(np.isfinite(present).all()) if len(present) else True
                dup = int(f.index.duplicated().sum())
                fok = finite and dup == 0 and int(len(f)) == n_bars and int(present.shape[0]) > 0
                d["fields"][key] = {"nan_count": nan_c, "all_finite_present": finite, "duplicate": dup, "ok": bool(fok)}
                all_field_ok &= fok
            # premium band consistency on present bars only (high>=open/close, low<=open/close)
            po = _as_series(pa, "prem_open", index).to_numpy(dtype=float)
            ph = _as_series(pa, "prem_high", index).to_numpy(dtype=float)
            pl = _as_series(pa, "prem_low", index).to_numpy(dtype=float)
            pc = _as_series(pa, "prem_close", index).to_numpy(dtype=float)
            band_mask = ~(np.isnan(po) | np.isnan(ph) | np.isnan(pl) | np.isnan(pc))
            band_ok = bool(
                np.all(ph[band_mask] >= np.maximum(po[band_mask], pc[band_mask]) - 1e-12)
                and np.all(pl[band_mask] <= np.minimum(po[band_mask], pc[band_mask]) + 1e-12)
                and np.all(ph[band_mask] >= pl[band_mask] - 1e-12)
            ) if band_mask.any() else False
            d["premium_band"] = {"high_ge_max_open_close": bool(np.all(ph[band_mask] >= np.maximum(po[band_mask], pc[band_mask]) - 1e-12)) if band_mask.any() else False,
                                 "low_le_min_open_close": bool(np.all(pl[band_mask] <= np.minimum(po[band_mask], pc[band_mask]) + 1e-12)) if band_mask.any() else False,
                                 "high_ge_low": bool(np.all(ph[band_mask] >= pl[band_mask] - 1e-12)) if band_mask.any() else False,
                                 "ok": band_ok}
            all_field_ok &= band_ok

            # execution price + funding from C299 reuse: must match C299 per-asset index
            c299_pa = (c299.get("per_asset") or {}).get(s)
            reuse_ok = False
            if isinstance(c299_pa, dict):
                c299_idx = c299_pa["index"]
                if not isinstance(c299_idx, pd.DatetimeIndex):
                    c299_idx = pd.DatetimeIndex(pd.asarray(c299_idx))
                close = pd.Series(np.asarray(c299_pa["closes"], dtype=float), index=c299_idx).reindex(index)
                funding = pd.Series(np.asarray(c299_pa["funding_rates"], dtype=float), index=c299_idx).reindex(index)
                c_nan = int(close.isna().sum())
                c_pos = bool((close.dropna().to_numpy(dtype=float) > 0).all()) if len(close.dropna()) else True
                c_fin = bool(np.isfinite(close.dropna().to_numpy(dtype=float)).all()) if len(close.dropna()) else True
                d["perp_close"] = {"nan_count": c_nan, "all_positive": c_pos, "all_finite": c_fin, "ok": bool(c_nan == 0 and c_pos and c_fin)}
                # funding boundary/staleness
                fmask = funding.notna()
                rows = int(fmask.sum())
                vals = funding[fmask]
                finite = bool(np.isfinite(vals.to_numpy(dtype=float)).all()) if len(vals) else False
                ts_b = funding.index[fmask.values]
                minute_ok = bool((ts_b.minute == 0).all()) if len(ts_b) else False
                hour_ok = bool((ts_b.hour % 8 == 0).all()) if len(ts_b) else False
                pos = np.where(fmask.values)[0]
                gap_f = int(np.diff(pos).max()) if len(pos) > 1 else 0
                tail_gap = int(len(index) - 1 - pos[-1]) if len(pos) else int(len(index))
                stale_ok = gap_f <= STALE_BARS and tail_gap <= STALE_BARS
                fund_ok = rows >= MIN_FUNDING_ROWS and finite and minute_ok and hour_ok and stale_ok
                d["funding"] = {"funding_rows": rows, "min_rows": MIN_FUNDING_ROWS, "all_finite": finite,
                                "minute_zero": minute_ok, "hour_multiple_of_8": hour_ok,
                                "max_boundary_gap_bars": gap_f, "tail_gap_bars": tail_gap,
                                "stale_limit_bars": STALE_BARS, "stale_ok": stale_ok, "ok": bool(fund_ok)}
                all_field_ok &= d["perp_close"]["ok"] and fund_ok
                reuse_ok = True
            if not reuse_ok:
                d["perp_close"] = {"ok": False, "error": "C299 per-asset entry missing"}
                d["funding"] = {"ok": False, "error": "C299 per-asset entry missing"}
                all_field_ok = False

            # walk-forward fit
            n_splits = len(wf_splits(n_bars, WF_TRAIN, WF_TEST, WF_STEP))
            wf_ok = n_bars >= MIN_BARS and n_splits > 0
            d["walk_forward"] = {"bars": n_bars, "train": WF_TRAIN, "test": WF_TEST, "step": WF_STEP,
                                 "min_bars": MIN_BARS, "n_splits": int(n_splits), "ok": bool(wf_ok)}
            all_field_ok &= wf_ok

            # feature warmup
            warm = {f"L={L}": {"min_periods": int(min_periods_for(L)),
                               "warm_before_first_test_bar": bool(min_periods_for(L) <= WF_TRAIN),
                               "ok": bool(min_periods_for(L) <= WF_TRAIN)} for L in LOOKBACKS_1H}
            warm_ok = all(v["ok"] for v in warm.values())
            d["feature_warmup"] = {"rule": "min_periods = max(20, L // 3) on native-1h per-asset features",
                                   "lookbacks_1h": list(LOOKBACKS_1H), "warmup": warm, "ok": bool(warm_ok)}
            all_field_ok &= warm_ok

            d["ok"] = bool(all_field_ok)
            asset_detail[s] = d
            asset_ok &= all_field_ok
        checks["assets"] = {"n_symbols": len(symbols), "symbols": symbols, "symbols_ok": bool(sym_ok),
                            "detail": asset_detail, "ok": bool(asset_ok and sym_ok)}
        if not asset_ok:
            blocked.append("one or more assets failed per-asset premium/perp/funding/WF/warmup checks")
        if not sym_ok:
            blocked.append("universe size mismatch")
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
        "campaign": 302,
        "part": "preflight",
        "checks": checks,
        "blocked_reasons": blocked,
    }
    print(json.dumps(result, indent=2, default=str))
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())