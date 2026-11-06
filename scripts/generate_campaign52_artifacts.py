#!/usr/bin/env python3
"""Generate Campaign 52 artifacts.

Campaign 52 — Path R-B (fail-closed, real data only): a GENUINELY DIFFERENT
pre-stated hypothesis on validated real_quote_volume (Binance spot klines col 5),
NOT a rerun of C23/C40/C41/C42/C43/C44/C45/C46/C47/C48/C49/C50/C51.

PRE-STATED HYPOTHESIS (fixed before seeing OOS results):
"Volume-Absolute-Return Rolling Correlation Shock Mean Reversion (Liquidity-Volatility
Co-movement Regime Shock Fade)"
- Compute rolling Pearson correlation between real quote volume and |ret1|
  (absolute 1-bar return, a realized-volatility proxy) over a causal window W=48h:
  corr_vr = corr(qvol, |ret1|, W). Z-score corr_vr over ZLB=168h (causal):
  cvr_z = (corr_vr - mean(corr_vr,ZLB))/std(corr_vr,ZLB). This measures
  LIQUIDITY-VOLATILITY CO-MOVEMENT / bivariate dependence structure — a
  genuinely different transform from all prior campaigns:
    * C23/C40/C41 use vol_z LEVEL (first-moment volume z, univariate).
    * C42 uses volume expansion (vol_z level breakout confirmation).
    * C43 uses unsloped vol_z divergence at price extremes.
    * C44 uses vol_z ROC (first difference/acceleration of vol_z).
    * C45 uses Amihud |ret|/volume (price-impact RATIO, pointwise).
    * C46 uses OBV cumulative sign*vol slopes (integrated signed volume).
    * C47 uses up/down partition imbalance ratio of qvol by return sign.
    * C48 uses z-score of ROLLING STD of qvol (2nd-moment dispersion, univariate).
    * C49 uses z-score of ROLLING EXCESS KURTOSIS of qvol (4th-moment tail-fatness).
    * C50 uses z-score of ROLLING SKEWNESS of qvol (3rd-moment asymmetry).
    * C51 uses z-score of ROLLING LAG-1 AUTOCORRELATION of qvol (serial dependence).
  cvr_z is a z-score of ROLLING CROSS-CORRELATION between qvol and |ret1| — a
  distinct bivariate dependence/co-movement statistic (liquidity-volatility coupling
  regime) using |ret1| jointly with qvol, not a univariate moment, not autocorrelation,
  not a pointwise ratio, and not any prior level/slope/ROC/divergence/partition transform.
- Entry (fade extreme liquidity-volatility co-movement shocks, mean reversion):
  when cvr_z >= ENTRY_Z (abnormally strong volume-volatility co-movement regime) AND
  ret_W > 0 -> SHORT (tight liquidity-vol coupling during up-move tends to normalize);
  cvr_z >= ENTRY_Z AND ret_W < 0 -> LONG (tight co-movement during down-move tends
  to normalize/revert). Extreme negative co-movement (cvr_z <= -ENTRY_Z, volume and
  |ret| decoupling/inverse regime) -> no entry (pre-stated asymmetry).
- Exit: cvr_z < EXIT_Z OR hold >= MAX_HOLD_BARS (12h) OR signal flips. Else flat.
- Execution shift t -> t+1 (causal).
- Walk-forward: rolling 720/168/168. Cost grid: fee+slip bps pairs
  [[0,0],[5,0],[0,5],[5,5],[10,0],[0,10],[10,10],[20,0],[0,20],[20,20]] (0-40bps).
- Benchmark: buy-and-hold per asset on union of OOS WF windows (gross).
- Pre-stated edge rule (fail-closed): oos_edge_proven=true IFF executed
  exposure>0 AND for ALL cost-grid slices OOS net sum > 0 AND OOS net sum > B&H
  OOS sum on same OOS windows. Else false. No in-sample tuning, no threshold
  weakening, no fabricated data/proxies.

Real data only. Causal trailing windows only. Fail-closed.
"""
from __future__ import annotations

import hashlib
import json
import logging
import pickle
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(ROOT))

