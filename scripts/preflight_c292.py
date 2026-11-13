#!/usr/bin/env python3
"""C292 preflight: fail-closed verification of the cross-venue real-spot 5m
cache (Binance cached + OKX paginated) before the basis/lead-lag campaign runs.

C292 is a NEW economic dimension (multi-venue real spot): cross-venue basis
convergence / lead-lag statistical arbitrage on the SAME USDT asset trading on
Binance and OKX. This preflight verifies:

- SHA256-from-bytes of the ingested pickle matches meta;
- meta/provenance real/fabricated flags and shape/window;
- every venue frame (binance/okx opens,highs,lows,closes,volumes) is exactly
  (26208 x n_symbols) over 2026-08-01T00:00Z -> 2026-10-30T23:55Z, zero NaNs,
  strictly positive, finite, duplicate-free index, exact 5m spacing;
- identical symbol columns and index across all 10 frames;
- walk-forward split math: train=720, test=168, step=168 -> 151 OOS splits;
- feature warmup for L in {288, 1008, 2016} (min_periods=max(20,L//3)) fits
  before the first OOS test bar.

Never fetches, imputes, resamples, or fabricates data. Exit 0 iff every check
passes; any mismatch is fail-closed.
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

PKL = CACHE / "campaign292_crossvenue_5m.pkl"
META = CACHE / "campaign292_crossvenue_5m.meta.json"
PROV = CACHE / "campaign292_crossvenue_5m.provenance.json"

EXPECTED_ROWS = 26208
EXPECTED_START = "2026-08-01 00:00:00+00:00"
EXPECTED_END = "2026-10-30 23:55:00+00:00"
EXPECTED_INTERVAL = "5m"
BINANCE_FRAMES = ("binance_opens", "binance_highs", "binance_lows", "binance_closes", "binance_volumes")
OKX_FRAMES = ("okx_opens", "okx_highs", "okx_lows", "okx_closes", "okx_volumes")
REQUIRED_FRAMES = BINANCE_FRAMES + OKX_FRAMES

LOOKBACKS_5M = (288, 1008, 2016)
WF_TRAIN = 720
WF_TEST = 168
WF_STEP = 168
EXPECTED_WF_SPLITS = 151
MIN_SYMBOLS = 2


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

    if not PKL.exists():
        print(json.dumps({"ready": False, "blocked_reasons": ["crossvenue pickle missing"]}, indent=2))
        return 1

    pkl_sha = sha256_file(PKL)
    try:
        meta = json.loads(META.read_text())
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"ready": False, "blocked_reasons": [f"meta unreadable: {exc}"]}, indent=2))
        return 1

    flags_ok = (
        meta.get("interval") == EXPECTED_INTERVAL
        and meta.get("rows") == EXPECTED_ROWS
        and meta.get("real_data_only") is True
        and meta.get("fabricated_data") is False
        and pkl_sha == meta.get("sha256_from_bytes")
    )
    checks["meta"] = {
        "interval": meta.get("interval"),
        "rows": meta.get("rows"),
        "n_symbols": meta.get("n_symbols"),
        "real_data_only": meta.get("real_data_only"),
        "fabricated_data": meta.get("fabricated_data"),
        "sha256_from_bytes": meta.get("sha256_from_bytes"),
        "actual_sha256": pkl_sha,
        "ok": bool(flags_ok),
    }
    if not flags_ok:
        blocked.append("meta flags/interval/rows/sha mismatch")

    try:
        prov = json.loads(PROV.read_text())
        prov_ok = prov.get("real_data_only") is True and prov.get("fabricated_data") is False
    except Exception:
        prov_ok = False
    checks["provenance"] = {"ok": bool(prov_ok)}
    if not prov_ok:
        blocked.append("provenance missing or flags invalid")

    try:
        with open(PKL, "rb") as fh:
            payload = pickle.load(fh)
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"ready": False, "blocked_reasons": [f"pickle unreadable: {exc}"]}, indent=2))
        return 1

    symbols = list(payload.get("symbols", []))
    sym_ok = len(symbols) >= MIN_SYMBOLS and len(symbols) == len(set(symbols))
    checks["symbols"] = {"n": len(symbols), "symbols": symbols, "ok": bool(sym_ok)}
    if not sym_ok:
        blocked.append("symbol set empty/too small/duplicated")

    frame_details = {}
    frames_ok = True
    ref_idx = None
    ref_cols = None
    for name in REQUIRED_FRAMES:
        if name not in payload:
            frames_ok = False
            frame_details[name] = {"present": False, "ok": False}
            continue
        df = payload[name]
        if not isinstance(df, pd.DataFrame):
            frames_ok = False
            frame_details[name] = {"present": True, "ok": False, "reason": "not_dataframe"}
            continue
        idx = df.index
        try:
            idx_utc = pd.DatetimeIndex(idx).tz_convert("UTC")
        except Exception:
            try:
                idx_utc = pd.DatetimeIndex(idx).tz_localize("UTC")
            except Exception:
                idx_utc = pd.DatetimeIndex(idx)
        shape_ok = tuple(df.shape) == (EXPECTED_ROWS, len(symbols))
        start_ok = str(idx_utc.min()) == EXPECTED_START
        end_ok = str(idx_utc.max()) == EXPECTED_END
        no_dupes = bool(idx_utc.is_unique)
        diffs = idx_utc.to_series().diff().dropna()
        spacing_ok = bool((diffs == pd.Timedelta(minutes=5)).all()) if len(diffs) else False
        cols_ok = list(df.columns) == symbols
        vals = df.to_numpy(dtype=float)
        nan_count = int(np.isnan(vals).sum())
        finite_ok = bool(np.isfinite(vals).all())
        is_volume = name.endswith("volumes")
        # Prices must be strictly positive; volume may legitimately be zero on
        # bars with no trades, so require finite non-negative volume instead.
        if is_volume:
            positive_ok = bool((vals >= 0).all()) if finite_ok else False
        else:
            positive_ok = bool((vals > 0).all()) if finite_ok else False
        if ref_idx is None:
            ref_idx = idx_utc
        if ref_cols is None:
            ref_cols = list(df.columns)
        aligned_ok = idx_utc.equals(ref_idx) and list(df.columns) == ref_cols
        ok = bool(shape_ok and start_ok and end_ok and no_dupes and spacing_ok and cols_ok and nan_count == 0 and finite_ok and positive_ok and aligned_ok)
        frame_details[name] = {
            "shape": list(df.shape),
            "start": str(idx_utc.min()),
            "end": str(idx_utc.max()),
            "nan_count": nan_count,
            "all_finite": finite_ok,
            "all_positive": positive_ok,
            "is_volume": is_volume,
            "duplicate_index": not no_dupes,
            "exact_5m_spacing": spacing_ok,
            "columns_match_symbols": cols_ok,
            "aligned_to_reference": aligned_ok,
            "ok": ok,
        }
        frames_ok = frames_ok and ok
    checks["frames"] = {"detail": frame_details, "ok": bool(frames_ok)}
    if not frames_ok:
        blocked.append("one or more venue frames failed shape/window/finite/positive/alignment checks")

    # WF math and warmup
    wf_ok = True
    wf_detail = {}
    try:
        n = EXPECTED_ROWS
        splits = []
        i = 0
        while i + WF_TRAIN + WF_TEST <= n:
            splits.append((i, i + WF_TRAIN, i + WF_TRAIN + WF_TEST))
            i += WF_STEP
        n_splits = len(splits)
        warmups = {}
        for L in LOOKBACKS_5M:
            mp = min_periods_for(L)
            first_test = splits[0][1] if splits else 0
            warm_ok = (mp - 1) < first_test  # need mp bars of history before first test bar
            warmups[str(L)] = {"min_periods": mp, "first_test_bar": first_test, "ok": bool(warm_ok)}
            wf_ok = wf_ok and warm_ok
        wf_detail = {"n_splits": n_splits, "expected": EXPECTED_WF_SPLITS, "warmups": warmups, "ok": bool(wf_ok and n_splits == EXPECTED_WF_SPLITS)}
        if n_splits != EXPECTED_WF_SPLITS:
            blocked.append(f"wf split count {n_splits} != {EXPECTED_WF_SPLITS}")
            wf_ok = False
        for L, d in warmups.items():
            if not d["ok"]:
                blocked.append(f"feature warmup insufficient for L={L}")
    except Exception as exc:  # noqa: BLE001
        wf_detail = {"ok": False, "error": str(exc)}
        blocked.append(f"wf/warmup check error: {exc}")
        wf_ok = False
    checks["walk_forward"] = wf_detail

    ready = bool(flags_ok and prov_ok and sym_ok and frames_ok and wf_ok and not blocked)
    result = {
        "ready": ready,
        "real_data_only": True,
        "fabricated_data": False,
        "campaign": 292,
        "part": "preflight",
        "checks": checks,
        "blocked_reasons": blocked,
    }
    print(json.dumps(result, indent=2, default=str))
    return 0 if ready else 2


if __name__ == "__main__":
    raise SystemExit(main())
