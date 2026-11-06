#!/usr/bin/env python3
"""Campaign #91 R-B (fail-closed, real data only): real_quote_volume-conditioned
Rolling BDS (Brock–Dechert–Scheinkman) NONLINEAR-INDEPENDENCE / correlation-integral
embedding-dimension statistic shock MR on real Binance spot quote volume (klines col 5)
+ real cached spot 1h.

PRE-STATED HYPOTHESIS (fixed before seeing OOS results): "Volume BDS Nonlinear-Independence Shock MR"
- For each asset, define log-volume first differences r_t = ln(v_t) - ln(v_{t-1})
  (v_t = quote_volume_usdt, positive finite). Over a causal trailing lookback W=168h
  compute the BDS embedding-dimension statistic (m=2, eps=0.5*sd(window)):
    embed Y_i^(m) = (r_i,...,r_{i+m-1}); correlation integral
    C_m(eps) = (count of pairs with ||Y_i-Y_j||_inf <= eps among nm*(nm-1) pairs);
    V_m = C_m(eps) - C_1(eps)^m.
  Under an i.i.d./independence null V_m ~ 0; significant V_m indicates nonlinear
  serial dependence / higher-order structure (clustering in embedding space).
- Causal z-score of V_m (lookback ZLB=168h). Trade BDS nonlinear-independence
  STRUCTURE SHOCKS as MR (fade extreme dependence shocks):
    if dz >= ENTRY_Z (1.25): SHORT  (fade unusually strong nonlinear-dependence shock)
    if dz <= -ENTRY_Z (-1.25): LONG  (fade unusually weak/independence shock)
  Exit: |dz| < EXIT_Z (0.25) OR hold >= MAX_HOLD (12h) OR signal flips.
- Execution shift t -> t+1. Walk-forward: rolling 720/168/168 (train/test/step).
- Cost grid bps (fee,slip): [[0,0],[5,5],[10,10],[20,20],[40,40]]. Benchmark: B&H
  per asset (gross) on union of OOS WF windows.
- Pre-stated edge rule (fail-closed): oos_edge_proven=true IFF OOS exposure>0 AND
  for ALL cost-grid slices OOS net sum > 0 AND mean OOS net mean beats mean B&H OOS
  mean on same WF windows. Else false. No in-sample tuning, no threshold weakening.

DISTINCTNESS (vs C23/C40-C90, mechanically stated) — NON-LOCATION, NON-TP,
NON-WALD–WOLFOWITZ-RUNS, NON-MEAN-RUN-LENGTH-PERSISTENCE, NON-VARIANCE-RATIO,
NON-DISPERSION, NON-ENTROPY, NON-SKEW/KURTOSIS, NON-AUTOCORR TRANSFORM:
- BDS V_m = C_m(eps) - C_1(eps)^m is a CORRELATION-INTEGRAL / EMBEDDING-DIMENSION
  NONLINEAR-INDEPENDENCE test (Brock–Dechert–Scheinkman): it measures joint
  higher-order dependence by comparing the fraction of m-dimensional embedding
  vectors within distance eps to the m-th power of the 1-dimensional fraction.
  It answers "is the series i.i.d./independent or does it exhibit nonlinear
  serial dependence/embedding-space clustering?" — a joint higher-order dependence
  functional, NOT a variance-scaling ratio, NOT a dichotomized run statistic,
  NOT a reversal count, NOT a single-lag linear correlation, NOT entropy.
- NON-VARIANCE-RATIO (vs C90): C90 VR(q)=Var(r^(q))/(q*Var(r)) is a multi-horizon
  VARIANCE-SCALING ratio (Lo/Craig–MacKinlay) on q-horizon aggregated returns — a
  second-moment linear-scaling relation across horizons. BDS uses correlation
  integrals in m-dimensional EMBEDDING SPACE (max-norm proximity of delay vectors)
  to test nonlinear/higher-order independence: different object (embedding-vector
  pair proximity vs horizon variance), different functional (C_m-C_1^m correlation
  integral vs variance ratio), different phenomenon (nonlinear joint dependence vs
  linear variance scaling).
- NON-MEAN-RUN-LENGTH-PERSISTENCE (vs C89): C89 L_mean=n_kept/R is mean DURATION
  of contiguous above/below-median runs on a MEDIAN-DICHOTOMIZED sequence. BDS
  operates on CONTINUOUS log-volume changes in m-dimensional embedding space via
  pairwise max-norm correlation integrals — no dichotomy, no run lengths.
- NON-WW-RUNS (vs C88): C88 Z_WW=(R-mu_R)/sigma_R is a standardized TOTAL-RUN-
  COUNT randomness statistic on a median dichotomy. BDS is a continuous embedding-
  space correlation-integral dependence test — no dichotomy, no run count.
- NON-TP (vs C87): C87 TP counts LOCAL PEAK/TROUGH REVERSALS of consecutive raw
  differences (triplet oscillation). BDS measures m-dimensional embedding
  proximity (joint dependence across embedded lags), not reversal frequency.
- NON-AUTOCORR (vs single-lag ACF): ACF(k) is a SINGLE-LAG LINEAR covariance/
  correlation coefficient. BDS detects NONLINEAR / HIGHER-ORDER joint dependence
  across an m-lag embedding (it can be significant when all linear ACFs are ~0).
  Mechanically distinct from a single-lag linear ACF signal.
- NON-LOCATION (explicitly NOT used): not C86 Hodges–Lehmann, C85 Gastwirth,
  C84 Midhinge, C83 Tukey trimean. BDS is a correlation-integral dependence
  functional, not a level/center.
- NON-DISPERSION/ENTROPY/SKEW/KURTOSIS: not MAD/AAD/IQR/IDR/range/semi-var/
  Gini/Theil/CV (dispersion magnitude), not Shannon/permutation/sample/Renyi
  entropy (symbol-probability information/complexity), not skewness/Bowley/Kelly/
  kurtosis (shape/asymmetry/tail). BDS is an embedding-space joint-dependence
  correlation integral.
- Data source identical (real Binance spot quote volume) but TRANSFORM is
  mechanically different: rolling BDS V_m=C_m-C_1^m on log-volume changes.
"""
from __future__ import annotations