from data.real_feed_loader import validate_and_load_real_feed  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [campaign52] %(levelname)s %(message)s")
logger = logging.getLogger("campaign52")

CACHE_DIR = ROOT / "data" / "cache"
REPORTS_DIR = ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

SPOT_CACHE = "0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7"
VOL_META = CACHE_DIR / "volume_1h_full.meta.json"
VOL_PROV = CACHE_DIR / "volume_1h_full.provenance.json"
COST_GRID = [[0, 0], [5, 0], [0, 5], [5, 5], [10, 0], [0, 10], [10, 10], [20, 0], [0, 20], [20, 20]]
TRAIN, TEST, STEP = 720, 168, 168
PARAMS = {
    "corr_window": 48,      # rolling window for corr(qvol, |ret1|)
    "z_lookback": 168,
    "entry_z": 1.25,        # extreme liquidity-volatility co-movement shock
    "exit_z": 0.25,
    "max_hold_bars": 12,
    "min_obs": 168,
    "eps": 1e-12,
}


def _utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _json_safe(value: Any) -> Any:
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        v = float(value)
        return None if (np.isnan(v) or np.isinf(v)) else v
    if isinstance(value, float):
        return None if (np.isnan(value) or np.isinf(value)) else value
    if isinstance(value, pd.Timestamp):
        return str(value)
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(v) for v in value]
    if isinstance(value, np.ndarray):
        return [_json_safe(v) for v in value.tolist()]
    try:
        json.dumps(value)
        return value
    except Exception:
        return str(value)


