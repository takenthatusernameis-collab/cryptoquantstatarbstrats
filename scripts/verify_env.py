#!/usr/bin/env python3
"""Verify that every Python import required by the repository is available.

This is the read-only companion to ``scripts/bootstrap_dev_env.py``.  It exits
0 only when all runtime and test dependencies import successfully.  It never
installs anything and never touches market data.
"""
from __future__ import annotations

import argparse
import importlib
import json
import sys

RUNTIME_MODULES = ("numpy", "pandas", "scipy", "statsmodels", "sklearn", "yaml")
TEST_MODULES = ("pytest", "pytest_asyncio", "hmmlearn", "pydantic", "aiohttp")
REQUIRED_MODULES = RUNTIME_MODULES + TEST_MODULES


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit a machine-readable JSON summary on stdout",
    )
    args = parser.parse_args()

    versions: dict[str, str] = {}
    missing: list[dict[str, str]] = []
    for name in REQUIRED_MODULES:
        try:
            module = importlib.import_module(name)
        except Exception as exc:  # noqa: BLE001 - report any import failure
            missing.append({"module": name, "error": f"{type(exc).__name__}: {exc}"})
            continue
        versions[name] = str(getattr(module, "__version__", "unknown"))

    ready = not missing
    payload = {
        "ready": ready,
        "missing": missing,
        "versions": versions,
        "python": sys.version.split()[0],
    }

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        for name in REQUIRED_MODULES:
            status = "ok" if name in versions else "MISSING"
            version = versions.get(name, "")
            print(f"{status:7s} {name} {version}")
        if missing:
            print("missing modules: " + ", ".join(item["module"] for item in missing))

    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())