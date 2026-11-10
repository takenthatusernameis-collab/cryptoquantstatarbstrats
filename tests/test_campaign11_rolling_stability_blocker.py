import hashlib
import json
from pathlib import Path

import pytest

from strategies.pairs_trading import CointegrationPairsStrategy

ROOT = Path(__file__).resolve().parents[1]
CACHE_PKL = ROOT / "data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl"
CACHE_META = Path(str(CACHE_PKL).replace(".pkl", ".meta.json"))


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_cached_spot_subset(cols=("BTC", "ETH"), n=300):
    import pickle

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


def test_c11_causal_per_bar_gate_breakdown_recorded_and_fail_closed_on_real_subset():
    df = _load_cached_spot_subset(("BTC", "ETH"), n=300)
    strat = CointegrationPairsStrategy(
        pair=("BTC", "ETH"),
        lookback=120,
        entry_threshold=2.0,
        cointegration_pvalue=0.05,
        cointegration_check_interval=24,
        use_enriched_gates=True,
        strict_enriched_gates=True,
    )
    sig = strat.generate_signals(df)
    assert "enriched_gates_ok" in sig.columns
    breakdown = strat.get_gate_breakdown()
    assert breakdown is not None and not breakdown.empty
    ok = sig["enriched_gates_ok"].fillna(0.0)
    assert set(ok.unique()).issubset({0.0, 1.0})
    assert int((sig["BTC"].abs() > 1e-12).sum()) == 0
    assert int((sig["ETH"].abs() > 1e-12).sum()) == 0


def test_c11_artifact_provenance_honesty_if_present():
    paths = sorted((ROOT / "reports").glob("campaign11_rolling_stability_blocker_*.json"))
    if not paths:
        pytest.skip("Campaign 11 artifact not yet produced in this run")
    p = paths[-1]
    data = json.loads(p.read_text())
    assert data.get("type") == "campaign11_rolling_stability_blocker"
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
    pairs = data.get("pairs") or {}
    assert len(pairs) >= 10
    expected = {"/".join(pr) for pr in WIDER_PAIRS}
    assert expected.issubset(set(pairs.keys()))
    for _, block in pairs.items():
        assert "sweeps" in block
        assert "any_bar_passes_all_gates" in block
        assert "rolling_stable_blocks_all_bars_all_sweeps" in block
