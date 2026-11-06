"""Generate Campaign 41 artifacts.

Campaign 41 — Path R-B (fail-closed, real data only): a GENUINELY DIFFERENT
pre-stated hypothesis on validated real_quote_volume (Binance spot klines col 5),
NOT a rerun of C23 "Abnormal Quote Volume Momentum" and NOT C40 "Quote Volume
Climax Mean Reversion / FADE".

PRE-STATED HYPOTHESIS (fixed before seeing OOS results): "Quote Volume Dry-Up Breakout Continuation"
- For each asset, compute causal rolling z-score of quote_volume_usdt (lookback ZVOL=168h).
- Compute short-term price breakout: ret6 = 6-bar return; vol-scaled breakout when |ret6| / (rolling std of 1h returns, RV=72h) > BREAK_K (1.25).
- Entry (liquidity dry-up + breakout): when vol_z < DRY_Z (-1.0) AND breakout fires, trade
  IN the breakout direction (long if ret6>0, short if ret6<0) expecting continuation as
  liquidity returns. This triggers on LOW volume (dry-up), opposite regime to C23/C40 which
  trigger on HIGH volume/climax; mechanic is breakout continuation, not C23 momentum-following
  on vol surge and not C40 fade.
- Exit: when vol_z > EXIT_Z (-0.2) OR hold >= MAX_HOLD (18h) OR signal flips direction.
- Else flat. Execution shift t -> t+1 (signal on bar close, trade next bar).
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
    format="%(asctime)s [campaign41] %(levelname)s %(message)s",
)
logger = logging.getLogger("campaign41")

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
    "rv_lookback": 72,
    "breakout_ret_bars": 6,
    "break_k": 1.25,
    "dry_z": -1.0,
    "exit_z": -0.2,
    "max_hold_bars": 18,
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
    vv = v.values.astype(float)
    vmean = pd.Series(vv).rolling(
        PARAMS["zvol_lookback"], min_periods=PARAMS["min_vol_obs"]
    ).mean().values
    vstd = pd.Series(vv).rolling(
        PARAMS["zvol_lookback"], min_periods=PARAMS["min_vol_obs"]
    ).std(ddof=0).values
    with np.errstate(divide="ignore", invalid="ignore"):
        volz = np.where((vstd > 1e-18) & np.isfinite(vstd), (vv - vmean) / vstd, np.nan)
    ret6 = pd.Series(p.values).pct_change(PARAMS["breakout_ret_bars"]).values
    rv = pd.Series(ret).rolling(PARAMS["rv_lookback"], min_periods=PARAMS["rv_lookback"]).std(ddof=0).values
    with np.errstate(divide="ignore", invalid="ignore"):
        bk = np.where((rv > 1e-18) & np.isfinite(rv), np.abs(ret6) / rv, np.nan)
    # C41 hypothesis: dry-up (LOW vol_z) + vol-scaled breakout -> continuation
    sig = np.zeros(n)
    cur = 0.0
    hold = 0
    warm = int(max(PARAMS["zvol_lookback"], PARAMS["rv_lookback"], PARAMS["breakout_ret_bars"]) + 2)
    for i in range(warm, int(n)):
        vz = volz[i]
        r6 = ret6[i]
        bki = bk[i]
        if not np.isfinite(vz) or not np.isfinite(r6) or not np.isfinite(bki):
            nxt = cur
            hold = hold + 1 if cur != 0 else 0
        else:
            desired = 0.0
            if vz < PARAMS["dry_z"] and bki > PARAMS["break_k"]:
                if r6 > 0:
                    desired = 1.0
                elif r6 < 0:
                    desired = -1.0
            if cur == 0.0:
                nxt = desired
                hold = 0 if desired == 0 else 1
            else:
                hold += 1
                exit_cond = (vz > PARAMS["exit_z"]) or (hold >= PARAMS["max_hold_bars"]) or (
                    desired != 0 and desired != cur
                )
                if exit_cond:
                    nxt = desired if (desired != 0 and desired != cur) else 0.0
                    hold = 0 if nxt == 0 else 1
                else:
                    nxt = cur
        cur = nxt
        if i + 1 < n:
            sig[i + 1] = cur  # execution shift t -> t+1
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
            oos_mask[tr_e:te_e] = True
            splits.append(
                {
                    "train_start": int(tr_s),
                    "train_end": int(tr_e),
                    "test_end": int(te_e),
                    "is_net": float(np.nansum(net[tr_s:tr_e])),
                    "oos_net": float(np.nansum(net[tr_e:te_e])),
                    "oos_turnover": float(np.nansum(turn[tr_e:te_e])),
                }
            )
        oos_net_sum = float(np.nansum(net[oos_mask])) if oos_mask.any() else 0.0
        is_net_sum = float(np.nansum(net[is_mask])) if is_mask.any() else 0.0
        bh_oos = float(np.nansum(ret[oos_mask])) if oos_mask.any() else 0.0
        key = f"fee{fee_b}_slip{slip_b}_bps"
        cost_slices[key] = {
            "fee_bps": fee_b,
            "slippage_bps": slip_b,
            "cost_per_turnover": cpr,
            "n_splits": len(splits),
            "oos_net_sum": oos_net_sum,
            "is_net_sum": is_net_sum,
            "bh_oos_sum": bh_oos,
            "oos_net_gt_zero": bool(oos_net_sum > 0),
            "oos_net_beat_bh": bool(oos_net_sum > bh_oos),
            "splits": splits,
        }
    has_exposure = bool(np.abs(sig).sum() > 0)
    oos_edge_proven = bool(
        has_exposure
        and all(cs["oos_net_gt_zero"] and cs["oos_net_beat_bh"] for cs in cost_slices.values())
    )
    return {
        "n_bars": int(n),
        "date_start": str(p.index[0]),
        "date_end": str(p.index[-1]),
        "has_exposure": has_exposure,
        "total_turnover": float(turn.sum()),
        "n_wf_splits": len(ws),
        "cost_slices": cost_slices,
        "oos_edge_proven": oos_edge_proven,
    }


def generate_campaign41() -> dict[str, Any]:
    logger.info("Loading validated real_quote_volume feed (fail-closed)...")
    spot_df, spot_meta, spot_sha = load_spot()
    vol_df, vol_report = load_volume()
    if not vol_report.get("ok"):
        raise RuntimeError(f"volume validation failed: {vol_report}")
    vol_wide = (
        vol_df.pivot_table(
            index="timestamp_utc", columns="symbol", values="quote_volume_usdt", aggfunc="first"
        )
        .sort_index()
    )
    if spot_df.index.tz is None:
        spot_df.index = spot_df.index.tz_localize("UTC")
    if vol_wide.index.tz is None:
        vol_wide.index = vol_wide.index.tz_localize("UTC")
    assets = [a for a in spot_df.columns if a in vol_wide.columns]
    if not assets:
        raise RuntimeError(f"No intersecting spot/volume assets for Campaign 41 spot={list(spot_df.columns)} vol={list(vol_wide.columns)[:8]}")
    by_asset: dict[str, Any] = {}
    for a in assets:
        try:
            by_asset[a] = run_asset(spot_df[a], vol_wide[a])
        except Exception as e:
            logger.warning("asset %s failed: %s", a, e)
            by_asset[a] = {"error": str(e), "has_exposure": False, "oos_edge_proven": False, "cost_slices": {}}
        logger.info("asset %s edge=%s exposure=%s", a, by_asset[a].get("oos_edge_proven"), by_asset[a].get("has_exposure"))
    n_edge = sum(1 for r in by_asset.values() if r["oos_edge_proven"])
    n_all_pos = sum(
        1
        for r in by_asset.values()
        if r["has_exposure"]
        and all(cs["oos_net_gt_zero"] for cs in r["cost_slices"].values())
    )
    n_all_bh = sum(
        1
        for r in by_asset.values()
        if r["has_exposure"]
        and all(cs["oos_net_beat_bh"] for cs in r["cost_slices"].values())
    )
    report = {
        "schema": "real_quote_volume_dryup_breakout_costed_oos.v1",
        "campaign": 41,
        "path": "R-B",
        "generated_at_utc": _utc_now_iso(),
        "fail_closed": True,
        "real_data_only": True,
        "fabricated_data": False,
        "provenance": {
            "spot_cache": SPOT_CACHE,
            "spot_cache_sha256": spot_sha,
            "spot_cache_meta": {
                k: spot_meta.get(k)
                for k in ["source", "start", "end", "interval", "assets", "n_bars"]
                if k in spot_meta
            },
            "volume_meta_path": str(VOL_META.relative_to(ROOT)),
            "volume_provenance_path": str(VOL_PROV.relative_to(ROOT)),
            "volume_meta_sha256": sha256_file(VOL_META),
            "volume_provenance_sha256": sha256_file(VOL_PROV),
            "loader_tool": "data.real_feed_loader.validate_and_load_real_feed",
            "feed_family": "real_quote_volume",
            "validation": {
                k: vol_report.get(k)
                for k in [
                    "ok",
                    "refused",
                    "reason",
                    "rows",
                    "family_spec",
                    "multi_symbol_long_frame",
                    "provenance_merged",
                ]
            },
            "source_provider": "www.binance.com public klines endpoint (column 5 quote asset volume)",
            "real_data_only": True,
            "fabricated_data": False,
            "intersection_assets_tested": assets,
        },
        "pre_stated_hypothesis": {
            "name": "Quote Volume Dry-Up Breakout Continuation",
            "description": (
                "Causal rolling z-score of real quote_volume_usdt; liquidity DRY-UP (z < -1.0) "
                "combined with a vol-scaled short-term breakout (|ret6|/RV72 > 1.25) triggers "
                "CONTINUATION in the breakout direction (long if ret6>0, short if ret6<0). "
                "Exit on vol normalization (z > -0.2), max hold, or direction flip. Execution "
                "shifted t->t+1. Triggers on LOW volume regime (dry-up), opposite of C23/C40 "
                "which trigger on HIGH volume/climax; different mechanic and regime."
            ),
            "params": PARAMS,
            "params_fixed_before_oos_evaluation": True,
            "no_in_sample_tuning": True,
            "differs_from_c23": (
                "C23 = momentum on HIGH vol surge (vol_z high) riding ret24 direction. "
                "C41 = continuation on LOW vol dry-up with vol-scaled breakout, different "
                "trigger regime and signal construction."
            ),
            "differs_from_c40": (
                "C40 = mean reversion/FADE on HIGH vol climax (opposite of ret24). "
                "C41 = continuation on LOW vol dry-up (opposite trigger regime), not a fade."
            ),
        },
        "config": {
            "assets": assets,
            "n_assets": len(assets),
            "cost_grid_bps_fee_slippage": COST_GRID,
            "walk_forward": {
                "mode": "rolling",
                "train_bars": TRAIN,
                "test_bars": TEST,
                "step_bars": STEP,
            },
            "benchmark": (
                "buy-and-hold per asset (gross, no recurring turnover) on union of OOS WF "
                "windows; strategy net of fee+slippage on turnover"
            ),
            "pre_stated_oos_edge_proven_rule": (
                "oos_edge_proven=true IFF executed exposure>0 AND for ALL cost-grid slices "
                "OOS net sum > 0 AND OOS net sum > B&H OOS sum on same OOS windows. Else "
                "false (fail-closed)."
            ),
            "explicitly_reported": NAMED,
        },
        "by_asset": by_asset,
        "aggregate": {
            "n_assets": len(by_asset),
            "n_oos_edge_proven": n_edge,
            "aggregate_oos_edge_proven_fail_closed": bool(n_edge > 0 and n_edge == len(by_asset)),
            "n_assets_all_slices_oos_net_positive": n_all_pos,
            "n_assets_all_slices_beat_benchmark": n_all_bh,
            "per_named": {
                sym: {
                    "oos_edge_proven": by_asset[sym].get("oos_edge_proven", False),
                    "has_exposure": by_asset[sym].get("has_exposure", False),
                    "bh_oos_sum": (by_asset[sym].get("cost_slices", {}).get("fee0_slip0_bps") or {}).get("bh_oos_sum"),
                    "oos_0bps_sum": (by_asset[sym].get("cost_slices", {}).get("fee0_slip0_bps") or {}).get("oos_net_sum"),
                    "oos_40bps_sum": (by_asset[sym].get("cost_slices", {}).get("fee20_slip20_bps") or {}).get("oos_net_sum"),
                    "all_slices_beat_bh": all(
                        (by_asset[sym].get("cost_slices", {}).get(f"fee{f}_slip{sl}_bps") or {}).get("oos_net_beat_bh", False)
                        for f, sl in COST_GRID
                    ),
                }
                for sym in NAMED
                if sym in by_asset
            },
        },
        "honest_assessment": (
            "PROVEN NET-OF-COST OOS EDGE (fail-closed rule met) for "
            f"{n_edge}/{len(by_asset)} assets."
            if n_edge > 0
            else "NO PROVEN NET-OF-COST OOS EDGE. oos_edge_proven=false for all tested assets "
            "under pre-stated fail-closed rule."
        ),
    }
    return report


def main() -> None:
    report = generate_campaign41()
    ts = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = REPORTS_DIR / f"real_quote_volume_dryup_breakout_costed_oos_{ts}.json"
    _write_json(out, report)
    logger.info("Wrote %s", out)
    print(f"Wrote {out}")
    print(
        "n_edge",
        report["aggregate"]["n_oos_edge_proven"],
        "n_assets",
        report["aggregate"]["n_assets"],
        "named",
        json.dumps(report["aggregate"]["per_named"], default=str),
    )
    print("sha256", sha256_file(out))


if __name__ == "__main__":
    main()
