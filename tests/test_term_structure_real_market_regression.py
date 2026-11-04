"""Network-independent regression tests for term_structure real-market validation.

Asserts the reports/term_structure_real_market.json artifact schema, real-data
provenance (real_data_only: true, fabricated_data: false), honest blocked-routes,
and that replay metrics are present and finite. No synthetic data as evidence.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

ARTIFACT = Path("reports/term_structure_real_market.json")

REPLAY_KEYS = ("total_return", "sharpe_ratio", "max_drawdown", "calmar_ratio", "final_equity")


def _is_finite(value) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def test_term_structure_real_market_artifact_schema() -> None:
    assert ARTIFACT.exists(), f"{ARTIFACT} must be produced from real Binance spot data"
    data = json.loads(ARTIFACT.read_text())
    assert data.get("assets") == ["BTC"]
    assert data.get("freq") == "1h"
    assert isinstance(data.get("n_bars"), int) and data["n_bars"] > 0
    assert isinstance(data.get("grid"), dict) and data["grid"]
    assert isinstance(data.get("walk_forward"), dict)
    assert isinstance(data.get("costs"), dict)
    assert "cost_sensitivity_grid" in data
    assert "assets_results" in data and isinstance(data["assets_results"], dict)
    assert "provenance" in data
    json.dumps(data)  # JSON-serializable


def test_term_structure_real_market_provenance() -> None:
    data = json.loads(ARTIFACT.read_text())
    prov = data["provenance"]
    assert prov.get("real_data_only") is True
    assert prov.get("fabricated_data") is False
    assert isinstance(prov.get("blocked_routes"), list)
    assert prov.get("computed_at")
    assert prov.get("rationale")


def test_term_structure_real_market_replay_metrics_finite() -> None:
    data = json.loads(ARTIFACT.read_text())
    results = data["assets_results"]
    for asset in data["assets"]:
        res = results[asset]
        assert "replay" in res and isinstance(res["replay"], dict)
        for key in REPLAY_KEYS:
            assert key in res["replay"], f"{asset} replay missing {key}"
            assert _is_finite(res["replay"][key]), f"{asset} replay {key} not finite"
        assert "benchmark_total_return" in res
        assert _is_finite(res["benchmark_total_return"])
        assert "cost_sensitivity" in res and isinstance(res["cost_sensitivity"], list)
        assert res["cost_sensitivity"], f"{asset} cost_sensitivity grid must be non-empty"
        for point in res["cost_sensitivity"]:
            assert "fee_rate" in point and "slippage" in point
            for key in REPLAY_KEYS:
                assert key in point and _is_finite(point[key])
