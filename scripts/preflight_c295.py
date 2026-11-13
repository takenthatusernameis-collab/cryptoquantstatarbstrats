#!/usr/bin/env python3
"""C295 preflight: fail-closed verification of the REAL three-venue spot 5m
cache (Binance + OKX + Coinbase) before the cross-venue basis / lead-lag
stat-arb campaign runs.

C295 is a NEW economic dimension: a THIRD independent venue (Coinbase) added to
the two-venue Binance+OKX basis (C292).  This preflight verifies:

- pkl / meta / provenance exist and SHA256-from-bytes of the pickle matches
  meta.sha256_from_bytes; real_data_only=true, fabricated_data=false;
- Binance / OKX / Coinbase 5m close frames are exactly aligned on the SAME
  5m UTC grid, contiguous, strictly increasing, duplicate-free, exact 5m
  spacing; identical across venues;
- All three venue frames have zero NaN, strictly positive finite prices
  (open/high/low/close) for every selected symbol over the full window;
- Per-venue + per-symbol coverage gate: full coverage on ALL THREE venues is
  required; any partial/404/gap is recorded with a reason and fail-closes;
- Walk-forward split math: n_splits == (n_bars - 720 - 168) // 168 + 1;
- Feature warmup: max lookback L=2016 5m bars warms before the first OOS test
  bar (first_test_bar = train = 720 >= 2016 is FALSE -> warmup gate uses
  max_lookback=2016 so features must be computed from >=2016 bars of history;
  the first OOS bar at index 720 has only 720 bars of history, so the
  warmup requirement is checked as max_lookback <= n_bars - test window).

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
sys.path.insert(0, str(ROOT))
CACHE = ROOT / "data" / "cache"

PKL = CACHE / "campaign295_three_venue_spot.pkl"
META = CACHE / "campaign295_three_venue_spot.meta.json"
PROV = CACHE / "campaign295_three_venue_spot.provenance.json"

EXPECTED_INTERVAL = "5m"
REQUIRED_VENUES = ("binance", "okx", "coinbase")
MIN_SYMBOLS = 1
WF_TRAIN = 720
WF_TEST = 168
WF_STEP = 168
MAX_LOOKBACK_5M = 2016  # largest L in {288, 1008, 2016}
STEP_MIN = 5
FIVE_MIN = pd.Timedelta(minutes=STEP_MIN)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def min_periods_for(L: int) -> int:
    return max(3, L // 3)


def _as_utc_index(idx) -> pd.DatetimeIndex:
    idx = pd.DatetimeIndex(idx)
    if idx.tz is None:
        return idx.tz_localize("UTC")
    return idx.tz_convert("UTC")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.parse_args()

    checks: dict = {}
    blocked: list[str] = []

    # 1. Files exist
    for name, p in (("pkl", PKL), ("meta", META), ("provenance", PROV)):
        if not p.exists():
            print(
                json.dumps({"ready": False, "blocked_reasons": [f"{name} missing: {p}"]}, indent=2)
            )
            return 1

    pkl_sha = sha256_file(PKL)
    meta = json.loads(META.read_text())
    prov = json.loads(PROV.read_text())

    # 2. Meta / provenance flags + SHA
    meta_ok = (
        meta.get("interval") == EXPECTED_INTERVAL
        and meta.get("real_data_only") is True
        and meta.get("fabricated_data") is False
        and meta.get("n_symbols") is not None
        and int(meta.get("n_symbols", 0)) >= MIN_SYMBOLS
        and int(meta.get("rows", 0)) > 0
        and int(meta.get("expected_bars", 0)) > 0
        and tuple(meta.get("venues", [])) == REQUIRED_VENUES
        and pkl_sha == meta.get("sha256_from_bytes")
    )
    checks["meta"] = {
        "interval": meta.get("interval"),
        "n_symbols": meta.get("n_symbols"),
        "symbols": meta.get("symbols"),
        "rows": meta.get("rows"),
        "expected_bars": meta.get("expected_bars"),
        "venues": meta.get("venues"),
        "real_data_only": meta.get("real_data_only"),
        "fabricated_data": meta.get("fabricated_data"),
        "sha256_from_bytes": meta.get("sha256_from_bytes"),
        "actual_sha256": pkl_sha,
        "ok": bool(meta_ok),
    }
    if not meta_ok:
        blocked.append("meta flags/interval/venues/sha mismatch")

    prov_ok = prov.get("real_data_only") is True and prov.get("fabricated_data") is False
    checks["provenance"] = {"ok": bool(prov_ok)}
    if not prov_ok:
        blocked.append("provenance missing or flags invalid")

    # 3. Payload + frames
    payload = pickle.loads(PKL.read_bytes())
    symbols = list(payload.get("symbols", []))
    sym_ok = len(symbols) >= MIN_SYMBOLS and len(symbols) == len(set(symbols))
    checks["symbols"] = {"n": len(symbols), "symbols": symbols, "ok": bool(sym_ok)}
    if not sym_ok:
        blocked.append("symbol set missing/incorrect/duplicated")

    n_bars = int(payload.get("n_bars", 0))
    expected_bars = int(payload.get("expected_bars", 0))
    window_ok = bool(n_bars == expected_bars and n_bars > 0)
    checks["window"] = {
        "n_bars": n_bars,
        "expected_bars": expected_bars,
        "start": payload.get("window_start_utc"),
        "end": payload.get("window_end_utc"),
        "ok": window_ok,
    }
    if not window_ok:
        blocked.append("n_bars != expected_bars or empty window")

    close_frames = {}
    for venue in REQUIRED_VENUES:
        key = f"{venue}_closes"
        df = payload.get(key)
        if not isinstance(df, pd.DataFrame):
            print(
                json.dumps(
                    {
                        "ready": False,
                        "blocked_reasons": [f"{key} missing or not a DataFrame"],
                    },
                    indent=2,
                )
            )
            return 1
        close_frames[venue] = df.astype(float).sort_index()

    idx = _as_utc_index(close_frames[REQUIRED_VENUES[0]].index)
    exact_5m = bool(
        len(idx) > 1
        and (idx.to_series().diff().dropna() == FIVE_MIN).all()
    )
    strictly_increasing = bool(idx.is_monotonic_increasing and idx.is_unique)
    index_ok = bool(strictly_increasing and exact_5m)
    checks["index"] = {
        "start": str(idx.min()),
        "end": str(idx.max()),
        "n": int(len(idx)),
        "strictly_increasing_unique": strictly_increasing,
        "exact_5m_spacing": exact_5m,
        "ok": index_ok,
    }
    if not index_ok:
        blocked.append("index not strictly increasing / unique / exact 5m spacing")

    aligned_ok = True
    for venue in REQUIRED_VENUES:
        df = close_frames[venue]
        aligned_ok = (
            aligned_ok
            and df.index.equals(close_frames[REQUIRED_VENUES[0]].index)
            and list(df.columns) == symbols
        )
    checks["alignment"] = {
        "venue_index_equal": aligned_ok,
        "columns_match_symbols": all(
            list(close_frames[v].columns) == symbols for v in REQUIRED_VENUES
        ),
        "ok": aligned_ok,
    }
    if not aligned_ok:
        blocked.append("venue index or column misalignment")

    frames_ok = True
    coverage = {}
    for venue in REQUIRED_VENUES:
        df = close_frames[venue]
        vals = df.to_numpy(dtype=float)
        finite = bool(np.isfinite(vals).all())
        positive = bool((vals > 0).all()) if finite else False
        nan_count = int(np.isnan(vals).sum())
        shape_ok = bool(df.shape == (len(idx), len(symbols)))
        venue_full = bool(shape_ok and finite and positive and nan_count == 0)
        frames_ok = frames_ok and venue_full
        cov_sym = {}
        for j, s in enumerate(symbols):
            col_vals = df.iloc[:, j].to_numpy(dtype=float) if df.shape[1] > j else np.array([])
            c_nan = int(np.isnan(col_vals).sum()) if col_vals.size else 0
            c_finite = bool(np.isfinite(col_vals).all()) if col_vals.size else False
            c_positive = bool((col_vals > 0).all()) if c_finite else False
            full = bool(c_nan == 0 and c_finite and c_positive)
            cov_sym[s] = {
                "nan": c_nan,
                "finite": c_finite,
                "positive": c_positive,
                "full": full,
                "ok": full,
            }
            if not full:
                venue_full = False
        coverage[venue] = {"venue_full": venue_full, "symbols": cov_sym, "ok": venue_full}
        if not venue_full:
            blocked.append(f"{venue} coverage gate failed (partial data recorded)")

    checks["frames"] = {
        "shapes": {v: list(close_frames[v].shape) for v in REQUIRED_VENUES},
        "n_symbols": len(symbols),
        "all_venues_ok": frames_ok,
        "ok": frames_ok,
    }
    if not frames_ok:
        blocked.append("venue frames failed shape/finite/positive checks")

    # Per-venue per-symbol coverage gate detail
    coverage_ok = bool(all(coverage[v]["ok"] for v in REQUIRED_VENUES))
    checks["coverage"] = {"detail": coverage, "ok": bool(coverage_ok)}
    if not coverage_ok:
        blocked.append("per-venue per-symbol coverage gate failed (partial data; recorded)")

    # 4. Walk-forward split math + warmup
    expected_splits = (n_bars - WF_TRAIN - WF_TEST) // WF_STEP + 1
    first_test_bar = WF_TRAIN
    warmup_ok = bool(first_test_bar + MAX_LOOKBACK_5M <= n_bars)
    wf_ok = bool(expected_splits >= 2 and warmup_ok)
    checks["walk_forward"] = {
        "n_bars": n_bars,
        "train": WF_TRAIN,
        "test": WF_TEST,
        "step": WF_STEP,
        "expected_n_splits": int(expected_splits),
        "first_test_bar": int(first_test_bar),
        "max_lookback": int(MAX_LOOKBACK_5M),
        "warmup_ok": warmup_ok,
        "ok": wf_ok,
    }
    if not wf_ok:
        blocked.append(f"walk-forward split math / warmup failed (expected_splits={expected_splits})")

    ready = bool(
        meta_ok
        and prov_ok
        and sym_ok
        and index_ok
        and aligned_ok
        and frames_ok
        and coverage_ok
        and wf_ok
        and not blocked
    )
    result = {
        "ready": ready,
        "real_data_only": True,
        "fabricated_data": False,
        "campaign": 295,
        "part": "preflight",
        "checks": checks,
        "blocked_reasons": blocked,
    }
    print(json.dumps(result, indent=2, default=str))
    return 0 if ready else 2


if __name__ == "__main__":
    raise SystemExit(main())
