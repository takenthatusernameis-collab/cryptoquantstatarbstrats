"""Network-independent tests for extended real-data validation artifacts."""

from __future__ import annotations

import json
from pathlib import Path


def test_pairs_real_market_oos_artifact_exists_and_schema():
    p = Path("reports/pairs_real_market_oos.json")
    assert p.exists()
    data = json.loads(p.read_text())
    assert isinstance(data, dict)
    assert data.get("oos_extended") is True
    for key in ("symbols", "start", "end", "freq", "pairs", "walk_forward"):
        assert key in data
    assert isinstance(data.get("pairs"), dict)
    for pair in ["BTC/ETH", "ETH/SOL", "BTC/SOL"]:
        assert pair in data["pairs"]
        entry = data["pairs"][pair]
        assert "top_ranked" in entry
        assert "replay" in entry
        assert "benchmark_total_return" in entry
    json.dumps(data)


def test_mean_reversion_real_oos_artifact_exists_and_schema():
    p = Path("reports/mean_reversion_real_oos.json")
    assert p.exists()
    data = json.loads(p.read_text())
    assert isinstance(data, dict)
    assert data.get("oos_extended") is True
    for key in ("assets", "start", "end", "freq", "assets_results", "walk_forward"):
        assert key in data
    res = data["assets_results"]
    for asset in ["BTC", "ETH", "SOL"]:
        assert asset in res
        entry = res[asset]
        assert "top_ranked" in entry
        assert "replay" in entry
        assert "benchmark_total_return" in entry
    json.dumps(data)


def test_pairs_real_market_wider_universe_artifact_exists_and_schema():
    p = Path("reports/pairs_real_market_wider_universe.json")
    assert p.exists()
    data = json.loads(p.read_text())
    assert isinstance(data, dict)
    assert data.get("wider_universe") is True
    pairs = data.get("pairs", {})
    assert isinstance(pairs, dict)
    assert len(pairs) >= 4
    for name, entry in pairs.items():
        assert isinstance(entry, dict)
    json.dumps(data)


def test_pairs_real_market_longer_walkforward_artifact_exists_and_schema():
    p = Path("reports/pairs_real_market_longer_walkforward.json")
    assert p.exists()
    data = json.loads(p.read_text())
    assert isinstance(data, dict)
    assert data.get("longer_horizon") is True
    wf = data.get("walk_forward", {})
    assert wf.get("n_splits", 0) >= 6 or wf.get("train_period", 0) >= 1000
    pairs = data.get("pairs", {})
    assert isinstance(pairs, dict)
    for pair in ["BTC/ETH", "ETH/SOL", "BTC/SOL"]:
        if pair in pairs and "error" not in pairs[pair]:
            assert "top_ranked" in pairs[pair]
    json.dumps(data)


def test_execution_realism_extended_artifact_exists_and_schema():
    p = Path("reports/execution_realism_extended.json")
    assert p.exists()
    data = json.loads(p.read_text())
    assert isinstance(data, dict)
    assert data.get("data_source") == "binance_public"
    assert data.get("oos_extended") is True
    assert data.get("wider_universe") is True
    models = data.get("models", {})
    for k in ("naive_market", "vwap", "twap"):
        assert k in models
    lob_keys = [k for k in models.keys() if k.startswith("lob")]
    assert len(lob_keys) >= 1
    for k, m in models.items():
        for req in [
            "order_type",
            "fills",
            "total_fees",
            "total_slippage_cost",
            "avg_slippage_cost_per_fill",
            "vs_naive_slippage_ratio",
        ]:
            assert req in m
    json.dumps(data)


def test_regime_cost_stress_extended_artifact_exists_and_schema():
    p = Path("reports/regime_cost_stress_extended.json")
    assert p.exists()
    data = json.loads(p.read_text())
    assert isinstance(data, dict)
    assert data.get("data_source") == "binance_public"
    assert "cost_stress" in data
    assert "regime_slices" in data
    assert isinstance(data["cost_stress"], dict)
    assert isinstance(data["regime_slices"], dict)
    json.dumps(data)
