#!/usr/bin/env python3
"""Campaign #12 causal per-bar enriched-gate evaluation for cache 4c3bc2f1.

Wraps ``examples/run_campaign12_causal_gates.py`` for cache
``4c3bc2f1ad1323961abdc5280080e595fc9f9b5791d8b7f642a1303eac6d26cd``. Real cached spot only; no network refetch; no synthetic
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
        "4c3bc2f1ad1323961abdc5280080e595fc9f9b5791d8b7f642a1303eac6d26cd",
    ]
    return subprocess.call(cmd, cwd=str(ROOT))


if __name__ == "__main__":
    raise SystemExit(main())
