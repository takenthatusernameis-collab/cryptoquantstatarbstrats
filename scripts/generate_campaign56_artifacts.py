#!/usr/bin/env python3
"""Generate Campaign 56 artifacts (fail-closed, real data only).

Campaign 56 — Path R-B: a GENUINELY DIFFERENT pre-stated hypothesis on validated
real_quote_volume (Binance spot klines col 5), NOT a rerun of C23/C40–C55.

PRE-STATED HYPOTHESIS (fixed before seeing OOS results):
"Volume Coefficient-of-Variation (Relative Dispersion) Shock Mean Reversion"

Mechanic (pre-stated):
- For each asset, compute rolling coefficient of variation of quote volume over
  causal window W=48h: CV_t = std(qvol[t-W+1..t]) / mean(qvol[t-W+1..t]).
  CV is a SCALE-NORMALIZED relative dispersion (std divided by mean), distinct
  from raw level or raw second moment.
- z-score CV_t over ZLB=168h (causal) -> cv_z.
- Mean-revert relative-dispersion shocks (fade extremes):
  cv_z >= ENTRY_Z (1.25) -> SHORT (abnormally unstable relative volume dispersion; fade);
  cv_z <= -ENTRY_Z (-1.25) -> LONG (abnormally stable/compressed dispersion; fade);
  |cv_z| < ENTRY_Z -> no new entry.
- Exit when |cv_z| < EXIT_Z (0.25), hold >= MAX_HOLD (12h), or signal flips.
- Execution shift t -> t+1 (causal). WF rolling 720/168/168. Cost grid 0-40bps
  (fee,slip pairs). B&H benchmark on same WF windows.

Edge rule (pre-stated, fail-closed): oos_edge_proven=true IFF exposure>0 AND ALL
cost-grid slices OOS net>0 AND OOS net beats B&H on same WF windows. Else false.
No in-sample tuning, no threshold weakening, no fabricated data/proxies.

DIFFERS FROM C23/C40–C55 (genuinely different transform/mechanic):
- C48 = rolling STD(qvol) (raw 2nd-moment scale, NOT normalized by mean). C56 divides
  std by rolling mean -> Coefficient of Variation (relative/scale-normalized dispersion).
- C23/C40/C41/C42 = vol_z of raw volume level/expansion (univariate level). C56 uses
  a ratio statistic (std/mean) capturing relative variability independent of level scale.
- C45 = Amihud |ret|/volume pointwise ratio (return per volume). C56 = std(qvol)/mean(qvol)
  within-volume dispersion ratio (no return term).
- C43 = unsloped vol_z divergence at price extremes. C44 = vol_z ROC (first difference).
  C46 = OBV signed-cumulative slopes. C47 = up/down partition imbalance.
  C49 = excess kurtosis (4th-moment). C50 = skewness (3rd-moment). C51 = lag-1 autocorr.
  C52 = contemporaneous Pearson corr(qvol,|ret|). C53 = signed lead corr(qvol,ret_{t+k}).
  C54 = contemporaneous OLS beta sensitivity. C55 = lead corr(qvol,|ret_{t+k}|) on magnitude.
C56 is a normalized relative-dispersion (CV = std/mean) statistic of qvol alone — distinct
from all above.
"""
from __future__ import annotations

import hashlib
import json
import logging
import math
import pickle
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.real_feed_loader import validate_and_load_real_feed  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [campaign56] %(levelname)s %(message)s")
logger = logging.getLogger("campaign56")

CACHE_DIR = ROOT / "data" / "cache"
REPORTS = ROOT / "reports"
SPOT_CACHE = "0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7"
VOL_META = CACHE_DIR / "volume_1h_full.meta.json"
VOL_PROV = CACHE_DIR / "volume_1h_full.provenance.json"

W_CV = 48
ZLB = 168
ENTRY_Z = 1.25
EXIT_Z = 0.25
MAX_HOLD = 12
WF_TRAIN, WF_TEST, WF_STEP = 720, 168, 168
COST_GRID = [(0, 0), (5, 0), (0, 5), (5, 5), (10, 0), (0, 10), (10, 10), (20, 0), (0, 20), (20, 20)]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_spot():
    pkl = CACHE_DIR / f"{SPOT_CACHE}.pkl"
    meta = json.loads((CACHE_DIR / f"{SPOT_CACHE}.meta.json").read_text(encoding="utf-8"))
    df = pickle.load(open(pkl, "rb"))
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


def rolling_cv(s: pd.Series, w: int) -> pd.Series:
    m = s.rolling(w, min_periods=w).mean()
    sd = s.rolling(w, min_periods=w).std(ddof=0)
    # guard zero/negative mean
    m = m.where(m > 0, np.nan)
    return sd / m


def zscore(s: pd.Series, lb: int) -> pd.Series:
    m = s.rolling(lb, min_periods=lb).mean()
    sd = s.rolling(lb, min_periods=lb).std(ddof=0)
    return (s - m) / sd.replace(0, np.nan)


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
        out.append(simulate(ret1.iloc[te:tst_e].reset_index(drop=True), sig.iloc[te:tst_e].reset_index(drop=True), fee_bps, slip_bps))
        start += WF_STEP
    return out


