#!/usr/bin/env python3
"""Generate Campaign 45 artifacts.

Campaign 45 — Path R-B (fail-closed, real data only): a GENUINELY DIFFERENT
pre-stated hypothesis on validated real_quote_volume (Binance spot klines col 5),
NOT a rerun of C23 "Abnormal Quote Volume Momentum", NOT C40 "Quote Volume
Climax Mean Reversion / FADE", NOT C41 "Quote Volume Dry-Up Breakout
Continuation", NOT C42 "Volume-Expansion Breakout Confirmation Continuation",
NOT C43 "Quote Volume Divergence Reversion (Fade on Volume-Price Divergence)",
and NOT C44 "Quote Volume Acceleration Trend Following (Volume-Z ROC Confirmation)".

PRE-STATED HYPOTHESIS (fixed before seeing OOS results):
"Illiquidity Shock Mean Reversion (Amihud Proxy on Real Quote Volume)"
- For each asset compute an Amihud-style illiquidity proxy: ILLIQ(t) = |ret1(t)| / (quote_volume_usdt(t) + eps),
  using real quote volume (magnitude, not a z of volume alone). This is a return/volume ratio.
- Compute causal rolling z-score of ILLIQ (lookback ILLIQ_Z=168h): illiq_z.
- Entry (mean reversion on illiquidity shock): when illiq_z > ILLIQ_ENTRY (1.5), liquidity is
  abnormally thin relative to the move size (shock) -> fade the contemporaneous move direction:
  if ret1 < 0 (shock down in thin liquidity) enter LONG expecting rebound; if ret1 > 0 enter SHORT.
  Requires the shock magnitude to be meaningful: |ret1| >= RET1_MIN.
- Exit: when illiq_z < ILLIQ_EXIT (0.0, illiquidity normalizes) OR hold >= MAX_HOLD_BARS (12h)
  OR signal flips. Else flat.
- Execution shift t -> t+1 (causal).
- Walk-forward: rolling 720/168/168. Cost grid: fee+slip bps pairs
  [[0,0],[5,0],[0,5],[5,5],[10,0],[0,10],[10,10],[20,0],[0,20],[20,20]] (0-40bps).
- Benchmark: buy-and-hold per asset on union of OOS WF windows (gross).
- Pre-stated edge rule (fail-closed): oos_edge_proven=true IFF executed exposure>0 AND for
  ALL cost-grid slices OOS net sum > 0 AND OOS net sum > B&H OOS sum on same OOS windows.
  Else false. No in-sample tuning, no threshold weakening, no fabricated data/proxies.

How this differs from prior hypotheses (genuinely different mechanic):
- C23/C40/C41/C42/C43/C44 all use vol_z (level of volume) or vol_z ROC (acceleration) as the
  primary volume signal. C45 uses ILLIQ = |return|/quote_volume (Amihud illiquidity ratio),
  a return-normalized liquidity measure — fundamentally different transformation of the feed.
- C40 fades on HIGH volume climax; C41 continues on LOW volume dry-up; C42 confirms breakouts on
  volume expansion; C43 fades on volume-price divergence (weak vol confirmation of extremes);
  C44 trend-follows on volume acceleration. C45 fades moves specifically when ILLIQUIDITY spikes
  (|ret| large relative to volume), regardless of absolute vol_z level regime.
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
    format="%(asctime)s [campaign45] %(levelname)s %(message)s",
)
logger = logging.getLogger("campaign45")

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
    "illiq_z_lookback": 168,
    "illiq_entry_z": 1.5,
    "illiq_exit_z": 0.0,
    "ret1_min_abs": 0.001,  # 0.1% min shock
    "max_hold_bars": 12,
    "min_obs": 168,
    "eps": 1e-12,
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
    out: dict[str, pd.Series] = {}
    if isinstance(vol_df, pd.DataFrame):
        # long format: timestamp_utc, symbol, quote_volume_usdt
        if {"symbol", "quote_volume_usdt"}.issubset(set(vol_df.columns)):
            piv = vol_df.pivot_table(
                index="timestamp_utc", columns="symbol", values="quote_volume_usdt", aggfunc="first"
            )
            for c in piv.columns:
                s = piv[c].dropna()
                if len(s) > 0:
                    out[str(c)] = s
            return out
        # wide format fallback
        for c in vol_df.columns:
            s = vol_df[c].dropna()
            if len(s) > 0:
                out[str(c)] = s
    elif isinstance(vol_df, dict):
        for k, v in vol_df.items():
            if isinstance(v, pd.Series):
                s = v.dropna()
                if len(s) > 0:
                    out[str(k)] = s
    return out


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


def compute_illiq_signal(close: pd.Series, vol: pd.Series, params: dict) -> pd.DataFrame:
    df = pd.DataFrame({"close": close.astype(float), "qvol": vol.astype(float)}).sort_index()
    df["ret1"] = df["close"].pct_change()
    illiq = df["ret1"].abs() / (df["qvol"].abs() + float(params["eps"]))
    zlb = int(params["illiq_z_lookback"])
    mu = illiq.rolling(zlb, min_periods=zlb).mean()
    sd = illiq.rolling(zlb, min_periods=zlb).std(ddof=0).replace(0, np.nan)
    df["illiq_z"] = (illiq - mu) / sd

    sig = np.zeros(len(df), dtype=float)
    raw = np.zeros(len(df), dtype=float)
    iz = df["illiq_z"].to_numpy()
    r1 = df["ret1"].to_numpy()
    entry = float(params["illiq_entry_z"])
    exit_z = float(params["illiq_exit_z"])
    rmin = float(params["ret1_min_abs"])
    mh = int(params["max_hold_bars"])

    # raw desired position at t (evaluated on bar t info)
    for i in range(len(df)):
        if np.isfinite(iz[i]) and iz[i] > entry and np.isfinite(r1[i]) and abs(r1[i]) >= rmin:
            raw[i] = 1.0 if r1[i] < 0 else -1.0  # fade shock
    # apply exits/holds
    hold = 0
    pos = 0.0
    for i in range(len(df)):
        desired = raw[i]
        if pos != 0.0:
            hold += 1
            norm = iz[i] < exit_z if np.isfinite(iz[i]) else False
            flip = desired != 0.0 and desired != pos
            if norm or hold >= mh or flip:
                if flip and desired != 0.0:
                    pos = desired
                    hold = 1
                else:
                    pos = 0.0
                    hold = 0
        else:
            if desired != 0.0:
                pos = desired
                hold = 1
        sig[i] = pos
    # execution shift t -> t+1
    sig_s = pd.Series(sig, index=df.index).shift(1).fillna(0.0)
    df["signal_exec"] = sig_s.to_numpy()
    df["bh_ret"] = df["ret1"].fillna(0.0)
    return df


def run_asset(close: pd.Series, vol: pd.Series) -> dict:
    df = compute_illiq_signal(close, vol, PARAMS)
    df = df.dropna(subset=["ret1", "illiq_z"]).copy()
    n = len(df)
    ws = wf_splits(n)
    if not ws:
        return {"n_obs": int(n), "oos_edge_proven": False, "reason": "insufficient_for_wf"}
    sig = df["signal_exec"].to_numpy()
    ret = df["ret1"].to_numpy()
    bh_ret = df["bh_ret"].to_numpy()
    gross = sig * ret
    turn = np.abs(np.diff(sig, prepend=0.0))
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
        "type": "real_quote_volume_illiq_shock_mean_reversion_costed_oos",
        "campaign": 45,
        "generated_at_utc": stamp_iso,
        "computed_at_stamp": ts,
        "real_data_only": True,
        "fabricated_data": False,
        "fail_closed": True,
        "no_threshold_weakening": True,
        "no_proxies_labeled_real": True,
        "path": "R-B",
        "pre_stated_hypothesis": {
            "name": "Illiquidity Shock Mean Reversion (Amihud Proxy on Real Quote Volume)",
            "description": (
                "Compute Amihud illiquidity proxy ILLIQ=|ret1|/(quote_volume+eps) and its causal z-score (168h). "
                "When illiq_z>1.5 and |ret1|>=0.1% (thin-liquidity shock), fade the move direction: "
                "long if ret1<0, short if ret1>0. Exit on illiq_z<0, max hold 12h, or flip. "
                "Execution t->t+1. WF 720/168/168, cost grid 0-40bps, B&H benchmark on same OOS windows."
            ),
            "params_fixed_before_oos_evaluation": True,
            "no_in_sample_tuning": True,
            "differs_from_c23": "C23 uses high vol_z LEVEL surge for momentum continuation; C45 uses |ret|/volume illiquidity ratio, not vol_z level.",
            "differs_from_c40": "C40 fades HIGH volume climax (vol_z level); C45 fades illiquidity SHOCKS (|ret|/volume z-score), different transformation.",
            "differs_from_c41": "C41 continues on LOW vol_z dry-up breakout; C45 fades on HIGH illiquidity ratio shocks.",
            "differs_from_c42": "C42 confirms breakouts on volume expansion (rising vol_z); C45 uses return-normalized illiquidity ratio, no breakout condition.",
            "differs_from_c43": "C43 fades volume-price divergence (weak vol_z confirmation of extremes); C45 fades illiquidity spikes (|ret|/volume).",
            "differs_from_c44": "C44 trend-follows on vol_z ROC acceleration; C45 mean-reverts on illiquidity ratio shocks — opposite direction/mechanic and different signal.",
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
    out_name = REPORTS_DIR / f"real_quote_volume_illiq_shock_mean_reversion_costed_oos_{ts}.json"
    _write_json(out_name, out)
    logger.info("wrote %s (oos_edge_proven=%s)", out_name, out["summary"]["oos_edge_proven"])
    print(json.dumps({"wrote": str(out_name), "summary": out["summary"]}))


if __name__ == "__main__":
    main()
