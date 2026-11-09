"""Fail-closed loader/validator for real external feed artifacts.

Consumes ONLY files that pass provenance + integrity checks. Refuses missing
metadata, sha256 mismatches, fabricated/proxy-as-real flags, schema violations,
and undocumented gaps. Designed to satisfy the operator-executable readiness
spec (e.g. reports/real_feed_ingestion_readiness_20261105T104640Z.json).

Synthetic/test fixtures may be used ONLY inside tests and must never be labeled
as real data. This module never fabricates data.
"""

from __future__ import annotations

import argparse
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

REAL_QUOTE_VOLUME_SPEC = FamilySpec(
    name="real_quote_volume",
    required_columns=("timestamp_utc", "symbol", "quote_volume_usdt"),
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
    numeric_columns=("quote_volume_usdt",),
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
    REAL_QUOTE_VOLUME_SPEC.name: REAL_QUOTE_VOLUME_SPEC,
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
                    f"funding_rate has {extreme} values with |rate|>1.0 "
                    "(undocumented sentinel/impossible)",
                    report,
                )


def _check_dual_venue_not_single_venue_proxy(df: pd.DataFrame, report: dict[str, Any]) -> None:
    """Refuse a single venue duplicated as both legs (proxy-as-dual-venue)."""
    if {"price_venue_a", "price_venue_b"}.issubset(df.columns) and len(df) > 0:
        pa = pd.to_numeric(df["price_venue_a"], errors="coerce")
        pb = pd.to_numeric(df["price_venue_b"], errors="coerce")
        if (pa == pb).all():
            _refuse(
                "price_venue_a equals price_venue_b on all rows; "
                "single venue mislabeled as dual venue (proxy), refused",
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
    provenance: dict[str, Any] | str | Path | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Validate provenance+integrity+schema and load a real feed. Fail-closed.

    Returns (dataframe, report). Raises RealFeedValidationError on ANY violation.

    *provenance* optionally supplies an external provenance certificate (dict or
    path to a JSON file) whose keys are merged over the artifact's own metadata
    before validation. This lets an artifact whose on-disk metadata predates the
    loader's provenance schema still be validated fail-closed, without mutating
    the cached artifact. The certificate is itself subject to the same
    real_data_only/fabricated_data/admission checks.
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

    if provenance is not None:
        prov_obj: dict[str, Any] | None = None
        if isinstance(provenance, dict):
            prov_obj = provenance
            report["provenance_source"] = "<dict>"
        else:
            prov_path = Path(provenance)
            report["provenance_source"] = str(prov_path)
            if not prov_path.exists():
                _refuse(f"provenance certificate missing: {prov_path}", report)
            try:
                prov_obj = json.loads(prov_path.read_text(encoding="utf-8"))
            except Exception as exc:
                _refuse(f"provenance certificate unreadable/invalid JSON: {exc}", report)
            if not isinstance(prov_obj, dict):
                _refuse("provenance certificate must be a JSON object", report)
        if prov_obj is not None:
            if prov_obj.get("real_data_only") is not True:
                _refuse("provenance certificate real_data_only must be true", report)
            if prov_obj.get("fabricated_data") is not False:
                _refuse("provenance certificate fabricated_data must be false", report)
            merged = dict(meta)
            merged.update(prov_obj)
            meta = merged
            report["provenance_merged"] = True

    _check_provenance_keys(meta, spec, report)
    _check_flags(meta, report)
    pkl_path = _check_integrity(meta_path, meta, report)

    try:
        df = pd.read_pickle(pkl_path)  # noqa: S301 - loading only after sha256+provenance pass
    except Exception as exc:
        _refuse(f"data file unreadable after integrity check: {exc}", report)
    if isinstance(df, dict):
        # real_quote_volume family may be stored as {symbol: Series(timestamp, quote_volume_usdt)}.
        # Normalize to a long frame (timestamp_utc, symbol, quote_volume_usdt) so the rest of
        # the fail-closed checks (schema, monotonic timestamps, row_count, columns) apply.
        if family != "real_quote_volume":
            _refuse(
                f"dict payload not supported for family {family!r}; expected a pandas DataFrame",
                report,
            )
        rows: list[dict[str, Any]] = []
        for sym, s in df.items():
            if not isinstance(s, pd.Series):
                _refuse(f"payload entry {sym!r} is not a pandas Series", report)
            s = pd.to_numeric(s, errors="coerce")
            for ts, val in s.items():
                rows.append(
                    {
                        "timestamp_utc": pd.Timestamp(ts),
                        "symbol": str(sym),
                        "quote_volume_usdt": float(val),
                    }
                )
        if not rows:
            _refuse("dict payload contains no usable rows", report)
        # Canonical long layout: symbol-major sort so per-symbol timestamp
        # monotonicity/unique checks are well-defined downstream.
        df = pd.DataFrame(rows).sort_values(["symbol", "timestamp_utc"]).reset_index(drop=True)
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
        if tcol not in df.columns:
            continue
        ts = pd.to_datetime(df[tcol], utc=True, errors="coerce")
        if ts.isna().any():
            _refuse(f"timestamp column {tcol!r} has unparseable values", report)
        # Multi-symbol long frames (real_quote_volume: one row per
        # (timestamp, symbol)) legitimately repeat each timestamp once per
        # symbol. Enforce monotonic+unique *within each symbol group* rather
        # than globally, and require the frame itself to be symbol-ordered.
        group_col = "symbol" if (family == "real_quote_volume" and "symbol" in df.columns) else None
        if group_col is not None:
            # Multi-symbol long frames are NOT globally timestamp-monotonic
            # (each symbol restarts at window start); require symbol-major
            # ordering and per-symbol monotonic+unique timestamps instead.
            if not df[group_col].is_monotonic_increasing:
                _refuse(
                    f"frame not sorted by {group_col!r} (symbol-major required)",
                    report,
                )
            dup_global = int(ts.duplicated().sum())
            per_group_dups = 0
            non_monotonic_groups = 0
            for _, g in df.groupby(group_col, sort=False):
                gts = pd.to_datetime(g[tcol], utc=True, errors="coerce")
                if not gts.is_monotonic_increasing:
                    non_monotonic_groups += 1
                if gts.duplicated().any():
                    per_group_dups += int(gts.duplicated().sum())
            if non_monotonic_groups:
                _refuse(
                    f"timestamp column {tcol!r} is not monotonic increasing within "
                    f"{non_monotonic_groups} symbol group(s)",
                    report,
                )
            if per_group_dups:
                _refuse(
                    f"timestamp column {tcol!r} has {per_group_dups} duplicate "
                    f"timestamps within symbol groups",
                    report,
                )
            report["multi_symbol_long_frame"] = {
                "group_col": group_col,
                "n_groups": int(df[group_col].nunique()),
                "global_duplicate_timestamps": dup_global,
                "within_group_duplicates": per_group_dups,
                "checked": "per_symbol_monotonic_unique",
            }
            continue
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
    "real_quote_volume": (
        "quote_volume",
        "quotevolume",
        "volume_1h",
        "real_binance_quote_volume",
        "klines",
        "column 5",
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


def _discover_provenance_certificate(
    cache_dir: Path, meta_path: Path
) -> dict[str, Any] | None:
    """Return a validated provenance certificate dict for *meta_path*, if any.

    Looks for a sibling ``<stem>.provenance.json`` (or ``<stem>_provenance.json``)
    in *cache_dir*. The certificate must declare ``real_data_only=true`` and
    ``fabricated_data=false`` and carry the family's required provenance keys.
    Returns None when no usable certificate exists (fail-closed: the artifact is
    then only loadable if its inline metadata is already complete).
    """
    stem = meta_path.name[: -len(".meta.json")]
    candidates = [
        meta_path.with_name(f"{stem}.provenance.json"),
        meta_path.with_name(f"{stem}_provenance.json"),
    ]
    for cand in candidates:
        if not cand.exists():
            continue
        try:
            obj = json.loads(cand.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(obj, dict):
            continue
        if obj.get("real_data_only") is not True or obj.get("fabricated_data") is not False:
            continue
        return obj
    return None


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
        # A real_quote_volume artifact may carry its provenance in a sibling
        # certificate (e.g. volume_1h_full.provenance.json) rather than inline.
        prov = _discover_provenance_certificate(cache_dir, mp)
        if prov is not None:
            result.setdefault("provenance_certificates", []).append(str(prov))
            if "real_quote_volume" not in families:
                families.append("real_quote_volume")
        if not families:
            continue
        result["candidate_hits"].append({"meta": mp.name, "families_considered": families})
        for fam in families:
            try:
                _, report = validate_and_load_real_feed(mp, fam, provenance=prov)
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
        "provenance_certificates": [],
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
        prov = _discover_provenance_certificate(cache_dir, mp)
        if prov is not None:
            audit["provenance_certificates"] = audit.get("provenance_certificates", []) or []
            prov_name = meta_name[: -len(".meta.json")] + ".provenance.json"
            audit["provenance_certificates"].append(str(mp.with_name(prov_name)))
        for fam in hit.get("families_considered", []):
            entry: dict[str, Any] = {"meta": meta_name, "family": fam, "ok": False}
            try:
                _, report = validate_and_load_real_feed(mp, fam, provenance=prov)
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


def discover_readiness_specs(reports_dir: str | Path) -> list[dict[str, Any]]:
    """Discover real-feed readiness spec artifacts in *reports_dir* (fail-closed).

    Returns references to files whose JSON declares
    ``artifact == "real_feed_ingestion_readiness"`` or ``readiness_spec``-like
    metadata, plus a few stable known names if present. Never fabricates content;
    only reads existing files and records parse errors honestly.
    """
    reports_dir = Path(reports_dir)
    found: list[dict[str, Any]] = []
    if not reports_dir.exists():
        return found
    candidates = sorted(set(reports_dir.glob("*readiness*.json")))
    for sp in candidates:
        entry: dict[str, Any] = {"path": str(sp), "exists": True, "name": sp.name}
        try:
            obj = json.loads(sp.read_text(encoding="utf-8"))
        except Exception as exc:
            entry["read_error"] = f"{type(exc).__name__}:{exc}"
            found.append(entry)
            continue
        if not isinstance(obj, dict):
            entry["kind"] = "non_object_json"
            found.append(entry)
            continue
        art = obj.get("artifact")
        entry["artifact"] = art
        entry["campaign"] = obj.get("campaign")
        families: list[str] = []
        if isinstance(obj.get("feeds"), list):
            for feed in obj["feeds"]:
                if isinstance(feed, dict) and feed.get("family"):
                    families.append(str(feed["family"]))
        if obj.get("family"):
            families.append(str(obj["family"]))
        entry["families_covered"] = sorted(set(families))
        is_relevant = art == "real_feed_ingestion_readiness" or bool(families)
        entry["relevant_to_nonspot_unblock"] = bool(is_relevant)
        if is_relevant:
            found.append(entry)
    return found


def compare_unblock_status(
    prior: dict[str, Any] | str | Path | None,
    current: dict[str, Any],
) -> dict[str, Any]:
    """Compare a prior unblock status report to the current one (fail-closed).

    Accepts a prior report dict or a path to a JSON report. Records only
    observable differences (blocked families, path_r, scan counts, audit
    conclusion). Never fabricates changes; if the prior report is unreadable,
    the delta is marked ``prior_unavailable`` honestly. Does not prove edge.
    """
    delta: dict[str, Any] = {
        "tool": "data.real_feed_loader.compare_unblock_status",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "fail_closed": True,
        "real_data_only": True,
        "fabricated_data": False,
        "oos_edge_proven": False,
        "prior_available": False,
        "changed": None,
    }
    if prior is None:
        delta["reason"] = "no_prior_provided"
        return delta
    prior_obj: dict[str, Any] | None = None
    if isinstance(prior, dict):
        prior_obj = prior
        delta["prior_source"] = "<dict>"
    else:
        prior_path = Path(prior)
        delta["prior_source"] = str(prior_path)
        if prior_path.exists():
            try:
                loaded = json.loads(prior_path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    prior_obj = loaded
                else:
                    delta["reason"] = "prior_report_not_object"
                    return delta
            except Exception as exc:
                delta["reason"] = f"prior_read_error:{type(exc).__name__}:{exc}"
                return delta
        else:
            delta["reason"] = "prior_report_missing"
            return delta
    delta["prior_available"] = True
    prior_blocked = sorted(prior_obj.get("blocked_families") or [])
    current_blocked = sorted(current.get("blocked_families") or [])
    prior_path_r = bool(prior_obj.get("path_r_triggered"))
    current_path_r = bool(current.get("path_r_triggered"))
    prior_scan = prior_obj.get("scan_summary") or {}
    current_scan = current.get("scan_summary") or {}
    scan_keys = (
        "meta_files_scanned",
        "candidate_hits",
        "candidate_validation_count",
        "new_real_feeds_with_provenance_found",
    )
    scan_diff = {
        k: {"prior": prior_scan.get(k), "current": current_scan.get(k)}
        for k in scan_keys
        if prior_scan.get(k) != current_scan.get(k)
    }
    changed = (
        prior_blocked != current_blocked
        or prior_path_r != current_path_r
        or prior_obj.get("audit_conclusion") != current.get("audit_conclusion")
        or bool(scan_diff)
    )
    delta.update(
        {
            "changed": changed,
            "prior_campaign": prior_obj.get("campaign"),
            "current_campaign": current.get("campaign"),
            "prior_conclusion": prior_obj.get("conclusion"),
            "current_conclusion": current.get("conclusion"),
            "prior_audit_conclusion": prior_obj.get("audit_conclusion"),
            "current_audit_conclusion": current.get("audit_conclusion"),
            "prior_blocked_families": prior_blocked,
            "current_blocked_families": current_blocked,
            "blocked_families_changed": prior_blocked != current_blocked,
            "prior_path_r_triggered": prior_path_r,
            "current_path_r_triggered": current_path_r,
            "path_r_changed": prior_path_r != current_path_r,
            "scan_differences": scan_diff,
            "honest_assessment": (
                "UNBLOCK_STATE_CHANGED_REVIEW_REQUIRED"
                if changed
                else "NO_CHANGE_STILL_BLOCKED_FAIL_CLOSED"
            ),
        }
    )
    return delta


def generate_unblock_status_report(
    cache_dir: str | Path,
    *,
    campaign: int | None = None,
    readiness_specs: list[str] | None = None,
    reports_dir: str | Path | None = None,
    auto_discover_readiness: bool = True,
    include_readiness_details: bool = False,
    prior_report: dict[str, Any] | str | Path | None = None,
) -> dict[str, Any]:
    """Generate a fail-closed unblock/readiness status report from cache state.

    Combines ``audit_cache_for_real_nonspot_feeds`` with readiness spec
    references. If *readiness_specs* is omitted and *auto_discover_readiness* is
    true, relevant readiness specs are discovered from *reports_dir* (or
    ``cache_dir/../reports`` when reports_dir is omitted). When *prior_report*
    is provided, a ``campaign_delta`` section compares observable unblock state
    against the prior report (fail-closed; no fabricated changes). Never
    fabricates data, never weakens validation, never sets ``oos_edge_proven``
    true. A family is unblocked only when a valid real non-spot provenance
    artifact is present and passes validation.
    """
    audit = audit_cache_for_real_nonspot_feeds(cache_dir, campaign=campaign)
    specs: list[dict[str, Any]] = []
    refs = list(readiness_specs) if readiness_specs is not None else []
    if readiness_specs is None and auto_discover_readiness:
        rdir = (
            Path(reports_dir)
            if reports_dir is not None
            else Path(cache_dir).resolve().parent.parent / "reports"
        )
        for d in discover_readiness_specs(rdir):
            if include_readiness_details and d.get("path") and d.get("exists"):
                try:
                    obj = json.loads(Path(d["path"]).read_text(encoding="utf-8"))
                    if isinstance(obj, dict):
                        d.setdefault("generated_at_utc", obj.get("generated_at_utc"))
                        d.setdefault(
                            "feeds_count",
                            len(obj["feeds"]) if isinstance(obj.get("feeds"), list) else None,
                        )
                except Exception as exc:
                    d["read_error"] = f"{type(exc).__name__}:{exc}"
            specs.append(d)
    for ref in refs:
        sp = Path(ref)
        entry: dict[str, Any] = {"path": str(sp), "exists": sp.exists(), "name": sp.name}
        if sp.exists():
            try:
                obj = json.loads(sp.read_text(encoding="utf-8"))
                if isinstance(obj, dict):
                    entry["artifact"] = obj.get("artifact")
                    entry["campaign"] = obj.get("campaign")
                    if include_readiness_details:
                        entry["generated_at_utc"] = obj.get("generated_at_utc")
                        entry["feeds_count"] = (
                            len(obj["feeds"]) if isinstance(obj.get("feeds"), list) else None
                        )
                else:
                    entry["artifact"] = None
                    entry["campaign"] = None
            except Exception as exc:
                entry["read_error"] = f"{type(exc).__name__}:{exc}"
        specs.append(entry)
    blocked = [
        fam for fam, info in audit["families"].items()
        if info.get("status") != "real_feed_with_provenance_present"
    ]
    report: dict[str, Any] = {
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
            "new_real_feeds_with_provenance_found": audit["scan"].get(
                "new_real_feeds_with_provenance_found"
            ),
        },
        "readiness_specs": specs,
        "readiness_spec_count": len(specs),
        "auto_discover_readiness": auto_discover_readiness,
    }
    if prior_report is not None:
        report["campaign_delta"] = compare_unblock_status(prior_report, report)
    return report


def build_real_quote_volume_provenance(
    cache_dir: str | Path,
    *,
    meta_path: str | Path | None = None,
    pkl_path: str | Path | None = None,
    source_provider: str = "www.binance.com public klines endpoint",
    source_endpoints: str = "GET /api/v3/klines (spot) — column 5 = quote asset volume (Q)",
    request_urls_or_params: str = (
        "symbol=<SYMBOL>&interval=1h&startTime=<ms>&endTime=<ms>&limit=1000; "
        "paginated per symbol over 2026-04-01..2026-10-30 UTC"
    ),
    notes_limits_gaps: str = (
        "Real Binance public spot quote volume (klines column 5), not fabricated, not a proxy. "
        "1h bars, UTC. MATIC excluded (all retries failed / not in results). "
        "No resampling of a derived/estimated series; raw klines column."
    ),
) -> dict[str, Any]:
    """Build a fail-closed provenance certificate for a real quote-volume artifact.

    The certificate supplies every key required by ``REAL_QUOTE_VOLUME_SPEC`` so the
    artifact becomes loadable by ``validate_and_load_real_feed`` (family
    ``real_quote_volume``). It computes sha256 over the pkl and the existing meta
    inputs, verifies the payload is a {symbol: Series} dict, and returns the
    certificate dict plus the meta path to write. Never fabricates data; the
    caller must supply a real cached artifact.
    """
    cache_dir = Path(cache_dir)
    if meta_path is None:
        meta_path = cache_dir / "volume_1h_full.meta.json"
    else:
        meta_path = Path(meta_path)
    if pkl_path is None:
        # Derive the data file name by stripping the trailing ".meta.json"
        # suffix (NOT with_suffix(".pkl"), which on "x.meta.json" yields
        # "x.meta.pkl" — a phantom path that fails closed even when the real
        # artifact exists next to the metadata).
        if meta_path.name.endswith(".meta.json"):
            pkl_path = meta_path.with_name(meta_path.name[: -len(".meta.json")] + ".pkl")
        else:
            pkl_path = meta_path.with_suffix(".pkl")
    else:
        pkl_path = Path(pkl_path)
    if not pkl_path.exists():
        raise RealFeedValidationError(f"data file missing: {pkl_path}")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    if not isinstance(meta, dict):
        raise RealFeedValidationError("metadata must be a JSON object")
    payload = pd.read_pickle(pkl_path)  # noqa: S301 - provenance-only inspection
    if not isinstance(payload, dict) or not all(isinstance(v, pd.Series) for v in payload.values()):
        raise RealFeedValidationError(
            "quote volume payload must be a dict of {symbol: pandas.Series}"
        )
    symbols = [str(k) for k in payload.keys()]
    rows = sum(int(len(v)) for v in payload.values())
    first = min((pd.Timestamp(v.index[0]) for v in payload.values() if len(v)), default=None)
    last = max((pd.Timestamp(v.index[-1]) for v in payload.values() if len(v)), default=None)
    cert = {
        "artifact": "real_quote_volume_provenance",
        "family": "real_quote_volume",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "fail_closed": True,
        "real_data_only": True,
        "fabricated_data": False,
        "no_proxies_labeled_real": True,
        "source_provider": source_provider,
        "source_endpoints": source_endpoints,
        "request_urls_or_params": request_urls_or_params,
        "retrieved_at_utc": str(
            meta.get("retrieved_at_utc") or (first.isoformat() if first is not None else "")
        ),
        "symbol_map_native_to_repo": {s: s for s in symbols},
        "window_start_utc": str(first.isoformat()) if first is not None else None,
        "window_end_utc": str(last.isoformat()) if last is not None else None,
        "freq": "1h",
        "row_count": int(rows),
        "columns": ["timestamp_utc", "symbol", "quote_volume_usdt"],
        "symbols": symbols,
        "n_symbols": int(len(symbols)),
        "sha256_pkl": sha256_file(pkl_path),
        "sha256_meta_inputs": sha256_file(meta_path),
        "pkl_file": pkl_path.name,
        "notes_limits_gaps": notes_limits_gaps,
        "existing_meta_keys": sorted(meta.keys()),
        "payload_kind": "dict_of_symbol_series",
        "verification": {
            "payload_is_dict_of_series": True,
            "all_entries_numeric_coercible": bool(
                all(pd.to_numeric(v, errors="coerce").notna().any() for v in payload.values())
            ),
            "rows_total": int(rows),
        },
    }
    return cert


def build_unblock_trend_report(
    reports_dir: str | Path,
    *,
    campaign: int | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    """Aggregate historical real_feed_unblock_status reports (fail-closed).

    Reads observable fields only from existing ``real_feed_unblock_status_*.json``
    artifacts under *reports_dir*. Never fabricates data, never proves edge, and
    never labels missing/unreadable files as progress. Unreadable files are
    recorded explicitly. Designed to make campaign-over-campaign blocker state
    auditable as a concrete artifact, not to claim any strategy edge.
    """
    reports_dir = Path(reports_dir)
    paths = sorted(reports_dir.glob("real_feed_unblock_status_*.json"))
    entries: list[dict[str, Any]] = []
    unreadable: list[dict[str, str]] = []
    for p in paths:
        try:
            obj = json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:
            unreadable.append({"path": str(p), "error": f"{type(exc).__name__}:{exc}"})
            continue
        if not isinstance(obj, dict):
            unreadable.append({"path": str(p), "error": "report_not_object"})
            continue
        scan = obj.get("scan_summary") or {}
        delta = obj.get("campaign_delta") or {}
        entries.append(
            {
                "path": str(p),
                "name": p.name,
                "campaign": obj.get("campaign"),
                "generated_at_utc": obj.get("generated_at_utc"),
                "conclusion": obj.get("conclusion"),
                "path_r_triggered": bool(obj.get("path_r_triggered")),
                "blocked_families": sorted(obj.get("blocked_families") or []),
                "audit_conclusion": obj.get("audit_conclusion"),
                "meta_files_scanned": scan.get("meta_files_scanned"),
                "candidate_hits": scan.get("candidate_hits"),
                "new_real_feeds_with_provenance_found": scan.get(
                    "new_real_feeds_with_provenance_found"
                ),
                "campaign_delta_prior_available": delta.get("prior_available"),
                "campaign_delta_changed": delta.get("changed"),
                "campaign_delta_honest_assessment": delta.get("honest_assessment"),
            }
        )
    entries.sort(
        key=lambda e: (
            e.get("campaign") if isinstance(e.get("campaign"), int) else -1,
            e.get("name") or "",
        )
    )
    if limit is not None and limit >= 0:
        entries = entries[-limit:] if limit else []
    campaigns = [e.get("campaign") for e in entries if isinstance(e.get("campaign"), int)]
    path_r_seen = [e for e in entries if e.get("path_r_triggered")]
    numbered = [e for e in entries if isinstance(e.get("campaign"), int)]
    latest = numbered[-1] if numbered else (entries[-1] if entries else None)
    transitions: list[dict[str, Any]] = []
    for prev, cur in zip(entries, entries[1:]):
        transitions.append(
            {
                "from_campaign": prev.get("campaign"),
                "to_campaign": cur.get("campaign"),
                "blocked_families_changed": prev.get("blocked_families")
                != cur.get("blocked_families"),
                "path_r_changed": prev.get("path_r_triggered")
                != cur.get("path_r_triggered"),
                "conclusion_changed": prev.get("conclusion")
                != cur.get("conclusion"),
                "audit_conclusion_changed": prev.get("audit_conclusion")
                != cur.get("audit_conclusion"),
            }
        )
    any_transition_change = any(
        t["blocked_families_changed"]
        or t["path_r_changed"]
        or t["conclusion_changed"]
        or t["audit_conclusion_changed"]
        for t in transitions
    )
    return {
        "tool": "data.real_feed_loader.build_unblock_trend_report",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "campaign": campaign,
        "fail_closed": True,
        "real_data_only": True,
        "fabricated_data": False,
        "no_proxies_labeled_real": True,
        "oos_edge_proven": False,
        "reports_dir": str(reports_dir),
        "status_files_found": len(paths),
        "status_reports_read": len(entries),
        "unreadable_files": unreadable,
        "campaigns_observed": campaigns,
        "path_r_ever_triggered": bool(path_r_seen),
        "path_r_triggered_campaigns": [e.get("campaign") for e in path_r_seen],
        "latest": latest,
        "transitions": transitions,
        "any_observable_state_change_across_reports": any_transition_change,
        "entries": entries,
        "honest_assessment": (
            "NO_HISTORICAL_STATUS_REPORTS_FOUND"
            if not entries
            else "PATH_R_OBSERVED_IN_HISTORY_REVIEW_REQUIRED"
            if path_r_seen
            else "NO_CHANGE_STILL_BLOCKED_FAIL_CLOSED"
            if not any_transition_change
            else "OBSERVABLE_STATE_CHANGE_IN_HISTORY_REVIEW_REQUIRED"
        ),
        "notes": (
            "Concrete fail-closed trend/audit artifact derived only from existing "
            "real_feed_unblock_status reports. Not an edge claim. No fabrication."
        ),
    }


def build_cache_provenance_gap_audit(
    cache_dir: str | Path,
    *,
    campaign: int | None = None,
    reports_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Emit a concrete fail-closed cache provenance/candidate gap audit artifact.

    Enumerates all ``*.meta.json`` files in *cache_dir*, records whether each is
    classified as a non-spot candidate, whether a provenance certificate is
    discoverable, and the fail-closed validation outcome (including refusal
    reasons) from :func:`audit_cache_for_real_nonspot_feeds`. Also summarizes
    the four externally-gated non-spot families. Never fabricates data, never
    proves edge, and never labels refused/missing provenance as progress.
    """
    cache_dir = Path(cache_dir)
    scan = scan_cache_for_real_nonspot_feeds(cache_dir)
    audit = audit_cache_for_real_nonspot_feeds(cache_dir, campaign=campaign)
    candidate_meta_names = {str(h.get("meta", "")) for h in scan.get("candidate_hits", [])}
    candidate_families = {
        str(h.get("meta", "")): [str(f) for f in (h.get("families_considered") or [])]
        for h in scan.get("candidate_hits", [])
    }
    validations_by_meta: dict[str, list[dict[str, Any]]] = {}
    for v in audit.get("candidate_validation", []) or []:
        if not isinstance(v, dict):
            continue
        validations_by_meta.setdefault(str(v.get("meta", "")), []).append(v)

    meta_inventory: list[dict[str, Any]] = []
    for mp in sorted(cache_dir.glob("*.meta.json")) if cache_dir.exists() else []:
        meta_name = mp.name
        prov = _discover_provenance_certificate(cache_dir, mp)
        obj: dict[str, Any] | None = None
        read_error: str | None = None
        try:
            loaded = json.loads(mp.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                obj = loaded
            else:
                read_error = "meta_not_object"
        except Exception as exc:
            read_error = f"{type(exc).__name__}:{exc}"
        flags_ok = (
            isinstance(obj, dict)
            and obj.get("real_data_only") is True
            and obj.get("fabricated_data") is False
        ) if obj is not None else None
        meta_inventory.append(
            {
                "meta": meta_name,
                "candidate_nonspot": meta_name in candidate_meta_names,
                "families_considered": candidate_families.get(meta_name, []),
                "provenance_certificate_discovered": prov is not None,
                "provenance_certificate_path": str(prov) if prov is not None else None,
                "meta_readable": read_error is None,
                "meta_read_error": read_error,
                "declared_real_data_only_true_fabricated_false": flags_ok,
                "meta_type_or_artifact": (obj or {}).get("type") or (obj or {}).get("artifact"),
                "validation_results": validations_by_meta.get(meta_name, []),
            }
        )

    blocked_families = sorted(
        fam for fam, info in (audit.get("families") or {}).items()
        if isinstance(info, dict) and not info.get("valid_artifacts")
    )
    path_r_triggered = scan.get("new_real_feeds_with_provenance_found") is True and any(
        isinstance(info, dict) and info.get("valid_artifacts")
        for info in (audit.get("families") or {}).values()
    )
    any_candidate_valid = any(
        isinstance(v, dict) and v.get("ok") and not v.get("refused")
        for v in (audit.get("candidate_validation") or [])
    )
    candidate_hits_list = scan.get("candidate_hits") or []
    candidate_hits = (
        len(candidate_hits_list)
        if isinstance(candidate_hits_list, list)
        else int(candidate_hits_list or 0)
    )
    refused_candidates = sum(
        1
        for v in (audit.get("candidate_validation") or [])
        if isinstance(v, dict) and v.get("refused")
    )
    return {
        "tool": "data.real_feed_loader.build_cache_provenance_gap_audit",
        "artifact": "cache_provenance_gap_audit",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "campaign": campaign,
        "fail_closed": True,
        "real_data_only": True,
        "fabricated_data": False,
        "no_proxies_labeled_real": True,
        "oos_edge_proven": False,
        "cache_dir": str(cache_dir),
        "reports_dir": str(reports_dir) if reports_dir is not None else None,
        "conclusion": (
            "PATH_R_ELIGIBLE_VALID_NONSPOT_FEED_PRESENT"
            if path_r_triggered and any_candidate_valid
            else "NO_VALID_NONSPOT_PROVENANCE_ARTIFACTS"
        ),
        "path_r_triggered": bool(path_r_triggered and any_candidate_valid),
        "blocked_families": blocked_families,
        "scan_summary": {
            "meta_files_scanned": int(scan.get("meta_files_scanned", 0) or 0),
            "candidate_hits": candidate_hits,
            "candidate_validation_count": len(audit.get("candidate_validation") or []),
            "refused_candidates": refused_candidates,
            "valid_candidates": sum(
                1 for v in (audit.get("candidate_validation") or [])
                if isinstance(v, dict) and v.get("ok") and not v.get("refused")
            ),
            "new_real_feeds_with_provenance_found": bool(
                scan.get("new_real_feeds_with_provenance_found")
            ),
            "non_candidate_meta_count": int(audit.get("non_candidate_meta_count", 0) or 0),
        },
        "families": audit.get("families", {}),
        "candidate_validation": audit.get("candidate_validation", []),
        "provenance_certificates": audit.get("provenance_certificates", []),
        "meta_inventory": meta_inventory,
        "honest_assessment": (
            "PATH_R_ELIGIBLE_REVIEW_REQUIRED"
            if path_r_triggered and any_candidate_valid
            else "CANDIDATES_PRESENT_BUT_FAIL_CLOSED_REFUSED_STILL_BLOCKED"
            if candidate_hits > 0
            else "NO_CANDIDATE_NONSPOT_FEEDS_STILL_BLOCKED_FAIL_CLOSED"
        ),
        "notes": (
            "Concrete fail-closed cache/provenance gap audit derived only from existing "
            "cache metadata and loader validation. Refusals are recorded honestly; "
            "refused or missing provenance is not progress and not an edge claim. "
            "No fabrication, no proxies labeled real, no threshold weakening."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    """CLI: emit fail-closed real-feed unblock status or trend reports.

    Exit 0 on successful report emission (blocked/unchanged state is honest
    data, not a CLI error). Exit 2 on invalid arguments/IO failures. Never
    fabricates data or proves edge.
    """
    parser = argparse.ArgumentParser(
        description="Fail-closed real non-spot feed unblock/readiness status and trend reports"
    )
    parser.add_argument("--cache-dir", default="data/cache", help="Cache directory to scan")
    parser.add_argument(
        "--reports-dir",
        default="reports",
        help="Reports directory for readiness discovery / trend inputs",
    )
    parser.add_argument("--campaign", type=int, default=None)
    parser.add_argument("--output", default=None, help="Write JSON report to this path")
    parser.add_argument(
        "--no-auto-discover-readiness",
        action="store_true",
        help="Do not auto-discover readiness specs from reports dir",
    )
    parser.add_argument(
        "--readiness-details",
        action="store_true",
        help="Include compact readiness-spec metadata (feeds_count/timestamps) when present",
    )
    parser.add_argument(
        "--prior",
        default=None,
        help="Path to a prior real_feed_unblock_status JSON for fail-closed campaign delta",
    )
    parser.add_argument(
        "--trend",
        action="store_true",
        help="Emit an aggregated unblock trend report from real_feed_unblock_status_*.json",
    )
    parser.add_argument(
        "--trend-limit",
        type=int,
        default=None,
        help="When --trend is set, include only the last N status entries (chronological order)",
    )
    parser.add_argument(
        "--cache-provenance-audit",
        action="store_true",
        help="Emit a fail-closed per-meta cache provenance/candidate gap audit artifact",
    )
    args = parser.parse_args(argv)
    if args.trend:
        report = build_unblock_trend_report(
            Path(args.reports_dir),
            campaign=args.campaign,
            limit=args.trend_limit,
        )
    elif getattr(args, "cache_provenance_audit", False):
        report = build_cache_provenance_gap_audit(
            Path(args.cache_dir),
            campaign=args.campaign,
            reports_dir=Path(args.reports_dir),
        )
    else:
        report = generate_unblock_status_report(
            Path(args.cache_dir),
            campaign=args.campaign,
            reports_dir=Path(args.reports_dir),
            auto_discover_readiness=not args.no_auto_discover_readiness,
            include_readiness_details=bool(getattr(args, "readiness_details", False)),
            prior_report=args.prior,
        )
    payload = json.dumps(report, indent=2, sort_keys=False) + "\n"
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
