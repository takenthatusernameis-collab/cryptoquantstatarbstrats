#!/usr/bin/env python3
"""Generate Campaign 44 artifacts.

Campaign 44 — Path R-B (fail-closed, real data only): a GENUINELY DIFFERENT
pre-stated hypothesis on validated real_quote_volume (Binance spot klines col 5),
NOT a rerun of C23 "Abnormal Quote Volume Momentum", NOT C40 "Quote Volume
Climax Mean Reversion / FADE", NOT C41 "Quote Volume Dry-Up Breakout Continuation",
NOT C42 "Volume-Expansion Breakout Confirmation Continuation", and NOT C43
"Quote Volume Divergence Reversion (Fade on Volume-Price Divergence)".

PRE-STATED HYPOTHESIS (fixed before seeing OOS results):
"Quote Volume Acceleration Trend Following (Volume-Z ROC Confirmation)"
- For each asset compute causal rolling z-score of quote_volume_usdt (lookback ZVOL=168h).
- Compute volume acceleration as rate-of-change of vol_z: volz_roc = vol_z(t) - vol_z(t-ROC_LAG)
  (ROC_LAG=12 bars). This captures *acceleration* of volume flow (second-order / delta of
  normalized volume), not the level of vol_z itself.
- Entry (trend following on acceleration): if volz_roc > ROC_THRESH (volume accelerating)
  AND ret24 > RET24_MIN (price trend aligned up) -> LONG. If volz_roc > ROC_THRESH and
  ret24 < -RET24_MIN -> SHORT. Requires acceleration to be rising into the trend direction.
- Exit: when volz_roc < ROC_EXIT (acceleration fades/reverses), or max hold MAX_HOLD_BARS,
  or if position opposes new acceleration signal.
- Execution shift t -> t+1 (causal).
- Walk-forward: rolling 720/168/168. Cost grid: fee+slip bps pairs
  [[0,0],[5,0],[0,5],[5,5],[10,0],[0,10],[10,10],[20,0],[0,20],[20,20]] (0-40bps).
- Benchmark: buy-and-hold per asset on union of OOS WF windows (gross).
- Pre-stated edge rule (fail-closed): oos_edge_proven=true IFF executed exposure>0 AND for
  ALL cost-grid slices OOS net sum > 0 AND OOS net sum > B&H OOS sum on same OOS windows.
  Else false. No in-sample tuning, no threshold weakening, no fabricated data/proxies.

How this differs from prior hypotheses (genuinely different mechanic):
- C23 (momentum): enters on HIGH vol_z level (surge) -> continuation. C44 uses vol_z ROC
  (acceleration/delta), not level; can trigger at moderate vol_z if accelerating.
- C40 (climax mean reversion): fades on HIGH vol_z climax. C44 follows trend on acceleration.
- C41 (dry-up breakout continuation): enters on LOW vol_z dry-up + price breakout continuation.
  C44 requires positive volume acceleration aligned with trend (opposite regime to dry-up).
- C42 (volume-expansion breakout confirmation continuation): confirms price breakout with
  rising vol_z/expansion above threshold. C44 uses ROC of vol_z as the signal with trend
  alignment (ret24) and no breakout/extreme condition.
- C43 (divergence reversion fade): fades new price extremes when volume confirmation is WEAK
  (vol_z < 0.5). C44 follows trend when volume is accelerating (positive ROC), not fading.
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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [campaign44] %(levelname)s %(message)s",
)
logger = logging.getLogger("campaign44")

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
    "zvol_lookback": 168,
    "roc_lag": 12,
    "roc_thresh": 0.5,       # volume acceleration threshold (delta z per 12 bars)
    "roc_exit": 0.0,         # exit when acceleration fades below 0
    "ret24_min": 0.005,      # minimum 24h trend alignment (0.5%)
    "max_hold_bars": 24,
    "min_vol_obs": 168,
}
NAMED = ["BTC", "ETH", "SOL", "BNB"]


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
    path.write_text(
        json.dumps(_json_safe(obj), indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def wf_windows(n: int) -> list[tuple[int, int, int]]:
    ws: list[tuple[int, int, int]] = []
    st = 0
    while st + TRAIN + TEST <= n:
        ws.append((st, st + TRAIN, st + TRAIN + TEST))
        st += STEP
    return ws


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


def _extract_vol_series(vol_df: Any) -> dict[str, pd.Series]:
    by_sym_vol: dict[str, pd.Series] = {}
    if isinstance(vol_df, pd.DataFrame):
        if (
            "symbol" in vol_df.columns
            and "quote_volume_usdt" in vol_df.columns
            and "timestamp_utc" in vol_df.columns
        ):
            for sym, g in vol_df.groupby("symbol"):
                ts = pd.to_datetime(g["timestamp_utc"], utc=True, errors="coerce")
                ser = pd.Series(g["quote_volume_usdt"].values, index=ts).sort_index()
                by_sym_vol[str(sym)] = ser
        elif "timestamp_utc" in vol_df.columns:
            ts = pd.to_datetime(vol_df["timestamp_utc"], utc=True, errors="coerce")
            for c in vol_df.columns:
                if c in ("timestamp_utc", "symbol"):
                    continue
                by_sym_vol[str(c)] = pd.Series(vol_df[c].values, index=ts).sort_index()
        else:
            for c in vol_df.columns:
                s = vol_df[c].dropna()
                if len(s) > 0:
                    by_sym_vol[str(c)] = pd.to_numeric(s, errors="coerce")
    elif isinstance(vol_df, dict):
        for k, v in vol_df.items():
            if isinstance(v, pd.Series):
                by_sym_vol[str(k)] = pd.to_numeric(v, errors="coerce")
            elif isinstance(v, pd.DataFrame) and "quote_volume_usdt" in v.columns:
                if "timestamp_utc" in v.columns:
                    ts = pd.to_datetime(v["timestamp_utc"], utc=True, errors="coerce")
                    by_sym_vol[str(k)] = pd.Series(v["quote_volume_usdt"].values, index=ts)
                else:
                    by_sym_vol[str(k)] = pd.to_numeric(v["quote_volume_usdt"], errors="coerce")
    return by_sym_vol


def run_asset(prices: pd.Series, vol: pd.Series) -> dict[str, Any]:
    # align on common timestamps
    p = pd.to_numeric(prices, errors="coerce")
    v = pd.to_numeric(vol, errors="coerce")
    idx = p.index.intersection(v.index)
    p = p.reindex(idx).astype(float)
    v = v.reindex(idx).astype(float)
    mask = p.notna() & v.notna() & (v > 0)
    p = p[mask]
    v = v[mask]
    n = len(p)
    if n < TRAIN + TEST + 50:
        return {"n_obs": int(n), "has_exposure": False, "oos_edge_proven": False,
                "insufficient_data": True, "cost_slices": {}}
    ret = p.pct_change().fillna(0.0).to_numpy(dtype=float)
    ret24 = p.pct_change(24).to_numpy(dtype=float)
    vv = v.to_numpy(dtype=float)
    vmean = pd.Series(vv).rolling(PARAMS["zvol_lookback"], min_periods=PARAMS["min_vol_obs"]).mean().to_numpy()
    vstd = pd.Series(vv).rolling(PARAMS["zvol_lookback"], min_periods=PARAMS["min_vol_obs"]).std(ddof=0).to_numpy()
    with np.errstate(divide="ignore", invalid="ignore"):
        volz = np.where((vstd > 1e-18) & np.isfinite(vstd), (vv - vmean) / vstd, np.nan)
    volz_lag = pd.Series(volz).shift(PARAMS["roc_lag"]).to_numpy()
    with np.errstate(invalid="ignore"):
        volz_roc = volz - volz_lag

    sig = np.zeros(n)
    cur = 0.0
    hold = 0
    warm = int(max(PARAMS["zvol_lookback"], PARAMS["roc_lag"]) + 30)
    for i in range(warm, n):
        roc = volz_roc[i]
        r24 = ret24[i]
        if not np.isfinite(roc) or not np.isfinite(r24):
            nxt = cur
            hold = hold + 1 if cur != 0 else 0
        else:
            desired = 0.0
            if roc > PARAMS["roc_thresh"] and r24 > PARAMS["ret24_min"]:
                desired = 1.0
            elif roc > PARAMS["roc_thresh"] and r24 < -PARAMS["ret24_min"]:
                desired = -1.0
            if cur == 0.0:
                nxt = desired
                hold = 0 if desired == 0 else 1
            else:
                hold += 1
                accel_fade = roc < PARAMS["roc_exit"]
                time_exit = hold >= PARAMS["max_hold_bars"]
                flip = desired != 0 and desired != cur
                if accel_fade or time_exit or flip:
                    nxt = desired if flip else 0.0
                    hold = 0 if nxt == 0 else 1
                else:
                    nxt = cur
        cur = nxt
        if i + 1 < n:
            sig[i + 1] = cur  # t -> t+1 execution

    gross = sig * ret
    turn = np.abs(np.diff(np.r_[0.0, sig]))
    ws = wf_windows(n)
    bh_ret = p.pct_change().fillna(0.0).to_numpy(dtype=float)
    cost_slices: dict[str, Any] = {}
    for fee_b, slip_b in COST_GRID:
        cpr = (fee_b + slip_b) / 10000.0
        net = gross - turn * cpr
        oos_mask = np.zeros(n, dtype=bool)
        for _tr_s, _tr_e, te_e in ws:
            oos_mask[te_e - TEST : te_e] = True
        net_oos = net[oos_mask]
        gross_oos = gross[oos_mask]
        turn_oos = turn[oos_mask]
        bh_oos = bh_ret[oos_mask]
        n_tr = int(turn_oos.sum())
        out = {
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
        cost_slices[f"fee{fee_b}_slip{slip_b}_bps"] = out
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
    by_sym_vol = _extract_vol_series(vol_df)

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
        "type": "real_quote_volume_acceleration_trend_following_costed_oos",
        "campaign": 44,
        "generated_at_utc": stamp_iso,
        "computed_at_stamp": ts,
        "real_data_only": True,
        "fabricated_data": False,
        "fail_closed": True,
        "no_threshold_weakening": True,
        "no_proxies_labeled_real": True,
        "path": "R-B",
        "pre_stated_hypothesis": {
            "name": "Quote Volume Acceleration Trend Following (Volume-Z ROC Confirmation)",
            "description": (
                "Trend-follow using acceleration of normalized quote volume: compute vol_z ROC = "
                "vol_z(t)-vol_z(t-12). Enter long when ROC>0.5 and ret24>0.5% (accelerating volume into uptrend); "
                "short when ROC>0.5 and ret24<-0.5%. Exit on ROC fade (<0), max hold 24h, or flip. "
                "Execution t->t+1. WF 720/168/168, cost grid 0-40bps, B&H benchmark on same OOS windows."
            ),
            "params_fixed_before_oos_evaluation": True,
            "no_in_sample_tuning": True,
            "differs_from_c23": "C23 uses high vol_z LEVEL surge for momentum continuation; C44 uses vol_z ROC (acceleration/delta), not level.",
            "differs_from_c40": "C40 fades HIGH vol climax (mean reversion); C44 follows trend on positive volume acceleration.",
            "differs_from_c41": "C41 enters on LOW vol dry-up breakout continuation; C44 requires positive volume acceleration aligned with trend.",
            "differs_from_c42": "C42 confirms price breakout with volume expansion level; C44 uses vol_z ROC signal with trend alignment, no breakout/extreme condition.",
            "differs_from_c43": "C43 fades price extremes on WEAK volume confirmation (divergence); C44 follows trend on ACCELERATING volume (opposite).",
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
    out_name = REPORTS_DIR / f"real_quote_volume_acceleration_trend_following_costed_oos_{ts}.json"
    _write_json(out_name, out)
    logger.info("wrote %s (oos_edge_proven=%s)", out_name, out["summary"]["oos_edge_proven"])
    print(json.dumps({"wrote": str(out_name), "summary": out["summary"]}))


if __name__ == "__main__":
    main()
