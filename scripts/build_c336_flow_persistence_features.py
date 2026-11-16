#!/usr/bin/env python3
"""C336 feature build — real USDT-M linear perp cross-sectional intraday
ORDER-FLOW PERSISTENCE / IMBALANCE AUTOCORRELATION SEASONAL DISLOCATION
mean-reversion raw inputs.

Reads the REAL, SHA-verified 5m USDT-M kline fields from the C312 USDT-M OFI
cache (data/cache/campaign312_usdt_m_ofi_5m/<SYM>.npz), aligns the common
5m grid across all 10 perps, and derives genuinely-distinct per-bar
order-flow PERSISTENCE / imbalance-autocorrelation inputs (real only) that are
NOT raw flow levels:

    data/cache/campaign336_flow_persistence_5m/<SYM>.npz
        index_ms        int64   common 5m grid (ms)
        perp_close      float32 real 5m kline close (execution price)
        log_return      float32 causal log-return (r[t]=log(c[t]/c[t-1]), r[0]=0)
        sign_imbalance  float32 per-bar order-flow sign imbalance
                                = trade_sign_sum / trade_count  (trade_count<=0 -> NaN)
        signed_vol_share float32 per-bar signed-volume share
                                = signed_volume / total_volume  (total_volume<=0 -> NaN)
        notional_imb     float32 per-bar notional imbalance ratio
                                = signed_volume / notional  (notional<=0 -> NaN)
        imb_ewm          float32 EWMA of sign_imbalance (halflife 24 bars;
                                NaN warmup >= 24 finite obs; no ffill/impute)
        imb_ac1          float32 rolling lag-1 autocorrelation of sign_imbalance
                                over trailing AC1_WINDOW=288 bars (causal; fully-finite
                                window required, else NaN; zero-variance -> NaN)
        streak_len       float32 current run-length of consecutive same-sign
                                trade_sign_sum (streak-length proxy; invalid bars -> NaN)
        funding_rate    float32 all-NaN (control only; USDT-M funding unreachable)

plus a meta manifest and a provenance JSON, all SHA256-from-bytes. The raw flow
fields (trade_sign_sum, trade_count, signed_volume, total_volume, notional) are
read from C312 during the build but are NOT stored in the C336 shards (the
runner only needs perp_close, log_return and the persistence features), which
keeps the cache under the 100 MB budget.

C336 is a genuinely-new modern campaign distinct from every executed family:
C316 size/volume/turnover liquidity LEVELS; C317 own realized-vol / higher-moment;
C318 return covariance/beta CROSS-ASSET co-movement; C319 price-level
cointegration / pairs; C320 intraday TIME-OF-DAY / DAY-OF-WEEK seasonal RETURN
mean-reversion; C321 intraday RANGE / BREAKOUT / OVERNIGHT-vs-INTRADAY split;
C322 intraday VWAP-close fair-value anchor; C323 causal same-tod ORDER-FLOW &
TRADE-ACTIVITY SEASONALITY LEVEL deviations (raw OFI / trade-sign-sum / count /
notional); C324 causal same-tod AMIHUD-ILLIQUIDITY SEASONAL DISLOCATION LEVEL
(|r|/notional); C325 cross-sectional intraday AVERAGE TRADE SIZE SEASONAL
DISLOCATION; C326 cross-sectional intraday RETURN AUTOCORRELATION SEASONAL
DISLOCATION; C327 cross-sectional intraday SIGNED JUMP-VARIATION SEASONAL
DISLOCATION; C328 cross-sectional intraday RETURN SIGN-RUN SEASONAL DISLOCATION;
C329 cross-sectional intraday RETURN SIGN ENTROPY SEASONAL DISLOCATION; C330
cross-sectional intraday RETURN-PATH DRAWDOWN/RUNUP/PATH-EFFICIENCY SEASONAL
DISLOCATION; C331 cross-sectional intraday RETURN TAIL-ASYMMETRY /
QUANTILE-SPREAD SEASONAL DISLOCATION; C332 cross-sectional intraday
RETURN-SIGNED-VOLUME CORRELATION SEASONAL DISLOCATION; C333 cross-sectional
intraday MICROSTRUCTURE NOISE & EFFECTIVE SPREAD SEASONAL DISLOCATION;
C334 cross-sectional intraday KYLE'S LAMBDA / PRICE-IMPACT COEFFICIENT SEASONAL
DISLOCATION; C335 cross-sectional intraday ORDER-FLOW TOXICITY / VPIN
SEASONAL DISLOCATION (informed-trading PROBABILITY estimators).

C332 measures return-vs-flow SYNCHRONY; C335 measures order-flow TOXICITY
PROBABILITY (|buy-sell|/volume). C336 instead measures ORDER-FLOW PERSISTENCE:
the degree to which the imbalance state (sign imbalance, signed-volume share,
notional imbalance) and its autocorrelation/streak structure persist relative
to their own same-(TOD x DOW) seasonal baseline. Persistence is a
mean-reversion-of-regime concept (unusually persistent imbalance -> expect
persistence decay), NOT a raw flow level (C323) and NOT a toxicity probability
(C335). Mechanically distinct.

PERSISTENCE INPUTS (per bar, causal, real only):
    sign_imbalance   = trade_sign_sum / trade_count                      (trade_count<=0 -> NaN)
    signed_vol_share = signed_volume / total_volume                      (total_volume<=0 -> NaN)
    notional_imb     = signed_volume / notional                          (notional<=0 -> NaN)
    imb_ewm          = EWMA(sign_imbalance, halflife=24 bars)            (NaN warmup)
    imb_ac1          = rolling lag-1 autocorr of sign_imbalance over 288 bars (NaN if
                       any bar in the window is invalid / zero variance)
    streak_len       = run-length of consecutive same-sign trade_sign_sum (NaN if invalid)

score = -(v - trailing seasonal mean of v at same (TOD x DOW) bucket); causal
shift(1); cross-sectional rank; dollar-neutral gross 1.0. An unusually HIGH
persistence vs its own same-bucket baseline -> LOW score (short, expect
persistence decay / mean-reversion of the imbalance regime); unusually LOW
persistence -> HIGH score (long).

PRE-REGISTERED NaN POLICY (verbatim):
- trade_count<=0 -> sign_imbalance NaN; total_volume<=0 -> signed_vol_share NaN;
  notional<=0 -> notional_imb NaN.
- imb_ewm EWMA NaN until >= 24 finite sign_imbalance obs accumulate; NaN inputs
  excluded from the EWMA (no ffill, no impute, never 0).
- imb_ac1 NaN if any bar in the trailing 288-bar window is invalid (non-finite
  sign_imbalance) or the window has zero variance (fail-closed).
- streak_len NaN at bars where sign is undefined (trade_count<=0).
- same-(TOD x DOW) bucket trailing stats are NaN-aware with explicit min_periods
  and EXCLUDE NaN same-bucket observations — do NOT forward-fill, do NOT impute,
  do NOT drop the whole shard, do NOT treat NaN as 0.
- The raw cache fields perp_close and log_return carry ZERO NaN; funding_rate
  all-NaN control.
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
DST_DIR = ROOT / "data" / "cache" / "campaign336_flow_persistence_5m"
DST_META = ROOT / "data" / "cache" / "campaign336_flow_persistence_5m.meta.json"
DST_PROV = ROOT / "data" / "cache" / "campaign336_flow_persistence_5m.provenance.json"

PUSH_LIMIT_BYTES = 100_000_000
CACHE_BUDGET_BYTES = 100_000_000
BAR_MS = 300_000
TOD_BARS = 288
WEEKDAYS = 7
N_BUCKETS = WEEKDAYS * TOD_BARS
WINDOW_START = "2023-01"
WINDOW_END = "2025-12"

# EWMA halflife in bars for the imbalance persistence proxy (24 * 5m = 2h).
HALFLIFE_BARS = 24
MIN_PERIODS_EWM = HALFLIFE_BARS
# Rolling lag-1 autocorrelation window (288 bars = 1 UTC day).
AC1_WINDOW = TOD_BARS
AC1_MIN_PERIODS = AC1_WINDOW  # require the full trailing window to be valid

FIELDS = ["index_ms", "perp_close", "log_return",
          "sign_imbalance", "signed_vol_share", "notional_imb",
          "imb_ewm", "imb_ac1", "streak_len", "funding_rate"]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def pd_ts(ms: int) -> str:
    return datetime.fromtimestamp(int(ms) / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S+00:00")


def _ewma_nan_aware(x: np.ndarray, halflife: float, min_periods: int) -> np.ndarray:
    """Stable causal EWMA over finite x: out[t] = sum_k w_k x_{t-k} / sum_k w_k over
    the finite observations at/before t, w_k=(1-alpha)^k, alpha=1-exp(-ln2/halflife);
    NaN until >= min_periods finite obs (fail-closed warmup)."""
    n = len(x)
    out = np.full(n, np.nan, dtype=np.float64)
    alpha = 1.0 - np.exp(-np.log(2.0) / float(halflife))
    decay = 1.0 - alpha
    num = 0.0
    den = 0.0
    cnt = 0
    for t in range(n):
        num *= decay
        den *= decay
        v = x[t]
        if np.isfinite(v):
            num += v
            den += 1.0
            cnt += 1
            if cnt >= min_periods and den > 0:
                out[t] = num / den
    return out


def _ewma_nan_aware_simple(x: np.ndarray, halflife: float, min_periods: int) -> np.ndarray:
    """Alias kept for runner import stability."""
    return _ewma_nan_aware(x, halflife, min_periods)


def _streak_len(sign: np.ndarray) -> np.ndarray:
    """Causal run-length of consecutive equal finite signs; NaN where sign is
    undefined (trade_count<=0). sign(0)=0 counts as its own sign."""
    n = len(sign)
    out = np.full(n, np.nan, dtype=np.float64)
    cur = 0.0
    prev = np.nan
    for t in range(n):
        s = sign[t]
        if np.isfinite(s):
            if np.isfinite(prev) and s == prev:
                cur += 1.0
            else:
                cur = 1.0
            out[t] = cur
            prev = s
        else:
            cur = 0.0
            prev = np.nan
    return out


def _rolling_ac1(x: np.ndarray, window: int) -> np.ndarray:
    """Rolling lag-1 autocorrelation of x over the trailing ``window`` bars ending
    at t (inclusive), computed causally. NaN unless the full window x[t-w+1..t] is
    finite and the window has nonzero variance (fail-closed)."""
    n = len(x)
    out = np.full(n, np.nan, dtype=np.float64)
    if n < window:
        return out
    xf = np.where(np.isfinite(x), x, 0.0)
    fin = np.isfinite(x).astype(float)
    csx = np.concatenate([[0.0], np.cumsum(xf)])
    csx2 = np.concatenate([[0.0], np.cumsum(xf * xf)])
    csf = np.concatenate([[0.0], np.cumsum(fin)])
    p = np.zeros(n, dtype=np.float64)
    pf = np.zeros(n, dtype=np.float64)
    p[1:] = xf[:-1] * xf[1:]
    pf[1:] = (np.isfinite(x[:-1]) & np.isfinite(x[1:])).astype(float)
    csp = np.concatenate([[0.0], np.cumsum(p)])
    cspf = np.concatenate([[0.0], np.cumsum(pf)])

    t_idx = np.arange(window - 1, n)
    a = t_idx - window + 1  # window start index (inclusive)
    np_ = window - 1  # number of lag-1 pairs in the window
    # require every element of the window x[a..t] finite
    full = (csf[t_idx + 1] - csf[a]) == window
    Sx = csx[t_idx] - csx[a]            # sum x[a..t-1]
    Sy = csx[t_idx + 1] - csx[a + 1]    # sum x[a+1..t]
    Sx2 = csx2[t_idx] - csx2[a]         # sum x[a..t-1]^2
    Sy2 = csx2[t_idx + 1] - csx2[a + 1] # sum x[a+1..t]^2
    Sxy = csp[t_idx] - csp[a]           # sum x[a..t-1]*x[a+1..t]
    numer = np_ * Sxy - Sx * Sy
    denom1 = np_ * Sx2 - Sx * Sx
    denom2 = np_ * Sy2 - Sy * Sy
    denom = np.sqrt(np.maximum(denom1, 0.0) * np.maximum(denom2, 0.0))
    with np.errstate(divide="ignore", invalid="ignore"):
        ac1 = np.where(denom > 0, numer / np.where(denom > 0, denom, np.nan), np.nan)
    out[t_idx] = np.where(full & (denom > 0), ac1, np.nan)
    return out


def _content_ok(path: Path) -> bool:
    """Content-level sanity of an existing shard (shape, finiteness, NaN policy)."""
    try:
        with np.load(path) as z:
            if set(z.files) != set(FIELDS):
                return False
            pc = np.asarray(z["perp_close"], dtype=float)
            lr = np.asarray(z["log_return"], dtype=float)
            si = np.asarray(z["sign_imbalance"], dtype=float)
            svs = np.asarray(z["signed_vol_share"], dtype=float)
            ni = np.asarray(z["notional_imb"], dtype=float)
            ie = np.asarray(z["imb_ewm"], dtype=float)
            ia = np.asarray(z["imb_ac1"], dtype=float)
            sl = np.asarray(z["streak_len"], dtype=float)
            fr = np.asarray(z["funding_rate"], dtype=float)
            idx = np.asarray(z["index_ms"], dtype="int64")
        n = len(idx)
        if not (n > 0 and all(len(a) == n for a in (pc, lr, si, svs, ni, ie, ia, sl, fr))):
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
    """Return True iff every committed shard exists, matches the C336 meta manifest
    SHA/size, and passes content checks (idempotent no-op)."""
    if not DST_META.exists() or not DST_PROV.exists():
        return False
    try:
        meta = json.loads(DST_META.read_text())
    except Exception:  # noqa: BLE001
        return False
    if int(meta.get("campaign") or 0) != 336:
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
            no = np.asarray(z["notional"], dtype=np.float64)
            sv = np.asarray(z["signed_volume"], dtype=np.float64)
            tv = np.asarray(z["total_volume"], dtype=np.float64) if "total_volume" in z.files else None
            tc = np.asarray(z["trade_count"], dtype=np.float64) if "trade_count" in z.files else None
            tss = np.asarray(z["trade_sign_sum"], dtype=np.float64) if "trade_sign_sum" in z.files else None
        if not np.isfinite(pc).all() or not (pc > 0).all():
            raise SystemExit(f"FATAL: source perp_close non-finite/non-positive for {s}")
        if not np.isfinite(no).all() or not (no >= 0).all():
            raise SystemExit(f"FATAL: source notional non-finite/negative for {s}")
        if not np.isfinite(sv).all():
            raise SystemExit(f"FATAL: source signed_volume non-finite for {s}")
        if tv is None:
            raise SystemExit(f"FATAL: source total_volume missing for {s}")
        if tc is None:
            raise SystemExit(f"FATAL: source trade_count missing for {s}")
        if tss is None:
            raise SystemExit(f"FATAL: source trade_sign_sum missing for {s}")
        per_asset[s] = {"index_ms": idx_ms, "perp_close": pc,
                        "notional": no, "signed_volume": sv,
                        "total_volume": tv, "trade_count": tc,
                        "trade_sign_sum": tss}
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
            "note": "C336 cache already present and faithful (SHA/size/content OK); left untouched.",
            "campaign": 336,
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
        no = _align(pa["notional"], pos, grid, direct)
        sv = _align(pa["signed_volume"], pos, grid, direct)
        tv = _align(pa["total_volume"], pos, grid, direct)
        tc = _align(pa["trade_count"], pos, grid, direct)
        tss = _align(pa["trade_sign_sum"], pos, grid, direct)

        log_return = np.zeros_like(pc, dtype=np.float64)
        log_return[1:] = np.log(pc[1:] / pc[:-1])
        log_return = np.where(np.isfinite(log_return), log_return, 0.0)

        # order-flow sign imbalance: trade_sign_sum / trade_count
        with np.errstate(divide="ignore", invalid="ignore"):
            sign_imbalance = np.where(tc > 0, tss / np.where(tc > 0, tc, np.nan), np.nan)
        sign = np.where(tc > 0, np.sign(tss), np.nan)

        # signed-volume share: signed_volume / total_volume
        with np.errstate(divide="ignore", invalid="ignore"):
            signed_vol_share = np.where(tv > 0, sv / np.where(tv > 0, tv, np.nan), np.nan)

        # notional imbalance ratio: signed_volume / notional
        with np.errstate(divide="ignore", invalid="ignore"):
            notional_imb = np.where(no > 0, sv / np.where(no > 0, no, np.nan), np.nan)

        # EWMA persistence of sign imbalance (halflife 24 bars)
        imb_ewm = _ewma_nan_aware(sign_imbalance, HALFLIFE_BARS, MIN_PERIODS_EWM)

        # rolling lag-1 autocorrelation of sign imbalance (288 bars)
        imb_ac1 = _rolling_ac1(sign_imbalance, AC1_WINDOW)

        # streak-length proxy: run-length of consecutive same-sign trade_sign_sum
        streak_len = _streak_len(sign)

        funding = np.full(len(grid), np.nan, dtype=np.float64)

        out = {
            "index_ms": grid.astype(np.int64),
            "perp_close": pc.astype(np.float32),
            "log_return": log_return.astype(np.float32),
            "sign_imbalance": sign_imbalance.astype(np.float32),
            "signed_vol_share": signed_vol_share.astype(np.float32),
            "notional_imb": notional_imb.astype(np.float32),
            "imb_ewm": imb_ewm.astype(np.float32),
            "imb_ac1": imb_ac1.astype(np.float32),
            "streak_len": streak_len.astype(np.float32),
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
            "source": "campaign312_usdt_m_ofi_5m (perp_close, trade_sign_sum, trade_count, signed_volume, total_volume, notional)",
            "source_sha256": shard_sha_meta.get(s),
            "log_return_nan": int(np.isnan(log_return).sum()),
            "trade_sign_sum_nan": int(np.isnan(tss).sum()),
            "trade_count_nan": int(np.isnan(tc).sum()),
            "signed_volume_nan": int(np.isnan(sv).sum()),
            "total_volume_nan": int(np.isnan(tv).sum()),
            "notional_nan": int(np.isnan(no).sum()),
            "sign_imbalance_nan": int(np.isnan(sign_imbalance).sum()),
            "signed_vol_share_nan": int(np.isnan(signed_vol_share).sum()),
            "notional_imb_nan": int(np.isnan(notional_imb).sum()),
            "imb_ewm_nan": int(np.isnan(imb_ewm).sum()),
            "imb_ac1_nan": int(np.isnan(imb_ac1).sum()),
            "streak_len_nan": int(np.isnan(streak_len).sum()),
            "funding_all_nan": bool(np.isnan(funding).all()),
        }

    manifest = {s: shard_sha256[s] for s in sorted(shard_sha256)}
    manifest_sha = sha256_bytes(json.dumps(manifest, sort_keys=True).encode())

    raw_nan_observed = {}
    for s in symbols:
        with np.load(DST_DIR / f"{s}.npz") as z:
            raw_nan_observed[s] = {
                "sign_imbalance": int(np.isnan(np.asarray(z["sign_imbalance"], dtype=float)).sum()),
                "signed_vol_share": int(np.isnan(np.asarray(z["signed_vol_share"], dtype=float)).sum()),
                "notional_imb": int(np.isnan(np.asarray(z["notional_imb"], dtype=float)).sum()),
                "imb_ewm": int(np.isnan(np.asarray(z["imb_ewm"], dtype=float)).sum()),
                "imb_ac1": int(np.isnan(np.asarray(z["imb_ac1"], dtype=float)).sum()),
                "streak_len": int(np.isnan(np.asarray(z["streak_len"], dtype=float)).sum()),
            }

    meta = {
        "generated_at_utc": ts,
        "campaign": 336,
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
        "persistence_halflife_bars": HALFLIFE_BARS,
        "persistence_min_periods_ewm": MIN_PERIODS_EWM,
        "ac1_window_bars": AC1_WINDOW,
        "ac1_min_periods": AC1_MIN_PERIODS,
        "persistence_definition": (
            "sign_imbalance=trade_sign_sum/trade_count; signed_vol_share=signed_volume/total_volume; "
            "notional_imb=signed_volume/notional; imb_ewm=EWMA(sign_imbalance,halflife=24 bars); "
            "imb_ac1=rolling lag-1 autocorr of sign_imbalance over 288 bars; "
            "streak_len=run-length of consecutive same-sign trade_sign_sum"
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
            "trade_sign_sum": "real signed taker trade-count delta from C312 (read at build, not stored); always finite, may be signed/zero",
            "trade_count": "real trade count from C312 (read at build, not stored); always finite, non-negative",
            "signed_volume": "real taker buy/sell signed volume from C312 (read at build, not stored); always finite",
            "total_volume": "real total volume from C312 (read at build, not stored); always finite",
            "notional": "real traded notional from C312 (read at build, not stored); always finite, non-negative",
            "sign_imbalance": "trade_sign_sum/trade_count; trade_count<=0 -> NaN (fail-closed)",
            "signed_vol_share": "signed_volume/total_volume; total_volume<=0 -> NaN (fail-closed)",
            "notional_imb": "signed_volume/notional; notional<=0 -> NaN (fail-closed)",
            "imb_ewm": "EWMA of finite sign_imbalance (halflife=24 bars); NaN until >= 24 finite obs; NaN inputs excluded, no ffill/impute",
            "imb_ac1": "rolling lag-1 autocorr over trailing 288 bars; NaN unless full window finite and nonzero variance",
            "streak_len": "run-length of consecutive same-sign trade_sign_sum; NaN where sign undefined",
            "runner_nan": "trailing same-bucket seasonal persistence stats NaN-aware min_periods excluding NaN obs; NaN-score bars weight 0",
            "raw_nan_observed": raw_nan_observed,
        },
    }
    DST_META.write_text(json.dumps(meta, indent=2) + "\n")

    prov = {
        "generated_at_utc": ts,
        "campaign": 336,
        "part": "provenance",
        "source_host": "https://data.binance.vision",
        "note": "C336 features are a read-only derivation of real C312 USDT-M 5m perp_close, trade_sign_sum, trade_count, signed_volume, total_volume, notional (log_return plus persistence / imbalance-autocorrelation estimates); raw flow fields are read at build time but not stored in shards; no network, no fabrication, no resampling.",
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
        "campaign": 336,
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
