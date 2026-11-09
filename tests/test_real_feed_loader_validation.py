"""Tests for fail-closed real feed loader/validator (Path C-maintain).

Uses synthetic test fixtures ONLY inside tests, explicitly flagged as test
fixtures; they are never labeled as real ingested data in production artifacts.
Proves the loader refuses missing/fabricated/proxy/invalid inputs.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from data.real_feed_loader import (
    CROSS_EXCHANGE_DUAL_VENUE_SAME_ASSET_SPEC,
    FUNDING_BASIS_CARRY_SPEC,
    INTRA_BAR_MICROSTRUCTURE_SPEC,
    TERM_STRUCTURE_REAL_IV_VOL_SURFACE_SPEC,
    RealFeedValidationError,
    build_cache_provenance_gap_audit,
    discover_readiness_specs,
    sha256_file,
    validate_and_load_real_feed,
)


def _valid_df() -> pd.DataFrame:
    # synthetic test fixture (test-only) — never labeled real data in artifacts
    return pd.DataFrame(
        {
            "timestamp_utc": pd.date_range("2026-04-01", periods=5, freq="1h", tz="UTC"),
            "symbol": ["BTCUSDT"] * 5,
            "funding_rate": [0.0001, -0.0002, 0.00005, 0.0, 0.0003],
            "mark_price_or_close": [50000.0, 50100.0, 49950.0, 50020.0, 50080.0],
        }
    )


def _write_artifact(tmp: Path, df: pd.DataFrame, meta_overrides: dict | None = None):
    pkl = tmp / "funding_binance_BTCUSDT_20260401_20260401_1h.pkl"
    df.to_pickle(pkl)
    meta = {
        "source_provider": "Binance",
        "source_endpoints": ["/fapi/v1/fundingRate"],
        "request_urls_or_params": {"symbol": "BTCUSDT"},
        "retrieved_at_utc": "2026-11-05T00:00:00Z",
        "symbol_map_native_to_repo": {"BTCUSDT": "BTC"},
        "window_start_utc": "2026-04-01T00:00:00Z",
        "window_end_utc": "2026-04-01T04:00:00Z",
        "freq": "1h",
        "row_count": len(df),
        "columns": list(df.columns),
        "sha256_pkl": sha256_file(pkl),
        "sha256_meta_inputs": "test-fixture",
        "real_data_only": True,
        "fabricated_data": False,
        "notes_limits_gaps": "none (test fixture payload; provenance fields satisfy schema)",
        "pkl_file": pkl.name,
    }
    if meta_overrides:
        meta.update(meta_overrides)
    meta_path = tmp / "funding_binance_BTCUSDT_20260401_20260401_1h.meta.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta_path, pkl


def test_valid_artifact_passes_fail_closed_checks(tmp_path: Path):
    meta_path, _ = _write_artifact(tmp_path, _valid_df())
    df, report = validate_and_load_real_feed(meta_path, "funding_basis_carry")
    assert report["ok"] is True and report["refused"] is False
    assert report["fail_closed"] is True
    assert len(df) == 5
    assert report["family_spec"] == FUNDING_BASIS_CARRY_SPEC.name


def test_refuses_missing_metadata(tmp_path: Path):
    missing = tmp_path / "nope.meta.json"
    with pytest.raises(RealFeedValidationError, match="metadata file missing"):
        validate_and_load_real_feed(missing)


def test_refuses_sha256_mismatch(tmp_path: Path):
    meta_path, pkl = _write_artifact(tmp_path, _valid_df())
    # tamper data
    df = _valid_df()
    df.loc[0, "funding_rate"] = 0.999
    df.to_pickle(pkl)
    with pytest.raises(RealFeedValidationError, match="sha256_pkl mismatch"):
        validate_and_load_real_feed(meta_path)


def test_refuses_missing_sha256(tmp_path: Path):
    meta_path, _ = _write_artifact(tmp_path, _valid_df(), {"sha256_pkl": ""})
    with pytest.raises(RealFeedValidationError, match="sha256_pkl missing"):
        validate_and_load_real_feed(meta_path)


def test_refuses_fabricated_flag(tmp_path: Path):
    meta_path, _ = _write_artifact(tmp_path, _valid_df(), {"fabricated_data": True})
    with pytest.raises(RealFeedValidationError, match="fabricated_data must be false"):
        validate_and_load_real_feed(meta_path)


def test_refuses_real_data_only_false(tmp_path: Path):
    meta_path, _ = _write_artifact(tmp_path, _valid_df(), {"real_data_only": False})
    with pytest.raises(RealFeedValidationError, match="real_data_only must be true"):
        validate_and_load_real_feed(meta_path)


def test_refuses_missing_data_file(tmp_path: Path):
    meta_path, pkl = _write_artifact(tmp_path, _valid_df())
    pkl.unlink()
    with pytest.raises(RealFeedValidationError, match="data file missing"):
        validate_and_load_real_feed(meta_path)


def test_refuses_missing_provenance_keys(tmp_path: Path):
    meta_path = tmp_path / "bad.meta.json"
    pkl = tmp_path / "bad.pkl"
    _valid_df().to_pickle(pkl)
    meta = {
        "real_data_only": True,
        "fabricated_data": False,
        "sha256_pkl": sha256_file(pkl),
        "pkl_file": pkl.name,
    }
    meta_path.write_text(json.dumps(meta), encoding="utf-8")
    with pytest.raises(RealFeedValidationError, match="missing required provenance keys"):
        validate_and_load_real_feed(meta_path)


def test_refuses_missing_required_columns(tmp_path: Path):
    df = _valid_df().drop(columns=["funding_rate"])
    meta_path, _ = _write_artifact(tmp_path, df)
    with pytest.raises(RealFeedValidationError, match="missing required columns"):
        validate_and_load_real_feed(meta_path)


def test_refuses_duplicate_timestamps(tmp_path: Path):
    df = _valid_df()
    df.loc[1, "timestamp_utc"] = df.loc[0, "timestamp_utc"]
    # keep monotonic check order realistic: make duplicates
    meta_path, _ = _write_artifact(tmp_path, df)
    with pytest.raises(RealFeedValidationError, match="not monotonic|duplicate"):
        validate_and_load_real_feed(meta_path)


def test_refuses_row_count_mismatch(tmp_path: Path):
    meta_path, _ = _write_artifact(tmp_path, _valid_df(), {"row_count": 999})
    with pytest.raises(RealFeedValidationError, match="row_count mismatch"):
        validate_and_load_real_feed(meta_path)


def test_refuses_unknown_family(tmp_path: Path):
    meta_path, _ = _write_artifact(tmp_path, _valid_df())
    with pytest.raises(RealFeedValidationError, match="unknown/unsupported family"):
        validate_and_load_real_feed(meta_path, "nonexistent_family")


def test_refuses_extreme_undocumented_funding_sentinel(tmp_path: Path):
    df = _valid_df()
    df.loc[0, "funding_rate"] = 99.0  # impossible, undocumented
    meta_path, _ = _write_artifact(tmp_path, df)
    with pytest.raises(RealFeedValidationError, match="impossible"):
        validate_and_load_real_feed(meta_path)


def test_refuses_proxy_labeled_real_in_notes(tmp_path: Path):
    meta_path, _ = _write_artifact(
        tmp_path,
        _valid_df(),
        {"notes_limits_gaps": "proxy labeled real funding derived from spot"},
    )
    with pytest.raises(RealFeedValidationError, match="proxy/fabricated-as-real"):
        validate_and_load_real_feed(meta_path)


def test_accepts_real_feed_in_cache_when_provenance_valid(tmp_path: Path):
    # Simulate a legitimately ingested file living under a cache-like dir.
    cache = tmp_path / "data" / "cache"
    cache.mkdir(parents=True)
    meta_path, _ = _write_artifact(cache, _valid_df())
    df, report = validate_and_load_real_feed(meta_path)
    assert report["ok"] and report["rows"] == 5


def test_scan_cache_empty_dir_reports_blocked(tmp_path: Path):
    from data.real_feed_loader import scan_cache_for_real_nonspot_feeds
    cache = tmp_path / "cache"
    cache.mkdir()
    r = scan_cache_for_real_nonspot_feeds(cache)
    assert r["fail_closed"] is True
    assert r["new_real_feeds_with_provenance_found"] is False
    assert all(v["status"] == "blocked_no_real_feed" for v in r["families"].values())


def test_scan_cache_missing_dir_reports_blocked(tmp_path: Path):
    from data.real_feed_loader import scan_cache_for_real_nonspot_feeds
    r = scan_cache_for_real_nonspot_feeds(tmp_path / "nope")
    assert r["cache_exists"] is False
    assert r["new_real_feeds_with_provenance_found"] is False


def test_scan_cache_rejects_spot_meta_as_nonspot_feed(tmp_path: Path):
    from data.real_feed_loader import scan_cache_for_real_nonspot_feeds
    cache = tmp_path / "cache"
    cache.mkdir()
    # existing spot-style meta (no non-spot family/provenance keys) must not count
    (cache / "BTC_2026-04-01_2026-10-30_1h.meta.json").write_text(
        json.dumps(
            {
                "symbols": ["BTC"],
                "start": "2026-04-01",
                "real_data_only": True,
                "fabricated_data": False,
            }
        ),
        encoding="utf-8",
    )
    r = scan_cache_for_real_nonspot_feeds(cache)
    assert r["new_real_feeds_with_provenance_found"] is False
    assert r["meta_files_scanned"] >= 1


def test_scan_cache_accepts_valid_nonspot_funding_artifact(tmp_path: Path):
    from data.real_feed_loader import scan_cache_for_real_nonspot_feeds
    cache = tmp_path / "cache"
    cache.mkdir()
    _write_artifact(cache, _valid_df())  # valid funding provenance+schema
    r = scan_cache_for_real_nonspot_feeds(cache)
    assert r["new_real_feeds_with_provenance_found"] is True
    assert r["families"]["funding_basis_carry"]["status"] == "real_feed_with_provenance_present"
    assert len(r["families"]["funding_basis_carry"]["valid_artifacts"]) == 1


def _valid_dual_venue_df() -> pd.DataFrame:
    # synthetic test fixture (test-only) — never labeled real data in artifacts
    return pd.DataFrame(
        {
            "timestamp_utc": pd.date_range("2026-04-01", periods=5, freq="1h", tz="UTC"),
            "asset": ["BTC"] * 5,
            "price_venue_a": [50000.0, 50100.0, 49950.0, 50020.0, 50080.0],
            "price_venue_b": [50005.0, 50110.0, 49945.0, 50025.0, 50090.0],
            "mid_or_close_flag_a": ["close"] * 5,
            "mid_or_close_flag_b": ["close"] * 5,
        }
    )


def _write_dual_venue_artifact(tmp: Path, df: pd.DataFrame, meta_overrides: dict | None = None):
    pkl = tmp / "dualvenue_BTC_binance_coinbase_20260401_20260401_1h.pkl"
    df.to_pickle(pkl)
    meta = {
        "source_provider_a": "Binance",
        "source_provider_b": "Coinbase",
        "endpoints_a": ["/api/v3/klines?symbol=BTCUSDT&interval=1h"],
        "endpoints_b": ["/products/BTC-USD/candles"],
        "retrieved_at_utc": "2026-11-05T00:00:00Z",
        "symbol_map_a": {"BTCUSDT": "BTC"},
        "symbol_map_b": {"BTC-USD": "BTC"},
        "clock_sync_assumption": "venue clocks aligned to UTC bar open",
        "row_count_aligned": len(df),
        "rows_dropped_misaligned": 0,
        "sha256_pkl": sha256_file(pkl),
        "sha256_meta_inputs": "test-fixture",
        "real_data_only": True,
        "fabricated_data": False,
        "notes_limits_gaps": "none (test fixture payload; provenance fields satisfy schema)",
        "pkl_file": pkl.name,
    }
    if meta_overrides:
        meta.update(meta_overrides)
    meta_path = tmp / "dualvenue_BTC_binance_coinbase_20260401_20260401_1h.meta.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta_path, pkl


def test_dual_venue_valid_artifact_passes_fail_closed_checks(tmp_path: Path):
    meta_path, _ = _write_dual_venue_artifact(tmp_path, _valid_dual_venue_df())
    df, report = validate_and_load_real_feed(
        meta_path, "cross_exchange_dual_venue_same_asset"
    )
    assert report["ok"] is True and report["refused"] is False
    assert report["fail_closed"] is True
    assert len(df) == 5
    assert report["family_spec"] == CROSS_EXCHANGE_DUAL_VENUE_SAME_ASSET_SPEC.name


def test_dual_venue_refuses_missing_metadata(tmp_path: Path):
    missing = tmp_path / "nope.meta.json"
    with pytest.raises(RealFeedValidationError, match="metadata file missing"):
        validate_and_load_real_feed(missing, "cross_exchange_dual_venue_same_asset")


def test_dual_venue_refuses_sha256_mismatch(tmp_path: Path):
    meta_path, pkl = _write_dual_venue_artifact(tmp_path, _valid_dual_venue_df())
    df = _valid_dual_venue_df()
    df.loc[0, "price_venue_a"] = 999999.0
    df.to_pickle(pkl)
    with pytest.raises(RealFeedValidationError, match="sha256_pkl mismatch"):
        validate_and_load_real_feed(meta_path, "cross_exchange_dual_venue_same_asset")


def test_dual_venue_refuses_missing_sha256(tmp_path: Path):
    meta_path, _ = _write_dual_venue_artifact(tmp_path, _valid_dual_venue_df(), {"sha256_pkl": ""})
    with pytest.raises(RealFeedValidationError, match="sha256_pkl missing"):
        validate_and_load_real_feed(meta_path, "cross_exchange_dual_venue_same_asset")


def test_dual_venue_refuses_fabricated_flag(tmp_path: Path):
    meta_path, _ = _write_dual_venue_artifact(
        tmp_path, _valid_dual_venue_df(), {"fabricated_data": True}
    )
    with pytest.raises(RealFeedValidationError, match="fabricated_data must be false"):
        validate_and_load_real_feed(meta_path, "cross_exchange_dual_venue_same_asset")


def test_dual_venue_refuses_real_data_only_false(tmp_path: Path):
    meta_path, _ = _write_dual_venue_artifact(
        tmp_path, _valid_dual_venue_df(), {"real_data_only": False}
    )
    with pytest.raises(RealFeedValidationError, match="real_data_only must be true"):
        validate_and_load_real_feed(meta_path, "cross_exchange_dual_venue_same_asset")


def test_dual_venue_refuses_missing_data_file(tmp_path: Path):
    meta_path, pkl = _write_dual_venue_artifact(tmp_path, _valid_dual_venue_df())
    pkl.unlink()
    with pytest.raises(RealFeedValidationError, match="data file missing"):
        validate_and_load_real_feed(meta_path, "cross_exchange_dual_venue_same_asset")


def test_dual_venue_refuses_missing_provenance_keys(tmp_path: Path):
    meta_path = tmp_path / "bad.meta.json"
    pkl = tmp_path / "bad.pkl"
    _valid_dual_venue_df().to_pickle(pkl)
    meta = {
        "real_data_only": True,
        "fabricated_data": False,
        "sha256_pkl": sha256_file(pkl),
        "pkl_file": pkl.name,
    }
    meta_path.write_text(json.dumps(meta), encoding="utf-8")
    with pytest.raises(RealFeedValidationError, match="missing required provenance keys"):
        validate_and_load_real_feed(meta_path, "cross_exchange_dual_venue_same_asset")


def test_dual_venue_refuses_missing_required_columns(tmp_path: Path):
    df = _valid_dual_venue_df().drop(columns=["price_venue_b"])
    meta_path, _ = _write_dual_venue_artifact(tmp_path, df)
    with pytest.raises(RealFeedValidationError, match="missing required columns"):
        validate_and_load_real_feed(meta_path, "cross_exchange_dual_venue_same_asset")


def test_dual_venue_refuses_duplicate_timestamps(tmp_path: Path):
    df = _valid_dual_venue_df()
    df.loc[1, "timestamp_utc"] = df.loc[0, "timestamp_utc"]
    meta_path, _ = _write_dual_venue_artifact(tmp_path, df)
    with pytest.raises(RealFeedValidationError, match="not monotonic|duplicate"):
        validate_and_load_real_feed(meta_path, "cross_exchange_dual_venue_same_asset")


def test_dual_venue_refuses_row_count_mismatch(tmp_path: Path):
    meta_path, _ = _write_dual_venue_artifact(
        tmp_path, _valid_dual_venue_df(), {"row_count_aligned": 999}
    )
    with pytest.raises(RealFeedValidationError, match="row_count mismatch"):
        validate_and_load_real_feed(meta_path, "cross_exchange_dual_venue_same_asset")


def test_dual_venue_refuses_unknown_family(tmp_path: Path):
    meta_path, _ = _write_dual_venue_artifact(tmp_path, _valid_dual_venue_df())
    with pytest.raises(RealFeedValidationError, match="unknown/unsupported family"):
        validate_and_load_real_feed(meta_path, "nonexistent_family")


def test_dual_venue_refuses_single_venue_as_dual_proxy(tmp_path: Path):
    df = _valid_dual_venue_df()
    df["price_venue_b"] = df["price_venue_a"]  # identical series -> proxy
    meta_path, _ = _write_dual_venue_artifact(tmp_path, df)
    with pytest.raises(RealFeedValidationError, match="single venue mislabeled as dual venue"):
        validate_and_load_real_feed(meta_path, "cross_exchange_dual_venue_same_asset")


def test_dual_venue_refuses_proxy_labeled_real_in_notes(tmp_path: Path):
    meta_path, _ = _write_dual_venue_artifact(
        tmp_path,
        _valid_dual_venue_df(),
        {"notes_limits_gaps": "venue b derived from venue a proxy labeled real"},
    )
    with pytest.raises(RealFeedValidationError, match="proxy/fabricated-as-real"):
        validate_and_load_real_feed(meta_path, "cross_exchange_dual_venue_same_asset")


def test_dual_venue_accepts_real_feed_in_cache_when_provenance_valid(tmp_path: Path):
    cache = tmp_path / "data" / "cache"
    cache.mkdir(parents=True)
    meta_path, _ = _write_dual_venue_artifact(cache, _valid_dual_venue_df())
    df, report = validate_and_load_real_feed(
        meta_path, "cross_exchange_dual_venue_same_asset"
    )
    assert report["ok"] and report["rows"] == 5

def _valid_term_structure_df() -> pd.DataFrame:
    # synthetic test fixture (test-only) — never labeled real data in artifacts
    return pd.DataFrame(
        {
            "timestamp_utc": pd.date_range("2026-04-01", periods=5, freq="1h", tz="UTC"),
            "underlying": ["BTC"] * 5,
            "iv_30d": [0.62, 0.63, 0.61, 0.64, 0.60],
            "iv_90d": [0.58, 0.59, 0.57, 0.60, 0.56],
        }
    )


def _write_term_structure_artifact(
    tmp: Path, df: pd.DataFrame, meta_overrides: dict | None = None
):
    pkl = tmp / "iv_deribit_BTC_20260401_20260401_1h.pkl"
    df.to_pickle(pkl)
    meta = {
        "source_provider": "Deribit",
        "endpoints": ["/public/get_historical_volatility?currency=BTC"],
        "retrieved_at_utc": "2026-11-05T00:00:00Z",
        "underlying_map": {"BTC": "BTC"},
        "iv_definition": "Deribit DVOL / implied volatility (30d, 90d tenor proxies as documented)",
        "row_count": len(df),
        "sha256_pkl": sha256_file(pkl),
        "sha256_meta_inputs": "test-fixture",
        "real_data_only": True,
        "fabricated_data": False,
        "notes_limits_gaps": "none (test fixture payload; provenance fields satisfy schema)",
        "pkl_file": pkl.name,
    }
    if meta_overrides:
        meta.update(meta_overrides)
    meta_path = tmp / "iv_deribit_BTC_20260401_20260401_1h.meta.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta_path, pkl


def test_term_structure_valid_artifact_passes_fail_closed_checks(tmp_path: Path):
    meta_path, _ = _write_term_structure_artifact(tmp_path, _valid_term_structure_df())
    df, report = validate_and_load_real_feed(
        meta_path, "term_structure_real_iv_vol_surface"
    )
    assert report["ok"] is True and report["refused"] is False
    assert report["fail_closed"] is True
    assert len(df) == 5
    assert report["family_spec"] == TERM_STRUCTURE_REAL_IV_VOL_SURFACE_SPEC.name


def test_term_structure_refuses_missing_metadata(tmp_path: Path):
    missing = tmp_path / "nope_iv.meta.json"
    with pytest.raises(RealFeedValidationError, match="metadata file missing"):
        validate_and_load_real_feed(missing, "term_structure_real_iv_vol_surface")


def test_term_structure_refuses_sha256_mismatch(tmp_path: Path):
    meta_path, pkl = _write_term_structure_artifact(tmp_path, _valid_term_structure_df())
    df = _valid_term_structure_df()
    df.loc[0, "iv_30d"] = 0.99
    df.to_pickle(pkl)
    with pytest.raises(RealFeedValidationError, match="sha256_pkl mismatch"):
        validate_and_load_real_feed(meta_path, "term_structure_real_iv_vol_surface")


def test_term_structure_refuses_missing_sha256(tmp_path: Path):
    meta_path, _ = _write_term_structure_artifact(
        tmp_path, _valid_term_structure_df(), {"sha256_pkl": ""}
    )
    with pytest.raises(RealFeedValidationError, match="sha256_pkl missing"):
        validate_and_load_real_feed(meta_path, "term_structure_real_iv_vol_surface")


def test_term_structure_refuses_fabricated_flag(tmp_path: Path):
    meta_path, _ = _write_term_structure_artifact(
        tmp_path, _valid_term_structure_df(), {"fabricated_data": True}
    )
    with pytest.raises(RealFeedValidationError, match="fabricated_data must be false"):
        validate_and_load_real_feed(meta_path, "term_structure_real_iv_vol_surface")


def test_term_structure_refuses_real_data_only_false(tmp_path: Path):
    meta_path, _ = _write_term_structure_artifact(
        tmp_path, _valid_term_structure_df(), {"real_data_only": False}
    )
    with pytest.raises(RealFeedValidationError, match="real_data_only must be true"):
        validate_and_load_real_feed(meta_path, "term_structure_real_iv_vol_surface")


def test_term_structure_refuses_missing_data_file(tmp_path: Path):
    meta_path, pkl = _write_term_structure_artifact(tmp_path, _valid_term_structure_df())
    pkl.unlink()
    with pytest.raises(RealFeedValidationError, match="data file missing"):
        validate_and_load_real_feed(meta_path, "term_structure_real_iv_vol_surface")


def test_term_structure_refuses_missing_provenance_keys(tmp_path: Path):
    meta_path = tmp_path / "bad_iv.meta.json"
    pkl = tmp_path / "bad_iv.pkl"
    _valid_term_structure_df().to_pickle(pkl)
    meta = {
        "real_data_only": True,
        "fabricated_data": False,
        "sha256_pkl": sha256_file(pkl),
        "pkl_file": pkl.name,
    }
    meta_path.write_text(json.dumps(meta), encoding="utf-8")
    with pytest.raises(RealFeedValidationError, match="missing required provenance keys"):
        validate_and_load_real_feed(meta_path, "term_structure_real_iv_vol_surface")


def test_term_structure_refuses_missing_required_columns_iv_30d(tmp_path: Path):
    df = _valid_term_structure_df().drop(columns=["iv_30d"])
    meta_path, _ = _write_term_structure_artifact(tmp_path, df)
    with pytest.raises(RealFeedValidationError, match="missing required columns"):
        validate_and_load_real_feed(meta_path, "term_structure_real_iv_vol_surface")


def test_term_structure_refuses_missing_required_columns_iv_90d(tmp_path: Path):
    df = _valid_term_structure_df().drop(columns=["iv_90d"])
    meta_path, _ = _write_term_structure_artifact(tmp_path, df)
    with pytest.raises(RealFeedValidationError, match="missing required columns"):
        validate_and_load_real_feed(meta_path, "term_structure_real_iv_vol_surface")


def test_term_structure_refuses_duplicate_timestamps(tmp_path: Path):
    df = _valid_term_structure_df()
    df.loc[1, "timestamp_utc"] = df.loc[0, "timestamp_utc"]
    meta_path, _ = _write_term_structure_artifact(tmp_path, df)
    with pytest.raises(RealFeedValidationError, match="not monotonic|duplicate"):
        validate_and_load_real_feed(meta_path, "term_structure_real_iv_vol_surface")


def test_term_structure_refuses_row_count_mismatch(tmp_path: Path):
    meta_path, _ = _write_term_structure_artifact(
        tmp_path, _valid_term_structure_df(), {"row_count": 999}
    )
    with pytest.raises(RealFeedValidationError, match="row_count mismatch"):
        validate_and_load_real_feed(meta_path, "term_structure_real_iv_vol_surface")


def test_term_structure_refuses_realized_vol_labeled_as_iv(tmp_path: Path):
    meta_path, _ = _write_term_structure_artifact(
        tmp_path,
        _valid_term_structure_df(),
        {"iv_definition": "realized volatility labeled as iv 30d/90d"},
    )
    with pytest.raises(RealFeedValidationError, match="realized-vol/proxy labeled as IV"):
        validate_and_load_real_feed(meta_path, "term_structure_real_iv_vol_surface")


def test_term_structure_refuses_realized_vol_without_implied_basis(tmp_path: Path):
    meta_path, _ = _write_term_structure_artifact(
        tmp_path,
        _valid_term_structure_df(),
        {"iv_definition": "30-day historical realized volatility series"},
    )
    with pytest.raises(RealFeedValidationError, match="proxy-as-IV|realized"):
        validate_and_load_real_feed(meta_path, "term_structure_real_iv_vol_surface")


def test_term_structure_refuses_proxy_labeled_real_in_notes(tmp_path: Path):
    meta_path, _ = _write_term_structure_artifact(
        tmp_path,
        _valid_term_structure_df(),
        {"notes_limits_gaps": "proxy labeled real IV derived from spot"},
    )
    with pytest.raises(RealFeedValidationError, match="proxy/fabricated-as-real"):
        validate_and_load_real_feed(meta_path, "term_structure_real_iv_vol_surface")


def _valid_intrabar_microstructure_df(kind: str = "trades") -> pd.DataFrame:
    # synthetic test fixture (test-only) — never labeled real data in artifacts
    base = {
        "timestamp_utc": pd.date_range("2026-04-01", periods=5, freq="1min", tz="UTC"),
        "symbol": ["BTCUSDT"] * 5,
    }
    if kind == "trades":
        base.update(
            {
                "price": [50000.0, 50010.0, 49990.0, 50005.0, 50015.0],
                "qty": [0.1, 0.2, 0.15, 0.3, 0.05],
                "side_or_is_buyer_maker": ["buy", "sell", "buy", "sell", "buy"],
            }
        )
    else:  # book
        base.update(
            {
                "bid_px_levels": [
                    [49995.0, 49990.0],
                    [50005.0, 50000.0],
                    [49998.0, 49993.0],
                    [50002.0, 49997.0],
                    [49999.0, 49994.0],
                ],
                "ask_px_levels": [
                    [50005.0, 50010.0],
                    [50015.0, 50020.0],
                    [50008.0, 50013.0],
                    [50012.0, 50017.0],
                    [50009.0, 50014.0],
                ],
                "bid_sz_levels": [
                    [0.5, 0.3],
                    [0.4, 0.2],
                    [0.6, 0.1],
                    [0.5, 0.3],
                    [0.7, 0.2],
                ],
                "ask_sz_levels": [
                    [0.3, 0.5],
                    [0.2, 0.4],
                    [0.1, 0.6],
                    [0.3, 0.5],
                    [0.2, 0.7],
                ],
                "depth": [1.0, 1.0, 1.0, 1.0, 1.0],
            }
        )
    return pd.DataFrame(base)


def _write_intrabar_microstructure_artifact(
    tmp: Path, df: pd.DataFrame, meta_overrides: dict | None = None, kind: str = "trades"
):
    pkl = tmp / f"micro_binance_BTCUSDT_20260401_20260401_1min_{kind}.pkl"
    df.to_pickle(pkl)
    meta = {
        "source_provider": "Binance",
        "endpoints_or_files": ["/api/v3/aggTrades?symbol=BTCUSDT"],
        "retrieved_at_utc": "2026-11-05T00:00:00Z",
        "symbol_map": {"BTCUSDT": "BTC"},
        "kind": kind,
        "row_count": len(df),
        "sha256_pkl": sha256_file(pkl),
        "sha256_meta_inputs": "test-fixture",
        "real_data_only": True,
        "fabricated_data": False,
        "notes_limits_gaps": "none (test fixture payload; provenance fields satisfy schema)",
        "pkl_file": pkl.name,
    }
    if meta_overrides:
        meta.update(meta_overrides)
    meta_path = tmp / f"micro_binance_BTCUSDT_20260401_20260401_1min_{kind}.meta.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta_path, pkl


def test_intrabar_microstructure_trades_valid_artifact_passes_fail_closed_checks(tmp_path: Path):
    meta_path, _ = _write_intrabar_microstructure_artifact(
        tmp_path, _valid_intrabar_microstructure_df("trades"), kind="trades"
    )
    df, report = validate_and_load_real_feed(meta_path, "intrabar_microstructure")
    assert report["ok"] is True and report["refused"] is False
    assert report["fail_closed"] is True
    assert len(df) == 5
    assert report["family_spec"] == INTRA_BAR_MICROSTRUCTURE_SPEC.name


def test_intrabar_microstructure_book_valid_artifact_passes_fail_closed_checks(tmp_path: Path):
    meta_path, _ = _write_intrabar_microstructure_artifact(
        tmp_path, _valid_intrabar_microstructure_df("book"), kind="book"
    )
    df, report = validate_and_load_real_feed(meta_path, "intrabar_microstructure")
    assert report["ok"] is True and report["refused"] is False
    assert report["fail_closed"] is True
    assert len(df) == 5
    assert report["family_spec"] == INTRA_BAR_MICROSTRUCTURE_SPEC.name


def test_intrabar_microstructure_refuses_missing_metadata(tmp_path: Path):
    missing = tmp_path / "nope_micro.meta.json"
    with pytest.raises(RealFeedValidationError, match="metadata file missing"):
        validate_and_load_real_feed(missing, "intrabar_microstructure")


def test_intrabar_microstructure_refuses_sha256_mismatch(tmp_path: Path):
    meta_path, pkl = _write_intrabar_microstructure_artifact(
        tmp_path, _valid_intrabar_microstructure_df("trades"), kind="trades"
    )
    df = _valid_intrabar_microstructure_df("trades")
    df.loc[0, "price"] = 999999.0
    df.to_pickle(pkl)
    with pytest.raises(RealFeedValidationError, match="sha256_pkl mismatch"):
        validate_and_load_real_feed(meta_path, "intrabar_microstructure")


def test_intrabar_microstructure_refuses_missing_sha256(tmp_path: Path):
    meta_path, _ = _write_intrabar_microstructure_artifact(
        tmp_path, _valid_intrabar_microstructure_df("trades"), {"sha256_pkl": ""}, kind="trades"
    )
    with pytest.raises(RealFeedValidationError, match="sha256_pkl missing"):
        validate_and_load_real_feed(meta_path, "intrabar_microstructure")


def test_intrabar_microstructure_refuses_fabricated_flag(tmp_path: Path):
    meta_path, _ = _write_intrabar_microstructure_artifact(
        tmp_path,
        _valid_intrabar_microstructure_df("trades"),
        {"fabricated_data": True},
        kind="trades",
    )
    with pytest.raises(RealFeedValidationError, match="fabricated_data must be false"):
        validate_and_load_real_feed(meta_path, "intrabar_microstructure")


def test_intrabar_microstructure_refuses_real_data_only_false(tmp_path: Path):
    meta_path, _ = _write_intrabar_microstructure_artifact(
        tmp_path,
        _valid_intrabar_microstructure_df("trades"),
        {"real_data_only": False},
        kind="trades",
    )
    with pytest.raises(RealFeedValidationError, match="real_data_only must be true"):
        validate_and_load_real_feed(meta_path, "intrabar_microstructure")


def test_intrabar_microstructure_refuses_missing_data_file(tmp_path: Path):
    meta_path, pkl = _write_intrabar_microstructure_artifact(
        tmp_path, _valid_intrabar_microstructure_df("trades"), kind="trades"
    )
    pkl.unlink()
    with pytest.raises(RealFeedValidationError, match="data file missing"):
        validate_and_load_real_feed(meta_path, "intrabar_microstructure")


def test_intrabar_microstructure_refuses_missing_provenance_keys(tmp_path: Path):
    meta_path = tmp_path / "bad_micro.meta.json"
    pkl = tmp_path / "bad_micro.pkl"
    _valid_intrabar_microstructure_df("trades").to_pickle(pkl)
    meta = {
        "real_data_only": True,
        "fabricated_data": False,
        "sha256_pkl": sha256_file(pkl),
        "pkl_file": pkl.name,
    }
    meta_path.write_text(json.dumps(meta), encoding="utf-8")
    with pytest.raises(RealFeedValidationError, match="missing required provenance keys"):
        validate_and_load_real_feed(meta_path, "intrabar_microstructure")


def test_intrabar_microstructure_refuses_invalid_kind(tmp_path: Path):
    meta_path, _ = _write_intrabar_microstructure_artifact(
        tmp_path, _valid_intrabar_microstructure_df("trades"), {"kind": "not_a_kind"}, kind="trades"
    )
    with pytest.raises(RealFeedValidationError, match="invalid/missing kind"):
        validate_and_load_real_feed(meta_path, "intrabar_microstructure")


def test_intrabar_microstructure_refuses_missing_required_columns_trades(tmp_path: Path):
    df = _valid_intrabar_microstructure_df("trades").drop(columns=["qty"])
    meta_path, _ = _write_intrabar_microstructure_artifact(tmp_path, df, kind="trades")
    with pytest.raises(RealFeedValidationError, match="missing required columns"):
        validate_and_load_real_feed(meta_path, "intrabar_microstructure")


def test_intrabar_microstructure_refuses_missing_required_columns_book(tmp_path: Path):
    df = _valid_intrabar_microstructure_df("book").drop(columns=["depth"])
    meta_path, _ = _write_intrabar_microstructure_artifact(tmp_path, df, kind="book")
    with pytest.raises(RealFeedValidationError, match="missing required columns"):
        validate_and_load_real_feed(meta_path, "intrabar_microstructure")


def test_intrabar_microstructure_refuses_duplicate_timestamps(tmp_path: Path):
    df = _valid_intrabar_microstructure_df("trades")
    df.loc[1, "timestamp_utc"] = df.loc[0, "timestamp_utc"]
    meta_path, _ = _write_intrabar_microstructure_artifact(tmp_path, df, kind="trades")
    with pytest.raises(RealFeedValidationError, match="not monotonic|duplicate"):
        validate_and_load_real_feed(meta_path, "intrabar_microstructure")


def test_intrabar_microstructure_refuses_row_count_mismatch(tmp_path: Path):
    meta_path, _ = _write_intrabar_microstructure_artifact(
        tmp_path,
        _valid_intrabar_microstructure_df("trades"),
        {"row_count": 999},
        kind="trades",
    )
    with pytest.raises(RealFeedValidationError, match="row_count mismatch"):
        validate_and_load_real_feed(meta_path, "intrabar_microstructure")


def test_intrabar_microstructure_refuses_unknown_family(tmp_path: Path):
    meta_path, _ = _write_intrabar_microstructure_artifact(
        tmp_path, _valid_intrabar_microstructure_df("trades"), kind="trades"
    )
    with pytest.raises(RealFeedValidationError, match="unknown/unsupported family"):
        validate_and_load_real_feed(meta_path, "nonexistent_family")


def test_intrabar_microstructure_refuses_resampled_to_1h_as_microstructure_proxy(tmp_path: Path):
    meta_path, _ = _write_intrabar_microstructure_artifact(
        tmp_path,
        _valid_intrabar_microstructure_df("trades"),
        {"notes_limits_gaps": "resampled to 1h from spot then presented as microstructure"},
        kind="trades",
    )
    with pytest.raises(RealFeedValidationError, match="resampled-to-1h-as-microstructure"):
        validate_and_load_real_feed(meta_path, "intrabar_microstructure")


def test_intrabar_microstructure_refuses_proxy_labeled_real_in_notes(tmp_path: Path):
    meta_path, _ = _write_intrabar_microstructure_artifact(
        tmp_path,
        _valid_intrabar_microstructure_df("trades"),
        {"notes_limits_gaps": "microstructure proxy labeled real derived from spot"},
        kind="trades",
    )
    with pytest.raises(RealFeedValidationError, match="proxy/fabricated-as-real"):
        validate_and_load_real_feed(meta_path, "intrabar_microstructure")


def test_intrabar_microstructure_accepts_real_feed_in_cache_when_provenance_valid(tmp_path: Path):
    cache = tmp_path / "data" / "cache"
    cache.mkdir(parents=True)
    meta_path, _ = _write_intrabar_microstructure_artifact(
        cache, _valid_intrabar_microstructure_df("trades"), kind="trades"
    )
    df, report = validate_and_load_real_feed(meta_path, "intrabar_microstructure")
    assert report["ok"] and report["rows"] == 5


# --- Campaign #17: audit_cache_for_real_nonspot_feeds (fail-closed infrastructure) ---
from data.real_feed_loader import audit_cache_for_real_nonspot_feeds  # noqa: E402 (appended)


def test_audit_cache_for_real_nonspot_feeds_no_candidates(tmp_path: Path):
    cache = tmp_path / "cache"
    cache.mkdir()
    (cache / "spot.meta.json").write_text(
        json.dumps({"kind": "binance_spot"}), encoding="utf-8"
    )
    result = audit_cache_for_real_nonspot_feeds(cache, campaign=17)
    assert result["fail_closed"] is True
    assert result["real_data_only"] is True
    assert result["fabricated_data"] is False
    assert result["oos_edge_proven"] is False
    assert result["campaign"] == 17
    assert result["conclusion"] == "NO_VALID_NONSPOT_PROVENANCE_ARTIFACTS"
    assert result["candidate_validation"] == []
    assert result["families"]["funding_basis_carry"]["status"] == "blocked_no_real_feed"
    assert result["scan"]["meta_files_scanned"] == 1
    assert result["non_candidate_meta_count"] == 1


def test_audit_cache_accepts_valid_nonspot_funding_artifact(tmp_path: Path):
    cache = tmp_path / "cache"
    cache.mkdir()
    _write_artifact(cache, _valid_df())
    result = audit_cache_for_real_nonspot_feeds(cache, campaign=17)
    assert result["scan"]["new_real_feeds_with_provenance_found"] is True
    assert (
        result["conclusion"] == "VALID_NONSPOT_PROVENANCE_ARTIFACTS_FOUND"
    )
    assert (
        result["families"]["funding_basis_carry"]["status"]
        == "real_feed_with_provenance_present"
    )
    assert len(result["candidate_validation"]) == 1
    assert result["candidate_validation"][0]["ok"] is True
    assert result["candidate_validation"][0]["family"] == "funding_basis_carry"
    assert result["oos_edge_proven"] is False


def test_audit_cache_records_candidate_refusal(tmp_path: Path):
    cache = tmp_path / "cache"
    cache.mkdir()
    pkl = cache / "funding_bad.pkl"
    _valid_df().to_pickle(pkl)
    meta = {
        "family": "funding_basis_carry",
        "real_data_only": False,
        "fabricated_data": True,
        "sha256_pkl": "bad",
        "pkl_file": pkl.name,
    }
    (cache / "funding_bad.meta.json").write_text(json.dumps(meta), encoding="utf-8")
    result = audit_cache_for_real_nonspot_feeds(cache, campaign=17)
    assert result["scan"]["candidate_hits"]
    assert result["conclusion"] == "NO_VALID_NONSPOT_PROVENANCE_ARTIFACTS"
    assert result["families"]["funding_basis_carry"]["status"] == "blocked_no_real_feed"
    assert any(
        v["ok"] is False and v["refused"] is True
        for v in result["candidate_validation"]
    )


# --- Campaign #18: generate_unblock_status_report (fail-closed infrastructure) ---
from data.real_feed_loader import (  # noqa: E402
    build_unblock_trend_report,
    compare_unblock_status,
    generate_unblock_status_report,
)


def test_generate_unblock_status_report_no_candidates(tmp_path: Path):
    cache = tmp_path / "cache"
    cache.mkdir()
    (cache / "spot.meta.json").write_text(json.dumps({"kind": "binance_spot"}), encoding="utf-8")
    result = generate_unblock_status_report(cache, campaign=18)
    assert result["fail_closed"] is True
    assert result["real_data_only"] is True
    assert result["fabricated_data"] is False
    assert result["oos_edge_proven"] is False
    assert result["campaign"] == 18
    assert result["path_r_triggered"] is False
    assert result["conclusion"] == "PATH_C_MAINTAIN_STILL_BLOCKED"
    assert result["audit_conclusion"] == "NO_VALID_NONSPOT_PROVENANCE_ARTIFACTS"
    required_blocked = {
        "funding_basis_carry",
        "cross_exchange_dual_venue_same_asset",
        "term_structure_real_iv_vol_surface",
        "intrabar_microstructure",
    }
    assert required_blocked.issubset(set(result["blocked_families"]))
    # real_quote_volume may also be tracked as blocked by current loader; honest.
    assert result["scan_summary"]["candidate_hits"] == 0
    assert result["scan_summary"]["new_real_feeds_with_provenance_found"] is False


def test_generate_unblock_status_report_accepts_valid_nonspot(tmp_path: Path):
    cache = tmp_path / "cache"
    cache.mkdir()
    _write_artifact(cache, _valid_df())
    result = generate_unblock_status_report(cache, campaign=18)
    assert result["path_r_triggered"] is True
    assert result["conclusion"] == "PATH_R_ELIGIBLE_VALID_NONSPOT_FEED_PRESENT"
    assert "funding_basis_carry" not in result["blocked_families"]
    assert result["scan_summary"]["new_real_feeds_with_provenance_found"] is True
    assert result["oos_edge_proven"] is False


def test_generate_unblock_status_report_records_readiness_specs(tmp_path: Path):
    cache = tmp_path / "cache"
    cache.mkdir()
    spec = tmp_path / "spec.json"
    spec.write_text(json.dumps({"artifact": "x"}), encoding="utf-8")
    missing = tmp_path / "missing.json"
    result = generate_unblock_status_report(
        cache, campaign=18, readiness_specs=[str(spec), str(missing)]
    )
    assert result["readiness_specs"][0]["exists"] is True
    assert result["readiness_specs"][0]["artifact"] == "x"
    assert result["readiness_specs"][1]["exists"] is False


def test_discover_readiness_specs_finds_real_feed_readiness(tmp_path: Path):
    reports = tmp_path / "reports"
    reports.mkdir()
    spec = reports / "real_feed_ingestion_readiness_20261105T104640Z.json"
    spec.write_text(
        json.dumps(
            {
                "artifact": "real_feed_ingestion_readiness",
                "campaign": 9,
                "feeds": [
                    {"family": "funding_basis_carry"},
                    {"family": "cross_exchange_dual_venue_same_asset"},
                ],
            }
        ),
        encoding="utf-8",
    )
    unrelated = reports / "live_readiness_checklist_mt.json"
    unrelated.write_text(json.dumps({"status": "blocked"}), encoding="utf-8")
    found = discover_readiness_specs(reports)
    assert len(found) == 1
    assert found[0]["artifact"] == "real_feed_ingestion_readiness"
    assert "funding_basis_carry" in found[0]["families_covered"]
    assert found[0]["relevant_to_nonspot_unblock"] is True


def test_discover_readiness_specs_handles_parse_error(tmp_path: Path):
    reports = tmp_path / "reports"
    reports.mkdir()
    bad = reports / "bad_readiness.json"
    bad.write_text("{not json", encoding="utf-8")
    found = discover_readiness_specs(reports)
    assert len(found) == 1
    assert found[0]["read_error"].startswith("JSONDecodeError:")


def test_generate_unblock_status_report_auto_discovers_readiness(tmp_path: Path):
    cache = tmp_path / "cache"
    cache.mkdir()
    reports = tmp_path / "reports"
    reports.mkdir()
    spec = reports / "real_feed_ingestion_readiness_20261105T104640Z.json"
    spec.write_text(
        json.dumps(
            {
                "artifact": "real_feed_ingestion_readiness",
                "feeds": [{"family": "funding_basis_carry"}],
            }
        ),
        encoding="utf-8",
    )
    result = generate_unblock_status_report(cache, campaign=19, reports_dir=reports)
    assert result["campaign"] == 19
    assert result["oos_edge_proven"] is False
    assert result["conclusion"] == "PATH_C_MAINTAIN_STILL_BLOCKED"
    assert len(result["readiness_specs"]) == 1
    assert result["readiness_specs"][0]["artifact"] == "real_feed_ingestion_readiness"


def test_unblock_status_cli_writes_report(tmp_path: Path):
    from data.real_feed_loader import main

    cache = tmp_path / "cache"
    cache.mkdir()
    reports = tmp_path / "reports"
    reports.mkdir()
    out = tmp_path / "out.json"
    rc = main(
        [
            "--cache-dir",
            str(cache),
            "--reports-dir",
            str(reports),
            "--campaign",
            "19",
            "--output",
            str(out),
            "--no-auto-discover-readiness",
        ]
    )
    assert rc == 0
    obj = json.loads(out.read_text(encoding="utf-8"))
    assert obj["tool"] == "data.real_feed_loader.generate_unblock_status_report"
    assert obj["campaign"] == 19
    assert obj["path_r_triggered"] is False
    assert obj["oos_edge_proven"] is False
    assert obj["conclusion"] == "PATH_C_MAINTAIN_STILL_BLOCKED"
    assert obj["readiness_specs"] == []


def test_generate_unblock_status_report_readiness_details_opt_in(tmp_path: Path):
    cache = tmp_path / "cache"
    cache.mkdir()
    reports = tmp_path / "reports"
    reports.mkdir()
    spec = reports / "real_feed_ingestion_readiness_x.json"
    spec.write_text(
        json.dumps(
            {
                "artifact": "real_feed_ingestion_readiness",
                "campaign": 9,
                "generated_at_utc": "2026-11-05T10:46:40Z",
                "feeds": [{"family": "funding_basis_carry"}],
            }
        ),
        encoding="utf-8",
    )
    base = generate_unblock_status_report(
        cache, campaign=19, reports_dir=reports, include_readiness_details=False
    )
    assert base["readiness_spec_count"] == 1
    assert base["auto_discover_readiness"] is True
    assert "generated_at_utc" not in base["readiness_specs"][0]
    detailed = generate_unblock_status_report(
        cache, campaign=19, reports_dir=reports, include_readiness_details=True
    )
    assert detailed["readiness_specs"][0]["generated_at_utc"] == "2026-11-05T10:46:40Z"
    assert detailed["readiness_specs"][0]["feeds_count"] == 1
    assert detailed["oos_edge_proven"] is False
    assert detailed["path_r_triggered"] is False


def test_unblock_status_cli_readiness_details_flag(tmp_path: Path):
    from data.real_feed_loader import main

    cache = tmp_path / "cache"
    cache.mkdir()
    reports = tmp_path / "reports"
    reports.mkdir()
    (reports / "real_feed_ingestion_readiness_x.json").write_text(
        json.dumps(
            {
                "artifact": "real_feed_ingestion_readiness",
                "generated_at_utc": "2026-11-05T10:46:40Z",
                "feeds": [{"family": "funding_basis_carry"}, {"family": "intrabar_microstructure"}],
            }
        ),
        encoding="utf-8",
    )
    out = tmp_path / "out.json"
    rc = main(
        [
            "--cache-dir",
            str(cache),
            "--reports-dir",
            str(reports),
            "--campaign",
            "19",
            "--readiness-details",
            "--output",
            str(out),
        ]
    )
    assert rc == 0
    obj = json.loads(out.read_text(encoding="utf-8"))
    assert obj["readiness_spec_count"] == 1
    assert obj["readiness_specs"][0]["feeds_count"] == 2
    assert obj["readiness_specs"][0]["generated_at_utc"] == "2026-11-05T10:46:40Z"
    assert obj["conclusion"] == "PATH_C_MAINTAIN_STILL_BLOCKED"


# --- Campaign #20: compare_unblock_status / campaign_delta (fail-closed infrastructure) ---


def test_compare_unblock_status_no_prior():
    delta = compare_unblock_status(None, {"blocked_families": ["funding_basis_carry"]})
    assert delta["fail_closed"] is True
    assert delta["oos_edge_proven"] is False
    assert delta["prior_available"] is False
    assert delta["reason"] == "no_prior_provided"
    assert delta["changed"] is None


def test_compare_unblock_status_missing_prior_file(tmp_path: Path):
    delta = compare_unblock_status(tmp_path / "nope.json", {"blocked_families": []})
    assert delta["prior_available"] is False
    assert delta["reason"] == "prior_report_missing"
    assert delta["changed"] is None


def test_compare_unblock_status_detects_no_change(tmp_path: Path):
    cache = tmp_path / "cache"
    cache.mkdir()
    current = generate_unblock_status_report(cache, campaign=20)
    prior_path = tmp_path / "prior.json"
    prior_path.write_text(json.dumps(current), encoding="utf-8")
    delta = compare_unblock_status(prior_path, current)
    assert delta["prior_available"] is True
    assert delta["changed"] is False
    assert delta["blocked_families_changed"] is False
    assert delta["path_r_changed"] is False
    assert delta["scan_differences"] == {}
    assert delta["honest_assessment"] == "NO_CHANGE_STILL_BLOCKED_FAIL_CLOSED"
    assert delta["oos_edge_proven"] is False


def test_compare_unblock_status_detects_change():
    prior = {
        "campaign": 19,
        "conclusion": "PATH_C_MAINTAIN_STILL_BLOCKED",
        "audit_conclusion": "NO_VALID_NONSPOT_PROVENANCE_ARTIFACTS",
        "path_r_triggered": False,
        "blocked_families": [
            "funding_basis_carry",
            "cross_exchange_dual_venue_same_asset",
            "term_structure_real_iv_vol_surface",
            "intrabar_microstructure",
        ],
        "scan_summary": {"meta_files_scanned": 21, "candidate_hits": 0},
    }
    current = {
        **prior,
        "campaign": 20,
        "path_r_triggered": True,
        "conclusion": "PATH_R_ELIGIBLE_VALID_NONSPOT_FEED_PRESENT",
        "blocked_families": [
            "cross_exchange_dual_venue_same_asset",
            "term_structure_real_iv_vol_surface",
            "intrabar_microstructure",
        ],
        "scan_summary": {"meta_files_scanned": 22, "candidate_hits": 1},
    }
    delta = compare_unblock_status(prior, current)
    assert delta["changed"] is True
    assert delta["blocked_families_changed"] is True
    assert delta["path_r_changed"] is True
    assert delta["scan_differences"]["candidate_hits"]["prior"] == 0
    assert delta["scan_differences"]["candidate_hits"]["current"] == 1
    assert delta["honest_assessment"] == "UNBLOCK_STATE_CHANGED_REVIEW_REQUIRED"


def test_generate_unblock_status_report_includes_campaign_delta(tmp_path: Path):
    cache = tmp_path / "cache"
    cache.mkdir()
    prior = generate_unblock_status_report(cache, campaign=19)
    prior_path = tmp_path / "prior.json"
    prior_path.write_text(json.dumps(prior), encoding="utf-8")
    current = generate_unblock_status_report(cache, campaign=20, prior_report=prior_path)
    assert current["campaign"] == 20
    assert current["oos_edge_proven"] is False
    assert current["conclusion"] == "PATH_C_MAINTAIN_STILL_BLOCKED"
    assert "campaign_delta" in current
    assert current["campaign_delta"]["prior_available"] is True
    assert current["campaign_delta"]["changed"] is False
    assert current["campaign_delta"]["prior_campaign"] == 19
    assert current["campaign_delta"]["current_campaign"] == 20


def test_unblock_status_cli_prior_flag(tmp_path: Path):
    from data.real_feed_loader import main

    cache = tmp_path / "cache"
    cache.mkdir()
    reports = tmp_path / "reports"
    reports.mkdir()
    prior_out = tmp_path / "prior.json"
    rc = main(
        [
            "--cache-dir",
            str(cache),
            "--reports-dir",
            str(reports),
            "--campaign",
            "19",
            "--output",
            str(prior_out),
            "--no-auto-discover-readiness",
        ]
    )
    assert rc == 0
    out = tmp_path / "out.json"
    rc = main(
        [
            "--cache-dir",
            str(cache),
            "--reports-dir",
            str(reports),
            "--campaign",
            "20",
            "--prior",
            str(prior_out),
            "--output",
            str(out),
            "--no-auto-discover-readiness",
        ]
    )
    assert rc == 0
    obj = json.loads(out.read_text(encoding="utf-8"))
    assert obj["campaign"] == 20
    assert obj["path_r_triggered"] is False
    assert obj["campaign_delta"]["prior_available"] is True
    assert obj["campaign_delta"]["changed"] is False
    assert obj["campaign_delta"]["honest_assessment"] == "NO_CHANGE_STILL_BLOCKED_FAIL_CLOSED"


# --- Campaign 21: fail-closed unblock trend aggregation (real, tested, no edge claim) ---

def test_build_unblock_trend_report_empty(tmp_path: Path):
    trend = build_unblock_trend_report(tmp_path / "reports", campaign=21)
    assert trend["tool"] == "data.real_feed_loader.build_unblock_trend_report"
    assert trend["fail_closed"] is True
    assert trend["real_data_only"] is True
    assert trend["fabricated_data"] is False
    assert trend["oos_edge_proven"] is False
    assert trend["status_files_found"] == 0
    assert trend["status_reports_read"] == 0
    assert trend["latest"] is None
    assert trend["honest_assessment"] == "NO_HISTORICAL_STATUS_REPORTS_FOUND"


def test_build_unblock_trend_report_aggregates_and_detects_no_change(tmp_path: Path):
    reports = tmp_path / "reports"
    reports.mkdir()
    base = {
        "tool": "data.real_feed_loader.generate_unblock_status_report",
        "fail_closed": True,
        "real_data_only": True,
        "fabricated_data": False,
        "oos_edge_proven": False,
        "path_r_triggered": False,
        "conclusion": "PATH_C_MAINTAIN_STILL_BLOCKED",
        "audit_conclusion": "NO_VALID_NONSPOT_PROVENANCE_ARTIFACTS",
        "blocked_families": [
            "funding_basis_carry",
            "cross_exchange_dual_venue_same_asset",
            "term_structure_real_iv_vol_surface",
            "intrabar_microstructure",
        ],
        "scan_summary": {
            "meta_files_scanned": 21,
            "candidate_hits": 0,
            "new_real_feeds_with_provenance_found": False,
        },
        "campaign_delta": {
            "prior_available": True,
            "changed": False,
            "honest_assessment": "NO_CHANGE_STILL_BLOCKED_FAIL_CLOSED",
        },
    }
    for camp, ts in [(19, "20261105T163015Z"), (20, "20261105T163640Z")]:
        obj = {**base, "campaign": camp, "generated_at_utc": ts}
        (reports / f"real_feed_unblock_status_{ts}.json").write_text(
            json.dumps(obj), encoding="utf-8"
        )
    trend = build_unblock_trend_report(reports, campaign=21)
    assert trend["status_files_found"] == 2
    assert trend["status_reports_read"] == 2
    assert trend["campaigns_observed"] == [19, 20]
    assert trend["path_r_ever_triggered"] is False
    assert trend["any_observable_state_change_across_reports"] is False
    assert trend["latest"]["campaign"] == 20
    assert len(trend["transitions"]) == 1
    assert trend["transitions"][0]["blocked_families_changed"] is False
    assert trend["honest_assessment"] == "NO_CHANGE_STILL_BLOCKED_FAIL_CLOSED"
    assert trend["oos_edge_proven"] is False


def test_build_unblock_trend_report_records_unreadable_and_path_r_history(tmp_path: Path):
    reports = tmp_path / "reports"
    reports.mkdir()
    (reports / "real_feed_unblock_status_20261105T000001Z.json").write_text(
        json.dumps(
            {
                "campaign": 19,
                "path_r_triggered": False,
                "conclusion": "PATH_C_MAINTAIN_STILL_BLOCKED",
                "blocked_families": ["funding_basis_carry"],
                "scan_summary": {"candidate_hits": 0},
            }
        ),
        encoding="utf-8",
    )
    (reports / "real_feed_unblock_status_20261105T000002Z.json").write_text(
        json.dumps(
            {
                "campaign": 20,
                "path_r_triggered": True,
                "conclusion": "PATH_R_ELIGIBLE_VALID_NONSPOT_FEED_PRESENT",
                "blocked_families": [],
                "scan_summary": {"candidate_hits": 1, "new_real_feeds_with_provenance_found": True},
            }
        ),
        encoding="utf-8",
    )
    (reports / "real_feed_unblock_status_20261105T000003Z.json").write_text(
        "{broken", encoding="utf-8"
    )
    trend = build_unblock_trend_report(reports, campaign=21)
    assert trend["status_files_found"] == 3
    assert trend["status_reports_read"] == 2
    assert len(trend["unreadable_files"]) == 1
    assert trend["path_r_ever_triggered"] is True
    assert trend["path_r_triggered_campaigns"] == [20]
    assert trend["any_observable_state_change_across_reports"] is True
    assert trend["honest_assessment"] == "PATH_R_OBSERVED_IN_HISTORY_REVIEW_REQUIRED"


def test_build_unblock_trend_report_limit(tmp_path: Path):
    reports = tmp_path / "reports"
    reports.mkdir()
    for camp, ts in [(18, "20261105T135404Z"), (19, "20261105T163015Z"), (20, "20261105T163640Z")]:
        (reports / f"real_feed_unblock_status_{ts}.json").write_text(
            json.dumps(
                {
                    "campaign": camp,
                    "path_r_triggered": False,
                    "blocked_families": ["x"],
                    "conclusion": "PATH_C_MAINTAIN_STILL_BLOCKED",
                }
            ),
            encoding="utf-8",
        )
    trend = build_unblock_trend_report(reports, campaign=21, limit=2)
    assert trend["campaigns_observed"] == [19, 20]
    assert trend["latest"]["campaign"] == 20


def test_unblock_trend_cli_flag(tmp_path: Path):
    from data.real_feed_loader import main

    cache = tmp_path / "cache"
    cache.mkdir()
    reports = tmp_path / "reports"
    reports.mkdir()
    (reports / "real_feed_unblock_status_20261105T163640Z.json").write_text(
        json.dumps(
            {
                "campaign": 20,
                "path_r_triggered": False,
                "conclusion": "PATH_C_MAINTAIN_STILL_BLOCKED",
                "audit_conclusion": "NO_VALID_NONSPOT_PROVENANCE_ARTIFACTS",
                "blocked_families": [
                    "funding_basis_carry",
                    "cross_exchange_dual_venue_same_asset",
                    "term_structure_real_iv_vol_surface",
                    "intrabar_microstructure",
                ],
                "scan_summary": {"meta_files_scanned": 21, "candidate_hits": 0},
            }
        ),
        encoding="utf-8",
    )
    out = tmp_path / "trend.json"
    rc = main(
        [
            "--trend",
            "--reports-dir",
            str(reports),
            "--campaign",
            "21",
            "--output",
            str(out),
        ]
    )
    assert rc == 0
    obj = json.loads(out.read_text(encoding="utf-8"))
    assert obj["tool"] == "data.real_feed_loader.build_unblock_trend_report"
    assert obj["campaign"] == 21
    assert obj["status_reports_read"] == 1
    assert obj["oos_edge_proven"] is False
    assert obj["honest_assessment"] == "NO_CHANGE_STILL_BLOCKED_FAIL_CLOSED"


def test_build_cache_provenance_gap_audit_empty_cache(tmp_path: Path):
    cache = tmp_path / "cache"
    cache.mkdir()
    audit = build_cache_provenance_gap_audit(cache, campaign=22)
    assert audit["tool"] == "data.real_feed_loader.build_cache_provenance_gap_audit"
    assert audit["artifact"] == "cache_provenance_gap_audit"
    assert audit["campaign"] == 22
    assert audit["fail_closed"] is True
    assert audit["real_data_only"] is True
    assert audit["fabricated_data"] is False
    assert audit["oos_edge_proven"] is False
    assert audit["path_r_triggered"] is False
    assert audit["scan_summary"]["meta_files_scanned"] == 0
    assert audit["scan_summary"]["candidate_hits"] == 0
    assert audit["meta_inventory"] == []
    assert audit["honest_assessment"] == "NO_CANDIDATE_NONSPOT_FEEDS_STILL_BLOCKED_FAIL_CLOSED"
    blocked_fams = [
        "funding_basis_carry",
        "cross_exchange_dual_venue_same_asset",
        "term_structure_real_iv_vol_surface",
        "intrabar_microstructure",
    ]
    for fam in blocked_fams:
        assert fam in audit["blocked_families"]
    # real_quote_volume is also tracked as a blocked family in current loader; honest.
    blocked = audit["blocked_families"]
    assert isinstance(blocked, list) and blocked == sorted(blocked)


def test_build_cache_provenance_gap_audit_refused_candidate_records_gap(tmp_path: Path):
    cache = tmp_path / "cache"
    cache.mkdir()
    # A candidate-shaped meta (mentions funding) but missing full provenance/integrity keys:
    # loader must refuse it fail-closed and the audit must record the refusal honestly.
    (cache / "funding_like.meta.json").write_text(
        json.dumps({"type": "funding_snapshot", "symbol": "BTC"}), encoding="utf-8"
    )
    pd.DataFrame({"x": [1]}).to_pickle(cache / "funding_like.pkl")
    audit = build_cache_provenance_gap_audit(cache, campaign=22)
    assert audit["scan_summary"]["candidate_hits"] >= 1
    inv = [m for m in audit["meta_inventory"] if m["meta"] == "funding_like.meta.json"]
    assert len(inv) == 1
    assert inv[0]["candidate_nonspot"] is True
    assert inv[0]["provenance_certificate_discovered"] is False
    # any validation result for this meta must be a refusal, not a pass
    vals = inv[0]["validation_results"]
    assert vals, "expected fail-closed validation results for candidate meta"
    assert all(v.get("refused") for v in vals)
    assert audit["scan_summary"]["refused_candidates"] >= 1
    assert audit["scan_summary"]["valid_candidates"] == 0
    assert audit["path_r_triggered"] is False
    conclusion_ok = (
        "NO_VALID_NONSPOT_PROVENANCE_ARTIFACTS" in audit["conclusion"]
        or audit["blocked_families"]
    )
    assert conclusion_ok
    assert audit["honest_assessment"] in {
        "CANDIDATES_PRESENT_BUT_FAIL_CLOSED_REFUSED_STILL_BLOCKED",
        "NO_CANDIDATE_NONSPOT_FEEDS_STILL_BLOCKED_FAIL_CLOSED",
    }


def test_cache_provenance_audit_cli_flag(tmp_path: Path):
    from data.real_feed_loader import main

    cache = tmp_path / "cache"
    cache.mkdir()
    out = tmp_path / "gap_audit.json"
    rc = main(
        [
            "--cache-provenance-audit",
            "--cache-dir",
            str(cache),
            "--campaign",
            "22",
            "--output",
            str(out),
        ]
    )
    assert rc == 0
    obj = json.loads(out.read_text(encoding="utf-8"))
    assert obj["tool"] == "data.real_feed_loader.build_cache_provenance_gap_audit"
    assert obj["campaign"] == 22
    assert obj["oos_edge_proven"] is False
    assert obj["fail_closed"] is True