import hashlib
import json
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
M, W_BDS, ZLB, ENTRY_Z, EXIT_Z, MAX_HOLD = 2, 168, 168, 1.25, 0.25, 12
EPS_SD_FRAC = 0.5
CAMPAIGN = 91
PRIOR_UNBLOCK = "reports/real_feed_unblock_status_20261106T130243Z.json"
PRIOR_REGISTRY = "reports/strategy_edge_registry_20261106T141245Z.json"
PRIOR_REGISTRY_SHA = "ebcf60997c4d29d07460a4de0e3db59d4f81fe4a854f230c4aeff2105d5a43d9"
PRIOR_C90_RB = "reports/real_quote_volume_variance_ratio_shock_mr_costed_oos_20261106T141032Z.json"
PRIOR_C90_RB_SHA = "e192f01f7d2b2e1532565f0462d02d98e6262b138f4c0d43d3a707cabfb0e0e5"


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


def bds_vm(x: np.ndarray, m: int = M, eps_sd_frac: float = EPS_SD_FRAC) -> float:
    """BDS V_m = C_m(eps) - C_1(eps)^m (raw) on 1d window, eps=eps_sd_frac*sd."""
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    n = len(x)
    if n < m + 15:
        return np.nan
    sd = np.std(x, ddof=1)
    if not np.isfinite(sd) or sd <= 1e-18:
        return np.nan
    eps = eps_sd_frac * sd
    if eps <= 0 or not np.isfinite(eps):
        return np.nan

    def C(m_):
        nm = n - m_ + 1
        if nm <= 1:
            return np.nan
        Y = np.column_stack([x[i : i + nm] for i in range(m_)])
        count = 0
        bs = 256
        for i in range(0, nm, bs):
            a = Y[i : i + bs]
            d = np.max(np.abs(a[:, None, :] - Y[None, :, :]), axis=2)
            count += int(np.sum(d <= eps))
        return (count - nm) / (nm * (nm - 1))

    c1 = C(1)
    cm = C(m)
    if not (np.isfinite(c1) and np.isfinite(cm)) or c1 <= 0 or c1 >= 1:
        return np.nan
    v = cm - (c1 ** m)
    return float(v) if np.isfinite(v) else np.nan


