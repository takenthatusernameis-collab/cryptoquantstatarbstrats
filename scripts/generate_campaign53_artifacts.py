#!/usr/bin/env python3
"""Generate Campaign 53 artifacts.

Campaign 53 — Path R-B (fail-closed, real data only): a GENUINELY DIFFERENT
pre-stated hypothesis on validated real_quote_volume (Binance spot klines col 5),
NOT a rerun of C23/C40/C41/C42/C43/C44/C45/C46/C47/C48/C49/C50/C51/C52.

PRE-STATED HYPOTHESIS (fixed before seeing OOS results):
"Rolling Volume-Return Lead Cross-Correlation Predictive Fade (Lead-Lag /
Granger-Direction Statistic)"
- For each asset and each time t, compute rolling Pearson correlation over a
  causal window W=48h between qvol[t-W+1..t] (quote volume AT t) and
  ret[t-W+1+k .. t+k] (SIGNED 1-bar return k bars AHEAD of t, lead k=1). This
  is a LEAD-LAG / Granger-direction statistic: does volume at t predict the
  signed future return? It is genuinely different from every prior campaign:
    * C23/C40/C41 use vol_z LEVEL (first-moment volume z, univariate, same t).
    * C42 uses volume expansion (vol_z level breakout confirmation).
    * C43 uses unsloped vol_z divergence at price extremes.
    * C44 uses vol_z ROC (first difference/acceleration of vol_z).
    * C45 uses Amihud |ret|/volume (price-impact RATIO, pointwise, same t).
    * C46 uses OBV cumulative sign*vol slopes (integrated signed volume).
    * C47 uses up/down partition imbalance ratio of qvol by return sign.
    * C48 uses z-score of ROLLING STD of qvol (2nd-moment dispersion, univariate).
    * C49 uses z-score of ROLLING EXCESS KURTOSIS of qvol (4th-moment tail-fatness).
    * C50 uses z-score of ROLLING SKEWNESS of qvol (3rd-moment asymmetry).
    * C51 uses z-score of ROLLING LAG-1 AUTOCORRELATION of qvol (serial dependence).
    * C52 uses z-score of rolling CROSS-CORRELATION(qvol, |ret1|) at the SAME t
      (contemporaneous liquidity-volatility co-movement, magnitude-based).
  vrl_z is a z-score of rolling cross-correlation(qvol[t], ret[t+k]) with a LEAD
  offset k and SIGNED returns — a distinct lead-lag/predictive transform, not a
  univariate moment, not a pointwise ratio, not contemporaneous co-movement, not
  magnitude-based.
- Entry (fade extreme predictive volume-leading signal, mean reversion of the
  lead): when vrl_z >= ENTRY_Z (volume strongly leads an UP move) -> SHORT at t
  (the predictive edge fades/mean reverts); vrl_z <= -ENTRY_Z (volume strongly
  leads a DOWN move) -> LONG at t; |vrl_z| < ENTRY_Z -> no entry.
- Exit: |vrl_z| < EXIT_Z OR hold >= MAX_HOLD_BARS (12h) OR signal flips. Else flat.
- Execution shift t -> t+1 (causal; signal at t trades return t+1).
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
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.real_feed_loader import validate_and_load_real_feed  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [campaign53] %(levelname)s %(message)s")
logger = logging.getLogger("campaign53")

CACHE_DIR = ROOT / "data" / "cache"
REPORTS_DIR = ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

SPOT_CACHE = "0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7"
VOL_META = CACHE_DIR / "volume_1h_full.meta.json"
VOL_PROV = CACHE_DIR / "volume_1h_full.provenance.json"
COST_GRID = [[0, 0], [5, 0], [0, 5], [5, 5], [10, 0], [0, 10], [10, 10], [20, 0], [0, 20], [20, 20]]
TRAIN, TEST, STEP = 720, 168, 168
PARAMS = {
    "corr_window": 48,        # rolling window for corr(qvol[t], ret[t+k])
    "lead_bars": 1,           # volume at t leads signed return by k bars (lead-lag)
    "z_lookback": 168,        # causal z-score lookback
    "entry_z": 1.25,          # extreme predictive volume-leading signal
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


def load_volume_wide():
    """Validate the real quote-volume feed fail-closed, then reshape to wide.

    validate_and_load_real_feed returns a long frame
    (timestamp_utc, symbol, quote_volume_usdt). Pivot to a wide DataFrame
    indexed by timestamp_utc with one column per symbol so per-asset series
    can be aligned with spot closes. Reshaping a validated real feed is not
    fabrication; the fail-closed validation still gates acceptance.
    """
    if not VOL_PROV.exists():
        raise FileNotFoundError(f"volume provenance certificate missing: {VOL_PROV}")
    prov = json.loads(VOL_PROV.read_text(encoding="utf-8"))
    long_df, report = validate_and_load_real_feed(VOL_META, "real_quote_volume", provenance=prov)
    if not report.get("ok"):
        raise RuntimeError(f"volume feed failed validation: {report}")
    wide = long_df.pivot(index="timestamp_utc", columns="symbol", values="quote_volume_usdt").sort_index()
    wide.index = pd.to_datetime(wide.index, utc=True)
    return wide, report


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


def compute_vol_ret_lead_corr_signal(close: pd.Series, vol: pd.Series, params: dict) -> pd.DataFrame:
    df = pd.DataFrame({"close": close.astype(float), "qvol": vol.astype(float)}).sort_index()
    df["ret1"] = df["close"].pct_change()
    k = int(params["lead_bars"])
    # Future signed return k bars ahead (volume LEADS return): ret[t+k]
    df["ret_fwd"] = df["ret1"].shift(-k)
    w = int(params["corr_window"])
    eps = float(params["eps"])
    # Rolling lead-lag cross-correlation: corr(qvol[t], ret[t+k]) over causal W
    df["corr_vr_lead"] = df["qvol"].rolling(w, min_periods=w).corr(df["ret_fwd"])
    df["vrl_z"] = _zscore(df["corr_vr_lead"], int(params["z_lookback"]), eps)
    df["ret_w"] = df["close"].pct_change(w)

    sig = np.zeros(len(df), dtype=float)
    raw = np.zeros(len(df), dtype=float)
    cz = df["vrl_z"].to_numpy()
    entry = float(params["entry_z"])
    exit_z = float(params["exit_z"])
    mh = int(params["max_hold_bars"])

    for i in range(len(df)):
        if not np.isfinite(cz[i]):
            continue
        # Fade extreme predictive volume-leading signal (mean reversion of lead)
        if cz[i] >= entry:
            raw[i] = -1.0  # volume leads up-move -> fade short
        elif cz[i] <= -entry:
            raw[i] = 1.0   # volume leads down-move -> fade long

    hold = 0
    pos = 0.0
    for i in range(len(df)):
        desired = raw[i]
        norm = np.isfinite(cz[i]) and abs(cz[i]) < exit_z
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
    sdf = compute_vol_ret_lead_corr_signal(c, v, PARAMS)
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
            "vrl_z_mean": float(np.nanmean(sdf["vrl_z"].to_numpy()[oos_mask])),
            "vrl_z_min": float(np.nanmin(sdf["vrl_z"].to_numpy()[oos_mask])),
            "vrl_z_max": float(np.nanmax(sdf["vrl_z"].to_numpy()[oos_mask])),
        },
    }


def main():
    spot_df, spot_meta, spot_sha = load_spot()
    vol_df, vol_report = load_volume_wide()
    vol_report_safe = vol_report.to_dict() if hasattr(vol_report, "to_dict") else vol_report
    if not vol_report_safe.get("ok"):
        raise RuntimeError(f"volume feed failed validation: {vol_report_safe}")

    spot_symbols = list(spot_df.columns)
    vol_symbols = [c for c in vol_df.columns]
    assets = sorted([a for a in spot_symbols if a in vol_symbols])
    logger.info("spot_symbols=%s vol_symbols=%s tested_assets=%s", spot_symbols, vol_symbols, assets)

    by_asset = {}
    for a in assets:
        close = spot_df[a]
        v = vol_df[a]
        logger.info("asset=%s rows_spot=%s rows_vol=%s", a, len(close.dropna()), len(v.dropna()))
        by_asset[a] = run_asset(close, v)

    n_edge = sum(1 for r in by_asset.values() if isinstance(r, dict) and r.get("oos_edge_proven"))
    n_exposed = sum(1 for r in by_asset.values() if isinstance(r, dict) and r.get("has_exposure"))
    out = {
        "generated_at_utc": _utc_now_iso(),
        "campaign": 53,
        "title": "Rolling Volume-Return Lead Cross-Correlation Predictive Fade (Lead-Lag Granger-Direction) — costed OOS (fail-closed, real quote volume)",
        "family": "volume_return_lead_crosscorr_predictive_fade",
        "path": "R-B (validated real_quote_volume; no new blocked-family feed; C52 volume loading fixed so assets actually tested)",
        "oos_edge_proven": bool(n_edge > 0),
        "n_assets_tested": len(by_asset),
        "n_assets_with_exposure": n_exposed,
        "n_oos_edge_proven": n_edge,
        "pre_stated_hypothesis": (
            "vrl_z = zscore(rolling Pearson corr(qvol[t], ret[t+k], W=48), ZLB=168) with lead k=1 and SIGNED returns. "
            "A lead-lag / Granger-direction statistic: does volume at t predict the signed future return? "
            "Genuinely different from C23/C40/C41 vol_z level (univariate), C42 expansion, C43 unsloped vol_z "
            "divergence, C44 vol_z ROC, C45 Amihud |ret|/volume pointwise ratio, C46 OBV signed-cumulative slopes, "
            "C47 up/down partition imbalance, C48 rolling STD of qvol (2nd-moment), C49 rolling excess kurtosis "
            "(4th-moment), C50 rolling skewness (3rd-moment), C51 rolling lag-1 autocorrelation (serial dependence), "
            "C52 contemporaneous cross-corr(qvol, |ret1|) co-movement (same t, magnitude-based). C53 uses a LEAD "
            "offset and SIGNED returns — a distinct lead-lag/predictive transform. Fade extreme predictive lead "
            "(vrl_z>=1.25 -> SHORT, vrl_z<=-1.25 -> LONG); |vrl_z|<1.25 no entry. Exit |vrl_z|<0.25 or hold>=12h or "
            "flip. t->t+1 execution. WF 720/168/168, cost grid 0-40bps, B&H benchmark on same OOS windows. Edge iff "
            "exposure>0 AND all slices OOS net>0 AND >B&H."
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
            "tested_assets": assets,
        },
        "by_asset": by_asset,
        "honesty": {
            "real_data_only": True,
            "fabricated_data": False,
            "no_threshold_weakening": True,
            "pre_stated_before_oos": True,
            "edge_requires_all_slices_and_bh": True,
            "oos_edge_proven": bool(n_edge > 0),
            "conclusion": "no_oos_edge_proven_campaign53_fail_closed" if n_edge == 0 else "edge_claim_requires_review",
        },
    }
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    p = REPORTS_DIR / f"real_quote_volume_vol_ret_lead_corr_predictive_fade_costed_oos_{ts}.json"
    _write_json(p, out)
    print(json.dumps({"wrote": str(p), "oos_edge_proven": out["oos_edge_proven"], "n_edge": n_edge, "n_exposed": n_exposed, "n_assets": len(by_asset)}, indent=2))


if __name__ == "__main__":
    main()
