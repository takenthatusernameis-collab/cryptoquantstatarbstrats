#!/usr/bin/env python3
"""C299 preflight: fail-closed verification of the real per-asset (2020-01 ..
2026-10) USDT-M perp 1h klines + funding + spot cache before the funding-carry /
spot-perp basis time-series campaign.

Each asset trades on its OWN maximal contiguous real coverage window (no
cross-asset K-coverage constraint).  Verifies:

- SHA256-from-bytes of the ingested pickle matches the meta-recorded sha;
- meta flags (real/fabricated), interval 1h, n_symbols, window, source hosts;
- for every selected asset: perp frames (open/high/low/close/volume) exactly
  (n_bars x 1) over its contiguous window, zero NaN, strictly positive, exact
  1h spacing, duplicate-free index; spot_closes carries the same index for the
  asset (basis leg), present values finite/positive, gaps (recorded) stay NaN;
- funding frame per asset: >= 90 finite funding rows, every funding value on a
  native Binance funding boundary (minute 0, hour multiple of the asset's real
  interval), no funding gap > 24h + 1 bar (fail-closed staleness);
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

PXL = CACHE / "campaign299_multianual_perp_funding_basis_ts.pkl"
PXL_META = CACHE / "campaign299_multianual_perp_funding_basis_ts.meta.json"
PXL_PROV = CACHE / "campaign299_multianual_perp_funding_basis_ts.provenance.json"

EXPECTED_INTERVAL = "1h"
REQUIRED_PER_ASSET_FIELDS = ("opens", "highs", "lows", "closes", "volumes", "spot_closes", "funding_rates")
FUNDING_FRAME_FIELD = "funding_rates"
VALID_FUNDING_INTERVALS = {1, 2, 4, 8}
MIN_FUNDING_ROWS = 90
STALE_BARS = 24 + 1  # 24h + 1 bar on the 1h grid
MIN_BARS = 2880  # one WF train+test (2160+720)

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

    try:
        meta = json.loads(PXL_META.read_text())
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"ready": False, "blocked_reasons": [f"meta unreadable: {exc}"]}, indent=2))
        return 1

    flags_ok = (
        meta.get("interval") == EXPECTED_INTERVAL
        and meta.get("source_interval") == "5m"
        and meta.get("n_symbols") is not None and int(meta.get("n_symbols")) >= 1
        and meta.get("window_start_utc") == "2020-01-01T00:00:00Z"
        and meta.get("window_end_utc") == "2026-10-31T23:00:00Z"
        and meta.get("real_data_only") is True
        and meta.get("fabricated_data") is False
        and meta.get("fetch_real_data_only") is True
        and meta.get("fetch_fabricated_data") is False
        and meta.get("source_host") == "https://data.binance.vision"
        and meta.get("spot_host") == "https://data-api.binance.vision"
        and pkl_sha == meta.get("sha256_from_bytes")
    )
    checks["meta"] = {
        "interval": meta.get("interval"),
        "source_interval": meta.get("source_interval"),
        "n_symbols": meta.get("n_symbols"),
        "total_bars": meta.get("total_bars"),
        "n_full_2020_2026_assets": meta.get("n_full_2020_2026_assets"),
        "window_start_utc": meta.get("window_start_utc"),
        "window_end_utc": meta.get("window_end_utc"),
        "real_data_only": meta.get("real_data_only"),
        "fabricated_data": meta.get("fabricated_data"),
        "source_host": meta.get("source_host"),
        "spot_host": meta.get("spot_host"),
        "sha256_from_bytes": meta.get("sha256_from_bytes"),
        "actual_sha256": pkl_sha,
        "ok": bool(flags_ok),
    }
    if not flags_ok:
        blocked.append("meta flags/interval/symbols/window/host/sha mismatch")

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
            index = pa.get("index")
            if not isinstance(index, pd.DatetimeIndex):
                index = pd.DatetimeIndex(pa.get("index", []))
            n_bars = int(pa.get("n_bars") or len(index))
            wstart = pd.Timestamp(pa.get("window_start_utc"))
            wend = pd.Timestamp(pa.get("window_end_utc"))
            exp_idx = pd.DatetimeIndex(pd.date_range(start=wstart, end=wend, freq="1h", tz="UTC"))
            d = {"symbol": s, "n_bars": n_bars, "expected_bars": int(len(exp_idx)), "window": {"start": str(wstart), "end": str(wend)}, "fields": {}}
            all_field_ok = True
            for key in REQUIRED_PER_ASSET_FIELDS:
                field_ok = True
                f = pa.get(key)
                if not isinstance(f, pd.Series):
                    d["fields"][key] = {"ok": False, "error": "missing or not a Series"}
                    all_field_ok = False
                    field_ok = False
                else:
                    fs = f.astype(float).reindex(exp_idx)
                    arr = fs.to_numpy(dtype=float)
                    nan_c = int(np.isnan(arr).sum())
                    present = arr[~np.isnan(arr)]
                    finite = bool(np.isfinite(present).all()) if len(present) else True
                    if key == "spot_closes":
                        positive = bool((present > 0).all()) if len(present) else True
                        vol_check = True
                    elif key == "volumes":
                        positive = bool((present >= 0).all()) if len(present) else True
                        vol_check = True
                    elif key == FUNDING_FRAME_FIELD:
                        # funding rates can be negative or zero (carry); only
                        # present values must be finite (positivity not required).
                        positive = True
                        vol_check = True
                    else:
                        # price frames: strictly positive
                        positive = bool((present > 0).all()) if len(present) else True
                        vol_check = bool((present >= 0).all()) if key == "volumes" and len(present) else True
                    idx = fs.index
                    dup = int(idx.duplicated().sum())
                    diffs = idx.to_series().diff().dropna()
                    spacing = bool((diffs == pd.Timedelta(hours=1)).all()) if len(diffs) else False
                    exact_index = bool(idx.equals(exp_idx))
                    in_window = bool((idx >= wstart).all() and (idx <= wend).all()) if len(idx) else False
                    shape_ok = int(len(fs)) == n_bars == int(len(exp_idx))
                    nan_allowed = key in ("spot_closes", FUNDING_FRAME_FIELD)
                    nan_ok = nan_c == 0 or (nan_allowed and nan_c >= 0)
                    fok = (
                        shape_ok
                        and finite
                        and positive
                        and vol_check
                        and dup == 0
                        and spacing
                        and exact_index
                        and in_window
                        and nan_ok
                    )
                    d["fields"][key] = {
                        "shape": int(len(fs)),
                        "expected_shape": n_bars,
                        "nan_count": nan_c,
                        "all_finite_present": finite,
                        "all_positive_present": positive,
                        "duplicate_index_count": dup,
                        "spacing_1h_ok": spacing,
                        "exact_index_ok": exact_index,
                        "index_in_window": in_window,
                        "ok": bool(fok),
                    }
                    all_field_ok &= fok
                    field_ok = fok
                if not field_ok:
                    all_field_ok = False
            # funding-specific boundary/staleness checks
            fcol = pa.get(FUNDING_FRAME_FIELD)
            fund_detail = {}
            fund_ok = True
            if isinstance(fcol, pd.Series):
                fr = fcol.astype(float).reindex(exp_idx)
                mask = fr.notna()
                rows = int(mask.sum())
                vals = fr[mask]
                finite = bool(np.isfinite(vals.to_numpy(dtype=float)).all()) if len(vals) else False
                iv = pa.get("funding_interval_hours", [8])
                iv = int(iv[0]) if isinstance(iv, list) else int(iv)
                iv_ok = iv in VALID_FUNDING_INTERVALS
                ts = fr.index[mask.values]
                minute_ok = bool((ts.minute == 0).all()) if len(ts) else False
                hour_ok = bool((ts.hour % iv == 0).all()) if len(ts) else False
                pos = np.where(mask.values)[0]
                gap = int(np.diff(pos).max()) if len(pos) > 1 else 0
                tail_gap = int(len(exp_idx) - 1 - pos[-1]) if len(pos) else int(len(exp_idx))
                stale_ok = gap <= STALE_BARS and tail_gap <= STALE_BARS
                fund_ok = rows >= MIN_FUNDING_ROWS and finite and iv_ok and minute_ok and hour_ok and stale_ok
                fund_detail = {
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
            else:
                fund_detail = {"ok": False, "error": "funding_rates missing or not a Series"}
                fund_ok = False
            d["funding"] = fund_detail
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
            warm = {f"L={L}": {"min_periods": int(min_periods_for(L)), "warm_before_first_test_bar": bool(min_periods_for(L) <= WF_TRAIN), "ok": bool(min_periods_for(L) <= WF_TRAIN)} for L in LOOKBACKS_1H}
            warm_ok = all(v["ok"] for v in warm.values())
            d["feature_warmup"] = {"rule": "min_periods = max(20, L // 3) on true-1h per-asset features", "lookbacks_1h": list(LOOKBACKS_1H), "warmup": warm, "ok": bool(warm_ok)}
            all_field_ok &= warm_ok
            d["ok"] = bool(all_field_ok)
            asset_detail[s] = d
            asset_ok &= all_field_ok
        checks["assets"] = {"n_symbols": len(symbols), "symbols": symbols, "symbols_ok": bool(sym_ok), "detail": asset_detail, "ok": bool(asset_ok and sym_ok)}
        if not asset_ok:
            blocked.append("one or more assets failed per-asset frame/funding/WF/warmup checks")
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
        "campaign": 299,
        "part": "preflight",
        "checks": checks,
        "blocked_reasons": blocked,
    }
    print(json.dumps(result, indent=2, default=str))
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
