#!/usr/bin/env python3
"""C294 — ingest REAL implied volatility (Deribit DVOL index) + real realized vol
(Binance spot 1h) for a variance-risk-premium / BTC-vs-ETH relative-value stat-arb.

C294 is a NEW economic dimension (a genuinely new asset class): real option IMPLIED
volatility, not a realized-vol proxy.  It unblocks the repo's former
`term_structure_real_iv_vol_surface` `blocked_no_real_feed` family.

Real sources (all verified reachable 2026-11-13, browser User-Agent):
- Deribit DVOL index (real 30-day constant-maturity implied vol, 1h):
    GET https://www.deribit.com/api/v2/public/get_volatility_index_data
        ?currency={BTC|ETH}&start_timestamp=<ms>&end_timestamp=<ms>&resolution=3600
    A request returns the most recent ~1000 points within [start,end]; page backward
    by moving end_timestamp to (oldest_ts - 1).  Verified contiguous hourly history
    from 2021-03-24T00:00Z (BTC & ETH, 49,462 points, zero gaps/NaN).
- Deribit historical volatility (realized-vol cross-check only, SHALLOW ~16 days):
    GET https://www.deribit.com/api/v2/public/get_historical_volatility?currency={BTC|ETH}
- Deribit option book summary (real per-strike/expiry mark IV snapshot):
    GET https://www.deribit.com/api/v2/public/get_book_summary_by_currency
        ?currency={BTC|ETH}&kind=option
- Binance BTC/ETH spot 1h closes (deep, real) for the realized-vol computation and
  the real-cashflow relative-value leg:
    GET https://data-api.binance.vision/api/v3/klines?symbol={BTCUSDT|ETHUSDT}&interval=1h

Realized vol is COMPUTED from Binance 1h closes (annualized std of 1h log returns);
the Deribit historical-vol pull is recorded as a cross-check only and is NOT the
backtest RV.  IV is genuine DVOL (`iv_definition: deribit_dvol_index`), never a
realized-vol proxy.

Persisted artifacts (all real_data_only: true, fabricated_data: false,
SHA256-from-bytes):
- data/cache/campaign294_deribit_dvol.pkl
- data/cache/campaign294_deribit_dvol.meta.json
- data/cache/campaign294_deribit_dvol.provenance.json

No synthetic data, no relabeled old caches, no forward-fill across DVOL gaps.
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
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "cache"

OUT_PKL = CACHE / "campaign294_deribit_dvol.pkl"
OUT_META = CACHE / "campaign294_deribit_dvol.meta.json"
OUT_PROV = CACHE / "campaign294_deribit_dvol.provenance.json"

DERIBIT_HOST = "https://www.deribit.com"
DVOL_ENDPOINT = "/api/v2/public/get_volatility_index_data"
HV_ENDPOINT = "/api/v2/public/get_historical_volatility"
OPT_ENDPOINT = "/api/v2/public/get_book_summary_by_currency"
BINANCE_HOST = "https://data-api.binance.vision"
BINANCE_KLINE_ENDPOINT = "/api/v3/klines"

SYMBOLS = ("BTC", "ETH")
BINANCE_SYMBOL = {"BTC": "BTCUSDT", "ETH": "ETHUSDT"}
INTERVAL = "1h"
DVOL_RESOLUTION = 3600  # seconds
ANNUALIZATION = float(24 * 365)  # 8760 hourly bars per year
HOUR_MS = 3_600_000
# DVOL verified history begins 2021-03-24T00:00Z; do not page before this floor.
DVOL_FLOOR_MS = 1_585_000_000_000  # ~2020-03-23, safety floor well before real start
# Spot 1h history is fetched from before the DVOL start so the first grid return is
# computable (log-return at bar 0 needs the prior close).
SPOT_PAD_MS = 40 * 24 * HOUR_MS

REQUEST_TIMEOUT = 30.0
MAX_DVOL_PAGES = 200
MAX_KLINE_PAGES = 400
SLEEP_BETWEEN_REQUESTS = 0.12
HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept": "application/json",
}


def sha256_bytes(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _http_get_json(url: str, timeout: float, retries: int = 6) -> dict:
    last_exc: Exception | None = None
    for attempt in range(retries):
        req = urllib.request.Request(url, method="GET", headers=HTTP_HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:  # noqa: BLE001
            if int(exc.code) == 429 and attempt < retries - 1:
                time.sleep(1.0 * (attempt + 1))
                continue
            raise RuntimeError(f"HTTP {exc.code} for {url}") from exc
        except Exception as exc:  # noqa: BLE001 transient network
            last_exc = exc
            time.sleep(0.6 * (attempt + 1))
    raise RuntimeError(f"GET failed after {retries} attempts: {url}: {last_exc}")


def to_epoch_ms(idx: pd.DatetimeIndex) -> np.ndarray:
    """Convert a UTC DatetimeIndex to integer epoch MILLISECONDS, unit-agnostic.

    pandas 3.x defaults to microsecond (datetime64[us]) resolution, so a naive
    view('int64') // 1_000_000 yields seconds, not milliseconds.  Normalise
    explicitly from the index unit.
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


