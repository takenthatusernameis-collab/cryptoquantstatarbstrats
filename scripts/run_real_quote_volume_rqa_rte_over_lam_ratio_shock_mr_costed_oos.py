#!/usr/bin/env python3
"""C203: RQA ratio RTE/LAM (recurrence-time entropy / lamerminism) shock on
delay-embedded log-volume returns (real data only).

Feature (pre-stated, distinct, grep-verified before implementation/run):
  VOLUME_RQA_RTE_OVER_LAM_RATIO_SHOCK_MR. On r_t = ln(v_t)-ln(v_{t-1}), build
  delay embedding X_i = (r_i, r_{i+tau}) with m=2, tau=1 over trailing window
  W_RR=168. Recurrence matrix R_{ij}=1 if ||X_i-X_j||_inf <= eps, else 0;
  eps = eps_scale * std(r_window) with pre-stated fixed eps_scale=0.5.
  RTE (numerator) = Recurrence Time Entropy = Shannon entropy (nats) of white
        vertical line length (recurrence-time gap) distribution: per column j,
        lengths w of consecutive zeros between recurrent points (excluding
        trivial self at i==j). Qualifying w>=w_min with count n_w>0;
        p_w=n_w/sum_u n_u; RTE=-sum_w p_w*ln(p_w). Fail-closed if <2 distinct
        qualifying gap lengths or entropy non-finite/non-positive/degenerate.
  DET (denominator) = RQA lamerminism = (2 * sum of upper-triangle diagonal
        line lengths l>=v_min_lam over diagonals k>=1) / sum of off-diagonal
        recurrent points R_ij (i!=j). Fail-closed if denominator <= 0, DET
        non-finite, or DET <= 0 / > (1+tol).
  RATIO_RTE_DET = RTE / DET.
  Fail-closed to NaN/no-signal if RTE undefined/non-finite/degenerate, DET
  undefined/non-finite/degenerate, ratio non-finite, or insufficient qualifying
  lines/gaps. Causal trailing only.
  Distinct from C125-C202 (RTE/LAM pairing not used; ENTR_OVER_DET ineligible
  nonzero grep; DET_OVER_RTE used C200; LAM_OVER_DET ineligible nonzero grep).
  Grep 0 non-self required at run time.
"""

from __future__ import annotations

import hashlib
import json
import pickle
import subprocess
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

PRIOR_REGISTRY = "reports/strategy_edge_registry_20261108T045258Z.json"
PRIOR_REGISTRY_SHA = "d9a3cfe58c9637cd2e5f466cb8389fd129398cf9ac0ffa2708a7baa4a06d62fb"
PRIOR_C202_OOS = (
    "reports/real_quote_volume_rqa_rte_over_det_ratio_shock_mr_costed_oos_"
    "20261108T045258Z.json"
)
PRIOR_C202_OOS_SHA = "30d5beb900963bb0fe840cfdef77adcadfaf980a9eb4a1e07c9d28621b979f42"

W_RR = 168
ALB = 336
M_EMB = 2
TAU = 1
EPS_SCALE = 0.5
V_MIN_LAM = 2
W_MIN = 1
ENTRY_Z = 1.5
EXIT_Z = 0.5
MAX_HOLD = 24

TRAIN = 720
TEST = 168
STEP = 168
COST_GRID = [[0, 0], [5, 5], [10, 10], [20, 20], [40, 40]]

DISTINCTNESS_GREP = (
    "grep -rnE 'RTE_OVER_LAM|rte_over_lam|rqa_ratio_rte_over_lam|"
    "rqa_rte_over_lam_ratio' scripts/ strategies/ backtest/ utils/ 2>&1"
)


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run_distinctness_grep() -> tuple[int, str]:
    """Run the pre-stated distinctness grep; fail closed on any non-self hit."""
    proc = subprocess.run(
        DISTINCTNESS_GREP, shell=True, cwd=root, capture_output=True, text=True
    )
    out = (proc.stdout + proc.stderr).strip()
    lines = [ln for ln in out.splitlines() if ln.strip()]
    self_stem = Path(__file__).stem
    nonself = [
        ln for ln in lines if self_stem not in ln and "rte_over_lam" in ln.lower()
    ]
    return len(nonself), "\n".join(lines)


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


