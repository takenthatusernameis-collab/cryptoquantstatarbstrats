#!/usr/bin/env python3
"""C311 — ingest REAL Binance COIN-M inverse perpetual ``aggTrades`` + native
``5m`` klines and build per-perp NATIVE 5m order-flow-imbalance (OFI) feature
panels for the C311 COIN-M inverse CROSS-SECTIONAL OFI-carry stat-arb campaign.

This is a genuinely new economic family, not a re-skin of any frozen campaign:

- C310 ingested the SAME COIN-M aggTrades but aggregated them to **1h** bars
  (BAR_MS = 3_600_000). That 1h campaign was a COMPLETE FORMAL NEGATIVE
  (``20261115T111243Z``, 0/504 survive Holm+BH, convexity-dominated).
- C311 re-ingests the raw trades at **NATIVE 5m** (BAR_MS = 300_000). OFI signal
  decay/holding at 5m is a distinct microstructure hypothesis that does not
  transfer from the 1h result. The C310 1h cache cannot be re-aggregated to 5m
  (its raw trades are discarded per month), so this is a fresh, streaming,
  per-month re-download of the full 48-month window.

Data (real, fail-closed; ``fapi`` REST is HTTP 451 and is NOT used):

- ``https://data.binance.vision/data/futures/cm/monthly/aggTrades/<SYM>/<SYM>-aggTrades-YYYY-MM.zip``
  -> per-5m-bar buy/sell/signed volume, trade_count, trade_sign_sum, notional, vwap.
- ``https://data.binance.vision/data/futures/cm/monthly/klines/<SYM>/5m/<SYM>-5m-YYYY-MM.zip``
  -> native 5m execution prices (close). COIN-M ``indexPriceKlines`` is HTTP 404
  and is never used.
- Universe: the 11 C307 COIN-M inverse perps. Window: 2022-07 .. 2026-06.
- Native 8h funding is a CONTROL leg only (never the C311 carry source); it is
  aligned from the verified C307 1h ``funding_rate_<SYM>`` column (forward-filled
  from the 1h grid onto the 5m grid) and excluded from total return.

Grid construction (fail-closed, never imputes execution prices):

- The COIN-M 5m klines archive has a genuine ~4-day outage for every symbol
  (2023-08-28 00:00 .. 2023-08-31 23:55). Execution prices are only available
  where klines exist, so the common 5m grid is the **intersection** of every
  symbol's kline bars (bars with no executable price are dropped, never filled).
- OFI aggTrades are then aligned onto that exact common grid; aggTrade-only bars
  (no kline price) are dropped and kline-only bars (no trades) carry NaN OFI legs
  (never imputed).

Storage (GitHub hard-rejects any single blob > 100 MB; a 5m panel of ~420k bars
x 11 perps cannot fit one pickle, so we shard per asset):

- ``data/cache/campaign311_coinm_ofi_5m/<SYM>.npz``  (float32 ndarrays, ~13 MB each)
- ``data/cache/campaign311_coinm_ofi_5m.meta.json``
- ``data/cache/campaign311_coinm_ofi_5m.provenance.json``

Every shard and the meta/provenance carry ``real_data_only:true``,
``fabricated_data:false``, ``executed_fills:false`` and a SHA256-from-bytes.
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
OUT_DIR = CACHE / "campaign311_coinm_ofi_5m"
OUT_META = CACHE / "campaign311_coinm_ofi_5m.meta.json"
OUT_PROV = CACHE / "campaign311_coinm_ofi_5m.provenance.json"

C307_CACHE = CACHE / "campaign307_coinm_multiasset_term_structure_carry.pkl"
C307_META = CACHE / "campaign307_coinm_multiasset_term_structure_carry.meta.json"

ARCHIVE_HOST = "https://data.binance.vision"
AGGTRADES_PATH = "/data/futures/cm/monthly/aggTrades/{sym}/{sym}-aggTrades-{month}.zip"
KLINES_PATH = "/data/futures/cm/monthly/klines/{sym}/5m/{sym}-5m-{month}.zip"

PERPS = (
    "BTCUSD_PERP", "ETHUSD_PERP", "ADAUSD_PERP", "LTCUSD_PERP", "XRPUSD_PERP",
    "BCHUSD_PERP", "LINKUSD_PERP", "TRXUSD_PERP", "ETCUSD_PERP", "XLMUSD_PERP",
    "DOTUSD_PERP",
)

DEFAULT_START = "2022-07"
DEFAULT_END = "2026-06"

INTERVAL = "5m"
BAR_MS = 300_000  # 5 minutes in milliseconds

AGGTRADE_COLUMNS = [
    "agg_trade_id", "price", "quantity", "first_trade_id",
    "last_trade_id", "transact_time", "is_buyer_maker",
]
AGGTRADE_USECOLS = ["price", "quantity", "transact_time", "is_buyer_maker"]
KLINE_COLUMNS = [
    "open_time", "open", "high", "low", "close", "volume", "close_time",
    "quote_volume", "count", "taker_buy_volume", "taker_buy_quote_volume", "ignore",
]

F32_LEGS = (
    "signed_volume", "total_volume", "trade_count", "trade_sign_sum",
    "notional", "vwap", "perp_close", "funding_rate",
)

PUSH_LIMIT_BYTES = 100_000_000  # GitHub hard-rejects any blob > 100 MB
HTTP_RETRIES = 6  # linear backoff 1s*k (flaky archive host)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def to_ms(idx: pd.DatetimeIndex) -> np.ndarray:
    """UTC epoch milliseconds as int64, robust to pandas datetime resolution."""
    return idx.tz_convert("UTC").tz_localize(None).as_unit("ms").asi8


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


def nominal_grid(start: str, end: str) -> pd.DatetimeIndex:
    first = pd.Timestamp(f"{start}-01 00:00:00", tz="UTC")
    ey, em = int(end[:4]), int(end[5:7])
    if em == 12:
        last = pd.Timestamp(f"{ey + 1:04d}-01 00:00:00", tz="UTC") - pd.Timedelta(minutes=5)
    else:
        last = pd.Timestamp(f"{ey:04d}-{em + 1:02d}-01 00:00:00", tz="UTC") - pd.Timedelta(minutes=5)
    return pd.date_range(first, last, freq="5min", tz="UTC")


def _http_get(url: str, timeout: float) -> tuple[int, bytes]:
    last_exc: Exception | None = None
    for attempt in range(1, HTTP_RETRIES + 1):
        req = urllib.request.Request(url, method="GET", headers={"User-Agent": "kilo-c311-ingest"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return int(resp.status), resp.read()
        except urllib.error.HTTPError as exc:  # 404/451: do not retry
            return int(exc.code), b""
        except Exception as exc:  # noqa: BLE001  transient network: retry w/ backoff
            last_exc = exc
            time.sleep(1.0 * attempt)
    raise RuntimeError(f"GET failed after {HTTP_RETRIES} attempts: {url}: {last_exc}")


def _first_line(raw: bytes) -> bytes:
    nl = raw.find(b"\n")
    return raw[: nl if nl >= 0 else len(raw)]


def read_aggtrades_zip(zip_bytes: bytes) -> pd.DataFrame:
    zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    raw = zf.read(zf.namelist()[0])
    has_header = b"agg_trade_id" in _first_line(raw)
    if has_header:
        df = pd.read_csv(io.BytesIO(raw), usecols=AGGTRADE_USECOLS)
    else:
        df = pd.read_csv(io.BytesIO(raw), header=None, names=AGGTRADE_COLUMNS,
                         usecols=AGGTRADE_USECOLS)
    for c in ("price", "quantity", "transact_time"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    if df["is_buyer_maker"].dtype == object:
        df["is_buyer_maker"] = df["is_buyer_maker"].astype(str).str.strip().str.lower().map(
            {"true": True, "false": False}
        )
    else:
        df["is_buyer_maker"] = df["is_buyer_maker"].astype(bool)
    return df


def read_klines_zip(zip_bytes: bytes) -> pd.Series:
    zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    raw = zf.read(zf.namelist()[0])
    has_header = b"open_time" in _first_line(raw)
    if has_header:
        df = pd.read_csv(io.BytesIO(raw), usecols=["open_time", "close"])
    else:
        df = pd.read_csv(io.BytesIO(raw), header=None, names=KLINE_COLUMNS,
                         usecols=["open_time", "close"])
    ot = pd.to_numeric(df["open_time"], errors="coerce")
    close = pd.to_numeric(df["close"], errors="coerce")
    dt = pd.to_datetime(ot.to_numpy(dtype="int64"), unit="ms", utc=True)
    s = pd.Series(close.to_numpy(dtype=float), index=dt)
    return s[~s.index.duplicated(keep="last")].sort_index()


def aggregate_month_5m(df: pd.DataFrame) -> pd.DataFrame:
    tt = df["transact_time"].to_numpy(dtype="int64")
    bar_ms = (tt // BAR_MS) * BAR_MS
    dt = pd.to_datetime(bar_ms, unit="ms", utc=True)
    qty = df["quantity"].to_numpy(dtype=float)
    price = df["price"].to_numpy(dtype=float)
    buy = ~df["is_buyer_maker"].to_numpy(dtype=bool)
    sign = np.where(buy, 1.0, -1.0)
    notional = qty * price
    g = pd.DataFrame({
        "bar": dt,
        "buy_volume": np.where(buy, qty, 0.0),
        "sell_volume": np.where(~buy, qty, 0.0),
        "signed_volume": np.where(buy, qty, -qty),
        "trade_count": 1.0,
        "trade_sign_sum": sign,
        "notional": notional,
    })
    agg = g.groupby("bar", sort=True).agg(
        buy_volume=("buy_volume", "sum"),
        sell_volume=("sell_volume", "sum"),
        signed_volume=("signed_volume", "sum"),
        trade_count=("trade_count", "sum"),
        trade_sign_sum=("trade_sign_sum", "sum"),
        notional=("notional", "sum"),
    ).reset_index().set_index("bar").sort_index()
    tot_qty = agg["buy_volume"] + agg["sell_volume"]
    agg["vwap"] = np.where(tot_qty > 0, agg["notional"] / tot_qty, np.nan)
    return agg


def _funding_on_grid(funding_1h: np.ndarray, f1h_ms: np.ndarray, grid_ms: np.ndarray) -> np.ndarray:
    """Forward-fill native 8h funding from the C307 1h grid onto the 5m grid."""
    idx = np.searchsorted(f1h_ms, grid_ms, side="right") - 1
    out = np.full(len(grid_ms), np.nan, dtype=float)
    valid = idx >= 0
    out[valid] = funding_1h[idx[valid]]
    return out


def prefetch_close(symbol: str, months: list[str], timeout: float) -> dict:
    """Download 5m klines for one symbol; return its close series + per-month log."""
    detail: dict = {"symbol": symbol, "per_month": [], "accepted_months": []}
    frames: list[pd.Series] = []
    for m in months:
        url = ARCHIVE_HOST + KLINES_PATH.format(sym=symbol, month=m)
        try:
            status, data = _http_get(url, timeout)
        except Exception as exc:  # noqa: BLE001
            detail["per_month"].append({"month": m, "url": url, "status": -1,
                                        "ok": False, "reason": repr(exc)[:200]})
            detail["status"] = "excluded"
            detail["exclusion_reason"] = f"klines month {m} fetch error"
            return detail
        if status != 200:
            detail["per_month"].append({"month": m, "url": url, "status": status,
                                        "ok": False, "reason": f"http_{status}"})
            detail["status"] = "excluded"
            detail["exclusion_reason"] = f"klines month {m} http status {status}"
            return detail
        s = read_klines_zip(data)
        if len(s) == 0:
            detail["per_month"].append({"month": m, "url": url, "status": status,
                                        "ok": False, "reason": "empty klines"})
            detail["status"] = "excluded"
            detail["exclusion_reason"] = f"klines month {m} empty"
            return detail
        detail["per_month"].append({"month": m, "status": status, "bars": int(len(s)), "ok": True})
        detail["accepted_months"].append(m)
        frames.append(s)
        del data
    close = pd.concat(frames, axis=0).sort_index()
    close = close[~close.index.duplicated(keep="last")]
    detail["status"] = "ok"
    detail["close"] = close
    detail["n_bars"] = int(len(close))
    return detail


def build_symbol(symbol: str, months: list[str], grid_index: pd.DatetimeIndex,
                 grid_ms: np.ndarray, close: pd.Series, funding_1h: np.ndarray,
                 f1h_ms: np.ndarray, timeout: float) -> dict:
    detail: dict = {"symbol": symbol, "per_month": [], "accepted_months": []}
    frames: list[pd.DataFrame] = []
    for m in months:
        url = ARCHIVE_HOST + AGGTRADES_PATH.format(sym=symbol, month=m)
        try:
            status, data = _http_get(url, timeout)
        except Exception as exc:  # noqa: BLE001
            detail["per_month"].append({"month": m, "url": url, "status": -1,
                                        "ok": False, "reason": repr(exc)[:200]})
            detail["status"] = "excluded"
            detail["exclusion_reason"] = f"aggTrades month {m} fetch error"
            return detail
        if status != 200:
            detail["per_month"].append({"month": m, "url": url, "status": status,
                                        "ok": False, "reason": f"http_{status}"})
            detail["status"] = "excluded"
            detail["exclusion_reason"] = f"aggTrades month {m} http status {status}"
            return detail
        df = read_aggtrades_zip(data)
        agg = aggregate_month_5m(df)
        if len(agg) == 0:
            detail["per_month"].append({"month": m, "url": url, "status": status,
                                        "ok": False, "reason": "empty after 5m aggregation"})
            detail["status"] = "excluded"
            detail["exclusion_reason"] = f"aggTrades month {m} empty after aggregation"
            return detail
        if not bool(np.isfinite(agg["vwap"].to_numpy(dtype=float)).all()):
            detail["per_month"].append({"month": m, "url": url, "status": status,
                                        "ok": False, "reason": "non-finite vwap"})
            detail["status"] = "excluded"
            detail["exclusion_reason"] = f"aggTrades month {m} non-finite vwap present"
            return detail
        if not bool((agg["trade_count"].to_numpy(dtype=float) > 0).all()):
            detail["per_month"].append({"month": m, "url": url, "status": status,
                                        "ok": False, "reason": "zero trade_count bar"})
            detail["status"] = "excluded"
            detail["exclusion_reason"] = f"aggTrades month {m} zero trade_count bar"
            return detail
        detail["per_month"].append({"month": m, "url": url, "status": status,
                                    "rows": int(len(df)), "bars": int(len(agg)), "ok": True})
        detail["accepted_months"].append(m)
        frames.append(agg)
        del df, agg, data

    ofi_all = pd.concat(frames, axis=0).sort_index()
    ofi_all = ofi_all[~ofi_all.index.duplicated(keep="last")].reindex(grid_index)
    close_all = close.reindex(grid_index)

    perp_close = close_all.to_numpy(dtype=float)
    if not bool(np.isfinite(perp_close).all()) or not bool((perp_close > 0).all()):
        detail["status"] = "excluded"
        detail["exclusion_reason"] = "5m klines close non-finite/non-positive on common grid"
        return detail

    n_gap = int(ofi_all["trade_count"].isna().sum())
    gap_bars = [str(b) for b in ofi_all.index[ofi_all["trade_count"].isna().values]]
    n_trade_bars = int(ofi_all["trade_count"].notna().sum())
    if n_trade_bars == 0:
        detail["status"] = "excluded"
        detail["exclusion_reason"] = "no trade bars in grid"
        return detail

    total_volume = (ofi_all["buy_volume"] + ofi_all["sell_volume"]).to_numpy(dtype=float)
    signed_volume = ofi_all["signed_volume"].to_numpy(dtype=float)
    trade_count = ofi_all["trade_count"].to_numpy(dtype=float)
    trade_sign_sum = ofi_all["trade_sign_sum"].to_numpy(dtype=float)
    notional = ofi_all["notional"].to_numpy(dtype=float)
    vwap = ofi_all["vwap"].to_numpy(dtype=float)
    funding = _funding_on_grid(funding_1h, f1h_ms, grid_ms)

    tc_ts = pd.Series(np.nan_to_num(trade_count), index=grid_index)
    daily_counts = {str(d.date()): int(v) for d, v in tc_ts.groupby(tc_ts.index.floor("D")).sum().items()}

    detail.update({
        "status": "ok",
        "n_bars": int(len(grid_index)),
        "n_trade_bars": n_trade_bars,
        "n_gap_bars": n_gap,
        "gap_bars": gap_bars,
        "daily_trade_counts": daily_counts,
        "signed_volume": signed_volume,
        "total_volume": total_volume,
        "trade_count": trade_count,
        "trade_sign_sum": trade_sign_sum,
        "notional": notional,
        "vwap": vwap,
        "perp_close": perp_close,
        "funding_rate": funding,
    })
    return detail


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--start-month", default=DEFAULT_START)
    ap.add_argument("--end-month", default=DEFAULT_END)
    ap.add_argument("--symbols", default="all", help="comma list or 'all'")
    ap.add_argument("--timeout", type=float, default=180.0)
    ap.add_argument("--workers", type=int, default=3)
    args = ap.parse_args(argv)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    CACHE.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if not C307_META.exists():
        raise SystemExit(f"FATAL: C307 meta missing: {C307_META}")
    c307_meta = json.loads(C307_META.read_text())
    if c307_meta.get("real_data_only") is not True or c307_meta.get("fabricated_data") is not False:
        raise SystemExit("FATAL: C307 cache provenance flags invalid")
    if c307_meta.get("executed_fills") is not False:
        raise SystemExit("FATAL: C307 cache executed_fills must be false")

    symbols = list(PERPS) if args.symbols == "all" else [s.strip() for s in args.symbols.split(",") if s.strip()]
    months = month_range(args.start_month, args.end_month)

    with open(C307_CACHE, "rb") as f:
        c307 = pickle.load(f)
    leg_b = c307["leg_b"]
    lb_symbols = list(leg_b.get("symbols") or [])
    c307_index = pd.DatetimeIndex(np.asarray(leg_b["index"]))
    if c307_index.tz is None:
        c307_index = c307_index.tz_localize("UTC")
    f1h_ms = to_ms(c307_index)
    for s in symbols:
        if s not in lb_symbols:
            raise SystemExit(f"FATAL: {s} not in C307 leg_b symbols")

    def _funding(sym: str) -> np.ndarray:
        return np.asarray(leg_b[f"funding_rate_{sym}"], dtype=float)

    # ---- Phase 1: prefetch 5m klines for every symbol, intersect to common grid ----
    close_map: dict[str, pd.Series] = {}
    kline_excluded: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futs = {pool.submit(prefetch_close, s, months, args.timeout): s for s in symbols}
        for fut in as_completed(futs):
            d = fut.result()
            if d.get("status") == "ok":
                close_map[d["symbol"]] = d["close"]
            else:
                kline_excluded[d["symbol"]] = d.get("exclusion_reason", "excluded")
    if not close_map:
        raise SystemExit(f"FATAL: no symbol has usable 5m klines. {json.dumps(kline_excluded)}")

    # common grid = intersection of all symbols' kline bars
    common_ms = None
    for s, close in close_map.items():
        ms = to_ms(close.index)
        common_ms = ms if common_ms is None else np.intersect1d(common_ms, ms, assume_unique=False)
    grid_index = pd.DatetimeIndex(pd.to_datetime(np.sort(common_ms), unit="ms", utc=True))
    grid_ms = to_ms(grid_index)
    n_nominal = len(nominal_grid(args.start_month, args.end_month))
    if len(grid_index) < 0.8 * n_nominal:
        raise SystemExit(f"FATAL: common 5m grid has {len(grid_index)} bars < 80% of nominal {n_nominal}")

    # ---- Phase 2: build OFI panels on the common grid ----
    built: dict[str, dict] = {}
    build_targets = [s for s in symbols if s in close_map]
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futs = {}
        for s in build_targets:
            futs[pool.submit(build_symbol, s, months, grid_index, grid_ms,
                             close_map[s], _funding(s), f1h_ms, args.timeout)] = s
        for fut in as_completed(futs):
            d = fut.result()
            built[d["symbol"]] = d

    selected = [s for s in symbols if built.get(s, {}).get("status") == "ok"]
    excluded = dict(kline_excluded)
    for s in symbols:
        if s in built and built[s].get("status") != "ok":
            excluded[s] = built[s].get("exclusion_reason", built[s].get("status"))
    if not selected:
        raise SystemExit(f"FATAL: no asset has a usable real window. Excluded: {json.dumps(excluded)}")

    shard_sha: dict[str, str] = {}
    shard_bytes: dict[str, int] = {}
    index_ms = grid_ms.astype(np.int64)
    for s in selected:
        d = built[s]
        arrays = {"index_ms": index_ms}
        for leg in F32_LEGS:
            arrays[leg] = np.asarray(d[leg], dtype=np.float32)
        sp = OUT_DIR / f"{s}.npz"
        np.savez_compressed(sp, **arrays)
        shard_sha[s] = sha256_file(sp)
        shard_bytes[s] = int(sp.stat().st_size)

    max_shard = max(shard_bytes.values())
    total_bytes = sum(shard_bytes.values())
    if max_shard >= PUSH_LIMIT_BYTES:
        raise SystemExit(f"FATAL: shard {max_shard/1e6:.2f} MB >= push limit")

    n_total_bars = sum(int(built[s]["n_bars"]) for s in selected)
    n_total_trade = sum(int(built[s]["n_trade_bars"]) for s in selected)
    n_total_gap = sum(int(built[s]["n_gap_bars"]) for s in selected)

    meta = {
        "generated_at_utc": ts,
        "campaign": 311,
        "part": "ingest",
        "interval": INTERVAL,
        "bar_ms": BAR_MS,
        "source_interval": "coin_m_aggTrades_ms",
        "symbols": selected,
        "n_symbols": len(selected),
        "n_universe": len(symbols),
        "total_bars": int(n_total_bars),
        "total_trade_bars": int(n_total_trade),
        "total_gap_bars": int(n_total_gap),
        "window_start_month": args.start_month,
        "window_end_month": args.end_month,
        "grid_start_utc": str(grid_index[0]),
        "grid_end_utc": str(grid_index[-1]),
        "n_grid_bars": int(len(grid_index)),
        "n_nominal_grid_bars": int(n_nominal),
        "grid_construction": "intersection_of_symbol_5m_kline_bars",
        "source_host": ARCHIVE_HOST,
        "aggtrades_endpoint": AGGTRADES_PATH,
        "klines_endpoint": KLINES_PATH,
        "execution_price_source": "coin_m_5m_klines_close",
        "funding_source": "C307_leg_b_native_8h_funding_control_only",
        "c307_cache": str(C307_CACHE.relative_to(ROOT)),
        "c307_cache_sha256": sha256_file(C307_CACHE),
        "storage": "per_asset_float32_npz_shards",
        "f32_legs": list(F32_LEGS),
        "shard_dir": str(OUT_DIR.relative_to(ROOT)),
        "shard_sha256": shard_sha,
        "shard_bytes": shard_bytes,
        "total_shard_bytes": int(total_bytes),
        "max_shard_bytes": int(max_shard),
        "push_limit_bytes": PUSH_LIMIT_BYTES,
        "under_push_limit": bool(max_shard < PUSH_LIMIT_BYTES),
        "cache_format": "per_asset_float32_npz_no_pandas",
        "real_data_only": True,
        "fabricated_data": False,
        "fetch_real_data_only": True,
        "fetch_fabricated_data": False,
        "executed_fills": False,
    }
    manifest = {s: shard_sha[s] for s in sorted(shard_sha)}
    meta["manifest_sha256"] = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()
    OUT_META.write_text(json.dumps(meta, indent=2) + "\n")

    per_symbol = {}
    for s in symbols:
        if s in selected:
            pa = built[s]
            per_symbol[s] = {
                "status": "ok",
                "n_bars": pa["n_bars"], "n_trade_bars": pa["n_trade_bars"],
                "n_gap_bars": pa["n_gap_bars"], "accepted_months": pa["accepted_months"],
                "n_days_with_trades": len(pa["daily_trade_counts"]),
                "shard": str((OUT_DIR / f"{s}.npz").relative_to(ROOT)),
                "shard_sha256": shard_sha[s], "shard_bytes": shard_bytes[s],
            }
        else:
            per_symbol[s] = {"status": "excluded", "exclusion_reason": excluded.get(s)}
    provenance = {
        "generated_at_utc": ts,
        "campaign": 311,
        "part": "provenance",
        "source_host": ARCHIVE_HOST,
        "aggtrades_endpoint": AGGTRADES_PATH,
        "klines_endpoint": KLINES_PATH,
        "interval": INTERVAL,
        "bar_ms": BAR_MS,
        "window_start_month": args.start_month,
        "window_end_month": args.end_month,
        "n_months": len(months),
        "symbols": selected,
        "excluded": excluded,
        "per_symbol": per_symbol,
        "grid_construction": "intersection_of_symbol_5m_kline_bars",
        "n_nominal_grid_bars": int(n_nominal),
        "n_grid_bars": int(len(grid_index)),
        "execution_price_source": "coin_m_5m_klines_close",
        "funding_source": "C307_leg_b_native_8h_funding_control_only",
        "c307_cache_sha256": sha256_file(C307_CACHE),
        "real_data_only": True,
        "fabricated_data": False,
        "fetch_real_data_only": True,
        "fetch_fabricated_data": False,
        "executed_fills": False,
        "manifest_sha256": meta["manifest_sha256"],
        "gap_bar_policy": "bars without 5m kline execution price are dropped (never filled); "
                          "kline-only bars carry NaN OFI legs (never imputed)",
    }
    OUT_PROV.write_text(json.dumps(provenance, indent=2) + "\n")

    print(json.dumps({
        "campaign": 311,
        "part": "ingest",
        "interval": INTERVAL,
        "symbols_ok": selected,
        "n_symbols": len(selected),
        "n_months": len(months),
        "n_grid_bars": int(len(grid_index)),
        "n_nominal_grid_bars": int(n_nominal),
        "total_trade_bars": int(n_total_trade),
        "total_gap_bars": int(n_total_gap),
        "max_shard_mb": round(max_shard / 1e6, 2),
        "total_shard_mb": round(total_bytes / 1e6, 2),
        "manifest_sha256": meta["manifest_sha256"],
        "excluded": excluded,
        "shard_dir": str(OUT_DIR.relative_to(ROOT)),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())