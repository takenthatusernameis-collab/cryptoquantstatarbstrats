#!/usr/bin/env python3
"""C313 preflight: fail-closed verification of the real COIN-M inverse quarterly
term-structure carry cache, with a reachability probe against the CORRECTED
data/futures/cm/ path when the cache is not yet built.

Verifies (cache present):
- per-asset float32 ``.npz`` shards exist and every shard SHA256 matches the
  meta manifest; every shard < 100 MB (GitHub push limit), total cache < 100 MB;
- meta flags (real_data_only:true, fabricated_data:false, executed_fills:false),
  interval=1h, source/host intact, resumable scheme recorded;
- the ARCHIVE-DISCOVERED universe: >= 6 tradable assets (8 expected), every
  excluded base documented with a reason (verified: DOGEUSD/MATICUSD/AVAXUSD have
  NO quarterly contracts in the archive, so they are excluded, not fabricated);
- the union 1h grid is non-empty, inside 2022-07..2026-06 and >= 6 assets;
- every asset has finite positive perp_close and finite front/next quarterly
  close + annualized basis wherever it has bars; NaN gaps never imputed;
- >= 2 quarterly contracts recorded per asset;
- walk-forward splits (train 12m -> test 3m, roll 3m) fit the union grid.

Verifies (cache absent):
- reachability of https://data.binance.vision/data/futures/cm/monthly/klines/
  for sample COIN-M perp + quarterly contract-months discovered from the S3
  listing (HTTP 200 required for >= 80% of probes);
- reports ready:false with blocker "cache_missing" and exit non-zero (fail-closed).

Stdlib-only reachability probe so it runs before the numpy/pandas bootstrap.
Never fetches, imputes, resamples, or fabricates data beyond the reachability probe.
Exit 0 iff ready:true.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "data" / "cache" / "campaign313_coinm_quarterly_carry"
CACHE_META = ROOT / "data" / "cache" / "campaign313_coinm_quarterly_carry.meta.json"
CACHE_PROV = ROOT / "data" / "cache" / "campaign313_coinm_quarterly_carry.provenance.json"
MANIFEST = ROOT / "data" / "cache" / "campaign313_coinm_quarterly_carry" / "months_manifest.json"

BASE = "https://data.binance.vision"
S3_LIST = ("https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"
           "?delimiter=/&prefix={prefix}")
KLINES_PATH = "/data/futures/cm/monthly/klines/{sym}/1h/{sym}-1h-{month}.zip"
PUSH_LIMIT_BYTES = 100_000_000
CACHE_BUDGET_BYTES = 100_000_000
HTTP_RETRIES = 6
PROBE_ATTEMPTS = 5
PROBE_TIMEOUT = 20.0
MIN_REACHABLE_RATE = 0.80

EXPECTED_INTERVAL = "1h"
EXPECTED_SOURCE_INTERVAL = "coin_m_klines_1h"
MIN_SYMBOLS = 6          # archive-discovered tradable universe floor
EXPECTED_SYMBOLS = 8     # BTC/ETH/BNB/XRP/ADA/DOT/LTC/SOL have quarterly contracts
WINDOW_START = "2022-07"
WINDOW_END = "2026-06"
PROBE_MONTHS = ("2024-01", "2024-06", "2025-06")

# Runner grid (must match run_c313_coinm_quarterly_carry_oos.py).
TRAIN_HOURS = 365 * 24          # train 12m in 1h bars
TEST_HOURS = 90 * 24            # test 3m in 1h bars
STEP_HOURS = 90 * 24            # roll 3m
LOOKBACKS_1H = (168, 720, 2160, 4320, 8760)
MIN_SPLITS = 5

_QSYM_RE = re.compile(r"^(?P<base>[A-Z0-9]+)USD_(?P<code>\d{6})$")


def _ctx() -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def probe_url(url: str) -> dict:
    """GET with retry-with-backoff; HTTP 200 = reachable."""
    last: dict = {}
    started = _now()
    for attempt in range(1, PROBE_ATTEMPTS + 1):
        t0 = time.time()
        try:
            req = urllib.request.Request(url, method="GET",
                                         headers={"User-Agent": "kilo-c313-preflight"})
            with urllib.request.urlopen(req, timeout=PROBE_TIMEOUT, context=_ctx()) as r:
                status = int(r.status)
                r.close()
            if status == 200:
                return {"url": url, "status": status, "attempts": attempt,
                        "started_utc": started, "finished_utc": _now(),
                        "elapsed_s": round(time.time() - t0, 3), "reachable": True}
            last = {"status": status, "attempts": attempt}
        except urllib.error.HTTPError as e:
            last = {"status": int(e.code), "attempts": attempt}
        except Exception as e:  # noqa: BLE001
            last = {"status": "ERR", "error": str(e)[:160], "attempts": attempt}
        if attempt < PROBE_ATTEMPTS:
            time.sleep(round(0.6 * attempt, 3))
    return {"url": url, "status": last.get("status", "ERR"),
            "error": last.get("error"), "attempts": PROBE_ATTEMPTS,
            "started_utc": started, "finished_utc": _now(),
            "elapsed_s": None, "reachable": False}


def list_quarterly_contracts(base: str) -> list[str]:
    url = S3_LIST.format(prefix=urllib.parse.quote(
        f"data/futures/cm/monthly/klines/{base}_", safe=""))
    req = urllib.request.Request(url, headers={"User-Agent": "kilo-c313-preflight"})
    with urllib.request.urlopen(req, timeout=PROBE_TIMEOUT, context=_ctx()) as resp:
        body = resp.read().decode("utf-8", "replace")
    out = []
    for p in re.findall(r"<Prefix>([^<]+)</Prefix>", body):
        sym = p.rstrip("/").rsplit("/", 1)[-1]
        if _QSYM_RE.match(sym) and sym.rsplit("_", 1)[0] == base:
            out.append(sym)
    return sorted(set(out))


def list_months(sym: str) -> list[str]:
    url = S3_LIST.format(prefix=urllib.parse.quote(
        f"data/futures/cm/monthly/klines/{sym}/1h/", safe=""))
    req = urllib.request.Request(url, headers={"User-Agent": "kilo-c313-preflight"})
    with urllib.request.urlopen(req, timeout=PROBE_TIMEOUT, context=_ctx()) as resp:
        body = resp.read().decode("utf-8", "replace")
    return sorted({m.group(1) for m in
                   (re.search(r"-(\d{4}-\d{2})\.zip$", k)
                    for k in re.findall(r"<Key>([^<]+)</Key>", body)) if m})


def wf_splits(n: int, train: int, test: int, step: int) -> list:
    out = []
    i = 0
    while i + train + test <= n:
        out.append((i, i + train, i + train + test))
        i += step
    return out


def min_periods_for(L: int) -> int:
    return max(20, L // 3)


def _as_index(pa: dict) -> pd.DatetimeIndex:
    idx = pa.get("index_ms")
    if idx is None:
        raise ValueError("shard missing index_ms")
    return pd.DatetimeIndex(pd.to_datetime(np.asarray(idx, dtype="int64"),
                                           unit="ms", utc=True))


def reachability_probe() -> dict:
    """Probe corrected path for archive-discovered perp + quarterly months."""
    rows: list[dict] = []
    bases = ["BTCUSD", "ETHUSD", "SOLUSD", "DOTUSD"]
    for s in bases:
        for m in PROBE_MONTHS:
            sym = s + "_PERP"
            rows.append(probe_url(BASE + KLINES_PATH.format(sym=sym, month=m)))
            time.sleep(0.05)
    # quarterly rows: first month each discovered contract really has
    for s in bases:
        try:
            qsyms = list_quarterly_contracts(s)
        except Exception as exc:  # noqa: BLE001
            rows.append({"url": f"listing:{s}", "status": "ERR",
                         "error": repr(exc)[:160], "reachable": False})
            continue
        for sym in qsyms[:4]:
            try:
                ms = list_months(sym)
            except Exception as exc:  # noqa: BLE001
                rows.append({"url": f"listing:{sym}", "status": "ERR",
                             "error": repr(exc)[:160], "reachable": False})
                continue
            if not ms:
                rows.append({"url": f"listing:{sym}", "status": "EMPTY",
                             "error": "no months listed", "reachable": False})
                continue
            rows.append(probe_url(BASE + KLINES_PATH.format(sym=sym, month=ms[-1])))
            time.sleep(0.05)
    n_ok = sum(1 for r in rows if r.get("reachable") is True)
    rate = n_ok / len(rows) if rows else 0.0
    return {"rows": rows, "n_probed": len(rows), "n_reachable": n_ok,
            "reachable_rate": rate, "min_required_rate": MIN_REACHABLE_RATE,
            "meets_rate": bool(rate >= MIN_REACHABLE_RATE),
            "path": BASE + "/data/futures/cm/monthly/klines/"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.parse_args()

    checks: dict = {}
    blocked: list[str] = []

    # ---- Case A: cache not yet built -> reachability probe + fail-closed ----
    if not CACHE_META.exists():
        probe = reachability_probe()
        result = {
            "ready": False, "real_data_only": True, "fabricated_data": False,
            "executed_fills": False, "campaign": 313, "part": "preflight",
            "blocked_reasons": ["cache_missing"],
            "checks": {"reachability": probe},
            "cache_missing": True,
        }
        print(json.dumps(result, indent=2, default=str))
        return 1

    try:
        meta = json.loads(CACHE_META.read_text())
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"ready": False, "blocked_reasons": [f"meta unreadable: {exc}"]},
                         indent=2))
        return 1

    shard_sha_meta = meta.get("shard_sha256") or {}
    shard_bytes_meta = meta.get("shard_bytes") or {}

    # ---- shard integrity ----
    shard_ok = True
    shard_detail = {}
    max_shard = 0
    for s, expected_sha in shard_sha_meta.items():
        sp = CACHE_DIR / f"{s}.npz"
        if not sp.exists():
            shard_detail[s] = {"exists": False, "ok": False}
            shard_ok = False
            continue
        actual = sha256_file(sp)
        nbytes = sp.stat().st_size
        max_shard = max(max_shard, nbytes)
        ok = bool(actual == expected_sha and nbytes == int(shard_bytes_meta.get(s, -1))
                  and nbytes < PUSH_LIMIT_BYTES)
        shard_detail[s] = {"exists": True, "sha_ok": actual == expected_sha,
                           "bytes": int(nbytes), "under_push_limit": bool(nbytes < PUSH_LIMIT_BYTES),
                           "ok": ok}
        shard_ok &= ok

    total_shard_bytes = sum(int(v) for v in shard_bytes_meta.values())
    flags_ok = (
        meta.get("interval") == EXPECTED_INTERVAL
        and meta.get("source_interval") == EXPECTED_SOURCE_INTERVAL
        and int(meta.get("n_symbols") or 0) >= MIN_SYMBOLS
        and meta.get("real_data_only") is True
        and meta.get("fabricated_data") is False
        and meta.get("executed_fills") is False
        and meta.get("source_host") == BASE
        and meta.get("under_push_limit") is True
        and int(meta.get("max_shard_bytes") or 0) < PUSH_LIMIT_BYTES
        and int(meta.get("total_shard_bytes") or 0) < CACHE_BUDGET_BYTES
        and meta.get("resumable") is True
        and meta.get("universe_source") == "s3_listing_data/futures/cm/monthly/klines/"
    )
    checks["meta"] = {
        "interval": meta.get("interval"), "source_interval": meta.get("source_interval"),
        "n_symbols": meta.get("n_symbols"), "n_universe": meta.get("n_universe"),
        "real_data_only": meta.get("real_data_only"),
        "fabricated_data": meta.get("fabricated_data"),
        "executed_fills": meta.get("executed_fills"), "source_host": meta.get("source_host"),
        "storage": meta.get("storage"), "resumable": meta.get("resumable"),
        "universe_source": meta.get("universe_source"),
        "max_shard_bytes": int(meta.get("max_shard_bytes") or 0),
        "max_shard_mb": round(int(meta.get("max_shard_bytes") or 0) / 1e6, 2),
        "total_shard_bytes": int(total_shard_bytes),
        "total_shard_mb": round(total_shard_bytes / 1e6, 2),
        "under_push_limit": meta.get("under_push_limit"),
        "under_cache_budget": meta.get("under_cache_budget"),
        "manifest_sha256": meta.get("manifest_sha256"),
        "window_start_month": meta.get("window_start_month"),
        "window_end_month": meta.get("window_end_month"),
        "ok": bool(flags_ok),
    }
    if not flags_ok:
        blocked.append("meta flags/interval/source/size mismatch")
    checks["shards"] = {"n_shards": len(shard_sha_meta), "ok": bool(shard_ok),
                        "detail": shard_detail}
    if not shard_ok:
        blocked.append("one or more shards missing / sha or size mismatch / over push limit")

    manifest = {s: shard_sha_meta[s] for s in sorted(shard_sha_meta)}
    manifest_sha = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()
    checks["manifest"] = {"expected": meta.get("manifest_sha256"), "actual": manifest_sha,
                          "ok": bool(manifest_sha == meta.get("manifest_sha256"))}
    if manifest_sha != meta.get("manifest_sha256"):
        blocked.append("shard manifest sha mismatch")

    # ---- universe (archive-discovered, exclusions documented) ----
    excluded_bases = meta.get("excluded_bases") or {}
    documented = {k: v.get("exclusion_reason") for k, v in excluded_bases.items()}
    universe_ok = (int(meta.get("n_symbols") or 0) >= MIN_SYMBOLS
                   and all(v in ("no_quarterly_contracts_listed",) for v in documented.values())
                   and set(documented) == {"DOGEUSD", "MATICUSD", "AVAXUSD"})
    checks["universe"] = {
        "symbols": list(meta.get("symbols") or []),
        "n_symbols": int(meta.get("n_symbols") or 0),
        "n_universe": int(meta.get("n_universe") or 0),
        "min_required": MIN_SYMBOLS, "expected": EXPECTED_SYMBOLS,
        "excluded_bases": documented,
        "excluded_contracts": len(meta.get("excluded_contracts") or {}),
        "universe_source": meta.get("universe_source"),
        "ok": bool(universe_ok),
    }
    if not universe_ok:
        blocked.append("universe smaller than archive-discovered floor or exclusions undocumented")

    # ---- grid + per-asset ----
    symbols = list(meta.get("symbols") or [])
    n_symbols = len(symbols)
    n_grid = int(meta.get("common_grid_bars") or meta.get("total_grid_bars") or 0)
    grid_start = meta.get("common_grid_start_utc") or meta.get("window_start_month")
    grid_end = meta.get("common_grid_end_utc") or meta.get("window_end_month")
    if n_grid == 0 or n_symbols < MIN_SYMBOLS:
        blocked.append("C313 common grid is empty or universe too small")
    in_window = bool(str(grid_start).startswith(WINDOW_START)
                     and str(grid_end).startswith(WINDOW_END[:4]))
    checks["grid"] = {"n_symbols": n_symbols, "symbols": symbols,
                      "total_grid_bars": int(meta.get("total_grid_bars") or 0),
                      "common_grid_bars": n_grid,
                      "common_grid_basis": meta.get("common_grid_basis"),
                      "grid_start_utc": str(grid_start), "grid_end_utc": str(grid_end),
                      "window_start_month": meta.get("window_start_month"),
                      "window_end_month": meta.get("window_end_month"),
                      "in_window": in_window}
    if not in_window:
        blocked.append("C313 grid not in 2022-07..2026-06 window")

    detail = {}
    all_ok = True
    for s in symbols:
        sp = CACHE_DIR / f"{s}.npz"
        d = {"symbol": s, "fields": {}, "ok": True}
        ok = True
        if not sp.exists():
            d["ok"] = False
            detail[s] = d
            all_ok = False
            continue
        with np.load(sp) as z:
            idx = _as_index({k: z[k] for k in z.files})
            n_bars = int(len(idx))
            for leg in ("perp_close", "front_close", "next_close",
                        "front_basis", "next_basis", "front_tte_hours",
                        "next_tte_hours"):
                v = np.asarray(z[leg], dtype=float)
                present = v[np.isfinite(v)]
                if leg == "perp_close":
                    leg_ok = bool(len(present) == n_bars and np.isfinite(present).all()
                                  and (present > 0).all())
                elif leg in ("front_close", "next_close"):
                    leg_ok = bool(len(present) == n_bars and np.isfinite(present).all()
                                  and (present > 0).all())
                else:
                    leg_ok = bool(len(v) == n_bars and np.isfinite(present).all())
                d["fields"][leg] = {"len": int(len(v)), "nan": int(np.isnan(v).sum()),
                                    "finite_present": int(len(present)), "ok": leg_ok}
                ok &= leg_ok
            exp = np.asarray(z["front_expiry_ms"], dtype=float)
            d["n_quarterly_front_expiries"] = int(len(np.unique(exp[np.isfinite(exp)])))
            ok &= d["n_quarterly_front_expiries"] >= 2
            d["n_bars"] = n_bars
        d["ok"] = bool(ok)
        detail[s] = d
        all_ok &= bool(ok)
    checks["per_asset"] = {"n_symbols": n_symbols, "detail": detail, "ok": bool(all_ok)}
    if not all_ok:
        blocked.append("one or more assets failed perp/quarterly/basis checks")

    # walk-forward fit
    n_splits = len(wf_splits(n_grid, TRAIN_HOURS, TEST_HOURS, STEP_HOURS))
    wf_ok = n_grid >= TRAIN_HOURS + TEST_HOURS and n_splits >= MIN_SPLITS
    checks["walk_forward"] = {"bars": n_grid, "train_hours": TRAIN_HOURS,
                              "test_hours": TEST_HOURS, "step_hours": STEP_HOURS,
                              "n_splits": int(n_splits), "min_splits": MIN_SPLITS,
                              "ok": bool(wf_ok)}
    if not wf_ok:
        blocked.append("walk-forward splits do not fit the grid")

    # feature warmup for all runner lookbacks
    warm = {f"L={L}": {"min_periods": int(min_periods_for(L)),
                       "fits_train": bool(min_periods_for(L) <= TRAIN_HOURS),
                       "ok": bool(min_periods_for(L) <= TRAIN_HOURS)} for L in LOOKBACKS_1H}
    warm_ok = all(v["ok"] for v in warm.values())
    checks["feature_warmup"] = {"rule": "min_periods = max(20, L // 3) on native-1h features",
                                "lookbacks_1h": [int(l) for l in LOOKBACKS_1H],
                                "warmup": warm, "ok": bool(warm_ok)}
    if not warm_ok:
        blocked.append("feature lookbacks do not fit the train window")

    checks["provenance"] = {"path": str(CACHE_PROV.relative_to(ROOT)) if CACHE_PROV.exists()
                            else str(CACHE_PROV),
                            "exists": bool(CACHE_PROV.exists()),
                            "ok": bool(CACHE_PROV.exists())}
    if not CACHE_PROV.exists():
        blocked.append("provenance json missing")

    checks["manifest_file"] = {"path": str(MANIFEST.relative_to(ROOT)) if MANIFEST.exists()
                               else str(MANIFEST),
                               "exists": bool(MANIFEST.exists()),
                               "ok": bool(MANIFEST.exists())}

    ready = not blocked
    result = {
        "ready": ready, "real_data_only": True, "fabricated_data": False,
        "executed_fills": False, "campaign": 313, "part": "preflight",
        "checks": checks, "blocked_reasons": blocked,
    }
    print(json.dumps(result, indent=2, default=str))
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())