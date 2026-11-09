"""Campaign #2: real LOB/intrabar microstructure feasibility (public spot snapshots).

Real public data only where feasible. Never fabricates fills/order books.
If full L2/intrabar history is unavailable, emits an honest feasibility artifact.
Emits reports/execution_lob_real.json.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from data.real_feed_loader import (
    fetch_spot_microstructure_snapshot,
    summarize_microstructure_snapshot,
)


def _json_default(obj):
    if hasattr(obj, "isoformat"):
        return obj.isoformat()
    return str(obj)


def main() -> None:
    generated_at = datetime.now(timezone.utc).isoformat()
    symbols = ["BTCUSDT", "ETHUSDT"]
    blocked_routes: list[dict] = []
    findings = []
    any_ok = False
    raw_checksums = {}
    for sym in symbols:
        try:
            snap, attempts = fetch_spot_microstructure_snapshot(
                sym, depth_limit=20, trades_limit=100, timeout=20.0
            )
            blocked_routes.extend(attempts.get("blocked_routes") or [])
            summary = summarize_microstructure_snapshot(snap)
            ok = bool(attempts.get("depth_fetched")) or bool(attempts.get("aggTrades_fetched"))
            any_ok = any_ok or ok
            raw = json.dumps(snap, sort_keys=True, default=_json_default).encode("utf-8")
            raw_checksums[sym] = hashlib.sha256(raw).hexdigest()
            findings.append(
                {
                    "symbol": sym,
                    "snapshot_captured": ok,
                    "attempts": attempts,
                    "summary": summary,
                    "notes": (
                        "Point-in-time public snapshot only; not historical L2/intrabar replay."
                    ),
                }
            )
        except Exception as exc:
            blocked_routes.append(
                {
                    "host": "loader",
                    "path": f"fetch_spot_microstructure_snapshot:{sym}",
                    "status": None,
                    "error": str(exc)[:220],
                }
            )
            findings.append(
                {"symbol": sym, "snapshot_captured": False, "error": str(exc), "summary": {}}
            )

    status = "partial" if any_ok else "blocked"
    result = {
        "real_data_only": True,
        "fabricated_data": False,
        "generated_at_utc": generated_at,
        "campaign": (
            "Campaign #2 - Funding/Basis-Carry + LOB/Intrabar Feasibility (LOB/intrabar component)"
        ),
        "status": status,
        "data_sources": {
            "family": "intrabar_microstructure_feasibility",
            "provider": "Binance public spot depth/aggTrades snapshot endpoints",
            "hosts_routes_attempted": [
                "https://www.binance.com/api/v3/depth",
                "https://data-api.binance.vision/api/v3/depth",
                "https://www.binance.com/api/v3/aggTrades",
                "https://data-api.binance.vision/api/v3/aggTrades",
            ],
        },
        "symbols": symbols,
        "time_window": {"type": "point_in_time_snapshot", "captured_at_utc": generated_at},
        "freq": "snapshot_not_historical_intrabar",
        "row_counts": {
            f["symbol"]: {
                "agg_trades_n": int((f.get("summary") or {}).get("agg_trades_n") or 0),
                "bid_levels": int((f.get("summary") or {}).get("bid_levels") or 0),
                "ask_levels": int((f.get("summary") or {}).get("ask_levels") or 0),
            }
            for f in findings
        },
        "checksums": {"snapshot_sha256": raw_checksums},
        "blocked_routes": blocked_routes,
        "feasibility": {
            "real_public_snapshot_feasible": any_ok,
            "historical_l2_intrabar_replay_feasible_from_public_routes": False,
            "observed_limits": [
                "Public depth/aggTrades endpoints provide current/limited snapshots, not "
                "full historical L2 replay in this environment.",
                "Historical tick/L2 reconstruction would require authenticated exchange "
                "archives, licensed data, or a persistent recorder not present in-repo.",
            ],
            "schema_provenance_expectations_for_real_history": {
                "family": "intrabar_microstructure",
                "required_provenance_keys": [
                    "source_provider",
                    "endpoints_or_files",
                    "retrieved_at_utc",
                    "symbol_map",
                    "kind",
                    "row_count",
                    "sha256_pkl",
                    "real_data_only",
                    "fabricated_data",
                ],
                "required_columns_trades": ["timestamp_utc", "symbol", "price", "qty"],
                "required_columns_book": [
                    "timestamp_utc",
                    "symbol",
                    "bid_px_levels",
                    "ask_px_levels",
                    "bid_sz_levels",
                    "ask_sz_levels",
                    "depth",
                ],
                "honesty_rules": [
                    "no fabricated fills/order books",
                    "no resampled 1h presented as microstructure",
                    "real_data_only true",
                    "fabricated_data false",
                    "sha256_pkl must match bytes",
                ],
            },
            "findings": findings,
        },
        "notes": [
            "No fabricated fills or order books.",
            "Snapshot metrics (spread/trade counts) are descriptive only; not execution PnL.",
            "451/403/404 routes recorded as blocked_routes when encountered.",
        ],
        "limitations": [
            "Point-in-time feasibility, not a backtestable historical intrabar dataset.",
            "Slippage/queue models require historical event data and are not inferred "
            "from snapshots.",
        ],
    }

    out_dir = Path("reports")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "execution_lob_real.json"
    out_path.write_text(
        json.dumps(result, indent=2, default=_json_default) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "artifact": str(out_path),
                "status": status,
                "blocked_routes": len(blocked_routes),
                "real_public_snapshot_feasible": any_ok,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