def fetch_dvol(currency: str, timeout: float) -> dict:
    """Paginate Deribit DVOL backward; return a close-price Series indexed by 1h UTC.

    Returns per-page detail, coverage stats and gaps.  No forward-fill: missing
    hours stay missing (recorded).
    """
    end_ms = int(time.time() * 1000)
    closes: dict[int, float] = {}
    detail_pages: list[dict] = []
    pages = 0
    while pages < MAX_DVOL_PAGES:
        url = (
            f"{DERIBIT_HOST}{DVOL_ENDPOINT}?currency={currency}"
            f"&start_timestamp={DVOL_FLOOR_MS}&end_timestamp={end_ms}&resolution={DVOL_RESOLUTION}"
        )
        payload = _http_get_json(url, timeout)
        page = {"currency": currency, "end_ms": end_ms, "status": "ok"}
        result = payload.get("result") or {}
        data = result.get("data") if isinstance(result, dict) else None
        data = data or []
        page["rows"] = int(len(data))
        detail_pages.append(page)
        if not data:
            break
        for row in data:
            try:
                closes[int(row[0])] = float(row[4])
            except Exception:  # noqa: BLE001
                continue
        oldest = int(min(int(r[0]) for r in data))
        pages += 1
        if oldest <= DVOL_FLOOR_MS:
            break
        end_ms = oldest - 1
        time.sleep(SLEEP_BETWEEN_REQUESTS)

    if not closes:
        return {"currency": currency, "status": "no_data", "ok": False, "pages": detail_pages, "series": None}

    ts = np.array(sorted(closes), dtype=np.int64)
    vals = np.array([closes[t] for t in ts], dtype=float)
    idx = pd.to_datetime(ts, unit="ms", utc=True)
    idx.name = "timestamp_utc"
    series = pd.Series(vals, index=idx, name=currency).sort_index()
    diffs_h = np.diff(ts) / HOUR_MS
    gaps = {
        "n_points": int(len(series)),
        "span_hours": float((ts[-1] - ts[0]) / HOUR_MS),
        "expected_points": int((ts[-1] - ts[0]) / HOUR_MS) + 1,
        "n_gaps_gt_1h": int((diffs_h > 1).sum()),
        "max_gap_hours": float(diffs_h.max()) if diffs_h.size else 0.0,
        "n_nan": int(np.isnan(vals).sum()),
        "n_non_finite": int((~np.isfinite(vals)).sum()),
        "min": float(np.nanmin(vals)),
        "max": float(np.nanmax(vals)),
    }
    return {
        "currency": currency,
        "status": "ok",
        "ok": bool(gaps["n_gaps_gt_1h"] == 0 and gaps["n_nan"] == 0 and gaps["n_non_finite"] == 0),
        "n_pages": pages,
        "pages": detail_pages,
        "earliest_ts_ms": int(ts[0]),
        "latest_ts_ms": int(ts[-1]),
        "earliest": str(series.index.min()),
        "latest": str(series.index.max()),
        "gaps": gaps,
        "series": series,
    }


