#!/usr/bin/env python3
"""C290 preflight: fail-closed verification of the wider-universe true-5m OHLCV
cache before the cross-sectional stat-arb campaign runs.

C290 is a NEW economic dimension (wider USDT spot universe, true-5m intrabar
range realized vol + true-5m quote volume + 5m close realized skew), absent from
the C281B..C286, C288, C289 record.  This preflight verifies:

- SHA256-from-bytes of the ingested OHLCV pickle matches the meta-recorded sha;
- meta JSON real/fabricated flags and shape/window;
- every frame (open/high/low/close/volume/quote_volume) is exactly
  (26208 x n_symbols) over 2026-08-01T00:00Z -> 2026-10-30T23:55Z, with zero NaNs,
  strictly positive prices, duplicate-free index, exact 5m spacing;
- walk-forward split math: train=720, test=168, step=168 -> 151 OOS splits, and the
  last OOS test window fits inside the cache;
- true-5m feature warmup: rolling features with min_periods=max(20,L//3) are warm
  before the first OOS test bar for every lookback L in {288, 1008, 2016}.

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

OHLCV = CACHE / "campaign290_ohlcv.pkl"
OHLCV_META = CACHE / "campaign290_ohlcv.meta.json"
OHLCV_PROV = CACHE / "campaign290_ohlcv.provenance.json"

EXPECTED_ROWS = 26208
EXPECTED_START = "2026-08-01 00:00:00+00:00"
EXPECTED_END = "2026-10-30 23:55:00+00:00"
EXPECTED_INTERVAL = "5m"
REQUIRED_FRAMES = ("opens", "highs", "lows", "closes", "volumes", "quote_volumes")

LOOKBACKS_5M = (288, 1008, 2016)
WF_TRAIN = 720
WF_TEST = 168
WF_STEP = 168
EXPECTED_WF_SPLITS = 151


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def min_periods_for(L: int) -> int:
    return max(20, L // 3)


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
        and meta.get("rows") == EXPECTED_ROWS
        and meta.get("real_data_only") is True
        and meta.get("fabricated_data") is False
        and meta.get("fetch_real_data_only") is True
        and meta.get("fetch_fabricated_data") is False
        and pkl_sha == meta.get("sha256_from_bytes")
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
            spacing = bool((diffs == pd.Timedelta(minutes=5)).all()) if len(diffs) else False
            start_ok = str(idx.min()) == EXPECTED_START
            end_ok = str(idx.max()) == EXPECTED_END
            cols_ok = tuple(str(c) for c in df.columns) == tuple(symbols)
            ok = (
                shape == (EXPECTED_ROWS, len(symbols))
                and nan_c == 0
                and finite
                and positive
                and dup == 0
                and spacing
                and start_ok
                and end_ok
                and cols_ok
            )
            frame_detail[key] = {
                "shape": list(shape),
                "expected_shape": [EXPECTED_ROWS, len(symbols)],
                "nan_count": nan_c,
                "all_finite": finite,
                "all_positive": positive,
                "duplicate_index_count": dup,
                "spacing_5m_ok": spacing,
                "start": str(idx.min()),
                "end": str(idx.max()),
                "columns_match": cols_ok,
                "ok": bool(ok),
            }
            frame_ok &= ok
        checks["frames"] = {"n_symbols": len(symbols), "detail": frame_detail, "ok": bool(frame_ok)}
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
        last_test_start = WF_TRAIN + (EXPECTED_WF_SPLITS - 1) * WF_STEP
        last_test_end = last_test_start + WF_TEST
        wf_ok = n_splits == EXPECTED_WF_SPLITS and last_test_end <= n_bars
        checks["walk_forward"] = {
            "bars": int(n_bars),
            "train": WF_TRAIN,
            "test": WF_TEST,
            "step": WF_STEP,
            "n_splits": int(n_splits),
            "expected_n_splits": EXPECTED_WF_SPLITS,
            "last_test_start": int(last_test_start),
            "last_test_end": int(last_test_end),
            "ok": bool(wf_ok),
        }
        if not wf_ok:
            blocked.append("walk-forward split count/fit check failed")

        warm = {}
        warm_ok = True
        for L in LOOKBACKS_5M:
            mp = min_periods_for(L)
            ok = bool(mp <= WF_TRAIN)
            warm[f"L={L}"] = {"min_periods": int(mp), "warm_before_first_test_bar": ok, "ok": ok}
            warm_ok &= ok
        checks["feature_warmup"] = {
            "rule": "min_periods = max(20, L // 3) on true-5m features",
            "lookbacks_5m": list(LOOKBACKS_5M),
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
        "campaign": 290,
        "part": "preflight",
        "checks": checks,
        "blocked_reasons": blocked,
    }
    print(json.dumps(result, indent=2, default=str))
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())