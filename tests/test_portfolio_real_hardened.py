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
    # Volume-aware execution
    vae = data.get("volume_aware_execution")
    assert isinstance(vae, dict)
    assert isinstance(vae.get("real_volume_attempts"), list)
    assert isinstance(vae.get("avg_quote_volume_usdt"), dict)
    assert isinstance(vae.get("cost_stress_grid_volume_aware"), list)
    assert len(vae["cost_stress_grid_volume_aware"]) > 0
    # Provenance
    assert isinstance(data.get("universe_changes"), list)
    assert isinstance(data.get("exclusions_with_rationale"), list)
    assert isinstance(data.get("funding_basis"), dict)
