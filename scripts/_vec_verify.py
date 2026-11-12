#!/usr/bin/env python3
"""Verify vectorized recurrence helpers produce IDENTICAL output to the original
Python-loop implementations in run_c275_rte_over_white_diag_medcouple_shock_mr_costed_oos.py
and run_c274_second_pearson_skew_param_sensitivity.py."""
from __future__ import annotations
import sys
import numpy as np
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))

# --- original implementations (copied verbatim from C275 script) ---
def white_diag_segment_lengths_orig(rec, w_min):
    n = rec.shape[0]; segs = []
    for k in range(-(n - 1), n):
        if k == 0:
            continue
        diag = np.diag(rec, k=k); count = 0
        for v in diag:
            if v == 0:
                count += 1
            else:
                if count >= w_min:
                    segs.append(count)
                count = 0
        if count >= w_min:
            segs.append(count)
    return segs

def _medcouple_kernel(xi, xj, m):
    denom = xj - xi
    if denom == 0.0:
        return 0.0
    return ((xj - m) - (m - xi)) / denom

def medcouple_orig(values):
    x = np.sort(np.asarray(values, dtype=float))
    n = len(x)
    if n < 3 or not np.all(np.isfinite(x)):
        return None
    if n % 2 == 1:
        mid = n // 2
        xm = float(x[mid])
        left = x[:mid + 1]
        right = x[mid:]
        hvals = []
        for xi in left:
            for xj in right:
                hvals.append(_medcouple_kernel(float(xi), float(xj), xm))
    else:
        xm = float(0.5 * (x[n // 2 - 1] + x[n // 2]))
        left = x[x <= xm]
        right = x[x >= xm]
        hvals = []
        for xi in left:
            for xj in right:
                hvals.append(_medcouple_kernel(float(xi), float(xj), xm))
    if not hvals:
        return None
    mc = float(np.median(np.asarray(hvals, dtype=float)))
    if not np.isfinite(mc):
        return None
    return mc

# --- vectorized implementations ---
def white_diag_segment_lengths_vec(rec, w_min):
    n = rec.shape[0]; segs = []
    for k in range(-(n - 1), n):
        if k == 0:
            continue
        diag = np.diag(rec, k=k)
        if diag.size == 0:
            continue
        d = np.concatenate([[1], diag, [1]]).astype(np.int8)
        diff = np.diff(d)
        starts = np.where(diff == -1)[0]
        ends = np.where(diff == 1)[0]
        lengths = ends - starts
        segs.extend(lengths[lengths >= w_min].tolist())
    return segs

def medcouple_vec(values):
    x = np.sort(np.asarray(values, dtype=float))
    n = len(x)
    if n < 3 or not np.all(np.isfinite(x)):
        return None
    if n % 2 == 1:
        mid = n // 2
        xm = float(x[mid])
        left = x[:mid + 1]
        right = x[mid:]
    else:
        xm = float(0.5 * (x[n // 2 - 1] + x[n // 2]))
        left = x[x <= xm]
        right = x[x >= xm]
    xi = left[:, None]
    xj = right[None, :]
    denom = xj - xi
    h = np.where(denom > 0, ((xj - xm) - (xm - xi)) / np.where(denom > 0, denom, 1.0), 0.0)
    hvals = h.flatten()
    if hvals.size == 0:
        return None
    mc = float(np.median(hvals))
    if not np.isfinite(mc):
        return None
    return mc

def main():
    rng = np.random.default_rng(42)
    all_ok = True
    # Test white_diag_segment_lengths on many random recurrence matrices
    for trial in range(200):
        n = rng.integers(5, 60)
        rec = rng.integers(0, 2, size=(n, n)).astype(np.uint8)
        w_min = int(rng.integers(1, 5))
        a = white_diag_segment_lengths_orig(rec, w_min)
        b = white_diag_segment_lengths_vec(rec, w_min)
        if a != b:
            print(f"MISMATCH segs trial {trial} n={n} w_min={w_min}: {a} vs {b}")
            all_ok = False
            break
    print("white_diag_segment_lengths:", "PASS" if all_ok else "FAIL")

    # Test medcouple on many random value sets (incl. even/odd, ties, negatives)
    mc_ok = True
    for trial in range(500):
        n = int(rng.integers(3, 80))
        x = rng.standard_normal(n) * rng.uniform(0.1, 5)
        # inject ties sometimes
        if trial % 3 == 0:
            x[:2] = x[1]
        a = medcouple_orig(x)
        b = medcouple_vec(x)
        if (a is None) != (b is None):
            print(f"MISMATCH mc None trial {trial}: {a} vs {b}")
            mc_ok = False
            break
        if a is not None and abs(a - b) > 1e-12:
            print(f"MISMATCH mc val trial {trial}: {a} vs {b}")
            mc_ok = False
            break
    print("medcouple:", "PASS" if mc_ok else "FAIL")

    # Edge cases
    assert medcouple_vec([1.0, 2.0]) is None
    assert medcouple_vec([1.0, 1.0, 1.0]) == 0.0
    assert white_diag_segment_lengths_vec(np.ones((3,3), dtype=np.uint8), 2) == []
    print("edge cases: PASS")

    sys.exit(0 if (all_ok and mc_ok) else 1)

if __name__ == '__main__':
    main()