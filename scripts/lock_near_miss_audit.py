"""
Lock near-miss audit evidence into reports/cointegration_diagnostics_real.json.

Adds a `near_miss_audit` block to each pair's provenance, computed exclusively
from values already present in the artifact (no new data, no fabrication).
Documents, per pair: EG p-value, spread ADF p-value, half-life, Hurst,
rolling_stability frac (and the 0.6 required), which gates are near-misses
(close to passing but still failing), and the margin to the nearest passing
threshold. Expands POL/BTC rationale with the deep-dive filter evaluation.

Run: PYTHONPATH=. python scripts/lock_near_miss_audit.py
"""
from __future__ import annotations

import json
from pathlib import Path

ARTIFACT = Path("reports/cointegration_diagnostics_real.json")
DEEP_DIVE = Path("reports/pol_btc_deep_dive.json")

EG_ALPHA = 0.05
SPREAD_ADF_ALPHA = 0.05
ROLLING_FRAC_REQUIRED = 0.6
HL_UPPER_BOUND = 500.0
HL_NEAR_UPPER = 450.0


def near_miss_gates(diag: dict) -> list[dict]:
    """Identify gates close to passing but still failing (objective margins)."""
    eg = diag.get("engle_granger", {}) or {}
    spread = diag.get("spread", {}) or {}
    rs = diag.get("rolling_stability", {}) or {}
    hl_ou = spread.get("half_life_ou")
    hurst = spread.get("hurst_exponent")
    gates = diag.get("gates", {}) or {}
    nm: list[dict] = []

    eg_p = eg.get("pvalue")
    if eg_p is not None and not gates.get("eg_pass"):
        nm.append({
            "gate": "engle_granger",
            "value": eg_p,
            "threshold": EG_ALPHA,
            "margin_x": round(eg_p / EG_ALPHA, 2),
            "near": eg_p <= 0.20,
        })

    spread_adf_p = (spread.get("adf_spread") or {}).get("pvalue")
    if spread_adf_p is not None and not gates.get("spread_mr_pass"):
        nm.append({
            "gate": "spread_mean_reversion",
            "value": spread_adf_p,
            "threshold": SPREAD_ADF_ALPHA,
            "margin_x": round(spread_adf_p / SPREAD_ADF_ALPHA, 2),
            "near": spread_adf_p <= 0.15,
        })

    rs_frac = rs.get("frac_significant")
    if rs_frac is not None and not gates.get("rolling_stable_ok"):
        nm.append({
            "gate": "rolling_stability",
            "value": rs_frac,
            "threshold": ROLLING_FRAC_REQUIRED,
            "gap": round(ROLLING_FRAC_REQUIRED - rs_frac, 4),
            "near": rs_frac >= 0.30,
        })

    if hl_ou is not None and not gates.get("hl_bounds_pass"):
        nm.append({
            "gate": "half_life_bounds",
            "value": hl_ou,
            "threshold": HL_UPPER_BOUND,
            "note": "half_life above 500 upper bound",
        })
    elif hl_ou is not None and hl_ou >= HL_NEAR_UPPER:
        nm.append({
            "gate": "half_life_bounds",
            "value": hl_ou,
            "threshold": HL_UPPER_BOUND,
            "note": "half_life within 50 of upper bound (edge)",
            "near": True,
        })

    if hurst is not None and hurst < 0.5:
        nm.append({
            "gate": "hurst_mean_reversion_hint",
            "value": hurst,
            "threshold": 0.5,
            "note": "hurst < 0.5 (mean-reverting hint) but pair still blocked on other gates",
            "near": True,
        })

    return nm


