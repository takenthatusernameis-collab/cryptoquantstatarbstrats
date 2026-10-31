"""
Network-independent tests for parameter_stability and tail_risk in the real
portfolio artifact (reports/portfolio_real.json).

These tests never call Binance. They validate the artifact schema and the
step-3 campaign invariants (regime_conditioned filled, permutation n>=3000,
parameter_stability provenance/degradation/regime notes, bootstrap n>=3000).
The artifact is validated but never regenerated here.
"""
from __future__ import annotations

import json
from pathlib import Path

ARTIFACT = Path("reports/portfolio_real.json")

PAIRS = [
    ("BTC", "ETH"),
    ("ETH", "SOL"),
    ("BTC", "SOL"),
    ("ADA", "ETH"),
    ("XRP", "BTC"),
    ("BNB", "ETH"),
    ("BTC", "BNB"),
    ("SOL", "BNB"),
    ("ADA", "BTC"),
    ("XRP", "ETH"),
    ("BNB", "BTC"),
    ("DOT", "BTC"),
    ("DOT", "ETH"),
    ("POL", "BTC"),
    ("AVAX", "BTC"),
    ("LINK", "BTC"),
    ("LTC", "BTC"),
]

PROVENANCE_KEYS = (
    "source",
    "real_data_only",
    "fabricated_data",
    "computed_at",
    "blocked_routes",
    "rationale",
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_artifact_is_real_data_only():
    data = _artifact()
    assert data.get("real_data_only") is True
    assert data.get("fabricated_data") is False


def test_tail_risk_regime_conditioned_filled():
    data = _artifact()
    tail_risk = data.get("tail_risk", {})
    assert isinstance(tail_risk, dict), "tail_risk must be a dict"
    rc = tail_risk.get("regime_conditioned")
    assert rc is not None, "tail_risk.regime_conditioned must not be None"
    assert isinstance(rc, dict), "tail_risk.regime_conditioned must be a dict"
    assert rc.get("regimes") is not None, "regime_conditioned.regimes must be present"
    prov = rc.get("provenance", {})
    for k in PROVENANCE_KEYS:
        assert k in prov, f"regime_conditioned provenance missing {k}"
    assert prov["real_data_only"] is True
    assert prov["fabricated_data"] is False


def test_tail_risk_permutation_test_n_ge_3000():
    data = _artifact()
    tail_risk = data.get("tail_risk", {})
    pt = tail_risk.get("permutation_test", {})
    assert pt, "tail_risk.permutation_test must be present"
    n = int(pt.get("n_permutations", 0))
    assert n >= 3000, f"permutation_test n_permutations={n} must be >= 3000"
    assert "p_value" in pt
    assert "observed_mean" in pt


def test_parameter_stability_per_pair_provenance_and_degradation():
    data = _artifact()
    ps = data.get("parameter_stability", {})
    assert isinstance(ps, dict)
    per_pair = ps.get("per_pair", {})
    assert isinstance(per_pair, dict)
    expected = {f"{a}/{b}" for a, b in PAIRS}
    assert set(per_pair.keys()) == expected, set(per_pair.keys())
    for pname, entry in per_pair.items():
        assert isinstance(entry, dict), f"{pname}: per_pair entry not a dict"
        assert "top_params" in entry, f"{pname}: missing top_params"
        assert "pair_metrics" in entry, f"{pname}: missing pair_metrics"
        prov = entry.get("provenance", {})
        for k in PROVENANCE_KEYS:
            assert k in prov, f"{pname}: provenance missing {k}"
        assert prov["real_data_only"] is True
        assert prov["fabricated_data"] is False
        assert "degradation" in entry, f"{pname}: missing degradation"
        assert "regime_notes" in entry, f"{pname}: missing regime_notes"
        assert isinstance(entry["regime_notes"], str) and entry["regime_notes"]


def test_parameter_stability_portfolio_level_provenance():
    data = _artifact()
    ps = data.get("parameter_stability", {})
    pl = ps.get("portfolio_level", {})
    assert isinstance(pl, dict)
    prov = pl.get("provenance", {})
    for k in PROVENANCE_KEYS:
        assert k in prov, f"portfolio_level provenance missing {k}"
    assert prov["real_data_only"] is True
    assert prov["fabricated_data"] is False


def test_bootstrap_ci_n_simulations_ge_3000():
    data = _artifact()
    bci = data.get("bootstrap_ci_portfolio_oos", {})
    assert isinstance(bci, dict)
    assert int(bci.get("n_simulations", 0)) >= 3000, (
        f"bootstrap n_simulations={bci.get('n_simulations')} must be >= 3000"
    )
    assert bci.get("seed") is not None


def test_no_fabrication_anywhere_in_artifact():
    data = _artifact()
    assert data.get("fabricated_data") is False
    assert data.get("real_data_only") is True
    # provenance blocks across the artifact must not claim fabrication.
    for section in ("tail_risk", "parameter_stability", "bootstrap_ci_portfolio_oos"):
        val = data.get(section)
        if isinstance(val, dict):
            prov = val.get("provenance", {})
            assert prov.get("fabricated_data") is False or prov == {}, (
                f"{section} provenance must not claim fabrication"
            )
