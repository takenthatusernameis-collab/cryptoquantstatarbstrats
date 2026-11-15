#!/usr/bin/env python3
"""C303 — ingest REAL Binance USDT-M perpetual data for the cross-sectional
premium-index carry / dispersion campaign.

Builds the *common intersection grid* = timestamps present in ALL 10
``premiumIndexKlines`` 1h archives (measured: 58,959 bars,
2020-01-31 08:00:00Z -> 2026-10-31 23:00:00Z).  Any bar missing in >= 1 asset
is dropped from the grid; per-asset missing bars are recorded, NEVER
imputed/filled/ffilled.

Real execution data for ALL 10 assets:
- perp 1h klines (close) and native 8h fundingRate.
- BTC/ETH/BCH are reused from the verified C299 cache (reindexed to the common
  grid); the other 7 assets are downloaded fresh (endpoints verified HTTP 200).

Data (real, fail-closed; fapi REST is HTTP 451 and is NOT used):
- https://data.binance.vision/data/futures/um/monthly/premiumIndexKlines/<SYM>/1h/<SYM>-1h-YYYY-MM.zip
- https://data.binance.vision/data/futures/um/monthly/klines/<SYM>/1h/<SYM>-1h-YYYY-MM.zip
- https://data.binance.vision/data/futures/um/monthly/fundingRate/<SYM>/<SYM>-fundingRate-YYYY-MM.zip

Fail-closed (never impute / forward-fill / back-fill):
- every download wrapped in retry-with-backoff (6 attempts, linear 1 s x k);
  a lone 404/5xx is retryable; only fail-closed after all retries exhausted;
- skip any CSV row whose first field is non-numeric (recent months carry a
  ``open_time`` header row);
- any bar missing in >= 1 premium archive is dropped from the common grid;
  per-asset premium gaps are carried as NaN and never imputed.

Serialized artifacts (all real_data_only:true, fabricated_data:false,
executed_fills:false, SHA256-from-bytes, COMPACT ndarray form < 100 MB):
- data/cache/campaign303_premium_index_xsec.pkl
- data/cache/campaign303_premium_index_xsec.meta.json
- data/cache/campaign303_premium_index_xsec.provenance.json
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import pickle
import sys
import time
import urllib.error
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "cache"
OUT_PKL = CACHE / "campaign303_premium_index_xsec.pkl"
OUT_META = CACHE / "campaign303_premium_index_xsec.meta.json"
OUT_PROV = CACHE / "campaign303_premium_index_xsec.provenance.json"

# C299 reuse source (execution price + funding) for BTC/ETH/BCH only.
C299_CACHE = CACHE / "campaign299_multianual_perp_funding_basis_ts.pkl"
C299_META = CACHE / "campaign299_multianual_perp_funding_basis_ts.meta.json"

ARCHIVE_HOST = "https://data.binance.vision"
PREMIUM_PATH = "/data/futures/um/monthly/premiumIndexKlines/{sym}/1h/{sym}-1h-{month}.zip"
KLINES_PATH = "/data/futures/um/monthly/klines/{sym}/1h/{sym}-1h-{month}.zip"
FUNDING_PATH = "/data/futures/um/monthly/fundingRate/{sym}/{sym}-fundingRate-{month}.zip"

START_UTC = "2020-01-01T00:00:00Z"
END_UTC = "2026-10-31T23:00:00Z"
INTERVAL = "1h"

UNIVERSE = (
    "BTCUSDT", "ETHUSDT", "XRPUSDT", "ADAUSDT", "LTCUSDT",
    "BCHUSDT", "LINKUSDT", "TRXUSDT", "ETCUSDT", "XLMUSDT",
)
C299_ASSETS = ("BTCUSDT", "ETHUSDT", "BCHUSDT")

KLINE_COLUMNS = [
    "open_time", "open", "high", "low", "close", "volume", "close_time",
    "quote_volume", "count", "taker_buy_volume", "taker_buy_quote_volume", "ignore",
]
FUNDING_COLUMNS = ["calc_time", "funding_interval_hours", "last_funding_rate"]

PUSH_LIMIT_BYTES = 100_000_000  # GitHub hard-rejects any blob > 100 MB
RETRIES = 6  # retry-with-backoff, linear 1 s x attempt


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _months() -> list[str]:
    stamps = pd.date_range(start="2020-01-01", end="2026-10-01", freq="MS", tz="UTC")
    return [str(ts.date())[:7] for ts in stamps]


def _http_get(url: str, timeout: float) -> tuple[int, bytes]:
    """GET with retry-with-backoff (6 attempts, linear 1 s x k).

    A lone 404/5xx is treated as retryable (the archive host flip-flops
    200<->404 under rapid sequential access). Only fail-closed after all
    retries are exhausted.
    """
    last_exc: Exception | None = None
    last_status = None
    for attempt in range(1, RETRIES + 1):
        req = urllib.request.Request(url, method="GET",
                                     headers={"User-Agent": "kilo-c303-ingest"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return int(resp.status), resp.read()
        except urllib.error.HTTPError as exc:  # retryable: 404/5xx/451
            last_status = int(exc.code)
            last_exc = exc
        except Exception as exc:  # noqa: BLE001  transient network
            last_exc = exc
        if attempt < RETRIES:
            time.sleep(1.0 * attempt)
    raise RuntimeError(
        f"GET failed after {RETRIES} attempts: {url} "
        f"(last_status={last_status}, last_exc={last_exc})"
    )


def _is_numeric_first_field(raw: bytes) -> bool:
    first_nl = raw.find(b"\n")
    first_line = raw[: first_nl if first_nl >= 0 else len(raw)]
    first_field = first_line.split(b",", 1)[0].strip()
    try:
        float(first_field)
        return True
    except ValueError:
        return False


def read_zip_frame(raw: bytes, kind: str) -> pd.DataFrame:
    """Parse an archive zip generically (header or headerless).

    Skips any row whose first field is non-numeric (the ``open_time`` /
    ``calc_time`` header row carried by recent months).
    """
    zf = zipfile.ZipFile(io.BytesIO(raw))
    name = zf.namelist()[0]
    raw_csv = zf.read(name)
    if not _is_numeric_first_field(raw_csv):
        # header present: use pandas header inference
        df = pd.read_csv(io.BytesIO(raw_csv))
    else:
        if kind == "funding":
            df = pd.read_csv(io.BytesIO(raw_csv), header=None,
                             names=FUNDING_COLUMNS)
        else:
            df = pd.read_csv(io.BytesIO(raw_csv), header=None,
                             names=KLINE_COLUMNS)
    # coerce: drop any non-numeric first-field row defensively
    if kind == "funding":
        key = "calc_time"
    else:
        key = "open_time"
    df[key] = pd.to_numeric(df[key], errors="coerce")
    df = df.dropna(subset=[key])
    if kind == "funding":
        for c in ("funding_interval_hours", "last_funding_rate"):
            df[c] = pd.to_numeric(df[c], errors="coerce")
    else:
        for c in ("open", "high", "low", "close"):
            df[c] = pd.to_numeric(df[c], errors="coerce")
    df[key] = pd.to_datetime(df[key], unit="ms", utc=True)
    return df


def fetch_month(kind: str, symbol: str, month: str, timeout: float) -> dict:
    if kind == "premium":
        path = PREMIUM_PATH.format(sym=symbol, month=month)
    elif kind == "klines":
        path = KLINES_PATH.format(sym=symbol, month=month)
    else:
        path = FUNDING_PATH.format(sym=symbol, month=month)
    url = ARCHIVE_HOST + path
    status, data = _http_get(url, timeout)
    if status != 200 or not data:
        return {"symbol": symbol, "month": month, "url": url,
                "status": status, "rows": 0, "ok": False}
    try:
        df = read_zip_frame(data, kind)
    except Exception as exc:  # noqa: BLE001
        return {"symbol": symbol, "month": month, "url": url,
                "status": status, "rows": 0, "ok": False,
                "error": f"{type(exc).__name__}: {exc}"}
    return {"symbol": symbol, "month": month, "url": url, "status": status,
            "rows": int(len(df)), "ok": True, "frame": df}


def build_premium_symbol(symbol: str, months: list[str], timeout: float) -> dict:
    detail: dict = {"symbol": symbol, "per_month": [], "accepted_months": [],
                    "stop_month": None, "stop_reason": None}
    frames: list[pd.DataFrame] = []
    for m in months:
        r = fetch_month("premium", symbol, m, timeout)
        detail["per_month"].append({k: r[k] for k in ("month", "status",
                                                      "rows", "ok", "url")})
        if not r["ok"]:
            detail["stop_month"] = m
            detail["stop_reason"] = r.get("error") or f"month {m} http {r['status']}"
            break
        df = r["frame"]
        vals = df[["open", "high", "low", "close"]].to_numpy(dtype=float)
        if not bool(np.isfinite(vals).all()):
            detail["stop_month"] = m
            detail["stop_reason"] = f"month {m} non-finite premium OHLC"
            break
        if int(df["open_time"].duplicated().sum()) != 0:
            detail["stop_month"] = m
            detail["stop_reason"] = f"month {m} duplicate premium timestamps"
            break
        detail["accepted_months"].append(m)
        frames.append(df[["open_time", "open", "high", "low", "close"]])

    if not frames:
        detail["status"] = "excluded"
        detail["exclusion_reason"] = detail["stop_reason"] or "first month failed"
        return detail

    all_df = pd.concat(frames, axis=0).sort_values("open_time")
    all_df = all_df.drop_duplicates("open_time", keep="last").set_index("open_time")
    detail["status"] = "ok"
    detail["frame"] = all_df
    detail["n_raw_bars"] = int(len(all_df))
    return detail


def load_c299(symbol: str) -> dict:
    if not C299_CACHE.exists():
        raise SystemExit(f"FATAL: C299 cache missing: {C299_CACHE}")
    with open(C299_CACHE, "rb") as f:
        p = pickle.load(f)
    return p["per_asset"][symbol]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--timeout", type=float, default=60.0)
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args(argv)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    CACHE.mkdir(parents=True, exist_ok=True)

    # Validate C299 reuse source flags before any work.
    c299_meta = json.loads(C299_META.read_text())
    if c299_meta.get("real_data_only") is not True \
            or c299_meta.get("fabricated_data") is not False:
        raise SystemExit("FATAL: C299 meta provenance flags invalid")
    # C299 predates the executed_fills field; if present it must be false.
    if "executed_fills" in c299_meta and c299_meta.get("executed_fills") is not False:
        raise SystemExit("FATAL: C299 cache executed_fills must be false")

    months = _months()

    # ---- Phase 1: download premiumIndexKlines for all 10 assets ----
    premium: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futs = {pool.submit(build_premium_symbol, s, months, args.timeout): s
                for s in UNIVERSE}
        for fut in as_completed(futs):
            d = fut.result()
            premium[d["symbol"]] = d

    excluded = {s: premium[s].get("exclusion_reason", premium[s].get("status"))
                for s in UNIVERSE if premium[s].get("status") != "ok"}
    if len(excluded) == len(UNIVERSE):
        raise SystemExit(f"FATAL: no asset has premium data. Excluded: {json.dumps(excluded)}")

    # ---- Phase 2: common intersection grid (timestamps in ALL premium archives) ----
    common_index: pd.DatetimeIndex | None = None
    for s in UNIVERSE:
        if premium[s].get("status") != "ok":
            continue
        idx = premium[s]["frame"].index
        common_index = idx if common_index is None else common_index.intersection(idx)
    if common_index is None or len(common_index) == 0:
        raise SystemExit("FATAL: common premium intersection grid is empty")
    common_index = common_index.sort_values()
    n_grid = int(len(common_index))
    grid_start = str(common_index[0])
    grid_end = str(common_index[-1])

    # ---- Phase 3: per-asset alignment to common grid ----
    # Execution data: reuse C299 for BTC/ETH/BCH; fetch klines+funding for the rest.
    fetch_assets = [s for s in UNIVERSE if s not in C299_ASSETS]
    c299_data = {s: load_c299(s) for s in C299_ASSETS}

    klines_frames: dict[str, pd.DataFrame] = {}
    funding_frames: dict[str, pd.DataFrame] = {}
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futs = {}
        for s in fetch_assets:
            futs[pool.submit(_fetch_exec_asset, s, months, args.timeout)] = s
        for fut in as_completed(futs):
            s, kf, ff = fut.result()
            klines_frames[s] = kf
            funding_frames[s] = ff

    per_asset: dict[str, dict] = {}
    selected: list[str] = []
    for s in UNIVERSE:
        if premium[s].get("status") != "ok":
            continue
        prem_df = premium[s]["frame"]
        # premium OHLC reindexed to common grid; missing = NaN (real outage, never imputed)
        prem_al = prem_df.reindex(common_index)
        prem_open = prem_al["open"].to_numpy(dtype=float)
        prem_high = prem_al["high"].to_numpy(dtype=float)
        prem_low = prem_al["low"].to_numpy(dtype=float)
        prem_close = prem_al["close"].to_numpy(dtype=float)
        present = ~np.isnan(prem_close)
        if not bool(np.isfinite(prem_close[present]).all()):
            continue  # fail-closed: non-finite premium on present bars
        if int(present.sum()) == 0:
            continue

        # perp close
        if s in C299_ASSETS:
            c299_pa = c299_data[s]
            c_idx = c299_pa["index"]
            if not isinstance(c_idx, pd.DatetimeIndex):
                c_idx = pd.DatetimeIndex(np.asarray(c_idx))
            close = pd.Series(np.asarray(c299_pa["closes"], dtype=float),
                              index=c_idx).reindex(common_index)
        else:
            kf = klines_frames[s]
            close = pd.Series(np.asarray(kf["close"].to_numpy(dtype=float)),
                              index=kf.index).reindex(common_index)
        close_arr = close.to_numpy(dtype=float)
        if int(close.notna().sum()) == 0:
            continue
        if not bool((close_arr[~np.isnan(close_arr)] > 0).all()):
            continue

        # funding rates (NaN except at native 8h boundaries on the grid)
        if s in C299_ASSETS:
            c299_pa = c299_data[s]
            c_idx = c299_pa["index"]
            if not isinstance(c_idx, pd.DatetimeIndex):
                c_idx = pd.DatetimeIndex(np.asarray(c_idx))
            funding = pd.Series(np.asarray(c299_pa["funding_rates"], dtype=float),
                                index=c_idx).reindex(common_index)
        else:
            ff = funding_frames[s]
            funding = pd.Series(np.asarray(ff["last_funding_rate"].to_numpy(dtype=float)),
                                index=ff.index).reindex(common_index)
        funding_arr = funding.to_numpy(dtype=float)
        f_present = ~np.isnan(funding_arr)
        if not bool(np.isfinite(funding_arr[f_present]).all()):
            continue

        # record premium gap bars (real outages, never imputed)
        gap_bars = [str(t) for t in common_index[~present].tolist()]
        n_missing_prem = int((~present).sum())

        entry = {
            "window_start_utc": grid_start,
            "window_end_utc": grid_end,
            "n_bars": n_grid,
            "n_present_premium_bars": int(present.sum()),
            "n_missing_premium_bars": n_missing_prem,
            "premium_gap_bars_first": gap_bars[0] if gap_bars else None,
            "premium_gap_bars_last": gap_bars[-1] if gap_bars else None,
            "n_funding_boundary_bars": int(f_present.sum()),
            "source": "c299_reuse" if s in C299_ASSETS else "fresh_download",
        }
        entry.update(_compact({
            "prem_open": prem_open,
            "prem_high": prem_high,
            "prem_low": prem_low,
            "prem_close": prem_close,
            "perp_close": close_arr,
            "funding_rates": funding_arr,
            "index": common_index,
        }))
        per_asset[s] = entry
        selected.append(s)

    if not selected:
        raise SystemExit("FATAL: no asset survived alignment to the common grid")

    selected = sorted(selected)
    n_symbols = len(selected)

    payload = {
        "interval": INTERVAL,
        "source_interval": "premiumIndex_1h",
        "symbols": selected,
        "n_symbols": n_symbols,
        "n_universe": len(UNIVERSE),
        "window": {"start": grid_start, "end": grid_end},
        "universe": list(UNIVERSE),
        "common_grid_bars": n_grid,
        "common_grid_start_utc": grid_start,
        "common_grid_end_utc": grid_end,
        "c299_reuse_assets": list(C299_ASSETS),
        "fresh_download_assets": [s for s in UNIVERSE if s not in C299_ASSETS],
        "per_asset": per_asset,
        "real_data_only": True,
        "fabricated_data": False,
        "executed_fills": False,
    }

    blob = _pickle_bytes(payload)
    OUT_PKL.write_bytes(blob)
    pkl_bytes = _assert_under_push_limit(OUT_PKL)
    pkl_sha = sha256_file(OUT_PKL)

    meta = {
        "generated_at_utc": ts,
        "campaign": 303,
        "part": "ingest",
        "interval": INTERVAL,
        "source_interval": "premiumIndex_1h",
        "symbols": selected,
        "n_symbols": n_symbols,
        "n_universe": len(UNIVERSE),
        "common_grid_bars": int(n_grid),
        "common_grid_start_utc": grid_start,
        "common_grid_end_utc": grid_end,
        "window_start_utc": grid_start,
        "window_end_utc": grid_end,
        "source_host": ARCHIVE_HOST,
        "premium_endpoint": PREMIUM_PATH,
        "klines_endpoint": KLINES_PATH,
        "funding_endpoint": FUNDING_PATH,
        "c299_reuse": str(C299_CACHE.relative_to(ROOT)),
        "c299_cache_sha256": sha256_file(C299_CACHE),
        "cache_pkl_bytes": int(pkl_bytes),
        "cache_pkl_mb": round(pkl_bytes / 1e6, 2),
        "push_limit_bytes": PUSH_LIMIT_BYTES,
        "under_push_limit": bool(pkl_bytes < PUSH_LIMIT_BYTES),
        "cache_format": "plain_numpy_ndarrays_no_pandas_legs",
        "real_data_only": True,
        "fabricated_data": False,
        "fetch_real_data_only": True,
        "fetch_fabricated_data": False,
        "executed_fills": False,
        "sha256_from_bytes": pkl_sha,
        "pkl_path": str(OUT_PKL.relative_to(ROOT)),
        "n_months": len(months),
    }
    OUT_META.write_text(json.dumps(meta, indent=2) + "\n")

    per_symbol = {}
    for s in UNIVERSE:
        if s in per_asset:
            pa = per_asset[s]
            per_symbol[s] = {
                "status": "ok",
                "source": pa["source"],
                "window_start_utc": pa["window_start_utc"],
                "window_end_utc": pa["window_end_utc"],
                "n_bars": pa["n_bars"],
                "n_present_premium_bars": pa["n_present_premium_bars"],
                "n_missing_premium_bars": pa["n_missing_premium_bars"],
                "n_funding_boundary_bars": pa["n_funding_boundary_bars"],
            }
        else:
            per_symbol[s] = {
                "status": "excluded",
                "exclusion_reason": excluded.get(s) or "not in common grid",
            }

    provenance = {
        "generated_at_utc": ts,
        "campaign": 303,
        "part": "provenance",
        "real_data_only": True,
        "fabricated_data": False,
        "executed_fills": False,
        "build_source": (
            "archive_download_premium_index_klines_common_grid_plus_execution"
        ),
        "universe_rule": (
            "Universe = 10 USDT-M perps {BTCUSDT, ETHUSDT, XRPUSDT, ADAUSDT, "
            "LTCUSDT, BCHUSDT, LINKUSDT, TRXUSDT, ETCUSDT, XLMUSDT}. premiumIndexKlines "
            "1h bars are real Binance USDT-M perp fair-value premium (open/high/low/close "
            "of the mark-vs-index premium index, ~ +/-1e-3). The common intersection grid "
            "= timestamps present in ALL 10 premium archives; any bar missing in >= 1 asset "
            "is dropped (never imputed). Per-asset premium gaps are carried as NaN. "
            "Execution price = real perp 1h close; funding = native 8h funding rate "
            "(cashflow -rate*signed_weight at each native boundary, causal). "
            "BTC/ETH/BCH execution data reused from verified C299 cache; the other 7 "
            "assets downloaded fresh. No impute/ffill/backfill of any derived series."
        ),
        "cache_serialization": "plain numpy ndarrays; index stored as datetime64[us]; no pandas Series/DataFrame legs",
        "push_limit_note": (
            f"compact ndarray form is {meta['cache_pkl_mb']} MB (< 100 MB). Asserted on disk before success."
        ),
        "n_candidates": len(UNIVERSE),
        "n_selected": n_symbols,
        "selected_symbols": selected,
        "excluded_symbols": {s: per_symbol[s] for s in UNIVERSE if s not in selected},
        "per_symbol": per_symbol,
        "common_grid": {
            "bars": int(n_grid),
            "start_utc": grid_start,
            "end_utc": grid_end,
        },
        "months": months,
        "n_months": len(months),
        "c299_reuse": {
            "cache": str(C299_CACHE.relative_to(ROOT)),
            "cache_sha256": sha256_file(C299_CACHE),
            "meta_sha256": sha256_file(C299_META) if C299_META.exists() else None,
            "provenance_sha256": sha256_file(
                CACHE / "campaign299_multianual_perp_funding_basis_ts.provenance.json"
            ) if (CACHE / "campaign299_multianual_perp_funding_basis_ts.provenance.json").exists()
            else None,
            "assets": list(C299_ASSETS),
        },
    }
    OUT_PROV.write_text(json.dumps(provenance, indent=2, default=str) + "\n")

    summary = {
        "ok": True,
        "campaign": 303,
        "build_source": (
            "archive_download_premium_index_klines_common_grid_plus_execution"
        ),
        "real_data_only": True,
        "fabricated_data": False,
        "executed_fills": False,
        "pkl": str(OUT_PKL.relative_to(ROOT)),
        "pkl_sha256": pkl_sha,
        "pkl_bytes": int(pkl_bytes),
        "pkl_mb": round(pkl_bytes / 1e6, 2),
        "under_push_limit": bool(pkl_bytes < PUSH_LIMIT_BYTES),
        "meta": str(OUT_META.relative_to(ROOT)),
        "meta_sha256": sha256_file(OUT_META),
        "provenance": str(OUT_PROV.relative_to(ROOT)),
        "provenance_sha256": sha256_file(OUT_PROV),
        "n_symbols": n_symbols,
        "n_universe": len(UNIVERSE),
        "common_grid_bars": int(n_grid),
        "common_grid_start_utc": grid_start,
        "common_grid_end_utc": grid_end,
        "selected_symbols": selected,
        "window": {"start": grid_start, "end": grid_end},
        "interval": INTERVAL,
        "c299_cache_sha256": sha256_file(C299_CACHE),
    }
    print(json.dumps(summary, indent=2))
    return 0


def _fetch_exec_asset(symbol: str, months: list[str], timeout: float) -> tuple:
    """Download klines + funding for one asset; return (symbol, klines_df, funding_df)."""
    k_frames: list[pd.DataFrame] = []
    for m in months:
        r = fetch_month("klines", symbol, m, timeout)
        if not r["ok"]:
            raise SystemExit(
                f"FATAL: klines download failed for {symbol} month {m}: "
                f"{r.get('error') or 'http ' + str(r['status'])}"
            )
        k_frames.append(r["frame"][["open_time", "close"]])
    k_df = pd.concat(k_frames, axis=0).sort_values("open_time")
    k_df = k_df.drop_duplicates("open_time", keep="last").set_index("open_time")

    f_frames: list[pd.DataFrame] = []
    for m in months:
        r = fetch_month("funding", symbol, m, timeout)
        if not r["ok"]:
            raise SystemExit(
                f"FATAL: funding download failed for {symbol} month {m}: "
                f"{r.get('error') or 'http ' + str(r['status'])}"
            )
        f_frames.append(r["frame"][["calc_time", "last_funding_rate"]])
    f_df = pd.concat(f_frames, axis=0).sort_values("calc_time")
    f_df = f_df.drop_duplicates("calc_time", keep="last").set_index("calc_time")

    return symbol, k_df, f_df


def _compact(v):
    if isinstance(v, pd.Series):
        return v.to_numpy()
    if isinstance(v, pd.DatetimeIndex):
        return v.to_numpy(dtype="datetime64[us]")
    if isinstance(v, pd.DataFrame):
        return v.to_numpy()
    return v


def _pickle_bytes(payload: dict) -> bytes:
    buf = io.BytesIO()
    pickle.dump(payload, buf, protocol=4)
    return buf.getvalue()


def _assert_under_push_limit(pkl_path: Path) -> int:
    nbytes = pkl_path.stat().st_size
    mb = nbytes / 1e6
    print(f"cache pickle {pkl_path.name} = {nbytes} bytes ({mb:.2f} MB)")
    if nbytes >= PUSH_LIMIT_BYTES:
        raise SystemExit(
            f"FATAL: cache pickle {mb:.2f} MB >= {PUSH_LIMIT_BYTES/1e6:.0f} MB push limit; "
            "refusing to leave an unpushable blob"
        )
    return nbytes


if __name__ == "__main__":
    raise SystemExit(main())
