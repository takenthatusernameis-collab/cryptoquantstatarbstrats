import hashlib
import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from examples.run_portfolio_real import PortfolioRiskController
from strategies.pairs_trading import CointegrationPairsStrategy

ROOT = Path(__file__).resolve().parents[1]
CACHE_PKL = ROOT / "data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl"
CACHE_META = (
    ROOT / "data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl"
).with_suffix(".meta.json")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_cached_spot_subset(cols=("BTC", "ETH"), n=240):
    if not CACHE_PKL.exists():
        pytest.skip("cached spot data unavailable")
    with open(CACHE_PKL, "rb") as f:
        df = pickle.load(f)
    df = df.sort_index()
    sub = df[list(cols)].dropna().iloc[:n].copy()
    if len(sub) < n:
        pytest.skip("insufficient cached rows for deterministic subset")
    return sub


def test_causal_per_bar_gate_breakdown_recorded_and_fail_closed_on_real_subset():
    # Causal per-bar path (no enriched_diagnostics supplied) must record a
    # per-bar gate breakdown and fail closed (no exposure) when trailing-window
    # diagnostics are unassessable/failing under strict mode.
    df = _load_cached_spot_subset(("BTC", "ETH"), n=300)
    strat = CointegrationPairsStrategy(
        pair=("BTC", "ETH"),
        lookback=120,
        entry_threshold=2.0,
        cointegration_pvalue=0.05,
        use_enriched_gates=True,
        strict_enriched_gates=True,
    )
    sig = strat.generate_signals(df)
    assert "enriched_gates_ok" in sig.columns
    breakdown = strat.get_gate_breakdown()
    assert breakdown is not None and not breakdown.empty
    # Every assessed bar must be either pass or fail (never unassessable after
    # bfill/ffill/fillna), and under strict mode unassessable->fail(0.0).
    ok = strat.generate_signals(df)["enriched_gates_ok"].fillna(0.0)
    assert set(ok.unique()).issubset({0.0, 1.0})
    # Fail-closed expectation on this real subset/window: no traded exposure.
    assert int((sig["BTC"].abs() > 1e-12).sum()) == 0
    assert int((sig["ETH"].abs() > 1e-12).sum()) == 0


def test_causal_vs_cached_parity_fail_closed():
    # Cached full-history aggregate (uniform fail-closed under strict) and causal
    # per-bar trailing diagnostics must agree on the fail-closed outcome when the
    # aggregate is all-pass but trailing windows are unassessable: cached path
    # applies the aggregate uniformly, causal path recomputes per-bar and fails
    # closed where unassessable. Both must not manufacture exposure.
    df = _load_cached_spot_subset(("BTC", "ETH"), n=300)

    from utils.cointegration import target_schema_diagnostics

    full_diag = target_schema_diagnostics(df["BTC"], df["ETH"], pair_name="BTC/ETH")

    # Cached path: aggregate applied uniformly under strict.
    strat_cached = CointegrationPairsStrategy(
        pair=("BTC", "ETH"),
        lookback=120,
        entry_threshold=2.0,
        cointegration_pvalue=0.05,
        enriched_diagnostics=full_diag,
        use_enriched_gates=True,
        strict_enriched_gates=True,
    )
    sig_cached = strat_cached.generate_signals(df)
    cached_decision = float(sig_cached["enriched_gates_ok"].iloc[0])
    assert cached_decision in (0.0, 1.0)

    # Causal path: trailing per-bar diagnostics.
    strat_causal = CointegrationPairsStrategy(
        pair=("BTC", "ETH"),
        lookback=120,
        entry_threshold=2.0,
        cointegration_pvalue=0.05,
        use_enriched_gates=True,
        strict_enriched_gates=True,
    )
    sig_causal = strat_causal.generate_signals(df)
    causal_ok = sig_causal["enriched_gates_ok"].fillna(0.0)
    assert set(causal_ok.unique()).issubset({0.0, 1.0})

    # Parity on exposure: neither path may emit same-direction exposure; both
    # fail closed on this short trailing subset.
    for sig in (sig_cached, sig_causal):
        prod = (sig["BTC"] * sig["ETH"]).fillna(0.0)
        assert (prod <= 1e-12).all()
        assert int((sig["BTC"].abs() > 1e-12).sum()) == 0
        assert int((sig["ETH"].abs() > 1e-12).sum()) == 0


def test_campaign9_artifact_provenance_honesty_if_present():
    paths = sorted((ROOT / "reports").glob("campaign9_causal_gate_edge_search_*.json"))
    if not paths:
        pytest.skip("Campaign 9 artifact not yet produced in this run")
    p = paths[-1]
    data = json.loads(p.read_text())
    assert data.get("type") == "campaign9_causal_gate_edge_search"
    assert data.get("real_data_only") is True
    assert data.get("fabricated_data") is False
    prov = data.get("provenance") or {}
    assert prov.get("network_fetch_performed") is False
    assert prov.get("no_synthetic_fabricated_inputs") is True
    assert prov.get("cache_spot_pkl_sha256") == _sha256(CACHE_PKL)
    assert prov.get("cache_spot_meta_sha256") == _sha256(CACHE_META)
    conclusion = data.get("conclusion") or {}
    assert conclusion.get("honest") is True
    assert conclusion.get("status") in {"edge", "no_edge", "insufficient_or_blocked"}
    assert conclusion.get("edge_claim") == (conclusion.get("status") == "edge")
    # Pairs sections present with causal gate accounting structure.
    pairs = data.get("pairs") or {}
    assert set(pairs.keys()) >= {"BTC/ETH", "ETH/SOL", "BTC/SOL"}
    for _, block in pairs.items():
        assert "paths" in block and "causal_per_bar" in block["paths"]
        causal = block["paths"]["causal_per_bar"]
        acct = causal.get("enriched_gate_accounting") or {}
        assert "bars_total" in acct and "pass_rate" in acct
        assert "path_comparison" in block


def test_portfolio_risk_controller_applies_declared_controls():
    idx = pd.date_range("2026-01-01", periods=50, freq="h", tz="UTC")
    cols = ["BTC", "ETH", "SOL"]
    w = pd.DataFrame(0.0, index=idx, columns=cols)
    w["BTC"] = 0.8
    w["ETH"] = 0.8
    w["SOL"] = 0.2
    pair_map = {"BTC/ETH": ["BTC", "ETH"]}
    rng = np.random.default_rng(0)
    rets = pd.DataFrame(rng.normal(0, 0.01, size=(len(idx), len(cols))), index=idx, columns=cols)
    rets.iloc[10:15, :] = -0.05
    ctrl = PortfolioRiskController(
        max_gross_exposure=1.4,
        per_pair_cap=0.32,
        max_correlation_exposure=0.5,
        max_cvar_allocation=0.25,
        drawdown_circuit_breaker=-0.10,
    )
    corr = rets.corr().to_dict()
    out = ctrl.apply(w, pair_map=pair_map, correlation_matrix=corr, returns=rets)
    assert (out.abs().sum(axis=1) <= 1.4 + 1e-9).all()
    assert (out[["BTC", "ETH"]].abs().sum(axis=1) <= 0.32 + 1e-9).all()
    assert (out.abs().max(axis=1) <= 0.5 + 1e-9).all()
    assert (out.iloc[-1].abs().sum() == 0.0) or (out.abs().sum(axis=1).min() == 0.0)
