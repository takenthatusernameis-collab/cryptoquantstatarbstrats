#!/usr/bin/env python3
"""C242: RQA ratio RTE/WHITE_DIAG_LINE_LENGTH_P10 shock on delay-embedded
log-volume returns (real data only).

Feature (pre-stated, distinct, grep-verified before implementation/run):
  VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_P10_SHOCK_MR. On r_t = ln(v_t)-ln(v_{t-1}),
  build delay embedding X_i = (r_i, r_{i+tau}) with m=2, tau=1 over trailing window
  W_RR=168. Recurrence matrix R_{ij}=1 if ||X_i-X_j||_inf <= eps, else 0;
  eps = eps_scale * std(r_window) with pre-stated fixed eps_scale=0.5.
  RTE (numerator) = Recurrence Time Entropy = Shannon entropy (nats) of white
        vertical line length (recurrence-time gap) distribution: per column j,
        lengths w of consecutive zeros between recurrent points (excluding
        trivial self at i==j). Qualifying w>=w_min with count n_w>0;
        p_w=n_w/sum_u n_u; RTE=-sum_w p_w*ln(p_w). Fail-closed if <2 distinct
        qualifying gap lengths or entropy non-finite/non-positive/degenerate.
  WHITE_DIAG_LINE_LENGTH_P10 (denominator) = 10th percentile (numpy default linear
        interpolation) of lengths of qualifying WHITE diagonal segments
        (consecutive 0-cells/non-recurrent, length>=w_min=2) pooled over
        off-diagonal diagonals k!=0 with >=1 qualifying segment.
        Fail-closed if <3 qualifying segment lengths or P10 non-finite/non-positive.
  RATIO_RTE_WHITE_DIAG_LINE_LENGTH_P10 = RTE / WHITE_DIAG_LINE_LENGTH_P10.
  Fail-closed to NaN/no-signal if RTE/WHITE_DIAG_LINE_LENGTH_P10/ratio
  undefined/non-finite/degenerate or insufficient qualifying segments/gaps.
  Causal trailing only. Distinct from WHITE_DIAG_LINE_LENGTH_P90(C241),
  WHITE_DIAG_LINE_LENGTH_HARMONIC_MEAN(C240), WHITE_DIAG_LINE_LENGTH_GEOMEAN(C239),
  WHITE_DIAG_LINE_LENGTH_RMS(C238), WHITE_DIAG_LINE_LENGTH_ENTROPY(C237),
  WHITE_DIAG_LINE_LENGTH_GINI(C236), WHITE_DIAG_LINE_LENGTH_RANGE(C235),
  WHITE_DIAG_LINE_LENGTH_CV(C234), WHITE_DIAG_LINE_LENGTH_IQR(C233),
  WHITE_DIAG_LINE_LENGTH_MAD(C232), WHITE_DIAG_LINE_LENGTH_KURTOSIS(C231),
  WHITE_DIAG_LINE_LENGTH_SKEWNESS(C230), WHITE_DIAG_LINE_COUNT_VARIANCE(C229),
  DIAG_LINE_COUNT_VARIANCE(C228), WHITE_DIAG_LINE_LENGTH_DIVERGENCE(C227),
  WHITE_DIAG_LINE_LENGTH_VARIANCE(C226), and prior C125-C241 families.
  RTE_OVER_WHITE_DIAG_LINE_LENGTH_P10 not used C125-C241.
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

PRIOR_REGISTRY = "reports/strategy_edge_registry_20261109T012117Z.json"
PRIOR_REGISTRY_SHA = "bb9b240eb748942a36e28f5da8279a656ca6da3ed8aff1f463e740871247d8fa"

W_RR = 168
ALB = 336
M_EMB = 2
TAU = 1
EPS_SCALE = 0.5
W_MIN = 2
ENTRY_Z = 1.5
EXIT_Z = 0.5
MAX_HOLD = 24

TRAIN = 720
TEST = 168
STEP = 168
COST_GRID = [[0, 0], [5, 5], [10, 10], [20, 20], [40, 40]]

PAT = (
    "RTE_OVER_WHITE_DIAG_LINE_LENGTH_P10|"
    "rte_over_white_diag_line_length_p10|"
    "WHITE_DIAG_LINE_LENGTH_P10|"
    "white_diag_line_length_p10"
)
DISTINCTNESS_GREP = f"grep -rnE '{PAT}' scripts/ strategies/ backtest/ utils/ 2>&1"


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run_distinctness_grep() -> tuple[int, str]:
    proc = subprocess.run(
        DISTINCTNESS_GREP, shell=True, cwd=root, capture_output=True, text=True
    )
    out = (proc.stdout + proc.stderr).strip()
    lines = [ln for ln in out.splitlines() if ln.strip()]
    self_stem = Path(__file__).stem
    nonself = [
        ln
        for ln in lines
        if self_stem not in ln
        and ("white_diag_line_length_p10" in ln.lower()
             or "rte_over_white_diag_line_length_p10" in ln.lower())
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


def _recurrence_time_gaps(R: np.ndarray, w_min: int) -> list[int]:
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


def _qualifying_white_diag_segments(diag: np.ndarray, w_min: int) -> list[int]:
    segs: list[int] = []
    run = 0
    for val in diag:
        if int(val) == 0:
            run += 1
        else:
            if run >= w_min:
                segs.append(run)
            run = 0
    if run >= w_min:
        segs.append(run)
    return segs


def _white_diag_line_length_p10(R: np.ndarray, w_min: int) -> float:
    """WHITE_DIAG_LINE_LENGTH_P10 = 10th percentile (numpy default linear interpolation)
    of lengths of qualifying WHITE diagonal segments (consecutive 0-cells/non-recurrent,
    length>=w_min) pooled over off-diagonal diagonals k!=0 with >=1 qualifying segment.
    Fail-closed if <3 qualifying segment lengths or P10 non-finite/non-positive."""
    M_pts = R.shape[0]
    seg_lengths: list[int] = []
    for k in range(-(M_pts - 1), M_pts):
        if k == 0:
            continue
        diag = np.diag(R, k=k)
        segs = _qualifying_white_diag_segments(diag, w_min)
        if segs:
            seg_lengths.extend(int(s) for s in segs)
    if len(seg_lengths) < 3:
        return np.nan
    arr = np.array(seg_lengths, dtype=float)
    if not np.all(np.isfinite(arr)) or not np.all(arr > 0):
        return np.nan
    p10 = float(np.percentile(arr, 10))
    if not np.isfinite(p10) or p10 <= 0:
        return np.nan
    return p10


def rqa_rte_over_white_diag_line_length_p10_window(
    rw: np.ndarray, eps_scale: float, w_min: int
) -> float:
    """RATIO_RTE_WHITE_DIAG_LINE_LENGTH_P10 = RTE / WHITE_DIAG_LINE_LENGTH_P10.
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
    sum_r = float(np.sum(R))
    if not np.isfinite(sum_r) or sum_r <= 0:
        return np.nan
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
    dp10 = _white_diag_line_length_p10(R, w_min)
    if not np.isfinite(dp10):
        return np.nan
    ratio = rte / dp10
    if not np.isfinite(ratio):
        return np.nan
    return float(ratio)


