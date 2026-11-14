#!/usr/bin/env python3
"""C302 — ingest REAL Binance USDT-M perpetual ``premiumIndexKlines`` (native 1h,
2020-01 .. 2026-10) and build per-asset continuous premium-index feature panels for
the C302 per-asset time-series premium-index stat-arb campaign.

This is a genuinely new REAL data family.  ``premiumIndexKlines`` is the real-time
fair-value premium index (mark vs index) that Binance uses to set funding.  It is a
distinct, higher-frequency real signal from the realized funding rate and the
perp/spot close basis used by C291/C293/C298/C299/C300, and it has never been
ingested by any prior campaign in this repository.

Data (real, fail-closed; the ``fapi`` REST API is HTTP 451 and is NOT used):

- ``https://data.binance.vision/data/futures/um/monthly/premiumIndexKlines/<SYM>/1h/<SYM>-1h-YYYY-MM.zip``
- Universe: C299's verified full-coverage {BTCUSDT, ETHUSDT, BCHUSDT}
  (each verified to have 82/82 monthly premium-index zips over 2020-01..2026-10).
- Schema: kline-shaped CSV, 12 columns
  ``open_time,open,high,low,close,volume,close_time,quote_volume,count,
  taker_buy_volume,taker_buy_quote_volume,ignore``; header present or absent by
  month (handled generically).  ``open_time`` is epoch MILLISECONDS; the premium
  ``close`` is a signed fraction (~ +/-1e-3).

Execution price + funding (reused from the verified C299 cache, NOT re-downloaded):

- ``data/cache/campaign299_multianual_perp_funding_basis_ts.pkl`` supplies real perp
  1h close and native 8h funding over 2020-01..2026-10 for the same 3 assets.  The
  premium-index bars are aligned to each asset's C299 1h index (verified identical
  grid); the runner trades on real perp close + real funding cashflows,
  ``executed_fills: false``.

Fail-closed (never impute / forward-fill / back-fill):

- any 404 / empty month / non-finite premium value / missing bar blocks the asset
  with a recorded reason;
- per-asset coverage and every gap bar are recorded.

Serialized artifacts (all real_data_only:true, fabricated_data:false,
executed_fills:false, SHA256-from-bytes, COMPACT ndarray form < 100 MB):

- ``data/cache/campaign302_premium_index_basis.pkl``
- ``data/cache/campaign302_premium_index_basis.meta.json``
- ``data/cache/campaign302_premium_index_basis.provenance.json``
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
OUT_PKL = CACHE / "campaign302_premium_index_basis.pkl"
OUT_META = CACHE / "campaign302_premium_index_basis.meta.json"
OUT_PROV = CACHE / "campaign302_premium_index_basis.provenance.json"

C299_CACHE = CACHE / "campaign299_multianual_perp_funding_basis_ts.pkl"
C299_META = CACHE / "campaign299_multianual_perp_funding_basis_ts.meta.json"
C299_PROV = CACHE / "campaign299_multianual_perp_funding_basis_ts.provenance.json"

ARCHIVE_HOST = "https://data.binance.vision"
PREMIUM_PATH = "/data/futures/um/monthly/premiumIndexKlines/{sym}/1h/{sym}-1h-{month}.zip"

START_UTC = "2020-01-01T00:00:00Z"
END_UTC = "2026-10-31T23:00:00Z"
INTERVAL = "1h"

UNIVERSE = ("BTCUSDT", "ETHUSDT", "BCHUSDT")

KLINE_COLUMNS = [
    "open_time", "open", "high", "low", "close", "volume", "close_time",
    "quote_volume", "count", "taker_buy_volume", "taker_buy_quote_volume", "ignore",
]

PUSH_LIMIT_BYTES = 100_000_000  # GitHub hard-rejects any blob > 100 MB

# Minimum contiguous 1h bars to attempt a per-asset WF split (train+test).
MIN_BARS = 2160 + 720  # train + one test (per C299 WF)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _months() -> list[str]:
    stamps = pd.date_range(start="2020-01-01", end="2026-10-01", freq="MS", tz="UTC")
    return [str(ts.date())[:7] for ts in stamps]


def _http_get(url: str, timeout: float, retries: int = 3) -> tuple[int, bytes]:
    last_exc: Exception | None = None
    for attempt in range(retries):
        req = urllib.request.Request(url, method="GET", headers={"User-Agent": "kilo-c302-ingest"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return int(resp.status), resp.read()
        except urllib.error.HTTPError as exc:  # 404/451: do not retry
            return int(exc.code), b""
        except Exception as exc:  # noqa: BLE001  transient network: retry
            last_exc = exc
            time.sleep(0.6 * (attempt + 1))
    raise RuntimeError(f"GET failed after {retries} attempts: {url}: {last_exc}")


def read_premium_zip(zip_bytes: bytes) -> pd.DataFrame:
    """Parse a premiumIndexKlines zip generically (header or headerless)."""
    zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    name = zf.namelist()[0]
    raw = zf.read(name)
    first_nl = raw.find(b"\n")
    first_line = raw[: first_nl if first_nl >= 0 else len(raw)]
    has_header = b"open_time" in first_line
    if has_header:
        df = pd.read_csv(io.BytesIO(raw))
    else:
        df = pd.read_csv(io.BytesIO(raw), header=None, names=KLINE_COLUMNS)
    df["open_time"] = pd.to_numeric(df["open_time"], errors="coerce")
    df = df.dropna(subset=["open_time"])
    for c in ("open", "high", "low", "close"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    return df


def fetch_premium_month(symbol: str, month: str, timeout: float) -> dict:
    url = ARCHIVE_HOST + PREMIUM_PATH.format(sym=symbol, month=month)
    status, data = _http_get(url, timeout)
    if status != 200:
        return {"symbol": symbol, "month": month, "url": url, "status": status, "rows": 0, "ok": False}
    df = read_premium_zip(data)
    return {"symbol": symbol, "month": month, "url": url, "status": status,
            "rows": int(len(df)), "ok": True, "frame": df}


def load_c299_index(symbol: str) -> pd.DatetimeIndex:
    if not C299_CACHE.exists():
        raise SystemExit(f"FATAL: C299 cache missing: {C299_CACHE}")
    with open(C299_CACHE, "rb") as f:
        p = pickle.load(f)
    pa = p["per_asset"][symbol]
    idx = pa["index"]
    if not isinstance(idx, pd.DatetimeIndex):
        idx = pd.DatetimeIndex(pd.asarray(idx))
    return idx


def build_symbol(symbol: str, months: list[str], timeout: float) -> dict:
    detail: dict = {"symbol": symbol, "per_month": [], "accepted_months": [],
                    "stop_month": None, "stop_reason": None}
    frames: list[pd.DataFrame] = []
    for m in months:
        r = fetch_premium_month(symbol, m, timeout)
        detail["per_month"].append({k: r[k] for k in ("month", "status", "rows", "ok", "url")})
        if not r["ok"]:
            detail["stop_month"] = m
            detail["stop_reason"] = f"month {m} http status {r['status']}"
            break
        df = r["frame"]
        # Fail-closed: premium OHLC must be finite; close is the tradable premium.
        vals = df[["open", "high", "low", "close"]].to_numpy(dtype=float)
        if not bool(np.isfinite(vals).all()):
            detail["stop_month"] = m
            detail["stop_reason"] = f"month {m} non-finite premium OHLC present"
            break
        if int(df["open_time"].duplicated().sum()) != 0:
            detail["stop_month"] = m
            detail["stop_reason"] = f"month {m} duplicate premium bar timestamps"
            break
        detail["accepted_months"].append(m)
        frames.append(df)

    if not frames:
        detail["status"] = "excluded"
        detail["exclusion_reason"] = detail["stop_reason"] or "first month failed"
        return detail

    all_df = pd.concat(frames, axis=0).sort_values("open_time")
    all_df = all_df.drop_duplicates("open_time", keep="last").set_index("open_time").sort_index()

    # Align to the asset's C299 1h execution grid (real perp close + funding).
    # Bars absent from the premium archive are REAL outages (e.g. the 2021-07-01
    # gap): they are carried as NaN and NEVER imputed.  The runner's fail-closed
    # gates make premium/score NaN there -> flat, so no trade uses a missing bar.
    idx = load_c299_index(symbol)
    aligned = all_df.reindex(idx)
    n_missing = int(aligned["close"].isna().sum())
    gap_bars = [str(b) for b in aligned.index[aligned["close"].isna().values]]
    prem = aligned[["open", "high", "low", "close"]].to_numpy(dtype=float)
    present = ~np.isnan(prem[:, 3])
    if not bool(np.isfinite(prem[present]).all()):
        detail["status"] = "excluded"
        detail["exclusion_reason"] = "non-finite premium on present bars after alignment"
        return detail
    if int(present.sum()) == 0:
        detail["status"] = "excluded"
        detail["exclusion_reason"] = "no present premium bars after alignment"
        return detail

    if int(len(idx)) < MIN_BARS:
        detail["status"] = "excluded"
        detail["exclusion_reason"] = f"insufficient contiguous window bars={len(idx)} < {MIN_BARS}"
        return detail

    detail.update({
        "status": "ok",
        "window_start_utc": START_UTC,
        "window_end_utc": END_UTC,
        "n_bars": int(len(idx)),
        "n_accepted_months": len(detail["accepted_months"]),
        "n_missing_vs_c299": n_missing,
        "n_present_bars": int(present.sum()),
        "gap_bars_first": gap_bars[0] if gap_bars else None,
        "gap_bars_last": gap_bars[-1] if gap_bars else None,
        "prem_open": aligned["open"].to_numpy(dtype=float),
        "prem_high": aligned["high"].to_numpy(dtype=float),
        "prem_low": aligned["low"].to_numpy(dtype=float),
        "prem_close": aligned["close"].to_numpy(dtype=float),
        "index": idx,
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
    ap.add_argument("--timeout", type=float, default=60.0)
    ap.add_argument("--workers", type=int, default=3)
    args = ap.parse_args(argv)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    CACHE.mkdir(parents=True, exist_ok=True)

    # Verify the C299 reuse source exists + flags before doing any work.
    if not C299_META.exists():
        raise SystemExit(f"FATAL: C299 meta missing: {C299_META}")
    c299_meta = json.loads(C299_META.read_text())
    if c299_meta.get("real_data_only") is not True or c299_meta.get("fabricated_data") is not False:
        raise SystemExit("FATAL: C299 cache provenance flags invalid")
    # C299 predates the executed_fills field; if present it must be false.
    if "executed_fills" in c299_meta and c299_meta.get("executed_fills") is not False:
        raise SystemExit("FATAL: C299 cache executed_fills must be false")

    months = _months()
    built: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = {pool.submit(build_symbol, s, months, args.timeout): s for s in UNIVERSE}
        for fut in as_completed(futures):
            d = fut.result()
            built[d["symbol"]] = d

    selected = [s for s in UNIVERSE if built[s].get("status") == "ok"]
    excluded = {s: built[s].get("exclusion_reason", built[s].get("status")) for s in UNIVERSE if built[s].get("status") != "ok"}
    if not selected:
        raise SystemExit(f"FATAL: no asset has a usable real premium-index window. Excluded: {json.dumps(excluded)}")

    per_asset = {}
    for s in selected:
        d = built[s]
        entry = {
            "window_start_utc": START_UTC,
            "window_end_utc": END_UTC,
            "n_bars": int(d["n_bars"]),
            "n_accepted_months": int(d["n_accepted_months"]),
            "n_missing_vs_c299": int(d["n_missing_vs_c299"]),
            "n_present_bars": int(d["n_present_bars"]),
            "gap_bars_first": d["gap_bars_first"],
            "gap_bars_last": d["gap_bars_last"],
            "accepted_months": d["accepted_months"],
        }
        entry.update(_compact({
            "prem_open": d["prem_open"],
            "prem_high": d["prem_high"],
            "prem_low": d["prem_low"],
            "prem_close": d["prem_close"],
            "index": d["index"],
        }))
        per_asset[s] = entry

    payload = {
        "interval": INTERVAL,
        "source_interval": "premiumIndex_1h",
        "symbols": list(selected),
        "n_symbols": len(selected),
        "window": {"start": START_UTC, "end": END_UTC},
        "universe": list(UNIVERSE),
        "n_universe": len(UNIVERSE),
        "execution_price_source": "C299_cache_perp_close_1h",
        "funding_source": "C299_cache_native_8h_funding",
        "c299_cache": str(C299_CACHE.relative_to(ROOT)),
        "c299_cache_sha256": sha256_file(C299_CACHE),
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

    meta = {
        "generated_at_utc": ts,
        "campaign": 302,
        "part": "ingest",
        "interval": INTERVAL,
        "source_interval": "premiumIndex_1h",
        "symbols": selected,
        "n_symbols": len(selected),
        "n_universe": len(UNIVERSE),
        "total_bars": int(n_total_bars),
        "window_start_utc": START_UTC,
        "window_end_utc": END_UTC,
        "source_host": ARCHIVE_HOST,
        "premium_endpoint": PREMIUM_PATH,
        "execution_price_source": "C299_cache_perp_close_1h",
        "funding_source": "C299_cache_native_8h_funding",
        "c299_cache": str(C299_CACHE.relative_to(ROOT)),
        "c299_cache_sha256": sha256_file(C299_CACHE),
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
        "n_months": len(months),
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
                "n_accepted_months": pa["n_accepted_months"],
                "n_missing_vs_c299": pa["n_missing_vs_c299"],
                "n_present_bars": pa["n_present_bars"],
                "gap_bars_first": pa["gap_bars_first"],
                "gap_bars_last": pa["gap_bars_last"],
            }
        else:
            per_symbol[s] = {"status": "excluded", "exclusion_reason": excluded.get(s)}

    provenance = {
        "generated_at_utc": ts,
        "campaign": 302,
        "part": "provenance",
        "real_data_only": True,
        "fabricated_data": False,
        "executed_fills": False,
        "build_source": "archive_download_premium_index_klines_plus_c299_reuse",
        "universe_rule": (
            "Universe = C299's verified full-coverage {BTCUSDT, ETHUSDT, BCHUSDT}. Premium-index "
            "bars are real Binance USDT-M perp premiumIndexKlines at native 1h (open/high/low/close of "
            "the fair-value premium index; ~ +/-1e-3). Bars are aligned to each asset's C299 1h execution "
            "grid (real perp close + native 8h funding, verified identical grid). The premium close is "
            "the tradable signal; execution price = perp 1h close and funding = native 8h funding rate "
            "reused from the verified C299 cache. Bars absent from the premium archive (a real "
            "outage, e.g. the 2021-07-01 gap) are carried as NaN and NEVER imputed/filled; the runner's "
            "fail-closed gates make the score NaN there so no trade uses a missing bar. No "
            "impute/ffill/resample of any derived series."
        ),
        "cache_serialization": "plain numpy ndarrays; index stored as datetime64[us]; no pandas Series/DataFrame legs",
        "push_limit_note": f"compact ndarray form is {meta['cache_pkl_mb']} MB (< 100 MB). Asserted on disk before success.",
        "n_candidates": len(UNIVERSE),
        "n_selected": len(selected),
        "selected_symbols": selected,
        "excluded_symbols": {s: per_symbol[s] for s in UNIVERSE if s not in selected},
        "per_symbol": per_symbol,
        "months": months,
        "n_months": len(months),
        "window": {"start": START_UTC, "end": END_UTC},
        "interval": INTERVAL,
        "c299_reuse": {
            "cache": str(C299_CACHE.relative_to(ROOT)),
            "cache_sha256": sha256_file(C299_CACHE),
            "meta_sha256": sha256_file(C299_META) if C299_META.exists() else None,
            "provenance_sha256": sha256_file(C299_PROV) if C299_PROV.exists() else None,
        },
    }
    OUT_PROV.write_text(json.dumps(provenance, indent=2, default=str) + "\n")

    summary = {
        "ok": True,
        "campaign": 302,
        "build_source": "archive_download_premium_index_klines_plus_c299_reuse",
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
        "selected_symbols": selected,
        "window": {"start": START_UTC, "end": END_UTC},
        "interval": INTERVAL,
        "c299_cache_sha256": sha256_file(C299_CACHE),
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())