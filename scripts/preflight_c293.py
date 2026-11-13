#!/usr/bin/env python3
"""C293 preflight: fail-closed verification of the cross-venue perp funding
cache (Binance USDT-M + OKX USDT-M) before the funding-carry campaign runs.

C293 is a NEW economic dimension (cross-venue perpetual futures funding carry):
cross-venue funding rate carry statistical arbitrage on the SAME asset trading
as USDT-M perp on Binance and OKX. This preflight verifies:

- SHA256-from-bytes of the ingested pickle matches meta;
- meta/provenance real/fabricated flags and shape/window;
- every frame (binance/okx closes, binance/okx funding rates) is exactly
  (23424 x 24) over 2026-08-10T16:00Z -> 2026-10-30T23:55Z, zero NaNs in closes,
  strictly positive, finite, duplicate-free index, exact 5m spacing;
- identical symbol columns and index across all frames;
- funding boundary alignment: OKX 8h native; Binance 8h/4h per symbol from
  binance_funding_intervals_by_symbol;
- per-venue coverage gate: per-symbol native funding coverage measured at
  ingest (8h symbols = 244 native points; 4h symbols = 488). BNB (Binance 129),
  TAO (OKX 244), ONDO (OKX 423), PUMP (OKX 451) are PARTIAL on one venue and
  must be excluded/flagged with recorded reasons before any PnL.
- walk-forward split math: train=720, test=168, step=168 -> 135 OOS splits;
- feature warmup: L in {8, 24, 60} 5m bars (rolling on ffilled funding spread),
  min_periods=max(3, L//3), warm before first OOS test bar.

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

PKL = CACHE / "campaign293_crossvenue_funding.pkl"
META = CACHE / "campaign293_crossvenue_funding.meta.json"
PROV = CACHE / "campaign293_crossvenue_funding.provenance.json"

EXPECTED_ROWS = 23424
EXPECTED_SYMBOLS = 24
EXPECTED_START = "2026-08-10 16:00:00+00:00"
EXPECTED_END = "2026-10-30 23:55:00+00:00"
EXPECTED_INTERVAL = "5m"
CLOSE_FRAMES = ("binance_closes", "okx_closes")
FUNDING_FRAMES = ("binance_funding_rates", "okx_funding_rates")
REQUIRED_FRAMES = CLOSE_FRAMES + FUNDING_FRAMES

# Feature lookbacks in 5m bars (rolling on ffilled funding spread)
LOOKBACKS_5M = (8, 24, 60)
WF_TRAIN = 720
WF_TEST = 168
WF_STEP = 168
EXPECTED_WF_SPLITS = 135  # (23424 - 720 - 168) // 168 + 1 = 135
MIN_SYMBOLS = 2

# Expected native funding points: 8h = 3 per day, ~81 days = 243; 4h = 6 per day = 486
OKX_8H_EXPECTED = 244
BINANCE_8H_EXPECTED = 244
BINANCE_4H_EXPECTED = 488

# Partial coverage symbols from ingest (must be excluded before PnL)
PARTIAL_SYMBOLS = {
    "BNBUSDT": {"binance_native": 129, "expected": BINANCE_8H_EXPECTED, "venue": "binance", "interval_h": 8},
    "TAOUSDT": {"okx_native": 244, "expected": OKX_8H_EXPECTED, "venue": "okx", "interval_h": 8},
    "ONDOUSDT": {"okx_native": 423, "expected": BINANCE_4H_EXPECTED, "venue": "okx", "interval_h": 4},
    "PUMPUSDT": {"okx_native": 451, "expected": BINANCE_4H_EXPECTED, "venue": "okx", "interval_h": 4},
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def min_periods_for(L: int) -> int:
    return max(3, L // 3)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.parse_args()

    checks: dict = {}
    blocked: list[str] = []
    excluded_symbols: list[str] = []

    if not PKL.exists():
        print(json.dumps({"ready": False, "blocked_reasons": ["crossvenue funding pickle missing"]}, indent=2))
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
        and meta.get("n_symbols") == EXPECTED_SYMBOLS
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
        blocked.append("meta flags/interval/rows/symbols/sha mismatch")

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

    # Verify okx_instids mapping
    okx_instids = payload.get("okx_instids", {})
    instids_ok = all(s in okx_instids for s in symbols)
    checks["okx_instids"] = {"ok": bool(instids_ok)}
    if not instids_ok:
        blocked.append("okx_instids missing for some symbols")

    # Verify binance_funding_intervals_by_symbol
    bfi = payload.get("binance_funding_intervals_by_symbol", {})
    bfi_ok = all(s in bfi for s in symbols)
    checks["binance_funding_intervals_by_symbol"] = {"ok": bool(bfi_ok)}
    if not bfi_ok:
        blocked.append("binance_funding_intervals_by_symbol missing for some symbols")

    # Check close frames (strict: zero NaN, positive, finite)
    frame_details = {}
    frames_ok = True
    ref_idx = None
    ref_cols = None
    for name in CLOSE_FRAMES:
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
            "is_funding": False,
            "duplicate_index": not no_dupes,
            "exact_5m_spacing": spacing_ok,
            "columns_match_symbols": cols_ok,
            "aligned_to_reference": aligned_ok,
            "ok": ok,
        }
        frames_ok = frames_ok and ok

    # Check funding frames (sparse by design: only native boundaries have values)
    for name in FUNDING_FRAMES:
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
        finite_ok = bool(np.isfinite(vals[~np.isnan(vals)]).all())  # only check non-NaN
        # Funding can be any finite value (positive, negative, zero)
        if ref_idx is None:
            ref_idx = idx_utc
        if ref_cols is None:
            ref_cols = list(df.columns)
        aligned_ok = idx_utc.equals(ref_idx) and list(df.columns) == ref_cols
        # For funding frames: shape, window, spacing, alignment must match; NaN expected
        ok = bool(shape_ok and start_ok and end_ok and no_dupes and spacing_ok and cols_ok and finite_ok and aligned_ok)
        frame_details[name] = {
            "shape": list(df.shape),
            "start": str(idx_utc.min()),
            "end": str(idx_utc.max()),
            "nan_count": nan_count,
            "all_finite_non_nan": finite_ok,
            "is_funding": True,
            "duplicate_index": not no_dupes,
            "exact_5m_spacing": spacing_ok,
            "columns_match_symbols": cols_ok,
            "aligned_to_reference": aligned_ok,
            "ok": ok,
        }
        frames_ok = frames_ok and ok

    checks["frames"] = {"detail": frame_details, "ok": bool(frames_ok)}
    if not frames_ok:
        blocked.append("one or more venue frames failed shape/window/finite/alignment checks")

    # Funding boundary alignment: all non-NaN funding timestamps must be minute=0
    funding_boundary_ok = True
    for name in FUNDING_FRAMES:
        df = payload[name]
        for s in symbols:
            col = df[s]
            mask = col.notna()
            if not mask.any():
                continue
            ts = pd.DatetimeIndex(df.index[mask.values])
            minute_ok = bool((ts.minute == 0).all())
            if not minute_ok:
                funding_boundary_ok = False
                blocked.append(f"{name}[{s}] funding timestamps not on minute=0 boundaries")
    checks["funding_boundary_minute_zero"] = {"ok": bool(funding_boundary_ok)}

    # Per-venue coverage check: flag partials, exclude them from trading universe
    coverage_ok = True
    coverage_detail = {}
    binance_fr = payload["binance_funding_rates"]
    okx_fr = payload["okx_funding_rates"]
    bfi = payload["binance_funding_intervals_by_symbol"]

    for s in symbols:
        s_ok = True
        s_detail = {}
        # Binance native funding count
        b_mask = binance_fr[s].notna()
        b_count = int(b_mask.sum())
        b_interval = int(bfi.get(s, 8))
        b_expected = BINANCE_8H_EXPECTED if b_interval == 8 else BINANCE_4H_EXPECTED
        b_ok = b_count >= b_expected
        if not b_ok:
            s_ok = False
        s_detail["binance"] = {
            "native_funding_points": b_count,
            "expected": b_expected,
            "interval_h": b_interval,
            "ok": bool(b_ok),
        }

        # OKX native funding count (all OKX are 8h)
        o_mask = okx_fr[s].notna()
        o_count = int(o_mask.sum())
        o_expected = OKX_8H_EXPECTED
        o_ok = o_count >= o_expected
        if not o_ok:
            s_ok = False
        s_detail["okx"] = {
            "native_funding_points": o_count,
            "expected": o_expected,
            "interval_h": 8,
            "ok": bool(o_ok),
        }

        coverage_detail[s] = s_detail

        # Flag partial coverage symbols for exclusion
        if s in PARTIAL_SYMBOLS:
            ps = PARTIAL_SYMBOLS[s]
            venue = ps['venue']
            native_key = f"{venue}_native"
            excluded_symbols.append(s)
            # Record exclusion reason in coverage detail, not as blocker
            s_detail["exclusion_reason"] = f"PARTIAL COVERAGE: {venue} native={ps[native_key]} expected={ps['expected']} interval={ps['interval_h']}h"
        elif not s_ok:
            coverage_ok = False
            blocked.append(f"COVERAGE FAIL: {s} binance_ok={b_ok} okx_ok={o_ok}")

    checks["funding_coverage"] = {"detail": coverage_detail, "excluded_symbols": excluded_symbols, "ok": bool(coverage_ok)}

    # Active symbols after exclusions
    active_symbols = [s for s in symbols if s not in excluded_symbols]
    checks["active_symbols"] = {"n": len(active_symbols), "symbols": active_symbols}
    if len(active_symbols) < MIN_SYMBOLS:
        blocked.append(f"too few active symbols after exclusions: {len(active_symbols)} < {MIN_SYMBOLS}")

    # Walk-forward + feature warmup
    try:
        n_bars = EXPECTED_ROWS
        splits = []
        i = 0
        while i + WF_TRAIN + WF_TEST <= n_bars:
            splits.append((i, i + WF_TRAIN, i + WF_TRAIN + WF_TEST))
            i += WF_STEP
        n_splits = len(splits)
        warmups = {}
        wf_ok = True
        for L in LOOKBACKS_5M:
            mp = min_periods_for(L)
            first_test = splits[0][1] if splits else 0
            # On ffilled 5m data, need mp 5m bars of history before first test bar
            warm_ok = mp <= first_test
            warmups[str(L)] = {"min_periods": mp, "first_test_bar": first_test, "ok": bool(warm_ok)}
            wf_ok = wf_ok and warm_ok
        wf_detail = {"n_splits": n_splits, "expected": EXPECTED_WF_SPLITS, "warmups": warmups, "ok": bool(wf_ok and n_splits == EXPECTED_WF_SPLITS)}
        if n_splits != EXPECTED_WF_SPLITS:
            blocked.append(f"wf split count {n_splits} != {EXPECTED_WF_SPLITS}")
            wf_ok = False
        for L, d in warmups.items():
            if not d["ok"]:
                blocked.append(f"feature warmup insufficient for L={L}")
        checks["walk_forward"] = wf_detail
    except Exception as exc:  # noqa: BLE001
        checks["walk_forward"] = {"ok": False, "error": str(exc)}
        blocked.append(f"wf/warmup check error: {exc}")
        wf_ok = False

    ready = bool(flags_ok and prov_ok and sym_ok and frames_ok and funding_boundary_ok and coverage_ok and wf_ok and len(active_symbols) >= MIN_SYMBOLS and not blocked)
    result = {
        "ready": ready,
        "real_data_only": True,
        "fabricated_data": False,
        "campaign": 293,
        "part": "preflight",
        "checks": checks,
        "blocked_reasons": blocked,
    }
    print(json.dumps(result, indent=2, default=str))
    return 0 if ready else 2


if __name__ == "__main__":
    raise SystemExit(main())