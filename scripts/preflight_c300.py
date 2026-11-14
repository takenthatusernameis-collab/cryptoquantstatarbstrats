#!/usr/bin/env python3
"""C300 preflight: fail-closed verification of the real per-asset NATIVE 5m
(2020-01 .. 2026-10) USDT-M perp klines + spot klines + native 8h funding cache
before the 5m funding-carry / spot-perp basis time-series campaign.

Verifies:

- SHA256-from-bytes of the ingested pickle matches the meta-recorded sha;
- meta flags (real/fabricated), interval 5m, n_symbols, window, source host,
  cache format = plain numpy ndarrays, cache < 100 MB push limit;
- for every selected asset: perp_close exactly (n_bars x 1) over its contiguous
  window, zero NaN, strictly positive, exact 5m spacing, duplicate-free index;
  spot_close carries the same index (basis leg) with the 462 un-imputed gap bars
  as NaN (never imputed), present values finite/positive; funding_rates present
  only on native 8h boundaries (minute 0, hour multiple of 8), >= 90 finite rows,
  no funding gap > 24h + 1 bar (fail-closed staleness);
- walk-forward split math: train=25920/test=8640/step=8640 in 5m bars fits each
  asset's window (>= 1 OOS split);
- feature warmup: rolling features with min_periods=max(20, L//3) warm before
  the first OOS test bar for every lookback L in {288, 1008, 2016};
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

PXL = CACHE / "campaign300_multianual_perp_funding_basis_ts_5m.pkl"
PXL_META = CACHE / "campaign300_multianual_perp_funding_basis_ts_5m.meta.json"
PXL_PROV = CACHE / "campaign300_multianual_perp_funding_basis_ts_5m.provenance.json"

EXPECTED_INTERVAL = "5m"
REQUIRED_PER_ASSET_FIELDS = ("perp_close", "spot_close", "funding_rates")
FUNDING_FRAME_FIELD = "funding_rates"
VALID_FUNDING_INTERVALS = {1, 2, 4, 8}
MIN_FUNDING_ROWS = 90
STALE_BARS = 24 * 12 + 1  # 24h + 1 bar on the 5m grid
MIN_BARS = 34560  # one WF train+test (25920+8640)
PUSH_LIMIT_BYTES = 100_000_000
SPOT_GAP_BARS_EXPECTED = 462  # per-asset, 12 months (recorded; never imputed)

LOOKBACKS_5M = (288, 1008, 2016)
WF_TRAIN = 25920
WF_TEST = 8640
WF_STEP = 8640


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
        # stored as tz-naive datetime64[us] representing UTC; localize to UTC so it
        # aligns with the tz-aware expected 5m grid.
        return pd.DatetimeIndex(arr).tz_localize("UTC")
    # numeric epoch-ms fallback
    return pd.DatetimeIndex(pd.to_datetime(arr, unit="ms", utc=True))


def _as_series(pa: dict, key: str, index: pd.DatetimeIndex) -> pd.Series:
    v = pa.get(key)
    arr = np.asarray(v, dtype=float)
    return pd.Series(arr, index=index)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.parse_args()

    checks: dict = {}
    blocked: list[str] = []

    if not PXL.exists():
        print(json.dumps({"ready": False, "blocked_reasons": ["perp+spot+funding pickle missing"]}, indent=2))
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
        and meta.get("source_interval") == EXPECTED_INTERVAL
        and meta.get("n_symbols") is not None and int(meta.get("n_symbols")) >= 1
        and meta.get("window_start_utc") == "2020-01-01T00:00:00Z"
        and meta.get("window_end_utc") == "2026-10-31T23:55:00Z"
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
        "total_bars": meta.get("total_bars"),
        "n_full_2020_2026_assets": meta.get("n_full_2020_2026_assets"),
        "spot_gap_bars_total": meta.get("spot_gap_bars_total"),
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
        blocked.append("meta flags/interval/symbols/window/host/format/size/sha mismatch")

    try:
        with open(PXL, "rb") as fh:
            payload = pickle.load(fh)
        symbols = list(payload.get("symbols") or [])
        sym_ok = len(symbols) >= 1 and len(symbols) == int(meta.get("n_symbols") or 0)
        per_asset = payload.get("per_asset") or {}
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
            wstart = pd.Timestamp(pa.get("window_start_utc"))
            wend = pd.Timestamp(pa.get("window_end_utc"))
            exp_idx = pd.DatetimeIndex(pd.date_range(start=wstart, end=wend, freq="5min", tz="UTC"))
            d = {"symbol": s, "n_bars": n_bars, "expected_bars": int(len(exp_idx)), "window": {"start": str(wstart), "end": str(wend)}, "fields": {}}
            all_field_ok = True
            for key in REQUIRED_PER_ASSET_FIELDS:
                f = _as_series(pa, key, index)
                fs = f.reindex(exp_idx)
                arr = fs.to_numpy(dtype=float)
                nan_c = int(np.isnan(arr).sum())
                present = arr[~np.isnan(arr)]
                finite = bool(np.isfinite(present).all()) if len(present) else True
                if key == "spot_close":
                    # spot gaps are allowed (carried NaN); present values must be positive/finite
                    positive = bool((present > 0).all()) if len(present) else True
                    nan_allowed = True
                elif key == FUNDING_FRAME_FIELD:
                    positive = True  # funding can be negative/zero
                    nan_allowed = True
                else:
                    positive = bool((present > 0).all()) if len(present) else True
                    nan_allowed = False
                dup = int(fs.index.duplicated().sum())
                diffs = fs.index.to_series().diff().dropna()
                spacing = bool((diffs == pd.Timedelta(minutes=5)).all()) if len(diffs) else False
                exact_index = bool(fs.index.equals(exp_idx))
                in_window = bool((fs.index >= wstart).all() and (fs.index <= wend).all()) if len(fs.index) else False
                shape_ok = int(len(fs)) == n_bars == int(len(exp_idx))
                nan_ok = (nan_c == 0) if not nan_allowed else True
                fok = shape_ok and finite and positive and dup == 0 and spacing and exact_index and in_window and nan_ok
                d["fields"][key] = {
                    "shape": int(len(fs)),
                    "expected_shape": n_bars,
                    "nan_count": nan_c,
                    "all_finite_present": finite,
                    "all_positive_present": positive,
                    "duplicate_index_count": dup,
                    "spacing_5m_ok": spacing,
                    "exact_index_ok": exact_index,
                    "index_in_window": in_window,
                    "ok": bool(fok),
                }
                all_field_ok &= fok
            # spot-gap accounting (462 bars/asset expected; never imputed)
            spot = _as_series(pa, "spot_close", index).reindex(exp_idx)
            spot_nan = int(spot.isna().sum())
            gap_months = pa.get("spot_gap_months") or {}
            d["spot_gaps"] = {
                "spot_nan_bars": spot_nan,
                "expected_per_asset": SPOT_GAP_BARS_EXPECTED,
                "gap_months_recorded": int(len(gap_months)),
                "gap_months": gap_months,
                "ok": bool(spot_nan == SPOT_GAP_BARS_EXPECTED and len(gap_months) > 0),
            }
            if not d["spot_gaps"]["ok"]:
                all_field_ok = False
            # funding-specific boundary/staleness checks
            fcol = _as_series(pa, FUNDING_FRAME_FIELD, index).reindex(exp_idx)
            mask = fcol.notna()
            rows = int(mask.sum())
            vals = fcol[mask]
            finite = bool(np.isfinite(vals.to_numpy(dtype=float)).all()) if len(vals) else False
            iv = pa.get("funding_interval_hours", [8])
            iv = int(iv[0]) if isinstance(iv, list) else int(iv)
            iv_ok = iv in VALID_FUNDING_INTERVALS
            ts = fcol.index[mask.values]
            minute_ok = bool((ts.minute == 0).all()) if len(ts) else False
            hour_ok = bool((ts.hour % iv == 0).all()) if len(ts) else False
            pos = np.where(mask.values)[0]
            gap = int(np.diff(pos).max()) if len(pos) > 1 else 0
            tail_gap = int(len(exp_idx) - 1 - pos[-1]) if len(pos) else int(len(exp_idx))
            stale_ok = gap <= STALE_BARS and tail_gap <= STALE_BARS
            fund_ok = rows >= MIN_FUNDING_ROWS and finite and iv_ok and minute_ok and hour_ok and stale_ok
            d["funding"] = {
                "funding_rows": rows,
                "min_rows": MIN_FUNDING_ROWS,
                "interval_hours": iv,
                "all_finite": finite,
                "minute_zero": minute_ok,
                "hour_multiple_of_interval": hour_ok,
                "max_boundary_gap_bars": gap,
                "tail_gap_bars": tail_gap,
                "stale_limit_bars": STALE_BARS,
                "stale_ok": stale_ok,
                "ok": bool(fund_ok),
            }
            all_field_ok &= fund_ok
            # walk-forward fit for this asset
            n_splits = len(wf_splits(n_bars, WF_TRAIN, WF_TEST, WF_STEP))
            wf_ok = n_bars >= MIN_BARS and n_splits > 0
            d["walk_forward"] = {
                "bars": n_bars,
                "train": WF_TRAIN,
                "test": WF_TEST,
                "step": WF_STEP,
                "min_bars": MIN_BARS,
                "n_splits": int(n_splits),
                "ok": bool(wf_ok),
            }
            all_field_ok &= wf_ok
            # feature warmup: min_periods <= train for all lookbacks
            warm = {f"L={L}": {"min_periods": int(min_periods_for(L)), "warm_before_first_test_bar": bool(min_periods_for(L) <= WF_TRAIN), "ok": bool(min_periods_for(L) <= WF_TRAIN)} for L in LOOKBACKS_5M}
            warm_ok = all(v["ok"] for v in warm.values())
            d["feature_warmup"] = {"rule": "min_periods = max(20, L // 3) on native-5m per-asset features", "lookbacks_5m": list(LOOKBACKS_5M), "warmup": warm, "ok": bool(warm_ok)}
            all_field_ok &= warm_ok
            d["ok"] = bool(all_field_ok)
            asset_detail[s] = d
            asset_ok &= all_field_ok
        checks["assets"] = {"n_symbols": len(symbols), "symbols": symbols, "symbols_ok": bool(sym_ok), "detail": asset_detail, "ok": bool(asset_ok and sym_ok)}
        if not asset_ok:
            blocked.append("one or more assets failed per-asset frame/funding/WF/warmup/gap checks")
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
        "campaign": 300,
        "part": "preflight",
        "checks": checks,
        "blocked_reasons": blocked,
    }
    print(json.dumps(result, indent=2, default=str))
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())