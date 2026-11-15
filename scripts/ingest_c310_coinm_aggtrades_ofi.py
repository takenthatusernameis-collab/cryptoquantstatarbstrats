#!/usr/bin/env python3
"""C310 — ingest REAL Binance COIN-M inverse perpetual ``aggTrades`` and build
per-perp 1h order-flow-imbalance (OFI) feature panels for the C310 COIN-M
inverse CROSS-SECTIONAL OFI-carry stat-arb campaign.

This is a genuinely new economic family (not a re-skin of any frozen campaign):

- C301 ingested USDT-M (linear) perp aggTrades for a PER-ASSET TIME-SERIES OFI
  campaign on {BTCUSDT, ETHUSDT, BCHUSDT} over 2023-01..02.
- C310 ingests COIN-M (inverse) perp aggTrades for a CROSS-SECTIONAL OFI carry
  campaign (long top-K / short bottom-K across the 11 COIN-M perps, dollar
  neutral) settled in inverse coin-margined PnL. COIN-M aggTrades have never
  been ingested before.

Data (real, fail-closed; ``fapi`` REST is HTTP 451 and is NOT used):

- ``https://data.binance.vision/data/futures/cm/monthly/aggTrades/<SYM>/<SYM>-aggTrades-YYYY-MM.zip``
- Universe: the 11 C307 COIN-M inverse perps.
- Default window: 2022-07 .. 2026-06 (48 months), aligned to the verified C307
  leg_b 1h grid (34,968 bars). ``--start-month``/``--end-month`` override.
- Schema: 7 columns, header in recent months (headerless older):
  ``agg_trade_id,price,quantity,first_trade_id,last_trade_id,transact_time,is_buyer_maker``.
  ``transact_time`` is epoch MILLISECONDS; ``is_buyer_maker`` is true/false.
  Bar = ``floor(transact_time_ms / 3600000)`` -> native 1h UTC bars.
  ``buy_volume = Sum(quantity where is_buyer_maker == false)``,
  ``sell_volume = Sum(quantity where is_buyer_maker == true)``,
  plus per-bar trade count, trade_sign_sum, notional, vwap.

Execution prices + funding (reused from the verified C307 cache, NOT re-downloaded):

- ``data/cache/campaign307_coinm_multiasset_term_structure_carry.pkl`` supplies
  real COIN-M perp 1h ``perp_close_<SYM>`` and native 8h ``funding_rate_<SYM>``
  over 2022-07..2026-06. OFI legs are aligned to that exact grid. Funding is a
  CONTROL leg only (never the C310 carry source) and is excluded from return.

Fail-closed (never impute / forward-fill / back-fill):

- any 404 / empty month / non-finite price / missing bar blocks the symbol;
- per-month trade counts, per-asset coverage and every gap bar are recorded;
- gap bars carry NaN and are never imputed.

Serialized artifacts (all real_data_only:true, fabricated_data:false,
executed_fills:false, SHA256-from-bytes, COMPACT ndarray form < 100 MB):

- ``data/cache/campaign310_coinm_aggtrades_ofi.pkl``
- ``data/cache/campaign310_coinm_aggtrades_ofi.meta.json``
- ``data/cache/campaign310_coinm_aggtrades_ofi.provenance.json``
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
OUT_PKL = CACHE / "campaign310_coinm_aggtrades_ofi.pkl"
OUT_META = CACHE / "campaign310_coinm_aggtrades_ofi.meta.json"
OUT_PROV = CACHE / "campaign310_coinm_aggtrades_ofi.provenance.json"

C307_CACHE = CACHE / "campaign307_coinm_multiasset_term_structure_carry.pkl"
C307_META = CACHE / "campaign307_coinm_multiasset_term_structure_carry.meta.json"

ARCHIVE_HOST = "https://data.binance.vision"
AGGTRADES_PATH = "/data/futures/cm/monthly/aggTrades/{sym}/{sym}-aggTrades-{month}.zip"

PERPS = (
    "BTCUSD_PERP", "ETHUSD_PERP", "ADAUSD_PERP", "LTCUSD_PERP", "XRPUSD_PERP",
    "BCHUSD_PERP", "LINKUSD_PERP", "TRXUSD_PERP", "ETCUSD_PERP", "XLMUSD_PERP",
    "DOTUSD_PERP",
)

DEFAULT_START = "2022-07"
DEFAULT_END = "2026-06"

INTERVAL = "1h"
BAR_MS = 3_600_000  # 1 hour in milliseconds

AGGTRADE_COLUMNS = [
    "agg_trade_id", "price", "quantity", "first_trade_id",
    "last_trade_id", "transact_time", "is_buyer_maker",
]

PUSH_LIMIT_BYTES = 100_000_000  # GitHub hard-rejects any blob > 100 MB
HTTP_RETRIES = 6  # linear backoff 1s*k (flaky archive host)


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
        req = urllib.request.Request(url, method="GET", headers={"User-Agent": "kilo-c310-ingest"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return int(resp.status), resp.read()
        except urllib.error.HTTPError as exc:  # 404/451: do not retry
            return int(exc.code), b""
        except Exception as exc:  # noqa: BLE001  transient network: retry w/ backoff
            last_exc = exc
            time.sleep(1.0 * attempt)
    raise RuntimeError(f"GET failed after {HTTP_RETRIES} attempts: {url}: {last_exc}")


def read_aggtrades_zip(zip_bytes: bytes) -> pd.DataFrame:
    """Parse a futures aggTrades zip generically (header or headerless)."""
    zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    name = zf.namelist()[0]
    raw = zf.read(name)
    first_nl = raw.find(b"\n")
    first_line = raw[: first_nl if first_nl >= 0 else len(raw)]
    has_header = b"agg_trade_id" in first_line
    if has_header:
        df = pd.read_csv(io.BytesIO(raw))
    else:
        df = pd.read_csv(io.BytesIO(raw), header=None, names=AGGTRADE_COLUMNS)
    for c in ("price", "quantity", "transact_time"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    if df["is_buyer_maker"].dtype == object:
        df["is_buyer_maker"] = df["is_buyer_maker"].astype(str).str.strip().str.lower().map(
            {"true": True, "false": False}
        )
    else:
        df["is_buyer_maker"] = df["is_buyer_maker"].astype(bool)
    return df


def aggregate_month(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate raw trades of one month into native 1h bars."""
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


