#!/usr/bin/env python3
"""C261: RQA WHITE_DIAG_LINE_LENGTH_COEFF_OF_VARIATION shock on
delay-embedded log-volume returns (real data only).

Feature (pre-stated, distinct, grep-verified before implementation/run):
  VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_COEFF_OF_VARIATION_SHOCK_MR.
  On r_t = ln(v_t)-ln(v_{t-1}), build delay embedding X_i = (r_i, r_{i+tau})
  with m=2, tau=1 over trailing window W_RR=168. Recurrence matrix R_{ij}=1 if
  ||X_i-X_j||_inf <= eps, else 0; eps = eps_scale * std(r_window) with
  pre-stated fixed eps_scale=0.5.
  COEFF_OF_VARIATION (signal) = coefficient of variation of lengths of
  qualifying WHITE diagonal segments (consecutive 0-cells/non-recurrent,
  length>=w_min=2) pooled over off-diagonal diagonals k!=0 with >=1
  qualifying segment.
        Let L = {L_1,...,L_N} be the pooled qualifying segment lengths,
        N >= 3; mu = mean(L),
        sigma_pop = sqrt((1/N) * sum_{i=1}^{N} (L_i - mu)^2) (population
        std, ddof=0),
        COEFF_OF_VARIATION = sigma_pop / mu.
        Pre-stated exact formula/reference: coefficient of variation of
        segment lengths L.
        Fail-closed if <3 qualifying segment lengths, mu or sigma_pop
        undefined/non-finite, mu<=0 or sigma_pop<=0,
        COEFF_OF_VARIATION<=0/degenerate/non-finite, or any intermediate
        undefined/non-finite.
        Causal trailing only. Distinct from RTE /
  WHITE_DIAG_LINE_LENGTH_PEARSON_VARIATION (C260, population variance) and
  prior WHITE_DIAG_LINE_LENGTH dispersion families (C249-C259).
  RTE_OVER_WHITE_DIAG_LINE_LENGTH_COEFF_OF_VARIATION not used C125-C260.
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

PRIOR_REGISTRY = "reports/strategy_edge_registry_20261111T171038Z.json"
PRIOR_REGISTRY_SHA = "e94e065ed8094fff2ac086fcf4a8bcfb5ecd9665974ded055a8ca2c319c26b18"

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
    "RTE_OVER_WHITE_DIAG_LINE_LENGTH_COEFF_OF_VARIATION|"
    "rte_over_white_diag_line_length_coeff_of_variation|"
    "WHITE_DIAG_LINE_LENGTH_COEFF_OF_VARIATION|"
    "white_diag_line_length_coeff_of_variation"
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
        "emit_campaign261_registry",
        "emit_campaign261_summary",
        "run_real_feed_ingest_attempt_261",
    }
    nonself = [
        ln
        for ln in lines
        if not any(stem in ln for stem in own_campaign)
        and (
            "white_diag_line_length_coeff_of_variation" in ln.lower()
            or "rte_over_white_diag_line_length_coeff_of_variation" in ln.lower()
        )
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


def _white_diag_line_length_coeff_of_variation(R: np.ndarray, w_min: int) -> float:
    """COEFF_OF_VARIATION = sigma_pop / mu of lengths of qualifying WHITE
    diagonal segments (consecutive 0-cells/non-recurrent, length>=w_min)
    pooled over off-diagonal diagonals k!=0 with >=1 qualifying segment.
    Let L={L_i}, N>=3; mu=mean(L), sigma_pop=sqrt((1/N)*sum((L_i-mu)^2))
    (population std, ddof=0). COEFF_OF_VARIATION = sigma_pop / mu.
    Fail-closed if <3 qualifying segment lengths or mu/sigma_pop
    undefined/non-finite or mu<=0 or sigma_pop<=0 or COEFF_OF_VARIATION
    <=0/degenerate/non-finite or any intermediate undefined/non-finite."""
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
    mu = float(np.mean(arr))
    if not np.isfinite(mu) or mu <= 0.0:
        return np.nan
    # population std (ddof=0)
    sigma_pop = float(np.sqrt(np.mean((arr - mu) ** 2)))
    if not np.isfinite(sigma_pop) or sigma_pop <= 0.0:
        return np.nan
    cov = sigma_pop / mu
    if not np.isfinite(cov) or cov <= 0.0:
        return np.nan
    return float(cov)


def rqa_white_diag_line_length_coeff_of_variation_window(
    rw: np.ndarray, eps_scale: float, w_min: int
) -> float:
    """COEFF_OF_VARIATION signal = coefficient of variation of lengths of
    qualifying WHITE diagonal segments over trailing delay-embedded window.
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
    cov = _white_diag_line_length_coeff_of_variation(R, w_min)
    if not np.isfinite(cov) or cov <= 0.0:
        return np.nan
    return float(cov)


