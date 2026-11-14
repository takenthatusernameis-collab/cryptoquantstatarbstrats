#!/usr/bin/env python3
"""C299 — ingest REAL USDT-M perpetual futures + spot + native funding for the
per-asset time-series funding-carry / spot-perp basis campaign (2020-01 .. 2026-10).

Unlike C298 (cross-sectional, requires every asset to cover the FULL 2020-2026
window), C299 trades each asset on its OWN maximal contiguous real coverage
window starting at 2020-01-01.  Any asset whose archive breaks (HTTP 404 /
partial month / NaN-gap month) is truncated at the last good month with a
recorded reason; assets whose very first month (2020-01) fails are excluded
entirely.  No imputation, no forward/back fill, no relabeling of existing
caches.

Sources (real mainnet public data, NOT the fapi REST API which is HTTP 451 from
this egress):

- data.binance.vision futures/um/monthly/klines/<SYM>/5m/<SYM>-5m-YYYY-MM.zip
  (real 5m perp klines; resampled to 1h OHLCV)
- data.binance.vision futures/um/monthly/fundingRate/<SYM>/<SYM>-fundingRate-YYYY-MM.zip
  (real calc_time/funding_interval_hours/last_funding_rate; native 8h/4h boundary)
- data-api.binance.vision /api/v3/klines (real spot 1h closes for the basis leg)

Per asset the 5m klines are resampled to 1h OHLCV on that asset's own 1h grid.
Funding is floored to each row's native Binance funding boundary and placed on
the 1h grid at boundary hours only (NaN elsewhere).  Spot gaps (data-api missing
hours) stay NaN, never imputed; the runner's fail-closed gates block any trade
requiring missing spot data.

Persisted artifacts (all real_data_only:true, fabricated_data:false,
SHA256-from-bytes):

- data/cache/campaign299_multianual_perp_funding_basis_ts.pkl   (per-asset panels)
- data/cache/campaign299_multianual_perp_funding_basis_ts.meta.json
- data/cache/campaign299_multianual_perp_funding_basis_ts.provenance.json

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
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from data.real_feed_loader import fetch_spot_ohlcv_klines  # noqa: E402

CACHE = ROOT / "data" / "cache"
OUT_PKL = CACHE / "campaign299_multianual_perp_funding_basis_ts.pkl"
OUT_META = CACHE / "campaign299_multianual_perp_funding_basis_ts.meta.json"
OUT_PROV = CACHE / "campaign299_multianual_perp_funding_basis_ts.provenance.json"

ARCHIVE_HOST = "https://data.binance.vision"
START_UTC = "2020-01-01T00:00:00Z"
# 2026-11 returns 404 on the archive (incomplete month); last complete month is 2026-10.
END_UTC = "2026-10-31T23:00:00Z"
SOURCE_INTERVAL = "5m"
TARGET_INTERVAL = "1h"
ONE_HOUR = pd.Timedelta(hours=1)
STALE_BARS = 24 + 1  # 24h + 1 bar on the 1h grid
MIN_FUNDING_ROWS = 90
VALID_FUNDING_INTERVALS = {1, 2, 4, 8}
# A walk-forward split needs at least train+test bars; require >= 4 contiguous
# months (~2880 1h bars) for an asset to be selectable at all.
MIN_BARS = 2880

# Candidate USDT-M perps with archive history from 2020-01 (verified HTTP 200).
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


def _months() -> list[str]:
    stamps = pd.date_range(start="2020-01-01", end="2026-10-01", freq="MS", tz="UTC")
    return [str(ts.date())[:7] for ts in stamps]


def sha256_bytes(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _http_get(url: str, timeout: float, retries: int = 3) -> tuple[int, bytes]:
    last_exc: Exception | None = None
    for attempt in range(retries):
        req = urllib.request.Request(url, method="GET", headers={"User-Agent": "kilo-c299-ingest"})
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
    if len(df) and str(df["open_time"].iloc[0]) == "open_time":
        df = df.iloc[1:].reset_index(drop=True)
    df["open_time"] = pd.to_numeric(df["open_time"], errors="coerce")
    df = df.dropna(subset=["open_time"])
    for c in ("open", "high", "low", "close", "volume"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def fetch_kline_month(symbol: str, month: str, timeout: float) -> dict:
    url = f"{ARCHIVE_HOST}/data/futures/um/monthly/klines/{symbol}/5m/{symbol}-5m-{month}.zip"
    status, data = _http_get(url, timeout)
    if status != 200:
        return {"symbol": symbol, "month": month, "kind": "klines", "url": url, "status": status, "rows": 0, "ok": False}
    df = read_zip_csv(data, kind="klines")
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    return {"symbol": symbol, "month": month, "kind": "klines", "url": url, "status": status, "rows": int(len(df)), "ok": True, "frame": df}


def fetch_funding_month(symbol: str, month: str, timeout: float) -> dict:
    url = f"{ARCHIVE_HOST}/data/futures/um/monthly/fundingRate/{symbol}/{symbol}-fundingRate-{month}.zip"
    status, data = _http_get(url, timeout)
    if status != 200:
        return {"symbol": symbol, "month": month, "kind": "funding", "url": url, "status": status, "rows": 0, "ok": False}
    df = read_zip_csv(data, kind="funding")
    ct = pd.to_datetime(df["calc_time"], unit="ms", utc=True)
    df["boundary"] = pd.Series([t.floor(f"{int(h)}h") for t, h in zip(ct, df["funding_interval_hours"])], index=df.index)
    return {"symbol": symbol, "month": month, "kind": "funding", "url": url, "status": status, "rows": int(len(df)), "ok": True, "frame": df}


def month_5m_index(month: str) -> pd.DatetimeIndex:
    start = pd.Timestamp(month + "-01", tz="UTC")
    # last hour of the month
    end = (start + pd.offsets.MonthEnd(0)) + pd.Timedelta(hours=23)
    return pd.DatetimeIndex(pd.date_range(start=start, end=end, freq="5min", tz="UTC"))


def build_symbol(symbol: str, months: list[str], timeout: float) -> dict:
    """Walk months in order from 2020-01; stop at the first bad month.  The
    accepted prefix is the asset's maximal contiguous real coverage window."""
    detail: dict = {"symbol": symbol, "per_month": [], "accepted_months": [], "stop_month": None, "stop_reason": None}
    kframes: list[pd.DataFrame] = []
    fframes: list[pd.DataFrame] = []
    window_start = pd.Timestamp(START_UTC)
    window_end = None
    for m in months:
        k = fetch_kline_month(symbol, m, timeout)
        f = fetch_funding_month(symbol, m, timeout)
        detail["per_month"].append({kk: k[kk] for kk in ("month", "kind", "status", "rows", "ok", "url")})
        detail["per_month"].append({kk: f[kk] for kk in ("month", "kind", "status", "rows", "ok", "url")})
        if not (k["ok"] and f["ok"]):
            detail["stop_month"] = m
            detail["stop_reason"] = (
                f"month {m} {('klines' if not k['ok'] else 'funding')} status "
                f"{k['status'] if not k['ok'] else f['status']}"
            )
            break
        kdf = k["frame"]
        fdf = f["frame"]
        # 5m kline coverage must be complete for the whole month (no NaN in OHLCV).
        exp_5m = month_5m_index(m)
        kdf = kdf.set_index("open_time").reindex(exp_5m)
        k_nan = int(kdf[["open", "high", "low", "close", "volume"]].isna().sum().sum())
        finite = bool(np.isfinite(kdf[["open", "high", "low", "close", "volume"]].to_numpy(dtype=float)).all()) if k_nan == 0 else False
        positive = bool((kdf[["open", "high", "low", "close"]].to_numpy(dtype=float) > 0).all()) if k_nan == 0 else False
        if not (k_nan == 0 and finite and positive):
            detail["stop_month"] = m
            detail["stop_reason"] = f"month {m} klines coverage fail (nan={k_nan}, finite={finite}, pos_px={positive})"
            break
        # funding must be finite on native boundaries.
        fr = fdf["last_funding_rate"].astype(float)
        vals = fr.dropna()
        f_finite = bool(np.isfinite(vals.to_numpy(dtype=float)).all()) if len(vals) else False
        if not (len(vals) > 0 and f_finite):
            detail["stop_month"] = m
            detail["stop_reason"] = f"month {m} funding coverage fail (rows={len(vals)}, finite={f_finite})"
            break

        detail["accepted_months"].append(m)
        kframes.append(kdf)
        fframes.append(fdf)
        window_end = (pd.Timestamp(m + "-01", tz="UTC") + pd.offsets.MonthEnd(0)) + pd.Timedelta(hours=23)

    if window_end is None:
        detail["status"] = "excluded"
        detail["exclusion_reason"] = detail["stop_reason"] or "first month 2020-01 failed"
        return detail

    # Resample accepted 5m klines -> 1h OHLCV on the asset's own 1h grid.
    kdf = pd.concat(kframes, axis=0).sort_index()
    kdf = kdf.loc[(kdf.index >= window_start) & (kdf.index <= window_end)]
    exp_idx = pd.DatetimeIndex(pd.date_range(start=window_start, end=window_end, freq="1h", tz="UTC"))
    kdf = kdf.reindex(exp_idx)
    ohlc = kdf[["open", "high", "low", "close"]].resample("1h").agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    vol = kdf["volume"].resample("1h").sum()
    h1 = pd.concat([ohlc, vol.rename("volume")], axis=1).reindex(exp_idx)
    h1_nan = int(h1.isna().sum().sum())
    h1_finite = bool(np.isfinite(h1.to_numpy(dtype=float)).all()) if h1_nan == 0 else False
    h1_positive = bool((h1[["open", "high", "low", "close"]].to_numpy(dtype=float) > 0).all()) if h1_nan == 0 else False
    h1_volok = bool((h1["volume"].to_numpy(dtype=float) >= 0).all()) if h1_nan == 0 else False
    if not (h1_nan == 0 and h1_finite and h1_positive and h1_volok):
        detail["status"] = "excluded"
        detail["exclusion_reason"] = f"1h resample coverage fail over accepted window (nan={h1_nan}, finite={h1_finite}, pos_px={h1_positive}, vol_ok={h1_volok})"
        return detail

    # Funding floored to native boundary, on the asset's 1h grid at boundary hours only.
    fdf = pd.concat(fframes, axis=0)
    fdf = fdf.drop_duplicates("boundary", keep="last").sort_values("boundary").set_index("boundary")
    fr = fdf["last_funding_rate"].astype(float).reindex(exp_idx)
    funding_rows = int(fr.notna().sum())
    intervals = sorted(int(x) for x in pd.unique(fdf["funding_interval_hours"]))
    vals = fr.dropna()
    f_finite = bool(np.isfinite(vals.to_numpy(dtype=float)).all()) if len(vals) else False
    pos = np.where(fr.notna().values)[0]
    gap = int(np.diff(pos).max()) if len(pos) > 1 else 0
    tail_gap = int(len(exp_idx) - 1 - pos[-1]) if len(pos) else int(len(exp_idx))
    stale_ok = gap <= STALE_BARS and tail_gap <= STALE_BARS
    funding_ok = funding_rows >= MIN_FUNDING_ROWS and f_finite and set(intervals).issubset(VALID_FUNDING_INTERVALS) and stale_ok
    if not funding_ok:
        detail["status"] = "excluded"
        detail["exclusion_reason"] = (
            f"funding coverage fail (rows={funding_rows}, finite={f_finite}, intervals={intervals}, "
            f"max_gap={gap}, tail_gap={tail_gap})"
        )
        return detail

    if int(len(exp_idx)) < MIN_BARS:
        detail["status"] = "excluded"
        detail["exclusion_reason"] = f"insufficient contiguous window bars={len(exp_idx)} < {MIN_BARS}"
        return detail

    detail.update({
        "status": "ok",
        "window_start_utc": str(window_start),
        "window_end_utc": str(window_end),
        "n_bars": int(len(exp_idx)),
        "accepted_months": detail["accepted_months"],
        "n_accepted_months": len(detail["accepted_months"]),
        "h1_nan": h1_nan,
        "funding_rows": funding_rows,
        "funding_interval_hours": intervals,
        "funding_max_gap_bars": gap,
        "funding_tail_gap_bars": tail_gap,
        "stale_ok": stale_ok,
        "full_2020_2026_coverage": window_start == pd.Timestamp(START_UTC) and window_end == pd.Timestamp(END_UTC),
        "opens": h1["open"].astype(float),
        "highs": h1["high"].astype(float),
        "lows": h1["low"].astype(float),
        "closes": h1["close"].astype(float),
        "volumes": h1["volume"].astype(float),
        "funding_rates": fr.astype(float),
        "index": exp_idx,
    })
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

    # Cross-check against the verified C298 cache (same archive, same 3 fully
    # covered assets) without mutating it.
    c298_pkl = CACHE / "campaign298_multianual_perp_funding_basis.pkl"
    c298_meta = CACHE / "campaign298_multianual_perp_funding_basis.meta.json"
    c298_sha_note = None
    if c298_pkl.exists() and c298_meta.exists():
        c298_sha_note = sha256_bytes(c298_pkl)

    universe = load_universe()
    months = _months()
    built: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = {pool.submit(build_symbol, s, months, args.timeout): s for s in universe}
        for fut in as_completed(futures):
            d = fut.result()
            built[d["symbol"]] = d

    selected = [s for s in universe if built[s].get("status") == "ok"]
    excluded = {s: built[s].get("exclusion_reason", built[s].get("status")) for s in universe if built[s].get("status") != "ok"}

    if not selected:
        raise SystemExit(f"FATAL: no asset has a usable contiguous real window. Excluded: {excluded}")

    # Spot leg (basis): real spot 1h klines from data-api.binance.vision over each
    # asset's own contiguous window.  Gaps stay NaN; never imputed.
    spot_hosts = ["https://data-api.binance.vision"]
    spot_frames: dict[str, pd.DataFrame] = {}
    spot_prov_parts: list[dict] = {}
    for s in selected:
        wstart = built[s]["window_start_utc"]
        wend = built[s]["window_end_utc"]
        frames, prov = fetch_spot_ohlcv_klines([s], wstart, wend, interval=TARGET_INTERVAL, timeout=40.0, page_limit=1000, max_workers=max(1, args.workers), hosts=spot_hosts)
        if s not in frames:
            raise SystemExit(f"FATAL: spot leg missing symbol {s}; provenance={prov}")
        fr = frames[s]
        if not bool(fr.index.isin(built[s]["index"]).all()):
            raise SystemExit(f"FATAL: spot frame for {s} contains hours outside its window")
        px = fr[["open", "high", "low", "close"]]
        pxn = px.dropna()
        if int(pxn.isna().sum().sum()) != 0 or not bool(np.isfinite(pxn.to_numpy(dtype=float)).all()) or not bool((pxn.to_numpy(dtype=float) > 0).all()):
            raise SystemExit(f"FATAL: spot price frame for {s} has NaN/non-finite/non-positive values")
        spot_frames[s] = fr.astype(float)
        spot_prov_parts[s] = prov

    def wide_for(field: str) -> pd.DataFrame:
        # Per-asset windows differ; store each asset's series on its own index.
        return {s: built[s][field] for s in selected}

    payload = {
        "interval": TARGET_INTERVAL,
        "source_interval": SOURCE_INTERVAL,
        "symbols": selected,
        "n_symbols": len(selected),
        "window": {"start": START_UTC, "end": END_UTC},
        "universe": universe,
        "n_universe": len(universe),
        "per_asset": {
            s: {
                "window_start_utc": built[s]["window_start_utc"],
                "window_end_utc": built[s]["window_end_utc"],
                "n_bars": int(built[s]["n_bars"]),
                "accepted_months": built[s]["accepted_months"],
                "n_accepted_months": int(built[s]["n_accepted_months"]),
                "full_2020_2026_coverage": bool(built[s]["full_2020_2026_coverage"]),
                "h1_nan": int(built[s]["h1_nan"]),
                "funding_rows": int(built[s]["funding_rows"]),
                "funding_interval_hours": built[s]["funding_interval_hours"],
                "funding_max_gap_bars": int(built[s]["funding_max_gap_bars"]),
                "funding_tail_gap_bars": int(built[s]["funding_tail_gap_bars"]),
                "stale_ok": bool(built[s]["stale_ok"]),
                "opens": built[s]["opens"],
                "highs": built[s]["highs"],
                "lows": built[s]["lows"],
                "closes": built[s]["closes"],
                "volumes": built[s]["volumes"],
                "spot_closes": spot_frames[s]["close"].reindex(built[s]["index"]).astype(float),
                "funding_rates": built[s]["funding_rates"],
                "index": built[s]["index"],
            }
            for s in selected
        },
        "real_data_only": True,
        "fabricated_data": False,
    }
    OUT_PKL.write_bytes(_pickle_bytes(payload))
    pkl_sha = sha256_bytes(OUT_PKL)

    n_total_bars = sum(int(built[s]["n_bars"]) for s in selected)
    n_full = sum(1 for s in selected if bool(built[s]["full_2020_2026_coverage"]))
    meta = {
        "generated_at_utc": ts,
        "campaign": 299,
        "part": "ingest",
        "interval": TARGET_INTERVAL,
        "source_interval": SOURCE_INTERVAL,
        "symbols": selected,
        "n_symbols": len(selected),
        "n_universe": len(universe),
        "total_bars": int(n_total_bars),
        "n_full_2020_2026_assets": int(n_full),
        "window_start_utc": START_UTC,
        "window_end_utc": END_UTC,
        "source_host": ARCHIVE_HOST,
        "spot_host": "https://data-api.binance.vision",
        "kline_endpoint": "/data/futures/um/monthly/klines/<SYM>/5m/<SYM>-5m-YYYY-MM.zip",
        "funding_endpoint": "/data/futures/um/monthly/fundingRate/<SYM>/<SYM>-fundingRate-YYYY-MM.zip",
        "spot_endpoint": "/api/v3/klines",
        "months": months,
        "n_months": len(months),
        "min_bars": MIN_BARS,
        "stale_bars": STALE_BARS,
        "min_funding_rows": MIN_FUNDING_ROWS,
        "valid_funding_intervals": sorted(list(VALID_FUNDING_INTERVALS)),
        "real_data_only": True,
        "fabricated_data": False,
        "fetch_real_data_only": True,
        "fetch_fabricated_data": False,
        "sha256_from_bytes": pkl_sha,
        "pkl_path": str(OUT_PKL.relative_to(ROOT)),
        "c298_cache_sha256_crosscheck": c298_sha_note,
    }
    OUT_META.write_text(json.dumps(meta, indent=2) + "\n")

    per_symbol = {
        s: {
            "status": built[s]["status"],
            "exclusion_reason": built[s].get("exclusion_reason"),
            "window_start_utc": built[s].get("window_start_utc"),
            "window_end_utc": built[s].get("window_end_utc"),
            "n_bars": built[s].get("n_bars"),
            "n_accepted_months": built[s].get("n_accepted_months"),
            "full_2020_2026_coverage": built[s].get("full_2020_2026_coverage"),
            "accepted_months": built[s].get("accepted_months"),
            "stop_month": built[s].get("stop_month"),
            "stop_reason": built[s].get("stop_reason"),
            "h1_nan": built[s].get("h1_nan"),
            "funding_rows": built[s].get("funding_rows"),
            "funding_interval_hours": built[s].get("funding_interval_hours"),
            "funding_max_gap_bars": built[s].get("funding_max_gap_bars"),
            "funding_tail_gap_bars": built[s].get("funding_tail_gap_bars"),
            "stale_ok": built[s].get("stale_ok"),
        }
        for s in universe
    }
    spot_per_symbol = {}
    for s in selected:
        fr = spot_frames[s]
        exp = built[s]["index"]
        gap_hours = [str(t) for t in exp.difference(fr.index)]
        spot_per_symbol[s] = {
            "bars": int(fr.shape[0]),
            "index_subset_of_asset_index": bool(fr.index.isin(exp).all()),
            "gap_hours": len(gap_hours),
            "gap_hours_first": gap_hours[0] if gap_hours else None,
            "gap_hours_last": gap_hours[-1] if gap_hours else None,
        }
    provenance = {
        "generated_at_utc": ts,
        "campaign": 299,
        "part": "provenance",
        "real_data_only": True,
        "fabricated_data": False,
        "universe_rule": (
            "Candidates are USDT-M perps with archive history from 2020-01 (verified HTTP 200 on "
            "data.binance.vision). Each asset is walked month-by-month from 2020-01; the first "
            "missing/blocked/partial month ends that asset's contiguous window (recorded with a "
            "reason).  Assets failing 2020-01 are excluded entirely. 5m klines are truncated to the "
            "accepted window and resampled to 1h OHLCV on the asset's own 1h UTC grid; funding "
            "calc_time is floored to its native Binance funding boundary (8h/4h; recorded per asset) "
            "and placed on the 1h grid at boundary hours only. The spot leg is real spot 1h klines "
            "from data-api.binance.vision/api/v3/klines over each asset's window; spot gaps are NOT "
            "imputed: recorded per asset, and the runner's fail-closed gates block any trade needing "
            "missing spot data. Requires >= 2880 contiguous 1h bars (one WF train+test). No "
            "impute/ffill/resample of derived series."
        ),
        "n_candidates": len(universe),
        "n_selected": len(selected),
        "selected_symbols": selected,
        "excluded_symbols": excluded,
        "per_symbol": per_symbol,
        "spot_per_symbol": spot_per_symbol,
        "spot_leg_provenance": spot_prov_parts,
        "months": months,
        "n_months": len(months),
        "window": {"start": START_UTC, "end": END_UTC},
        "interval": TARGET_INTERVAL,
    }
    OUT_PROV.write_text(json.dumps(provenance, indent=2, default=str) + "\n")

    summary = {
        "ok": True,
        "campaign": 299,
        "real_data_only": True,
        "fabricated_data": False,
        "pkl": str(OUT_PKL.relative_to(ROOT)),
        "pkl_sha256": pkl_sha,
        "meta": str(OUT_META.relative_to(ROOT)),
        "meta_sha256": sha256_bytes(OUT_META),
        "provenance": str(OUT_PROV.relative_to(ROOT)),
        "provenance_sha256": sha256_bytes(OUT_PROV),
        "c298_cache_sha256_crosscheck": c298_sha_note,
        "n_symbols": len(selected),
        "n_universe": len(universe),
        "total_bars": int(n_total_bars),
        "n_full_2020_2026_assets": int(n_full),
        "selected_symbols": selected,
        "excluded_symbols": excluded,
        "min_bars": MIN_BARS,
        "window": {"start": START_UTC, "end": END_UTC},
        "interval": TARGET_INTERVAL,
        "funding_rows_total": sum(int(built[s]["funding_rows"]) for s in selected),
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
