#!/usr/bin/env python3
"""Recovery: compact the C300 5m cache pickle below the GitHub 100 MB push limit.

Diagnosis: ``data/cache/campaign300_multianual_perp_funding_basis_ts_5m.pkl`` is
148.08 MB on disk.  GitHub's pre-receive hook rejects any blob > 100.00 MB, so
``git push origin main`` from local HEAD 429acf7 is hard-blocked.  The bloat is
pandas overhead, not data: every per-asset leg is a ``pandas.Series`` whose
pickle is ~3x the raw ndarray (index + metadata are serialised per element
family).  Raw payload is ~69 MB total.

Fix: re-serialise the same payload with ``pandas.Series`` legs converted to
plain ``numpy.ndarray`` (``DatetimeIndex`` -> ``np.datetime64[us]`` array).
``scripts/run_c300_multianual_funding_basis_ts_oos.py`` already handles the
non-``DatetimeIndex`` / non-``Series`` shape (lines 266-270: isinstance check +
``pd.DatetimeIndex(pa["index"])`` + ``.astype(float).reindex(index)``), so this
is a pure container-format change with zero data or semantics change.

Safety:
- original file is copied verbatim to ``data/cache/recovery/campaign300_multianual_perp_funding_basis_ts_5m.pkl.orig``
  before any rewrite, so the pre-push blob is recoverable.
- every array leg is byte-compared against the original before overwrite.
- SHA256 of the new file is printed for the handoff.

Usage: python scripts/recovery_c300_cache_compact.py
"""
from __future__ import annotations

import hashlib
import json
import pickle
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd

CACHE = Path("data/cache")
SRC = CACHE / "campaign300_multianual_perp_funding_basis_ts_5m.pkl"
BACKUP_DIR = CACHE / "recovery"
BACKUP = BACKUP_DIR / "campaign300_multianual_perp_funding_basis_ts_5m.pkl.orig"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def compact_payload(obj: dict) -> tuple[dict, bool]:
    """Return (compacted_copy, changed)."""
    changed = False
    out = dict(obj)
    pa = out.get("per_asset")
    if not isinstance(pa, dict):
        return out, False
    new_pa = {}
    for sym, d in pa.items():
        if not isinstance(d, dict):
            new_pa[sym] = d
            continue
        nd = {}
        sym_changed = False
        for k, v in d.items():
            if isinstance(v, pd.Series):
                nd[k] = v.to_numpy()
                sym_changed = True
            elif isinstance(v, pd.DatetimeIndex):
                # np.asarray() on a DatetimeIndex yields an object array; force the
                # native microsecond unit so the payload stays compact and
                # np.isfinite/isnan work downstream.
                nd[k] = v.to_numpy(dtype="datetime64[us]")
                sym_changed = True
            elif isinstance(v, pd.DataFrame):
                nd[k] = v.to_numpy()
                sym_changed = True
            else:
                nd[k] = v
        new_pa[sym] = nd
        changed = changed or sym_changed
    out["per_asset"] = new_pa
    return out, changed


def main() -> int:
    if not SRC.exists():
        print(f"ERROR: missing {SRC}", file=sys.stderr)
        return 2
    size_mb = SRC.stat().st_size / 1e6
    print(f"source {SRC} = {size_mb:.2f} MB")

    with open(SRC, "rb") as f:
        original = pickle.load(f)

    compacted, changed = compact_payload(original)
    if not changed:
        print("no pandas legs found; nothing to do")
        return 0

    # Byte-level equality check on every converted leg.
    ok = True
    for sym, d in original.get("per_asset", {}).items():
        c = compacted["per_asset"][sym]
        for k, v in d.items():
            if isinstance(v, pd.Series):
                a = v.to_numpy()
            elif isinstance(v, pd.DatetimeIndex):
                a = v.to_numpy(dtype="datetime64[us]")
            else:
                continue
            b = c[k]
            # NaN-aware: spot_close/funding_rates carry the 462 un-imputed gap
            # bars as NaN.  equal_nan only works on floating dtypes.
            try:
                same = np.array_equal(a, b, equal_nan=True)
            except TypeError:
                same = np.array_equal(a, b)
            if not same:
                ok = False
                print(f"  MISMATCH {sym}.{k}", file=sys.stderr)
            else:
                print(f"  ok {sym}.{k}: {a.shape} {a.dtype}")
    if not ok:
        print("ERROR: converted legs differ from original; aborting", file=sys.stderr)
        return 1

    blob = pickle.dumps(compacted, protocol=4)
    new_mb = len(blob) / 1e6
    print(f"compacted in-memory pickle = {new_mb:.2f} MB")
    if new_mb > 100.0:
        print(
            f"ERROR: still {new_mb:.2f} MB, above the 100 MB push limit",
            file=sys.stderr,
        )
        return 1

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SRC, BACKUP)
    print(f"backup written {BACKUP} ({BACKUP.stat().st_size/1e6:.2f} MB)")

    with open(SRC, "wb") as f:
        f.write(blob)

    new_sha = sha256_file(SRC)
    print(f"new file sha256 = {new_sha}")
    print(f"new file size = {SRC.stat().st_size/1e6:.2f} MB")
    print("recovery_c300_cache_compact: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())