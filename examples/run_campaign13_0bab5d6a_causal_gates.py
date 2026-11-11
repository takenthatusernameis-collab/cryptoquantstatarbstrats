#!/usr/bin/env python3
"""Campaign #13 causal per-bar enriched-gate evaluation for cache 0bab5d6a.

Wraps ``examples/run_campaign13_causal_gates.py`` for cache
``0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7``.
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
        str(ROOT / "examples" / "run_campaign13_causal_gates.py"),
        "--cache",
        "0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7",
    ]
    return subprocess.call(cmd, cwd=str(ROOT))


if __name__ == "__main__":
    raise SystemExit(main())
