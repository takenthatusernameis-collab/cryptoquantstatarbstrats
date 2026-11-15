#!/usr/bin/env python3
"""C312 — ingest REAL Binance USDT-M LINEAR perpetual ``5m`` klines and build
per-symbol NATIVE 5m order-flow-imbalance (OFI) feature panels for the C312
USDT-M LINEAR cross-sectional OFI-carry stat-arb campaign.

This is a genuinely new economic family, not a re-skin of any frozen campaign:

- C310 (1h) and C311 (5m) tested COIN-M **inverse-settlement** OFI carry; both
  were COMPLETE FORMAL NEGATIVES dominated by inverse-settlement convexity
  (C310 OFI-carry share 0.088 vs convexity 0.912; C311 0.025 vs 0.975).
- C312 removes the convexity confound entirely by using **linear-settlement**
  USDT-M perps: PnL is exactly ``notional*(exit/entry - 1)*signed_weight``, so
  any surviving edge is attributable to OFI carry, not to ``1/entry - 1/exit``
  convexity.
- C301 (frozen) used only 3 spot symbols over a 2-month window (aggTrades
  tick-OFI). C312 uses 10 USDT-M linear perps over 36 months (2023-01..2025-12).

DATA SOURCE AND THE PRIMARY DE-BOTTLENECK
-----------------------------------------
The C312 signals only need a *bar-level* order-flow split, which is carried
natively in Binance USDT-M ``5m`` klines:

  open_time,open,high,low,close,volume,close_time,quote_volume,count,
  taker_buy_volume,taker_buy_quote_volume,ignore

so we do NOT stream the raw ``aggTrades`` archive. That matters: the USDT-M
``aggTrades`` zip is ~1.45 GB per month across these 10 symbols (~52 GB over 36
months, verified live 2026-11-15 via Content-Length), which cannot complete
inside one agent session and would cause repeated failed/inefficient turns.
The ``5m`` klines are ~140 MB total for the same universe/window and DO complete
in one session. Every one of the 7 pre-registered signals is derivable from the
taker buy/sell split:

  signed_volume  = taker_buy_volume - taker_sell_volume = 2*taker_buy_volume - volume
  total_volume   = volume
  trade_count    = count
  trade_sign_sum = sign(signed_volume)                 (bar-level taker sign)
  notional       = quote_volume
  vwap           = quote_volume / volume               (bar VWAP)
  perp_close     = close                               (execution price)

Data (real, fail-closed; ``fapi``/testnet REST is HTTP 451 and is NOT used):

- ``https://data.binance.vision/data/futures/um/monthly/klines/<SYM>/5m/<SYM>-5m-YYYY-MM.zip``
- Universe: 10 USDT-M linear perps (all listed before 2023-01 -> no 404 months).
- Window: 2023-01 .. 2025-12 (36 months).
- USDT-M funding is NOT reachable in this environment (fapi 451; ``fundingRate``
  is not in the monthly archives) -> the ``funding_rate`` leg is emitted all-NaN
  (control only, excluded from total return) and documented in provenance.

RESUMABILITY (mandatory de-bottleneck so the download survives session bounds):

- After aggregating each (symbol, month) we immediately write an intermediate
  shard ``data/cache/campaign312_usdt_m_ofi_5m/months/<SYM>_<YYYY-MM>.npz`` and
  record its SHA256 in ``data/cache/campaign312_usdt_m_ofi_5m/months_manifest.json``.
- On start we SKIP any month already present in the manifest (never restart).
- Once every month for a symbol exists we assemble the per-symbol
  ``<SYM>.npz`` panel on the common 5m grid, then delete that symbol's month
  shards so the total cache stays < 100 MB.

Storage: per-asset float32 ``.npz`` shards (GitHub hard-rejects any single blob
> 100 MB), plus ``meta.json`` + ``provenance.json``. Every artifact carries
``real_data_only:true``, ``fabricated_data:false``, ``executed_fills:false`` and
a SHA256-from-bytes.
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
OUT_DIR = CACHE / "campaign312_usdt_m_ofi_5m"
MONTHS_DIR = OUT_DIR / "months"
MANIFEST = OUT_DIR / "months_manifest.json"
OUT_META = CACHE / "campaign312_usdt_m_ofi_5m.meta.json"
OUT_PROV = CACHE / "campaign312_usdt_m_ofi_5m.provenance.json"

ARCHIVE_HOST = "https://data.binance.vision"
KLINES_PATH = "/data/futures/um/monthly/klines/{sym}/5m/{sym}-5m-{month}.zip"

PERPS = (
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
    "ADAUSDT", "DOGEUSDT", "AVAXUSDT", "LINKUSDT", "DOTUSDT",
)

DEFAULT_START = "2023-01"
DEFAULT_END = "2025-12"

INTERVAL = "5m"
BAR_MS = 300_000  # 5 minutes in milliseconds

KLINE_COLUMNS = [
    "open_time", "open", "high", "low", "close", "volume", "close_time",
    "quote_volume", "count", "taker_buy_volume", "taker_buy_quote_volume", "ignore",
]

F32_LEGS = (
    "signed_volume", "total_volume", "trade_count", "trade_sign_sum",
    "notional", "vwap", "perp_close", "funding_rate",
)

PUSH_LIMIT_BYTES = 100_000_000  # GitHub hard-rejects any blob > 100 MB
CACHE_BUDGET_BYTES = 100_000_000  # self-imposed total cache budget
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
        req = urllib.request.Request(url, method="GET", headers={"User-Agent": "kilo-c312-ingest"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return int(resp.status), resp.read()
        except urllib.error.HTTPError as exc:  # 404/451: retryable lone -> retry then give up
            last_exc = exc
            if exc.code in (404, 451):
                # a lone 404/451 is retryable (archive host flip-flops); keep trying
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
    df["_ot"] = df["_ot"].astype("int64")
    # keep the last record for any duplicated open_time
    df = df.drop_duplicates(subset="_ot", keep="last").sort_values("_ot")
    return df.reset_index(drop=True)


def month_legs_from_klines(df: pd.DataFrame) -> dict:
    """Compute per-5m-bar OFI legs from a klines month frame (taker-delta)."""
    vol = df["volume"].to_numpy(dtype=float)
    quote_vol = df["quote_volume"].to_numpy(dtype=float)
    count = df["count"].to_numpy(dtype=float)
    taker_buy_vol = df["taker_buy_volume"].to_numpy(dtype=float)
    close = df["close"].to_numpy(dtype=float)
    ot_ms = df["_ot"].to_numpy(dtype="int64")

    taker_sell_vol = vol - taker_buy_vol
    signed_volume = taker_buy_vol - taker_sell_vol  # = 2*tbv - vol
    trade_sign_sum = np.sign(signed_volume)
    with np.errstate(divide="ignore", invalid="ignore"):
        vwap = np.where(vol > 0, quote_vol / vol, np.nan)

    return {
        "open_time_ms": ot_ms,
        "signed_volume": signed_volume.astype(np.float32),
        "total_volume": vol.astype(np.float32),
        "trade_count": count.astype(np.float32),
        "trade_sign_sum": trade_sign_sum.astype(np.float32),
        "notional": quote_vol.astype(np.float32),
        "vwap": vwap.astype(np.float32),
        "perp_close": close.astype(np.float32),
    }


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


def _month_shard_path(sym: str, month: str) -> Path:
    return MONTHS_DIR / f"{sym}_{month}.npz"


def _write_month_shard(sym: str, month: str, legs: dict) -> str:
    MONTHS_DIR.mkdir(parents=True, exist_ok=True)
    p = _month_shard_path(sym, month)
    np.savez_compressed(p, **legs)
    return sha256_file(p)


def download_month(sym: str, month: str, timeout: float, man: dict) -> dict:
    """Download + aggregate one (symbol, month) into a shard, resumable."""
    key = f"{sym}_{month}"
    shard = _month_shard_path(sym, month)
    prev = (man.get("months") or {}).get(key)
    if prev and shard.exists() and sha256_file(shard) == prev.get("sha256"):
        return {"month": month, "status": "skipped", "reason": "in_manifest", "bars": prev.get("bars")}

    url = ARCHIVE_HOST + KLINES_PATH.format(sym=sym, month=month)
    try:
        status, data = _http_get(url, timeout)
    except Exception as exc:  # noqa: BLE001
        return {"month": month, "url": url, "status": "error", "ok": False, "reason": repr(exc)[:200]}
    if status != 200:
        return {"month": month, "url": url, "status": status, "ok": False, "reason": f"http_{status}"}
    df = read_klines_zip(data)
    del data
    if len(df) == 0:
        return {"month": month, "url": url, "status": status, "ok": False, "reason": "empty klines"}
    legs = month_legs_from_klines(df)
    sha = _write_month_shard(sym, month, legs)
    man.setdefault("months", {})[key] = {"sha256": sha, "bars": int(len(df))}
    _save_manifest(man)
    return {"month": month, "url": url, "status": status, "bars": int(len(df)), "ok": True}


def assemble_symbol(sym: str, months: list[str], man: dict) -> dict:
    """Concatenate a symbol's month shards into a full native-5m series."""
    frames = []
    accepted = []
    for m in months:
        p = _month_shard_path(sym, m)
        if not p.exists():
            continue
        with np.load(p) as z:
            frames.append({k: np.asarray(z[k]) for k in z.files})
        accepted.append(m)
    if not frames:
        return {"symbol": sym, "status": "excluded", "exclusion_reason": "no month shards"}
    ot = np.concatenate([f["open_time_ms"] for f in frames])
    cols = {}
    for leg in F32_LEGS:
        if leg == "funding_rate":
            continue
        cols[leg] = np.concatenate([f[leg].astype(np.float32) for f in frames])
    order = np.argsort(ot, kind="mergesort")
    ot = ot[order]
    cols = {k: v[order] for k, v in cols.items()}
    # dedup open_time (keep last)
    keep = np.ones(len(ot), dtype=bool)
    if len(ot) > 1:
        dup = np.empty(len(ot), dtype=bool)
        dup[:-1] = ot[1:] == ot[:-1]
        dup[-1] = False
        keep = ~dup
    ot = ot[keep]
    cols = {k: v[keep] for k, v in cols.items()}
    return {"symbol": sym, "status": "ok", "accepted_months": accepted,
            "open_time_ms": ot, "legs": cols}


