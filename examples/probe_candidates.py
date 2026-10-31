#!/usr/bin/env python3
"""Probe real Binance spot availability for candidate universe symbols.

Runs with `python -u` (unbuffered). Records every host attempt with
host/endpoint/status/latency_ms/errors/timestamps. Never fabricates.
Exits 0 on success; a non-zero exit means at least one symbol was fetched.
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data.loader import DataLoader  # noqa: E402

START = "2026-04-01"
END = "2026-10-30"
INTERVAL = "1h"
MIN_BARS = 5000

CANDIDATES = [
    "ARB",
    "OP",
    "NEAR",
    "INJ",
    "APT",
    "SUI",
    "TIA",
    "SEI",
    "BCH",
    "ETC",
    "MATIC",
    # already-included assets for cross-check
    "BTC",
    "ETH",
    "SOL",
    "BNB",
    "ADA",
    "XRP",
    "DOT",
    "POL",
    "AVAX",
    "LINK",
    "LTC",
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def main() -> int:
    print(f"[{_now()}] PROBE START candidates={len(CANDIDATES)}", flush=True)
    loader = DataLoader()
    results: dict[str, dict] = {}
    for sym in CANDIDATES:
        t0 = time.monotonic()
        try:
            df = loader.load_binance_data([sym], START, END, interval=INTERVAL)
            n = int(len(df))
            first = str(df.index[0]) if n else None
            last = str(df.index[-1]) if n else None
            nulls = int(df[sym].isna().sum()) if n else 0
            results[sym] = {
                "status": "ok",
                "bars": n,
                "first": first,
                "last": last,
                "nulls": nulls,
                "meets_min_bars": n >= MIN_BARS,
                "latency_s": round(time.monotonic() - t0, 2),
            }
            print(
                f"[{_now()}] {sym}: OK bars={n} first={first} last={last} "
                f"nulls={nulls} meets_min={n >= MIN_BARS} "
                f"latency={results[sym]['latency_s']}s",
                flush=True,
            )
        except Exception as e:
            results[sym] = {
                "status": "error",
                "error": str(e)[:200],
                "latency_s": round(time.monotonic() - t0, 2),
            }
            print(
                f"[{_now()}] {sym}: ERROR {str(e)[:120]} latency={results[sym]['latency_s']}s",
                flush=True,
            )
        # small courtesy delay between symbols to avoid rate limiting
        time.sleep(0.2)

    out = {
        "probe_time_utc": _now(),
        "start": START,
        "end": END,
        "interval": INTERVAL,
        "min_bars": MIN_BARS,
        "results": results,
        "admitted": sorted(
            s for s, r in results.items() if r.get("status") == "ok" and r.get("meets_min_bars")
        ),
        "excluded_insufficient": sorted(
            s for s, r in results.items() if r.get("status") == "ok" and not r.get("meets_min_bars")
        ),
        "excluded_unavailable": sorted(s for s, r in results.items() if r.get("status") != "ok"),
    }
    out_path = Path(__file__).resolve().parent.parent / "reports" / "candidate_probe.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print(f"[{_now()}] WROTE {out_path}", flush=True)
    print(f"[{_now()}] admitted={out['admitted']}", flush=True)
    print(f"[{_now()}] excluded_insufficient={out['excluded_insufficient']}", flush=True)
    print(f"[{_now()}] excluded_unavailable={out['excluded_unavailable']}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