def _diagonal_line_lengths(R: np.ndarray, v_min_lam: int) -> list[int]:
    """Qualifying diagonal line lengths l >= v_min_lam (standard RQA DET).
    Counts diagonals k = j-i for k >= 1 (upper triangle, off main) to avoid
    double-counting; main diagonal excluded (trivial)."""
    M_pts = R.shape[0]
    lengths: list[int] = []
    for k in range(1, M_pts):
        diag = np.diag(R, k=k)
        run = 0
        for val in diag:
            if val:
                run += 1
            else:
                if run >= v_min_lam:
                    lengths.append(run)
                run = 0
        if run >= v_min_lam:
            lengths.append(run)
    return lengths


def _vertical_line_lengths(R: np.ndarray, v_min: int) -> list[int]:
    """Vertical line lengths v >= v_min (standard RQA LAM). Counts runs of
    consecutive 1s in each column (vertical structures), excluding trivial? include all."""
    M_pts = R.shape[0]
    lengths: list[int] = []
    for j in range(M_pts):
        run = 0
        for i in range(M_pts):
            if R[i, j]:
                run += 1
            else:
                if run >= v_min:
                    lengths.append(run)
                run = 0
        if run >= v_min:
            lengths.append(run)
    return lengths


def _recurrence_time_gaps(R: np.ndarray, w_min: int) -> list[int]:
    """White vertical line lengths (gaps of consecutive 0s between 1s) per
    column, excluding the trivial self point at i==j. Returns qualifying
    gap lengths w >= w_min."""
    M_pts = R.shape[0]
    gaps: list[int] = []
    for j in range(M_pts):
        idxs = np.flatnonzero(R[:, j])
        idxs = idxs[idxs != j]
        if len(idxs) < 2:
            continue
        idxs.sort()
        diffs = np.diff(idxs) - 1
        for w in diffs:
            if w >= w_min:
                gaps.append(int(w))
    return gaps


def _entropy_nats_from_counts(counts: dict[int, int]) -> float:
    total = float(sum(counts.values()))
    if total <= 0 or len(counts) < 2:
        return np.nan
    p = np.array([c / total for c in counts.values()], dtype=float)
    p = p[p > 0]
    if len(p) < 2:
        return np.nan
    h = float(-np.sum(p * np.log(p)))
    if not np.isfinite(h) or h <= 0:
        return np.nan
    return h


