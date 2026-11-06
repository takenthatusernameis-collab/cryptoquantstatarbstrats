#!/usr/bin/env python3
"""Generate Campaign 76 artifacts (fail-closed, real data only).

Campaign 76 — Path R-B: a GENUINELY DIFFERENT pre-stated hypothesis on
validated real_quote_volume (Binance spot klines col 5), NOT a rerun of
C23/C40–C75.

PRE-STATED HYPOTHESIS (fixed before seeing OOS results):
"Volume Theil L (GE(0) Mean-Log Deviation) Inequality Shock Mean Reversion"

Mechanic (pre-stated):
- For each asset, compute rolling Theil L index (generalized entropy GE(0),
  mean log deviation) of quote-volume observations over a causal window W=48h:
    μ_t = mean(x_i) over window
    TL_t = mean( ln(μ_t / x_i) ) over valid x_i > 0 in window
  Requires μ_t>0 and at least 80% positive observations. TL>=0; larger TL means
  greater inequality with sensitivity to the LOWER tail (small-volume
  observations). Computed on raw volume observations (not normalized shares).

Distinctness (pre-stated; differs from C23/C40–C75):
- C74 Theil T (GE(1)): mean((x/μ)*ln(x/μ)) = value-weighted r*ln(r) form using
  (x/μ)*ln(x/μ) per observation. GE(0)/Theil L uses mean(ln(μ/x)) = mean of
  log-ratio of mean to observation — different generalized-entropy order,
  different functional form, different tail sensitivity (GE(0) lower-tail,
  GE(1) upper-tail). Not the same transform with a sign/scale change.
- C41 Shannon entropy: binned/histogram entropy (-Σp log p over discretized
  bins). TL is GE(0) inequality on raw observations, no binning, no histogram.
- C75 Rényi-2 collision entropy H2: -ln(Σ p_i^2) over normalized shares
  p_i=x_i/Σx_i (HHI/collision, order α=2). Different object (shares/HHI) and
  form vs GE(0) mean log deviation.
- C51 Gini mean-difference: L1 pairwise inequality, no logs.
- C45 CV (σ/μ): second-moment dispersion, no log-ratio per observation.
- C48 kurtosis: fourth-moment tail weight.
- Not asymmetry ratios (C72 Bowley, C73 Kelly), not dispersion magnitudes
  (C66 IDR, C69/70 LQD/UQD), not permutation/sample/Hurst/autocorr/corr/beta,
  not level/ROC/ratio/cumulative/partition/imbalance transforms in C23/C40-C75.

- z-score TL_t over ZLB=168h (causal) -> d_z.
- Mean-revert inequality shocks (fade deviations):
  d_z >= ENTRY_Z (1.25) -> SHORT (abnormally high GE(0) inequality; fade);
  d_z <= -ENTRY_Z (-1.25) -> LONG (abnormally low GE(0) inequality; fade);
  |d_z| < EXIT_Z (0.25) -> no new entry.
- Exit when |d_z| < EXIT_Z, hold >= MAX_HOLD (12h), or signal flips.
- Execution shift t -> t+1 (causal). WF rolling 720/168/168. Cost grid 0-40bps.
  B&H benchmark on same WF windows.

Edge rule (pre-stated, fail-closed): oos_edge_proven=true IFF exposure>0 AND ALL
cost-grid slices OOS net>0 AND OOS net beats B&H on same WF windows. Else false.
No in-sample tuning, no threshold weakening, no fabricated data/proxies.
"""
from __future__ import annotations

import hashlib
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from data.real_feed_loader import validate_and_load_real_feed  # noqa: E402

UTC = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
REPORTS = ROOT / "reports"
CACHE = ROOT / "data" / "cache"
VOL_META = CACHE / "volume_1h_full.meta.json"
VOL_PROV = CACHE / "volume_1h_full.provenance.json"

