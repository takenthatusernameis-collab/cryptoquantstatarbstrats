"""Campaign #2 tests: funding carry + LOB/intrabar feasibility helpers/artifacts.

Network calls are mocked; test fixtures are not labeled as real market data.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from data import real_feed_loader


class _Resp:
    def __init__(self, payload, status=200):
        self._body = json.dumps(payload).encode("utf-8")
        self.status = status

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_compute_funding_carry_metrics_empty():
    out = real_feed_loader.compute_funding_carry_metrics(pd.DataFrame(), intervals_per_day=3)
    assert out["status"] == "no_data"


def test_compute_funding_carry_metrics_basic():
    df = pd.DataFrame(
        {
            "timestamp_utc": pd.to_datetime(["2026-01-01T00:00Z", "2026-01-01T08:00Z"], utc=True),
            "symbol": ["BTCUSDT", "BTCUSDT"],
            "funding_rate": [0.0001, -0.0001],
            "mark_price_or_close": [50000.0, 50100.0],
        }
    )
    out = real_feed_loader.compute_funding_carry_metrics(df, intervals_per_day=3)
    s = out["per_symbol"]["BTCUSDT"]
    assert s["rows"] == 2
    assert abs(s["mean_funding_rate"]) < 1e-12
    assert s["annualized_carry_simple"] == 0.0
    assert out["cross_symbol"]["n_symbols"] == 1


def test_fetch_binance_funding_rates_records_blocked_route(monkeypatch):
    def fake_urlopen(req, timeout=20.0):
        from urllib.error import HTTPError

        raise HTTPError(req.full_url, 451, "restricted", hdrs=None, fp=None)

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    df, att = real_feed_loader.fetch_binance_funding_rates(
        ["BTCUSDT"], "2026-10-01", "2026-10-02", hosts=["https://fapi.binance.com"]
    )
    assert df.empty
    assert att["row_count"] == 0
    assert att["blocked_routes"]


def test_fetch_binance_funding_rates_parses_rows(monkeypatch):
    payload = [
        {
            "symbol": "BTCUSDT",
            "fundingTime": 1759276800000,
            "fundingRate": "0.00010000",
            "markPrice": "60000",
        },
        {
            "symbol": "BTCUSDT",
            "fundingTime": 1759305600000,
            "fundingRate": "-0.00005000",
            "markPrice": "60100",
        },
    ]

    def fake_urlopen(req, timeout=20.0):
        return _Resp(payload)

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    df, att = real_feed_loader.fetch_binance_funding_rates(
        ["BTCUSDT"], "2025-10-01", "2025-10-02", hosts=["https://www.binance.com"]
    )
    assert len(df) == 2
    cols = {"timestamp_utc", "symbol", "funding_rate", "mark_price_or_close"}
    assert set(df.columns) >= cols
    assert att["row_count"] == 2
    assert not att["blocked_routes"]


def test_summarize_microstructure_snapshot_ok():
    snap = {
        "symbol": "BTCUSDT",
        "depth": {"bids": [["100.0", "1"]], "asks": [["101.0", "2"]]},
        "agg_trades": [{"p": "100.5", "q": "0.1"}],
    }
    out = real_feed_loader.summarize_microstructure_snapshot(snap)
    assert out["status"] == "ok"
    assert out["spread_abs"] == 1.0
    assert out["agg_trades_n"] == 1


def test_fetch_spot_microstructure_snapshot_mock(monkeypatch):
    def fake_urlopen(req, timeout=20.0):
        url = req.full_url
        if "/depth" in url:
            return _Resp({"bids": [["100", "1"]], "asks": [["101", "1"]]})
        return _Resp([{"p": "100.5", "q": "0.1", "T": 1}])

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    snap, att = real_feed_loader.fetch_spot_microstructure_snapshot(
        "BTCUSDT", hosts=["https://www.binance.com"]
    )
    assert att["depth_fetched"] is True
    assert att["aggTrades_fetched"] is True
    assert snap["depth"]["bids"]
    assert snap["agg_trades"]


def test_campaign2_artifacts_have_required_schema():
    required = [
        "real_data_only",
        "fabricated_data",
        "generated_at_utc",
        "campaign",
        "status",
        "blocked_routes",
        "notes",
    ]
    funding_keys = [
        "data_sources",
        "symbols",
        "time_window",
        "freq",
        "row_counts",
        "checksums",
        "metrics",
        "limitations",
    ]
    lob_keys = [
        "data_sources",
        "symbols",
        "time_window",
        "freq",
        "row_counts",
        "checksums",
        "feasibility",
        "limitations",
    ]
    for path, family in [
        (Path("reports/funding_carry_real.json"), "funding"),
        (Path("reports/execution_lob_real.json"), "lob"),
    ]:
        assert path.exists(), f"missing required artifact {path}"
        obj = json.loads(path.read_text(encoding="utf-8"))
        for key in required:
            assert key in obj, f"{path} missing {key}"
        assert obj["real_data_only"] is True
        assert obj["fabricated_data"] is False
        assert obj["status"] in {"ok", "partial", "blocked"}
        assert isinstance(obj["blocked_routes"], list)
        for key in funding_keys if family == "funding" else lob_keys:
            assert key in obj
