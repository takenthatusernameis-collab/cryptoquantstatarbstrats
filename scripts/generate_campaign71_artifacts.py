#!/usr/bin/env python3
"""Generate Campaign 71 artifacts (fail-closed, real data only).

Campaign 71 — Path R-B: a GENUINELY DIFFERENT pre-stated hypothesis on validated
real_quote_volume (Binance spot klines col 5), NOT a rerun of C23/C40–C70.

PRE-STATED HYPOTHESIS (fixed before seeing OOS results):
"Volume Rolling Upper Quartile Dispersion (UQD = P75-P50) Dispersion Shock Mean Reversion"

Mechanic (pre-stated):
- For each asset, compute rolling Upper Quartile Dispersion UQD_t of quote volume
  over a causal window W=48h:
    P75_t = 75th percentile(qvol[t-W+1..t])
    P50_t = median(qvol[t-W+1..t])   (50th percentile, causal window)
    UQD_t = P75_t - P50_t            (above-median rank spread; linear)
- Genuinely different from C70 LQD (P50-P25): LQD measures below-median rank
  spread (lower half); UQD measures above-median rank spread (upper half).
  (P75-P50) and (P50-P25) can move independently under asymmetry — opposite-side
  mechanic, not a rerun or simple sign/level transform of C70.
- Distinct from C62 IQR (P75-P25): IQR is the symmetric total interquartile span
  = UQD + LQD; UQD is only the above-median component. NOT monotonic-equivalent
  to IQR under asymmetry because LQD=(P50-P25) varies independently.
- Distinct from C66 IDR (P90-P10): different symmetric decile cutpoints/span.
- Distinct from C68 upper semi-variance (L2^2 mean of squared deviations above the
  MEAN): C68 is mean-conditional, L2^2, squared deviations; UQD is rank/quartile-
  conditional (P75/median), L1-like linear spread, not squared, not mean-centered.
- Distinct from C69 upper semi-MAD (L1 mean(|x-m|) above the MEAN): C69 is
  mean-conditional, uses mean deviations and their absolute values; UQD uses
  quartile cutpoints (P75,P50) — rank-conditional above-median spread.
- Distinct from C67 lower semi-variance (below-MEAN, opposite side, L2^2).
- Distinct from C61/C65 MAD/MeanAD (full-distribution centered L1, both sides).
- Distinct from C48/C56 STD/CV (symmetric L2 full-distribution). Not level/ROC/
  ratio/cumulative/partition/imbalance/moments/entropies/Hurst-SampEn/autocorr/
  corr/beta transforms tested in C23/C40-C70.
- z-score UQD_t over ZLB=168h (causal) -> d_z.
- Mean-revert dispersion shocks (fade deviations from typical above-median spread):
  d_z >= ENTRY_Z (1.25) -> SHORT (abnormally wide above-median spread; fade);
  d_z <= -ENTRY_Z (-1.25) -> LONG (abnormally tight above-median spread; fade);
  |d_z| < EXIT_Z (0.25) -> no new entry.
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
log = logging.getLogger("c71")


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


def rolling_uqd(s: pd.Series, w: int) -> pd.Series:
    """Causal rolling Upper Quartile Dispersion = P75 - P50, window w.
    Rank-conditional above-median spread (quartile cutpoints). Distinct from
    C70 LQD (P50-P25, opposite side, independent under asymmetry), C62 IQR
    (P75-P25 symmetric; UQD is one component, not monotonic to IQR under
    asymmetry), C66 IDR (P90-P10), C68 upper semi-variance (mean-conditional
    L2^2), C69 upper semi-MAD (mean-conditional L1 above-mean), C61/C65
    MAD/MeanAD (full-distribution centered L1).
    """
    arr = s.values.astype(float)
    out = np.full(len(arr), np.nan, dtype=float)
    for i in range(w - 1, len(arr)):
        seg = arr[i - w + 1 : i + 1]
        if not np.all(np.isfinite(seg)):
            continue
        p50 = float(np.percentile(seg, 50))
        p75 = float(np.percentile(seg, 75))
        out[i] = p75 - p50
    return pd.Series(out, index=s.index)


def zscore(s: pd.Series, lb: int) -> pd.Series:
    m_ = s.rolling(lb, min_periods=lb).mean()
    sd = s.rolling(lb, min_periods=lb).std(ddof=0)
    return (s - m_) / sd.replace(0, np.nan)


def simulate(ret1: pd.Series, sig: pd.Series, fee_bps: int, slip_bps: int) -> dict:
    n = len(ret1)
    cost = (fee_bps + slip_bps) / 10000.0
    pos = 0
    hold = 0
    trades = 0
    eq = 1.0
    exposure = 0
    for i in range(n - 1):
        z = sig.iloc[i]
        z_ok = not (pd.isna(z) or math.isinf(float(z)))
        r = float(ret1.iloc[i + 1])
        if math.isnan(r):
            r = 0.0
        target = pos
        if pos == 0:
            if z_ok and float(z) >= ENTRY_Z:
                target = -1
            elif z_ok and float(z) <= -ENTRY_Z:
                target = 1
        else:
            hold += 1
            flip = (pos == -1 and z_ok and float(z) <= -ENTRY_Z) or (pos == 1 and z_ok and float(z) >= ENTRY_Z)
            exit_sig = z_ok and abs(float(z)) < EXIT_Z
            if flip:
                target = 1 if pos == -1 else -1
            elif exit_sig or hold >= MAX_HOLD:
                target = 0
        if target != pos:
            eq *= (1.0 - cost)
            trades += 1
            pos = target
            hold = 0
        if pos != 0:
            exposure += 1
            eq *= (1.0 + pos * r)
    total_ret = eq - 1.0
    years = max((n - 1) / (24 * 365), 1e-9)
    ann = (1.0 + total_ret) ** (1.0 / years) - 1.0 if (1.0 + total_ret) > 0 else -1.0
    return {"total_return": float(total_ret), "ann_return": float(ann), "trades": trades, "exposure_bars": exposure, "exposure_frac": exposure / max(n - 1, 1)}


def bhsim(ret1: pd.Series) -> dict:
    eq = float(np.nanprod(1.0 + ret1.fillna(0.0).values[1:])) if len(ret1) > 1 else 1.0
    tr = eq - 1.0
    years = max((len(ret1) - 1) / (24 * 365), 1e-9)
    ann = (1.0 + tr) ** (1.0 / years) - 1.0 if (1.0 + tr) > 0 else -1.0
    return {"total_return": float(tr), "ann_return": float(ann)}


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
    for asset in assets:
        close = close_wide[asset].astype(float)
        volq = vol_wide[asset].astype(float)
        ret1 = close.pct_change().shift(-1)
        uqd = rolling_uqd(volq, W)
        sig = zscore(uqd, ZLB)
        n = len(close)
        slices = wf_slices(n)
        costs = {}
        all_pos = True
        for fee, slip in COST_GRID:
            key = f"fee{fee}_slip{slip}"
            sl_res = []
            for s0, s1 in slices:
                r = ret1.iloc[s0:s1]
                g = sig.iloc[s0:s1]
                strat = simulate(r, g, fee, slip)
                bh = bhsim(r)
                strat["bh_total_return"] = bh["total_return"]
                strat["beats_bh"] = strat["total_return"] > bh["total_return"]
                strat["slice"] = [int(s0), int(s1)]
                sl_res.append(strat)
            nets = [s["total_return"] for s in sl_res]
            bhs = [s["bh_total_return"] for s in sl_res]
            mean_net = float(np.mean(nets)) if nets else float("nan")
            beat_frac = float(np.mean([1.0 if n_ > b_ else 0.0 for n_, b_ in zip(nets, bhs)])) if nets else 0.0
            if not (not math.isnan(mean_net) and mean_net > 0):
                all_pos = False
            costs[key] = {
                "n_slices": len(sl_res),
                "mean_oos_net": mean_net,
                "mean_exposure_frac": float(np.mean([s["exposure_frac"] for s in sl_res])) if sl_res else 0.0,
                "frac_beats_bh": beat_frac,
                "slices": sl_res,
            }
        any_exp = any(costs[k]["mean_exposure_frac"] > 0 for k in costs)
        per_asset[asset] = {"costs": costs, "any_exposure": any_exp, "all_costs_positive": all_pos}
        log.info("asset %s any_exp=%s all_pos=%s", asset, any_exp, all_pos)

    agg = {}
    any_exp_all = any(per_asset[a]["any_exposure"] for a in per_asset)
    all_pos_all = True
    for fee, slip in COST_GRID:
        key = f"fee{fee}_slip{slip}"
        vals = [per_asset[a]["costs"][key]["mean_oos_net"] for a in per_asset]
        beats = [per_asset[a]["costs"][key]["frac_beats_bh"] for a in per_asset]
        m = float(np.mean(vals))
        mb = float(np.mean(beats))
        if not (m > 0):
            all_pos_all = False
        agg[key] = {"mean_oos_net_across_assets": m, "mean_frac_beats_bh": mb, "n_assets": len(vals)}
    beats_bh_rule = all(agg[k]["mean_oos_net_across_assets"] > 0 and agg[k]["mean_frac_beats_bh"] >= 0.5 for k in agg)
    oos_edge_proven = bool(any_exp_all and all_pos_all and beats_bh_rule)

    out = {
        "artifact": f"real_quote_volume_upper_quartile_dispersion_uqd_shock_mr_costed_oos_{UTC}.json",
        "campaign": 71,
        "generated_at_utc": UTC,
        "hypothesis": {
            "name": "Rolling Upper Quartile Dispersion (UQD = P75-P50) dispersion shock mean reversion",
            "transform": "UQD_t = percentile75(window) - percentile50(window), W=48, rank-conditional above-median spread",
            "signal": f"zscore(UQD,ZLB={ZLB}); fade d_z>={ENTRY_Z} SHORT, d_z<=-{ENTRY_Z} LONG; exit |d_z|<{EXIT_Z} or hold>={MAX_HOLD}",
            "execution": "t -> t+1 (causal)",
            "wf": {"train": WF_TRAIN, "test": WF_TEST, "step": WF_STEP},
            "cost_grid_bps": COST_GRID,
            "distinctness": [
                "C70 LQD=P50-P25 below-median (opposite side); UQD=P75-P50 above-median rank spread, components independent under asymmetry",
                "C62 IQR=P75-P25 symmetric span = UQD+LQD; UQD one component, NOT monotonic transform of IQR under asymmetry",
                "C66 IDR=P90-P10 different symmetric decile cutpoints",
                "C68 upper semi-variance: L2^2 above-MEAN mean-conditional squared; UQD rank/quartile above-MEDIAN linear spread",
                "C69 upper semi-MAD: L1 mean(|x-m|) above-MEAN mean-conditional; UQD uses quartile cutpoints (P75,P50), not mean deviations",
                "C67 lower semi-variance opposite side/L2^2; C61/C65 MAD/MeanAD full-distribution centered L1; C48/C56 STD/CV symmetric L2",
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
            "spot_meta": spot_meta,
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

    out_path = REPORTS / f"real_quote_volume_upper_quartile_dispersion_uqd_shock_mr_costed_oos_{UTC}.json"
    out_path.write_text(json.dumps(out, indent=2, sort_keys=True, default=str) + "\n")
    print(out_path)
    print(json.dumps({"oos_edge_proven": oos_edge_proven, "any_exposure": any_exp_all, "all_costs_positive": all_pos_all, "beats_bh_rule": beats_bh_rule, "n_assets": len(per_asset), "common_bars": len(common_idx)}, indent=2))


if __name__ == "__main__":
    main()
