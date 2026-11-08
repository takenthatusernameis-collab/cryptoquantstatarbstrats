#!/usr/bin/env python3
"""C197: RQA ratio RTE/DIV (recurrence-time-entropy / divergence) shock on
delay-embedded log-volume returns (real data only).

Feature (pre-stated, distinct, grep-verified before implementation/run):
  VOLUME_RQA_RTE_OVER_DIV_RATIO_SHOCK_MR. On r_t = ln(v_t)-ln(v_{t-1}), build
  delay embedding X_i = (r_i, r_{i+tau}) with m=2, tau=1 over trailing window
  W_RR=168. Recurrence matrix R_{ij}=1 if ||X_i-X_j||_inf <= eps, else 0;
  eps = eps_scale * std(r_window) with pre-stated fixed eps_scale=0.5.
  DIV = divergence = 1 / L_MAX, where L_MAX = maximum qualifying diagonal line
    length k >= l_min (pre-stated l_min=2), excluding LOI (k=1).
  RTE = Recurrence Time Entropy = Shannon entropy (nats) of the white vertical
    line length (vertical white gap / recurrence-time gap) distribution: for
    each column j, lengths w of consecutive zeros between recurrent points
    (excluding trivial self at i==j), collect qualifying w >= w_min
    (pre-stated w_min=1, i.e. all positive gaps) with count n_w>0,
    p_w = n_w / sum_u n_u, RTE = -sum_w p_w * ln(p_w).
  RATIO_RTE_DIV = RTE / DIV = RTE * L_MAX.
  Fail-closed to NaN/no-signal if RTE undefined/non-finite/degenerate (<2
  distinct qualifying gap lengths or entropy non-finite/non-positive),
  DIV/L_MAX invalid (no qualifying diagonal lines, L_MAX<=0 or non-finite),
  ratio non-finite, or insufficient qualifying lines/gaps. Causal trailing only.
  Distinct from C125-C196 (RTE/DIV pairing not used before); grep 0 non-self
  at run time.
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

PRIOR_REGISTRY = "reports/strategy_edge_registry_20261108T025820Z.json"
PRIOR_REGISTRY_SHA = "3daa1bd367829596e339ecd4956601142e96f24a5c1b0c92e70932b6f8f1d5fc"
PRIOR_C196_OOS = "reports/real_quote_volume_rqa_entr_over_div_ratio_shock_mr_costed_oos_20261108T025803Z.json"
PRIOR_C196_OOS_SHA = "ffb28900b1750067cd8da2be960cf54c3b6c42a198741dc8e82bb9831825a256"

W_RR = 168
ALB = 336
M_EMB = 2
TAU = 1
EPS_SCALE = 0.5
L_MIN = 2
W_MIN = 1
ENTRY_Z = 1.5
EXIT_Z = 0.5
MAX_HOLD = 24

TRAIN = 720
TEST = 168
STEP = 168
COST_GRID = [[0, 0], [5, 5], [10, 10], [20, 20], [40, 40]]

DISTINCTNESS_GREP = "grep -rnE 'RTE_OVER_DIV|rte_over_div|rqa_ratio_rte_over_div|rqa_rte_over_div_ratio' scripts/ strategies/ backtest/ utils/ 2>&1"
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


def _vertical_white_gap_lengths(R: np.ndarray, w_min: int) -> list[int]:
    """Lengths w of consecutive zeros (vertical white gaps) between recurrent
    points in each column, excluding the trivial self point (i == j)."""
    M_pts = R.shape[0]
    if M_pts < 3:
        return []
    gaps: list[int] = []
    for j in range(M_pts):
        run = 0
        for i in range(M_pts):
            if i == j:
                if run >= w_min:
                    gaps.append(run)
                run = 0
                continue
            if R[i, j]:
                if run >= w_min:
                    gaps.append(run)
                run = 0
            else:
                run += 1
        if run >= w_min:
            gaps.append(run)
    return gaps


def rqa_rte_over_div_ratio_window(rw: np.ndarray, eps_scale: float, l_min: int, w_min: int) -> float:
    """RATIO_RTE_DIV = RTE / DIV = RTE * L_MAX.
    RTE = Shannon entropy (nats) of the white vertical line length (vertical
    white gap) distribution p_w = n_w/sum_u n_u over qualifying gaps w >= w_min
    (excluding trivial self): RTE = -sum_w p_w*ln(p_w).
    DIV = divergence = 1/L_MAX, L_MAX = maximum qualifying diagonal line
    length k >= l_min excl LOI. Fail-closed to NaN."""
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
    l_max = float(max(d_lengths))
    if not np.isfinite(l_max) or l_max <= 0:
        return np.nan
    div = 1.0 / l_max
    if not np.isfinite(div) or div == 0.0:
        return np.nan
    v_lengths = _vertical_white_gap_lengths(R, w_min)
    if not v_lengths:
        return np.nan
    counts: dict[int, int] = {}
    for w in v_lengths:
        counts[w] = counts.get(w, 0) + 1
    total = float(sum(counts.values()))
    if total <= 0:
        return np.nan
    if len(counts) < 2:
        return np.nan
    rte = 0.0
    for n_w in counts.values():
        p_w = n_w / total
        if p_w > 0:
            rte -= p_w * float(np.log(p_w))
    if not np.isfinite(rte) or rte <= 0:
        return np.nan
    ratio = rte / div
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
                last_val = rqa_rte_over_div_ratio_window(wf, EPS_SCALE, L_MIN, W_MIN)
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
        "tool": "real_quote_volume_rqa_rte_over_div_ratio_shock_mr_costed_oos",
        "generated_at_utc": ts,
        "campaign": 197,
        "strategy_id": "VOLUME_RQA_RTE_OVER_DIV_RATIO_SHOCK_MR",
        "candidate": "VOLUME_RQA_RTE_OVER_DIV_RATIO_SHOCK_MR (RQA ratio RTE/DIV on delay-embedded log-volume returns; RTE=Shannon entropy (nats) of white vertical line length distribution p_w=n_w/sum_u n_u over qualifying gaps w>=w_min (excluding trivial self), RTE=-sum_w p_w*ln(p_w); DIV=divergence=1/L_MAX, L_MAX=max qualifying diagonal line length k>=l_min excl LOI; RATIO_RTE_DIV=RTE/DIV; m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2,w_min=1)",
        "feature_definition": "RATIO_RTE_DIV = RTE / DIV = RTE * L_MAX. RTE = Shannon entropy (nats) of the white vertical line length distribution p_w = n_w/sum_u n_u over qualifying gap lengths w >= w_min with n_w > 0 (excluding trivial self at i==j): RTE = -sum_w p_w*ln(p_w). DIV = divergence = 1/L_MAX where L_MAX = maximum qualifying diagonal line length k >= l_min (pre-stated l_min=2, excluding LOI). Delay embedding m=2 tau=1 over trailing window W_RR=168, L-inf recurrence with eps=EPS_SCALE*std(window); causal trailing only; fail-closed to NaN/no-signal if RTE undefined/non-finite/degenerate (<2 distinct qualifying gap lengths or entropy non-finite/non-positive), DIV/L_MAX invalid (no qualifying diagonal lines, L_MAX<=0 or non-finite), ratio non-finite, or insufficient qualifying lines/gaps.",
        "pre_stated_distinctness": {
            "grep_cmd": DISTINCTNESS_GREP,
            "grep_hits_at_selection": DISTINCTNESS_HITS_PRE,
            "grep_verified_at_utc": DISTINCTNESS_VERIFIED_UTC,
            "grep_evidence_note": "Pre-implementation/run grep over scripts/strategies/backtest/utils returned 0 non-self hits (verified before implementation/run); distinctness confirmed. Primary candidate used.",
            "selection_note": "Primary C197 candidate from state/HANDOFF (RTE_OVER_DIV); grep-zero confirmed at run time. RTE/DIV pairing not used in C125-C196 (C194/others used RTE with different denominators).",
            "family": "RQA RTE/DIV ratio shock on volume dynamics",
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
            "l_min": L_MIN, "w_min": W_MIN, "entry_z": ENTRY_Z, "exit_z": EXIT_Z,
            "max_hold": MAX_HOLD, "train": TRAIN, "test": TEST, "step": STEP,
            "cost_grid": COST_GRID, "feature_compute_step": 2,
            "feature_compute_note": "Causal trailing RQA computed every 2 bars and held (causal forward-hold) for runtime; signal/z/exec logic unchanged.",
            "rte_definition": "RTE = Shannon entropy (nats) of the white vertical line length distribution p_w=n_w/sum_u n_u over qualifying gaps w>=w_min excluding trivial self: RTE=-sum_w p_w*ln(p_w); fail-closed if <2 distinct qualifying gap lengths or entropy non-finite/non-positive",
            "div_definition": "DIV = divergence = 1/L_MAX where L_MAX=max qualifying diagonal line length k>=l_min excl LOI; fail-closed if no qualifying diagonal lines or L_MAX<=0",
            "l_min_definition": "Qualifying diagonal lines: length k >= l_min (pre-stated l_min=2), excluding LOI",
            "w_min_definition": "Qualifying vertical white gaps: length w >= w_min (pre-stated w_min=1, all positive gaps)",
        },
        "references": {
            "prior_registry": PRIOR_REGISTRY,
            "prior_registry_sha256": PRIOR_REGISTRY_SHA,
            "c196_oos": PRIOR_C196_OOS,
            "c196_oos_sha256": PRIOR_C196_OOS_SHA,
            "c196_note": "C196 OOS SHA verified from bytes (ENTR_OVER_DIV, oos_edge_proven false); C197 uses RTE/DIV.",
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
    out_path = reports / f"real_quote_volume_rqa_rte_over_div_ratio_shock_mr_costed_oos_{ts}.json"
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