def fetch_deribit_hv(currency: str, timeout: float) -> dict:
    """Deribit historical volatility (SHALLOW ~16 days) — cross-check only."""
    payload = _http_get_json(f"{DERIBIT_HOST}{HV_ENDPOINT}?currency={currency}", timeout)
    rows = payload.get("result") or []
    parsed = []
    for r in rows:
        try:
            parsed.append([int(r[0]), float(r[1])])
        except Exception:  # noqa: BLE001
            continue
    if not parsed:
        return {"currency": currency, "status": "no_data", "ok": False, "rows": 0}
    ts = [p[0] for p in parsed]
    return {
        "currency": currency,
        "status": "ok",
        "ok": True,
        "rows": len(parsed),
        "earliest": str(pd.to_datetime(min(ts), unit="ms", utc=True)),
        "latest": str(pd.to_datetime(max(ts), unit="ms", utc=True)),
        "sample": parsed,
    }


def fetch_option_chain(currency: str, timeout: float) -> dict:
    """Deribit option book summary snapshot (real per-strike/expiry mark IV)."""
    payload = _http_get_json(f"{DERIBIT_HOST}{OPT_ENDPOINT}?currency={currency}&kind=option", timeout)
    rows = payload.get("result") or []
    instruments = []
    for r in rows:
        try:
            instruments.append(
                {
                    "instrument_name": r.get("instrument_name"),
                    "mark_iv": (float(r["mark_iv"]) if r.get("mark_iv") is not None else None),
                    "underlying_price": (float(r["underlying_price"]) if r.get("underlying_price") is not None else None),
                    "mid_price": (float(r["mid_price"]) if r.get("mid_price") is not None else None),
                }
            )
        except Exception:  # noqa: BLE001
            continue
    finite_iv = [x["mark_iv"] for x in instruments if x["mark_iv"] is not None and np.isfinite(x["mark_iv"])]
    return {
        "currency": currency,
        "status": "ok",
        "ok": len(instruments) > 0,
        "n_instruments": int(len(instruments)),
        "n_finite_mark_iv": int(len(finite_iv)),
        "mark_iv_min": float(np.min(finite_iv)) if finite_iv else None,
        "mark_iv_max": float(np.max(finite_iv)) if finite_iv else None,
        "retrieved_at_utc": str(datetime.now(timezone.utc)),
        "instruments": instruments,
    }


def fetch_binance_klines_1h(symbol: str, start_ms: int, timeout: float) -> dict:
    """Paginate Binance spot 1h klines forward; return close Series indexed by 1h UTC."""
    frames: list[pd.DataFrame] = []
    cursor = int(start_ms)
    pages = 0
    detail_pages: list[dict] = []
    while pages < MAX_KLINE_PAGES:
        url = (
            f"{BINANCE_HOST}{BINANCE_KLINE_ENDPOINT}?symbol={symbol}"
            f"&interval={INTERVAL}&startTime={cursor}&limit=1000"
        )
        payload = _http_get_json(url, timeout)
        rows = payload if isinstance(payload, list) else []
        page = {"symbol": symbol, "start_ms": cursor, "rows": int(len(rows))}
        detail_pages.append(page)
        if not rows:
            break
        parsed = []
        for r in rows:
            try:
                parsed.append({"ts": int(r[0]), "close": float(r[4])})
            except Exception:  # noqa: BLE001
                continue
        if not parsed:
            break
        df = pd.DataFrame(parsed)
        frames.append(df)
        last_open = int(df["ts"].max())
        pages += 1
        if len(rows) < 1000:
            break
        cursor = last_open + HOUR_MS
        time.sleep(SLEEP_BETWEEN_REQUESTS)

    if not frames:
        return {"symbol": symbol, "status": "no_data", "ok": False, "pages": detail_pages, "series": None}

    raw = pd.concat(frames, axis=0).drop_duplicates("ts", keep="last").sort_values("ts")
    raw = raw.set_index("ts")
    idx = pd.to_datetime(raw.index.values, unit="ms", utc=True)
    idx.name = "timestamp_utc"
    series = pd.Series(raw["close"].to_numpy(dtype=float), index=idx, name=symbol).sort_index()
    return {
        "symbol": symbol,
        "status": "ok",
        "ok": True,
        "n_pages": pages,
        "pages": detail_pages,
        "rows": int(len(series)),
        "earliest": str(series.index.min()),
        "latest": str(series.index.max()),
        "series": series,
    }


