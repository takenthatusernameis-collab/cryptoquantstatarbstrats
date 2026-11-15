#!/usr/bin/env python3
"""C308 preflight: fail-closed verification of the real C307 cache before the C308
runner validates the C307 edge.

Verifies:
- the C307 pickle exists, SHA256-from-bytes matches meta, meta flags
  (real_data_only:true, fabricated_data:false, executed_fills:false),
  interval/source/host/format/push-limit are intact;
- the common funding grid (Leg B) is non-empty, restricted to 2022-07..2026-06,
  with >= 2 (indeed >= 10 for K=5) assets having finite funding overlap;
- the 44 C307 edge configs are REPRODUCIBLE from the cache: re-running the
  pre-registered Leg B sweep over the cache yields exactly 432 runs with
  44 costed-OOS edge-proven configs (all Leg B, gate=off,
  L in {720,1440}, K in {2,3,5}, holds {1,6,24});
- the C307 sweep artifact set exists with real-data flags and SHA256-from-bytes.

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
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import run_c308_c307_edge_validation_oos as c308  # noqa: E402

CACHE = ROOT / "data" / "cache" / "campaign307_coinm_multiasset_term_structure_carry.pkl"
CACHE_META = ROOT / "data" / "cache" / "campaign307_coinm_multiasset_term_structure_carry.meta.json"
CACHE_PROV = ROOT / "data" / "cache" / "campaign307_coinm_multiasset_term_structure_carry.provenance.json"
PUSH_LIMIT_BYTES = 100_000_000

EXPECTED_INTERVAL = "1h"
EXPECTED_SOURCE_INTERVAL = "coin_m_klines_1h"
EXPECTED_N_EDGE_LEG_B = 44
EXPECTED_N_RUNS_LEG_B = 432


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _as_index(pa: dict) -> pd.DatetimeIndex:
    idx = pa.get("index")
    if isinstance(idx, pd.DatetimeIndex):
        return idx
    arr = np.asarray(idx)
    if np.issubdtype(arr.dtype, np.datetime64):
        return pd.DatetimeIndex(arr).tz_localize("UTC")
    return pd.DatetimeIndex(pd.to_datetime(arr, unit="ms", utc=True))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.parse_args()

    checks: dict = {}
    blocked: list[str] = []

    if not CACHE.exists():
        print(json.dumps({"ready": False, "blocked_reasons": ["C307 pickle missing"]}, indent=2))
        return 1
    pkl_sha = sha256_file(CACHE)
    pkl_bytes = CACHE.stat().st_size

    try:
        meta = json.loads(CACHE_META.read_text())
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
        with open(CACHE, "rb") as fh:
            payload = pickle.load(fh)
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"ready": False, "blocked_reasons": [f"cache could not be loaded: {exc}"]}, indent=2))
        return 1

    leg_b = payload.get("leg_b") or {}
    leg_b_symbols = leg_b.get("symbols") or []
    n_leg_b_symbols = len(leg_b_symbols)
    n_fund = int(leg_b.get("n_bars") or 0)
    leg_b_index = _as_index(leg_b) if "index" in leg_b else None

    if leg_b_index is None or len(leg_b_index) == 0:
        blocked.append("Leg B common funding grid is empty")
    else:
        start_ok = leg_b_index[0] >= pd.Timestamp("2022-07-01", tz="UTC")
        end_ok = leg_b_index[-1] < pd.Timestamp("2026-07-01", tz="UTC")
        if not (start_ok and end_ok):
            blocked.append(f"Leg B funding grid outside 2022-07..2026-06: start={leg_b_index[0]}, end={leg_b_index[-1]}")
    checks["leg_b_grid"] = {
        "n_symbols": n_leg_b_symbols,
        "symbols": leg_b_symbols,
        "window_start_utc": leg_b.get("window_start_utc"),
        "window_end_utc": leg_b.get("window_end_utc"),
        "n_bars": n_fund,
        "start_utc": str(leg_b_index[0]) if leg_b_index is not None and len(leg_b_index) else None,
        "end_utc": str(leg_b_index[-1]) if leg_b_index is not None and len(leg_b_index) else None,
    }

    n_assets_fund = int(leg_b.get("n_assets_with_funding") or 0)
    if n_assets_fund < 10:
        blocked.append(f"Leg B has {n_assets_fund} assets with finite funding overlap (< 10 needed for K=5)")

    leg_b_detail = {}
    leg_b_ok = True
    for s in leg_b_symbols:
        d = {"symbol": s, "fields": {}, "ok": True}
        all_field_ok = True
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
        fp_key = f"funding_present_{s}"
        if fp_key in leg_b:
            fp = np.asarray(leg_b[fp_key], dtype=float)
            d["fields"][fp_key] = {"sum": int(fp.sum()), "ok": bool(fp.sum() > 0)}
            all_field_ok &= d["fields"][fp_key]["ok"]
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
        "n_symbols": n_leg_b_symbols, "n_bars": n_fund,
        "n_assets_with_funding": n_assets_fund, "detail": leg_b_detail, "ok": bool(leg_b_ok),
    }
    if not leg_b_ok:
        blocked.append("one or more Leg B symbols failed perp/funding/premium/mark checks")

    # Build the Leg B series (mirrors the runner) for the reproducibility sweep.
    lb = c308.build_leg_b_series(leg_b)

    # Reproduce the 44 C307 edge configs from cache (Leg B sweep only).
    results = []
    c308.sweep_leg_b(lb, results)
    n_runs_b = len(results)
    edge_runs_b = [r for r in results if r["edge_proven"]]
    n_edge_b = len(edge_runs_b)
    edge_signals = sorted(set(r["signal"] for r in edge_runs_b))
    edge_lookbacks = sorted(set(r["lookback"] for r in edge_runs_b))
    edge_K = sorted(set(r["K"] for r in edge_runs_b))
    edge_holds = sorted(set(r["hold"] for r in edge_runs_b))
    edge_gates = sorted(set(r["gate"] for r in edge_runs_b))

    repro_ok = (
        n_runs_b == EXPECTED_N_RUNS_LEG_B
        and n_edge_b == EXPECTED_N_EDGE_LEG_B
        and set(edge_signals) <= {"fund_level", "fund_z", "fund_sign"}
        and set(edge_lookbacks) <= {720, 1440}
        and set(edge_K) <= {2, 3, 5}
        and set(edge_holds) <= {1, 6, 24}
        and set(edge_gates) <= {"off"}
    )
    checks["leg_b_reproducibility"] = {
        "n_runs": int(n_runs_b),
        "n_edge_proven": int(n_edge_b),
        "expected_n_runs": EXPECTED_N_RUNS_LEG_B,
        "expected_n_edge": EXPECTED_N_EDGE_LEG_B,
        "edge_signals": edge_signals,
        "edge_lookbacks": edge_lookbacks,
        "edge_K": edge_K,
        "edge_holds": edge_holds,
        "edge_gates": edge_gates,
        "ok": bool(repro_ok),
    }
    if not repro_ok:
        blocked.append(
            f"Leg B edge not reproducible from cache: runs={n_runs_b} (expected {EXPECTED_N_RUNS_LEG_B}), "
            f"edge={n_edge_b} (expected {EXPECTED_N_EDGE_LEG_B})"
        )

    # C307 sweep artifact set exists with real-data flags and SHA256-from-bytes.
    c307_parts = ("oos_sweep", "tradable_edge_registry", "summary", "verdict")
    c307_artifact_ok = True
    c307_artifact_detail = {}
    for part in c307_parts:
        matches = sorted(ROOT.glob(f"reports/campaign307_{part}_*.json"))
        c307_artifact_detail[part] = {"exists": bool(matches), "latest": matches[-1].name if matches else None}
        if not matches:
            c307_artifact_ok = False
            blocked.append(f"missing C307 artifact for {part}")
            continue
        payload_art = json.loads(matches[-1].read_text())
        c307_artifact_detail[part]["real_data_only"] = payload_art.get("real_data_only")
        c307_artifact_detail[part]["fabricated_data"] = payload_art.get("fabricated_data")
        c307_artifact_detail[part]["executed_fills"] = payload_art.get("executed_fills")
        ok_flags = (payload_art.get("real_data_only") is True
                    and payload_art.get("fabricated_data") is False
                    and payload_art.get("executed_fills") is False)
        c307_artifact_detail[part]["flags_ok"] = bool(ok_flags)
        if not ok_flags:
            c307_artifact_ok = False
            blocked.append(f"C307 artifact {part} provenance flags not real_data_only/fabricated_data")
    checks["c307_artifacts"] = {"detail": c307_artifact_detail, "ok": bool(c307_artifact_ok)}

    checks["provenance"] = {
        "path": str(CACHE_PROV.relative_to(ROOT)) if CACHE_PROV.exists() else str(CACHE_PROV),
        "exists": CACHE_PROV.exists(),
        "ok": bool(CACHE_PROV.exists()),
    }
    if not CACHE_PROV.exists():
        blocked.append("provenance json missing")

    ready = not blocked
    result = {
        "ready": ready,
        "real_data_only": True,
        "fabricated_data": False,
        "executed_fills": False,
        "campaign": 308,
        "part": "preflight",
        "checks": checks,
        "blocked_reasons": blocked,
    }
    print(json.dumps(result, indent=2, default=str))
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
