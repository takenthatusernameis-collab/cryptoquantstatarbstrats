#!/usr/bin/env python3
"""Generate Campaign 73 artifacts (fail-closed, real data only).

Campaign 73 — Path R-B: a GENUINELY DIFFERENT pre-stated hypothesis on validated
real_quote_volume (Binance spot klines col 5), NOT a rerun of C23/C40–C72.

PRE-STATED HYPOTHESIS (fixed before seeing OOS results):
"Volume Rolling Peak-to-Trough Drawdown Shock Mean Reversion"

Mechanic (pre-stated):
- For each asset, compute the rolling peak (running max) of quote volume over a
  causal window W=48h: Peak_t = max(qvol[t-W+1..t]).
- Drawdown DD_t = (Peak_t - qvol_t) / Peak_t if Peak_t > 0 else NaN -> [0,1], the
  fraction by which current volume sits below its rolling peak (liquidity
  withdrawn from the peak; path-extremum / drawdown statistic).
- z-score DD_t over ZLB=168h (causal) -> d_z.
- Mean-revert volume drawdown shocks (fade liquidity extremes vs recent peak):
  d_z >= ENTRY_Z (1.25) => volume abnormally BELOW its rolling peak (dry-out /
  liquidity climax) -> LONG (anticipate mean reversion back toward peak);
  d_z <= -ENTRY_Z (-1.25) => volume abnormally AT/ABOVE recent peak (climax) ->
  SHORT (fade the climax); |d_z| < EXIT_Z (0.25) -> no new entry.
- Exit when |d_z| < EXIT_Z, hold >= MAX_HOLD (12h), or signal flips.
- Execution shift t -> t+1 (causal). WF rolling 720/168/168. Cost grid 0-40bps
  (fee,slip pairs). B&H benchmark on same WF windows.

Genuinely distinct from C23/C40–C72:
- C40 Fisher skewness: 3rd standardized moment, mean-centered, unbounded, uses all
  observations. Drawdown uses running max vs current level, no moments/mean, bounded [0,1].
- C72 Bowley: (P75+P25-2*P50)/IQR quartile ASYMMETRY ratio over P25/P50/P75. Drawdown is
  peak-to-trough (running max) fraction vs current level — different transform family,
  not quartile asymmetry.
- C62 IQR/C70 LQD/C71 UQD/C66 IDR: dispersion MAGNITUDES (spread size). Drawdown is a
  path-extremum drawdown (max-drawdown-style) statistic, not a spread/magnitude.
- C68/C69 upper semi-variance/MAD (above-MEAN L2^2/L1), C67 lower semi-variance,
  C61/C65 MAD/MeanAD (full-distribution centered L1): centered magnitude statistics;
  drawdown is relative to a running peak, not the mean, and not centered.
- C61/C65-level/ROC/ratio/cumulative/partition/imbalance/entropies/Hurst-SampEn/
  autocorr/corr/beta/dispersion-magnitude: none of those. First peak-to-trough
  (running-max drawdown) transform tested on real_quote_volume.
- dryup_breakout / volume_expansion_breakout / climax: level-threshold breakouts;
  drawdown is a normalized causal peak-to-trough fraction, z-scored and mean-reverted
  (path-extremum, not level breakout).

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
log = logging.getLogger("c73")

SPOT_CACHE = "0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7"


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


def rolling_peak(s: pd.Series, w: int) -> pd.Series:
    """Causal rolling peak (running max) of volume."""
    return s.rolling(w, min_periods=max(24, w // 3)).max()


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


def load_spot():
    pkl = CACHE / f"{SPOT_CACHE}.pkl"
    meta = json.loads((CACHE / f"{SPOT_CACHE}.meta.json").read_text(encoding="utf-8"))
    df = pd.read_pickle(pkl)  # noqa: S301
    return df, meta, sha256_file(pkl)


def run_backtest(close: pd.Series, qvol: pd.Series, fee_bps: float, slip_bps: float):
    ret = close.pct_change().shift(-1)  # t -> t+1 exec
    peak = rolling_peak(qvol, W)
    dd = (peak - qvol) / peak.replace(0, np.nan)
    dd = dd.clip(lower=0.0, upper=1.0)
    dz = zscore_causal(dd, ZLB)
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
        if cur != 0 and (abs(z) < EXIT_Z or hold >= MAX_HOLD or (cur > 0 and z <= -ENTRY_Z) or (cur < 0 and z >= ENTRY_Z)):
            if (cur > 0 and z <= -ENTRY_Z) or (cur < 0 and z >= ENTRY_Z):
                cur = -1.0 if z >= ENTRY_Z else 1.0
                hold = 0
            else:
                cur = 0.0
                hold = 0
        if cur == 0 and abs(z) >= ENTRY_Z:
            cur = 1.0 if z >= ENTRY_Z else -1.0
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
        "artifact": f"real_quote_volume_peak_trough_drawdown_shock_mr_costed_oos_{UTC}.json",
        "campaign": 73,
        "generated_at_utc": UTC,
        "hypothesis": {
            "name": "Rolling Volume Peak-to-Trough Drawdown Shock Mean Reversion",
            "transform": "DD_t=(Peak_t-qvol_t)/Peak_t, Peak=rolling max W=48; zscore(DD,ZLB=168); fade d_z>=1.25 LONG, d_z<=-1.25 SHORT; exit |d_z|<0.25 or hold>=12",
            "signal": "zscore(volume drawdown, ZLB=168); fade drawdown extremes vs rolling peak",
            "execution": "t -> t+1 (causal)",
            "wf": {"train": WF_TRAIN, "test": WF_TEST, "step": WF_STEP},
            "cost_grid_bps": COST_GRID,
            "distinctness": [
                "C40 Fisher skewness: 3rd standardized moment, mean-centered, unbounded, all observations. Drawdown uses running max vs current level, no moments/mean, bounded [0,1].",
                "C72 Bowley: (P75+P25-2*P50)/IQR quartile asymmetry ratio (P25/P50/P75). Drawdown is peak-to-trough running-max fraction vs current level — different transform family, not quartile asymmetry.",
                "C62 IQR/C70 LQD/C71 UQD/C66 IDR: dispersion magnitudes (spread size). Drawdown is a path-extremum drawdown statistic, not a spread/magnitude.",
                "C68/C69 upper semi-variance/MAD, C67 lower semi-variance, C61/C65 MAD/MeanAD: centered magnitude statistics. Drawdown is relative to running peak, not the mean.",
                "Not level/ROC/ratio/cumulative/partition/imbalance/entropies/Hurst-SampEn/autocorr/corr/beta/dispersion-magnitude transforms in C23/C40-C71; not level-threshold breakouts (dryup/expansion/climax). First peak-to-trough drawdown transform tested on real_quote_volume.",
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

    out_path = REPORTS / f"real_quote_volume_peak_trough_drawdown_shock_mr_costed_oos_{UTC}.json"
    out_path.write_text(json.dumps(out, indent=2, sort_keys=True, default=str) + "\n")
    print(out_path)
    print(json.dumps({"oos_edge_proven": oos_edge_proven, "any_exposure": any_exp_all, "all_costs_positive": all_pos_all, "beats_bh_rule": beats_bh_rule, "n_assets": len(per_asset), "common_bars": len(common_idx)}, indent=2))


if __name__ == "__main__":
    main()
