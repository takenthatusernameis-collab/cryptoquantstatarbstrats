#!/usr/bin/env python3
"""C357 — rigorous costed out-of-sample test of the cross-sectional intraday
LEMPEL–ZIV COMPLEXITY (LZC, LZ76 / Kaspar–Schuster) × SEASONAL-DISLOCATION
mean-reversion stat-arb family on 10 USDT-M linear perps at native 5m
(1296 pre-registered configs).

GENUINELY NEW FAMILY (not a re-skin of any frozen modern campaign)
-----------------------------------------------------------------
C281B-C356 (all FROZEN formal negatives) exhausted carry, OFI/microstructure,
premium/index/mark basis, quarterly term-structure, same-asset spot-perp
lead-lag, autocorrelation/chop/vol-clustering/close-envelope/rescaled-range/
drawdown-duration/realized-variance-concentration/ordinal-pattern-entropy/
DFA-scaling-exponent/GPH-log-periodogram/local-Whittle/variance-ratio/
Higuchi-fractal-dimension/sample-entropy/multiscale-entropy families.
C357 is the first modern campaign to trade each asset's CAUSAL trailing same-
(TOD x DOW) seasonal deviation of its NORMALIZED LEMPEL–ZIV COMPLEXITY:

    For each bar t, take trailing W=256 returns X = r[t-W+1 .. t].
    (A) Sign binary sequence: s[i] = 1 if X[i] >= 0 else 0, i=0..W-1.
    (B) Magnitude-threshold binary sequence: med = median(|X|) over the window;
        m[i] = 1 if |X[i]| >= med else 0, i=0..W-1.
    (C) LZ76 phrase count c(N) via exhaustive parsing of each length-N=W binary
        sequence: c = number of phrases, where the phrase at position i is the
        shortest prefix of S[i:] that does NOT occur as a substring of S[:i].
    (D) Normalized LZC: LZC_norm = c(N) * log2(N) / N.
        lzc_sign[t] = LZC_norm(sign sequence); lzc_mag[t] = LZC_norm(mag seq).

lzc_sign (complexity of the sign/direction pattern) and lzc_mag (complexity of
the return-magnitude pattern above/below the window median) are two
genuinely-distinct real signals.

score = -(v - seasonal_mean) / seasonal_std (symmetric z-fade).

Unlike C329 (Shannon entropy of the binary SIGN sequence: probability-based
H=-sum p log p over the sign alphabet), C357 uses the LZ76 dictionary phrase
count c(N) on a binary sequence (compression-based). Unlike C344 (sign-change /
chop rate: local transition count), C357 uses a global dictionary parsing. Unlike
C349 (permutation/Bandt-Pompe entropy over m=3 rank orderings), C355 (single-scale
Sample Entropy: tolerance-based template matching), C356 (Multiscale Entropy:
coarse-grained SampEn profile), C354 (Higuchi fractal dimension: curve-length
scaling), C350 (DFA detrended fluctuation slope), C351 (GPH log-periodogram OLS
slope), C352 (local-Whittle exact MLE), C353 (variance ratio VR(q)), C346 (R/S
single-window range): C357 is Lempel–Ziv dictionary complexity. C343 (|r| autocorr),
C344 (sign-change rate), C347 (drawdown duration), C345 (close-in-envelope),
C317 (realized-vol LEVELS): C357 is LZC. C342/C340/C341 need volume/notional/
price-impact; C357 is price-only and volume-free. C315/C320 trade raw seasonal
RETURN mean-reversion — C357 fades seasonal dislocation in Lempel–Ziv complexity.
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

CACHE_DIR = cache_dir / "campaign357_lempel_ziv_5m"
CACHE_META = cache_dir / "campaign357_lempel_ziv_5m.meta.json"
CACHE_PROV = cache_dir / "campaign357_lempel_ziv_5m.provenance.json"
REQUIRED_FIELDS = ["index_ms", "perp_close", "log_return", "abs_ret", "funding_rate"]

# ---- pre-registered grid ----
SIGNALS = ("lzc_sign_dev", "lzc_mag_dev", "lzc_sign_placebo", "lzc_mag_placebo")
LOOKBACKS = (60, 120, 240, 480, 960, 1920)          # bars (seasonal baseline history)
REBALANCES = (1, 4, 12)                            # bars
FEES = (0.0004, 0.0007, 0.0010)
SLIPS = (0.0, 0.0001, 0.0002)
COST_VARIANTS = ("taker", "maker_blend")
FRAC = 1.0 / 3.0
ALPHA = 0.05
MIN_PERIODS_BASELINE = 3
PLACEBO_SEED = 20261223
TRAIN_M, TEST_M, ROLL_M = 12, 3, 3
STABILITY_MIN_SIGN_CONSISTENCY = 0.70
STABILITY_MIN_SHARPE_CORR = 0.50
DOMINANT_SHARE_MIN = 0.50

# lempel-ziv complexity parameters (fixed, pre-registered)
LZC_W = 256                                         # intrinsic window (fixed, decoupled from seasonal lookback)

TOD_BARS_PER_DAY = 288
WEEKDAYS = 7
N_BUCKETS = WEEKDAYS * TOD_BARS_PER_DAY

N_TRIALS = (len(SIGNALS) * len(LOOKBACKS) *
             len(REBALANCES) * len(FEES) * len(SLIPS) * len(COST_VARIANTS))  # 1296

# signal -> (base_metric_key, kind)
# kind in {"dev","placebo_dev"}
SIGNAL_FAMILY = {
    "lzc_sign_dev": ("lzc_sign", "dev"),
    "lzc_mag_dev": ("lzc_mag", "dev"),
    "lzc_sign_placebo": ("lzc_sign", "placebo_dev"),
    "lzc_mag_placebo": ("lzc_mag", "placebo_dev"),
}

ATTR_REPRESENTATIVES = {
    "lzc_sign_dev": "lzc_sign_dev",
    "lzc_mag_dev": "lzc_mag_dev",
}


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


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


def _phase_randomized_surrogate(x: np.ndarray, seed: int) -> np.ndarray:
    """Phase-randomized surrogate of x: same marginal distribution (rank-restored),
    temporal alignment destroyed (FFT phases randomized). Deterministic seed.
    NaN positions stay NaN."""
    n = len(x)
    out = np.full(n, np.nan, dtype=float)
    fin = np.isfinite(x)
    k = int(fin.sum())
    if k < 8:
        return out
    xf = np.asarray(x[fin], dtype=float)
    xc = xf - xf.mean()
    F = np.fft.rfft(xc)
    amp = np.abs(F)
    rng = np.random.default_rng(int(seed))
    phase = np.zeros(F.shape[0])
    if F.shape[0] > 2:
        phase[1:-1] = rng.uniform(0.0, 2.0 * np.pi, size=F.shape[0] - 2)
    F_new = amp * np.exp(1j * phase)
    y = np.fft.irfft(F_new, n=k)
    order = np.argsort(np.argsort(y))
    sorted_x = np.sort(xf)
    restored = sorted_x[order]
    out[fin] = restored
    return out


def _bucket_of(index_ms: np.ndarray) -> np.ndarray:
    """(weekday × tod) bucket id in [0, 2016) from index_ms (ms since epoch, UTC)."""
    ts = pd.to_datetime(index_ms, unit="ms", utc=True)
    dow = ts.dayofweek.to_numpy().astype(np.int64)
    secs = (ts.hour.to_numpy().astype(np.int64) * 3600
            + ts.minute.to_numpy().astype(np.int64) * 60
            + ts.second.to_numpy().astype(np.int64))
    tod = secs // 300
    return dow * TOD_BARS_PER_DAY + tod


def _same_bucket_stats_1d(bucket: np.ndarray, x: np.ndarray, window, min_periods: int):
    """Trailing mean/std of x over the same (weekday×tod) bucket, using only
    history strictly BEFORE each bar (causal). NaN-aware, min_periods gate."""
    n = len(x)
    mean = np.full(n, np.nan, dtype=float)
    std = np.full(n, np.nan, dtype=float)
    if n == 0:
        return mean, std
    order = np.argsort(bucket, kind="mergesort")
    b_sorted = bucket[order]
    x_sorted = x[order]
    uniq, starts, counts = np.unique(b_sorted, return_index=True, return_counts=True)
    mean_s = np.full(n, np.nan, dtype=float)
    std_s = np.full(n, np.nan, dtype=float)
    for u, s0, c in zip(uniq, starts, counts):
        xs = x_sorted[s0:s0 + c]
        cs = np.concatenate(([0.0], np.nancumsum(xs)))
        cs2 = np.concatenate(([0.0], np.nancumsum(np.where(np.isfinite(xs), xs * xs, 0.0))))
        cn = np.concatenate(([0], np.cumsum(np.isfinite(xs).astype(np.int64))))
        m = len(xs)
        for j in range(m):
            lo = max(0, j - window + 1)
            a, b = lo, j
            cnt = int(cn[b] - cn[a])
            if cnt >= min_periods:
                sm = cs[b] - cs[a]
                sm2 = cs2[b] - cs2[a]
                mu = sm / cnt
                var = max(0.0, sm2 / cnt - mu * mu)
                mean_s[s0 + j] = mu
                std_s[s0 + j] = math.sqrt(var)
    mean[order] = mean_s
    std[order] = std_s
    return mean, std


def _same_bucket_stats(bucket: np.ndarray, x: np.ndarray, window, min_periods: int):
    """2-D (n_assets, n_bars) version of _same_bucket_stats_1d."""
    n_assets, n_bars = x.shape
    mean = np.full((n_assets, n_bars), np.nan, dtype=float)
    std = np.full((n_assets, n_bars), np.nan, dtype=float)
    for i in range(n_assets):
        m, s = _same_bucket_stats_1d(bucket, np.asarray(x[i], dtype=float), window, min_periods)
        mean[i] = m
        std[i] = s
    return mean, std


# ---------------------------------------------------------------- lempel-ziv complexity
def _lz76_count(seq) -> int:
    """LZ76 (Kaspar–Schuster) phrase count c(N) for a binary sequence.

    At each phrase start i, the phrase is the shortest prefix of S[i:] that does
    NOT occur as a substring of S[:i] (history). Implemented via bytes.find: the
    longest prefix of S[i:] occurring at a start index < i is extended; phrase
    length = that length + 1. Returns the number of phrases c(N).
    """
    if isinstance(seq, (bytes, bytearray)):
        S = bytes(seq)
    else:
        S = bytes(1 if int(v) else 0 for v in seq)
    n = len(S)
    if n == 0:
        return 0
    i = 0
    c = 0
    while i < n:
        c += 1
        hi = n - i
        L = 0
        while L < hi:
            pref = S[i:i + L + 1]
            idx = S.find(pref)
            if idx != -1 and idx < i:
                L += 1
            else:
                break
        i += L + 1
    return c


def _lzc_norm(seq) -> float:
    """Normalized Lempel–Ziv complexity LZC_norm = c(N) * log2(N) / N."""
    n = len(seq)
    if n <= 0:
        return float("nan")
    c = _lz76_count(seq)
    return c * math.log2(n) / n


def _lzc_bruteforce(r: np.ndarray, W: int = LZC_W) -> dict:
    """Brute-force reference LZC implementation for testing.
    Returns dict with 'lzc_sign' and 'lzc_mag' arrays (NaN where undefined).
    Manual loop over windows, explicit sign & magnitude-threshold binarization,
    explicit LZ76 phrase count (shortest-unseen-prefix exhaustive parsing)."""
    n = len(r)
    lzc_sign = np.full(n, np.nan, dtype=float)
    lzc_mag = np.full(n, np.nan, dtype=float)
    if n < W:
        return {"lzc_sign": lzc_sign, "lzc_mag": lzc_mag}

    def bf_phrase_count(S):
        # authoritative reference: history = S[:i], substring match
        nS = len(S)
        if nS == 0:
            return 0
        i = 0
        c = 0
        while i < nS:
            c += 1
            L = 0
            while i + L + 1 <= nS:
                pref = S[i:i + L + 1]
                hit = False
                for s in range(0, i):
                    if S[s:s + L + 1] == pref:
                        hit = True
                        break
                if hit:
                    L += 1
                else:
                    break
            i += L + 1
        return c

    for t in range(W, n):
        window = r[t - W + 1:t + 1]
        if not np.isfinite(window).all():
            continue
        # sign sequence
        s = [1 if window[i] >= 0 else 0 for i in range(W)]
        c_s = bf_phrase_count(s)
        lzc_sign[t] = c_s * math.log2(W) / W
        # magnitude-threshold sequence
        med = float(np.median(np.abs(window)))
        m = [1 if abs(window[i]) >= med else 0 for i in range(W)]
        c_m = bf_phrase_count(m)
        lzc_mag[t] = c_m * math.log2(W) / W
    return {"lzc_sign": lzc_sign, "lzc_mag": lzc_mag}


def compute_lzc_metrics(r: np.ndarray, W: int = LZC_W) -> dict:
    """Fast Lempel–Ziv complexity for one asset over fixed intrinsic window W
    bars ending at bar t. lzc_sign[t] and lzc_mag[t] are NaN for t < W or if any
    r in the window is NaN. Passes a brute-force equality test (tests)."""
    n = len(r)
    lzc_sign = np.full(n, np.nan, dtype=float)
    lzc_mag = np.full(n, np.nan, dtype=float)
    if n < W:
        return {"lzc_sign": lzc_sign, "lzc_mag": lzc_mag}
    r_arr = np.asarray(r, dtype=float)
    if not np.isfinite(r_arr).all():
        bf = _lzc_bruteforce(r_arr, W)
        lzc_sign[:] = bf["lzc_sign"]
        lzc_mag[:] = bf["lzc_mag"]
        return {"lzc_sign": lzc_sign, "lzc_mag": lzc_mag}
    return _compute_lzc_vectorized(r_arr, W, lzc_sign, lzc_mag)


def _compute_lzc_vectorized(r: np.ndarray, W: int,
                            lzc_sign: np.ndarray, lzc_mag: np.ndarray) -> dict:
    """Lempel–Ziv complexity across all bars. For each trailing window of length
    W ending at bar t: binarize sign sequence and magnitude-threshold sequence,
    compute LZ76 phrase count c(N), normalized LZC_norm = c(N)*log2(N)/N.
    NaN for t<W (i==0 window dropped). Validated against _lzc_bruteforce."""
    from numpy.lib.stride_tricks import sliding_window_view

    n = len(r)
    n_win = n - W + 1
    if n < W or n_win <= 1:
        return {"lzc_sign": lzc_sign, "lzc_mag": lzc_mag}

    log2W = math.log2(W)
    invW = 1.0 / W

    # Extract all windows once (n_win, W); wins[i] = r[i..i+W-1], trailing
    # window ending at bar t = i + W - 1.
    wins = sliding_window_view(r, W)  # (n_win, W)
    # sign matrix: wins >= 0
    sign_u8 = (wins >= 0).astype(np.uint8)
    # magnitude-threshold matrix: |X| >= median(|X|) per row
    a = np.abs(wins)
    med = np.median(a, axis=1, keepdims=True)
    mag_u8 = (a >= med).astype(np.uint8)

    # iterate windows i=1..n_win-1 (skip i==0 -> t=W-1 < W dropped)
    for i in range(1, n_win):
        c_s = _lz76_count(sign_u8[i].tobytes())
        lzc_sign[i + W - 1] = c_s * log2W * invW
        c_m = _lz76_count(mag_u8[i].tobytes())
        lzc_mag[i + W - 1] = c_m * log2W * invW

    return {"lzc_sign": lzc_sign, "lzc_mag": lzc_mag}


def build_underlying(bs: dict) -> dict:
    """Compute the causal per-bar LZC series used by every signal.
    Returns dict with matrices (n_assets, n_bars): one entry per base metric."""
    n_assets = int(bs["n_assets"])
    n_bars = int(bs["n_bars"])
    log_return = bs["log_return"]
    series: dict = {}
    METRIC_KEYS = ("lzc_sign", "lzc_mag")
    mats = {k: np.full((n_assets, n_bars), np.nan, dtype=float) for k in METRIC_KEYS}
    for i in range(n_assets):
        m = compute_lzc_metrics(np.asarray(log_return[i], dtype=float), LZC_W)
        mats["lzc_sign"][i] = np.asarray(m["lzc_sign"], dtype=float)
        mats["lzc_mag"][i] = np.asarray(m["lzc_mag"], dtype=float)
    for k in METRIC_KEYS:
        series[k] = mats[k]
    return series


def build_scores(series: dict, bucket: np.ndarray) -> dict:
    """Compute causal score per (signal, seasonal_lookback).
    Returns {(signal, L): score(n_assets, n_bars)} shifted by 1 bar (causal).
    score = -(v - seasonal_mean) / seasonal_std."""
    scores: dict = {}
    for signal in SIGNALS:
        base, kind = SIGNAL_FAMILY[signal]
        surrogate = kind.startswith("placebo")
        for L in LOOKBACKS:
            v = series[base]  # (n_assets, n_bars)
            base_arr = np.apply_along_axis(
                lambda row: _phase_randomized_surrogate(row, PLACEBO_SEED), 1, v) if surrogate else v
            m, sd = _same_bucket_stats(bucket, base_arr, L, MIN_PERIODS_BASELINE)
            with np.errstate(divide="ignore", invalid="ignore"):
                raw = -(base_arr - m) / np.where(sd > 0, sd, np.nan)
            score = np.where((sd > 0) & np.isfinite(base_arr) & np.isfinite(m) & np.isfinite(sd),
                             raw, np.nan)
            sc = np.full_like(score, np.nan)
            sc[:, 1:] = score[:, :-1]  # causal shift(1)
            scores[(signal, int(L))] = sc
    return scores


def verify_cache() -> tuple:
    if not CACHE_META.exists():
        raise SystemExit(f"FATAL: C357 meta missing: {CACHE_META}")
    meta = json.loads(CACHE_META.read_text())
    if meta.get("real_data_only") is not True or meta.get("fabricated_data") is not False:
        raise SystemExit("FATAL: C357 cache not real_data_only/fabricated_data=false")
    if int(meta.get("campaign") or 0) != 357:
        raise SystemExit("FATAL: C357 meta campaign != 357")
    shard_sha = meta.get("shard_sha256") or {}
    symbols = list(meta.get("symbols") or [])
    payload = {"symbols": symbols, "per_asset": {}, "n_bars": int(meta.get("n_grid_bars") or 0)}
    for s in symbols:
        sp = CACHE_DIR / f"{s}.npz"
        if not sp.exists():
            raise SystemExit(f"FATAL: C357 shard missing: {sp}")
        if sha256_file(sp) != shard_sha.get(s):
            raise SystemExit(f"FATAL: C357 shard sha mismatch: {s}")
        with np.load(sp) as z:
            payload["per_asset"][s] = {k: np.asarray(z[k]) for k in REQUIRED_FIELDS}
    cache_sha = sha256_file(CACHE_META)
    meta_sha = sha256_file(CACHE_META)
    prov_sha = sha256_file(CACHE_PROV) if CACHE_PROV.exists() else None
    return payload, meta, cache_sha, meta_sha, prov_sha


def build_series(payload: dict):
    symbols = list(payload.get("symbols") or [])
    n_assets = len(symbols)
    per_asset = payload.get("per_asset") or {}
    first = per_asset[symbols[0]]
    idx_ms = np.asarray(first["index_ms"], dtype="int64")
    index = pd.DatetimeIndex(pd.to_datetime(idx_ms, unit="ms", utc=True))
    n_b = len(index)
    if n_b == 0:
        raise SystemExit("FATAL: C357 common grid is empty")
    if n_b % TOD_BARS_PER_DAY != 0:
        raise SystemExit("FATAL: C357 grid is not a whole number of 288-bar days")

    def mat(key):
        out = np.zeros((n_assets, n_b), dtype=float)
        for i, s in enumerate(symbols):
            out[i] = np.asarray(per_asset[s][key], dtype=float)
        return out

    perp_close = mat("perp_close")
    log_return = mat("log_return")
    abs_ret = mat("abs_ret")

    if not (np.isfinite(perp_close).all() and (perp_close > 0).all()):
        raise SystemExit("FATAL: non-finite/non-positive perp_close")
    if not np.isfinite(log_return).all():
        raise SystemExit("FATAL: non-finite log_return in cache")
    if not np.isfinite(abs_ret).all():
        raise SystemExit("FATAL: non-finite abs_ret in cache")

    bucket = _bucket_of(idx_ms)
    day_ord = (idx_ms // (86400 * 1000) - idx_ms[0] // (86400 * 1000)).astype(np.int64)
    n_days = n_b // TOD_BARS_PER_DAY
    if not np.array_equal(day_ord, np.repeat(np.arange(n_days), TOD_BARS_PER_DAY)):
        raise SystemExit("FATAL: day boundaries are not aligned to 288-bar UTC days")

    splits = wf_splits_by_month(index, TRAIN_M, TEST_M, ROLL_M)
    if not splits:
        raise SystemExit("FATAL: no OOS splits")

    return {"symbols": symbols, "n_assets": n_assets, "index": index, "n_bars": n_b,
            "n_days": n_days, "perp_close": perp_close, "log_return": log_return,
            "abs_ret": abs_ret, "bucket": bucket, "splits": splits}


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


def cost_rate(fee: float, slip: float, cv: str) -> float:
    if cv == "taker":
        return fee + slip
    return 0.5 * fee + slip


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

    series = build_underlying(bs)
    scores = build_scores(series, bs["bucket"])

    gross_turn_cache: dict = {}

    def get_gross_turn(signal: str, L: int, H: int):
        key = (signal, L, H)
        if key in gross_turn_cache:
            return gross_turn_cache[key]
        sc = scores[(signal, L)]
        pos = xsec_positions(sc, FRAC, H)
        gross = (pos * perp_ret).sum(axis=0)
        dpos = np.abs(np.diff(pos, axis=1, prepend=pos[:, :1]))
        turn = dpos.sum(axis=0)
        gross_turn_cache[key] = (gross, turn)
        return gross, turn

    results: list[dict] = []

    def run_config(signal: str, L: int, H: int, fee: float, slip: float, cv: str):
        gross, turn = get_gross_turn(signal, L, H)
        cost_rate_val = cost_rate(fee, slip, cv)
        seg_gross, seg_turn, seg_len = [], [], []
        for (tr_s, tr_e, te_s, te_e) in splits:
            seg_gross.append(float(gross[te_s:te_e].sum()))
            seg_turn.append(float(turn[te_s:te_e].sum()))
            seg_len.append(int(te_e - te_s))
        net = [g - cost_rate_val * t for g, t in zip(seg_gross, seg_turn)]
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
            "fee": float(fee), "slippage": float(slip), "cost_variant": cv,
            "n_splits": int(n_splits),
            "oos_net_sum": net_sum, "oos_net_mean": net_mean,
            "oos_net_per_split": [float(x) for x in net],
            "gross_sum": float(sum(seg_gross)), "turnover_total": float(sum(seg_turn)),
            "edge_proven": bool(all_pos), "p_value": float(p_val),
            "per_split_mean_bps": per_split_bps, "sharpe_obs": float(sr),
            "mde_bps": float(mde_bps),
            "cost_rate_bps_effective": float(cost_rate_val * 10000.0),
        }

    ref_cfg = dict(signal="lzc_sign_dev", L=240, H=4,
                   fee=0.0007, slip=0.0001, cv="taker")
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

    # ---- signal-vs-placebo attribution (mean |OOS net| share per signal across all its configs) ----
    signal_nets: dict = {s: [] for s in SIGNALS}
    for r in results:
        signal_nets[r["signal"]].append(r["oos_net_mean"])
    attrib = {s: abs(float(np.mean(signal_nets[s]))) if signal_nets[s] else 0.0 for s in SIGNALS}
    attrib_total = sum(attrib.values())
    if attrib_total > 0:
        attrib_share = {k: float(v / attrib_total) for k, v in attrib.items()}
    else:
        attrib_share = {k: 0.0 for k in SIGNALS}
    dominant = max(attrib_share, key=attrib_share.get) if attrib_total > 0 else None
    dominant_share = float(attrib_share[dominant]) if dominant else 0.0
    attribution_ok = bool(dominant in ATTR_REPRESENTATIVES
                          and dominant_share >= DOMINANT_SHARE_MIN)

    def stability():
        gross, turn = get_gross_turn(ref_cfg["signal"], ref_cfg["L"], ref_cfg["H"])
        cr = cost_rate(ref_cfg["fee"], ref_cfg["slip"], ref_cfg["cv"])
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
            "reference_config": ref_cfg,
            "per_split_net": [float(x) for x in seg_nets],
            "sign_consistency": sign_consistency,
            "first_half_sharpe": _sharpe(first),
            "second_half_sharpe": _sharpe(second),
            "sharpe_corr": sharpe_corr,
            "stable": stable,
        }

    stability_ref = stability()

    sc_ref = scores[(ref_cfg["signal"], ref_cfg["L"])]
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
        "generated_at_utc": ts, "campaign": 357, "part": "oos_sweep",
        "analysis": "c357_lempel_ziv_xsec_stat_arb_oos_5m",
        "verdict": verdict, "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "fail_closed": True,
        "mandate": (
            "C357 — test the cross-sectional intraday LEMPEL–ZIV COMPLEXITY (LZC) "
            "x SEASONAL-DISLOCATION mean-reversion stat-arb family on 10 USDT-M "
            "linear perps at native 5m (1296 pre-registered configs). Per-bar "
            "primitives: log_return=log(c[t]/c[t-1]) (r[0]=0) from real perp_close; "
            "abs_ret=|log_return|. Lempel–Ziv complexity metric over fixed intrinsic "
            "window W=256 bars ending at bar t: sign sequence s[i]=1 if r>=0 else 0; "
            "magnitude-threshold sequence m[i]=1 if |r|>=median(|X|) else 0; LZ76 "
            "phrase count c(N) (exhaustive shortest-unseen-prefix parsing) on each "
            "length-N=W binary sequence; LZC_norm=c(N)*log2(N)/N. "
            "Seasonal baseline = trailing mean/std at same (weekday,tod) bucket from "
            "history strictly before bar t (causal shift(1)), NaN-aware, excluding "
            "NaN obs. Signals: 2 real (lzc_sign_dev, lzc_mag_dev) + 2 placebos "
            "(phase-randomized surrogates, never edges). Single-leg dollar-neutral "
            "perp PnL with costs on turnover (taker=fee+slip; maker_blend=0.5*fee+slip). "
            "Gates: Holm+BH at alpha=0.05 (BOTH), MDE, stability, "
            "signal-vs-placebo attribution. PRE-REGISTERED NaN policy: metric NaN "
            "unless sufficient finite obs and valid denominators; seasonal stats "
            "NaN-aware min_periods excluding NaN obs; NaN-score bars weight 0."
        ),
        "preflight": dataset_block, "data_source": dataset_block,
        "universe": {"symbols": symbols, "n_assets": bs["n_assets"],
                     "common_grid_bars": int(n_b),
                     "common_grid_start_utc": str(index[0]),
                     "common_grid_end_utc": str(index[-1]),
                     "n_splits": int(n_splits)},
        "config": {
            "walk_forward": {"train_m": TRAIN_M, "test_m": TEST_M, "roll_m": ROLL_M},
            "signals": list(SIGNALS), "lookbacks_bars": list(LOOKBACKS),
            "rebalances_bars": list(REBALANCES),
            "fee": list(FEES), "slippage": list(SLIPS),
            "selection_frac": float(FRAC), "cost_variants": list(COST_VARIANTS),
            "placebo_seed": int(PLACEBO_SEED),
            "min_periods_baseline": MIN_PERIODS_BASELINE,
            "alpha": ALPHA, "n_trials": N_TRIALS, "total_runs": n_total,
            "lzc_params": {"W": LZC_W,
                           "binary_sequences": ["sign (r>=0)", "magnitude_threshold (|r|>=median|X|)"],
                           "phrase_count": "LZ76_kaspar_schuster_exhaustive_parsing",
                           "normalization": "c(N)*log2(N)/N"},
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
                "reference_config": ref_cfg,
                **{f"{s}_net": signal_nets[s] and float(np.mean(signal_nets[s])) or 0.0 for s in SIGNALS},
                "shares": attrib_share, "dominant": dominant,
                "dominant_share": dominant_share, "attribution_ok": attribution_ok,
                "placebo_seed": int(PLACEBO_SEED),
            },
            "data_quality": {
                "reference_signal": ref_cfg["signal"], "reference_lookback": int(ref_cfg["L"]),
                "reference_score_nan_share": sc_ref_nan_share,
                "note": "metric NaN share dominated by t<W=256 window requirement.",
            },
        },
        "methodology": {
            "buckets": "(weekday,tod)=dayofweek*288+seconds-of-day//300 (0..2015), exact 288 bars per UTC day.",
            "raw_features": "log_return=log(c[t]/c[t-1]) (r[0]=0) from real strictly-positive perp_close; abs_ret=|log_return|.",
            "primitives": "fixed intrinsic window W=256 bars ending at t: sign sequence s[i]=1 if r>=0 else 0; magnitude-threshold sequence m[i]=1 if |r|>=median(|X|) else 0; LZ76 phrase count c(N) via exhaustive shortest-unseen-prefix parsing on each length-N=W binary sequence; LZC_norm=c(N)*log2(N)/N. Real signals lzc_sign[t] and lzc_mag[t].",
            "signals": "lzc_sign/lzc_mag over fixed W=256; score=-(v-m)/sd with m/sd trailing same-bucket mean/std (min_periods=3, excluding NaN, causal shift(1)); cross-sectional rank, dollar-neutral gross 1.0; NaN-score assets weight 0.",
            "pnl": "single-leg perp: pnl = sum_i pos_i * perp_ret_i.",
            "costs": "charged on turnover; taker = fee+slip; maker_blend = 0.5*fee+slip.",
            "missing_data": "non-finite -> NaN; never impute/ffill; insufficient valid obs -> NaN -> not traded (fail-closed).",
            "multiple_testing": "one-sided paired t-test of per-split OOS net vs 0; Holm step-down AND Benjamini-Hochberg over all 1296 configs at alpha=0.05.",
            "mde": "two-sided alpha=0.05, power=0.80: (t_{0.975}+t_{0.80})*s/sqrt(n_splits).",
            "attribution": "mean |OOS net| per signal across all its configs; shares=|mean|/sum(|means|) over all 4 signals incl. placebos; dominant must be a real (non-placebo) signal with share >= 0.5 for attribution_ok.",
            "stability": "sign consistency >= 0.70 of splits AND first/second-half Sharpe corr >= 0.5.",
            "placebo": "phase-randomized surrogate via FFT phase randomization + rank restoration to original marginal; deterministic seed recorded; same marginal distribution, destroyed temporal alignment.",
            "lzc_invariance_note": "LZ76 phrase count c(N) depends only on the binary pattern (sign or magnitude-threshold), invariant to monotone transforms of |r| and to the constant-per-bar shift of the z-score. Validated against brute force in tests.",
            "funding": "USDT-M funding unreachable (fapi 451) -> excluded (control leg).",
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
    op = reports / f"campaign357_oos_sweep_{ts}.json"
    op.write_text(json.dumps(slim, indent=2, default=jdefault) + "\n")
    sweep_sha = sha256_file(op)
    full = reports / f"campaign357_oos_sweep_{ts}.full.json"
    full.write_text(json.dumps(sweep_obj, indent=2, default=jdefault) + "\n")

    surviving = [results[i] for i in edge_idx if rej_holm[i] and rej_bh[i]]
    registry = {
        "generated_at_utc": ts, "campaign": 357, "part": "registry",
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
    op_reg = reports / f"campaign357_tradable_edge_registry_{ts}.json"
    op_reg.write_text(json.dumps(registry, indent=2, default=jdefault) + "\n")
    reg_sha = sha256_file(op_reg)

    summary = {
        "generated_at_utc": ts, "campaign": 357, "part": "summary",
        "analysis": "validation_summary", "verdict": verdict, "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "universe": sweep_obj["universe"], "config": sweep_obj["config"],
        "gates": sweep_obj["gates"], "summary": sweep_obj["summary"],
        "oos_sweep_artifact": str(op.relative_to(ROOT)), "oos_sweep_sha256": sweep_sha,
        "registry_artifact": str(op_reg.relative_to(ROOT)), "registry_sha256": reg_sha,
    }
    op_sum = reports / f"campaign357_summary_{ts}.json"
    op_sum.write_text(json.dumps(summary, indent=2, default=jdefault) + "\n")
    sum_sha = sha256_file(op_sum)

    verdict_obj = {
        "generated_at_utc": ts, "campaign": 357, "part": "verdict",
        "analysis": "final_verdict",
        "verdict": verdict, "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
        "finding": (
            f"C357 cross-sectional intraday Lempel–Ziv Complexity "
            f"x seasonal-dislocation mean-reversion stat-arb edge {verdict} "
            f"({n_edge} deterministic edge configs, {n_survive_both} "
            f"survive Holm+BH over {n_total}); binding constraint: {binding}; "
            f"dominant attribution: {dominant} ({dominant_share:.4f})."
        ),
        "basis": "c357_lempel_ziv_xsec_stat_arb_costed_oos_5m",
        "dataset": dataset_block,
        "oos_sweep_artifact": str(op.relative_to(ROOT)), "oos_sweep_sha256": sweep_sha,
        "registry_artifact": str(op_reg.relative_to(ROOT)), "registry_sha256": reg_sha,
        "summary_artifact": str(op_sum.relative_to(ROOT)), "summary_sha256": sum_sha,
        "binding_constraint": binding,
        "n_deterministic_edge": int(n_edge),
        "n_survive_holm": n_survive_holm, "n_survive_bh": n_survive_bh,
        "n_survive_both": n_survive_both,
        "attribution_shares": attrib_share,
        "dominant_attribution": dominant, "dominant_share": dominant_share,
        "hard_bans_honored": [
            "No synthetic/fabricated data; no relabeling existing caches as new",
            "No threshold/gate weakening; no cherry-picked windows/costs",
            "No edge claim unless the costed OOS test survives Holm+BH over all 1296 configs",
            "Real USDT-M linear 5m perp_close; funding excluded (control leg)",
            "Single-leg PnL with costs on turnover; executed_fills: false",
            "Only RNG is recorded-seed placebo phase randomization (not market data)",
        ],
        "binding_constraint_artifact": None,
        "binding_constraint_sha256": None,
    }
    binding_obj = {
        "generated_at_utc": ts, "campaign": 357, "part": "binding_constraint",
        "binding_constraint": binding,
        "n_survive_both": n_survive_both, "n_edge_proven": n_edge,
        "attribution_ok": attribution_ok, "dominant": dominant,
        "dominant_share": dominant_share,
        "stable": stability_ref["stable"],
        "verdict": verdict, "edge_proven": edge_proven,
        "real_data_only": True, "fabricated_data": False, "executed_fills": False,
    }
    op_bc = reports / f"campaign357_binding_constraint_{ts}.json"
    op_bc.write_text(json.dumps(binding_obj, indent=2, default=jdefault) + "\n")
    bc_sha = sha256_file(op_bc)
    verdict_obj["binding_constraint_artifact"] = str(op_bc.relative_to(ROOT))
    verdict_obj["binding_constraint_sha256"] = bc_sha

    op_ver = reports / f"campaign357_verdict_{ts}.json"
    op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")

    print(json.dumps({
        "campaign": 357, "verdict": verdict, "edge_proven": edge_proven,
        "n_total": n_total, "n_survive_both": n_survive_both,
        "dominant": dominant, "dominant_share": dominant_share,
        "binding": binding,
        "oos_sweep": str(op.relative_to(ROOT)),
        "oos_sweep_sha256": sweep_sha,
        "registry_sha256": reg_sha, "summary_sha256": sum_sha,
        "binding_constraint_sha256": bc_sha,
        "verdict_sha256": sha256_file(op_ver),
    }, indent=2, default=jdefault))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())