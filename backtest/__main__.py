"""Allow running the CLI as ``python -m backtest``."""

from __future__ import annotations

import sys

from backtest.cli import main

if __name__ == "__main__":
    sys.exit(main())
