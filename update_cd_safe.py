#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

repo = Path('/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats')
sys.path.insert(0, str(repo))

from data.loader import DataLoader
from strategies.pairs_trading import CointegrationPairsStrategy

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

SYMBOLS = sorted(set([s for p in PAIRS for s in p]))
START = "2026-04-01"
END = "2026-10-30"
FREQ = "1h"

def main():
    loader = DataLoader()
    print("Loading data...", flush=True)
    data = loader.load_binance_data(SYMBOLS, START, END, interval=FREQ)
    data = loader.clean_data(data)
    print(f"Loaded {len(data)} bars", flush=True)

    pair_diagnostics = {}
    for pair in PAIRS:
        pname = "/".join(pair)
        try:
            print(f"Computing {pname}...", flush=True)
            a, b = pair
            diag = CointegrationPairsStrategy(pair=pair).get_cointegration_diagnostics(
                data[a], data[b]
            )
            pair_diagnostics[pname] = diag
            print(f"  done {pname}", flush=True)
        except Exception as e:
            print(f"  failed {pname}: {e}", flush=True)
            from utils.cointegration import blocked_schema_diagnostics
            pair_diagnostics[pname] = blocked_schema_diagnostics(
                list(pair),
                [{"error": str(e)[:80]}],
                f"computation_failed: {str(e)[:120]}",
            )

    out_path = repo / "reports" / "portfolio_real.json"
    artifact = json.loads(out_path.read_text(encoding="utf-8"))

    artifact["cointegration_diagnostics"] = pair_diagnostics
    br = []
    for pname, diag in pair_diagnostics.items():
        if isinstance(diag, dict):
            pbr = diag.get("provenance", {}).get("blocked_routes", [])
            if isinstance(pbr, list):
                br.extend(pbr)
    seen = set()
    br_out = []
    for r in br:
        try:
            key = json.dumps(r, sort_keys=True)
        except Exception:
            key = str(r)
        if key not in seen:
            seen.add(key)
            br_out.append(r)
    artifact["blocked_routes"] = br_out

    out_path.write_text(json.dumps(artifact, indent=2, default=float), encoding="utf-8")
    print(f"Wrote updated artifact to {out_path}", flush=True)

if __name__ == "__main__":
    main()
