#!/usr/bin/env python3
"""C298 — ingest REAL USDT-M perpetual futures 5m klines + funding rates over the
deep multi-year archive (2020-01 .. 2026-10, full monthly calendar months) and the
real spot leg for the spot/perp basis feature.

C298 tests the C291/C293 funding-carry + spot/perp basis cross-sectional stat-arb
family across 2020-2026 multi-regime history.  This is the data step.  It fetches
REAL mainnet public Binance USDT-M futures archives (NOT the fapi REST API, which
is HTTP 451 from this egress) from the public-data archive host
``data.binance.vision``:

- ``data/futures/um/monthly/klines/<SYM>/5m/<SYM>-5m-YYYY-MM.zip``
  columns: open_time, open, high, low, close, volume, close_time, quote_volume,
  count, taker_buy_volume, taker_buy_quote_volume, ignore
- ``data/futures/um/monthly/fundingRate/<SYM>/<SYM>-fundingRate-YYYY-MM.zip``
  columns: calc_time, funding_interval_hours, last_funding_rate  (8h interval,
  4h where applicable; real data)

and the spot leg from ``data-api.binance.vision/api/v3/klines`` (1h candles over
the same window, paginated).

The 5m perp klines are resampled to 1h OHLCV (open=first, high=max, low=min,
close=last, volume=sum) and reindexed on the exact 1h UTC grid.  Funding is
floored to each row's native Binance funding boundary and reindexed onto the 1h
grid (value only at native boundary hours, NaN elsewhere).  Only symbols with
EXACT full coverage over the whole window are eligible; any symbol whose perp
kline or funding archive is missing/blocked/partial in any month is excluded with
a recorded reason (never silently, never imputed).

Persisted artifacts (all ``real_data_only: true``, ``fabricated_data: false``,
SHA256-from-bytes):

- ``data/cache/campaign298_multianual_perp_funding_basis.pkl``  (1h perp OHLCV +
  spot closes + funding frames)
- ``data/cache/campaign298_multianual_perp_funding_basis.meta.json``
- ``data/cache/campaign298_multianual_perp_funding_basis.provenance.json``

No synthetic data, no relabeled old caches, no resampling of a derived series,
no forward/back fill, no imputation.
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
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from data.real_feed_loader import fetch_spot_ohlcv_klines  # noqa: E402

CACHE = ROOT / "data" / "cache"
OUT_PKL = CACHE / "campaign298_multianual_perp_funding_basis.pkl"
OUT_META = CACHE / "campaign298_multianual_perp_funding_basis.meta.json"
OUT_PROV = CACHE / "campaign298_multianual_perp_funding_basis.provenance.json"

ARCHIVE_HOST = "https://data.binance.vision"
START_UTC = "2020-01-01T00:00:00Z"
# 2026-11 returns 404 on the archive (incomplete month); the window ends at the
# last complete monthly archive, 2026-10-31T23:00:00Z on the 1h grid.
END_UTC = "2026-10-31T23:00:00Z"
SOURCE_INTERVAL = "5m"
TARGET_INTERVAL = "1h"
ONE_HOUR = pd.Timedelta(hours=1)
STALE_BARS = 24 + 1  # 24h + 1 bar on the 1h grid
MIN_FUNDING_ROWS = 90
VALID_FUNDING_INTERVALS = {1, 2, 4, 8}

# Candidate USDT-M perps with archive history from 2020-01 (verified 200).
# BSVUSDT/DOTUSDT/XTZUSDT return 404 for 2020-01 and are not candidates.
CANDIDATES = (
    "BTCUSDT",
    "ETHUSDT",
    "XRPUSDT",
    "BCHUSDT",
    "LTCUSDT",
    "EOSUSDT",
    "TRXUSDT",
    "ADAUSDT",
    "LINKUSDT",
)
MIN_SELECTED = 2  # at least a long/short cross-section


def _months() -> list[str]:
    stamps = pd.date_range(start="2020-01-01", end="2026-10-01", freq="MS", tz="UTC")
    return [str(ts.date())[:7] for ts in stamps]


def sha256_bytes(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expected_index() -> pd.DatetimeIndex:
    return pd.DatetimeIndex(
        pd.date_range(start=pd.Timestamp(START_UTC), end=pd.Timestamp(END_UTC), freq="1h", tz="UTC")
    )


def expected_5m_index() -> pd.DatetimeIndex:
    return pd.DatetimeIndex(
        pd.date_range(start=pd.Timestamp(START_UTC), end=pd.Timestamp(END_UTC), freq="5min", tz="UTC")
    )


def kline_url(symbol: str, month: str) -> str:
    return f"{ARCHIVE_HOST}/data/futures/um/monthly/klines/{symbol}/5m/{symbol}-5m-{month}.zip"


def funding_url(symbol: str, month: str) -> str:
    return f"{ARCHIVE_HOST}/data/futures/um/monthly/fundingRate/{symbol}/{symbol}-fundingRate-{month}.zip"


def _http_get(url: str, timeout: float, retries: int = 3) -> tuple[int, bytes]:
    last_exc: Exception | None = None
    for attempt in range(retries):
        req = urllib.request.Request(url, method="GET", headers={"User-Agent": "kilo-c298-ingest"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return int(resp.status), resp.read()
        except urllib.error.HTTPError as exc:  # 404/451 etc: do not retry
            return int(exc.code), b""
        except Exception as exc:  # noqa: BLE001  transient network: retry
            last_exc = exc
            time.sleep(0.6 * (attempt + 1))
    raise RuntimeError(f"GET failed after {retries} attempts: {url}: {last_exc}")


KLINE_COLUMNS = [
    "open_time", "open", "high", "low", "close", "volume", "close_time",
    "quote_volume", "count", "taker_buy_volume", "taker_buy_quote_volume", "ignore",
]


def read_zip_csv(zip_bytes: bytes, kind: str = "klines") -> pd.DataFrame:
    zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    name = zf.namelist()[0]
    raw = zf.read(name)
    if kind == "funding":
        return pd.read_csv(io.BytesIO(raw))
    df = pd.read_csv(io.BytesIO(raw), header=None, names=KLINE_COLUMNS)
    # Some archive months embed a header row ("open_time,open,...") as the first
    # data row; drop it if present.
    if len(df) and str(df["open_time"].iloc[0]) == "open_time":
        df = df.iloc[1:].reset_index(drop=True)
    df["open_time"] = pd.to_numeric(df["open_time"], errors="coerce")
    df = df.dropna(subset=["open_time"])
    for c in ("open", "high", "low", "close", "volume"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def fetch_kline_month(symbol: str, month: str, timeout: float) -> dict:
    url = kline_url(symbol, month)
    status, data = _http_get(url, timeout)
    if status != 200:
        return {"symbol": symbol, "month": month, "kind": "klines", "url": url, "status": status, "rows": 0, "ok": False}
    df = read_zip_csv(data, kind="klines")
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    return {"symbol": symbol, "month": month, "kind": "klines", "url": url, "status": status, "rows": int(len(df)), "ok": True, "frame": df}


def fetch_funding_month(symbol: str, month: str, timeout: float) -> dict:
    url = funding_url(symbol, month)
    status, data = _http_get(url, timeout)
    if status != 200:
        return {"symbol": symbol, "month": month, "kind": "funding", "url": url, "status": status, "rows": 0, "ok": False}
    df = read_zip_csv(data, kind="funding")
    # Binance `calc_time` is the funding boundary + 1 ms; floor each row to its OWN
    # native funding interval (8h for most perps, 4h for some).
    ct = pd.to_datetime(df["calc_time"], unit="ms", utc=True)
    df["boundary"] = pd.Series([t.floor(f"{int(h)}h") for t, h in zip(ct, df["funding_interval_hours"])], index=df.index)
    return {"symbol": symbol, "month": month, "kind": "funding", "url": url, "status": status, "rows": int(len(df)), "ok": True, "frame": df}


def build_symbol(symbol: str, months: list[str], exp_idx: pd.DatetimeIndex, exp_5m: pd.DatetimeIndex, timeout: float) -> dict:
    """Fetch all months for one symbol and assemble aligned 1h perp OHLCV + funding."""
    per_month = []
    for m in months:
        k = fetch_kline_month(symbol, m, timeout)
        f = fetch_funding_month(symbol, m, timeout)
        per_month.extend([k, f])

    kline_ok = all(p["ok"] for p in per_month if p["kind"] == "klines")
    funding_ok = all(p["ok"] for p in per_month if p["kind"] == "funding")
    first_bad = next((p for p in per_month if not p["ok"]), None)
    detail = {
        "symbol": symbol,
        "kline_ok": kline_ok,
        "funding_ok": funding_ok,
        "per_month": [
            {k2: p[k2] for k2 in ("month", "kind", "status", "rows", "ok", "url")} for p in per_month
        ],
    }
    if not (kline_ok and funding_ok):
        detail["status"] = "excluded"
        detail["exclusion_reason"] = (
            f"month {first_bad['month']} {first_bad['kind']} status {first_bad['status']}"
            if first_bad is not None else "unknown"
        )
        return detail

    kframes = [p["frame"] for p in per_month if p["kind"] == "klines"]
    kdf = pd.concat(kframes, axis=0).sort_values("open_time").drop_duplicates("open_time", keep="last")
    kdf = kdf.set_index("open_time")
    kdf = kdf.loc[(kdf.index >= pd.Timestamp(START_UTC)) & (kdf.index <= pd.Timestamp(END_UTC))]
    kdf = kdf.reindex(exp_5m)
    kline_nan = int(kdf[["open", "high", "low", "close", "volume"]].isna().sum().sum())
    finite = bool(np.isfinite(kdf[["open", "high", "low", "close", "volume"]].to_numpy(dtype=float)).all()) if kline_nan == 0 else False
    positive_px = bool((kdf[["open", "high", "low", "close"]].to_numpy(dtype=float) > 0).all()) if kline_nan == 0 else False
    volume_ok = bool((kdf["volume"].to_numpy(dtype=float) >= 0).all()) if kline_nan == 0 else False
    if not (kline_nan == 0 and finite and positive_px and volume_ok):
        detail["status"] = "excluded"
        detail["exclusion_reason"] = f"5m kline coverage fail (nan={kline_nan}, finite={finite}, pos_px={positive_px}, vol_ok={volume_ok})"
        return detail

    # resample 5m -> 1h OHLCV on the exact 1h grid
    ohlc = kdf[["open", "high", "low", "close"]].resample("1h").agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    vol = kdf["volume"].resample("1h").sum()
    h1 = pd.concat([ohlc, vol.rename("volume")], axis=1)
    h1 = h1.reindex(exp_idx)
    h1_nan = int(h1.isna().sum().sum())
    h1_finite = bool(np.isfinite(h1.to_numpy(dtype=float)).all()) if h1_nan == 0 else False
    h1_positive_px = bool((h1[["open", "high", "low", "close"]].to_numpy(dtype=float) > 0).all()) if h1_nan == 0 else False
    h1_volume_ok = bool((h1["volume"].to_numpy(dtype=float) >= 0).all()) if h1_nan == 0 else False
    if not (h1_nan == 0 and h1_finite and h1_positive_px and h1_volume_ok):
        detail["status"] = "excluded"
        detail["exclusion_reason"] = f"1h resample coverage fail (nan={h1_nan}, finite={h1_finite}, pos_px={h1_positive_px}, vol_ok={h1_volume_ok})"
        return detail

    fframes = [p["frame"] for p in per_month if p["kind"] == "funding"]
    fdf = pd.concat(fframes, axis=0)
    fdf = fdf.drop_duplicates("boundary", keep="last").sort_values("boundary").set_index("boundary")
    fr = fdf["last_funding_rate"].reindex(exp_idx)  # value only at native boundary hours
    funding_rows = int(fr.notna().sum())
    intervals = sorted(int(x) for x in pd.unique(fdf["funding_interval_hours"]))
    vals = fr.dropna()
    finite = bool(np.isfinite(vals.to_numpy(dtype=float)).all()) if len(vals) else False
    pos = np.where(fr.notna().values)[0]
    gap = int(np.diff(pos).max()) if len(pos) > 1 else 0
    tail_gap = int(len(exp_idx) - 1 - pos[-1]) if len(pos) else int(len(exp_idx))
    stale_ok = gap <= STALE_BARS and tail_gap <= STALE_BARS
    funding_ok_shape = funding_rows >= MIN_FUNDING_ROWS and finite and set(intervals).issubset(VALID_FUNDING_INTERVALS) and stale_ok
    if not funding_ok_shape:
        detail["status"] = "excluded"
        detail["exclusion_reason"] = f"funding coverage fail (rows={funding_rows}, finite={finite}, intervals={intervals}, max_gap={gap}, tail_gap={tail_gap})"
        return detail

    detail.update({
        "status": "ok",
        "bars": int(len(h1)),
        "kline_nan": kline_nan,
        "h1_nan": h1_nan,
        "full_coverage": True,
        "funding_rows": funding_rows,
        "funding_interval_hours": intervals,
        "funding_max_gap_bars": gap,
        "funding_tail_gap_bars": tail_gap,
        "stale_ok": stale_ok,
    })
    detail["opens"] = h1["open"].astype(float)
    detail["highs"] = h1["high"].astype(float)
    detail["lows"] = h1["low"].astype(float)
    detail["closes"] = h1["close"].astype(float)
    detail["volumes"] = h1["volume"].astype(float)
    detail["funding_rates"] = fr.astype(float)
    return detail


def load_universe() -> list[str]:
    return list(CANDIDATES)


def _pickle_bytes(payload: dict) -> bytes:
    buf = io.BytesIO()
    pickle.dump(payload, buf, protocol=pickle.HIGHEST_PROTOCOL)
    return buf.getvalue()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--timeout", type=float, default=60.0)
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args(argv)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    CACHE.mkdir(parents=True, exist_ok=True)

    universe = load_universe()
    months = _months()
    exp_idx = expected_index()
    exp_5m = expected_5m_index()
    n_expected = int(len(exp_idx))

    built: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = [pool.submit(build_symbol, s, months, exp_idx, exp_5m, args.timeout) for s in universe]
        for fut in futures:
            d = fut.result()
            built[d["symbol"]] = d

    selected = [s for s in universe if built[s].get("status") == "ok"]
    excluded = {s: built[s].get("exclusion_reason", built[s].get("status")) for s in universe if built[s].get("status") != "ok"}

    if len(selected) < MIN_SELECTED:
        raise SystemExit(
            f"FATAL: only {len(selected)} symbols have full perp kline+funding coverage over "
            f"{START_UTC}..{END_UTC}; need >= {MIN_SELECTED}. Excluded: {excluded}"
        )

    # spot leg for the basis feature: real spot 1h klines from data-api.binance.vision
    spot_hosts = ["https://data-api.binance.vision"]
    spot_frames, spot_prov = fetch_spot_ohlcv_klines(selected, START_UTC, END_UTC, interval=TARGET_INTERVAL, timeout=40.0, page_limit=1000, max_workers=max(1, args.workers), hosts=spot_hosts)
    missing_spot = [s for s in selected if s not in spot_frames]
    if missing_spot:
        raise SystemExit(f"FATAL: spot leg missing symbols: {missing_spot}; provenance={spot_prov}")
    spot_closes_wide: dict[str, pd.Series] = {}
    spot_gaps: dict[str, list[str]] = {}
    for s in selected:
        fr = spot_frames[s]
        if not bool(fr.index.isin(exp_idx).all()):
            raise SystemExit(f"FATAL: spot frame for {s} contains hours outside the window")
        px = fr[["open", "high", "low", "close"]]
        px_nna = px.dropna()
        if int(px_nna.isna().sum().sum()) != 0 or not bool(np.isfinite(px_nna.to_numpy(dtype=float)).all()) or not bool((px_nna.to_numpy(dtype=float) > 0).all()):
            raise SystemExit(f"FATAL: spot price frame for {s} has NaN/non-finite/non-positive values")
        if not bool((fr["volume"].dropna().to_numpy(dtype=float) >= 0).all()):
            raise SystemExit(f"FATAL: spot volume frame for {s} has negative values")
        spot_closes_wide[s] = fr["close"].astype(float)
        spot_gaps[s] = [str(t) for t in exp_idx.difference(fr.index)]

    def wide(field: str) -> pd.DataFrame:
        return pd.concat({s: built[s][field] for s in selected}, axis=1).reindex(exp_idx).astype(float)

    opens = wide("opens")
    highs = wide("highs")
    lows = wide("lows")
    closes = wide("closes")
    volumes = wide("volumes")
    funding_rates = wide("funding_rates")
    spot_closes = pd.concat(spot_closes_wide, axis=1)[selected].reindex(exp_idx).astype(float)

    n_bars = int(len(exp_idx))
    shape = (n_bars, len(selected))
    for name, df in (("opens", opens), ("highs", highs), ("lows", lows), ("closes", closes), ("volumes", volumes), ("spot_closes", spot_closes), ("funding_rates", funding_rates)):
        if df.shape != shape:
            raise SystemExit(f"FATAL: aligned {name} shape {df.shape} != {shape}")

    payload = {
        "interval": TARGET_INTERVAL,
        "symbols": selected,
        "window_start_utc": START_UTC,
        "window_end_utc": END_UTC,
        "n_bars": n_bars,
        "source_interval": SOURCE_INTERVAL,
        "opens": opens,
        "highs": highs,
        "lows": lows,
        "closes": closes,
        "volumes": volumes,
        "spot_closes": spot_closes,
        "funding_rates": funding_rates,
    }
    OUT_PKL.write_bytes(_pickle_bytes(payload))

    pkl_sha = sha256_bytes(OUT_PKL)
    meta = {
        "generated_at_utc": ts,
        "campaign": 298,
        "part": "ingest",
        "interval": TARGET_INTERVAL,
        "source_interval": SOURCE_INTERVAL,
        "symbols": selected,
        "n_symbols": len(selected),
        "rows": n_bars,
        "expected_bars": n_expected,
        "columns_per_frame": ["open", "high", "low", "close", "volume"],
        "spot_column": "close",
        "funding_column": "funding_rates",
        "window_start_utc": START_UTC,
        "window_end_utc": END_UTC,
        "real_data_only": True,
        "fabricated_data": False,
        "fetch_real_data_only": True,
        "fetch_fabricated_data": False,
        "source_host": ARCHIVE_HOST,
        "spot_host": "https://data-api.binance.vision",
        "kline_endpoint": "/data/futures/um/monthly/klines/<SYM>/5m/<SYM>-5m-YYYY-MM.zip",
        "funding_endpoint": "/data/futures/um/monthly/fundingRate/<SYM>/<SYM>-fundingRate-YYYY-MM.zip",
        "spot_endpoint": "/api/v3/klines",
        "months": months,
        "n_months": len(months),
        "funding_intervals_by_symbol": {s: built[s].get("funding_interval_hours") for s in selected},
        "sha256_from_bytes": pkl_sha,
        "pkl_path": str(OUT_PKL.relative_to(ROOT)),
    }
    OUT_META.write_text(json.dumps(meta, indent=2) + "\n")

    per_symbol = {
        s: {
            "status": built[s]["status"],
            "exclusion_reason": built[s].get("exclusion_reason"),
            "bars": built[s].get("bars"),
            "kline_nan": built[s].get("kline_nan"),
            "h1_nan": built[s].get("h1_nan"),
            "full_coverage": built[s].get("full_coverage"),
            "funding_rows": built[s].get("funding_rows"),
            "funding_interval_hours": built[s].get("funding_interval_hours"),
            "funding_max_gap_bars": built[s].get("funding_max_gap_bars"),
            "funding_tail_gap_bars": built[s].get("funding_tail_gap_bars"),
            "stale_ok": built[s].get("stale_ok"),
        }
        for s in universe
    }
    spot_per_symbol = {
        s: {
            "bars": int(spot_frames[s].shape[0]),
            "index_subset_of_expected": bool(spot_frames[s].index.isin(exp_idx).all()),
            "gap_hours": len(spot_gaps[s]),
            "gap_hours_first": spot_gaps[s][0] if spot_gaps[s] else None,
            "gap_hours_last": spot_gaps[s][-1] if spot_gaps[s] else None,
        }
        for s in selected
    }
    provenance = {
        "generated_at_utc": ts,
        "campaign": 298,
        "part": "provenance",
        "real_data_only": True,
        "fabricated_data": False,
        "universe_rule": (
            "Candidates are USDT-M perps with archive history from 2020-01 (verified HTTP 200 on "
            "data.binance.vision). Every candidate must have full klines+funding coverage for every "
            "calendar month 2020-01..2026-10; any month missing/blocked/partial excludes the symbol "
            "with a recorded reason. 5m klines are truncated to the exact window and resampled to 1h "
            "OHLCV on the exact 1h UTC grid; funding calc_time is floored to its native Binance "
            "funding boundary (8h for most perps, 4h for some; recorded per symbol) and placed on the "
            "1h grid at boundary hours only. The spot leg is real spot 1h klines from "
            "data-api.binance.vision/api/v3/klines over the same window; spot feed gaps are NOT "
            "imputed: they are recorded per symbol and the runner's fail-closed gates block any trade "
            "requiring missing spot data. No impute/ffill/resample of derived series."
        ),
        "n_candidates": len(universe),
        "n_selected": len(selected),
        "selected_symbols": selected,
        "excluded_symbols": excluded,
        "per_symbol": per_symbol,
        "spot_per_symbol": spot_per_symbol,
        "spot_gap_hours_by_symbol": spot_gaps,
        "spot_leg_provenance": spot_prov,
        "months": months,
        "n_months": len(months),
        "window": {"start": START_UTC, "end": END_UTC},
        "interval": TARGET_INTERVAL,
    }
    OUT_PROV.write_text(json.dumps(provenance, indent=2, default=str) + "\n")

    summary = {
        "ok": True,
        "campaign": 298,
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
        "expected_bars": n_expected,
        "window": {"start": START_UTC, "end": END_UTC},
        "interval": TARGET_INTERVAL,
        "selected_symbols": selected,
        "excluded_symbols": excluded,
        "funding_rows_total": int(funding_rates.notna().sum().sum()),
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
