#!/usr/bin/env python3
"""Generate Campaign 73 artifacts (fail-closed, real data only).

Campaign 73 — Path R-B: a GENUINELY DIFFERENT pre-stated hypothesis on validated
real_quote_volume (Binance spot klines col 5), NOT a rerun of C23/C40–C72.

PRE-STATED HYPOTHESIS (fixed before seeing OOS results):
"Volume Kelly (Decile) Skewness Shock Mean Reversion"

Mechanic (pre-stated):
- For each asset, compute rolling Kelly decile skewness K_t of quote volume over
  a causal window W=48h:
    P10_t = 10th percentile(qvol[t-W+1..t])
    P50_t = median(qvol[t-W+1..t])
    P90_t = 90th percentile(qvol[t-W+1..t])
    IDR_t = P90_t - P10_t
    K_t   = (P90_t + P10_t - 2*P50_t) / IDR_t   if IDR_t > 0 else NaN
  K_t in [-1,1] (bounded, rank/decile-based asymmetry of the volume
  distribution): K_t>0 => upper-decile mass stretched above median relative to
  lower; K_t<0 => lower-decile mass stretched. Measures DIRECTION/ASYMMETRY of
  decile spread, not its magnitude.

Distinctness (pre-stated; differs from C23/C40–C72):
- C66 IDR (P90-P10): same decile CUTPOINTS but IDR is a DISPERSION MAGNITUDE
  (symmetric span size). Kelly normalizes the above/below imbalance into an
  ASYMMETRY coefficient (direction) — fundamentally different transform (ratio
  vs magnitude) on the same decile region.
- C72 Bowley (P75+P25-2*P50)/(P75-P25): same asymmetry-ratio family but uses
  QUARTILE cutpoints (P25/P75, 50% central mass). Kelly uses DECILE cutpoints
  (P10/P90, 80% mass, 10% tails each side) — different tail sensitivity and
  cutpoints (inner vs outer rank region).
- C40 Fisher skewness: 3rd standardized moment, mean-centered, unbounded, uses
  all observations with L2/L3 moment weighting. Kelly is rank/decile-based
  (only P10,P50,P90), bounded, no moments/mean; different statistic family.
- Not level/ROC/ratio/cumulative/partition/imbalance/moments/entropies/
  Hurst-SampEn/autocorr/corr/beta/dispersion-magnitude transforms tested in
  C23/C40-C72.

- z-score K_t over ZLB=168h (causal) -> d_z.
- Mean-revert decile-asymmetry shocks (fade deviations from typical volume
  asymmetry): d_z >= ENTRY_Z (1.25) -> SHORT (abnormally upper-skewed volume
  distribution; fade); d_z <= -ENTRY_Z (-1.25) -> LONG (abnormally lower-skewed;
  fade); |d_z| < EXIT_Z (0.25) -> no new entry.
- Exit when |d_z| < EXIT_Z, hold >= MAX_HOLD (12h), or signal flips.
- Execution shift t -> t+1 (causal). WF rolling 720/168/168. Cost grid 0-40bps
  (fee,slip pairs). B&H benchmark on same WF windows.

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
log = logging.getLogger("c73")


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


def rolling_kelly_decile_skew(s: pd.Series, w: int) -> pd.Series:
    """Causal rolling Kelly decile skewness = (P90+P10-2*P50)/IDR.
    Rank/decile-based asymmetry (direction), bounded [-1,1]. Distinct from C66
    IDR (P90-P10 dispersion magnitude, same cutpoints) — Kelly is an asymmetry
    ratio, not magnitude. Distinct from C72 Bowley (quartile P25/P75 cutpoints)
    — Kelly uses decile P10/P90 (outer 80% mass). Distinct from C40 Fisher 3rd
    standardized moment (mean-centered, unbounded).
    """
    arr = s.values.astype(float)
    out = np.full(len(arr), np.nan, dtype=float)
    for i in range(w - 1, len(arr)):
        seg = arr[i - w + 1 : i + 1]
        if not np.all(np.isfinite(seg)):
            continue
        p10 = float(np.percentile(seg, 10))
        p50 = float(np.percentile(seg, 50))
        p90 = float(np.percentile(seg, 90))
        idr = p90 - p10
        if idr > 1e-12 and np.isfinite(idr):
            out[i] = (p90 + p10 - 2.0 * p50) / idr
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
    sk = rolling_kelly_decile_skew(qvol, W)
    dz = zscore_causal(sk, ZLB)
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
    # align
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

    # aggregate across assets per cost
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
        "artifact": f"real_quote_volume_kelly_decile_skewness_shock_mr_costed_oos_{UTC}.json",
        "campaign": 73,
        "generated_at_utc": UTC,
        "fail_closed": True,
        "real_data_only": True,
        "fabricated_data": False,
        "no_proxies_labeled_real": True,
        "hypothesis": {
            "name": "Volume Kelly (Decile) Skewness Shock Mean Reversion",
            "family": "rolling_kelly_decile_skewness_volume_shock_mr",
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
            "formula": "K_t=(P90+P10-2*P50)/(P90-P10); z(d_z,168)->fade shocks d_z>=1.25 SHORT, <=-1.25 LONG; t->t+1",
            "distinctness": [
                "C66 IDR=P90-P10: same decile cutpoints but IDR is a dispersion MAGNITUDE (symmetric span). Kelly normalizes decile imbalance into an ASYMMETRY coefficient (direction) — different transform (ratio vs magnitude).",
                "C72 Bowley=(P75+P25-2*P50)/(P75-P25): same asymmetry-ratio family but QUARTILE cutpoints (P25/P75, 50% central). Kelly uses DECILE cutpoints (P10/P90, 80% mass, outer tails) — different tail sensitivity/cutpoints.",
                "C40 Fisher skewness: 3rd standardized moment, mean-centered, unbounded, all observations (L2/L3). Kelly is rank/decile-based (P10,P50,P90 only), bounded [-1,1], no moments/mean — different statistic family.",
                "Not level/ROC/ratio/cumulative/partition/imbalance/moments/entropies/Hurst-SampEn/autocorr/corr/beta/dispersion-magnitude transforms tested in C23/C40-C72.",
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
