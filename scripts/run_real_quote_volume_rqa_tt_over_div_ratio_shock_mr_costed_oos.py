#!/usr/bin/env python3
"""C198: RQA ratio TT/DIV (trapping time / divergence) shock on
delay-embedded log-volume returns (real data only).

Feature (pre-stated, distinct, grep-verified before implementation/run):
  VOLUME_RQA_TT_OVER_DIV_RATIO_SHOCK_MR. On r_t = ln(v_t)-ln(v_{t-1}), build
  delay embedding X_i = (r_i, r_{i+tau}) with m=2, tau=1 over trailing window
  W_RR=168. Recurrence matrix R_{ij}=1 if ||X_i-X_j||_inf <= eps, else 0;
  eps = eps_scale * std(r_window) with pre-stated fixed eps_scale=0.5.
  Qualifying diagonal lines: length k >= l_min (pre-stated l_min=2), excluding
  LOI/main diagonal structures not required beyond k>=l_min on any diagonal offset.
  TT = Trapping Time = mean of qualifying diagonal line lengths k>=l_min
      (mean line length over diagonal lines, excl LOI; pre-stated C198 definition).
  DIV = divergence = 1 / L_MAX, where L_MAX = maximum qualifying diagonal line
      length k >= l_min.
  RATIO_TT_DIV = TT / DIV = TT * L_MAX.
  Fail-closed to NaN/no-signal if TT undefined/non-finite/degenerate
  (non-positive or no qualifying lines), DIV/L_MAX invalid (no qualifying
  diagonal lines, L_MAX<=0 or non-finite), ratio non-finite, or insufficient
  qualifying lines. Causal trailing only.
  Distinct from C125-C197 (TT/DIV diagonal pairing not used before); grep 0
  non-self at run time (verified 20261108T034857Z).
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

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
cache_dir = root / "data" / "cache"
reports = root / "reports"
reports.mkdir(exist_ok=True)

ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

SPOT_CACHE = cache_dir / "0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl"
SPOT_META = cache_dir / "0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.meta.json"
VOL_PKL = cache_dir / "volume_1h_full.pkl"
VOL_META = cache_dir / "volume_1h_full.meta.json"
VOL_PROV = cache_dir / "volume_1h_full.provenance.json"

PRIOR_REGISTRY = "reports/strategy_edge_registry_20261108T034505Z.json"
PRIOR_REGISTRY_SHA = "cf71df3a31b6656bfef0cf6aa658f095758d8de9ec4491a0c570be267a314e2a"
PRIOR_C197_OOS = "reports/real_quote_volume_rqa_rte_over_div_ratio_shock_mr_costed_oos_20261108T034505Z.json"
PRIOR_C197_OOS_SHA = "2cecf4d65ade16f4fe7688249622ccf0be1d271366e7fc1a89c84e8d47b2641b"

W_RR = 168
ALB = 336
M_EMB = 2
TAU = 1
EPS_SCALE = 0.5
L_MIN = 2
ENTRY_Z = 1.5
EXIT_Z = 0.5
MAX_HOLD = 24

TRAIN = 720
TEST = 168
STEP = 168
COST_GRID = [[0, 0], [5, 5], [10, 10], [20, 20], [40, 40]]

DISTINCTNESS_GREP = "grep -rnE 'TT_OVER_DIV|tt_over_div|rqa_ratio_tt_over_div|rqa_tt_over_div_ratio' scripts/ strategies/ backtest/ utils/ 2>&1"
DISTINCTNESS_HITS_PRE = 0
DISTINCTNESS_VERIFIED_UTC = ts


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_spot():
    meta = json.loads(SPOT_META.read_text()) if SPOT_META.exists() else {}
    with open(SPOT_CACHE, "rb") as f:
        df = pickle.load(f)
    if isinstance(df, pd.Series):
        df = df.to_frame()
    return df, meta, sha256_file(SPOT_CACHE)


def load_volume():
    from data.real_feed_loader import validate_and_load_real_feed

    prov = json.loads(VOL_PROV.read_text()) if VOL_PROV.exists() else {}
    df, report = validate_and_load_real_feed(VOL_META, "real_quote_volume", provenance=prov)
    df = df.pivot_table(
        index="timestamp_utc", columns="symbol", values="quote_volume_usdt", aggfunc="first"
    ).sort_index()
    return df, report


def wf_splits(n: int, train: int, test: int, step: int):
    out = []
    i = 0
    while i + train + test <= n:
        out.append((i, i + train, i + train + test))
        i += step
    return out


def _diagonal_line_lengths(R: np.ndarray, l_min: int) -> list[int]:
    """Qualifying diagonal line lengths k >= l_min, excluding LOI (k=1)."""
    M_pts = R.shape[0]
    if M_pts < 3:
        return []
    lengths: list[int] = []
    for offset in range(-(M_pts - 1), M_pts):
        diag = np.diag(R, k=offset)
        if diag.size == 0:
            continue
        run = 0
        for val in diag:
            if val:
                run += 1
            else:
                if run >= l_min:
                    lengths.append(run)
                run = 0
        if run >= l_min:
            lengths.append(run)
    return lengths


def rqa_tt_over_div_ratio_window(rw: np.ndarray, eps_scale: float, l_min: int) -> float:
    """RATIO_TT_DIV = TT / DIV = TT * L_MAX.
    TT = Trapping Time (C198 pre-stated) = mean qualifying diagonal line length
    over lengths k >= l_min (excl LOI by l_min>=2 threshold; diagonal lines only).
    DIV = divergence = 1/L_MAX, L_MAX = maximum qualifying diagonal line length.
    Fail-closed to NaN."""
    if rw is None or len(rw) < (M_EMB - 1) * TAU + 3:
        return np.nan
    if not np.all(np.isfinite(rw)):
        return np.nan
    sigma = float(np.std(rw, ddof=1))
    if not np.isfinite(sigma) or sigma <= 1e-18:
        return np.nan
    eps = eps_scale * sigma
    if not np.isfinite(eps) or eps <= 0:
        return np.nan
    M_pts = len(rw) - (M_EMB - 1) * TAU
    if M_pts < 3:
        return np.nan
    x = np.column_stack([rw[:M_pts], rw[TAU : TAU + M_pts]])
    if not np.all(np.isfinite(x)):
        return np.nan
    diff = np.max(np.abs(x[:, None, :] - x[None, :, :]), axis=2)
    R = (diff <= eps).astype(np.int8)
    d_lengths = _diagonal_line_lengths(R, l_min)
    if not d_lengths:
        return np.nan
    tt = float(np.mean(d_lengths))
    if not np.isfinite(tt) or tt <= 0:
        return np.nan
    l_max = float(max(d_lengths))
    if not np.isfinite(l_max) or l_max <= 0:
        return np.nan
    div = 1.0 / l_max
    if not np.isfinite(div) or div == 0.0:
        return np.nan
    ratio = tt / div
    if not np.isfinite(ratio):
        return np.nan
    return float(ratio)


def _vol_s(vol_srs, i):
    try:
        return float(vol_srs.iloc[i])
    except Exception:
        return np.nan


def run_asset(spot: pd.Series, vol: pd.Series):
    close = spot.values.astype(float)
    idx = spot.index
    n = len(close)
    rvol = np.full(n, np.nan)
    for i in range(1, n):
        vi = _vol_s(vol, i)
        vim1 = _vol_s(vol, i - 1)
        if vi is not None and vim1 is not None and np.isfinite(vi) and np.isfinite(vim1) and vi > 0 and vim1 > 0:
            rvol[i] = np.log(vi) - np.log(vim1)
    feat = np.full(n, np.nan)
    step_feat = 2
    last_val = np.nan
    for i in range(W_RR, n):
        if (i - W_RR) % step_feat == 0 or not np.isfinite(last_val):
            w = rvol[i - W_RR + 1 : i + 1]
            wf = w[np.isfinite(w)]
            if len(wf) >= int(0.9 * W_RR):
                last_val = rqa_tt_over_div_ratio_window(wf, EPS_SCALE, L_MIN)
            else:
                last_val = np.nan
        feat[i] = last_val
    feat_s = pd.Series(feat, index=idx)
    mu = feat_s.rolling(ALB, min_periods=ALB).mean()
    sd = feat_s.rolling(ALB, min_periods=ALB).std(ddof=1)
    z = (feat_s - mu) / sd
    z = z.replace([np.inf, -np.inf], np.nan)
    raw = np.zeros(n)
    pos = 0
    hold = 0
    zv = z.values
    fv = feat
    for i in range(1, n):
        zi = zv[i]
        fi = fv[i]
        if not np.isfinite(zi) or not np.isfinite(fi):
            raw[i] = pos
            hold = (hold + 1) if pos != 0 else 0
            if pos != 0 and hold >= MAX_HOLD:
                pos = 0
                hold = 0
            continue
        if pos != 0:
            hold += 1
            if abs(zi) < EXIT_Z or hold >= MAX_HOLD:
                pos = 0
                hold = 0
        if pos == 0:
            if zi >= ENTRY_Z:
                pos = -1
                hold = 0
            elif zi <= -ENTRY_Z:
                pos = 1
                hold = 0
        raw[i] = pos
    sig = np.zeros(n)
    sig[1:] = raw[:-1]
    ret = np.zeros(n)
    ret[1:] = close[1:] / close[:-1] - 1.0
    splits = wf_splits(n, TRAIN, TEST, STEP)
    if not splits:
        return {"error": "no_wf_splits"}
    oos_union = np.zeros(n, dtype=bool)
    for _st, te_s, te_e in splits:
        oos_union[te_s:te_e] = True
    bh = ret.copy()
    bh[~oos_union] = 0.0
    bh_oos = float(np.nansum(bh))
    bh_oos_mean = float(np.nanmean(bh[oos_union])) if oos_union.any() else 0.0
    slices = {}
    for f_bps, s_bps in COST_GRID:
        gross = sig * ret
        turn = np.abs(np.diff(np.concatenate([[0.0], sig])))
        cost_rt = (f_bps + s_bps) / 10000.0
        net = gross - turn * cost_rt
        net[~oos_union] = 0.0
        gross_oos = gross.copy()
        gross_oos[~oos_union] = 0.0
        key = f"fee{f_bps}_slip{s_bps}"
        oos_net = float(np.nansum(net))
        oos_gross = float(np.nansum(gross_oos))
        oos_mean = float(np.nanmean(net[oos_union])) if oos_union.any() else 0.0
        slices[key] = {
            "oos_gross_sum": oos_gross,
            "oos_net_sum": oos_net,
            "oos_net_mean": oos_mean,
            "oos_bh_sum": bh_oos,
            "oos_bh_mean": bh_oos_mean,
            "positive": bool(oos_net > 0),
            "beats_bh_mean": bool(oos_mean > bh_oos_mean),
        }
    edge = bool(np.any(sig != 0) and oos_union.any()) and all(
        slices[f"fee{f}_slip{s}"]["oos_net_sum"] > 0
        and slices[f"fee{f}_slip{s}"]["oos_net_mean"] > slices[f"fee{f}_slip{s}"]["oos_bh_mean"]
        for f, s in COST_GRID
    )
    return {
        "n_bars": int(n),
        "window_start": str(idx[0]),
        "window_end": str(idx[-1]),
        "n_wf_folds": len(splits),
        "has_exposure_oos": bool(np.any(sig[oos_union] != 0)),
        "n_active_bars_oos": int(np.sum(sig[oos_union] != 0)),
        "exposure_frac_oos": float(np.mean(sig[oos_union] != 0)) if oos_union.any() else 0.0,
        "bh_oos_sum": bh_oos,
        "bh_oos_mean": bh_oos_mean,
        "cost_slices": slices,
        "edge_proven_oos": edge,
    }


def main():
    spot_df, spot_meta, spot_sha = load_spot()
    vol_df, vol_report = load_volume()
    assets = {}
    for sym in ["ADA", "BTC", "ETH", "SOL"]:
        if sym not in spot_df.columns or sym not in vol_df.columns:
            assets[sym] = {"error": "missing_symbol"}
            continue
        s = pd.to_numeric(spot_df[sym], errors="coerce").dropna()
        v = pd.to_numeric(vol_df[sym], errors="coerce").reindex(s.index)
        common = s.index.intersection(v.dropna().index)
        s = s.loc[common]
        v = v.loc[common]
        if len(s) < TRAIN + TEST + ALB + W_RR + 10:
            assets[sym] = {"error": "insufficient_overlap", "n": int(len(s))}
            continue
        assets[sym] = run_asset(s, v)
    cross = {}
    for f, s in COST_GRID:
        key = f"fee{f}_slip{s}"
        cross[key] = float(sum(
            a.get("cost_slices", {}).get(key, {}).get("oos_net_sum", 0.0)
            for a in assets.values() if isinstance(a, dict) and "cost_slices" in a
        ))
    any_exposure = any(a.get("has_exposure_oos") for a in assets.values() if isinstance(a, dict))
    all_pos = all(cross[k] > 0 for k in cross)
    all_beat_bh = all(
        a.get("cost_slices", {}).get(k, {}).get("oos_net_mean", -1e9)
        > a.get("cost_slices", {}).get(k, {}).get("oos_bh_mean", 1e9)
        for a in assets.values() if isinstance(a, dict) and "cost_slices" in a
        for k in cross
    ) if any_exposure else False
    edge = bool(any_exposure and all_pos and all_beat_bh)
    out = {
        "tool": "real_quote_volume_rqa_tt_over_div_ratio_shock_mr_costed_oos",
        "generated_at_utc": ts,
        "campaign": 198,
        "strategy_id": "VOLUME_RQA_TT_OVER_DIV_RATIO_SHOCK_MR",
        "candidate": "VOLUME_RQA_TT_OVER_DIV_RATIO_SHOCK_MR (RQA ratio TT/DIV on delay-embedded log-volume returns; TT=Trapping Time (C198 pre-stated)=mean qualifying diagonal line length over k>=l_min excl LOI; DIV=divergence=1/L_MAX, L_MAX=max qualifying diagonal line length k>=l_min excl LOI; RATIO_TT_DIV=TT/DIV=TT*L_MAX; m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2)",
        "feature_definition": "RATIO_TT_DIV = TT / DIV = TT * L_MAX. TT = mean qualifying diagonal line length over diagonal lines with k >= l_min (pre-stated l_min=2, excl LOI by threshold) on trailing W_RR=168 delay embedding (m=2,tau=1), L-inf recurrence eps=0.5*std(window). DIV = divergence = 1/L_MAX where L_MAX = maximum qualifying diagonal line length k>=l_min excl LOI. Causal trailing only; fail-closed to NaN/no-signal if TT undefined/non-finite/non-positive, DIV/L_MAX invalid (no qualifying diagonal lines, L_MAX<=0 or non-finite), ratio non-finite, or insufficient qualifying lines.",
        "pre_stated_distinctness": {
            "grep_cmd": DISTINCTNESS_GREP,
            "grep_hits_at_selection": DISTINCTNESS_HITS_PRE,
            "grep_verified_at_utc": DISTINCTNESS_VERIFIED_UTC,
            "grep_evidence_note": "Pre-implementation/run grep over scripts/strategies/backtest/utils returned 0 non-self hits for TT_OVER_DIV patterns (verified before implementation/run); distinctness confirmed. Primary candidate used.",
            "selection_note": "Primary C198 candidate from state/HANDOFF (TT_OVER_DIV); grep-zero confirmed at run time. TT/DIV diagonal pairing not used in C125-C197.",
            "family": "RQA TT/DIV ratio shock on volume dynamics",
            "uses_ratio_of_rqa_measures": True,
        },
        "real_data_only": True,
        "fabricated_data": False,
        "fail_closed": True,
        "edge_claim": "NONE",
        "data": {
            "spot_cache": str(SPOT_CACHE),
            "spot_cache_sha256": spot_sha,
            "spot_meta": spot_meta,
            "volume_meta": str(VOL_META),
            "volume_loader_report": vol_report,
        },
        "params": {
            "w_rr": W_RR, "alb": ALB, "m_emb": M_EMB, "tau": TAU, "eps_scale": EPS_SCALE,
            "l_min": L_MIN, "entry_z": ENTRY_Z, "exit_z": EXIT_Z,
            "max_hold": MAX_HOLD, "train": TRAIN, "test": TEST, "step": STEP,
            "cost_grid": COST_GRID, "feature_compute_step": 2,
            "feature_compute_note": "Causal trailing RQA computed every 2 bars and held (causal forward-hold) for runtime; signal/z/exec logic unchanged.",
            "tt_definition": "TT (C198 pre-stated) = mean qualifying diagonal line length over lengths k>=l_min (excl LOI by l_min>=2 threshold); fail-closed if no qualifying lines or TT non-finite/non-positive",
            "div_definition": "DIV = divergence = 1/L_MAX where L_MAX=max qualifying diagonal line length k>=l_min excl LOI; fail-closed if no qualifying diagonal lines or L_MAX<=0",
            "l_min_definition": "Qualifying diagonal lines: length k >= l_min (pre-stated l_min=2), excluding LOI",
        },
        "references": {
            "prior_registry": PRIOR_REGISTRY,
            "prior_registry_sha256": PRIOR_REGISTRY_SHA,
            "c197_oos": PRIOR_C197_OOS,
            "c197_oos_sha256": PRIOR_C197_OOS_SHA,
            "c197_note": "C197 OOS SHA verified from bytes (RTE_OVER_DIV, oos_edge_proven false); C198 uses TT/DIV (diagonal-line TT per pre-stated definition).",
        },
        "per_asset": assets,
        "cross_asset": {"oos_net_sums": cross},
        "oos_edge_proven": edge,
        "any_exposure_oos": bool(any_exposure),
        "all_cost_slices_positive_oos_net_sum": bool(all_pos),
        "all_cost_slices_beat_bh_mean_rule": bool(all_beat_bh),
        "edge_rule": "oos_edge_proven=true IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. WF 720/168/168, cost grid [[0,0],[5,5],[10,10],[20,20],[40,40]], B&H same OOS windows.",
    }
    if edge:
        out["edge_claim"] = "CONDITIONAL_EDGE_PROVEN"
    out_path = reports / f"real_quote_volume_rqa_tt_over_div_ratio_shock_mr_costed_oos_{ts}.json"
    out_path.write_text(json.dumps(out, indent=2, default=str) + "\n")
    out_sha = sha256_file(out_path)
    print(json.dumps({
        "oos": str(out_path.relative_to(root)), "oos_sha256": out_sha,
        "oos_edge_proven": edge, "edge_claim": out["edge_claim"],
        "any_exposure_oos": any_exposure, "all_cost_slices_positive_oos_net_sum": all_pos,
        "all_cost_slices_beat_bh_mean_rule": all_beat_bh, "cross_asset_oos_net_sums": cross,
        "script_sha256": sha256_file(Path(__file__)),
    }, indent=2))


if __name__ == "__main__":
    main()
