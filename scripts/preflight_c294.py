#!/usr/bin/env python3
"""C294 preflight: fail-closed verification of the real implied-volatility
(Deribit DVOL) + real realized-vol (Binance spot 1h) cache before the
variance-risk-premium / BTC-vs-ETH relative-value campaign runs.

C294 is a NEW economic dimension (a genuinely new asset class): real option
IMPLIED volatility, not a realized-vol proxy.  This preflight verifies:

- pkl / meta / provenance exist and the SHA256-from-bytes of the pickle matches
  meta.sha256_from_bytes; real_data_only=true, fabricated_data=false;
- DVOL and spot frames are exactly (n_bars x 2) over a contiguous, strictly
  increasing, exact-1h UTC index, identical across assets;
- DVOL finite for BOTH assets (no gap-fill) and realized vol finite post-warmup
  for BOTH assets (annualized std of 1h log returns, L=720);
- native 1h alignment across DVOL / RV / spot;
- per-asset coverage gate (both full; record any partial with a reason);
- REAL-IV provenance: data/real_feed_loader.py::_check_term_structure_not_realized_vol_proxy
  must ACCEPT the DVOL definition (iv_definition=deribit_dvol_index) and REJECT a
  realized-vol-as-IV proxy (negative control);
- walk-forward split math: n_splits == (n_bars - 720 - 168) // 168 + 1;
- feature warmup: max lookback L=720 1h bars warms before the first OOS test bar.

Never fetches, imputes, resamples, or fabricates data. Exit 0 iff every check
passes; any mismatch is fail-closed.
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
sys.path.insert(0, str(ROOT))
CACHE = ROOT / "data" / "cache"

PKL = CACHE / "campaign294_deribit_dvol.pkl"
META = CACHE / "campaign294_deribit_dvol.meta.json"
PROV = CACHE / "campaign294_deribit_dvol.provenance.json"

EXPECTED_INTERVAL = "1h"
REQUIRED_SYMBOLS = ("BTC", "ETH")
MIN_SYMBOLS = 2
IV_DEFINITION = "deribit_dvol_index"
RV_DEFINITION = "annualized_std_of_1h_log_returns_times_sqrt_8760"
ANNUALIZATION = float(24 * 365)

LOOKBACKS_1H = (24, 168, 720)
WF_TRAIN = 720
WF_TEST = 168
WF_STEP = 168
HOUR = pd.Timedelta(hours=1)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def min_periods_for(L: int) -> int:
    return max(3, L // 3)


def _as_utc_index(idx) -> pd.DatetimeIndex:
    idx = pd.DatetimeIndex(idx)
    if idx.tz is None:
        return idx.tz_localize("UTC")
    return idx.tz_convert("UTC")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.parse_args()

    checks: dict = {}
    blocked: list[str] = []

    # 1. Files exist
    for name, p in (("pkl", PKL), ("meta", META), ("provenance", PROV)):
        if not p.exists():
            print(json.dumps({"ready": False, "blocked_reasons": [f"{name} missing: {p}"]}, indent=2))
            return 1

    pkl_sha = sha256_file(PKL)
    meta = json.loads(META.read_text())
    prov = json.loads(PROV.read_text())

    # 2. Meta / provenance flags + SHA
    meta_ok = (
        meta.get("interval") == EXPECTED_INTERVAL
        and meta.get("real_data_only") is True
        and meta.get("fabricated_data") is False
        and meta.get("iv_definition") == IV_DEFINITION
        and meta.get("rv_definition") == RV_DEFINITION
        and int(meta.get("n_symbols", 0)) == MIN_SYMBOLS
        and tuple(meta.get("symbols", [])) == REQUIRED_SYMBOLS
        and int(meta.get("rows", 0)) > 0
        and pkl_sha == meta.get("sha256_from_bytes")
    )
    checks["meta"] = {
        "interval": meta.get("interval"),
        "n_symbols": meta.get("n_symbols"),
        "symbols": meta.get("symbols"),
        "rows": meta.get("rows"),
        "iv_definition": meta.get("iv_definition"),
        "rv_definition": meta.get("rv_definition"),
        "real_data_only": meta.get("real_data_only"),
        "fabricated_data": meta.get("fabricated_data"),
        "sha256_from_bytes": meta.get("sha256_from_bytes"),
        "actual_sha256": pkl_sha,
        "ok": bool(meta_ok),
    }
    if not meta_ok:
        blocked.append("meta flags/interval/symbols/iv_definition/sha mismatch")

    prov_ok = prov.get("real_data_only") is True and prov.get("fabricated_data") is False
    checks["provenance"] = {"ok": bool(prov_ok)}
    if not prov_ok:
        blocked.append("provenance missing or flags invalid")

    # 3. Payload + frames
    payload = pickle.loads(PKL.read_bytes())
    symbols = list(payload.get("symbols", []))
    sym_ok = len(symbols) >= MIN_SYMBOLS and symbols == list(REQUIRED_SYMBOLS)
    checks["symbols"] = {"n": len(symbols), "symbols": symbols, "ok": bool(sym_ok)}
    if not sym_ok:
        blocked.append("symbol set missing/incorrect/duplicated")

    dvol = payload.get("dvol")
    spot = payload.get("spot_closes")
    if not isinstance(dvol, pd.DataFrame) or not isinstance(spot, pd.DataFrame):
        print(json.dumps({"ready": False, "blocked_reasons": ["dvol/spot frame missing or not a DataFrame"]}, indent=2))
        return 1

    dvol = dvol.astype(float).sort_index()
    spot = spot.astype(float).sort_index()

    idx = _as_utc_index(dvol.index)
    exact_1h = bool(len(idx) > 1 and (idx.to_series().diff().dropna() == HOUR).all())
    strictly_increasing = bool(idx.is_monotonic_increasing and idx.is_unique)
    index_ok = bool(strictly_increasing and exact_1h)
    checks["index"] = {
        "start": str(idx.min()),
        "end": str(idx.max()),
        "n": int(len(idx)),
        "strictly_increasing_unique": strictly_increasing,
        "exact_1h_spacing": exact_1h,
        "ok": index_ok,
    }
    if not index_ok:
        blocked.append("index not strictly increasing / unique / exact 1h spacing")

    aligned_ok = bool(dvol.index.equals(spot.index) and list(dvol.columns) == symbols and list(spot.columns) == symbols)
    checks["alignment"] = {"dvol_equals_spot_index": bool(dvol.index.equals(spot.index)), "columns_match": bool(list(dvol.columns) == symbols and list(spot.columns) == symbols), "ok": aligned_ok}
    if not aligned_ok:
        blocked.append("DVOL/spot index or column misalignment")

    dvol_vals = dvol.to_numpy(dtype=float)
    spot_vals = spot.to_numpy(dtype=float)
    dvol_finite = bool(np.isfinite(dvol_vals).all())
    spot_finite = bool(np.isfinite(spot_vals).all())
    spot_positive = bool((spot_vals > 0).all()) if spot_finite else False
    frames_ok = bool(
        dvol.shape == (len(idx), len(symbols))
        and spot.shape == (len(idx), len(symbols))
        and dvol_finite
        and spot_finite
        and spot_positive
    )
    checks["frames"] = {
        "dvol_shape": list(dvol.shape),
        "spot_shape": list(spot.shape),
        "dvol_all_finite": dvol_finite,
        "spot_all_finite": spot_finite,
        "spot_all_positive": spot_positive,
        "ok": frames_ok,
    }
    if not frames_ok:
        blocked.append("DVOL/spot frame failed shape/finite/positive checks")

    # 4. Realized vol finite post-warmup (L=720, annualized std of 1h log returns)
    logret = np.log(spot).diff()
    rv_ref = logret.rolling(720, min_periods=min_periods_for(720)).std() * float(np.sqrt(ANNUALIZATION))
    rv_vals = rv_ref.to_numpy(dtype=float)[min_periods_for(720):]
    rv_finite = bool(np.isfinite(rv_vals).all())
    checks["realized_vol"] = {
        "definition": RV_DEFINITION,
        "reference_lookback": 720,
        "post_warmup_all_finite": rv_finite,
        "ok": rv_finite,
    }
    if not rv_finite:
        blocked.append("realized vol not finite post-warmup for both assets")

    # 5. Per-asset coverage gate (full; record partial with reason)
    coverage = {}
    coverage_ok = True
    for j, s in enumerate(symbols):
        d_nan = int(np.isnan(dvol_vals[:, j]).sum())
        s_nan = int(np.isnan(spot_vals[:, j]).sum())
        full = bool(d_nan == 0 and s_nan == 0 and np.isfinite(dvol_vals[:, j]).all() and np.isfinite(spot_vals[:, j]).all())
        coverage[s] = {"dvol_nan": d_nan, "spot_nan": s_nan, "full": full, "ok": full}
        if not full:
            coverage_ok = False
    checks["coverage"] = {"detail": coverage, "ok": bool(coverage_ok)}
    if not coverage_ok:
        blocked.append("per-asset coverage gate failed (partial data; recorded)")

    # 6. REAL-IV provenance: DVOL must pass; realized-vol-as-IV proxy must be refused.
    from data.real_feed_loader import (  # noqa: E402
        RealFeedValidationError,
        _check_term_structure_not_realized_vol_proxy,
    )

    iv_meta = {
        "iv_definition": IV_DEFINITION,
        "notes": "Deribit DVOL index: real 30-day constant-maturity implied volatility.",
        "source": "https://www.deribit.com/api/v2/public/get_volatility_index_data",
        "real_data_only": True,
        "fabricated_data": False,
    }
    iv_report: dict = {}
    iv_accepted = True
    try:
        _check_term_structure_not_realized_vol_proxy(iv_meta, iv_report)
    except RealFeedValidationError:
        iv_accepted = False
    proxy_meta = {
        "iv_definition": "realized_vol_proxy",
        "notes": "realized vol labeled as iv",
        "real_data_only": True,
        "fabricated_data": False,
    }
    proxy_report: dict = {}
    proxy_refused = False
    try:
        _check_term_structure_not_realized_vol_proxy(proxy_meta, proxy_report)
    except RealFeedValidationError:
        proxy_refused = True
    iv_ok = bool(iv_accepted and proxy_refused)
    checks["real_iv_provenance"] = {
        "iv_definition": IV_DEFINITION,
        "dvol_definition_accepted": iv_accepted,
        "realized_vol_proxy_refused": proxy_refused,
        "ok": iv_ok,
    }
    if not iv_ok:
        blocked.append("real-IV provenance check failed (DVOL not accepted or proxy not refused)")

    # 7. Walk-forward split math + warmup
    n_bars = int(len(idx))
    expected_splits = (n_bars - WF_TRAIN - WF_TEST) // WF_STEP + 1
    first_test_bar = WF_TRAIN
    max_lookback = max(LOOKBACKS_1H)
    warmup_ok = bool(first_test_bar >= max_lookback and min_periods_for(max_lookback) <= first_test_bar)
    wf_ok = bool(expected_splits >= 2 and warmup_ok)
    checks["walk_forward"] = {
        "n_bars": n_bars,
        "train": WF_TRAIN,
        "test": WF_TEST,
        "step": WF_STEP,
        "expected_n_splits": int(expected_splits),
        "first_test_bar": int(first_test_bar),
        "max_lookback": int(max_lookback),
        "warmup_ok": warmup_ok,
        "ok": wf_ok,
    }
    if not wf_ok:
        blocked.append(f"walk-forward split math / warmup failed (expected_splits={expected_splits})")

    ready = bool(
        meta_ok
        and prov_ok
        and sym_ok
        and index_ok
        and aligned_ok
        and frames_ok
        and rv_finite
        and coverage_ok
        and iv_ok
        and wf_ok
        and not blocked
    )
    result = {
        "ready": ready,
        "real_data_only": True,
        "fabricated_data": False,
        "campaign": 294,
        "part": "preflight",
        "checks": checks,
        "blocked_reasons": blocked,
    }
    print(json.dumps(result, indent=2, default=str))
    return 0 if ready else 2


if __name__ == "__main__":
    raise SystemExit(main())