def agg(slices):
    if not slices:
        return {"n": 0, "oos_net_sum": 0.0, "exposure": 0.0}
    rets = [s["total_return"] for s in slices]
    return {"n": len(slices), "oos_net_sum": float(np.prod([1 + r for r in rets]) - 1.0), "exposure": float(np.mean([s["exposure_frac"] for s in slices]))}


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
        cv = rolling_cv(qv, W_CV)
        cv_z = zscore(cv, ZLB)
        logger.info("asset=%s rows=%s", a, len(common))

        cost_slices = {}
        for fee, slip in COST_GRID:
            key = f"fee{fee}_slip{slip}_bps"
            sl = wf_oos(ret1, cv_z, fee, slip)
            ag = agg(sl)
            bh_sl = []
            n = len(ret1); st = 0
            while True:
                te = st + WF_TRAIN; tst_e = te + WF_TEST
                if tst_e > n: break
                rsl = ret1.iloc[te:tst_e].fillna(0.0)
                bh_sl.append({"total_return": float((1 + rsl).prod() - 1.0), "exposure_frac": 1.0})
                st += WF_STEP
            bh_net = agg(bh_sl)["oos_net_sum"] if bh_sl else 0.0
            cost_slices[key] = {"net_oos_sum": ag["oos_net_sum"], "bh_oos_sum": bh_net,
                                "oos_net_gt_zero": ag["oos_net_sum"] > 0, "oos_net_beat_bh": ag["oos_net_sum"] > bh_net,
                                "n_slices": ag["n"], "exposure": ag["exposure"]}
        exposure = cost_slices["fee0_slip0_bps"]["exposure"] > 0
        all_pos = all(v["oos_net_gt_zero"] for v in cost_slices.values())
        all_bh = all(v["oos_net_beat_bh"] for v in cost_slices.values())
        edge = exposure and all_pos and all_bh
        if exposure: n_exposed += 1
        if edge: n_edge += 1
        by_asset[a] = {"rows": len(common), "has_exposure": exposure, "oos_edge_proven": edge, "cost_slices": cost_slices}

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "campaign": 56,
        "title": "Volume Coefficient-of-Variation (Relative Dispersion) Shock Mean Reversion — costed OOS (fail-closed, real quote volume)",
        "family": "volume_cv_relative_dispersion_shock_mr",
        "path": "R-B (validated real_quote_volume; no new blocked-family feed)",
        "oos_edge_proven": n_edge > 0,
        "n_assets_tested": len(by_asset),
        "n_assets_with_exposure": n_exposed,
        "n_oos_edge_proven": n_edge,
        "pre_stated_hypothesis": (
            "CV_t = std(qvol[t-W+1..t])/mean(qvol[t-W+1..t]), W=48 (scale-normalized relative dispersion). "
            "cv_z=zscore(CV_t,ZLB=168). Fade shocks: cv_z>=1.25 SHORT, cv_z<=-1.25 LONG, "
            "exit |cv_z|<0.25 or hold>=12 or flip. Exec t->t+1. WF 720/168/168. Cost grid 0-40bps. "
            "Edge iff exposure>0 AND all slices OOS net>0 AND >B&H. Genuinely different from C23/C40-C55."
        ),
        "hypothesis_differs_from_c23_c40_c55": (
            "C56=CV=rolling_std(qvol)/rolling_mean(qvol) (scale-normalized relative dispersion, a ratio). "
            "C48=rolling STD(qvol) raw 2nd-moment (NOT normalized by mean). "
            "C23/40/41/42=vol_z of raw volume level/expansion. C45=Amihud |ret|/volume (return per volume). "
            "C43=unsloped vol_z divergence; C44=vol_z ROC; C46=OBV signed-cumulative slopes; C47=up/down imbalance; "
            "C49=kurtosis; C50=skewness; C51=lag-1 autocorr; C52=contemporaneous corr(qvol,|ret|); "
            "C53=signed lead corr(qvol,ret_{t+k}); C54=contemporaneous OLS beta sensitivity; "
            "C55=lead corr(qvol,|ret_{t+k}|) on magnitude."
        ),
        "config": {
            "spot_cache": SPOT_CACHE, "spot_meta": spot_meta, "spot_sha256": spot_sha,
            "volume_meta": str(VOL_META.relative_to(ROOT)), "volume_provenance": str(VOL_PROV.relative_to(ROOT)),
            "volume_validation": vol_report, "w_cv": W_CV, "zlb": ZLB,
            "entry_z": ENTRY_Z, "exit_z": EXIT_Z, "max_hold": MAX_HOLD,
            "wf": [WF_TRAIN, WF_TEST, WF_STEP], "cost_grid_bps_fee_slippage": COST_GRID,
        },
        "by_asset": by_asset,
    }
    out = REPORTS / f"real_quote_volume_cv_relative_dispersion_shock_mr_costed_oos_{ts}.json"
    out.write_text(json.dumps(report, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"wrote": str(out), "oos_edge_proven": report["oos_edge_proven"], "n_edge": n_edge, "n_exposed": n_exposed, "n_assets": len(by_asset)}))


if __name__ == "__main__":
    main()
