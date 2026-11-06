#!/usr/bin/env python3
"""Generate Campaign 46 artifacts.

Campaign 46 — Path R-B (fail-closed, real data only): a GENUINELY DIFFERENT
pre-stated hypothesis on validated real_quote_volume (Binance spot klines col 5),
NOT a rerun of C23 "Abnormal Quote Volume Momentum", NOT C40 "Quote Volume
Climax Mean Reversion / FADE", NOT C41 "Quote Volume Dry-Up Breakout
Continuation", NOT C42 "Volume-Expansion Breakout Confirmation Continuation",
NOT C43 "Quote Volume Divergence Reversion (Fade on Volume-Price Divergence)",
NOT C44 "Quote Volume Acceleration Trend Following (Volume-Z ROC Confirmation)",
and NOT C45 "Illiquidity Shock Mean Reversion (Amihud Proxy on Real Quote Volume)".

PRE-STATED HYPOTHESIS (fixed before seeing OOS results):
"OBV-Price Slope Divergence Continuation (Accumulation/Distribution Proxy on Real Quote Volume)"
- Build a causal On-Balance Quote Volume proxy: OBV(t) = cumsum(sign(ret1(t)) * quote_volume_usdt(t)),
  using real quote volume signed by contemporaneous return direction (Wyckoff-style accumulation proxy).
  This is an INTEGRATED signed-volume measure — fundamentally different from vol_z level (C23/C40/C41),
  vol_z extremes/divergence (C43), vol_z ROC acceleration (C44), and |ret|/volume illiquidity ratio (C45).
- Compute causal rolling slopes (lookback SLOPE_LB=24h): obv_slope = zscore of OBV.diff(SLOPE_LB) over
  ZLB=168h; price_slope = zscore of close.pct_change(SLOPE_LB) over ZLB=168h.
- Entry (divergence continuation / hidden accumulation-distribution): when slopes diverge with sufficient
  magnitude (|obv_slope|>=ENTRY_Z and |price_slope|>=ENTRY_Z and signs differ):
  * obv_slope > 0 and price_slope < 0 (accumulation while price falling) -> LONG continuation.
  * obv_slope < 0 and price_slope > 0 (distribution while price rising) -> SHORT continuation.
- Exit: when slopes realign (same sign) OR |obv_slope| < EXIT_Z OR hold >= MAX_HOLD_BARS (12h)
  OR signal flips. Else flat.
- Execution shift t -> t+1 (causal).
- Walk-forward: rolling 720/168/168. Cost grid: fee+slip bps pairs
  [[0,0],[5,0],[0,5],[5,5],[10,0],[0,10],[10,10],[20,0],[0,20],[20,20]] (0-40bps).
- Benchmark: buy-and-hold per asset on union of OOS WF windows (gross).
- Pre-stated edge rule (fail-closed): oos_edge_proven=true IFF executed exposure>0 AND for
  ALL cost-grid slices OOS net sum > 0 AND OOS net sum > B&H OOS sum on same OOS windows.
  Else false. No in-sample tuning, no threshold weakening, no fabricated data/proxies.

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

logging.basicConfig(level=logging.INFO, format="%(asctime)s [campaign46] %(levelname)s %(message)s")
logger = logging.getLogger("campaign46")

CACHE_DIR = ROOT / "data" / "cache"
REPORTS_DIR = ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

SPOT_CACHE = "0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7"
VOL_META = CACHE_DIR / "volume_1h_full.meta.json"
VOL_PROV = CACHE_DIR / "volume_1h_full.provenance.json"
COST_GRID = [[0, 0], [5, 0], [0, 5], [5, 5], [10, 0], [0, 10], [10, 10], [20, 0], [0, 20], [20, 20]]
TRAIN, TEST, STEP = 720, 168, 168
# Fixed before OOS evaluation (pre-stated)
PARAMS = {
    "slope_lb": 24,
    "z_lookback": 168,
    "entry_z": 1.25,
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


def compute_obv_div_signal(close: pd.Series, vol: pd.Series, params: dict) -> pd.DataFrame:
    df = pd.DataFrame({"close": close.astype(float), "qvol": vol.astype(float)}).sort_index()
    df["ret1"] = df["close"].pct_change()
    obv = (np.sign(df["ret1"].fillna(0.0)) * df["qvol"].fillna(0.0)).cumsum()
    slb = int(params["slope_lb"])
    zlb = int(params["z_lookback"])
    eps = float(params["eps"])
    obv_slope = obv.diff(slb)
    price_slope = df["close"].pct_change(slb)
    df["obv_z"] = _zscore(obv_slope, zlb, eps)
    df["px_z"] = _zscore(price_slope, zlb, eps)

    sig = np.zeros(len(df), dtype=float)
    raw = np.zeros(len(df), dtype=float)
    oz = df["obv_z"].to_numpy()
    pz = df["px_z"].to_numpy()
    entry = float(params["entry_z"])
    exit_z = float(params["exit_z"])
    mh = int(params["max_hold_bars"])

    for i in range(len(df)):
        if not (np.isfinite(oz[i]) and np.isfinite(pz[i])):
            continue
        if abs(oz[i]) >= entry and abs(pz[i]) >= entry and np.sign(oz[i]) != np.sign(pz[i]):
            # accumulation (OBV up, price down) -> long; distribution -> short
            raw[i] = 1.0 if oz[i] > 0 else -1.0

    hold = 0
    pos = 0.0
    for i in range(len(df)):
        desired = raw[i]
        realign = np.isfinite(oz[i]) and np.isfinite(pz[i]) and np.sign(oz[i]) == np.sign(pz[i])
        weak = np.isfinite(oz[i]) and abs(oz[i]) < exit_z
        if pos != 0.0:
            hold += 1
            flip = desired != 0.0 and desired != pos
            if realign or weak or hold >= mh or flip:
                if flip and desired != 0.0:
                    pos = desired
                    hold = 0
                elif not (flip and desired != 0.0):
                    # if a new divergent signal exists now (desired same sign handled by non-flip), reset/exit
                    if desired == pos and desired != 0.0:
                        pos = desired
                    else:
                        pos = 0.0
                        hold = 0
                        if desired != 0.0 and flip is False:
                            pos = desired
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
    c, v = c.align(v, join="inner")
    if len(c) < PARAMS["min_obs"] + TRAIN + TEST:
        return {"error": "insufficient_aligned_obs", "n_obs": int(len(c)), "has_exposure": False, "oos_edge_proven": False}
    sdf = compute_obv_div_signal(c, v, PARAMS)
    sig = sdf["signal"].to_numpy(dtype=float)
    ret = sdf["ret1"].fillna(0.0).to_numpy(dtype=float)
    gross = sig * ret
    turn = np.abs(np.diff(np.r_[0.0, sig]))
    bh_ret = sdf["ret1"].fillna(0.0).to_numpy(dtype=float)
    n = len(sdf)
    ws = wf_splits(n)
    if not ws:
        return {"error": "no_wf_splits", "n_obs": int(n), "has_exposure": False, "oos_edge_proven": False}
    cost_slices = {}
    for fee_b, slip_b in COST_GRID:
        cost = (fee_b + slip_b) / 10000.0
        net = gross - turn * cost
        oos_mask = np.zeros(n, dtype=bool)
        for _tr_s, _tr_e, te_e in ws:
            oos_mask[te_e - TEST : te_e] = True
        net_oos = net[oos_mask]
        gross_oos = gross[oos_mask]
        turn_oos = turn[oos_mask]
        bh_oos = bh_ret[oos_mask]
        n_tr = int(turn_oos.sum())
        cost_slices[f"fee{fee_b}_slip{slip_b}_bps"] = {
            "n_obs": int(n),
            "n_oos_obs": int(oos_mask.sum()),
            "n_windows": len(ws),
            "wf_train": TRAIN,
            "wf_test": TEST,
            "wf_step": STEP,
            "gross_oos_sum": float(gross_oos.sum()),
            "net_oos_sum": float(net_oos.sum()),
            "turnover_oos_count": n_tr,
            "turnover_oos_rate": float(n_tr / max(1, int(oos_mask.sum()))),
            "bh_gross_oos_sum": float(bh_oos.sum()),
            "bh_oos_sum": float(bh_oos.sum()),
            "oos_net_gt_zero": bool(float(net_oos.sum()) > 0.0),
            "oos_net_beat_bh": bool(float(net_oos.sum()) > float(bh_oos.sum())),
            "has_exposure": bool(float(np.abs(sig[oos_mask]).sum()) > 0.0),
        }
    all_pos = all(cost_slices[f"fee{f}_slip{s}_bps"]["oos_net_gt_zero"] for f, s in COST_GRID)
    all_bh = all(cost_slices[f"fee{f}_slip{s}_bps"]["oos_net_beat_bh"] for f, s in COST_GRID)
    exp = bool(float(np.abs(sig).sum()) > 0.0)
    edge = bool(exp and all_pos and all_bh)
    return {"n_obs": int(n), "has_exposure": exp, "cost_slices": cost_slices, "oos_edge_proven": edge}


def main() -> None:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    stamp_iso = datetime.now(timezone.utc).isoformat()
    spot_df, spot_meta, spot_sha = load_spot()
    vol_df, vol_report = load_volume()

    by_sym_spot: dict[str, pd.Series] = {}
    for c in spot_df.columns:
        s = spot_df[c].dropna()
        if len(s) > 0:
            by_sym_spot[str(c)] = s

    # vol_df is long-format validated DataFrame
    by_sym_vol: dict[str, pd.Series] = {}
    if isinstance(vol_df, pd.DataFrame) and {"symbol", "quote_volume_usdt"}.issubset(vol_df.columns):
        for sym, g in vol_df.groupby("symbol"):
            s = pd.Series(g["quote_volume_usdt"].to_numpy(), index=pd.to_datetime(g["timestamp_utc"], utc=True, errors="coerce")).dropna()
            s = s[~s.index.isna()].sort_index()
            if len(s) > 0:
                by_sym_vol[str(sym)] = s
    elif isinstance(vol_df, pd.DataFrame):
        for c in vol_df.columns:
            s = vol_df[c].dropna()
            if len(s) > 0:
                by_sym_vol[str(c)] = s

    syms = sorted(set(by_sym_spot) & set(by_sym_vol))
    results = {}
    for sym in syms:
        try:
            results[sym] = run_asset(by_sym_spot[sym], by_sym_vol[sym])
        except Exception as exc:
            logger.warning("asset %s failed: %s", sym, exc)
            results[sym] = {"error": str(exc), "oos_edge_proven": False, "has_exposure": False}

    n_edge = sum(1 for v in results.values() if isinstance(v, dict) and v.get("oos_edge_proven"))
    n_exp = sum(1 for v in results.values() if isinstance(v, dict) and v.get("has_exposure"))
    out = {
        "type": "real_quote_volume_obv_price_slope_divergence_costed_oos",
        "campaign": 46,
        "generated_at_utc": stamp_iso,
        "computed_at_stamp": ts,
        "real_data_only": True,
        "fabricated_data": False,
        "fail_closed": True,
        "no_threshold_weakening": True,
        "no_proxies_labeled_real": True,
        "path": "R-B",
        "pre_stated_hypothesis": {
            "name": "OBV-Price Slope Divergence Continuation (Accumulation/Distribution Proxy on Real Quote Volume)",
            "description": (
                "Build causal OBV proxy OBV=cumsum(sign(ret1)*quote_volume_usdt) (integrated signed volume). "
                "Compute z-scored slopes over 24h (z lookback 168h) for OBV and price. "
                "When slopes diverge with magnitude (|obv_z|,|px_z|>=1.25, opposite signs): "
                "OBV up + price down -> LONG (accumulation continuation); OBV down + price up -> SHORT. "
                "Exit on realignment, weak OBV slope, max hold 12h, or flip. Execution t->t+1. "
                "WF 720/168/168, cost grid 0-40bps, B&H benchmark on same OOS windows."
            ),
            "params_fixed_before_oos_evaluation": True,
            "no_in_sample_tuning": True,
            "differs_from_c23": "C23 uses high vol_z LEVEL for momentum continuation; C46 uses integrated signed volume (OBV) slope divergence.",
            "differs_from_c40": "C40 fades HIGH volume climax (vol_z level); C46 uses OBV (sign(ret)*volume cumulative) slope vs price slope divergence — different construction.",
            "differs_from_c41": "C41 continues on LOW vol_z dry-up breakout; C46 trades OBV-price slope divergences (accumulation/distribution), no dry-up/breakout condition.",
            "differs_from_c42": "C42 confirms breakouts on volume expansion (rising vol_z); C46 uses signed integrated volume OBV slope, not expansion confirmation.",
            "differs_from_c43": "C43 fades volume-price DIVERGENCE using vol_z (unsloped volume level z at price extremes) as a reversion fade; C46 uses OBV slope (integrated signed flow) vs price slope divergence as a CONTINUATION of hidden accumulation/distribution with different signal math (slope z-scores, opposite trade intent framing).",
            "differs_from_c44": "C44 trend-follows on vol_z ROC acceleration; C46 uses OBV cumulative signed-volume slope divergence, not volume acceleration.",
            "differs_from_c45": "C45 mean-reverts on illiquidity SHOCKS (|ret|/volume Amihud ratio z-score); C46 uses signed volume integration OBV vs price slopes — different transform and mechanic.",
            **PARAMS,
        },
        "data": {
            "spot_cache": SPOT_CACHE,
            "spot_cache_sha256_pkl": spot_sha,
            "spot_meta": spot_meta,
            "volume_meta_path": str(VOL_META),
            "volume_provenance_path": str(VOL_PROV),
            "volume_validation_report_ok": bool(vol_report.get("ok")) if isinstance(vol_report, dict) else False,
            "real_quote_volume_validated": True,
        },
        "config": {
            "train_test_step": [TRAIN, TEST, STEP],
            "cost_grid_bps_fee_slippage": COST_GRID,
            "benchmark": "buy_and_hold_same_oos_windows",
            "execution_shift": "t->t+1",
            "causal_windows_only": True,
        },
        "symbols_tested": sorted(syms),
        "by_asset": results,
        "summary": {
            "n_symbols_tested": len(syms),
            "n_assets_with_exposure": n_exp,
            "n_oos_edge_proven": n_edge,
            "oos_edge_proven": bool(n_edge > 0 and n_edge == n_exp and n_exp > 0),
            "edge_rule": "exposure>0 AND all cost-grid slices OOS net>0 AND OOS net>B&H on same OOS windows (pre-stated, fail-closed)",
        },
        "_source_files": {"generator": str(Path(__file__).relative_to(ROOT))},
    }
    out_name = REPORTS_DIR / f"real_quote_volume_obv_price_slope_divergence_costed_oos_{ts}.json"
    _write_json(out_name, out)
    logger.info("wrote %s (oos_edge_proven=%s)", out_name, out["summary"]["oos_edge_proven"])
    print(json.dumps({"wrote": str(out_name), "summary": out["summary"]}))


if __name__ == "__main__":
    main()
