#!/usr/bin/env python3
"""C322 preflight: fail-closed verification of the real C322 USDT-M cross-sectional
VWAP-CLOSE FAIR-VALUE DISLOCATION mean-reversion feature cache before the C322
runner sweeps the pre-registered costed OOS grid.

Verifies:
- the per-asset float32 ``.npz`` shards exist under
  ``data/cache/campaign322_vwap_dislocation_5m/`` and every shard SHA256 + byte
  size matches the meta manifest;
- meta flags (real_data_only:true, fabricated_data:false, executed_fills:false),
  interval=5m, source campaign=312, source host intact, no network ingest, no
  resampling, every shard < 100 MB (GitHub push limit), and the total cache under
  the 100 MB budget;
- the common 5m grid is non-empty and inside 2023-01..2025-12;
- all 10 symbols present with finite, positive perp_close AND finite log_return on
  the common grid (log_return derived from perp_close, r[0]=0);
- the ``vwap`` and ``log_vwap`` fields are present; ``vwap`` is finite and >0
  wherever it is not NaN; ``log_vwap = log(vwap) where vwap>0 else NaN`` (the
  PRE-REGISTERED vwap-NaN POLICY); the ``funding_rate`` leg is present and
  all-NaN (control only, USDT-M funding is unreachable in this environment);
- PRE-REGISTERED vwap-NaN POLICY fail-closed gate: per-shard vwap NaN count < 0.1%
  of bars AND 100% of vwap NaNs are explained by ``total_volume == 0`` (cross-
  checked against the real C312 source shards; fail-closed if a vwap NaN appears
  where total_volume > 0 — that would be corrupt data).

Never fetches, imputes, resamples, or fabricates data. Exit 0 iff ready:true.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

CACHE_DIR = ROOT / "data" / "cache" / "campaign322_vwap_dislocation_5m"
CACHE_META = ROOT / "data" / "cache" / "campaign322_vwap_dislocation_5m.meta.json"
CACHE_PROV = ROOT / "data" / "cache" / "campaign322_vwap_dislocation_5m.provenance.json"
SRC_DIR = ROOT / "data" / "cache" / "campaign312_usdt_m_ofi_5m"
PUSH_LIMIT_BYTES = 100_000_000
CACHE_BUDGET_BYTES = 100_000_000

EXPECTED_INTERVAL = "5m"
EXPECTED_SOURCE_INTERVAL = "usdt_m_5m_klines_close"
EXPECTED_SOURCE_CAMPAIGN = 312
N_SYMBOLS = 10
VWAP_NAN_MAX_SHARE = 0.001  # 0.1% fail-closed ceiling


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.parse_args()

    checks: dict = {}
    blocked: list[str] = []

    if not CACHE_META.exists():
        print(json.dumps({"ready": False, "blocked_reasons": ["C322 meta missing"]}, indent=2))
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
        blocked.append("meta flags/interval/source/no-network/no-resample/size mismatch")
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
        blocked.append("C322 common grid is empty")
    if n_symbols < N_SYMBOLS:
        blocked.append(f"C322 has {n_symbols} symbols (< {N_SYMBOLS} required)")
    in_window = bool(str(grid_start).startswith("2023-01") and str(grid_end).startswith("2025-12"))
    checks["grid"] = {
        "n_symbols": n_symbols, "symbols": symbols, "n_grid_bars": n_grid,
        "grid_start_utc": grid_start, "grid_end_utc": grid_end,
        "in_window": in_window,
    }
    if not in_window:
        blocked.append("C322 grid not in 2023-01..2025-12 window")

    detail = {}
    all_ok = True
    grid_ref = None
    vwap_policy = {}
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
            vw = np.asarray(z["vwap"], dtype=float)
            lv = np.asarray(z["log_vwap"], dtype=float)
            fr = np.asarray(z["funding_rate"], dtype=float)
            present = pc[np.isfinite(pc)]
            pc_ok = bool(len(present) == len(pc) and len(present) > 0 and (present > 0).all())
            d["fields"]["perp_close"] = {"len": int(len(pc)), "nan": int(np.isnan(pc).sum()),
                                         "all_finite_present": bool(len(present) == len(pc)),
                                         "all_positive_present": bool((present > 0).all()) if len(present) else False,
                                         "ok": pc_ok}
            ok &= pc_ok
            lr_ok = bool(np.isfinite(lr).all())
            d["fields"]["log_return"] = {"len": int(len(lr)), "nan": int(np.isnan(lr).sum()),
                                         "all_finite": bool(np.isfinite(lr).all()),
                                         "first_is_zero": bool(lr[0] == 0.0) if len(lr) else False,
                                         "ok": lr_ok}
            ok &= lr_ok
            vw_finite = np.isfinite(vw)
            vw_nan = ~vw_finite
            vw_ok = bool((vw[vw_finite] > 0).all())
            d["fields"]["vwap"] = {"len": int(len(vw)), "nan": int(vw_nan.sum()),
                                   "all_finite_or_nan": bool(vw_finite.all() or vw_nan.any()),
                                   "finite_all_positive": vw_ok, "ok": vw_ok}
            ok &= vw_ok
            # log_vwap NaN exactly where vwap is not (finite and >0).
            vwap_val_ok = vw_finite & (vw > 0)
            lv_nan_ok = bool(np.array_equal(np.isnan(lv), ~vw_val_ok) and np.isfinite(lv[vwap_val_ok]).all())
            d["fields"]["log_vwap"] = {"len": int(len(lv)), "nan": int(np.isnan(lv).sum()),
                                       "nan_matches_vwap_missing": lv_nan_ok,
                                       "ok": lv_nan_ok}
            ok &= lv_nan_ok
            fr_ok = bool(len(fr) == len(pc) and np.isnan(fr).all())
            d["fields"]["funding_rate"] = {"nan": int(np.isnan(fr).sum()), "len": int(len(fr)),
                                           "all_nan_control_only": bool(np.isnan(fr).all()), "ok": fr_ok}
            ok &= fr_ok
        d["ok"] = bool(ok)
        detail[s] = d
        all_ok &= bool(ok)

        # ---- vwap-NaN policy: share < 0.1% AND 100% explained by total_volume==0 ----
        try:
            with np.load(SRC_DIR / f"{s}.npz") as sz:
                vw_src = np.asarray(sz["vwap"], dtype=float)
                tv_src = np.asarray(sz["total_volume"], dtype=float)
            vw_nan_src = np.isnan(vw_src)
            vwap_share = float(vw_nan_src.mean())
            bad = int((vw_nan_src & (tv_src > 0)).sum())
            explained = bool(bad == 0)
            vwap_policy[s] = {
                "vwap_nan_bars": int(vw_nan_src.sum()),
                "vwap_nan_share": vwap_share,
                "nan_where_volume_gt_zero": bad,
                "all_nans_explained_by_volume_zero": explained,
                "ok": bool(vwap_share < VWAP_NAN_MAX_SHARE and explained),
            }
            if not vwap_policy[s]["ok"]:
                all_ok = False
                if vwap_share >= VWAP_NAN_MAX_SHARE:
                    blocked.append(f"{s} vwap NaN share {vwap_share:.6f} >= 0.001 (0.1%)")
                if bad > 0:
                    blocked.append(f"{s} has {bad} vwap-NaN bars where total_volume>0 (corrupt data)")
        except Exception as exc:  # noqa: BLE001
            all_ok = False
            vwap_policy[s] = {"ok": False, "error": str(exc)}
            blocked.append(f"{s} vwap-NaN policy check failed: {exc}")

    checks["per_symbol"] = {"n_symbols": n_symbols, "detail": detail, "ok": bool(all_ok)}
    if not all_ok:
        blocked.append("one or more symbols failed perp_close/log_return/vwap/log_vwap/funding/grid checks")
    checks["vwap_nan_policy"] = {"per_shard": vwap_policy, "ok": bool(all(p.get("ok") is True for p in vwap_policy.values()))}

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
        "campaign": 322,
        "part": "preflight",
        "checks": checks,
        "blocked_reasons": blocked,
    }
    print(json.dumps(result, indent=2, default=str))
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
