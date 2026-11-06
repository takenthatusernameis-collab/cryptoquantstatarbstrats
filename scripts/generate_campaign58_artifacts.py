#!/usr/bin/env python3
"""Generate Campaign 58 artifacts (fail-closed, real data only).

Campaign 58 — Path R-B: a GENUINELY DIFFERENT pre-stated hypothesis on validated
real_quote_volume (Binance spot klines col 5), NOT a rerun of C23/C40–C57.

PRE-STATED HYPOTHESIS (fixed before seeing OOS results):
"Volume Permutation Entropy (Ordinal/Temporal Complexity) Shock Mean Reversion"

Mechanic (pre-stated):
- For each asset, compute rolling Bandt–Pompe normalized permutation entropy of
  quote volume over a causal window W=48h with embedding dimension m=3 and delay
  tau=1 (m! = 6 possible ordinal patterns). For each embedded vector
  v_i = (x_{i}, x_{i+tau}, ..., x_{i+(m-1)*tau}) within the window, map to its
  ordinal pattern (rank permutation, ties broken by index order = stable/left
  rank to remain deterministic and causal). Compute p_pi as the relative
  frequency of each ordinal pattern over all valid embeddings in the window.
  Normalized permutation entropy: PE_t = -sum(p_pi * log2(p_pi)) / log2(m!).
  PE_t in [0,1]: 1 ~ maximally complex/random ordinal dynamics; lower ~ more
  regular/predictable ordinal structure.
- z-score PE_t over ZLB=168h (causal) -> pe_z.
- Mean-revert ordinal-complexity shocks (fade extremes):
  pe_z >= ENTRY_Z (1.25) -> SHORT (abnormally complex/random volume ordering; fade);
  pe_z <= -ENTRY_Z (-1.25) -> LONG (abnormally regular/predictable ordering; fade);
  |pe_z| < ENTRY_Z -> no new entry.
- Exit when |pe_z| < EXIT_Z (0.25), hold >= MAX_HOLD (12h), or signal flips.
- Execution shift t -> t+1 (causal). WF rolling 720/168/168. Cost grid 0-40bps
  (fee,slip pairs). B&H benchmark on same WF windows.

Edge rule (pre-stated, fail-closed): oos_edge_proven=true IFF exposure>0 AND ALL
cost-grid slices OOS net>0 AND OOS net beats B&H on same WF windows. Else false.
No in-sample tuning, no threshold weakening, no fabricated data/proxies.

DIFFERS FROM C23/C40–C57 (genuinely different transform/mechanic):
- C57 = Shannon entropy of BINNED qvol VALUES (distributional uncertainty over
  magnitudes, quantile bins; ignores temporal/ordinal order). C58 = Bandt–Pompe
  PERMUTATION entropy of ordinal PATTERNS (temporal/sequence complexity from
  rank orderings of embedded vectors) — orthogonal to value-bin magnitude entropy.
- C51 = lag-1 autocorrelation (LINEAR temporal dependence at a single lag).
  C58 captures NONLINEAR/ORDINAL pattern complexity across an embedding (m=3,
  tau=1), not a single-lag linear moment.
- C48 = rolling STD (raw 2nd-moment). C49 = excess kurtosis (4th-moment).
  C50 = skewness (3rd-moment). C56 = CV = std/mean (relative dispersion ratio).
  C58 is an ordinal-pattern entropy, not any moment or moment ratio.
- C23/40/41/42 = vol_z of raw volume level/expansion. C43 = unsloped vol_z
  divergence at price extremes. C44 = vol_z ROC. C45 = Amihud |ret|/volume.
  C46 = OBV signed-cumulative slopes. C47 = up/down partition imbalance.
  C52 = contemporaneous corr(qvol,|ret|). C53 = signed lead corr(qvol,ret_{t+k}).
  C54 = contemporaneous OLS beta sensitivity (Cov/Var). C55 = lead
  corr(qvol,|ret_{t+k}|) on magnitude.
C58 uses Bandt–Pompe permutation entropy (ordinal/temporal complexity of the
sequence) — orthogonal to all value-bin entropies, moments, ratios, correlations,
betas, partitions, levels, and ROC statistics tested in C23/C40–C57.
"""
from __future__ import annotations

