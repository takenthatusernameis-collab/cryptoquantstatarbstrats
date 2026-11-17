#!/usr/bin/env python3
"""C338 feature build — real USDT-M linear perp cross-sectional intraday
ORDER-FLOW ENTROPY / INFORMATION CONTENT / TRADE BURSTINESS SEASONAL DISLOCATION
mean-reversion stat-arb raw inputs.

Reads the REAL, SHA-verified 5m USDT-M kline/flow fields from the C312 USDT-M OFI
cache (data/cache/campaign312_usdt_m_ofi_5m/<SYM>.npz), aligns the common 5m grid
across all 10 perps, and derives genuinely-distinct per-bar order-flow entropy /
information-content / burstiness inputs (real only):

    data/cache/campaign338_orderflow_entropy_5m/<SYM>.npz
        index_ms        int64   common 5m grid (ms)
        perp_close      float32 real 5m kline close (execution price)
        log_return      float32 causal log-return (r[t]=log(c[t]/c[t-1]), r[0]=0)
        imb             float32 per-bar order-flow imbalance
                            = signed_volume / total_volume  (total_volume<=0 -> NaN)
        sign            float32 per-bar order-flow sign
                            = sign(trade_sign_sum)  (trade_count<=0 -> NaN)
        atsv            float32 avg-trade-size proxy = total_volume / trade_count
                            (trade_count<=0 -> NaN); used as inter-trade-intensity proxy
        funding_rate    float32 all-NaN (control only; USDT-M funding unreachable)

plus a meta manifest and a provenance JSON, all SHA256-from-bytes. The raw flow
fields (signed_volume, total_volume, trade_count, trade_sign_sum) are read from
C312 during the build but are NOT stored in the C338 shards (the runner only needs
perp_close, log_return, imb, sign, atsv), which keeps the cache under the 100 MB
budget.

C338 is a genuinely-new modern campaign distinct from every executed family:
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
DISLOCATION; C335 cross-sectional intraday ORDER-FLOW TOXICITY / VPIN SEASONAL
DISLOCATION; C336 cross-sectional intraday ORDER-FLOW PERSISTENCE / IMBALANCE
AUTOCORRELATION SEASONAL DISLOCATION; C337 cross-sectional intraday ORDER-FLOW
SKEW / ASYMMETRIC IMPULSE SEASONAL DISLOCATION.

C338 instead measures information-theoretic and burstiness properties of the
per-bar order-flow imbalance SIGN sequence within each asset's trailing lookback,
vs its own same-(TOD x DOW) seasonal baseline: unusually low entropy / high
burstiness / high information content vs same-bucket history -> expect
mean-reversion of the order-flow regime; score = -seasonal-dislocation. NOT a raw
flow level (C323), NOT a toxicity probability (C335), NOT a persistence measure
(C336), NOT a skew/asymmetry measure (C337). Mechanically distinct.

PER-BAR INPUTS (per bar, causal, real only, fail-closed NaN):
    imb_t         = signed_volume_t / total_volume_t                      (total_volume<=0 -> NaN)
    sign_t        = sign(trade_sign_sum_t)                                (trade_count<=0 -> NaN)
    atsv_t        = total_volume_t / trade_count_t                        (trade_count<=0 -> NaN)

score = -(signal_t - seasonal baseline at same (TOD x DOW) bucket) / seasonal_std;
causal shift(1); cross-sectional rank; dollar-neutral gross 1.0. The runner
parameterizes entropy/burstiness/information metrics over trailing lookbacks
{60,120,240,480,960,1920} bars; this build only stores the per-bar primitives.

PRE-REGISTERED NaN POLICY (verbatim):
- total_volume<=0 -> imb NaN.
- trade_count<=0 -> sign NaN and atsv NaN.
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
DST_DIR = ROOT / "data" / "cache" / "campaign338_orderflow_entropy_5m"
DST_META = ROOT / "data" / "cache" / "campaign338_orderflow_entropy_5m.meta.json"
DST_PROV = ROOT / "data" / "cache" / "campaign338_orderflow_entropy_5m.provenance.json"

PUSH_LIMIT_BYTES = 100_000_000
CACHE_BUDGET_BYTES = 100_000_000
BAR_MS = 300_000
TOD_BARS = 288
WEEKDAYS = 7
N_BUCKETS = WEEKDAYS * TOD_BARS
WINDOW_START = "2023-01"
WINDOW_END = "2025-12"

FIELDS = ["index_ms", "perp_close", "log_return",
          "imb", "sign", "atsv", "funding_rate"]


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
            imb = np.asarray(z["imb"], dtype=float)
            sign = np.asarray(z["sign"], dtype=float)
            atsv = np.asarray(z["atsv"], dtype=float)
            fr = np.asarray(z["funding_rate"], dtype=float)
            idx = np.asarray(z["index_ms"], dtype="int64")
        n = len(idx)
        if not (n > 0 and all(len(a) == n for a in (pc, lr, imb, sign, atsv, fr))):
            return False
        if not (np.isfinite(pc).all() and (pc > 0).all()):
            return False
        if not np.isfinite(lr).all():
            return False
        if not np.isnan(fr).all():
            return False
        return True
    except Exception:  # noqa: BLE001
        return False


def _verify_existing(symbols: list[str]) -> bool:
    """Return True iff every committed shard exists, matches the C338 meta manifest
    SHA/size, and passes content checks (idempotent no-op)."""
    if not DST_META.exists() or not DST_PROV.exists():
        return False
    try:
        meta = json.loads(DST_META.read_text())
    except Exception:  # noqa: BLE001
        return False
    if int(meta.get("campaign") or 0) != 338:
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
            sv = np.asarray(z["signed_volume"], dtype=np.float64)
            tv = np.asarray(z["total_volume"], dtype=np.float64) if "total_volume" in z.files else None
            tc = np.asarray(z["trade_count"], dtype=np.float64) if "trade_count" in z.files else None
            tss = np.asarray(z["trade_sign_sum"], dtype=np.float64) if "trade_sign_sum" in z.files else None
        if not np.isfinite(pc).all() or not (pc > 0).all():
            raise SystemExit(f"FATAL: source perp_close non-finite/non-positive for {s}")
        if not np.isfinite(sv).all():
            raise SystemExit(f"FATAL: source signed_volume non-finite for {s}")
        if tv is None:
            raise SystemExit(f"FATAL: source total_volume missing for {s}")
        if not np.isfinite(tv).all() or not (tv >= 0).all():
            raise SystemExit(f"FATAL: source total_volume non-finite/negative for {s}")
        if tc is None:
            raise SystemExit(f"FATAL: source trade_count missing for {s}")
        if not np.isfinite(tc).all() or not (tc >= 0).all():
            raise SystemExit(f"FATAL: source trade_count non-finite/negative for {s}")
        if tss is None:
            raise SystemExit(f"FATAL: source trade_sign_sum missing for {s}")
        if not np.isfinite(tss).all():
            raise SystemExit(f"FATAL: source trade_sign_sum non-finite for {s}")
        per_asset[s] = {"index_ms": idx_ms, "perp_close": pc,
                        "signed_volume": sv, "total_volume": tv,
                        "trade_count": tc, "trade_sign_sum": tss}
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
            "note": "C338 cache already present and faithful (SHA/size/content OK); left untouched.",
            "campaign": 338,
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
        tss = _align(pa["trade_sign_sum"], pos, grid, direct)

        log_return = np.zeros_like(pc, dtype=np.float64)
        log_return[1:] = np.log(pc[1:] / pc[:-1])
        log_return = np.where(np.isfinite(log_return), log_return, 0.0)

        # order-flow imbalance: signed_volume / total_volume (fail-closed NaN)
        with np.errstate(divide="ignore", invalid="ignore"):
            imb = np.where(tv > 0, sv / np.where(tv > 0, tv, np.nan), np.nan)

        # order-flow sign: sign(trade_sign_sum) (fail-closed NaN)
        sign = np.where(tc > 0, np.sign(tss), np.nan)

        # avg-trade-size proxy (inter-trade-intensity proxy): total_volume / trade_count
        with np.errstate(divide="ignore", invalid="ignore"):
            atsv = np.where(tc > 0, tv / np.where(tc > 0, tc, np.nan), np.nan)

        funding = np.full(len(grid), np.nan, dtype=np.float64)

        out = {
            "index_ms": grid.astype(np.int64),
            "perp_close": pc.astype(np.float32),
            "log_return": log_return.astype(np.float32),
            "imb": imb.astype(np.float32),
            "sign": sign.astype(np.float32),
            "atsv": atsv.astype(np.float32),
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
            "source": "campaign312_usdt_m_ofi_5m (perp_close, signed_volume, total_volume, trade_count, trade_sign_sum)",
            "source_sha256": shard_sha_meta.get(s),
            "log_return_nan": int(np.isnan(log_return).sum()),
            "signed_volume_nan": int(np.isnan(sv).sum()),
            "total_volume_nan": int(np.isnan(tv).sum()),
            "trade_count_nan": int(np.isnan(tc).sum()),
            "trade_sign_sum_nan": int(np.isnan(tss).sum()),
            "imb_nan": int(np.isnan(imb).sum()),
            "sign_nan": int(np.isnan(sign).sum()),
            "atsv_nan": int(np.isnan(atsv).sum()),
            "funding_all_nan": bool(np.isnan(funding).all()),
        }

    manifest = {s: shard_sha256[s] for s in sorted(shard_sha256)}
    manifest_sha = sha256_bytes(json.dumps(manifest, sort_keys=True).encode())

    raw_nan_observed = {}
    for s in symbols:
        with np.load(DST_DIR / f"{s}.npz") as z:
            raw_nan_observed[s] = {
                "imb": int(np.isnan(np.asarray(z["imb"], dtype=float)).sum()),
                "sign": int(np.isnan(np.asarray(z["sign"], dtype=float)).sum()),
                "atsv": int(np.isnan(np.asarray(z["atsv"], dtype=float)).sum()),
            }

    meta = {
        "generated_at_utc": ts,
        "campaign": 338,
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
            "imb=signed_volume/total_volume (total_volume<=0 -> NaN); "
            "sign=sign(trade_sign_sum) (trade_count<=0 -> NaN); "
            "atsv=total_volume/trade_count (trade_count<=0 -> NaN); "
            "runner computes entropy/burstiness/information metrics over trailing "
            "lookback L bars ending at bar t-1 (causal)"
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
            "signed_volume": "real taker buy/sell signed volume from C312; always finite, may be signed/zero",
            "total_volume": "real total volume from C312; always finite, non-negative",
            "trade_count": "real trade count from C312; always finite, non-negative",
            "trade_sign_sum": "real signed trade count from C312; always finite, signed",
            "imb": "signed_volume/total_volume; total_volume<=0 -> NaN (fail-closed)",
            "sign": "sign(trade_sign_sum); trade_count<=0 -> NaN (fail-closed)",
            "atsv": "total_volume/trade_count; trade_count<=0 -> NaN (fail-closed)",
            "runner_nan": "trailing same-bucket seasonal stats NaN-aware min_periods excluding NaN obs; NaN-score bars weight 0",
            "raw_nan_observed": raw_nan_observed,
        },
    }
    DST_META.write_text(json.dumps(meta, indent=2) + "\n")

    prov = {
        "generated_at_utc": ts,
        "campaign": 338,
        "part": "provenance",
        "source_host": "https://data.binance.vision",
        "note": "C338 features are a read-only derivation of real C312 USDT-M 5m perp_close, signed_volume, total_volume, trade_count, trade_sign_sum (log_return plus per-bar imbalance/sign/avg-trade-size primitives); raw flow fields are read at build time but not stored in shards; no network, no fabrication, no resampling.",
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
        "campaign": 338,
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