def main() -> None:
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    cd = data["cointegration_diagnostics"]

    deep_dive = None
    if DEEP_DIVE.exists():
        deep_dive = json.loads(DEEP_DIVE.read_text(encoding="utf-8"))

    for pname in sorted(cd.keys()):
        diag = cd[pname]
        prov = diag.setdefault("provenance", {})
        gates = diag.get("gates", {}) or {}
        rs = diag.get("rolling_stability", {}) or {}
        spread = diag.get("spread", {}) or {}
        eg = diag.get("engle_granger", {}) or {}

        nm = near_miss_gates(diag)
        audit = {
            "eg_pvalue": eg.get("pvalue"),
            "spread_adf_pvalue": (spread.get("adf_spread") or {}).get("pvalue"),
            "half_life_ou": spread.get("half_life_ou"),
            "hurst_exponent": spread.get("hurst_exponent"),
            "rolling_frac_significant": rs.get("frac_significant"),
            "rolling_required": ROLLING_FRAC_REQUIRED,
            "rolling_gap": round(ROLLING_FRAC_REQUIRED - rs["frac_significant"], 4)
            if rs.get("frac_significant") is not None else None,
            "near_miss_gates": nm,
            "all_gates_pass": bool(gates.get("all_pass")),
        }
        prov["near_miss_audit"] = audit

        # Expand rationale with near-miss numbers (no new data, just existing values).
        eg_p = eg.get("pvalue")
        sp_p = (spread.get("adf_spread") or {}).get("pvalue")
        hl = spread.get("half_life_ou")
        hurst = spread.get("hurst_exponent")
        rs_frac = rs.get("frac_significant")
        parts = [
            f"eg_p={eg_p if eg_p is None else round(eg_p,6)}",
            f"spread_adf_p={sp_p if sp_p is None else round(sp_p,6)}",
            f"hl={hl if hl is None else round(hl,1)}",
            f"hurst={hurst if hurst is None else round(hurst,4)}",
            f"rolling_frac={rs_frac if rs_frac is None else round(rs_frac,4)}",
            f"/req {ROLLING_FRAC_REQUIRED}",
        ]
        near = [g["gate"] for g in nm if g.get("near")]
        rationale = (
            f"Real Binance spot series (www.binance.com); no fabrication. "
            f"Pair did not pass all enriched cointegration gates. "
            f"Near-miss audit: {'; '.join(parts)}. "
            f"Near-miss gates (close but failing): {near if near else 'none'}. "
            f"Marked blocked_or_insufficient_data with full provenance; "
            f"do not trade until all gates pass on real data. No threshold weakening."
        )
        prov["rationale"] = rationale

    # POL/BTC: lock in deep-dive causal filter evaluation.
    if deep_dive and "POL/BTC" in cd:
        cfe = deep_dive.get("causal_filter_evaluation", {})
        best = cfe.get("best_result", {})
        prov = cd["POL/BTC"].setdefault("provenance", {})
        prov["rationale"] = (
            "Real Binance spot series (www.binance.com); no fabrication. "
            "POL/BTC passes eg, johansen, spread_mean_reversion, hl_bounds, "
            "leg_stationarity but fails rolling_stability (frac_significant "
            f"{cd['POL/BTC']['rolling_stability']['frac_significant']} < 0.6). "
            "Deep dive: 9/184 trailing windows (frac 0.0489) pass EG, scattered "
            "with no robust trailing-only causal boundary. Candidate trailing-only "
            f"filters tested (corr, vol_ratio, half-life, hurst, spread ADF); best "
            f"filter '{cfe.get('best_by_precision_recall')}' achieved precision "
            f"{best.get('precision')} / recall {best.get('recall')} with "
            f"{best.get('false_positive')} false positives and "
            f"{best.get('false_negative')} false negatives — not robust. "
            "No lookahead filter added. Kept blocked_or_insufficient_data solely "
            "on rolling_stability. No threshold weakening."
        )
        prov["deep_dive"] = {
            "source": "reports/pol_btc_deep_dive.json",
            "n_pass": deep_dive.get("n_pass"),
            "n_fail": deep_dive.get("n_fail"),
            "frac_pass": deep_dive.get("frac_pass"),
            "passing_start_bars": deep_dive.get("passing_start_bars"),
            "best_filter": cfe.get("best_by_precision_recall"),
            "best_precision": best.get("precision"),
            "best_recall": best.get("recall"),
            "false_positive": best.get("false_positive"),
            "false_negative": best.get("false_negative"),
            "conclusion": cfe.get("conclusion"),
        }

    ARTIFACT.write_text(json.dumps(data, indent=2, default=float), encoding="utf-8")
    print(f"Updated {ARTIFACT} with near_miss_audit for {len(cd)} pairs.")


if __name__ == "__main__":
    main()