import hashlib
import json
import logging
import math
import pickle
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.real_feed_loader import validate_and_load_real_feed  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [campaign58] %(levelname)s %(message)s")
logger = logging.getLogger("campaign58")

CACHE_DIR = ROOT / "data" / "cache"
REPORTS = ROOT / "reports"
SPOT_CACHE = "0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7"
VOL_META = CACHE_DIR / "volume_1h_full.meta.json"
VOL_PROV = CACHE_DIR / "volume_1h_full.provenance.json"

W_PE = 48
M_EMB = 3
TAU = 1
ZLB = 168
ENTRY_Z = 1.25
EXIT_Z = 0.25
MAX_HOLD = 12
WF_TRAIN = 720
WF_TEST = 168
WF_STEP = 168
COST_GRID = [(0, 0), (5, 5), (10, 10), (20, 20)]


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_spot():
    pkl = CACHE_DIR / f"{SPOT_CACHE}.pkl"
    meta = json.loads((CACHE_DIR / f"{SPOT_CACHE}.meta.json").read_text(encoding="utf-8"))
    df = pickle.load(open(pkl, "rb"))
    return df, meta, sha256_file(pkl)


def load_volume_wide():
    if not VOL_PROV.exists():
        raise FileNotFoundError(f"volume provenance certificate missing: {VOL_PROV}")
    prov = json.loads(VOL_PROV.read_text(encoding="utf-8"))
    long_df, report = validate_and_load_real_feed(VOL_META, "real_quote_volume", provenance=prov)
    if not report.get("ok"):
        raise RuntimeError(f"volume feed failed validation: {report}")
    wide = long_df.pivot(index="timestamp_utc", columns="symbol", values="quote_volume_usdt").sort_index()
    wide.index = pd.to_datetime(wide.index, utc=True)
    return wide, report


def _pattern_index(vec: np.ndarray) -> int:
    # stable argsort (ties broken by index) -> ordinal ranks -> permutation index
    order = np.argsort(vec, kind="mergesort")
    ranks = np.empty_like(order)
    ranks[order] = np.arange(len(order))
    # map permutation tuple to a unique index via Lehmer-like base-factoradic
    idx = 0
    r = ranks.tolist()
    m = len(r)
    fact = 1
    for i in range(2, m):
        fact *= i
    for i in range(m):
        smaller = sum(1 for j in range(i + 1, m) if r[j] < r[i])
        idx += smaller * fact
        if m - 1 - i > 1:
            fact //= (m - 1 - i)
    return idx


def rolling_permutation_entropy(s: pd.Series, w: int, m: int, tau: int) -> pd.Series:
    arr = s.values.astype(float)
    out = np.full(len(arr), np.nan, dtype=float)
    m_fact = math.factorial(m)
    log_mf = math.log2(m_fact)
    emb_span = (m - 1) * tau + 1
    if w < emb_span:
        return pd.Series(out, index=s.index)
    for i in range(w - 1, len(arr)):
        win = arr[i - w + 1 : i + 1]
        if np.any(~np.isfinite(win)):
            continue
        n_emb = w - emb_span + 1
        counts = np.zeros(m_fact, dtype=float)
        for j in range(n_emb):
            vec = win[j : j + emb_span : tau]
            if len(vec) != m or np.any(~np.isfinite(vec)):
                continue
            counts[_pattern_index(vec)] += 1.0
        tot = counts.sum()
        if tot <= 0:
            continue
        p = counts[counts > 0] / tot
        h = -np.sum(p * np.log2(p))
        out[i] = h / log_mf if log_mf > 0 else np.nan
    return pd.Series(out, index=s.index)


def zscore(s: pd.Series, lb: int) -> pd.Series:
    m = s.rolling(lb, min_periods=lb).mean()
    sd = s.rolling(lb, min_periods=lb).std(ddof=0)
    return (s - m) / sd.replace(0, np.nan)