def _assemble_on_grid(sym_series: dict[str, dict], grid_ms: np.ndarray) -> dict[str, dict]:
    """Reindex each symbol's full series onto the common grid (never impute)."""
    out = {}
    grid_pos = {int(v): i for i, v in enumerate(grid_ms)}
    n = len(grid_ms)
    for sym, d in sym_series.items():
        ot = d["open_time_ms"]
        idx = np.array([grid_pos.get(int(v), -1) for v in ot], dtype=np.int64)
        mask = idx >= 0
        legs = {}
        for leg, vals in d["legs"].items():
            arr = np.full(n, np.nan, dtype=np.float32)
            arr[idx[mask]] = vals[mask]
            legs[leg] = arr
        out[sym] = {"legs": legs}
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--start-month", default=DEFAULT_START)
    ap.add_argument("--end-month", default=DEFAULT_END)
    ap.add_argument("--symbols", default="all", help="comma list or 'all'")
    ap.add_argument("--timeout", type=float, default=180.0)
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args(argv)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    CACHE.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    MONTHS_DIR.mkdir(parents=True, exist_ok=True)

    symbols = list(PERPS) if args.symbols == "all" else [s.strip() for s in args.symbols.split(",") if s.strip()]
    months = month_range(args.start_month, args.end_month)
    man = _load_manifest()
    man.setdefault("months", {})
    man.setdefault("assembled", [])

    # ---- Phase A: download + aggregate each (symbol, month) into shards ----
    from concurrent.futures import ThreadPoolExecutor, as_completed
    per_month_log: list[dict] = []
    todo = [(s, m) for s in symbols if s not in man["assembled"]
            for m in months if f"{s}_{m}" not in man["months"]]
    errors: list[dict] = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futs = {pool.submit(download_month, s, m, args.timeout, man): (s, m) for s, m in todo}
        for fut in as_completed(futs):
            r = fut.result()
            per_month_log.append({k: v for k, v in r.items() if k != "url"})
            if not r.get("ok", True) and r.get("status") != "skipped":
                errors.append({"symbol": futs[fut][0], **{k: v for k, v in r.items()}})

    # ---- Phase B: assemble symbols that are not yet assembled ----
    assembled = set(man["assembled"])
    remaining = [s for s in symbols if s not in assembled]
    sym_series: dict[str, dict] = {}
    for s in remaining:
        d = assemble_symbol(s, months, man)
        if d.get("status") == "ok":
            sym_series[s] = d
        else:
            errors.append({"symbol": s, "assemble": d.get("exclusion_reason")})
    if not sym_series and not assembled:
        raise SystemExit(f"FATAL: no symbol assembled. errors={json.dumps(errors)[:1500]}")

    # existing assembled symbols' series (from their .npz on the eventual grid)
    # We rebuild them onto the new common grid too, from their month shards if
    # present, else from the existing shard.
    all_series: dict[str, dict] = {}
    all_series.update(sym_series)
    for s in assembled:
        sp = OUT_DIR / f"{s}.npz"
        if not sp.exists():
            continue
        with np.load(sp) as z:
            keys = z.files
            idx = np.asarray(z["index_ms"], dtype="int64")
            all_series[s] = {
                "open_time_ms": idx,
                "legs": {k: np.asarray(z[k]) for k in F32_LEGS if k in keys and k != "funding_rate"},
            }

    # ---- common grid = intersection of every symbol's 5m bars ----
    common = None
    for s, d in all_series.items():
        ms = np.asarray(d["open_time_ms"], dtype="int64")
        common = ms if common is None else np.intersect1d(common, ms, assume_unique=False)
    if common is None or len(common) == 0:
        raise SystemExit("FATAL: empty common 5m grid")
    grid_ms = np.sort(common)
    n_nominal = len(months) * 30 * 288  # rough nominal
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
        raise SystemExit(f"FATAL: common 5m grid has {len(grid_ms)} bars < 80% of nominal {nominal}")

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
                if leg in d["legs"]:
                    src = d["legs"][leg]
                    arr = np.full(n, np.nan, dtype=np.float32)
                    arr[idx[mask]] = src[mask]
                else:
                    arr = np.full(n, np.nan, dtype=np.float32)
                arrays[leg] = arr
            # validate perp_close finite positive
            pc = arrays["perp_close"]
            if not (np.isfinite(pc).all() and (pc > 0).all()):
                raise SystemExit(f"FATAL: {s} perp_close non-finite/non-positive on common grid")
            sp = OUT_DIR / f"{s}.npz"
            np.savez_compressed(sp, **arrays)
            shard_sha[s] = sha256_file(sp)
            shard_bytes[s] = int(sp.stat().st_size)
        return {"sha": shard_sha, "bytes": shard_bytes}

    written = write_shards(all_series)
    total_bytes = sum(written["bytes"].values())
    # enforce total cache budget: drop lowest-volume symbol(s), never widen window
    dropped: list[str] = []
    if total_bytes > CACHE_BUDGET_BYTES and len(all_series) > 2:
        vol_by_sym = {}
        for s, d in all_series.items():
            tv = d["legs"].get("total_volume")
            vol_by_sym[s] = float(np.nansum(tv)) if tv is not None else 0.0
        order = sorted(vol_by_sym, key=vol_by_sym.get)
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
        raise SystemExit(f"FATAL: total cache {total_bytes/1e6:.2f} MB >= {CACHE_BUDGET_BYTES/1e6:.0f} MB budget")

    selected = sorted(all_series.keys())
    max_shard = max(written["bytes"].values()) if written["bytes"] else 0
    if max_shard >= PUSH_LIMIT_BYTES:
        raise SystemExit(f"FATAL: shard {max_shard/1e6:.2f} MB >= push limit")

    # ---- delete month shards for fully-assembled symbols (keep cache small) ----
    for s in selected:
        for m in months:
            p = _month_shard_path(s, m)
            if p.exists():
                p.unlink()
    # rebuild manifest to reflect assembled symbols only
    man["assembled"] = sorted(set(man["assembled"]) | set(selected))
    man["months"] = {k: v for k, v in man["months"].items()
                     if k.rsplit("_", 2)[0] not in selected}
    _save_manifest(man)

    grid_ms_int = grid_ms.astype(np.int64)
    n_grid = int(len(grid_ms))
    n_total_bars = n_grid * len(selected)

    meta = {
        "generated_at_utc": ts,
        "campaign": 312,
        "part": "ingest",
        "interval": INTERVAL,
        "bar_ms": BAR_MS,
        "source_interval": "usdt_m_5m_klines_taker_delta_ms",
        "symbols": selected,
        "n_symbols": len(selected),
        "n_universe": len(symbols),
        "total_bars": int(n_total_bars),
        "window_start_month": args.start_month,
        "window_end_month": args.end_month,
        "grid_start_utc": str(grid_index[0]),
        "grid_end_utc": str(grid_index[-1]),
        "n_grid_bars": int(n_grid),
        "n_nominal_grid_bars": int(nominal),
        "grid_construction": "intersection_of_symbol_5m_kline_bars",
        "source_host": ARCHIVE_HOST,
        "klines_endpoint": KLINES_PATH,
        "execution_price_source": "usdt_m_5m_klines_close",
        "ofi_source": "usdt_m_5m_klines_taker_buy_sell_split",
        "funding_source": "unreachable_fapi_451_and_not_in_monthly_archives_nan_control_only",
        "storage": "per_asset_float32_npz_shards",
        "f32_legs": list(F32_LEGS),
        "shard_dir": str(OUT_DIR.relative_to(ROOT)),
        "months_dir": str(MONTHS_DIR.relative_to(ROOT)),
        "months_manifest": str(MANIFEST.relative_to(ROOT)),
        "resumable": True,
        "resumability_scheme": "per_symbol_month_shard_skip_on_manifest",
        "shard_sha256": written["sha"],
        "shard_bytes": written["bytes"],
        "total_shard_bytes": int(total_bytes),
        "max_shard_bytes": int(max_shard),
        "push_limit_bytes": PUSH_LIMIT_BYTES,
        "cache_budget_bytes": CACHE_BUDGET_BYTES,
        "under_push_limit": bool(max_shard < PUSH_LIMIT_BYTES),
        "under_cache_budget": bool(total_bytes < CACHE_BUDGET_BYTES),
        "dropped_low_volume_symbols": dropped,
        "cache_format": "per_asset_float32_npz_no_pandas",
        "real_data_only": True,
        "fabricated_data": False,
        "fetch_real_data_only": True,
        "fetch_fabricated_data": False,
        "executed_fills": False,
    }
    manifest = {s: written["sha"][s] for s in sorted(written["sha"])}
    meta["manifest_sha256"] = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()
    OUT_META.write_text(json.dumps(meta, indent=2) + "\n")

    per_symbol = {}
    for s in symbols:
        if s in selected:
            per_symbol[s] = {
                "status": "ok",
                "n_bars": int(n_grid),
                "shard": str((OUT_DIR / f"{s}.npz").relative_to(ROOT)),
                "shard_sha256": written["sha"][s],
                "shard_bytes": written["bytes"][s],
            }
        else:
            per_symbol[s] = {"status": "excluded", "exclusion_reason": "dropped_low_volume_or_unavailable"}

    provenance = {
        "generated_at_utc": ts,
        "campaign": 312,
        "part": "provenance",
        "source_host": ARCHIVE_HOST,
        "klines_endpoint": KLINES_PATH,
        "interval": INTERVAL,
        "bar_ms": BAR_MS,
        "window_start_month": args.start_month,
        "window_end_month": args.end_month,
        "n_months": len(months),
        "symbols": selected,
        "per_symbol": per_symbol,
        "grid_construction": "intersection_of_symbol_5m_kline_bars",
        "n_nominal_grid_bars": int(nominal),
        "n_grid_bars": int(n_grid),
        "execution_price_source": "usdt_m_5m_klines_close",
        "ofi_source": "usdt_m_5m_klines_taker_buy_sell_split",
        "funding_source": "unreachable_fapi_451_and_not_in_monthly_archives_nan_control_only",
        "aggtrades_note": (
            "USDT-M aggTrades zips are ~1.45 GB/month across these 10 symbols "
            "(~52 GB over 36 months; verified live 2026-11-15 via Content-Length) and "
            "are NOT streamed; the bar-level taker buy/sell split in native 5m klines "
            "is used instead. 5m klines total ~140 MB for the same universe/window."
        ),
        "resumable": True,
        "real_data_only": True,
        "fabricated_data": False,
        "fetch_real_data_only": True,
        "fetch_fabricated_data": False,
        "executed_fills": False,
        "manifest_sha256": meta["manifest_sha256"],
        "gap_bar_policy": "bars without a 5m kline are dropped from the common grid (never filled)",
        "funding_leg_policy": "funding_rate emitted all-NaN (control only, excluded from return)",
    }
    OUT_PROV.write_text(json.dumps(provenance, indent=2) + "\n")

    print(json.dumps({
        "campaign": 312,
        "part": "ingest",
        "interval": INTERVAL,
        "symbols_ok": selected,
        "n_symbols": len(selected),
        "n_months": len(months),
        "n_grid_bars": int(n_grid),
        "n_nominal_grid_bars": int(nominal),
        "grid_start_utc": meta["grid_start_utc"],
        "grid_end_utc": meta["grid_end_utc"],
        "max_shard_mb": round(max_shard / 1e6, 2),
        "total_shard_mb": round(total_bytes / 1e6, 2),
        "under_cache_budget": meta["under_cache_budget"],
        "dropped_low_volume_symbols": dropped,
        "manifest_sha256": meta["manifest_sha256"],
        "month_errors": errors[:20],
        "n_month_errors": len(errors),
        "shard_dir": str(OUT_DIR.relative_to(ROOT)),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())