def _pickle_bytes(payload: dict) -> bytes:
    buf = io.BytesIO()
    pickle.dump(payload, buf, protocol=pickle.HIGHEST_PROTOCOL)
    return buf.getvalue()


def longest_finite_run(idx: pd.DatetimeIndex, finite_mask: np.ndarray) -> tuple[int, int, list[dict]]:
    """Longest run of consecutive finite bars at exact 1h spacing (no gap-fill).

    Returns (start_pos, end_pos_inclusive, dropped_runs).  Any bar that is not
    finite, or that breaks the exact 1h spacing, is excluded fail-closed.
    """
    ts = to_epoch_ms(pd.DatetimeIndex(idx))
    n = len(idx)
    runs: list[tuple[int, int]] = []
    dropped: list[dict] = []
    i = 0
    while i < n:
        if not bool(finite_mask[i]):
            j = i
            while j + 1 < n and not bool(finite_mask[j + 1]):
                j += 1
            dropped.append({"start": str(idx[i]), "end": str(idx[min(j, n - 1)]), "bars": int(j - i + 1), "reason": "non_finite"})
            i = j + 1
            continue
        j = i
        while j + 1 < n and bool(finite_mask[j + 1]) and (ts[j + 1] - ts[j]) == HOUR_MS:
            j += 1
        runs.append((i, j))
        i = j + 1
    if not runs:
        raise SystemExit("FATAL: no contiguous finite 1h run available")
    best = max(runs, key=lambda r: r[1] - r[0])
    return best[0], best[1], dropped


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--timeout", type=float, default=REQUEST_TIMEOUT)
    args = ap.parse_args(argv)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    CACHE.mkdir(parents=True, exist_ok=True)

    print("[C294] Fetching Deribit DVOL (paginated) for BTC & ETH ...", flush=True)
    dvol_results = {cur: fetch_dvol(cur, args.timeout) for cur in SYMBOLS}
    for cur, r in dvol_results.items():
        print(
            f"  [DVOL] {cur}: status={r['status']} ok={r['ok']} pages={r.get('n_pages')} "
            f"points={r['gaps']['n_points'] if r.get('series') is not None else 0} "
            f"earliest={r.get('earliest')} latest={r.get('latest')}",
            flush=True,
        )

    if not all(dvol_results[cur]["ok"] and dvol_results[cur]["series"] is not None for cur in SYMBOLS):
        raise SystemExit(f"FATAL: DVOL incomplete: {({c: dvol_results[c]['status'] for c in SYMBOLS})}")

    dvol = pd.concat({cur: dvol_results[cur]["series"] for cur in SYMBOLS}, axis=1).sort_index()
    dvol = dvol.astype(float)
    if not dvol.index.is_unique:
        raise SystemExit("FATAL: duplicate DVOL timestamps after concat")
    if int(dvol.isna().sum().sum()) != 0:
        raise SystemExit("FATAL: NaN present in aligned DVOL frame (BTC/ETH index mismatch)")
    if not bool(np.isfinite(dvol.to_numpy(dtype=float)).all()):
        raise SystemExit("FATAL: non-finite value in DVOL frame")
    if not bool((dvol.to_numpy(dtype=float) > 0).all()):
        raise SystemExit("FATAL: non-positive DVOL value")

    grid_start_ms = int(to_epoch_ms(pd.DatetimeIndex([dvol.index.min()]))[0])
    spot_start_ms = grid_start_ms - SPOT_PAD_MS
    print(
        f"[C294] DVOL grid: {dvol.index.min()} .. {dvol.index.max()} ({len(dvol)} bars). "
        f"Fetching Binance BTC/ETH 1h spot ...",
        flush=True,
    )
    spot_results = {
        cur: fetch_binance_klines_1h(BINANCE_SYMBOL[cur], spot_start_ms, args.timeout) for cur in SYMBOLS
    }
    for cur, r in spot_results.items():
        print(
            f"  [SPOT] {cur}: status={r['status']} rows={r.get('rows')} "
            f"earliest={r.get('earliest')} latest={r.get('latest')}",
            flush=True,
        )
    if not all(spot_results[cur]["ok"] and spot_results[cur]["series"] is not None for cur in SYMBOLS):
        raise SystemExit("FATAL: Binance spot 1h incomplete")

    # Reindex spot onto the DVOL grid (real closes; prior close retained for the
    # first grid return by the 40-day pad).
    spot_full = pd.concat(
        {cur: spot_results[cur]["series"].astype(float).reindex(dvol.index) for cur in SYMBOLS}, axis=1
    )
    # Restrict to the longest contiguous run where BOTH DVOL and spot are finite at
    # exact 1h spacing (no forward-fill; dropped bars recorded fail-closed).
    finite_mask = np.isfinite(dvol.to_numpy(dtype=float)).all(axis=1) & np.isfinite(
        spot_full.to_numpy(dtype=float)
    ).all(axis=1)
    s0, s1, dropped_runs = longest_finite_run(dvol.index, finite_mask)
    dvol = dvol.iloc[s0 : s1 + 1]
    spot = spot_full.iloc[s0 : s1 + 1]
    if not dvol.index.equals(spot.index):
        raise SystemExit("FATAL: DVOL/spot index mismatch after run selection")
    if int(dvol.isna().sum().sum()) != 0 or int(spot.isna().sum().sum()) != 0:
        raise SystemExit("FATAL: NaN in DVOL/spot after run selection")
    if not bool(np.isfinite(spot.to_numpy(dtype=float)).all()):
        raise SystemExit("FATAL: non-finite spot close on grid")
    if not bool((spot.to_numpy(dtype=float) > 0).all()):
        raise SystemExit("FATAL: non-positive spot close on grid")

    # Realized vol is derived in the runner from these real closes; verify it is
    # finite for both assets over the post-warmup region here (no gap-fill).
    logret = np.log(spot).diff()
    rv_ref = logret.rolling(720, min_periods=240).std() * float(np.sqrt(ANNUALIZATION))
    rv_finite_both = bool(np.isfinite(rv_ref.to_numpy(dtype=float)[240:]).all())
    if not rv_finite_both:
        raise SystemExit("FATAL: realized vol (L=720) not finite for both assets post-warmup")
    print(
        f"[C294] Analysis grid: {dvol.index.min()} .. {dvol.index.max()} ({len(dvol)} bars); "
        f"dropped {len(dropped_runs)} non-finite run(s): {dropped_runs}",
        flush=True,
    )

    # Recorded cross-checks (shallow Deribit HV + option book snapshot).
    hv = {cur: fetch_deribit_hv(cur, args.timeout) for cur in SYMBOLS}
    opt = {cur: fetch_option_chain(cur, args.timeout) for cur in SYMBOLS}
    for cur in SYMBOLS:
        print(
            f"  [XCHECK] {cur}: HV rows={hv[cur].get('rows')} options={opt[cur].get('n_instruments')}",
            flush=True,
        )

    n_bars = int(len(dvol))
    payload = {
        "campaign": 294,
        "part": "data",
        "interval": INTERVAL,
        "symbols": list(SYMBOLS),
        "iv_definition": "deribit_dvol_index",
        "rv_definition": "annualized_std_of_1h_log_returns_times_sqrt_8760",
        "annualization": ANNUALIZATION,
        "window_start_utc": str(dvol.index.min()),
        "window_end_utc": str(dvol.index.max()),
        "n_bars": n_bars,
        "dvol": dvol,
        "spot_closes": spot,
        "dvol_gaps": {cur: dvol_results[cur]["gaps"] for cur in SYMBOLS},
        "dvol_pages": {cur: dvol_results[cur].get("n_pages") for cur in SYMBOLS},
        "dropped_bars": dropped_runs,
        "deribit_hv": hv,
        "option_chain": opt,
        "real_data_only": True,
        "fabricated_data": False,
    }
    OUT_PKL.write_bytes(_pickle_bytes(payload))

    pkl_sha = sha256_bytes(OUT_PKL)
    meta = {
        "generated_at_utc": ts,
        "campaign": 294,
        "part": "ingest",
        "interval": INTERVAL,
        "symbols": list(SYMBOLS),
        "n_symbols": len(SYMBOLS),
        "rows": n_bars,
        "expected_rows": n_bars,
        "window_start_utc": str(dvol.index.min()),
        "window_end_utc": str(dvol.index.max()),
        "real_data_only": True,
        "fabricated_data": False,
        "fetch_real_data_only": True,
        "fetch_fabricated_data": False,
        "iv_definition": "deribit_dvol_index",
        "rv_definition": "annualized_std_of_1h_log_returns_times_sqrt_8760",
        "rv_source": "binance_spot_1h_closes (data-api.binance.vision/api/v3/klines)",
        "source_host_deribit": DERIBIT_HOST,
        "source_endpoint_dvol": DVOL_ENDPOINT,
        "source_endpoint_hv": HV_ENDPOINT,
        "source_endpoint_option": OPT_ENDPOINT,
        "source_host_binance": BINANCE_HOST,
        "source_endpoint_binance": BINANCE_KLINE_ENDPOINT,
        "dvol_pages": {cur: dvol_results[cur].get("n_pages") for cur in SYMBOLS},
        "dvol_earliest": {cur: dvol_results[cur].get("earliest") for cur in SYMBOLS},
        "dvol_latest": {cur: dvol_results[cur].get("latest") for cur in SYMBOLS},
        "dvol_gaps": {cur: dvol_results[cur]["gaps"] for cur in SYMBOLS},
        "dropped_bars": dropped_runs,
        "n_dropped_bars": int(sum(d["bars"] for d in dropped_runs)),
        "sha256_from_bytes": pkl_sha,
        "pkl_path": str(OUT_PKL.relative_to(ROOT)),
    }
    OUT_META.write_text(json.dumps(meta, indent=2) + "\n")

    provenance = {
        "generated_at_utc": ts,
        "campaign": 294,
        "part": "provenance",
        "real_data_only": True,
        "fabricated_data": False,
        "mechanism": "real_implied_vol_variance_risk_premium_and_btc_eth_relative_value_stat_arb",
        "universe_rule": (
            "Real Deribit DVOL index (30-day constant-maturity implied vol, 1h) for BTC and ETH, paginated "
            "backward (1000 points/request) over the full contiguous history from 2021-03-24T00:00Z. "
            "Realized vol is computed from real Binance BTC/ETH spot 1h closes "
            "(data-api.binance.vision/api/v3/klines). Deribit get_historical_volatility (~16d, shallow) is a "
            "recorded cross-check only, never the backtest RV. IV is genuine implied volatility "
            "(iv_definition=deribit_dvol_index), not a realized-vol proxy. No forward-fill across gaps."
        ),
        "n_assets": len(SYMBOLS),
        "assets": list(SYMBOLS),
        "window": {"start": str(dvol.index.min()), "end": str(dvol.index.max())},
        "bars": n_bars,
        "dvol_contiguous": {cur: dvol_results[cur]["gaps"] for cur in SYMBOLS},
        "dropped_bars": dropped_runs,
        "deribit_hv_crosscheck": {cur: {k: hv[cur].get(k) for k in ("rows", "earliest", "latest")} for cur in SYMBOLS},
        "option_chain_snapshot": {cur: {k: opt[cur].get(k) for k in ("n_instruments", "n_finite_mark_iv", "mark_iv_min", "mark_iv_max")} for cur in SYMBOLS},
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
        "campaign": 294,
        "real_data_only": True,
        "fabricated_data": False,
        "pkl": str(OUT_PKL.relative_to(ROOT)),
        "pkl_sha256": pkl_sha,
        "meta": str(OUT_META.relative_to(ROOT)),
        "meta_sha256": sha256_bytes(OUT_META),
        "provenance": str(OUT_PROV.relative_to(ROOT)),
        "provenance_sha256": sha256_bytes(OUT_PROV),
        "n_symbols": len(SYMBOLS),
        "n_bars": n_bars,
        "window": {"start": str(dvol.index.min()), "end": str(dvol.index.max())},
        "dvol_contiguous": {cur: dvol_results[cur]["gaps"] for cur in SYMBOLS},
        "dropped_bars": dropped_runs,
        "iv_definition": "deribit_dvol_index",
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())