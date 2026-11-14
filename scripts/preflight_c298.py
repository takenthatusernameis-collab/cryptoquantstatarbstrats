#!/usr/bin/env python3
"""C298 preflight: fail-closed verification of the real multi-year (2020-01 ..
2026-10) USDT-M perp 1h klines + funding + spot cache before the funding-carry /
spot/perp basis cross-sectional campaign.

Verifies:

- SHA256-from-bytes of the ingested pickle matches the meta-recorded sha;
- meta flags (real/fabricated), interval 1h, rows, n_symbols, source hosts;
- every perp frame (open/high/low/close/volume) is exactly (n_bars x n_symbols)
  over 2020-01-01T00:00Z -> 2026-10-31T23:00Z, zero NaNs, strictly positive,
  exact 1h spacing, duplicate-free index, columns == symbols; spot_closes carries
  the same shape/index for every symbol (basis leg);
- funding frame is (n_bars x n_symbols) with >= 90 finite funding rows per asset,
  every funding value sitting on a native Binance funding boundary (minute 0,
  hour a multiple of the symbol's real interval), and no funding gap >
  24h + 1 bar (fail-closed staleness);
- walk-forward split math: train=2160, test=720, step=720 in 1h bars -> every
  OOS test window fits inside the cache;
- feature warmup: rolling features with min_periods=max(20, L//3) are warm before
  the first OOS test bar for every lookback L in {168, 720, 2160};
- provenance json exists.

The script never fetches, imputes, resamples, or fabricates data. Exit 0 iff every
check passes; any mismatch/missing file is a fail-closed blocker.
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

PXL = CACHE / "campaign298_multianual_perp_funding_basis.pkl"
PXL_META = CACHE / "campaign298_multianual_perp_funding_basis.meta.json"
PXL_PROV = CACHE / "campaign298_multianual_perp_funding_basis.provenance.json"

EXPECTED_START = "2020-01-01 00:00:00+00:00"
EXPECTED_END = "2026-10-31 23:00:00+00:00"
EXPECTED_INTERVAL = "1h"
REQUIRED_FRAMES = ("opens", "highs", "lows", "closes", "volumes", "spot_closes")
FUNDING_FRAME = "funding_rates"
VALID_FUNDING_INTERVALS = {1, 2, 4, 8}
MIN_FUNDING_ROWS = 90
STALE_BARS = 24 + 1  # 24h + 1 bar on the 1h grid
MIN_SELECTED = 2

LOOKBACKS_1H = (168, 720, 2160)
WF_TRAIN = 2160
WF_TEST = 720
WF_STEP = 720


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def min_periods_for(L: int) -> int:
    return max(20, L // 3)


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

    expected_rows = int(meta.get("expected_bars") or 0)
    n_symbols_meta = int(meta.get("n_symbols") or 0)

    flags_ok = (
        meta.get("interval") == EXPECTED_INTERVAL
        and meta.get("source_interval") == "5m"
        and meta.get("rows") == expected_rows
        and expected_rows > 0
        and meta.get("n_symbols") >= 2
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
        "rows": meta.get("rows"),
        "expected_rows": expected_rows,
        "n_symbols": meta.get("n_symbols"),
        "real_data_only": meta.get("real_data_only"),
        "fabricated_data": meta.get("fabricated_data"),
        "source_host": meta.get("source_host"),
        "spot_host": meta.get("spot_host"),
        "sha256_from_bytes": meta.get("sha256_from_bytes"),
        "actual_sha256": pkl_sha,
        "ok": bool(flags_ok),
    }
    if not flags_ok:
        blocked.append("meta flags/interval/rows/symbols/host/sha mismatch")

    try:
        with open(PXL, "rb") as fh:
            payload = pickle.load(fh)
        symbols = list(payload.get("symbols") or meta.get("symbols") or [])
        sym_ok = len(symbols) >= MIN_SELECTED and len(symbols) == n_symbols_meta
        exp_idx = pd.DatetimeIndex(pd.date_range(start="2020-01-01", end="2026-10-31T23:00", freq="1h", tz="UTC"))
        frame_ok = True
        frame_detail = {}
        perp_frames = REQUIRED_FRAMES  # open/high/low/close/volume + spot_closes handled below
        for key in ("opens", "highs", "lows", "closes", "volumes"):
            df = payload.get(key)
            if not isinstance(df, pd.DataFrame):
                frame_detail[key] = {"ok": False, "error": "missing or not a DataFrame"}
                frame_ok = False
                continue
            arr = df.to_numpy(dtype=float)
            nan_c = int(np.isnan(arr).sum())
            finite = bool(np.isfinite(arr).all())
            positive = bool((arr > 0).all()) if key != "volumes" else bool((arr >= 0).all())
            shape = tuple(int(x) for x in df.shape)
            idx = pd.DatetimeIndex(df.index)
            dup = int(idx.duplicated().sum())
            diffs = idx.to_series().diff().dropna()
            spacing = bool((diffs == pd.Timedelta(hours=1)).all()) if len(diffs) else False
            start_ok = str(idx.min()) == EXPECTED_START
            end_ok = str(idx.max()) == EXPECTED_END
            cols_ok = tuple(str(c) for c in df.columns) == tuple(symbols)
            exact_index = bool(df.index.equals(exp_idx))
            ok = (
                shape == (expected_rows, len(symbols))
                and nan_c == 0
                and finite
                and positive
                and dup == 0
                and spacing
                and start_ok
                and end_ok
                and cols_ok
                and exact_index
            )
            frame_detail[key] = {
                "shape": list(shape),
                "expected_shape": [expected_rows, len(symbols)],
                "nan_count": nan_c,
                "all_finite": finite,
                "all_positive": positive,
                "duplicate_index_count": dup,
                "spacing_1h_ok": spacing,
                "exact_index_ok": exact_index,
                "start": str(idx.min()),
                "end": str(idx.max()),
                "columns_match": cols_ok,
                "ok": bool(ok),
            }
            frame_ok &= ok
        # spot leg: full perp window required, but spot feed gaps (recorded in
        # provenance) are NOT imputed -- NaN only at those hours; gates block
        # any trade needing missing spot data.
        spot = payload.get("spot_closes")
        if not isinstance(spot, pd.DataFrame):
            frame_detail["spot_closes"] = {"ok": False, "error": "missing or not a DataFrame"}
            frame_ok = False
        else:
            sarr = spot.to_numpy(dtype=float)
            sidx = pd.DatetimeIndex(spot.index)
            snan = int(np.isnan(sarr).sum())
            sfinite = bool(np.isfinite(sarr[~np.isnan(sarr)]).all()) if snan < sarr.size else True
            spos = bool((sarr[~np.isnan(sarr)] > 0).all()) if snan < sarr.size else True
            sshape = tuple(int(x) for x in spot.shape)
            sup = int(spot.index.duplicated().sum())
            sin_window = bool((sidx >= pd.Timestamp(EXPECTED_START)).all() and (sidx <= pd.Timestamp(EXPECTED_END)).all()) if len(sidx) else False
            ssubset = bool(sidx.isin(exp_idx).all())
            scols = tuple(str(c) for c in spot.columns) == tuple(symbols)
            sok = (sshape == (expected_rows, len(symbols)) and sfinite and spos and sup == 0 and sin_window and ssubset and scols)
            frame_detail["spot_closes"] = {
                "shape": list(sshape),
                "expected_shape": [expected_rows, len(symbols)],
                "nan_count": snan,
                "all_finite_present": sfinite,
                "all_positive_present": spos,
                "duplicate_index_count": sup,
                "index_in_window": sin_window,
                "index_subset_of_expected": ssubset,
                "columns_match": scols,
                "ok": bool(sok),
            }
            frame_ok &= sok
        checks["frames"] = {
            "n_symbols": len(symbols),
            "symbols": symbols,
            "symbols_ok": bool(sym_ok),
            "detail": frame_detail,
            "ok": bool(frame_ok and sym_ok),
        }
        if not frame_ok:
            blocked.append("one or more frames failed shape/window/nan/positive/spacing/index check")
        if not sym_ok:
            blocked.append("universe size mismatch")
    except Exception as exc:  # noqa: BLE001
        checks["frames"] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        blocked.append("frames could not be loaded")

    # ---- funding frame: coverage, boundary alignment, staleness ----
    try:
        fr = payload.get(FUNDING_FRAME)
        if not isinstance(fr, pd.DataFrame):
            checks["funding"] = {"ok": False, "error": "funding_rates missing or not a DataFrame"}
            blocked.append("funding_rates frame missing")
        else:
            idx = pd.DatetimeIndex(fr.index)
            fund_detail = {}
            fund_ok = True
            total_rows = 0
            intervals_by_symbol = meta.get("funding_intervals_by_symbol", {}) or {}
            for s in symbols:
                col = fr[s]
                mask = col.notna()
                rows = int(mask.sum())
                total_rows += rows
                vals = col[mask]
                finite = bool(np.isfinite(vals.to_numpy(dtype=float)).all()) if len(vals) else False
                iv = intervals_by_symbol.get(s, [8])
                iv = int(iv[0]) if isinstance(iv, list) else int(iv)
                iv_ok = iv in VALID_FUNDING_INTERVALS
                ts = idx[mask.values]
                minute_ok = bool((ts.minute == 0).all()) if len(ts) else False
                hour_ok = bool((ts.hour % iv == 0).all()) if len(ts) else False
                pos = np.where(mask.values)[0]
                gap = int(np.diff(pos).max()) if len(pos) > 1 else 0
                tail_gap = int(len(idx) - 1 - pos[-1]) if len(pos) else int(len(idx))
                stale_ok = gap <= STALE_BARS and tail_gap <= STALE_BARS
                sym_ok = rows >= MIN_FUNDING_ROWS and finite and iv_ok and minute_ok and hour_ok and stale_ok
                fund_detail[s] = {
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
                    "ok": bool(sym_ok),
                }
                fund_ok &= sym_ok
            checks["funding"] = {
                "total_funding_rows": total_rows,
                "detail": fund_detail,
                "ok": bool(fund_ok),
            }
            if not fund_ok:
                blocked.append("one or more symbols failed funding coverage/boundary/staleness check")
    except Exception as exc:  # noqa: BLE001
        checks["funding"] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        blocked.append("funding checks could not be computed")

    # ---- walk-forward + feature warmup (on perp closes) ----
    try:
        closes = payload["closes"].astype(float).sort_index()
        n_bars = len(closes)
        n_splits = (n_bars - WF_TRAIN - WF_TEST) // WF_STEP + 1
        last_test_start = WF_TRAIN
        last_test_end = last_test_start + WF_TEST + (n_splits - 1) * WF_STEP
        wf_ok = n_splits > 0 and last_test_end <= n_bars
        checks["walk_forward"] = {
            "bars": int(n_bars),
            "train": WF_TRAIN,
            "test": WF_TEST,
            "step": WF_STEP,
            "n_splits": int(n_splits),
            "last_test_start": int(last_test_start),
            "last_test_end": int(last_test_end),
            "ok": bool(wf_ok),
        }
        if not wf_ok:
            blocked.append("walk-forward split count/fit check failed")

        warm = {}
        warm_ok = True
        for L in LOOKBACKS_1H:
            mp = min_periods_for(L)
            ok = bool(mp <= WF_TRAIN)
            warm[f"L={L}"] = {"min_periods": int(mp), "warm_before_first_test_bar": ok, "ok": ok}
            warm_ok &= ok
        checks["feature_warmup"] = {
            "rule": "min_periods = max(20, L // 3) on true-1h features",
            "lookbacks_1h": list(LOOKBACKS_1H),
            "warmup": warm,
            "ok": bool(warm_ok),
        }
        if not warm_ok:
            blocked.append("feature warmup insufficient before first OOS test window")
    except Exception as exc:  # noqa: BLE001
        checks["walk_forward"] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        checks["feature_warmup"] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        blocked.append("walk-forward/feature warmup checks could not be computed")

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
        "campaign": 298,
        "part": "preflight",
        "checks": checks,
        "blocked_reasons": blocked,
    }
    print(json.dumps(result, indent=2, default=str))
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