def build_symbol(symbol: str, months: list[str], grid_index: pd.DatetimeIndex,
                 c307_close: np.ndarray, c307_funding: np.ndarray,
                 timeout: float) -> dict:
    detail: dict = {"symbol": symbol, "per_month": [], "accepted_months": []}
    frames: list[pd.DataFrame] = []
    for m in months:
        url = ARCHIVE_HOST + AGGTRADES_PATH.format(sym=symbol, month=m)
        try:
            status, data = _http_get(url, timeout)
        except Exception as exc:  # noqa: BLE001
            detail["per_month"].append({"month": m, "url": url, "status": -1, "rows": 0,
                                        "ok": False, "reason": repr(exc)[:200]})
            detail["status"] = "excluded"
            detail["exclusion_reason"] = f"month {m} fetch error"
            return detail
        if status != 200:
            detail["per_month"].append({"month": m, "url": url, "status": status, "rows": 0,
                                        "ok": False, "reason": f"http_{status}"})
            detail["status"] = "excluded"
            detail["exclusion_reason"] = f"month {m} http status {status}"
            return detail
        df = read_aggtrades_zip(data)
        agg = aggregate_month(df)
        if len(agg) == 0:
            detail["per_month"].append({"month": m, "url": url, "status": status, "rows": 0,
                                        "ok": False, "reason": "empty after aggregation"})
            detail["status"] = "excluded"
            detail["exclusion_reason"] = f"month {m} empty after aggregation"
            return detail
        if not bool(np.isfinite(agg["vwap"].to_numpy(dtype=float)).all()):
            detail["per_month"].append({"month": m, "url": url, "status": status, "rows": int(len(df)),
                                        "ok": False, "reason": "non-finite vwap"})
            detail["status"] = "excluded"
            detail["exclusion_reason"] = f"month {m} non-finite vwap present"
            return detail
        if not bool((agg["trade_count"].to_numpy(dtype=float) > 0).all()):
            detail["per_month"].append({"month": m, "url": url, "status": status, "rows": int(len(df)),
                                        "ok": False, "reason": "zero trade_count bar"})
            detail["status"] = "excluded"
            detail["exclusion_reason"] = f"month {m} zero trade_count bar"
            return detail
        detail["per_month"].append({"month": m, "url": url, "status": status, "rows": int(len(df)),
                                    "bars": int(len(agg)), "ok": True})
        detail["accepted_months"].append(m)
        frames.append(agg)
        del df, agg, data

    agg_all = pd.concat(frames, axis=0).sort_index()
    agg_all = agg_all[~agg_all.index.duplicated(keep="last")]
    agg_all = agg_all.reindex(grid_index)
    n_gap = int(agg_all["trade_count"].isna().sum())
    gap_bars = [str(b) for b in agg_all.index[agg_all["trade_count"].isna().values]]
    n_trade_bars = int(agg_all["trade_count"].notna().sum())
    if n_trade_bars == 0:
        detail["status"] = "excluded"
        detail["exclusion_reason"] = "no trade bars in grid"
        return detail

    # Per-bar arrays on the exact C307 1h grid (gap bars = NaN, never imputed).
    buy_volume = agg_all["buy_volume"].to_numpy(dtype=float)
    sell_volume = agg_all["sell_volume"].to_numpy(dtype=float)
    signed_volume = agg_all["signed_volume"].to_numpy(dtype=float)
    trade_count = agg_all["trade_count"].to_numpy(dtype=float)
    trade_sign_sum = agg_all["trade_sign_sum"].to_numpy(dtype=float)
    notional = agg_all["notional"].to_numpy(dtype=float)
    vwap = agg_all["vwap"].to_numpy(dtype=float)

    # Fail-closed on the execution-price leg (C307 perp_close).
    if not bool(np.isfinite(c307_close).all()) or not bool((c307_close > 0).all()):
        detail["status"] = "excluded"
        detail["exclusion_reason"] = "C307 perp_close non-finite/non-positive"
        return detail

    tc_ts = pd.Series(np.nan_to_num(trade_count), index=grid_index)
    daily_counts = {str(d.date()): int(v) for d, v in tc_ts.groupby(tc_ts.index.floor("D")).sum().items()}

    detail.update({
        "status": "ok",
        "n_bars": int(len(grid_index)),
        "n_trade_bars": n_trade_bars,
        "n_gap_bars": n_gap,
        "gap_bars": gap_bars,
        "daily_trade_counts": daily_counts,
        "buy_volume": buy_volume,
        "sell_volume": sell_volume,
        "signed_volume": signed_volume,
        "trade_count": trade_count,
        "trade_sign_sum": trade_sign_sum,
        "notional": notional,
        "vwap": vwap,
        "perp_close": c307_close,
        "funding_rate": c307_funding,
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
    if nbytes >= PUSH_LIMIT_BYTES:
        raise SystemExit(f"FATAL: cache pickle {nbytes/1e6:.2f} MB >= push limit")
    return nbytes


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
    grid_index = pd.DatetimeIndex(np.asarray(leg_b["index"]))
    if isinstance(grid_index.tz, type(None)):
        grid_index = grid_index.tz_localize("UTC")
    for s in symbols:
        if s not in lb_symbols:
            raise SystemExit(f"FATAL: {s} not in C307 leg_b symbols")

    def _leg(sym: str) -> tuple[np.ndarray, np.ndarray]:
        return (np.asarray(leg_b[f"perp_close_{sym}"], dtype=float),
                np.asarray(leg_b[f"funding_rate_{sym}"], dtype=float))

    built: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futs = {}
        for s in symbols:
            pc, fr = _leg(s)
            futs[pool.submit(build_symbol, s, months, grid_index, pc, fr, args.timeout)] = s
        for fut in as_completed(futs):
            d = fut.result()
            built[d["symbol"]] = d

    selected = [s for s in symbols if built[s].get("status") == "ok"]
    excluded = {s: built[s].get("exclusion_reason", built[s].get("status"))
                for s in symbols if built[s].get("status") != "ok"}
    if not selected:
        raise SystemExit(f"FATAL: no asset has a usable real window. Excluded: {json.dumps(excluded)}")

    per_asset = {}
    for s in selected:
        d = built[s]
        entry = {
            "n_bars": int(d["n_bars"]),
            "n_trade_bars": int(d["n_trade_bars"]),
            "n_gap_bars": int(d["n_gap_bars"]),
            "gap_bars": d["gap_bars"],
            "daily_trade_counts": d["daily_trade_counts"],
            "per_month": d["per_month"],
            "accepted_months": d["accepted_months"],
        }
        entry.update(_compact({
            "buy_volume": d["buy_volume"], "sell_volume": d["sell_volume"],
            "signed_volume": d["signed_volume"], "trade_count": d["trade_count"],
            "trade_sign_sum": d["trade_sign_sum"], "notional": d["notional"],
            "vwap": d["vwap"], "perp_close": d["perp_close"], "funding_rate": d["funding_rate"],
            "index": grid_index,
        }))
        per_asset[s] = entry

    payload = {
        "interval": INTERVAL,
        "bar_ms": BAR_MS,
        "source_interval": "coin_m_aggTrades_ms",
        "campaign": 310,
        "symbols": list(selected),
        "n_symbols": len(selected),
        "window": {"start": args.start_month, "end": args.end_month},
        "universe": list(symbols),
        "n_universe": len(symbols),
        "grid_start_utc": str(grid_index[0]),
        "grid_end_utc": str(grid_index[-1]),
        "n_grid_bars": int(len(grid_index)),
        "execution_price_source": "C307_leg_b_perp_close_1h",
        "funding_source": "C307_leg_b_native_8h_funding_control_only",
        "c307_cache": str(C307_CACHE.relative_to(ROOT)),
        "c307_cache_sha256": sha256_file(C307_CACHE),
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
    n_total_trade = sum(int(per_asset[s]["n_trade_bars"]) for s in selected)
    n_total_gap = sum(int(per_asset[s]["n_gap_bars"]) for s in selected)

    meta = {
        "generated_at_utc": ts,
        "campaign": 310,
        "part": "ingest",
        "interval": INTERVAL,
        "source_interval": "coin_m_aggTrades_ms",
        "bar_ms": BAR_MS,
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
        "source_host": ARCHIVE_HOST,
        "aggtrades_endpoint": AGGTRADES_PATH,
        "execution_price_source": "C307_leg_b_perp_close_1h",
        "funding_source": "C307_leg_b_native_8h_funding_control_only",
        "c307_cache": str(C307_CACHE.relative_to(ROOT)),
        "c307_cache_sha256": sha256_file(C307_CACHE),
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
    }
    OUT_META.write_text(json.dumps(meta, indent=2) + "\n")

    per_symbol = {}
    for s in symbols:
        if s in selected:
            pa = per_asset[s]
            per_symbol[s] = {
                "status": "ok",
                "n_bars": pa["n_bars"], "n_trade_bars": pa["n_trade_bars"],
                "n_gap_bars": pa["n_gap_bars"], "accepted_months": pa["accepted_months"],
                "n_days_with_trades": len(pa["daily_trade_counts"]),
            }
        else:
            per_symbol[s] = {"status": "excluded", "exclusion_reason": excluded.get(s)}

    provenance = {
        "generated_at_utc": ts,
        "campaign": 310,
        "part": "provenance",
        "source_host": ARCHIVE_HOST,
        "aggtrades_endpoint": AGGTRADES_PATH,
        "interval": INTERVAL,
        "bar_ms": BAR_MS,
        "window_start_month": args.start_month,
        "window_end_month": args.end_month,
        "n_months": len(months),
        "symbols": selected,
        "excluded": excluded,
        "per_symbol": per_symbol,
        "execution_price_source": "C307_leg_b_perp_close_1h",
        "funding_source": "C307_leg_b_native_8h_funding_control_only",
        "c307_cache_sha256": sha256_file(C307_CACHE),
        "real_data_only": True,
        "fabricated_data": False,
        "fetch_real_data_only": True,
        "fetch_fabricated_data": False,
        "executed_fills": False,
        "cache_pkl_sha256": pkl_sha,
        "cache_meta_sha256": sha256_file(OUT_META),
        "gap_bar_policy": "gap bars carry NaN; never imputed or forward/back-filled",
    }
    OUT_PROV.write_text(json.dumps(provenance, indent=2) + "\n")

    print(json.dumps({
        "campaign": 310,
        "part": "ingest",
        "symbols_ok": selected,
        "n_symbols": len(selected),
        "n_months": len(months),
        "total_trade_bars": int(n_total_trade),
        "total_gap_bars": int(n_total_gap),
        "cache_pkl_mb": meta["cache_pkl_mb"],
        "sha256": pkl_sha,
        "excluded": excluded,
        "cache": str(OUT_PKL.relative_to(ROOT)),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())