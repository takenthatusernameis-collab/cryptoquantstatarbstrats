#!/usr/bin/env python3
"""Vectorized recurrence-analysis helpers shared by C274/C275 hot loops.

These are byte-for-byte equivalent to the original pure-Python loop
implementations (verified by scripts/_vec_verify.py) but run ~100x faster
because the per-diagonal and per-pair loops are replaced with numpy ops.

Originals (verbatim reference):
  white_diag_segment_lengths_orig, medcouple_orig in
  scripts/_vec_verify.py
"""
from __future__ import annotations
import numpy as np


def white_diag_segment_lengths(rec: np.ndarray, w_min: int) -> list[int]:
    """Lengths of runs of 0-cells on off-diagonals (k != 0), length >= w_min."""
    n = rec.shape[0]
    segs: list[int] = []
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
        segs.extend((ends - starts)[(ends - starts) >= w_min].tolist())
    return segs


def medcouple(values: np.ndarray) -> float | None:
    """Brys-Hubert-Struyf medcouple, deterministic. Fail-closed on invalid."""
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
    h = np.where(
        denom > 0,
        ((xj - xm) - (xm - xi)) / np.where(denom > 0, denom, 1.0),
        0.0,
    )
    hvals = h.flatten()
    if hvals.size == 0:
        return None
    mc = float(np.median(hvals))
    if not np.isfinite(mc):
        return None
    return mc


def black_diag_segment_lengths(rec: np.ndarray, min_len: int = 1) -> list[int]:
    """Lengths of runs of non-zero cells on off-diagonals (k != 0), length >= min_len."""
    n = rec.shape[0]
    segs: list[int] = []
    for k in range(-(n - 1), n):
        if k == 0:
            continue
        diag = np.diag(rec, k=k)
        if diag.size == 0:
            continue
        d = np.concatenate([[0], diag, [0]]).astype(np.int8)
        diff = np.diff(d)
        starts = np.where(diff == 1)[0]
        ends = np.where(diff == -1)[0]
        segs.extend((ends - starts)[(ends - starts) >= min_len].tolist())
    return segs