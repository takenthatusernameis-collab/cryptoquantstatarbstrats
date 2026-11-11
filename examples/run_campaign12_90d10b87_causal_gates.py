#!/usr/bin/env python3
"""Campaign #12 causal per-bar enriched-gate evaluation for cache 90d10b87.

Wraps ``examples/run_campaign12_causal_gates.py`` for cache
``90d10b876bb8eda9619cbba73ed19d6c7db4ea7327284f2e33f10a7872a5b263``.
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
        "90d10b876bb8eda9619cbba73ed19d6c7db4ea7327284f2e33f10a7872a5b263",
    ]
    return subprocess.call(cmd, cwd=str(ROOT))


if __name__ == "__main__":
    raise SystemExit(main())
