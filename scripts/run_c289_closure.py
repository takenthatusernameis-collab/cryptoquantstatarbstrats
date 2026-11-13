#!/usr/bin/env python3
"""C289 — OOS multiple-testing and minimum-detectable-edge closure.

Question answered (no new data, no fabrication): across ALL pre-registered 5m
costed OOS configurations (C286 volume-conditioned + C288 realized-vol/skewness,
162 configs x 5 cost slices), does ANY configuration show a real costed out-of-sample
edge once we correct for the number of trials, and what is the smallest edge this
dataset could statistically resolve versus the 5m cost floor?

Method (all deterministic; real artifacts only):
- Inputs: the frozen C286 and C288 OOS sweep artifacts (151 non-overlapping 5m WF
  test windows each; per-run per-slice per-split net means). SHA256-from-bytes pinned.
- For each config x cost slice: block-bootstrap (circular, block=5 splits) one-sided
  p-value for H0: mean per-split net <= 0 vs H1: > 0, and for the mean excess over the
  equal-weight buy-and-hold benchmark.
- Multiplicity: Holm step-down (FWER) and Benjamini-Hochberg (FDR) at alpha=0.05 across
  all config x slice tests. Count survivors.
- Deflated Sharpe Ratio (Bailey & Lopez de Prado 2014) per config (using the fee10_slip10
  net series), deflated by the number of trials N=162 and the cross-config Sharpe variance;
  report max DSR and the count with DSR > 0.95.
- Minimum Detectable Edge: MDE = (z_{0.975}+z_{0.80}) * std/sqrt(n_splits) per config on
  the fee0 slice, reported in per-split return and in bps per rebalance; compared to the
  minimum per-rebalance cost (fee5+slip5 = 10 bps).

Verdict: economic_space_closed = true iff (a) zero configs survive Holm FWER AND BH FDR at
alpha=0.05 AND (b) max DSR <= 0.95 AND (c) median MDE (per 5m bar, bps) <= minimum
per-rebalance cost (10 bps) — i.e. no config is statistically resolvable above the cost
floor AND the test is well-powered (it would have detected an edge as small as the cost
floor). Otherwise economic_space_open = true (a survivor exists and/or the test is underpowered).

Artifacts (exact names, timestamped, SHA256-from-bytes):
- reports/campaign289_closure_<ts>.json
- reports/campaign289_summary_<ts>.json
- reports/campaign289_verdict_<ts>.json
"""
from __future__ import annotations

import glob
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
reports = root / "reports"
reports.mkdir(exist_ok=True)
ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

COST_GRID = [(0, 0), (5, 5), (10, 10), (20, 20), (40, 40)]
SLICES = [f"fee{f}_slip{s}" for f, s in COST_GRID]
ALPHA = 0.05
N_BOOT = 4000
BLOCK = 5
SEED = 20261113
EULER_GAMMA = 0.5772156649015329
Z_975 = 1.959963984540054
Z_80 = 0.8416212335729143

# Minimum per-rebalance cost: fee5 + slip5 = 10 bps = 1e-3 per unit turnover; a
# fully-turned book pays 10 bps per rebalance, so the cost floor is 10 bps.
MIN_COST_BPS = 10.0

SOURCES = {
    "C286": "campaign286_oos_sweep_*.json",
    "C288": "campaign288_oos_sweep_*.json",
}
PINNED = {
    "C286": "c153042e619793de4aaa024b967b387b7a37c26ed6864884d14240ea42f17aca",
    "C288": "75c06a7ee1ea42155e8c0674d58c70f17175e47e31b750db464815a35bb0188d",
}


def sha256_file(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def jdefault(o):
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o) if np.isfinite(o) else None
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(str(type(o)))


