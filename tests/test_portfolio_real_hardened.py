import json
from pathlib import Path


def test_portfolio_real_artifact_hardened_schema():
    p = Path("reports/portfolio_real.json")
    assert p.exists()
    data = json.loads(p.read_text())
    assert data.get("real_data_only") is True
    assert data.get("fabricated_data") is False
    # Multi-timeframe walk-forward
    mtf = data.get("multi_timeframe_walk_forward")
    assert isinstance(mtf, dict)
    for tf in ["1h", "4h", "1d"]:
        assert tf in mtf
        m = mtf[tf]
        assert isinstance(m, dict)
        assert m.get("status") == "ok"
        assert int(m.get("n_bars", 0)) > 0
        wf = m.get("walk_forward")
        assert isinstance(wf, dict)
        assert int(wf.get("n_splits", 0)) >= 12
        splits = wf.get("splits")
        assert isinstance(splits, list)
        assert len(splits) >= 12
        # Per-split IS/OOS and stability/degradation must be present.
        for s in splits:
            assert "oos_total_return" in s
            assert "is_total_return" in s
            assert "stability" in s and isinstance(s["stability"], dict)
    # Bootstrap CI
    bci = data.get("bootstrap_ci_portfolio_oos")
    assert isinstance(bci, dict)
    assert int(bci.get("n_simulations", 0)) >= 2000
    assert bci.get("seed") is not None
    assert isinstance(bci.get("ci95_total_return"), list)
    assert len(bci["ci95_total_return"]) == 2
    assert isinstance(bci.get("ci95_sharpe_ratio"), list)
    assert isinstance(bci.get("ci95_max_drawdown"), list)
    assert isinstance(bci.get("per_timeframe"), dict)
    for tf in ["1h", "4h", "1d"]:
        if tf in mtf and mtf[tf].get("status") == "ok":
            assert tf in bci["per_timeframe"]
    # Transaction-cost impact across bootstrap must be present and auditable.
    ci = bci.get("cost_impact")
    assert isinstance(ci, dict)
    assert "ci95_total_return_net" in ci
    assert "mean_turnover_per_period" in ci
    assert "cost_per_period_assumed" in ci
    # Distinguishability from breakeven must be present.
    assert "distinguishability_from_zero" in bci
    assert "p_value_final_equity_le_1" in bci["distinguishability_from_zero"]
    # Volume-aware execution
    vae = data.get("volume_aware_execution")
    assert isinstance(vae, dict)
    assert isinstance(vae.get("real_volume_attempts"), list)
    assert isinstance(vae.get("avg_quote_volume_usdt"), dict)
    assert isinstance(vae.get("cost_stress_grid_volume_aware"), list)
    assert len(vae["cost_stress_grid_volume_aware"]) > 0
    # Real volume fetch must have actually succeeded for at least one symbol
    # (not a silent zero-fill / all-failed fallback). This is the control that
    # prevents the volume-aware block from being vacuously present.
    assert len(vae["avg_quote_volume_usdt"]) > 0, "no real quote volume fetched"
    assert all(
        isinstance(v, (int, float)) and v > 0
        for v in vae["avg_quote_volume_usdt"].values()
    )
    # Real volume fetch must have attempted at least one host per symbol with
    # a logged endpoint; it must NOT be a silent zero-fill.
    hosts = {a.get("host") for a in vae["real_volume_attempts"]}
    assert any("binance.com" in (h or "") for h in hosts)
    # Provenance
    assert isinstance(data.get("universe_changes"), list)
    assert len(data.get("universe_changes", [])) > 0
    assert isinstance(data.get("exclusions_with_rationale"), list)
    assert isinstance(data.get("funding_basis"), dict)
    # Universe changes must not contradict exclusions: an excluded single-leg
    # candidate whose base asset is already inside an included pair is a
    # contradiction and must not be asserted as both.
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