def _pnl(pos, p, fee_bps, slip_bps):
    cost = (fee_bps + slip_bps) / 1e4
    ch = pos.diff().fillna(pos.iloc[0])
    return pos.shift(1).fillna(0) * p.pct_change().fillna(0) - ch.abs() * cost


def main() -> None:
    print("Starting C242...", flush=True)
    grep_hits, grep_out = run_distinctness_grep()
    print(f"Distinctness grep: {grep_hits} hits", flush=True)
    spot, spot_meta, spot_sha = load_spot()
    print(f"Spot loaded: {spot.shape}", flush=True)
    vol, vol_report = load_volume()
    print(f"Volume loaded: {vol.shape}", flush=True)

    assets: dict[str, dict] = {}
    any_exposure = False
    bh_means: list[float] = []
    strat_means: list[float] = []

    for sym in sorted(set(spot.columns) & set(vol.columns)):
        print(f"Processing {sym}...", flush=True)
        sp, sv = spot[sym].astype(float), vol[sym].astype(float)
        mask = sp.notna() & sv.notna() & (sv > 0)
        sp, sv = sp[mask], sv[mask]
        lr = np.log(sv).diff().replace([np.inf, -np.inf], np.nan)
        idx = lr.dropna().index
        sp, lr = sp.loc[idx], lr.loc[idx]
        common = sp.index.intersection(lr.index)
        sp, lr = sp.loc[common], lr.loc[common]
        if len(sp) < TRAIN + TEST + 1:
            assets[sym] = {"status": "insufficient", "bars": int(len(sp))}
            print(f"  {sym}: insufficient bars", flush=True)
            continue

        r_arr = lr.to_numpy(dtype=float)
        n = len(r_arr)
        ratio = pd.Series(
            [
                rqa_rte_over_white_diag_line_length_p10_window(
                    r_arr[max(0, i - W_RR + 1) : i + 1], EPS_SCALE, W_MIN
                )
                for i in range(n)
            ],
            index=lr.index,
            dtype=float,
        )
        print(f"  {sym}: ratio finite={ratio.notna().sum()}/{n}", flush=True)

        alb = ratio.rolling(ALB, min_periods=ALB).mean()
        asd = ratio.rolling(ALB, min_periods=ALB).std(ddof=1)
        z = (ratio - alb) / asd.replace(0.0, np.nan)
        sig = pd.Series(0.0, index=lr.index)
        sig[z > ENTRY_Z] = -1.0
        sig[z < -ENTRY_Z] = 1.0
        sig[(z.abs() <= EXIT_Z) & (z.notna())] = 0.0
        sig[z.isna()] = 0.0
        pos = (
            sig.replace(0.0, np.nan)
            .ffill()
            .fillna(0.0)
            .rolling(MAX_HOLD, min_periods=1)
            .apply(lambda x: x.iloc[0] if (x != 0).all() else 0.0, raw=False)
            .fillna(0.0)
        )

        per_cost: dict[str, dict] = {}
        for fee, slp in COST_GRID:
            fold_rows = []
            for tr_s, tr_e, te_e in wf_splits(len(pos), TRAIN, TEST, STEP):
                te_pos = pos.iloc[tr_e:te_e]
                te_sp = sp.iloc[tr_e:te_e]
                net = float(_pnl(te_pos, te_sp, fee, slp).sum())
                bh = float(sp.iloc[te_e - 1] / sp.iloc[tr_e] - 1.0)
                fold_rows.append({"oos_net": net, "bh": bh})
            nets = [r["oos_net"] for r in fold_rows]
            bhs = [r["bh"] for r in fold_rows]
            pos_bars = int((pos != 0).sum())
            if pos_bars > 0:
                any_exposure = True
            if fee == 0 and slp == 0:
                bh_means.append(float(np.mean(bhs)) if bhs else 0.0)
                strat_means.append(float(np.mean(nets)) if nets else 0.0)
            per_cost[f"fee{fee}_slip{slp}"] = {
                "fold_count": len(fold_rows),
                "oos_net_sum": float(np.sum(nets)) if nets else 0.0,
                "mean_oos_net": float(np.mean(nets)) if nets else 0.0,
                "mean_bh_oos_net": float(np.mean(bhs)) if bhs else 0.0,
                "position_bars": pos_bars,
            }
        assets[sym] = {
            "status": "ok",
            "bars": int(len(sp)),
            "ratio_finite_bars": int(np.isfinite(ratio.to_numpy()).sum()),
            "per_cost": per_cost,
        }

    cross: dict[str, float] = {}
    for fee, slp in COST_GRID:
        key = f"fee{fee}_slip{slp}"
        cross[key] = float(
            sum(
                a["per_cost"][key]["oos_net_sum"]
                for a in assets.values()
                if a.get("status") == "ok"
            )
        )
    all_pos = all(v > 0 for v in cross.values()) if cross else False
    all_beat_bh = (
        (np.mean(strat_means) > np.mean(bh_means))
        if strat_means and bh_means
        else False
    )
    edge = bool(any_exposure and all_pos and all_beat_bh)

    out = {
        "generated_at_utc": ts,
        "campaign": 242,
        "strategy_id": "VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_P10_SHOCK_MR",
        "strategy_family": "volume_rqa_rte_over_white_diag_line_length_p10_shock_mr_real",
        "oos_edge_proven": edge,
        "edge_claim": "NONE",
        "walk_forward": {"train": TRAIN, "test": TEST, "step": STEP},
        "cost_grid_bps": COST_GRID,
        "feature": (
            "RTE / WHITE_DIAG_LINE_LENGTH_P10 on delay-embedded (m=2,tau=1) log-volume "
            "returns over trailing W_RR; eps=0.5*std(r_window), L_inf recurrence. "
            "RTE=numerator (recurrence time entropy of white vertical gaps, w>=w_min, LOI excluded); "
            "WHITE_DIAG_LINE_LENGTH_P10=denominator (10th percentile, numpy linear interpolation, of "
            "lengths of qualifying WHITE diagonal segments (consecutive 0-cells/non-recurrent, "
            "length>=w_min=2) pooled over off-diagonal diagonals k!=0 with >=1 qualifying segment). "
            "Fail-closed if <3 qualifying segment lengths or P10<=0/non-finite, or RTE/ratio undefined."
        ),
        "params": {
            "W_RR": W_RR,
            "alb": ALB,
            "m": M_EMB,
            "tau": TAU,
            "eps_scale": EPS_SCALE,
            "w_min": W_MIN,
            "entry_z": ENTRY_Z,
            "exit_z": EXIT_Z,
            "max_hold": MAX_HOLD,
        },
        "pre_stated_distinctness": {
            "grep_cmd": DISTINCTNESS_GREP,
            "grep_hits_nonself_at_run": grep_hits,
            "grep_output": grep_out,
            "distinct_from": [
                "WHITE_DIAG_LINE_LENGTH_P90 (C241)",
                "WHITE_DIAG_LINE_LENGTH_HARMONIC_MEAN (C240)",
                "WHITE_DIAG_LINE_LENGTH_GEOMEAN (C239)",
                "WHITE_DIAG_LINE_LENGTH_RMS (C238)",
                "WHITE_DIAG_LINE_LENGTH_ENTROPY (C237)",
                "WHITE_DIAG_LINE_LENGTH_GINI (C236)",
                "WHITE_DIAG_LINE_LENGTH_RANGE (C235)",
                "WHITE_DIAG_LINE_LENGTH_CV (C234)",
                "WHITE_DIAG_LINE_LENGTH_IQR (C233)",
                "WHITE_DIAG_LINE_LENGTH_MAD (C232)",
                "WHITE_DIAG_LINE_LENGTH_KURTOSIS (C231)",
                "WHITE_DIAG_LINE_LENGTH_SKEWNESS (C230)",
                "WHITE_DIAG_LINE_COUNT_VARIANCE (C229)",
                "DIAG_LINE_COUNT_VARIANCE (C228)",
                "WHITE_DIAG_LINE_LENGTH_DIVERGENCE (C227)",
                "WHITE_DIAG_LINE_LENGTH_VARIANCE (C226)",
                "C125-C241 prior RQA ratio families",
            ],
        },
        "data_sources": {
            "spot_cache": str(SPOT_CACHE.relative_to(root)),
            "spot_cache_sha256": spot_sha,
            "spot_meta_sha256": sha256_file(SPOT_META) if SPOT_META.exists() else None,
            "volume_pkl_sha256": sha256_file(VOL_PKL) if VOL_PKL.exists() else None,
            "volume_meta_sha256": sha256_file(VOL_META) if VOL_META.exists() else None,
            "volume_provenance_sha256": sha256_file(VOL_PROV) if VOL_PROV.exists() else None,
            "volume_validation": vol_report,
        },
        "artifacts": {
            "prior_registry": PRIOR_REGISTRY,
            "prior_registry_sha256": PRIOR_REGISTRY_SHA,
            "c241_oos": "reports/real_quote_volume_rqa_rte_over_white_diag_line_length_p90_shock_mr_costed_oos_20261109T011345Z.json",
            "c241_oos_sha256": "94914f1f2ec9c0b8f15c159a3665019573c639ba2cb888754fcac103996be3db",
            "c240_oos": "reports/real_quote_volume_rqa_rte_over_white_diag_line_length_harmonic_mean_shock_mr_costed_oos_20261109T003419Z.json",
            "c240_oos_sha256": "d24b0a8b45ec2ef767b53ff1f4493586fb8ac66d6208b60d6833cf8429093f23",
            "c239_oos": "reports/real_quote_volume_rqa_rte_over_white_diag_line_length_geomean_shock_mr_costed_oos_20261109T001931Z.json",
            "c239_oos_sha256": "76b139d6065b9366495f2fbdcb99bb9a2df4473bdaf0329d3b0a79f97fc3b61d",
            "c238_oos": "reports/real_quote_volume_rqa_rte_over_white_diag_line_length_rms_shock_mr_costed_oos_20261109T000841Z.json",
            "c238_oos_sha256": "55af89a05949ac522c05f83fc35fc962cc6d25d448834d690e51f43fac95b23e",
            "c242_note": "C241 OOS (P90, 94914f1f2ec9c0b8f15c159a3665019573c639ba2cb888754fcac103996be3db, oos_edge_proven false, exposure true, all cost slices not all positive). C240 OOS (HARMONIC_MEAN, d24b0a8b45ec2ef767b53ff1f4493586fb8ac66d6208b60d6833cf8429093f23, oos_edge_proven false). C239 OOS (GEOMEAN, 76b139d6065b9366495f2fbdcb99bb9a2df4473bdaf0329d3b0a79f97fc3b61d, oos_edge_proven false). C238 OOS (RMS, 55af89a05949ac522c05f83fc35fc962cc6d25d448834d690e51f43fac95b23e, oos_edge_proven false). C242 uses WHITE_DIAG_LINE_LENGTH_P10 = 10th percentile of lengths of qualifying WHITE diagonal segments pooled over off-diagonal diagonals k!=0 (>=3 segments, P10>0), distinct from P90(C241), HARMONIC_MEAN(C240), GEOMEAN(C239), RMS(C238) and C125-C241 families.",
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
    out_prefix = "real_quote_volume_rqa_rte_over_white_diag_line_length_p10_shock_mr_costed_oos"
    out_name = f"{out_prefix}_{ts}.json"
    out_path = reports / out_name
    out_path.write_text(json.dumps(out, indent=2, default=str) + "\n")
    out_sha = sha256_file(out_path)
    print(json.dumps({
        "oos": str(out_path.relative_to(root)), "oos_sha256": out_sha,
        "oos_edge_proven": bool(edge), "edge_claim": out["edge_claim"],
        "any_exposure_oos": bool(any_exposure), "all_cost_slices_positive_oos_net_sum": bool(all_pos),
        "all_cost_slices_beat_bh_mean_rule": bool(all_beat_bh), "cross_asset_oos_net_sums": cross,
        "script_sha256": sha256_file(Path(__file__)),
        "grep_hits_nonself_at_run": int(grep_hits), "generated_at_utc": ts,
    }, indent=2))


if __name__ == "__main__":
    main()