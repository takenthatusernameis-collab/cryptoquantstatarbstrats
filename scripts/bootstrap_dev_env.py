#!/usr/bin/env python3
"""Idempotent dependency bootstrap for the scheduled Kilo worker shell.

The CI agent shell can start without the repository's Python dependencies.
Historically the scheduled "Kilo General Agent Loop" worker failed with
``ModuleNotFoundError: No module named 'numpy'`` (and later ``pandas``,
``hmmlearn``, ``pydantic``, ``aiohttp``).  This script installs the runtime and
test dependencies with ``--user`` and then verifies every import.

It never edits ``.github/workflows/main.yml`` and never fetches market data.
Run it before any campaign or test command.
"""
from __future__ import annotations

import argparse
import importlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

RUNTIME_MODULES = ("numpy", "pandas", "scipy", "statsmodels", "sklearn", "yaml")
TEST_MODULES = ("pytest", "pytest_asyncio", "hmmlearn", "pydantic", "aiohttp")
REQUIRED_MODULES = RUNTIME_MODULES + TEST_MODULES


def missing_modules() -> list[str]:
    missing: list[str] = []
    for name in REQUIRED_MODULES:
        try:
            importlib.import_module(name)
        except Exception:
            missing.append(name)
    return missing


def install_requirements(timeout: int) -> tuple[int, str]:
    cmd = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--disable-pip-version-check",
        "--no-input",
        "--user",
        "-r",
        str(ROOT / "requirements.txt"),
        "pytest",
        "pytest-asyncio",
        "hmmlearn",
        "pydantic",
        "aiohttp",
    ]
    print("+ " + " ".join(cmd), flush=True)
    try:
        proc = subprocess.run(
            cmd,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return 124, f"pip install exceeded {timeout}s"
    except FileNotFoundError as exc:
        return 127, f"pip executable not found: {exc}"
    output = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, output[-4000:]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit a machine-readable JSON summary on stdout",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="maximum seconds for the pip install step (default: 600)",
    )
    args = parser.parse_args()

    missing_before = missing_modules()
    install_rc: int | None = None
    install_tail = ""
    if missing_before:
        install_rc, install_tail = install_requirements(max(60, args.timeout))

    missing_after = missing_modules()
    ready = not missing_after
    payload = {
        "ready": ready,
        "missing_before": missing_before,
        "missing_after": missing_after,
        "pip_returncode": install_rc,
        "pip_output_tail": install_tail,
        "python": sys.version.split()[0],
        "repo": str(ROOT),
        "note": (
            "Runtime and test dependencies are importable."
            if ready
            else "Dependency bootstrap incomplete; do not fabricate a campaign result."
        ),
    }

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(json.dumps(payload, indent=2))

    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())