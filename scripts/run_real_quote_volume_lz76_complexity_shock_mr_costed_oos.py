#!/usr/bin/env python3
"""Campaign #93 R-B (fail-closed, real data only): real_quote_volume-conditioned
Rolling Lempel–Ziv (LZ76) algorithmic/phrase-parsing complexity shock MR on a
median-dichotomized log-volume change sequence (real Binance spot quote volume
klines col 5) + real cached spot 1h.

PRE-STATED HYPOTHESIS (fixed before seeing OOS results): "Volume Lempel–Ziv LZ76
Algorithmic Complexity Shock MR"
- For each asset, compute log-volume changes r_t = ln(v_t) - ln(v_{t-1}) (v_t =
  quote_volume_usdt, positive finite). Over a causal trailing lookback W=168h form
  a binary sequence s_t in {0,1} by median-dichotomizing r within the window:
  s_t = 1 if r_t >= median(r_{t-W+1:t}) else 0 (deterministic, causal; ties -> 1).
- Compute the Lempel–Ziv 76 (LZ76) phrase-parsing complexity c(n) = the number of
  distinct phrases produced by the Lempel–Ziv parsing of the binary sequence of
  length n. Normalize: LZC = c(n) * log2(n) / n (asymptotic-normalized, standard;
  for very short n use raw c(n)/n guard). This is an ALGORITHMIC/COMPRESSION
  (dictionary-phrase parsing, Kolmogorov-complexity proxy) measure — it counts
  parsed dictionary phrases, not symbol probabilities.
- Causal z-score of LZC (lookback ZLB=168h). Trade LZ76 complexity SHOCKS as MR
  (fade extreme algorithmic-complexity shocks):
    if dz >= ENTRY_Z (1.25): SHORT  (fade unusually HIGH complexity / irregularity shock)
    if dz <= -ENTRY_Z (-1.25): LONG  (fade unusually LOW complexity / regularity shock)
  Exit: |dz| < EXIT_Z (0.25) OR hold >= MAX_HOLD (12h) OR signal flips.
- Execution shift t -> t+1. Walk-forward: rolling 720/168/168 (train/test/step).
- Cost grid bps (fee,slip): [[0,0],[5,5],[10,10],[20,20],[40,40]]. Benchmark: B&H
  per asset (gross) on union of OOS WF windows.
- Pre-stated edge rule (fail-closed): oos_edge_proven=true IFF OOS exposure>0 AND
  for ALL cost-grid slices OOS net sum > 0 AND mean OOS net mean beats mean B&H OOS
  mean on same WF windows. Else false. No in-sample tuning, no threshold weakening.

DISTINCTNESS (vs C23/C40-C92, mechanically stated) — NON-LOCATION, NON-TP,
NON-WALD–WOLFOWITZ-RUNS, NON-MEAN-RUN-LENGTH-PERSISTENCE, NON-VARIANCE-RATIO,
NON-BDS, NON-OU/HL, NON-DISPERSION, NON-ENTROPY, NON-SKEW/KURTOSIS,
NON-SINGLE-LAG-ACF TRANSFORM:
- LZ76 complexity c(n) is an ALGORITHMIC/COMPRESSION (dictionary-PHRASE PARSING)
  complexity: it scans a sequence left-to-right and increments a phrase count
  whenever the current substring is NOT a substring of the history (the
  Lempel–Ziv parsing into distinct phrases). The signal is the normalized phrase
  count — a Kolmogorov-complexity proxy measuring structural/parsing complexity.
- NON-ENTROPY (vs C-scope Shannon/permutation/sample/Renyi2 entropy families):
  entropy measures are SYMBOL-PROBABILITY / ORDINAL-PATTERN INFORMATION measures
  computed from distributions (e.g., p*log(p) over symbols, ordinal pattern
  frequencies, template-match probabilities). LZ76 counts PARSED DICTIONARY PHRASES
  via substring parsing — a combinatorial compression/dictionary object, NOT a
  probability-distribution information measure. Different mathematical object and
  different phenomenon (structural phrase novelty vs distributional uncertainty).
- NON-WW-runs (vs C88) / NON-MEAN-RUN-LENGTH-PERSISTENCE (vs C89) / NON-TP (vs C87):
  C88 is a standardized TOTAL-RUN-COUNT randomness statistic (how many contiguous
  same-sign runs). C89 is mean DURATION (length) of contiguous runs. C87 counts
  LOCAL PEAK/TROUGH REVERSALS (triplet oscillation) of consecutive raw differences.
  LZ76 counts DISTINCT PHRASES in a parsing dictionary — it does NOT count runs,
  run durations, or reversals. A sequence can have few runs but high LZ complexity
  (alternating patterns parsed into many phrases) or many runs but constrained
  parsing; the objects (phrase dictionary vs run/reversal counts/durations) differ.
- NON-BDS (vs C91): C91 BDS V_m=C_m-C_1^m is a CORRELATION-INTEGRAL /
  EMBEDDING-DIMENSION NONLINEAR-INDEPENDENCE test on delay-embedded change vectors
  (pair proximity in m-space). LZ76 is a 1D phrase-parsing compression count on a
  dichotomized binary sequence — no embedding, no correlation integral, no C_m.
- NON-VARIANCE-RATIO (vs C90): VR(q) is a multi-horizon VARIANCE-SCALING ratio
  (second-moment). LZ76 is a phrase-parsing complexity count.
- NON-OU/HL (vs C92): OU/HL is a parametric AR(1) LEVELS regression yielding a
  mean-reversion SPEED/HALF-LIFE timescale (theta, HL). LZ76 is a combinatorial
  parsing complexity of a dichotomized change sequence — no regression, no timescale.
- NON-SINGLE-LAG-ACF (explicit): not a normalized covariance/correlation at any lag.
- NON-LOCATION (explicitly NOT used): not C86 Hodges–Lehmann, C85 Gastwirth,
  C84 Midhinge, C83 Tukey trimean. LZ76 is a complexity measure, not a level.
- NON-DISPERSION/SKEW/KURTOSIS: not MAD/AAD/IQR/IDR/range/semi-variance/
  Gini/Theil/CV (dispersion magnitude), not skewness/Bowley/Kelly/kurtosis (shape).
- Data source identical (real Binance spot quote volume) but TRANSFORM is
  mechanically different: rolling LZ76 phrase-parsing algorithmic complexity of
  median-dichotomized log-volume changes.
"""
from __future__ import annotations

