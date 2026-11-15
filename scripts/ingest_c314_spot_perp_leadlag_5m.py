#!/usr/bin/env python3
"""C314 — ingest REAL Binance SPOT + USDT-M LINEAR PERPETUAL ``5m`` klines and
build per-symbol lead-lag feature panels for the C314 spot-perp lead-lag
statistical-arbitrage campaign.

This is a genuinely new economic family, not a re-skin of any frozen campaign:

- C281B-C313 (all FROZEN formal negatives) exhausted linear/ inverse carry, OFI,
  premium/index/mark basis and quarterly term-structure families.
- C314 tests a DISTINCT signal: the cross-sectional lead-lag relationship between
  the SAME asset's spot and USDT-M perp price (spot leads / lags perp). It is a
  two-leg (spot + perp) USDT-quoted relative-value trade, not a directional carry.

DATA SOURCE (verified live 2026-11-15, HTTP 206 for spot AND USDT-M perp 5m):

  spot: https://data.binance.vision/data/spot/monthly/klines/<SYM>/5m/<SYM>-5m-YYYY-MM.zip
  perp: https://data.binance.vision/data/futures/um/monthly/klines/<SYM>/5m/<SYM>-5m-YYYY-MM.zip

Universe: 10 USDT-M linear perps that also have spot books
(BTC,ETH,BNB,SOL,XRP,ADA,DOGE,DOT,LTC,AVAX)USDT.
Window: 2023-01 .. 2025-12 (36 months). Frequency: native 5m.
A 404 month = pre-listing exclusion for that (symbol, market), NOT an outage.
USDT-M funding is NOT in the monthly archives and fapi is HTTP 451 -> the
``funding_rate`` leg is emitted all-NaN (control only, excluded from PnL).

RESUMABILITY (mandatory de-bottleneck so the download survives session bounds):
- After aggregating each (symbol, market, month) we write an intermediate shard
  ``months/<SYM>_<market>_<YYYY-MM>.npz`` and record its SHA256 in
  ``months_manifest.json``; on start we SKIP any month already in the manifest.
- Once every month for a symbol exists we assemble the per-symbol
  ``<SYM>.npz`` panel on the common 5m grid, then delete that symbol's month
  shards so the total cache stays < 100 MB.

Storage: per-asset float32 ``.npz`` shards (``spot_close``, ``perp_close``,
``funding_rate``), plus ``meta.json`` + ``provenance.json``. Every artifact
carries ``real_data_only:true``, ``fabricated_data:false``, ``executed_fills:false``
and a SHA256-from-bytes. Raw CSV is discarded after feature extraction.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
import time
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "cache"
OUT_DIR = CACHE / "campaign314_spot_perp_leadlag_5m"
MONTHS_DIR = OUT_DIR / "months"
MANIFEST = OUT_DIR / "months_manifest.json"
OUT_META = CACHE / "campaign314_spot_perp_leadlag_5m.meta.json"
OUT_PROV = CACHE / "campaign314_spot_perp_leadlag_5m.provenance.json"

ARCHIVE_HOST = "https://data.binance.vision"
SPOT_PATH = "/data/spot/monthly/klines/{sym}/5m/{sym}-5m-{month}.zip"
PERP_PATH = "/data/futures/um/monthly/klines/{sym}/5m/{sym}-5m-{month}.zip"
MARKETS = ("spot", "perp")
PATHS = {"spot": SPOT_PATH, "perp": PERP_PATH}

SYMBOLS = (
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
    "ADAUSDT", "DOGEUSDT", "DOTUSDT", "LTCUSDT", "AVAXUSDT",
)

DEFAULT_START = "2023-01"
DEFAULT_END = "2025-12"
INTERVAL = "5m"
BAR_MS = 300_000

KLINE_COLUMNS = [
    "open_time", "open", "high", "low", "close", "volume", "close_time",
    "quote_volume", "count", "taker_buy_volume", "taker_buy_quote_volume", "ignore",
]

# Persisted float32 legs per symbol shard (funding_rate is control-only NaN).
F32_LEGS = ("spot_close", "perp_close", "funding_rate")

PUSH_LIMIT_BYTES = 100_000_000
CACHE_BUDGET_BYTES = 100_000_000
HTTP_RETRIES = 6


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def month_range(start: str, end: str) -> list[str]:
    out = []
    y, m = int(start[:4]), int(start[5:7])
    ey, em = int(end[:4]), int(end[5:7])
    while (y, m) <= (ey, em):
        out.append(f"{y:04d}-{m:02d}")
        m += 1
        if m > 12:
            m = 1
            y += 1
    return out


def _http_get(url: str, timeout: float) -> tuple[int, bytes]:
    last_exc: Exception | None = None
    for attempt in range(1, HTTP_RETRIES + 1):
        req = urllib.request.Request(url, method="GET", headers={"User-Agent": "kilo-c314-ingest"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return int(resp.status), resp.read()
        except urllib.error.HTTPError as exc:  # 404/451 lone -> retry then give up
            last_exc = exc
            if exc.code in (404, 451):
                time.sleep(1.0 * attempt)
                continue
            return int(exc.code), b""
        except Exception as exc:  # noqa: BLE001  transient network: retry w/ backoff
            last_exc = exc
            time.sleep(1.0 * attempt)
    raise RuntimeError(f"GET failed after {HTTP_RETRIES} attempts: {url}: {last_exc}")


def _first_line(raw: bytes) -> bytes:
    nl = raw.find(b"\n")
    return raw[: nl if nl >= 0 else len(raw)]


def normalize_open_time_ms(ot) -> np.ndarray:
    """Normalize kline ``open_time`` to MILLISECONDS.

    Binance SPOT 5m archives switched ``open_time`` to MICROSECONDS from 2025-01
    (e.g. 1735689600000000) while USDT-M futures remain in milliseconds
    (1735689600000). A raw microsecond value is ~1e15; a millisecond value is
    ~1e12. Anything above 1e14 is microseconds -> divide by 1000. This is the
    key de-bottleneck that makes 2025 spot/perp timestamps intersect.
    """
    arr = np.asarray(ot, dtype="int64")
    if arr.size and int(np.nanmax(arr)) > 100_000_000_000_000:  # > 1e14 => microseconds
        arr = arr // 1000
    return arr


def read_klines_zip(zip_bytes: bytes) -> pd.DataFrame:
    zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    raw = zf.read(zf.namelist()[0])
    has_header = b"open_time" in _first_line(raw)
    if has_header:
        df = pd.read_csv(io.BytesIO(raw))
    else:
        df = pd.read_csv(io.BytesIO(raw), header=None, names=KLINE_COLUMNS)
    for c in KLINE_COLUMNS:
        if c not in df.columns:
            raise ValueError(f"missing kline column {c}")
        if c != "open_time":
            df[c] = pd.to_numeric(df[c], errors="coerce")
    ot = pd.to_numeric(df["open_time"], errors="coerce")
    df = df.assign(_ot=ot)
    df = df[df["_ot"].notna()]
    df["_ot"] = normalize_open_time_ms(df["_ot"].to_numpy(dtype="int64"))
    df = df.drop_duplicates(subset="_ot", keep="last").sort_values("_ot")
    return df.reset_index(drop=True)


def month_legs_from_klines(df: pd.DataFrame) -> dict:
    """Persist the per-5m-bar close for one market-month."""
    close = df["close"].to_numpy(dtype=float)
    ot_ms = df["_ot"].to_numpy(dtype="int64")
    return {"open_time_ms": ot_ms, "close": close.astype(np.float32)}


def _load_manifest() -> dict:
    if MANIFEST.exists():
        try:
            return json.loads(MANIFEST.read_text())
        except Exception:  # noqa: BLE001
            return {"months": {}, "assembled": []}
    return {"months": {}, "assembled": []}


def _save_manifest(man: dict) -> None:
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(man, indent=2, sort_keys=True) + "\n")


def _month_shard_path(sym: str, market: str, month: str) -> Path:
    return MONTHS_DIR / f"{sym}_{market}_{month}.npz"


def _write_month_shard(sym: str, market: str, month: str, legs: dict) -> str:
    MONTHS_DIR.mkdir(parents=True, exist_ok=True)
    p = _month_shard_path(sym, market, month)
    np.savez_compressed(p, **legs)
    return sha256_file(p)


def download_month(sym: str, market: str, month: str, timeout: float, man: dict) -> dict:
    """Download + aggregate one (symbol, market, month) into a shard, resumable."""
    key = f"{sym}_{market}_{month}"
    shard = _month_shard_path(sym, market, month)
    prev = (man.get("months") or {}).get(key)
    if prev and shard.exists() and sha256_file(shard) == prev.get("sha256"):
        return {"month": month, "market": market, "status": "skipped",
                "reason": "in_manifest", "bars": prev.get("bars")}

    url = ARCHIVE_HOST + PATHS[market].format(sym=sym, month=month)
    try:
        status, data = _http_get(url, timeout)
    except Exception as exc:  # noqa: BLE001
        return {"month": month, "market": market, "url": url, "status": "error",
                "ok": False, "reason": repr(exc)[:200]}
    if status != 200:
        return {"month": month, "market": market, "url": url, "status": status,
                "ok": False, "reason": f"http_{status}"}
    df = read_klines_zip(data)
    del data
    if len(df) == 0:
        return {"month": month, "market": market, "url": url, "status": status,
                "ok": False, "reason": "empty klines"}
    legs = month_legs_from_klines(df)
    sha = _write_month_shard(sym, market, month, legs)
    man.setdefault("months", {})[key] = {"sha256": sha, "bars": int(len(df))}
    _save_manifest(man)
    return {"month": month, "market": market, "url": url, "status": status,
            "bars": int(len(df)), "ok": True}


def _series_from_shards(sym: str, market: str, months: list[str]) -> dict:
    """open_time -> close for one (symbol, market) from its month shards."""
    ot_all: list[np.ndarray] = []
    cl_all: list[np.ndarray] = []
    accepted: list[str] = []
    for m in months:
        p = _month_shard_path(sym, market, m)
        if not p.exists():
            continue
        with np.load(p) as z:
            ot_all.append(normalize_open_time_ms(np.asarray(z["open_time_ms"], dtype="int64")))
            cl_all.append(np.asarray(z["close"], dtype=np.float32))
        accepted.append(m)
    if not ot_all:
        return {"status": "excluded", "exclusion_reason": "no month shards"}
    ot = np.concatenate(ot_all)
    cl = np.concatenate(cl_all)
    order = np.argsort(ot, kind="mergesort")
    ot, cl = ot[order], cl[order]
    # dedup open_time (keep last)
    keep = np.ones(len(ot), dtype=bool)
    if len(ot) > 1:
        dup = np.empty(len(ot), dtype=bool)
        dup[:-1] = ot[1:] == ot[:-1]
        dup[-1] = False
        keep = ~dup
    return {"status": "ok", "open_time_ms": ot[keep], "close": cl[keep],
            "accepted_months": accepted}


def build_symbol(sym: str, months: list[str]) -> dict:
    """Align a symbol's spot & perp close on their common 5m open_times."""
    spot = _series_from_shards(sym, "spot", months)
    perp = _series_from_shards(sym, "perp", months)
    if spot["status"] != "ok" or perp["status"] != "ok":
        return {"symbol": sym, "status": "excluded",
                "exclusion_reason": f"spot={spot.get('status')} perp={perp.get('status')}"}
    common = np.intersect1d(spot["open_time_ms"], perp["open_time_ms"], assume_unique=False)
    common = np.sort(common)
    if len(common) == 0:
        return {"symbol": sym, "status": "excluded", "exclusion_reason": "empty spot/perp intersection"}
    spot_map = dict(zip(spot["open_time_ms"].tolist(), spot["close"].tolist()))
    perp_map = dict(zip(perp["open_time_ms"].tolist(), perp["close"].tolist()))
    spot_close = np.array([spot_map.get(int(v), np.nan) for v in common], dtype=np.float32)
    perp_close = np.array([perp_map.get(int(v), np.nan) for v in common], dtype=np.float32)
    return {"symbol": sym, "status": "ok", "open_time_ms": common,
            "spot_close": spot_close, "perp_close": perp_close,
            "n_spot_months": len(spot["accepted_months"]),
            "n_perp_months": len(perp["accepted_months"])}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--start-month", default=DEFAULT_START)
    ap.add_argument("--end-month", default=DEFAULT_END)
    ap.add_argument("--symbols", default="all", help="comma list or 'all'")
    ap.add_argument("--timeout", type=float, default=180.0)
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args(argv)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    CACHE.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    MONTHS_DIR.mkdir(parents=True, exist_ok=True)

    symbols = list(SYMBOLS) if args.symbols == "all" else [s.strip() for s in args.symbols.split(",") if s.strip()]
    months = month_range(args.start_month, args.end_month)
    man = _load_manifest()
    man.setdefault("months", {})
    man.setdefault("assembled", [])

    # ---- Phase A: download + aggregate each (symbol, market, month) -> shard ----
    from concurrent.futures import ThreadPoolExecutor, as_completed
    todo = [(s, mkt, m) for s in symbols if s not in man["assembled"]
            for mkt in MARKETS for m in months
            if f"{s}_{mkt}_{m}" not in man["months"]]
    per_month_log: list[dict] = []
    errors: list[dict] = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futs = {pool.submit(download_month, s, mkt, m, args.timeout, man): (s, mkt, m)
                for s, mkt, m in todo}
        for fut in as_completed(futs):
            r = fut.result()
            per_month_log.append({k: v for k, v in r.items() if k != "url"})
            if not r.get("ok", True) and r.get("status") != "skipped":
                errors.append({"symbol": futs[fut][0], "market": futs[fut][1],
                               **{k: v for k, v in r.items() if k != "url"}})

    # ---- Phase B: assemble each symbol's spot/perp panel ----
    assembled = set(man["assembled"])
    remaining = [s for s in symbols if s not in assembled]
    built: dict[str, dict] = {}
    for s in remaining:
        d = build_symbol(s, months)
        if d.get("status") == "ok":
            built[s] = d
        else:
            errors.append({"symbol": s, "assemble": d.get("exclusion_reason")})
    if not built and not assembled:
        raise SystemExit(f"FATAL: no symbol assembled. errors={json.dumps(errors)[:2000]}")

    # include already-assembled symbols by reading their existing shards
    all_series: dict[str, dict] = {}
    all_series.update(built)
    for s in assembled:
        sp = OUT_DIR / f"{s}.npz"
        if not sp.exists():
            continue
        with np.load(sp) as z:
            all_series[s] = {
                "open_time_ms": np.asarray(z["index_ms"], dtype="int64"),
                "spot_close": np.asarray(z["spot_close"], dtype=np.float32),
                "perp_close": np.asarray(z["perp_close"], dtype=np.float32),
            }

    # ---- common grid = intersection of every symbol's spot/perp open_times ----
    common = None
    for s, d in all_series.items():
        ms = np.asarray(d["open_time_ms"], dtype="int64")
        common = ms if common is None else np.intersect1d(common, ms, assume_unique=False)
    if common is None or len(common) == 0:
        raise SystemExit("FATAL: empty common 5m grid")
    grid_ms = np.sort(common)

    # nominal 5m bar count in window
    nominal = 0
    y, mo = int(args.start_month[:4]), int(args.start_month[5:7])
    ey, em = int(args.end_month[:4]), int(args.end_month[5:7])
    while (y, mo) <= (ey, em):
        if mo == 12:
            nxt = pd.Timestamp(f"{y + 1:04d}-01-01", tz="UTC")
        else:
            nxt = pd.Timestamp(f"{y:04d}-{mo + 1:02d}-01", tz="UTC")
        first = pd.Timestamp(f"{y:04d}-{mo:02d}-01", tz="UTC")
        nominal += int((nxt - first).total_seconds() // 300)
        mo += 1
        if mo > 12:
            mo = 1
            y += 1
    if len(grid_ms) < 0.8 * nominal:
        raise SystemExit(f"FATAL: common 5m grid {len(grid_ms)} bars < 80% of nominal {nominal}")

    grid_index = pd.DatetimeIndex(pd.to_datetime(grid_ms, unit="ms", utc=True))

    # ---- write per-symbol npz on the common grid; enforce cache budget ----
    def write_shards(series_map: dict[str, dict]) -> dict:
        grid_pos = {int(v): i for i, v in enumerate(grid_ms)}
        n = len(grid_ms)
        shard_sha: dict[str, str] = {}
        shard_bytes: dict[str, int] = {}
        for s, d in series_map.items():
            ot = np.asarray(d["open_time_ms"], dtype="int64")
            idx = np.array([grid_pos.get(int(v), -1) for v in ot], dtype=np.int64)
            mask = idx >= 0
            arrays = {"index_ms": grid_ms.astype(np.int64)}
            for leg in F32_LEGS:
                if leg == "funding_rate":
                    arrays[leg] = np.full(n, np.nan, dtype=np.float32)
                    continue
                src = d.get(leg)
                arr = np.full(n, np.nan, dtype=np.float32)
                if src is not None:
                    arr[idx[mask]] = np.asarray(src, dtype=np.float32)[mask]
                arrays[leg] = arr
            spot_close = arrays["spot_close"]
            perp_close = arrays["perp_close"]
            if not (np.isfinite(spot_close).all() and (spot_close > 0).all()):
                raise SystemExit(f"FATAL: {s} spot_close non-finite/non-positive on common grid")
            if not (np.isfinite(perp_close).all() and (perp_close > 0).all()):
                raise SystemExit(f"FATAL: {s} perp_close non-finite/non-positive on common grid")
            sp = OUT_DIR / f"{s}.npz"
            np.savez_compressed(sp, **arrays)
            shard_sha[s] = sha256_file(sp)
            shard_bytes[s] = int(sp.stat().st_size)
        return {"sha": shard_sha, "bytes": shard_bytes}

    written = write_shards(all_series)
    total_bytes = sum(written["bytes"].values())
    dropped: list[str] = []
    if total_bytes > CACHE_BUDGET_BYTES and len(all_series) > 2:
        # drop highest-storage symbols first (never widen the window)
        order = sorted(all_series, key=lambda s: written["bytes"].get(s, 0), reverse=True)
        while total_bytes > CACHE_BUDGET_BYTES and len(all_series) > 2:
            drop = order.pop(0)
            sp = OUT_DIR / f"{drop}.npz"
            if sp.exists():
                total_bytes -= sp.stat().st_size
                sp.unlink()
            all_series.pop(drop, None)
            dropped.append(drop)
            written = write_shards(all_series)
            total_bytes = sum(written["bytes"].values())
    if total_bytes >= CACHE_BUDGET_BYTES:
        raise SystemExit(f"FATAL: total cache {total_bytes/1e6:.2f} MB >= budget")
    selected = sorted(all_series.keys())
    max_shard = max(written["bytes"].values()) if written["bytes"] else 0
    if max_shard >= PUSH_LIMIT_BYTES:
        raise SystemExit(f"FATAL: shard {max_shard/1e6:.2f} MB >= push limit")

    # ---- delete month shards for fully-assembled symbols (keep cache small) ----
    for s in selected:
        for mkt in MARKETS:
            for m in months:
                p = _month_shard_path(s, mkt, m)
                if p.exists():
                    p.unlink()
    man["assembled"] = sorted(set(man["assembled"]) | set(selected))
    man["months"] = {k: v for k, v in man["months"].items()
                     if k.rsplit("_", 3)[0] not in selected}
    _save_manifest(man)

    n_grid = int(len(grid_ms))
    meta = {
        "generated_at_utc": ts,
        "campaign": 314,
        "part": "ingest",
        "interval": INTERVAL,
        "bar_ms": BAR_MS,
        "source_interval": "spot_and_usdt_m_5m_klines_close",
        "markets": list(MARKETS),
        "symbols": selected,
        "n_symbols": len(selected),
        "n_universe": len(symbols),
        "total_bars": int(n_grid * len(selected)),
        "window_start_month": args.start_month,
        "window_end_month": args.end_month,
        "grid_start_utc": str(grid_index[0]),
        "grid_end_utc": str(grid_index[-1]),
        "n_grid_bars": n_grid,
        "n_nominal_grid_bars": int(nominal),
        "grid_construction": "intersection_of_symbol_spot_and_perp_5m_kline_bars",
        "source_host": ARCHIVE_HOST,
        "spot_klines_endpoint": SPOT_PATH,
        "perp_klines_endpoint": PERP_PATH,
        "execution_price_source": "spot_and_perp_5m_klines_close",
        "funding_source": "unreachable_fapi_451_and_not_in_monthly_archives_nan_control_only",
        "storage": "per_asset_float32_npz_shards",
        "f32_legs": list(F32_LEGS),
        "shard_dir": str(OUT_DIR.relative_to(ROOT)),
        "months_dir": str(MONTHS_DIR.relative_to(ROOT)),
        "months_manifest": str(MANIFEST.relative_to(ROOT)),
        "resumable": True,
        "resumability_scheme": "per_symbol_market_month_shard_skip_on_manifest",
        "shard_sha256": written["sha"],
        "shard_bytes": written["bytes"],
        "total_shard_bytes": int(total_bytes),
        "max_shard_bytes": int(max_shard),
        "push_limit_bytes": PUSH_LIMIT_BYTES,
        "cache_budget_bytes": CACHE_BUDGET_BYTES,
        "under_push_limit": bool(max_shard < PUSH_LIMIT_BYTES),
        "under_cache_budget": bool(total_bytes < CACHE_BUDGET_BYTES),
        "dropped_symbols": dropped,
        "cache_format": "per_asset_float32_npz_no_pandas",
        "real_data_only": True,
        "fabricated_data": False,
        "fetch_real_data_only": True,
        "fetch_fabricated_data": False,
        "executed_fills": False,
    }
    manifest_sha = hashlib.sha256(
        json.dumps({s: written["sha"][s] for s in sorted(written["sha"])}, sort_keys=True).encode()
    ).hexdigest()
    meta["manifest_sha256"] = manifest_sha
    OUT_META.write_text(json.dumps(meta, indent=2) + "\n")

    per_symbol = {}
    for s in symbols:
        per_symbol[s] = ({
            "status": "ok", "n_bars": n_grid,
            "shard": str((OUT_DIR / f"{s}.npz").relative_to(ROOT)),
            "shard_sha256": written["sha"][s], "shard_bytes": written["bytes"][s],
        } if s in selected else {"status": "excluded", "exclusion_reason": "unavailable_or_dropped"})

    provenance = {
        "generated_at_utc": ts, "campaign": 314, "part": "provenance",
        "source_host": ARCHIVE_HOST,
        "spot_klines_endpoint": SPOT_PATH, "perp_klines_endpoint": PERP_PATH,
        "interval": INTERVAL, "bar_ms": BAR_MS,
        "window_start_month": args.start_month, "window_end_month": args.end_month,
        "n_months": len(months), "markets": list(MARKETS), "symbols": selected,
        "per_symbol": per_symbol,
        "grid_construction": "intersection_of_symbol_spot_and_perp_5m_kline_bars",
        "n_nominal_grid_bars": int(nominal), "n_grid_bars": n_grid,
        "execution_price_source": "spot_and_perp_5m_klines_close",
        "funding_source": "unreachable_fapi_451_and_not_in_monthly_archives_nan_control_only",
        "raw_csv_discarded_after_feature_extraction": True,
        "resumable": True,
        "real_data_only": True, "fabricated_data": False,
        "fetch_real_data_only": True, "fetch_fabricated_data": False,
        "executed_fills": False,
        "manifest_sha256": manifest_sha,
        "gap_bar_policy": "bars without a spot or perp 5m kline are dropped from the common grid (never filled)",
        "funding_leg_policy": "funding_rate emitted all-NaN (control only, excluded from PnL)",
        "reachability_note": "spot AND USDT-M perp 5m klines verified HTTP 206 live 2026-11-15 across edge months (2023-06, 2025-12); 404 months are pre-listing exclusions, not outages",
    }
    OUT_PROV.write_text(json.dumps(provenance, indent=2) + "\n")

    print(json.dumps({
        "campaign": 314, "part": "ingest", "interval": INTERVAL,
        "symbols_ok": selected, "n_symbols": len(selected),
        "n_months": len(months), "n_grid_bars": n_grid,
        "n_nominal_grid_bars": int(nominal),
        "grid_start_utc": meta["grid_start_utc"], "grid_end_utc": meta["grid_end_utc"],
        "max_shard_mb": round(max_shard / 1e6, 2),
        "total_shard_mb": round(total_bytes / 1e6, 2),
        "under_cache_budget": meta["under_cache_budget"],
        "dropped_symbols": dropped,
        "manifest_sha256": manifest_sha,
        "n_month_errors": len(errors), "month_errors": errors[:20],
        "shard_dir": str(OUT_DIR.relative_to(ROOT)),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())