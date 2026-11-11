#!/usr/bin/env python3
"""Campaign #13: causal per-bar enriched-gate evaluation on cache 6d2e08d4.

Determines whether cache 6d2e08d4 (2sym POL,BTC, 1h, 5112 bars,
2026-04-01..2026-10-30) yields a causal per-bar enriched-gate edge (any bar
passes all enriched gates under unmodified thresholds) on any pair across
trailing configs, without weakening thresholds and without fabrication.
Produces honest edge/no_edge/insufficient_or_blocked per cache.

Cached real data only. No network refetch. No synthetic/fabricated prices,
IV, volume, fills, order books, labels, or metrics.

Usage:
  PYTHONPATH=$PWD python examples/run_campaign13_6d2e08d4_20261111T023222Z.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE_FULL = "6d2e08d4d7b969d92b61773c7eead387a52ad74b1c3fb0c69552bd6402dd4383"
CACHE8 = "6d2e08d4"


def main() -> None:
    script = ROOT / "examples/run_campaign12_causal_gates.py"
    if not script.exists():
        sys.exit(f"Missing delegate script: {script}")

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