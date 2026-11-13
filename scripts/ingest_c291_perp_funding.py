#!/usr/bin/env python3
"""C291 — ingest REAL USDT-M perpetual futures 5m klines + 8h funding rates.

C291 is a NEW economic dimension (derivatives): cross-sectional statistical
arbitrage on USDT-M perpetual futures with real funding cashflows and spot/perp
basis.  This is the data step.  It fetches REAL mainnet public Binance USDT-M
futures archives (NOT the fapi REST API, which is HTTP 451 from this egress) from
the public-data archive host ``data.binance.vision``:

- ``data/futures/um/monthly/klines/<SYM>/5m/<SYM>-5m-YYYY-MM.zip``
  columns: open_time, open, high, low, close, volume, close_time, quote_volume,
  count, taker_buy_volume, taker_buy_quote_volume, ignore
- ``data/futures/um/monthly/fundingRate/<SYM>/<SYM>-fundingRate-YYYY-MM.zip``
  columns: calc_time, funding_interval_hours, last_funding_rate  (8h interval)

For the C290 spot symbols (26), the USDT-M perp archives are probed; symbols whose
perp archives 404 (recorded) are excluded.  The expected result is the 24-perp
universe (C290 spot symbols minus ``PEPEUSDT`` and ``UUSDT``).

The already-verified real C290 spot 5m cache is NOT copied or relabeled here: the
spot leg is only referenced by the runner for the basis feature.

Persisted artifacts (all ``real_data_only: true``, ``fabricated_data: false``,
SHA256-from-bytes):

- ``data/cache/campaign291_perp_5m.pkl``          (perp OHLCV + funding frames)
- ``data/cache/campaign291_perp_5m.meta.json``
- ``data/cache/campaign291_perp_5m.provenance.json``

No synthetic data, no relabeled old caches, no resampling.  Klines are truncated to
the exact window and reindexed on the exact 5m UTC grid; funding is floored to its
8h boundary.
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
CACHE = ROOT / "data" / "cache"
META_290 = CACHE / "campaign290_ohlcv.meta.json"

OUT_PKL = CACHE / "campaign291_perp_5m.pkl"
OUT_META = CACHE / "campaign291_perp_5m.meta.json"
OUT_PROV = CACHE / "campaign291_perp_5m.provenance.json"

ARCHIVE_HOST = "https://data.binance.vision"
MONTHS = ("2026-08", "2026-09", "2026-10")
START_UTC = "2026-08-01T00:00:00Z"
END_UTC = "2026-10-30T23:55:00Z"
INTERVAL = "5m"
FUNDING_INTERVAL_HOURS = 8  # nominal Binance interval; some perps use 4h (real data)
VALID_FUNDING_INTERVALS = {1, 2, 4, 8}  # Binance USDT-M funding schedules
EXPECTED_SYMBOLS = 24  # C290 spot symbols minus the two without USDT-M archives

# Binance archive `calc_time` is boundary + 1 ms; floor to the 8h boundary.
FUNDING_STALE_BARS = int(24 * 60 / 5) + 1  # 24h + 1 bar of 5m bars


def sha256_bytes(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expected_index() -> pd.DatetimeIndex:
    step = pd.Timedelta(minutes=5)
    idx = pd.date_range(start=pd.Timestamp(START_UTC), end=pd.Timestamp(END_UTC), freq=step, tz="UTC")
    return pd.DatetimeIndex(idx)


def kline_url(symbol: str, month: str) -> str:
    return f"{ARCHIVE_HOST}/data/futures/um/monthly/klines/{symbol}/5m/{symbol}-5m-{month}.zip"


def funding_url(symbol: str, month: str) -> str:
    return f"{ARCHIVE_HOST}/data/futures/um/monthly/fundingRate/{symbol}/{symbol}-fundingRate-{month}.zip"


def _http_get(url: str, timeout: float, retries: int = 3) -> tuple[int, bytes]:
    last_exc: Exception | None = None
    for attempt in range(retries):
        req = urllib.request.Request(url, method="GET", headers={"User-Agent": "kilo-c291-ingest"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return int(resp.status), resp.read()
        except urllib.error.HTTPError as exc:  # 404/451 etc: do not retry
            return int(exc.code), b""
        except Exception as exc:  # noqa: BLE001  transient network: retry
            last_exc = exc
            time.sleep(0.6 * (attempt + 1))
    raise RuntimeError(f"GET failed after {retries} attempts: {url}: {last_exc}")


def read_zip_csv(zip_bytes: bytes) -> pd.DataFrame:
    zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    name = zf.namelist()[0]
    raw = zf.read(name)
    return pd.read_csv(io.BytesIO(raw))


def fetch_kline_month(symbol: str, month: str, timeout: float) -> dict:
    url = kline_url(symbol, month)
    status, data = _http_get(url, timeout)
    if status != 200:
        return {"symbol": symbol, "month": month, "kind": "klines", "url": url, "status": status, "rows": 0, "ok": False}
    df = read_zip_csv(data)
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    return {
        "symbol": symbol, "month": month, "kind": "klines", "url": url,
        "status": status, "rows": int(len(df)), "ok": True, "frame": df,
    }


def fetch_funding_month(symbol: str, month: str, timeout: float) -> dict:
    url = funding_url(symbol, month)
    status, data = _http_get(url, timeout)
    if status != 200:
        return {"symbol": symbol, "month": month, "kind": "funding", "url": url, "status": status, "rows": 0, "ok": False}
    df = read_zip_csv(data)
    # Binance `calc_time` is the funding boundary + 1 ms; floor each row to its OWN
    # native funding interval (8h for most perps, 4h for some) so 04:00/12:00/20:00
    # events are attributed to the correct boundary instead of collapsing to 8h.
    ct = pd.to_datetime(df["calc_time"], unit="ms", utc=True)
    df["boundary"] = pd.Series(
        [t.floor(f"{int(h)}h") for t, h in zip(ct, df["funding_interval_hours"])],
        index=df.index,
    )
    return {
        "symbol": symbol, "month": month, "kind": "funding", "url": url,
        "status": status, "rows": int(len(df)), "ok": True, "frame": df,
    }


def build_symbol(symbol: str, months: tuple[str, ...], exp_idx: pd.DatetimeIndex, timeout: float) -> dict:
    """Fetch all months for one symbol and assemble aligned perp OHLCV + funding."""
    per_month = []
    for m in months:
        k = fetch_kline_month(symbol, m, timeout)
        f = fetch_funding_month(symbol, m, timeout)
        per_month.extend([k, f])

    kline_ok = all(p["ok"] for p in per_month if p["kind"] == "klines")
    funding_ok = all(p["ok"] for p in per_month if p["kind"] == "funding")
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
        return detail

    kframes = [p["frame"] for p in per_month if p["kind"] == "klines"]
    kdf = pd.concat(kframes, axis=0).sort_values("open_time").drop_duplicates("open_time", keep="last")
    kdf = kdf.set_index("open_time")

    fframes = [p["frame"] for p in per_month if p["kind"] == "funding"]
    fdf = pd.concat(fframes, axis=0)
    fdf = fdf.drop_duplicates("boundary", keep="last").sort_values("boundary").set_index("boundary")

    # truncate klines to window and reindex on exact 5m grid
    kdf = kdf.reindex(exp_idx)
    n_bars = len(exp_idx)
    kline_nan = int(kdf[["open", "high", "low", "close", "volume"]].isna().sum().sum())
    finite = bool(np.isfinite(kdf[["open", "high", "low", "close", "volume"]].to_numpy(dtype=float)).all()) if kline_nan == 0 else False
    positive = bool((kdf[["open", "high", "low", "close", "volume"]].to_numpy(dtype=float) > 0).all()) if kline_nan == 0 else False
    full_coverage = (kline_nan == 0 and finite and positive)

    # funding reindex on the 5m grid: value only at native funding boundary bars, NaN elsewhere
    fr = fdf["last_funding_rate"].reindex(exp_idx)
    funding_rows = int(fr.notna().sum())
    intervals = sorted(int(x) for x in pd.unique(fdf["funding_interval_hours"]))
    funding_ok_shape = funding_rows >= 90 and set(intervals).issubset(VALID_FUNDING_INTERVALS)

    detail.update({
        "status": "ok" if full_coverage else "kline_coverage_fail",
        "bars": int(len(kdf)),
        "kline_nan": kline_nan,
        "kline_finite": finite,
        "kline_positive": positive,
        "full_coverage": full_coverage,
        "funding_rows": funding_rows,
        "funding_interval_hours": intervals,
        "funding_ok_shape": funding_ok_shape,
    })
    if not (full_coverage and funding_ok_shape):
        detail["status"] = "excluded"
        return detail

    detail["opens"] = kdf["open"].astype(float)
    detail["highs"] = kdf["high"].astype(float)
    detail["lows"] = kdf["low"].astype(float)
    detail["closes"] = kdf["close"].astype(float)
    detail["volumes"] = kdf["volume"].astype(float)
    detail["funding_rates"] = fr.astype(float)
    return detail


def load_universe() -> list[str]:
    if not META_290.exists():
        raise SystemExit(f"FATAL: C290 meta missing, cannot establish C291 universe: {META_290}")
    meta = json.loads(META_290.read_text())
    symbols = list(meta.get("symbols") or [])
    if not symbols:
        raise SystemExit("FATAL: C290 meta has no symbols")
    return symbols


def _pickle_bytes(payload: dict) -> bytes:
    buf = io.BytesIO()
    pickle.dump(payload, buf, protocol=pickle.HIGHEST_PROTOCOL)
    return buf.getvalue()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--timeout", type=float, default=60.0)
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args(argv)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    CACHE.mkdir(parents=True, exist_ok=True)

    universe = load_universe()
    exp_idx = expected_index()
    n_expected = len(exp_idx)

    built: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = [pool.submit(build_symbol, s, MONTHS, exp_idx, args.timeout) for s in universe]
        for fut in futures:
            d = fut.result()
            built[d["symbol"]] = d

    selected = [s for s in universe if built[s].get("status") == "ok"]
    excluded = {s: built[s].get("status") for s in universe if built[s].get("status") != "ok"}

    if len(selected) < EXPECTED_SYMBOLS:
        raise SystemExit(
            f"FATAL: only {len(selected)} symbols have full perp kline+funding coverage; "
            f"expected {EXPECTED_SYMBOLS}. Excluded: {excluded}"
        )

    def wide(field: str) -> pd.DataFrame:
        return pd.concat({s: built[s][field] for s in selected}, axis=1).reindex(exp_idx).astype(float)

    opens = wide("opens")
    highs = wide("highs")
    lows = wide("lows")
    closes = wide("closes")
    volumes = wide("volumes")
    funding_rates = wide("funding_rates")

    n_bars = int(len(exp_idx))
    shape = (n_bars, len(selected))
    for name, df in (("opens", opens), ("highs", highs), ("lows", lows), ("closes", closes), ("volumes", volumes)):
        if df.shape != shape:
            raise SystemExit(f"FATAL: aligned {name} shape {df.shape} != {shape}")

    payload = {
        "interval": INTERVAL,
        "symbols": selected,
        "window_start_utc": START_UTC,
        "window_end_utc": END_UTC,
        "n_bars": n_bars,
        "funding_interval_hours": FUNDING_INTERVAL_HOURS,
        "opens": opens,
        "highs": highs,
        "lows": lows,
        "closes": closes,
        "volumes": volumes,
        "funding_rates": funding_rates,
    }
    OUT_PKL.write_bytes(_pickle_bytes(payload))

    pkl_sha = sha256_bytes(OUT_PKL)
    meta = {
        "generated_at_utc": ts,
        "campaign": 291,
        "part": "ingest",
        "interval": INTERVAL,
        "symbols": selected,
        "n_symbols": len(selected),
        "rows": n_bars,
        "expected_bars": n_expected,
        "columns_per_frame": ["open", "high", "low", "close", "volume"],
        "funding_columns": ["boundary", "last_funding_rate"],
        "funding_interval_hours": FUNDING_INTERVAL_HOURS,
        "funding_intervals_by_symbol": {
            s: built[s].get("funding_interval_hours") for s in selected
        },
        "funding_rule": "real funding applied at each symbol's native Binance funding boundary (8h or 4h); calc_time floored to that boundary",
        "window_start_utc": START_UTC,
        "window_end_utc": END_UTC,
        "real_data_only": True,
        "fabricated_data": False,
        "fetch_real_data_only": True,
        "fetch_fabricated_data": False,
        "source_host": ARCHIVE_HOST,
        "kline_endpoint": "/data/futures/um/monthly/klines/<SYM>/5m/<SYM>-5m-YYYY-MM.zip",
        "funding_endpoint": "/data/futures/um/monthly/fundingRate/<SYM>/<SYM>-fundingRate-YYYY-MM.zip",
        "sha256_from_bytes": pkl_sha,
        "pkl_path": str(OUT_PKL.relative_to(ROOT)),
    }
    OUT_META.write_text(json.dumps(meta, indent=2) + "\n")

    per_symbol = {
        s: {
            "status": built[s]["status"],
            "bars": built[s].get("bars"),
            "kline_nan": built[s].get("kline_nan"),
            "full_coverage": built[s].get("full_coverage"),
            "funding_rows": built[s].get("funding_rows"),
            "funding_interval_hours": built[s].get("funding_interval_hours"),
            "funding_ok_shape": built[s].get("funding_ok_shape"),
        }
        for s in universe
    }
    provenance = {
        "generated_at_utc": ts,
        "campaign": 291,
        "part": "provenance",
        "real_data_only": True,
        "fabricated_data": False,
        "universe_rule": (
            "C290 spot universe (26 USDT symbols). USDT-M perp archives are fetched from the "
            "data.binance.vision public futures archive; any symbol whose perp kline or funding "
            "archive is missing/blocked/partial is excluded with a recorded reason. Klines are "
            "truncated to the exact 2026-08-01T00:00Z..2026-10-30T23:55Z window and reindexed on "
            "the exact 5m UTC grid; funding calc_time is floored to its native Binance funding "
            "boundary (8h for most perps, 4h for some; recorded per symbol). The spot leg "
            "for the basis feature is the already-verified C290 cache, referenced (never copied/relabeled)."
        ),
        "months": list(MONTHS),
        "n_universe": len(universe),
        "n_selected": len(selected),
        "selected_symbols": selected,
        "excluded_symbols": excluded,
        "per_symbol": per_symbol,
        "spot_leg_reference": {
            "path": str((CACHE / "campaign290_ohlcv.pkl").relative_to(ROOT)),
            "note": "verified real C290 spot 5m cache; used only as the spot leg for basis",
        },
    }
    OUT_PROV.write_text(json.dumps(provenance, indent=2, default=str) + "\n")

    summary = {
        "ok": True,
        "campaign": 291,
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
        "funding_rows_total": int(funding_rates.notna().sum().sum()),
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())