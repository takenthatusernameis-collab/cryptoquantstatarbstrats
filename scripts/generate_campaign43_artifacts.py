"""Generate Campaign 43 artifacts.

Campaign 43 — Path R-B (fail-closed, real data only): a GENUINELY DIFFERENT
pre-stated hypothesis on validated real_quote_volume (Binance spot klines col 5),
NOT a rerun of C23 "Abnormal Quote Volume Momentum", NOT C40 "Quote Volume
Climax Mean Reversion / FADE", NOT C41 "Quote Volume Dry-Up Breakout Continuation",
and NOT C42 "Volume-Expansion Breakout Confirmation Continuation".

PRE-STATED HYPOTHESIS (fixed before seeing OOS results): "Quote Volume Divergence Reversion (Fade on Volume-Price Divergence)"
- For each asset, compute causal rolling z-score of quote_volume_usdt (lookback ZVOL=168h).
- Compute short-term momentum: ret24 = 24-bar return; also track price extreme.
- Volume-Price Divergence (VPD): detect when price makes a new local high/low over LOOKBACK_P (48h)
  BUT quote volume is NOT confirming - i.e. vol_z at/near divergence is BELOW threshold
  (vol_z < DIV_VOL_Z_MAX, e.g. < 0.5) indicating lack of volume support for the move.
- Entry (fade divergence): if price reaches new 48h high with weak volume confirmation (vol_z < 0.5)
  AND ret24 > 0 (extended move) -> SHORT expecting mean reversion (divergence fade).
  If price reaches new 48h low with weak volume confirmation (vol_z < 0.5) AND ret24 < 0 -> LONG
  expecting mean reversion. This is FADE/MEAN REVERSION on DIVERGENCE, opposite of C23/C41/C42
  which are continuation; different from C40 (which fads on HIGH vol climax/surge). C43 fads
  specifically on LOW volume confirmation of extremes (divergence) - genuinely different regime/mechanic.
- Exit: take profit/stop by time-based (max hold MAX_HOLD_BARS=12h) OR if volume confirms
  (vol_z > CONFIRM_Z=0.8, move being confirmed) OR if price reverts back towards mean
  (ret1 > 0 when short, ret1 < 0 when long) OR signal invalidated.
- Execution shift t -> t+1.
- Walk-forward: rolling 720/168/168 (train/test/step). Cost grid: fee+slip bps pairs
  [[0,0],[5,0],[0,5],[5,5],[10,0],[0,10],[10,10],[20,0],[0,20],[20,20]] (0-40bps).
- Benchmark: buy-and-hold per asset (gross, no recurring turnover) on union of OOS WF windows.
- Pre-stated edge rule (fail-closed): oos_edge_proven=true IFF executed exposure>0 AND for
  ALL cost-grid slices OOS net sum > 0 AND OOS net sum > B&H OOS sum on same OOS windows.
  Else false. No in-sample tuning, no threshold weakening, no fabricated data/proxies.
  This is a genuine Path R-B test on real_quote_volume; oos_edge_proven=false is valid.
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
    format="%(asctime)s [campaign43] %(levelname)s %(message)s",
)
logger = logging.getLogger("campaign43")

CACHE_DIR = ROOT / "data" / "cache"
REPORTS_DIR = ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

SPOT_CACHE = "0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7"
VOL_META = CACHE_DIR / "volume_1h_full.meta.json"
VOL_PROV = CACHE_DIR / "volume_1h_full.provenance.json"
COST_GRID = [[0, 0], [5, 0], [0, 5], [5, 5], [10, 0], [0, 10], [10, 10], [20, 0], [0, 20], [20, 20]]
TRAIN, TEST, STEP = 720, 168, 168
PARAMS = {
    "zvol_lookback": 168,
    "div_vol_z_max": 0.5,  # weak volume confirmation
    "confirm_vol_z": 0.8,  # volume confirms -> exit
    "lookback_extreme": 48,
    "ret24_thresh": 0.0,
    "max_hold_bars": 12,
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


def run_asset(prices: pd.Series, vol: pd.Series) -> dict[str, Any]:
    idx = prices.index.intersection(vol.index)
    p = prices.reindex(idx).astype(float)
    v = pd.to_numeric(vol.reindex(idx), errors="coerce")
    mask = p.notna() & v.notna() & (v > 0)
    p = p[mask]
    v = v[mask]
    n = len(p)
    ret = p.pct_change().fillna(0.0).values
    ret1 = pd.Series(ret).shift(1).fillna(0.0).values
    ret24 = pd.Series(p.values).pct_change(24).values
    vv = v.values.astype(float)
    vmean = pd.Series(vv).rolling(
        PARAMS["zvol_lookback"], min_periods=PARAMS["min_vol_obs"]
    ).mean().values
    vstd = pd.Series(vv).rolling(
        PARAMS["zvol_lookback"], min_periods=PARAMS["min_vol_obs"]
    ).std(ddof=0).values
    with np.errstate(divide="ignore", invalid="ignore"):
        volz = np.where((vstd > 1e-18) & np.isfinite(vstd), (vv - vmean) / vstd, np.nan)

    # rolling extremes
    roll_max = pd.Series(p.values).rolling(PARAMS["lookback_extreme"], min_periods=PARAMS["lookback_extreme"]).max().values
    roll_min = pd.Series(p.values).rolling(PARAMS["lookback_extreme"], min_periods=PARAMS["lookback_extreme"]).min().values

    sig = np.zeros(n)
    cur = 0.0
    hold = 0
    warm = int(max(PARAMS["zvol_lookback"], PARAMS["lookback_extreme"]) + 5)
    for i in range(warm, int(n)):
        vz = volz[i]
        r24 = ret24[i]
        pcur = p.values[i]
        if not np.isfinite(vz) or not np.isfinite(r24):
            nxt = cur
            hold = hold + 1 if cur != 0 else 0
        else:
            desired = 0.0
            # divergence: new extreme with weak volume confirmation
            is_new_high = np.isfinite(roll_max[i]) and pcur >= roll_max[i] - 1e-18  # at/near new high
            is_new_low = np.isfinite(roll_min[i]) and pcur <= roll_min[i] + 1e-18   # at/near new low
            weak_vol = vz < PARAMS["div_vol_z_max"]  # low volume confirmation
            if weak_vol and is_new_high and r24 > PARAMS["ret24_thresh"]:
                desired = -1.0  # fade short
            elif weak_vol and is_new_low and r24 < -PARAMS["ret24_thresh"]:
                desired = 1.0   # fade long
            if cur == 0.0:
                nxt = desired
                hold = 0 if desired == 0 else 1
            else:
                hold += 1
                # exit if volume confirms or hold exceeded or reversion starting
                vol_confirms = vz > PARAMS["confirm_vol_z"]
                time_exit = hold >= PARAMS["max_hold_bars"]
                # reversion signal
                if cur == -1.0 and np.isfinite(ret1[i]) and ret1[i] > 0:  # price bouncing up while short
                    revert_exit = True
                elif cur == 1.0 and np.isfinite(ret1[i]) and ret1[i] < 0:   # price bouncing down while long
                    revert_exit = True
                else:
                    revert_exit = False
                exit_cond = vol_confirms or time_exit or revert_exit or (desired != 0 and desired != cur)
                if exit_cond:
                    nxt = desired if (desired != 0 and desired != cur) else 0.0
                    hold = 0 if nxt == 0 else 1
                else:
                    nxt = cur
        cur = nxt
        if i + 1 < n:
            sig[i + 1] = cur
    gross = sig * ret
    turn = np.abs(np.diff(np.r_[0.0, sig]))
    ws = wf_windows(n)
    cost_slices: dict[str, Any] = {}
    for fee_b, slip_b in COST_GRID:
        cpr = (fee_b + slip_b) / 10000.0
        net = gross - turn * cpr
        oos_mask = np.zeros(n, dtype=bool)
        is_mask = np.zeros(n, dtype=bool)
        splits = []
        for tr_s, tr_e, te_e in ws:
            is_mask[tr_s:tr_e] = True
            oos_mask[te_e - TEST : te_e] = True
            splits.append({"train": [int(tr_s), int(tr_e)], "test": [int(te_e - TEST), int(te_e)]})
        net_oos = net[oos_mask]
        gross_oos = gross[oos_mask]
        turn_oos = turn[oos_mask]
        bh_ret = p.pct_change().fillna(0.0).values
        bh_oos = bh_ret[oos_mask]
        n_tr = int(turn_oos.sum())
        out = {
            "n_obs": int(n),
            "n_oos_obs": int(oos_mask.sum()),
            "n_windows": len(ws),
            "splits": splits,
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
            "has_exposure": bool(float(np.abs(sig).sum()) > 0.0),
        }
        cost_slices[f"fee{fee_b}_slip{slip_b}_bps"] = out
    all_pos = all(cost_slices[f"fee{f}_slip{s}_bps"]["oos_net_gt_zero"] for f, s in COST_GRID)
    all_bh = all(cost_slices[f"fee{f}_slip{s}_bps"]["oos_net_beat_bh"] for f, s in COST_GRID)
    exp = bool(float(np.abs(sig).sum()) > 0.0)
    edge = bool(exp and all_pos and all_bh)
    return {
        "n_obs": int(n),
        "has_exposure": exp,
        "cost_slices": cost_slices,
        "oos_edge_proven": edge,
    }


def main() -> None:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    stamp_iso = datetime.now(timezone.utc).isoformat()
    spot_df, spot_meta, spot_sha = load_spot()
    vol_df, vol_report = load_volume()

    by_sym_spot: dict[str, pd.Series] = {}
    for c in spot_df.columns:
        s = spot_df[c].dropna()
        if len(s) > 0:
            by_sym_spot[c] = s
    by_sym_vol: dict[str, pd.Series] = {}
    if isinstance(vol_df, pd.DataFrame):
        if "symbol" in vol_df.columns and "quote_volume_usdt" in vol_df.columns and "timestamp_utc" in vol_df.columns:
            for sym, g in vol_df.groupby("symbol"):
                g2 = g.set_index("timestamp_utc")["quote_volume_usdt"]
                by_sym_vol[str(sym)] = g2
        else:
            for c in vol_df.columns:
                s = vol_df[c].dropna()
                if len(s) > 0:
                    by_sym_vol[c] = s
    elif isinstance(vol_df, dict):
        for k, v in vol_df.items():
            if isinstance(v, pd.Series):
                by_sym_vol[k] = v
            elif isinstance(v, pd.DataFrame) and "quote_volume_usdt" in v.columns:
                if "timestamp_utc" in v.columns:
                    by_sym_vol[k] = v.set_index("timestamp_utc")["quote_volume_usdt"]
                else:
                    by_sym_vol[k] = v["quote_volume_usdt"]

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
        "type": "real_quote_volume_volume_price_divergence_reversion_costed_oos",
        "campaign": 43,
        "generated_at_utc": stamp_iso,
        "computed_at_stamp": ts,
        "real_data_only": True,
        "fabricated_data": False,
        "fail_closed": True,
        "no_threshold_weakening": True,
        "no_proxies_labeled_real": True,
        "path": "R-B",
        "pre_stated_hypothesis": {
            "name": "Quote Volume Divergence Reversion (Fade on Volume-Price Divergence)",
            "description": "Fade price extremes when volume fails to confirm (divergence). Short new 48h highs with vol_z < 0.5 and positive 24h return; long new 48h lows with vol_z < 0.5 and negative 24h return. Exit on volume confirmation (vol_z>0.8), max hold 12h, or price reversion. Genuinely different from C23 momentum, C40 climax fade, C41 dry-up continuation, C42 volume-expansion breakout confirmation.",
            "params_fixed_before_oos_evaluation": True,
            "no_in_sample_tuning": True,
            "differs_from_c23": "C23 rides momentum on high vol_z surge; C43 fades on weak volume confirmation of extremes (opposite direction).",
            "differs_from_c40": "C40 fades on HIGH vol climax; C43 fades on LOW volume confirmation (weak vol_z < 0.5) at extremes.",
            "differs_from_c41": "C41 trades continuation on LOW vol dry-up breakout; C43 trades mean-reversion fade on divergence (weak vol confirmation) regardless of breakout, different mechanic.",
            "differs_from_c42": "C42 trades continuation on volume-EXPANSION breakout confirmation (rising vol_z>0); C43 fades on lack of volume confirmation (vol_z<0.5) - opposite regime.",
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
        "_source_files": {
            "generator": str(Path(__file__).relative_to(ROOT)),
        },
    }
    out_name = REPORTS_DIR / f"real_quote_volume_volume_price_divergence_reversion_costed_oos_{ts}.json"
    _write_json(out_name, out)
    logger.info("wrote %s (oos_edge_proven=%s)", out_name, out["summary"]["oos_edge_proven"])
    print(json.dumps({"wrote": str(out_name), "summary": out["summary"]}))


if __name__ == "__main__":
    main()
