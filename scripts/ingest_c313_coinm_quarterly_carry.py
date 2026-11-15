#!/usr/bin/env python3
"""C313 — ingest REAL Binance COIN-M inverse 1h klines for the quarterly
term-structure carry campaign. Resumable per (symbol, contract, month).

Builds, per underlying asset, a common 1h grid where the perpetual AND at least
two dated quarterly contracts (front + next expiry) both have klines data.
Per-asset float32 .npz shards record perp_close, front/next quarterly close,
annualized basis, and time-to-expiry hours. Raw monthly CSVs are discarded
after aggregation; resume via months_manifest.json.

Real data only (fail-closed; fapi REST is HTTP 451 and is NOT used):
- https://data.binance.vision/data/futures/cm/monthly/klines/<SYM>/1h/<SYM>-1h-YYYY-MM.zip
  perp: <BASE>USD_PERP; quarterly: <BASE>USD_<YYMMDD> (expiry last Friday of
  Mar/Jun/Sep/Dec at 08:00 UTC).
- data/coin-m/ and data.binance.vision/data/coin-m/quarterly_klines/ DO NOT
  EXIST (404); the data/futures/cm/ layout is used verbatim.

AUTHORITATIVE CONTRACT DISCOVERY (live-verified 2026-11-15T19:4xZ):
The archive is listed, never guessed. Quarterly contracts exist ONLY for a
subset of COIN-M perps, so a synthetic expiry schedule would fire thousands of
guaranteed-404 requests (the primary C313 bottleneck). Instead:
  * ``list_contract_months(sym)`` reads the S3 listing for a contract's 1h
    prefix and returns only months that really exist;
  * ``list_quarterly_contracts(base)`` reads
    ``data/futures/cm/monthly/klines/<BASE>_`` and keeps only ``<BASE>USD_<YYMMDD>``
    dirs;
  * bases with ZERO quarterly contracts (verified: DOGEUSD, MATICUSD, AVAXUSD)
    are EXCLUDED from the tradable universe and recorded in provenance with
    ``exclusion_reason: no_quarterly_contracts_listed`` (never silently).
A genuine 404 on a listed month is recorded as an exclusion, NOT retried six
times; only transport/5xx errors retry (6 attempts, linear 1 s x k).

Fail-closed: never impute/ffill/backfill; skip CSV rows whose first field is
non-numeric (header row); every shard SHA256 is recorded in the meta manifest.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "cache"
OUT_DIR = CACHE / "campaign313_coinm_quarterly_carry"
MONTHS_DIR = OUT_DIR / "months"
MANIFEST = OUT_DIR / "months_manifest.json"
OUT_META = CACHE / "campaign313_coinm_quarterly_carry.meta.json"
OUT_PROV = CACHE / "campaign313_coinm_quarterly_carry.provenance.json"

ARCHIVE_HOST = "https://data.binance.vision"
S3_LIST = ("https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"
           "?delimiter=/&prefix={prefix}")
KLINES_PATH = "/data/futures/cm/monthly/klines/{sym}/1h/{sym}-1h-{month}.zip"

INTERVAL = "1h"
HOURS_PER_YEAR = 365.0 * 24.0

# COIN-M inverse perpetuals (BASE). Quarterly availability is DISCOVERED, not
# assumed: DOGEUSD/MATICUSD/AVAXUSD have no quarterly contracts in the archive.
PERPS = (
    "BTCUSD", "ETHUSD", "BNBUSD", "XRPUSD", "ADAUSD", "DOGEUSD",
    "SOLUSD", "MATICUSD", "DOTUSD", "AVAXUSD", "LTCUSD",
)
MIN_ASSETS_REQUIRED = 6

QUARTERLY_EXPIRY_START = "2022-09"
QUARTERLY_EXPIRY_END = "2026-12"
WINDOW_START = "2022-07"
WINDOW_END = "2026-06"

KLINE_COLUMNS = [
    "open_time", "open", "high", "low", "close", "volume", "close_time",
    "quote_volume", "count", "taker_buy_volume", "taker_buy_quote_volume", "ignore",
]
F32_LEGS = (
    "index_ms", "perp_close", "front_close", "next_close",
    "front_basis", "next_basis", "front_tte_hours", "next_tte_hours",
    "front_expiry_ms", "next_expiry_ms",
)
PUSH_LIMIT_BYTES = 100_000_000
CACHE_BUDGET_BYTES = 100_000_000
HTTP_RETRIES = 6
LIST_TIMEOUT = 30.0

_QSYM_RE = re.compile(r"^(?P<base>[A-Z0-9]+)USD_(?P<code>\d{6})$")


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


def _quarterly_expiries() -> list[tuple[pd.Timestamp, str]]:
    """Last Friday of Mar/Jun/Sep/Dec at 08:00 UTC -> (expiry, YYMMDD code)."""
    expiries: list[tuple[pd.Timestamp, str]] = []
    for y in range(2021, 2027):
        for mo in (3, 6, 9, 12):
            last_day = pd.Timestamp(f"{y}-{mo:02d}-01", tz="UTC") + pd.offsets.MonthEnd(0)
            d = last_day
            while d.weekday() != 4:
                d -= pd.Timedelta(days=1)
            expiry = d.replace(hour=8, minute=0, second=0, microsecond=0)
            expiries.append((expiry, f"{expiry:%y%m%d}"))
    start = pd.Timestamp(QUARTERLY_EXPIRY_START, tz="UTC")
    end = pd.Timestamp(QUARTERLY_EXPIRY_END, tz="UTC")
    return [(e, c) for e, c in expiries if start <= e <= end]


def expiry_by_code() -> dict[str, pd.Timestamp]:
    return {code: exp for exp, code in _quarterly_expiries()}


def _s3_list(prefix: str, delimiter: str | None) -> tuple[list[str], list[str]]:
    """Return (common_prefixes, keys) under ``prefix`` (paginated if cut)."""
    prefs: list[str] = []
    keys: list[str] = []
    marker = None
    for _ in range(40):
        url = S3_LIST.format(prefix=urllib.parse.quote(prefix, safe=""))
        if delimiter:
            url = ("https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"
                   "?delimiter=" + urllib.parse.quote(delimiter, safe="") +
                   "&prefix=" + urllib.parse.quote(prefix, safe=""))
        if marker:
            url += "&marker=" + urllib.parse.quote(marker, safe="")
        req = urllib.request.Request(url, headers={"User-Agent": "kilo-c313-ingest"})
        with urllib.request.urlopen(req, timeout=LIST_TIMEOUT) as resp:
            body = resp.read().decode("utf-8", "replace")
        prefs.extend(re.findall(r"<Prefix>([^<]+)</Prefix>", body))
        keys.extend(re.findall(r"<Key>([^<]+)</Key>", body))
        if "<IsTruncated>true</IsTruncated>" not in body:
            break
        m = re.search(r"<NextMarker>([^<]+)</NextMarker>", body)
        if not m:
            break
        marker = m.group(1)
    return sorted(set(prefs)), sorted(set(keys))


def list_contract_months(sym: str) -> list[str]:
    """Months (YYYY-MM) that really exist for a contract's 1h klines prefix."""
    _, keys = _s3_list(f"data/futures/cm/monthly/klines/{sym}/1h/", None)
    months = []
    for k in keys:
        if not k.endswith(".zip"):
            continue
        m = re.search(r"-(\d{4}-\d{2})\.zip$", k)
        if m:
            months.append(m.group(1))
    return sorted(set(months))


