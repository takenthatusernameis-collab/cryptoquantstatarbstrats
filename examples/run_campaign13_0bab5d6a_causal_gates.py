#!/usr/bin/env python3
"""Campaign #13 causal per-bar enriched-gate evaluation for cache 0bab5d6a.

Wraps ``examples/run_campaign12_causal_gates.py`` for cache
``0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7``
(11sym ADA,AVAX,BNB,BTC,DOT,ETH,LINK,LTC,POL,SOL,XRP; 1h; 5112 bars;
2026-04-01..2026-10-30). Real cached spot only; no network refetch; no
synthetic inputs; gate thresholds unmodified.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    cmd = [
        sys.executable,
        str(ROOT / "examples" / "run_campaign12_causal_gates.py"),
        "--cache",
        "0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7",
    ]
    return subprocess.call(cmd, cwd=str(ROOT))


if __name__ == "__main__":
    raise SystemExit(main())
