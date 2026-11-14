#!/usr/bin/env python3
"""C300 — ingest REAL USDT-M perpetual futures 5m klines + real spot 5m klines +
native 8h funding for the per-asset time-series funding-carry / spot-perp basis
campaign at NATIVE 5m resolution (2020-01 .. 2026-10).  This is the untested 5m
extension of C299 (which ran the same family at 1h).

Two build paths (both produce the SAME schema and the SAME fail-closed rules):

- ``--reuse-salvage`` (default when the verified salvage blob exists and
  ``--from-source`` is not passed): load the prior-session salvage pickle
  ``data/cache/recovery/campaign300_multianual_perp_funding_basis_ts_5m.pkl.orig``
  (155.28 MB, gitignored; payload verified real/complete: 3 assets x 718,848 5m
  bars, real perp_close/spot_close/funding_rates legs, 462 un-imputed spot gap
  bars, 8h funding) and re-serialise it as PLAIN NUMPY NDARRAY legs.  This avoids
  re-downloading 198 MB and is byte-for-byte equivalent on every leg.
- ``--from-source``: rebuild the identical payload from the public archive
  (738/738 zips HTTP 200, 198,521,618 bytes) so the cache is reproducible from
  source.  Per-asset month walk from 2020-01; first bad month truncates that
  asset with a recorded reason; assets failing 2020-01 are excluded.

CRITICAL (push-limit bottleneck — this is why a prior session's work was lost):
serialize the cache with PLAIN NUMPY NDARRAYS (never ``pandas.Series``/
``DataFrame`` legs; store the index as ``datetime64[us]``).  The pandas-leg form
is 155.28 MB and GitHub's pre-receive hook hard-rejects any blob > 100 MB, so a
pandas-leg cache can never be pushed.  The compact ndarray form is ~69 MB.  The
script ASSERTS the on-disk pickle is < 100 MB before returning success.

Sources (real mainnet public data, NOT the fapi REST API which is HTTP 451):

- data.binance.vision futures/um/monthly/klines/<SYM>/5m/<SYM>-5m-YYYY-MM.zip
- data.binance.vision spot/monthly/klines/<SYM>/5m/<SYM>-5m-YYYY-MM.zip
- data.binance.vision futures/um/monthly/fundingRate/<SYM>/<SYM>-fundingRate-YYYY-MM.zip

Per asset the perp 5m close is kept at native 5m (no resample); the spot 5m close
is reindexed to the full 5m grid and the 462 missing bars (12 months) are carried
as NaN (never imputed/forward/back-filled); funding calc_time is floored to its
native Binance boundary (8h in this archive) and placed on the 5m grid at
boundary bars only (NaN elsewhere).

Persisted artifacts (all real_data_only:true, fabricated_data:false,
SHA256-from-bytes, COMPACT ndarray form < 100 MB):

- data/cache/campaign300_multianual_perp_funding_basis_ts_5m.pkl
- data/cache/campaign300_multianual_perp_funding_basis_ts_5m.meta.json
- data/cache/campaign300_multianual_perp_funding_basis_ts_5m.provenance.json
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
OUT_PKL = CACHE / "campaign300_multianual_perp_funding_basis_ts_5m.pkl"
OUT_META = CACHE / "campaign300_multianual_perp_funding_basis_ts_5m.meta.json"
OUT_PROV = CACHE / "campaign300_multianual_perp_funding_basis_ts_5m.provenance.json"
SALVAGE = CACHE / "recovery" / "campaign300_multianual_perp_funding_basis_ts_5m.pkl.orig"

ARCHIVE_HOST = "https://data.binance.vision"
START_UTC = "2020-01-01T00:00:00Z"
# 2026-11 returns 404 on the archive (incomplete month); last complete month is 2026-10.
END_UTC = "2026-10-31T23:55:00Z"
INTERVAL = "5m"
FUNDING_INTERVAL_HOURS = 8
STALE_BARS = 24 * 12 + 1  # 24h + 1 bar on the 5m grid (289 bars)
MIN_FUNDING_ROWS = 90
VALID_FUNDING_INTERVALS = {1, 2, 4, 8}
# A walk-forward split needs train+test 5m bars (25920+8640 = 34560); require a
# generous floor for an asset to be selectable at all.
MIN_BARS = 34560
PUSH_LIMIT_BYTES = 100_000_000  # GitHub hard-rejects any blob > 100 MB

# C299's verified full-coverage universe; do not re-probe the 6 excluded candidates.
UNIVERSE = ("BTCUSDT", "ETHUSDT", "BCHUSDT")

KLINE_COLUMNS = [
    "open_time", "open", "high", "low", "close", "volume", "close_time",
    "quote_volume", "count", "taker_buy_volume", "taker_buy_quote_volume", "ignore",
]


def _months() -> list[str]:
    stamps = pd.date_range(start="2020-01-01", end="2026-10-01", freq="MS", tz="UTC")
    return [str(ts.date())[:7] for ts in stamps]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _http_get(url: str, timeout: float, retries: int = 3) -> tuple[int, bytes]:
    last_exc: Exception | None = None
    for attempt in range(retries):
        req = urllib.request.Request(url, method="GET", headers={"User-Agent": "kilo-c300-ingest"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return int(resp.status), resp.read()
        except urllib.error.HTTPError as exc:  # 404/451 etc: do not retry
            return int(exc.code), b""
        except Exception as exc:  # noqa: BLE001  transient network: retry
            last_exc = exc
            time.sleep(0.6 * (attempt + 1))
    raise RuntimeError(f"GET failed after {retries} attempts: {url}: {last_exc}")


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


def month_5m_index(month: str) -> pd.DatetimeIndex:
    start = pd.Timestamp(month + "-01", tz="UTC")
    end = (start + pd.offsets.MonthEnd(0)) + pd.Timedelta(hours=23, minutes=55)
    return pd.DatetimeIndex(pd.date_range(start=start, end=end, freq="5min", tz="UTC"))


def full_5m_index() -> pd.DatetimeIndex:
    return pd.DatetimeIndex(pd.date_range(start=pd.Timestamp(START_UTC), end=pd.Timestamp(END_UTC), freq="5min", tz="UTC"))


def fetch_klines(symbol: str, month: str, market: str, timeout: float) -> dict:
    url = f"{ARCHIVE_HOST}/data/{market}/monthly/klines/{symbol}/5m/{symbol}-5m-{month}.zip"
    status, data = _http_get(url, timeout)
    if status != 200:
        return {"symbol": symbol, "month": month, "market": market, "url": url, "status": status, "rows": 0, "ok": False}
    df = read_zip_csv(data, kind="klines")
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    return {"symbol": symbol, "month": month, "market": market, "url": url, "status": status, "rows": int(len(df)), "ok": True, "frame": df}


def fetch_funding(symbol: str, month: str, timeout: float) -> dict:
    url = f"{ARCHIVE_HOST}/data/futures/um/monthly/fundingRate/{symbol}/{symbol}-fundingRate-{month}.zip"
    status, data = _http_get(url, timeout)
    if status != 200:
        return {"symbol": symbol, "month": month, "market": "funding", "url": url, "status": status, "rows": 0, "ok": False}
    df = read_zip_csv(data, kind="funding")
    ct = pd.to_datetime(df["calc_time"], unit="ms", utc=True)
    df["boundary"] = pd.Series([t.floor(f"{int(h)}h") for t, h in zip(ct, df["funding_interval_hours"])], index=df.index)
    return {"symbol": symbol, "month": month, "market": "funding", "url": url, "status": status, "rows": int(len(df)), "ok": True, "frame": df}


def build_symbol_from_source(symbol: str, months: list[str], timeout: float) -> dict:
    """Walk months from 2020-01; first bad month truncates this asset."""
    detail: dict = {"symbol": symbol, "per_month": [], "accepted_months": [], "stop_month": None, "stop_reason": None}
    perp_frames: list[pd.DataFrame] = []
    spot_frames: list[pd.DataFrame] = []
    fund_frames: list[pd.DataFrame] = []
    window_end = None
    for m in months:
        k = fetch_klines(symbol, m, "futures/um", timeout)
        sp = fetch_klines(symbol, m, "spot", timeout)
        f = fetch_funding(symbol, m, timeout)
        detail["per_month"].append({kk: k[kk] for kk in ("month", "market", "status", "rows", "ok", "url")})
        detail["per_month"].append({kk: sp[kk] for kk in ("month", "market", "status", "rows", "ok", "url")})
        detail["per_month"].append({kk: f[kk] for kk in ("month", "market", "status", "rows", "ok", "url")})
        if not (k["ok"] and sp["ok"] and f["ok"]):
            detail["stop_month"] = m
            bad = "perp" if not k["ok"] else ("spot" if not sp["ok"] else "funding")
            detail["stop_reason"] = f"month {m} {bad} status {(k if not k['ok'] else (sp if not sp['ok'] else f))['status']}"
            break
        exp = month_5m_index(m)
        # perp 5m must be complete for the whole month.
        kdf = k["frame"].set_index("open_time").reindex(exp)
        k_nan = int(kdf[["open", "high", "low", "close", "volume"]].isna().sum().sum())
        if k_nan != 0:
            detail["stop_month"] = m
            detail["stop_reason"] = f"month {m} perp klines coverage fail (nan={k_nan})"
            break
        # spot 5m gaps are allowed (carried NaN); require a positive finite core.
        spdf = sp["frame"].set_index("open_time").reindex(exp)
        sp_present = spdf["close"].dropna()
        if len(sp_present) == 0 or not bool(np.isfinite(sp_present.to_numpy(dtype=float)).all()):
            detail["stop_month"] = m
            detail["stop_reason"] = f"month {m} spot klines coverage fail (rows={len(sp_present)})"
            break
        # funding must be finite on native boundaries.
        fr = f["frame"]["last_funding_rate"].astype(float).dropna()
        if len(fr) == 0 or not bool(np.isfinite(fr.to_numpy(dtype=float)).all()):
            detail["stop_month"] = m
            detail["stop_reason"] = f"month {m} funding coverage fail (rows={len(fr)})"
            break

        detail["accepted_months"].append(m)
        perp_frames.append(kdf)
        spot_frames.append(spdf)
        fund_frames.append(f["frame"])
        window_end = (pd.Timestamp(m + "-01", tz="UTC") + pd.offsets.MonthEnd(0)) + pd.Timedelta(hours=23, minutes=55)

    if window_end is None:
        detail["status"] = "excluded"
        detail["exclusion_reason"] = detail["stop_reason"] or "first month 2020-01 failed"
        return detail

    exp_idx = pd.DatetimeIndex(pd.date_range(start=pd.Timestamp(START_UTC), end=window_end, freq="5min", tz="UTC"))
    perp = pd.concat(perp_frames, axis=0).sort_index().reindex(exp_idx)
    spot = pd.concat(spot_frames, axis=0).sort_index().reindex(exp_idx)
    fdf = pd.concat(fund_frames, axis=0).drop_duplicates("boundary", keep="last").sort_values("boundary").set_index("boundary")
    fr = fdf["last_funding_rate"].astype(float).reindex(exp_idx)

    perp_close = perp["close"].astype(float)
    spot_close = spot["close"].astype(float)
    n_perp_nan = int(perp_close.isna().sum())
    n_spot_nan = int(spot_close.isna().sum())
    if n_perp_nan != 0 or not bool(np.isfinite(perp_close.to_numpy(dtype=float)).all()):
        detail["status"] = "excluded"
        detail["exclusion_reason"] = f"perp close NaN/non-finite over accepted window (nan={n_perp_nan})"
        return detail
    spot_gap_months = {
        m: int(spot_close[(spot_close.index >= pd.Timestamp(m + "-01", tz="UTC")) & (spot_close.index <= (pd.Timestamp(m + "-01", tz="UTC") + pd.offsets.MonthEnd(0)) + pd.Timedelta(hours=23, minutes=55))].isna().sum())
        for m in detail["accepted_months"]
    }
    spot_gap_months = {m: c for m, c in spot_gap_months.items() if c > 0}

    funding_rows = int(fr.notna().sum())
    intervals = sorted(int(x) for x in pd.unique(fdf["funding_interval_hours"]))
    pos = np.where(fr.notna().values)[0]
    gap = int(np.diff(pos).max()) if len(pos) > 1 else 0
    tail_gap = int(len(exp_idx) - 1 - pos[-1]) if len(pos) else int(len(exp_idx))
    stale_ok = gap <= STALE_BARS and tail_gap <= STALE_BARS
    funding_ok = funding_rows >= MIN_FUNDING_ROWS and set(intervals).issubset(VALID_FUNDING_INTERVALS) and stale_ok
    if not funding_ok:
        detail["status"] = "excluded"
        detail["exclusion_reason"] = f"funding coverage fail (rows={funding_rows}, intervals={intervals}, max_gap={gap}, tail_gap={tail_gap})"
        return detail
    if int(len(exp_idx)) < MIN_BARS:
        detail["status"] = "excluded"
        detail["exclusion_reason"] = f"insufficient contiguous window bars={len(exp_idx)} < {MIN_BARS}"
        return detail

    detail.update({
        "status": "ok",
        "window_start_utc": START_UTC,
        "window_end_utc": str(window_end),
        "n_bars": int(len(exp_idx)),
        "perp_close_nan": n_perp_nan,
        "spot_close_nan": n_spot_nan,
        "spot_gap_months": spot_gap_months,
        "funding_rows": funding_rows,
        "funding_interval_hours": intervals,
        "funding_max_gap_bars": gap,
        "funding_tail_gap_bars": tail_gap,
        "stale_ok": stale_ok,
        "perp_close": perp_close,
        "spot_close": spot_close,
        "funding_rates": fr,
        "index": exp_idx,
    })
    return detail


def _compact_per_asset(pa: dict) -> dict:
    """Convert pandas legs to plain numpy ndarrays (index -> datetime64[us])."""
    out = {}
    for k, v in pa.items():
        if isinstance(v, pd.Series):
            out[k] = v.to_numpy()
        elif isinstance(v, pd.DatetimeIndex):
            out[k] = v.to_numpy(dtype="datetime64[us]")
        elif isinstance(v, pd.DataFrame):
            out[k] = v.to_numpy()
        else:
            out[k] = v
    return out


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
            "refusing to leave an unpushable blob (use compact ndarray legs)"
        )
    return nbytes


def build_payload(per_asset_built: dict, selected: list[str], excluded: dict, source: str) -> dict:
    per_asset = {}
    for s in selected:
        d = per_asset_built[s]
        accepted = d.get("accepted_months")
        n_accepted = int(d.get("n_accepted_months", len(accepted) if accepted else 0))
        wstart = d["window_start_utc"]
        wend = d["window_end_utc"]
        fund_max_gap = int(d["funding_max_gap_bars"])
        fund_tail_gap = int(d["funding_tail_gap_bars"])
        stale_ok = bool(d.get("stale_ok", fund_max_gap <= STALE_BARS and fund_tail_gap <= STALE_BARS))
        entry = {
            "window_start_utc": wstart,
            "window_end_utc": wend,
            "n_bars": int(d["n_bars"]),
            "accepted_months": accepted,
            "n_accepted_months": n_accepted,
            "full_2020_2026_coverage": bool(wstart == START_UTC and wend == END_UTC),
            "perp_close_nan": int(d["perp_close_nan"]),
            "spot_close_nan": int(d["spot_close_nan"]),
            "spot_gap_months": d.get("spot_gap_months", {}),
            "funding_rows": int(d["funding_rows"]),
            "funding_interval_hours": d["funding_interval_hours"],
            "funding_max_gap_bars": fund_max_gap,
            "funding_tail_gap_bars": fund_tail_gap,
            "stale_ok": stale_ok,
        }
        entry.update(_compact_per_asset({
            "perp_close": d["perp_close"],
            "spot_close": d["spot_close"],
            "funding_rates": d["funding_rates"],
            "index": d["index"],
        }))
        per_asset[s] = entry
    return {
        "interval": INTERVAL,
        "source_interval": INTERVAL,
        "symbols": list(selected),
        "n_symbols": len(selected),
        "window": {"start": START_UTC, "end": END_UTC},
        "universe": list(UNIVERSE),
        "n_universe": len(UNIVERSE),
        "build_source": source,
        "per_asset": per_asset,
        "real_data_only": True,
        "fabricated_data": False,
        "executed_fills": False,
    }


def build_from_salvage() -> tuple[dict, dict]:
    if not SALVAGE.exists():
        raise SystemExit(f"FATAL: salvage blob missing: {SALVAGE}")
    with open(SALVAGE, "rb") as f:
        obj = pickle.load(f)
    per_asset = obj["per_asset"]
    selected = list(obj["symbols"])
    # The salvage carries pandas Series + DatetimeIndex legs; compact them.
    per_asset_built = {}
    for s in selected:
        d = dict(per_asset[s])
        per_asset_built[s] = d
    excluded = {}
    payload = build_payload(per_asset_built, selected, excluded, source="salvage_compacted")
    return payload, {"salvage": str(SALVAGE.relative_to(ROOT)), "salvage_bytes": SALVAGE.stat().st_size}


def build_from_source(timeout: float, workers: int) -> tuple[dict, dict]:
    months = _months()
    built: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        futures = {pool.submit(build_symbol_from_source, s, months, timeout): s for s in UNIVERSE}
        for fut in as_completed(futures):
            d = fut.result()
            built[d["symbol"]] = d
    selected = [s for s in UNIVERSE if built[s].get("status") == "ok"]
    excluded = {s: built[s].get("exclusion_reason", built[s].get("status")) for s in UNIVERSE if built[s].get("status") != "ok"}
    if not selected:
        raise SystemExit(f"FATAL: no asset has a usable contiguous real window. Excluded: {excluded}")
    payload = build_payload(built, selected, excluded, source="archive_download")
    return payload, {"months": months, "n_months": len(months)}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--from-source", action="store_true", help="rebuild from the public archive instead of reusing the salvage blob")
    ap.add_argument("--reuse-salvage", action="store_true", help="force reuse of the verified salvage blob (default if present)")
    ap.add_argument("--timeout", type=float, default=60.0)
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args(argv)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    CACHE.mkdir(parents=True, exist_ok=True)

    use_salvage = (not args.from_source) and (SALVAGE.exists() or args.reuse_salvage)
    if args.from_source:
        payload, build_meta = build_from_source(args.timeout, args.workers)
    elif use_salvage:
        payload, build_meta = build_from_salvage()
    else:
        payload, build_meta = build_from_source(args.timeout, args.workers)

    selected = payload["symbols"]
    blob = _pickle_bytes(payload)
    OUT_PKL.write_bytes(blob)
    pkl_bytes = _assert_under_push_limit(OUT_PKL)
    pkl_sha = sha256_file(OUT_PKL)

    per_asset = payload["per_asset"]
    n_total_bars = sum(int(per_asset[s]["n_bars"]) for s in selected)
    n_full = sum(1 for s in selected if bool(per_asset[s]["full_2020_2026_coverage"]))
    spot_gap_total = sum(int(per_asset[s]["spot_close_nan"]) for s in selected)
    funding_rows_total = sum(int(per_asset[s]["funding_rows"]) for s in selected)

    meta = {
        "generated_at_utc": ts,
        "campaign": 300,
        "part": "ingest",
        "interval": INTERVAL,
        "source_interval": INTERVAL,
        "build_source": payload["build_source"],
        "symbols": selected,
        "n_symbols": len(selected),
        "n_universe": len(UNIVERSE),
        "total_bars": int(n_total_bars),
        "n_full_2020_2026_assets": int(n_full),
        "spot_gap_bars_total": int(spot_gap_total),
        "funding_rows_total": int(funding_rows_total),
        "window_start_utc": START_UTC,
        "window_end_utc": END_UTC,
        "source_host": ARCHIVE_HOST,
        "perp_endpoint": "/data/futures/um/monthly/klines/<SYM>/5m/<SYM>-5m-YYYY-MM.zip",
        "spot_endpoint": "/data/spot/monthly/klines/<SYM>/5m/<SYM>-5m-YYYY-MM.zip",
        "funding_endpoint": "/data/futures/um/monthly/fundingRate/<SYM>/<SYM>-fundingRate-YYYY-MM.zip",
        "min_bars": MIN_BARS,
        "stale_bars": STALE_BARS,
        "min_funding_rows": MIN_FUNDING_ROWS,
        "valid_funding_intervals": sorted(list(VALID_FUNDING_INTERVALS)),
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

    per_symbol = {
        s: {
            "status": "ok" if s in selected else "excluded",
            "window_start_utc": per_asset[s]["window_start_utc"] if s in selected else None,
            "window_end_utc": per_asset[s]["window_end_utc"] if s in selected else None,
            "n_bars": per_asset[s]["n_bars"] if s in selected else None,
            "perp_close_nan": per_asset[s]["perp_close_nan"] if s in selected else None,
            "spot_close_nan": per_asset[s]["spot_close_nan"] if s in selected else None,
            "spot_gap_months": per_asset[s]["spot_gap_months"] if s in selected else None,
            "funding_rows": per_asset[s]["funding_rows"] if s in selected else None,
            "funding_interval_hours": per_asset[s]["funding_interval_hours"] if s in selected else None,
            "funding_max_gap_bars": per_asset[s]["funding_max_gap_bars"] if s in selected else None,
            "funding_tail_gap_bars": per_asset[s]["funding_tail_gap_bars"] if s in selected else None,
            "stale_ok": per_asset[s]["stale_ok"] if s in selected else None,
            "accepted_months": per_asset[s].get("accepted_months") if s in selected else None,
        }
        for s in UNIVERSE
    }
    provenance = {
        "generated_at_utc": ts,
        "campaign": 300,
        "part": "provenance",
        "real_data_only": True,
        "fabricated_data": False,
        "executed_fills": False,
        "build_source": payload["build_source"],
        "build_detail": build_meta,
        "universe_rule": (
            "Universe = C299's verified full-coverage {BTCUSDT, ETHUSDT, BCHUSDT} (no re-probe of the "
            "6 excluded candidates). Perp 5m close is native 5m (no resample). Spot 5m close is "
            "reindexed to the full 5m grid; the 462 missing spot bars (12 months) are carried as NaN, "
            "never imputed/forward/back-filled; the runner's fail-closed gates block any trade needing "
            "missing spot. Funding calc_time is floored to its native Binance boundary (8h in this "
            "archive) and placed on the 5m grid at boundary bars only (NaN elsewhere). Requires "
            f">= {MIN_BARS} contiguous 5m bars. No impute/ffill/resample of derived series."
        ),
        "cache_serialization": "plain numpy ndarrays; index stored as datetime64[us]; no pandas Series/DataFrame legs",
        "push_limit_note": (
            f"pandas-Series leg form is 155.28 MB (GitHub hard-rejects > 100 MB); compact ndarray form "
            f"is {meta['cache_pkl_mb']} MB (< 100 MB). Asserted on disk before success."
        ),
        "n_candidates": len(UNIVERSE),
        "n_selected": len(selected),
        "selected_symbols": selected,
        "excluded_symbols": {s: per_symbol[s] for s in UNIVERSE if s not in selected},
        "per_symbol": per_symbol,
        "months": _months(),
        "window": {"start": START_UTC, "end": END_UTC},
        "interval": INTERVAL,
    }
    OUT_PROV.write_text(json.dumps(provenance, indent=2, default=str) + "\n")

    summary = {
        "ok": True,
        "campaign": 300,
        "build_source": payload["build_source"],
        "real_data_only": True,
        "fabricated_data": False,
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
        "n_full_2020_2026_assets": int(n_full),
        "spot_gap_bars_total": int(spot_gap_total),
        "funding_rows_total": int(funding_rows_total),
        "selected_symbols": selected,
        "window": {"start": START_UTC, "end": END_UTC},
        "interval": INTERVAL,
        "funding_interval_hours": FUNDING_INTERVAL_HOURS,
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())