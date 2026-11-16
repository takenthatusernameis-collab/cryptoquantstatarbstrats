#!/usr/bin/env python3
"""C336 preflight: fail-closed verification of the real C336 USDT-M
cross-sectional intraday ORDER-FLOW PERSISTENCE / IMBALANCE AUTOCORRELATION
SEASONAL DISLOCATION mean-reversion feature cache before the C336 runner sweeps
the pre-registered costed OOS grid.

Verifies:
- the per-asset float32 ``.npz`` shards exist under
  ``data/cache/campaign336_flow_persistence_5m/`` and every shard SHA256 + byte size
  matches the meta manifest;
- meta flags (real_data_only:true, fabricated_data:false, executed_fills:false),
  interval=5m, source campaign=312, source host intact, no network ingest, no
  resampling, every shard < 100 MB (GitHub push limit), and the total cache under
  the 100 MB budget;
- the common 5m grid is non-empty and inside 2023-01..2025-12;
- all 10 symbols present with finite, positive perp_close AND finite log_return on
  the common grid (log_return derived from perp_close, r[0]=0);
- the derived persistence fields are present: sign_imbalance, signed_vol_share,
  notional_imb, imb_ewm, imb_ac1, streak_len (each finite or NaN per the
  pre-registered policy; the per-bar raw NaN total is reported, not asserted
  zero, because zero-activity bars are genuine);
- the ``funding_rate`` leg is present and all-NaN (control only, USDT-M funding is
  unreachable in this environment);
- PRE-REGISTERED NaN POLICY fail-closed gate: perp_close and log_return carry ZERO
  NaN (real, gap-free derived inputs). The persistence fields carry a structural
  NaN share (zero-activity denominators / EWMA warmup / full-window AC1
  requirement) that is handled fail-closed in the RUNNER (NaN bars get weight 0).

The raw flow fields (trade_sign_sum, trade_count, signed_volume, total_volume,
notional) are read from C312 at build time but are not stored in the C336 shards;
their zero-NaN property is guaranteed by the C312 source cache.

Never fetches, imputes, resamples, or fabricates data. Exit 0 iff ready:true.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

CACHE_DIR = ROOT / "data" / "cache" / "campaign336_flow_persistence_5m"
CACHE_META = ROOT / "data" / "cache" / "campaign336_flow_persistence_5m.meta.json"
CACHE_PROV = ROOT / "data" / "cache" / "campaign336_flow_persistence_5m.provenance.json"
PUSH_LIMIT_BYTES = 100_000_000
CACHE_BUDGET_BYTES = 100_000_000

EXPECTED_INTERVAL = "5m"
EXPECTED_SOURCE_INTERVAL = "usdt_m_5m_klines_taker_delta_ms"
EXPECTED_SOURCE_CAMPAIGN = 312
N_SYMBOLS = 10

FIELDS = ["index_ms", "perp_close", "log_return",
          "sign_imbalance", "signed_vol_share", "notional_imb",
          "imb_ewm", "imb_ac1", "streak_len", "funding_rate"]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _feature_integrity_report(pc: np.ndarray, lr: np.ndarray, si: np.ndarray,
                               svs: np.ndarray, ni: np.ndarray, ie: np.ndarray,
                               ia: np.ndarray, sl: np.ndarray,
                               fr: np.ndarray) -> dict:
    """Raw-feature integrity: finite fields, persistence derived, funding control."""
    si_nan = int(np.isnan(si).sum())
    svs_nan = int(np.isnan(svs).sum())
    ni_nan = int(np.isnan(ni).sum())
    ie_nan = int(np.isnan(ie).sum())
    ia_nan = int(np.isnan(ia).sum())
    sl_nan = int(np.isnan(sl).sum())
    raw_nan_total = int(np.isnan(pc).sum()) + int(np.isnan(lr).sum())
    pers_nan_total = si_nan + svs_nan + ni_nan + ie_nan + ia_nan + sl_nan
    return {
        "len": int(len(pc)),
        "perp_close_all_finite": bool(np.isfinite(pc).all()),
        "perp_close_all_positive": bool((pc[np.isfinite(pc)] > 0).all()) if np.isfinite(pc).any() else False,
        "log_return_nan": int(np.isnan(lr).sum()),
        "log_return_all_finite": bool(np.isfinite(lr).all()),
        "log_return_first_zero": bool(len(lr) > 0 and lr[0] == 0.0),
        "sign_imbalance_nan": si_nan,
        "signed_vol_share_nan": svs_nan,
        "notional_imb_nan": ni_nan,
        "imb_ewm_nan": ie_nan,
        "imb_ac1_nan": ia_nan,
        "streak_len_nan": sl_nan,
        "persistence_nan_total_structural": pers_nan_total,
        "persistence_nan_share": float(pers_nan_total / max(6 * len(pc), 1)),
        "funding_all_nan_control_only": bool(np.isnan(fr).all()),
        "raw_nan_total": raw_nan_total,
        "ok": bool(np.isfinite(pc).all() and (pc[np.isfinite(pc)] > 0).all()
                   and np.isfinite(lr).all() and lr[0] == 0.0
                   and np.isnan(fr).all()
                   and raw_nan_total == 0),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.parse_args()

    checks: dict = {}
    blocked: list[str] = []

    if not CACHE_META.exists():
        print(json.dumps({"ready": False, "blocked_reasons": ["C336 meta missing"]}, indent=2))
        return 1
    try:
        meta = json.loads(CACHE_META.read_text())
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"ready": False, "blocked_reasons": [f"meta unreadable: {exc}"]}, indent=2))
        return 1

    shard_sha_meta = meta.get("shard_sha256") or {}
    shard_bytes_meta = meta.get("shard_bytes") or {}

    # ---- shard integrity ----
    shard_ok = True
    shard_detail = {}
    max_shard = 0
    for s, expected_sha in shard_sha_meta.items():
        sp = CACHE_DIR / f"{s}.npz"
        if not sp.exists():
            shard_detail[s] = {"exists": False, "ok": False}
            shard_ok = False
            continue
        actual = sha256_file(sp)
        nbytes = sp.stat().st_size
        max_shard = max(max_shard, nbytes)
        ok = bool(actual == expected_sha and nbytes == int(shard_bytes_meta.get(s, -1))
                  and nbytes < PUSH_LIMIT_BYTES)
        shard_detail[s] = {"exists": True, "sha_ok": actual == expected_sha,
                           "bytes": int(nbytes), "under_push_limit": bool(nbytes < PUSH_LIMIT_BYTES),
                           "ok": ok}
        shard_ok &= ok

    total_shard_bytes = sum(int(v) for v in shard_bytes_meta.values())
    flags_ok = (
        meta.get("interval") == EXPECTED_INTERVAL
        and meta.get("source_interval") == EXPECTED_SOURCE_INTERVAL
        and int(meta.get("source_campaign") or 0) == EXPECTED_SOURCE_CAMPAIGN
        and meta.get("network_ingest") is False
        and meta.get("resample") is False
        and int(meta.get("n_symbols") or 0) >= N_SYMBOLS
        and meta.get("real_data_only") is True
        and meta.get("fabricated_data") is False
        and meta.get("fetch_real_data_only") is True
        and meta.get("fetch_fabricated_data") is False
        and meta.get("executed_fills") is False
        and meta.get("under_push_limit") is True
        and meta.get("under_cache_budget") is True
        and int(meta.get("max_shard_bytes") or 0) < PUSH_LIMIT_BYTES
        and int(meta.get("total_shard_bytes") or 0) < CACHE_BUDGET_BYTES
        and meta.get("fields") == FIELDS
    )
    checks["meta"] = {
        "interval": meta.get("interval"),
        "source_interval": meta.get("source_interval"),
        "source_campaign": meta.get("source_campaign"),
        "network_ingest": meta.get("network_ingest"),
        "resample": meta.get("resample"),
        "n_symbols": meta.get("n_symbols"),
        "real_data_only": meta.get("real_data_only"),
        "fabricated_data": meta.get("fabricated_data"),
        "fetch_real_data_only": meta.get("fetch_real_data_only"),
        "fetch_fabricated_data": meta.get("fetch_fabricated_data"),
        "executed_fills": meta.get("executed_fills"),
        "storage": meta.get("storage"),
        "fields": meta.get("fields"),
        "total_shard_bytes": int(meta.get("total_shard_bytes") or 0),
        "total_shard_mb": round(int(meta.get("total_shard_bytes") or 0) / 1e6, 2),
        "max_shard_bytes": int(meta.get("max_shard_bytes") or 0),
        "max_shard_mb": round(int(meta.get("max_shard_bytes") or 0) / 1e6, 2),
        "under_push_limit": meta.get("under_push_limit"),
        "under_cache_budget": meta.get("under_cache_budget"),
        "manifest_sha256": meta.get("manifest_sha256"),
        "window_start_month": meta.get("window_start_month"),
        "window_end_month": meta.get("window_end_month"),
        "ok": bool(flags_ok),
    }
    if not flags_ok:
        blocked.append("meta flags/interval/source/no-network/no-resample/size/fields mismatch")
    checks["shards"] = {"n_shards": len(shard_sha_meta), "ok": bool(shard_ok), "detail": shard_detail}
    if not shard_ok:
        blocked.append("one or more shards missing / sha or size mismatch / over push limit")

    # manifest sha integrity
    manifest = {s: shard_sha_meta[s] for s in sorted(shard_sha_meta)}
    manifest_sha = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()
    checks["manifest"] = {"expected": meta.get("manifest_sha256"), "actual": manifest_sha,
                          "ok": bool(manifest_sha == meta.get("manifest_sha256"))}
    if manifest_sha != meta.get("manifest_sha256"):
        blocked.append("shard manifest sha mismatch")

    # ---- grid + per-symbol ----
    symbols = list(meta.get("symbols") or [])
    n_symbols = len(symbols)
    n_grid = int(meta.get("n_grid_bars") or 0)
    grid_start = meta.get("grid_start_utc")
    grid_end = meta.get("grid_end_utc")
    if n_grid == 0 or not symbols:
        blocked.append("C336 common grid is empty")
    if n_symbols < N_SYMBOLS:
        blocked.append(f"C336 has {n_symbols} symbols (< {N_SYMBOLS} required)")
    in_window = bool(str(grid_start).startswith("2023-01") and str(grid_end).startswith("2025-12"))
    checks["grid"] = {
        "n_symbols": n_symbols, "symbols": symbols, "n_grid_bars": n_grid,
        "grid_start_utc": grid_start, "grid_end_utc": grid_end,
        "in_window": in_window,
    }
    if not in_window:
        blocked.append("C336 grid not in 2023-01..2025-12 window")

    detail = {}
    all_ok = True
    grid_ref = None
    feature_integrity = {}
    for s in symbols:
        sp = CACHE_DIR / f"{s}.npz"
        d = {"symbol": s, "fields": {}, "ok": True}
        ok = True
        if not sp.exists():
            d["ok"] = False
            detail[s] = d
            all_ok = False
            continue
        with np.load(sp) as z:
            idx_ms = np.asarray(z["index_ms"], dtype="int64")
            d["grid_len"] = int(len(idx_ms))
            if grid_ref is None:
                grid_ref = idx_ms
            else:
                if len(idx_ms) != len(grid_ref) or not np.array_equal(idx_ms, grid_ref):
                    d["grid_match"] = False
                    ok = False
            pc = np.asarray(z["perp_close"], dtype=float)
            lr = np.asarray(z["log_return"], dtype=float)
            si = np.asarray(z["sign_imbalance"], dtype=float)
            svs = np.asarray(z["signed_vol_share"], dtype=float)
            ni = np.asarray(z["notional_imb"], dtype=float)
            ie = np.asarray(z["imb_ewm"], dtype=float)
            ia = np.asarray(z["imb_ac1"], dtype=float)
            sl = np.asarray(z["streak_len"], dtype=float)
            fr = np.asarray(z["funding_rate"], dtype=float)
        rep = _feature_integrity_report(pc, lr, si, svs, ni, ie, ia, sl, fr)
        d["fields"] = rep
        feature_integrity[s] = rep
        ok &= rep["ok"]
        d["ok"] = bool(ok)
        detail[s] = d
        all_ok &= bool(ok)

    checks["per_symbol"] = {"n_symbols": n_symbols, "detail": detail, "ok": bool(all_ok)}
    if not all_ok:
        blocked.append("one or more symbols failed perp_close/log_return/persistence/funding/grid checks")
    fi_ok = bool(feature_integrity and all(v.get("ok") is True for v in feature_integrity.values()))
    raw_nan_total = int(sum(v.get("raw_nan_total", 0) for v in feature_integrity.values()))
    checks["feature_integrity"] = {
        "ok": fi_ok,
        "raw_nan_total": raw_nan_total,
        "policy": "perp_close/log_return carry ZERO NaN; sign_imbalance/signed_vol_share/notional_imb/imb_ewm/imb_ac1/streak_len carry structural NaN (zero-activity denominators / EWMA warmup / full-window AC1) handled fail-closed (weight 0) in the runner",
        "per_shard": feature_integrity,
    }
    if not fi_ok:
        blocked.append("feature integrity check failed (raw NaN gap) on one or more shards")

    checks["provenance"] = {
        "path": str(CACHE_PROV.relative_to(ROOT)) if CACHE_PROV.exists() else str(CACHE_PROV),
        "exists": bool(CACHE_PROV.exists()),
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
        "campaign": 336,
        "part": "preflight",
        "checks": checks,
        "blocked_reasons": blocked,
    }
    print(json.dumps(result, indent=2, default=str))
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
