import json
from pathlib import Path


def test_cost_sensitivity_real_exists():
    p = Path("reports/cost_sensitivity_real.json")
    assert p.exists()
    data = json.loads(p.read_text())
    assert "cost_sensitivity" in data
    assert isinstance(data["cost_sensitivity"], dict)
    block = data["cost_sensitivity"]
    assert block.get("pair") == ["ETH", "SOL"] or block.get("pair") == ("ETH", "SOL")
    assert isinstance(block.get("grid"), list)
    assert isinstance(block.get("rows"), list)
    assert len(block["rows"]) >= 1
    # Ensure JSON-serializable structure
    assert isinstance(block["rows"][0].get("replay"), dict)
    assert "total_return" in block["rows"][0]["replay"]
