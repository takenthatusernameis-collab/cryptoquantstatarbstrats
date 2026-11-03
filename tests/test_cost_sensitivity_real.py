import json
from pathlib import Path

import pytest


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


def test_cost_sensitivity_real_provenance_is_honest():
    """Artifact must declare real-data-only provenance with no fabrication.

    The cost-sensitivity report is derived from real Binance spot candles and
    is gated by the cointegration pairs edge. Every failing gate must be
    recorded in ``blocked_routes`` so no blocked pair masquerades as
    computable. This is a regression test for the provenance gap that let the
    artifact ship without ``real_data_only`` / ``fabricated_data`` /
    ``blocked_routes`` / ``rationale``.
    """
    p = Path("reports/cost_sensitivity_real.json")
    if not p.exists():
        pytest.skip(f"Missing {p}")
    data = json.loads(p.read_text())

    assert data.get("real_data_only") is True
    assert data.get("fabricated_data") is False
    prov = data.get("provenance") or {}
    assert prov.get("real_data_only") is True
    assert prov.get("fabricated_data") is False
    assert isinstance(prov.get("blocked_routes"), list)
    assert isinstance(prov.get("rationale"), str) and prov["rationale"]

    block = data["cost_sensitivity"]
    block_prov = block.get("provenance") or {}
    assert block_prov.get("real_data_only") is True
    assert block_prov.get("fabricated_data") is False
    assert isinstance(block_prov.get("rationale"), str)

    # Cointegration diagnostics must be present and consistent with the gates.
    diag = data.get("cointegration_diagnostics") or {}
    gates = diag.get("gates") or {}
    blocked = diag.get("blocked_routes") or []
    assert isinstance(blocked, list)
    failing = [g for g in ("eg_pass", "johansen_pass", "spread_mr_pass",
                            "hl_bounds_pass", "leg_stationarity_ok",
                            "rolling_stable_ok", "no_structural_break")
               if gates.get(g) is False]
    assert set(b.get("gate") for b in blocked) == set(failing), (
        "blocked_routes must list exactly the failing gates"
    )
    # ``all_pass`` must be consistent with the individual gates.
    assert bool(gates.get("all_pass")) == (len(failing) == 0)

    # Structural breaks are a hard block under both modes.
    if gates.get("no_structural_break") is False:
        assert any(
            b.get("gate") == "structural_break" for b in blocked
        )

    # Fetch provenance must record the real host(s) tried and never fabricate.
    fetch_prov = data.get("fetch_provenance") or {}
    per_symbol = fetch_prov.get("per_symbol") or {}
    assert set(per_symbol.keys()) >= set(data.get("symbols", []))
    for sym, info in per_symbol.items():
        assert info.get("status") == "ok"
        assert int(info.get("bars", 0)) > 0
