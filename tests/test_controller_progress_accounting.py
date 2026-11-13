"""Tests for the scheduled workflow's controller progress accounting.

The workflow calls ``scripts/controller_progress.py`` after each worker session.
A change that touches only ``.github/workflows/`` must not be credited as
project progress; a non-workflow change must be.  These tests use only the
standard library so they also run in the minimal controller-tests venv.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CONTROLLER_PROGRESS = Path(__file__).resolve().parents[1] / "scripts" / "controller_progress.py"


def _git(repo: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=repo, text=True, stderr=subprocess.STDOUT
    ).strip()


def _commit(repo: Path, filename: str, content: str) -> str:
    path = repo / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    _git(repo, "add", filename)
    _git(repo, "commit", "-m", f"change {filename}")
    return _git(repo, "rev-parse", "HEAD")


def _run(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CONTROLLER_PROGRESS), *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )


def test_controller_progress_accounting(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")
    base = _commit(repo, "README.md", "base\n")

    workflow_head = _commit(repo, ".github/workflows/main.yml", "name: test\n")
    proc = _run(repo, "--base-sha", base, "--head-sha", workflow_head)
    assert proc.returncode == 1, proc.stdout + proc.stderr

    code_head = _commit(repo, "strategies/example.py", "value = 1\n")
    proc = _run(repo, "--base-sha", base, "--head-sha", code_head)
    assert proc.returncode == 0, proc.stdout + proc.stderr

    proc = _run(
        repo,
        "--base-sha",
        base,
        "--head-sha",
        code_head,
        "--verified-remote-sha",
        "0" * 40,
    )
    assert proc.returncode == 1, proc.stdout + proc.stderr

    proc = _run(repo, "--base-sha", code_head, "--head-sha", code_head)
    assert proc.returncode == 1, proc.stdout + proc.stderr