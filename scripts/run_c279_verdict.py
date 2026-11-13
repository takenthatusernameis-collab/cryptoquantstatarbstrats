#!/usr/bin/env python3
"""C279C — Negative result verdict for C279 (zero tradable spot-price configs).
Emits reports/campaign279_negative_result_<ts>.json.
No new statistic invented, no thresholds lowered, no gates fabricated.
"""
from __future__ import annotations
import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
reports = root / "reports"
ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')

def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def jdefault(o):
    import numpy as np, pandas as pd
    if isinstance(o, (np.bool_,)): return bool(o)
    if isinstance(o, (np.integer,)): return int(o)
    if isinstance(o, (np.floating,)): return float(o) if np.isfinite(o) else None
    if isinstance(o, np.ndarray): return o.tolist()
    if isinstance(o, pd.Timestamp): return str(o)
    raise TypeError(str(type(o)))

C279A = reports / "campaign279_causal_pairs_20261113T020211Z.json"
C279B = reports / "campaign279_price_only_sweep_20261113T020443Z.json"

a = json.loads(C279A.read_text())
b = json.loads(C279B.read_text())

negative = {
    "generated_at_utc": ts,
    "campaign": 279,
    "part": "C",
    "analysis": "negative_result_verdict",
    "verdict": "NOT_TRADABLE",
    "finding": "No spot-price config in the repo produces costed OOS PnL on the real 11-asset cache. Zero tradable edge across C279A (causal cointegration pairs) and C279B (single-asset price-only MeanReversion + Momentum).",
    "basis": "spot_price_only",
    "c279a": {
        "artifact": str(C279A.relative_to(root)),
        "sha256": sha256_file(C279A),
        "pairs": a["summary"]["n_pairs"],
        "configs_per_pair": a["summary"]["n_configs_per_pair"],
        "total_runs": a["summary"]["n_total_runs"],
        "edge_proven": a["summary"]["n_edge_proven"],
        "zero_exposure_runs": a["summary"]["n_zero_exposure"],
        "blocking_evidence": "rolling_stable_ok pass share = 0.0 across all pair runs; causal per-bar cointegration gates fail-closed on every bar (no entries permitted). Last trailing EG p-values all > 0.05 on rolling windows; pairs not cointegrated on this 6-month cache.",
    },
    "c279b": {
        "artifact": str(C279B.relative_to(root)),
        "sha256": sha256_file(C279B),
        "assets": b["summary"]["n_assets"],
        "mean_reversion_configs": b["summary"]["n_mr_configs"],
        "momentum_configs": b["summary"]["n_momentum_configs"],
        "total_runs": b["summary"]["n_total_runs"],
        "edge_proven": b["summary"]["n_edge_proven"],
        "with_exposure": b["summary"]["n_with_exposure"],
        "grids": {
            "mean_reversion": {"lookback": [24, 48, 96, 120], "entry_threshold": [1.5, 2.0, 2.5], "exit_threshold": [0.25, 0.5]},
            "momentum": {"n": [10, 20, 40], "m": [20, 40, 80], "entry_threshold": [0.005, 0.01, 0.02]},
        },
        "finding": "All 561 single-asset configs produced exposure but none achieved price_only_edge_proven=true (all cost slices OOS net sum > 0 AND mean OOS net > mean equal-weight B&H spot-price mean).",
    },
    "cost_grid_bps": [[0, 0], [5, 5], [10, 10], [20, 20], [40, 40]],
    "walk_forward": {"train": 720, "test": 168, "step": 168},
    "data_cache": {
        "path": "data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl",
        "sha256": "5607573327c089e0ab990ac48f931752a99e6e89f60599cb2557246f0f5f8c9b",
        "assets": ["ADA", "AVAX", "BNB", "BTC", "DOT", "ETH", "LINK", "LTC", "POL", "SOL", "XRP"],
        "bars": 5112,
        "interval": "1h",
        "window": "2026-04-01 -> 2026-10-30",
    },
    "conclusion": "No tradable edge. Do not invent a new statistic, lower thresholds, coerce gates, or fabricate data. C279 complete; no spot-price strategy on this cache passes the costed OOS edge test.",
}
op = reports / f"campaign279_negative_result_{ts}.json"
op.write_text(json.dumps(negative, indent=2, default=jdefault) + "\n")
print(json.dumps({
    "artifact": str(op.relative_to(root)),
    "sha256": sha256_file(op),
    "verdict": "NOT_TRADABLE",
}, indent=2))
