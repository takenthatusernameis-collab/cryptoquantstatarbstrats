#!/usr/bin/env python3
"""Campaign #12 causal per-bar enriched-gate evaluation for cache 595e501a.

Wraps ``examples/run_campaign12_causal_gates.py`` for cache
``595e501ade340390c6c3310634c01a4f50de9056b16ccc5af5e16123215b14d5``.
Real cached spot only; no network refetch; no synthetic inputs; gate
thresholds unmodified.
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
        "595e501ade340390c6c3310634c01a4f50de9056b16ccc5af5e16123215b14d5",
    ]
    return subprocess.call(cmd, cwd=str(ROOT))


if __name__ == "__main__":
    raise SystemExit(main())
