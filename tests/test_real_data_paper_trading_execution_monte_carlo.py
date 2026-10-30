"""Network-independent tests for real-data paper trading, execution realism, Monte Carlo."""

from __future__ import annotations

import json
from pathlib import Path


def test_paper_trading_real_artifact_exists_and_schema():
    p = Path("reports/paper_trading_real.json")
    assert p.exists()
    data = json.loads(p.read_text())
    assert isinstance(data, dict)
    for key in ("session_summary", "fills", "equity_curve", "positions"):
        assert key in data
    ss = data["session_summary"]
    for key in ("initial_capital", "realized_pnl", "num_fills"):
        assert key in ss
    assert "equity_curve_summary" in data or "equity_curve_summary" in ss
    ecs = data.get("equity_curve_summary") or ss.get("equity_curve_summary")
    assert isinstance(ecs, dict)
    for key in ("start_equity", "end_equity", "max_drawdown"):
        assert key in ecs
    assert isinstance(data.get("fills"), list)
    assert "fees" in data
    assert "slippage" in data
    assert "drawdown" in data
    json.dumps(data)


def test_execution_realism_real_artifact_exists_and_schema():
    p = Path("reports/execution_realism_real.json")
    assert p.exists()
    data = json.loads(p.read_text())
    assert isinstance(data, dict)
    assert data.get("data_source") == "binance_public"
    assert isinstance(data.get("models"), dict)
    models = data["models"]
    assert "naive_market" in models
    assert "vwap" in models
    assert "twap" in models
    lob_keys = [k for k in models.keys() if k.startswith("lob")]
    assert len(lob_keys) >= 1
    reqs = [
        "order_type",
        "fills",
        "total_fees",
        "total_slippage_cost",
        "avg_slippage_cost_per_fill",
    ]
    for k, m in models.items():
        for req in reqs:
            assert req in m
    for k, m in models.items():
        assert "vs_naive_slippage_ratio" in m
    json.dumps(data)


def test_monte_carlo_real_artifact_exists_and_schema():
    p = Path("reports/monte_carlo_real.json")
    assert p.exists()
    data = json.loads(p.read_text())
    assert isinstance(data, dict)
    assert data.get("data_source") == "binance_public"
    mc = data.get("monte_carlo")
    assert isinstance(mc, dict)
    for pair in ["BTC/ETH", "ETH/SOL", "BTC/SOL"]:
        assert pair in mc
        entry = mc[pair]
        assert "bootstrap" in entry
        assert "shuffle" in entry
        assert "confidence_intervals" in entry
        ci = entry["confidence_intervals"]
        for metric in ("total_return", "sharpe_ratio", "max_drawdown"):
            assert metric in ci
            for q in ("p5", "p50", "p95"):
                assert q in ci[metric]
    assert "portfolio" in mc
    port_ci = mc["portfolio"]["confidence_intervals"]
    assert "total_return" in port_ci
    assert "sharpe_ratio" in port_ci
    assert "max_drawdown" in port_ci
    json.dumps(data)
