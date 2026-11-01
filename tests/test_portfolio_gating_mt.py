from __future__ import annotations

import json
from pathlib import Path

import pytest


def test_portfolio_gating_mt_schema_and_gating():
    path = Path("reports/portfolio_gating_mt.json")
    if not path.exists():
        pytest.skip(f"Missing {path}")
    data = json.loads(path.read_text(encoding="utf-8"))

    assert data.get("real_data_only") is True
    assert data.get("fabricated_data") is False
    assert data.get("type") == "portfolio_gating_mt"
    assert "results_by_timeframe" in data
    results = data["results_by_timeframe"]
    for tf in ["1h", "4h", "1d"]:
        assert tf in results
        r = results[tf]
        assert r.get("n_eligible", 0) >= 0
        assert isinstance(r.get("eligible_pairs"), list)
        assert isinstance(r.get("excluded_pairs"), dict)
        # Fail-closed: blocked pairs never in pair_map if present
        pair_map = r.get("pair_map") or {}
        excluded = r.get("excluded_pairs") or {}
        for ep in excluded:
            # if pair_map contains excluded pair name, it must not have weight - but structure shows pair_map built from eligible
            assert ep not in pair_map
        # Gating enforced
        rc = r.get("risk_controls") or {}
        assert rc.get("gating_enforced") is True
        assert rc.get("fail_closed") is True
        assert rc.get("no_blocked_pairs_have_weight") is True
        # Provenance on excluded entries
        for pname, ex in excluded.items():
            br = ex.get("blocked_routes") or []
            assert isinstance(br, list) and len(br) >= 1
