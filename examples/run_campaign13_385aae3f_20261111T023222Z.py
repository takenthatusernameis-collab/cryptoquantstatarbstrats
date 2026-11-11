#!/usr/bin/env python3
"""Campaign #13: causal per-bar enriched-gate evaluation on cache 385aae3f.

Determines whether cache 385aae3f (2sym BTC,ETH, 1h, 5064 bars,
2026-04-01..2026-10-28, fetch_real_data_only:true) yields a causal per-bar
enriched-gate edge (any bar passes all enriched gates under unmodified
thresholds) on any pair across trailing configs, without weakening thresholds
and without fabrication. Produces honest edge/no_edge/insufficient_or_blocked
per cache.

Cached real data only. No network refetch. No synthetic/fabricated prices,
IV, volume, fills, order books, labels, or metrics.

Usage:
  PYTHONPATH=$PWD python examples/run_campaign13_385aae3f_20261111T023222Z.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE_FULL = "385aae3f022b2d7bba4ec502cb8e7399d26cb31b961a016aebf7d165450fd4ba"
CACHE8 = "385aae3f"


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