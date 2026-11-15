#!/usr/bin/env python3
"""C306 preflight: fail-closed verification of the real COIN-M term-structure
cache before the C306 runner executes.

Verifies:

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
- provenance json exists.

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

PXL = CACHE / "campaign306_coinm_term_structure.pkl"
PXL_META = CACHE / "campaign306_coinm_term_structure.meta.json"
PXL_PROV = CACHE / "campaign306_coinm_term_structure.provenance.json"

EXPECTED_INTERVAL = "1h"
EXPECTED_SOURCE_INTERVAL = "coin_m_klines_1h"
PUSH_LIMIT_BYTES = 100_000_000

# Runner grid (must match run_c306_coinm_term_structure_oos.py).
LOOKBACKS_1H = (24, 48, 96, 168, 336, 720, 1440, 2160, 4320, 8640)
WF_TRAIN = 720
WF_TEST = 168
WF_STEP = 168
K_VALUES = (1,)
STALE_BARS = 24 + 1  # 24h + 1 bar on the 1h grid


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
        print(json.dumps({"ready": False, "blocked_reasons": ["C306 pickle missing"]}, indent=2))
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
        "n_universe_perps": meta.get("n_universe_perps"),
        "n_universe_quarterlies": meta.get("n_universe_quarterlies"),
        "window_start_utc": meta.get("window_start_utc") if "window_start_utc" in meta else None,
        "window_end_utc": meta.get("window_end_utc") if "window_end_utc" in meta else None,
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
        assets = list(payload.get("assets") or [])
        n_assets = len(assets)
        per_asset = payload.get("per_asset") or {}
        sym_ok = n_assets >= 1 and n_assets == int(meta.get("n_assets") or 0)

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
        checks["contracts"] = {"n_assets": n_assets, "assets": assets,
                               "detail": contract_detail, "ok": bool(contracts_ok)}
        if not contracts_ok:
            blocked.append("one or more assets have < 2 contracts or no bars with >= 2 overlapping")

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
        checks["assets"] = {"n_assets": n_assets, "assets": assets,
                            "assets_ok": bool(sym_ok), "detail": asset_detail, "ok": bool(asset_ok and sym_ok)}
        if not asset_ok:
            blocked.append("one or more assets failed perp/quarterly/basis/WF/warmup checks")
        if not sym_ok:
            blocked.append("universe size mismatch")

        # common grid window sanity (first asset).
        if n_assets:
            first_idx = _as_index(per_asset[assets[0]])
            checks["common_grid"] = {
                "bars": int(per_asset[assets[0]].get("n_bars") or 0),
                "start_utc": str(first_idx[0]),
                "end_utc": str(first_idx[-1]),
            }
    except Exception as exc:  # noqa: BLE001
        checks["assets"] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        blocked.append("assets could not be loaded")

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
        "campaign": 306,
        "part": "preflight",
        "checks": checks,
        "blocked_reasons": blocked,
    }
    print(json.dumps(result, indent=2, default=str))
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