_MONTHS_CACHE: dict[str, list[str]] = {}


def list_contract_months_cached(sym: str) -> list[str]:
    """Cached wrapper: the archive listing is immutable within a session."""
    if sym not in _MONTHS_CACHE:
        _MONTHS_CACHE[sym] = list_contract_months(sym)
    return _MONTHS_CACHE[sym]


def list_quarterly_contracts(base: str) -> list[str]:
    """Quarterly contract symbols actually listed for ``base`` (empty if none)."""
    prefs, _ = _s3_list(f"data/futures/cm/monthly/klines/{base}_", "/")
    out = []
    for p in prefs:
        sym = p.rstrip("/").rsplit("/", 1)[-1]
        if _QSYM_RE.match(sym) and sym.rsplit("_", 1)[0] == base:
            out.append(sym)
    return sorted(set(out))


def _http_get(url: str, timeout: float) -> tuple[int, bytes]:
    last_exc: Exception | None = None
    last_status = None
    for attempt in range(1, HTTP_RETRIES + 1):
        req = urllib.request.Request(url, method="GET",
                                     headers={"User-Agent": "kilo-c313-ingest"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return int(resp.status), resp.read()
        except urllib.error.HTTPError as exc:
            last_status = int(exc.code)
            last_exc = exc
            if last_status in (404, 403, 410):
                raise
        except Exception as exc:  # noqa: BLE001 transient network
            last_exc = exc
        if attempt < HTTP_RETRIES:
            time.sleep(1.0 * attempt)
    raise RuntimeError(f"GET failed after {HTTP_RETRIES} attempts: {url} "
                       f"(last_status={last_status}, last_exc={last_exc})")


def _is_numeric_first_field(raw: bytes) -> bool:
    nl = raw.find(b"\n")
    first_field = raw[: nl if nl >= 0 else len(raw)].split(b",", 1)[0].strip()
    try:
        float(first_field)
        return True
    except ValueError:
        return False


def read_klines_zip(raw: bytes) -> pd.DataFrame:
    zf = zipfile.ZipFile(io.BytesIO(raw))
    csv_raw = zf.read(zf.namelist()[0])
    if _is_numeric_first_field(csv_raw):
        df = pd.read_csv(io.BytesIO(csv_raw), header=None, names=KLINE_COLUMNS)
    else:
        df = pd.read_csv(io.BytesIO(csv_raw))
    df["open_time"] = pd.to_numeric(df["open_time"], errors="coerce")
    df = df.dropna(subset=["open_time"])
    for c in ("open", "high", "low", "close"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["open", "high", "low", "close"])
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    df = df.drop_duplicates("open_time", keep="last").sort_values("open_time")
    return df.set_index("open_time")[["open", "high", "low", "close"]]


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


def _write_month_shard(sym: str, month: str, df: pd.DataFrame) -> str:
    MONTHS_DIR.mkdir(parents=True, exist_ok=True)
    p = _month_shard_path(sym, month)
    np.savez_compressed(p, open_time=df.index.values.astype("datetime64[ns]").view("int64"),
                        open=df["open"].to_numpy(dtype=np.float32),
                        high=df["high"].to_numpy(dtype=np.float32),
                        low=df["low"].to_numpy(dtype=np.float32),
                        close=df["close"].to_numpy(dtype=np.float32))
    return sha256_file(p)


def download_month(sym: str, month: str, timeout: float, man: dict) -> dict:
    """Download + aggregate one (symbol, month) into a shard, resumable.

    A 404 on a LISTED month is an exclusion (contract not yet trading), never an
    outage and never retried six times.
    """
    key = f"{sym}_{month}"
    shard = _month_shard_path(sym, month)
    prev = (man.get("months") or {}).get(key)
    if prev and shard.exists() and sha256_file(shard) == prev.get("sha256"):
        return {"month": month, "status": "skipped", "reason": "in_manifest",
                "bars": int(prev.get("bars", 0))}
    url = ARCHIVE_HOST + KLINES_PATH.format(sym=sym, month=month)
    try:
        status, data = _http_get(url, timeout)
    except urllib.error.HTTPError as exc:
        return {"month": month, "url": url, "status": int(exc.code), "ok": False,
                "reason": f"http_{exc.code}_excluded"}
    except Exception as exc:  # noqa: BLE001
        return {"month": month, "url": url, "status": "ERR", "ok": False,
                "reason": repr(exc)[:200]}
    if status != 200 or not data:
        return {"month": month, "url": url, "status": status, "ok": False,
                "reason": f"http_{status}"}
    try:
        df = read_klines_zip(data)
    except Exception as exc:  # noqa: BLE001
        return {"month": month, "url": url, "status": status, "ok": False,
                "reason": f"parse:{type(exc).__name__}:{exc}"[:200]}
    del data
    if len(df) == 0:
        return {"month": month, "url": url, "status": status, "ok": False,
                "reason": "empty klines"}
    sha = _write_month_shard(sym, month, df)
    man.setdefault("months", {})[key] = {"sha256": sha, "bars": int(len(df)),
                                         "sym": sym, "month": month}
    _save_manifest(man)
    return {"month": month, "url": url, "status": status, "bars": int(len(df)),
            "ok": True}


def build_contract_series(sym: str, months: list[str]) -> pd.DataFrame | None:
    """Stitch one contract's 1h klines across its listed months (resumable)."""
    frames: list[pd.DataFrame] = []
    for m in months:
        shard = _month_shard_path(sym, m)
        if not shard.exists():
            continue
        with np.load(shard) as z:
            ot = pd.to_datetime(np.asarray(z["open_time"], dtype="int64"),
                                unit="ns", utc=True)
            frames.append(pd.DataFrame({
                "open": np.asarray(z["open"], dtype=float),
                "high": np.asarray(z["high"], dtype=float),
                "low": np.asarray(z["low"], dtype=float),
                "close": np.asarray(z["close"], dtype=float),
            }, index=ot))
    if not frames:
        return None
    all_df = pd.concat(frames).sort_index()
    return all_df[~all_df.index.duplicated(keep="last")]


def assemble_asset(base: str, perp_df: pd.DataFrame,
                   q_series: dict[str, pd.DataFrame],
                   q_expiry: dict[str, pd.Timestamp],
                   start: pd.Timestamp, end: pd.Timestamp) -> dict | None:
    """Common 1h grid for one asset: perp + front + next unexpired quarterly.

    Vectorised: expiries are sorted once and located with ``searchsorted`` so the
    per-bar work is O(1) amortised (the naive per-bar python scan over every
    contract was the C313 ingest bottleneck).
    """
    qsyms = sorted(q_series.keys(), key=lambda s: (q_expiry[s], s))
    if len(qsyms) < 2:
        return None
    exp_ns = np.array([q_expiry[s].value for s in qsyms], dtype="int64")
    order = np.argsort(exp_ns, kind="mergesort")
    qsyms = [qsyms[i] for i in order]
    exp_ns = exp_ns[order]
    close_by_sym = {s: q_series[s].reindex(q_series[s].index)["close"] for s in qsyms}

    all_index = perp_df.index
    for df in q_series.values():
        all_index = all_index.union(df.index)
    all_index = all_index[(all_index >= start) & (all_index <= end)].sort_values()
    n = len(all_index)
    if n == 0:
        return None
    t_ns = all_index.values.astype("datetime64[ns]").view("int64")
    pc = perp_df.reindex(all_index)["close"].to_numpy(dtype=float)
    q_close = np.vstack([close_by_sym[s].reindex(all_index).to_numpy(dtype=float)
                         for s in qsyms]) if qsyms else np.empty((0, n))

    front_close = np.full(n, np.nan); next_close = np.full(n, np.nan)
    front_basis = np.full(n, np.nan); next_basis = np.full(n, np.nan)
    front_tte = np.full(n, np.nan); next_tte = np.full(n, np.nan)
    front_exp = np.full(n, np.nan, dtype="int64"); next_exp = np.full(n, np.nan, dtype="int64")

    n_syms = len(qsyms)
    for i in range(n):
        p = pc[i]
        if not np.isfinite(p) or p <= 0:
            continue
        t = t_ns[i]
        k = int(np.searchsorted(exp_ns, t, side="right"))
        found = 0
        closes: list[float] = []
        idx_found: list[int] = []
        j = k
        while j < n_syms and found < 2:
            c = q_close[j, i]
            if np.isfinite(c) and c > 0:
                closes.append(float(c)); idx_found.append(j); found += 1
            j += 1
        if found < 2:
            continue
        fj, sj = idx_found[0], idx_found[1]
        fq, sq = closes[0], closes[1]
        ftte_h = (exp_ns[fj] - t) / 1e9 / 3600.0
        stte_h = (exp_ns[sj] - t) / 1e9 / 3600.0
        if ftte_h <= 0 or stte_h <= 0:
            continue
        front_close[i] = fq; next_close[i] = sq
        front_exp[i] = exp_ns[fj] // 1_000_000; next_exp[i] = exp_ns[sj] // 1_000_000
        front_tte[i] = ftte_h; next_tte[i] = stte_h
        with np.errstate(divide="ignore", invalid="ignore"):
            front_basis[i] = np.log(fq / p) * HOURS_PER_YEAR / ftte_h
            next_basis[i] = np.log(sq / p) * HOURS_PER_YEAR / stte_h

    valid = np.isfinite(front_close) & np.isfinite(next_close) & \
        np.isfinite(front_basis) & np.isfinite(next_basis)
    if int(valid.sum()) == 0:
        return None
    idx = all_index[valid]
    arrays = {"index_ms": idx.values.astype("datetime64[ns]").view("int64") // 1_000_000,
              "perp_close": pc[valid].astype(np.float32),
              "front_close": front_close[valid].astype(np.float32),
              "next_close": next_close[valid].astype(np.float32),
              "front_basis": front_basis[valid].astype(np.float32),
              "next_basis": next_basis[valid].astype(np.float32),
              "front_tte_hours": front_tte[valid].astype(np.float32),
              "next_tte_hours": next_tte[valid].astype(np.float32),
              "front_expiry_ms": front_exp[valid],
              "next_expiry_ms": next_exp[valid]}
    return {"asset": base, "n_bars": int(valid.sum()),
            "window_start_utc": str(idx[0]), "window_end_utc": str(idx[-1]),
            "quarterly_contracts": list(qsyms),
            "arrays": arrays}


def _assert_under_budget(paths: list[Path], total_bytes: int) -> None:
    for p in paths:
        if p.stat().st_size >= PUSH_LIMIT_BYTES:
            raise SystemExit(f"FATAL: shard {p.name} >= {PUSH_LIMIT_BYTES/1e6:.0f} MB push limit")
    if total_bytes >= CACHE_BUDGET_BYTES:
        raise SystemExit(f"FATAL: total cache {total_bytes/1e6:.2f} MB >= {CACHE_BUDGET_BYTES/1e6:.0f} MB budget")


def discover_universe(symbols: list[str]) -> tuple[dict[str, dict], dict[str, dict]]:
    """Return (per_base_contracts, exclusions) using the ARCHIVE LISTING only."""
    per_base: dict[str, dict] = {}
    excluded: dict[str, dict] = {}
    for base in symbols:
        qsyms = list_quarterly_contracts(base)
        if len(qsyms) < 1:
            excluded[base] = {"status": "excluded",
                              "exclusion_reason": "no_quarterly_contracts_listed",
                              "n_quarterly": 0}
            continue
        per_base[base] = {"quarterly": qsyms, "n_quarterly": len(qsyms),
                          "status": "eligible"}
    return per_base, excluded


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--start-month", default=WINDOW_START)
    ap.add_argument("--end-month", default=WINDOW_END)
    ap.add_argument("--symbols", default="all", help="comma list of BASE symbols or 'all'")
    ap.add_argument("--timeout", type=float, default=60.0)
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args(argv)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    CACHE.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    MONTHS_DIR.mkdir(parents=True, exist_ok=True)

    symbols = list(PERPS) if args.symbols == "all" else [s.strip() for s in args.symbols.split(",") if s.strip()]
    months = month_range(args.start_month, args.end_month)
    man = _load_manifest()
    man.setdefault("months", {}); man.setdefault("assembled", [])

    # ---- authoritative discovery from the archive listing ----
    per_base, excluded = discover_universe(symbols)
    if len(per_base) < MIN_ASSETS_REQUIRED:
        raise SystemExit(f"FATAL: only {len(per_base)} bases have quarterly contracts "
                         f"(< {MIN_ASSETS_REQUIRED}); refusing to fabricate a universe")
    exp_by_code = expiry_by_code()
    q_expiry: dict[str, pd.Timestamp] = {}
    contract_excluded: dict[str, str] = {}
    for base, info in per_base.items():
        for qs in info["quarterly"]:
            code = qs.rsplit("_", 1)[1]
            exp = exp_by_code.get(code)
            if exp is None or not (pd.Timestamp(WINDOW_START, tz="UTC") - pd.Timedelta(days=1) <= exp):
                contract_excluded[qs] = "expiry_code_outside_mapped_schedule"
                continue
            if exp > pd.Timestamp(WINDOW_END, tz="UTC") + pd.offsets.MonthEnd(0):
                contract_excluded[qs] = "expiry_after_window"
                continue
            q_expiry[qs] = exp
    eligible_q = {b: [q for q in info["quarterly"] if q in q_expiry]
                  for b, info in per_base.items()}
    eligible_q = {b: sorted(q, key=lambda s: (q_expiry[s], s)) for b, q in eligible_q.items()}
    dropped = sorted(b for b, q in eligible_q.items() if len(q) < 2)
    eligible_q = {b: q for b, q in eligible_q.items() if len(q) >= 2}
    for b in dropped:
        excluded[b] = {"status": "excluded",
                       "exclusion_reason": "fewer_than_two_quarterly_contracts_after_expiry_mapping"}
    if len(eligible_q) < MIN_ASSETS_REQUIRED:
        raise SystemExit(f"FATAL: only {len(eligible_q)} assets keep >=2 quarterly contracts "
                         f"(< {MIN_ASSETS_REQUIRED})")

    # ---- Phase A: download every (contract, listed month) shard, resumable ----
    todo: list[tuple[str, str]] = []
    for base in sorted(eligible_q):
        perps = base + "_PERP"
        perp_months = [m for m in list_contract_months_cached(perps) if m in set(months)]
        for m in perp_months:
            todo.append((perps, m))
        for qs in eligible_q[base]:
            qmonths = [m for m in list_contract_months_cached(qs) if m in set(months)]
            for m in qmonths:
                todo.append((qs, m))
    todo = [(s, m) for s, m in todo if f"{s}_{m}" not in (man.get("months") or {})]
    errors: list[dict] = []
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futs = {pool.submit(download_month, s, m, args.timeout, man): (s, m) for s, m in todo}
        for fut in as_completed(futs):
            r = fut.result()
            if not r.get("ok", True) and r.get("status") != "skipped":
                errors.append({**r, "sym": futs[fut][0]})
    dl_s = round(time.time() - t0, 1)

    # ---- Phase B: assemble per-asset common grids ----
    start_ts = pd.Timestamp(f"{args.start_month[:4]}-{args.start_month[5:7]}-01", tz="UTC")
    end_ts = pd.Timestamp(f"{args.end_month[:4]}-{args.end_month[5:7]}-01", tz="UTC") + pd.offsets.MonthEnd(0)
    assembled: list[str] = []
    shard_meta: dict[str, dict] = {}
    per_asset_meta: dict[str, dict] = {}
    for base in sorted(eligible_q):
        perp_sym = base + "_PERP"
        perp_months = [m for m in list_contract_months_cached(perp_sym) if m in set(months)]
        perp_df = build_contract_series(perp_sym, perp_months)
        if perp_df is None or len(perp_df) == 0:
            per_asset_meta[base] = {"status": "excluded", "exclusion_reason": "no perp data"}
            excluded[base] = per_asset_meta[base]
            continue
        q_series: dict[str, pd.DataFrame] = {}
        for qs in eligible_q[base]:
            qmonths = [m for m in list_contract_months_cached(qs) if m in set(months)]
            df = build_contract_series(qs, qmonths)
            if df is not None and len(df) > 0:
                q_series[qs] = df
        if len(q_series) < 2:
            per_asset_meta[base] = {"status": "excluded",
                                    "exclusion_reason": f"only {len(q_series)} quarterly contracts with data"}
            excluded[base] = per_asset_meta[base]
            continue
        entry = assemble_asset(base, perp_df, q_series, q_expiry, start_ts, end_ts)
        if entry is None:
            per_asset_meta[base] = {"status": "excluded",
                                    "exclusion_reason": "empty common term-structure grid"}
            excluded[base] = per_asset_meta[base]
            continue
        sp = OUT_DIR / f"{base}.npz"
        np.savez_compressed(sp, **entry["arrays"])
        sha = sha256_file(sp)
        nbytes = int(sp.stat().st_size)
        shard_meta[base] = {"sha256": sha, "bytes": nbytes}
        per_asset_meta[base] = {"status": "ok", "n_bars": entry["n_bars"],
                                "window_start_utc": entry["window_start_utc"],
                                "window_end_utc": entry["window_end_utc"],
                                "shard": str(sp.relative_to(ROOT)), "shard_sha256": sha,
                                "shard_bytes": nbytes,
                                "quarterly_contracts": sorted(q_series.keys())}
        assembled.append(base)
        for s in [perp_sym] + eligible_q[base]:
            for m in months:
                p = _month_shard_path(s, m)
                if p.exists():
                    p.unlink()
        man["assembled"] = sorted(set(man.get("assembled", [])) | {base})
        for s in [perp_sym] + eligible_q[base]:
            man["months"] = {k: v for k, v in (man.get("months") or {}).items()
                             if not k.startswith(s + "_")}
        _save_manifest(man)

    if not assembled:
        raise SystemExit("FATAL: no asset assembled a common term-structure grid")

    total_bytes = sum(int(v["bytes"]) for v in shard_meta.values())
    _assert_under_budget([OUT_DIR / f"{s}.npz" for s in assembled], total_bytes)

    selected = sorted(assembled)
    max_shard = max(shard_meta[s]["bytes"] for s in selected)
    grid_bars = sum(per_asset_meta[s]["n_bars"] for s in selected)
    union_idx = None
    for s in selected:
        with np.load(OUT_DIR / f"{s}.npz") as z:
            idx = np.asarray(z["index_ms"], dtype="int64")
        union_idx = idx if union_idx is None else np.union1d(union_idx, idx)
    common_grid_bars = int(len(union_idx))
    common_grid_start = str(pd.Timestamp(int(union_idx[0]), unit="ms", tz="UTC"))
    common_grid_end = str(pd.Timestamp(int(union_idx[-1]), unit="ms", tz="UTC"))

    meta = {
        "generated_at_utc": ts, "campaign": 313, "part": "ingest",
        "interval": INTERVAL, "source_interval": "coin_m_klines_1h",
        "symbols": selected, "n_symbols": len(selected), "n_universe": len(symbols),
        "excluded_bases": excluded,
        "excluded_contracts": contract_excluded,
        "universe_source": "s3_listing_data/futures/cm/monthly/klines/",
        "window_start_month": args.start_month, "window_end_month": args.end_month,
        "quarterly_expiry_start": QUARTERLY_EXPIRY_START,
        "quarterly_expiry_end": QUARTERLY_EXPIRY_END,
        "source_host": ARCHIVE_HOST, "klines_endpoint": KLINES_PATH,
        "storage": "per_asset_float32_npz_shards",
        "f32_legs": list(F32_LEGS),
        "shard_dir": str(OUT_DIR.relative_to(ROOT)),
        "months_dir": str(MONTHS_DIR.relative_to(ROOT)),
        "months_manifest": str(MANIFEST.relative_to(ROOT)),
        "resumable": True,
        "resumability_scheme": "per_symbol_contract_listed_month_shard_skip_on_manifest",
        "shard_sha256": {s: shard_meta[s]["sha256"] for s in selected},
        "shard_bytes": {s: shard_meta[s]["bytes"] for s in selected},
        "total_shard_bytes": int(total_bytes), "max_shard_bytes": int(max_shard),
        "total_grid_bars": int(grid_bars),
        "per_asset_n_bars": {s: int(per_asset_meta[s]["n_bars"]) for s in selected},
        "common_grid_bars": common_grid_bars,
        "common_grid_start_utc": common_grid_start,
        "common_grid_end_utc": common_grid_end,
        "common_grid_basis": "union_of_per_asset_valid_1h_bars",
        "push_limit_bytes": PUSH_LIMIT_BYTES, "cache_budget_bytes": CACHE_BUDGET_BYTES,
        "under_push_limit": bool(max_shard < PUSH_LIMIT_BYTES),
        "under_cache_budget": bool(total_bytes < CACHE_BUDGET_BYTES),
        "real_data_only": True, "fabricated_data": False,
        "fetch_real_data_only": True, "fetch_fabricated_data": False,
        "executed_fills": False,
    }
    manifest_map = {s: shard_meta[s]["sha256"] for s in sorted(shard_meta)}
    meta["manifest_sha256"] = hashlib.sha256(
        json.dumps(manifest_map, sort_keys=True).encode()).hexdigest()
    OUT_META.write_text(json.dumps(meta, indent=2) + "\n")

    provenance = {
        "generated_at_utc": ts, "campaign": 313, "part": "provenance",
        "source_host": ARCHIVE_HOST, "klines_endpoint": KLINES_PATH,
        "interval": INTERVAL, "window_start_month": args.start_month,
        "window_end_month": args.end_month, "n_months": len(months),
        "symbols": selected, "n_universe": len(symbols),
        "excluded_bases": excluded,
        "excluded_contracts": contract_excluded,
        "universe_discovery": "S3 ListBucketResult common-prefix listing (authoritative)",
        "per_asset": per_asset_meta,
        "grid_construction": "perp_plus_front_and_next_unexpired_quarterly_common_1h_grid",
        "quarterly_expiry_rule": "last Friday of Mar/Jun/Sep/Dec 08:00 UTC; code <BASE>USD_YYMMDD",
        "basis_rule": "annualized basis = ln(q_close/perp_close) * hours_per_year / tte_hours",
        "funding_source": "unreachable_fapi_451_and_not_in_monthly_archives_nan_control_only",
        "download": {"n_pairs": len(todo), "n_month_errors": len(errors),
                     "errors": errors[:20], "elapsed_s": dl_s},
        "resumable": True, "real_data_only": True, "fabricated_data": False,
        "fetch_real_data_only": True, "fetch_fabricated_data": False,
        "executed_fills": False,
        "manifest_sha256": meta["manifest_sha256"],
        "blocked_routes": ["data.binance.vision/data/coin-m/ (404, does not exist)",
                           "data.binance.vision/data/coin-m/quarterly_klines/ (404, does not exist)",
                           "COIN-M indexPriceKlines (404)", "fapi fundingRate (451)"],
        "gap_bar_policy": "bars without a 1h kline are dropped (never filled)",
    }
    OUT_PROV.write_text(json.dumps(provenance, indent=2) + "\n")

    print(json.dumps({
        "campaign": 313, "part": "ingest", "interval": INTERVAL,
        "symbols_ok": selected, "n_symbols": len(selected),
        "excluded_bases": {k: v.get("exclusion_reason") for k, v in excluded.items()},
        "n_months": len(months), "n_download_pairs": len(todo),
        "download_elapsed_s": dl_s, "n_month_errors": len(errors),
        "total_grid_bars": int(grid_bars),
        "common_grid_bars": int(common_grid_bars),
        "common_grid_start_utc": common_grid_start,
        "common_grid_end_utc": common_grid_end,
        "excluded_contracts": len(contract_excluded),
        "max_shard_mb": round(max_shard / 1e6, 2),
        "total_shard_mb": round(total_bytes / 1e6, 2),
        "under_cache_budget": bool(total_bytes < CACHE_BUDGET_BYTES),
        "manifest_sha256": meta["manifest_sha256"],
        "shard_dir": str(OUT_DIR.relative_to(ROOT)),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())