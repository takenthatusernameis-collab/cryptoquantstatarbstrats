#!/usr/bin/env python3
"""C301 preflight: fail-closed verification of the real 2023-01 .. 2023-02
USDT-M perp aggTrades-derived 5m OFI feature cache before the C301 order-flow
imbalance / trade-sign autocorrelation per-asset time-series campaign runs.

Verifies:

- SHA256-from-bytes of the ingested pickle matches the meta-recorded sha;
- meta flags (real/fabricated), interval 5m, source interval aggTrades_ms,
  n_symbols, window (2023-01-01 .. 2023-02-28 23:55), source host, C300 reuse
  cache sha, cache format = plain numpy ndarrays, cache < 100 MB push limit;
- for every selected asset: perp_close exactly (n_bars x 1) over the contiguous
  window, zero NaN, strictly positive; funding_rates present only on native 8h
  boundaries (>= 90 finite rows, stale gap <= 24h + 1 bar on the 5m grid); the
  OFI legs (buy_volume, sell_volume, signed_volume, trade_count, trade_sign_sum,
  vwap) carry the same 5m index, present values finite, signed_volume ==
  buy_volume - sell_volume, trade_count > 0 on trade bars, vwap > 0 on trade
  bars; gap bars (no trades) are NaN on the OFI legs and never imputed;
- walk-forward split math: train=2880/test=1152/step=1152 in 5m bars fits each
  asset's window (>= 1 OOS split, 12 splits expected over 16992 bars);
- feature warmup: rolling features with min_periods=max(20, L//3) warm before
  the first OOS test bar for every lookback L in {288, 1008, 2016};
- provenance json exists and carries real_data_only/fabricated_data/executed_fills.

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

PXL = CACHE / "campaign301_aggtrades_ofi.pkl"
PXL_META = CACHE / "campaign301_aggtrades_ofi.meta.json"
PXL_PROV = CACHE / "campaign301_aggtrades_ofi.provenance.json"
C300_CACHE = CACHE / "campaign300_multianual_perp_funding_basis_ts_5m.pkl"

EXPECTED_INTERVAL = "5m"
EXPECTED_SOURCE_INTERVAL = "aggTrades_ms"
WINDOW_START = "2023-01-01T00:00:00Z"
WINDOW_END = "2023-02-28T23:55:00Z"
OFI_LEGS = ("buy_volume", "sell_volume", "signed_volume", "trade_count", "trade_sign_sum", "vwap")
VALID_FUNDING_INTERVALS = {1, 2, 4, 8}
MIN_FUNDING_ROWS = 90
STALE_BARS = 24 * 12 + 1  # 24h + 1 bar on the 5m grid
MIN_BARS = 2880 + 1152  # train + one test
PUSH_LIMIT_BYTES = 100_000_000

LOOKBACKS_5M = (288, 1008, 2016)
WF_TRAIN = 2880
WF_TEST = 1152
WF_STEP = 1152


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
        print(json.dumps({"ready": False, "blocked_reasons": ["C301 OFI pickle missing"]}, indent=2))
        return 1
    pkl_sha = sha256_file(PXL)
    pkl_bytes = PXL.stat().st_size

    try:
        meta = json.loads(PXL_META.read_text())
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"ready": False, "blocked_reasons": [f"meta unreadable: {exc}"]}, indent=2))
        return 1

    # C300 reuse cache must exist and match recorded sha.
    c300_sha = sha256_file(C300_CACHE) if C300_CACHE.exists() else None

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
        and meta.get("c300_cache_sha256") == c300_sha
    )
    checks["meta"] = {
        "interval": meta.get("interval"),
        "source_interval": meta.get("source_interval"),
        "n_symbols": meta.get("n_symbols"),
        "total_bars": meta.get("total_bars"),
        "total_trade_bars": meta.get("total_trade_bars"),
        "total_gap_bars": meta.get("total_gap_bars"),
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
        "c300_cache_sha256": meta.get("c300_cache_sha256"),
        "c300_cache_actual_sha256": c300_sha,
        "sha256_from_bytes": meta.get("sha256_from_bytes"),
        "actual_sha256": pkl_sha,
        "ok": bool(flags_ok),
    }
    if not flags_ok:
        blocked.append("meta flags/interval/source/window/host/format/size/sha/C300-reuse mismatch")

    try:
        with open(PXL, "rb") as fh:
            payload = pickle.load(fh)
        symbols = list(payload.get("symbols") or [])
        sym_ok = len(symbols) >= 1 and len(symbols) == int(meta.get("n_symbols") or 0)
        per_asset = payload.get("per_asset") or {}
        exp_idx = pd.DatetimeIndex(pd.date_range(start=pd.Timestamp(WINDOW_START), end=pd.Timestamp(WINDOW_END), freq="5min", tz="UTC"))
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
            d = {"symbol": s, "n_bars": n_bars, "expected_bars": int(len(exp_idx)), "fields": {}}
            all_field_ok = True
            # perp close: exact index, zero NaN, positive, finite
            close = _as_series(pa, "perp_close", index).reindex(exp_idx)
            c_arr = close.to_numpy(dtype=float)
            c_nan = int(np.isnan(c_arr).sum())
            c_pos = bool((close.dropna().to_numpy(dtype=float) > 0).all()) if len(close.dropna()) else True
            c_fin = bool(np.isfinite(close.dropna().to_numpy(dtype=float)).all()) if len(close.dropna()) else True
            c_dup = int(close.index.duplicated().sum())
            c_exact = bool(close.index.equals(exp_idx))
            c_ok = c_nan == 0 and c_pos and c_fin and c_dup == 0 and c_exact and int(len(close)) == n_bars
            d["fields"]["perp_close"] = {"nan_count": c_nan, "all_positive": c_pos, "all_finite": c_fin, "duplicate": c_dup, "exact_index": c_exact, "ok": bool(c_ok)}
            all_field_ok &= c_ok

            # OFI legs: same index, present finite, signed == buy - sell, count > 0, vwap > 0 on trade bars
            trade_count = _as_series(pa, "trade_count", index).reindex(exp_idx)
            buy = _as_series(pa, "buy_volume", index).reindex(exp_idx)
            sell = _as_series(pa, "sell_volume", index).reindex(exp_idx)
            signed = _as_series(pa, "signed_volume", index).reindex(exp_idx)
            tss = _as_series(pa, "trade_sign_sum", index).reindex(exp_idx)
            vwap = _as_series(pa, "vwap", index).reindex(exp_idx)
            present = trade_count.notna().values
            gap = ~present
            n_gap = int(gap.sum())
            n_trade = int(present.sum())
            signed_ok = bool(np.allclose(signed.to_numpy(dtype=float)[present], (buy.to_numpy(dtype=float) - sell.to_numpy(dtype=float))[present], equal_nan=False))
            count_ok = bool((trade_count.to_numpy(dtype=float)[present] > 0).all())
            vwap_ok = bool(np.isfinite(vwap.to_numpy(dtype=float)[present]).all() and (vwap.to_numpy(dtype=float)[present] > 0).all())
            # gap bars must be NaN on all OFI legs (never imputed)
            gap_nan_ok = bool(
                np.isnan(trade_count.to_numpy(dtype=float)[gap]).all()
                and np.isnan(signed.to_numpy(dtype=float)[gap]).all()
                and np.isnan(buy.to_numpy(dtype=float)[gap]).all()
                and np.isnan(sell.to_numpy(dtype=float)[gap]).all()
                and np.isnan(tss.to_numpy(dtype=float)[gap]).all()
                and np.isnan(vwap.to_numpy(dtype=float)[gap]).all()
            )
            # trade-sign consistency: |trade_sign_sum| <= trade_count and same sign as signed_volume
            sign_le = bool((np.abs(tss.to_numpy(dtype=float)[present]) <= trade_count.to_numpy(dtype=float)[present] + 1e-9).all())
            ofi_ok = signed_ok and count_ok and vwap_ok and gap_nan_ok and sign_le
            d["fields"]["ofi"] = {
                "n_trade_bars": n_trade,
                "n_gap_bars": n_gap,
                "signed_equals_buy_minus_sell": signed_ok,
                "trade_count_positive_on_trade_bars": count_ok,
                "vwap_finite_positive_on_trade_bars": vwap_ok,
                "gap_bars_nan_all_legs": gap_nan_ok,
                "abs_trade_sign_sum_le_trade_count": sign_le,
                "ok": bool(ofi_ok),
            }
            all_field_ok &= ofi_ok

            # funding boundary/staleness
            fcol = _as_series(pa, "funding_rates", index).reindex(exp_idx)
            fmask = fcol.notna()
            rows = int(fmask.sum())
            vals = fcol[fmask]
            finite = bool(np.isfinite(vals.to_numpy(dtype=float)).all()) if len(vals) else False
            ts_b = fcol.index[fmask.values]
            minute_ok = bool((ts_b.minute == 0).all()) if len(ts_b) else False
            hour_ok = bool((ts_b.hour % 8 == 0).all()) if len(ts_b) else False
            pos = np.where(fmask.values)[0]
            gap_f = int(np.diff(pos).max()) if len(pos) > 1 else 0
            tail_gap = int(len(exp_idx) - 1 - pos[-1]) if len(pos) else int(len(exp_idx))
            stale_ok = gap_f <= STALE_BARS and tail_gap <= STALE_BARS
            fund_ok = rows >= MIN_FUNDING_ROWS and finite and minute_ok and hour_ok and stale_ok
            d["funding"] = {
                "funding_rows": rows,
                "min_rows": MIN_FUNDING_ROWS,
                "all_finite": finite,
                "minute_zero": minute_ok,
                "hour_multiple_of_8": hour_ok,
                "max_boundary_gap_bars": gap_f,
                "tail_gap_bars": tail_gap,
                "stale_limit_bars": STALE_BARS,
                "stale_ok": stale_ok,
                "ok": bool(fund_ok),
            }
            all_field_ok &= fund_ok

            # walk-forward fit
            n_splits = len(wf_splits(n_bars, WF_TRAIN, WF_TEST, WF_STEP))
            wf_ok = n_bars >= MIN_BARS and n_splits > 0
            d["walk_forward"] = {"bars": n_bars, "train": WF_TRAIN, "test": WF_TEST, "step": WF_STEP, "min_bars": MIN_BARS, "n_splits": int(n_splits), "ok": bool(wf_ok)}
            all_field_ok &= wf_ok

            # feature warmup
            warm = {f"L={L}": {"min_periods": int(min_periods_for(L)), "warm_before_first_test_bar": bool(min_periods_for(L) <= WF_TRAIN), "ok": bool(min_periods_for(L) <= WF_TRAIN)} for L in LOOKBACKS_5M}
            warm_ok = all(v["ok"] for v in warm.values())
            d["feature_warmup"] = {"rule": "min_periods = max(20, L // 3) on native-5m per-asset features", "lookbacks_5m": list(LOOKBACKS_5M), "warmup": warm, "ok": bool(warm_ok)}
            all_field_ok &= warm_ok

            d["ok"] = bool(all_field_ok)
            asset_detail[s] = d
            asset_ok &= all_field_ok
        checks["assets"] = {"n_symbols": len(symbols), "symbols": symbols, "symbols_ok": bool(sym_ok), "detail": asset_detail, "ok": bool(asset_ok and sym_ok)}
        if not asset_ok:
            blocked.append("one or more assets failed per-asset perp/ofi/funding/WF/warmup checks")
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
        "campaign": 301,
        "part": "preflight",
        "checks": checks,
        "blocked_reasons": blocked,
    }
    print(json.dumps(result, indent=2, default=str))
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())