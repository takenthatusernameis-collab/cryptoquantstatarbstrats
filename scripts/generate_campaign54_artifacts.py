#!/usr/bin/env python3
"""Generate Campaign 54 artifacts (fail-closed, real data only).

Campaign 54 — Path R-B: a GENUINELY DIFFERENT pre-stated hypothesis on validated
real_quote_volume, NOT a rerun of C23/C40/C41/C42/C43/C44/C45/C46/C47/C48/C49/C50/C51/C52/C53.

PRE-STATED HYPOTHESIS (fixed before seeing OOS results):
"Volume-Absolute-Return OLS Beta Sensitivity Shock Mean Reversion (Liquidity-Volatility
Scale/Sensitivity)"

- For each asset compute rolling OLS slope beta_t = Cov(qvol, |ret1|; W=48) / Var(|ret1|; W=48)
  (causal), the regression sensitivity of quote volume to contemporaneous absolute return
  (volatility). beta captures the *scale* of liquidity response per unit volatility.
- z-score beta_t over ZLB=168h (causal) -> beta_z.
- Mean-reversion of sensitivity shocks: beta_z >= ENTRY_Z (1.25) -> SHORT (over-sensitive
  liquidity response, fade); beta_z <= -ENTRY_Z -> LONG (under-sensitive, fade);
  |beta_z| < ENTRY_Z -> no new entry.
- Exit when |beta_z| < EXIT_Z (0.25), hold >= MAX_HOLD (12h), or signal flips.
- Execution shift t -> t+1 (causal). WF rolling 720/168/168. Cost grid 0-40bps (fee,slip pairs).
- Fail-closed: validate_and_load_real_feed for real_quote_volume; reshape long->wide.

DIFFERS FROM C23/C40-C53:
C23/C40/C41=vol_z level/expansion (univariate volume level); C42=expansion confirmation;
C43=unsloped vol_z divergence; C44=vol_z ROC (acceleration); C45=Amihud |ret|/volume
pointwise ratio; C46=OBV signed-cumulative slopes; C47=up/down partition imbalance of qvol;
C48=rolling STD of qvol (2nd-moment dispersion); C49=rolling excess kurtosis (4th-moment
tail-fatness); C50=rolling skewness (3rd-moment asymmetry); C51=rolling lag-1 autocorrelation
(serial dependence/persistence); C52=rolling Pearson CORRELATION corr(qvol,|ret1|) same t
(normalized co-movement, magnitude, no scale); C53=rolling corr(qvol, signed ret[t+k]) with
LEAD k=1 (lead-lag/Granger predictive direction). C54 is the OLS REGRESSION SLOPE beta=Cov/Var
of qvol on |ret1| — a sensitivity/SCALE statistic (how much volume moves per unit |ret|), not
a normalized correlation, not lead-lag, not signed, not a univariate moment/ratio/partition/
ROC/cumulative/imbalance/autocorr transform.
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

logging.basicConfig(level=logging.INFO, format="%(asctime)s [campaign54] %(levelname)s %(message)s")
logger = logging.getLogger("campaign54")

CACHE_DIR = ROOT / "data" / "cache"
REPORTS = ROOT / "reports"
SPOT_CACHE = "0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7"
VOL_META = CACHE_DIR / "volume_1h_full.meta.json"
VOL_PROV = CACHE_DIR / "volume_1h_full.provenance.json"

W_BETA = 48
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


def rolling_beta(x: pd.Series, y: pd.Series, w: int) -> pd.Series:
    cov = x.rolling(w, min_periods=w).cov(y)
    var = y.rolling(w, min_periods=w).var(ddof=0)
    return cov / var.replace(0, np.nan)


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
        absret = ret1.abs()
        beta = rolling_beta(qv, absret, W_BETA)
        beta_z = zscore(beta, ZLB)
        logger.info("asset=%s rows=%s", a, len(common))

        cost_slices = {}
        for fee, slip in COST_GRID:
            key = f"fee{fee}_slip{slip}_bps"
            sl = wf_oos(ret1, beta_z, fee, slip)
            ag = agg(sl)
            # BH on same windows
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
        "campaign": 54,
        "title": "Volume-Absolute-Return OLS Beta Sensitivity Shock Mean Reversion — costed OOS (fail-closed, real quote volume)",
        "family": "volume_absret_ols_beta_sensitivity_shock_mr",
        "path": "R-B (validated real_quote_volume; no new blocked-family feed)",
        "oos_edge_proven": n_edge > 0,
        "n_assets_tested": len(by_asset),
        "n_assets_with_exposure": n_exposed,
        "n_oos_edge_proven": n_edge,
        "pre_stated_hypothesis": (
            "beta_t = Cov(qvol,|ret1|;W=48)/Var(|ret1|;W=48) (OLS regression slope = liquidity-volatility sensitivity/scale); "
            "beta_z=zscore(beta_t,ZLB=168). Mean-revert sensitivity shocks: beta_z>=1.25 SHORT, beta_z<=-1.25 LONG, "
            "exit |beta_z|<0.25 or hold>=12 or flip. Exec t->t+1. WF 720/168/168. Cost grid 0-40bps. Edge iff exposure>0 "
            "AND all slices OOS net>0 AND >B&H. Genuinely different from C23/C40-C53: regression SLOPE (scale/sensitivity), "
            "not C52 normalized correlation (co-movement), not C53 signed lead-lag corr (predictive direction), not any "
            "prior univariate moment/level/ROC/ratio/cumulative/partition/imbalance/autocorr transform."
        ),
        "hypothesis_differs_from_c23_c40_c53": (
            "C54 = OLS beta Cov(qvol,|ret1|)/Var(|ret1|) sensitivity/scale. C52 = Pearson corr (normalized). "
            "C53 = corr(qvol, ret[t+k]) signed lead-lag. C23/40/41/42=vol_z level/expansion; C43=divergence; C44=ROC; "
            "C45=Amihud ratio; C46=OBV slopes; C47=up/down imbalance; C48=STD; C49=kurtosis; C50=skewness; C51=autocorr."
        ),
        "config": {
            "spot_cache": SPOT_CACHE, "spot_meta": spot_meta, "spot_sha256": spot_sha,
            "volume_meta": str(VOL_META.relative_to(ROOT)), "volume_provenance": str(VOL_PROV.relative_to(ROOT)),
            "volume_validation": vol_report, "w_beta": W_BETA, "zlb": ZLB, "entry_z": ENTRY_Z, "exit_z": EXIT_Z,
            "max_hold": MAX_HOLD, "wf": [WF_TRAIN, WF_TEST, WF_STEP], "cost_grid_bps_fee_slippage": COST_GRID,
        },
        "by_asset": by_asset,
    }
    out = REPORTS / f"real_quote_volume_vol_absret_beta_sensitivity_shock_mr_costed_oos_{ts}.json"
    out.write_text(json.dumps(report, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"wrote": str(out), "oos_edge_proven": report["oos_edge_proven"], "n_edge": n_edge, "n_exposed": n_exposed, "n_assets": len(by_asset)}))


if __name__ == "__main__":
    main()
