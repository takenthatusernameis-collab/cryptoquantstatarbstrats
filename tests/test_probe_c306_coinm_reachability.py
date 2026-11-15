"""Offline tests for the C306 COIN-M (inverse futures) reachability probe.

The probe is the capability evidence that `data.binance.vision/data/futures/cm/`
(COIN-M inverse perpetual + dated quarterly futures) is reachable, which reopens
the program after the scope-limited C305 USDT-M/spot-only exhaustion probe.
These tests exercise URL/family constants, status classification, family
classification, and summary derivation with NO network access.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import probe_c306_coinm_reachability as probe  # noqa: E402


def _row(bucket, family, asset, reachable, month="2026-10"):
    return {
        "bucket": bucket,
        "family": family,
        "asset": asset,
        "month": month,
        "reachable": reachable,
        "status": 200 if reachable else 404,
        "attempts": 1 if reachable else 5,
    }


def test_constants_target_coin_m_only() -> None:
    # COIN-M uses BASEUSD_PERP naming, never BASEUSDT.
    assert all(s.endswith("_PERP") for s in probe.CM_PERPS)
    assert "BTCUSDT" not in probe.CM_PERPS
    assert all(t.startswith("/data/futures/cm/") for _, t in probe.CM_PERP_FAMILIES)
    # EOSUSD_PERP is 404 upstream; it must not be in the breadth universe.
    assert "EOSUSD_PERP" not in probe.CM_PERPS


def test_classify_reachable_and_unavailable() -> None:
    rows = [
        _row("coin_m_perp_monthly", "klines_1h", "BTCUSD_PERP", True),
        _row("coin_m_perp_monthly", "klines_1h", "BTCUSD_PERP", True),
        _row("coin_m_perp_monthly", "indexPriceKlines_1h", "BTCUSD_PERP", False),
        _row("coin_m_perp_monthly", "indexPriceKlines_1h", "BTCUSD_PERP", False),
    ]
    fam = probe.classify(rows)
    assert fam["coin_m_perp_monthly|klines_1h|BTCUSD_PERP"]["classification"] == "REACHABLE"
    assert (
        fam["coin_m_perp_monthly|indexPriceKlines_1h|BTCUSD_PERP"]["classification"]
        == "UNAVAILABLE"
    )


def test_summary_flags_new_family_when_perp_and_quarterly_reachable() -> None:
    rows = [
        _row("coin_m_perp_monthly", "klines_1h", "BTCUSD_PERP", True, "2026-10"),
        _row("coin_m_perp_monthly", "premiumIndexKlines_1h", "BTCUSD_PERP", True, "2026-10"),
        _row("coin_m_perp_monthly", "markPriceKlines_1h", "BTCUSD_PERP", True, "2026-10"),
        _row("coin_m_perp_monthly", "fundingRate", "BTCUSD_PERP", True, "2026-10"),
        _row("coin_m_perp_universe", "klines_1h", "BTCUSD_PERP", True),
        _row("coin_m_perp_universe", "klines_1h", "ETHUSD_PERP", True),
        _row("coin_m_quarterly_monthly", "klines_1h", "BTCUSD_250627", True, "2025-06"),
        _row("coin_m_quarterly_monthly", "klines_1h", "BTCUSD_261225", True, "2026-10"),
    ]
    s = probe.summarize(rows)
    assert s["perp_klines_reachable"] is True
    assert s["quarterly_term_structure_reachable"] is True
    assert s["path_a_available"] is True
    assert "coin_m_inverse_quarterly_futures_term_structure_carry" in (
        s["genuinely_new_reachable_families"]
    )


def test_summary_path_a_false_when_no_quarterly_reachable() -> None:
    rows = [_row("coin_m_perp_monthly", "klines_1h", "BTCUSD_PERP", True, "2026-10")]
    s = probe.summarize(rows)
    assert s["quarterly_term_structure_reachable"] is False
    assert s["path_a_available"] is False
    assert s["genuinely_new_reachable_families"] == []


def test_unreachable_perp_does_not_flag_family() -> None:
    rows = [
        _row("coin_m_perp_monthly", "klines_1h", "BTCUSD_PERP", False, "2026-10"),
        _row("coin_m_quarterly_monthly", "klines_1h", "BTCUSD_261225", True, "2026-10"),
    ]
    s = probe.summarize(rows)
    assert s["perp_klines_reachable"] is False
    assert s["path_a_available"] is False