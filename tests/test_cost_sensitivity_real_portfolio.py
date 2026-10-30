import json
from pathlib import Path


def test_cost_sensitivity_real_portfolio_exists():
    p = Path("reports/cost_sensitivity_real_portfolio.json")
    assert p.exists()
    data = json.loads(p.read_text())
    assert data.get("type") == "pairs_portfolio_cost_sensitivity" or "pairs" in data
    assert isinstance(data.get("pairs"), list)
    assert isinstance(data.get("grid"), list)
    assert isinstance(data.get("rows"), list)
    assert len(data["rows"]) >= 1
    row = data["rows"][0]
    for k in ("fee_rate", "slippage", "total_return", "sharpe_ratio", "max_drawdown"):
        assert k in row
    # Ensure JSON-serializable
    assert isinstance(data["rows"][0]["total_return"], float)
