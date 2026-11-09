#!/usr/bin/env python3
"""Campaign #3: ML-augmented signal filtering for cointegration persistence.

Real Binance spot data only (cached/public). No fabrication. Fail-closed when
data/model/labels insufficient. Purged walk-forward CV with embargo to control
leakage. Emits reports/ml_gated_pairs.json.
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd

from data.loader import DataLoader
from strategies.ml_gated_pairs import MLGatedPairsStrategy
from utils.ml_gating import (
    FEATURE_NAMES,
    extract_persistence_features,
    fit_final_model,
    sha256_json_obj,
    train_persistence_classifier,
)

SYMBOLS = ["ADA", "BNB", "BTC", "DOT", "ETH", "SOL", "XRP"]
PAIRS = [
    ("BTC", "ETH"),
    ("ETH", "SOL"),
    ("BTC", "SOL"),
    ("ADA", "ETH"),
    ("XRP", "BTC"),
    ("BNB", "ETH"),
    ("BTC", "BNB"),
    ("DOT", "BTC"),
]
START = "2026-04-01"
END = "2026-10-30"
INTERVAL = "1h"
LOOKBACK = 120  # 5 days hourly (tractable, still causal)
HORIZON = 48   # label horizon (hours)
EMBARGO = LOOKBACK  # purge gap >= lookback to avoid overlap/leakage
STEP = 72      # sample every 3 days for tractability on CI-scale runs
TRAIN_SIZE = 60
TEST_SIZE = 20
THRESHOLD = 0.55
EG_PERSIST_PVALUE = 0.10
HL_MAX = 500.0


def _json_safe(x: Any) -> Any:
    if x is None or isinstance(x, (str, bool, int)):
        return x
    if isinstance(x, float):
        return x if np.isfinite(x) else None
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.floating,)):
        v = float(x)
        return v if np.isfinite(v) else None
    if isinstance(x, (np.bool_,)):
        return bool(x)
    if isinstance(x, dict):
        return {str(k): _json_safe(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_json_safe(v) for v in x]
    try:
        return str(x)
    except Exception:
        return None


def _label_persistence(a: pd.Series, b: pd.Series) -> int | None:
    """Forward-looking persistence label computed on a future window only.

    Used for supervised evaluation; runner ensures feature/label windows are
    separated by embargo and never fed to decisions at feature time.
    """
    try:
        from utils.cointegration import (
            calculate_spread,
            engle_granger_test,
            estimate_hedge_ratio_ols,
            half_life_ou,
        )
        if len(a) < 30 or len(b) < 30:
            return None
        eg = engle_granger_test(a, b)
        pv = eg.get("pvalue")
        if pv is None or not np.isfinite(float(pv)):
            return None
        beta = estimate_hedge_ratio_ols(a, b)
        sp = calculate_spread(a, b, beta if np.isfinite(beta) else None)
        hl = half_life_ou(sp).get("half_life")
        hl_ok = hl is not None and np.isfinite(float(hl)) and 1.0 < float(hl) < HL_MAX
        return int((float(pv) <= EG_PERSIST_PVALUE) and hl_ok)
    except Exception:
        return None


def build_dataset(
    data: pd.DataFrame, pairs: list[tuple[str, str]]
) -> tuple[pd.DataFrame, dict[str, Any]]:
    rows = []
    diag: dict[str, Any] = {"pairs": {}, "sampled_points": 0, "labeled_points": 0}
    for p in pairs:
        a1, a2 = p
        pair_diag = {"rows": 0, "labeled": 0, "skipped_missing": 0}
        if a1 not in data.columns or a2 not in data.columns:
            pair_diag["skipped_missing"] = 1
            diag["pairs"][f"{a1}/{a2}"] = pair_diag
            continue
        s1 = data[a1].dropna()
        s2 = data[a2].dropna()
        idx = s1.index.intersection(s2.index)
        s1 = s1.loc[idx]
        s2 = s2.loc[idx]
        n = len(idx)
        # sample decision points
        t = LOOKBACK
        while t + EMBARGO + HORIZON <= n:
            feats = extract_persistence_features(
                s1.iloc[:t], s2.iloc[:t], lookback=LOOKBACK, min_obs=max(30, LOOKBACK // 2)
            )
            # label from strictly future window after embargo
            ls = t + EMBARGO
            le = ls + HORIZON
            lab = _label_persistence(s1.iloc[ls:le], s2.iloc[ls:le])
            rec = {"pair": f"{a1}/{a2}", "t_idx": int(t), "t": str(idx[t - 1])}
            rec.update(feats)
            rec["label_persistent"] = lab
            rows.append(rec)
            diag["sampled_points"] += 1
            pair_diag["rows"] += 1
            if lab is not None:
                diag["labeled_points"] += 1
                pair_diag["labeled"] += 1
            t += STEP
        diag["pairs"][f"{a1}/{a2}"] = pair_diag
    df = pd.DataFrame(rows)
    return df, diag


def evaluate_ml_gating_oos_proxy(
    data: pd.DataFrame, pairs: list[tuple[str, str]], model: Any | None
) -> dict[str, Any]:
    """Small causal proxy: compare gated vs ungated signal counts on tail
    segment. Honest proxy only (not a profitability claim). Uses last 20% as
    evaluation segment with trailing-feature gating decisions; no future
    features used for decisions.
    """
    n = len(data)
    if n < 500:
        return {"status": "insufficient_data", "reason": "series_too_short"}
    split = int(n * 0.8)
    eval_data = data.iloc[max(0, split - LOOKBACK) :]
    per_pair = {}
    total_gated = 0
    total_ungated = 0
    for p in pairs:
        if p[0] not in data.columns or p[1] not in data.columns:
            per_pair[f"{p[0]}/{p[1]}"] = {"status": "missing"}
            continue
        try:
            gated = MLGatedPairsStrategy(
                pair=p, lookback=LOOKBACK, ml_model=model, ml_threshold=THRESHOLD
            )
            ungated = MLGatedPairsStrategy(
                pair=p, lookback=LOOKBACK, ml_model=None, ml_threshold=THRESHOLD
            )
            gs = gated.generate_signals(eval_data)
            us = ungated.generate_signals(eval_data)
            gc = int((gs[[p[0], p[1]]].abs().sum(axis=1) > 1e-12).sum())
            uc = int((us[[p[0], p[1]]].abs().sum(axis=1) > 1e-12).sum())
            # with no model, gate_persistence fails closed => gated <= ungated
            per_pair[f"{p[0]}/{p[1]}"] = {
                "gated_active_bars": gc,
                "ungated_active_bars": uc,
                "gate_reduced_or_equal": gc <= uc,
                "model_present": model is not None,
            }
            total_gated += gc
            total_ungated += uc
        except Exception as exc:
            per_pair[f"{p[0]}/{p[1]}"] = {"status": "error", "error": str(exc)[:160]}
    eval_start = str(eval_data.index[0])
    eval_end = str(eval_data.index[-1])
    return {
        "status": "ok",
        "eval_window": {
            "start": eval_start,
            "end": eval_end,
            "rows": int(len(eval_data)),
        },
        "split_index": int(split),
        "total_gated_active_bars": int(total_gated),
        "total_ungated_active_bars": int(total_ungated),
        "gate_fail_closed_effective": bool(total_gated <= total_ungated),
        "per_pair": per_pair,
        "note": "Proxy counts only (active signal bars on tail segment). Not a "
        "PnL/profitability claim.",
    }


def main() -> int:
    generated_at = datetime.now(timezone.utc).isoformat()
    blocked_routes: list[dict[str, Any]] = []
    provenance: dict[str, Any] = {}
    data = pd.DataFrame()
    status = "blocked"
    notes: list[str] = []
    errors: list[str] = []

    try:
        loader = DataLoader()
        data, provenance = loader.fetch_with_provenance(
            SYMBOLS, START, END, interval=INTERVAL, quote_asset="USDT", use_cache=True
        )
        for k in ("blocked_hosts", "blocked_routes"):
            v = provenance.get(k)
            if isinstance(v, list):
                blocked_routes.extend(v)
    except Exception as exc:
        errors.append(f"data_load:{str(exc)[:200]}")
        try:
            lp = getattr(loader, "last_fetch_provenance", None)
            if isinstance(lp, dict):
                provenance = lp
                for k in ("blocked_hosts", "blocked_routes"):
                    v = lp.get(k)
                    if isinstance(v, list):
                        blocked_routes.extend(v)
        except Exception:
            pass

    dataset_info: dict[str, Any] = {}
    cv_result: dict[str, Any] = {"ok": False, "reason": "no_data"}
    model_meta: dict[str, Any] = {"ok": False, "reason": "no_data"}
    model = None
    oos_proxy: dict[str, Any] = {"status": "not_run"}

    if not data.empty:
        try:
            ds, diag = build_dataset(data, PAIRS)
            labeled_rows = int(
                ds["label_persistent"].notna().sum()
            ) if "label_persistent" in ds else 0
            dataset_info = {
                "rows": int(len(ds)),
                "labeled_rows": labeled_rows,
                "pairs_with_labels": int(
                    sum(
                        1
                        for v in diag.get("pairs", {}).values()
                        if v.get("labeled", 0) > 0
                    )
                ),
                "diagnostics": diag,
                "label_definition": {
                    "feature_window": f"trailing {LOOKBACK} bars, causal only",
                    "embargo_bars": EMBARGO,
                    "horizon_bars": HORIZON,
                    "persistence_rule": (
                        f"EG pvalue <= {EG_PERSIST_PVALUE} AND 1 < half_life < "
                        f"{HL_MAX} on future [t+embargo,t+embargo+horizon)"
                    ),
                },
            }
            if len(ds) and "label_persistent" in ds:
                train_ds = ds.dropna(subset=["label_persistent"]).copy()
                if len(train_ds) >= 30:
                    X = train_ds[FEATURE_NAMES]
                    y = train_ds["label_persistent"].astype(int)
                    cv_result = train_persistence_classifier(
                        X, y,
                        train_size=TRAIN_SIZE,
                        test_size=TEST_SIZE,
                        step=max(10, TEST_SIZE // 2),
                        embargo=max(EMBARGO // max(1, STEP), 1) if STEP >= 1 else 1,
                        threshold=THRESHOLD,
                        random_state=42,
                    )
                    model, model_meta = fit_final_model(X, y, random_state=42)
                else:
                    cv_result = {
                        "ok": False,
                        "reason": "insufficient_labeled_rows",
                        "labeled_rows": int(len(train_ds)),
                    }
                    model_meta = {"ok": False, "reason": "insufficient_labeled_rows"}
            else:
                cv_result = {"ok": False, "reason": "empty_dataset"}
                model_meta = {"ok": False, "reason": "empty_dataset"}
        except Exception as exc:
            errors.append(f"dataset_or_model:{str(exc)[:200]}")
            cv_result = {"ok": False, "reason": "exception", "error": str(exc)[:200]}

        try:
            oos_proxy = evaluate_ml_gating_oos_proxy(data, PAIRS, model)
        except Exception as exc:
            oos_proxy = {"status": "error", "error": str(exc)[:200]}
            errors.append(f"oos_proxy:{str(exc)[:200]}")

        if cv_result.get("ok") or model_meta.get("ok") or dataset_info.get(
            "labeled_rows", 0
        ) > 0:
            status = "ok" if (cv_result.get("ok") and not errors) else "partial"
        else:
            status = "partial" if not errors else "blocked"
    else:
        status = "blocked"
        notes.append("No market data loaded; artifact is honest blocked/empty result.")

    # Deterministic checksums from canonical JSON slices
    checksums = {
        "data_index_sha256": hashlib.sha256(
            (str(data.index.min()) + "|" + str(data.index.max()) + "|" + str(len(data))).encode()
        ).hexdigest()
        if not data.empty
        else None,
        "config_sha256": sha256_json_obj(
            {
                "symbols": SYMBOLS,
                "pairs": PAIRS,
                "start": START,
                "end": END,
                "interval": INTERVAL,
                "lookback": LOOKBACK,
                "horizon": HORIZON,
                "embargo": EMBARGO,
                "step": STEP,
                "train_size": TRAIN_SIZE,
                "test_size": TEST_SIZE,
                "threshold": THRESHOLD,
                "features": FEATURE_NAMES,
            }
        ),
    }

    result = {
        "real_data_only": True,
        "fabricated_data": False,
        "generated_at_utc": generated_at,
        "campaign": "Campaign #3 - ML-augmented signal filtering for cointegration persistence",
        "status": status,
        "data_sources": {
            "provider": "Binance public spot (via DataLoader/cache)",
            "symbols_requested": SYMBOLS,
            "pairs": [f"{a}/{b}" for a, b in PAIRS],
            "time_window": {"start_utc": START, "end_utc": END},
            "interval": INTERVAL,
            "rows_loaded": int(len(data)),
            "columns": list(data.columns) if not data.empty else [],
            "provenance": _json_safe(
                {
                    k: v
                    for k, v in (provenance or {}).items()
                    if k
                    in (
                        "requested_symbols",
                        "start",
                        "end",
                        "interval",
                        "quote_asset",
                        "per_symbol",
                        "excluded",
                        "cache",
                        "blocked_hosts",
                        "blocked_routes",
                    )
                }
            ),
        },
        "blocked_routes": _json_safe(blocked_routes),
        "methodology": {
            "classifier": (
                "LogisticRegression(pipeline: StandardScaler+LogReg, "
                "class_weight=balanced)"
            ),
            "features": FEATURE_NAMES,
            "purged_walk_forward_cv": {
                "train_size": TRAIN_SIZE,
                "test_size": TEST_SIZE,
                "step": max(10, TEST_SIZE // 2),
                "embargo": max(EMBARGO // max(1, STEP), 1),
                "note": "Embargo/purge gap applied between train and test; label "
                "horizon is strictly future of features.",
            },
            "leakage_controls": [
                "Features computed from trailing windows only (no future bars).",
                "Labels computed from future window [t+embargo,t+embargo+horizon] "
                "only; never used as features.",
                "Purged walk-forward splits with embargo gap between train/test.",
                "Fail-closed when model/features/data insufficient.",
            ],
            "ml_gating": {
                "threshold": THRESHOLD,
                "fail_closed": True,
                "sizing_effect": "Candidate entries blocked when gate fails; "
                "exits not blocked.",
            },
        },
        "dataset": _json_safe(dataset_info),
        "cv_evaluation": _json_safe(cv_result),
        "final_model": _json_safe(
            {
                **model_meta,
                "artifact_model_persisted": False,
                "reason_not_persisted": "no binary model artifact committed; "
                "evaluation/provenance recorded in JSON",
            }
        ),
        "oos_proxy": _json_safe(oos_proxy),
        "checksums": checksums,
        "limitations": [
            "Research artifact only; not evidence of trading edge or investment "
            "advice.",
            "Cointegration persistence labels are heuristic (EG p-value + "
            "half-life on forward window) and may be noisy.",
            "OOS proxy reports signal-bar counts on a tail segment, not "
            "PnL/profitability.",
            "Purged CV uses sampled points (step) for tractability; embargo set "
            "from lookback/horizon policy.",
            "No fabricated data/fills/order books/labels/metrics; blocked routes "
            "recorded honestly.",
        ],
        "errors": errors,
        "notes": notes,
    }

    out = Path("reports") / "ml_gated_pairs.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(_json_safe(result), indent=2) + "\n")
    print(
        json.dumps(
            {
                "artifact": str(out),
                "status": status,
                "labeled_rows": dataset_info.get("labeled_rows"),
                "cv_ok": cv_result.get("ok"),
                "blocked_routes": len(blocked_routes),
                "errors": errors,
            },
            indent=2,
        )
    )
    return 0 if status in ("ok", "partial") else 2


if __name__ == "__main__":
    raise SystemExit(main())
