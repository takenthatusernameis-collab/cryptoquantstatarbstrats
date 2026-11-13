#!/usr/bin/env python3
"""C291 preflight: fail-closed verification of the real USDT-M perp 5m klines +
funding cache before the derivatives funding-carry / basis cross-sectional campaign.

C291 is a NEW economic dimension (USDT-M perpetual futures with real funding
cashflows and spot/perp basis), absent from the C281B..C286/C288/C289/C290 record.
This preflight verifies:

- SHA256-from-bytes of the ingested perp pickle matches the meta-recorded sha;
- meta flags (real/fabricated), interval, rows, n_symbols, source host;
- every perp frame (open/high/low/close/volume) is exactly (26208 x 24) over
  2026-08-01T00:00Z -> 2026-10-30T23:55Z, zero NaNs, strictly positive, exact 5m
  spacing, duplicate-free index, columns == symbols;
- funding frame is (26208 x 24) with >= 90 finite funding rows per asset, every
  funding value sitting on a native Binance funding boundary (minute 0, hour a
  multiple of the symbol's real interval), and no funding gap > 24h + 1 bar
  (fail-closed staleness);
- the spot leg reference (verified C290 5m cache) exists, its SHA matches, and it
  contains every perp symbol so the basis feature is computable;
- walk-forward split math: train=720, test=168, step=168 -> 151 OOS splits, and the
  last OOS test window fits inside the cache;
- feature warmup: rolling features with min_periods=max(20, L//3) are warm before
  the first OOS test bar for every lookback L in {288, 1008, 2016}.

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

PERP = CACHE / "campaign291_perp_5m.pkl"
PERP_META = CACHE / "campaign291_perp_5m.meta.json"
PERP_PROV = CACHE / "campaign291_perp_5m.provenance.json"
SPOT = CACHE / "campaign290_ohlcv.pkl"
SPOT_META = CACHE / "campaign290_ohlcv.meta.json"

EXPECTED_ROWS = 26208
EXPECTED_SYMBOLS = 24
EXPECTED_START = "2026-08-01 00:00:00+00:00"
EXPECTED_END = "2026-10-30 23:55:00+00:00"
EXPECTED_INTERVAL = "5m"
REQUIRED_FRAMES = ("opens", "highs", "lows", "closes", "volumes")
FUNDING_FRAME = "funding_rates"
VALID_FUNDING_INTERVALS = {1, 2, 4, 8}
MIN_FUNDING_ROWS = 90
STALE_BARS = int(24 * 60 / 5) + 1  # 24h + 1 bar of 5m bars

LOOKBACKS_5M = (288, 1008, 2016)
WF_TRAIN = 720
WF_TEST = 168
WF_STEP = 168
EXPECTED_WF_SPLITS = 151


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

    if not PERP.exists():
        print(json.dumps({"ready": False, "blocked_reasons": ["perp pickle missing"]}, indent=2))
        return 1
    pkl_sha = sha256_file(PERP)

    try:
        meta = json.loads(PERP_META.read_text())
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"ready": False, "blocked_reasons": [f"meta unreadable: {exc}"]}, indent=2))
        return 1

    flags_ok = (
        meta.get("interval") == EXPECTED_INTERVAL
        and meta.get("rows") == EXPECTED_ROWS
        and meta.get("n_symbols") == EXPECTED_SYMBOLS
        and meta.get("real_data_only") is True
        and meta.get("fabricated_data") is False
        and meta.get("fetch_real_data_only") is True
        and meta.get("fetch_fabricated_data") is False
        and meta.get("source_host") == "https://data.binance.vision"
        and pkl_sha == meta.get("sha256_from_bytes")
    )
    checks["meta"] = {
        "interval": meta.get("interval"),
        "rows": meta.get("rows"),
        "n_symbols": meta.get("n_symbols"),
        "real_data_only": meta.get("real_data_only"),
        "fabricated_data": meta.get("fabricated_data"),
        "source_host": meta.get("source_host"),
        "sha256_from_bytes": meta.get("sha256_from_bytes"),
        "actual_sha256": pkl_sha,
        "ok": bool(flags_ok),
    }
    if not flags_ok:
        blocked.append("meta flags/interval/rows/symbols/host/sha mismatch")

    try:
        with open(PERP, "rb") as fh:
            payload = pickle.load(fh)
        symbols = list(payload.get("symbols") or meta.get("symbols") or [])
        sym_ok = len(symbols) == EXPECTED_SYMBOLS
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
                shape == (EXPECTED_ROWS, EXPECTED_SYMBOLS)
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
                "expected_shape": [EXPECTED_ROWS, EXPECTED_SYMBOLS],
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
        checks["frames"] = {
            "n_symbols": len(symbols),
            "symbols": symbols,
            "symbols_ok": bool(sym_ok),
            "detail": frame_detail,
            "ok": bool(frame_ok and sym_ok),
        }
        if not frame_ok:
            blocked.append("one or more perp OHLCV frames failed shape/window/nan/positive/spacing check")
        if not sym_ok:
            blocked.append("perp universe size mismatch")
    except Exception as exc:  # noqa: BLE001
        checks["frames"] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        blocked.append("perp frames could not be loaded")

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
            for s in symbols:
                col = fr[s]
                mask = col.notna()
                rows = int(mask.sum())
                total_rows += rows
                vals = col[mask]
                finite = bool(np.isfinite(vals.to_numpy(dtype=float)).all())
                # boundary alignment: minute 0 and hour % interval == 0
                ts = idx[mask.values]
                iv = int(meta.get("funding_intervals_by_symbol", {}).get(s, [8])[0]) if isinstance(
                    meta.get("funding_intervals_by_symbol", {}).get(s), list
                ) else 8
                iv_ok = iv in VALID_FUNDING_INTERVALS
                minute_ok = bool((ts.minute == 0).all()) if len(ts) else False
                hour_ok = bool((ts.hour % iv == 0).all()) if len(ts) else False
                # staleness: max gap between consecutive funding boundaries
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

    # ---- spot leg reference (verified C290 cache) ----
    try:
        spot_ok = SPOT.exists() and SPOT_META.exists()
        spot_detail = {"path": str(SPOT.relative_to(ROOT)), "exists": bool(SPOT.exists())}
        if spot_ok:
            spot_sha = sha256_file(SPOT)
            smeta = json.loads(SPOT_META.read_text())
            spot_sha_ok = spot_sha == smeta.get("sha256_from_bytes")
            with open(SPOT, "rb") as fh:
                spayload = pickle.load(fh)
            spot_cols = set(str(c) for c in spayload["closes"].columns)
            covers = set(symbols).issubset(spot_cols)
            spot_detail.update({
                "sha256": spot_sha,
                "sha_matches_meta": bool(spot_sha_ok),
                "n_spot_columns": len(spot_cols),
                "covers_all_perp_symbols": bool(covers),
                "ok": bool(spot_sha_ok and covers),
            })
            spot_ok = bool(spot_sha_ok and covers)
        else:
            spot_detail["ok"] = False
        checks["spot_leg"] = spot_detail
        if not spot_ok:
            blocked.append("spot leg (C290 cache) missing/sha mismatch/does not cover perp symbols")
    except Exception as exc:  # noqa: BLE001
        checks["spot_leg"] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        blocked.append("spot leg reference could not be verified")

    # ---- walk-forward + feature warmup (on perp closes) ----
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

    checks["provenance"] = {
        "path": str(PERP_PROV.relative_to(ROOT)) if PERP_PROV.exists() else str(PERP_PROV),
        "exists": PERP_PROV.exists(),
        "ok": bool(PERP_PROV.exists()),
    }
    if not PERP_PROV.exists():
        blocked.append("provenance json missing")

    ready = not blocked
    result = {
        "ready": ready,
        "real_data_only": True,
        "fabricated_data": False,
        "campaign": 291,
        "part": "preflight",
        "checks": checks,
        "blocked_reasons": blocked,
    }
    print(json.dumps(result, indent=2, default=str))
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())