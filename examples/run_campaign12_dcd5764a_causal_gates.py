#!/usr/bin/env python3
"""Campaign #12 causal per-bar enriched-gate evaluation for cache dcd5764a.

Wraps ``examples/run_campaign12_causal_gates.py`` for cache
``dcd5764a``. Real cached spot only; no network refetch; no synthetic
inputs; gate thresholds unmodified.
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
        "dcd5764a",
    ]
    return subprocess.call(cmd, cwd=str(ROOT))


if __name__ == "__main__":
    raise SystemExit(main())
