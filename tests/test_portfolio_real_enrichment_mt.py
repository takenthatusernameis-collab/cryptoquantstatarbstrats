"""
Network-independent tests for the Campaign 28 enrichment of reports/portfolio_real.json.

Validates the enriched artifact schema: tail_risk (regime_conditioned filled,
permutation n>=3000), parameter_stability (per-pair coverage + portfolio_level
provenance.source), bootstrap_ci_portfolio_oos (n_simulations>=3000), and that
enriched values derive from real computation with complete provenance.

These tests never call Binance. They validate the artifact only.
"""

from __future__ import annotations

import json
from pathlib import Path

ARTIFACT = Path("reports/portfolio_real.json")

PAIRS = [
    "BTC/ETH",
    "ETH/SOL",
    "BTC/SOL",
    "ADA/ETH",
    "XRP/BTC",
    "BNB/ETH",
    "BTC/BNB",
    "SOL/BNB",
    "ADA/BTC",
    "XRP/ETH",
    "BNB/BTC",
    "DOT/BTC",
    "DOT/ETH",
    "POL/BTC",
    "AVAX/BTC",
    "LINK/BTC",
    "LTC/BTC",
]

PROVENANCE_KEYS = (
    "source",
    "real_data_only",
    "fabricated_data",
    "computed_at",
    "blocked_routes",
    "rationale",
)

BOOTSTRAP_KEYS = (
    "ci95_total_return",
    "ci95_sharpe_ratio",
    "ci95_max_drawdown",
    "per_timeframe",
    "cost_impact",
    "distinguishability_from_zero",
)
BOOTSTRAP_N = 3000
PERMUTATION_N = 3000


def _artifact() -> dict:
    assert ARTIFACT.exists(), "reports/portfolio_real.json must exist"
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def _assert_provenance(prov: dict, ctx: str) -> None:
    assert isinstance(prov, dict), f"{ctx}: provenance must be a dict"
    for k in PROVENANCE_KEYS:
        assert k in prov, f"{ctx}: provenance missing {k}"
    assert prov["real_data_only"] is True, f"{ctx}: real_data_only must be True"
    assert prov["fabricated_data"] is False, f"{ctx}: fabricated_data must be False"


def test_artifact_type_and_mandate():
    data = _artifact()
    assert data.get("type") == "multi_asset_portfolio_real"
    assert data.get("real_data_only") is True
    assert data.get("fabricated_data") is False
    assert isinstance(data.get("symbols"), list) and len(data["symbols"]) > 0
    assert isinstance(data.get("pairs"), list) and len(data["pairs"]) > 0


def test_portfolio_block():
    data = _artifact()
    port = data.get("portfolio")
    assert isinstance(port, dict), "portfolio block must be present"
    for k in ("total_return", "sharpe_ratio", "max_drawdown", "equity_curve"):
        assert k in port, f"portfolio missing {k}"
    assert isinstance(port["equity_curve"], list)


def test_risk_metrics_block():
    data = _artifact()
    rm = data.get("risk_metrics")
    assert isinstance(rm, dict), "risk_metrics block must be present"
    required = (
        "var_95",
        "cvar_95",
        "max_gross_exposure_limit",
        "per_pair_cap",
        "drawdown_circuit_breaker",
    )
    for k in required:
        assert k in rm, f"risk_metrics missing {k}"
    assert rm["max_correlation_exposure_limit"] > 0
    assert rm["max_cvar_allocation_limit"] > 0
    assert "max_asset_gross_exposure" in rm
    assert rm["max_asset_gross_exposure"] <= rm["max_correlation_exposure_limit"] + 1e-9


def test_walk_forward_portfolio_block():
    data = _artifact()
    wf = data.get("walk_forward_portfolio")
    assert isinstance(wf, dict), "walk_forward_portfolio block must be present"
    assert int(wf.get("n_splits", 0)) >= 10
    splits = wf.get("splits")
    assert isinstance(splits, list) and len(splits) >= 10
    agg = wf.get("aggregate", {})
    assert "is_mean_return" in agg or "oos_mean_return" in agg


