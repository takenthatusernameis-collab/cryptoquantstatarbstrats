#!/usr/bin/env python3
"""Generate Campaign 61 artifacts (fail-closed, real data only).

Campaign 61 — Path R-B: a GENUINELY DIFFERENT pre-stated hypothesis on validated
real_quote_volume (Binance spot klines col 5), NOT a rerun of C23/C40–C60.

PRE-STATED HYPOTHESIS (fixed before seeing OOS results):
"Volume Median Absolute Deviation (Robust Dispersion / Scale) Shock Mean Reversion"

Mechanic (pre-stated):
- For each asset, compute rolling Median Absolute Deviation (MAD) D_t of quote
  volume over a causal window W=48h:
    med_t = median(qvol_{t-W+1..t})
    D_t   = median(|qvol_{t-W+1..t} - med_t|)
  MAD is a robust (L1, median-based) scale/dispersion estimator of qvol variability.
- z-score D_t over ZLB=168h (causal) -> d_z.
- Mean-revert robust-dispersion shocks (fade deviations from typical qvol scale):
  d_z >= ENTRY_Z (1.25) -> SHORT (abnormally high robust dispersion/instability; fade);
  d_z <= -ENTRY_Z (-1.25) -> LONG (abnormally low robust dispersion/compressed; fade);
  |d_z| < EXIT_Z (0.25) -> no new entry.
- Exit when |d_z| < EXIT_Z, hold >= MAX_HOLD (12h), or signal flips.
- Execution shift t -> t+1 (causal). WF rolling 720/168/168. Cost grid 0-40bps
  (fee,slip pairs). B&H benchmark on same WF windows.

Edge rule (pre-stated, fail-closed): oos_edge_proven=true IFF exposure>0 AND ALL
cost-grid slices OOS net>0 AND OOS net beats B&H on same WF windows. Else false.
No in-sample tuning, no threshold weakening, no fabricated data/proxies.

DIFFERS FROM C23/C40–C60 (genuinely different transform/mechanic):
- C48 = rolling STD (L2, mean-based 2nd-moment dispersion). C61 = rolling MAD
  (L1, median-based ROBUST scale) — different estimator, different center, robust
  to outliers/heavy tails in qvol; not a rescaling of STD.
- C56 = CV = std/mean (relative dispersion ratio). C61 = absolute robust MAD scale,
  not normalized by mean; different quantity and estimator.
- C60 = Sample Entropy (value-space template-matching regularity/predictability).
  C61 is a dispersion/scale magnitude, not a template-regularity statistic.
- C59 = Hurst exponent / R/S (fractal long-memory scaling across lags). C61 is a
  single-window robust dispersion measure, not a scaling exponent.
- C58 = Bandt–Pompe permutation entropy (ordinal sequence complexity). C57 = Shannon
  value-bin entropy (distributional uncertainty). C61 is neither an entropy nor
  ordinal pattern statistic.
- C49 = kurtosis (4th-moment tail-fatness); C50 = skewness (3rd-moment asymmetry).
  C61 is a 1st-order robust scale (MAD), not a standardized higher moment.
- C51 = lag-1 autocorrelation (temporal dependence). C52/C53/C55 = cross-correlations;
  C54 = OLS beta (scale). C45 = Amihud ratio. C46 = OBV cumulative signed. C47 = up/down
  imbalance partition. C43 = unsloped divergence; C44 = ROC. C23/40/41/42 = vol_z level/
  expansion. None is a rolling median-based robust absolute-deviation scale.
C61 uses rolling MAD (robust L1 median-based dispersion/scale of qvol) — orthogonal
to all L2 moments, relative ratios, entropies, autocorrs, correlations, betas,
partitions, levels, ROC statistics, ordinal/fractal/scaling/template transforms
tested in C23/C40–C60.
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

logging.basicConfig(level=logging.INFO, format="%(asctime)s [campaign61] %(levelname)s %(message)s")
logger = logging.getLogger("campaign61")

CACHE_DIR = ROOT / "data" / "cache"
REPORTS = ROOT / "reports"
SPOT_CACHE = "0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7"
VOL_META = CACHE_DIR / "volume_1h_full.meta.json"
VOL_PROV = CACHE_DIR / "volume_1h_full.provenance.json"

W_MAD = 48
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
    df = pd.read_pickle(pkl)  # noqa: S301 - cached artifact verified by sha256/provenance context
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


def rolling_mad(s: pd.Series, w: int) -> pd.Series:
    """Causal rolling MAD: median(|x - median(x)|) over window w."""
    arr = s.values.astype(float)
    out = np.full(len(arr), np.nan, dtype=float)
    n = len(arr)
    if n < w:
        return pd.Series(out, index=s.index)
    for i in range(w - 1, n):
        win = arr[i - w + 1 : i + 1]
        if not np.all(np.isfinite(win)):
            continue
        med = np.median(win)
        out[i] = float(np.median(np.abs(win - med)))
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
        d = rolling_mad(qv, W_MAD)
        d_z = zscore(d, ZLB)
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
        "campaign": 61,
        "title": "Volume Median Absolute Deviation (Robust Dispersion / Scale) Shock Mean Reversion — costed OOS (fail-closed, real quote volume)",
        "family": "volume_mad_robust_dispersion_shock_mr",
        "path": "R-B (validated real_quote_volume; no new blocked-family feed)",
        "oos_edge_proven": n_edge > 0,
        "n_assets_tested": len(by_asset),
        "n_assets_with_exposure": n_exposed,
        "n_oos_edge_proven": n_edge,
        "pre_stated_hypothesis": (
            "D_t = rolling Median Absolute Deviation of qvol[t-W+1..t], W=48: "
            "med_t=median(qvol_{t-W+1..t}), D_t=median(|qvol_{t-W+1..t}-med_t|) "
            "(robust L1, median-based scale/dispersion). d_z=zscore(D_t,ZLB=168). "
            "Mean-revert robust-dispersion shocks: d_z>=1.25 SHORT (abnormally high robust "
            "dispersion/instability; fade), d_z<=-1.25 LONG (abnormally low robust "
            "dispersion/compressed; fade), exit |d_z|<0.25 or hold>=12 or flip. "
            "Exec t->t+1. WF 720/168/168. Cost grid 0-40bps. Edge iff exposure>0 AND all "
            "slices OOS net>0 AND >B&H. Genuinely different from C23/C40-C60."
        ),
        "hypothesis_differs_from_c23_c40_c60": (
            "C61=rolling MAD (robust L1, median-based absolute-dispersion/scale of qvol). "
            "C48=rolling STD (L2, mean-based 2nd-moment dispersion) — different estimator/"
            "center, robust vs outlier-sensitive. C56=CV=std/mean (relative dispersion ratio) "
            "— C61 is absolute robust scale, not mean-normalized. C60=Sample Entropy "
            "(value-space template-matching regularity/predictability), not dispersion. "
            "C59=Hurst exponent / R/S rescaled-range (fractal long-memory scaling across lags). "
            "C58=Bandt–Pompe permutation entropy (ordinal sequence complexity). C57=Shannon "
            "value-bin entropy (distributional uncertainty). C49=kurtosis (4th-moment "
            "tail-fatness); C50=skewness (3rd-moment asymmetry) — C61 is 1st-order robust "
            "scale, not standardized higher moment. C51=lag-1 autocorrelation. "
            "C52=corr(qvol,|ret|); C53=signed lead corr(qvol,ret_{t+k}); C54=OLS beta; "
            "C55=lead corr(qvol,|ret_{t+k}|). C45=Amihud |ret|/vol. C46=OBV signed-cumulative. "
            "C47=up/down imbalance. C43=unsloped divergence; C44=ROC. C23/40/41/42=vol_z "
            "level/expansion. None is a rolling median-based robust absolute-deviation scale; "
            "C61 orthogonal to all L2 moments, relative ratios, entropies, autocorrs, "
            "correlations, betas, partitions, levels, ROC, ordinal/fractal/scaling/template "
            "transforms tested in C23/C40–C60."
        ),
        "config": {
            "spot_cache": SPOT_CACHE,
            "spot_meta": spot_meta,
            "spot_sha256": spot_sha,
            "volume_meta": str(VOL_META.relative_to(ROOT)),
            "volume_provenance": str(VOL_PROV.relative_to(ROOT)),
            "volume_validation": vol_report,
            "w_mad": W_MAD,
            "zlb": ZLB,
            "entry_z": ENTRY_Z,
            "exit_z": EXIT_Z,
            "max_hold": MAX_HOLD,
            "wf": [WF_TRAIN, WF_TEST, WF_STEP],
            "cost_grid_bps_fee_slippage": COST_GRID,
        },
        "by_asset": by_asset,
    }
    out = REPORTS / f"real_quote_volume_mad_dispersion_shock_mr_costed_oos_{ts}.json"
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
