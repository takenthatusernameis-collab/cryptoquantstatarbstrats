"""Campaign #2: real public funding/basis-carry analysis (Binance USD-M).

Real public data only. Never fabricates data. Records blocked_routes honestly.
Emits reports/funding_carry_real.json.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from data.real_feed_loader import compute_funding_carry_metrics, fetch_binance_funding_rates


def _json_default(obj):
    if hasattr(obj, "isoformat"):
        return obj.isoformat()
    return str(obj)


def main() -> None:
    generated_at = datetime.now(timezone.utc).isoformat()
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]
    start_utc = "2026-05-01T00:00:00Z"
    end_utc = "2026-11-08T00:00:00Z"
    blocked_routes: list[dict] = []
    df = None
    attempts: dict = {}
    try:
        df, attempts = fetch_binance_funding_rates(symbols, start_utc, end_utc, timeout=20.0)
        blocked_routes.extend(attempts.get("blocked_routes") or [])
    except Exception as exc:
        attempts = {"error": str(exc)}
        blocked_routes.append(
            {
                "host": "loader",
                "path": "fetch_binance_funding_rates",
                "status": None,
                "error": str(exc)[:220],
            }
        )
        import pandas as pd

        df = pd.DataFrame()

    metrics = (
        compute_funding_carry_metrics(df, intervals_per_day=3)
        if df is not None
        else {"status": "error"}
    )
    have_data = df is not None and not df.empty
    per = (metrics or {}).get("per_symbol", {})
    symbols_with_rows = [s for s, v in per.items() if isinstance(v, dict) and v.get("rows", 0) > 0]
    status = "ok" if (have_data and symbols_with_rows) else ("partial" if have_data else "blocked")

    sample_hashes = {}
    if have_data:
        sample = df.head(25).to_csv(index=False).encode("utf-8")
        sample_hashes["head25_csv_sha256"] = hashlib.sha256(sample).hexdigest()
        full = df.to_csv(index=False).encode("utf-8")
        sample_hashes["full_payload_sha256"] = hashlib.sha256(full).hexdigest()

    result = {
        "real_data_only": True,
        "fabricated_data": False,
        "generated_at_utc": generated_at,
        "campaign": (
            "Campaign #2 - Funding/Basis-Carry + LOB/Intrabar Feasibility (funding component)"
        ),
        "status": status,
        "data_sources": {
            "family": "funding_basis_carry",
            "provider": "Binance USD-M public fundingRate endpoint",
            "hosts_attempted": attempts.get("hosts", []),
            "routes_attempted": ["/fapi/v1/fundingRate"],
            "attempts": attempts,
        },
        "symbols": symbols,
        "symbols_fetched": attempts.get("symbols_fetched", symbols_with_rows),
        "time_window": {"start_utc": start_utc, "end_utc": end_utc},
        "freq": "8h_funding_intervals",
        "row_counts": {
            "total": int(len(df)) if df is not None else 0,
            "per_symbol": {s: int(v.get("rows", 0)) for s, v in per.items() if isinstance(v, dict)},
        },
        "checksums": sample_hashes,
        "blocked_routes": blocked_routes,
        "metrics": metrics,
        "notes": [
            "Real public Binance fundingRate data only; no fabricated numbers.",
            "Annualized carry is a simple funding-sum/mean projection (intervals/day * 365), "
            "not a tradable PnL claim.",
            "Basis/perp-spot dislocation not computed without a matched real spot+perp mark "
            "series in this artifact; funding carry metrics are computed honestly from "
            "observed funding rates.",
            "451/403/404 hosts recorded as blocked_routes; working public routes used "
            "where available.",
        ],
        "limitations": [
            "No lookahead introduced by script logic.",
            "Exchange-specific funding schedule/limits apply; row counts depend on public "
            "API availability.",
            "Not an edge claim (oos_edge_proven not asserted).",
        ],
    }

    out_dir = Path("reports")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "funding_carry_real.json"
    out_path.write_text(
        json.dumps(result, indent=2, default=_json_default) + "\n", encoding="utf-8"
    )
    summary = {
        "artifact": str(out_path),
        "status": status,
        "rows": result["row_counts"]["total"],
        "blocked_routes": len(blocked_routes),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
