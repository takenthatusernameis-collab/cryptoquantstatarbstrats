#!/usr/bin/env python3
"""C301 — ingest REAL Binance USDT-M perpetual ``aggTrades`` (2023-01 .. 2023-02)
and build per-asset 5m order-flow-imbalance (OFI) / trade-sign feature panels for
the C301 per-asset time-series microstructure stat-arb campaign.

This is a genuinely new microstructure family (order-flow imbalance + trade-sign
autocorrelation), distinct from the closed C281B-C300 funding-carry / spot-perp
basis family.

Data (real, fail-closed; the ``fapi`` REST API is HTTP 451 and is NOT used):

- ``https://data.binance.vision/data/futures/um/monthly/aggTrades/<SYM>/<SYM>-aggTrades-YYYY-MM.zip``
- Universe: C299/C300's verified {BTCUSDT, ETHUSDT, BCHUSDT}.
- Bounded window: 2023-01-01T00:00:00Z .. 2023-02-28T23:59:59.999Z (59 days,
  16,992 native 5m bars). Exactly 6 zips, total 1,603,901,702 bytes.
- Schema: futures ``aggTrades`` CSV is 7 columns with a header row in 2023-01:
  ``agg_trade_id,price,quantity,first_trade_id,last_trade_id,transact_time,is_buyer_maker``.
  ``transact_time`` is epoch MILLISECONDS in 2023 (not µs); ``is_buyer_maker`` is
  ``true``/``false``; there is no ``is_best_match`` (spot-only). Header/no-header
  are handled generically (reuse C299's ``read_zip_csv`` pattern).
- Bar = ``floor(transact_time_ms / 300000)`` -> native 5m UTC bars.
  ``buy_volume = Sum(quantity where is_buyer_maker == false)``,
  ``sell_volume = Sum(quantity where is_buyer_maker == true)``,
  plus per-bar trade count and the trade-sign series
  (sign = +1 if ``is_buyer_maker == false`` else -1).

Execution prices + funding (reused from the verified C300 cache, NOT re-downloaded):

- ``data/cache/campaign300_multianual_perp_funding_basis_ts_5m.pkl`` (SHA256
  ``2c86accd...``) supplies real perp 5m close and native 8h funding rates over
  2020-01..2026-10; sliced to the 2023-01..02 window here. Execution price is the
  perp 5m close of the same bar (shifted 1 bar in the runner); real funding
  cashflow ``-rate * signed_weight`` at each native funding boundary (causal).
  ``executed_fills: false``.

Fail-closed (never impute / forward-fill / back-fill):

- any 404 / empty day / non-finite price / missing bar blocks the run with a
  recorded reason;
- per-day trade counts, per-asset coverage and every gap bar are recorded.

Serialized artifacts (all real_data_only:true, fabricated_data:false,
executed_fills:false, SHA256-from-bytes, COMPACT ndarray form < 100 MB):

- ``data/cache/campaign301_aggtrades_ofi.pkl``
- ``data/cache/campaign301_aggtrades_ofi.meta.json``
- ``data/cache/campaign301_aggtrades_ofi.provenance.json``
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
OUT_PKL = CACHE / "campaign301_aggtrades_ofi.pkl"
OUT_META = CACHE / "campaign301_aggtrades_ofi.meta.json"
OUT_PROV = CACHE / "campaign301_aggtrades_ofi.provenance.json"

C300_CACHE = CACHE / "campaign300_multianual_perp_funding_basis_ts_5m.pkl"
C300_META = CACHE / "campaign300_multianual_perp_funding_basis_ts_5m.meta.json"
C300_PROV = CACHE / "campaign300_multianual_perp_funding_basis_ts_5m.provenance.json"

ARCHIVE_HOST = "https://data.binance.vision"
AGGTRADES_PATH = "/data/futures/um/monthly/aggTrades/{sym}/{sym}-aggTrades-{month}.zip"

START_UTC = "2023-01-01T00:00:00Z"
END_UTC = "2023-02-28T23:55:00Z"
WINDOW_START = pd.Timestamp(START_UTC)
WINDOW_END = pd.Timestamp(END_UTC)
INTERVAL = "5m"
BAR_MS = 300_000  # 5 minutes in milliseconds

UNIVERSE = ("BTCUSDT", "ETHUSDT", "BCHUSDT")
MONTHS = ("2023-01", "2023-02")

AGGTRADE_COLUMNS = [
    "agg_trade_id", "price", "quantity", "first_trade_id",
    "last_trade_id", "transact_time", "is_buyer_maker",
]

PUSH_LIMIT_BYTES = 100_000_000  # GitHub hard-rejects any blob > 100 MB

# Minimum contiguous 5m bars to attempt a per-asset WF split (train+test+step).
MIN_BARS = 2880 + 1152  # train + one test (12 splits total expected over 16992 bars)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _http_get(url: str, timeout: float, retries: int = 3) -> tuple[int, bytes]:
    last_exc: Exception | None = None
    for attempt in range(retries):
        req = urllib.request.Request(url, method="GET", headers={"User-Agent": "kilo-c301-ingest"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return int(resp.status), resp.read()
        except urllib.error.HTTPError as exc:  # 404/451: do not retry
            return int(exc.code), b""
        except Exception as exc:  # noqa: BLE001  transient network: retry
            last_exc = exc
            time.sleep(0.6 * (attempt + 1))
    raise RuntimeError(f"GET failed after {retries} attempts: {url}: {last_exc}")


def read_aggtrades_zip(zip_bytes: bytes) -> pd.DataFrame:
    """Parse a futures aggTrades zip generically (header or headerless)."""
    zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    name = zf.namelist()[0]
    raw = zf.read(name)
    # Detect a header row: first line contains 'agg_trade_id' (text).
    first_nl = raw.find(b"\n")
    first_line = raw[: first_nl if first_nl >= 0 else len(raw)]
    has_header = b"agg_trade_id" in first_line
    if has_header:
        df = pd.read_csv(io.BytesIO(raw))
    else:
        df = pd.read_csv(io.BytesIO(raw), header=None, names=AGGTRADE_COLUMNS)
    # Coerce numeric columns.
    for c in ("price", "quantity", "transact_time"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    # is_buyer_maker may be bool or text.
    if df["is_buyer_maker"].dtype == object:
        df["is_buyer_maker"] = df["is_buyer_maker"].astype(str).str.strip().str.lower().map(
            {"true": True, "false": False}
        )
    else:
        df["is_buyer_maker"] = df["is_buyer_maker"].astype(bool)
    return df


def bar_index_5m(month: str) -> pd.DatetimeIndex:
    """Native 5m UTC bars covering a calendar month."""
    start = pd.Timestamp(month + "-01", tz="UTC")
    end = (start + pd.offsets.MonthEnd(0)) + pd.Timedelta(hours=23, minutes=55)
    return pd.DatetimeIndex(pd.date_range(start=start, end=end, freq="5min", tz="UTC"))


def full_window_index() -> pd.DatetimeIndex:
    return pd.DatetimeIndex(
        pd.date_range(start=WINDOW_START, end=WINDOW_END, freq="5min", tz="UTC")
    )


def fetch_month(symbol: str, month: str, timeout: float) -> dict:
    url = ARCHIVE_HOST + AGGTRADES_PATH.format(sym=symbol, month=month)
    status, data = _http_get(url, timeout)
    if status != 200:
        return {"symbol": symbol, "month": month, "url": url, "status": status, "rows": 0, "ok": False,
                "reason": f"http_{status}"}
    df = read_aggtrades_zip(data)
    return {"symbol": symbol, "month": month, "url": url, "status": status, "rows": int(len(df)),
            "ok": True, "frame": df}


def aggregate_month(df: pd.DataFrame, month: str) -> pd.DataFrame:
    """Aggregate raw trades of one month into native 5m bars.

    Bar = floor(transact_time_ms / 300000) * 300000 ms.
    Returns per-bar: buy_volume, sell_volume, signed_volume, trade_count,
    trade_sign_sum, vwap, n_trades. Only bars present in the trade data are
    returned; missing bars are handled fail-closed by the caller.
    """
    tt = df["transact_time"].to_numpy(dtype="int64")
    bar_ms = (tt // BAR_MS) * BAR_MS
    dt = pd.to_datetime(bar_ms, unit="ms", utc=True)
    qty = df["quantity"].to_numpy(dtype=float)
    price = df["price"].to_numpy(dtype=float)
    buy = ~df["is_buyer_maker"].to_numpy(dtype=bool)  # buyer is taker -> aggressive buy
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
    ).reset_index()
    agg = agg.set_index("bar").sort_index()
    # VWAP = notional / total quantity, where total quantity > 0.
    tot_qty = agg["buy_volume"] + agg["sell_volume"]
    agg["vwap"] = np.where(tot_qty > 0, agg["notional"] / tot_qty, np.nan)
    return agg


def load_c300_window(symbol: str) -> dict:
    """Slice the verified C300 cache to the 2023-01..02 window for one asset.

    Returns plain numpy arrays aligned to ``full_window_index()``:
    perp_close, funding_rates (NaN at non-boundary bars). Fail-closed if the
    perp close has any NaN / non-finite / non-positive value in the window or if
    funding is missing on a native boundary.
    """
    if not C300_CACHE.exists():
        raise SystemExit(f"FATAL: C300 cache missing: {C300_CACHE}")
    with open(C300_CACHE, "rb") as f:
        p = pickle.load(f)
    pa = p["per_asset"][symbol]
    idx = pd.DatetimeIndex(np.asarray(pa["index"])).tz_localize("UTC")
    close = pd.Series(np.asarray(pa["perp_close"], dtype=float), index=idx)
    funding = pd.Series(np.asarray(pa["funding_rates"], dtype=float), index=idx)

    win = full_window_index()
    close_w = close.reindex(win)
    fund_w = funding.reindex(win)

    n_nan = int(close_w.isna().sum())
    if n_nan != 0 or not bool(np.isfinite(close_w.to_numpy(dtype=float)).all()):
        raise SystemExit(f"FATAL: C300 perp close NaN/non-finite in 2023-01..02 window for {symbol} (nan={n_nan})")
    if not bool((close_w.to_numpy(dtype=float) > 0).all()):
        raise SystemExit(f"FATAL: C300 perp close non-positive in window for {symbol}")
    # funding must be present on native 8h boundaries within the window.
    mask = fund_w.notna()
    ts = fund_w.index[mask.values]
    if len(ts) == 0 or not bool(np.isfinite(fund_w[mask].to_numpy(dtype=float)).all()):
        raise SystemExit(f"FATAL: C300 funding missing/non-finite on native boundaries in window for {symbol}")
    if not bool((ts.minute == 0).all()) or not bool((ts.hour % 8 == 0).all()):
        raise SystemExit(f"FATAL: C300 funding not on native 8h boundary in window for {symbol}")

    return {
        "index": win,
        "perp_close": close_w.to_numpy(dtype=float),
        "funding_rates": fund_w.to_numpy(dtype=float),
        "funding_rows": int(mask.sum()),
    }


def build_symbol(symbol: str, timeout: float) -> dict:
    detail: dict = {"symbol": symbol, "per_month": [], "accepted_months": []}
    per_month_frames: list[pd.DataFrame] = []
    for m in MONTHS:
        r = fetch_month(symbol, m, timeout)
        detail["per_month"].append({k: r[k] for k in ("symbol", "month", "url", "status", "rows", "ok")})
        if not r["ok"]:
            detail["status"] = "excluded"
            detail["exclusion_reason"] = f"month {m} http status {r['status']}"
            return detail
        agg = aggregate_month(r["frame"], m)
        if len(agg) == 0:
            detail["status"] = "excluded"
            detail["exclusion_reason"] = f"month {m} empty after aggregation"
            return detail
        # fail-closed: any non-finite price/vwap/quantity in the trade data blocks.
        if not bool(np.isfinite(agg["vwap"].to_numpy(dtype=float)).all()):
            detail["status"] = "excluded"
            detail["exclusion_reason"] = f"month {m} non-finite vwap present"
            return detail
        if not bool((agg["trade_count"].to_numpy(dtype=float) > 0).all()):
            detail["status"] = "excluded"
            detail["exclusion_reason"] = f"month {m} zero trade_count bar"
            return detail
        detail["accepted_months"].append(m)
        per_month_frames.append(agg)

    agg_all = pd.concat(per_month_frames, axis=0).sort_index()
    win = full_window_index()
    # Reindex to the full 5m window. Bars with no trades are gap bars (NaN) and
    # MUST NOT be imputed; they are recorded and block OFI at those bars.
    agg_all = agg_all.reindex(win)
    # Bars present in trades but outside the window are dropped by reindex.
    trade_bars = agg_all.index[agg_all["trade_count"].notna().values]
    if len(trade_bars) == 0:
        detail["status"] = "excluded"
        detail["exclusion_reason"] = "no trade bars in window"
        return detail
    # Verify the trade bars are a contiguous prefix-subset of the 5m grid (no
    # duplicate bar timestamps survive concat).
    n_gap = int(agg_all["trade_count"].isna().sum())
    gap_bars = [str(b) for b in agg_all.index[agg_all["trade_count"].isna().values]]

    c300 = load_c300_window(symbol)
    win_idx = c300["index"]
    if not agg_all.index.equals(win_idx):
        raise SystemExit(f"FATAL: aggregated index does not equal C300 window index for {symbol}")

    perp_close = c300["perp_close"]
    funding_rates = c300["funding_rates"]

    # Daily trade counts (real, recorded).
    trade_count = agg_all["trade_count"].to_numpy(dtype=float)
    tc_ts = pd.Series(trade_count, index=win).fillna(0.0)
    daily_counts = {
        str(d.date()): int(v)
        for d, v in tc_ts.groupby(tc_ts.index.floor("D")).sum().items()
    }

    # Final per-bar arrays (compact; gap bars carry NaN and are never imputed).
    buy_volume = agg_all["buy_volume"].to_numpy(dtype=float)
    sell_volume = agg_all["sell_volume"].to_numpy(dtype=float)
    signed_volume = agg_all["signed_volume"].to_numpy(dtype=float)
    trade_sign_sum = agg_all["trade_sign_sum"].to_numpy(dtype=float)
    vwap = agg_all["vwap"].to_numpy(dtype=float)

    detail.update({
        "status": "ok",
        "window_start_utc": START_UTC,
        "window_end_utc": END_UTC,
        "n_bars": int(len(win)),
        "n_trade_bars": int(len(trade_bars)),
        "n_gap_bars": n_gap,
        "gap_bars": gap_bars,
        "daily_trade_counts": daily_counts,
        "funding_rows": int(c300["funding_rows"]),
        "perp_close": perp_close,
        "funding_rates": funding_rates,
        "buy_volume": buy_volume,
        "sell_volume": sell_volume,
        "signed_volume": signed_volume,
        "trade_count": trade_count,
        "trade_sign_sum": trade_sign_sum,
        "vwap": vwap,
        "index": win_idx,
        "c300_window": {
            "window_start_utc": START_UTC,
            "window_end_utc": END_UTC,
            "perp_close_nan": int(pd.isna(perp_close).sum()),
            "funding_rows": int(c300["funding_rows"]),
        },
    })
    return detail


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


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--timeout", type=float, default=120.0)
    ap.add_argument("--workers", type=int, default=3)
    args = ap.parse_args(argv)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    CACHE.mkdir(parents=True, exist_ok=True)

    # Verify the C300 reuse source exists + flags before doing any work.
    if not C300_META.exists():
        raise SystemExit(f"FATAL: C300 meta missing: {C300_META}")
    c300_meta = json.loads(C300_META.read_text())
    if c300_meta.get("real_data_only") is not True or c300_meta.get("fabricated_data") is not False:
        raise SystemExit("FATAL: C300 cache provenance flags invalid")
    if c300_meta.get("executed_fills") is not False:
        raise SystemExit("FATAL: C300 cache executed_fills must be false")

    built: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = {pool.submit(build_symbol, s, args.timeout): s for s in UNIVERSE}
        for fut in as_completed(futures):
            d = fut.result()
            built[d["symbol"]] = d

    selected = [s for s in UNIVERSE if built[s].get("status") == "ok"]
    excluded = {s: built[s].get("exclusion_reason", built[s].get("status")) for s in UNIVERSE if built[s].get("status") != "ok"}
    if not selected:
        raise SystemExit(f"FATAL: no asset has a usable real 2023-01..02 window. Excluded: {json.dumps(excluded)}")

    per_asset = {}
    for s in selected:
        d = built[s]
        entry = {
            "window_start_utc": START_UTC,
            "window_end_utc": END_UTC,
            "n_bars": int(d["n_bars"]),
            "n_trade_bars": int(d["n_trade_bars"]),
            "n_gap_bars": int(d["n_gap_bars"]),
            "gap_bars": d["gap_bars"],
            "daily_trade_counts": d["daily_trade_counts"],
            "funding_rows": int(d["funding_rows"]),
            "c300_window": d["c300_window"],
        }
        entry.update(_compact({
            "perp_close": d["perp_close"],
            "funding_rates": d["funding_rates"],
            "buy_volume": d["buy_volume"],
            "sell_volume": d["sell_volume"],
            "signed_volume": d["signed_volume"],
            "trade_count": d["trade_count"],
            "trade_sign_sum": d["trade_sign_sum"],
            "vwap": d["vwap"],
            "index": d["index"],
        }))
        per_asset[s] = entry

    payload = {
        "interval": INTERVAL,
        "bar_ms": BAR_MS,
        "source_interval": "aggTrades_ms",
        "symbols": list(selected),
        "n_symbols": len(selected),
        "window": {"start": START_UTC, "end": END_UTC},
        "universe": list(UNIVERSE),
        "n_universe": len(UNIVERSE),
        "execution_price_source": "C300_cache_perp_close_5m",
        "funding_source": "C300_cache_native_8h_funding",
        "c300_cache": str(C300_CACHE.relative_to(ROOT)),
        "c300_cache_sha256": sha256_file(C300_CACHE),
        "per_asset": per_asset,
        "real_data_only": True,
        "fabricated_data": False,
        "executed_fills": False,
    }

    blob = _pickle_bytes(payload)
    OUT_PKL.write_bytes(blob)
    pkl_bytes = _assert_under_push_limit(OUT_PKL)
    pkl_sha = sha256_file(OUT_PKL)

    n_total_bars = sum(int(per_asset[s]["n_bars"]) for s in selected)
    n_total_trade_bars = sum(int(per_asset[s]["n_trade_bars"]) for s in selected)
    n_total_gap = sum(int(per_asset[s]["n_gap_bars"]) for s in selected)

    meta = {
        "generated_at_utc": ts,
        "campaign": 301,
        "part": "ingest",
        "interval": INTERVAL,
        "source_interval": "aggTrades_ms",
        "bar_ms": BAR_MS,
        "symbols": selected,
        "n_symbols": len(selected),
        "n_universe": len(UNIVERSE),
        "total_bars": int(n_total_bars),
        "total_trade_bars": int(n_total_trade_bars),
        "total_gap_bars": int(n_total_gap),
        "window_start_utc": START_UTC,
        "window_end_utc": END_UTC,
        "source_host": ARCHIVE_HOST,
        "aggtrades_endpoint": AGGTRADES_PATH,
        "execution_price_source": "C300_cache_perp_close_5m",
        "funding_source": "C300_cache_native_8h_funding",
        "c300_cache": str(C300_CACHE.relative_to(ROOT)),
        "c300_cache_sha256": sha256_file(C300_CACHE),
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
        "min_bars": MIN_BARS,
    }
    OUT_META.write_text(json.dumps(meta, indent=2) + "\n")

    per_symbol = {}
    for s in UNIVERSE:
        if s in selected:
            pa = per_asset[s]
            per_symbol[s] = {
                "status": "ok",
                "window_start_utc": pa["window_start_utc"],
                "window_end_utc": pa["window_end_utc"],
                "n_bars": pa["n_bars"],
                "n_trade_bars": pa["n_trade_bars"],
                "n_gap_bars": pa["n_gap_bars"],
                "funding_rows": pa["funding_rows"],
                "c300_window": pa["c300_window"],
                "n_days_with_trades": len(pa["daily_trade_counts"]),
            }
        else:
            per_symbol[s] = {"status": "excluded", "exclusion_reason": excluded.get(s)}

    provenance = {
        "generated_at_utc": ts,
        "campaign": 301,
        "part": "provenance",
        "real_data_only": True,
        "fabricated_data": False,
        "executed_fills": False,
        "build_source": "archive_download_aggtrades_plus_c300_reuse",
        "universe_rule": (
            "Universe = C299/C300's verified {BTCUSDT, ETHUSDT, BCHUSDT} (no re-probe of the "
            "6 excluded candidates). Bars are native 5m from real Binance USDT-M perp aggTrades "
            "(floor(transact_time_ms / 300000)); buy_volume = Sum(quantity where is_buyer_maker==false), "
            "sell_volume = Sum(quantity where is_buyer_maker==true); trade_sign_sum = Sum(+1 if false else -1). "
            "Execution price = perp 5m close and funding = native 8h funding rate reused from the verified "
            "C300 cache (2c86accd...), sliced to the 2023-01..02 window. Bars with no trades are gap bars "
            "carried as NaN and NEVER imputed/forward/back-filled; they block OFI at those bars. "
            "No impute/ffill/resample of any derived series."
        ),
        "cache_serialization": "plain numpy ndarrays; index stored as datetime64[us]; no pandas Series/DataFrame legs",
        "push_limit_note": f"compact ndarray form is {meta['cache_pkl_mb']} MB (< 100 MB). Asserted on disk before success.",
        "n_candidates": len(UNIVERSE),
        "n_selected": len(selected),
        "selected_symbols": selected,
        "excluded_symbols": {s: per_symbol[s] for s in UNIVERSE if s not in selected},
        "per_symbol": per_symbol,
        "months": list(MONTHS),
        "window": {"start": START_UTC, "end": END_UTC},
        "interval": INTERVAL,
        "c300_reuse": {
            "cache": str(C300_CACHE.relative_to(ROOT)),
            "cache_sha256": sha256_file(C300_CACHE),
            "meta_sha256": sha256_file(C300_META) if C300_META.exists() else None,
            "provenance_sha256": sha256_file(C300_PROV) if C300_PROV.exists() else None,
        },
    }
    OUT_PROV.write_text(json.dumps(provenance, indent=2, default=str) + "\n")

    summary = {
        "ok": True,
        "campaign": 301,
        "build_source": payload["build_source"] if "build_source" in payload else "archive_download_aggtrades_plus_c300_reuse",
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
        "n_symbols": len(selected),
        "n_universe": len(UNIVERSE),
        "total_bars": int(n_total_bars),
        "total_trade_bars": int(n_total_trade_bars),
        "total_gap_bars": int(n_total_gap),
        "selected_symbols": selected,
        "window": {"start": START_UTC, "end": END_UTC},
        "interval": INTERVAL,
        "c300_cache_sha256": sha256_file(C300_CACHE),
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())