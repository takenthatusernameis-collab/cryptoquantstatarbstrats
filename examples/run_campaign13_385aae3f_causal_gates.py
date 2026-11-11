#!/usr/bin/env python3
"""Campaign #13 causal per-bar enriched-gate evaluation for cache 385aae3f.

Wraps ``examples/run_campaign12_causal_gates.py`` for cache
``385aae3f022b2d7bba4ec502cb8e7399d26cb31b961a016aebf7d165450fd4ba``
(2sym BTC,ETH; 1h; 5064 bars; 2026-04-01..2026-10-28). Real cached spot
only; no network refetch; no synthetic inputs; gate thresholds unmodified.
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
        "385aae3f022b2d7bba4ec502cb8e7399d26cb31b961a016aebf7d165450fd4ba",
    ]
    return subprocess.call(cmd, cwd=str(ROOT))


if __name__ == "__main__":
    raise SystemExit(main())