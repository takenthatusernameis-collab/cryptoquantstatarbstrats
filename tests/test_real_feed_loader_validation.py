"""Tests for fail-closed real feed loader/validator (Path C-maintain).

Uses synthetic test fixtures ONLY inside tests, explicitly flagged as test
fixtures; they are never labeled as real ingested data in production artifacts.
Proves the loader refuses missing/fabricated/proxy/invalid inputs.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd
import pytest

from data.real_feed_loader import (
    FUNDING_BASIS_CARRY_SPEC,
    RealFeedValidationError,
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
