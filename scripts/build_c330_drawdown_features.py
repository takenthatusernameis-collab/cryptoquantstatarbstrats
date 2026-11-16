#!/usr/bin/env python3
"""C330 feature build — real USDT-M linear perp cross-sectional intraday
RETURN-PATH DRAWDOWN / RUNUP / PATH-EFFICIENCY SEASONAL DISLOCATION mean-reversion
raw inputs.

Reads the REAL, SHA-verified 5m USDT-M kline ``perp_close`` from the C312 USDT-M
OFI cache (``data/cache/campaign312_usdt_m_ofi_5m/<SYM>.npz``), aligns the common
5m grid across all 10 perps, derives the causal log-return
``r[t]=log(c[t]/c[t-1])`` (r[0]=0) and the genuinely-distinct per-bar intraday
PATH fields (all reset at 00:00 UTC, causal, real only):

    data/cache/campaign330_drawdown_5m/<SYM>.npz
        index_ms        int64   common 5m grid (ms)
        perp_close      float32 real 5m kline close (execution price)
        log_return      float32 causal log-return (r[t]=log(c[t]/c[t-1]), r[0]=0)
        cumret          float32 intraday-to-date cumulative log-return since 00:00 UTC
                                (cumret[t] = sum of log_return over the UTC day up to t)
        drawdown        float32 intraday running max drawdown of cumret (<= 0);
                                cumret[t] - max_{j<=t, same UTC day} cumret[j]
        runup           float32 intraday running max rise of cumret (>= 0);
                                cumret[t] - min_{j<=t, same UTC day} cumret[j]
        path_eff        float32 intraday path efficiency = |cumret| / sum_{j<=t}|r_j|
                                in [0,1] (directional signal / noise); NaN where the
                                denominator <= 0
        funding_rate    float32 all-NaN (control only; USDT-M funding unreachable)

plus a meta manifest and a provenance JSON, all SHA256-from-bytes.

C330 is a genuinely-new modern campaign distinct from every executed family:
C316 size/volume/turnover liquidity LEVELS; C317 own realized-vol / higher-moment;
C318 return covariance/beta; C319 price-level cointegration / pairs; C320 intraday
TIME-OF-DAY / DAY-OF-WEEK seasonal RETURN mean-reversion; C321 intraday RANGE /
BREAKOUT / OVERNIGHT-vs-INTRADAY split; C322 intraday VWAP-close fair-value anchor;
C323 causal same-tod ORDER-FLOW & TRADE-ACTIVITY SEASONALITY deviations;
C324 causal same-tod AMIHUD-ILLIQUIDITY SEASONAL DISLOCATION deviations;
C325 cross-sectional intraday AVERAGE TRADE SIZE SEASONAL DISLOCATION mean-reversion;
C326 cross-sectional intraday RETURN AUTOCORRELATION SEASONAL DISLOCATION mean-reversion;
C327 cross-sectional intraday SIGNED JUMP-VARIATION / DISCONTINUITY SEASONAL
DISLOCATION mean-reversion; C328 cross-sectional intraday RETURN SIGN-RUN /
DIRECTIONAL STREAK SEASONAL DISLOCATION mean-reversion; C329 cross-sectional
intraday RETURN SIGN ENTROPY / DIRECTIONAL DISORDER SEASONAL DISLOCATION
mean-reversion. C330 is the FIRST modern campaign to trade each asset's CAUSAL
trailing same-time-of-day seasonal deviation of its OWN intraday RETURN-PATH
DRAWDOWN (peak-to-trough loss within the UTC day), intraday RUNUP (trough-to-peak
gain), and intraday PATH EFFICIENCY (|net move| / |total variation|, a
directional-persistence scalar), then cross-sectionally rank. These path-dependent
extreme / shape measures are DISTINCT from variance (C317), jump variation (C327),
sign entropy (C329), sign-run length (C328), autocorrelation (C326), and
return level (C320).

The RUNNER forms, per asset/bar-of-day bucket over a trailing window of the last
L same-tod occurrences (min_periods=L):
    v = drawdown | runup | path_eff
score = -(v - trailing_mean_L(v at same tod)) so an unusually DEEP drawdown (more
negative than its own same-tod baseline) -> HIGH score (long, expect recovery),
an unusually LARGE runup / high path efficiency -> LOW score (short, expect
pullback / normalization). Causal shift(1); cross-sectional rank; dollar-neutral
gross 1.0.

PRE-REGISTERED zero-activity / NaN POLICY (verbatim):
- denominators/values <= 0 -> NaN (path_eff denominator sum|r| <= 0 -> NaN).
- same-time-of-day trailing stats are NaN-aware with an explicit min_periods
  (min_periods=L seasonal occurrences) and EXCLUDE NaN same-tod observations — do
  NOT forward-fill, do NOT impute, do NOT drop the whole shard, do NOT treat NaN
  as 0.
- The raw cache fields perp_close, log_return, cumret, drawdown, runup carry ZERO
  NaN; path_eff carries NaN only where the intraday sum|r| denominator is 0
  (an exactly-zero return bar at the day open), reported by preflight and required
  to be < 0.1% and 100% explained by zero-absolute-return bars.
- Any asset whose score is NaN at bar t receives cross-sectional weight 0 at t
  (others renormalized to gross 1.0).

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
DST_DIR = ROOT / "data" / "cache" / "campaign330_drawdown_5m"
DST_META = ROOT / "data" / "cache" / "campaign330_drawdown_5m.meta.json"
DST_PROV = ROOT / "data" / "cache" / "campaign330_drawdown_5m.provenance.json"

PUSH_LIMIT_BYTES = 100_000_000
CACHE_BUDGET_BYTES = 100_000_000
BAR_MS = 300_000
TOD_BARS = 288
WINDOW_START = "2023-01"
WINDOW_END = "2025-12"

FIELDS = ["index_ms", "perp_close", "log_return", "cumret", "drawdown", "runup",
          "path_eff", "funding_rate"]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def pd_ts(ms: int) -> str:
    return datetime.fromtimestamp(int(ms) / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S+00:00")


def _content_ok(path: Path) -> bool:
    """Content-level sanity of an existing shard (shape, finiteness, NaN policy)."""
    try:
        with np.load(path) as z:
            if set(z.files) != set(FIELDS):
                return False
            pc = np.asarray(z["perp_close"], dtype=float)
            lr = np.asarray(z["log_return"], dtype=float)
            cumret = np.asarray(z["cumret"], dtype=float)
            dd = np.asarray(z["drawdown"], dtype=float)
            ru = np.asarray(z["runup"], dtype=float)
            pe = np.asarray(z["path_eff"], dtype=float)
            fr = np.asarray(z["funding_rate"], dtype=float)
            idx = np.asarray(z["index_ms"], dtype="int64")
        n = len(idx)
        if not (n > 0 and len(pc) == len(lr) == len(cumret) == len(dd)
                == len(ru) == len(pe) == len(fr) == n):
            return False
        if not (np.isfinite(pc).all() and (pc > 0).all()):
            return False
        for arr in (lr, cumret, dd, ru):
            if not np.isfinite(arr).all():
                return False
        if dd[0] != 0.0:
            return False
        # drawdown <= 0 and runup >= 0 (float32 tolerance)
        if not (dd <= 1e-6).all() or not (ru >= -1e-6).all():
            return False
        if not np.isnan(fr).all():
            return False
        bad = np.isfinite(pe) & ((pe < -1e-6) | (pe > 1.0 + 1e-6))
        if bad.any():
            return False
        return True
    except Exception:  # noqa: BLE001
        return False


def _verify_existing(symbols: list[str]) -> bool:
    """Return True iff every committed shard exists, matches the C330 meta manifest
    SHA/size, and passes content checks — i.e. the cache is a faithful real-data
    derivation already (idempotent no-op)."""
    if not DST_META.exists() or not DST_PROV.exists():
        return False
    try:
        meta = json.loads(DST_META.read_text())
    except Exception:  # noqa: BLE001
        return False
    if int(meta.get("campaign") or 0) != 330:
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

    # ---- verify + load each source shard (fail-closed on SHA/size) ----
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

    # ---- idempotent fast path: existing committed cache already faithful ----
    if not args.force and DST_DIR.exists() and _verify_existing(symbols):
        meta = json.loads(DST_META.read_text())
        summary = {
            "built": False,
            "verified": True,
            "note": "C330 cache already present and faithful (SHA/size/content OK); left untouched.",
            "campaign": 330,
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

        # ---- genuinely-distinct intraday PATH fields (reset at 00:00 UTC) ----
        n = len(grid)
        day_idx = np.arange(n) // TOD_BARS
        starts = np.arange(0, n, TOD_BARS)
        cs = np.cumsum(log_return)
        base = cs[starts] - log_return[starts]
        cumret = cs - base[day_idx]
        run_max = np.empty(n, dtype=np.float64)
        run_min = np.empty(n, dtype=np.float64)
        for d in range(len(starts)):
            sl = slice(starts[d], starts[d] + TOD_BARS)
            seg = cumret[sl]
            run_max[sl] = np.maximum.accumulate(seg)
            run_min[sl] = np.minimum.accumulate(seg)
        drawdown = cumret - run_max
        runup = cumret - run_min
        abs_cs = np.cumsum(np.abs(log_return))
        abs_base = abs_cs[starts] - np.abs(log_return[starts])
        abs_sum = abs_cs - abs_base[day_idx]
        with np.errstate(invalid="ignore", divide="ignore"):
            path_eff = np.where(abs_sum > 0.0, np.abs(cumret) / abs_sum, np.nan)

        funding = np.full(n, np.nan, dtype=np.float64)

        out = {
            "index_ms": grid.astype(np.int64),
            "perp_close": pc.astype(np.float32),
            "log_return": log_return.astype(np.float32),
            "cumret": cumret.astype(np.float32),
            "drawdown": drawdown.astype(np.float32),
            "runup": runup.astype(np.float32),
            "path_eff": path_eff.astype(np.float32),
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
            "log_return_nan": int(np.isnan(log_return).sum()),
            "cumret_nan": int(np.isnan(cumret).sum()),
            "drawdown_nan": int(np.isnan(drawdown).sum()),
            "runup_nan": int(np.isnan(runup).sum()),
            "path_eff_nan": int(np.isnan(path_eff).sum()),
            "path_eff_nan_share": float(np.isnan(path_eff).mean()),
            "zero_abs_return_bars": int((log_return == 0.0).sum()),
            "funding_all_nan": bool(np.isnan(funding).all()),
        }

    manifest = {s: shard_sha256[s] for s in sorted(shard_sha256)}
    manifest_sha = sha256_bytes(json.dumps(manifest, sort_keys=True).encode())

    meta = {
        "generated_at_utc": ts,
        "campaign": 330,
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
            "cumret_drawdown_runup": "intraday path fields reset at 00:00 UTC; always finite",
            "path_eff": "NaN only where intraday sum|r| <= 0 (exactly-zero return bar); <0.1% and 100% explained",
            "runner_nan": "zero-variance/insufficient-obs/min_periods NaNs fail-closed; NaN bars get weight 0",
            "zero_activity_nan_ceiling": 0.001,
            "raw_nan_observed": {s: {
                "log_return": int(np.isnan(np.asarray(np.load(DST_DIR / f"{s}.npz")["log_return"], dtype=float)).sum()),
                "cumret": int(np.isnan(np.asarray(np.load(DST_DIR / f"{s}.npz")["cumret"], dtype=float)).sum()),
                "drawdown": int(np.isnan(np.asarray(np.load(DST_DIR / f"{s}.npz")["drawdown"], dtype=float)).sum()),
                "runup": int(np.isnan(np.asarray(np.load(DST_DIR / f"{s}.npz")["runup"], dtype=float)).sum()),
                "path_eff": int(np.isnan(np.asarray(np.load(DST_DIR / f"{s}.npz")["path_eff"], dtype=float)).sum()),
            } for s in symbols},
        },
    }
    DST_META.write_text(json.dumps(meta, indent=2) + "\n")

    prov = {
        "generated_at_utc": ts,
        "campaign": 330,
        "part": "provenance",
        "source_host": "https://data.binance.vision",
        "note": "C330 features are a read-only derivation of real C312 USDT-M 5m perp_close (log_return plus genuinely-distinct intraday path fields cumret/drawdown/runup/path_eff); no network, no fabrication, no resampling.",
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
        "campaign": 330,
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
        "raw_nan_observed": meta["nan_policy"]["raw_nan_observed"],
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
