#!/usr/bin/env python3
"""Campaign #13: causal per-bar enriched-gate evaluation on cache 0bab5d6a.

Determines whether cache 0bab5d6a (11sym ADA,AVAX,BNB,BTC,DOT,ETH,LINK,LTC,POL,SOL,XRP,
1h, 5112 bars, 2026-04-01..2026-10-30) yields a causal per-bar enriched-gate edge
(any bar passes all enriched gates under unmodified thresholds) on any pair across
trailing configs, without weakening thresholds and without fabrication. Produces
honest edge/no_edge/insufficient_or_blocked per cache.

Cached real data only. No network refetch. No synthetic/fabricated prices,
IV, volume, fills, order books, labels, or metrics.

Usage:
  PYTHONPATH=$PWD python examples/run_campaign13_0bab5d6a_20261111T023222Z.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE_FULL = "0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7"
CACHE8 = "0bab5d6a"


def main() -> None:
    # Delegate to the shared causal gates script with Campaign #13 labeling
    script = ROOT / "examples/run_campaign12_causal_gates.py"
    if not script.exists():
        sys.exit(f"Missing delegate script: {script}")

    # Run the C12 logic but with C13 output naming via env var
    import os
    os.environ["CAMPAIGN_LABEL"] = "13"
    os.environ["CAMPAIGN_CACHE8"] = CACHE8

    cmd = [
        sys.executable,
        str(script),
        "--cache",
        CACHE_FULL,
    ]
    result = subprocess.run(cmd, cwd=ROOT, capture_output=False)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
