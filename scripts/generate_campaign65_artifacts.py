#!/usr/bin/env python3
"""Generate Campaign 65 artifacts (fail-closed, real data only).

Campaign 65 — Path R-B: a GENUINELY DIFFERENT pre-stated hypothesis on validated
real_quote_volume (Binance spot klines col 5), NOT a rerun of C23/C40–C64.

PRE-STATED HYPOTHESIS (fixed before seeing OOS results):
"Volume Rolling Mean Absolute Deviation around the Arithmetic Mean (MeanAD)
Dispersion Shock Mean Reversion"

Mechanic (pre-stated):
- For each asset, compute rolling MeanAD D_t of quote volume over a causal window
  W=48h:
    mu_t = mean(qvol[t-W+1..t])
    D_t  = mean(|qvol[t-W+1..t] - mu_t|)
  MeanAD is an L1 dispersion statistic centered at the ARITHMETIC MEAN. It averages
  absolute deviations of ALL in-window observations from the mean. It is genuinely
  different from C61 MAD (median-centered: median(|x - median(x)|); different center,
  uses median not mean — different estimator and robustness), C63 GMD (Gini Mean
  Difference: mean pairwise |x_i-x_j| over all pairs, O(n^2) pairwise distances,
  no central reference), C48 STD (L2: sqrt(mean((x-mu)^2)), squared deviations),
  C56 CV (std/mean, relative L2 ratio), C62 IQR (Q3-Q1 rank quartiles, middle 50%,
  ignores tail magnitudes beyond cutpoints), and C64 Range (max-min, full extremes
  using only two order statistics). MeanAD is mean-centered L1 (not median-centered,
  not pairwise, not squared, not rank-quartile, not extremal).
- z-score D_t over ZLB=168h (causal) -> d_z.
- Mean-revert robust dispersion shocks (fade deviations from typical MeanAD
  dispersion of qvol):
  d_z >= ENTRY_Z (1.25) -> SHORT (abnormally high MeanAD dispersion; fade);
  d_z <= -ENTRY_Z (-1.25) -> LONG (abnormally low MeanAD dispersion; fade);
  |d_z| < EXIT_Z (0.25) -> no new entry.
- Exit when |d_z| < EXIT_Z, hold >= MAX_HOLD (12h), or signal flips.
- Execution shift t -> t+1 (causal). WF rolling 720/168/168. Cost grid 0-40bps
  (fee,slip pairs). B&H benchmark on same WF windows.

Edge rule (pre-stated, fail-closed): oos_edge_proven=true IFF exposure>0 AND ALL
cost-grid slices OOS net>0 AND OOS net beats B&H on same WF windows. Else false.
No in-sample tuning, no threshold weakening, no fabricated data/proxies.

DIFFERS FROM C23/C40–C64 (genuinely different transform/mechanic):
- C61 = rolling MAD median(|x-median(x)|), L1 dispersion centered at the MEDIAN.
  C65 = rolling MeanAD mean(|x-mean(x)|), L1 dispersion centered at the ARITHMETIC
  MEAN — different center (mean vs median), different estimator and sensitivity.
- C63 = rolling Gini Mean Difference (mean pairwise |x_i-x_j|, all in-window
  pairwise L1 distances, no central reference). C65 uses deviations from a single
  center (mean), not pairwise distances.
- C64 = rolling Range (max-min), full-extremes using ONLY two order statistics.
  C65 uses all in-window observations via mean absolute deviation.
- C62 = rolling IQR (Q3-Q1), rank quartile dispersion of the middle 50%. C65 uses
  magnitudes of deviations from the mean, not rank cutpoints.
- C48 = rolling STD (L2, mean-based squared deviations). C65 is L1 (absolute, not
  squared) — different norm and outlier sensitivity.
- C56 = CV = std/mean (relative L2 ratio). C65 is absolute L1 dispersion around mean,
  not mean-normalized and not squared.
- C49/C50 = kurtosis/skewness (standardized higher moments); C57/C58/C60 = entropies;
  C59 = Hurst fractal scaling; C51 = lag-1 autocorr; C52/C53/C55 = cross-corrs;
  C54 = OLS beta; C45 = Amihud; C46 = OBV; C47 = imbalance; C43/44 = divergence/ROC;
  C23/40/41/42 = vol_z level/expansion. None is a rolling mean-centered MeanAD.
C65 uses rolling MeanAD mean(|x-mean(x)|) — orthogonal to C61 MAD (median center),
C63 GMD (pairwise), C64 Range (extremes), C62 IQR (quartiles), C48/C56 STD/CV (L2),
higher moments (C49/C50), entropies (C57/C58/C60), Hurst scaling (C59),
autocorrs/correlations/betas (C51-C55), and all levels/ROC/cumulative/partition/
imbalance transforms in C23/C40-C64.
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

logging.basicConfig(level=logging.INFO, format="%(asctime)s [campaign65] %(levelname)s %(message)s")
logger = logging.getLogger("campaign65")

CACHE_DIR = ROOT / "data" / "cache"
REPORTS = ROOT / "reports"
SPOT_CACHE = "0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7"
VOL_META = CACHE_DIR / "volume_1h_full.meta.json"
VOL_PROV = CACHE_DIR / "volume_1h_full.provenance.json"

W_MEANAD = 48
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


def rolling_meanad(s: pd.Series, w: int) -> pd.Series:
    """Causal rolling MeanAD = mean(|x - mean(x)|) over window w (mean-centered L1)."""
    arr = s.values.astype(float)
    out = np.full(len(arr), np.nan, dtype=float)
    n = len(arr)
    for i in range(w - 1, n):
        seg = arr[i - w + 1 : i + 1]
        if not np.all(np.isfinite(seg)):
            continue
        mu = np.mean(seg)
        out[i] = float(np.mean(np.abs(seg - mu)))
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
        disp = rolling_meanad(qv, W_MEANAD)
        d_z = zscore(disp, ZLB)
        logger.info("asset=%s rows=%s", a, len(common))

        cost_slices = {}
        for fee, slip in COST_GRID:
            key = f"fee{fee}_slip{slip}_bps"
            sl = wf_oos(ret1, d_z, fee, slip)
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
        "campaign": 65,
        "title": "Volume Rolling MeanAD (mean-centered L1) Dispersion Shock Mean Reversion — costed OOS (fail-closed, real quote volume)",
        "family": "volume_meanad_mean_centered_l1_dispersion_shock_mr",
        "path": "R-B (validated real_quote_volume; no new blocked-family feed)",
        "oos_edge_proven": n_edge > 0,
        "n_assets_tested": len(by_asset),
        "n_assets_with_exposure": n_exposed,
        "n_oos_edge_proven": n_edge,
        "pre_stated_hypothesis": (
            "D_t = rolling MeanAD of qvol[t-W+1..t], W=48: D_t = mean(|qvol_i - mean(qvol)|) "
            "(mean-centered L1 absolute deviations of ALL observations from the arithmetic mean). "
            "d_z=zscore(D_t,ZLB=168). Mean-revert dispersion shocks: "
            "d_z>=1.25 SHORT (abnormally high MeanAD dispersion; fade), "
            "d_z<=-1.25 LONG (abnormally low MeanAD dispersion; fade), "
            "exit |d_z|<0.25 or hold>=12 or flip. Exec t->t+1. WF 720/168/168. "
            "Cost grid 0-40bps. Edge iff exposure>0 AND all slices OOS net>0 AND >B&H. "
            "Genuinely different from C23/C40-C64."
        ),
        "hypothesis_differs_from_c23_c40_c64": (
            "C65=rolling MeanAD mean(|x-mean(x)|) of qvol (mean-centered L1 dispersion "
            "using ALL observations, arithmetic-mean center). C61=rolling MAD "
            "median(|x-median(x)|), L1 dispersion centered at the MEDIAN — different "
            "center (mean vs median) and estimator. C63=rolling Gini Mean Difference "
            "(mean pairwise |x_i-x_j|, all pairwise L1 distances, no central reference). "
            "C64=rolling Range (max-min), full-extremes using ONLY two order statistics. "
            "C62=rolling IQR (Q3-Q1), rank quartile middle 50%, ignores tail magnitudes. "
            "C48=rolling STD (L2, mean-based squared deviations). C56=CV=std/mean "
            "(relative L2 ratio). C49/C50=kurtosis/skewness (standardized higher moments). "
            "C57/C58/C60=Shannon/Bandt-Pompe/Sample entropies. C59=Hurst R/S fractal "
            "scaling. C51=lag-1 autocorr. C52/C53/C55=cross-corrs; C54=OLS beta. "
            "C45=Amihud. C46=OBV. C47=imbalance. C43/44=divergence/ROC. "
            "C23/40/41/42=vol_z level/expansion. None is rolling mean-centered MeanAD; "
            "C65 orthogonal to C23/C40-C64."
        ),
        "config": {
            "spot_cache": SPOT_CACHE,
            "spot_meta": spot_meta,
            "spot_sha256": spot_sha,
            "volume_meta": str(VOL_META.relative_to(ROOT)),
            "volume_provenance": str(VOL_PROV.relative_to(ROOT)),
            "volume_validation": vol_report,
            "w_meanad": W_MEANAD,
            "zlb": ZLB,
            "entry_z": ENTRY_Z,
            "exit_z": EXIT_Z,
            "max_hold": MAX_HOLD,
            "wf": [WF_TRAIN, WF_TEST, WF_STEP],
            "cost_grid_bps_fee_slippage": COST_GRID,
        },
        "by_asset": by_asset,
    }
    out = REPORTS / f"real_quote_volume_meanad_mean_centered_l1_dispersion_shock_mr_costed_oos_{ts}.json"
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