def test_regime_adaptive_meta_selector_block():
    data = _artifact()
    ras = data.get("regime_adaptive_meta_selector")
    assert isinstance(ras, dict)
    assert ras.get("implemented") is True
    assert ras.get("validated_oos") is True


def test_portfolio_construction_block():
    data = _artifact()
    pc = data.get("portfolio_construction", {})
    assert pc.get("risk_controller") == "correlation_aware_cvar_style"
    assert pc.get("circuit_breaker_tested") is True


def test_multi_timeframe_walk_forward():
    data = _artifact()
    mtf = data.get("multi_timeframe_walk_forward")
    assert isinstance(mtf, dict)
    for tf in ["1h", "4h", "1d"]:
        assert tf in mtf, f"multi_timeframe_walk_forward missing {tf}"
        m = mtf[tf]
        assert isinstance(m, dict)
        assert m.get("status") == "ok", f"{tf} status not ok: {m.get('status')}"
        assert int(m.get("n_bars", 0)) > 0
        wf = m.get("walk_forward")
        assert isinstance(wf, dict)
        assert int(wf.get("n_splits", 0)) >= 12, f"{tf} n_splits < 12"
        splits = wf.get("splits")
        assert isinstance(splits, list) and len(splits) >= 12, f"{tf} splits < 12"
        for s in splits:
            assert "oos_total_return" in s
            assert "is_total_return" in s
            assert "stability" in s and isinstance(s["stability"], dict)


def test_bootstrap_ci_block():
    data = _artifact()
    bci = data.get("bootstrap_ci_portfolio_oos")
    assert isinstance(bci, dict), "bootstrap_ci_portfolio_oos block must be present"
    assert int(bci.get("n_simulations", 0)) >= 3000, (
        f"bootstrap n_simulations={bci.get('n_simulations')} must be >= 3000"
    )
    assert bci.get("seed") is not None
    assert isinstance(bci.get("ci95_total_return"), list) and len(bci["ci95_total_return"]) == 2
    assert isinstance(bci.get("ci95_sharpe_ratio"), list) and len(bci["ci95_sharpe_ratio"]) == 2
    assert isinstance(bci.get("ci95_max_drawdown"), list) and len(bci["ci95_max_drawdown"]) == 2
    assert isinstance(bci.get("per_timeframe"), dict)
    for tf in ["1h", "4h", "1d"]:
        assert tf in bci["per_timeframe"], f"bootstrap per_timeframe missing {tf}"
    ci = bci.get("cost_impact")
    assert isinstance(ci, dict)
    assert "ci95_total_return_net" in ci
    assert "mean_turnover_per_period" in ci
    assert "cost_per_period_assumed" in ci
    dfz = bci.get("distinguishability_from_zero")
    assert isinstance(dfz, dict)
    assert "p_value_final_equity_le_1" in dfz


def test_tail_risk_regime_conditioned_filled():
    data = _artifact()
    tail_risk = data.get("tail_risk")
    assert isinstance(tail_risk, dict), "tail_risk must be a dict"
    rc = tail_risk.get("regime_conditioned")
    assert rc is not None, "tail_risk.regime_conditioned must not be None"
    assert isinstance(rc, dict)
    assert rc.get("regimes") is not None
    _assert_provenance(rc.get("provenance", {}), "tail_risk.regime_conditioned")


def test_tail_risk_permutation_test_n_ge_3000():
    data = _artifact()
    tail_risk = data.get("tail_risk", {})
    pt = tail_risk.get("permutation_test", {})
    assert pt, "tail_risk.permutation_test must be present"
    n = int(pt.get("n_permutations", 0))
    assert n >= 3000, f"permutation_test n_permutations={n} must be >= 3000"
    assert "p_value" in pt
    assert "observed_mean" in pt


