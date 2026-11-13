#!/usr/bin/env python3
"""Return 0 iff a commit range contains meaningful repository progress.

The scheduled Kilo workflow calls this after each worker session to decide
whether the session produced creditable progress.  Workflow definitions are
maintainer-owned and cannot be persisted by the repository-scoped token, so a
change that touches only ``.github/workflows/`` is not project progress.

Exit codes:
- 0: meaningful non-workflow changes exist (and, when requested, the verified
  remote SHA matches ``--head-sha``).
- 1: no meaningful progress, or the verification precondition failed.
"""
from __future__ import annotations

import argparse
import subprocess
import sys

WORKFLOW_PREFIX = ".github/workflows/"


def changed_paths(base_sha: str, head_sha: str) -> list[str]:
    proc = subprocess.run(
        ["git", "diff", "--name-only", "-z", base_sha, head_sha],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "git diff failed")
    return [path for path in proc.stdout.split("\0") if path]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-sha", required=True)
    parser.add_argument("--head-sha", required=True)
    parser.add_argument(
        "--verified-remote-sha",
        default=None,
        help="when supplied, must equal --head-sha for progress to be credited",
    )
    args = parser.parse_args()

    if args.verified_remote_sha is not None and args.verified_remote_sha != args.head_sha:
        print(
            "progress=no: verified remote sha does not match head sha",
            file=sys.stderr,
        )
        return 1

    if args.base_sha == args.head_sha:
        print("progress=no: base sha equals head sha", file=sys.stderr)
        return 1

    try:
        paths = changed_paths(args.base_sha, args.head_sha)
    except RuntimeError as exc:
        print(f"progress=no: {exc}", file=sys.stderr)
        return 1

    if not paths:
        print("progress=no: commit range has no changed paths", file=sys.stderr)
        return 1

    meaningful = [path for path in paths if not path.startswith(WORKFLOW_PREFIX)]
    if not meaningful:
        print(
            "progress=no: only workflow files changed: " + ", ".join(paths),
            file=sys.stderr,
        )
        return 1

    print(
        "progress=yes: "
        + ", ".join(meaningful[:20])
        + (f" (+{len(meaningful) - 20} more)" if len(meaningful) > 20 else "")
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())