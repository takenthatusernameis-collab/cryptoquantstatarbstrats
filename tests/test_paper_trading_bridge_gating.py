from __future__ import annotations

import json
from pathlib import Path

import pytest


def test_paper_trading_bridge_preserves_gating():
    bridge_path = Path("reports/paper_trading_bridge_mt.json")
    gating_path = Path("reports/portfolio_gating_mt.json")
    if not bridge_path.exists() or not gating_path.exists():
        pytest.skip("Missing artifacts")
    bridge = json.loads(bridge_path.read_text(encoding="utf-8"))
    gating = json.loads(gating_path.read_text(encoding="utf-8"))

    assert bridge.get("real_data_only") is True
    assert bridge.get("fabricated_data") is False
    assert bridge.get("type") == "paper_trading_bridge_mt"

    g_res = gating.get("results_by_timeframe") or {}
    b_res = bridge.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        g_r = g_res[tf]
        b_r = b_res[tf]
        eligible_g = set(g_r.get("eligible_pairs") or [])
        eligible_b = set(b_r.get("eligible_pairs") or [])
        # Only gated-eligible pairs allowed
        assert eligible_b == eligible_g
        for pname, binfo in (b_r.get("pairs") or {}).items():
            if pname in eligible_g:
                assert binfo.get("bridge_allowed") is True
                assert binfo.get("fills_allowed") is True
                assert binfo.get("eligible") is True
            else:
                assert binfo.get("bridge_allowed") is False
                assert binfo.get("fills_allowed") is False
                assert binfo.get("eligible") is False
                assert float(binfo.get("allocation_usdt", -1.0)) == 0.0
                rl = binfo.get("rejection_log") or []
                assert isinstance(rl, list) and len(rl) >= 1
                br = binfo.get("blocked_routes") or []
                assert isinstance(br, list) and len(br) >= 1
            prov = binfo.get("provenance") or {}
            assert prov.get("real_data_only") is True
            gc = binfo.get("gating_context") or {}
            assert gc.get("source_gating") == "reports/portfolio_gating_mt.json"
