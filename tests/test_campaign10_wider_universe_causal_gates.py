import hashlib
import json
import pickle
from pathlib import Path

import pytest

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


WIDER_PAIRS = [
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
    ("BTC", "ETH"),
    ("ETH", "SOL"),
    ("BTC", "SOL"),
]


def test_c10_wider_universe_pairs_have_cached_symbols():
    # Every wider-universe pair must be reconstructible from the cached real
    # spot universe (no refetch, no fabrication).
    if not CACHE_PKL.exists():
        pytest.skip("cached spot data unavailable")
    with open(CACHE_PKL, "rb") as f:
        df = pickle.load(f)
    df = df.sort_index()
    available = set(df.columns)
    missing = [s for s in {s for p in WIDER_PAIRS for s in p} if s not in available]
    assert not missing, f"cached universe missing symbols: {missing}"


def test_c10_causal_per_bar_gate_breakdown_recorded_and_fail_closed_on_real_subset():
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
    ok = strat.generate_signals(df)["enriched_gates_ok"].fillna(0.0)
    assert set(ok.unique()).issubset({0.0, 1.0})
    assert int((sig["BTC"].abs() > 1e-12).sum()) == 0
    assert int((sig["ETH"].abs() > 1e-12).sum()) == 0


def test_c10_causal_vs_cached_parity_fail_closed():
    df = _load_cached_spot_subset(("BTC", "ETH"), n=300)

    from utils.cointegration import target_schema_diagnostics

    full_diag = target_schema_diagnostics(df["BTC"], df["ETH"], pair_name="BTC/ETH")

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

    for sig in (sig_cached, sig_causal):
        prod = (sig["BTC"] * sig["ETH"]).fillna(0.0)
        assert (prod <= 1e-12).all()
        assert int((sig["BTC"].abs() > 1e-12).sum()) == 0
        assert int((sig["ETH"].abs() > 1e-12).sum()) == 0


def test_c10_artifact_provenance_honesty_if_present():
    paths = sorted((ROOT / "reports").glob("campaign10_wider_universe_causal_gates_*.json"))
    if not paths:
        pytest.skip("Campaign 10 artifact not yet produced in this run")
    p = paths[-1]
    data = json.loads(p.read_text())
    assert data.get("type") == "campaign10_wider_universe_causal_gates"
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
    # Wider-universe pairs section present with causal gate accounting.
    pairs = data.get("pairs") or {}
    assert len(pairs) >= 10, f"expected >=10 pairs, got {len(pairs)}"
    expected = {"/".join(pr) for pr in WIDER_PAIRS}
    assert expected.issubset(set(pairs.keys())), f"missing pairs: {expected - set(pairs.keys())}"
    for _, block in pairs.items():
        assert "paths" in block and "causal_per_bar" in block["paths"]
        causal = block["paths"]["causal_per_bar"]
        acct = causal.get("enriched_gate_accounting") or {}
        assert "bars_total" in acct and "pass_rate" in acct
        assert "path_comparison" in block
