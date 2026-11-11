#!/usr/bin/env python3
"""Campaign #13 causal per-bar enriched-gate evaluation for cache 6d2e08d4.

Wraps ``examples/run_campaign13_causal_gates.py`` for cache
``6d2e08d4d7b969d92b61773c7eead387a52ad74b1c3fb0c69552bd6402dd4383``.
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
        "6d2e08d4d7b969d92b61773c7eead387a52ad74b1c3fb0c69552bd6402dd4383",
    ]
    return subprocess.call(cmd, cwd=str(ROOT))


if __name__ == "__main__":
    raise SystemExit(main())
