#!/usr/bin/env python3
"""C297 preflight: fail-closed verification of the real DAILY (1d) multi-year
spot OHLCV cache before the cross-sectional stat-arb campaign runs.

C297 is a NEW economic regime (daily horizon over a multi-year window,
2021-01-01 .. 2026-11-13), absent from the C281B..C296 record (5m/1h over a
single ~3-month window).  This preflight verifies:

- SHA256-from-bytes of the ingested OHLCV pickle matches the meta-recorded sha;
- meta JSON real/fabricated flags, interval=1d, and internal shape/window;
- every frame (open/high/low/close/volume/quote_volume) is exactly
  (n_rows x n_symbols) over the daily UTC grid, with zero NaNs, strictly positive
  prices, duplicate-free index, exact 1-day spacing, identical columns;
- walk-forward split math: train=504, test=126, step=126 -> >=4 OOS splits, and
  the last OOS test window fits inside the cache;
- daily feature warmup: rolling features with min_periods=max(20,L//3) are warm
  before the first OOS test bar for every lookback L in {20, 60, 120}.

The script never fetches, imputes, resamples, or fabricates data. Exit code 0 iff
every check passes; any mismatch/missing file is a fail-closed blocker.
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

OHLCV = CACHE / "campaign297_daily_ohlcv.pkl"
OHLCV_META = CACHE / "campaign297_daily_ohlcv.meta.json"
OHLCV_PROV = CACHE / "campaign297_daily_ohlcv.provenance.json"

EXPECTED_INTERVAL = "1d"
REQUIRED_FRAMES = ("opens", "highs", "lows", "closes", "volumes", "quote_volumes")
ONE_DAY = pd.Timedelta(days=1)

LOOKBACKS_DAILY = (20, 60, 120)
WF_TRAIN = 504
WF_TEST = 126
WF_STEP = 126
MIN_SPLITS = 4


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

    # ---- meta + sha ----
    if not OHLCV.exists():
        print(json.dumps({"ready": False, "blocked_reasons": ["ohlcv pickle missing"]}, indent=2))
        return 1
    pkl_sha = sha256_file(OHLCV)

    try:
        meta = json.loads(OHLCV_META.read_text())
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"ready": False, "blocked_reasons": [f"meta unreadable: {exc}"]}, indent=2))
        return 1

    flags_ok = (
        meta.get("interval") == EXPECTED_INTERVAL
        and meta.get("real_data_only") is True
        and meta.get("fabricated_data") is False
        and meta.get("fetch_real_data_only") is True
        and meta.get("fetch_fabricated_data") is False
        and pkl_sha == meta.get("sha256_from_bytes")
        and isinstance(meta.get("rows"), int)
        and meta.get("rows", 0) > 0
    )
    checks["meta"] = {
        "interval": meta.get("interval"),
        "rows": meta.get("rows"),
        "real_data_only": meta.get("real_data_only"),
        "fabricated_data": meta.get("fabricated_data"),
        "sha256_from_bytes": meta.get("sha256_from_bytes"),
        "actual_sha256": pkl_sha,
        "ok": bool(flags_ok),
    }
    if not flags_ok:
        blocked.append("meta flags/interval/rows/sha mismatch")

    # ---- frames ----
    try:
        with open(OHLCV, "rb") as fh:
            payload = pickle.load(fh)
        symbols = list(payload.get("symbols") or meta.get("symbols") or [])
        frame_ok = True
        frame_detail = {}
        rows_seen: set[int] = set()
        for key in REQUIRED_FRAMES:
            df = payload.get(key)
            if not isinstance(df, pd.DataFrame):
                frame_detail[key] = {"ok": False, "error": "missing or not a DataFrame"}
                frame_ok = False
                continue
            arr = df.to_numpy(dtype=float)
            nan_c = int(np.isnan(arr).sum())
            finite = bool(np.isfinite(arr).all())
            positive = bool((arr > 0).all())
            shape = tuple(int(x) for x in df.shape)
            idx = pd.DatetimeIndex(df.index)
            dup = int(idx.duplicated().sum())
            diffs = idx.to_series().diff().dropna()
            spacing = bool((diffs == ONE_DAY).all()) if len(diffs) else False
            cols_ok = tuple(str(c) for c in df.columns) == tuple(symbols)
            rows_seen.add(shape[0])
            n_rows = int(meta.get("rows") or 0)
            ok = (
                n_rows > 0
                and shape[0] == n_rows
                and shape[1] == len(symbols)
                and nan_c == 0
                and finite
                and positive
                and dup == 0
                and spacing
                and cols_ok
            )
            frame_detail[key] = {
                "shape": list(shape),
                "expected_rows": n_rows,
                "n_symbols": len(symbols),
                "nan_count": nan_c,
                "all_finite": finite,
                "all_positive": positive,
                "duplicate_index_count": dup,
                "spacing_1d_ok": spacing,
                "start": str(idx.min()),
                "end": str(idx.max()),
                "columns_match": cols_ok,
                "ok": bool(ok),
            }
            frame_ok &= ok
        if len(rows_seen) > 1:
            frame_ok = False
        checks["frames"] = {
            "n_symbols": len(symbols),
            "n_rows": int(meta.get("rows") or 0),
            "detail": frame_detail,
            "ok": bool(frame_ok),
        }
        if not frame_ok:
            blocked.append("one or more OHLCV frames failed shape/window/nan/positive/spacing check")
    except Exception as exc:  # noqa: BLE001
        checks["frames"] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        blocked.append("ohlcv frames could not be loaded")

    # ---- walk-forward + feature warmup (on closes) ----
    try:
        closes = payload["closes"].astype(float).sort_index()
        n_bars = len(closes)
        n_splits = (n_bars - WF_TRAIN - WF_TEST) // WF_STEP + 1
        last_test_start = WF_TRAIN + (n_splits - 1) * WF_STEP
        last_test_end = last_test_start + WF_TEST
        wf_ok = n_splits >= MIN_SPLITS and last_test_end <= n_bars
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
        for L in LOOKBACKS_DAILY:
            mp = min_periods_for(L)
            ok = bool(mp <= WF_TRAIN)
            warm[f"L={L}"] = {"min_periods": int(mp), "warm_before_first_test_bar": ok, "ok": ok}
            warm_ok &= ok
        checks["feature_warmup"] = {
            "rule": "min_periods = max(20, L // 3) on daily features",
            "lookbacks_daily": list(LOOKBACKS_DAILY),
            "warmup": warm,
            "ok": bool(warm_ok),
        }
        if not warm_ok:
            blocked.append("feature warmup insufficient before first OOS test window")
    except Exception as exc:  # noqa: BLE001
        checks["walk_forward"] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        checks["feature_warmup"] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        blocked.append("walk-forward/feature warmup checks could not be computed")

    # ---- provenance present ----
    checks["provenance"] = {
        "path": str(OHLCV_PROV.relative_to(ROOT)) if OHLCV_PROV.exists() else str(OHLCV_PROV),
        "exists": OHLCV_PROV.exists(),
        "ok": bool(OHLCV_PROV.exists()),
    }
    if not OHLCV_PROV.exists():
        blocked.append("provenance json missing")

    ready = not blocked
    result = {
        "ready": ready,
        "real_data_only": True,
        "fabricated_data": False,
        "campaign": 297,
        "part": "preflight",
        "checks": checks,
        "blocked_reasons": blocked,
    }
    print(json.dumps(result, indent=2, default=str))
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())