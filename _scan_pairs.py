#!/usr/bin/env python3
"""Honest per-window cointegration gate scan on REAL cached Binance data.

Scans sliding windows over the real hourly series for BTC/ETH, ETH/SOL, BTC/SOL
and reports, per window, the full enriched gate set. Answers: does ANY real window
pass all gates? Which gate is the blocker and on what share of windows?

No fabrication. Real cached data only.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from data.loader import DataLoader
from utils.cointegration import target_schema_diagnostics

PAIRS = [("BTC", "ETH"), ("ETH", "SOL"), ("BTC", "SOL")]
WINDOWS = [240, 360, 500, 720]
STEP = 24


def scan() -> dict:
    loader = DataLoader()
    data, prov = loader.fetch_with_provenance(
        ["BTC", "ETH", "SOL"], "2026-04-01", "2026-10-30", "1h", use_cache=True
    )
    n = len(data)
    out: dict = {
        "n_bars": int(n),
        "cache_used": prov.get("cache", {}).get("used"),
        "blocked_routes": prov.get("blocked_routes"),
        "provenance": {
            "real_data_only": True,
            "fabricated_data": False,
            "source": "data.loader.DataLoader.fetch_with_provenance (cached Binance spot)",
        },
        "windows": [],
    }
    for a, b in PAIRS:
        p1 = data[a]
        p2 = data[b]
        entry: dict = {"pair": f"{a}/{b}", "window_scans": []}
        for w in WINDOWS:
            if w > n:
                continue
            rows = []
            for start in range(0, n - w + 1, STEP):
                end = start + w
                s1 = p1.iloc[start:end]
                s2 = p2.iloc[start:end]
                try:
                    diag = target_schema_diagnostics(s1, s2, pair_name=f"{a}/{b}")
                except Exception as e:
                    diag = {"error": str(e)[:80]}
                g = diag.get("gates", {}) if isinstance(diag, dict) else {}
                eg = diag.get("engle_granger", {}) if isinstance(diag, dict) else {}
                rs = diag.get("rolling_stability", {}) if isinstance(diag, dict) else {}
                rows.append(
                    {
                        "start": int(start),
                        "end": int(end),
                        "gates": {k: bool(v) for k, v in g.items() if k != "all_pass"},
                        "all_pass": bool(g.get("all_pass")),
                        "eg_pvalue": eg.get("pvalue"),
                        "rolling_frac": rs.get("frac_significant"),
                        "rolling_n_windows": rs.get("n_windows"),
                        "status": diag.get("status"),
                    }
                )
            entry["window_scans"].append({"window": int(w), "n_windows_scanned": len(rows), "rows": rows})
        out["windows"].append(entry)
    return out


def summarize(scan: dict) -> dict:
    summ: dict = {"pairs": []}
    for entry in scan["windows"]:
        pair_sum = {"pair": entry["pair"], "windows": []}
        for ws in entry["window_scans"]:
            rows = ws["rows"]
            if not rows:
                continue
            gate_names = [k for k in rows[0]["gates"]]
            share = {g: float(np.mean([r["gates"][g] for r in rows])) for g in gate_names}
            all_pass_share = float(np.mean([r["all_pass"] for r in rows]))
            blocker = min(share, key=lambda g: share[g])
            pair_sum["windows"].append(
                {
                    "window": ws["window"],
                    "n_scanned": len(rows),
                    "all_pass_share": all_pass_share,
                    "gate_pass_share": {k: round(v, 4) for k, v in share.items()},
                    "rarest_gate": blocker,
                    "n_all_pass": int(sum(1 for r in rows if r["all_pass"])),
                }
            )
        summ["pairs"].append(pair_sum)
    return summ


if __name__ == "__main__":
    scan = scan()
    summ = summarize(scan)
    ts = pd.Timestamp.now(tz="UTC").strftime("%Y%m%dT%H%M%SZ")
    out_path = Path("reports") / f"pairs_gate_breakdown_{ts}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps({"scan": scan, "summary": summ}, indent=2, default=float), encoding="utf-8"
    )
    print(json.dumps(summ, indent=2, default=float))
    print(f"\nWrote {out_path}")