import hashlib
import json
import math
import pickle
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
CACHE_DIR = ROOT / "data" / "cache"
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)
TS = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

SPOT_CACHE = "0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7"
VOL_META = CACHE_DIR / "volume_1h_full.meta.json"
VOL_PROV = CACHE_DIR / "volume_1h_full.provenance.json"
COST_GRID = [[0, 0], [5, 5], [10, 10], [20, 20], [40, 40]]
TRAIN, TEST, STEP = 720, 168, 168
W_LZ, ZLB, ENTRY_Z, EXIT_Z, MAX_HOLD = 168, 168, 1.25, 0.25, 12
CAMPAIGN = 93
PRIOR_UNBLOCK = "reports/real_feed_unblock_status_20261106T130243Z.json"
PRIOR_UNBLOCK_SHA = "49699fadedfd0802ad4bf43fcf95eaff4a67ddfbc9611513221800aafc7a6d80"
PRIOR_REGISTRY = "reports/strategy_edge_registry_20261106T142846Z.json"
PRIOR_REGISTRY_SHA = "f47ca60e7fa36067c5f214815d7663638c2e1692dbcf5693e31f2bab75279"
PRIOR_C92_RB = "reports/real_quote_volume_ou_halflife_shock_mr_costed_oos_20261106T142846Z.json"
PRIOR_C92_RB_SHA = "d7237f2967485234841d84319b1ff1b027b29a804646f3ec192892487eecb8ad"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def wf_windows(n):
    ws = []
    start = 0
    while start + TRAIN + TEST <= n:
        ws.append((start, start + TRAIN, start + TRAIN + TEST))
        start += STEP
    return ws


def lz76_complexity_norm(binary: np.ndarray) -> float:
    """LZ76 phrase-parsing complexity c(n) on a binary 0/1 sequence, normalized.
    Returns c(n) * log2(n) / n (-> ~1 for random binary). Fail-closed NaN if
    sequence is too short/degenerate."""
    s = np.asarray(binary, dtype=np.int8)
    s = s[np.isfinite(binary) if np.issubdtype(binary.dtype, np.floating) else np.ones(len(binary), bool)]
    n = len(s)
    if n < 16:
        return np.nan
    # Degenerate constant sequence => minimal complexity
    if s.min() == s.max():
        # c(n)=2 phrases conceptually for constant; normalized -> 0 in limit
        c = 2
        return float(c * math.log2(n) / n)
    # LZ76 parsing (Kaspar–Schuster style)
    i = 0
    k = 1
    l = 1
    c = 1
    k_max = 1
    # work on Python list for simple slicing semantics
    seq = s.tolist()
    while True:
        if seq[i + k - 1] == seq[l + k - 1]:
            k += 1
            if l + k > n:
                c += 1
                break
        else:
            if k > k_max:
                k_max = k
            i += 1
            if i == l:
                c += 1
                l += k_max
                if l + 1 > n:
                    break
                i = 0
                k = 1
                k_max = 1
            else:
                k = 1
    if c < 1 or not math.isfinite(c):
        return np.nan
    norm = c * math.log2(n) / n
    return float(norm) if math.isfinite(norm) else np.nan


