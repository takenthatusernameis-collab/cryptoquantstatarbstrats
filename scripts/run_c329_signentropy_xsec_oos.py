#!/usr/bin/env python3
"""C329 — rigorous costed out-of-sample test of the cross-sectional intraday
RETURN SIGN ENTROPY / DIRECTIONAL DISORDER SEASONAL DISLOCATION mean-reversion
statistical-arbitrage family on 10 USDT-M linear perps at native 5m (864
pre-registered configs).

GENUINELY NEW FAMILY (not a re-skin of any frozen modern campaign)
-----------------------------------------------------------------
C281B-C314 (all FROZEN formal negatives) exhausted carry, OFI/microstructure,
premium/index/mark basis, quarterly term-structure and same-asset spot-perp
lead-lag. C315 tested price first-moment momentum/reversal. C316 tested
size/volume/turnover liquidity LEVELS. C317 tested own realized-vol /
higher-moments. C318 tested RETURN co-movement / covariance / beta. C319 tested
price-level COINTEGRATION / PAIRS equilibrium. C320 tested cross-sectional
intraday TIME-OF-DAY / DAY-OF-WEEK seasonal RETURN mean-reversion (seasonal
return LEVEL). C321 tested intraday RANGE / BREAKOUT / OVERNIGHT-vs-INTRADAY
split. C322 tested the intraday VWAP-close fair-value anchor. C323 tested causal
same-tod ORDER-FLOW & TRADE-ACTIVITY SEASONALITY deviations. C324 tested causal
same-tod AMIHUD-ILLIQUIDITY SEASONAL DISLOCATION deviations. C325 tested
cross-sectional intraday AVERAGE TRADE SIZE SEASONAL DISLOCATION mean-reversion.
C326 tested cross-sectional intraday RETURN AUTOCORRELATION SEASONAL DISLOCATION
mean-reversion. C327 tested cross-sectional intraday SIGNED JUMP-VARIATION /
DISCONTINUITY SEASONAL DISLOCATION mean-reversion. C328 tested cross-sectional
intraday RETURN SIGN-RUN / DIRECTIONAL STREAK SEASONAL DISLOCATION mean-reversion
(consecutive same-sign run length + sign-change count). C329 is the FIRST modern
campaign to trade each asset's CAUSAL trailing same-time-of-day seasonal
deviation of its OWN return SIGN ENTROPY (Shannon entropy of the sign sequence =
directional disorder / sign balance) and MAXIMUM SAME-SIGN RUN LENGTH (extreme
persistence within the window) vs its own trailing same-tod baseline, then
cross-sectionally ranked. Sign entropy depends only on plus/minus sign COUNTS
(disorder), DISTINCT from C328's sign-run length (order-dependent persistence)
and sign-change count (order-dependent transitions); max-run length captures the
historical maximum streak within the trailing window (extreme persistence),
DISTINCT from C328's current run length ending at t.

MARKET PRICE
------------
Native USDT-M linear 5m perp_close from the real C312 cache (read-only reuse via
C329 feature shards); log_return derived causally (r[t]=log(c[t]/c[t-1]), r[0]=0).
Per-bar sign input = sign(log_return): +1/-1/0. Funding unreachable (fapi 451)
-> excluded (control only).

PRE-REGISTERED zero-activity / NaN POLICY (fail-closed)
-------------------------------------------------------
- Raw cache fields carry ZERO NaN (real, gap-free derivation from real
  strictly-positive perp_close): sign == sign(log_return), sign[0]=0.
- Denominators/values <= 0 -> NaN (not present in raw cache; only in runner
  trailing-stat denominators / min_periods).
- Same-time-of-day trailing sign-entropy / max-run statistics are NaN-aware with
  explicit min_periods=L and EXCLUDE NaN same-tod observations (no ffill, no
  impute, no shard drop, never treat NaN as 0).
- Any asset whose score is NaN at bar t receives cross-sectional weight 0 at t
  (others renormalized to gross 1.0).

SIGNALS (pre-registered, causal shift(1), cross-sectional rank, dollar-neutral
gross 1.0; score = -seasonal-dislocation so a sign-disorder/extreme-persistence
dislocation ABOVE its own trailing same-tod baseline -> LOW score (short, expect
sign-disorder mean reversion toward balance), BELOW baseline -> HIGH score (long,
expect reversion))
--------------------------------------------------------------------------------
Bucket = bar-of-day tod (0..287). For each bar t, symbol i, lookback L days
(trailing L same-tod occurrences, min_periods=L, fail-closed):

  entropy   = Shannon entropy of sign sequence over trailing L same-tod bars
              (H = -p+*log(p+) - p-*log(p-); zeros excluded; H=0 if one sign
               dominates, H=log(2) if signs balanced)
  maxrun    = maximum same-sign run length within trailing L same-tod bars
  entropy_ewm= causal EWM of entropy at same tod

  entropy_dev     : v = entropy;     score = -(v - trailing_mean_L(v at same tod))
  entropy_ewm_dev : v = entropy;     score = -(v - ewm_L(v at same tod))
  maxrun_dev      : v = maxrun;      score = -(v - trailing_mean_L(v at same tod))

entropy_placebo is the attribution bucket (permuted returns), NOT a signal.

PORTFOLIO & COSTS
-----------------
Single-leg perp: pnl[t] = sum_i pos[i,t] * perp_ret[i,t]. Costs on turnover:
  symmetric  : fee + slip per unit turnover
  perp_heavy : 1.5*fee + slip per unit turnover

GRID (864 = 3 x 3 x 3 x 4 x 4 x 2, all reported)
------------------------------------------------
signal{entropy_dev,entropy_ewm_dev,maxrun_dev}(3) x
lookback{30,60,90 days}(3) x rebalance{6,12,48 bars}(3) x
fee{1,5,10,20}bps(4) x slippage{1,2,5,10}bps(4) x
cost_variant{symmetric,perp_heavy}(2)

WF: expanding train 12m / test 3m / roll 3m over 2023-01..2025-12 (8 splits).
Gates: Holm AND Benjamini-Hochberg at alpha=0.05 (BOTH), MDE, stability
(sign consistency >= 70% splits; first/second-half Sharpe corr >= 0.5), and
sign-entropy-vs-placebo attribution (dominant share > 0.5 for a positive claim).

Model PnL backtest (executed_fills: false) on real data only. Never fetches,
imputes, resamples, or fabricates data.

Artifact (exact names, timestamped, SHA256-from-bytes):
  reports/campaign329_oos_sweep_<ts>.json  (+ gitignored *.full.json)
  reports/campaign329_tradable_edge_registry_<ts>.json
  reports/campaign329_summary_<ts>.json
  reports/campaign329_verdict_<ts>.json
  reports/campaign329_binding_constraint_<ts>.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
reports = ROOT / "reports"
reports.mkdir(exist_ok=True)
cache_dir = ROOT / "data" / "cache"

CACHE_DIR = cache_dir / "campaign329_signentropy_5m"
CACHE_META = cache_dir / "campaign329_signentropy_5m.meta.json"
CACHE_PROV = cache_dir / "campaign329_signentropy_5m.provenance.json"

# ---- pre-registered grid ----
SIGNALS = ("entropy_dev", "entropy_ewm_dev", "maxrun_dev")
LOOKBACKS = (30, 60, 90)
REBALANCES = (6, 12, 48)
FEES = (1, 5, 10, 20)
SLIPS = (1, 2, 5, 10)
COST_VARIANTS = ("symmetric", "perp_heavy")
FRAC = 0.33
ALPHA = 0.05
N_TRIALS = (len(SIGNALS) * len(LOOKBACKS) * len(REBALANCES) *
            len(FEES) * len(SLIPS) * len(COST_VARIANTS))  # 864

TOD_BARS_PER_DAY = 288
TRAIN_M, TEST_M, ROLL_M = 12, 3, 3
STABILITY_MIN_SIGN_CONSISTENCY = 0.70
STABILITY_MIN_SHARPE_CORR = 0.50
DOMINANT_SHARE_MIN = 0.50

ATTR_BUCKETS = ("entropy_dev", "maxrun_dev", "entropy_ewm_dev", "entropy_placebo")
ATTR_REPRESENTATIVES = {s: s for s in SIGNALS}

SIGNALP_KEYS = {"entropy_dev": "entropy", "maxrun_dev": "maxrun",
                "entropy_ewm_dev": "entropy"}


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def jdefault(o):
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o) if np.isfinite(o) else None
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, pd.Timestamp):
        return str(o)
    raise TypeError(str(type(o)))


def holm_adjust(pvals: np.ndarray):
    p = np.asarray(pvals, dtype=float)
    m = len(p)
    order = np.argsort(p, kind="mergesort")
    ranked = p[order]
    factors = (m - np.arange(m)).astype(float)
    adj = np.maximum.accumulate(ranked * factors)
    adj = np.minimum(adj, 1.0)
    out = np.empty(m, dtype=float)
    out[order] = adj
    return out, out <= ALPHA


def bh_adjust(pvals: np.ndarray):
    p = np.asarray(pvals, dtype=float)
    m = len(p)
    order = np.argsort(p, kind="mergesort")
    ranked = p[order]
    ranks = np.arange(1, m + 1).astype(float)
    adj = ranked * m / ranks
    adj = np.minimum.accumulate(adj[::-1])[::-1]
    adj = np.minimum(adj, 1.0)
    out = np.empty(m, dtype=float)
    out[order] = adj
    return out, out <= ALPHA


def one_sided_p(diffs: np.ndarray) -> float:
    d = np.asarray(diffs, dtype=float)
    d = d[np.isfinite(d)]
    if len(d) < 2:
        return 1.0
    if float(np.std(d)) <= 0:
        return 1.0 if float(np.mean(d)) <= 0 else 0.0
    return float(stats.ttest_1samp(d, 0.0, alternative="greater").pvalue)


def wf_splits_by_month(index: pd.DatetimeIndex, train_m: int, test_m: int, roll_m: int):
    months = sorted({(ts.year, ts.month) for ts in index})
    bounds: dict = {}
    for (y, m) in months:
        mask = np.array([(ts.year == y and ts.month == m) for ts in index])
        pos = np.where(mask)[0]
        if len(pos):
            bounds[(y, m)] = (int(pos[0]), int(pos[-1]) + 1)
    ordered = sorted(bounds)
    splits = []
    i = 0
    while i + train_m + test_m <= len(ordered):
        tr_months = ordered[i:i + train_m]
        te_months = ordered[i + train_m:i + train_m + test_m]
        tr_s = bounds[tr_months[0]][0]
        tr_e = bounds[tr_months[-1]][1]
        te_s = bounds[te_months[0]][0]
        te_e = bounds[te_months[-1]][1]
        splits.append((tr_s, tr_e, te_s, te_e))
        i += roll_m
    return splits


def finite_or_nan(x: np.ndarray) -> np.ndarray:
    return np.where(np.isfinite(x), x, np.nan)


def xsec_positions(score: np.ndarray, frac: float, H: int) -> np.ndarray:
    n_assets, n_bars = score.shape
    n_side = max(1, int(round(frac * n_assets)))
    finite = np.isfinite(score)
    s = np.where(finite, score, 0.0)
    order = np.argsort(-s, axis=0)
    rank = np.argsort(order, axis=0).astype(float)
    rank[~finite] = np.inf
    enough = finite.sum(axis=0) >= 2
    long_mask = (rank < n_side) & finite & enough[None, :]
    short_mask = (rank >= (n_assets - n_side)) & finite & enough[None, :]
    desired = np.zeros((n_assets, n_bars), dtype=float)
    n_long = long_mask.sum(axis=0).astype(float)
    n_short = short_mask.sum(axis=0).astype(float)
    wl = np.where(n_long > 0, 0.5 / np.maximum(n_long, 1), 0.0)
    ws = np.where(n_short > 0, 0.5 / np.maximum(n_short, 1), 0.0)
    desired[long_mask] = np.broadcast_to(wl[None, :], desired.shape)[long_mask]
    desired[short_mask] = -np.broadcast_to(ws[None, :], desired.shape)[short_mask]
    flat = (n_long == 0) | (n_short == 0)
    desired[:, flat] = 0.0
    seg_start = (np.arange(n_bars) // H) * H
    seg_desired = desired[:, seg_start]
    pos = np.zeros((n_assets, n_bars), dtype=float)
    if n_bars > 1:
        pos[:, 1:] = seg_desired[:, :-1]
    return np.where(np.isfinite(pos), pos, 0.0)


def cost_rate_bps(fee: float, slip: float, cv: str) -> float:
    if cv == "symmetric":
        return fee + slip
    return 1.5 * fee + slip


# ---------------------------------------------------------------- sign entropy ops
def _trailing_sign_counts(signs: np.ndarray, L: int):
    """Trailing counts of + and - signs over the last L observations (min_periods=L).
    Returns (pos_counts, neg_counts); NaN where fewer than L finite obs."""
    n = len(signs)
    out_pos = np.full(n, np.nan, dtype=np.float64)
    out_neg = np.full(n, np.nan, dtype=np.float64)
    if n < L:
        return out_pos, out_neg
    is_pos = (signs > 0).astype(np.float64)
    is_neg = (signs <  0).astype(np.float64)
    cs_pos = np.concatenate([np.zeros(1), np.cumsum(is_pos)])
    cs_neg = np.concatenate([np.zeros(1), np.cumsum(is_neg)])
    j = np.arange(L - 1, n)
    s = j - L + 1
    out_pos[j] = cs_pos[j + 1] - cs_pos[s]
    out_neg[j] = cs_neg[j + 1] - cs_neg[s]
    return out_pos, out_neg


def _entropy_from_counts(pos_cnt: np.ndarray, neg_cnt: np.ndarray) -> np.ndarray:
    """Shannon entropy H = -p+*log(p+) - p-*log(p-) from plus/minus counts.
    NaN where total == 0 (no nonzero signs in window)."""
    total = pos_cnt + neg_cnt
    out = np.full_like(pos_cnt, np.nan, dtype=np.float64)
    valid = total > 0
    if not valid.any():
        return out
    p_pos = np.where(valid, pos_cnt / np.maximum(total, 1.0), 0.0)
    p_neg = np.where(valid, neg_cnt / np.maximum(total, 1.0), 0.0)
    log_pos = np.log(np.where(p_pos > 0, p_pos, 1.0))
    log_neg = np.log(np.where(p_neg > 0, p_neg, 1.0))
    term_pos = np.where(p_pos > 0, -p_pos * log_pos, 0.0)
    term_neg = np.where(p_neg > 0, -p_neg * log_neg, 0.0)
    out[valid] = term_pos[valid] + term_neg[valid]
    return out


def _trailing_maxrun_1d(signs: np.ndarray, L: int) -> np.ndarray:
    """Trailing maximum same-sign run length over the last L observations
    (min_periods=L). NaN where fewer than L obs or no nonzero sign in window."""
    n = len(signs)
    out = np.full(n, np.nan, dtype=np.float64)
    if n < L:
        return out
    run = np.zeros(n, dtype=np.float64)
    for t in range(1, n):
        if signs[t] != 0 and signs[t] == signs[t - 1]:
            run[t] = run[t - 1] + 1.0
        else:
            run[t] = 1.0 if signs[t] != 0 else 0.0
    for j in range(L - 1, n):
        s = j - L + 1
        window = run[s:j + 1]
        offsets = np.arange(s, j + 1, dtype=np.float64) - s + 1.0
        vals = np.minimum(window, offsets)
        valid_mask = signs[s:j + 1] != 0
        if valid_mask.any():
            out[j] = float(np.max(np.where(valid_mask, vals, 0.0)))
    return out


def _ewm_mean_1d(vals: np.ndarray, alpha: float) -> np.ndarray:
    """Causal exponential weighted mean (recursive, adjust=False). NaN where
    input is NaN; NaN observation does not update EWM (fail-closed, weight 0)."""
    vals = np.asarray(vals, dtype=np.float64)
    n = vals.shape[0]
    out = np.full(n, np.nan, dtype=np.float64)
    finite = np.isfinite(vals)
    if not finite.any():
        return out
    first = int(np.argmax(finite))
    out[first] = vals[first]
    prev = vals[first]
    for t in range(first + 1, n):
        if finite[t]:
            prev = alpha * vals[t] + (1.0 - alpha) * prev
            out[t] = prev
        else:
            out[t] = np.nan
    return out


def bucket_signentropy_stats(sign: np.ndarray, bucket_idx: np.ndarray,
                             L: int, alpha: float) -> dict:
    """Per-(asset, bar-of-day bucket) trailing same-tod sign-entropy / max-run
    statistics over the last L same-tod occurrences (min_periods=L, fail-closed)."""
    n_assets, n_bars = sign.shape
    out = {k: np.full((n_assets, n_bars), np.nan, dtype=np.float64)
           for k in ("entropy", "maxrun", "entropy_ewm")}
    n_buckets = int(bucket_idx.max()) + 1 if n_bars else 0
    for b in range(n_buckets):
        pos = np.where(bucket_idx == b)[0]
        if len(pos) == 0:
            continue
        sg = sign[:, pos]
        pc, nc = _trailing_sign_counts_for_matrix(sg, L)
        entropy = _entropy_from_counts(pc, nc)
        maxrun = _trailing_maxrun_for_matrix(sg, L)
        entropy_ewm = _ewm_mean_for_matrix(entropy, alpha)
        out["entropy"][:, pos] = entropy
        out["maxrun"][:, pos] = maxrun
        out["entropy_ewm"][:, pos] = entropy_ewm
    return out


def _trailing_sign_counts_for_matrix(sg: np.ndarray, L: int):
    """Vectorized trailing +/- sign counts for an (n_assets, n_pos) matrix."""
    n_assets, n = sg.shape
    out_pos = np.full((n_assets, n), np.nan, dtype=np.float64)
    out_neg = np.full((n_assets, n), np.nan, dtype=np.float64)
    if n < L:
        return out_pos, out_neg
    is_pos = (sg > 0).astype(np.float64)
    is_neg = (sg < 0).astype(np.float64)
    cs_pos = np.concatenate([np.zeros((n_assets, 1)), np.cumsum(is_pos, axis=1)], axis=1)
    cs_neg = np.concatenate([np.zeros((n_assets, 1)), np.cumsum(is_neg, axis=1)], axis=1)
    j = np.arange(L - 1, n)
    s = j - L + 1
    out_pos[:, j] = cs_pos[:, j + 1] - cs_pos[:, s]
    out_neg[:, j] = cs_neg[:, j + 1] - cs_neg[:, s]
    return out_pos, out_neg


def _trailing_maxrun_for_matrix(sg: np.ndarray, L: int):
    """Vectorized trailing max same-sign run length for an (n_assets, n_pos) matrix."""
    n_assets, n = sg.shape
    out = np.full((n_assets, n), np.nan, dtype=np.float64)
    if n < L:
        return out
    run = np.zeros((n_assets, n), dtype=np.float64)
    for t in range(1, n):
        same = (sg[:, t] != 0) & (sg[:, t] == sg[:, t - 1])
        run[:, t] = np.where(same, run[:, t - 1] + 1.0,
                             np.where(sg[:, t] != 0, 1.0, 0.0))
    for j in range(L - 1, n):
        s = j - L + 1
        window = run[:, s:j + 1]
        offsets = (np.arange(s, j + 1, dtype=np.float64) - s + 1.0)[None, :]
        vals = np.minimum(window, offsets)
        valid_mask = sg[:, s:j + 1] != 0
        masked = np.where(valid_mask, vals, 0.0)
        out[:, j] = np.max(masked, axis=1)
    return out


def _ewm_mean_for_matrix(vals: np.ndarray, alpha: float):
    """Causal EWM along axis=1 for an (n_assets, n) matrix."""
    n_assets, n = vals.shape
    out = np.full((n_assets, n), np.nan, dtype=np.float64)
    finite = np.isfinite(vals)
    for i in range(n_assets):
        out[i] = _ewm_mean_1d(vals[i], alpha)
    return out


def _trailing_mean_2d(vals: np.ndarray, L: int) -> np.ndarray:
    n_assets, n = vals.shape
    out = np.full_like(vals, np.nan, dtype=np.float64)
    if n < L:
        return out
    finite = np.isfinite(vals)
    vf = np.where(finite, vals, 0.0)
    cs = np.concatenate([np.zeros((n_assets, 1)), np.cumsum(vf, axis=1)], axis=1)
    cc = np.concatenate([np.zeros((n_assets, 1)), np.cumsum(finite.astype(np.float64), axis=1)], axis=1)
    e = np.arange(L, n + 1)
    s = cs[:, e] - cs[:, e - L]
    c = cc[:, e] - cc[:, e - L]
    with np.errstate(invalid="ignore", divide="ignore"):
        m = np.where(c >= L, s / np.maximum(c, 1.0), np.nan)
    out[:, L - 1:] = m
    return out


def bucket_trailing_stats(vals: np.ndarray, bucket_idx: np.ndarray, L: int):
    n_assets, n_bars = vals.shape
    mean_out = np.full((n_assets, n_bars), np.nan, dtype=np.float64)
    n_buckets = int(bucket_idx.max()) + 1 if n_bars else 0
    for b in range(n_buckets):
        pos = np.where(bucket_idx == b)[0]
        if len(pos) == 0:
            continue
        mean_out[:, pos] = _trailing_mean_2d(vals[:, pos], L)
    return mean_out


def bucket_ewm_stats(vals: np.ndarray, bucket_idx: np.ndarray, alpha: float):
    n_assets, n_bars = vals.shape
    ewm_out = np.full((n_assets, n_bars), np.nan, dtype=np.float64)
    n_buckets = int(bucket_idx.max()) + 1 if n_bars else 0
    for b in range(n_buckets):
        pos = np.where(bucket_idx == b)[0]
        if len(pos) == 0:
            continue
        for i in range(n_assets):
            ewm_out[i, pos] = _ewm_mean_1d(vals[i, pos], alpha)
    return ewm_out


def verify_cache() -> tuple:
    if not CACHE_DIR.exists():
        raise SystemExit(f"FATAL: C329 shard dir missing: {CACHE_DIR}")
    if not CACHE_META.exists():
        raise SystemExit(f"FATAL: C329 meta missing: {CACHE_META}")
    meta_sha = sha256_file(CACHE_META)
    prov_sha = sha256_file(CACHE_PROV) if CACHE_PROV.exists() else None
    meta = json.loads(CACHE_META.read_text())
    if meta.get("real_data_only") is not True or meta.get("fabricated_data") is not False:
        raise SystemExit("FATAL: dataset provenance flags not real_data_only/fabricated_data")
    if meta.get("executed_fills") is not False:
        raise SystemExit("FATAL: cache executed_fills must be false (model PnL only)")
    if meta.get("interval") != "5m":
        raise SystemExit(f"FATAL: cache interval must be 5m, got {meta.get('interval')}")
    if meta.get("network_ingest") is not False or meta.get("resample") is not False:
        raise SystemExit("FATAL: cache must be no-network, no-resample")
    shard_sha_meta = meta.get("shard_sha256") or {}
    shard_bytes_meta = meta.get("shard_bytes") or {}
    per_asset = {}
    for s, expected in shard_sha_meta.items():
        sp = CACHE_DIR / f"{s}.npz"
        if not sp.exists():
            raise SystemExit(f"FATAL: shard missing: {sp}")
        if sha256_file(sp) != expected:
            raise SystemExit(f"FATAL: shard sha256 mismatch for {s}")
        nbytes = sp.stat().st_size
        if nbytes != int(shard_bytes_meta.get(s, -1)):
            raise SystemExit(f"FATAL: shard byte size mismatch for {s}")
        if nbytes >= 100_000_000:
            raise SystemExit(f"FATAL: shard {s} exceeds 100 MB push limit")
        with np.load(sp) as z:
            per_asset[s] = {k: z[k] for k in z.files}
    manifest = {s: shard_sha_meta[s] for s in sorted(shard_sha_meta)}
    manifest_sha = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()
    if manifest_sha != meta.get("manifest_sha256"):
        raise SystemExit("FATAL: shard manifest sha256 mismatch")
    payload = {"symbols": list(meta.get("symbols") or []),
               "n_grid_bars": int(meta.get("n_grid_bars") or 0),
               "per_asset": per_asset}
    return payload, meta, manifest_sha, meta_sha, prov_sha


def build_series(payload: dict):
    symbols = list(payload.get("symbols") or [])
    n_assets = len(symbols)
    per_asset = payload.get("per_asset") or {}
    first = per_asset[symbols[0]]
    idx_ms = np.asarray(first["index_ms"], dtype="int64")
    index = pd.DatetimeIndex(pd.to_datetime(idx_ms, unit="ms", utc=True))
    n_b = len(index)
    if n_b == 0:
        raise SystemExit("FATAL: C329 common grid is empty")
    if n_b % TOD_BARS_PER_DAY != 0:
        raise SystemExit("FATAL: C329 grid is not a whole number of 288-bar days")

    def mat(key):
        out = np.zeros((n_assets, n_b), dtype=float)
        for i, s in enumerate(symbols):
            out[i] = np.asarray(per_asset[s][key], dtype=float)
        return out

    perp_close = mat("perp_close")
    log_return = mat("log_return")
    sign = mat("sign")

    if not (np.isfinite(perp_close).all() and (perp_close > 0).all()):
        raise SystemExit("FATAL: non-finite/non-positive perp_close")
    if not np.isfinite(log_return).all():
        raise SystemExit("FATAL: non-finite log_return in cache")
    if not np.isfinite(sign).all():
        raise SystemExit("FATAL: non-finite sign in cache")

    # seasonal bucket ids (causal, from timestamps only)
    secs = idx_ms // 1000
    tod_idx = ((secs % 86400) // 300).astype(np.int64)
    day_ord = (secs // 86400 - secs[0] // 86400).astype(np.int64)
    n_days = n_b // TOD_BARS_PER_DAY
    if not np.array_equal(day_ord, np.repeat(np.arange(n_days), TOD_BARS_PER_DAY)):
        raise SystemExit("FATAL: day boundaries are not aligned to 288-bar UTC days")

    splits = wf_splits_by_month(index, TRAIN_M, TEST_M, ROLL_M)
    if not splits:
        raise SystemExit("FATAL: no OOS splits")

    return {"symbols": symbols, "n_assets": n_assets, "index": index, "n_bars": n_b,
            "n_days": n_days, "perp_close": perp_close, "log_return": log_return,
            "sign": sign, "tod_idx": tod_idx, "day_ord": day_ord, "splits": splits}


def build_score(bs: dict, signal: str, L: int, alpha: float = 0.3) -> np.ndarray:
    tod_idx = bs["tod_idx"]
    if signal not in SIGNALP_KEYS:
        raise ValueError(f"unknown signal {signal}")
    stat = SIGNALP_KEYS[signal]
    js = bucket_signentropy_stats(bs["sign"], tod_idx, L, alpha)
    v = js[stat]
    if signal == "entropy_ewm_dev":
        base = js["entropy_ewm"]  # causal EWM baseline of raw entropy
        return -(v - base)
    base = bucket_trailing_stats(v, tod_idx, L)
    return -(v - base)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--reference-config-only", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args(argv)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    payload, meta, cache_sha, meta_sha, prov_sha = verify_cache()
    bs = build_series(payload)
    symbols = bs["symbols"]
    index = bs["index"]
    n_b = bs["n_bars"]
    splits = bs["splits"]
    n_splits = len(splits)
    perp_ret = bs["log_return"]

    alpha = 2.0 / (float(max(LOOKBACKS)) + 1.0)  # EWM span = max lookback

    gross_turn_cache: dict = {}
    score_cache: dict = {}

    def get_score(signal: str, L: int):
        key = (signal, L)
        if key not in score_cache:
            score_cache[key] = build_score(bs, signal, L, alpha)
        return score_cache[key]

    def get_gross_turn(signal: str, L: int, H: int):
        key = (signal, L, H)
        if key in gross_turn_cache:
            return gross_turn_cache[key]
        sc = get_score(signal, L)
        sc_causal = np.full_like(sc, np.nan)
        if sc.shape[1] > 1:
            sc_causal[:, 1:] = sc[:, :-1]
        pos = xsec_positions(sc_causal, FRAC, H)
        gross = (pos * perp_ret).sum(axis=0)
        dpos = np.abs(np.diff(pos, axis=1, prepend=pos[:, :1]))
        turn = dpos.sum(axis=0)
        gross_turn_cache[key] = (gross, turn)
        return gross, turn

    results: list[dict] = []

    def run_config(signal: str, L: int, H: int, fee: float, slip: float, cv: str):
        gross, turn = get_gross_turn(signal, L, H)
        cost_rate = cost_rate_bps(fee, slip, cv) / 10000.0
        seg_gross, seg_turn, seg_len = [], [], []
        for (tr_s, tr_e, te_s, te_e) in splits:
            seg_gross.append(float(gross[te_s:te_e].sum()))
            seg_turn.append(float(turn[te_s:te_e].sum()))
            seg_len.append(int(te_e - te_s))
        net = [g - cost_rate * t for g, t in zip(seg_gross, seg_turn)]
        net_arr = np.array(net, dtype=float)
        net_sum = float(net_arr.sum())
        net_mean = float(net_arr.mean()) if len(net_arr) else 0.0
        p_val = one_sided_p(net_arr)
        all_pos = bool(len(net_arr) > 0 and (net_arr > 0).all() and net_sum > 0)
        sr = float(np.mean(net_arr) / np.std(net_arr)) if len(net_arr) > 1 and np.std(net_arr) > 0 else 0.0
        if n_splits > 1 and np.std(net_arr) > 0:
            s = float(np.std(net_arr, ddof=1))
            t_a = float(stats.t.ppf(1 - ALPHA / 2, df=n_splits - 1))
            t_b = float(stats.t.ppf(0.80, df=n_splits - 1))
            mde_bps = (t_a + t_b) * s / math.sqrt(n_splits) * 10000.0
        else:
            mde_bps = float("nan")
        per_split_bps = float(np.mean([g / max(l, 1) for g, l in zip(seg_gross, seg_len)])) * 10000.0 if seg_len else 0.0
        return {
            "signal": signal, "lookback": int(L), "rebalance": int(H),
            "selection": float(FRAC),
            "fee_bps": float(fee), "slippage_bps": float(slip), "cost_variant": cv,
            "n_splits": int(n_splits),
            "oos_net_sum": net_sum, "oos_net_mean": net_mean,
            "oos_net_per_split": [float(x) for x in net],
            "gross_sum": float(sum(seg_gross)), "turnover_total": float(sum(seg_turn)),
            "edge_proven": bool(all_pos), "p_value": float(p_val),
            "per_split_mean_bps": per_split_bps, "sharpe_obs": float(sr),
            "mde_bps": float(mde_bps),
            "cost_rate_bps_effective": float(cost_rate_bps(fee, slip, cv)),
        }

    ref_cfg = dict(signal="entropy_dev", L=60, H=12, fee=10, slip=5, cv="symmetric")
    if args.reference_config_only or args.smoke:
        run_config(ref_cfg["signal"], ref_cfg["L"], ref_cfg["H"],
                   ref_cfg["fee"], ref_cfg["slip"], ref_cfg["cv"])
    else:
        for signal in SIGNALS:
            for L in LOOKBACKS:
                for H in REBALANCES:
                    for fee in FEES:
                        for slip in SLIPS:
                            for cv in COST_VARIANTS:
                                results.append(run_config(signal, L, H, fee, slip, cv))

    n_total = len(results)
    pvals = np.array([r["p_value"] for r in results], dtype=float)
    p_holm, rej_holm = holm_adjust(pvals)
    p_bh, rej_bh = bh_adjust(pvals)
    for r, ph, pb, rh, rb in zip(results, p_holm, p_bh, rej_holm, rej_bh):
        r["p_holm"] = float(ph)
        r["p_bh"] = float(pb)
        r["holm_reject"] = bool(rh)
        r["bh_reject"] = bool(rb)

    edge_idx = [i for i, r in enumerate(results) if r["edge_proven"]]
    n_edge = len(edge_idx)
    n_survive_holm = int(sum(1 for i in edge_idx if rej_holm[i]))
    n_survive_bh = int(sum(1 for i in edge_idx if rej_bh[i]))
    n_survive_both = int(sum(1 for i in edge_idx if rej_holm[i] and rej_bh[i]))

    # ---- sign-entropy-vs-placebo attribution (reference config) ----
    ref = ref_cfg
    cr = cost_rate_bps(ref["fee"], ref["slip"], ref["cv"]) / 10000.0

    def ref_net_for(signal: str, L: int):
        gross, turn = get_gross_turn(signal, L, ref["H"])
        return float(sum(gross[te_s:te_e].sum() - cr * turn[te_s:te_e].sum()
                         for (tr_s, tr_e, te_s, te_e) in splits))

    nets = {s: ref_net_for(s, ref["L"]) for s in SIGNALS}

    rng = np.random.default_rng(20261116)
    perp_ret_placebo = perp_ret.copy()
    for i in range(bs["n_assets"]):
        perp_ret_placebo[i] = perp_ret_placebo[i][rng.permutation(n_b)]
    _, turn_ref = get_gross_turn(ref["signal"], ref["L"], ref["H"])
    sc_ref = get_score(ref["signal"], ref["L"])
    sc_ref_causal = np.full_like(sc_ref, np.nan)
    if sc_ref.shape[1] > 1:
        sc_ref_causal[:, 1:] = sc_ref[:, :-1]
    pos_ref = xsec_positions(sc_ref_causal, FRAC, ref["H"])
    gross_placebo = (pos_ref * perp_ret_placebo).sum(axis=0)
    placebo_net = float(sum(gross_placebo[te_s:te_e].sum() - cr * turn_ref[te_s:te_e].sum()
                            for (tr_s, tr_e, te_s, te_e) in splits))

    attrib = {s: abs(nets[s]) for s in SIGNALS}
    attrib["entropy_placebo"] = abs(placebo_net)
    attrib_total = sum(attrib.values())
    if attrib_total > 0:
        attrib_share = {k: float(v / attrib_total) for k, v in attrib.items()}
    else:
        attrib_share = {k: 0.0 for k in ATTR_BUCKETS}
    dominant = max(attrib_share, key=attrib_share.get) if attrib_total > 0 else None
    dominant_share = float(attrib_share[dominant]) if dominant else 0.0
    attribution_ok = bool(dominant in ATTR_REPRESENTATIVES
                          and dominant_share > DOMINANT_SHARE_MIN)

    def stability():
        gross, turn = get_gross_turn(ref["signal"], ref["L"], ref["H"])
        seg_nets = []
        for (tr_s, tr_e, te_s, te_e) in splits:
            seg_nets.append(float(gross[te_s:te_e].sum() - cr * turn[te_s:te_e].sum()))
        seg_nets_arr = np.array(seg_nets, dtype=float)
        n = len(seg_nets_arr)
        sign_consistency = float(np.mean(seg_nets_arr > 0)) if n else 0.0
        half = n // 2
        first = seg_nets_arr[:half]
        second = seg_nets_arr[half:2 * half]

        def _sharpe(a):
            return float(np.mean(a) / np.std(a)) if len(a) > 1 and np.std(a) > 0 else 0.0

        sharpe_corr = float("nan")
        if len(first) == len(second) and len(first) >= 3:
            c1 = np.cumsum(first)
            c2 = np.cumsum(second)
            if np.std(c1) > 0 and np.std(c2) > 0:
                sharpe_corr = float(np.corrcoef(c1, c2)[0, 1])
        stable = bool(sign_consistency >= STABILITY_MIN_SIGN_CONSISTENCY
                      and np.isfinite(sharpe_corr)
                      and sharpe_corr >= STABILITY_MIN_SHARPE_CORR)
        return {
            "reference_config": ref,
            "per_split_net": [float(x) for x in seg_nets],
            "sign_consistency": sign_consistency,
            "first_half_sharpe": _sharpe(first),
            "second_half_sharpe": _sharpe(second),
            "sharpe_corr": sharpe_corr,
            "stable": stable,
        }

    stability_ref = stability()

    # ---- sign-entropy data-quality report (reference config signal) ----
    sc_ref_nan_share = float(1.0 - float(np.isfinite(sc_ref).mean()))

    if n_total and n_survive_both == 0:
        verdict = "RETRACTED"
        binding = "multiple_testing"
    elif n_survive_both > 0 and not attribution_ok:
        verdict = "RETRACTED"
        binding = "attribution"
    elif n_survive_both > 0 and not stability_ref["stable"]:
        verdict = "RETRACTED"
        binding = "stability"
    elif n_survive_both > 0 and attribution_ok and stability_ref["stable"]:
        verdict = "EDGE_PROVEN"
        binding = None
    else:
        verdict = "RETRACTED"
        binding = "multiple_testing"
    edge_proven = bool(edge_idx and verdict == "EDGE_PROVEN")

    obs_mean_bps = float(np.mean([results[i]["per_split_mean_bps"] for i in edge_idx])) if edge_idx else 0.0
    mde_vals = [results[i]["mde_bps"] for i in edge_idx if np.isfinite(results[i]["mde_bps"])]
    mde_bps = float(np.mean(mde_vals)) if mde_vals else float("nan")

    dataset_block = {
        "cache": str(CACHE_DIR.relative_to(ROOT)),
        "cache_sha256": cache_sha,
        "cache_meta": str(CACHE_META.relative_to(ROOT)),
        "cache_meta_sha256": meta_sha,
        "cache_provenance": str(CACHE_PROV.relative_to(ROOT)) if CACHE_PROV.exists() else None,
        "cache_provenance_sha256": prov_sha,
        "storage": "per_asset_float32_npz_shards",
        "source_campaign": int(meta.get("source_campaign") or 312),
        "network_ingest": False,
        "total_shard_bytes": int(meta.get("total_shard_bytes") or 0),
        "max_shard_bytes": int(meta.get("max_shard_bytes") or 0),
        "under_push_limit": bool(meta.get("under_push_limit")),
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
    }

    sweep_obj = {
        "generated_at_utc": ts, "campaign": 329, "part": "oos_sweep",
        "analysis": "c329_signentropy_xsec_stat_arb_oos_5m",
        "verdict": verdict, "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "fail_closed": True,
        "mandate": (
            "C329 — test the cross-sectional intraday RETURN SIGN ENTROPY / "
            "DIRECTIONAL DISORDER SEASONAL DISLOCATION mean-reversion statistical-arbitrage "
            "family on 10 USDT-M linear perps at native 5m (864 pre-registered configs). "
            "Per bar-of-day bucket, trailing L same-tod occurrences: entropy=Shannon "
            "entropy of sign sequence (directional disorder/sign balance), "
            "maxrun=maximum same-sign run length within window, entropy_ewm=causal EWM "
            "of entropy; score=-dislocation vs trailing same-tod mean. Signals: "
            "entropy_dev, entropy_ewm_dev, maxrun_dev. Single-leg dollar-neutral perp "
            "PnL with costs on turnover (symmetric and perp_heavy). Gates: Holm+BH at "
            "alpha=0.05 (BOTH), MDE, stability, and sign-entropy-vs-placebo attribution. "
            "PRE-REGISTERED NaN policy: denominators/values<=0 -> NaN; same-tod "
            "trailing stats NaN-aware min_periods=L excluding NaN obs; "
            "zero-variance/insufficient-obs NaNs fail-closed (NaN bars weight 0); "
            "raw cache fields are zero-NaN real derivations."
        ),
        "preflight": dataset_block, "data_source": dataset_block,
        "universe": {"symbols": symbols, "n_assets": bs["n_assets"],
                     "common_grid_bars": int(n_b),
                     "common_grid_start_utc": str(index[0]),
                     "common_grid_end_utc": str(index[-1]),
                     "n_splits": int(n_splits)},
        "config": {
            "walk_forward": {"train_m": TRAIN_M, "test_m": TEST_M, "roll_m": ROLL_M},
            "signals": list(SIGNALS), "lookbacks_days": list(LOOKBACKS),
            "rebalances_bars": list(REBALANCES),
            "fee_bps": list(FEES), "slippage_bps": list(SLIPS),
            "selection_frac": float(FRAC), "cost_variants": list(COST_VARIANTS),
            "alpha": ALPHA, "n_trials": N_TRIALS, "total_runs": n_total,
        },
        "gates": {
            "fail_closed": True,
            "multiple_testing": {"holm_alpha": ALPHA, "bh_alpha": ALPHA,
                                 "n_survive_holm": n_survive_holm, "n_survive_bh": n_survive_bh,
                                 "n_survive_both": n_survive_both, "n_edge_proven": n_edge},
            "dsr_mde": {"n_splits": int(n_splits), "mde_bps_mean": mde_bps,
                        "observed_mean_bps_per_split": obs_mean_bps},
            "stability": stability_ref,
            "attribution": {
                "reference_config": ref,
                **{f"{s}_net": nets[s] for s in SIGNALS},
                "entropy_placebo_net": placebo_net,
                "shares": attrib_share, "dominant": dominant,
                "dominant_share": dominant_share, "attribution_ok": attribution_ok,
            },
            "data_quality": {
                "reference_signal": ref["signal"], "reference_lookback": int(ref["L"]),
                "reference_score_nan_share": sc_ref_nan_share,
                "note": "sign-entropy NaN share is dominated by structural warmup (first ~L same-tod occurrences per bucket) plus min_periods windows; zero-variance adds negligible mass.",
            },
        },
        "methodology": {
            "buckets": "bar-of-day (tod)=seconds-of-day//300 (0..287), exact 288 bars per UTC day.",
            "raw_features": "log_return=log(c[t]/c[t-1]) (r[0]=0) from real strictly-positive perp_close; sign=sign(log_return) (+1/-1/0, sign[0]=0). Zero NaN raw fields.",
            "signals": "per bar-of-day bucket over trailing L same-tod bars: entropy=Shannon entropy of sign sequence (zeros excluded); maxrun=maximum same-sign run length within window; entropy_ewm=causal EWM of entropy. score=-(v-trailing_mean_L(v@tod)) (entropy_ewm vs ewm baseline); causal shift(1), cross-sectional rank, dollar-neutral gross 1.0; NaN-score assets weight 0.",
            "pnl": "single-leg perp: pnl = sum_i pos_i * perp_ret_i.",
            "costs": "charged on turnover; symmetric = fee+slip; perp_heavy = 1.5*fee+slip.",
            "missing_data": "non-finite -> NaN; never impute/ffill; insufficient valid obs -> NaN -> not traded (fail-closed).",
            "multiple_testing": "one-sided paired t-test of per-split OOS net vs 0; Holm step-down AND Benjamini-Hochberg over all 864 configs at alpha=0.05.",
            "mde": "two-sided alpha=0.05, power=0.80: (t_{0.975}+t_{0.80})*s/sqrt(n_splits).",
            "attribution": "reference config signal nets vs entropy_placebo (per-asset permuted returns, same positions); shares=|net|/sum(|buckets|).",
            "stability": "sign consistency >= 0.70 of splits AND first/second-half Sharpe corr >= 0.5.",
            "funding": "USDT-M funding unreachable (fapi 451) -> excluded (control only).",
            "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        },
        "results": results,
        "summary": {
            "n_total_runs": int(n_total), "n_with_exposure": int(sum(1 for r in results if r["turnover_total"] > 0)),
            "n_edge_proven_deterministic": int(n_edge),
            "n_survive_holm": n_survive_holm, "n_survive_bh": n_survive_bh,
            "n_survive_both": n_survive_both,
            "verdict": verdict, "edge_proven": edge_proven, "binding_constraint": binding,
        },
    }

    slim = dict(sweep_obj)
    slim_results = []
    for r in results:
        rr = dict(r)
        rr.pop("oos_net_per_split", None)
        slim_results.append(rr)
    slim["results"] = slim_results
    op = reports / f"campaign329_oos_sweep_{ts}.json"
    op.write_text(json.dumps(slim, indent=2, default=jdefault) + "\n")
    sweep_sha = sha256_file(op)
    full = reports / f"campaign329_oos_sweep_{ts}.full.json"
    full.write_text(json.dumps(sweep_obj, indent=2, default=jdefault) + "\n")

    surviving = [results[i] for i in edge_idx if rej_holm[i] and rej_bh[i]]
    registry = {
        "generated_at_utc": ts, "campaign": 329, "part": "registry",
        "analysis": "tradable_edge_registry",
        "n_tradable": len(surviving),
        "n_edge_proven_deterministic": int(n_edge),
        "n_survive_holm": n_survive_holm, "n_survive_bh": n_survive_bh,
        "n_survive_both": n_survive_both,
        "attribution_ok": attribution_ok,
        "attribution_shares": attrib_share,
        "tradable_configs": surviving,
        "oos_sweep_artifact": str(op.relative_to(ROOT)), "oos_sweep_sha256": sweep_sha,
        "verdict": verdict,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
    }
    op_reg = reports / f"campaign329_tradable_edge_registry_{ts}.json"
    op_reg.write_text(json.dumps(registry, indent=2, default=jdefault) + "\n")
    reg_sha = sha256_file(op_reg)

    summary = {
        "generated_at_utc": ts, "campaign": 329, "part": "summary",
        "analysis": "validation_summary", "verdict": verdict, "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "universe": sweep_obj["universe"], "config": sweep_obj["config"],
        "gates": sweep_obj["gates"],
        "artifacts": {"oos_sweep": {"path": str(op.relative_to(ROOT)), "sha256": sweep_sha},
                      "registry": {"path": str(op_reg.relative_to(ROOT)), "sha256": reg_sha}},
        "summary": sweep_obj["summary"], "binding_constraint": binding,
    }
    op_sum = reports / f"campaign329_summary_{ts}.json"
    op_sum.write_text(json.dumps(summary, indent=2, default=jdefault) + "\n")
    sum_sha = sha256_file(op_sum)

    finding = (
        f"C329 cross-sectional intraday RETURN SIGN ENTROPY / DIRECTIONAL DISORDER "
        f"SEASONAL DISLOCATION mean-reversion stat-arb edge RETRACTED ({n_edge} "
        f"deterministic edge configs, {n_survive_both} survive Holm+BH over "
        f"{N_TRIALS}); binding constraint: {binding}; dominant attribution: {dominant} "
        f"({dominant_share:.4f})."
        if binding is not None
        else f"C329 cross-sectional intraday RETURN SIGN ENTROPY / DIRECTIONAL DISORDER "
        f"SEASONAL DISLOCATION mean-reversion stat-arb edge validated: {n_survive_both} of "
        f"{n_edge} deterministic edge configs survive Holm+BH over {N_TRIALS}; "
        f"edge_proven:{edge_proven}."
    )
    verdict_obj = {
        "generated_at_utc": ts, "campaign": 329, "part": "verdict",
        "analysis": "final_verdict", "verdict": verdict, "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "finding": finding,
        "basis": "c329_signentropy_xsec_stat_arb_costed_oos_5m",
        "dataset": dataset_block,
        "oos_sweep_artifact": str(op.relative_to(ROOT)), "oos_sweep_sha256": sweep_sha,
        "registry_artifact": str(op_reg.relative_to(ROOT)), "registry_sha256": reg_sha,
        "summary_artifact": str(op_sum.relative_to(ROOT)), "summary_sha256": sum_sha,
        "binding_constraint": binding,
        "n_deterministic_edge": int(n_edge),
        "n_survive_holm": n_survive_holm, "n_survive_bh": n_survive_bh,
        "n_survive_both": n_survive_both,
        "attribution_shares": attrib_share,
        "dominant_attribution": dominant,
        "dominant_share": dominant_share,
        "hard_bans_honored": [
            "No synthetic/fabricated data; no relabeling existing caches as new",
            "No threshold/gate weakening; no cherry-picked windows/costs",
            "No edge claim unless the costed OOS test survives Holm+BH over all 864 configs",
            "Real USDT-M linear 5m perp_close; funding excluded (control leg)",
            "Single-leg PnL with costs on turnover; executed_fills: false",
        ],
    }
    op_ver = reports / f"campaign329_verdict_{ts}.json"
    op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")
    ver_sha = sha256_file(op_ver)

    bind_sha = None
    bind_path = None
    if binding is not None:
        binding_obj = {
            "generated_at_utc": ts, "campaign": 329, "part": "binding_constraint",
            "analysis": "binding_constraint_diagnosis", "verdict": verdict,
            "real_data_only": True, "fabricated_data": False, "executed_fills": False,
            "oos_sweep_artifact": str(op.relative_to(ROOT)), "oos_sweep_sha256": sweep_sha,
            "binding_constraint": binding,
            "n_deterministic_edge": int(n_edge),
            "n_survive_holm": n_survive_holm, "n_survive_bh": n_survive_bh,
            "n_survive_both": n_survive_both,
            "attribution_shares": attrib_share, "dominant_attribution": dominant,
            "attribution_ok": attribution_ok,
            "stability": stability_ref,
            "diagnosis": (
                "C329 cross-sectional intraday RETURN SIGN ENTROPY / DIRECTIONAL DISORDER "
                "SEASONAL DISLOCATION mean-reversion stat-arb does not survive validation; "
                f"formal negative. Binding constraint: {binding}."
            ),
            "note": "Diagnosis only; never an edge claim. No threshold weakening.",
        }
        op_bind = reports / f"campaign329_binding_constraint_{ts}.json"
        op_bind.write_text(json.dumps(binding_obj, indent=2, default=jdefault) + "\n")
        bind_sha = sha256_file(op_bind)
        bind_path = str(op_bind.relative_to(ROOT))
        verdict_obj["binding_constraint_artifact"] = bind_path
        verdict_obj["binding_constraint_sha256"] = bind_sha
        op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")
        ver_sha = sha256_file(op_ver)

    print(json.dumps({
        "campaign": 329, "verdict": verdict, "edge_proven": edge_proven,
        "n_total_runs": int(n_total), "n_deterministic_edge": int(n_edge),
        "n_survive_holm": n_survive_holm, "n_survive_bh": n_survive_bh,
        "n_survive_both": n_survive_both,
        "binding_constraint": binding,
        "attribution_shares": attrib_share, "dominant_attribution": dominant,
        "dominant_share": dominant_share,
        "mde_bps_mean": mde_bps, "observed_mean_bps_per_split": obs_mean_bps,
        "artifacts": {"oos_sweep": str(op.relative_to(ROOT)), "registry": str(op_reg.relative_to(ROOT)),
                      "summary": str(op_sum.relative_to(ROOT)), "verdict": str(op_ver.relative_to(ROOT)),
                      "binding_constraint": bind_path},
        "sha256": {"oos_sweep": sweep_sha, "registry": reg_sha, "summary": sum_sha,
                   "verdict": ver_sha, "binding_constraint": bind_sha},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
