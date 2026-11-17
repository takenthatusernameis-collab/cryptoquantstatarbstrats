#!/usr/bin/env python3
"""C342 feature build — real USDT-M linear perp cross-sectional intraday
VOLUME-WEIGHTED RETURN SKEWNESS/KURTOSIS SEASONAL DISLOCATION mean-reversion
stat-arb raw inputs.

Reads the REAL, SHA-verified 5m USDT-M kline/flow fields from the C312 USDT-M OFI
cache (data/cache/campaign312_usdt_m_ofi_5m/<SYM>.npz), aligns the common 5m grid
across all 10 perps, and stores genuinely-distinct per-bar raw inputs (real only):

    data/cache/campaign342_vol_weighted_return_moments_5m/<SYM>.npz
        index_ms        int64   common 5m grid (ms)
        perp_close      float32 real 5m kline close (execution price)
        log_return      float32 causal log-return (r[t]=log(c[t]/c[t-1]), r[0]=0)
        total_volume    float32 real per-bar total volume (USDT-M)
        notional        float32 real per-bar notional volume
        trade_count     float32 real per-bar trade count
        signed_volume   float32 real per-bar signed volume (buy - sell)
        funding_rate    float32 all-NaN (control only; USDT-M funding unreachable)

plus a meta manifest and a provenance JSON, all SHA256-from-bytes. The raw fields
are read from C312 during the build but stored in the C342 shards so the runner can
derive per-bar volume-weighted return vw_ret_t = log_return_t * sqrt(notional_t)
and its sample skewness / excess kurtosis over trailing lookbacks. Cache stays
under the 100 MB budget.

C342 is a genuinely-new modern campaign distinct from every executed family:
C316 size/volume/turnover liquidity LEVELS; C317 own realized-vol / higher-moment;
C318 return covariance/beta CROSS-ASSET co-movement; C319 price-level
cointegration / pairs; C320 intraday TIME-OF-DAY / DAY-OF-WEEK seasonal RETURN
mean-reversion; C321 intraday RANGE / BREAKOUT / OVERNIGHT-vs-INTRADAY split;
C322 intraday VWAP-close fair-value anchor; C323 causal same-tod ORDER-FLOW &
TRADE-ACTIVITY SEASONALITY LEVEL deviations; C324 causal same-tod AMIHUD-ILLIQUIDITY
SEASONAL DISLOCATION LEVEL; C325 cross-sectional intraday AVERAGE TRADE SIZE
SEASONAL DISLOCATION; C326 cross-sectional intraday RETURN AUTOCORRELATION
SEASONAL DISLOCATION; C327 cross-sectional intraday SIGNED JUMP-VARIATION
SEASONAL DISLOCATION; C328 cross-sectional intraday RETURN SIGN-RUN SEASONAL
DISLOCATION; C329 cross-sectional intraday RETURN SIGN ENTROPY SEASONAL
DISLOCATION; C330 cross-sectional intraday RETURN-PATH DRAWDOWN/RUNUP/PATH-EFFICIENCY
SEASONAL DISLOCATION; C331 cross-sectional intraday RETURN TAIL-ASYMMETRY /
QUANTILE-SPREAD SEASONAL DISLOCATION; C332 cross-sectional intraday
RETURN-SIGNED-VOLUME CORRELATION SEASONAL DISLOCATION; C333 cross-sectional
intraday MICROSTRUCTURE NOISE & EFFECTIVE SPREAD SEASONAL DISLOCATION;
C334 cross-sectional intraday KYLE'S LAMBDA / PRICE-IMPACT COEFFICIENT SEASONAL
DISLOCATION (LEVEL of sum(r*f)/sum(f^2)); C335 cross-sectional intraday
ORDER-FLOW TOXICITY / VPIN SEASONAL DISLOCATION; C336 cross-sectional intraday
ORDER-FLOW PERSISTENCE / IMBALANCE AUTOCORRELATION SEASONAL DISLOCATION;
C337 cross-sectional intraday ORDER-FLOW SKEW / ASYMMETRIC IMPULSE SEASONAL
DISLOCATION; C338 cross-sectional intraday ORDER-FLOW ENTROPY / INFORMATION
CONTENT / TRADE BURSTINESS SEASONAL DISLOCATION; C341 cross-sectional intraday
PRICE IMPACT DISPERSION / VOLUME-WEIGHTED RETURN VOLATILITY SEASONAL DISLOCATION
(pi=|r|/max(|sv|,eps), pid=CV(pi), vwvol=sqrt(sum(v*r^2)/sum(v))); C340 cross-sectional intraday
TRADING-ACTIVITY DISPERSION / VOLUME-OF-ACTIVITY SEASONAL DISLOCATION
(coefficient-of-variation of per-bar activity MAGNITUDE: volume, notional,
|signed_volume|, trade_count).

C342 instead trades each asset's CAUSAL trailing same-(TOD x DOW) seasonal
deviation of its OWN volume-weighted return HIGHER MOMENTS — sample skewness
and excess kurtosis of vw_ret_t = log_return_t * sqrt(notional_t) over trailing
lookback bars — vs its own same-bucket baseline, score = -seasonal-dislocation.
It is NOT a level (C316/C323/C324/C325), NOT a return moment (C317), NOT
sign-sequence burstiness (C338/C329), NOT Kyle's lambda level (C334), NOT
price-impact dispersion / vwvol (C341), NOT activity-magnitude CV (C340).
Mechanically distinct: trades the third and fourth moments of volume-weighted
returns, not first-moment price impact or activity magnitude dispersion.

PER-BAR INPUTS (per bar, causal, real only, fail-closed NaN):
    perp_close_t   real 5m kline close (always finite, strictly positive)
    log_return_t   causal log-return (always finite from real perp_close; r[0]=0)
    notional_t     real per-bar notional volume (finite, non-negative; NaN if <= 0)
    total_volume_t real per-bar total volume (finite, non-negative)
    trade_count_t  real per-bar trade count (finite, non-negative)
    signed_volume_t real per-bar signed volume (finite, may be signed/zero)

score = -(signal_t - seasonal baseline at same (TOD x DOW) bucket) / seasonal_std;
causal shift(1); cross-sectional rank; dollar-neutral gross 1.0. The runner
parameterizes skewness / excess kurtosis metrics over trailing lookbacks
{60,120,240,480,960,1920} bars; this build only stores the per-bar primitives.

PRE-REGISTERED NaN POLICY (verbatim):
- perp_close<=0 or non-finite -> runner NaN (fail-closed).
- log_return non-finite -> runner NaN (should never happen from real perp_close).
- notional<=0 -> vw_ret undefined -> runner NaN.
- std(vw_ret)<=0 or insufficient finite obs in window -> runner NaN.
- same-(TOD x DOW) bucket trailing stats are NaN-aware with explicit min_periods
  and EXCLUDE NaN same-bucket observations — no ffill, no impute, no shard drop,
  never treat NaN as 0.
- perp_close and log_return carry ZERO NaN; funding_rate all-NaN control.
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
DST_DIR = ROOT / "data" / "cache" / "campaign342_vol_weighted_return_moments_5m"
DST_META = ROOT / "data" / "cache" / "campaign342_vol_weighted_return_moments_5m.meta.json"
DST_PROV = ROOT / "data" / "cache" / "campaign342_vol_weighted_return_moments_5m.provenance.json"

PUSH_LIMIT_BYTES = 100_000_000
CACHE_BUDGET_BYTES = 100_000_000
BAR_MS = 300_000
TOD_BARS = 288
WEEKDAYS = 7
N_BUCKETS = WEEKDAYS * TOD_BARS
WINDOW_START = "2023-01"
WINDOW_END = "2025-12"

FIELDS = ["index_ms", "perp_close", "log_return",
          "total_volume", "notional", "trade_count", "signed_volume", "funding_rate"]


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
            idx = np.asarray(z["index_ms"], dtype="int64")
            pc = np.asarray(z["perp_close"], dtype=float)
            lr = np.asarray(z["log_return"], dtype=float)
            tv = np.asarray(z["total_volume"], dtype=float)
            nt = np.asarray(z["notional"], dtype=float)
            tc = np.asarray(z["trade_count"], dtype=float)
            sv = np.asarray(z["signed_volume"], dtype=float)
            fr = np.asarray(z["funding_rate"], dtype=float)
        n = len(idx)
        if not (n > 0 and all(len(a) == n for a in (pc, lr, tv, nt, tc, sv, fr))):
            return False
        if not (np.isfinite(pc).all() and (pc > 0).all()):
            return False
        if not np.isfinite(lr).all():
            return False
        if not np.isfinite(sv).all():
            return False
        if not np.isfinite(tv).all() or not (tv >= 0).all():
            return False
        if not np.isfinite(nt).all() or not (nt >= 0).all():
            return False
        if not np.isfinite(tc).all() or not (tc >= 0).all():
            return False
        if not np.isnan(fr).all():
            return False
        return True
    except Exception:  # noqa: BLE001
        return False


def _verify_existing(symbols: list[str]) -> bool:
    """Return True iff every committed shard exists, matches the C342 meta manifest
    SHA/size, and passes content checks (idempotent no-op)."""
    if not DST_META.exists() or not DST_PROV.exists():
        return False
    try:
        meta = json.loads(DST_META.read_text())
    except Exception:  # noqa: BLE001
        return False
    if int(meta.get("campaign") or 0) != 342:
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

    REQUIRED_SRC_FIELDS = ("index_ms", "perp_close", "signed_volume", "total_volume", "trade_count", "notional")
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
            missing = [f for f in REQUIRED_SRC_FIELDS if f not in z.files]
            if missing:
                raise SystemExit(f"FATAL: source shard {s} missing fields: {missing}")
            idx_ms = np.asarray(z["index_ms"], dtype=np.int64)
            pc = np.asarray(z["perp_close"], dtype=np.float64)
            sv = np.asarray(z["signed_volume"], dtype=np.float64)
            tv = np.asarray(z["total_volume"], dtype=np.float64)
            tc = np.asarray(z["trade_count"], dtype=np.float64)
            nt = np.asarray(z["notional"], dtype=np.float64)
        if not np.isfinite(pc).all() or not (pc > 0).all():
            raise SystemExit(f"FATAL: source perp_close non-finite/non-positive for {s}")
        if not np.isfinite(sv).all():
            raise SystemExit(f"FATAL: source signed_volume non-finite for {s}")
        if not np.isfinite(tv).all() or not (tv >= 0).all():
            raise SystemExit(f"FATAL: source total_volume non-finite/negative for {s}")
        if not np.isfinite(tc).all() or not (tc >= 0).all():
            raise SystemExit(f"FATAL: source trade_count non-finite/negative for {s}")
        if not np.isfinite(nt).all() or not (nt >= 0).all():
            raise SystemExit(f"FATAL: source notional non-finite/negative for {s}")
        per_asset[s] = {"index_ms": idx_ms, "perp_close": pc,
                        "signed_volume": sv, "total_volume": tv,
                        "trade_count": tc, "notional": nt}
        grid_sets.append(set(idx_ms.tolist()))

    common = set.intersection(*grid_sets)
    if not common:
        raise SystemExit("FATAL: empty common 5m grid across symbols")
    grid = np.array(sorted(common), dtype=np.int64)
    if len(np.unique(np.diff(grid))) != 1:
        steps, counts = np.unique(np.diff(grid), return_counts=True)
        if int(steps[int(np.argmax(counts))]) != BAR_MS:
            raise SystemExit("FATAL: common grid is not uniformly 5m")

    # ---- idempotent fast path ----
    if not args.force and DST_DIR.exists() and _verify_existing(symbols):
        meta = json.loads(DST_META.read_text())
        summary = {
            "built": False,
            "verified": True,
            "note": "C342 cache already present and faithful (SHA/size/content OK); left untouched.",
            "campaign": 342,
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
        sv = _align(pa["signed_volume"], pos, grid, direct)
        tv = _align(pa["total_volume"], pos, grid, direct)
        tc = _align(pa["trade_count"], pos, grid, direct)
        nt = _align(pa["notional"], pos, grid, direct)

        log_return = np.zeros_like(pc, dtype=np.float64)
        log_return[1:] = np.log(pc[1:] / pc[:-1])
        log_return = np.where(np.isfinite(log_return), log_return, 0.0)

        funding = np.full(len(grid), np.nan, dtype=np.float64)

        out = {
            "index_ms": grid.astype(np.int64),
            "perp_close": pc.astype(np.float32),
            "log_return": log_return.astype(np.float32),
            "total_volume": tv.astype(np.float32),
            "notional": nt.astype(np.float32),
            "trade_count": tc.astype(np.float32),
            "signed_volume": sv.astype(np.float32),
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
            "source": "campaign312_usdt_m_ofi_5m (perp_close, signed_volume, total_volume, trade_count, notional)",
            "source_sha256": shard_sha_meta.get(s),
            "perp_close_nan": int(np.isnan(pc).sum()),
            "log_return_nan": int(np.isnan(log_return).sum()),
            "total_volume_nan": int(np.isnan(tv).sum()),
            "notional_nan": int(np.isnan(nt).sum()),
            "trade_count_nan": int(np.isnan(tc).sum()),
            "signed_volume_nan": int(np.isnan(sv).sum()),
            "funding_all_nan": bool(np.isnan(funding).all()),
        }

    manifest = {s: shard_sha256[s] for s in sorted(shard_sha256)}
    manifest_sha = sha256_bytes(json.dumps(manifest, sort_keys=True).encode())

    raw_nan_observed = {}
    for s in symbols:
        with np.load(DST_DIR / f"{s}.npz") as z:
            raw_nan_observed[s] = {
                "total_volume": int(np.isnan(np.asarray(z["total_volume"], dtype=float)).sum()),
                "notional": int(np.isnan(np.asarray(z["notional"], dtype=float)).sum()),
                "trade_count": int(np.isnan(np.asarray(z["trade_count"], dtype=float)).sum()),
                "signed_volume": int(np.isnan(np.asarray(z["signed_volume"], dtype=float)).sum()),
                "log_return": int(np.isnan(np.asarray(z["log_return"], dtype=float)).sum()),
            }

    meta = {
        "generated_at_utc": ts,
        "campaign": 342,
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
        "field_definition": (
            "total_volume, notional, trade_count, signed_volume: real per-bar "
            "trading-activity magnitudes from C312 (all 0-NaN verified); "
            "log_return=log(c[t]/c[t-1]) (r[0]=0) derived from perp_close; "
            "runner derives volume-weighted return vw_ret_t=log_return_t*sqrt(notional_t) "
            "(NaN when notional<=0) and its sample skewness / excess kurtosis over "
            "trailing lookback L bars ending at bar t-1 (causal), NaN where "
            "std<=0 or insufficient finite obs."
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
            "notional": "real notional from C312; always finite, non-negative; runner NaN where notional<=0 (vw_ret undefined)",
            "total_volume": "real total volume from C312; always finite, non-negative",
            "trade_count": "real trade count from C312; always finite, non-negative",
            "signed_volume": "real signed volume from C312; always finite, may be signed/zero",
            "runner_nan": "trailing same-bucket seasonal stats NaN-aware min_periods excluding NaN obs; NaN-score bars weight 0",
            "raw_nan_observed": raw_nan_observed,
        },
    }
    DST_META.write_text(json.dumps(meta, indent=2) + "\n")

    prov = {
        "generated_at_utc": ts,
        "campaign": 342,
        "part": "provenance",
        "source_host": "https://data.binance.vision",
        "note": "C342 features are a read-only derivation of real C312 USDT-M 5m perp_close, signed_volume, total_volume, trade_count, notional (volume-weighted return skewness/kurtosis metrics derived in runner); log_return derived from perp_close; no network, no fabrication, no resampling.",
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
        "campaign": 342,
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
