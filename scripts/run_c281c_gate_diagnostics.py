#!/usr/bin/env python3
"""C281C — why-no-edge gate diagnostics on the refreshed real spot cache.

Explanatory only. This never claims an edge and never weakens a gate. It
re-runs the same fail-closed cointegration-pairs diagnostics that C281B used
(strict enriched gates, no cached/static diagnostics) and reports the per-gate
pass share at each causal refresh bar, so the binding constraint can be
localized.

Single-asset strategies (MeanReversion/Momentum) build their enriched
diagnostics from a static all-True table (strategies/mean_reversion.py,
strategies/momentum.py), so there is nothing to localize there; this is
recorded explicitly rather than misreported as a real gate evaluation.

Artifacts:
    campaign281c_gate_diagnostics_<ts>.json
    campaign281c_summary_<ts>.json
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
reports = root / "reports"
reports.mkdir(exist_ok=True)
cache_dir = root / "data" / "cache"
ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

NEW_CACHE = cache_dir / "26736ab8fbb16974dd59f123855ab7e4810026d12712a05a363eabacd814ade2.pkl"
NEW_CACHE_META = NEW_CACHE.with_suffix(".meta.json")
NEW_CACHE_SHA_EXPECTED = "9355aed62b00a56b46ebba70eec4f9855620e8fea1b6eeae417ec6d7dea349df"
PORTFOLIO = root / "reports" / "portfolio_real.json"

TRAIN, TEST, STEP = 720, 168, 168
PAIR_LOOKBACKS = (240, 480, 720)
GATE_NAMES = (
    "eg_pass",
    "johansen_pass",
    "spread_mr_pass",
    "hl_bounds_pass",
    "leg_stationarity_ok",
    "rolling_stable_ok",
    "no_structural_break",
)


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def jdefault(o):
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o) if np.isfinite(o) else None
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, pd.Timestamp):
        return str(o)
    raise TypeError(str(type(o)))


def load_spot(path: Path) -> pd.DataFrame:
    with open(path, "rb") as f:
        df = pd.read_pickle(f)
    if isinstance(df, pd.Series):
        df = df.to_frame()
    return df.astype(float).sort_index()


def main():
    if not NEW_CACHE.exists() or not NEW_CACHE_META.exists():
        raise SystemExit("FATAL: C281A cache/meta missing")
    cache_sha = sha256_file(NEW_CACHE)
    if cache_sha != NEW_CACHE_SHA_EXPECTED:
        raise SystemExit(f"FATAL: cache sha256 mismatch {cache_sha}")

    df = load_spot(NEW_CACHE)
    portfolio = json.loads(PORTFOLIO.read_text())
    pairs = [tuple(p) for p in portfolio.get("pairs", [])]

    from strategies.pairs_trading import CointegrationPairsStrategy

    per_eval = []
    for a, b in pairs:
        pair_df = df[[a, b]].dropna()
        nn = len(pair_df)
        if nn < TRAIN + TEST + 10:
            per_eval.append({"pair": f"{a}/{b}", "status": "insufficient_data", "bars": int(nn)})
            continue
        for lookback in PAIR_LOOKBACKS:
            strategy = CointegrationPairsStrategy(
                pair=(a, b),
                lookback=lookback,
                entry_threshold=2.0,
                exit_threshold=0.5,
                cointegration_pvalue=0.05,
                cointegration_check_interval=lookback,
                use_enriched_gates=True,
                strict_enriched_gates=True,
            )
            strategy.generate_signals(pair_df)
            bd = strategy._gate_breakdown
            if bd is None:
                per_eval.append({
                    "pair": f"{a}/{b}",
                    "lookback": int(lookback),
                    "bars": int(nn),
                    "status": "no_breakdown_captured",
                })
                continue

            # Causal refresh bars are exactly where the strategy recomputed
            # diagnostics (every cointegration_check_interval bars from
            # lookback-1). Non-refresh rows are never written by the strategy,
            # so read only the refresh rows.
            refresh_idx = list(range(lookback - 1, nn, lookback))
            rows = bd.iloc[refresh_idx]
            n_eval = int(len(rows))
            gate_pass = {}
            for g in GATE_NAMES:
                if g not in rows.columns:
                    gate_pass[g] = {"pass": 0, "n": n_eval, "pass_share": None}
                    continue
                p = int(rows[g].fillna(False).astype(bool).sum())
                gate_pass[g] = {
                    "pass": p,
                    "n": n_eval,
                    "pass_share": (p / n_eval) if n_eval else None,
                }
            if "all_pass" in rows.columns:
                ap = int(rows["all_pass"].fillna(False).astype(bool).sum())
            else:
                ap = 0
            all_pass_share = (ap / n_eval) if n_eval else None
            binding = min(
                (g for g in GATE_NAMES if gate_pass[g]["pass_share"] is not None),
                key=lambda g: gate_pass[g]["pass_share"],
                default=None,
            )
            per_eval.append({
                "pair": f"{a}/{b}",
                "lookback": int(lookback),
                "bars": int(nn),
                "n_refresh_evaluations": n_eval,
                "status": "ok",
                "gate_pass": gate_pass,
                "all_pass": {"pass": ap, "n": n_eval, "pass_share": all_pass_share},
                "binding_gate": binding,
            })

    # Pooled per-gate pass share across all causal refresh evaluations.
    pooled = {}
    for g in GATE_NAMES:
        num = 0
        den = 0
        for e in per_eval:
            if e.get("status") != "ok":
                continue
            gp = e["gate_pass"][g]
            num += gp["pass"]
            den += gp["n"]
        pooled[g] = {"pass": num, "n": den, "pass_share": (num / den) if den else None}

    ranked = sorted(
        (g for g in GATE_NAMES if pooled[g]["pass_share"] is not None),
        key=lambda g: pooled[g]["pass_share"],
    )
    binding_overall = ranked[0] if ranked else None

    payload = {
        "generated_at_utc": ts,
        "campaign": 281,
        "part": "C_gate_diagnostics",
        "analysis": "why_no_edge_gate_pass_share",
        "explanatory_only": True,
        "edge_claim": "NONE",
        "weakens_gates": False,
        "real_data_only": True,
        "fabricated_data": False,
        "dataset": {
            "path": str(NEW_CACHE.relative_to(root)),
            "sha256": cache_sha,
            "bars": int(len(df)),
            "window": {"start": str(df.index.min()), "end": str(df.index.max())},
        },
        "protocol": {
            "strict_enriched_gates": True,
            "use_enriched_gates": True,
            "no_pair_diagnostics_file": True,
            "no_enriched_diagnostics": True,
            "cointegration_pvalue": 0.05,
            "cointegration_check_interval": "= lookback (causal refresh)",
            "refresh_bar_definition": "range(lookback-1, n, lookback)",
        },
        "single_asset_note": (
            "MeanReversionStrategy._build_diagnostics and MomentumStrategy._build_diagnostics "
            "return a static all-True gate table, so single-asset enriched gates are not a "
            "per-bar diagnostic and are excluded from the breakdown rather than misreported."
        ),
        "per_evaluation": per_eval,
        "pooled_gate_pass_share": pooled,
        "binding_gate_overall": binding_overall,
        "interpretation": (
            f"Lowest pooled pass share is '{binding_overall}' "
            f"({pooled[binding_overall]['pass_share']:.4f}) — this is the binding constraint "
            "that most often blocks pair entries under strict fail-closed gates. "
            "This localizes the cause only; it is not an edge and must not be used to weaken gates."
            if binding_overall
            else "No evaluable pair refresh bars."
        ),
    }

    op = reports / f"campaign281c_gate_diagnostics_{ts}.json"
    op.write_text(json.dumps(payload, indent=2, default=jdefault) + "\n")
    op_sha = sha256_file(op)

    summary = {
        "generated_at_utc": ts,
        "campaign": 281,
        "part": "C_summary",
        "analysis": "gate_diagnostics_summary",
        "explanatory_only": True,
        "edge_claim": "NONE",
        "n_pair_evaluations": sum(1 for e in per_eval if e.get("status") == "ok"),
        "n_pair_evaluations_total": len(per_eval),
        "pooled_gate_pass_share": pooled,
        "binding_gate_overall": binding_overall,
        "artifacts": {
            "gate_diagnostics": {"path": str(op.relative_to(root)), "sha256": op_sha},
        },
        "next_action": (
            "Diagnosis complete. C282 must test a materially different, pre-registered hypothesis "
            "on the same real data; do not weaken gates and do not re-run C281B/C281C."
        ),
    }
    op_sum = reports / f"campaign281c_summary_{ts}.json"
    op_sum.write_text(json.dumps(summary, indent=2, default=jdefault) + "\n")
    sum_sha = sha256_file(op_sum)

    print(json.dumps({
        "campaign": 281,
        "part": "C",
        "n_pair_evaluations": summary["n_pair_evaluations"],
        "binding_gate_overall": binding_overall,
        "pooled_gate_pass_share": pooled,
        "artifacts": {
            "gate_diagnostics": str(op.relative_to(root)),
            "summary": str(op_sum.relative_to(root)),
        },
        "sha256": {"gate_diagnostics": op_sha, "summary": sum_sha},
    }, indent=2))


if __name__ == "__main__":
    main()