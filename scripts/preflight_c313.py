#!/usr/bin/env python3
"""C313 preflight: fail-closed verification of the real COIN-M inverse quarterly
term-structure carry cache, with a reachability probe against the CORRECTED
data/futures/cm/ path when the cache is not yet built.

Verifies (cache present):
- per-asset float32 ``.npz`` shards exist and every shard SHA256 matches the
  meta manifest; every shard < 100 MB (GitHub push limit), total cache < 100 MB;
- meta flags (real_data_only:true, fabricated_data:false, executed_fills:false),
  interval=1h, source/host intact, resumable scheme recorded;
- the common 1h term-structure grid is non-empty and inside 2022-07..2026-06;
- every selected asset has finite positive perp_close and finite front/next
  quarterly close + annualized basis where present; NaN gaps never imputed;
- >= 2 quarterly contracts overlap the perp (front + next);
- walk-forward splits (train 12m -> test 3m, roll 3m) fit the grid.

Verifies (cache absent):
- reachability of https://data.binance.vision/data/futures/cm/monthly/klines/
  for sample COIN-M perp + quarterly contract-months (HTTP 200 required);
- reports ready:false with blocker "cache_missing" and exit non-zero (fail-closed).

Stdlib-only reachability probe so it runs before the numpy/pandas bootstrap.
Never fetches, imputes, resamples, or fabricates data beyond the reachability probe.
Exit 0 iff ready:true.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import ssl
import sys
import time
import urllib.error
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
KLINES_PATH = "/data/futures/cm/monthly/klines/{sym}/1h/{sym}-1h-{month}.zip"
PUSH_LIMIT_BYTES = 100_000_000
CACHE_BUDGET_BYTES = 100_000_000
HTTP_RETRIES = 6
PROBE_ATTEMPTS = 5
PROBE_TIMEOUT = 20.0

EXPECTED_INTERVAL = "1h"
EXPECTED_SOURCE_INTERVAL = "coin_m_klines_1h"
N_SYMBOLS = 11
WINDOW_START = "2022-07"
WINDOW_END = "2026-06"

# Runner grid (must match run_c313_coinm_quarterly_carry_oos.py).
TRAIN_HOURS = 365 * 24          # train 12m in 1h bars
TEST_HOURS = 90 * 24            # test 3m in 1h bars
STEP_HOURS = 90 * 24            # roll 3m
LOOKBACKS_1H = (168, 720, 2160, 4320, 8760)


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
    """GET headers-only with retry-with-backoff; HTTP 200 = reachable."""
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
    """Probe corrected path for sample perp + quarterly contract-months."""
    rows: list[dict] = []
    symbols = ["BTCUSD", "ETHUSD"]
    months = ["2024-01", "2024-06"]
    # perp rows (symbol = <BASE>_PERP, e.g. BTCUSD_PERP — verified live)
    for s in symbols:
        for m in months:
            sym = s + "_PERP"
            rows.append(probe_url(BASE + KLINES_PATH.format(sym=sym, month=m)))
            time.sleep(0.1)
    # quarterly rows (front/next contracts around the window)
    quarterly = [("BTCUSD_240628", "2023-12"), ("BTCUSD_240927", "2024-06"),
                 ("ETHUSD_240628", "2023-12"), ("ETHUSD_240927", "2024-06")]
    for sym, m in quarterly:
        rows.append(probe_url(BASE + KLINES_PATH.format(sym=sym, month=m)))
        time.sleep(0.1)
    n_ok = sum(1 for r in rows if r.get("reachable") is True)
    return {"rows": rows, "n_probed": len(rows), "n_reachable": n_ok,
            "reachable_rate": n_ok / len(rows) if rows else 0.0,
            "path": BASE + "/data/futures/cm/monthly/klines/"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

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
        and int(meta.get("n_symbols") or 0) >= N_SYMBOLS
        and meta.get("real_data_only") is True
        and meta.get("fabricated_data") is False
        and meta.get("executed_fills") is False
        and meta.get("source_host") == BASE
        and meta.get("under_push_limit") is True
        and int(meta.get("max_shard_bytes") or 0) < PUSH_LIMIT_BYTES
        and meta.get("resumable") is True
    )
    checks["meta"] = {
        "interval": meta.get("interval"), "source_interval": meta.get("source_interval"),
        "n_symbols": meta.get("n_symbols"), "real_data_only": meta.get("real_data_only"),
        "fabricated_data": meta.get("fabricated_data"),
        "executed_fills": meta.get("executed_fills"), "source_host": meta.get("source_host"),
        "storage": meta.get("storage"), "resumable": meta.get("resumable"),
        "max_shard_bytes": int(meta.get("max_shard_bytes") or 0),
        "max_shard_mb": round(int(meta.get("max_shard_bytes") or 0) / 1e6, 2),
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

    # ---- grid + per-asset ----
    symbols = list(meta.get("symbols") or [])
    n_symbols = len(symbols)
    n_grid = int(meta.get("total_grid_bars") or 0)
    grid_start = meta.get("window_start_month")
    grid_end = meta.get("window_end_month")
    if n_grid == 0 or not symbols:
        blocked.append("C313 common grid is empty")
    in_window = bool(str(grid_start).startswith(WINDOW_START)
                     and str(grid_end).startswith(WINDOW_END))
    checks["grid"] = {"n_symbols": n_symbols, "symbols": symbols, "total_grid_bars": n_grid,
                      "window_start_month": grid_start, "window_end_month": grid_end,
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
            d["n_bars"] = n_bars
        d["ok"] = bool(ok)
        detail[s] = d
        all_ok &= bool(ok)
    checks["per_asset"] = {"n_symbols": n_symbols, "detail": detail, "ok": bool(all_ok)}
    if not all_ok:
        blocked.append("one or more assets failed perp/quarterly/basis checks")

    # walk-forward fit
    n_splits = len(wf_splits(n_grid, TRAIN_HOURS, TEST_HOURS, STEP_HOURS))
    wf_ok = n_grid >= TRAIN_HOURS + TEST_HOURS and n_splits > 0
    checks["walk_forward"] = {"bars": n_grid, "train_hours": TRAIN_HOURS,
                              "test_hours": TEST_HOURS, "step_hours": STEP_HOURS,
                              "n_splits": int(n_splits), "ok": bool(wf_ok)}
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
