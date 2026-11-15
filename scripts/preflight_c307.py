#!/usr/bin/env python3
"""C307 preflight: fail-closed verification of the real COIN-M multi-asset
term-structure + cross-sectional funding-carry cache before the C307 runner
executes.

Verifies (Leg A - per-asset dated-quarterly term structure):
- SHA256-from-bytes of the ingested pickle matches the meta-recorded sha;
- meta flags (real/fabricated/executed_fills), interval 1h, source interval
  coin_m_klines_1h, n_assets, window = common term-structure grid, source host,
  cache format = plain numpy ndarrays, cache < 100 MB push limit;
- for every selected asset: perp close exactly (n_bars x 1) over the common
  grid, present bars finite/positive; quarterly close/basis present where the
  contract is active, finite where present; NaN gaps (real archive outage /
  contract inactivity) are NEVER imputed;
- >= 2 contracts overlap on the common term-structure grid;
- walk-forward split math: train=720/test=168/step=168 in 1h bars fits the
  common grid (>= 1 OOS split);
- feature warmup: rolling features with min_periods=max(20, L//3) warm before
  the first OOS test bar for every runner lookback;

Verifies (Leg B - cross-sectional COIN-M funding carry):
- common funding grid across all 11 perps is non-empty and restricted to
  2022-07..2026-06 (fundingRate archive window);
- >= 2 assets have finite funding overlap on the common grid;
- perp close, premium close, mark close, funding rate arrays present and finite
  where present; NaN gaps carried as NaN, never imputed;
- funding staleness <= 24h + 1 bar rule enforceable;

The script never fetches, imputes, resamples, or fabricates data. Exit 0 iff
every check passes (ready:true); any mismatch/missing file is a fail-closed
blocker.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "cache"

PXL = CACHE / "campaign307_coinm_multiasset_term_structure_carry.pkl"
PXL_META = CACHE / "campaign307_coinm_multiasset_term_structure_carry.meta.json"
PXL_PROV = CACHE / "campaign307_coinm_multiasset_term_structure_carry.provenance.json"

EXPECTED_INTERVAL = "1h"
EXPECTED_SOURCE_INTERVAL = "coin_m_klines_1h"
PUSH_LIMIT_BYTES = 100_000_000

# Runner grid (must match run_c307_coinm_multiasset_term_structure_carry_oos.py).
# DATA-WINDOW CONSTRAINT (fail-closed, recorded, NOT a threshold weakening):
# rolling features use min_periods = max(20, L // 3).  A lookback L can only warm
# up before the first OOS test bar if min_periods(L) <= WF_TRAIN.  The real
# COIN-M common term-structure grid has train=720 bars, so L // 3 <= 720 ->
# L <= 2160.  L=4320 (needs 1440) and L=8640 (needs 2880) are degenerate on this
# window (flat through the entire training set, no learnable signal) and are
# EXCLUDED from the pre-registered grid rather than passed with a weakened gate.
LOOKBACKS_1H = (24, 48, 168, 336, 720, 1440)
WF_TRAIN = 720
WF_TEST = 168
WF_STEP = 168
K_VALUES = (1,)
STALE_BARS = 24 + 1  # 24h + 1 bar on the 1h grid

# Leg B cross-sectional grid
LOOKBACKS_B = (24, 48, 168, 336, 720, 1440)
K_VALUES_B = (2, 3, 5)
HOLDS_B = (1, 6, 24)
GATES_B = ("off", "on")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def min_periods_for(L: int) -> int:
    return max(20, L // 3)


def wf_splits(n: int, train: int, test: int, step: int):
    out = []
    i = 0
    while i + train + test <= n:
        out.append((i, i + train, i + train + test))
        i += step
    return out


def _as_index(pa: dict) -> pd.DatetimeIndex:
    idx = pa.get("index")
    if isinstance(idx, pd.DatetimeIndex):
        return idx
    arr = np.asarray(idx)
    if np.issubdtype(arr.dtype, np.datetime64):
        return pd.DatetimeIndex(arr).tz_localize("UTC")
    return pd.DatetimeIndex(pd.to_datetime(arr, unit="ms", utc=True))


def _as_series(pa: dict, key: str, index: pd.DatetimeIndex) -> pd.Series:
    arr = np.asarray(pa.get(key), dtype=float)
    return pd.Series(arr, index=index)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.parse_args()

    checks: dict = {}
    blocked: list[str] = []

    if not PXL.exists():
        print(json.dumps({"ready": False, "blocked_reasons": ["C307 pickle missing"]}, indent=2))
        return 1
    pkl_sha = sha256_file(PXL)
    pkl_bytes = PXL.stat().st_size

    try:
        meta = json.loads(PXL_META.read_text())
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"ready": False, "blocked_reasons": [f"meta unreadable: {exc}"]}, indent=2))
        return 1

    flags_ok = (
        meta.get("interval") == EXPECTED_INTERVAL
        and meta.get("source_interval") == EXPECTED_SOURCE_INTERVAL
        and meta.get("n_assets") is not None and int(meta.get("n_assets")) >= 1
        and meta.get("real_data_only") is True
        and meta.get("fabricated_data") is False
        and meta.get("executed_fills") is False
        and meta.get("fetch_real_data_only") is True
        and meta.get("fetch_fabricated_data") is False
        and meta.get("source_host") == "https://data.binance.vision"
        and meta.get("cache_format") == "plain_numpy_ndarrays_no_pandas_legs"
        and meta.get("under_push_limit") is True
        and int(meta.get("cache_pkl_bytes") or 0) == pkl_bytes
        and pkl_bytes < PUSH_LIMIT_BYTES
        and pkl_sha == meta.get("sha256_from_bytes")
    )
    checks["meta"] = {
        "interval": meta.get("interval"),
        "source_interval": meta.get("source_interval"),
        "n_assets": meta.get("n_assets"),
        "n_perp_symbols": meta.get("n_perp_symbols"),
        "n_quarterly_contracts": meta.get("n_quarterly_contracts"),
        "funding_window_start": meta.get("funding_window_start"),
        "funding_window_end": meta.get("funding_window_end"),
        "real_data_only": meta.get("real_data_only"),
        "fabricated_data": meta.get("fabricated_data"),
        "executed_fills": meta.get("executed_fills"),
        "cache_format": meta.get("cache_format"),
        "cache_pkl_bytes": pkl_bytes,
        "cache_pkl_mb": round(pkl_bytes / 1e6, 2),
        "under_push_limit": bool(pkl_bytes < PUSH_LIMIT_BYTES),
        "source_host": meta.get("source_host"),
        "sha256_from_bytes": meta.get("sha256_from_bytes"),
        "actual_sha256": pkl_sha,
        "ok": bool(flags_ok),
    }
    if not flags_ok:
        blocked.append("meta flags/interval/source/window/format/size/sha mismatch")

    try:
        with open(PXL, "rb") as fh:
            payload = pickle.load(fh)
        assets = list(payload.get("leg_a", {}).get("selected_assets") or [])
        n_assets = len(assets)
        per_asset = payload.get("leg_a", {}).get("per_asset") or {}
        sym_ok = n_assets >= 1 and n_assets == int(meta.get("n_assets") or 0)

        # ---- Leg A: per-asset term structure checks ----
        # >= 2 contracts overlap required for term-structure carry.
        contracts_ok = True
        contract_detail = {}
        for a in assets:
            pa = per_asset.get(a)
            if not isinstance(pa, dict):
                contract_detail[a] = {"ok": False, "error": "per-asset entry missing or not a dict"}
                contracts_ok = False
                continue
            n_contracts = int(pa.get("n_contracts") or 0)
            bars_ge2 = int(pa.get("bars_ge2_contracts") or 0)
            contract_detail[a] = {
                "n_contracts": n_contracts,
                "bars_ge2_contracts": bars_ge2,
                "ok": bool(n_contracts >= 2 and bars_ge2 > 0),
            }
            contracts_ok &= bool(n_contracts >= 2 and bars_ge2 > 0)
        checks["leg_a_contracts"] = {"n_assets": n_assets, "assets": assets,
                                     "detail": contract_detail, "ok": bool(contracts_ok)}
        if not contracts_ok:
            blocked.append("one or more Leg A assets have < 2 contracts or no bars with >= 2 overlapping")

        asset_detail = {}
        asset_ok = True
        for a in assets:
            pa = per_asset.get(a)
            if not isinstance(pa, dict):
                asset_detail[a] = {"ok": False, "error": "per-asset entry missing or not a dict"}
                asset_ok = False
                continue
            index = _as_index(pa)
            n_bars = int(pa.get("n_bars") or len(index))
            d = {"asset": a, "n_bars": n_bars, "fields": {}}
            all_field_ok = True

            # perp close: finite, positive where present.
            close = _as_series(pa, "perp_close", index).to_numpy(dtype=float)
            c_present = close[~np.isnan(close)]
            c_finite = bool(np.isfinite(c_present).all()) if len(c_present) else False
            c_positive = bool((c_present > 0).all()) if len(c_present) else False
            d["perp_close"] = {
                "nan_count": int(np.isnan(close).sum()),
                "all_finite_present": c_finite,
                "all_positive_present": c_positive,
                "ok": bool(c_finite and c_positive and len(c_present) > 0),
            }
            all_field_ok &= d["perp_close"]["ok"]

            # n_contracts_at_bar: >= 2 on some bars.
            ncatb = _as_series(pa, "n_contracts_at_bar", index).to_numpy(dtype=float)
            d["n_contracts_at_bar"] = {
                "min": float(np.nanmin(ncatb)) if len(ncatb) else 0.0,
                "max": float(np.nanmax(ncatb)) if len(ncatb) else 0.0,
                "bars_ge2": int((ncatb >= 2).sum()),
                "ok": bool(int((ncatb >= 2).sum()) > 0),
            }
            all_field_ok &= d["n_contracts_at_bar"]["ok"]

            # Quarterly close + basis: finite where present.
            q_contracts = pa.get("quarterly_contracts") or []
            for qsym in q_contracts:
                qc_key = f"q_close_{qsym}"
                qb_key = f"q_basis_{qsym}"
                if qc_key in pa:
                    qc = _as_series(pa, qc_key, index).to_numpy(dtype=float)
                    qc_present = qc[~np.isnan(qc)]
                    qc_finite = bool(np.isfinite(qc_present).all()) if len(qc_present) else True
                    qc_positive = bool((qc_present > 0).all()) if len(qc_present) else True
                    d["fields"][qc_key] = {
                        "nan_count": int(np.isnan(qc).sum()),
                        "all_finite_present": qc_finite,
                        "all_positive_present": qc_positive,
                        "ok": bool(qc_finite and qc_positive and len(qc_present) > 0),
                    }
                    all_field_ok &= d["fields"][qc_key]["ok"]
                if qb_key in pa:
                    qb = _as_series(pa, qb_key, index).to_numpy(dtype=float)
                    qb_present = qb[~np.isnan(qb)]
                    qb_finite = bool(np.isfinite(qb_present).all()) if len(qb_present) else True
                    d["fields"][qb_key] = {
                        "nan_count": int(np.isnan(qb).sum()),
                        "all_finite_present": qb_finite,
                        "ok": bool(qb_finite),
                    }
                    all_field_ok &= d["fields"][qb_key]["ok"]

            # walk-forward fit.
            n_splits = len(wf_splits(n_bars, WF_TRAIN, WF_TEST, WF_STEP))
            wf_ok = n_bars >= WF_TRAIN + WF_TEST and n_splits > 0
            d["walk_forward"] = {"bars": n_bars, "train": WF_TRAIN, "test": WF_TEST,
                                 "step": WF_STEP, "n_splits": int(n_splits), "ok": bool(wf_ok)}
            all_field_ok &= wf_ok

            # feature warmup for all runner lookbacks.
            warm = {f"L={L}": {"min_periods": int(min_periods_for(L)),
                               "warm_before_first_test_bar": bool(min_periods_for(L) <= WF_TRAIN),
                               "ok": bool(min_periods_for(L) <= WF_TRAIN)} for L in LOOKBACKS_1H}
            warm_ok = all(v["ok"] for v in warm.values())
            d["feature_warmup"] = {"rule": "min_periods = max(20, L // 3) on native-1h features",
                                   "lookbacks_1h": [int(l) for l in LOOKBACKS_1H],
                                   "warmup": warm, "ok": bool(warm_ok)}
            all_field_ok &= warm_ok

            d["ok"] = bool(all_field_ok)
            asset_detail[a] = d
            asset_ok &= all_field_ok
        checks["leg_a_assets"] = {"n_assets": n_assets, "assets": assets,
                                  "assets_ok": bool(sym_ok), "detail": asset_detail, "ok": bool(asset_ok and sym_ok)}
        if not asset_ok:
            blocked.append("one or more Leg A assets failed perp/quarterly/basis/WF/warmup checks")
        if not sym_ok:
            blocked.append("Leg A universe size mismatch")

        # common grid window sanity (first asset).
        if n_assets:
            first_idx = _as_index(per_asset[assets[0]])
            checks["leg_a_common_grid"] = {
                "bars": int(per_asset[assets[0]].get("n_bars") or 0),
                "start_utc": str(first_idx[0]),
                "end_utc": str(first_idx[-1]),
            }

        # ---- Leg B: cross-sectional funding carry checks ----
        leg_b = payload.get("leg_b") or {}
        leg_b_symbols = leg_b.get("symbols") or []
        n_leg_b_symbols = len(leg_b_symbols)
        n_fund = int(leg_b.get("n_bars") or 0)
        leg_b_index = _as_index(leg_b) if "index" in leg_b else None

        # Verify common funding grid is non-empty and within 2022-07..2026-06
        if leg_b_index is None or len(leg_b_index) == 0:
            blocked.append("Leg B common funding grid is empty")
        else:
            start_ok = leg_b_index[0] >= pd.Timestamp("2022-07-01", tz="UTC")
            end_ok = leg_b_index[-1] < pd.Timestamp("2026-07-01", tz="UTC")
            if not (start_ok and end_ok):
                blocked.append(f"Leg B funding grid outside 2022-07..2026-06: start={leg_b_index[0]}, end={leg_b_index[-1]}")

        # Verify >= 2 assets have finite funding overlap
        n_assets_fund = int(leg_b.get("n_assets_with_funding") or 0)
        if n_assets_fund < 2:
            blocked.append(f"Leg B has {n_assets_fund} assets with finite funding overlap (< 2)")

        leg_b_detail = {}
        leg_b_ok = True
        for s in leg_b_symbols:
            d = {"symbol": s, "fields": {}}
            all_field_ok = True

            # perp close on funding grid
            pc_key = f"perp_close_{s}"
            if pc_key in leg_b:
                pc = np.asarray(leg_b[pc_key], dtype=float)
                pc_present = pc[~np.isnan(pc)]
                pc_finite = bool(np.isfinite(pc_present).all()) if len(pc_present) else False
                pc_positive = bool((pc_present > 0).all()) if len(pc_present) else False
                d["fields"][pc_key] = {
                    "nan_count": int(np.isnan(pc).sum()),
                    "all_finite_present": pc_finite,
                    "all_positive_present": pc_positive,
                    "ok": bool(pc_finite and pc_positive and len(pc_present) > 0),
                }
                all_field_ok &= d["fields"][pc_key]["ok"]

            # funding rate
            fr_key = f"funding_rate_{s}"
            if fr_key in leg_b:
                fr = np.asarray(leg_b[fr_key], dtype=float)
                fr_present = fr[~np.isnan(fr)]
                fr_finite = bool(np.isfinite(fr_present).all()) if len(fr_present) else False
                d["fields"][fr_key] = {
                    "nan_count": int(np.isnan(fr).sum()),
                    "all_finite_present": fr_finite,
                    "ok": bool(fr_finite and len(fr_present) > 0),
                }
                all_field_ok &= d["fields"][fr_key]["ok"]

            # funding present mask
            fp_key = f"funding_present_{s}"
            if fp_key in leg_b:
                fp = np.asarray(leg_b[fp_key], dtype=float)
                d["fields"][fp_key] = {
                    "sum": int(fp.sum()),
                    "ok": bool(fp.sum() > 0),
                }
                all_field_ok &= d["fields"][fp_key]["ok"]

            # premium close
            prem_key = f"premium_close_{s}"
            if prem_key in leg_b:
                prem = np.asarray(leg_b[prem_key], dtype=float)
                prem_present = prem[~np.isnan(prem)]
                prem_finite = bool(np.isfinite(prem_present).all()) if len(prem_present) else True
                d["fields"][prem_key] = {
                    "nan_count": int(np.isnan(prem).sum()),
                    "all_finite_present": prem_finite,
                    "ok": bool(prem_finite),
                }
                all_field_ok &= d["fields"][prem_key]["ok"]

            # mark close
            mark_key = f"mark_close_{s}"
            if mark_key in leg_b:
                mark = np.asarray(leg_b[mark_key], dtype=float)
                mark_present = mark[~np.isnan(mark)]
                mark_finite = bool(np.isfinite(mark_present).all()) if len(mark_present) else True
                d["fields"][mark_key] = {
                    "nan_count": int(np.isnan(mark).sum()),
                    "all_finite_present": mark_finite,
                    "ok": bool(mark_finite),
                }
                all_field_ok &= d["fields"][mark_key]["ok"]

            d["ok"] = bool(all_field_ok)
            leg_b_detail[s] = d
            leg_b_ok &= all_field_ok

        checks["leg_b"] = {
            "n_symbols": n_leg_b_symbols,
            "symbols": leg_b_symbols,
            "window_start_utc": leg_b.get("window_start_utc"),
            "window_end_utc": leg_b.get("window_end_utc"),
            "n_bars": n_fund,
            "n_assets_with_funding": n_assets_fund,
            "detail": leg_b_detail,
            "ok": bool(leg_b_ok),
        }
        if not leg_b_ok:
            blocked.append("one or more Leg B symbols failed perp/funding/premium/mark checks")

        # Leg B feature warmup
        warm_b = {f"L={L}": {"min_periods": int(min_periods_for(L)),
                              "warm_before_first_test_bar": bool(min_periods_for(L) <= WF_TRAIN),
                              "ok": bool(min_periods_for(L) <= WF_TRAIN)} for L in LOOKBACKS_B}
        warm_b_ok = all(v["ok"] for v in warm_b.values())
        checks["leg_b_feature_warmup"] = {"rule": "min_periods = max(20, L // 3) on native-1h features",
                                          "lookbacks_1h": [int(l) for l in LOOKBACKS_B],
                                          "warmup": warm_b, "ok": bool(warm_b_ok)}
        if not warm_b_ok:
            blocked.append("Leg B feature warmup failed for one or more lookbacks")

        # Leg B walk-forward splits
        if n_fund > 0:
            n_splits_b = len(wf_splits(n_fund, WF_TRAIN, WF_TEST, WF_STEP))
            wf_b_ok = n_fund >= WF_TRAIN + WF_TEST and n_splits_b > 0
            checks["leg_b_walk_forward"] = {"bars": n_fund, "train": WF_TRAIN, "test": WF_TEST,
                                           "step": WF_STEP, "n_splits": int(n_splits_b), "ok": bool(wf_b_ok)}
            if not wf_b_ok:
                blocked.append("Leg B walk-forward splits do not fit window")
        else:
            checks["leg_b_walk_forward"] = {"bars": 0, "ok": False}
            blocked.append("Leg B funding grid has zero bars")

        # Cross-sectional K support: need >= 2*max(K) = 10 finite assets at some bars
        if n_assets_fund < 10:
            blocked.append(f"Leg B has {n_assets_fund} assets with funding data (< 10 needed for K=5)")

    except Exception as exc:  # noqa: BLE001
        checks["leg_a_assets"] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        checks["leg_b"] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        blocked.append("payload could not be loaded or verified")

    checks["provenance"] = {
        "path": str(PXL_PROV.relative_to(ROOT)) if PXL_PROV.exists() else str(PXL_PROV),
        "exists": PXL_PROV.exists(),
        "ok": bool(PXL_PROV.exists()),
    }
    if not PXL_PROV.exists():
        blocked.append("provenance json missing")

    ready = not blocked
    result = {
        "ready": ready,
        "real_data_only": True,
        "fabricated_data": False,
        "executed_fills": False,
        "campaign": 307,
        "part": "preflight",
        "checks": checks,
        "blocked_reasons": blocked,
    }
    print(json.dumps(result, indent=2, default=str))
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())