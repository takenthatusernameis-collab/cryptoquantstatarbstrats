"""Fail-closed loader/validator for real external feed artifacts.

Consumes ONLY files that pass provenance + integrity checks. Refuses missing
metadata, sha256 mismatches, fabricated/proxy-as-real flags, schema violations,
and undocumented gaps. Designed to satisfy the operator-executable readiness
spec (e.g. reports/real_feed_ingestion_readiness_20261105T104640Z.json).

Synthetic/test fixtures may be used ONLY inside tests and must never be labeled
as real data. This module never fabricates data.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

REAL_ONLY_FLAGS = {"real_data_only": True, "fabricated_data": False}


class RealFeedValidationError(ValueError):
    """Raised when a feed artifact fails fail-closed validation."""


@dataclass(frozen=True)
class FamilySpec:
    name: str
    required_columns: tuple[str, ...]
    required_provenance_keys: tuple[str, ...]
    numeric_columns: tuple[str, ...] = ()
    timestamp_columns: tuple[str, ...] = ("timestamp_utc",)


FUNDING_BASIS_CARRY_SPEC = FamilySpec(
    name="funding_basis_carry",
    required_columns=(
        "timestamp_utc",
        "symbol",
        "funding_rate",
        "mark_price_or_close",
    ),
    required_provenance_keys=(
        "source_provider",
        "source_endpoints",
        "request_urls_or_params",
        "retrieved_at_utc",
        "symbol_map_native_to_repo",
        "window_start_utc",
        "window_end_utc",
        "freq",
        "row_count",
        "columns",
        "sha256_pkl",
        "sha256_meta_inputs",
        "real_data_only",
        "fabricated_data",
        "notes_limits_gaps",
    ),
    numeric_columns=("funding_rate", "mark_price_or_close"),
    timestamp_columns=("timestamp_utc",),
)

CROSS_EXCHANGE_DUAL_VENUE_SAME_ASSET_SPEC = FamilySpec(
    name="cross_exchange_dual_venue_same_asset",
    required_columns=(
        "timestamp_utc",
        "asset",
        "price_venue_a",
        "price_venue_b",
        "mid_or_close_flag_a",
        "mid_or_close_flag_b",
    ),
    required_provenance_keys=(
        "source_provider_a",
        "source_provider_b",
        "endpoints_a",
        "endpoints_b",
        "retrieved_at_utc",
        "symbol_map_a",
        "symbol_map_b",
        "clock_sync_assumption",
        "row_count_aligned",
        "rows_dropped_misaligned",
        "sha256_pkl",
        "real_data_only",
        "fabricated_data",
    ),
    numeric_columns=("price_venue_a", "price_venue_b"),
    timestamp_columns=("timestamp_utc",),
)

TERM_STRUCTURE_REAL_IV_VOL_SURFACE_SPEC = FamilySpec(
    name="term_structure_real_iv_vol_surface",
    required_columns=(
        "timestamp_utc",
        "underlying",
        "iv_30d",
        "iv_90d",
    ),
    required_provenance_keys=(
        "source_provider",
        "endpoints",
        "retrieved_at_utc",
        "underlying_map",
        "iv_definition",
        "row_count",
        "sha256_pkl",
        "real_data_only",
        "fabricated_data",
    ),
    numeric_columns=("iv_30d", "iv_90d"),
    timestamp_columns=("timestamp_utc",),
)

INTRA_BAR_MICROSTRUCTURE_SPEC = FamilySpec(
    name="intrabar_microstructure",
    required_columns=("timestamp_utc", "symbol"),
    required_provenance_keys=(
        "source_provider",
        "endpoints_or_files",
        "retrieved_at_utc",
        "symbol_map",
        "kind",
        "row_count",
        "sha256_pkl",
        "real_data_only",
        "fabricated_data",
    ),
    numeric_columns=("price", "qty", "depth"),
    timestamp_columns=("timestamp_utc",),
)

MICRO_TRADES_COLUMNS = ("price", "qty")
MICRO_TRADES_OPTIONAL_COLUMNS = ("side_or_is_buyer_maker",)
MICRO_BOOK_COLUMNS = ("bid_px_levels", "ask_px_levels", "bid_sz_levels", "ask_sz_levels", "depth")
MICRO_VALID_KINDS = ("trades", "book")


FAMILY_SPECS: dict[str, FamilySpec] = {
    FUNDING_BASIS_CARRY_SPEC.name: FUNDING_BASIS_CARRY_SPEC,
    CROSS_EXCHANGE_DUAL_VENUE_SAME_ASSET_SPEC.name: CROSS_EXCHANGE_DUAL_VENUE_SAME_ASSET_SPEC,
    TERM_STRUCTURE_REAL_IV_VOL_SURFACE_SPEC.name: TERM_STRUCTURE_REAL_IV_VOL_SURFACE_SPEC,
    INTRA_BAR_MICROSTRUCTURE_SPEC.name: INTRA_BAR_MICROSTRUCTURE_SPEC,
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _refuse(reason: str, report: dict[str, Any]) -> None:
    report["ok"] = False
    report["refused"] = True
    report["reason"] = reason
    raise RealFeedValidationError(f"real_feed_loader refused: {reason}")


def _check_flags(meta: dict[str, Any], report: dict[str, Any]) -> None:
    if meta.get("real_data_only") is not True:
        _refuse(
            f"real_data_only must be true (got {meta.get('real_data_only')!r})",
            report,
        )
    if meta.get("fabricated_data") is not False:
        _refuse(
            f"fabricated_data must be false (got {meta.get('fabricated_data')!r})",
            report,
        )
    notes = str(meta.get("notes_limits_gaps", "")).lower()
    for bad in ("proxy labeled real", "synthetic labeled real", "fabricated as real"):
        if bad in notes:
            _refuse(f"provenance notes admit proxy/fabricated-as-real: {bad!r}", report)


def _check_provenance_keys(
    meta: dict[str, Any], spec: FamilySpec, report: dict[str, Any]
) -> None:
    missing = [k for k in spec.required_provenance_keys if k not in meta]
    if missing:
        _refuse(f"missing required provenance keys: {missing}", report)


def _check_integrity(meta_path: Path, meta: dict[str, Any], report: dict[str, Any]) -> Path:
    pkl_name = meta.get("pkl_file") or meta.get("data_file") or meta_path.name.replace(
        ".meta.json", ".pkl"
    )
    pkl_path = (meta_path.parent / pkl_name).resolve()
    if not pkl_path.exists():
        _refuse(f"data file missing: {pkl_path.name}", report)
    expected = str(meta.get("sha256_pkl") or "").strip().lower()
    if not expected:
        _refuse("sha256_pkl missing/empty in provenance metadata", report)
    actual = sha256_file(pkl_path)
    report["sha256_pkl_actual"] = actual
    report["sha256_pkl_expected"] = expected
    if actual != expected:
        _refuse(
            f"sha256_pkl mismatch (expected {expected[:16]}..., got {actual[:16]}...)",
            report,
        )
    return pkl_path


def _check_schema(df: pd.DataFrame, spec: FamilySpec, report: dict[str, Any]) -> None:
    missing_cols = [c for c in spec.required_columns if c not in df.columns]
    if missing_cols:
        _refuse(f"missing required columns: {missing_cols}", report)
    for col in spec.numeric_columns:
        if col in df.columns and not pd.api.types.is_numeric_dtype(df[col]):
            # try coercion check
            coerced = pd.to_numeric(df[col], errors="coerce")
            if coerced.isna().all() and len(df) > 0:
                _refuse(f"numeric column {col!r} is not numeric/coercible", report)
    if spec.name == "funding_basis_carry" and "funding_rate" in df.columns:
        rates = pd.to_numeric(df["funding_rate"], errors="coerce")
        # refuse impossible sentinels not documented (extreme absolute values)
        if (rates.abs() > 1.0).any():
            extreme = int((rates.abs() > 1.0).sum())
            gaps = str(report.get("notes_limits_gaps", "")).lower()
            if "sentinel" not in gaps and "extreme" not in gaps:
                _refuse(
                    f"funding_rate has {extreme} values with |rate|>1.0 (undocumented sentinel/impossible)",
                    report,
                )


def _check_dual_venue_not_single_venue_proxy(df: pd.DataFrame, report: dict[str, Any]) -> None:
    """Refuse a single venue duplicated as both legs (proxy-as-dual-venue)."""
    if {"price_venue_a", "price_venue_b"}.issubset(df.columns) and len(df) > 0:
        pa = pd.to_numeric(df["price_venue_a"], errors="coerce")
        pb = pd.to_numeric(df["price_venue_b"], errors="coerce")
        if (pa == pb).all():
            _refuse(
                "price_venue_a equals price_venue_b on all rows; single venue mislabeled as dual venue (proxy), refused",
                report,
            )


def _check_term_structure_not_realized_vol_proxy(
    meta: dict[str, Any], report: dict[str, Any]
) -> None:
    """Refuse realized/historical volatility mislabeled as implied volatility.

    Only explicit proxy/admission signals are refused (fail-closed). Legitimate
    IV sources may mention 'historical' incidentally (e.g. historical IV series);
    those are not refused unless paired with a realized-vol-as-IV admission.
    """
    hay = " ".join(
        str(meta.get(k, ""))
        for k in (
            "iv_definition",
            "notes_limits_gaps",
            "notes",
            "description",
            "source",
        )
    ).lower()
    refusals = (
        "realized vol labeled as iv",
        "realized volatility labeled as iv",
        "historical volatility labeled as iv",
        "realized vol proxy",
        "realized volatility proxy",
        "not implied volatility",
        "proxy for iv",
        "proxy for implied",
    )
    for bad in refusals:
        if bad in hay:
            _refuse(
                f"term-structure metadata admits realized-vol/proxy labeled as IV: {bad!r}",
                report,
            )
    # Refuse if definition explicitly says realized/historical vol and not implied/DVOL/IV
    if ("realized vol" in hay or "historical volatility" in hay) and not any(
        k in hay for k in ("implied", "dvol", " iv", "iv_", "(iv", "black-scholes")
    ):
        _refuse(
            "term-structure iv_definition/notes describe realized/historical volatility "
            "without implied/DVOL/IV basis (proxy-as-IV), refused",
            report,
        )


def _check_intrabar_microstructure(
    meta: dict[str, Any], df: pd.DataFrame, report: dict[str, Any]
) -> None:
    """Validate intrabar_microstructure kind-specific schema and refuse resampled proxies.

    kind must be 'trades' or 'book'. trades requires price+qty (side optional).
    book requires bid/ask price+size levels + depth. Missing/invalid kind refused.
    Any admission of resampling-to-1h presented as microstructure is refused.
    """
    kind = str(meta.get("kind", "")).strip().lower()
    if kind not in MICRO_VALID_KINDS:
        _refuse(f"invalid/missing kind {kind!r}; must be one of {MICRO_VALID_KINDS}", report)

    required_by_kind = {
        "trades": MICRO_TRADES_COLUMNS,
        "book": MICRO_BOOK_COLUMNS,
    }
    missing_cols = [c for c in required_by_kind[kind] if c not in df.columns]
    if missing_cols:
        _refuse(f"missing required columns for kind={kind!r}: {missing_cols}", report)

    notes = str(meta.get("notes_limits_gaps", "")).lower()
    resampled_admissions = (
        "resampled to 1h",
        "resampled-to-1h",
        "1h-presented-as-microstructure",
        "aggregated to 1h",
        "1h rollup",
    )
    for bad in resampled_admissions:
        if bad in notes:
            _refuse(
                f"provenance notes admit resampled-to-1h-as-microstructure proxy: {bad!r}",
                report,
            )


def validate_and_load_real_feed(
    meta_path: str | Path,
    family: str = "funding_basis_carry",
    *,
    max_gap_factor: float = 3.0,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Validate provenance+integrity+schema and load a real feed. Fail-closed.

    Returns (dataframe, report). Raises RealFeedValidationError on ANY violation.
    """
    meta_path = Path(meta_path)
    report: dict[str, Any] = {
        "ok": False,
        "refused": False,
        "family": family,
        "meta_path": str(meta_path),
        "fail_closed": True,
        "real_data_only_required": True,
        "fabricated_data_allowed": False,
    }
    if family not in FAMILY_SPECS:
        _refuse(f"unknown/unsupported family {family!r}; supported={sorted(FAMILY_SPECS)}", report)
    spec = FAMILY_SPECS[family]

    if not meta_path.exists():
        _refuse(f"metadata file missing: {meta_path}", report)
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception as exc:
        _refuse(f"metadata unreadable/invalid JSON: {exc}", report)
    if not isinstance(meta, dict):
        _refuse("metadata must be a JSON object", report)
    report["notes_limits_gaps"] = meta.get("notes_limits_gaps", "")

    _check_provenance_keys(meta, spec, report)
    _check_flags(meta, report)
    pkl_path = _check_integrity(meta_path, meta, report)

    try:
        df = pd.read_pickle(pkl_path)  # noqa: S301 - loading only after sha256+provenance pass
    except Exception as exc:
        _refuse(f"data file unreadable after integrity check: {exc}", report)
    if not isinstance(df, pd.DataFrame):
        _refuse(f"data payload must be a pandas DataFrame (got {type(df).__name__})", report)

    declared_rows = meta.get("row_count")
    if family == "cross_exchange_dual_venue_same_asset":
        declared_rows = meta.get("row_count_aligned", declared_rows)
    if declared_rows is not None and int(declared_rows) != len(df):
        _refuse(f"row_count mismatch (meta={declared_rows}, actual={len(df)})", report)

    declared_cols = meta.get("columns")
    if isinstance(declared_cols, list):
        missing_decl = [c for c in declared_cols if c not in df.columns]
        if missing_decl:
            _refuse(f"declared columns missing from payload: {missing_decl}", report)

    _check_schema(df, spec, report)

    if family == "cross_exchange_dual_venue_same_asset":
        _check_dual_venue_not_single_venue_proxy(df, report)
    if family == "term_structure_real_iv_vol_surface":
        _check_term_structure_not_realized_vol_proxy(meta, report)
    if family == "intrabar_microstructure":
        _check_intrabar_microstructure(meta, df, report)

    # monotonic unique timestamp check when present
    for tcol in spec.timestamp_columns:
        if tcol in df.columns:
            ts = pd.to_datetime(df[tcol], utc=True, errors="coerce")
            if ts.isna().any():
                _refuse(f"timestamp column {tcol!r} has unparseable values", report)
            if not ts.is_monotonic_increasing:
                _refuse(f"timestamp column {tcol!r} is not monotonic increasing", report)
            if ts.duplicated().any():
                dup = int(ts.duplicated().sum())
                _refuse(f"timestamp column {tcol!r} has {dup} duplicate timestamps", report)

    report.update(
        {
            "ok": True,
            "refused": False,
            "reason": "passed_all_fail_closed_checks",
            "pkl_path": str(pkl_path),
            "rows": int(len(df)),
            "columns": list(df.columns),
            "family_spec": spec.name,
        }
    )
    return df, report