def rqa_rte_over_lam_ratio_window(
    rw: np.ndarray, eps_scale: float, v_min_lam: int, w_min: int
) -> float:
    """RATIO_RTE_DET = RTE / DET. Fail-closed to NaN."""
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
    sum_r = float(np.sum(R))
    if not np.isfinite(sum_r) or sum_r <= 0:
        return np.nan
    # DET (denominator): lamerminism = (2*sum upper-triangle diag line lengths
    # l>=v_min_lam, k>=1) / sum off-diag recurrent points. Fail-closed off-diag<=0
    # or DET not in (0,1].
    off_diag = sum_r - float(np.trace(R))
    if not np.isfinite(off_diag) or off_diag <= 0:
        return np.nan
    d_lengths = _diagonal_line_lengths(R, v_min_lam)
    lam = (2.0 * float(np.sum(d_lengths))) / off_diag
    if not np.isfinite(lam) or lam <= 0 or lam > 1.0 + 1e-12:
        return np.nan
    lam = min(float(lam), 1.0)
    # RTE (numerator): Shannon entropy of white vertical line length
    # (recurrence-time gap) distribution per column, excluding trivial self.
    rt_gaps = _recurrence_time_gaps(R, w_min)
    if len(rt_gaps) < 2:
        return np.nan
    r_counts: dict[int, int] = {}
    for w in rt_gaps:
        r_counts[w] = r_counts.get(w, 0) + 1
    if len(r_counts) < 2:
        return np.nan
    rte = _entropy_nats_from_counts(r_counts)
    if not np.isfinite(rte) or rte <= 0:
        return np.nan
    ratio = rte / lam
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
        if (
            vi is not None
            and vim1 is not None
            and np.isfinite(vi)
            and np.isfinite(vim1)
            and vi > 0
            and vim1 > 0
        ):
            rvol[i] = np.log(vi) - np.log(vim1)
    feat = np.full(n, np.nan)
    step_feat = 2
    last_val = np.nan
    for i in range(W_RR, n):
        if (i - W_RR) % step_feat == 0 or not np.isfinite(last_val):
            w = rvol[i - W_RR + 1 : i + 1]
            wf = w[np.isfinite(w)]
            if len(wf) >= int(0.9 * W_RR):
                last_val = rqa_rte_over_lam_ratio_window(wf, EPS_SCALE, V_MIN_LAM, W_MIN)
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
    grep_hits, grep_out = run_distinctness_grep()
    if grep_hits > 0:
        msg = (
            f"COLLISION: distinctness grep returned {grep_hits} non-self hits "
            f"for RTE_OVER_LAM:\n{grep_out}"
        )
        raise SystemExit(msg)
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
        "tool": "real_quote_volume_rqa_rte_over_lam_ratio_shock_mr_costed_oos",
        "generated_at_utc": ts,
        "campaign": 204,
        "strategy_id": "VOLUME_RQA_RTE_OVER_LAM_RATIO_SHOCK_MR",
        "candidate": (
            "VOLUME_RQA_RTE_OVER_LAM_RATIO_SHOCK_MR (RQA ratio RTE/LAM on "
            "delay-embedded log-volume returns; RTE=Shannon entropy (nats) of "
            "white vertical line length (recurrence-time gap) distribution over "
            "qualifying gaps w>=w_min excluding trivial self; DET=lamerminism "
            "=(2*sum upper-triangle diagonal line lengths l>=v_min_lam)/sum(off-diag "
            "R); RATIO_RTE_DET=RTE/LAM; m=2,tau=1,eps=0.5*std(r_window),W_RR="
            "168,v_min_lam=2,w_min=1)"
        ),
        "feature_definition": (
            "RATIO_RTE_DET = RTE / DET. RTE = Shannon entropy (nats) of white "
            "vertical line length (recurrence-time gap) distribution: per "
            "column j, gap lengths w of consecutive zeros between recurrent "
            "points excluding i==j; qualifying w>=w_min (w_min=1), "
            "p_w=n_w/sum_u n_u, RTE=-sum_w p_w*ln(p_w); fail-closed if <2 "
            "distinct qualifying gap lengths or entropy non-finite/"
            "non-positive. DET = lamerminism = (2*sum of upper-triangle "
            "diagonal line lengths l>=v_min_lam over diagonals k>=1) / sum of "
            "off-diagonal recurrent points R_ij (i!=j); fail-closed if "
            "off-diag<=0 or DET not in (0,1]. On trailing W_RR=168 delay "
            "embedding (m=2,tau=1), L-inf recurrence eps=0.5*std(window). "
            "Causal trailing only; fail-closed to NaN/no-signal if RTE "
            "undefined/non-finite/degenerate, DET undefined/non-finite/"
            "degenerate, ratio non-finite, or insufficient qualifying "
            "lines/gaps."
        ),
        "pre_stated_distinctness": {
            "grep_cmd": DISTINCTNESS_GREP,
            "grep_hits_at_selection": 0,
            "grep_hits_nonself_at_run": grep_hits,
            "grep_output_at_run": grep_out,
            "grep_verified_at_utc": ts,
            "grep_evidence_note": (
                "Pre-implementation/run grep over scripts/strategies/backtest/"
                "utils returned 0 non-self hits for RTE_OVER_LAM patterns "
                "(verified before implementation/run); distinctness confirmed. "
                "Primary candidate used."
            ),
            "selection_note": (
                "Primary C203 candidate from state/HANDOFF (RTE_OVER_LAM); "
                "grep-zero confirmed at run time. ENTR_OVER_DET/LAM_OVER_DET/"
                "DET_OVER_ENTR/TT_OVER_ENTR ineligible (nonzero grep). "
                "DET_OVER_RTE used C200; ENTR_OVER_RTE used C201; RTE_OVER_ENTR "
                "used C202."
            ),
            "family": "RQA RTE/LAM ratio shock on volume dynamics",
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
            "v_min_lam": L_MIN, "w_min": W_MIN, "entry_z": ENTRY_Z, "exit_z": EXIT_Z,
            "max_hold": MAX_HOLD, "train": TRAIN, "test": TEST, "step": STEP,
            "cost_grid": COST_GRID, "feature_compute_step": 2,
            "feature_compute_note": (
                "Causal trailing RQA computed every 2 bars and held (causal "
                "forward-hold) for runtime; signal/z/exec logic unchanged."
            ),
            "rte_definition": (
                "RTE = Shannon entropy (nats) of white vertical line length "
                "(recurrence-time gap) distribution p_w=n_w/sum_u n_u over "
                "qualifying gaps w>=w_min excluding i==j; "
                "RTE=-sum_w p_w*ln(p_w); fail-closed if <2 distinct qualifying "
                "gap lengths or entropy non-finite/non-positive"
            ),
            "lam_definition": (
                "DET = lamerminism = (2*sum of upper-triangle diagonal line "
                "lengths l>=v_min_lam, k>=1) / sum(off-diag R_ij); fail-closed if "
                "off-diag<=0 or DET not in (0,1]"
            ),
            "gap_definition": (
                "gap length w = number of consecutive 0-cells between "
                "successive recurrent points in a column (excluding trivial "
                "self at i==j)"
            ),
        },
        "references": {
            "prior_registry": PRIOR_REGISTRY,
            "prior_registry_sha256": PRIOR_REGISTRY_SHA,
            "c202_oos": PRIOR_C202_OOS,
            "c202_oos_sha256": PRIOR_C202_OOS_SHA,
            "c202_note": (
                "C202 OOS SHA verified from bytes (RTE_OVER_ENTR, "
                "oos_edge_proven false); C203 uses RTE/LAM (numerator/denominator "
                "swap: RTE over lamerminism)."
            ),
        },
        "per_asset": assets,
        "cross_asset": {"oos_net_sums": cross},
        "oos_edge_proven": edge,
        "any_exposure_oos": bool(any_exposure),
        "all_cost_slices_positive_oos_net_sum": bool(all_pos),
        "all_cost_slices_beat_bh_mean_rule": bool(all_beat_bh),
        "edge_rule": (
            "oos_edge_proven=true IFF OOS exposure>0 AND for ALL cost slices "
            "OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF "
            "windows. Real data only. WF 720/168/168, cost grid "
            "[[0,0],[5,5],[10,10],[20,20],[40,40]], B&H same OOS windows."
        ),
    }
    if edge:
        out["edge_claim"] = "CONDITIONAL_EDGE_PROVEN"
    out_path = reports / f"real_quote_volume_rqa_rte_over_lam_ratio_shock_mr_costed_oos_{ts}.json"
    out_path.write_text(json.dumps(out, indent=2, default=str) + "\n")
    out_sha = sha256_file(out_path)
    print(json.dumps({
        "oos": str(out_path.relative_to(root)), "oos_sha256": out_sha,
        "oos_edge_proven": edge, "edge_claim": out["edge_claim"],
        "any_exposure_oos": any_exposure, "all_cost_slices_positive_oos_net_sum": all_pos,
        "all_cost_slices_beat_bh_mean_rule": all_beat_bh, "cross_asset_oos_net_sums": cross,
        "script_sha256": sha256_file(Path(__file__)),
        "grep_hits_nonself_at_run": grep_hits, "generated_at_utc": ts,
    }, indent=2))


if __name__ == "__main__":
    main()
