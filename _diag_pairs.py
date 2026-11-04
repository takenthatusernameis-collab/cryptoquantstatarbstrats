"""Diagnostic: evaluate enriched cointegration gates on cached real data.

Records per-pair gate outcomes so the zero-trades blocker can be localised.
Real data only; never fabricates.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from data.cache import load_cached
from data.loader import DataLoader
from utils.cointegration import target_schema_diagnostics

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

SYMBOLS = sorted({s for p in PAIRS for s in p})


def main() -> int:
    loader = DataLoader()
    data, prov = load_cached(loader, SYMBOLS, "2026-04-01", "2026-10-28", "1h")
    print(f"loaded {data.shape[0]} bars x {data.shape[1]} symbols; cache_hit={prov.get('cache_hit')}")

    out: dict[str, dict] = {}
    for a, b in PAIRS:
        diag = target_schema_diagnostics(data[a], data[b], f"{a}/{b}")
        g = diag["gates"]
        spread = diag["spread"]
        rs = diag["rolling_stability"]
        leg = diag["leg_stationarity"]
        out[f"{a}/{b}"] = {
            "gates": g,
            "eg_pvalue": diag["engle_granger"]["pvalue"],
            "johansen_rank": diag["johansen"]["rank"],
            "spread_adf_pvalue": spread.get("adf_spread", {}).get("pvalue"),
            "half_life_ou": spread.get("half_life_ou"),
            "rolling_frac_stable": rs.get("frac_significant"),
            "rolling_n_windows": rs.get("n_windows"),
            "leg1_adf_pvalue": leg.get("leg1_pvalue"),
            "leg2_adf_pvalue": leg.get("leg2_pvalue"),
            "structural_break_flagged": diag["structural_breaks"].get("flagged"),
        }
        print(f"{a}/{b}: all_pass={g['all_pass']} eg={diag['engle_granger']['pvalue']:.4f} "
              f"spread_adf={spread.get('adf_spread', {}).get('pvalue')} "
              f"hl={spread.get('half_life_ou')} roll={rs.get('frac_significant')} "
              f"leg1={leg.get('leg1_pvalue')} leg2={leg.get('leg2_pvalue')} "
              f"sb={diag['structural_breaks'].get('flagged')}")

    # Without the conceptually-mis-specified leg_stationarity gate, which
    # requires both legs to be stationary (contradicting the definition of
    # cointegration, where non-stationary legs combine into a stationary
    # spread), which pairs pass the remaining gates?
    print("\n--- Without leg_stationarity_ok ---")
    for name, d in out.items():
        g = dict(d["gates"])
        g["leg_stationarity_ok"] = True
        g["all_pass"] = all(g[k] for k in (
            "eg_pass", "johansen_pass", "spread_mr_pass", "hl_bounds_pass",
            "rolling_stable_ok", "no_structural_break",
        ))
        print(f"{name}: all_pass={g['all_pass']} "
              f"eg={g['eg_pass']} joh={g['johansen_pass']} spread={g['spread_mr_pass']} "
              f"hl={g['hl_bounds_pass']} roll={g['rolling_stable_ok']} sb={g['no_structural_break']}")

    out_path = Path(__file__).resolve().parent / "reports" / "pairs_gate_diagnosis_real.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, default=float), encoding="utf-8")
    print(f"\nwrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())