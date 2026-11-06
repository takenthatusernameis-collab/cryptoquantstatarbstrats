#!/usr/bin/env python3
"""Generate Campaign 59 artifacts (fail-closed, real data only).

Campaign 59 — Path R-B: a GENUINELY DIFFERENT pre-stated hypothesis on validated
real_quote_volume (Binance spot klines col 5), NOT a rerun of C23/C40–C58.

PRE-STATED HYPOTHESIS (fixed before seeing OOS results):
"Volume Hurst Exponent (Fractal / Long-Memory Scaling) Shock Mean Reversion"

Mechanic (pre-stated):
- For each asset, compute rolling Hurst exponent H_t of quote volume over a
  causal window W=48h using rescaled-range (R/S) analysis across lag set
  L={2,4,8,16}: H = slope of log(E[R/S]) vs log(lag) via OLS. H in [0,1]:
  H<0.5 anti-persistent (mean-reverting), H>0.5 persistent (trending),
  H≈0.5 random walk (no memory).
- z-score H_t over ZLB=168h (causal) -> h_z.
- Mean-revert fractal-scaling shocks (fade deviations from random-walk memory):
  h_z >= ENTRY_Z (1.25) -> SHORT (abnormally persistent/trending qvol; fade);
  h_z <= -ENTRY_Z (-1.25) -> LONG (abnormally anti-persistent/mean-reverting qvol; fade);
  |h_z| < EXIT_Z (0.25) -> no new entry.
- Exit when |h_z| < EXIT_Z, hold >= MAX_HOLD (12h), or signal flips.
- Execution shift t -> t+1 (causal). WF rolling 720/168/168. Cost grid 0-40bps
  (fee,slip pairs). B&H benchmark on same WF windows.

Edge rule (pre-stated, fail-closed): oos_edge_proven=true IFF exposure>0 AND ALL
cost-grid slices OOS net>0 AND OOS net beats B&H on same WF windows. Else false.
No in-sample tuning, no threshold weakening, no fabricated data/proxies.

DIFFERS FROM C23/C40–C58 (genuinely different transform/mechanic):
- C58 = Bandt–Pompe permutation entropy of ordinal PATTERNS (temporal/sequence
  complexity via rank orderings). C59 = Hurst exponent / R/S rescaled-range
  (fractal long-memory scaling exponent via lag-dependent dispersion) —
  orthogonal to ordinal pattern entropy.
- C57 = Shannon entropy of BINNED qvol VALUES (distributional uncertainty over
  magnitudes, quantile bins). C59 is a scaling exponent across lags, not a value
  histogram entropy.
- C51 = lag-1 autocorrelation (single-lag linear temporal dependence).
  C59 estimates a scaling exponent across multiple lags via R/S — not a single
  lag moment.
- C48=STD (2nd moment), C49=kurtosis (4th), C50=skewness (3rd), C56=CV (ratio).
  C59 is not any moment or moment ratio.
- C23/40/41/42 = vol_z level/expansion. C43=unsloped divergence. C44=ROC.
  C45=Amihud |ret|/volume. C46=OBV signed-cumulative. C47=up/down imbalance.
  C52=corr(qvol,|ret|). C53=signed lead corr(qvol,ret_{t+k}). C54=OLS beta.
  C55=lead corr(qvol,|ret_{t+k}|) magnitude. None is a Hurst/scaling exponent.
C59 uses Hurst exponent / R/S rescaled-range (fractal long-memory scaling of the
qvol sequence) — orthogonal to all value-bin entropies, moments, ratios,
correlations, betas, partitions, levels, ROC statistics, ordinal-pattern entropy,
and single-lag autocorrelation tested in C23/C40–C58.
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

logging.basicConfig(level=logging.INFO, format="%(asctime)s [campaign59] %(levelname)s %(message)s")
logger = logging.getLogger("campaign59")

CACHE_DIR = ROOT / "data" / "cache"
REPORTS = ROOT / "reports"
SPOT_CACHE = "0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7"
VOL_META = CACHE_DIR / "volume_1h_full.meta.json"
VOL_PROV = CACHE_DIR / "volume_1h_full.provenance.json"

W_HURST = 48
LAGS = (2, 4, 8, 16)
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
    df = pd.read_pickle(pkl)  # noqa: S301 - cached artifact verified by sha256 in caller config
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


def _rs_statistics(arr: np.ndarray, lags: tuple[int, ...]):
    """Rescaled-range statistics per lag: mean(R/S) over non-overlapping blocks."""
    n = len(arr)
    rs_means = []
    valid_lags = []
    for lag in lags:
        if lag < 2 or n < 2 * lag:
            continue
        n_blocks = n // lag
        if n_blocks < 2:
            continue
        block_vals = []
        for b in range(n_blocks):
            seg = arr[b * lag : (b + 1) * lag]
            if not np.all(np.isfinite(seg)):
                continue
            mean = float(np.mean(seg))
            dev = seg - mean
            cum = np.cumsum(dev)
            r = float(np.max(cum) - np.min(cum))
            s = float(np.std(seg, ddof=1)) if lag > 1 else 0.0
            if s <= 0 or not np.isfinite(s):
                continue
            block_vals.append(r / s)
        if len(block_vals) < 2:
            continue
        rs_means.append(float(np.mean(block_vals)))
        valid_lags.append(lag)
    return np.array(rs_means, dtype=float), np.array(valid_lags, dtype=float)


def rolling_hurst(s: pd.Series, w: int, lags: tuple[int, ...]) -> pd.Series:
    arr = s.values.astype(float)
    out = np.full(len(arr), np.nan, dtype=float)
    n = len(arr)
    if n < w:
        return pd.Series(out, index=s.index)
    for i in range(w - 1, n):
        win = arr[i - w + 1 : i + 1]
        if not np.all(np.isfinite(win)):
            continue
        rs_means, valid_lags = _rs_statistics(win, lags)
        if len(rs_means) < 2 or len(valid_lags) < 2:
            continue
        x = np.log(valid_lags.astype(float))
        y = np.log(np.maximum(rs_means, 1e-12))
        xm = float(np.mean(x))
        xd = float(np.sum((x - xm) ** 2))
        if xd <= 0 or not np.isfinite(xd):
            continue
        ym = float(np.mean(y))
        slope = float(np.sum((x - xm) * (y - ym)) / xd)
        h = float(np.clip(slope, 0.0, 1.0)) if np.isfinite(slope) else np.nan
        out[i] = h
    return pd.Series(out, index=s.index)


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
        h = rolling_hurst(qv, W_HURST, LAGS)
        h_z = zscore(h, ZLB)
        logger.info("asset=%s rows=%s", a, len(common))

        cost_slices = {}
        for fee, slip in COST_GRID:
            key = f"fee{fee}_slip{slip}_bps"
            sl = wf_oos(ret1, h_z, fee, slip)
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
        "campaign": 59,
        "title": "Volume Hurst Exponent (Fractal / Long-Memory Scaling) Shock Mean Reversion — costed OOS (fail-closed, real quote volume)",
        "family": "volume_hurst_exponent_shock_mr",
        "path": "R-B (validated real_quote_volume; no new blocked-family feed)",
        "oos_edge_proven": n_edge > 0,
        "n_assets_tested": len(by_asset),
        "n_assets_with_exposure": n_exposed,
        "n_oos_edge_proven": n_edge,
        "pre_stated_hypothesis": (
            "H_t = rolling Hurst exponent of qvol[t-W+1..t], W=48, via R/S rescaled-range "
            "across lags {2,4,8,16}: H=slope(log(E[R/S]) vs log(lag)); H<0.5 anti-persistent, "
            "H>0.5 persistent, H≈0.5 random walk. h_z=zscore(H_t,ZLB=168). Mean-revert "
            "fractal-scaling shocks: h_z>=1.25 SHORT (persistent/trending qvol; fade), "
            "h_z<=-1.25 LONG (anti-persistent/mean-reverting qvol; fade), exit |h_z|<0.25 "
            "or hold>=12 or flip. Exec t->t+1. WF 720/168/168. Cost grid 0-40bps. "
            "Edge iff exposure>0 AND all slices OOS net>0 AND >B&H. "
            "Genuinely different from C23/C40-C58 (fractal long-memory scaling exponent)."
        ),
        "hypothesis_differs_from_c23_c40_c58": (
            "C59=Hurst exponent / R/S rescaled-range (fractal long-memory scaling exponent "
            "across lag set {2,4,8,16}) — captures persistence/memory scaling of the qvol "
            "sequence, not ordinal patterns. C58=Bandt–Pompe permutation entropy of ordinal "
            "PATTERNS (temporal/sequence complexity via rank orderings, m=3 tau=1). "
            "C57=Shannon entropy of BINNED qvol VALUES (magnitude distributional uncertainty). "
            "C51=lag-1 autocorrelation (single-lag linear temporal dependence). C56=CV=std/mean. "
            "C48=STD 2nd-moment. C49=kurtosis 4th-moment. C50=skewness 3rd-moment. "
            "C23/40/41/42=vol_z level/expansion. C43=unsloped divergence; C44=ROC; "
            "C45=Amihud |ret|/vol; C46=OBV signed-cumulative; C47=up/down imbalance; "
            "C52=corr(qvol,|ret|); C53=signed lead corr(qvol,ret_{t+k}); C54=OLS beta; "
            "C55=lead corr(qvol,|ret_{t+k}|) magnitude."
        ),
        "config": {
            "spot_cache": SPOT_CACHE,
            "spot_meta": spot_meta,
            "spot_sha256": spot_sha,
            "volume_meta": str(VOL_META.relative_to(ROOT)),
            "volume_provenance": str(VOL_PROV.relative_to(ROOT)),
            "volume_validation": vol_report,
            "w_hurst": W_HURST,
            "lags": list(LAGS),
            "zlb": ZLB,
            "entry_z": ENTRY_Z,
            "exit_z": EXIT_Z,
            "max_hold": MAX_HOLD,
            "wf": [WF_TRAIN, WF_TEST, WF_STEP],
            "cost_grid_bps_fee_slippage": COST_GRID,
        },
        "by_asset": by_asset,
    }
    out = REPORTS / f"real_quote_volume_hurst_exponent_shock_mr_costed_oos_{ts}.json"
    out.write_text(json.dumps(report, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"wrote": str(out), "oos_edge_proven": report["oos_edge_proven"], "n_edge": n_edge, "n_exposed": n_exposed, "n_assets": len(by_asset)}))


if __name__ == "__main__":
    main()