def rolling_lz76(logv: np.ndarray, w: int) -> np.ndarray:
    out = np.full(len(logv), np.nan)
    r = np.full(len(logv), np.nan)
    r[1:] = np.diff(logv)
    for i in range(w, len(logv)):
        win = r[i - w + 1 : i + 1]
        if not np.isfinite(win).all() or len(win) < w:
            continue
        med = np.median(win)
        binary = (win >= med).astype(np.int8)
        out[i] = lz76_complexity_norm(binary)
    return out


def rolling_z(x: np.ndarray, lb: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    for i in range(lb - 1, len(x)):
        win = x[i - lb + 1 : i + 1]
        win = win[np.isfinite(win)]
        if win.size < max(30, lb // 3):
            continue
        mu = win.mean()
        sd = win.std(ddof=0)
        if sd <= 1e-18 or not np.isfinite(x[i]):
            continue
        out[i] = (x[i] - mu) / sd
    return out


def run_asset(prices: pd.Series, vol: pd.Series):
    idx = prices.index.intersection(vol.index)
    p = prices.reindex(idx).astype(float)
    v = pd.to_numeric(vol.reindex(idx), errors="coerce")
    mask = p.notna() & v.notna() & (v > 0)
    p, v = p[mask], v[mask]
    n = len(p)
    ret = p.pct_change().fillna(0.0).values
    logv = np.log(v.values.astype(float))
    feat = rolling_lz76(logv, W_LZ)
    dz = rolling_z(feat, ZLB)
    sig = np.zeros(n)
    cur = 0.0
    hold = 0
    warm = max(W_LZ, ZLB) + 4
    for i in range(warm, n):
        z = dz[i]
        if not np.isfinite(z):
            nxt = cur
            hold = hold + 1 if cur != 0 else 0
        else:
            desired = 0.0
            if z >= ENTRY_Z:
                desired = -1.0  # fade unusually HIGH complexity/irregularity shock
            elif z <= -ENTRY_Z:
                desired = 1.0   # fade unusually LOW complexity/regularity shock
            if cur == 0.0:
                nxt = desired
                hold = 0 if desired == 0 else 1
            else:
                hold += 1
                flip = desired != 0 and desired != cur
                exit_cond = (abs(z) < EXIT_Z) or (hold >= MAX_HOLD) or flip
                if exit_cond:
                    nxt = desired if flip else 0.0
                    hold = 0 if nxt == 0 else 1
                else:
                    nxt = cur
        cur = nxt
        if i + 1 < n:
            sig[i + 1] = cur
    gross = sig * ret
    turn = np.abs(np.diff(np.r_[0.0, sig]))
    ws = wf_windows(n)
    oos_union = np.zeros(n, dtype=bool)
    for _, tr_e, te_e in ws:
        oos_union[tr_e:te_e] = True
    oos_ret_bh = ret[oos_union]
    bh_oos = float(np.nansum(oos_ret_bh)) if oos_ret_bh.size else 0.0
    bh_oos_mean = float(np.nanmean(oos_ret_bh)) if oos_ret_bh.size else 0.0
    slices = {}
    for fee, slip in COST_GRID:
        cr = (fee + slip) / 10000.0
        net = gross - turn * cr
        oos_net = net[oos_union]
        oos_sum = float(np.nansum(oos_net))
        oos_mean = float(np.nanmean(oos_net)) if oos_net.size else 0.0
        key = f"fee{fee}_slip{slip}"
        slices[key] = {
            "oos_net_sum": oos_sum,
            "oos_net_mean": oos_mean,
            "oos_bh_sum": bh_oos,
            "oos_bh_mean": bh_oos_mean,
            "oos_net_gt_zero": oos_sum > 0,
            "oos_net_beats_bh_mean": oos_mean > bh_oos_mean,
            "total_turnover": float(np.nansum(turn)),
        }
    edge = bool(
        ((np.abs(sig[oos_union]) > 0).sum() > 0 if oos_union.any() else False)
        and all(s["oos_net_gt_zero"] and s["oos_net_beats_bh_mean"] for s in slices.values())
    )
    return {
        "n_bars": n,
        "window_start": str(idx[0]) if n else None,
        "window_end": str(idx[-1]) if n else None,
        "n_wf_folds": len(ws),
        "has_exposure_oos": bool((np.abs(sig[oos_union]) > 0).sum() > 0) if oos_union.any() else False,
        "n_active_bars_oos": int((np.abs(sig[oos_union]) > 0).sum()) if oos_union.any() else 0,
        "bh_oos_sum": bh_oos,
        "bh_oos_mean": bh_oos_mean,
        "cost_slices": slices,
        "oos_edge_proven": edge,
    }


def main():
    spot = pickle.load(open(CACHE_DIR / f"{SPOT_CACHE}.pkl", "rb"))
    spot_sha = sha256_file(CACHE_DIR / f"{SPOT_CACHE}.pkl")
    from data.real_feed_loader import validate_and_load_real_feed

    prov = json.loads(VOL_PROV.read_text(encoding="utf-8"))
    vol_df, vol_report = validate_and_load_real_feed(VOL_META, "real_quote_volume", provenance=prov)
    vol_wide = (
        vol_df.pivot_table(index="timestamp_utc", columns="symbol", values="quote_volume_usdt", aggfunc="first")
        .sort_index()
    )
    if spot.index.tz is None:
        spot.index = spot.index.tz_localize("UTC")
    if vol_wide.index.tz is None:
        vol_wide.index = vol_wide.index.tz_localize("UTC")
    per = {}
    syms = [s for s in spot.columns if s in vol_wide.columns]
    for sym in syms:
        per[sym] = run_asset(spot[sym], vol_wide[sym])
    agg = {k: {sk: 0.0 for sk in [f"fee{f}_slip{s}" for f, s in COST_GRID]} for k in ["oos_net_sum", "oos_net_mean"]}
    for sym, r in per.items():
        for sk, v in r["cost_slices"].items():
            agg["oos_net_sum"][sk] += v["oos_net_sum"]
            agg["oos_net_mean"][sk] += v["oos_net_mean"]
    n = max(1, len(per))
    for sk in agg["oos_net_mean"]:
        agg["oos_net_mean"][sk] /= n
    any_exp = any(r["has_exposure_oos"] for r in per.values())
    all_pos = all(agg["oos_net_sum"][sk] > 0 for sk in agg["oos_net_sum"])
    bh_mean = float(np.mean([r["bh_oos_mean"] for r in per.values()])) if per else 0.0
    beats = all(agg["oos_net_mean"][sk] > bh_mean for sk in agg["oos_net_mean"])
    edge = bool(any_exp and all_pos and beats)
    artifact = {
        "tool": "scripts/run_real_quote_volume_lz76_complexity_shock_mr_costed_oos.py",
        "generated_at_utc": TS,
        "campaign": CAMPAIGN,
        "prior_unblock": PRIOR_UNBLOCK,
        "prior_unblock_sha256": PRIOR_UNBLOCK_SHA,
        "prior_registry": PRIOR_REGISTRY,
        "prior_registry_sha256": PRIOR_REGISTRY_SHA,
        "prior_c92_rb": PRIOR_C92_RB,
        "prior_c92_rb_sha256": PRIOR_C92_RB_SHA,
        "data_source": {
            "spot_cache": SPOT_CACHE,
            "spot_cache_sha256": spot_sha,
            "volume_meta": str(VOL_META.relative_to(ROOT)),
            "volume_provenance": str(VOL_PROV.relative_to(ROOT)),
            "volume_loader_report": vol_report,
            "real_data_only": True,
            "fabricated_data": False,
            "no_proxies_labeled_real": True,
        },
        "hypothesis_prestated": {
            "id": "VOLUME_LZ76_ALGORITHMIC_COMPLEXITY_SHOCK_MR",
            "description": "Fade causal z-score shocks of rolling Lempel–Ziv 76 (LZ76) phrase-parsing algorithmic complexity (normalized c(n)*log2(n)/n) of a median-dichotomized log-volume change sequence (W=168) as algorithmic-complexity/irregularity shocks; t->t+1.",
            "lz_window": W_LZ,
            "entry_z": ENTRY_Z,
            "exit_z": EXIT_Z,
            "max_hold": MAX_HOLD,
            "z_lookback": ZLB,
            "walkforward": {"train": TRAIN, "test": TEST, "step": STEP},
            "cost_grid_bps": COST_GRID,
            "benchmark": "buy_and_hold_gross_same_oos_windows",
        },
        "distinctness_mechanical": {
            "lz76_complexity": "LZ76 phrase-parsing complexity c(n) is an ALGORITHMIC/COMPRESSION (dictionary-phrase parsing, Kolmogorov-complexity proxy): left-to-right scan incrementing a phrase count when the current substring is NOT a substring of history. Signal = normalized phrase count c(n)*log2(n)/n — structural/parsing complexity, not a probability-distribution measure.",
            "non_entropy_vs_Shannon_perm_sample_Renyi2": "Entropy families (Shannon/permutation/sample/Renyi2) are SYMBOL-PROBABILITY / ORDINAL-PATTERN INFORMATION measures from distributions (p*log p, ordinal pattern frequencies, template-match probabilities). LZ76 counts PARSED DICTIONARY PHRASES via substring parsing — a combinatorial compression/dictionary object, NOT a probability-distribution information measure. Different mathematical object/phenomenon (structural phrase novelty vs distributional uncertainty).",
            "non_WW_runs_vs_C88_non_mean_run_length_vs_C89_non_TP_vs_C87": "C88 = standardized TOTAL-RUN-COUNT randomness (contiguous same-sign runs). C89 = mean DURATION (length) of contiguous runs. C87 = LOCAL PEAK/TROUGH REVERSAL count (triplet oscillation) of consecutive raw differences. LZ76 counts DISTINCT PHRASES in a parsing dictionary — NOT runs, run durations, or reversals. Few runs can coexist with high LZ complexity (alternating patterns parsed into many phrases) and vice versa; objects differ (phrase dictionary vs run/reversal counts/durations).",
            "non_bds_vs_C91": "C91 BDS V_m=C_m-C_1^m is a CORRELATION-INTEGRAL/EMBEDDING-DIMENSION NONLINEAR-INDEPENDENCE test on delay-embedded change vectors (pair proximity in m-space). LZ76 is a 1D phrase-parsing compression count on a dichotomized binary sequence — no embedding, no correlation integral, no C_m.",
            "non_variance_ratio_vs_C90": "C90 VR(q) is multi-horizon VARIANCE-SCALING (second-moment). LZ76 is a phrase-parsing complexity count.",
            "non_ou_hl_vs_C92": "C92 OU/HL is a parametric AR(1) LEVELS regression yielding mean-reversion SPEED/HALF-LIFE timescale (theta, HL). LZ76 is a combinatorial parsing complexity of a dichotomized change sequence — no regression, no timescale.",
            "non_single_lag_acf_explicit": "Not a normalized covariance/correlation at any lag.",
            "non_location_explicit": "NOT a location estimator. Distinct from C86 Hodges–Lehmann, C85 Gastwirth, C84 Midhinge, C83 Tukey trimean. LZ76 is a complexity measure, not a level.",
            "non_dispersion_skew_kurtosis": "Not MAD/AAD/IQR/IDR/range/semi-variance/Gini/Theil/CV (dispersion magnitude), not skewness/Bowley/Kelly/kurtosis (shape).",
            "vs_C23_C40_C92": "Mechanically distinct rolling LZ76 phrase-parsing algorithmic complexity (dictionary-phrase count) transform; not in C23/C40-C92 families.",
            "data_source_identical_transform_mechanically_different": True,
        },
        "edge_rule_exact": "oos_edge_proven=true IFF OOS exposure>0 AND all cost slices OOS net sum>0 AND mean OOS net mean beats mean B&H OOS mean on same WF windows; else false.",
        "aggregate": {
            "n_assets": len(per),
            "any_exposure_oos": any_exp,
            "all_cost_slices_positive_oos_net_sum": all_pos,
            "mean_bh_oos_mean_across_assets": bh_mean,
            "all_cost_slices_beat_bh_mean_rule": beats,
            "oos_edge_proven": edge,
            "cross_asset_sum_oos_net_sum": agg["oos_net_sum"],
            "cross_asset_mean_oos_net_mean": agg["oos_net_mean"],
        },
        "per_asset": per,
        "fail_closed": True,
        "oos_edge_proven": edge,
        "conclusion": "OOS_EDGE_PROVEN" if edge else "NO_OOS_EDGE_PROVEN_FAIL_CLOSED",
    }
    out = REPORTS / f"real_quote_volume_lz76_complexity_shock_mr_costed_oos_{TS}.json"
    out.write_text(json.dumps(artifact, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps({
        "out": str(out.relative_to(ROOT)),
        "sha256": sha256_file(out),
        "oos_edge_proven": edge,
        "n_assets": len(per),
        "any_exposure": any_exp,
        "all_pos": all_pos,
        "beats_bh": beats,
        "bh_mean": bh_mean,
        "agg_net_sum": agg["oos_net_sum"],
    }, indent=2))


if __name__ == "__main__":
    main()
