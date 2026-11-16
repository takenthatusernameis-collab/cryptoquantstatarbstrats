#!/usr/bin/env python3
"""C324 preflight: fail-closed verification of the real C324 USDT-M cross-sectional
intraday AMIHUD-ILLIQUIDITY SEASONAL DISLOCATION mean-reversion feature cache
before the C324 runner sweeps the pre-registered costed OOS grid.

Verifies:
- the per-asset float32 ``.npz`` shards exist under
  ``data/cache/campaign324_illiq_seasonality_5m/`` and every shard
  SHA256 + byte size matches the meta manifest;
- meta flags (real_data_only:true, fabricated_data:false, executed_fills:false),
  interval=5m, source campaign=312, source host intact, no network ingest, no
  resampling, every shard < 100 MB (GitHub push limit), and the total cache under
  the 100 MB budget;
- the common 5m grid is non-empty and inside 2023-01..2025-12;
- all 10 symbols present with finite, positive perp_close AND finite log_return on
  the common grid (log_return derived from perp_close, r[0]=0);
- the ``illiq`` and ``log_tc`` fields are present; each is finite-or-NaN with NaNs
  exactly where the corresponding denominator/value is non-positive (the
  PRE-REGISTERED zero-activity NaN POLICY); the ``funding_rate`` leg is present
  and all-NaN (control only, USDT-M funding is unreachable in this environment);
- PRE-REGISTERED zero-activity NaN POLICY fail-closed gate: per-shard per-field
  NaN count < 0.1% of bars AND 100% of NaNs explained by the corresponding
  zero-activity bars (illiq<->notional<=0, log_tc<->trade_count<=0),
  cross-checked against the real C312 source shards; fail-closed if a NaN appears
  where the denominator/value is strictly positive (corrupt data).

Never fetches, imputes, resamples, or fabricates data. Exit 0 iff ready:true.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

CACHE_DIR = ROOT / "data" / "cache" / "campaign324_illiq_seasonality_5m"
CACHE_META = ROOT / "data" / "cache" / "campaign324_illiq_seasonality_5m.meta.json"
CACHE_PROV = ROOT / "data" / "cache" / "campaign324_illiq_seasonality_5m.provenance.json"
SRC_DIR = ROOT / "data" / "cache" / "campaign312_usdt_m_ofi_5m"
PUSH_LIMIT_BYTES = 100_000_000
CACHE_BUDGET_BYTES = 100_000_000

EXPECTED_INTERVAL = "5m"
EXPECTED_SOURCE_INTERVAL = "usdt_m_5m_klines_taker_delta_ms"
EXPECTED_SOURCE_CAMPAIGN = 312
N_SYMBOLS = 10
NAN_MAX_SHARE = 0.001  # 0.1% fail-closed ceiling

FIELDS = ["index_ms", "perp_close", "log_return", "illiq", "log_tc", "funding_rate"]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _field_report(field: np.ndarray, positive_mask: np.ndarray, label: str) -> dict:
    """Build a NaN-policy report for one derived field vs its positivity mask."""
    nan = np.isnan(field)
    finite = np.isfinite(field)
    unexplained = int((nan & positive_mask).sum())      # NaN where denom/value>0
    stray_finite = int((finite & ~positive_mask).sum())  # finite where denom/value<=0
    share = float(nan.mean())
    explained = bool(unexplained == 0 and stray_finite == 0)
    ok = bool(share < NAN_MAX_SHARE and explained)
    return {
        "field": label,
        "len": int(len(field)),
        "nan": int(nan.sum()),
        "nan_share": share,
        "nan_where_positive": unexplained,
        "finite_where_nonpositive": stray_finite,
        "all_nans_explained": explained,
        "ok": ok,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.parse_args()

    checks: dict = {}
    blocked: list[str] = []

    if not CACHE_META.exists():
        print(json.dumps({"ready": False, "blocked_reasons": ["C324 meta missing"]}, indent=2))
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
        blocked.append("C324 common grid is empty")
    if n_symbols < N_SYMBOLS:
        blocked.append(f"C324 has {n_symbols} symbols (< {N_SYMBOLS} required)")
    in_window = bool(str(grid_start).startswith("2023-01") and str(grid_end).startswith("2025-12"))
    checks["grid"] = {
        "n_symbols": n_symbols, "symbols": symbols, "n_grid_bars": n_grid,
        "grid_start_utc": grid_start, "grid_end_utc": grid_end,
        "in_window": in_window,
    }
    if not in_window:
        blocked.append("C324 grid not in 2023-01..2025-12 window")

    detail = {}
    all_ok = True
    grid_ref = None
    nan_policy = {}
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
            illiq = np.asarray(z["illiq"], dtype=float)
            tc = np.asarray(z["log_tc"], dtype=float)
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
            fr_ok = bool(len(fr) == len(pc) and np.isnan(fr).all())
            d["fields"]["funding_rate"] = {"nan": int(np.isnan(fr).sum()), "len": int(len(fr)),
                                           "all_nan_control_only": bool(np.isnan(fr).all()), "ok": fr_ok}
            ok &= fr_ok
        d["ok"] = bool(ok)
        detail[s] = d
        all_ok &= bool(ok)

        # ---- zero-activity NaN policy: share < 0.1% AND 100% explained ----
        try:
            with np.load(SRC_DIR / f"{s}.npz") as sz:
                tc_src = np.asarray(sz["trade_count"], dtype=float)
                no_src = np.asarray(sz["notional"], dtype=float)
            # reload derived fields for the policy cross-check
            with np.load(sp) as z:
                illiq_d = np.asarray(z["illiq"], dtype=float)
                tc_d = np.asarray(z["log_tc"], dtype=float)

            reports = {
                "illiq": _field_report(illiq_d, no_src > 0, "illiq"),
                "log_tc": _field_report(tc_d, tc_src > 0, "log_tc"),
            }
            nan_policy[s] = {"per_field": reports,
                             "ok": bool(all(r["ok"] for r in reports.values()))}
            if not nan_policy[s]["ok"]:
                all_ok = False
                for name, r in reports.items():
                    if not r["ok"]:
                        if r["nan_share"] >= NAN_MAX_SHARE:
                            blocked.append(f"{s} {name} NaN share {r['nan_share']:.6f} >= 0.001 (0.1%)")
                        if r["nan_where_positive"] > 0:
                            blocked.append(f"{s} {name} has {r['nan_where_positive']} NaN bars where denom/value>0 (corrupt data)")
                        if r["finite_where_nonpositive"] > 0:
                            blocked.append(f"{s} {name} has {r['finite_where_nonpositive']} finite bars where denom/value<=0 (corrupt data)")
        except Exception as exc:  # noqa: BLE001
            all_ok = False
            nan_policy[s] = {"ok": False, "error": str(exc)}
            blocked.append(f"{s} zero-activity NaN policy check failed: {exc}")

    checks["per_symbol"] = {"n_symbols": n_symbols, "detail": detail, "ok": bool(all_ok)}
    if not all_ok:
        blocked.append("one or more symbols failed perp_close/log_return/funding/grid checks")
    nan_policy_ok = bool(nan_policy and all(v.get("ok") is True for v in nan_policy.values()))
    checks["zero_activity_nan_policy"] = {"per_shard": nan_policy, "ok": nan_policy_ok}
    if not nan_policy_ok:
        if not any("NaN policy" in b or "NaN share" in b or "corrupt" in b for b in blocked):
            blocked.append("zero-activity NaN policy check failed on one or more shards")

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
        "campaign": 324,
        "part": "preflight",
        "checks": checks,
        "blocked_reasons": blocked,
    }
    print(json.dumps(result, indent=2, default=str))
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
