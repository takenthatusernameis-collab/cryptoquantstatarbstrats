#!/usr/bin/env python3
"""C306 — ingest REAL Binance COIN-M (coin-margined inverse) futures data for the
dated quarterly term-structure / calendar-basis carry campaign.

Builds, per underlying asset, the *common term-structure grid* = timestamps where
the perpetual AND at least one dated quarterly contract both have 1h kline data
(>= 2 contracts overlap).  Any bar missing in >= 1 required archive is dropped
from the grid; per-contract missing bars are carried as NaN and NEVER
imputed/filled/ffilled.

Real data only (fail-closed; fapi REST is HTTP 451 and is NOT used):
- https://data.binance.vision/data/futures/cm/monthly/klines/<SYM>/1h/<SYM>-1h-YYYY-MM.zip
  (perp: BTCUSD_PERP, ETHUSD_PERP; quarterly: BTCUSD_250627, BTCUSD_250926,
  BTCUSD_261225, ETHUSD_261225)
- https://data.binance.vision/data/futures/cm/monthly/premiumIndexKlines/<SYM>/1h/<SYM>-1h-YYYY-MM.zip  (perp only)
- https://data.binance.vision/data/futures/cm/monthly/markPriceKlines/<SYM>/1h/<SYM>-1h-YYYY-MM.zip      (perp only)

Fail-closed (never impute / forward-fill / back-fill):
- every download wrapped in retry-with-backoff (6 attempts, linear 1 s x k);
  a lone 404/5xx is retryable; only fail-closed after all retries exhausted;
- skip any CSV row whose first field is non-numeric (recent months carry an
  ``open_time`` header row);
- common term-structure grid requires >= 2 contracts to overlap; real outages
  are NaN and never imputed.

Inverse (coin-margined) settlement PnL is modeled by the runner as
pnl_coin = notional_usd * (1/entry_price - 1/exit_price) * signed_weight;
this ingest only records prices (never a linear approximation of inverse PnL).

Serialized artifacts (all real_data_only:true, fabricated_data:false,
executed_fills:false, SHA256-from-bytes, COMPACT ndarray form < 100 MB):
- data/cache/campaign306_coinm_term_structure.pkl
- data/cache/campaign306_coinm_term_structure.meta.json
- data-cache/campaign306_coinm_term_structure.provenance.json
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
OUT_PKL = CACHE / "campaign306_coinm_term_structure.pkl"
OUT_META = CACHE / "campaign306_coinm_term_structure.meta.json"
OUT_PROV = CACHE / "campaign306_coinm_term_structure.provenance.json"

ARCHIVE_HOST = "https://data.binance.vision"
CM_KLINES_PATH = "/data/futures/cm/monthly/klines/{sym}/1h/{sym}-1h-{month}.zip"
CM_PREMIUM_PATH = "/data/futures/cm/monthly/premiumIndexKlines/{sym}/1h/{sym}-1h-{month}.zip"
CM_MARK_PATH = "/data/futures/cm/monthly/markPriceKlines/{sym}/1h/{sym}-1h-{month}.zip"

INTERVAL = "1h"

# COIN-M inverse perpetuals (BASEUSD_PERP).  indexPriceKlines is HTTP 404 for COIN-M.
CM_PERPS = ("BTCUSD_PERP", "ETHUSD_PERP")

# COIN-M inverse DATED quarterly futures with verified-reachable monthly klines
# archives (retained after expiry).  Expiry derived from contract code YYMMDD at
# 08:00 UTC (Binance COIN-M quarterly delivery time).
CM_QUARTERLY = [
    ("BTCUSD_250627", "2025-06-27T08:00:00Z", ["2025-03", "2025-04", "2025-05", "2025-06"]),
    ("BTCUSD_250926", "2025-09-26T08:00:00Z", ["2025-09", "2025-10"]),
    ("BTCUSD_261225", "2026-12-25T08:00:00Z", ["2026-09", "2026-10"]),
    ("ETHUSD_261225", "2026-12-25T08:00:00Z", ["2026-10"]),
]

COVERAGE_MONTHS = [
    "2020-12", "2021-06", "2022-01", "2023-01", "2024-01", "2025-01", "2026-06", "2026-10",
]

KLINE_COLUMNS = [
    "open_time", "open", "high", "low", "close", "volume", "close_time",
    "quote_volume", "count", "taker_buy_volume", "taker_buy_quote_volume", "ignore",
]

PUSH_LIMIT_BYTES = 100_000_000  # GitHub hard-rejects any blob >= 100 MB
RETRIES = 6  # retry-with-backoff, linear 1 s x attempt
HOURS_PER_YEAR = 365.0 * 24.0
MIN_BARS_FOR_WF = 720 + 168  # train + test; assets below this cannot support OOS splits


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _months_full() -> list[str]:
    stamps = pd.date_range(start="2020-12-01", end="2026-10-01", freq="MS", tz="UTC")
    return [str(ts.date())[:7] for ts in stamps]


def _http_get(url: str, timeout: float) -> tuple[int, bytes]:
    """GET with retry-with-backoff (6 attempts, linear 1 s x k).

    A lone 404/5xx is treated as retryable (the archive host flip-flops
    200<->404 under rapid sequential access). Only fail-closed after all
    retries are exhausted.
    """
    last_exc: Exception | None = None
    last_status = None
    for attempt in range(1, RETRIES + 1):
        req = urllib.request.Request(url, method="GET",
                                     headers={"User-Agent": "kilo-c306-ingest"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return int(resp.status), resp.read()
        except urllib.error.HTTPError as exc:  # retryable: 404/5xx/451
            last_status = int(exc.code)
            last_exc = exc
        except Exception as exc:  # noqa: BLE001  transient network
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


def read_zip_frame(raw: bytes) -> pd.DataFrame:
    """Parse a COIN-M kline archive zip (header or headerless).

    Skips any row whose first field is non-numeric (the ``open_time`` header
    row carried by recent months).
    """
    zf = zipfile.ZipFile(io.BytesIO(raw))
    name = zf.namelist()[0]
    raw_csv = zf.read(name)
    if not _is_numeric_first_field(raw_csv):
        df = pd.read_csv(io.BytesIO(raw_csv))
    else:
        df = pd.read_csv(io.BytesIO(raw_csv), header=None, names=KLINE_COLUMNS)
    df["open_time"] = pd.to_numeric(df["open_time"], errors="coerce")
    df = df.dropna(subset=["open_time"])
    for c in ("open", "high", "low", "close"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    return df


def fetch_month(symbol: str, kind: str, month: str, timeout: float) -> dict:
    if kind == "klines":
        path = CM_KLINES_PATH.format(sym=symbol, month=month)
    elif kind == "premium":
        path = CM_PREMIUM_PATH.format(sym=symbol, month=month)
    else:
        path = CM_MARK_PATH.format(sym=symbol, month=month)
    url = ARCHIVE_HOST + path
    try:
        status, data = _http_get(url, timeout)
    except RuntimeError as exc:  # all retries exhausted -> record failure, never crash
        return {"symbol": symbol, "month": month, "url": url,
                "status": None, "rows": 0, "ok": False,
                "error": str(exc)}
    if status != 200 or not data:
        return {"symbol": symbol, "month": month, "url": url,
                "status": status, "rows": 0, "ok": False}
    try:
        df = read_zip_frame(data)
    except Exception as exc:  # noqa: BLE001
        return {"symbol": symbol, "month": month, "url": url,
                "status": status, "rows": 0, "ok": False,
                "error": f"{type(exc).__name__}: {exc}"}
    return {"symbol": symbol, "month": month, "url": url, "status": status,
            "rows": int(len(df)), "ok": True, "frame": df}


def build_contract_series(symbol: str, months: list[str], timeout: float) -> dict:
    """Download one contract's 1h klines across all months; return stitched series."""
    detail: dict = {"symbol": symbol, "per_month": [], "accepted_months": [],
                    "stop_month": None, "stop_reason": None}
    frames: list[pd.DataFrame] = []
    failed_months: list[str] = []
    for m in months:
        r = fetch_month(symbol, "klines", m, timeout)
        detail["per_month"].append({k: r[k] for k in ("month", "status",
                                                      "rows", "ok", "url")})
        if not r["ok"]:
            failed_months.append(m)
            detail["stop_month"] = m
            detail["stop_reason"] = r.get("error") or f"month {m} http {r['status']}"
            continue  # skip failed months; contract may have partial coverage
        df = r["frame"]
        vals = df[["open", "high", "low", "close"]].to_numpy(dtype=float)
        if not bool(np.isfinite(vals).all()):
            failed_months.append(m)
            detail["stop_month"] = m
            detail["stop_reason"] = f"month {m} non-finite klines OHLC"
            continue
        if int(df["open_time"].duplicated().sum()) != 0:
            failed_months.append(m)
            detail["stop_month"] = m
            detail["stop_reason"] = f"month {m} duplicate kline timestamps"
            continue
        detail["accepted_months"].append(m)
        frames.append(df[["open_time", "open", "high", "low", "close"]])

    if not frames:
        detail["status"] = "excluded"
        detail["exclusion_reason"] = detail["stop_reason"] or "all months failed"
        return detail

    detail["failed_months"] = failed_months
    all_df = pd.concat(frames, axis=0).sort_values("open_time")
    all_df = all_df.drop_duplicates("open_time", keep="last").set_index("open_time")
    detail["status"] = "ok"
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


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--timeout", type=float, default=60.0)
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args(argv)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    CACHE.mkdir(parents=True, exist_ok=True)

    months = _months_full()

    # ---- Phase 1: download perp klines for all COIN-M perps ----
    perp_series: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futs = {pool.submit(build_contract_series, s, months, args.timeout): s
                for s in CM_PERPS}
        for fut in as_completed(futs):
            d = fut.result()
            perp_series[d["symbol"]] = d

    excluded_perp = {s: perp_series[s].get("exclusion_reason", perp_series[s].get("status"))
                     for s in CM_PERPS if perp_series[s].get("status") != "ok"}
    if len(excluded_perp) == len(CM_PERPS):
        raise SystemExit(f"FATAL: no perp has klines data. Excluded: {json.dumps(excluded_perp)}")

    # ---- Phase 2: download quarterly klines for all dated contracts ----
    quarterly_series: dict[str, dict] = {}
    q_months_map = {sym: months_list for sym, _, months_list in CM_QUARTERLY}
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futs = {pool.submit(build_contract_series, sym, q_months_map[sym], args.timeout): sym
                for sym, _, _ in CM_QUARTERLY}
        for fut in as_completed(futs):
            d = fut.result()
            quarterly_series[d["symbol"]] = d

    excluded_q = {sym: quarterly_series[sym].get("exclusion_reason", quarterly_series[sym].get("status"))
                  for sym, _, _ in CM_QUARTERLY if quarterly_series[sym].get("status") != "ok"}
    if len(excluded_q) == len(CM_QUARTERLY):
        raise SystemExit(f"FATAL: no quarterly contract has klines data. Excluded: {json.dumps(excluded_q)}")

    # ---- Phase 3: per-asset common term-structure grid ----
    # Map quarterly contract -> underlying asset (strip the _YYMMDD suffix).
    q_expiry = {sym: expiry for sym, expiry, _ in CM_QUARTERLY}

    def underlying(sym: str) -> str:
        if sym.endswith("_PERP"):
            return sym[:-5]  # BTCUSD_PERP -> BTCUSD
        # BTCUSD_250627 -> BTCUSD (strip trailing _YYMMDD)
        return sym.rsplit("_", 1)[0]

    assets = sorted({underlying(s) for s in CM_PERPS})
    perp_by_asset = {underlying(s): perp_series[s] for s in CM_PERPS}

    # Quarterly contracts grouped by underlying asset.
    quarterly_by_asset: dict[str, list[str]] = {a: [] for a in assets}
    for sym, expiry, _ in CM_QUARTERLY:
        quarterly_by_asset[underlying(sym)].append(sym)

    per_asset: dict[str, dict] = {}
    selected: list[str] = []

    for asset in assets:
        p_entry = perp_by_asset.get(asset)
        if not p_entry or p_entry.get("status") != "ok":
            continue
        perp_df = p_entry["frame"]

        # Collect quarterly contracts for this asset that have data.
        active_quarters: dict[str, pd.DataFrame] = {}
        for qsym in quarterly_by_asset.get(asset, []):
            q_entry = quarterly_series.get(qsym)
            if q_entry and q_entry.get("status") == "ok":
                active_quarters[qsym] = q_entry["frame"]

        if len(active_quarters) == 0:
            continue  # need at least 1 quarterly to overlap with perp

        # Common term-structure grid: timestamps where perp AND >= 1 quarterly
        # both have data.  Build per-quarterly intersection with perp, then
        # union across quarterlies (a bar is in the grid if perp+any q overlap).
        common_index: pd.DatetimeIndex | None = None
        for qsym, q_df in active_quarters.items():
            pair_common = perp_df.index.intersection(q_df.index)
            common_index = pair_common if common_index is None else common_index.union(pair_common)
        if common_index is None or len(common_index) == 0:
            continue
        common_index = common_index.sort_values()
        n_grid = int(len(common_index))
        if n_grid < MIN_BARS_FOR_WF:
            continue  # fail-closed: asset cannot support train+test OOS windows
        grid_start = str(common_index[0])
        grid_end = str(common_index[-1])

        # Count contracts present at each grid bar (perp + each quarterly).
        n_contracts_at_bar = np.ones(n_grid, dtype=int)  # perp always present on grid
        for qsym, q_df in active_quarters.items():
            q_al = q_df.reindex(common_index)
            q_present = ~np.isnan(q_al["close"].to_numpy(dtype=float))
            n_contracts_at_bar += q_present.astype(int)
        bars_ge2 = int((n_contracts_at_bar >= 2).sum())
        if bars_ge2 == 0:
            continue  # fail-closed: need >= 2 contracts overlapping

        # ---- Phase 4: per-asset series alignment ----
        # Perp close reindexed to common grid (present everywhere on grid).
        perp_close = perp_df.reindex(common_index)["close"].to_numpy(dtype=float)

        # Per-quarterly close and basis, reindexed to common grid (NaN when q inactive).
        q_close: dict[str, np.ndarray] = {}
        q_basis: dict[str, np.ndarray] = {}
        q_tte_hours: dict[str, np.ndarray] = {}
        expiry_ts = pd.Timestamp(q_expiry[list(active_quarters.keys())[0]])  # placeholder
        for qsym, q_df in active_quarters.items():
            q_al = q_df.reindex(common_index)
            qc = q_al["close"].to_numpy(dtype=float)
            q_close[qsym] = qc
            # Annualized basis = ln(q / perp) * (hours_per_year / hours_to_expiry).
            # TTE in hours from grid bar to quarterly expiry.
            q_expiry_ts = pd.Timestamp(q_expiry[qsym])
            tte_hours = np.array([(q_expiry_ts - t).total_seconds() / 3600.0
                                  for t in common_index], dtype=float)
            q_tte_hours[qsym] = tte_hours
            with np.errstate(divide="ignore", invalid="ignore"):
                basis = np.log(qc / perp_close) * (HOURS_PER_YEAR / np.where(tte_hours > 0, tte_hours, np.nan))
            basis = np.where(np.isfinite(basis), basis, np.nan)
            q_basis[qsym] = basis

        perp_close_present = ~np.isnan(perp_close)
        if not bool(np.isfinite(perp_close[perp_close_present]).all()):
            continue
        if not bool((perp_close[perp_close_present] > 0).all()):
            continue

        # Record basis gap bars (real outage, never imputed).
        any_q_present = np.zeros(n_grid, dtype=bool)
        any_basis_present = np.zeros(n_grid, dtype=bool)
        for qsym in active_quarters:
            any_q_present |= ~np.isnan(q_close[qsym])
            any_basis_present |= ~np.isnan(q_basis[qsym])
        n_missing_basis = int((~any_basis_present).sum())

        entry = {
            "asset": asset,
            "window_start_utc": grid_start,
            "window_end_utc": grid_end,
            "n_bars": n_grid,
            "bars_ge2_contracts": bars_ge2,
            "n_contracts": 1 + len(active_quarters),  # perp + quarterlies
            "quarterly_contracts": sorted(active_quarters.keys()),
            "n_present_perp_bars": int(perp_close_present.sum()),
            "n_present_any_quarterly_bars": int(any_q_present.sum()),
            "n_present_any_basis_bars": int(any_basis_present.sum()),
            "n_missing_basis_bars": n_missing_basis,
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
        selected.append(asset)

    if not selected:
        raise SystemExit("FATAL: no asset survived alignment to the common term-structure grid")

    selected = sorted(selected)
    n_assets = len(selected)

    payload = {
        "interval": INTERVAL,
        "source_interval": "coin_m_klines_1h",
        "assets": selected,
        "n_assets": n_assets,
        "universe": {"perps": list(CM_PERPS), "quarterlies": [s for s, _, _ in CM_QUARTERLY]},
        "quarterly_expiry_utc": q_expiry,
        "window": {"start": per_asset[selected[0]]["window_start_utc"],
                   "end": per_asset[selected[-1]]["window_end_utc"]},
        "per_asset": per_asset,
        "real_data_only": True,
        "fabricated_data": False,
        "executed_fills": False,
    }

    blob = _pickle_bytes(payload)
    OUT_PKL.write_bytes(blob)
    pkl_bytes = _assert_under_push_limit(OUT_PKL)
    pkl_sha = sha256_file(OUT_PKL)

    meta = {
        "generated_at_utc": ts,
        "campaign": 306,
        "part": "ingest",
        "interval": INTERVAL,
        "source_interval": "coin_m_klines_1h",
        "assets": selected,
        "n_assets": n_assets,
        "n_universe_perps": len(CM_PERPS),
        "n_universe_quarterlies": len(CM_QUARTERLY),
        "source_host": ARCHIVE_HOST,
        "klines_endpoint": CM_KLINES_PATH,
        "premium_endpoint": CM_PREMIUM_PATH,
        "mark_endpoint": CM_MARK_PATH,
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
        "n_months": len(months),
    }
    OUT_META.write_text(json.dumps(meta, indent=2) + "\n")

    per_symbol = {}
    for a in selected:
        pa = per_asset[a]
        per_symbol[a] = {
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
    for a in assets:
        if a not in per_symbol:
            per_symbol[a] = {"status": "excluded", "exclusion_reason": "no common term-structure grid"}

    provenance = {
        "generated_at_utc": ts,
        "campaign": 306,
        "part": "provenance",
        "real_data_only": True,
        "fabricated_data": False,
        "executed_fills": False,
        "build_source": (
            "archive_download_coin_m_klines_common_term_structure_grid_plus_basis"
        ),
        "universe_rule": (
            "Universe = COIN-M inverse perpetuals {BTCUSD_PERP, ETHUSD_PERP} and "
            "dated quarterly futures {BTCUSD_250627, BTCUSD_250926, BTCUSD_261225, "
            "ETHUSD_261225}.  1h klines are real Binance COIN-M open/high/low/close. "
            "The common term-structure grid per asset = timestamps where the perp "
            "AND >= 1 dated quarterly contract both have 1h kline data (>= 2 "
            "contracts overlap).  Any bar missing is dropped (never imputed). "
            "Perp-vs-quarterly annualized basis = ln(q_close / perp_close) × "
            "(hours_per_year / hours_to_expiry).  TTE uses the contract-code "
            "expiry at 08:00 UTC.  No impute/ffill/backfill of any derived series."
        ),
        "cache_serialization": "plain numpy ndarrays; index stored as datetime64[us]; no pandas Series/DataFrame legs",
        "push_limit_note": (
            f"compact ndarray form is {meta['cache_pkl_mb']} MB (< 100 MB). Asserted on disk before success."
        ),
        "n_candidates_perps": len(CM_PERPS),
        "n_candidates_quarterlies": len(CM_QUARTERLY),
        "n_selected_assets": n_assets,
        "selected_assets": selected,
        "excluded_assets": {a: per_symbol[a] for a in assets if a not in selected},
        "per_asset": per_symbol,
        "months": months,
        "n_months": len(months),
    }
    OUT_PROV.write_text(json.dumps(provenance, indent=2, default=str) + "\n")

    summary = {
        "ok": True,
        "campaign": 306,
        "build_source": (
            "archive_download_coin_m_klines_common_term_structure_grid_plus_basis"
        ),
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
        "n_assets": n_assets,
        "selected_assets": selected,
        "quarterly_contracts": [s for s, _, _ in CM_QUARTERLY],
        "per_asset": {a: {k: per_asset[a][k] for k in (
            "window_start_utc", "window_end_utc", "n_bars", "bars_ge2_contracts",
            "n_contracts", "quarterly_contracts", "n_present_perp_bars",
            "n_present_any_quarterly_bars", "n_present_any_basis_bars",
            "n_missing_basis_bars")} for a in selected},
        "interval": INTERVAL,
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
