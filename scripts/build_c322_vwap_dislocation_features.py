#!/usr/bin/env python3
"""C322 feature build — real USDT-M linear perp cross-sectional VWAP-CLOSE
FAIR-VALUE DISLOCATION mean-reversion raw inputs.

Reads the REAL, SHA-verified 5m USDT-M kline ``perp_close`` AND ``vwap`` fields
from the C312 USDT-M OFI cache (``data/cache/campaign312_usdt_m_ofi_5m/<SYM>.npz``),
aligns the common 5m grid across all 10 perps, derives the causal log-return and
the causal log-VWAP, and writes per-asset C322 feature shards:

    data/cache/campaign322_vwap_dislocation_5m/<SYM>.npz
        index_ms     int64   common 5m grid (ms)
        perp_close   float32 real 5m kline close (execution price)
        log_return   float32 causal log-return (r[t]=log(c[t]/c[t-1]), r[0]=0)
        vwap         float32 real 5m volume-weighted trade price (NaN where total_volume==0)
        log_vwap     float32 log(vwap) where vwap>0, else NaN  (PRE-REGISTERED vwap-NaN POLICY)
        funding_rate float32 all-NaN (control only; USDT-M funding unreachable)

plus a meta manifest and a provenance JSON, all SHA256-from-bytes.

C322 is the FIRST modern campaign to trade each asset's ``perp_close`` vs its
CAUSAL trailing same-time-of-day ``vwap`` (volume-weighted trade price) from
trailing days ONLY, then cross-sectionally ranked. VWAP is a fair-value anchor
never traded by any prior modern campaign: carry/OFI/basis/term-structure/lead-
lag = C281B-C314; price first-moment momentum/reversal = C315; size/volume/
turnover liquidity = C316; own realized-vol / higher-moment = C317; return co-
movement / covariance / beta = C318; price-level cointegration / pairs = C319;
intraday TIME-OF-DAY / DAY-OF-WEEK seasonal RETURN mean-reversion = C320;
intraday RANGE / BREAKOUT / OVERNIGHT-vs-INTRADAY split (close only) = C321.
C322 trades the intraday FAIR-VALUE anchor (own intraday VWAP), a distinct
signal source, not a re-skin.

PRE-REGISTERED vwap-NaN POLICY (measured on disk 2026-11-16T06:39Z, verbatim):
- log_vwap = log(vwap) where vwap>0, else NaN.
- same-time-of-day trailing mean/std/ewm are NaN-aware with an explicit
  min_periods floor and simply EXCLUDE NaN same-tod observations — do NOT
  forward-fill, do NOT impute, do NOT drop the whole shard, do NOT treat NaN as 0.
- any asset whose feature is NaN at bar t receives cross-sectional weight 0 at t
  (others renormalized to gross 1.0) — enforced in the runner, not by imputation.
- preflight asserts per-shard vwap NaN count < 0.1% of bars and 100% of NaNs
  explained by total_volume==0 (fail-closed if a NaN appears where volume>0).

This is a READ-ONLY reuse of real on-disk data — no network, no fabrication, no
resampling, no imputation. Any SHA mismatch vs the C312 source meta BLOCKS the
build (fail-closed). When the destination shards already exist and pass integrity
+ content checks the build is a no-op that leaves the committed bytes untouched
(idempotent), so re-running never churns real on-disk SHAs.
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
DST_DIR = ROOT / "data" / "cache" / "campaign322_vwap_dislocation_5m"
DST_META = ROOT / "data" / "cache" / "campaign322_vwap_dislocation_5m.meta.json"
DST_PROV = ROOT / "data" / "cache" / "campaign322_vwap_dislocation_5m.provenance.json"

PUSH_LIMIT_BYTES = 100_000_000
CACHE_BUDGET_BYTES = 100_000_000
BAR_MS = 300_000
WINDOW_START = "2023-01"
WINDOW_END = "2025-12"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def pd_ts(ms: int) -> str:
    return datetime.fromtimestamp(int(ms) / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S+00:00")


def _content_ok(path: Path) -> bool:
    """Content-level sanity of an existing shard (shape, finiteness, vwap-NaN policy)."""
    try:
        with np.load(path) as z:
            if set(z.files) != {"index_ms", "perp_close", "log_return", "vwap", "log_vwap", "funding_rate"}:
                return False
            pc = np.asarray(z["perp_close"], dtype=float)
            lr = np.asarray(z["log_return"], dtype=float)
            vw = np.asarray(z["vwap"], dtype=float)
            lv = np.asarray(z["log_vwap"], dtype=float)
            fr = np.asarray(z["funding_rate"], dtype=float)
            idx = np.asarray(z["index_ms"], dtype="int64")
        if not (len(idx) == len(pc) == len(lr) == len(vw) == len(lv) == len(fr) and len(idx) > 0):
            return False
        if not (np.isfinite(pc).all() and (pc > 0).all()):
            return False
        if not np.isfinite(lr).all():
            return False
        if not np.isnan(fr).all():
            return False
        # vwap: finite and >0 wherever not NaN; NaN allowed.
        vw_finite = np.isfinite(vw)
        if not ((vw[vw_finite] > 0).all()):
            return False
        # log_vwap NaN exactly where vwap is not (finite and >0); log_vwap finite where vwap>0.
        vwap_ok = vw_finite & (vw > 0)
        expected_lv_nan = ~vwap_ok
        if not np.array_equal(np.isnan(lv), expected_lv_nan):
            return False
        if not np.isfinite(lv[vwap_ok]).all():
            return False
        return True
    except Exception:  # noqa: BLE001
        return False


def _verify_existing(symbols: list[str]) -> bool:
    """Return True iff every committed shard exists, matches the C322 meta manifest
    SHA/size, and passes content checks — i.e. the cache is a faithful real-data
    derivation already (idempotent no-op)."""
    if not DST_META.exists() or not DST_PROV.exists():
        return False
    try:
        meta = json.loads(DST_META.read_text())
    except Exception:  # noqa: BLE001
        return False
    if int(meta.get("campaign") or 0) != 322:
        return False
    if meta.get("real_data_only") is not True or meta.get("fabricated_data") is not False:
        return False
    if meta.get("interval") != "5m" or int(meta.get("source_campaign") or 0) != 312:
        return False
    if list(meta.get("symbols") or []) != list(symbols):
        return False
    shard_sha_meta = meta.get("shard_sha256") or {}
    shard_bytes_meta = meta.get("shard_bytes") or {}
    manifest = {s: shard_sha_meta[s] for s in sorted(shard_sha_meta)}
    if sha256_bytes(json.dumps(manifest, sort_keys=True).encode()) != meta.get("manifest_sha256"):
        return False
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

    # ---- verify + load each source shard (fail-closed on SHA/size) ----
    per_asset: dict[str, dict] = {}
    grid_sets: list[set] = []
    vwap_nan_counts: dict[str, int] = {}
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
            idx_ms = np.asarray(z["index_ms"], dtype="int64")
            pc = np.asarray(z["perp_close"], dtype=np.float64)
            vw = np.asarray(z["vwap"], dtype=np.float64)
            tv = np.asarray(z["total_volume"], dtype=np.float64)
        if not np.isfinite(pc).all() or not (pc > 0).all():
            raise SystemExit(f"FATAL: source perp_close non-finite/non-positive for {s}")
        per_asset[s] = {"index_ms": idx_ms, "perp_close": pc, "vwap": vw, "total_volume": tv}
        grid_sets.append(set(idx_ms.tolist()))
        vwap_nan_counts[s] = int(np.isnan(vw).sum())

    # ---- vwap-NaN policy fail-closed check: 100% of vwap NaNs explained by total_volume==0 ----
    for s in symbols:
        vw = per_asset[s]["vwap"]
        tv = per_asset[s]["total_volume"]
        vw_nan = np.isnan(vw)
        bad = vw_nan & (tv > 0)
        if int(bad.sum()) > 0:
            raise SystemExit(f"FATAL: {s} has {int(bad.sum())} vwap-NaN bars where total_volume>0 (corrupt data)")
        vwap_share = float(vw_nan.mean())
        if vwap_share >= 0.001:
            raise SystemExit(f"FATAL: {s} vwap NaN share {vwap_share:.6f} >= 0.1% (0.001)")

    common = set.intersection(*grid_sets)
    if not common:
        raise SystemExit("FATAL: empty common 5m grid across symbols")
    grid = np.array(sorted(common), dtype=np.int64)
    if len(np.unique(np.diff(grid))) != 1:
        steps, counts = np.unique(np.diff(grid), return_counts=True)
        if int(steps[int(np.argmax(counts))]) != BAR_MS:
            raise SystemExit("FATAL: common grid is not uniformly 5m")

    # ---- idempotent fast path: existing committed cache already faithful ----
    if not args.force and DST_DIR.exists() and _verify_existing(symbols):
        meta = json.loads(DST_META.read_text())
        summary = {
            "built": False,
            "verified": True,
            "note": "C322 cache already present and faithful (SHA/size/content OK); left untouched.",
            "campaign": 322,
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
            "vwap_nan_policy": {s: vwap_nan_counts[s] for s in symbols},
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
        pos = {int(v): i for i, v in enumerate(per_asset[s]["index_ms"].tolist())}

        def align(key):
            arr = per_asset[s][key]
            out = np.empty(len(grid), dtype=np.float64)
            for j, g in enumerate(grid):
                out[j] = arr[pos[int(g)]]
            return out

        pc = align("perp_close")
        vw = align("vwap")

        log_return = np.zeros_like(pc, dtype=np.float64)
        log_return[1:] = np.log(pc[1:] / pc[:-1])
        log_return = np.where(np.isfinite(log_return), log_return, 0.0)

        # PRE-REGISTERED vwap-NaN POLICY: log_vwap = log(vwap) where vwap>0 else NaN.
        log_vwap = np.full_like(pc, np.nan, dtype=np.float64)
        vwap_ok = np.isfinite(vw) & (vw > 0)
        log_vwap[vwap_ok] = np.log(vw[vwap_ok])

        funding = np.full(len(grid), np.nan, dtype=np.float64)

        out = {
            "index_ms": grid.astype(np.int64),
            "perp_close": pc.astype(np.float32),
            "log_return": log_return.astype(np.float32),
            "vwap": vw.astype(np.float32),
            "log_vwap": log_vwap.astype(np.float32),
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
            "source": "campaign312_usdt_m_ofi_5m (perp_close, vwap)",
            "source_sha256": shard_sha_meta.get(s),
            "log_return_nan": int(np.isnan(log_return).sum()),
            "vwap_nan": int(vwap_nan_counts[s]),
            "log_vwap_nan": int((~np.isfinite(log_vwap)).sum()),
            "funding_all_nan": bool(np.isnan(funding).all()),
        }

    manifest = {s: shard_sha256[s] for s in sorted(shard_sha256)}
    manifest_sha = sha256_bytes(json.dumps(manifest, sort_keys=True).encode())

    meta = {
        "generated_at_utc": ts,
        "campaign": 322,
        "part": "feature_build",
        "interval": "5m",
        "bar_ms": BAR_MS,
        "source_interval": "usdt_m_5m_klines_close",
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
        "fields": ["index_ms", "perp_close", "log_return", "vwap", "log_vwap", "funding_rate"],
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
        "funding_source": "unreachable_fapi_451_and_not_in_monthly_archives_nan_control_only",
        "network_ingest": False,
        "resample": False,
        "real_data_only": True,
        "fabricated_data": False,
        "fetch_real_data_only": True,
        "fetch_fabricated_data": False,
        "executed_fills": False,
        "manifest_sha256": manifest_sha,
        "vwap_nan_policy": {s: vwap_nan_counts[s] for s in symbols},
    }
    DST_META.write_text(json.dumps(meta, indent=2) + "\n")

    prov = {
        "generated_at_utc": ts,
        "campaign": 322,
        "part": "provenance",
        "source_host": "https://data.binance.vision",
        "note": "C322 features are a read-only derivation of real C312 USDT-M 5m perp_close + vwap (log_return/log_vwap derived); no network, no fabrication, no resampling.",
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
        "campaign": 322,
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
        "vwap_nan_policy": {s: vwap_nan_counts[s] for s in symbols},
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