ASSETS = ["ADA", "AVAX", "BNB", "BTC", "DOT", "ETH", "LINK", "LTC", "POL", "SOL", "XRP"]
W = 48
ZLB = 168
ENTRY_Z = 1.25
EXIT_Z = 0.25
MAX_HOLD = 12
WF_TRAIN, WF_TEST, WF_STEP = 720, 168, 168
COST_GRID = [(0, 0), (5, 5), (10, 10), (20, 20), (40, 40)]
SPOT_CACHE = "0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7"
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("c76")


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for ch in iter(lambda: f.read(1 << 20), b""):
            h.update(ch)
    return h.hexdigest()


def load_volume_wide():
    if not VOL_PROV.exists():
        raise FileNotFoundError(f"volume provenance certificate missing: {VOL_PROV}")
    prov = json.loads(VOL_PROV.read_text(encoding="utf-8"))
    long_df, report = validate_and_load_real_feed(VOL_META, "real_quote_volume", provenance=prov)
    if not report.get("ok"):
        raise RuntimeError(f"volume feed failed validation: {report}")
    wide = long_df.pivot(index="timestamp_utc", columns="symbol", values="quote_volume_usdt").sort_index()
    wide.index = pd.to_datetime(wide.index, utc=True)
    return wide, report


def rolling_theil_l_ge0(s: pd.Series, w: int) -> pd.Series:
    """Causal rolling Theil L / GE(0) mean log deviation: mean(ln(mu/x)), x>0.
    Distinct from C74 Theil T GE(1) mean((x/mu)*ln(x/mu)) (upper-tail, r*ln r),
    C41 Shannon binned, C75 Rényi-2 H2=-ln(Σp^2), C51 Gini L1, C45 CV, etc.
    """
    arr = s.values.astype(float)
    out = np.full(len(arr), np.nan, dtype=float)
    for i in range(w - 1, len(arr)):
        seg = arr[i - w + 1 : i + 1]
        if not np.all(np.isfinite(seg)):
            continue
        pos_mask = seg > 1e-18
        if pos_mask.sum() < w * 0.8:
            continue
        pos = seg[pos_mask]
        mu = float(np.mean(pos))
        if mu <= 1e-18 or not np.isfinite(mu):
            continue
        tl = float(np.mean(np.log(mu / pos)))
        if np.isfinite(tl):
            out[i] = tl
    return pd.Series(out, index=s.index)


