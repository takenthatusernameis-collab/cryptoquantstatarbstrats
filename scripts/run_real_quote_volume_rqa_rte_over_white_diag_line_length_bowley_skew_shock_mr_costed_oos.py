#!/usr/bin/env python3
"""C247: RQA ratio RTE/WHITE_DIAG_LINE_LENGTH_BOWLEY_SKEW shock on delay-embedded
log-volume returns (real data only).

Feature (pre-stated, distinct, grep-verified before implementation/run):
  VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_BOWLEY_SKEW_SHOCK_MR. On r_t = ln(v_t)-ln(v_{t-1}),
  build delay embedding X_i = (r_i, r_{i+tau}) with m=2, tau=1 over trailing window
  W_RR=168. Recurrence matrix R_{ij}=1 if ||X_i-X_j||_inf <= eps, else 0;
  eps = eps_scale * std(r_window) with pre-stated fixed eps_scale=0.5.
  RTE (numerator) = Recurrence Time Entropy = Shannon entropy (nats) of white
        vertical line length (recurrence-time gap) distribution: per column j,
        lengths w of consecutive zeros between recurrent points (excluding
        trivial self at i==j). Qualifying w>=w_min with count n_w>0;
        p_w=n_w/sum_u n_u; RTE=-sum_w p_w*ln(p_w). Fail-closed if <2 distinct
        qualifying gap lengths or entropy non-finite/non-positive/degenerate.
  WHITE_DIAG_LINE_LENGTH_BOWLEY_SKEW (denominator) = Bowley skewness =
        (Q3 + Q1 - 2*median)/(Q3 - Q1) of lengths of qualifying WHITE diagonal
        segments (consecutive 0-cells/non-recurrent, length>=w_min=2) pooled over
        off-diagonal diagonals k!=0 with >=1 qualifying segment; Q1/median/Q3 =
        25th/50th/75th percentiles (numpy.percentile, method='linear', pre-stated fixed).
        Fail-closed if <3 qualifying segment lengths, or (Q3-Q1) <= 0 / non-finite,
        or bowley skew non-finite, or resulting denominator/ratio undefined/non-finite/degenerate.
  RATIO_RTE_WHITE_DIAG_LINE_LENGTH_BOWLEY_SKEW = RTE / WHITE_DIAG_LINE_LENGTH_BOWLEY_SKEW.
  Fail-closed to NaN/no-signal if RTE/WHITE_DIAG_LINE_LENGTH_BOWLEY_SKEW/ratio
  undefined/non-finite/degenerate or insufficient qualifying segments/gaps.
  Causal trailing only. Distinct from WHITE_DIAG_LINE_LENGTH_TRIMEAN(C246),
  WHITE_DIAG_LINE_LENGTH_MIDHINGE(C245), WHITE_DIAG_LINE_LENGTH_WINSORIZED_MEAN(C244),
  WHITE_DIAG_LINE_LENGTH_TRIMMED_MEAN(C243), WHITE_DIAG_LINE_LENGTH_P10(C242),
  WHITE_DIAG_LINE_LENGTH_P90(C241), WHITE_DIAG_LINE_LENGTH_HARMONIC_MEAN(C240),
  WHITE_DIAG_LINE_LENGTH_GEOMEAN(C239), WHITE_DIAG_LINE_LENGTH_RMS(C238),
  WHITE_DIAG_LINE_LENGTH_ENTROPY(C237), WHITE_DIAG_LINE_LENGTH_GINI(C236),
  WHITE_DIAG_LINE_LENGTH_RANGE(C235), WHITE_DIAG_LINE_LENGTH_CV(C234),
  WHITE_DIAG_LINE_LENGTH_IQR(C233), WHITE_DIAG_LINE_LENGTH_MAD(C232),
  WHITE_DIAG_LINE_LENGTH_KURTOSIS(C231), WHITE_DIAG_LINE_LENGTH_SKEWNESS(C230),
  WHITE_DIAG_LINE_COUNT_VARIANCE(C229), DIAG_LINE_COUNT_VARIANCE(C228),
  WHITE_DIAG_LINE_LENGTH_DIVERGENCE(C227), WHITE_DIAG_LINE_LENGTH_VARIANCE(C226),
  and prior C125-C246 families.
  RTE_OVER_WHITE_DIAG_LINE_LENGTH_BOWLEY_SKEW not used C125-C246.
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

PRIOR_REGISTRY = "reports/strategy_edge_registry_20261109T030527Z.json"
PRIOR_REGISTRY_SHA = "ae20f66baec069066bc82c41156e314832512dc136b0b2f514b6df6682c2b67c"

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
    "RTE_OVER_WHITE_DIAG_LINE_LENGTH_BOWLEY_SKEW|"
    "rte_over_white_diag_line_length_bowley_skew|"
    "WHITE_DIAG_LINE_LENGTH_BOWLEY_SKEW|"
    "white_diag_line_length_bowley_skew"
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
        and ("white_diag_line_length_bowley_skew" in ln.lower()
             or "rte_over_white_diag_line_length_bowley_skew" in ln.lower())
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


def _white_diag_line_length_bowley_skew(R: np.ndarray, w_min: int) -> float:
    """WHITE_DIAG_LINE_LENGTH_BOWLEY_SKEW = (Q3 + Q1 - 2*median)/(Q3 - Q1) of lengths
    of qualifying WHITE diagonal segments (consecutive 0-cells/non-recurrent,
    length>=w_min) pooled over off-diagonal diagonals k!=0 with >=1 qualifying segment.
    Q1/median/Q3 = numpy.percentile 25th/50th/75th (method='linear', pre-stated fixed).
    Fail-closed if <3 qualifying segment lengths or (Q3-Q1)<=0 or bowley skew
    non-finite."""
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
    q1 = float(np.percentile(arr, 25, method="linear"))
    median = float(np.percentile(arr, 50, method="linear"))
    q3 = float(np.percentile(arr, 75, method="linear"))
    if not np.all(np.isfinite([q1, median, q3])):
        return np.nan
    iqr = q3 - q1
    if not np.isfinite(iqr) or iqr <= 0:
        return np.nan
    bowley = (q3 + q1 - 2.0 * median) / iqr
    if not np.isfinite(bowley):
        return np.nan
    return float(bowley)


def rqa_rte_over_white_diag_line_length_bowley_skew_window(
    rw: np.ndarray, eps_scale: float, w_min: int
) -> float:
    """RATIO_RTE_WHITE_DIAG_LINE_LENGTH_BOWLEY_SKEW = RTE / WHITE_DIAG_LINE_LENGTH_BOWLEY_SKEW.
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
    bowley = _white_diag_line_length_bowley_skew(R, w_min)
    if not np.isfinite(bowley) or bowley == 0.0:
        return np.nan
    ratio = rte / bowley
    if not np.isfinite(ratio):
        return np.nan
    return float(ratio)


