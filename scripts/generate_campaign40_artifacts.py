"""Generate Campaign 40 artifacts.

Campaign 40 — Path R-B (fail-closed, real data only): a GENUINELY DIFFERENT
pre-stated hypothesis on validated real_quote_volume (Binance spot klines col 5),
NOT a rerun of C23 "Abnormal Quote Volume Momentum" and NOT a structurally-similar
spot retest on the same cache.

PRE-STATED HYPOTHESIS (fixed before seeing OOS results): "Quote Volume Climax Mean Reversion"
- For each asset, compute causal rolling z-score of quote_volume_usdt (lookback ZVOL=168h).
- Entry (volume climax / liquidity exhaustion): when vol_z > ENTRY_Z (1.5), take the
  OPPOSITE direction of recent RET_LOOKBACK (24h) return — FADE the climax:
  short if ret24 > 0 (climax buying exhausts), long if ret24 < 0 (climax selling exhausts).
  This is mean reversion, opposite sign and opposite mechanic to C23 momentum.
- Exit: when vol_z < EXIT_Z (0.5) OR hold >= MAX_HOLD (24h) OR signal flips direction.
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
    format="%(asctime)s [campaign40] %(levelname)s %(message)s",
)
logger = logging.getLogger("campaign40")

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
    "ret_lookback": 24,
    "entry_z": 1.5,
    "exit_z": 0.5,
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
    retN = pd.Series(p.values).pct_change(PARAMS["ret_lookback"]).values
    # C40 hypothesis (mean reversion / FADE, opposite of C23 momentum):
    # vol climax (vol_z > entry_z) -> fade recent return direction:
    #   ret24 > 0 -> short (-1), ret24 < 0 -> long (+1)
    sig = np.zeros(n)
    cur = 0.0
    hold = 0
    warm = int(max(PARAMS["zvol_lookback"], PARAMS["ret_lookback"]) + 2)
    for i in range(warm, int(n)):
        vz = volz[i]
        rN = retN[i]
        if not np.isfinite(vz) or not np.isfinite(rN):
            nxt = cur
            hold = hold + 1 if cur != 0 else 0
        else:
            desired = 0.0
            if vz > PARAMS["entry_z"]:
                if rN > 0:
                    desired = -1.0  # fade: short after climax buying
                elif rN < 0:
                    desired = 1.0  # fade: long after climax selling
            if cur == 0.0:
                nxt = desired
                hold = 0 if desired == 0 else 1
            else:
                hold += 1
                exit_cond = (vz < PARAMS["exit_z"]) or (hold >= PARAMS["max_hold_bars"]) or (
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
    oos_union = np.zeros(n, dtype=bool)
    for _, tr_e, te_e in ws:
        oos_union[tr_e:te_e] = True
    bh_oos = float(np.nansum(ret[oos_union])) if oos_union.sum() else 0.0
    bh_is = float(np.nansum(ret[~oos_union]))
    has_exp = bool((np.abs(sig) > 0).sum() > 0)
    slices: dict[str, Any] = {}
    for fee, slip in COST_GRID:
        cr = (fee + slip) / 10000.0
        net = gross - turn * cr
        oos_sum = float(np.nansum(net[oos_union]))
        is_sum = float(np.nansum(net[~oos_union]))
        slices[f"fee{fee}_slip{slip}_bps"] = {
            "oos_net_sum": oos_sum,
            "is_net_sum": is_sum,
            "bh_oos_sum": bh_oos,
            "oos_net_gt_zero": bool(oos_sum > 0),
            "oos_net_beat_bh": bool(oos_sum > bh_oos),
            "total_turnover": float(np.nansum(turn)),
        }
    edge = bool(
        has_exp
        and all(
            slices[f"fee{f}_slip{s}_bps"]["oos_net_gt_zero"]
            and slices[f"fee{f}_slip{s}_bps"]["oos_net_beat_bh"]
            for f, s in COST_GRID
        )
    )
    return {
        "n_bars": int(n),
        "window_start": str(idx[0]) if n else None,
        "window_end": str(idx[-1]) if n else None,
        "n_wf_folds": int(len(ws)),
        "has_exposure": has_exp,
        "n_active_bars": int((np.abs(sig) > 0).sum()),
        "exposure_frac": float((np.abs(sig) > 0).mean()) if n else 0.0,
        "bh_oos_sum": bh_oos,
        "bh_is_sum": bh_is,
        "cost_slices": slices,
        "oos_edge_proven": bool(edge),
    }


def generate_campaign40() -> dict[str, Any]:
    spot, spot_meta, spot_sha = load_spot()
    vol_df, vol_report = load_volume()
    vol_wide = (
        vol_df.pivot_table(
            index="timestamp_utc", columns="symbol", values="quote_volume_usdt", aggfunc="first"
        )
        .sort_index()
    )
    if spot.index.tz is None:
        spot.index = spot.index.tz_localize("UTC")
    if vol_wide.index.tz is None:
        vol_wide.index = vol_wide.index.tz_localize("UTC")
    assets = [a for a in spot.columns if a in vol_wide.columns]
    if not assets:
        raise RuntimeError("No intersecting spot/volume assets for Campaign 40")
    by_asset: dict[str, Any] = {}
    for a in assets:
        try:
            by_asset[a] = run_asset(spot[a], vol_wide[a])
        except Exception as e:
            logger.warning("asset %s failed: %s", a, e)
            by_asset[a] = {
                "error": str(e),
                "has_exposure": False,
                "oos_edge_proven": False,
                "cost_slices": {},
            }
    n_edge = sum(1 for v in by_asset.values() if v.get("oos_edge_proven"))
    n_all_pos = sum(
        1
        for v in by_asset.values()
        if all(
            v.get("cost_slices", {}).get(f"fee{f}_slip{s}_bps", {}).get("oos_net_gt_zero", False)
            for f, s in COST_GRID
        )
    )
    n_all_bh = sum(
        1
        for v in by_asset.values()
        if all(
            v.get("cost_slices", {}).get(f"fee{f}_slip{s}_bps", {}).get("oos_net_beat_bh", False)
            for f, s in COST_GRID
        )
    )
    report = {
        "report": "real_quote_volume_climax_mean_reversion_costed_oos",
        "campaign": 40,
        "path": "R-B",
        "family": "real_quote_volume",
        "generated_at_utc": _utc_now_iso(),
        "fail_closed": True,
        "real_data_only": True,
        "fabricated_data": False,
        "no_proxies_labeled_real": True,
        "no_threshold_weakening": True,
        "not_c23_rerun": True,
        "hypothesis_differs_from_c23": True,
        "mandate": (
            "Campaign 40 Path R-B — pre-stated costed OOS test of Quote Volume Climax Mean "
            "Reversion using real Binance spot quote volume (klines col 5) with verifiable "
            "provenance. Genuinely different from C23 Abnormal Quote Volume Momentum: mean "
            "reversion (fade) mechanic with opposite signal sign, not momentum/trend. "
            "Fail-closed, real data only, no fabrication, no proxies labeled real, no "
            "threshold weakening. oos_edge_proven=false is valid."
        ),
        "provenance": {
            "real_data_only": True,
            "fabricated_data": False,
            "fail_closed": True,
            "no_threshold_weakening": True,
            "no_proxies_labeled_real": True,
            "new_external_feeds_ingested_this_session": False,
            "feed_present_and_validated_fail_closed": True,
            "spot_cache": {
                "path": f"data/cache/{SPOT_CACHE}.pkl",
                "sha256": spot_sha,
                "bars": int(len(spot)),
                "assets": list(spot.columns),
            },
            "volume_feed": {
                "meta": "data/cache/volume_1h_full.meta.json",
                "pkl": "data/cache/volume_1h_full.pkl",
                "provenance_cert": "data/cache/volume_1h_full.provenance.json",
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
                        "source_provider": (
                            "www.binance.com public klines endpoint "
                            "(column 5 quote asset volume)"
                        ),
                "real_data_only": True,
                "fabricated_data": False,
            },
            "intersection_assets_tested": assets,
        },
        "pre_stated_hypothesis": {
            "name": "Quote Volume Climax Mean Reversion",
            "description": (
                "Causal rolling z-score of real quote_volume_usdt; volume climax (z>1.5) "
                "triggers a FADE of the recent 24h return direction (mean reversion, opposite "
                "of C23 momentum): short if ret24>0, long if ret24<0. Exit on vol normalization, "
                "max hold, or direction flip. Execution shifted t->t+1. Genuinely different "
                "mechanic and sign from C23 Abnormal Quote Volume Momentum."
            ),
            "params": PARAMS,
            "params_fixed_before_oos_evaluation": True,
            "no_in_sample_tuning": True,
            "differs_from_c23": (
                "C23 = momentum (vol surge -> ride ret24 direction). C40 = mean reversion / "
                "fade (vol climax -> opposite of ret24 direction). Different hypothesis, "
                "different signal sign, not a C23 rerun."
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
                    "bh_oos_sum": by_asset[sym].get("bh_oos_sum"),
                    "oos_0bps_sum": by_asset[sym].get("cost_slices", {}).get(
                        "fee0_slip0_bps", {}
                    ).get("oos_net_sum"),
                    "oos_40bps_sum": by_asset[sym].get("cost_slices", {}).get(
                        "fee20_slip20_bps", {}
                    ).get("oos_net_sum"),
                    "all_slices_beat_bh": all(
                        by_asset[sym].get("cost_slices", {}).get(
                            f"fee{f}_slip{sl}_bps", {}
                        ).get("oos_net_beat_bh", False)
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
    report = generate_campaign40()
    ts = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = REPORTS_DIR / f"real_quote_volume_climax_mean_reversion_costed_oos_{ts}.json"
    _write_json(out, report)
    logger.info("Wrote %s", out)
    print(f"Wrote {out}")
    print(
        "n_edge",
        report["aggregate"]["n_oos_edge_proven"],
        "n_assets",
        report["aggregate"]["n_assets"],
        "named",
        report["aggregate"]["per_named"],
    )
    print("sha256", sha256_file(out))


if __name__ == "__main__":
    main()