def rolling_bds(logv: np.ndarray, w: int, m: int) -> np.ndarray:
    out = np.full(len(logv), np.nan)
    r_all = np.diff(logv)  # length n-1
    for i in range(w, len(logv)):
        win_r = r_all[i - w : i]
        win_r = win_r[np.isfinite(win_r)]
        out[i] = bds_vm(win_r, m=m)
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
    feat = rolling_bds(logv, W_BDS, M)
    dz = rolling_z(feat, ZLB)
    sig = np.zeros(n)
    cur = 0.0
    hold = 0
    warm = max(W_BDS, ZLB, M) + 4
    for i in range(warm, n):
        z = dz[i]
        if not np.isfinite(z):
            nxt = cur
            hold = hold + 1 if cur != 0 else 0
        else:
            desired = 0.0
            if z >= ENTRY_Z:
                desired = -1.0  # fade strong nonlinear-dependence shock
            elif z <= -ENTRY_Z:
                desired = 1.0   # fade weak/independence shock
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
        "tool": "scripts/run_real_quote_volume_bds_nonlinear_independence_shock_mr_costed_oos.py",
        "generated_at_utc": TS,
        "campaign": CAMPAIGN,
        "prior_unblock": PRIOR_UNBLOCK,
        "prior_registry": PRIOR_REGISTRY,
        "prior_registry_sha256": PRIOR_REGISTRY_SHA,
        "prior_c90_rb": PRIOR_C90_RB,
        "prior_c90_rb_sha256": PRIOR_C90_RB_SHA,
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
            "id": "VOLUME_BDS_NONLINEAR_INDEPENDENCE_SHOCK_MR",
            "description": "Fade causal z-score shocks of BDS V_m=C_m(eps)-C_1(eps)^m (m=2, eps=0.5*sd, W=168) on log-volume changes as nonlinear-independence/embedding-space dependence shocks; t->t+1.",
            "m_embedding": M,
            "eps_sd_frac": EPS_SD_FRAC,
            "bds_window": W_BDS,
            "entry_z": ENTRY_Z,
            "exit_z": EXIT_Z,
            "max_hold": MAX_HOLD,
            "z_lookback": ZLB,
            "walkforward": {"train": TRAIN, "test": TEST, "step": STEP},
            "cost_grid_bps": COST_GRID,
            "benchmark": "buy_and_hold_gross_same_oos_windows",
        },
        "distinctness_mechanical": {
            "bds_correlation_integral": "V_m=C_m(eps)-C_1(eps)^m on continuous log-volume changes r_t=ln(v_t)-ln(v_{t-1}); C_m is the fraction of m-dimensional delay-embedding vectors within max-norm eps=0.5*sd (pairwise). Under i.i.d. V_m~0; significant V_m indicates nonlinear/higher-order serial dependence (embedding-space clustering). A joint higher-order dependence functional (Brock–Dechert–Scheinkman), not variance-scaling, not dichotomized runs, not reversal count, not single-lag linear correlation, not entropy.",
            "non_variance_ratio_vs_C90": "C90 VR(q)=Var(r^(q))/(q*Var(r)) is a multi-horizon VARIANCE-SCALING ratio (second-moment linear scaling across horizon q). BDS uses correlation integrals in m-dimensional EMBEDDING SPACE (max-norm proximity of delay vectors) for nonlinear/higher-order independence — different object (embedding-vector pair proximity vs horizon variance), functional (C_m-C_1^m vs variance ratio), phenomenon (nonlinear joint dependence vs linear variance scaling).",
            "non_mean_run_length_persistence_vs_C89": "C89 L_mean=n_kept/R is mean DURATION of contiguous above/below-median runs on a MEDIAN-DICHOTOMIZED sequence. BDS operates on CONTINUOUS log-volume changes in embedding space via pairwise correlation integrals — no dichotomy, no run lengths.",
            "non_WW_runs_vs_C88": "C88 Z_WW=(R-mu_R)/sigma_R is standardized TOTAL-RUN-COUNT randomness on a median dichotomy. BDS is a continuous embedding-space correlation-integral dependence test — no dichotomy, no run count.",
            "non_TP_vs_C87": "C87 TP counts local peak/trough REVERSALS of consecutive raw differences (triplet oscillation). BDS measures m-dimensional embedding proximity (joint dependence across embedded lags), not reversal frequency.",
            "non_autocorr": "ACF(k) is a SINGLE-LAG LINEAR covariance/correlation. BDS detects NONLINEAR/HIGHER-ORDER joint dependence across an m-lag embedding (can be significant when linear ACFs ~0). Mechanically distinct from single-lag ACF signal.",
            "non_location_explicit": "NOT a location estimator. Distinct from C86 Hodges–Lehmann, C85 Gastwirth, C84 Midhinge, C83 Tukey trimean. BDS is a correlation-integral dependence functional, not a level/center.",
            "non_dispersion_entropy_skew_kurtosis": "Not MAD/AAD/IQR/IDR/range/semi-variance/Gini/Theil/CV (dispersion magnitude), not Shannon/permutation/sample/Renyi entropy (symbol-probability information/complexity), not skewness/Bowley/Kelly/kurtosis (shape/asymmetry/tail). BDS is an embedding-space joint-dependence correlation integral.",
            "vs_C23_C40_C90": "Mechanically distinct rolling BDS nonlinear-independence (correlation-integral embedding-dimension) transform on log-volume changes; not in C23/C40-C90 families.",
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
    out = REPORTS / f"real_quote_volume_bds_nonlinear_independence_shock_mr_costed_oos_{TS}.json"
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