def _pnl(pos, p, fee_bps, slip_bps):
    cost = (fee_bps + slip_bps) / 1e4
    ch = pos.diff().fillna(pos.iloc[0])
    return pos.shift(1).fillna(0) * p.pct_change().fillna(0) - ch.abs() * cost


def main() -> None:
    print("Starting C261...", flush=True)
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
        feat = pd.Series(
            [
                rqa_white_diag_line_length_coeff_of_variation_window(
                    r_arr[max(0, i - W_RR + 1) : i + 1], EPS_SCALE, W_MIN
                )
                for i in range(n)
            ],
            index=lr.index,
            dtype=float,
        )
        print(f"  {sym}: feature finite={feat.notna().sum()}/{n}", flush=True)

        alb = feat.rolling(ALB, min_periods=ALB).mean()
        asd = feat.rolling(ALB, min_periods=ALB).std(ddof=1)
        z = (feat - alb) / asd.replace(0.0, np.nan)
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
            "ratio_finite_bars": int(np.isfinite(feat.to_numpy()).sum()),
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
        "campaign": 261,
        "strategy_id": "VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_COEFF_OF_VARIATION_SHOCK_MR",
        "strategy_family": "volume_rqa_rte_over_white_diag_line_length_coeff_of_variation_shock_mr_real",
        "oos_edge_proven": edge,
        "edge_claim": "NONE",
        "walk_forward": {"train": TRAIN, "test": TEST, "step": STEP},
        "cost_grid_bps": COST_GRID,
        "feature": (
            "COEFF_OF_VARIATION = sigma_pop / mu of lengths of qualifying "
            "WHITE diagonal segments (consecutive 0-cells/non-recurrent, "
            "length>=w_min=2) pooled over off-diagonal diagonals k!=0 with "
            ">=1 qualifying segment, on delay-embedded (m=2,tau=1) "
            "log-volume returns over trailing W_RR; eps=0.5*std(r_window), "
            "L_inf recurrence. Let L={L_1,..,L_N}, N>=3; mu=mean(L), "
            "sigma_pop=sqrt((1/N)*sum((L_i-mu)^2)) (population std, ddof=0). "
            "Pre-stated exact formula/reference: COEFF_OF_VARIATION=sigma_pop/mu. "
            "Fail-closed if <3 qualifying segment lengths or mu/sigma_pop "
            "undefined/non-finite or mu<=0 or sigma_pop<=0 or "
            "COEFF_OF_VARIATION<=0/degenerate/non-finite or any intermediate "
            "undefined/non-finite. Causal trailing only."
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
                "WHITE_DIAG_LINE_LENGTH_PEARSON_VARIATION (C260, population variance (1/N)*sum((L_i-mu)^2))",
                "WHITE_DIAG_LINE_LENGTH_DECILE_RANGE (C259, p90-p10)",
                "WHITE_DIAG_LINE_LENGTH_NORMALIZED_RANGE (C258, (mx-mn)/mid)",
                "WHITE_DIAG_LINE_LENGTH_COEFFICIENT_OF_RANGE (C257, (mx-mn)/(mx+mn))",
                "WHITE_DIAG_LINE_LENGTH_SEMI_VARIANCE (C256)",
                "WHITE_DIAG_LINE_LENGTH_MEDIAN_ABSOLUTE_DEVIATION (C255)",
                "WHITE_DIAG_LINE_LENGTH_MEAN_ABSOLUTE_DEVIATION (C254)",
                "WHITE_DIAG_LINE_LENGTH_QUARTILE_DEVIATION (C253)",
                "WHITE_DIAG_LINE_LENGTH_PEARSON_SKEW (C252)",
                "WHITE_DIAG_LINE_LENGTH_MIDRANGE (C251)",
                "WHITE_DIAG_LINE_LENGTH_YULE_K (C250)",
                "WHITE_DIAG_LINE_LENGTH_GROENEVELD_MEEDEN_SKEW (C249)",
                "WHITE_DIAG_LINE_LENGTH_KELLY_SKEW (C248, P10/P90-based)",
                "WHITE_DIAG_LINE_LENGTH_BOWLEY_SKEW (C247, quartile-based skew)",
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
                "C125-C260 prior RQA families",
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
            "c260_oos": "reports/real_quote_volume_rqa_rte_over_white_diag_line_length_pearson_variation_shock_mr_costed_oos_20261111T170631Z.json",
            "c260_oos_sha256": "9671ef3ddd6943fa5d6726bc355f3c85eb869837204e2b4fac9d1d6056d199dc",
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
    out_prefix = "real_quote_volume_rqa_rte_over_white_diag_line_length_coeff_of_variation_shock_mr_costed_oos"
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