def test_parameter_stability_per_pair_coverage_and_provenance():
    data = _artifact()
    ps = data.get("parameter_stability")
    assert isinstance(ps, dict)
    per_pair = {k: v for k, v in ps.items() if k != "portfolio_level"}
    assert isinstance(per_pair, dict)
    expected = set(PAIRS)
    assert set(per_pair.keys()) == expected, (
        f"per-pair coverage mismatch: extra={set(per_pair.keys())-expected}, "
        f"missing={expected-set(per_pair.keys())}"
    )
    for pname, entry in per_pair.items():
        assert isinstance(entry, dict), f"{pname}: entry not a dict"
        assert "selected_params" in entry, f"{pname}: missing selected_params"
        assert "degradation" in entry, f"{pname}: missing degradation"
        assert "regime_notes" in entry, f"{pname}: missing regime_notes"
        assert isinstance(entry["regime_notes"], str) and entry["regime_notes"], (
            f"{pname}: regime_notes must be a non-empty string"
        )
        _assert_provenance(entry.get("provenance", {}), f"parameter_stability.{pname}")


def test_parameter_stability_portfolio_level_provenance():
    data = _artifact()
    ps = data.get("parameter_stability")
    pl = ps.get("portfolio_level", {})
    assert isinstance(pl, dict), "parameter_stability.portfolio_level must be a dict"
    prov = pl.get("provenance", {})
    for k in PROVENANCE_KEYS:
        assert k in prov, f"portfolio_level provenance missing {k}"
    assert "source" in prov, "portfolio_level provenance.source is required"
    assert prov["real_data_only"] is True
    assert prov["fabricated_data"] is False


def test_volume_aware_execution_real():
    data = _artifact()
    vae = data.get("volume_aware_execution")
    assert isinstance(vae, dict), "volume_aware_execution block must be present"
    assert isinstance(vae.get("real_volume_attempts"), list)
    assert isinstance(vae.get("avg_quote_volume_usdt"), dict)
    assert len(vae["avg_quote_volume_usdt"]) > 0, "no real quote volume fetched"
    assert all(isinstance(v, (int, float)) and v > 0 for v in vae["avg_quote_volume_usdt"].values())
    assert isinstance(vae.get("cost_stress_grid_volume_aware"), list)
    assert len(vae["cost_stress_grid_volume_aware"]) > 0
    hosts = {a.get("host") for a in vae["real_volume_attempts"]}
    assert any("binance.com" in (h or "") for h in hosts), "no binance.com host attempt logged"


def test_universe_and_exclusions():
    data = _artifact()
    assert isinstance(data.get("universe_changes"), list) and len(data["universe_changes"]) > 0
    assert isinstance(data.get("exclusions_with_rationale"), list)
    assert isinstance(data.get("funding_basis"), dict)
    included_assets = set()
    for u in data["universe_changes"]:
        if u.get("action") == "include":
            included_assets.update(u["pair"].split("/"))
    for e in data["exclusions_with_rationale"]:
        cand = e.get("candidate", "")
        base = cand.split("/")[0] if cand else ""
        if base and base in included_assets:
            bad_actions = ("excluded_insufficient_history", "excluded_unavailable")
            assert e.get("action") not in bad_actions, (
                f"Contradiction: {cand} excluded as unavailable but asset {base} is included"
            )


def test_no_fabrication_anywhere_in_artifact():
    data = _artifact()
    assert data.get("fabricated_data") is False
    assert data.get("real_data_only") is True
    for section in (
        "tail_risk",
        "parameter_stability",
        "bootstrap_ci_portfolio_oos",
    ):
        val = data.get(section)
        if isinstance(val, dict):
            prov = val.get("provenance", {})
            assert prov.get("fabricated_data") is False or prov == {}, (
                f"{section} provenance must not claim fabrication"
            )


def test_enriched_blocks_have_complete_provenance():
    data = _artifact()
    _assert_provenance(
        data.get("tail_risk", {}).get("regime_conditioned", {}).get(
            "provenance", {}
        ),
        "tail_risk.regime_conditioned",
    )
    pl = data.get("parameter_stability", {}).get("portfolio_level", {})
    _assert_provenance(pl.get("provenance", {}), "parameter_stability.portfolio_level")
    for pname in PAIRS:
        entry = data.get("parameter_stability", {}).get(pname, {})
        _assert_provenance(entry.get("provenance", {}), f"parameter_stability.{pname}")


def test_bootstrap_n_simulations_minimum():
    data = _artifact()
    bci = data.get("bootstrap_ci_portfolio_oos", {})
    assert int(bci.get("n_simulations", 0)) >= BOOTSTRAP_N
