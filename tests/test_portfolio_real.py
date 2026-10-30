import json
from pathlib import Path


def test_portfolio_real_artifact_exists_and_schema():
    p = Path("reports/portfolio_real.json")
    assert p.exists()
    data = json.loads(p.read_text())
    assert data.get("type") == "multi_asset_portfolio_real"
    assert data.get("real_data_only") is True
    assert data.get("fabricated_data") is False
    assert isinstance(data.get("symbols"), list)
    assert isinstance(data.get("pairs"), list)
    assert "portfolio" in data
    port = data["portfolio"]
    for k in ("total_return", "sharpe_ratio", "max_drawdown", "equity_curve"):
        assert k in port
    assert isinstance(port["equity_curve"], list)
    assert "risk_metrics" in data
    rm = data["risk_metrics"]
    required_rm = (
        "var_95",
        "cvar_95",
        "max_gross_exposure_limit",
        "per_pair_cap",
        "drawdown_circuit_breaker",
    )
    for k in required_rm:
        assert k in rm
    assert "walk_forward_portfolio" in data
    wf = data["walk_forward_portfolio"]
    assert wf.get("n_splits", 0) >= 6
    assert isinstance(wf.get("splits"), list)
    assert len(wf["splits"]) >= 6
    agg = wf.get("aggregate", {})
    assert "is_mean_return" in agg or "oos_mean_return" in agg
    assert "regime_adaptive_meta_selector" in data
    assert data["regime_adaptive_meta_selector"].get("implemented") is True
    assert data["regime_adaptive_meta_selector"].get("validated_oos") is True
    assert "funding_basis" in data
    assert isinstance(port["total_return"], float)
