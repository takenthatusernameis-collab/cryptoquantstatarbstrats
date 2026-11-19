#!/usr/bin/env python3
"""C377 feature build — real USDT-M linear perp cross-sectional intraday
WINDOW OLS TREND-SLOPE T-STATISTIC (PSLOPE) x seasonal-dislocation
mean-reversion stat-arb raw inputs.

Reads the REAL, SHA-verified 5m USDT-M kline close from the C312 USDT-M OFI
cache (data/cache/campaign312_usdt_m_ofi_5m/<SYM>.npz), aligns the common 5m
grid across all 10 perps, and stores genuinely-distinct per-bar raw inputs
(real only):

    data/cache/campaign377_pslope_5m/<SYM>.npz
        index_ms        int64   common 5m grid (ms)
        perp_close      float32 real 5m kline close (execution price)
        log_return      float32 causal log-return (r[t]=log(c[t]/c[t-1]), r[0]=0)
        abs_ret         float32 |log_return_t| (absolute return magnitude)
        funding_rate    float32 all-NaN (control)

The runner derives the causal per-bar PSLOPE scalars over a fixed intrinsic
window W=256 bars ending at bar t (trailing prices C=perp_close[t-W+1..t],
y=log(C), s=0..W-1; b=Σ(s-s̄)(y-ȳ)/Σ(s-s̄)², a=ȳ-b·s̄, sse=Σ(y-a-b·s)²,
sxx=Σ(s-s̄)²):

    pslope_t[t]   = b / sqrt((sse/(W-2))/sxx)      # trend significance (OLS slope t-stat)
    pslope_slope[t] = b·W                          # fitted net log-drift over the window

NaN if t<W-1, any NaN/non-finite/<=0 price in the window, sxx<=0, sse<=0, or
non-finite output. PSLOPE is fitted-trend SIGNIFICANCE — genuinely distinct
from C365 (KER net-displacement/path-length ratio), C346/C350 (Hurst/DFA
scaling exponents), C353 (variance ratio), C326 (lag-1 autocorr), C343 (|r|
autocorr), and every moment/entropy/quantile/geometry family C281B–C376.
Cache stays under the 100 MB budget. Read-only reuse of real on-disk data — no
network, no fabrication, no resampling, no imputation.

C377 is genuinely distinct from all prior families C281B–C376.
Price-only (perp_close), volume-free.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

SRC_DIR = ROOT / "data" / "cache" / "campaign312_usdt_m_ofi_5m"
SRC_META = ROOT / "data" / "cache" / "campaign312_usdt_m_ofi_5m.meta.json"
DST_DIR = ROOT / "data" / "cache" / "campaign377_pslope_5m"
DST_META = ROOT / "data" / "cache" / "campaign377_pslope_5m.meta.json"
DST_PROV = ROOT / "data" / "cache" / "campaign377_pslope_5m.provenance.json"

PUSH_LIMIT_BYTES = 100_000_000
CACHE_BUDGET_BYTES = 100_000_000
BAR_MS = 300_000
TOD_BARS = 288
WEEKDAYS = 7
N_BUCKETS = WEEKDAYS * TOD_BARS
WINDOW_START = "2023-01"
WINDOW_END = "2025-12"

FIELDS = ["index_ms", "perp_close", "log_return", "abs_ret", "funding_rate"]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def pd_ts(ms: int) -> str:
    return datetime.fromtimestamp(int(ms) / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S+00:00")


def _content_ok(path: Path) -> bool:
    try:
        with np.load(path) as z:
            if set(z.files) != set(FIELDS):
                return False
            idx = np.asarray(z["index_ms"], dtype="int64")
            pc = np.asarray(z["perp_close"], dtype=float)
            lr = np.asarray(z["log_return"], dtype=float)
            ar = np.asarray(z["abs_ret"], dtype=float)
            fr = np.asarray(z["funding_rate"], dtype=float)
        n = len(idx)
        if not (n > 0 and all(len(a) == n for a in (pc, lr, ar, fr))):
            return False
        if not (np.isfinite(pc).all() and (pc > 0).all()):
            return False
        if not np.isfinite(lr).all():
            return False
        if not np.isfinite(ar).all():
            return False
        if not np.isnan(fr).all():
            return False
        return True
    except Exception:  # noqa: BLE001
        return False


def _verify_existing(symbols: list[str]) -> bool:
    if not DST_META.exists() or not DST_PROV.exists():
        return False
    try:
        meta = json.loads(DST_META.read_text())
    except Exception:  # noqa: BLE001
        return False
    if int(meta.get("campaign") or 0) != 377:
        return False
    if meta.get("real_data_only") is not True or meta.get("fabricated_data") is not False:
        return False
    if meta.get("interval") != "5m" or int(meta.get("source_campaign") or 0) != 312:
        return False
    if list(meta.get("symbols") or []) != list(symbols):
        return False
    shard_sha_meta = meta.get("shard_sha256") or {}
    manifest = {s: shard_sha_meta[s] for s in sorted(shard_sha_meta)}
    if sha256_bytes(json.dumps(manifest, sort_keys=True).encode()) != meta.get("manifest_sha256"):
        return False
    shard_bytes_meta = meta.get("shard_bytes") or {}
    for s in symbols:
        sp = DST_DIR / f"{s}.npz"
        if not sp.exists():
            return False
        if sha256_file(sp) != shard_sha_meta.get(s):
            return False
        if sp.stat().st_size != int(shard_bytes_meta.get(s, -1)):
            return False
        if not _content_ok(sp):
            return False
    return True


def _align(arr: np.ndarray, pos: dict, grid: np.ndarray, direct: bool) -> np.ndarray:
    if direct:
        return np.asarray(arr, dtype=np.float64)
    out = np.empty(len(grid), dtype=np.float64)
    for j, g in enumerate(grid):
        out[j] = arr[pos[int(g)]]
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true", help="emit a JSON summary")
    ap.add_argument("--force", action="store_true", help="rebuild even if the destination verifies")
    args = ap.parse_args(argv)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    if not SRC_META.exists():
        raise SystemExit(f"FATAL: C312 source meta missing: {SRC_META}")
    src = json.loads(SRC_META.read_text())
    if src.get("real_data_only") is not True or src.get("fabricated_data") is not False:
        raise SystemExit("FATAL: C312 source flags are not real_data_only/fabricated_data")
    if src.get("interval") != "5m":
        raise SystemExit(f"FATAL: C312 source interval must be 5m, got {src.get('interval')}")

    src_sha = sha256_file(SRC_META)
    shard_sha_meta = src.get("shard_sha256") or {}
    shard_bytes_meta = src.get("shard_bytes") or {}
    symbols = list(src.get("symbols") or [])
    if len(symbols) < 10:
        raise SystemExit(f"FATAL: need >= 10 symbols, got {len(symbols)}")

    REQUIRED_SRC_FIELDS = ("index_ms", "perp_close")
    per_asset: dict[str, dict] = {}
    grid_sets: list[set] = []
    for s in symbols:
        sp = SRC_DIR / f"{s}.npz"
        if not sp.exists():
            raise SystemExit(f"FATAL: source shard missing: {sp}")
        actual = sha256_file(sp)
        if actual != shard_sha_meta.get(s):
            raise SystemExit(f"FATAL: source shard sha256 mismatch for {s}")
        nbytes = sp.stat().st_size
        if nbytes != int(shard_bytes_meta.get(s, -1)):
            raise SystemExit(f"FATAL: source shard byte size mismatch for {s}")
        with np.load(sp) as z:
            missing = [f for f in REQUIRED_SRC_FIELDS if f not in z.files]
            if missing:
                raise SystemExit(f"FATAL: source shard {s} missing fields: {missing}")
            idx_ms = np.asarray(z["index_ms"], dtype=np.int64)
            pc = np.asarray(z["perp_close"], dtype=np.float64)
        if not np.isfinite(pc).all() or not (pc > 0).all():
            raise SystemExit(f"FATAL: source perp_close non-finite/non-positive for {s}")
        per_asset[s] = {"index_ms": idx_ms, "perp_close": pc}
        grid_sets.append(set(idx_ms.tolist()))

    common = set.intersection(*grid_sets)
    if not common:
        raise SystemExit("FATAL: empty common 5m grid across symbols")
    grid = np.array(sorted(common), dtype=np.int64)
    if len(np.unique(np.diff(grid))) != 1:
        steps, counts = np.unique(np.diff(grid), return_counts=True)
        if int(steps[int(np.argmax(counts))]) != BAR_MS:
            raise SystemExit("FATAL: common grid is not uniformly 5m")

    if not args.force and DST_DIR.exists() and _verify_existing(symbols):
        meta = json.loads(DST_META.read_text())
        summary = {
            "built": False,
            "verified": True,
            "note": "C377 cache already present and faithful (SHA/size/content OK); left untouched.",
            "campaign": 377,
            "part": "feature_build",
            "symbols": symbols,
            "n_symbols": len(symbols),
            "n_grid_bars": int(len(grid)),
            "total_shard_bytes": int(meta.get("total_shard_bytes") or 0),
            "max_shard_bytes": int(meta.get("max_shard_bytes") or 0),
            "under_push_limit": meta.get("under_push_limit"),
            "under_cache_budget": meta.get("under_cache_budget"),
            "meta_sha256": sha256_file(DST_META),
            "provenance_sha256": sha256_file(DST_PROV),
            "manifest_sha256": meta.get("manifest_sha256"),
            "source_meta_sha256": src_sha,
            "real_data_only": True,
            "fabricated_data": False,
            "executed_fills": False,
        }
        print(json.dumps(summary, indent=2))
        return 0

    DST_DIR.mkdir(parents=True, exist_ok=True)

    shard_sha256: dict[str, str] = {}
    shard_bytes: dict[str, int] = {}
    per_symbol_prov: dict[str, dict] = {}
    total = 0
    max_shard = 0

    for s in symbols:
        pa = per_asset[s]
        idx_src = pa["index_ms"]
        direct = bool(np.array_equal(idx_src, grid))
        if direct:
            pos = {}
        else:
            pos = {int(v): i for i, v in enumerate(idx_src.tolist())}

        pc = _align(pa["perp_close"], pos, grid, direct)

        log_return = np.zeros_like(pc, dtype=np.float64)
        log_return[1:] = np.log(pc[1:] / pc[:-1])
        log_return = np.where(np.isfinite(log_return), log_return, 0.0)

        abs_ret = np.abs(log_return)

        funding = np.full(len(grid), np.nan, dtype=np.float64)

        out = {
            "index_ms": grid.astype(np.int64),
            "perp_close": pc.astype(np.float32),
            "log_return": log_return.astype(np.float32),
            "abs_ret": abs_ret.astype(np.float32),
            "funding_rate": funding.astype(np.float32),
        }
        dst = DST_DIR / f"{s}.npz"
        np.savez_compressed(dst, **out)

        b = dst.read_bytes()
        sha = sha256_bytes(b)
        shard_sha256[s] = sha
        shard_bytes[s] = len(b)
        total += len(b)
        max_shard = max(max_shard, len(b))
        per_symbol_prov[s] = {
            "status": "ok",
            "n_bars": int(len(grid)),
            "shard": str(dst.relative_to(ROOT)),
            "shard_sha256": sha,
            "shard_bytes": int(len(b)),
            "source": "campaign312_usdt_m_ofi_5m (perp_close)",
            "source_sha256": shard_sha_meta.get(s),
            "perp_close_nan": int(np.isnan(pc).sum()),
            "log_return_nan": int(np.isnan(log_return).sum()),
            "abs_ret_nan": int(np.isnan(abs_ret).sum()),
            "funding_all_nan": bool(np.isnan(funding).all()),
        }

    manifest = {s: shard_sha256[s] for s in sorted(shard_sha256)}
    manifest_sha = sha256_bytes(json.dumps(manifest, sort_keys=True).encode())

    raw_nan_observed = {}
    for s in symbols:
        with np.load(DST_DIR / f"{s}.npz") as z:
            raw_nan_observed[s] = {
                "log_return": int(np.isnan(np.asarray(z["log_return"], dtype=float)).sum()),
                "abs_ret": int(np.isnan(np.asarray(z["abs_ret"], dtype=float)).sum()),
            }

    meta = {
        "generated_at_utc": ts,
        "campaign": 377,
        "part": "feature_build",
        "interval": "5m",
        "bar_ms": BAR_MS,
        "source_interval": "usdt_m_5m_klines_taker_delta_ms",
        "source_campaign": 312,
        "source_cache": str(SRC_DIR.relative_to(ROOT)),
        "source_meta": str(SRC_META.relative_to(ROOT)),
        "source_meta_sha256": src_sha,
        "symbols": symbols,
        "n_symbols": len(symbols),
        "n_universe": len(symbols),
        "n_grid_bars": int(len(grid)),
        "window_start_month": WINDOW_START,
        "window_end_month": WINDOW_END,
        "grid_start_utc": pd_ts(grid[0]),
        "grid_end_utc": pd_ts(grid[-1]),
        "grid_construction": "intersection_of_c312_perp_5m_bars",
        "fields": FIELDS,
        "storage": "per_asset_float32_npz_shards",
        "shard_dir": str(DST_DIR.relative_to(ROOT)),
        "shard_sha256": shard_sha256,
        "shard_bytes": shard_bytes,
        "total_shard_bytes": int(total),
        "max_shard_bytes": int(max_shard),
        "cache_budget_bytes": CACHE_BUDGET_BYTES,
        "push_limit_bytes": PUSH_LIMIT_BYTES,
        "under_push_limit": bool(total < PUSH_LIMIT_BYTES and max_shard < PUSH_LIMIT_BYTES),
        "under_cache_budget": bool(total < CACHE_BUDGET_BYTES),
        "n_buckets_tod_dow": int(N_BUCKETS),
        "pslope_params": {
            "window_W": 256,
        },
        "field_definition": (
            "perp_close: real 5m kline close from C312 (strictly positive, gap-free); "
            "log_return=log(c[t]/c[t-1]) (r[0]=0) derived from perp_close; "
            "abs_ret=|log_return|; "
            "funding_rate all-NaN control (USDT-M funding unreachable). "
            "Runner derives PSLOPE scalars over fixed intrinsic window W=256 bars "
            "ending at t (trailing prices C=perp_close[t-W+1..t], y=log(C), "
            "s=0..W-1): b=Σ(s-s̄)(y-ȳ)/Σ(s-s̄)², a=ȳ-b·s̄, sse=Σ(y-a-b·s)², "
            "sxx=Σ(s-s̄)²; pslope_t=b/sqrt((sse/(W-2))/sxx) (OLS slope t-stat, "
            "trend significance); pslope_slope=b·W (fitted net log-drift). "
            "Seasonal deviation of each scalar at same "
            "(weekday,tod) bucket from history strictly before t (causal shift(1)), "
            "NaN-aware min_periods=3."
        ),
        "funding_source": "unreachable_fapi_451_and_not_in_monthly_archives_nan_control_only",
        "network_ingest": False,
        "resample": False,
        "real_data_only": True,
        "fabricated_data": False,
        "fetch_real_data_only": True,
        "fetch_fabricated_data": False,
        "executed_fills": False,
        "manifest_sha256": manifest_sha,
        "nan_policy": {
            "log_return": "causal log-return from real strictly-positive perp_close; always finite (r[0]=0)",
            "abs_ret": "|log_return|; always finite",
            "funding_rate": "all-NaN control only (USDT-M funding unreachable in this environment)",
            "runner_nan": "trailing same-bucket seasonal stats NaN-aware min_periods excluding NaN obs; NaN-score bars weight 0; PSLOPE scalars NaN where t<W-1, any NaN/non-finite/<=0 price in window, sxx<=0, sse<=0, or non-finite output.",
            "raw_nan_observed": raw_nan_observed,
        },
    }
    DST_META.write_text(json.dumps(meta, indent=2) + "\n")

    prov = {
        "generated_at_utc": ts,
        "campaign": 377,
        "part": "provenance",
        "source_host": "https://data.binance.vision",
        "note": "C377 features are a read-only derivation of real C312 USDT-M 5m perp_close (log_return, abs_ret derived); no network, no fabrication, no resampling.",
        "interval": "5m",
        "bar_ms": BAR_MS,
        "window_start_month": WINDOW_START,
        "window_end_month": WINDOW_END,
        "n_months": 36,
        "symbols": symbols,
        "per_symbol": per_symbol_prov,
        "total_shard_bytes": int(total),
        "max_shard_bytes": int(max_shard),
        "real_data_only": True,
        "fabricated_data": False,
        "executed_fills": False,
        "manifest_sha256": manifest_sha,
    }
    prov["meta_sha256"] = sha256_file(DST_META)
    prov["provenance_sha256"] = sha256_bytes(json.dumps(prov, indent=2).encode())
    DST_PROV.write_text(json.dumps(prov, indent=2) + "\n")
    prov_sha = sha256_file(DST_PROV)

    summary = {
        "built": True,
        "campaign": 377,
        "part": "feature_build",
        "symbols": symbols,
        "n_symbols": len(symbols),
        "n_grid_bars": int(len(grid)),
        "total_shard_bytes": int(total),
        "max_shard_bytes": int(max_shard),
        "under_push_limit": meta["under_push_limit"],
        "under_cache_budget": meta["under_cache_budget"],
        "meta_sha256": sha256_file(DST_META),
        "provenance_sha256": prov_sha,
        "manifest_sha256": manifest_sha,
        "real_data_only": True,
        "fabricated_data": False,
        "executed_fills": False,
        "raw_nan_observed": raw_nan_observed,
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
