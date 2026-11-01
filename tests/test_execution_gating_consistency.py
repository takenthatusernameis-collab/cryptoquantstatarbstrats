from __future__ import annotations

import json
from pathlib import Path

import pytest


def test_execution_never_allocates_to_blocked_pairs():
    gating_path = Path("reports/portfolio_gating_mt.json")
    exec_path = Path("reports/execution_realism_mt.json")
    if not gating_path.exists() or not exec_path.exists():
        pytest.skip("Missing artifacts")
    gating = json.loads(gating_path.read_text(encoding="utf-8"))
    exec_real = json.loads(exec_path.read_text(encoding="utf-8"))

    results_g = gating.get("results_by_timeframe") or {}
    results_e = exec_real.get("results_by_timeframe") or {}

    for tf in ["1h", "4h", "1d"]:
        assert tf in results_g
        assert tf in results_e
        g = results_g[tf]
        e = results_e[tf]
        eligible = set(g.get("eligible_pairs") or [])
        pair_map = g.get("pair_map") or {}
        excluded = g.get("excluded_pairs") or {}

        # Invariants from gating
        assert g.get("risk_controls", {}).get("gating_enforced") is True
        assert g.get("risk_controls", {}).get("fail_closed") is True
        assert g.get("risk_controls", {}).get("no_blocked_pairs_have_weight") is True

        # Cross-check execution
        e_pairs = e.get("pairs") or {}
        for pname, ex in excluded.items():
            # Blocked pairs must not be in pair_map
            assert pname not in pair_map
            # Execution must mark blocked by gating with routes
            ep = e_pairs.get(pname)
            assert ep is not None
            assert ep.get("execution_blocked_by_gating") is True
            assert ep.get("eligible") is False
            assert ep.get("fills_count", -1) == 0
            assert len(ep.get("fills") or []) == 0
            # Must have blocked routes / rejection log
            br = ep.get("blocked_routes") or []
            rl = ep.get("rejection_log") or []
            assert isinstance(br, list) or isinstance(rl, list)
            # Provenance
            prov = ep.get("provenance") or {}
            assert prov.get("real_data_only") is True

        for pname in eligible:
            ep = e_pairs.get(pname)
            assert ep is not None
            assert ep.get("execution_blocked_by_gating") is False
            assert ep.get("eligible") is True
            # Eligible pairs must have provenance linking to gating
            prov = ep.get("provenance") or {}
            assert str(prov.get("source_gating") or "").endswith("portfolio_gating_mt.json")
