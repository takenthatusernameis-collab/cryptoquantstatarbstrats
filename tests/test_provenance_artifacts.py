"""
Regression tests for real-data provenance on portfolio and cointegration artifacts.

Asserts real_data_only/fabricated_data flags, presence of provenance fields
(source, real_data_only, fabricated_data, computed_at, blocked_routes, rationale)
where expected, and that blocked_routes are never fabricated/honest.
"""
from __future__ import annotations

import json
from pathlib import Path

PORTFOLIO_ART = Path("reports/portfolio_real.json")
COINT_DIAG_ART = Path("reports/cointegration_diagnostics_real.json")


PROV_KEYS = (
    "source",
    "real_data_only",
    "fabricated_data",
    "computed_at",
    "blocked_routes",
    "rationale",
)


def test_portfolio_real_provenance_mandate():
    assert PORTFOLIO_ART.exists(), "reports/portfolio_real.json must exist"
    data = json.loads(PORTFOLIO_ART.read_text(encoding="utf-8"))
    assert data.get("real_data_only") is True
    assert data.get("fabricated_data") is False
    # blocked_routes must exist and be a list (honest; may be empty only if nothing blocked)
    br = data.get("blocked_routes")
    assert isinstance(br, list), "portfolio blocked_routes must be a list"
    # If any blocked route entry exists, it must carry provenance with real-data flags
    for i, entry in enumerate(br):
        if isinstance(entry, dict):
            prov = entry.get("provenance") or {}
            if prov:
                msg1 = (
                    f"portfolio blocked_routes[{i}].provenance.real_data_only must be True"
                )
                msg2 = (
                    f"portfolio blocked_routes[{i}].provenance.fabricated_data must be False"
                )
                assert prov.get("real_data_only") is True, msg1
                assert prov.get("fabricated_data") is False, msg2

    # Funding/basis attempts must be logged with provenance (no fabrication).
    funding_basis = data.get("funding_basis") or {}
    assert isinstance(funding_basis, dict), "funding_basis must be a dict"
    assert funding_basis.get("real_data_only") is True
    assert funding_basis.get("fabricated_data") is False
    fb_prov = funding_basis.get("provenance") or {}
    for k in PROV_KEYS:
        assert k in fb_prov, f"funding_basis.provenance missing {k}"
    assert fb_prov.get("real_data_only") is True
    assert fb_prov.get("fabricated_data") is False
    assert isinstance(fb_prov.get("blocked_routes"), list)
    assert isinstance(funding_basis.get("attempts"), list)
    basis = funding_basis.get("basis") or {}
    assert isinstance(basis.get("attempts"), list)


def test_cointegration_diagnostics_real_provenance_per_pair():
    assert COINT_DIAG_ART.exists(), "reports/cointegration_diagnostics_real.json must exist"
    data = json.loads(COINT_DIAG_ART.read_text(encoding="utf-8"))
    assert data.get("real_data_only") is True
    assert data.get("fabricated_data") is False
    cd = data.get("cointegration_diagnostics", {})
    assert isinstance(cd, dict) and len(cd) == 17
    for pname, diag in cd.items():
        prov = diag.get("provenance") or {}
        for k in PROV_KEYS:
            assert k in prov, f"{pname}: provenance missing {k}"
        assert prov["real_data_only"] is True, f"{pname}: real_data_only must be True"
        assert prov["fabricated_data"] is False, f"{pname}: fabricated_data must be False"
        assert isinstance(prov["blocked_routes"], list), f"{pname}: blocked_routes must be a list"
        assert isinstance(prov["computed_at"], str) and prov["computed_at"]
        assert isinstance(prov["rationale"], str) and prov["rationale"]