def simulate(ret1: pd.Series, sig: pd.Series, fee_bps: int, slip_bps: int) -> dict:
    n = len(ret1)
    cost = (fee_bps + slip_bps) / 10000.0
    pos = 0
    hold = 0
    trades = 0
    eq = 1.0
    exposure = 0
    for i in range(n - 1):
        z = sig.iloc[i]
        z_ok = not (pd.isna(z) or math.isinf(float(z)))
        r = float(ret1.iloc[i + 1])
        if math.isnan(r):
            r = 0.0
        target = pos
        if pos == 0:
            if z_ok and float(z) >= ENTRY_Z:
                target = -1
            elif z_ok and float(z) <= -ENTRY_Z:
                target = 1
        else:
            hold += 1
            flip = (pos == -1 and z_ok and float(z) <= -ENTRY_Z) or (pos == 1 and z_ok and float(z) >= ENTRY_Z)
            exit_sig = z_ok and abs(float(z)) < EXIT_Z
            if flip:
                target = 1 if pos == -1 else -1
            elif exit_sig or hold >= MAX_HOLD:
                target = 0
        if target != pos:
            eq *= (1.0 - cost)
            trades += 1
            hold = 0
        pos = target
        if pos != 0:
            exposure += 1
            eq *= (1.0 + pos * r)
    return {"total_return": eq - 1.0, "trades": trades, "exposure_frac": exposure / max(1, n - 1)}


def wf_oos(ret1: pd.Series, sig: pd.Series, fee_bps: int, slip_bps: int):
    n = len(ret1)
    out = []
    start = 0
    while True:
        te = start + WF_TRAIN
        tst_e = te + WF_TEST
        if tst_e > n:
            break
        out.append(simulate(ret1.iloc[te:tst_e].reset_index(drop=True), sig.iloc[te:tst_e].reset_index(drop=True), fee_bps, slip_bps))
        start += WF_STEP
    return out


def agg(slices):
    if not slices:
        return {"n": 0, "oos_net_sum": 0.0, "exposure": 0.0}
    rets = [s["total_return"] for s in slices]
    return {"n": len(slices), "oos_net_sum": float(np.prod([1 + r for r in rets]) - 1.0), "exposure": float(np.mean([s["exposure_frac"] for s in slices]))}


