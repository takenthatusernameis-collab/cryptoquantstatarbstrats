import json
from pathlib import Path


def test_regime_robustness_real_has_cost_stress():
    p = Path("reports/regime_robustness_real.json")
    assert p.exists()
    data = json.loads(p.read_text())
    assert "cost_stress" in data
    cs = data["cost_stress"]
    assert isinstance(cs.get("grid"), list)
    assert isinstance(cs.get("pairs"), dict)
    assert isinstance(cs.get("mean_reversion"), dict)
    # Check that at least one entry has cost_stress_slices
    found = False
    for v in cs.get("pairs", {}).values():
        if isinstance(v, dict) and isinstance(v.get("cost_stress_slices"), list):
            found = True
            break
    if not found:
        for v in cs.get("mean_reversion", {}).values():
            if isinstance(v, dict) and isinstance(v.get("cost_stress_slices"), list):
                found = True
                break
    assert found
