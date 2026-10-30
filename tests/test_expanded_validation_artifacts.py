import json
from pathlib import Path


def test_pairs_real_market_expanded_exists():
    p = Path("reports/pairs_real_market_expanded.json")
    assert p.exists()
    data = json.loads(p.read_text())
    assert "pairs" in data
    assert isinstance(data["pairs"], dict)
    assert len(data["pairs"]) >= 1


def test_regime_robustness_real_exists():
    p = Path("reports/regime_robustness_real.json")
    assert p.exists()
    data = json.loads(p.read_text())
    assert "pairs" in data or "mean_reversion" in data
    assert isinstance(data.get("pairs", {}), dict)
