"""Frozen campaign artifacts must be strict JSON with no bare non-finite tokens.

Python's ``json`` parser accepts ``NaN``/``Infinity`` by default, but strict
JSON consumers reject them.  The C281-C284 evidence is frozen; this test guards
against a future edit silently introducing a non-finite token.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

NON_FINITE_TOKEN = re.compile(r"(?<![\w\"])-?(?:NaN|Infinity)(?![\w\"])")
FROZEN_GLOBS = (
    "campaign281*.json",
    "campaign282*.json",
    "campaign283*.json",
    "campaign284*.json",
)


def test_frozen_campaign_artifacts_are_strict_json() -> None:
    reports = Path("reports")
    files: list[Path] = []
    for pattern in FROZEN_GLOBS:
        files.extend(sorted(reports.glob(pattern)))
    assert files, "no frozen campaign artifacts found"

    for path in files:
        text = path.read_text(encoding="utf-8")
        match = NON_FINITE_TOKEN.search(text)
        assert match is None, f"bare non-finite token {match.group(0)!r} in {path}"
        json.loads(text)