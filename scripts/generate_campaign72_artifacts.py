#!/usr/bin/env python3
"""Generate Campaign 72 artifacts (fail-closed, real data only).

Campaign 72 — Path R-B: a GENUINELY DIFFERENT pre-stated hypothesis on validated
real_quote_volume (Binance spot klines col 5), NOT a rerun of C23/C40–C71.

PRE-STATED HYPOTHESIS (fixed before seeing OOS results):
"Volume Bowley (Quartile/Galton) Skewness Shock Mean Reversion"

Mechanic (pre-stated):
- For each asset, compute rolling Bowley (quartile/Galton) skewness B_t of quote
  volume over a causal window W=48h:
    P25_t = 25th percentile(qvol[t-W+1..t])
    P50_t = median(qvol[t-W+1..t])
    P75_t = 75th percentile(qvol[t-W+1..t])
    IQR_t = P75_t - P25_t
    B_t   = (P75_t + P25_t - 2*P50_t) / IQR_t   if IQR_t > 0 else NaN
  B_t in [-1,1] (bounded, rank/quartile-based asymmetry of the volume
  distribution): B_t>0 => upper-quartile mass stretched above median relative to
  lower; B_t<0 => lower-quartile mass stretched. Measures DIRECTION/ASYMMETRY of
  quartile spread, not its magnitude.
- Genuinely different from C40 Fisher skewness (3rd standardized moment, mean-
  centered, unbounded, uses all observations with L2/L3 moment weighting):
  Bowley is rank/quartile-based (only P25,P50,P75), bounded, no moments/mean.
  Different statistic family and sensitivity (robust to tails/extremes).
- Distinct from C62 IQR (P75-P25, dispersion magnitude — symmetric span) and
  C70 LQD (P50-P25, below-median magnitude) / C71 UQD (P75-P50, above-median
  magnitude): those measure SPREAD SIZE on quartile sides; Bowley normalizes the
  above/below imbalance into an ASYMMETRY coefficient (direction). Same quartile
  inputs but a fundamentally different transform (asymmetry ratio vs magnitude).
- Distinct from C66 IDR (P90-P10 dispersion). Distinct from C68/C69 upper semi-
  variance/MAD (above-MEAN, L2^2/L1 magnitude). Distinct from C67 lower semi-
  variance. Distinct from C61/C65 MAD/MeanAD (full-distribution centered L1
  magnitude). Not level/ROC/ratio/cumulative/partition/imbalance/moments/
  entropies/Hurst-SampEn/autocorr/corr/beta/dispersion-magnitude transforms
  tested in C23/C40-C71.
- z-score B_t over ZLB=168h (causal) -> d_z.
- Mean-revert quartile-asymmetry shocks (fade deviations from typical volume
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
import math
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
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("c72")


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


def rolling_bowley(s: pd.Series, w: int) -> pd.Series:
    """Causal rolling Bowley (quartile/Galton) skewness = (P75+P25-2*P50)/IQR.
    Rank/quartile-based asymmetry (direction), bounded [-1,1]. Distinct from C40
    Fisher skewness (3rd standardized moment, mean-centered, unbounded). Distinct
    from C62/C70/C71/C66 quartile dispersion magnitudes (spread size) — Bowley is
    an asymmetry ratio of the same quartile region, not a magnitude.
    """
    arr = s.values.astype(float)
    out = np.full(len(arr), np.nan, dtype=float)
    for i in range(w - 1, len(arr)):
        seg = arr[i - w + 1 : i + 1]
        if not np.all(np.isfinite(seg)):
            continue
        p25 = float(np.percentile(seg, 25))
        p50 = float(np.percentile(seg, 50))
        p75 = float(np.percentile(seg, 75))
        iqr = p75 - p25
        if iqr > 1e-12 and np.isfinite(iqr):
            out[i] = (p75 + p25 - 2.0 * p50) / iqr
    return pd.Series(out, index=s.index)


def zscore_causal(s: pd.Series, lb: int) -> pd.Series:
    m = s.rolling(lb, min_periods=max(24, lb // 3)).mean()
    sd = s.rolling(lb, min_periods=max(24, lb // 3)).std(ddof=0)
    z = (s - m) / sd.replace(0, np.nan)
    return z


def wf_slices(n: int):
    out = []
    t = WF_TRAIN
    while t + WF_TEST <= n:
        out.append((t, t + WF_TEST))
        t += WF_STEP
    return out


SPOT_CACHE = "0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7"


def load_spot():
    pkl = CACHE / f"{SPOT_CACHE}.pkl"
    meta = json.loads((CACHE / f"{SPOT_CACHE}.meta.json").read_text(encoding="utf-8"))
    df = pd.read_pickle(pkl)  # noqa: S301
    return df, meta, sha256_file(pkl)


def run_backtest(close: pd.Series, qvol: pd.Series, fee_bps: float, slip_bps: float):
    ret = close.pct_change().shift(-1)  # t -> t+1 exec
    bow = rolling_bowley(qvol, W)
    dz = zscore_causal(bow, ZLB)
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
        if cur != 0 and (abs(z) < EXIT_Z or hold >= MAX_HOLD or (cur > 0 and z >= ENTRY_Z) or (cur < 0 and z <= -ENTRY_Z)):
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
    # WF
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
    spot_df.index = pd.to_datetime(spot_df.index, utc=True)
    common_idx = vol_wide.index.intersection(spot_df.index)
    if len(common_idx) < WF_TRAIN + WF_TEST + ZLB + W + 10:
        raise RuntimeError(f"FAIL_CLOSED: insufficient common bars {len(common_idx)}")
    vol_wide = vol_wide.loc[common_idx]
    close_wide = spot_df.loc[common_idx]
    assets = [a for a in ASSETS if a in vol_wide.columns and a in close_wide.columns]
    if not assets:
        raise RuntimeError("FAIL_CLOSED: no overlapping assets")

    per_asset = {}
    for a in assets:
        c = close_wide[a].astype(float)
        v = vol_wide[a].astype(float)
        df = pd.DataFrame({"c": c, "v": v}).dropna()
        if len(df) < WF_TRAIN + WF_TEST + 10:
            per_asset[a] = {"skipped": "insufficient_bars", "bars": int(len(df))}
            continue
        per_asset[a] = {"bars": int(len(df))}
        for fee, slip in COST_GRID:
            res = run_backtest(df["c"], df["v"], fee, slip)
            per_asset[a][f"fee{fee}_slip{slip}"] = res

    # Aggregate edge rule
    agg = {}
    any_exp_all = False
    all_pos_all = True
    for fee, slip in COST_GRID:
        key = f"fee{fee}_slip{slip}"
        vals = []
        bh_beats = []
        for a, d in per_asset.items():
            r = d.get(key)
            if not r:
                continue
            vals.append(r["oos_net_sum"])
            bh_beats.append(1.0 if r["oos_net_sum"] > r["oos_bh_sum"] else 0.0)
            if r.get("any_exposure"):
                any_exp_all = True
        m = float(np.mean(vals)) if vals else float("nan")
        mb = float(np.mean(bh_beats)) if bh_beats else float("nan")
        if not vals or m <= 0:
            all_pos_all = False
        agg[key] = {"mean_oos_net_across_assets": m, "mean_frac_beats_bh": mb, "n_assets": len(vals)}
    beats_bh_rule = all(agg[k]["mean_oos_net_across_assets"] > 0 and agg[k]["mean_frac_beats_bh"] >= 0.5 for k in agg)
    oos_edge_proven = bool(any_exp_all and all_pos_all and beats_bh_rule)

    out = {
        "artifact": f"real_quote_volume_bowley_quartile_skewness_shock_mr_costed_oos_{UTC}.json",
        "campaign": 72,
        "generated_at_utc": UTC,
        "hypothesis": {
            "name": "Rolling Volume Bowley (Quartile/Galton) Skewness Shock Mean Reversion",
            "transform": "B_t = (P75+P25-2*P50)/(P75-P25), W=48, rank/quartile asymmetry (bounded [-1,1])",
            "signal": f"zscore(B,ZLB={ZLB}); fade d_z>={ENTRY_Z} SHORT, d_z<=-{ENTRY_Z} LONG; exit |d_z|<{EXIT_Z} or hold>={MAX_HOLD}",
            "execution": "t -> t+1 (causal)",
            "wf": {"train": WF_TRAIN, "test": WF_TEST, "step": WF_STEP},
            "cost_grid_bps": COST_GRID,
            "distinctness": [
                "C40 Fisher skewness: 3rd standardized moment, mean-centered, unbounded, uses all observations (L2/L3 weighting). Bowley is rank/quartile-based (P25,P50,P75 only), bounded [-1,1], no moments/mean; robust to tails — different statistic family.",
                "C62 IQR=P75-P25, C70 LQD=P50-P25, C71 UQD=P75-P50, C66 IDR=P90-P10: those are dispersion MAGNITUDES (spread size). Bowley normalizes quartile imbalance into an ASYMMETRY coefficient (direction), not magnitude — fundamentally different transform on quartile inputs.",
                "C68/C69 upper semi-variance/MAD: above-MEAN L2^2/L1 magnitude; C67 lower semi-variance opposite; C61/C65 MAD/MeanAD full-distribution centered L1 magnitude.",
                "Not level/ROC/ratio/cumulative/partition/imbalance/moments/entropies/Hurst-SampEn/autocorr/corr/beta/dispersion-magnitude transforms tested in C23/C40-C71.",
            ],
            "edge_rule_pre_stated": "oos_edge_proven=true iff exposure>0 AND all cost-grid slices OOS net>0 AND beats B&H on same WF windows",
        },
        "data": {
            "real_data_only": True,
            "fabricated": False,
            "feed": "real_quote_volume",
            "volume_meta_file": str(VOL_META),
            "volume_meta_sha256": sha256_file(VOL_META),
            "volume_pkl_file": str(CACHE / "volume_1h_full.pkl"),
            "volume_pkl_sha256": sha256_file(CACHE / "volume_1h_full.pkl"),
            "provenance_file": str(VOL_PROV),
            "provenance_sha256": sha256_file(VOL_PROV),
            "spot_cache": SPOT_CACHE,
            "spot_sha256": spot_sha,
            "spot_meta": str(spot_meta),
            "volume_validation": vol_report,
            "assets": assets,
            "common_bars": int(len(common_idx)),
            "date_start": str(common_idx[0]),
            "date_end": str(common_idx[-1]),
        },
        "aggregate": agg,
        "any_exposure": any_exp_all,
        "all_costs_positive": all_pos_all,
        "beats_bh_rule": beats_bh_rule,
        "oos_edge_proven": oos_edge_proven,
        "per_asset": per_asset,
    }

    out_path = REPORTS / f"real_quote_volume_bowley_quartile_skewness_shock_mr_costed_oos_{UTC}.json"
    out_path.write_text(json.dumps(out, indent=2, sort_keys=True, default=str) + "\n")
    print(out_path)
    print(json.dumps({"oos_edge_proven": oos_edge_proven, "any_exposure": any_exp_all, "all_costs_positive": all_pos_all, "beats_bh_rule": beats_bh_rule, "n_assets": len(per_asset), "common_bars": len(common_idx)}, indent=2))


if __name__ == "__main__":
    main()