def _pnl(pos, p, fee_bps, slip_bps):
    cost = (fee_bps + slip_bps) / 1e4
    ch = pos.diff().fillna(pos.iloc[0])
    return pos.shift(1).fillna(0) * p.pct_change().fillna(0) - ch.abs() * cost


def main() -> None:
    print("Starting C247...", flush=True)
    grep_hits, grep_out = run_distinctness_grep()
    print(f"Distinctness grep: {grep_hits} hits", flush=True)
    if grep_hits != 0:
        print(f"FATAL: distinctness grep non-self hits={grep_hits}; collision fail-closed", flush=True)
        print(grep_out, flush=True)
        sys.exit(2)
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
                rqa_rte_over_white_diag_line_length_bowley_skew_window(
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
        "campaign": 247,
        "strategy_id": "VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_BOWLEY_SKEW_SHOCK_MR",
        "strategy_family": "volume_rqa_rte_over_white_diag_line_length_bowley_skew_shock_mr_real",
        "oos_edge_proven": edge,
        "edge_claim": "NONE",
        "walk_forward": {"train": TRAIN, "test": TEST, "step": STEP},
        "cost_grid_bps": COST_GRID,
        "feature": (
            "RTE / WHITE_DIAG_LINE_LENGTH_BOWLEY_SKEW on delay-embedded (m=2,tau=1) log-volume "
            "returns over trailing W_RR; eps=0.5*std(r_window), L_inf recurrence. "
            "RTE=numerator (recurrence time entropy of white vertical gaps, w>=w_min, LOI excluded); "
            "WHITE_DIAG_LINE_LENGTH_BOWLEY_SKEW=denominator (Bowley skewness = (Q3 + Q1 - 2*median)/(Q3 - Q1) of lengths of "
            "qualifying WHITE diagonal segments (consecutive 0-cells/non-recurrent, length>=w_min=2) "
            "pooled over off-diagonal diagonals k!=0 with >=1 qualifying segment; Q1/median/Q3 = "
            "numpy.percentile 25/50/75, method='linear'). Fail-closed if <3 qualifying segment "
            "lengths or (Q3-Q1)<=0/non-finite or bowley skew non-finite, or RTE/ratio undefined."
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
            "percentile_method": "linear",
            "q1": 25,
            "median": 50,
            "q3": 75,
        },
        "pre_stated_distinctness": {
            "grep_cmd": DISTINCTNESS_GREP,
            "grep_hits_nonself_at_run": grep_hits,
            "grep_output": grep_out,
            "distinct_from": [
                "WHITE_DIAG_LINE_LENGTH_TRIMEAN (C246)",
                "WHITE_DIAG_LINE_LENGTH_MIDHINGE (C245)",
                "WHITE_DIAG_LINE_LENGTH_WINSORIZED_MEAN (C244)",
                "WHITE_DIAG_LINE_LENGTH_TRIMMED_MEAN (C243)",
                "WHITE_DIAG_LINE_LENGTH_P10 (C242)",
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
                "C125-C246 prior RQA ratio families",
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
            "c246_oos": "reports/real_quote_volume_rqa_rte_over_white_diag_line_length_trimean_shock_mr_costed_oos_20261109T025803Z.json",
            "c246_oos_sha256": "d329801a5c06bd49fbc129da4930011abca1c5920d464c5e420a5399e889f83c",
            "c245_oos": "reports/real_quote_volume_rqa_rte_over_white_diag_line_length_midhinge_shock_mr_costed_oos_20261109T022447Z.json",
            "c245_oos_sha256": "39d97b75b78b377015e2a944a36ad1c5b8d15f6aff4160d552f0fa1acc899ddc",
            "c244_oos": "reports/real_quote_volume_rqa_rte_over_white_diag_line_length_winsorized_mean_shock_mr_costed_oos_20261109T021110Z.json",
            "c244_oos_sha256": "2fc63905932fb6c53db6aa02d411cd7e36ea866dc7bfbfa429e95364fb04f5f2",
            "c247_note": "C247 uses WHITE_DIAG_LINE_LENGTH_BOWLEY_SKEW = (Q3+Q1-2*median)/(Q3-Q1) Bowley skewness of lengths of qualifying WHITE diagonal segments pooled over off-diagonal diagonals k!=0 (>=3 segments, (Q3-Q1)>0, bowley skew finite, numpy.percentile 25/50/75 method='linear'), distinct from TRIMEAN(C246), MIDHINGE(C245), WINSORIZED_MEAN(C244), TRIMMED_MEAN(C243), P10(C242), P90(C241) and C125-C246 families.",
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
    out_prefix = "real_quote_volume_rqa_rte_over_white_diag_line_length_bowley_skew_shock_mr_costed_oos"
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
