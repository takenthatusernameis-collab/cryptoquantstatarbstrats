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
    assert wf.get("n_splits", 0) >= 10
    assert isinstance(wf.get("splits"), list)
    assert len(wf["splits"]) >= 10
    agg = wf.get("aggregate", {})
    assert "is_mean_return" in agg or "oos_mean_return" in agg
    assert "regime_adaptive_meta_selector" in data
    assert data["regime_adaptive_meta_selector"].get("implemented") is True
    assert data["regime_adaptive_meta_selector"].get("validated_oos") is True
    assert "funding_basis" in data
    assert isinstance(port["total_return"], float)
    # Hardened risk controls must be present and enforced (not dead config).
    rm = data["risk_metrics"]
    assert "max_correlation_exposure_limit" in rm
    assert "max_cvar_allocation_limit" in rm
    assert rm["max_correlation_exposure_limit"] > 0
    assert rm["max_cvar_allocation_limit"] > 0
    assert "max_asset_gross_exposure" in rm
    # Per-asset gross exposure must respect the correlation-exposure cap.
    assert rm["max_asset_gross_exposure"] <= rm["max_correlation_exposure_limit"] + 1e-9
    # Portfolio construction must declare the hardened meta-selector + risk controller.
    pc = data.get("portfolio_construction", {})
    assert pc.get("risk_controller") == "correlation_aware_cvar_style"
    assert pc.get("circuit_breaker_tested") is True