def main() -> None:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    spot_df, spot_meta, spot_sha = load_spot()
    vol_wide, vol_report = load_volume_wide()
    vol_symbols = sorted(vol_wide.columns.tolist())
    spot_symbols = list(spot_df.columns)
    assets = sorted([a for a in spot_symbols if a in vol_symbols])
    logger.info("spot_symbols=%s vol_symbols=%s tested_assets=%s", spot_symbols, vol_symbols, assets)

    by_asset = {}
    n_exposed = n_edge = 0
    for a in assets:
        close = pd.to_numeric(spot_df[a], errors="coerce")
        ret1 = close.pct_change()
        qv = pd.to_numeric(vol_wide[a], errors="coerce")
        common = close.index.intersection(qv.index)
        close, ret1, qv = close.reindex(common), ret1.reindex(common), qv.reindex(common)
        pe = rolling_permutation_entropy(qv, W_PE, M_EMB, TAU)
        pe_z = zscore(pe, ZLB)
        logger.info("asset=%s rows=%s", a, len(common))

        cost_slices = {}
        for fee, slip in COST_GRID:
            key = f"fee{fee}_slip{slip}_bps"
            sl = wf_oos(ret1, pe_z, fee, slip)
            ag = agg(sl)
            bh_sl = []
            n = len(ret1); st = 0
            while True:
                te = st + WF_TRAIN; tst_e = te + WF_TEST
                if tst_e > n: break
                rsl = ret1.iloc[te:tst_e].fillna(0.0)
                bh_sl.append({"total_return": float((1 + rsl).prod() - 1.0), "exposure_frac": 1.0})
                st += WF_STEP
            bh_net = agg(bh_sl)["oos_net_sum"] if bh_sl else 0.0
            cost_slices[key] = {"net_oos_sum": ag["oos_net_sum"], "bh_oos_sum": bh_net,
                                "oos_net_gt_zero": ag["oos_net_sum"] > 0, "oos_net_beat_bh": ag["oos_net_sum"] > bh_net,
                                "n_slices": ag["n"], "exposure": ag["exposure"]}
        exposure = cost_slices["fee0_slip0_bps"]["exposure"] > 0
        all_pos = all(v["oos_net_gt_zero"] for v in cost_slices.values())
        all_bh = all(v["oos_net_beat_bh"] for v in cost_slices.values())
        edge = exposure and all_pos and all_bh
        if exposure: n_exposed += 1
        if edge: n_edge += 1
        by_asset[a] = {"rows": len(common), "has_exposure": exposure, "oos_edge_proven": edge, "cost_slices": cost_slices}

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "campaign": 58,
        "title": "Volume Permutation Entropy (Ordinal/Temporal Complexity) Shock Mean Reversion — costed OOS (fail-closed, real quote volume)",
        "family": "volume_permutation_entropy_shock_mr",
        "path": "R-B (validated real_quote_volume; no new blocked-family feed)",
        "oos_edge_proven": n_edge > 0,
        "n_assets_tested": len(by_asset),
        "n_assets_with_exposure": n_exposed,
        "n_oos_edge_proven": n_edge,
        "pre_stated_hypothesis": (
            "PE_t = normalized Bandt–Pompe permutation entropy of qvol[t-W+1..t], W=48, embedding m=3, "
            "delay tau=1 (6 ordinal patterns, ties broken by index=stable; causal). PE_t=-sum(p*pi*log2)/log2(6). "
            "pe_z=zscore(PE_t,ZLB=168). Fade ordinal-complexity shocks: pe_z>=1.25 SHORT (complex/random), "
            "pe_z<=-1.25 LONG (regular/predictable), exit |pe_z|<0.25 or hold>=12 or flip. "
            "Exec t->t+1. WF 720/168/168. Cost grid 0-40bps. Edge iff exposure>0 AND all slices OOS net>0 AND >B&H. "
            "Genuinely different from C23/C40-C57 (ordinal/temporal sequence complexity)."
        ),
        "hypothesis_differs_from_c23_c40_c57": (
            "C58=Bandt–Pompe permutation entropy of ordinal PATTERNS (temporal/sequence complexity via rank "
            "orderings of embedded vectors, m=3 tau=1) — captures nonlinear/ordinal dynamics. "
            "C57=Shannon entropy of BINNED qvol VALUES (magnitude distributional uncertainty, ignores temporal order). "
            "C51=lag-1 autocorrelation (linear temporal dependence at single lag). C56=CV=std/mean. "
            "C48=STD 2nd-moment. C49=kurtosis 4th-moment. C50=skewness 3rd-moment. "
            "C23/40/41/42=vol_z level/expansion. C43=unsloped divergence; C44=ROC; C45=Amihud |ret|/vol; "
            "C46=OBV signed-cumulative; C47=up/down imbalance; C52=corr(qvol,|ret|); C53=signed lead corr(qvol,ret_{t+k}); "
            "C54=OLS beta sensitivity; C55=lead corr(qvol,|ret_{t+k}|) magnitude."
        ),
        "config": {
            "spot_cache": SPOT_CACHE, "spot_meta": spot_meta, "spot_sha256": spot_sha,
            "volume_meta": str(VOL_META.relative_to(ROOT)), "volume_provenance": str(VOL_PROV.relative_to(ROOT)),
            "volume_validation": vol_report, "w_pe": W_PE, "m_embedding": M_EMB, "tau": TAU, "zlb": ZLB,
            "entry_z": ENTRY_Z, "exit_z": EXIT_Z, "max_hold": MAX_HOLD,
            "wf": [WF_TRAIN, WF_TEST, WF_STEP], "cost_grid_bps_fee_slippage": COST_GRID,
        },
        "by_asset": by_asset,
    }
    out = REPORTS / f"real_quote_volume_permutation_entropy_shock_mr_costed_oos_{ts}.json"
    out.write_text(json.dumps(report, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"wrote": str(out), "oos_edge_proven": report["oos_edge_proven"], "n_edge": n_edge, "n_exposed": n_exposed, "n_assets": len(by_asset)}))


if __name__ == "__main__":
    main()
