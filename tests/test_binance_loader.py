"""Tests for the free historical market-data adapter."""

from __future__ import annotations

import io
import json

import pandas as pd
import pytest

from data.loader import DataLoader


def test_binance_loader_parses_public_candles(monkeypatch):
    # Binance kline format: open time, open, high, low, close, volume, ...
    rows = [
        [0, "100", "101", "99", "100.5", "10", 3_599_999, "1000"],
        [3_600_000, "100.5", "102", "100", "101.5", "12", 7_199_999, "1200"],
    ]
    seen_urls = []

    def fake_urlopen(url, timeout=20.0):
        seen_urls.append(url)
        return io.BytesIO(json.dumps(rows).encode("utf-8"))

    monkeypatch.setattr("data.loader.urlopen", fake_urlopen)
    result = DataLoader().load_binance_data(
        ["BTC"],
        "1970-01-01T00:00:00Z",
        "1970-01-01T01:00:00Z",
        interval="1h",
    )

    assert list(result.columns) == ["BTC"]
    assert result["BTC"].tolist() == [100.5, 101.5]
    assert isinstance(result.index, pd.DatetimeIndex)
    assert str(result.index.tz) == "UTC"
    assert "symbol=BTCUSDT" in seen_urls[0]


def test_binance_loader_rejects_reversed_dates():
    with pytest.raises(ValueError, match="end_date must not precede"):
        DataLoader().load_binance_data(["BTC"], "2024-02-01", "2024-01-01")


def test_binance_loader_rejects_unsupported_interval():
    with pytest.raises(ValueError, match="Unsupported Binance interval"):
        DataLoader().load_binance_data(
            ["BTC"], "2024-01-01", "2024-01-02", interval="10h"
        )
