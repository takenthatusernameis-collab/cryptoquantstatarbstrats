#!/usr/bin/env python3
"""C274: RQA WHITE_DIAG_LINE_LENGTH_SECOND_PEARSON_SKEW shock on delay-embedded
log-volume returns (real data only).

Feature (pre-stated, distinct, grep-verified before implementation/run):
  VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_SECOND_PEARSON_SKEW_SHOCK_MR.
  On r_t = ln(v_t)-ln(v_{t-1}), build delay embedding X_i = (r_i, r_{i+tau})
  with m=2, tau=1 over trailing window W_RR=168. Recurrence matrix R_{ij}=1 if
  ||X_i-X_j||_inf <= eps, else 0; eps = eps_scale * std(r_window) with
  pre-stated fixed eps_scale=0.5.
  SECOND_PEARSON_SKEW (signal): 3*(mean(L) - median(L)) / std(L) over qualifying
  WHITE diagonal segment lengths L pooled over off-diagonal diagonals k!=0,
  length>=w_min=2, N>=3. mean/median/std: numpy (population std ddof=0).
  Fail-closed if N<3; std<=0/non-finite; mean/median/std/skew non-finite
  or undefined. Causal trailing only. Grep 0 non-self required at run time.
  Distinct from GROENEVELD_MEEDEN_SKEW(C249), PEARSON_MODE_SKEW(C269),
  KELLY_SKEW(C248), BOWLEY_SKEW(C247), moment SKEWNESS(C230).
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
    "SECOND_PEARSON_SKEW|"
    "RTE_OVER_WHITE_DIAG_LINE_LENGTH_SECOND_PEARSON_SKEW|"
    "WHITE_DIAG_LINE_LENGTH_SECOND_PEARSON_SKEW"
)
DISTINCTNESS_GREP = f"grep -rnE '{PAT}' scripts/ strategies/ backtest/ utils/ 2>&1"

STRATEGY_ID = "VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_SECOND_PEARSON_SKEW_SHOCK_MR"


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run_distinctness_grep() -> tuple[int, str]:
    proc = subprocess.run(
        DISTINCTNESS_GREP, shell=True, cwd=root, capture_output=True, text=True
    )
    out = (proc.stdout + proc.stderr).strip()
    lines = [ln for ln in out.splitlines() if ln.strip()]
    self_stems = {
        Path(__file__).stem,
        "run_c274_second_pearson_skew_full_pipeline",
        "build_c274_promotion_evidence_package",
        "verify_c274_second_pearson_skew_edge",
        "run_c274_second_pearson_skew_split_decomposition",
        "run_c274_second_pearson_skew_param_sensitivity",
    }
    nonself = []
    for ln in lines:
        if any(stem in ln for stem in self_stems):
            continue
        low = ln.lower()
        if "second_pearson_skew" in low or "white_diag_line_length_second_pearson_skew" in low:
            nonself.append(ln)
    return len(nonself), "\n".join(lines)


def load_spot():
    with open(SPOT_CACHE, "rb") as f:
        df = pickle.load(f)
    if isinstance(df, pd.Series):
        df = df.to_frame()
    return df, sha256_file(SPOT_CACHE)


def load_volume():
    from data.real_feed_loader import validate_and_load_real_feed

    prov = json.loads(VOL_PROV.read_text()) if VOL_PROV.exists() else {}
    df, report = validate_and_load_real_feed(VOL_META, "real_quote_volume", provenance=prov)
    df = df.pivot_table(
        index="timestamp_utc", columns="symbol", values="quote_volume_usdt", aggfunc="first"
    ).sort_index()
    return df, report


def white_diag_segment_lengths(rec: np.ndarray, w_min: int) -> list[int]:
    n = rec.shape[0]
    segs: list[int] = []
    for k in range(-(n - 1), n):
        if k == 0:
            continue
        diag = np.diag(rec, k=k)
        count = 0
        for v in diag:
            if v == 0:
                count += 1
            else:
                if count >= w_min:
                    segs.append(count)
                count = 0
        if count >= w_min:
            segs.append(count)
    return segs


def compute_feature(r_window: np.ndarray) -> tuple[float, dict]:
    # r_window must have length W_RR
    if len(r_window) != W_RR:
        return float("nan"), {"fail": "bad_window_len", "len": int(len(r_window))}
    if not np.all(np.isfinite(r_window)):
        return float("nan"), {"fail": "nonfinite_r"}
    sd = float(np.std(r_window, ddof=0))
    if not np.isfinite(sd) or sd <= 0:
        return float("nan"), {"fail": "zero_or_nonfinite_std_r"}
    eps = EPS_SCALE * sd
    n_emb = W_RR - (M_EMB - 1) * TAU
    if n_emb < 3:
        return float("nan"), {"fail": "too_few_embeddings"}
    X = np.column_stack([r_window[i:i + n_emb] for i in range(M_EMB)])
    d_inf = np.abs(X[:, None, :] - X[None, :, :]).max(axis=2)
    rec = (d_inf <= eps).astype(np.uint8)
    segs = white_diag_segment_lengths(rec, W_MIN)
    if len(segs) < 3:
        return float("nan"), {"fail": "too_few_segments", "n_segments": len(segs)}
    arr = np.asarray(segs, dtype=float)
    mean_l = float(np.mean(arr))
    med_l = float(np.median(arr))
    std_l = float(np.std(arr, ddof=0))
    if not np.isfinite(std_l) or std_l <= 0:
        return float("nan"), {"fail": "std_nonpositive", "n_segments": len(segs)}
    skew = 3.0 * (mean_l - med_l) / std_l
    if not np.isfinite(skew):
        return float("nan"), {"fail": "nonfinite_skew", "n_segments": len(segs)}
    return float(skew), {
        "fail": None, "n_segments": len(segs), "mean_l": mean_l,
        "median_l": med_l, "std_l": std_l, "eps": float(eps),
    }


def compute_feature_series(log_vol: np.ndarray) -> np.ndarray:
    T = len(log_vol)
    feat = np.full(T, np.nan, dtype=float)
    for i in range(W_RR, T):
        lv_win = log_vol[i - W_RR:i + 1]
        if not np.all(np.isfinite(lv_win)):
            continue
        r = np.diff(lv_win)  # length W_RR
        if len(r) != W_RR:
            continue
        f, _ = compute_feature(r)
        feat[i] = f
    return feat


def trading_signals(feat: np.ndarray, entry_z: float, exit_z: float, max_hold: int):
    T = len(feat)
    pos = np.zeros(T, dtype=int)
    cur = 0
    hold = 0
    for t in range(T):
        z = feat[t]
        if cur != 0:
            hold += 1
            exit_cond = (not np.isfinite(z)) or (abs(z) <= exit_z) or (hold >= max_hold)
            if exit_cond:
                cur = 0
                hold = 0
        if cur == 0 and np.isfinite(z):
            if z >= entry_z:
                cur = -1
                hold = 0
            elif z <= -entry_z:
                cur = 1
                hold = 0
        pos[t] = cur
    return pos


def net_pnl(pos: np.ndarray, close: np.ndarray, fee_bps: float, slip_bps: float):
    ret = np.zeros(len(close), dtype=float)
    ret[1:] = close[1:] / close[:-1] - 1.0
    gross = pos[:-1] * ret[1:]
    dpos = np.diff(np.concatenate([[0], pos]))
    cost = np.abs(dpos[1:]) * (fee_bps + slip_bps) / 10000.0
    net = gross - cost
    return net


def walk_forward(close: np.ndarray, feat: np.ndarray, fee_bps: float, slip_bps: float,
                 train: int, test: int, step: int, entry_z: float, exit_z: float, max_hold: int):
    T = len(close)
    oos_net = []
    bh_oos = []
    splits = 0
    exposures = []
    idx = 0
    while idx + train + test <= T:
        te_s = idx + train
        te_e = te_s + test
        pos_full = trading_signals(feat, entry_z, exit_z, max_hold)
        net = net_pnl(pos_full, close, fee_bps, slip_bps)
        oos_slice = net[te_s:te_e - 1] if te_e - 1 <= len(net) else net[te_s:len(net)]
        if len(oos_slice) == 0:
            idx += step
            continue
        oos_net.extend(oos_slice.tolist())
        bh = close[te_s + 1:te_e] / close[te_s:te_e - 1] - 1.0 if te_e <= T else np.array([])
        if len(bh):
            bh_oos.extend(bh.tolist())
        exposures.append(float(np.mean(np.abs(pos_full[te_s:te_e]) > 0)) if te_e <= T else 0.0)
        splits += 1
        idx += step
    return {
        "oos_net_sum": float(np.sum(oos_net)) if oos_net else 0.0,
        "oos_net_mean": float(np.mean(oos_net)) if oos_net else 0.0,
        "bh_oos_mean": float(np.mean(bh_oos)) if bh_oos else 0.0,
        "n_oos_periods": len(oos_net),
        "n_splits": splits,
        "mean_exposure": float(np.mean(exposures)) if exposures else 0.0,
        "any_exposure": any(e > 0 for e in exposures),
    }


def main():
    nhits, out = run_distinctness_grep()
    distinctness = {
        "grep_cmd": DISTINCTNESS_GREP,
        "grep_hits_nonself_at_run": nhits,
        "grep_output": out,
        "collision_fail_closed": nhits != 0,
    }
    if nhits != 0:
        result = {
            "strategy_id": STRATEGY_ID, "generated_at_utc": ts,
            "oos_edge_proven": False, "edge_claim": "NONE",
            "fail_reason": "DISTINCTNESS_COLLISION",
            "pre_stated_distinctness": distinctness,
        }
        outp = reports / f"real_quote_volume_rqa_rte_over_white_diag_line_length_second_pearson_skew_shock_mr_costed_oos_{ts}.json"
        outp.write_text(json.dumps(result, indent=2, sort_keys=True))
        print(json.dumps({"fail": "DISTINCTNESS_COLLISION", "hits": nhits, "out": str(outp)}, indent=2))
        return 2

    spot_df, spot_sha = load_spot()
    vol_df, vol_report = load_volume()

    common_cols = sorted(set(spot_df.columns) & set(vol_df.columns))
    if not common_cols:
        raise SystemExit("No common symbols between spot and volume caches")
    spot = spot_df[common_cols].sort_index()
    vol = vol_df[common_cols].sort_index()
    common_idx = spot.index.intersection(vol.index)
    spot = spot.loc[common_idx]
    vol = vol.loc[common_idx]
    close = spot.ffill().bfill().to_numpy(dtype=float)
    log_vol = np.log(np.clip(vol.ffill().bfill().to_numpy(dtype=float), 1e-12, None))

    per_asset = {}
    cross_cost = {f"fee{f}_slip{s}": [] for f, s in COST_GRID}
    any_exposure = False

    for j, sym in enumerate(common_cols):
        c = close[:, j]
        lv = log_vol[:, j]
        feat = compute_feature_series(lv)
        asset_costs = {}
        for f, s in COST_GRID:
            wf = walk_forward(c, feat, f, s, TRAIN, TEST, STEP, ENTRY_Z, EXIT_Z, MAX_HOLD)
            k = f"fee{f}_slip{s}"
            asset_costs[k] = wf
            cross_cost[k].append(wf["oos_net_sum"])
            if wf["any_exposure"]:
                any_exposure = True
        per_asset[sym] = asset_costs

    cross_asset = {"oos_net_sums": {}, "mean_oos_net_means": {}, "mean_bh_oos_means": {}}
    all_pos = True
    all_beat = True
    for f, s in COST_GRID:
        k = f"fee{f}_slip{s}"
        ssum = float(np.sum(cross_cost[k]))
        means = [per_asset[sym][k]["oos_net_mean"] for sym in common_cols]
        bh_means = [per_asset[sym][k]["bh_oos_mean"] for sym in common_cols]
        mmean = float(np.mean(means)) if means else 0.0
        mbh = float(np.mean(bh_means)) if bh_means else 0.0
        cross_asset["oos_net_sums"][k] = ssum
        cross_asset["mean_oos_net_means"][k] = mmean
        cross_asset["mean_bh_oos_means"][k] = mbh
        if ssum <= 0:
            all_pos = False
        if mmean <= mbh:
            all_beat = False

    oos_edge_proven = bool(any_exposure and all_pos and all_beat)
    edge_claim = "CONDITIONAL_EDGE_PROVEN" if oos_edge_proven else "NONE"

    result = {
        "strategy_id": STRATEGY_ID,
        "strategy_family": "RQA WHITE_DIAG_LINE_LENGTH_SECOND_PEARSON_SKEW shock on delay-embedded log-volume returns",
        "generated_at_utc": ts,
        "campaign": 274,
        "edge_claim": edge_claim,
        "oos_edge_proven": oos_edge_proven,
        "edge_rule": "oos_edge_proven=true IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only.",
        "any_exposure_oos": any_exposure,
        "all_cost_slices_positive_oos_net_sum": all_pos,
        "all_cost_slices_beat_bh_mean_rule": all_beat,
        "walk_forward": {"train": TRAIN, "test": TEST, "step": STEP},
        "cost_grid_bps": COST_GRID,
        "params": {
            "W_RR": W_RR, "ALB": ALB, "M_EMB": M_EMB, "TAU": TAU, "EPS_SCALE": EPS_SCALE,
            "W_MIN": W_MIN, "ENTRY_Z": ENTRY_Z, "EXIT_Z": EXIT_Z, "MAX_HOLD": MAX_HOLD,
            "feature": "3*(mean(L)-median(L))/std(L) of WHITE diagonal segment lengths L, N>=3, std>0, ddof=0",
        },
        "pre_stated_distinctness": distinctness,
        "assets": common_cols,
        "n_assets": len(common_cols),
        "cross_asset": cross_asset,
        "per_asset": per_asset,
        "data": {
            "spot_cache": str(SPOT_CACHE.relative_to(root)),
            "spot_cache_sha256": spot_sha,
            "volume_pkl": str(VOL_PKL.relative_to(root)),
            "volume_pkl_sha256": sha256_file(VOL_PKL),
            "volume_meta": str(VOL_META.relative_to(root)),
            "volume_meta_sha256": sha256_file(VOL_META),
            "volume_provenance": str(VOL_PROV.relative_to(root)),
            "volume_provenance_sha256": sha256_file(VOL_PROV),
            "real_data_only": True,
            "volume_validation": vol_report,
        },
    }

    oos_path = reports / f"real_quote_volume_rqa_rte_over_white_diag_line_length_second_pearson_skew_shock_mr_costed_oos_{ts}.json"
    oos_path.write_text(json.dumps(result, indent=2, sort_keys=True))

    ingest = {
        "generated_at_utc": ts, "campaign": 274, "strategy_id": STRATEGY_ID,
        "real_data_only": True, "network_refetch": False,
        "caches_used": {
            "spot": {"path": str(SPOT_CACHE.relative_to(root)), "sha256": spot_sha},
            "volume_pkl": {"path": str(VOL_PKL.relative_to(root)), "sha256": sha256_file(VOL_PKL)},
            "volume_meta": {"path": str(VOL_META.relative_to(root)), "sha256": sha256_file(VOL_META)},
            "volume_provenance": {"path": str(VOL_PROV.relative_to(root)), "sha256": sha256_file(VOL_PROV)},
        },
        "volume_validation": vol_report,
        "distinctness": distinctness,
        "oos_artifact": str(oos_path.relative_to(root)),
        "oos_sha256": sha256_file(oos_path),
    }
    ingest_path = reports / f"real_feed_ingest_attempt_274_{ts}.json"
    ingest_path.write_text(json.dumps(ingest, indent=2, sort_keys=True))

    registry = {
        "generated_at_utc": ts, "campaign": 274,
        "strategy_id": STRATEGY_ID, "edge_claim": edge_claim, "oos_edge_proven": oos_edge_proven,
        "oos_artifact": str(oos_path.relative_to(root)), "oos_sha256": sha256_file(oos_path),
        "cross_asset_oos_net_sums": cross_asset["oos_net_sums"],
        "any_exposure_oos": any_exposure,
        "all_cost_slices_positive_oos_net_sum": all_pos,
        "all_cost_slices_beat_bh_mean_rule": all_beat,
    }
    registry_path = reports / f"strategy_edge_registry_274_{ts}.json"
    registry_path.write_text(json.dumps(registry, indent=2, sort_keys=True))

    summary = {
        "generated_at_utc": ts, "campaign": 274, "strategy_id": STRATEGY_ID,
        "edge_claim": edge_claim, "oos_edge_proven": oos_edge_proven,
        "distinctness_grep_hits_nonself_at_run": nhits,
        "cross_asset_oos_net_sums": cross_asset["oos_net_sums"],
        "any_exposure_oos": any_exposure,
        "all_cost_slices_positive_oos_net_sum": all_pos,
        "all_cost_slices_beat_bh_mean_rule": all_beat,
        "artifacts": {
            "oos": {"path": str(oos_path.relative_to(root)), "sha256": sha256_file(oos_path)},
            "ingest": {"path": str(ingest_path.relative_to(root)), "sha256": sha256_file(ingest_path)},
            "registry": {"path": str(registry_path.relative_to(root)), "sha256": sha256_file(registry_path)},
            "script": {"path": str(Path(__file__).relative_to(root)), "sha256": sha256_file(Path(__file__))},
        },
    }
    summary_path = reports / f"campaign274_execution_summary_{ts}.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True))

    print(json.dumps({
        "oos": str(oos_path), "oos_sha": sha256_file(oos_path),
        "ingest": str(ingest_path), "ingest_sha": sha256_file(ingest_path),
        "registry": str(registry_path), "registry_sha": sha256_file(registry_path),
        "summary": str(summary_path), "summary_sha": sha256_file(summary_path),
        "script_sha": sha256_file(Path(__file__)),
        "edge_claim": edge_claim, "oos_edge_proven": oos_edge_proven,
        "cross_asset_oos_net_sums": cross_asset["oos_net_sums"],
        "any_exposure_oos": any_exposure,
        "distinctness_hits": nhits,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main() or 0)
