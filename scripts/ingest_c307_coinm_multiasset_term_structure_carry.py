#!/usr/bin/env python3
"""C307 — ingest REAL Binance COIN-M (coin-margined inverse) futures data for the
multi-asset term-structure + cross-sectional funding-carry campaign.

Leg A (per-asset dated-quarterly term structure): BTCUSD, ETHUSD, XRPUSD.
Common term-structure grid per asset = 1h timestamps where the perpetual AND at
least one dated quarterly contract both have kline data; annualized
perp-vs-quarterly basis + time-to-expiry computed on the grid. Assets with
<888 overlapping bars are excluded from WF with a documented scope note (not the
whole campaign).

Leg B (cross-sectional COIN-M funding carry): all 11 perps ranked by native
fundingRate on the common funding grid (1h intersection restricted to
2022-07..2026-06). Funding is native 8h (schema calc_time, funding_interval_hours,
last_funding_rate; 90 rows/month); rate is carried causally (last rate known at
or before each bar, staleness <= 24h+1 bar), never imputed across outages.

Real data only, fail-closed:
- https://data.binance.vision/data/futures/cm/monthly/{kind}/{SYM}/1h/<SYM>-1h-YYYY-MM.zip
  kind in {klines, premiumIndexKlines, markPriceKlines} for perps; kind=klines
  for dated quarterlies. indexPriceKlines is HTTP 404 for COIN-M; not used.
- https://data.binance.vision/data/futures/cm/monthly/fundingRate/<SYM>/<SYM>-fundingRate-YYYY-MM.zip
  fundingRate only 2022-07..2026-06; 2022-06 and 2026-07..2026-10 are 404.
- XLMUSD_PERP klines start 2021-04 (2021-01..03 are 404).
Retry 6x linear 1 s x k; lone 404/5xx retryable then fail-closed per asset/month;
skip non-numeric open_time header rows; real outages carried as NaN, never
imputed/ffilled/backfilled.
Inverse settlement PnL is modeled by the runner as
pnl_coin = notional_usd * (1/entry_price - 1/exit_price) * signed_weight;
this ingest only records prices (never a linear approximation of inverse PnL).

Serialized artifacts (real_data_only:true, fabricated_data:false,
executed_fills:false, SHA256-from-bytes, compact ndarray form < 100 MB):
- data/cache/campaign307_coinm_multiasset_term_structure_carry.pkl
- data/cache/campaign307_coinm_multiasset_term_structure_carry.meta.json
- data/cache/campaign307_coinm_multiasset_term_structure_carry.provenance.json
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
OUT_PKL = CACHE / "campaign307_coinm_multiasset_term_structure_carry.pkl"
OUT_META = CACHE / "campaign307_coinm_multiasset_term_structure_carry.meta.json"
OUT_PROV = CACHE / "campaign307_coinm_multiasset_term_structure_carry.provenance.json"

ARCHIVE_HOST = "https://data.binance.vision"
CM_KLINES_PATH = "/data/futures/cm/monthly/klines/{sym}/1h/{sym}-1h-{month}.zip"
CM_PREMIUM_PATH = "/data/futures/cm/monthly/premiumIndexKlines/{sym}/1h/{sym}-1h-{month}.zip"
CM_MARK_PATH = "/data/futures/cm/monthly/markPriceKlines/{sym}/1h/{sym}-1h-{month}.zip"
CM_FUNDING_PATH = "/data/futures/cm/monthly/fundingRate/{sym}/{sym}-fundingRate-{month}.zip"

INTERVAL = "1h"

# COIN-M inverse perpetuals (BASEUSD_PERP). indexPriceKlines is HTTP 404.
CM_PERPS = (
    "BTCUSD_PERP", "ETHUSD_PERP", "ADAUSD_PERP", "LTCUSD_PERP", "XRPUSD_PERP",
    "BCHUSD_PERP", "LINKUSD_PERP", "TRXUSD_PERP", "ETCUSD_PERP", "XLMUSD_PERP",
    "DOTUSD_PERP",
)

FUNDING_MONTHS_START = "2022-07"
FUNDING_MONTHS_END = "2026-06"

# Dated quarterly contracts with verified reachable monthly klines archives.
CM_QUARTERLY = [
    ("BTCUSD_250627", "2025-06-27T08:00:00Z", ["2025-03", "2025-04", "2025-05", "2025-06"]),
    ("BTCUSD_250926", "2025-09-26T08:00:00Z", ["2025-03", "2025-04", "2025-05", "2025-06", "2025-07", "2025-08", "2025-09"]),
    ("BTCUSD_261225", "2026-12-25T08:00:00Z", ["2026-09", "2026-10"]),
    ("ETHUSD_250627", "2025-06-27T08:00:00Z", ["2025-03", "2025-04", "2025-05", "2025-06"]),
    ("ETHUSD_250926", "2025-09-26T08:00:00Z", ["2025-03", "2025-04", "2025-05", "2025-06", "2025-07", "2025-08", "2025-09"]),
    ("ETHUSD_261225", "2026-12-25T08:00:00Z", ["2026-09", "2026-10"]),
    ("XRPUSD_261225", "2026-12-25T08:00:00Z", ["2026-09", "2026-10"]),
]

PUSH_LIMIT_BYTES = 100_000_000
RETRIES = 6
HOURS_PER_YEAR = 365.0 * 24.0
MIN_BARS_FOR_WF = 720 + 168  # train + test; assets below this cannot support OOS
FUNDING_STALENESS_HOURS = 24.0 + 1.0  # 25 h max staleness for a carried funding rate


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _months_range(start_ym: str, end_ym: str) -> list[str]:
    stamps = pd.date_range(start=start_ym + "-01", end=end_ym + "-01", freq="MS", tz="UTC")
    return [str(ts.date())[:7] for ts in stamps]


def _perp_klines_months(symbol: str) -> list[str]:
    months = _months_range("2020-12", "2026-10")
    if symbol == "XLMUSD_PERP":
        months = [m for m in months if m >= "2021-04"]
    return months


def _http_get(url: str, timeout: float) -> tuple[int, bytes]:
    last_exc: Exception | None = None
    last_status = None
    for attempt in range(1, RETRIES + 1):
        req = urllib.request.Request(url, method="GET", headers={"User-Agent": "kilo-c307-ingest"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return int(resp.status), resp.read()
        except urllib.error.HTTPError as exc:
            last_status = int(exc.code)
            last_exc = exc
        except Exception as exc:
            last_exc = exc
        if attempt < RETRIES:
            time.sleep(1.0 * attempt)
    raise RuntimeError(
        f"GET failed after {RETRIES} attempts: {url} "
        f"(last_status={last_status}, last_exc={last_exc})"
    )


def _is_numeric_first_field(raw: bytes) -> bool:
    first_nl = raw.find(b"\n")
    first_line = raw[: first_nl if first_nl >= 0 else len(raw)]
    first_field = first_line.split(b",", 1)[0].strip()
    try:
        float(first_field)
        return True
    except ValueError:
        return False


def read_kline_frame(raw: bytes) -> pd.DataFrame:
    zf = zipfile.ZipFile(io.BytesIO(raw))
    name = zf.namelist()[0]
    raw_csv = zf.read(name)
    if _is_numeric_first_field(raw_csv):
        df = pd.read_csv(io.BytesIO(raw_csv), header=None, names=[
            "open_time", "open", "high", "low", "close", "volume", "close_time",
            "quote_volume", "count", "taker_buy_volume", "taker_buy_quote_volume", "ignore",
        ])
    else:
        df = pd.read_csv(io.BytesIO(raw_csv))
    df["open_time"] = pd.to_numeric(df["open_time"], errors="coerce")
    df = df.dropna(subset=["open_time"])
    for c in ("open", "high", "low", "close"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    return df[["open_time", "open", "high", "low", "close"]]


def read_funding_frame(raw: bytes) -> pd.DataFrame:
    raw_csv = raw
    if _is_numeric_first_field(raw_csv):
        df = pd.read_csv(io.BytesIO(raw_csv), header=None, names=["calc_time", "funding_interval_hours", "last_funding_rate"])
    else:
        df = pd.read_csv(io.BytesIO(raw_csv))
    df["calc_time"] = pd.to_numeric(df["calc_time"], errors="coerce")
    df = df.dropna(subset=["calc_time"])
    df["last_funding_rate"] = pd.to_numeric(df["last_funding_rate"], errors="coerce")
    df["calc_time"] = pd.to_datetime(df["calc_time"], unit="ms", utc=True)
    return df[["calc_time", "last_funding_rate"]]


def fetch_month(symbol: str, kind: str, month: str, timeout: float) -> dict:
    if kind == "klines":
        path = CM_KLINES_PATH.format(sym=symbol, month=month)
    elif kind == "premium":
        path = CM_PREMIUM_PATH.format(sym=symbol, month=month)
    elif kind == "mark":
        path = CM_MARK_PATH.format(sym=symbol, month=month)
    elif kind == "funding":
        path = CM_FUNDING_PATH.format(sym=symbol, month=month)
    else:
        raise ValueError(f"unknown kind {kind}")
    url = ARCHIVE_HOST + path
    try:
        status, data = _http_get(url, timeout)
    except RuntimeError as exc:
        return {"symbol": symbol, "month": month, "url": url, "status": None, "rows": 0, "ok": False, "error": str(exc)}
    if status != 200 or not data:
        return {"symbol": symbol, "month": month, "url": url, "status": status, "rows": 0, "ok": False}
    try:
        if kind == "funding":
            df = read_funding_frame(data)
        else:
            df = read_kline_frame(data)
    except Exception as exc:
        return {"symbol": symbol, "month": month, "url": url, "status": status, "rows": 0, "ok": False, "error": f"{type(exc).__name__}: {exc}"}
    return {"symbol": symbol, "month": month, "url": url, "status": status, "rows": int(len(df)), "ok": True, "frame": df}


def build_contract_series(symbol: str, months: list[str], kind: str, timeout: float) -> dict:
    detail = {"symbol": symbol, "kind": kind, "per_month": [], "accepted_months": [],
              "failed_months": [], "stop_month": None, "stop_reason": None}
    frames = []
    for m in months:
        r = fetch_month(symbol, kind, m, timeout)
        detail["per_month"].append({k: r[k] for k in ("month", "status", "rows", "ok", "url")})
        if not r["ok"]:
            detail["failed_months"].append(m)
            detail["stop_month"] = m
            detail["stop_reason"] = r.get("error") or f"month {m} http {r['status']}"
            continue
        df = r["frame"]
        if kind == "funding":
            vals = df["last_funding_rate"].to_numpy(dtype=float)
            time_col = "calc_time"
        else:
            vals = df[["open", "high", "low", "close"]].to_numpy(dtype=float)
            time_col = "open_time"
        if not bool(np.isfinite(vals).all()):
            detail["failed_months"].append(m)
            detail["stop_month"] = m
            detail["stop_reason"] = f"month {m} non-finite values"
            continue
        if int(df[time_col].duplicated().sum()) != 0:
            detail["failed_months"].append(m)
            detail["stop_month"] = m
            detail["stop_reason"] = f"month {m} duplicate timestamps"
            continue
        detail["accepted_months"].append(m)
        frames.append(df[[time_col] + (["last_funding_rate"] if kind == "funding" else ["open", "high", "low", "close"])])

    if not frames:
        detail["status"] = "excluded"
        detail["exclusion_reason"] = detail["stop_reason"] or "all months failed"
        return detail

    detail["status"] = "ok"
    all_df = pd.concat(frames, axis=0).sort_values(time_col)
    all_df = all_df.drop_duplicates(time_col, keep="last").set_index(time_col)
    detail["frame"] = all_df
    detail["n_raw_bars"] = int(len(all_df))
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


def _underlying(sym: str) -> str:
    if sym.endswith("_PERP"):
        return sym[:-5]
    return sym.rsplit("_", 1)[0]


def _causal_funding_on_grid(funding_df: pd.DataFrame, grid: pd.DatetimeIndex) -> np.ndarray:
    """Last funding rate known at or before each grid bar, staleness-capped."""
    rates = funding_df["last_funding_rate"].to_numpy(dtype=float)
    times = funding_df.index.to_numpy(dtype="datetime64[us]")
    out = np.full(len(grid), np.nan, dtype=float)
    j = 0
    last_rate = np.nan
    last_time = None
    for i, t in enumerate(grid.to_numpy(dtype="datetime64[us]")):
        while j < len(times) and times[j] <= t:
            last_rate = rates[j]
            last_time = times[j]
            j += 1
        if not np.isnan(last_rate) and last_time is not None:
            stale_h = (t.astype("datetime64[us]").astype("int64") - last_time.astype("int64")) / 1e6 / 3600.0
            if stale_h <= FUNDING_STALENESS_HOURS:
                out[i] = last_rate
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--timeout", type=float, default=60.0)
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args(argv)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    CACHE.mkdir(parents=True, exist_ok=True)

    funding_months = _months_range(FUNDING_MONTHS_START, FUNDING_MONTHS_END)

    # ---- Phase 1: perp klines for all 11 perps ----
    perp_series: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futs = {pool.submit(build_contract_series, s, _perp_klines_months(s), "klines", args.timeout): s for s in CM_PERPS}
        for fut in as_completed(futs):
            d = fut.result()
            perp_series[d["symbol"]] = d

    excluded_perp = {s: perp_series[s].get("exclusion_reason", perp_series[s].get("status")) for s in CM_PERPS if perp_series[s].get("status") != "ok"}
    if len(excluded_perp) == len(CM_PERPS):
        raise SystemExit(f"FATAL: no perp has klines data. Excluded: {json.dumps(excluded_perp)}")

    # ---- Phase 2: perp premiumIndexKlines + markPriceKlines for all 11 perps ----
    perp_premium: dict[str, dict] = {}
    perp_mark: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futs = {}
        for s in CM_PERPS:
            futs[pool.submit(build_contract_series, s, _perp_klines_months(s), "premium", args.timeout)] = ("premium", s)
            futs[pool.submit(build_contract_series, s, _perp_klines_months(s), "mark", args.timeout)] = ("mark", s)
        for fut in as_completed(futs):
            kind, s = futs[fut]
            d = fut.result()
            if kind == "premium":
                perp_premium[s] = d
            else:
                perp_mark[s] = d

    # ---- Phase 3: fundingRate for all 11 perps (2022-07..2026-06 only) ----
    perp_funding: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futs = {pool.submit(build_contract_series, s, funding_months, "funding", args.timeout): s for s in CM_PERPS}
        for fut in as_completed(futs):
            d = fut.result()
            perp_funding[d["symbol"]] = d

    excluded_fund = {s: perp_funding[s].get("exclusion_reason", perp_funding[s].get("status")) for s in CM_PERPS if perp_funding[s].get("status") != "ok"}
    if len(excluded_fund) == len(CM_PERPS):
        raise SystemExit(f"FATAL: no perp has funding data. Excluded: {json.dumps(excluded_fund)}")

    # ---- Phase 4: dated quarterly klines for the 7 verified contracts ----
    quarterly_series: dict[str, dict] = {}
    q_months_map = {sym: months_list for sym, _, months_list in CM_QUARTERLY}
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futs = {pool.submit(build_contract_series, sym, q_months_map[sym], "klines", args.timeout): sym for sym, _, _ in CM_QUARTERLY}
        for fut in as_completed(futs):
            d = fut.result()
            quarterly_series[d["symbol"]] = d

    # ---- Leg A: per-asset common term-structure grids ----
    quarterly_by_asset: dict[str, list[str]] = {}
    for sym, expiry, _ in CM_QUARTERLY:
        quarterly_by_asset.setdefault(_underlying(sym), []).append(sym)

    term_assets = sorted({_underlying(s) for s in CM_PERPS})
    perp_by_asset = {_underlying(s): perp_series[s] for s in CM_PERPS}

    per_asset: dict[str, dict] = {}
    selected_assets: list[str] = []
    excluded_assets: dict[str, dict] = {}

    for asset in term_assets:
        p_entry = perp_by_asset.get(asset)
        if not p_entry or p_entry.get("status") != "ok":
            excluded_assets[asset] = {"status": "excluded", "exclusion_reason": "no perp klines"}
            continue
        perp_df = p_entry["frame"]

        active_quarters: dict[str, pd.DataFrame] = {}
        for qsym in quarterly_by_asset.get(asset, []):
            q_entry = quarterly_series.get(qsym)
            if q_entry and q_entry.get("status") == "ok":
                active_quarters[qsym] = q_entry["frame"]

        if len(active_quarters) == 0:
            excluded_assets[asset] = {"status": "excluded", "exclusion_reason": "no quarterly contract with data"}
            continue

        common_index: pd.DatetimeIndex | None = None
        for qsym, q_df in active_quarters.items():
            pair_common = perp_df.index.intersection(q_df.index)
            common_index = pair_common if common_index is None else common_index.union(pair_common)
        if common_index is None or len(common_index) == 0:
            excluded_assets[asset] = {"status": "excluded", "exclusion_reason": "empty common term-structure grid"}
            continue
        common_index = common_index.sort_values()
        n_grid = int(len(common_index))
        if n_grid < MIN_BARS_FOR_WF:
            excluded_assets[asset] = {"status": "excluded", "exclusion_reason": f"common grid {n_grid} bars < train+test {MIN_BARS_FOR_WF}"}
            continue

        n_contracts_at_bar = np.ones(n_grid, dtype=int)
        perp_close = perp_df.reindex(common_index)["close"].to_numpy(dtype=float)

        q_close: dict[str, np.ndarray] = {}
        q_basis: dict[str, np.ndarray] = {}
        q_tte_hours: dict[str, np.ndarray] = {}
        q_expiry = {sym: expiry for sym, expiry, _ in CM_QUARTERLY}

        for qsym, q_df in active_quarters.items():
            q_al = q_df.reindex(common_index)
            qc = q_al["close"].to_numpy(dtype=float)
            q_close[qsym] = qc
            q_present = ~np.isnan(qc)
            n_contracts_at_bar += q_present.astype(int)
            q_expiry_ts = pd.Timestamp(q_expiry[qsym])
            tte_hours = np.array([(q_expiry_ts - t).total_seconds() / 3600.0 for t in common_index], dtype=float)
            q_tte_hours[qsym] = tte_hours
            with np.errstate(divide="ignore", invalid="ignore"):
                basis = np.log(qc / perp_close) * (HOURS_PER_YEAR / np.where(tte_hours > 0, tte_hours, np.nan))
            basis = np.where(np.isfinite(basis), basis, np.nan)
            q_basis[qsym] = basis

        perp_close_present = ~np.isnan(perp_close)
        if not bool(np.isfinite(perp_close[perp_close_present]).all()) or not bool((perp_close[perp_close_present] > 0).all()):
            excluded_assets[asset] = {"status": "excluded", "exclusion_reason": "perp close non-finite or non-positive"}
            continue

        bars_ge2 = int((n_contracts_at_bar >= 2).sum())
        if bars_ge2 == 0:
            excluded_assets[asset] = {"status": "excluded", "exclusion_reason": "no bar with >= 2 contracts overlapping"}
            continue

        any_q_present = np.zeros(n_grid, dtype=bool)
        any_basis_present = np.zeros(n_grid, dtype=bool)
        for qsym in active_quarters:
            any_q_present |= ~np.isnan(q_close[qsym])
            any_basis_present |= ~np.isnan(q_basis[qsym])

        entry = {
            "asset": asset,
            "window_start_utc": str(common_index[0]),
            "window_end_utc": str(common_index[-1]),
            "n_bars": n_grid,
            "bars_ge2_contracts": bars_ge2,
            "n_contracts": 1 + len(active_quarters),
            "quarterly_contracts": sorted(active_quarters.keys()),
            "n_present_perp_bars": int(perp_close_present.sum()),
            "n_present_any_quarterly_bars": int(any_q_present.sum()),
            "n_present_any_basis_bars": int(any_basis_present.sum()),
            "n_missing_basis_bars": int((~any_basis_present).sum()),
            "source": "fresh_download",
        }
        entry.update(_compact({
            "index": common_index,
            "perp_close": perp_close,
            "n_contracts_at_bar": n_contracts_at_bar,
        }))
        for qsym in sorted(active_quarters.keys()):
            entry[f"q_close_{qsym}"] = q_close[qsym]
            entry[f"q_basis_{qsym}"] = q_basis[qsym]
            entry[f"q_tte_hours_{qsym}"] = q_tte_hours[qsym]

        per_asset[asset] = entry
        selected_assets.append(asset)

    for asset in term_assets:
        if asset not in per_asset:
            excluded_assets.setdefault(asset, {"status": "excluded", "exclusion_reason": "no common term-structure grid"})

    selected_assets = sorted(selected_assets)

    # ---- Leg B: common funding grid across all 11 perps ----
    perp_1h_indexes: dict[str, pd.DatetimeIndex] = {}
    perp_closes: dict[str, pd.Series] = {}
    for s in CM_PERPS:
        pe = perp_series[s]
        if pe.get("status") == "ok":
            perp_1h_indexes[s] = pe["frame"].index
            perp_closes[s] = pe["frame"]["close"]

    common_fund_index: pd.DatetimeIndex | None = None
    for s in CM_PERPS:
        idx = perp_1h_indexes.get(s)
        if idx is None:
            continue
        window = idx[(idx >= pd.Timestamp("2022-07-01", tz="UTC")) & (idx < pd.Timestamp("2026-07-01", tz="UTC"))]
        common_fund_index = window if common_fund_index is None else common_fund_index.intersection(window)
    if common_fund_index is None or len(common_fund_index) == 0:
        raise SystemExit("FATAL: Leg B common funding grid is empty")

    common_fund_index = common_fund_index.sort_values()
    n_fund = int(len(common_fund_index))

    fund_rate: dict[str, np.ndarray] = {}
    fund_present: dict[str, np.ndarray] = {}
    perp_close_on_fund: dict[str, np.ndarray] = {}
    premium_close_on_fund: dict[str, np.ndarray] = {}
    mark_close_on_fund: dict[str, np.ndarray] = {}

    for s in CM_PERPS:
        pe = perp_series[s]
        if pe.get("status") != "ok":
            continue
        pc = pe["frame"].reindex(common_fund_index)["close"].to_numpy(dtype=float)
        perp_close_on_fund[s] = pc

        prem = perp_premium.get(s)
        mark = perp_mark.get(s)
        if prem and prem.get("status") == "ok":
            premium_close_on_fund[s] = prem["frame"].reindex(common_fund_index)["close"].to_numpy(dtype=float)
        if mark and mark.get("status") == "ok":
            mark_close_on_fund[s] = mark["frame"].reindex(common_fund_index)["close"].to_numpy(dtype=float)

        fe = perp_funding.get(s)
        if fe and fe.get("status") == "ok":
            fr = _causal_funding_on_grid(fe["frame"], common_fund_index)
        else:
            fr = np.full(n_fund, np.nan, dtype=float)
        fund_rate[s] = fr
        fund_present[s] = ~np.isnan(fr)

    n_assets_fund = int(sum(1 for s in CM_PERPS if bool(fund_present[s].any())))
    if n_assets_fund < 2:
        raise SystemExit(f"FATAL: Leg B has {n_assets_fund} assets with finite funding overlap (< 2)")

    payload = {
        "interval": INTERVAL,
        "source_interval": "coin_m_klines_1h",
        "campaign": 307,
        "assets": selected_assets,
        "n_assets": len(selected_assets),
        "perp_symbols": list(CM_PERPS),
        "n_perp_symbols": len(CM_PERPS),
        "quarterly_contracts": [s for s, _, _ in CM_QUARTERLY],
        "funding_months": {"start": FUNDING_MONTHS_START, "end": FUNDING_MONTHS_END},
        "leg_a": {"per_asset": per_asset, "selected_assets": selected_assets, "excluded_assets": excluded_assets},
        "leg_b": {
            "symbols": [s for s in CM_PERPS if s in perp_close_on_fund],
            "n_symbols": len(perp_close_on_fund),
            "window_start_utc": str(common_fund_index[0]),
            "window_end_utc": str(common_fund_index[-1]),
            "n_bars": n_fund,
            "n_assets_with_funding": n_assets_fund,
        },
        "real_data_only": True,
        "fabricated_data": False,
        "executed_fills": False,
    }
    payload["leg_b"].update(_compact({"index": common_fund_index}))
    for s in perp_close_on_fund:
        payload["leg_b"][f"perp_close_{s}"] = perp_close_on_fund[s]
        payload["leg_b"][f"funding_rate_{s}"] = fund_rate[s]
        payload["leg_b"][f"funding_present_{s}"] = fund_present[s].astype(np.float64)
        if s in premium_close_on_fund:
            payload["leg_b"][f"premium_close_{s}"] = premium_close_on_fund[s]
        if s in mark_close_on_fund:
            payload["leg_b"][f"mark_close_{s}"] = mark_close_on_fund[s]

    blob = _pickle_bytes(payload)
    OUT_PKL.write_bytes(blob)
    pkl_bytes = _assert_under_push_limit(OUT_PKL)
    pkl_sha = sha256_file(OUT_PKL)

    meta = {
        "generated_at_utc": ts,
        "campaign": 307,
        "part": "ingest",
        "interval": INTERVAL,
        "source_interval": "coin_m_klines_1h",
        "assets": selected_assets,
        "n_assets": len(selected_assets),
        "perp_symbols": list(CM_PERPS),
        "n_perp_symbols": len(CM_PERPS),
        "quarterly_contracts": [s for s, _, _ in CM_QUARTERLY],
        "funding_window_start": FUNDING_MONTHS_START,
        "funding_window_end": FUNDING_MONTHS_END,
        "source_host": ARCHIVE_HOST,
        "klines_endpoint": CM_KLINES_PATH,
        "premium_endpoint": CM_PREMIUM_PATH,
        "mark_endpoint": CM_MARK_PATH,
        "funding_endpoint": CM_FUNDING_PATH,
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
        "n_funding_months": len(funding_months),
    }
    OUT_META.write_text(json.dumps(meta, indent=2) + "\n")

    leg_a_summary = {}
    for a in selected_assets:
        pa = per_asset[a]
        leg_a_summary[a] = {
            "status": "ok",
            "source": pa["source"],
            "window_start_utc": pa["window_start_utc"],
            "window_end_utc": pa["window_end_utc"],
            "n_bars": pa["n_bars"],
            "bars_ge2_contracts": pa["bars_ge2_contracts"],
            "n_contracts": pa["n_contracts"],
            "quarterly_contracts": pa["quarterly_contracts"],
            "n_present_perp_bars": pa["n_present_perp_bars"],
            "n_present_any_quarterly_bars": pa["n_present_any_quarterly_bars"],
            "n_present_any_basis_bars": pa["n_present_any_basis_bars"],
            "n_missing_basis_bars": pa["n_missing_basis_bars"],
        }
    for a, exc in excluded_assets.items():
        leg_a_summary[a] = exc

    provenance = {
        "generated_at_utc": ts,
        "campaign": 307,
        "part": "provenance",
        "real_data_only": True,
        "fabricated_data": False,
        "executed_fills": False,
        "build_source": (
            "archive_download_coin_m_klines_premium_mark_funding_common_grids_plus_basis"
        ),
        "universe_rule": (
            "Universe = COIN-M inverse perpetuals {BTCUSD_PERP, ETHUSD_PERP, "
            "ADAUSD_PERP, LTCUSD_PERP, XRPUSD_PERP, BCHUSD_PERP, LINKUSD_PERP, "
            "TRXUSD_PERP, ETCUSD_PERP, XLMUSD_PERP, DOTUSD_PERP} and dated "
            "quarterly futures {BTCUSD_250627, BTCUSD_250926, BTCUSD_261225, "
            "ETHUSD_250627, ETHUSD_250926, ETHUSD_261225, XRPUSD_261225}. "
            "1h klines are real Binance COIN-M open/high/low/close. "
            "Leg A common term-structure grid per asset = timestamps where the "
            "perp AND >= 1 dated quarterly contract both have 1h kline data "
            "(>= 2 contracts overlap); missing bars dropped, never imputed. "
            "Perp-vs-quarterly annualized basis = ln(q_close / perp_close) × "
            "(hours_per_year / hours_to_expiry); TTE uses contract-code expiry "
            "at 08:00 UTC. Assets with <888 overlapping bars excluded from WF "
            "with a documented scope note. Leg B common funding grid = 1h "
            "intersection of all perp klines within 2022-07..2026-06; native "
            "8h funding carried causally (last rate at/before each bar, staleness "
            "<= 25 h), never imputed across outages. Funding outside 2022-07..2026-06 "
            "is not downloaded (404). indexPriceKlines is HTTP 404 for COIN-M; not used."
        ),
        "cache_serialization": "plain numpy ndarrays; index stored as datetime64[us]; no pandas Series/DataFrame legs",
        "push_limit_note": f"compact ndarray form is {meta['cache_pkl_mb']} MB (< 100 MB). Asserted on disk before success.",
        "n_candidates_perps": len(CM_PERPS),
        "n_candidates_quarterlies": len(CM_QUARTERLY),
        "n_selected_leg_a_assets": len(selected_assets),
        "selected_leg_a_assets": selected_assets,
        "excluded_leg_a_assets": excluded_assets,
        "n_leg_b_symbols": n_assets_fund,
        "leg_b_symbols": [s for s in CM_PERPS if s in perp_close_on_fund],
        "leg_b_window_start_utc": str(common_fund_index[0]),
        "leg_b_window_end_utc": str(common_fund_index[-1]),
        "leg_b_n_bars": n_fund,
        "months_perp_klines": _perp_klines_months("BTCUSD_PERP"),
        "months_funding": funding_months,
        "n_months_perp_klines": len(_perp_klines_months("BTCUSD_PERP")),
        "n_months_funding": len(funding_months),
    }
    OUT_PROV.write_text(json.dumps(provenance, indent=2, default=str) + "\n")

    summary = {
        "ok": True,
        "campaign": 307,
        "build_source": provenance["build_source"],
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
        "n_assets_leg_a": len(selected_assets),
        "selected_assets_leg_a": selected_assets,
        "n_symbols_leg_b": n_assets_fund,
        "leg_b_symbols": [s for s in CM_PERPS if s in perp_close_on_fund],
        "leg_b_window_start_utc": str(common_fund_index[0]),
        "leg_b_window_end_utc": str(common_fund_index[-1]),
        "leg_b_n_bars": n_fund,
        "quarterly_contracts": [s for s, _, _ in CM_QUARTERLY],
        "per_asset": leg_a_summary,
        "interval": INTERVAL,
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