def zscore_causal(s: pd.Series, lb: int) -> pd.Series:
    m = s.rolling(lb, min_periods=max(24, lb // 3)).mean()
    sd = s.rolling(lb, min_periods=max(24, lb // 3)).std(ddof=0)
    return (s - m) / sd.replace(0, np.nan)


def wf_slices(n: int):
    out = []
    t = WF_TRAIN
    while t + WF_TEST <= n:
        out.append((t, t + WF_TEST))
        t += WF_STEP
    return out


def load_spot():
    pkl = CACHE / f"{SPOT_CACHE}.pkl"
    meta = json.loads((CACHE / f"{SPOT_CACHE}.meta.json").read_text(encoding="utf-8"))
    df = pd.read_pickle(pkl)  # noqa: S301
    return df, meta, sha256_file(pkl)


def run_backtest(close: pd.Series, qvol: pd.Series, fee_bps: float, slip_bps: float):
    ret = close.pct_change().shift(-1)  # t -> t+1 exec
    sig_base = rolling_theil_l_ge0(qvol, W)
    dz = zscore_causal(sig_base, ZLB)
    n = len(close)
    pos = np.zeros(n)
    cur = 0.0
    hold = 0
    for t in range(n):
        z = dz.iloc[t]
        if not np.isfinite(z) or not np.isfinite(ret.iloc[t]):
            pos[t] = cur
            if cur != 0:
                hold += 1
            continue
        if cur != 0 and (
            abs(z) < EXIT_Z
            or hold >= MAX_HOLD
            or (cur > 0 and z >= ENTRY_Z)
            or (cur < 0 and z <= -ENTRY_Z)
        ):
            if (cur > 0 and z >= ENTRY_Z) or (cur < 0 and z <= -ENTRY_Z):
                cur = -1.0 if z >= ENTRY_Z else 1.0
                hold = 0
            else:
                cur = 0.0
                hold = 0
        if cur == 0 and abs(z) >= ENTRY_Z:
            cur = -1.0 if z >= ENTRY_Z else 1.0
            hold = 0
        pos[t] = cur
        if cur != 0:
            hold += 1
    pos_s = pd.Series(pos, index=close.index)
    turnover = pos_s.diff().abs().fillna(abs(pos_s.iloc[0]) if len(pos_s) else 0)
    cost = turnover * (fee_bps + slip_bps) / 10000.0
    strat = pos_s * ret.fillna(0) - cost
    bh = ret.fillna(0)
    slices = []
    for s1, s2 in wf_slices(n):
        sl = slice(s1, s2)
        sr = strat.iloc[sl]
        br = bh.iloc[sl]
        if len(sr) == 0:
            continue
        slices.append(
            {
                "start": str(close.index[s1]),
                "end": str(close.index[min(s2 - 1, n - 1)]),
                "bars": int(len(sr)),
                "oos_net": float(sr.sum()),
                "oos_bh": float(br.sum()),
                "oos_turnover": float(turnover.iloc[sl].sum()),
                "oos_exposure_frac": float((pos_s.iloc[sl] != 0).mean()),
            }
        )
    any_exposure = bool((pos_s != 0).any())
    oos_net = float(sum(x["oos_net"] for x in slices))
    oos_bh = float(sum(x["oos_bh"] for x in slices))
    return {
        "any_exposure": any_exposure,
        "n_slices": len(slices),
        "oos_net_sum": oos_net,
        "oos_bh_sum": oos_bh,
        "beats_bh": bool(oos_net > oos_bh),
        "slices": slices,
    }


def main():
    REPORTS.mkdir(parents=True, exist_ok=True)
    vol_wide, vol_report = load_volume_wide()
    spot_df, spot_meta, spot_sha = load_spot()
    common_idx = vol_wide.index.intersection(spot_df.index)
    vol_wide = vol_wide.loc[common_idx]
    spot_df = spot_df.loc[common_idx]
    assets = [a for a in ASSETS if a in vol_wide.columns and a in spot_df.columns]
    log.info("assets=%s common_bars=%s", assets, len(common_idx))

    per_asset = {}
    for asset in assets:
        close = spot_df[asset].astype(float)
        qvol = vol_wide[asset].astype(float)
        by_cost = {}
        for fee, slip in COST_GRID:
            key = f"fee{fee}_slip{slip}"
            by_cost[key] = run_backtest(close, qvol, fee, slip)
        per_asset[asset] = {"by_cost": by_cost}

    aggregate = {}
    for fee, slip in COST_GRID:
        key = f"fee{fee}_slip{slip}"
        nets = [per_asset[a]["by_cost"][key]["oos_net_sum"] for a in assets]
        bhs = [per_asset[a]["by_cost"][key]["oos_bh_sum"] for a in assets]
        beats = [1.0 if per_asset[a]["by_cost"][key]["beats_bh"] else 0.0 for a in assets]
        aggregate[key] = {
            "n_assets": len(assets),
            "mean_oos_net_across_assets": float(np.mean(nets)) if nets else None,
            "mean_oos_bh_across_assets": float(np.mean(bhs)) if bhs else None,
            "mean_frac_beats_bh": float(np.mean(beats)) if beats else None,
        }

    any_exposure = any(
        per_asset[a]["by_cost"][f"fee{COST_GRID[0][0]}_slip{COST_GRID[0][1]}"]["any_exposure"]
        for a in assets
    )
    all_costs_positive = all(aggregate[k]["mean_oos_net_across_assets"] > 0 for k in aggregate)
    beats_bh_rule = all(aggregate[k]["mean_frac_beats_bh"] == 1.0 for k in aggregate)
    oos_edge_proven = bool(any_exposure and all_costs_positive and beats_bh_rule)

    out = {
        "artifact": f"real_quote_volume_theil_l_ge0_mld_shock_mr_costed_oos_{UTC}.json",
        "campaign": 76,
        "generated_at_utc": UTC,
        "fail_closed": True,
        "real_data_only": True,
        "fabricated_data": False,
        "no_proxies_labeled_real": True,
        "hypothesis": {
            "name": "Volume Theil L (GE(0) Mean-Log Deviation) Inequality Shock Mean Reversion",
            "family": "rolling_theil_l_ge0_volume_shock_mr",
            "path": "R-B",
            "pre_stated": True,
            "params": {
                "W": W,
                "ZLB": ZLB,
                "ENTRY_Z": ENTRY_Z,
                "EXIT_Z": EXIT_Z,
                "MAX_HOLD": MAX_HOLD,
                "WF_TRAIN": WF_TRAIN,
                "WF_TEST": WF_TEST,
                "WF_STEP": WF_STEP,
            },
            "formula": "TL_t=mean(ln(mu_t/x_i)) over x_i>0, W=48 (GE(0)/MLD, lower-tail sensitive); z(d_z,168)->fade shocks d_z>=1.25 SHORT, <=-1.25 LONG; t->t+1",
            "distinctness": [
                "C74 Theil T (GE(1)): mean((x/mu)*ln(x/mu)) = upper-tail, value-weighted r*ln(r). GE(0)/Theil L uses mean(ln(mu/x)) — different generalized-entropy order, functional form, and tail sensitivity (GE(0) lower-tail). Not a sign/scale of C74.",
                "C41 Shannon entropy: binned/histogram (-Σp log p over discretized bins). TL is GE(0) inequality on raw observations, no binning/histogram.",
                "C75 Rényi-2 collision entropy H2: -ln(Σ p_i^2) over normalized shares p_i=x_i/Σx_i (HHI/collision, α=2). Different object/form vs GE(0) mean log deviation.",
                "C51 Gini mean-difference: L1 pairwise inequality, no logs.",
                "C45 CV (σ/μ): second-moment dispersion, no log-ratio per observation.",
                "C48 kurtosis: fourth-moment tail weight.",
                "Not asymmetry ratios (C72 Bowley, C73 Kelly), not dispersion magnitudes (C66 IDR, C69/70 LQD/UQD), not permutation/sample/Hurst/autocorr/corr/beta, not level/ROC/ratio/cumulative/partition/imbalance transforms in C23/C40-C75.",
            ],
            "cost_grid_bps": COST_GRID,
        },
        "data": {
            "assets": assets,
            "common_bars": int(len(common_idx)),
            "date_start": str(common_idx.min()),
            "date_end": str(common_idx.max()),
            "feed": "real_quote_volume",
            "real_data_only": True,
            "fabricated": False,
            "spot_cache": SPOT_CACHE,
            "spot_meta": str(spot_meta),
            "spot_sha256": spot_sha,
            "volume_meta_file": str(VOL_META),
            "volume_meta_sha256": sha256_file(VOL_META),
            "volume_pkl_file": str(CACHE / "volume_1h_full.pkl"),
            "volume_pkl_sha256": sha256_file(CACHE / "volume_1h_full.pkl"),
            "provenance_file": str(VOL_PROV),
            "provenance_sha256": sha256_file(VOL_PROV),
            "volume_validation": vol_report,
        },
        "per_asset": per_asset,
        "aggregate": aggregate,
        "any_exposure": any_exposure,
        "all_costs_positive": all_costs_positive,
        "beats_bh_rule": beats_bh_rule,
        "oos_edge_proven": oos_edge_proven,
        "edge_rule_pre_stated": "oos_edge_proven=true IFF exposure>0 AND ALL cost-grid slices OOS net>0 AND beats B&H on same WF windows; else false.",
    }
    path = REPORTS / out["artifact"]
    path.write_text(json.dumps(out, indent=2, sort_keys=True, default=str) + "\n")
    log.info("wrote %s oos_edge_proven=%s any_exposure=%s", path, oos_edge_proven, any_exposure)
    print(json.dumps({"wrote": str(path), "oos_edge_proven": oos_edge_proven, "any_exposure": any_exposure, "aggregate": aggregate}))


if __name__ == "__main__":
    main()
