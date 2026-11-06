#!/usr/bin/env python3
"""Generate Campaign 64 artifacts (fail-closed, real data only).

Campaign 64 — Path R-B: a GENUINELY DIFFERENT pre-stated hypothesis on validated
real_quote_volume (Binance spot klines col 5), NOT a rerun of C23/C40–C63.

PRE-STATED HYPOTHESIS (fixed before seeing OOS results):
"Volume Rolling Range (Max-Min) Dispersion Shock Mean Reversion"

Mechanic (pre-stated):
- For each asset, compute rolling Range R_t of quote volume over a causal window
  W=48h:
    R_t = max(qvol[t-W+1..t]) - min(qvol[t-W+1..t])
  Range is a full-extremes dispersion statistic: it uses the window maximum and
  minimum only (the two order statistics at the extremes). It is genuinely
  different from C48 STD (L2 squared deviations from mean), C56 CV (relative
  std/mean), C61 MAD (median-centered absolute deviation), C62 IQR (Q3-Q1, middle
  50%, ignores tails), and C63 GMD (mean pairwise absolute difference, all
  pairwise distances). Range is neither pairwise, nor median-centered, nor
  mean-based, nor quartile-based, nor a standardized higher moment.
- z-score R_t over ZLB=168h (causal) -> r_z.
- Mean-revert robust dispersion shocks (fade deviations from typical range
  dispersion of qvol):
  r_z >= ENTRY_Z (1.25) -> SHORT (abnormally wide range dispersion; fade);
  r_z <= -ENTRY_Z (-1.25) -> LONG (abnormally narrow range dispersion; fade);
  |r_z| < EXIT_Z (0.25) -> no new entry.
- Exit when |r_z| < EXIT_Z, hold >= MAX_HOLD (12h), or signal flips.
- Execution shift t -> t+1 (causal). WF rolling 720/168/168. Cost grid 0-40bps
  (fee,slip pairs). B&H benchmark on same WF windows.

Edge rule (pre-stated, fail-closed): oos_edge_proven=true IFF exposure>0 AND ALL
cost-grid slices OOS net>0 AND OOS net beats B&H on same WF windows. Else false.
No in-sample tuning, no threshold weakening, no fabricated data/proxies.

DIFFERS FROM C23/C40–C63 (genuinely different transform/mechanic):
- C63 = rolling Gini Mean Difference (mean pairwise |x_i-x_j|, L1 dispersion
  using ALL in-window observations, two-sample U-statistic). C64 = rolling Range
  (max-min), the full-extremes order-statistic dispersion using ONLY the two
  extremes — different estimator, different quantity, different robustness profile.
- C62 = rolling IQR (Q3-Q1), rank/order-statistic dispersion of the middle 50%
  using two quartile cutpoints; ignores tails beyond Q1/Q3. C64 uses the tails
  (max/min) directly, not quartiles.
- C61 = rolling MAD median(|x-median(x)|), L1 robust scale centered at the median
  using absolute deviations of ALL observations. C64 is max-min, not median-centered.
- C48 = rolling STD (L2, mean-based 2nd-moment, outlier-sensitive). C64 is not
  squared or mean-based.
- C56 = CV = std/mean (relative L2 ratio). C64 is absolute full-extremes dispersion,
  not mean-normalized and not L2-based.
- C49/C50 = kurtosis/skewness (standardized higher moments); C57/C58/C60 = entropies;
  C59 = Hurst fractal scaling; C51 = lag-1 autocorr; C52/C53/C55 = cross-corrs;
  C54 = OLS beta; C45 = Amihud; C46 = OBV; C47 = imbalance; C43/44 = divergence/ROC;
  C23/40/41/42 = vol_z level/expansion. None is a rolling max-min range dispersion.
C64 uses rolling Range (max-min of qvol) — orthogonal to IQR (C62), MAD (C61),
GMD (C63), STD/CV (C48/C56), higher moments (C49/C50), entropies (C57/C58/C60),
Hurst scaling (C59), autocorrs/correlations/betas (C51-C55), and all levels/ROC/
cumulative/partition/imbalance transforms in C23/C40-C63.
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

logging.basicConfig(level=logging.INFO, format="%(asctime)s [campaign64] %(levelname)s %(message)s")
logger = logging.getLogger("campaign64")

CACHE_DIR = ROOT / "data" / "cache"
REPORTS = ROOT / "reports"
SPOT_CACHE = "0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7"
VOL_META = CACHE_DIR / "volume_1h_full.meta.json"
VOL_PROV = CACHE_DIR / "volume_1h_full.provenance.json"

W_RANGE = 48
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
    df = pd.read_pickle(pkl)  # noqa: S301 - cached artifact verified by provenance context
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


def rolling_range(s: pd.Series, w: int) -> pd.Series:
    """Causal rolling Range = max - min over window w (full-extremes dispersion)."""
    arr = s.values.astype(float)
    out = np.full(len(arr), np.nan, dtype=float)
    n = len(arr)
    if n < w:
        return pd.Series(out, index=s.index)
    rmax = pd.Series(arr, index=s.index).rolling(w, min_periods=w).max().values
    rmin = pd.Series(arr, index=s.index).rolling(w, min_periods=w).min().values
    for i in range(w - 1, n):
        if not np.all(np.isfinite(arr[i - w + 1 : i + 1])):
            continue
        out[i] = float(rmax[i] - rmin[i])
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
            hold = 0
        pos = target
        if pos != 0:
            exposure += 1
            eq *= (1.0 + pos * r)
    return {"total_return": eq - 1.0, "trades": trades, "exposure_frac": exposure / max(1, n - 1)}


def wf_oos(ret1: pd.Series, sig: pd.Series, fee_bps: int, slip_bps: int):
    n = len(ret1)
    out = []
    start = 0
    while True:
        te = start + WF_TRAIN
        tst_e = te + WF_TEST
        if tst_e > n:
            break
        out.append(
            simulate(
                ret1.iloc[te:tst_e].reset_index(drop=True),
                sig.iloc[te:tst_e].reset_index(drop=True),
                fee_bps,
                slip_bps,
            )
        )
        start += WF_STEP
    return out


def agg(slices):
    if not slices:
        return {"n": 0, "oos_net_sum": 0.0, "exposure": 0.0}
    rets = [s["total_return"] for s in slices]
    return {
        "n": len(slices),
        "oos_net_sum": float(np.prod([1 + r for r in rets]) - 1.0),
        "exposure": float(np.mean([s["exposure_frac"] for s in slices])),
    }


def main() -> None:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    spot_df, spot_meta, spot_sha = load_spot()
    vol_wide, vol_report = load_volume_wide()
    vol_symbols = sorted(vol_wide.columns.tolist())
    spot_symbols = list(spot_df.columns)
    assets = sorted([a for a in spot_symbols if a in vol_symbols])
    logger.info("spot_symbols=%s vol_symbols=%s tested_assets=%s", spot_symbols, vol_symbols, assets)

    by_asset = {}
    n_exposed = n_edge = 0
    for a in assets:
        close = pd.to_numeric(spot_df[a], errors="coerce")
        ret1 = close.pct_change()
        qv = pd.to_numeric(vol_wide[a], errors="coerce")
        common = close.index.intersection(qv.index)
        close, ret1, qv = close.reindex(common), ret1.reindex(common), qv.reindex(common)
        disp = rolling_range(qv, W_RANGE)
        r_z = zscore(disp, ZLB)
        logger.info("asset=%s rows=%s", a, len(common))

        cost_slices = {}
        for fee, slip in COST_GRID:
            key = f"fee{fee}_slip{slip}_bps"
            sl = wf_oos(ret1, r_z, fee, slip)
            ag = agg(sl)
            bh_sl = []
            n = len(ret1)
            st = 0
            while True:
                te = st + WF_TRAIN
                tst_e = te + WF_TEST
                if tst_e > n:
                    break
                rsl = ret1.iloc[te:tst_e].fillna(0.0)
                bh_sl.append({"total_return": float((1 + rsl).prod() - 1.0), "exposure_frac": 1.0})
                st += WF_STEP
            bh_net = agg(bh_sl)["oos_net_sum"] if bh_sl else 0.0
            cost_slices[key] = {
                "net_oos_sum": ag["oos_net_sum"],
                "bh_oos_sum": bh_net,
                "oos_net_gt_zero": ag["oos_net_sum"] > 0,
                "oos_net_beat_bh": ag["oos_net_sum"] > bh_net,
                "n_slices": ag["n"],
                "exposure": ag["exposure"],
            }
        exposure = cost_slices["fee0_slip0_bps"]["exposure"] > 0
        all_pos = all(v["oos_net_gt_zero"] for v in cost_slices.values())
        all_bh = all(v["oos_net_beat_bh"] for v in cost_slices.values())
        edge = exposure and all_pos and all_bh
        if exposure:
            n_exposed += 1
        if edge:
            n_edge += 1
        by_asset[a] = {
            "rows": len(common),
            "has_exposure": exposure,
            "oos_edge_proven": edge,
            "cost_slices": cost_slices,
        }

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "campaign": 64,
        "title": "Volume Rolling Range (Max-Min) Dispersion Shock Mean Reversion — costed OOS (fail-closed, real quote volume)",
        "family": "volume_range_max_min_dispersion_shock_mr",
        "path": "R-B (validated real_quote_volume; no new blocked-family feed)",
        "oos_edge_proven": n_edge > 0,
        "n_assets_tested": len(by_asset),
        "n_assets_with_exposure": n_exposed,
        "n_oos_edge_proven": n_edge,
        "pre_stated_hypothesis": (
            "R_t = rolling Range of qvol[t-W+1..t], W=48: R_t = max(qvol) - min(qvol) "
            "(full-extremes order-statistic dispersion using ONLY the window max/min). "
            "r_z=zscore(R_t,ZLB=168). Mean-revert dispersion shocks: "
            "r_z>=1.25 SHORT (abnormally wide range dispersion; fade), "
            "r_z<=-1.25 LONG (abnormally narrow range dispersion; fade), "
            "exit |r_z|<0.25 or hold>=12 or flip. Exec t->t+1. WF 720/168/168. "
            "Cost grid 0-40bps. Edge iff exposure>0 AND all slices OOS net>0 AND >B&H. "
            "Genuinely different from C23/C40-C63."
        ),
        "hypothesis_differs_from_c23_c40_c63": (
            "C64=rolling Range (max-min of qvol, full-extremes dispersion using ONLY "
            "the two extremes). C63=rolling Gini Mean Difference (mean pairwise |x_i-x_j|, "
            "L1 dispersion using ALL in-window observations). C62=rolling IQR (Q3-Q1, "
            "middle 50%, ignores tails beyond Q1/Q3). C61=rolling MAD median(|x-median|), "
            "median-centered L1 deviation of ALL observations. C48=rolling STD (L2, "
            "mean-based 2nd-moment). C56=CV=std/mean (relative L2 ratio). C49/C50="
            "kurtosis/skewness (standardized higher moments). C57/C58/C60=Shannon/"
            "Bandt-Pompe/Sample entropies. C59=Hurst R/S fractal scaling. C51=lag-1 "
            "autocorr. C52/C53/C55=cross-corrs; C54=OLS beta. C45=Amihud. C46=OBV. "
            "C47=imbalance. C43/44=divergence/ROC. C23/40/41/42=vol_z level/expansion. "
            "None is a rolling max-min range dispersion; C64 orthogonal to C23/C40-C63."
        ),
        "config": {
            "spot_cache": SPOT_CACHE,
            "spot_meta": spot_meta,
            "spot_sha256": spot_sha,
            "volume_meta": str(VOL_META.relative_to(ROOT)),
            "volume_provenance": str(VOL_PROV.relative_to(ROOT)),
            "volume_validation": vol_report,
            "w_range": W_RANGE,
            "zlb": ZLB,
            "entry_z": ENTRY_Z,
            "exit_z": EXIT_Z,
            "max_hold": MAX_HOLD,
            "wf": [WF_TRAIN, WF_TEST, WF_STEP],
            "cost_grid_bps_fee_slippage": COST_GRID,
        },
        "by_asset": by_asset,
    }
    out = REPORTS / f"real_quote_volume_range_max_min_dispersion_shock_mr_costed_oos_{ts}.json"
    out.write_text(json.dumps(report, indent=2, default=str) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "wrote": str(out),
                "oos_edge_proven": report["oos_edge_proven"],
                "n_edge": n_edge,
                "n_exposed": n_exposed,
                "n_assets": len(by_asset),
            }
        )
    )


if __name__ == "__main__":
    main()