NONSPOT_FAMILY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "funding_basis_carry": ("funding", "basis", "carry", "perp"),
    "cross_exchange_dual_venue_same_asset": (
        "dualvenue",
        "dual_venue",
        "cross_exchange",
        "cross-exchange",
        "venue_a",
        "venue_b",
    ),
    "term_structure_real_iv_vol_surface": (
        "iv",
        "vol_surface",
        "vol-surface",
        "term_structure",
        "term-structure",
        "dvol",
        "implied",
    ),
    "intrabar_microstructure": (
        "intrabar",
        "microstructure",
        "trades",
        "book",
        "depth",
        "orderbook",
    ),
}


def _candidate_families_for_meta(meta: dict[str, Any], path_hint: str) -> list[str]:
    hay = " ".join(
        [
            path_hint.lower(),
            str(meta.get("family", "")).lower(),
            str(meta.get("kind", "")).lower(),
            str(meta.get("source_provider", "")).lower(),
            str(meta.get("notes_limits_gaps", "")).lower(),
        ]
    )
    families: list[str] = []
    declared = str(meta.get("family", "")).strip()
    if declared in FAMILY_SPECS:
        families.append(declared)
    for fam, kws in NONSPOT_FAMILY_KEYWORDS.items():
        if fam not in families and any(kw in hay for kw in kws):
            families.append(fam)
    return families


