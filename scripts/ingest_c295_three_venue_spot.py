#!/usr/bin/env python3
"""C295 — ingest REAL three-venue spot 5m klines (Binance + OKX + Coinbase).

C295 is a NEW economic dimension (three-venue real spot): cross-venue basis
convergence / dispersion / lead-lag statistical arbitrage on the SAME asset
trading on Binance, OKX and Coinbase simultaneously.  This is the data step.
It assembles:

- Binance spot 5m klines: fetched fresh from
  https://data-api.binance.vision/api/v3/klines?symbol=<SYM>USDT&interval=5m
  (paginated forward with startTime/endTime, limit=1000).
- OKX spot 5m klines: fetched fresh from
  https://www.okx.com/api/v5/market/history-candles?instId=<SYM>-USDT&bar=5m&limit=300[&after=<ms>]
  (paginated backward with after=<ms>, browser UA required).
- Coinbase spot 5m candles: fetched fresh from
  https://api.exchange.coinbase.com/products/<SYM>-USD/candles?granularity=300&start=<ISO>&end=<ISO>
  (paginated backward by explicit start+end, <=300 bars/page == ~25h per page,
  row [time_s,low,high,open,close,volume], time in seconds).

Only USDT/USD-quoted pairs present on ALL THREE venues with FULL 26,208-bar
coverage over 2026-08-01T00:00Z -> 2026-10-30T23:55Z are retained.  Symbols
with any gap/404/partial history are excluded fail-closed with a recorded
reason.

Persisted artifacts (all real_data_only: true, fabricated_data: false,
SHA256-from-bytes):

- data/cache/campaign295_three_venue_spot.pkl        (binance_/okx_/coinbase_ OHLCV frames)
- data/cache/campaign295_three_venue_spot.meta.json
- data/cache/campaign295_three_venue_spot.provenance.json

No synthetic data, no relabeled two-venue caches, no resampling.  All frames are
reindexed on the exact 5m UTC grid and truncated to the exact window.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import pickle
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "cache"
C290_PKL = CACHE / "campaign290_ohlcv.pkl"

OUT_PKL = CACHE / "campaign295_three_venue_spot.pkl"
OUT_META = CACHE / "campaign295_three_venue_spot.meta.json"
OUT_PROV = CACHE / "campaign295_three_venue_spot.provenance.json"

START_UTC = "2026-08-01T00:00:00Z"
END_UTC = "2026-10-30T23:55:00Z"
INTERVAL = "5m"
STEP_MIN = 5
REQUEST_TIMEOUT = 30.0
# All three public market-data endpoints reject non-browser User-Agent strings;
# use a standard browser UA so they stay reachable (CloudFront).
HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
    "Accept": "application/json",
}
BINANCE_LIMIT = 1000
OKX_LIMIT = 300
COINBASE_LIMIT = 300  # Coinbase hard cap per request (~25h at 5m)
SLEEP_BETWEEN_PAGES = 0.12  # polite pacing
MAX_PAGES_PER_SYMBOL_VENUE = 4000  # safety bound for deep pagination
RETRY_STATUS = {429}
MAX_RETRIES = 6


def binance_to_okx(symbol: str) -> str:
    return symbol[:-4] + "-" + symbol[-4:] if symbol.endswith("USDT") else symbol


def symbol_to_coinbase(symbol: str) -> str:
    return symbol[:-4] + "-USD" if symbol.endswith("USDT") else symbol


def sha256_bytes(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expected_index() -> pd.DatetimeIndex:
    step = pd.Timedelta(minutes=STEP_MIN)
    idx = pd.date_range(
        start=pd.Timestamp(START_UTC), end=pd.Timestamp(END_UTC), freq=step, tz="UTC"
    )
    return pd.DatetimeIndex(idx)


def to_epoch_ms(ts_sec_or_ms: int, unit: str) -> int:
    if unit == "s":
        return ts_sec_or_ms * 1_000
    if unit == "ms":
        return ts_sec_or_ms
    if unit == "us":
        return ts_sec_or_ms // 1_000
    if unit == "ns":
        return ts_sec_or_ms // 1_000_000
    raise RuntimeError(f"unsupported timestamp unit: {unit}")


def iso_from_ms(ms: int) -> str:
    return pd.Timestamp(ms, unit="ms", tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


def _http_get(url: str, timeout: float, retries: int = MAX_RETRIES) -> tuple[int, bytes]:
    last_exc: Exception | None = None
    for attempt in range(retries):
        req = urllib.request.Request(url, method="GET", headers=HTTP_HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return int(resp.status), resp.read()
        except urllib.error.HTTPError as exc:  # noqa: BLE001
            if int(exc.code) in RETRY_STATUS and attempt < retries - 1:
                time.sleep(0.8 * (attempt + 1))
                continue
            return int(exc.code), b""  # 404/400/451 etc: do not retry
        except Exception as exc:  # noqa: BLE001 transient network: retry
            last_exc = exc
            time.sleep(0.6 * (attempt + 1))
    raise RuntimeError(f"GET failed after {retries} attempts: {url}: {last_exc}")


def _rows_from_candles(candles, ts_unit: str) -> list[dict]:
    rows: list[dict] = []
    for c in candles:
        try:
            rows.append(
                {
                    "ts_ms": to_epoch_ms(int(c[0]), ts_unit),
                    "open": float(c[1]),
                    "high": float(c[2]),
                    "low": float(c[3]),
                    "close": float(c[4]),
                    "volume": float(c[5]),
                }
            )
        except Exception:
            continue
    return rows


def build_venue_frame(
    rows: list[dict], exp_idx: pd.DatetimeIndex
) -> tuple[pd.DataFrame | None, dict]:
    """Reindex raw rows onto the exact 5m UTC grid and compute coverage stats.

    Returns (frame_or_None, stats).  frame is None unless coverage is full
    (zero NaN, strictly positive finite prices, duplicate-free, exact span).
    """
    stats: dict = {
        "n_raw": int(len(rows)),
        "full_coverage": False,
        "ok": False,
    }
    if not rows:
        stats["status"] = "no_data"
        return None, stats
    raw = pd.DataFrame(rows)
    raw = raw.drop_duplicates("ts_ms", keep="last").sort_values("ts_ms")
    idx = pd.DatetimeIndex(pd.to_datetime(raw["ts_ms"], unit="ms", utc=True))
    if not idx.is_unique:
        stats["status"] = "duplicate_ts"
        return None, stats
    df = raw.set_index(idx)[["open", "high", "low", "close", "volume"]].astype(float)
    df = df.reindex(exp_idx)
    n_expected = int(len(exp_idx))
    vals = df.to_numpy(dtype=float)
    nan_count = int(np.isnan(vals).sum())
    price_vals = df[["open", "high", "low", "close"]].to_numpy(dtype=float)
    vol_vals = df[["volume"]].to_numpy(dtype=float)
    finite = bool(np.isfinite(vals).all()) if nan_count == 0 else False
    positive_prices = bool((price_vals > 0).all()) if nan_count == 0 else False
    volume_nonneg = bool((vol_vals >= 0).all()) if nan_count == 0 else False
    correct_span = bool(len(df) == n_expected)
    full_coverage = bool(
        correct_span and nan_count == 0 and finite and positive_prices and volume_nonneg
    )
    stats.update(
        {
            "status": "ok" if full_coverage else "coverage_fail",
            "ok": full_coverage,
            "nan_count": nan_count,
            "all_finite": finite,
            "all_prices_positive": positive_prices,
            "volume_nonneg": volume_nonneg,
            "full_coverage": full_coverage,
            "bars_after_reindex": int(len(df)),
            "expected_bars": n_expected,
            "min_volume": float(np.nanmin(vol_vals)) if vol_vals.size else None,
            "oldest_ts_ms": int(raw["ts_ms"].min()),
            "newest_ts_ms": int(raw["ts_ms"].max()),
        }
    )
    return (df if full_coverage else None), stats


# ---------------------------------------------------------------- Binance ----


def fetch_binance(symbol: str, exp_idx: pd.DatetimeIndex, timeout: float) -> dict:
    """Paginate Binance klines forward from window_start until window_end covered."""
    detail_pages = []
    frames = []
    start_ms = int(pd.Timestamp(START_UTC).timestamp() * 1000)
    end_ms = int(pd.Timestamp(END_UTC).timestamp() * 1000)
    target_start_ms = start_ms
    target_end_ms = end_ms
    cursor = target_start_ms
    pages = 0
    newest_ts: int | None = None
    oldest_ts: int | None = None
    status = "ok"

    while cursor <= target_end_ms and pages < MAX_PAGES_PER_SYMBOL_VENUE:
        url = (
            f"https://data-api.binance.vision/api/v3/klines"
            f"?symbol={symbol}&interval={INTERVAL}&limit={BINANCE_LIMIT}"
            f"&startTime={cursor}&endTime={target_end_ms + 86_400_000}"
        )
        st, data = _http_get(url, timeout)
        page = {"venue": "binance", "symbol": symbol, "url": url, "status": st, "start": cursor}
        if st != 200:
            page["rows"] = 0
            detail_pages.append(page)
            status = f"http_{st}"
            break
        try:
            payload = json.loads(data.decode())
        except Exception as exc:  # noqa: BLE001
            page["rows"] = 0
            page["error"] = f"json parse: {exc}"
            detail_pages.append(page)
            status = "json_error"
            break
        if not isinstance(payload, list) or not payload:
            page["rows"] = 0
            detail_pages.append(page)
            break
        page["rows"] = int(len(payload))
        detail_pages.append(page)
        rows = _rows_from_candles(payload, "ms")
        if not rows:
            break
        df_page = pd.DataFrame(rows)
        frames.append(df_page)
        page_newest = int(df_page["ts_ms"].max())
        page_oldest = int(df_page["ts_ms"].min())
        newest_ts = page_newest if newest_ts is None else max(newest_ts, page_newest)
        oldest_ts = page_oldest if oldest_ts is None else min(oldest_ts, page_oldest)
        pages += 1
        if page_newest >= target_end_ms:
            break
        cursor = page_newest + 1
        time.sleep(SLEEP_BETWEEN_PAGES)

    if not frames:
        return {
            "venue": "binance",
            "symbol": symbol,
            "status": status or "no_data",
            "pages": detail_pages,
            "n_pages": pages,
            "ok": False,
            "full_coverage": False,
        }
    raw = pd.concat(frames, axis=0).drop_duplicates("ts_ms", keep="last").sort_values("ts_ms")
    rows = raw.to_dict("records")
    frame, cov = build_venue_frame(rows, exp_idx)
    cov.update({
        "venue": "binance",
        "symbol": symbol,
        "n_pages": pages,
        "oldest_ts_ms": oldest_ts,
        "newest_ts_ms": newest_ts,
        "target_end_ms": target_end_ms,
    })
    return {
        "venue": "binance",
        "symbol": symbol,
        "status": cov["status"],
        "pages": detail_pages,
        "n_pages": pages,
        "frame": frame,
        "full_coverage": bool(frame is not None),
        "ok": bool(frame is not None),
        **cov,
    }


# ---------------------------------------------------------------- OKX --------


def fetch_okx(inst_id: str, exp_idx: pd.DatetimeIndex, timeout: float) -> dict:
    """Paginate OKX history-candles backward until window_start is covered."""
    detail_pages = []
    frames = []
    after_ms: int | None = None
    pages = 0
    oldest_ts: int | None = None
    newest_ts: int | None = None
    target_start_ms = int(pd.Timestamp(START_UTC).timestamp() * 1000)
    status = "ok"

    while pages < MAX_PAGES_PER_SYMBOL_VENUE:
        url = (
            f"https://www.okx.com/api/v5/market/history-candles"
            f"?instId={inst_id}&bar={INTERVAL}&limit={OKX_LIMIT}"
        )
        if after_ms is not None:
            url += f"&after={after_ms}"
        st, data = _http_get(url, timeout)
        page = {
            "venue": "okx",
            "instId": inst_id,
            "url": url,
            "status": st,
            "after": after_ms,
        }
        if st != 200:
            page["rows"] = 0
            detail_pages.append(page)
            status = f"http_{st}"
            break
        try:
            payload = json.loads(data.decode())
        except Exception as exc:  # noqa: BLE001
            page["rows"] = 0
            page["error"] = f"json parse: {exc}"
            detail_pages.append(page)
            status = "json_error"
            break
        if payload.get("code") != "0":
            page["rows"] = 0
            page["error"] = f"okx code {payload.get('code')}: {payload.get('msg')}"
            detail_pages.append(page)
            status = f"okx_code_{payload.get('code')}"
            break
        candles = payload.get("data") or []
        if not candles:
            page["rows"] = 0
            detail_pages.append(page)
            break
        page["rows"] = int(len(candles))
        detail_pages.append(page)
        rows = _rows_from_candles(candles, "ms")
        if not rows:
            break
        df_page = pd.DataFrame(rows)
        frames.append(df_page)
        page_oldest = int(df_page["ts_ms"].min())
        page_newest = int(df_page["ts_ms"].max())
        oldest_ts = page_oldest if oldest_ts is None else min(oldest_ts, page_oldest)
        newest_ts = page_newest if newest_ts is None else max(newest_ts, page_newest)
        after_ms = page_oldest - 1
        pages += 1
        if page_oldest <= target_start_ms:
            break
        time.sleep(SLEEP_BETWEEN_PAGES)

    if not frames:
        return {
            "venue": "okx",
            "instId": inst_id,
            "status": status or "no_data",
            "pages": detail_pages,
            "n_pages": pages,
            "ok": False,
            "full_coverage": False,
        }
    raw = pd.concat(frames, axis=0).drop_duplicates("ts_ms", keep="last").sort_values("ts_ms")
    rows = raw.to_dict("records")
    frame, cov = build_venue_frame(rows, exp_idx)
    cov.update({
        "venue": "okx",
        "instId": inst_id,
        "symbol": inst_id,
        "n_pages": pages,
        "oldest_ts_ms": oldest_ts,
        "newest_ts_ms": newest_ts,
        "target_start_ms": target_start_ms,
    })
    return {
        "venue": "okx",
        "instId": inst_id,
        "status": cov["status"],
        "pages": detail_pages,
        "n_pages": pages,
        "frame": frame,
        "full_coverage": bool(frame is not None),
        "ok": bool(frame is not None),
        **cov,
    }


# ------------------------------------------------------------- Coinbase ------


def fetch_coinbase(product: str, exp_idx: pd.DatetimeIndex, timeout: float) -> dict:
    """Paginate Coinbase candles backward by explicit start+end (<=300 bars/page)."""
    detail_pages = []
    frames = []
    pages = 0
    end_ms = int(pd.Timestamp(END_UTC).timestamp() * 1000)
    start_ms = int(pd.Timestamp(START_UTC).timestamp() * 1000)
    target_start_ms = start_ms
    target_end_ms = end_ms
    cursor_end = target_end_ms
    oldest_ts: int | None = None
    newest_ts: int | None = None
    status = "ok"
    # Coinbase cap: 300 candles at granularity 300 (5m) == 25h per page.
    page_span_ms = int(COINBASE_LIMIT * STEP_MIN * 60 * 1000)

    while cursor_end > target_start_ms and pages < MAX_PAGES_PER_SYMBOL_VENUE:
        cursor_start = max(target_start_ms, cursor_end - page_span_ms)
        url = (
            f"https://api.exchange.coinbase.com/products/{product}/candles"
            f"?granularity=300&start={iso_from_ms(cursor_start)}&end={iso_from_ms(cursor_end)}"
        )
        st, data = _http_get(url, timeout)
        page = {
            "venue": "coinbase",
            "product": product,
            "url": url,
            "status": st,
            "start": iso_from_ms(cursor_start),
            "end": iso_from_ms(cursor_end),
        }
        if st != 200:
            page["rows"] = 0
            detail_pages.append(page)
            status = f"http_{st}"
            break
        try:
            payload = json.loads(data.decode())
        except Exception as exc:  # noqa: BLE001
            page["rows"] = 0
            page["error"] = f"json parse: {exc}"
            detail_pages.append(page)
            status = "json_error"
            break
        if not isinstance(payload, list) or not payload:
            page["rows"] = 0
            detail_pages.append(page)
            break
        page["rows"] = int(len(payload))
        detail_pages.append(page)
        rows = _rows_from_candles(payload, "s")
        if not rows:
            break
        df_page = pd.DataFrame(rows)
        frames.append(df_page)
        page_oldest = int(df_page["ts_ms"].min())
        page_newest = int(df_page["ts_ms"].max())
        oldest_ts = page_oldest if oldest_ts is None else min(oldest_ts, page_oldest)
        newest_ts = page_newest if newest_ts is None else max(newest_ts, page_newest)
        pages += 1
        if page_oldest <= target_start_ms:
            break
        cursor_end = page_oldest - 1_000  # move one ms older to avoid dup boundary
        time.sleep(SLEEP_BETWEEN_PAGES)

    if not frames:
        return {
            "venue": "coinbase",
            "product": product,
            "status": status or "no_data",
            "pages": detail_pages,
            "n_pages": pages,
            "ok": False,
            "full_coverage": False,
        }
    raw = pd.concat(frames, axis=0).drop_duplicates("ts_ms", keep="last").sort_values("ts_ms")
    rows = raw.to_dict("records")
    frame, cov = build_venue_frame(rows, exp_idx)
    cov.update({
        "venue": "coinbase",
        "product": product,
        "symbol": product,
        "n_pages": pages,
        "oldest_ts_ms": oldest_ts,
        "newest_ts_ms": newest_ts,
        "target_start_ms": target_start_ms,
        "target_end_ms": target_end_ms,
    })
    return {
        "venue": "coinbase",
        "product": product,
        "status": cov["status"],
        "pages": detail_pages,
        "n_pages": pages,
        "frame": frame,
        "full_coverage": bool(frame is not None),
        "ok": bool(frame is not None),
        **cov,
    }


def _pickle_bytes(payload: dict) -> bytes:
    buf = io.BytesIO()
    pickle.dump(payload, buf, protocol=pickle.HIGHEST_PROTOCOL)
    return buf.getvalue()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--timeout", type=float, default=REQUEST_TIMEOUT)
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args(argv)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    CACHE.mkdir(parents=True, exist_ok=True)

    exp_idx = expected_index()
    n_expected = int(len(exp_idx))

    if not C290_PKL.exists():
        raise SystemExit(
            f"FATAL: C290 spot cache missing, cannot establish C295 universe: {C290_PKL}"
        )
    with open(C290_PKL, "rb") as fh:
        bpayload = pickle.load(fh)
    universe_symbols = list(bpayload["symbols"])
    if not universe_symbols:
        raise SystemExit("FATAL: C290 cache has no symbols")

    binance_host = "https://data-api.binance.vision"
    okx_host = "https://www.okx.com"
    coinbase_host = "https://api.exchange.coinbase.com"

    print(
        f"[C295] Fetching 5m for {len(universe_symbols)} symbols x 3 venues, "
        f"window {START_UTC}..{END_UTC} ({n_expected} bars)",
        flush=True,
    )

    # One task per (symbol, venue); pagination within a task is sequential.
    tasks: list[tuple[str, str, str]] = []  # (symbol, venue, venue_id)
    for s in universe_symbols:
        tasks.append((s, "binance", s))
        tasks.append((s, "okx", binance_to_okx(s)))
        tasks.append((s, "coinbase", symbol_to_coinbase(s)))

    results: dict[tuple[str, str], dict] = {}
    with ThreadPoolExecutor(max_workers=max(1, int(args.workers))) as ex:
        futs = {}
        for sym, venue, vid in tasks:
            if venue == "binance":
                futs[ex.submit(fetch_binance, sym, exp_idx, args.timeout)] = (sym, venue)
            elif venue == "okx":
                futs[ex.submit(fetch_okx, vid, exp_idx, args.timeout)] = (sym, venue)
            else:
                futs[ex.submit(fetch_coinbase, vid, exp_idx, args.timeout)] = (sym, venue)
        for fut in as_completed(futs):
            key = futs[fut]
            try:
                results[key] = fut.result()
            except Exception as exc:  # noqa: BLE001
                results[key] = {
                    "venue": key[1],
                    "symbol": key[0],
                    "status": "fetch_error",
                    "error": str(exc),
                    "pages": [],
                    "full_coverage": False,
                    "ok": False,
                }

    # Print per-symbol per-venue coverage.
    for s in universe_symbols:
        line = f"  [C295] {s}:"
        for venue in ("binance", "okx", "coinbase"):
            r = results.get((s, venue), {})
            line += f" {venue}={r.get('status')} full={r.get('full_coverage')} pages={r.get('n_pages')} nan={r.get('nan_count')}"
        print(line, flush=True)

    selected: list[str] = []
    excluded: dict[str, str] = {}
    venue_frames: dict[str, dict[str, pd.DataFrame]] = {
        "binance": {},
        "okx": {},
        "coinbase": {},
    }
    coverage: dict[str, dict] = {}

    for s in universe_symbols:
        cov_sym = {}
        ok_all = True
        reason = None
        for venue in ("binance", "okx", "coinbase"):
            r = results.get((s, venue), {})
            cov_sym[venue] = {
                "venue": venue,
                "symbol": s,
                "source_host": {
                    "binance": binance_host,
                    "okx": okx_host,
                    "coinbase": coinbase_host,
                }[venue],
                "full_coverage": bool(r.get("full_coverage")),
                "status": r.get("status"),
                "n_pages": r.get("n_pages"),
                "nan_count": r.get("nan_count"),
                "oldest_ts_ms": r.get("oldest_ts_ms"),
                "newest_ts_ms": r.get("newest_ts_ms"),
            }
            if not r.get("ok"):
                ok_all = False
                reason = str(r.get("status", "unknown"))
        coverage[s] = cov_sym
        if not ok_all:
            excluded[s] = reason or "incomplete_coverage"
            continue
        selected.append(s)
        for venue in ("binance", "okx", "coinbase"):
            r = results[(s, venue)]
            key = {"binance": "binance", "okx": "okx", "coinbase": "coinbase"}[venue]
            venue_frames[key][s] = r["frame"]

    selected = sorted(selected)

    # Assemble per-venue frames on the exact window grid.
    n_bars = n_expected
    frames_payload: dict = {}
    for venue, colmap in (
        ("binance", ("open", "high", "low", "close", "volume")),
        ("okx", ("open", "high", "low", "close", "volume")),
        ("coinbase", ("open", "high", "low", "close", "volume")),
    ):
        for col in colmap:
            key = f"{venue}_{col}s" if col != "volume" else f"{venue}_volumes"
            if not selected:
                frames_payload[key] = pd.DataFrame(index=exp_idx)
            else:
                arr = np.column_stack(
                    [venue_frames[venue][s][col].to_numpy(dtype=float) for s in selected]
                )
                frames_payload[key] = pd.DataFrame(arr, index=exp_idx, columns=selected)

    payload = {
        "campaign": 295,
        "part": "data",
        "interval": INTERVAL,
        "symbols": selected,
        "window_start_utc": START_UTC,
        "window_end_utc": END_UTC,
        "n_bars": n_bars,
        "expected_bars": n_expected,
        "binance_opens": frames_payload["binance_opens"],
        "binance_highs": frames_payload["binance_highs"],
        "binance_lows": frames_payload["binance_lows"],
        "binance_closes": frames_payload["binance_closes"],
        "binance_volumes": frames_payload["binance_volumes"],
        "okx_opens": frames_payload["okx_opens"],
        "okx_highs": frames_payload["okx_highs"],
        "okx_lows": frames_payload["okx_lows"],
        "okx_closes": frames_payload["okx_closes"],
        "okx_volumes": frames_payload["okx_volumes"],
        "coinbase_opens": frames_payload["coinbase_opens"],
        "coinbase_highs": frames_payload["coinbase_highs"],
        "coinbase_lows": frames_payload["coinbase_lows"],
        "coinbase_closes": frames_payload["coinbase_closes"],
        "coinbase_volumes": frames_payload["coinbase_volumes"],
        "universe_binance": universe_symbols,
        "excluded_symbols": excluded,
        "coverage": coverage,
    }
    OUT_PKL.write_bytes(_pickle_bytes(payload))

    pkl_sha = sha256_bytes(OUT_PKL)
    okx_instids = {s: binance_to_okx(s) for s in selected}
    coinbase_products = {s: symbol_to_coinbase(s) for s in selected}
    meta = {
        "generated_at_utc": ts,
        "campaign": 295,
        "part": "ingest",
        "interval": INTERVAL,
        "symbols": selected,
        "n_symbols": len(selected),
        "rows": n_bars,
        "expected_bars": n_expected,
        "columns_per_frame": ["open", "high", "low", "close", "volume"],
        "venues": ["binance", "okx", "coinbase"],
        "venue_frames": {
            "binance": [
                "binance_opens",
                "binance_highs",
                "binance_lows",
                "binance_closes",
                "binance_volumes",
            ],
            "okx": [
                "okx_opens",
                "okx_highs",
                "okx_lows",
                "okx_closes",
                "okx_volumes",
            ],
            "coinbase": [
                "coinbase_opens",
                "coinbase_highs",
                "coinbase_lows",
                "coinbase_closes",
                "coinbase_volumes",
            ],
        },
        "window_start_utc": START_UTC,
        "window_end_utc": END_UTC,
        "real_data_only": True,
        "fabricated_data": False,
        "fetch_real_data_only": True,
        "fetch_fabricated_data": False,
        "source_host_binance": binance_host,
        "source_endpoint_binance": "/api/v3/klines",
        "source_host_okx": okx_host,
        "source_endpoint_okx": "/api/v5/market/history-candles",
        "source_host_coinbase": coinbase_host,
        "source_endpoint_coinbase": "/products/<SYM>-USD/candles",
        "coinbase_granularity": 300,
        "okx_bar": INTERVAL,
        "okx_limit": OKX_LIMIT,
        "binance_limit": BINANCE_LIMIT,
        "sha256_from_bytes": pkl_sha,
        "pkl_path": str(OUT_PKL.relative_to(ROOT)),
    }
    OUT_META.write_text(json.dumps(meta, indent=2) + "\n")

    provenance = {
        "generated_at_utc": ts,
        "campaign": 295,
        "part": "provenance",
        "real_data_only": True,
        "fabricated_data": False,
        "mechanism": (
            "three_venue_real_spot_basis_dispersion_leadlag_stat_arb_ingest "
            "(Binance + OKX + Coinbase 5m closes)"
        ),
        "universe_rule": (
            "Binance spot universe (26 USDT symbols from verified C290 cache). Binance, OKX and Coinbase "
            "5m klines/candles are fetched fresh from their public endpoints. A symbol is retained only if "
            "ALL THREE venues have full 26,208-bar coverage over "
            "2026-08-01T00:00Z..2026-10-30T23:55Z on the exact 5m UTC grid, zero NaNs, strictly positive "
            "finite prices. Symbols with any gap, 404/400, or partial history are excluded fail-closed with "
            "a recorded reason. No synthetic data, no relabeled two-venue caches, no resampling."
        ),
        "n_universe_binance": len(universe_symbols),
        "n_selected": len(selected),
        "selected_symbols": selected,
        "excluded_symbols": excluded,
        "okx_instids": okx_instids,
        "coinbase_products": coinbase_products,
        "per_symbol": {
            s: {
                "binance_symbol": s,
                "okx_inst_id": binance_to_okx(s),
                "coinbase_product": symbol_to_coinbase(s),
                "binance_full_coverage": coverage[s]["binance"]["full_coverage"],
                "okx_full_coverage": coverage[s]["okx"]["full_coverage"],
                "coinbase_full_coverage": coverage[s]["coinbase"]["full_coverage"],
                "binance_status": coverage[s]["binance"]["status"],
                "okx_status": coverage[s]["okx"]["status"],
                "coinbase_status": coverage[s]["coinbase"]["status"],
                "binance_nan_count": coverage[s]["binance"]["nan_count"],
                "okx_nan_count": coverage[s]["okx"]["nan_count"],
                "coinbase_nan_count": coverage[s]["coinbase"]["nan_count"],
                "binance_n_pages": coverage[s]["binance"]["n_pages"],
                "okx_n_pages": coverage[s]["okx"]["n_pages"],
                "coinbase_n_pages": coverage[s]["coinbase"]["n_pages"],
            }
            for s in universe_symbols
        },
        "blocked_routes": {
            "fapi.binance.com": 451,
            "testnet.binance.vision": 451,
            "api.binance.com": 451,
            "api.bybit.com": 403,
        },
    }
    OUT_PROV.write_text(json.dumps(provenance, indent=2, default=str) + "\n")

    summary = {
        "ok": True,
        "campaign": 295,
        "real_data_only": True,
        "fabricated_data": False,
        "pkl": str(OUT_PKL.relative_to(ROOT)),
        "pkl_sha256": pkl_sha,
        "meta": str(OUT_META.relative_to(ROOT)),
        "meta_sha256": sha256_bytes(OUT_META),
        "provenance": str(OUT_PROV.relative_to(ROOT)),
        "provenance_sha256": sha256_bytes(OUT_PROV),
        "n_symbols": len(selected),
        "n_bars": n_bars,
        "window": {"start": START_UTC, "end": END_UTC},
        "selected_symbols": selected,
        "excluded_symbols": excluded,
        "venue_counts": {
            "binance_full": sum(1 for s in selected if coverage[s]["binance"]["full_coverage"]),
            "okx_full": sum(1 for s in selected if coverage[s]["okx"]["full_coverage"]),
            "coinbase_full": sum(1 for s in selected if coverage[s]["coinbase"]["full_coverage"]),
        },
        "overlap_rule": "full coverage on Binance, OKX and Coinbase over the exact window",
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
