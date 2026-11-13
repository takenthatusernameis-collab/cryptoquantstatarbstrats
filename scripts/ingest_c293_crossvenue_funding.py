#!/usr/bin/env python3
"""C293 — ingest REAL cross-venue USDT-M perp funding + prices (OKX + Binance C291 cache).

C293 is a NEW economic dimension (multi-venue perp derivatives): cross-venue funding-
carry convergence / carry statistical arbitrage on the SAME USDT asset's perpetual
futures trading on different exchanges (OKX USDT-M perp vs Binance USDT-M perp).
This is the data step. It assembles:

- OKX perp funding-rate history: paginated public endpoint
  https://www.okx.com/api/v5/public/funding-rate-history?instId=<SYM>-USDT-SWAP&limit=100[&after=<fundingTime_ms>]
  A browser User-Agent is required (non-browser UA gets HTTP 403 from CloudFront).
- OKX perp 5m klines: https://www.okx.com/api/v5/market/history-candles?instId=<SYM>-USDT-SWAP&bar=5m&limit=100[&after=<ms>]
  (same endpoint pattern as C292 spot, perp instId suffix).
- Binance USDT-M perp funding + 5m closes: reused from the verified C291 cache
  (data/cache/campaign291_perp_5m.pkl) -- never copied, never relabeled.

The pre-registered common window is ≈2026-08-10T00:00Z → 2026-10-30T23:55Z (≈81 days),
set by OKX ~95-day funding depth vs the Binance C291 cache (2026-08-01→2026-10-30T23:55Z).
Funding is aligned on each symbol's native funding boundary (OKX 8h; Binance 8h/4h per
symbol, recorded) and forward-filled to the 5m grid for feature computation; funding
cashflows apply only at native boundary bars.

Perps present on BOTH venues with full common-window funding coverage are retained;
symbols with any gap/404/partial history are excluded fail-closed with a recorded reason.

Persisted artifacts (all real_data_only: true, fabricated_data: false, SHA256-from-bytes):
- data/cache/campaign293_crossvenue_funding.pkl
- data/cache/campaign293_crossvenue_funding.meta.json
- data/cache/campaign293_crossvenue_funding.provenance.json

No synthetic data, no relabeled old caches, no resampling.
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
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "cache"
C291_PKL = CACHE / "campaign291_perp_5m.pkl"

OUT_PKL = CACHE / "campaign293_crossvenue_funding.pkl"
OUT_META = CACHE / "campaign293_crossvenue_funding.meta.json"
OUT_PROV = CACHE / "campaign293_crossvenue_funding.provenance.json"

OKX_HOST = "https://www.okx.com"
OKX_FUNDING_ENDPOINT = "/api/v5/public/funding-rate-history"
OKX_KLINE_ENDPOINT = "/api/v5/market/history-candles"
OKX_BAR = "5m"
# OKX market/funding history endpoints accept up to limit=300 (verified
# 2026-11-13: funding-rate-history returns the full 286-point depth in one page;
# history-candles returns 300 bars/page).  Using 300 cuts kline pagination from
# ~234 to ~78 pages/symbol -- a real-data-only speedup (no resampling).
OKX_LIMIT = 300
REQUEST_TIMEOUT = 30.0
# OKX rejects non-browser User-Agent strings with HTTP 403 (CloudFront).  Use a
# standard browser UA so the public market-data endpoint stays reachable.
HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
    "Accept": "application/json",
}
# OKX public market-data rate limit is ~20 requests / 2s / IP.  With 3 workers a
# 0.15s sleep exceeds that and risks HTTP 429; 0.4s matches the proven-safe C292
# pacing (~7.5 req/s aggregate).
SLEEP_BETWEEN_REQUESTS = 0.4
MAX_PAGES_PER_SYMBOL = 20000
OKX_RETRY_STATUS = {429}

# Pre-registered common window: OKX perp funding depth measured 2026-11-13 starts
# 2026-08-10T16:00Z for the 8h symbols (286 points) and 2026-08-10T12:00Z for the
# 4h symbols (PUMP/TAO/ONDO/GRAM/TRUMP); the LATER of these (16:00Z) is the first
# bar where EVERY symbol has an OKX funding sample. Binance C291 cache covers
# 2026-08-01 -> 2026-10-30T23:55Z. Common window = intersection = 16:00Z start.
COMMON_START_UTC = "2026-08-10T16:00:00Z"
COMMON_END_UTC = "2026-10-30T23:55:00Z"
INTERVAL = "5m"
MIN_SYMBOLS = 2

FUNDING_STALE_BARS = int(24 * 60 / 5) + 1  # 24h + 1 bar of 5m bars


def sha256_bytes(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def to_epoch_ms(idx: pd.DatetimeIndex) -> np.ndarray:
    """Convert a UTC DatetimeIndex to integer epoch MILLISECONDS, unit-agnostic.

    pandas 3.x defaults to microsecond (datetime64[us]) resolution, so a naive
    view('int64') // 1_000_000 yields seconds, not milliseconds. OKX timestamps
    are epoch milliseconds, so normalise explicitly from the index unit.
    """
    idx = pd.DatetimeIndex(idx)
    if idx.tz is None:
        idx = idx.tz_localize("UTC")
    else:
        idx = idx.tz_convert("UTC")
    unit = getattr(idx.dtype, "unit", "ns")
    vals = idx.asi8
    if unit == "s":
        return vals * 1_000
    if unit == "ms":
        return vals
    if unit == "us":
        return vals // 1_000
    if unit == "ns":
        return vals // 1_000_000
    raise RuntimeError(f"unsupported datetime unit: {unit}")


def _http_get(url: str, timeout: float, retries: int = 6) -> tuple[int, bytes]:
    last_exc: Exception | None = None
    for attempt in range(retries):
        req = urllib.request.Request(url, method="GET", headers=HTTP_HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return int(resp.status), resp.read()
        except urllib.error.HTTPError as exc:  # noqa: BLE001
            if int(exc.code) in OKX_RETRY_STATUS and attempt < retries - 1:
                time.sleep(1.0 * (attempt + 1))
                continue  # rate limit: retry
            return int(exc.code), b""  # 404/451 etc: do not retry
        except Exception as exc:  # noqa: BLE001 transient network: retry
            last_exc = exc
            time.sleep(0.6 * (attempt + 1))
    raise RuntimeError(f"GET failed after {retries} attempts: {url}: {last_exc}")


def binance_to_okx(symbol: str) -> str:
    return symbol[:-4] + "-USDT-SWAP" if symbol.endswith("USDT") else symbol


def fetch_okx_funding(inst_id: str, target_start_ms: int, timeout: float) -> dict:
    """Paginate OKX funding-rate-history backward until target_start is covered.

    Returns per-page detail plus a frame of (fundingTime, fundingRate) records,
    or an exclusion reason if coverage is incomplete.
    """
    detail_pages = []
    records = []
    after_ms: int | None = None
    pages = 0
    oldest_ts: int | None = None

    while pages < MAX_PAGES_PER_SYMBOL:
        url = f"{OKX_HOST}{OKX_FUNDING_ENDPOINT}?instId={inst_id}&limit={OKX_LIMIT}"
        if after_ms is not None:
            url += f"&after={after_ms}"
        status, data = _http_get(url, timeout)
        page = {"instId": inst_id, "url": url, "status": status, "after": after_ms}
        if status != 200:
            page["rows"] = 0
            detail_pages.append(page)
            break
        try:
            payload = json.loads(data.decode())
        except Exception as exc:  # noqa: BLE001
            page["rows"] = 0
            page["error"] = f"json parse: {exc}"
            detail_pages.append(page)
            break
        code = payload.get("code")
        if code != "0":
            page["rows"] = 0
            page["error"] = f"okx code {code}: {payload.get('msg')}"
            detail_pages.append(page)
            break
        candles = payload.get("data") or []
        if not candles:
            page["rows"] = 0
            detail_pages.append(page)
            break
        page["rows"] = int(len(candles))
        detail_pages.append(page)
        for c in candles:
            try:
                records.append(
                    {
                        "fundingTime_ms": int(c["fundingTime"]),
                        "fundingRate": float(c["fundingRate"]),
                    }
                )
            except Exception:
                continue
        page_records = records[-len(candles):]
        page_oldest = int(min(r["fundingTime_ms"] for r in page_records))
        oldest_ts = page_oldest if oldest_ts is None else min(oldest_ts, page_oldest)
        # OKX returns newest first; paginate back using the oldest ts seen.
        after_ms = page_oldest - 1
        pages += 1
        if page_oldest <= target_start_ms:
            break
        time.sleep(SLEEP_BETWEEN_REQUESTS)

    if not records:
        return {
            "instId": inst_id,
            "status": "no_data",
            "pages": detail_pages,
            "ok": False,
            "records": [],
        }

    df = pd.DataFrame(records).drop_duplicates("fundingTime_ms").sort_values("fundingTime_ms")
    df["fundingTime"] = pd.to_datetime(df["fundingTime_ms"], unit="ms", utc=True)
    return {
        "instId": inst_id,
        "status": "ok",
        "pages": detail_pages,
        "n_pages": pages,
        "n_records": int(len(df)),
        "oldest_ts_ms": int(df["fundingTime_ms"].min()),
        "newest_ts_ms": int(df["fundingTime_ms"].max()),
        "oldest_ts": str(df["fundingTime"].min()),
        "newest_ts": str(df["fundingTime"].max()),
        "ok": True,
        "frame": df,
    }


def fetch_okx_klines(inst_id: str, exp_idx: pd.DatetimeIndex, timeout: float) -> dict:
    """Paginate OKX perp 5m history-candles backward until window_start is covered.

    Returns dict with status, bars collected, per-page detail, and the raw
    frame (ts, open, high, low, close, volume) indexed by ts, or an exclusion
    reason if coverage is incomplete.
    """
    detail_pages = []
    frames = []
    after_ms: int | None = None
    pages = 0
    oldest_ts: int | None = None
    target_start_ms = int(exp_idx[0].timestamp() * 1000)

    while pages < MAX_PAGES_PER_SYMBOL:
        url = f"{OKX_HOST}{OKX_KLINE_ENDPOINT}?instId={inst_id}&bar={OKX_BAR}&limit={OKX_LIMIT}"
        if after_ms is not None:
            url += f"&after={after_ms}"
        status, data = _http_get(url, timeout)
        page = {
            "instId": inst_id,
            "url": url,
            "status": status,
            "after": after_ms,
        }
        if status != 200:
            page["rows"] = 0
            detail_pages.append(page)
            break
        try:
            payload = json.loads(data.decode())
        except Exception as exc:  # noqa: BLE001
            page["rows"] = 0
            page["error"] = f"json parse: {exc}"
            detail_pages.append(page)
            break
        code = payload.get("code")
        if code != "0":
            page["rows"] = 0
            page["error"] = f"okx code {code}: {payload.get('msg')}"
            detail_pages.append(page)
            break
        candles = payload.get("data") or []
        if not candles:
            page["rows"] = 0
            detail_pages.append(page)
            break
        page["rows"] = int(len(candles))
        detail_pages.append(page)
        rows = []
        for c in candles:
            # OKX: [ts, o, h, l, c, vol, volCcy, volCcyQuote, confirm]
            try:
                rows.append(
                    {
                        "ts": int(c[0]),
                        "open": float(c[1]),
                        "high": float(c[2]),
                        "low": float(c[3]),
                        "close": float(c[4]),
                        "volume": float(c[5]),
                    }
                )
            except Exception:
                continue
        df_page = pd.DataFrame(rows)
        frames.append(df_page)
        page_oldest = int(df_page["ts"].min())
        oldest_ts = page_oldest if oldest_ts is None else min(oldest_ts, page_oldest)
        # OKX returns newest first; paginate back using the oldest ts seen.
        after_ms = page_oldest - 1
        pages += 1
        if page_oldest <= target_start_ms:
            break
        time.sleep(SLEEP_BETWEEN_REQUESTS)

    if not frames:
        return {
            "instId": inst_id,
            "status": "no_data",
            "pages": detail_pages,
            "ok": False,
        }

    raw = pd.concat(frames, axis=0).drop_duplicates("ts", keep="last").sort_values("ts")
    raw = raw.set_index("ts")
    # Reindex onto the exact 5m UTC grid (ms -> datetime UTC).
    grid_ms = to_epoch_ms(exp_idx)
    grid_idx = pd.Index(grid_ms, name="ts")
    raw = raw.reindex(grid_idx)
    n_expected = len(exp_idx)
    raw = raw[["open", "high", "low", "close", "volume"]]
    price_vals = raw[["open", "high", "low", "close"]].to_numpy(dtype=float)
    vol_vals = raw[["volume"]].to_numpy(dtype=float)
    vals = raw.to_numpy(dtype=float)
    nan_c = int(np.isnan(vals).sum())
    finite = bool(np.isfinite(vals).all()) if nan_c == 0 else False
    # Coverage requires strictly positive PRICES; zero-volume 5m bars are legitimate
    # real market data (no trades) and must NOT fail an instrument.
    positive_prices = bool((price_vals > 0).all()) if nan_c == 0 else False
    volume_nonneg = bool((vol_vals >= 0).all()) if nan_c == 0 else False
    full_coverage = bool(nan_c == 0 and finite and positive_prices and volume_nonneg)
    min_volume = float(np.nanmin(vol_vals)) if vol_vals.size else None

    return {
        "instId": inst_id,
        "status": "ok" if full_coverage else "okx_coverage_fail",
        "pages": detail_pages,
        "n_pages": pages,
        "oldest_ts_ms": oldest_ts,
        "target_start_ms": target_start_ms,
        "bars": int(len(raw)),
        "nan_count": nan_c,
        "all_finite": finite,
        "all_prices_positive": positive_prices,
        "volume_nonneg": volume_nonneg,
        "min_volume": min_volume,
        "full_coverage": full_coverage,
        "frame": raw if full_coverage else None,
        "ok": full_coverage,
    }


def native_funding_interval_hours(series: pd.Series) -> float | None:
    """Modal spacing (hours) between native funding boundaries of a symbol.

    The C291 cache stores funding rates on the 5m grid with NaN between native
    boundaries; the non-NaN timestamps are the native funding times.  The index
    unit is read explicitly (pandas 3.x defaults to microseconds).
    """
    s = series.dropna()
    if len(s) < 2:
        return None
    idx = pd.DatetimeIndex(s.index)
    unit = getattr(idx.dtype, "unit", "ns")
    vals = idx.asi8
    if unit == "s":
        secs = vals
    elif unit == "ms":
        secs = vals // 1_000
    elif unit == "us":
        secs = vals // 1_000_000
    elif unit == "ns":
        secs = vals // 1_000_000_000
    else:
        raise RuntimeError(f"unsupported datetime unit: {unit}")
    diffs = np.diff(secs)
    diffs = diffs[diffs > 0]
    if diffs.size == 0:
        return None
    hours = np.round(diffs / 3600.0, 6)
    uniq, counts = np.unique(hours, return_counts=True)
    return float(uniq[int(np.argmax(counts))])


def load_binance_perp_universe() -> tuple[list[str], dict]:
    if not C291_PKL.exists():
        raise SystemExit(f"FATAL: C291 perp cache missing, cannot establish C293 universe: {C291_PKL}")
    with open(C291_PKL, "rb") as fh:
        payload = pickle.load(fh)
    symbols = list(payload["symbols"])
    if not symbols:
        raise SystemExit("FATAL: C291 cache has no symbols")
    closes = payload["closes"]
    funding_rates = payload["funding_rates"]
    funding_intervals = payload.get("funding_intervals_by_symbol") or {}
    if not funding_intervals:
        # C291 cache omits the field; derive each symbol's native interval from
        # the actual funding timestamps so provenance records the truth.
        funding_intervals = {s: native_funding_interval_hours(funding_rates[s]) for s in symbols}
    return symbols, {
        "closes": closes,
        "funding_rates": funding_rates,
        "funding_intervals": funding_intervals,
        "payload": payload,
    }


def _pickle_bytes(payload: dict) -> bytes:
    buf = io.BytesIO()
    pickle.dump(payload, buf, protocol=pickle.HIGHEST_PROTOCOL)
    return buf.getvalue()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--timeout", type=float, default=REQUEST_TIMEOUT)
    ap.add_argument("--workers", type=int, default=3)
    args = ap.parse_args(argv)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    CACHE.mkdir(parents=True, exist_ok=True)

    exp_start = pd.Timestamp(COMMON_START_UTC)
    exp_end = pd.Timestamp(COMMON_END_UTC)
    step = pd.Timedelta(minutes=5)
    exp_idx = pd.date_range(start=exp_start, end=exp_end, freq=step, tz="UTC")
    n_expected = len(exp_idx)
    target_start_ms = int(exp_start.timestamp() * 1000)

    binance_symbols, binance_data = load_binance_perp_universe()
    binance_closes_full = binance_data["closes"].astype(float)
    binance_funding_full = binance_data["funding_rates"].astype(float)
    binance_funding_intervals = binance_data["funding_intervals"]

    inst_for = {s: binance_to_okx(s) for s in binance_symbols}

    print(
        f"[C293] Fetching OKX funding + 5m klines for {len(binance_symbols)} symbols, "
        f"common window {COMMON_START_UTC}..{COMMON_END_UTC} ({n_expected} bars)",
        flush=True,
    )

    funding_results: dict[str, dict] = {}
    kline_results: dict[str, dict] = {}

    with ThreadPoolExecutor(max_workers=max(1, int(args.workers))) as ex:
        futs: dict = {}
        for s in binance_symbols:
            futs[ex.submit(fetch_okx_funding, inst_for[s], target_start_ms, args.timeout)] = ("funding", s)
            futs[ex.submit(fetch_okx_klines, inst_for[s], exp_idx, args.timeout)] = ("klines", s)
        for fut in as_completed(futs):
            kind, sym = futs[fut]
            try:
                res = fut.result()
            except Exception as exc:  # noqa: BLE001
                res = {
                    "instId": inst_for[sym],
                    "status": "fetch_error",
                    "error": str(exc),
                    "ok": False,
                }
            if kind == "funding":
                funding_results[sym] = res
            else:
                kline_results[sym] = res
            r = funding_results.get(sym, {}) if kind == "funding" else kline_results.get(sym, {})
            print(
                f"  [OKX] {sym} ({inst_for[sym]}): {kind} {r.get('status')} ok={r.get('ok')} "
                f"n={r.get('n_records', r.get('bars', 0))}",
                flush=True,
            )

    # Select symbols with full OKX funding coverage from COMMON_START + full OKX kline
    # coverage + full Binance coverage over the common window.
    selected: list[str] = []
    excluded: dict[str, str] = {}
    okx_instids: dict[str, str] = {}
    okx_funding_frames: dict[str, pd.DataFrame] = {}
    okx_kline_frames: dict[str, pd.DataFrame] = {}
    binance_funding_frames: dict[str, pd.Series] = {}
    binance_close_frames: dict[str, pd.Series] = {}

    for sym in binance_symbols:
        okx_instids[sym] = inst_for[sym]
        fr = funding_results.get(sym, {})
        kr = kline_results.get(sym, {})

        funding_ok = (
            fr.get("ok")
            and fr.get("oldest_ts_ms") is not None
            and int(fr["oldest_ts_ms"]) <= target_start_ms
            and int(fr.get("newest_ts_ms", 0)) >= int(exp_end.timestamp() * 1000)
        )
        kline_ok = bool(kr.get("ok")) and bool(kr.get("full_coverage"))

        if not funding_ok:
            excluded[sym] = (
                f"okx_funding_coverage_fail (status={fr.get('status')}, "
                f"oldest={fr.get('oldest_ts')}, newest={fr.get('newest_ts')})"
            )
            continue
        if not kline_ok:
            excluded[sym] = f"okx_kline_coverage_fail (status={kr.get('status')})"
            continue

        # Binance data: truncate to common window
        b_closes = binance_closes_full[[sym]].reindex(exp_idx)
        b_funding = binance_funding_full[[sym]].reindex(exp_idx)
        b_vals = b_closes.to_numpy(dtype=float).reshape(-1)
        b_fvals = b_funding.to_numpy(dtype=float).reshape(-1)
        b_finite_vals = b_fvals[~np.isnan(b_fvals)]
        b_ok = bool(
            np.isfinite(b_vals).all()
            and (b_vals > 0).all()
            and (b_finite_vals.size == 0 or np.isfinite(b_finite_vals).all())
        )

        if not b_ok:
            excluded[sym] = "binance_coverage_fail"
            continue

        selected.append(sym)
        okx_funding_frames[sym] = fr["frame"]
        okx_kline_frames[sym] = kr["frame"]
        binance_funding_frames[sym] = b_funding[sym]
        binance_close_frames[sym] = b_closes[sym]

    selected = sorted(selected)
    print(
        f"[C293] Selected {len(selected)} symbols, excluded {len(excluded)}: {excluded}",
        flush=True,
    )

    if len(selected) < MIN_SYMBOLS:
        raise SystemExit(
            f"FATAL: only {len(selected)} symbols have full cross-venue coverage; "
            f"need >= {MIN_SYMBOLS}. Excluded: {excluded}"
        )

    # Build frames on the common grid.
    binance_closes = pd.concat(
        {s: binance_close_frames[s].astype(float) for s in selected}, axis=1
    ).reindex(exp_idx)
    binance_funding = pd.concat(
        {s: binance_funding_frames[s].astype(float) for s in selected}, axis=1
    ).reindex(exp_idx)

    def okx_close_df(col: str) -> pd.DataFrame:
        arr = np.column_stack([okx_kline_frames[s][col].to_numpy(dtype=float) for s in selected])
        return pd.DataFrame(arr, index=exp_idx, columns=selected)

    def okx_funding_df() -> pd.DataFrame:
        # Map OKX funding times onto the common 5m grid: rate at exact funding
        # boundary bars, NaN elsewhere (cashflows apply only at native boundaries).
        result: dict[str, pd.Series] = {}
        for s in selected:
            fdf = okx_funding_frames[s]
            s_rate = fdf.set_index("fundingTime")["fundingRate"].astype(float)
            # Floor funding times to 5m so they land on grid bars exactly.
            s_rate.index = s_rate.index.floor("5min")
            reindexed = s_rate.reindex(exp_idx)
            result[s] = reindexed
        return pd.DataFrame(result, index=exp_idx)

    okx_closes = okx_close_df("close")
    okx_funding = okx_funding_df()

    # Validate all frames: shape, no NaN, finite, positive prices.
    for name, df in [("binance_closes", binance_closes), ("okx_closes", okx_closes)]:
        vals = df.to_numpy(dtype=float)
        if df.shape != (n_expected, len(selected)):
            raise SystemExit(f"FATAL: {name} shape {df.shape} != {(n_expected, len(selected))}")
        if int(np.isnan(vals).sum()) != 0:
            raise SystemExit(f"FATAL: {name} contains NaNs")
        if not bool(np.isfinite(vals).all()):
            raise SystemExit(f"FATAL: {name} contains non-finite values")
        if not bool((vals > 0).all()):
            raise SystemExit(f"FATAL: {name} contains non-positive prices")

    n_bars = n_expected

    payload = {
        "campaign": 293,
        "part": "data",
        "interval": INTERVAL,
        "symbols": selected,
        "okx_instids": {s: inst_for[s] for s in selected},
        "window_start_utc": COMMON_START_UTC,
        "window_end_utc": COMMON_END_UTC,
        "n_bars": n_bars,
        "binance_closes": binance_closes,
        "okx_closes": okx_closes,
        "binance_funding_rates": binance_funding,
        "okx_funding_rates": okx_funding,
        "binance_funding_intervals_by_symbol": binance_funding_intervals,
        "universe_binance": binance_symbols,
        "excluded_symbols": excluded,
    }
    OUT_PKL.write_bytes(_pickle_bytes(payload))

    pkl_sha = sha256_bytes(OUT_PKL)
    meta = {
        "generated_at_utc": ts,
        "campaign": 293,
        "part": "ingest",
        "interval": INTERVAL,
        "symbols": selected,
        "n_symbols": len(selected),
        "rows": n_bars,
        "expected_rows": n_expected,
        "window_start_utc": COMMON_START_UTC,
        "window_end_utc": COMMON_END_UTC,
        "real_data_only": True,
        "fabricated_data": False,
        "fetch_real_data_only": True,
        "fetch_fabricated_data": False,
        "source_host_binance": "data.binance.vision (verified C291 cache, reused, never relabeled)",
        "source_endpoint_binance": (
            "/data/futures/um/monthly/fundingRate/<SYM>/<SYM>-fundingRate-YYYY-MM.zip "
            "+ klines (verified C291 cache)"
        ),
        "source_host_okx": OKX_HOST,
        "source_endpoint_okx_funding": OKX_FUNDING_ENDPOINT,
        "source_endpoint_okx_klines": OKX_KLINE_ENDPOINT,
        "okx_bar": OKX_BAR,
        "okx_limit": OKX_LIMIT,
        "common_window_rule": (
            "Pre-registered common window 2026-08-10T00:00Z..2026-10-30T23:55Z; a symbol is retained only if "
            "OKX funding covers from 2026-08-10 and OKX klines + Binance data cover the full window."
        ),
        "sha256_from_bytes": pkl_sha,
        "pkl_path": str(OUT_PKL.relative_to(ROOT)),
    }
    OUT_META.write_text(json.dumps(meta, indent=2) + "\n")

    per_symbol: dict[str, dict] = {}
    for s in binance_symbols:
        fr = funding_results.get(s, {})
        kr = kline_results.get(s, {})
        per_symbol[s] = {
            "binance_symbol": s,
            "okx_inst_id": inst_for[s],
            "binance_full_coverage": True,
            "okx_funding_status": fr.get("status"),
            "okx_funding_ok": bool(fr.get("ok")),
            "okx_funding_n_records": fr.get("n_records"),
            "okx_funding_oldest_ts": fr.get("oldest_ts"),
            "okx_funding_newest_ts": fr.get("newest_ts"),
            "okx_funding_n_pages": fr.get("n_pages"),
            "okx_kline_status": kr.get("status"),
            "okx_kline_ok": bool(kr.get("ok")),
            "okx_kline_bars": kr.get("bars"),
            "okx_kline_nan_count": kr.get("nan_count"),
            "okx_kline_full_coverage": bool(kr.get("full_coverage")),
            "selected": s in selected,
            "excluded_reason": excluded.get(s),
        }

    provenance = {
        "generated_at_utc": ts,
        "campaign": 293,
        "part": "provenance",
        "real_data_only": True,
        "fabricated_data": False,
        "mechanism": "cross_venue_perp_funding_carry_stat_arb",
        "universe_rule": (
            "Binance USDT-M perp universe (24 symbols from verified C291 cache). OKX USDT-M perp funding-rate "
            "history is fetched from www.okx.com/api/v5/public/funding-rate-history "
            "(instId=<SYM>-USDT-SWAP, paginated with after=<fundingTime_ms>, browser User-Agent). "
            "OKX perp 5m klines are fetched from www.okx.com/api/v5/market/history-candles "
            "(instId=<SYM>-USDT-SWAP, bar=5m, paginated with after=<ms>). "
            "A symbol is retained only if BOTH venues have full coverage over the pre-registered "
            "common window 2026-08-10T00:00Z..2026-10-30T23:55Z with zero NaNs, finite positive prices. "
            "Symbols with any gap, 404, or partial history are excluded fail-closed with a recorded reason. "
            "Binance frames are the verified C291 cache (referenced, never copied/relabeled). Funding is aligned "
            "on each symbol's native funding boundary (OKX 8h; Binance 8h/4h per symbol) and forward-filled to "
            "the 5m grid for features; funding cashflows apply only at native boundary bars."
        ),
        "n_universe_binance": len(binance_symbols),
        "n_selected": len(selected),
        "selected_symbols": selected,
        "excluded_symbols": excluded,
        "per_symbol": per_symbol,
        "blocked_routes": {
            "fapi.binance.com": 451,
            "testnet.binance.vision": 451,
            "api.binance.com": 451,
        },
    }
    OUT_PROV.write_text(json.dumps(provenance, indent=2, default=str) + "\n")

    summary = {
        "ok": True,
        "campaign": 293,
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
        "window": {"start": COMMON_START_UTC, "end": COMMON_END_UTC},
        "selected_symbols": selected,
        "excluded_symbols": excluded,
        "overlap_rule": "full coverage on both Binance and OKX over the common window",
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
