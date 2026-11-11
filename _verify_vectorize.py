#!/usr/bin/env python3
"""Verify vectorized recurrence + pair computation produce IDENTICAL results to the
loop-based reference implementation in the C266 runner script."""
import numpy as np

np.random.seed(0)


def qualifying_white_diag_segments(diag, w_min):
    segs = []
    run = 0
    for val in diag:
        if int(val) == 0:
            run += 1
        else:
            if run >= w_min:
                segs.append(run)
            run = 0
    if run >= w_min:
        segs.append(run)
    return segs


def white_diag_r_mad_loop(R, w_min):
    M_pts = R.shape[0]
    seg_lengths = []
    for k in range(-(M_pts - 1), M_pts):
        if k == 0:
            continue
        diag = np.diag(R, k=k)
        segs = qualifying_white_diag_segments(diag, w_min)
        if segs:
            seg_lengths.extend(int(s) for s in segs)
    if len(seg_lengths) < 3:
        return np.nan
    arr = np.array(seg_lengths, dtype=float)
    if not np.all(np.isfinite(arr)) or not np.all(arr > 0):
        return np.nan
    mean_l = float(np.mean(arr))
    if not np.isfinite(mean_l) or mean_l <= 0:
        return np.nan
    n = len(arr)
    s = 0.0
    for i in range(n):
        for j in range(i + 1, n):
            s += abs(arr[i] - arr[j])
    mad_rel = s / (n * (n - 1) / 2.0) / (2.0 * mean_l)
    if not np.isfinite(mad_rel) or mad_rel <= 0 or mad_rel < 0:
        return np.nan
    return float(mad_rel)


def white_diag_r_mad_vec(R, w_min):
    M_pts = R.shape[0]
    seg_lengths = []
    for k in range(-(M_pts - 1), M_pts):
        if k == 0:
            continue
        diag = np.diag(R, k=k)
        segs = qualifying_white_diag_segments(diag, w_min)
        if segs:
            seg_lengths.extend(int(s) for s in segs)
    if len(seg_lengths) < 3:
        return np.nan
    arr = np.array(seg_lengths, dtype=float)
    if not np.all(np.isfinite(arr)) or not np.all(arr > 0):
        return np.nan
    mean_l = float(np.mean(arr))
    if not np.isfinite(mean_l) or mean_l <= 0:
        return np.nan
    n = len(arr)
    # vectorized: sum of |a-b| over unordered pairs = sum of upper triangle
    diff = np.abs(arr[:, None] - arr[None, :])
    s = float(diff.sum()) / 2.0
    mad_rel = s / (n * (n - 1) / 2.0) / (2.0 * mean_l)
    if not np.isfinite(mad_rel) or mad_rel <= 0 or mad_rel < 0:
        return np.nan
    return float(mad_rel)


def recurrence_loop(X, eps):
    R = np.zeros((X.shape[0], X.shape[0]), dtype=float)
    for i in range(X.shape[0]):
        di = np.max(np.abs(X - X[i:i + 1]), axis=1)
        R[i] = (di <= eps + 1e-18).astype(float)
    return R


def recurrence_vec(X, eps):
    # L_inf distance matrix via broadcast: shape (m, m, d) -> max over d
    d = np.max(np.abs(X[:, None, :] - X[None, :, :]), axis=2)
    return (d <= eps + 1e-18).astype(float)


# Test recurrence equivalence across many random windows
for trial in range(200):
    m = np.random.randint(5, 200)
    d = np.random.randint(1, 5)
    X = np.random.randn(m, d)
    eps = np.random.uniform(0.1, 2.0)
    Rl = recurrence_loop(X, eps)
    Rv = recurrence_vec(X, eps)
    if not np.array_equal(Rl, Rv):
        print("RECURRENCE MISMATCH", trial, m, d, eps)
        raise SystemExit(1)
    # also test feature equivalence
    fl = white_diag_r_mad_loop(Rl, 2)
    fv = white_diag_r_mad_vec(Rv, 2)
    if (np.isnan(fl) and np.isnan(fv)) or abs(fl - fv) < 1e-15:
        continue
    print("FEATURE MISMATCH", trial, fl, fv)
    raise SystemExit(1)

print("ALL EQUIVALENT: recurrence + R_MAD vectorization is result-preserving")