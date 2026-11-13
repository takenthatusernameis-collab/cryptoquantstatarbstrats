"""Tests for the C291 derivatives-reachability probe.

The probe is the capability evidence that the USDT-M futures public archive is
reachable (data.binance.vision) even though fapi.binance.com is HTTP 451 from
this egress. These tests exercise URL construction, status classification,
per-symbol probing, and report persistence/SHA256 without any network access.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import probe_c291_derivatives_archives as probe  # noqa: E402


def _fake_opener(present: set[str], blocked: set[str] | None = None):
    blocked = blocked or set()

    def opener(url: str, method: str, timeout: float):
        if url in present:
            return 200, {"Content-Length": "123"}, b""
        if url in blocked:
            return 451, {}, b'{"code":0,"msg":"restricted"}'
        return 404, {}, b""

    return opener


def test_url_builders_are_exact() -> None:
    assert probe.kline_url("BTCUSDT", "2026-09") == (
        "https://data.binance.vision/data/futures/um/monthly/klines/BTCUSDT/5m/BTCUSDT-5m-2026-09.zip"
    )
    assert probe.funding_url("BTCUSDT", "2026-09") == (
        "https://data.binance.vision/data/futures/um/monthly/fundingRate/BTCUSDT/"
        "BTCUSDT-fundingRate-2026-09.zip"
    )


def test_classify_status() -> None:
    assert probe.classify(200, 10)["ok"] is True
    assert probe.classify(404, None)["reason"] == "not_found"
    assert probe.classify(451, None)["reason"] == "blocked"
    assert probe.classify(500, None)["reason"] == "http_500"


def test_probe_symbol_all_present() -> None:
    months = ("2026-08", "2026-09")
    present = {probe.kline_url("BTCUSDT", m) for m in months} | {
        probe.funding_url("BTCUSDT", m) for m in months
    }
    out = probe.probe_symbol("BTCUSDT", months, opener=_fake_opener(present))
    assert out["fully_reachable"] is True
    assert set(out["months"]) == set(months)


def test_probe_symbol_missing_funding_blocks() -> None:
    months = ("2026-09",)
    present = {probe.kline_url("BTCUSDT", "2026-09")}
    out = probe.probe_symbol("BTCUSDT", months, opener=_fake_opener(present))
    assert out["fully_reachable"] is False
    assert out["months"]["2026-09"]["klines"]["ok"] is True
    assert out["months"]["2026-09"]["funding"]["ok"] is False


def test_probe_symbol_blocked_route_is_not_permissive() -> None:
    months = ("2026-09",)
    urls = [probe.kline_url("BTCUSDT", "2026-09"), probe.funding_url("BTCUSDT", "2026-09")]
    out = probe.probe_symbol("BTCUSDT", months, opener=_fake_opener(set(), set(urls)))
    assert out["fully_reachable"] is False
    assert out["months"]["2026-09"]["funding"]["reason"] == "blocked"


def test_main_writes_report_with_sha_and_ready(tmp_path) -> None:
    months = probe.MONTHS
    syms = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    present = set()
    for sym in syms:
        for m in months:
            present.add(probe.kline_url(sym, m))
            present.add(probe.funding_url(sym, m))
    code = probe.main(
        ["--json", "--reports-dir", str(tmp_path), "--workers", "4"],
        opener=_fake_opener(present, {probe.BLOCKED_ROUTES[0][1]}),
        symbols=syms,
    )
    assert code == 2  # 3 reachable symbols < floor of 10: fail-closed
    files = list(tmp_path.glob("campaign291_derivatives_reachability_*.json"))
    assert len(files) == 1
    raw = files[0].read_bytes()
    report = json.loads(raw)
    assert report["campaign"] == 291
    assert report["real_data_only"] is True
    assert report["fabricated_data"] is False
    assert report["ready"] is False
    assert report["summary"]["n_fully_reachable"] == 3
    assert report["summary"]["any_funding_reachable"] is True
    assert "artifact_sha256" not in report  # self-hash is printed, not embedded


def test_main_ready_when_floor_met(tmp_path) -> None:
    months = probe.MONTHS
    symbols = [f"S{i}USDT" for i in range(probe.MIN_READY_SYMBOLS)]
    present = set()
    for sym in symbols:
        for m in months:
            present.add(probe.kline_url(sym, m))
            present.add(probe.funding_url(sym, m))
    code = probe.main(
        ["--json", "--reports-dir", str(tmp_path)],
        opener=_fake_opener(present),
        symbols=symbols,
    )
    assert code == 0
    report = json.loads(next(tmp_path.glob("campaign291_derivatives_reachability_*.json")).read_text())
    assert report["ready"] is True
    assert report["summary"]["n_fully_reachable"] == probe.MIN_READY_SYMBOLS
    assert all(not r["ok"] for r in report["blocked_routes"])


def test_write_report_returns_sha256_from_bytes(tmp_path) -> None:
    report = probe.build_report(
        ["BTCUSDT"], ("2026-09",), opener=_fake_opener(set(), set())
    )
    path, sha = probe.write_report(report, tmp_path)
    assert path.exists()
    assert hashlib.sha256(path.read_bytes()).hexdigest() == sha