def _write_json(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_json_safe(obj), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


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


def load_volume():
    if not VOL_PROV.exists():
        raise FileNotFoundError(f"volume provenance certificate missing: {VOL_PROV}")
    prov = json.loads(VOL_PROV.read_text(encoding="utf-8"))
    df, report = validate_and_load_real_feed(VOL_META, "real_quote_volume", provenance=prov)
    return df, report


def wf_splits(n: int, train: int = TRAIN, test: int = TEST, step: int = STEP):
    splits = []
    start = 0
    while True:
        tr_s = start
        tr_e = tr_s + train
        te_e = tr_e + test
        if te_e > n:
            break
        splits.append((tr_s, tr_e, te_e))
        start += step
    return splits


def _zscore(s: pd.Series, lb: int, eps: float) -> pd.Series:
    mu = s.rolling(lb, min_periods=lb).mean()
    sd = s.rolling(lb, min_periods=lb).std(ddof=0).replace(0, np.nan)
    return (s - mu) / (sd + eps)


def compute_vol_absret_corr_signal(close: pd.Series, vol: pd.Series, params: dict) -> pd.DataFrame:
    df = pd.DataFrame({"close": close.astype(float), "qvol": vol.astype(float)}).sort_index()
    df["ret1"] = df["close"].pct_change()
    df["absret"] = df["ret1"].abs()
    w = int(params["corr_window"])
    eps = float(params["eps"])
    # Rolling cross-correlation: liquidity-volatility co-movement
    df["corr_vr"] = df["qvol"].rolling(w, min_periods=w).corr(df["absret"])
    df["cvr_z"] = _zscore(df["corr_vr"], int(params["z_lookback"]), eps)
    df["ret_w"] = df["close"].pct_change(w)

    sig = np.zeros(len(df), dtype=float)
    raw = np.zeros(len(df), dtype=float)
    cz = df["cvr_z"].to_numpy()
    rw = df["ret_w"].to_numpy()
    entry = float(params["entry_z"])
    exit_z = float(params["exit_z"])
    mh = int(params["max_hold_bars"])

    for i in range(len(df)):
        if not (np.isfinite(cz[i]) and np.isfinite(rw[i])):
            continue
        # pre-stated asymmetry: fade extreme liquidity-volatility co-movement shocks
        if cz[i] >= entry and rw[i] > 0:
            raw[i] = -1.0  # tight co-movement during up-move -> fade short
        elif cz[i] >= entry and rw[i] < 0:
            raw[i] = 1.0   # tight co-movement during down-move -> fade long
        # cz <= -entry: extreme decoupling/inverse regime -> no entry (pre-stated)

    hold = 0
    pos = 0.0
    for i in range(len(df)):
        desired = raw[i]
        norm = np.isfinite(cz[i]) and cz[i] < exit_z
        if pos != 0.0:
            hold += 1
            flip = desired != 0.0 and desired != pos
            if norm or hold >= mh or flip:
                if flip:
                    pos = desired
                    hold = 0
                else:
                    pos = 0.0
                    hold = 0
        else:
            if desired != 0.0:
                pos = desired
                hold = 0
        sig[i] = pos
    df["sig_raw"] = sig
    df["signal"] = df["sig_raw"].shift(1).fillna(0.0)  # t->t+1 execution
    return df


def run_asset(close: pd.Series, vol: pd.Series):
    c, v = close.align(vol, join="inner")
    c = c.dropna()
    v = v.reindex(c.index).dropna()
    c = c.reindex(v.index)
    sdf = compute_vol_absret_corr_signal(c, v, PARAMS)
    splits = wf_splits(len(sdf))
    if not splits:
        return {"error": "insufficient_length", "rows": int(len(sdf)), "splits": 0}
    oos_mask = np.zeros(len(sdf), dtype=bool)
    for _, tr_e, te_e in splits:
        oos_mask[tr_e:te_e] = True
    ret1 = sdf["ret1"].fillna(0.0).to_numpy()
    signal = sdf["signal"].to_numpy()
    gross = signal * ret1
    slices = {}
    for fee, slip in COST_GRID:
        tc_bps = fee + slip
        turnover = np.abs(np.diff(signal, prepend=0.0))
        cost = turnover * (tc_bps / 10000.0)
        net = gross - cost
        oos_net = net[oos_mask]
        oos_gross = gross[oos_mask]
        oos_bh = ret1[oos_mask]
        slices[f"fee{fee}_slip{slip}_bps"] = {
            "tc_bps_roundtrip_assumed": tc_bps,
            "net_oos_sum": float(np.nansum(oos_net)),
            "gross_oos_sum": float(np.nansum(oos_gross)),
            "bh_oos_sum": float(np.nansum(oos_bh)),
            "n_oos_bars": int(oos_mask.sum()),
            "exposure_bars": int((signal[oos_mask] != 0).sum()),
            "turnover_sum": float(np.nansum(turnover[oos_mask])),
            "oos_net_gt_zero": bool(np.nansum(oos_net) > 0),
            "oos_net_beat_bh": bool(np.nansum(oos_net) > np.nansum(oos_bh)),
        }
    has_exposure = bool((signal[oos_mask] != 0).any())
    all_gt_zero = all(s["oos_net_gt_zero"] for s in slices.values())
    all_beat_bh = all(s["oos_net_beat_bh"] for s in slices.values())
    edge = bool(has_exposure and all_gt_zero and all_beat_bh)
    return {
        "rows": int(len(sdf)),
        "splits": len(splits),
        "oos_bars": int(oos_mask.sum()),
        "has_exposure": has_exposure,
        "all_slices_oos_net_gt_zero": all_gt_zero,
        "all_slices_oos_net_beat_bh": all_beat_bh,
        "oos_edge_proven": edge,
        "cost_slices": slices,
        "signal_counts_oos": {
            "short": int((signal[oos_mask] == -1).sum()),
            "flat": int((signal[oos_mask] == 0).sum()),
            "long": int((signal[oos_mask] == 1).sum()),
        },
        "z_stats_oos": {
            "cvr_z_mean": float(np.nanmean(sdf["cvr_z"].to_numpy()[oos_mask])),
            "cvr_z_min": float(np.nanmin(sdf["cvr_z"].to_numpy()[oos_mask])),
            "cvr_z_max": float(np.nanmax(sdf["cvr_z"].to_numpy()[oos_mask])),
        },
    }


def main():
    spot_df, spot_meta, spot_sha = load_spot()
    vol_df, vol_report = load_volume()
    vol_report_safe = vol_report.to_dict() if hasattr(vol_report, "to_dict") else vol_report
    if not vol_report_safe.get("ok"):
        raise RuntimeError(f"volume feed failed validation: {vol_report_safe}")

    assets = [c for c in spot_df.columns.get_level_values(0).unique() if c in vol_df.columns]
    by_asset = {}
    for a in sorted(assets):
        close = spot_df[(a, "close")] if (a, "close") in spot_df.columns else spot_df[a]["close"]
        v = vol_df[a]
        logger.info("asset=%s rows_spot=%s rows_vol=%s", a, len(close.dropna()), len(v.dropna()))
        by_asset[a] = run_asset(close, v)

    n_edge = sum(1 for r in by_asset.values() if isinstance(r, dict) and r.get("oos_edge_proven"))
    n_exposed = sum(1 for r in by_asset.values() if isinstance(r, dict) and r.get("has_exposure"))
    out = {
        "generated_at_utc": _utc_now_iso(),
        "campaign": 52,
        "title": "Volume-Absolute-Return Rolling Correlation Shock Mean Reversion (Liquidity-Volatility Co-movement) — costed OOS (fail-closed, real quote volume)",
        "family": "liquidity_volatility_comovement_mean_reversion",
        "path": "R-B (validated real_quote_volume; no new blocked-family feed)",
        "oos_edge_proven": bool(n_edge > 0),
        "n_assets_tested": len(by_asset),
        "n_assets_with_exposure": n_exposed,
        "n_oos_edge_proven": n_edge,
        "pre_stated_hypothesis": (
            "cvr_z = zscore(rolling Pearson corr(qvol, |ret1|, W=48), ZLB=168) is a bivariate liquidity-volatility "
            "co-movement/dependence statistic (uses |ret1| jointly with qvol). Genuinely different from C23/C40/C41 "
            "vol_z level (univariate), C42 expansion, C43 unsloped vol_z divergence, C44 vol_z ROC, C45 Amihud "
            "|ret|/volume pointwise ratio, C46 OBV signed-cumulative slopes, C47 up/down partition imbalance, C48 "
            "rolling STD of qvol (2nd-moment), C49 rolling excess kurtosis (4th-moment), C50 rolling skewness "
            "(3rd-moment), C51 rolling lag-1 autocorrelation (serial dependence). Fade extreme positive co-movement "
            "shocks (cvr_z>=1.25): ret_W>0 -> SHORT, ret_W<0 -> LONG; extreme decoupling (cvr_z<=-1.25) -> no entry "
            "(pre-stated asymmetry). Exit cvr_z<0.25 or hold>=12h or flip. t->t+1 execution. WF 720/168/168, "
            "cost grid 0-40bps, B&H benchmark on same OOS windows. Edge iff exposure>0 AND all slices OOS net>0 AND >B&H."
        ),
        "config": {
            "spot_cache": SPOT_CACHE,
            "spot_meta": spot_meta,
            "spot_sha256": spot_sha,
            "volume_meta": str(VOL_META.relative_to(ROOT)),
            "volume_provenance": str(VOL_PROV.relative_to(ROOT)),
            "volume_validation": vol_report_safe,
            "cost_grid_bps_fee_slippage": COST_GRID,
            "wf": {"train": TRAIN, "test": TEST, "step": STEP},
            "params": PARAMS,
            "execution": "signal_t -> return_{t+1}",
        },
        "by_asset": by_asset,
        "honesty": {
            "real_data_only": True,
            "fabricated_data": False,
            "no_threshold_weakening": True,
            "pre_stated_before_oos": True,
            "edge_requires_all_slices_and_bh": True,
            "oos_edge_proven": bool(n_edge > 0),
            "conclusion": "no_oos_edge_proven_campaign52_fail_closed" if n_edge == 0 else "edge_claim_requires_review",
        },
    }
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    p = REPORTS_DIR / f"real_quote_volume_vol_absret_corr_shock_mean_reversion_costed_oos_{ts}.json"
    _write_json(p, out)
    print(json.dumps({"wrote": str(p), "oos_edge_proven": out["oos_edge_proven"], "n_edge": n_edge, "n_exposed": n_exposed}, indent=2))

if __name__ == "__main__":
    main()
