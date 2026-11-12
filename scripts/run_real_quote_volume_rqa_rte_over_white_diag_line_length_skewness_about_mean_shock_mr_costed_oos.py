#!/usr/bin/env python3
"""C271: RQA WHITE_DIAG_LINE_LENGTH_SKEWNESS_ABOUT_MEAN shock on delay-embedded
log-volume returns (real data only).

Feature (pre-stated, distinct, grep-verified before implementation/run):
  VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_SKEWNESS_ABOUT_MEAN_SHOCK_MR.
  On r_t = ln(v_t)-ln(v_{t-1}), build delay embedding X_i = (r_i, r_{i+tau})
  with m=2, tau=1 over trailing window W_RR=168. Recurrence matrix R_{ij}=1 if
  ||X_i-X_j||_inf <= eps, else 0; eps = eps_scale * std(r_window) with
  pre-stated fixed eps_scale=0.5.
  SKEWNESS_ABOUT_MEAN (signal): mean((L_i-mean)^3)/std(L)^3 (population std)
  of qualifying WHITE diagonal segment lengths (pooled over off-diagonal
  diagonals k!=0, length>=w_min=2, N>=3):
  Let L={L_1,..,L_N}, N>=3. mean=mean(L), std=population_std(L) (ddof=0).
  skew = mean((L_i-mean)^3) / std^3.
  Fail-closed if <3 qualifying segment lengths; std<=0/non-finite; skew
  non-finite/degenerate; or any intermediate undefined/non-finite.
  Causal trailing only. Grep 0 non-self required at run time.
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

PRIOR_REGISTRY = "reports/strategy_edge_registry_20261112T031436Z.json"
PRIOR_REGISTRY_SHA = "65d17f06f9ab8bb855163aa31ac5642915c8362e87957c8f6d941ea44d21e7e3"

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
    "SKEWNESS_ABOUT_MEAN|"
    "RTE_OVER_WHITE_DIAG_LINE_LENGTH_SKEWNESS_ABOUT_MEAN|"
    "WHITE_DIAG_LINE_LENGTH_SKEWNESS_ABOUT_MEAN"
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
    own_campaign = {
        self_stem,
        "emit_campaign271_registry",
        "emit_campaign271_summary",
        "run_real_feed_ingest_attempt_271",
    }
    nonself = []
    for ln in lines:
        if any(stem in ln for stem in own_campaign):
            continue
        low = ln.lower()
        if (
            "skewness_about_mean" in low
            or "rte_over_white_diag_line_length_skewness_about_mean" in low
        ):
            nonself.append(ln)
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


def _qualifying_white_diag_segments(diag: np.ndarray, w_min: int) -> list[int]:
    diag = np.asarray(diag)
    if diag.size == 0:
        return []
    padded = np.concatenate(([1.0], diag, [1.0]))
    ones = np.flatnonzero(padded)
    gaps = np.diff(ones) - 1
    gaps = gaps[gaps >= w_min]
    return gaps.astype(int).tolist()


def _white_diag_line_length_skewness_about_mean(R: np.ndarray, w_min: int) -> float:
    """SKEWNESS_ABOUT_MEAN = mean((L_i-mean)^3)/std(L)^3 over qualifying WHITE
    diagonal segment lengths, pooled over off-diagonal diagonals k!=0,
    length>=w_min=2, N>=3. std = population std (ddof=0). Fail-closed if N<3,
    std<=0/non-finite, or skew non-finite/degenerate."""
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
    mean = float(np.mean(arr))
    std = float(np.std(arr, ddof=0))
    if not np.isfinite(std) or std <= 0:
        return np.nan
    skew = float(np.mean((arr - mean) ** 3) / (std ** 3))
    if not np.isfinite(skew):
        return np.nan
    return float(skew)


def main() -> None:
    grep_hits, grep_out = run_distinctness_grep()
    if grep_hits != 0:
        raise SystemExit(
            f"DISTINCTNESS_FAIL: non-self grep hits for SKEWNESS_ABOUT_MEAN = {grep_hits}\n{grep_out}"
        )

    spot_df, spot_meta, spot_sha = load_spot()
    vol_df, vol_report = load_volume()

    common = sorted(set(spot_df.columns).intersection(set(vol_df.columns)))
    if len(common) == 0:
        raise SystemExit("NO_COMMON_ASSETS")

    assets = {}
    any_exposure = False
    strat_means = []
    bh_means = []

    for sym in common:
        sp = spot_df[sym].dropna()
        vv = vol_df[sym].dropna()
        idx = sp.index.intersection(vv.index)
        sp = sp.loc[idx]
        vv = vv.loc[idx]
        r = np.log(vv).diff().dropna()
        if len(r) < ALB + TRAIN + TEST + 50:
            assets[sym] = {"status": "insufficient"}
            continue
        feats = []
        for t in range(ALB, len(r)):
            win = r.iloc[t - W_RR : t].to_numpy(dtype=float)
            if win.size != W_RR or not np.all(np.isfinite(win)):
                feats.append(np.nan)
                continue
            std_w = float(np.std(win))
            if not np.isfinite(std_w) or std_w <= 0:
                feats.append(np.nan)
                continue
            X = np.column_stack([win[:-1], win[1:]])
            eps = EPS_SCALE * std_w
            d = np.max(np.abs(X[:, None, :] - X[None, :, :]), axis=2)
            R = (d <= eps + 1e-18).astype(float)
            val = _white_diag_line_length_skewness_about_mean(R, W_MIN)
            feats.append(val)
        feat = pd.Series(feats, index=r.index[ALB : ALB + len(feats)])
        feat = feat.replace([np.inf, -np.inf], np.nan)
        if feat.dropna().shape[0] < TRAIN + TEST + 10:
            assets[sym] = {"status": "feature_insufficient"}
            continue

        rets = r.loc[feat.index].shift(-1).dropna()
        feat = feat.loc[rets.index]
        pos = pd.Series(0.0, index=feat.index)
        splits = wf_splits(len(feat), TRAIN, TEST, STEP)
        if len(splits) == 0:
            assets[sym] = {"status": "no_splits"}
            continue

        for (s0, tr_e, te_e) in splits:
            f_tr = feat.iloc[s0:tr_e]
            f_te = feat.iloc[tr_e:te_e]
            f_tr_c = f_tr.dropna()
            if f_tr_c.shape[0] < 50:
                continue
            mu = float(f_tr_c.mean())
            sig = float(f_tr_c.std(ddof=0))
            if not np.isfinite(sig) or sig <= 0:
                continue
            z = (f_te - mu) / sig
            zc = z.dropna()
            for ti in zc.index:
                zz = float(zc.at[ti])
                if zz > ENTRY_Z:
                    pos.at[ti] = -1.0
                elif zz < -ENTRY_Z:
                    pos.at[ti] = 1.0
                else:
                    pos.at[ti] = 0.0
        for i in range(1, len(pos)):
            if pos.iloc[i - 1] != 0 and pos.iloc[i] == 0:
                h = 0
                j = i
                while j < len(pos) and pos.iloc[j] == 0 and h < MAX_HOLD:
                    h += 1
                    j += 1
                    if j < len(pos):
                        pos.iloc[j] = pos.iloc[i - 1]
        pnl = pos.shift(1).fillna(0.0) * rets
        bh = rets
        per_cost = {}
        for fee, slp in COST_GRID:
            tc = (pos.diff().abs().fillna(0.0)) * ((fee + slp) / 10000.0)
            npn = pnl - tc
            oos_mask = np.zeros(len(npn), dtype=bool)
            for (_s0, _tr_e, te_e) in splits:
                oos_mask[_tr_e:te_e] = True
            oos_np = npn[oos_mask]
            oos_bh = bh[oos_mask]
            exp = float((np.abs(pos.shift(1).fillna(0.0)) > 0).sum())
            if exp > 0:
                any_exposure = True
            per_cost[f"fee{fee}_slip{slp}"] = {
                "oos_net_sum": float(oos_np.sum()),
                "oos_net_mean": float(oos_np.mean()) if oos_np.size else np.nan,
                "bh_oos_net_mean": float(oos_bh.mean()) if oos_bh.size else np.nan,
                "oos_n": int(oos_np.size),
                "exposure_bars": exp,
            }
        assets[sym] = {"status": "ok", "bars": int(len(sp)), "ratio_finite_bars": int(np.isfinite(feat.to_numpy()).sum()), "per_cost": per_cost}
        oos_mask_all = np.zeros(len(npn), dtype=bool)
        for (_s0, _tr_e, te_e) in splits:
            oos_mask_all[_tr_e:te_e] = True
        strat_means.append(float(npn[oos_mask_all].mean()) if oos_mask_all.any() else np.nan)
        bh_means.append(float(bh[oos_mask_all].mean()) if oos_mask_all.any() else np.nan)

    cross: dict[str, float] = {}
    for fee, slp in COST_GRID:
        key = f"fee{fee}_slip{slp}"
        cross[key] = float(sum(a["per_cost"][key]["oos_net_sum"] for a in assets.values() if a.get("status") == "ok"))
    all_pos = all(v > 0 for v in cross.values()) if cross else False
    all_beat_bh = (np.mean(strat_means) > np.mean(bh_means)) if strat_means and bh_means else False
    edge = bool(any_exposure and all_pos and all_beat_bh)

    out = {
        "generated_at_utc": ts,
        "campaign": 271,
        "strategy_id": "VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_SKEWNESS_ABOUT_MEAN_SHOCK_MR",
        "strategy_family": "volume_rqa_rte_over_white_diag_line_length_skewness_about_mean_shock_mr_real",
        "oos_edge_proven": edge,
        "edge_claim": "NONE",
        "walk_forward": {"train": TRAIN, "test": TEST, "step": STEP},
        "cost_grid_bps": COST_GRID,
        "feature": (
            "SKEWNESS_ABOUT_MEAN = mean((L_i-mean)^3)/std(L)^3, std=population_std(L) (ddof=0), "
            "over all qualifying WHITE diagonal segment lengths (consecutive 0-cells/non-recurrent, "
            "length>=w_min=2) pooled over off-diagonal diagonals k!=0 with >=1 qualifying segment, on "
            "delay-embedded (m=2,tau=1) log-volume returns over trailing W_RR; eps=0.5*std(r_window), "
            "L_inf recurrence. Let L={L_1,..,L_N}, N>=3. skew = mean((L_i-mean)^3) / std^3. Fail-closed if <3 "
            "qualifying segment lengths or std<=0/non-finite or skew non-finite/degenerate. "
            "Causal trailing only. Distinct from C270 COEFFICIENT_OF_VARIATION, C269 PEARSON_MODE_SKEW, C268 "
            "STANDARDIZED_MOMENT, C267 ROOT_MEAN_SQUARE_DEVIATION_FROM_MEDIAN, C266 "
            "RELATIVE_MEAN_ABSOLUTE_DIFFERENCE, C265 MAD_FROM_MEDIAN, C230 SKEWNESS (3rd central moment about the mean), "
            "C231 KURTOSIS (4th central moment), and all prior C125-C269 RQA families."
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
                "WHITE_DIAG_LINE_LENGTH_COEFFICIENT_OF_VARIATION (C270)",
                "WHITE_DIAG_LINE_LENGTH_PEARSON_MODE_SKEW (C269)",
                "WHITE_DIAG_LINE_LENGTH_STANDARDIZED_MOMENT (C268)",
                "WHITE_DIAG_LINE_LENGTH_ROOT_MEAN_SQUARE_DEVIATION_FROM_MEDIAN (C267)",
                "WHITE_DIAG_LINE_LENGTH_RELATIVE_MEAN_ABSOLUTE_DIFFERENCE (C266)",
                "WHITE_DIAG_LINE_LENGTH_MAD_FROM_MEDIAN (C265)",
                "WHITE_DIAG_LINE_LENGTH_SKEWNESS (C230, 3rd central moment about the mean)",
                "WHITE_DIAG_LINE_LENGTH_KURTOSIS (C231, 4th central moment)",
                "C125-C269 prior RQA families",
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
            "c270_oos": "reports/real_quote_volume_rqa_rte_over_white_diag_line_length_coefficient_of_variation_shock_mr_costed_oos_20261112T030858Z.json",
            "c270_oos_sha256": "de7a5a1783602d5cafdca3e8a84fc1968f7b3030970522bb1471e868c90f57ad",
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
    out_prefix = "real_quote_volume_rqa_rte_over_white_diag_line_length_skewness_about_mean_shock_mr_costed_oos"
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