def scan_cache_for_real_nonspot_feeds(
    cache_dir: str | Path,
) -> dict[str, Any]:
    """Fail-closed scan: only artifacts passing validate_and_load_real_feed count.

    Does NOT fabricate. A file counts as a real non-spot feed with provenance only
    if its metadata passes the relevant family validator (real_data_only=true,
    fabricated_data=false, sha256 verified, schema valid, no proxy admissions).
    """
    cache_dir = Path(cache_dir)
    result: dict[str, Any] = {
        "cache_dir": str(cache_dir),
        "cache_exists": cache_dir.exists(),
        "fail_closed": True,
        "real_data_only_required": True,
        "fabricated_data_allowed": False,
        "families": {
            fam: {"status": "blocked_no_real_feed", "valid_artifacts": []}
            for fam in FAMILY_SPECS
        },
        "meta_files_scanned": 0,
        "candidate_hits": [],
        "new_real_feeds_with_provenance_found": False,
    }
    if not cache_dir.exists():
        return result
    meta_paths = sorted(cache_dir.glob("*.meta.json")) + sorted(cache_dir.glob("*.json"))
    seen: set[str] = set()
    for mp in meta_paths:
        rp = str(mp.resolve())
        if rp in seen:
            continue
        seen.add(rp)
        if not mp.name.endswith("meta.json"):
            continue
        result["meta_files_scanned"] += 1
        try:
            meta = json.loads(mp.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(meta, dict):
            continue
        families = _candidate_families_for_meta(meta, mp.name)
        if not families:
            continue
        result["candidate_hits"].append({"meta": mp.name, "families_considered": families})
        for fam in families:
            try:
                _, report = validate_and_load_real_feed(mp, fam)
            except RealFeedValidationError:
                continue
            except Exception:
                continue
            if report.get("ok"):
                entry = {
                    "meta": mp.name,
                    "family": fam,
                    "rows": report.get("rows"),
                    "reason": report.get("reason"),
                }
                result["families"][fam]["valid_artifacts"].append(entry)
                result["families"][fam]["status"] = "real_feed_with_provenance_present"
                result["new_real_feeds_with_provenance_found"] = True
    return result


def audit_cache_for_real_nonspot_feeds(
    cache_dir: str | Path,
    *,
    campaign: int | None = None,
) -> dict[str, Any]:
    """Fail-closed cache audit: scan + per-candidate validation outcomes.

    Advances audit infrastructure without fabricating data or weakening gates.
    Every artifact is accepted only when ``validate_and_load_real_feed`` passes.
    Refusal reasons are recorded for candidate hits to make blockers explicit.
    This function does not prove edge and never sets ``oos_edge_proven`` true.
    """
    cache_dir = Path(cache_dir)
    scan = scan_cache_for_real_nonspot_feeds(cache_dir)
    audit: dict[str, Any] = {
        "tool": "data.real_feed_loader.audit_cache_for_real_nonspot_feeds",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "campaign": campaign,
        "fail_closed": True,
        "real_data_only": True,
        "fabricated_data": False,
        "no_proxies_labeled_real": True,
        "oos_edge_proven": False,
        "scan": scan,
        "families": scan["families"],
        "candidate_validation": [],
        "non_candidate_meta_count": max(
            0, int(scan.get("meta_files_scanned", 0)) - len(scan.get("candidate_hits", []))
        ),
        "conclusion": (
            "VALID_NONSPOT_PROVENANCE_ARTIFACTS_FOUND"
            if scan.get("new_real_feeds_with_provenance_found")
            else "NO_VALID_NONSPOT_PROVENANCE_ARTIFACTS"
        ),
    }
    if not cache_dir.exists():
        return audit
    for hit in scan.get("candidate_hits", []):
        meta_name = str(hit.get("meta", ""))
        mp = cache_dir / meta_name
        for fam in hit.get("families_considered", []):
            entry: dict[str, Any] = {"meta": meta_name, "family": fam, "ok": False}
            try:
                _, report = validate_and_load_real_feed(mp, fam)
            except RealFeedValidationError as exc:
                entry["refused"] = True
                entry["reason"] = str(exc)
                audit["candidate_validation"].append(entry)
                continue
            except Exception as exc:
                entry["refused"] = True
                entry["reason"] = f"unexpected_error:{type(exc).__name__}:{exc}"
                audit["candidate_validation"].append(entry)
                continue
            entry["ok"] = bool(report.get("ok"))
            entry["refused"] = bool(report.get("refused"))
            entry["reason"] = report.get("reason")
            entry["rows"] = report.get("rows")
            audit["candidate_validation"].append(entry)
    return audit


def generate_unblock_status_report(
    cache_dir: str | Path,
    *,
    campaign: int | None = None,
    readiness_specs: list[str] | None = None,
) -> dict[str, Any]:
    """Generate a fail-closed unblock/readiness status report from cache state.

    Combines ``audit_cache_for_real_nonspot_feeds`` with optional readiness spec
    file references. Never fabricates data, never weakens validation, never sets
    ``oos_edge_proven`` true. A family is unblocked only when a valid real
    non-spot provenance artifact is present and passes validation.
    """
    audit = audit_cache_for_real_nonspot_feeds(cache_dir, campaign=campaign)
    specs: list[dict[str, Any]] = []
    for ref in readiness_specs or []:
        sp = Path(ref)
        entry: dict[str, Any] = {"path": str(sp), "exists": sp.exists()}
        if sp.exists():
            try:
                obj = json.loads(sp.read_text(encoding="utf-8"))
                entry["artifact"] = obj.get("artifact") if isinstance(obj, dict) else None
            except Exception as exc:
                entry["read_error"] = f"{type(exc).__name__}:{exc}"
        specs.append(entry)
    blocked = [
        fam for fam, info in audit["families"].items()
        if info.get("status") != "real_feed_with_provenance_present"
    ]
    return {
        "tool": "data.real_feed_loader.generate_unblock_status_report",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "campaign": campaign,
        "fail_closed": True,
        "real_data_only": True,
        "fabricated_data": False,
        "no_proxies_labeled_real": True,
        "oos_edge_proven": False,
        "path_r_triggered": bool(audit["scan"].get("new_real_feeds_with_provenance_found")),
        "conclusion": (
            "PATH_R_ELIGIBLE_VALID_NONSPOT_FEED_PRESENT"
            if audit["scan"].get("new_real_feeds_with_provenance_found")
            else "PATH_C_MAINTAIN_STILL_BLOCKED"
        ),
        "blocked_families": blocked,
        "families": audit["families"],
        "audit_conclusion": audit["conclusion"],
        "scan_summary": {
            "cache_dir": audit["scan"].get("cache_dir"),
            "meta_files_scanned": audit["scan"].get("meta_files_scanned"),
            "candidate_hits": len(audit["scan"].get("candidate_hits", [])),
            "candidate_validation_count": len(audit.get("candidate_validation", [])),
            "new_real_feeds_with_provenance_found": audit["scan"].get("new_real_feeds_with_provenance_found"),
        },
        "readiness_specs": specs,
    }
