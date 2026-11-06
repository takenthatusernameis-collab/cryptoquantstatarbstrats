#!/usr/bin/env python3
"""Generate Campaign 49 artifacts.

Campaign 49 — Path R-B (fail-closed, real data only): a GENUINELY DIFFERENT
pre-stated hypothesis on validated real_quote_volume (Binance spot klines col 5),
NOT a rerun of C23 "Abnormal Quote Volume Momentum", NOT C40 "Quote Volume
Climax Mean Reversion / FADE", NOT C41 "Quote Volume Dry-Up Breakout
Continuation", NOT C42 "Volume-Expansion Breakout Confirmation Continuation",
NOT C43 "Quote Volume Divergence Reversion (Fade on Volume-Price Divergence)",
NOT C44 "Quote Volume Acceleration Trend Following (Volume-Z ROC Confirmation)",
NOT C45 "Illiquidity Shock Mean Reversion (Amihud Proxy on Real Quote Volume)",
NOT C46 "OBV-Price Slope Divergence Continuation", NOT C47 "Up-Down Quote
Volume Imbalance Exhaustion Mean Reversion", and NOT C48 "Volume-of-Volume Shock
Mean Reversion (Volatility-of-Liquidity Burst Fade)".

PRE-STATED HYPOTHESIS (fixed before seeing OOS results):
"Volume Kurtosis Shock Mean Reversion (Liquidity Tail-Fatness Burst Fade)"
- Compute rolling excess kurtosis (Fisher, 4th-moment tail-fatness) of real quote
  volume over a causal window W=24h: kurt = excess_kurtosis(qvol, W). Z-score
  kurt over ZLB=168h (causal): kurt_z = (kurt - mean(kurt,ZLB))/std(kurt,ZLB).
  This measures LIQUIDITY TAIL-FATNESS / spiky lumpiness of the volume
  distribution — a different transform from all prior campaigns:
    * C23/C40/C41 use vol_z LEVEL (first-moment volume z).
    * C42 uses volume expansion (vol_z level breakout confirmation).
    * C43 uses unsloped vol_z divergence at price extremes.
    * C44 uses vol_z ROC (first difference/acceleration of vol_z).
    * C45 uses Amihud |ret|/volume (price-impact ratio).
    * C46 uses OBV cumulative sign*vol slopes (integrated signed volume).
    * C47 uses up/down partition imbalance ratio of qvol by return sign.
    * C48 uses z-score of ROLLING STD of qvol (2nd-moment dispersion).
  kurt_z is a z-score of ROLLING EXCESS KURTOSIS of qvol — a distinct 4th-moment
  tail-shape transform (fat tails / spikiness), not dispersion magnitude.
- Entry (fade extreme tail-fatness burst, mean reversion): when kurt_z >= ENTRY_Z
  (extreme spiky/lumpy liquidity burst) AND recent price move ret_W > 0 -> SHORT
  (tail-fat burst during up-move tends to normalize/revert); kurt_z >= ENTRY_Z AND
  ret_W < 0 -> LONG. If kurt_z <= -ENTRY_Z (extreme platykurtic/uniform calm)
  no directional fade is taken (no entry) — asymmetry pre-stated to avoid
  over-trading uniform regimes.
- Exit: kurt_z < EXIT_Z OR hold >= MAX_HOLD_BARS (12h) OR signal flips. Else flat.
- Execution shift t -> t+1 (causal).
- Walk-forward: rolling 720/168/168. Cost grid: fee+slip bps pairs
  [[0,0],[5,0],[0,5],[5,5],[10,0],[0,10],[10,10],[20,0],[0,20],[20,20]] (0-40bps).
- Benchmark: buy-and-hold per asset on union of OOS WF windows (gross).
- Pre-stated edge rule (fail-closed): oos_edge_proven=true IFF executed exposure>0
  AND for ALL cost-grid slices OOS net sum > 0 AND OOS net sum > B&H OOS sum on
  same OOS windows. Else false. No in-sample tuning, no threshold weakening, no
  fabricated data/proxies.

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

logging.basicConfig(level=logging.INFO, format="%(asctime)s [campaign49] %(levelname)s %(message)s")
logger = logging.getLogger("campaign49")

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
    "kurt_window": 24,     # rolling window for excess kurtosis of volume
    "z_lookback": 168,
    "entry_z": 1.25,       # extreme tail-fatness (spiky liquidity) shock
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


def compute_kurtosis_shock_signal(close: pd.Series, vol: pd.Series, params: dict) -> pd.DataFrame:
    df = pd.DataFrame({"close": close.astype(float), "qvol": vol.astype(float)}).sort_index()
    df["ret1"] = df["close"].pct_change()
    w = int(params["kurt_window"])
    eps = float(params["eps"])
    # Excess kurtosis (Fisher): 4th-moment tail-fatness of real quote volume
    df["vkurt"] = df["qvol"].rolling(w, min_periods=w).kurt()
    df["kurt_z"] = _zscore(df["vkurt"], int(params["z_lookback"]), eps)
    df["ret_w"] = df["close"].pct_change(w)

    sig = np.zeros(len(df), dtype=float)
    raw = np.zeros(len(df), dtype=float)
    kz = df["kurt_z"].to_numpy()
    rw = df["ret_w"].to_numpy()
    entry = float(params["entry_z"])
    exit_z = float(params["exit_z"])
    mh = int(params["max_hold_bars"])

    for i in range(len(df)):
        if not (np.isfinite(kz[i]) and np.isfinite(rw[i])):
            continue
        # pre-stated asymmetry: only fade extreme tail-fatness (spiky liquidity) shocks
        if kz[i] >= entry and rw[i] > 0:
            raw[i] = -1.0  # fat-tailed burst during up-move -> fade short
        elif kz[i] >= entry and rw[i] < 0:
            raw[i] = 1.0   # fat-tailed burst during down-move -> fade long
        # kz <= -entry: extreme platykurtic/uniform -> no entry (pre-stated)

    hold = 0
    pos = 0.0
    for i in range(len(df)):
        desired = raw[i]
        norm = np.isfinite(kz[i]) and kz[i] < exit_z
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
    c, v = c.align(v, join="inner")
    if len(c) < PARAMS["min_obs"] + TRAIN + TEST:
        return {"error": "insufficient_aligned_obs", "n_obs": int(len(c)), "has_exposure": False, "oos_edge_proven": False}
    sdf = compute_kurtosis_shock_signal(c, v, PARAMS)
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
    elif isinstance(vol_df, dict):
        for k, v in vol_df.items():
            if isinstance(v, pd.Series):
                by_sym_vol[str(k)] = v.dropna()

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
        "type": "real_quote_volume_kurtosis_shock_mean_reversion_costed_oos",
        "campaign": 49,
        "generated_at_utc": stamp_iso,
        "computed_at_stamp": ts,
        "real_data_only": True,
        "fabricated_data": False,
        "fail_closed": True,
        "no_threshold_weakening": True,
        "no_proxies_labeled_real": True,
        "path": "R-B",
        "pre_stated_hypothesis": {
            "name": "Volume Kurtosis Shock Mean Reversion (Liquidity Tail-Fatness Burst Fade)",
            "description": (
                "Compute rolling excess kurtosis (Fisher, 4th-moment) of real quote volume over 24h, "
                "z-score over 168h (causal) -> kurt_z. Fade extreme tail-fatness/spiky liquidity shocks: "
                "kurt_z >= 1.25 and ret_W>0 -> SHORT; kurt_z >= 1.25 and ret_W<0 -> LONG. "
                "Extreme platykurtic calm (kurt_z <= -1.25) -> no entry (pre-stated asymmetry). "
                "Exit on kurt_z < 0.25, max hold 12h, or flip. Execution t->t+1. "
                "WF 720/168/168, cost grid 0-40bps, B&H benchmark on same OOS windows."
            ),
            "params_fixed_before_oos_evaluation": True,
            "no_in_sample_tuning": True,
            "differs_from_c23": "C23 trades high vol_z LEVEL (first-moment volume z) momentum continuation; C49 uses z-score of rolling EXCESS KURTOSIS of qvol (4th-moment tail-fatness) as a shock fade.",
            "differs_from_c40": "C40 fades HIGH volume climax on aggregate vol_z level; C49 fades TAIL-FATNESS (kurtosis) of volume — different transform (4th moment shape, not volume level).",
            "differs_from_c41": "C41 continues on LOW vol_z dry-up breakout; C49 mean-reverts on extreme volume tail-fatness shocks (high kurt_z).",
            "differs_from_c42": "C42 confirms breakouts on volume expansion (level); C49 uses volume kurtosis (tail shape) shock fade, no breakout/expansion confirmation.",
            "differs_from_c43": "C43 fades volume-price divergence using unsloped vol_z at price extremes; C49 uses kurt_z (tail-fatness of volume) shock with ret_W confirmation — different transform and trigger.",
            "differs_from_c44": "C44 trend-follows on vol_z ROC acceleration; C49 mean-reverts on extreme kurt_z tail-fatness shocks, no ROC/acceleration.",
            "differs_from_c45": "C45 mean-reverts on Amihud illiquidity shocks (|ret|/volume, price-impact ratio); C49 uses rolling excess kurtosis of qvol (tail shape), not a price-impact ratio.",
            "differs_from_c46": "C46 continues on OBV (cumulative sign*vol) slope divergence vs price slope; C49 uses kurt_z tail-fatness shock fade — different transform (4th moment vs OBV slopes) and opposite mechanic.",
            "differs_from_c47": "C47 uses up/down volume split imbalance ratio (directional partitioned sums) exhaustion fade; C49 uses rolling excess kurtosis of total qvol (undirected tail-shape/4th moment) — different construction.",
            "differs_from_c48": "C48 uses z-score of rolling STD of qvol (2nd-moment dispersion/volatility-of-liquidity); C49 uses z-score of rolling EXCESS KURTOSIS of qvol (4th-moment tail-fatness/spikiness) — distinct higher-moment statistic measuring tail shape, not dispersion magnitude.",
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
    out_name = REPORTS_DIR / f"real_quote_volume_kurtosis_shock_mean_reversion_costed_oos_{ts}.json"
    _write_json(out_name, out)
    logger.info("wrote %s (oos_edge_proven=%s)", out_name, out["summary"]["oos_edge_proven"])
    print(json.dumps({"wrote": str(out_name), "summary": out["summary"]}))


if __name__ == "__main__":
    main()
