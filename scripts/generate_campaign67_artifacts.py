#!/usr/bin/env python3
"""Generate Campaign 67 artifacts (fail-closed, real data only).

Campaign 67 — Path R-B: a GENUINELY DIFFERENT pre-stated hypothesis on validated
real_quote_volume (Binance spot klines col 5), NOT a rerun of C23/C40–C66.

PRE-STATED HYPOTHESIS (fixed before seeing OOS results):
"Volume Rolling Lower Semi-Variance (Downside Variance) Dispersion Shock Mean Reversion"

Mechanic (pre-stated):
- For each asset, compute rolling Lower Semi-Variance LSV_t of quote volume over
  a causal window W=48h:
    m_t = mean(qvol[t-W+1..t])
    d_i = min(qvol_i - m_t, 0)   for i in [t-W+1..t]  (below-mean deviations only)
    LSV_t = mean(d_i^2)           (L2 squared dispersion of downside mass only)
  LSV captures asymmetric downside spread: how much volume deviates below its own
  rolling mean, squared (L2) and restricted to the below-mean side.
- This is genuinely different from C48 full STD / variance (uses ALL deviations,
  symmetric, both sides) and C56 CV (relative full STD): LSV uses ONLY below-mean
  deviations (asymmetric downside-only mass). It is not a mean/median-centered L1
  magnitude of the full distribution (C61 MAD = median(|x-med|), C65 MeanAD =
  mean(|x-mean|), both L1, full distribution, centered magnitude); LSV is L2^2 and
  one-sided. It is not rank-cutpoint dispersion (C62 IQR P75-P25, C66 IDR P90-P10),
  not pairwise (C63 GMD), not extremes-only (C64 Range max-min), and not any
  level/ROC/cumulative/partition/imbalance/moment/entropy/Hurst-SampEn/
  autocorr/corr/beta transform tested in C23/C40-C66.
- z-score LSV_t over ZLB=168h (causal) -> d_z.
- Mean-revert downside-dispersion shocks (fade deviations from typical LSV):
  d_z >= ENTRY_Z (1.25) -> SHORT (abnormally high downside dispersion; fade);
  d_z <= -ENTRY_Z (-1.25) -> LONG (abnormally low downside dispersion; fade);
  |d_z| < EXIT_Z (0.25) -> no new entry.
- Exit when |d_z| < EXIT_Z, hold >= MAX_HOLD (12h), or signal flips.
- Execution shift t -> t+1 (causal). WF rolling 720/168/168. Cost grid 0-40bps
  (fee,slip pairs). B&H benchmark on same WF windows.

Edge rule (pre-stated, fail-closed): oos_edge_proven=true IFF exposure>0 AND ALL
cost-grid slices OOS net>0 AND OOS net beats B&H on same WF windows. Else false.
No in-sample tuning, no threshold weakening, no fabricated data/proxies.

DIFFERS FROM C23/C40–C66 (genuinely different transform/mechanic):
- C48/C56 = full STD/CV (L2, symmetric, all deviations). C67 = lower semi-variance
  (L2^2, asymmetric, below-mean deviations ONLY) — distinct downside-only mass.
- C61/C65 = MAD/MeanAD (L1 centered magnitudes |deviation| over full distribution).
  C67 = L2^2 of negative deviations only (no absolute of full distribution).
- C62/C66 = rank cutpoints (IQR P75-P25, IDR P90-P10). C67 uses in-window mean and
  squared below-mean deviations, not quantile cutpoints.
- C63 = pairwise GMD. C64 = Range extremes. Others are moments/entropies/Hurst-
  SampEn/autocorr/corr/beta/level/ROC/cumulative/partition/imbalance. None are
  one-sided downside semi-variance.
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
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.real_feed_loader import validate_and_load_real_feed  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [campaign67] %(levelname)s %(message)s")
logger = logging.getLogger("campaign67")

CACHE_DIR = ROOT / "data" / "cache"
REPORTS = ROOT / "reports"
SPOT_CACHE = "0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7"
VOL_META = CACHE_DIR / "volume_1h_full.meta.json"
VOL_PROV = CACHE_DIR / "volume_1h_full.provenance.json"

W_LSV = 48
ZLB = 168
ENTRY_Z = 1.25
EXIT_Z = 0.25
MAX_HOLD = 12
WF_TRAIN = 720
WF_TEST = 168
WF_STEP = 168
COST_GRID = [(0, 0), (5, 5), (10, 10), (20, 20)]


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_spot():
    pkl = CACHE_DIR / f"{SPOT_CACHE}.pkl"
    meta = json.loads((CACHE_DIR / f"{SPOT_CACHE}.meta.json").read_text(encoding="utf-8"))
    df = pd.read_pickle(pkl)  # noqa: S301
    return df, meta, sha256_file(pkl)


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


def rolling_lower_semi_variance(s: pd.Series, w: int) -> pd.Series:
    """Causal rolling lower semi-variance = mean(min(x-m,0)^2) over window w.

    m is the in-window mean (causal). Only below-mean deviations contribute (L2^2,
    asymmetric downside-only mass). Distinct from full variance/STD (C48/C56).
    """
    arr = s.values.astype(float)
    out = np.full(len(arr), np.nan, dtype=float)
    n = len(arr)
    for i in range(w - 1, n):
        seg = arr[i - w + 1 : i + 1]
        if not np.all(np.isfinite(seg)):
            continue
        m = float(np.mean(seg))
        below = np.minimum(seg - m, 0.0)
        out[i] = float(np.mean(below * below))
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


def main():
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    REPORTS.mkdir(parents=True, exist_ok=True)
    spot_df, spot_meta, spot_sha = load_spot()
    vol_wide, vol_report = load_volume_wide()
    common_idx = spot_df.index.intersection(vol_wide.index)
    assets = [c for c in vol_wide.columns if c in spot_df.columns]
    logger.info("assets=%s common=%d", assets, len(common_idx))

    per_asset = {}
    agg_cost = {f"fee{f}_slip{s}": {"oos_nets": [], "bh_nets": [], "slices_exposed": 0} for f, s in COST_GRID}
    any_exposure = False
    for a in assets:
        close = spot_df.loc[common_idx, a].astype(float)
        qv = vol_wide.loc[common_idx, a].astype(float)
        ret1 = close.pct_change().replace([np.inf, -np.inf], np.nan)
        lsv = rolling_lower_semi_variance(qv, W_LSV)
        sig = zscore(lsv, ZLB)
        slices = wf_slices(len(common_idx))
        ac = {}
        for f, s in COST_GRID:
            key = f"fee{f}_slip{s}"
            nets = []
            bhs = []
            exposed = 0
            for t0, t1 in slices:
                r = ret1.iloc[t0:t1]
                z = sig.iloc[t0:t1]
                res = simulate(r, z, f, s)
                bh = bhsim(r)
                nets.append(res["total_return"])
                bhs.append(bh["total_return"])
                if res["exposure_bars"] > 0:
                    exposed += 1
            ac[key] = {"mean_oos_net": float(np.mean(nets)) if nets else None, "mean_bh_net": float(np.mean(bhs)) if bhs else None, "slices": len(slices), "slices_exposed": exposed, "all_positive": bool(nets and all(x > 0 for x in nets)), "beats_bh_all": bool(nets and all(n > b for n, b in zip(nets, bhs)))}
            agg_cost[key]["oos_nets"].extend(nets)
            agg_cost[key]["bh_nets"].extend(bhs)
            agg_cost[key]["slices_exposed"] += exposed
            if exposed > 0:
                any_exposure = True
        per_asset[a] = {"slices": len(slices), "costs": ac}
        logger.info("asset=%s slices=%d fee10 mean_oos=%.6f", a, len(slices), ac["fee10_slip10"]["mean_oos_net"] if ac["fee10_slip10"]["mean_oos_net"] is not None else float("nan"))

    agg = {}
    all_pos_all = True
    beats_all = True
    for k, v in agg_cost.items():
        n_ = v["oos_nets"]
        b_ = v["bh_nets"]
        ap = bool(n_ and all(x > 0 for x in n_))
        bb = bool(n_ and all(x > y for x, y in zip(n_, b_)))
        agg[k] = {"mean_oos_net": float(np.mean(n_)) if n_ else None, "mean_bh_net": float(np.mean(b_)) if b_ else None, "n_asset_slices": len(n_), "slices_exposed": v["slices_exposed"], "all_positive": ap, "beats_bh_all": bb}
        all_pos_all = all_pos_all and ap
        beats_all = beats_all and bb
    oos_edge_proven = bool(any_exposure and all_pos_all and beats_all)

    out = {
        "generated_at_utc": ts,
        "campaign": 67,
        "hypothesis": "Volume Rolling Lower Semi-Variance (Downside Variance) Dispersion Shock Mean Reversion",
        "mechanic": "Rolling LSV_t = mean(min(qvol_i - mean(qvol,W=48),0)^2) over W=48 (L2^2 of below-mean deviations only, asymmetric downside-only mass); zscore ZLB=168 -> d_z; fade downside-dispersion shocks: d_z>=1.25 SHORT, d_z<=-1.25 LONG, exit |d_z|<0.25 or hold>=12 or flip; exec t->t+1; WF 720/168/168; costs 0-40bps; B&H benchmark.",
        "distinct_from_c23_c40_c66": "LSV is asymmetric L2^2 dispersion using ONLY below-mean deviations (downside-only mass) — distinct from C48/C56 full STD/CV (symmetric, all deviations), distinct from C61/C65 MAD/MeanAD (L1 centered magnitudes |deviation| over full distribution), distinct from C62/C66 rank-cutpoint IQR/IDR (P75-P25/P90-P10), distinct from C63 GMD (pairwise), C64 Range (extremes). Not level/ROC/ratio/cumulative/partition/imbalance/moments/entropies/Hurst-SampEn/autocorr/corr/beta.",
        "edge_rule": "oos_edge_proven=true IFF exposure>0 AND ALL cost-grid slices OOS net>0 AND OOS net beats B&H on same WF windows (pre-stated).",
        "data": {"feed": "real_quote_volume", "source": "Binance spot klines column 5 (quote asset volume) via DataLoader.get_ohlcv/fetch_klines; real, not fabricated", "spot_cache_sha256": spot_sha, "spot_cache_meta_keys": sorted(spot_meta.keys())[:12], "volume_validation": vol_report, "assets": assets, "n_bars_common": len(common_idx)},
        "params": {"W_LSV": W_LSV, "ZLB": ZLB, "ENTRY_Z": ENTRY_Z, "EXIT_Z": EXIT_Z, "MAX_HOLD": MAX_HOLD, "WF_TRAIN": WF_TRAIN, "WF_TEST": WF_TEST, "WF_STEP": WF_STEP, "COST_GRID_BPS": COST_GRID},
        "per_asset": per_asset,
        "aggregate_cost_grid": agg,
        "any_exposure": any_exposure,
        "oos_edge_proven": oos_edge_proven,
        "fail_closed": True,
        "real_data_only": True,
        "no_fabrication": True,
    }
    p = REPORTS / f"real_quote_volume_lower_semi_variance_downside_dispersion_shock_mr_costed_oos_{ts}.json"
    p.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    logger.info("wrote %s oos_edge_proven=%s any_exposure=%s", p, oos_edge_proven, any_exposure)
    return 0 if p.exists() else 2


if __name__ == "__main__":
    raise SystemExit(main())