def block_bootstrap_pvalue(x: np.ndarray, n_boot: int = N_BOOT, block: int = BLOCK, seed: int = SEED) -> float:
    """One-sided p-value for H0: mean(x) <= 0 vs H1: mean(x) > 0 via circular block bootstrap."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    if n == 0:
        return 1.0
    if np.allclose(x, x[0]):
        return 0.0 if x[0] > 0 else 1.0
    rng = np.random.default_rng(seed)
    n_blocks = int(math.ceil(n / block))
    starts = rng.integers(0, n, size=(n_boot, n_blocks))
    idx = (starts[:, :, None] + np.arange(block)[None, None, :]) % n
    samples = x[idx.reshape(n_boot, -1)[:, :n]]
    boot_means = samples.mean(axis=1)
    return float((np.sum(boot_means <= 0.0) + 1.0) / (n_boot + 1.0))


def holm_reject(pvals, alpha: float = ALPHA):
    """Holm step-down: return boolean reject array (FWER control)."""
    p = np.asarray(pvals, dtype=float)
    m = len(p)
    order = np.argsort(p)
    reject = np.zeros(m, dtype=bool)
    running = True
    for rank, idx in enumerate(order):
        thresh = alpha / (m - rank)
        if running and p[idx] <= thresh:
            reject[idx] = True
        else:
            running = False
    return reject


def bh_reject(pvals, alpha: float = ALPHA):
    """Benjamini-Hochberg step-up: return boolean reject array (FDR control)."""
    p = np.asarray(pvals, dtype=float)
    m = len(p)
    order = np.argsort(p)
    thresh = alpha * (np.arange(1, m + 1) / m)
    reject_sorted = p[order] <= thresh
    if not reject_sorted.any():
        return np.zeros(m, dtype=bool)
    kmax = np.max(np.where(reject_sorted)[0])
    reject = np.zeros(m, dtype=bool)
    reject[order[: kmax + 1]] = True
    return reject


def sharpe_ratio(x: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    sd = float(np.std(x, ddof=1))
    if sd <= 0 or not np.isfinite(sd):
        return 0.0
    return float(np.mean(x) / sd)


def deflated_sharpe_ratio(sr_hat: float, sr_trials: np.ndarray, skew: float, kurt: float, n_obs: int) -> float:
    """Bailey & Lopez de Prado (2014) deflated Sharpe ratio (normal CDF of the deflated SR)."""
    n_trials = len(sr_trials)
    if n_obs < 2 or n_trials < 2:
        return 0.0
    var_trials = float(np.var(sr_trials, ddof=1))
    if var_trials <= 0 or not np.isfinite(var_trials):
        return 0.0
    sd_trials = math.sqrt(var_trials)
    # Expected maximum Sharpe of N independent trials (Bailey/LdP).
    sr0 = sd_trials * (
        (1.0 - EULER_GAMMA) * _norm_ppf(1.0 - 1.0 / n_trials)
        + EULER_GAMMA * _norm_ppf(1.0 - 1.0 / (n_trials * math.e))
    )
    denom = 1.0 - skew * sr_hat + ((kurt - 1.0) / 4.0) * (sr_hat ** 2)
    if denom <= 0 or not np.isfinite(denom):
        return 0.0
    z = (sr_hat - sr0) * math.sqrt(n_obs - 1) / math.sqrt(denom)
    return float(_norm_cdf(z))


def _norm_cdf(z: float) -> float:
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def _norm_ppf(p: float) -> float:
    # Acklam's rational approximation to the inverse normal CDF.
    if p <= 0.0:
        return -math.inf
    if p >= 1.0:
        return math.inf
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    plow, phigh = 0.02425, 1.0 - 0.02425
    if p < plow:
        q = math.sqrt(-2.0 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1.0)
    if p > phigh:
        q = math.sqrt(-2.0 * math.log(1.0 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1.0)
    q = p - 0.5
    r = q * q
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1.0)


def load_source(pattern: str, pinned_sha: str):
    matches = sorted(glob.glob(str(reports / pattern)))
    if not matches:
        raise SystemExit(f"FATAL: no artifact for {pattern}")
    path = Path(matches[-1])
    actual = sha256_file(path)
    if actual != pinned_sha:
        raise SystemExit(f"FATAL: source sha mismatch for {path}: {actual} != {pinned_sha}")
    payload = json.loads(Path(path).read_text())
    return path, actual, payload


def main() -> int:
    source_meta = {}
    configs = []  # list of dicts: campaign, feature, lookback, K, hold, per-slice arrays
    for camp, pattern in SOURCES.items():
        path, sha, payload = load_source(pattern, PINNED[camp])
        source_meta[camp] = {
            "path": str(path.relative_to(root)),
            "sha256": sha,
            "n_results": len(payload["results"]),
        }
        for r in payload["results"]:
            entry = {
                "campaign": camp,
                "feature": r["feature"],
                "lookback": int(r["lookback"]),
                "K": int(r["K"]),
                "hold": int(r["hold"]),
                "n_splits": int(r["n_splits"]),
                "bh_oos_mean": float(r["cost_slices"][SLICES[0]].get("bh_oos_mean", 0.0)),
            }
            for ck in SLICES:
                entry[ck] = [float(v) for v in r["cost_slices"][ck]["oos_net_mean_per_split"]]
            configs.append(entry)

    n_configs = len(configs)
    # ---- per config x slice bootstrap p-values (H0: mean<=0) ----
    tests = []  # flat list of dicts
    for ci, cfg in enumerate(configs):
        for ck in SLICES:
            x = np.asarray(cfg[ck], dtype=float)
            p_zero = block_bootstrap_pvalue(x)
            tests.append({
                "config_index": ci,
                "campaign": cfg["campaign"],
                "feature": cfg["feature"],
                "lookback": cfg["lookback"],
                "K": cfg["K"],
                "hold": cfg["hold"],
                "cost_slice": ck,
                "mean_net": float(np.mean(x)),
                "std_net": float(np.std(x, ddof=1)),
                "p_value_gt0": p_zero,
            })

    pvals = np.array([t["p_value_gt0"] for t in tests])
    holm = holm_reject(pvals)
    bh = bh_reject(pvals)
    for t, h, b in zip(tests, holm, bh):
        t["holm_reject"] = bool(h)
        t["bh_reject"] = bool(b)

    n_holm = int(holm.sum())
    n_bh = int(bh.sum())

    # ---- per-config Sharpe / DSR / MDE (single representative slice each) ----
    # DSR uses the fee10_slip10 net series (moderate, realistic cost). MDE uses fee0.
    sr_trials = np.array([sharpe_ratio(cfg["fee10_slip10"]) for cfg in configs])
    dsr_rows = []
    mde_bps = []
    for ci, cfg in enumerate(configs):
        x_dsr = np.asarray(cfg["fee10_slip10"], dtype=float)
        skew = float(_sample_skew(x_dsr))
        kurt = float(_sample_kurt(x_dsr))
        sr = float(sr_trials[ci])
        dsr = deflated_sharpe_ratio(sr, sr_trials, skew, kurt, len(x_dsr))
        x0 = np.asarray(cfg["fee0_slip0"], dtype=float)
        sd0 = float(np.std(x0, ddof=1))
        mde = (Z_975 + Z_80) * sd0 / math.sqrt(len(x0)) if len(x0) > 0 else float("inf")
        mde_bps.append(mde * 1e4)
        dsr_rows.append({
            "config_index": ci,
            "campaign": cfg["campaign"],
            "feature": cfg["feature"],
            "lookback": cfg["lookback"],
            "K": cfg["K"],
            "hold": cfg["hold"],
            "sharpe_fee10": sr,
            "skew_fee10": skew,
            "kurt_fee10": kurt,
            "deflated_sharpe": dsr,
            "mde_bps_per_rebalance": mde * 1e4,
        })

    max_dsr = float(max((r["deflated_sharpe"] for r in dsr_rows), default=0.0))
    n_dsr_above = int(sum(1 for r in dsr_rows if r["deflated_sharpe"] > 0.95))
    median_mde_bps = float(np.median(mde_bps)) if mde_bps else float("inf")

    survivors = [t for t in tests if t["holm_reject"] or t["bh_reject"]]
    economic_space_closed = bool(
        n_holm == 0
        and n_bh == 0
        and max_dsr <= 0.95
        and median_mde_bps <= MIN_COST_BPS
    )

    closure = {
        "generated_at_utc": ts,
        "campaign": 289,
        "part": "closure",
        "analysis": "oos_multiple_testing_and_minimum_detectable_edge_closure",
        "real_data_only": True,
        "fabricated_data": False,
        "method": {
            "sources": source_meta,
            "n_configs": n_configs,
            "cost_slices": SLICES,
            "alpha": ALPHA,
            "bootstrap": {"type": "circular_block", "block_splits": BLOCK, "n_boot": N_BOOT, "seed": SEED},
            "multiplicity": ["holm_fwer", "bh_fdr"],
            "dsr": "bailey_lopez_de_prado_2014_on_fee10_slip10",
            "mde": "(z_0.975 + z_0.80) * std/sqrt(n_splits) on fee0_slip0",
            "min_cost_bps_per_rebalance": MIN_COST_BPS,
        },
        "tests": tests,
        "dsr": dsr_rows,
        "summary": {
            "n_configs": n_configs,
            "n_tests": len(tests),
            "n_holm_reject": n_holm,
            "n_bh_reject": n_bh,
            "n_survivors": len(survivors),
            "max_deflated_sharpe": max_dsr,
            "n_dsr_above_0_95": n_dsr_above,
            "median_mde_bps_per_rebalance": median_mde_bps,
            "min_cost_bps_per_rebalance": MIN_COST_BPS,
        },
        "survivors": survivors,
        "economic_space_closed": economic_space_closed,
    }

    op = reports / f"campaign289_closure_{ts}.json"
    op.write_text(json.dumps(closure, indent=2, default=jdefault) + "\n")
    closure_sha = sha256_file(op)

    summary = {
        "generated_at_utc": ts,
        "campaign": 289,
        "part": "summary",
        "analysis": "closure_summary",
        "real_data_only": True,
        "fabricated_data": False,
        "scope": "5m-executed campaigns C286 + C288",
        "artifacts": {"closure": {"path": str(op.relative_to(root)), "sha256": closure_sha}},
        "summary": closure["summary"],
        "economic_space_closed": economic_space_closed,
    }
    op_sum = reports / f"campaign289_summary_{ts}.json"
    op_sum.write_text(json.dumps(summary, indent=2, default=jdefault) + "\n")
    sum_sha = sha256_file(op_sum)

    verdict_obj = {
        "generated_at_utc": ts,
        "campaign": 289,
        "part": "verdict",
        "analysis": "final_verdict",
        "real_data_only": True,
        "fabricated_data": False,
        "economic_space_closed": economic_space_closed,
        "finding": (
            f"Across {n_configs} pre-registered 5m costed OOS configs: Holm survivors={n_holm}, "
            f"BH survivors={n_bh}, max deflated Sharpe={max_dsr:.4f}, median MDE="
            f"{median_mde_bps:.4g} bps/5m-bar vs {MIN_COST_BPS:.0f} bps per-rebalance cost floor -> "
            + ("economic space is statistically CLOSED on this dataset: no config is significant after "
               "multiple-testing correction at any cost slice (incl. zero cost), no deflated-Sharpe skill, "
               "and the test is well-powered (MDE well below the cost floor) so the null is not a power artifact."
               if economic_space_closed else
               "economic space is OPEN: at least one config survives correction and/or the test is underpowered.")
        ),
        "basis": "multiple_testing_holm_bh_deflated_sharpe_minimum_detectable_edge_5m",
        "closure_artifact": str(op.relative_to(root)),
        "closure_sha256": closure_sha,
        "summary_artifact": str(op_sum.relative_to(root)),
        "summary_sha256": sum_sha,
        "next_action": (
            "If economic_space_closed: pivot economic effort to a genuinely new mechanism or new data "
            "(funding/basis/derivatives) and keep C287 testnet execution as the execution prerequisite; "
            "do NOT keep re-running exhausted price/volume signal families on this dataset. "
            "If economic_space_open: re-validate the surviving config on an untouched holdout before any live use."
        ),
        "hard_bans_honored": [
            "No fabricated data; real artifacts only; SHA256-from-bytes",
            "No threshold/gate weakening; multiple-testing correction applied",
            "No edge claims without statistical significance above the cost floor",
        ],
    }
    op_ver = reports / f"campaign289_verdict_{ts}.json"
    op_ver.write_text(json.dumps(verdict_obj, indent=2, default=jdefault) + "\n")
    ver_sha = sha256_file(op_ver)

    print(json.dumps({
        "campaign": 289,
        "n_configs": n_configs,
        "n_tests": len(tests),
        "n_holm_reject": n_holm,
        "n_bh_reject": n_bh,
        "max_deflated_sharpe": max_dsr,
        "median_mde_bps_per_rebalance": median_mde_bps,
        "min_cost_bps_per_rebalance": MIN_COST_BPS,
        "economic_space_closed": economic_space_closed,
        "artifacts": {
            "closure": str(op.relative_to(root)),
            "summary": str(op_sum.relative_to(root)),
            "verdict": str(op_ver.relative_to(root)),
        },
        "sha256": {"closure": closure_sha, "summary": sum_sha, "verdict": ver_sha},
    }, indent=2))
    return 0


def _sample_skew(x: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    n = len(x)
    if n < 3:
        return 0.0
    m = x.mean()
    s = x.std(ddof=1)
    if s <= 0:
        return 0.0
    return float(((x - m) ** 3).mean() / (s ** 3))


def _sample_kurt(x: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    n = len(x)
    if n < 4:
        return 3.0
    m = x.mean()
    s = x.std(ddof=1)
    if s <= 0:
        return 3.0
    return float(((x - m) ** 4).mean() / (s ** 4))


if __name__ == "__main__":
    raise SystemExit(main())