from __future__ import annotations

import json
from pathlib import Path

import pytest


def test_kill_switch_preserves_gating_and_schema():
    ks_path = Path("reports/kill_switch_rules_mt.json")
    recon_path = Path("reports/post_trade_reconciliation_mt.json")
    gating_path = Path("reports/portfolio_gating_mt.json")
    if not ks_path.exists() or not recon_path.exists() or not gating_path.exists():
        pytest.skip("Missing artifacts")
    ks = json.loads(ks_path.read_text(encoding="utf-8"))
    recon = json.loads(recon_path.read_text(encoding="utf-8"))
    gating = json.loads(gating_path.read_text(encoding="utf-8"))

    assert ks.get("real_data_only") is True
    assert ks.get("fabricated_data") is False
    assert ks.get("type") == "kill_switch_rules_mt"
    assert ks.get("kill_switch_summary", {}).get("no_auto_lift_blocks") is True
    assert ks.get("kill_switch_summary", {}).get("fail_closed") is True

    g_res = gating.get("results_by_timeframe") or {}
    k_res = ks.get("results_by_timeframe") or {}
    r_res = recon.get("results_by_timeframe") or {}
    for tf in ["1h", "4h", "1d"]:
        g_r = g_res[tf]
        k_r = k_res[tf]
        r_r = r_res[tf]
        eligible_g = set(g_r.get("eligible_pairs") or [])
        eligible_k = set(k_r.get("eligible_pairs") or [])
        eligible_r = set(r_r.get("eligible_pairs") or [])
        assert eligible_k == eligible_g
        assert eligible_r == eligible_g
        inv = k_r.get("kill_switch_invariants") or {}
        assert inv.get("cointegration_gated") is True
        assert inv.get("respect_gating") is True
        assert inv.get("fail_closed") is True
        assert inv.get("no_auto_lift_of_blocks") is True
        r_inv = r_r.get("recon_invariants") or {}
        assert r_inv.get("auto_lift_blocks_forbidden") is True
        assert r_inv.get("never_auto_lift_gates") is True
        for pname, kinfo in (k_r.get("pairs") or {}).items():
            if pname not in eligible_g:
                assert kinfo.get("eligible") is False
                br = kinfo.get("blocked_routes") or []
                assert isinstance(br, list) and len(br) >= 1
                triggers = kinfo.get("triggers") or []
                assert isinstance(triggers, list) and len(triggers) >= 1
                for t in triggers:
                    assert t.get("evidence_required") is True
                    assert (
                        t.get("auto_lift_blocks_forbidden") is True
                        or t.get("gating_aware") is True
                        or t.get("respect_gating") is True
                    )
            else:
                assert kinfo.get("eligible") is True
            prov = kinfo.get("provenance") or {}
            assert prov.get("real_data_only") is True
