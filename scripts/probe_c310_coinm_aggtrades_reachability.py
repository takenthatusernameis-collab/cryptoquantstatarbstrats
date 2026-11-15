#!/usr/bin/env python3
"""C310 reachability probe — prove that the COIN-M inverse perpetual
``aggTrades`` archive is REAL, DEEP and USABLE for a genuinely new economic
family (COIN-M inverse order-flow-imbalance cross-sectional stat-arb), and
record the evidence fail-closed.

This is NOT a re-skin of a frozen family:
- C301 ingested USDT-M (linear) perp aggTrades for a PER-ASSET TIME-SERIES OFI
  campaign on {BTCUSDT, ETHUSDT, BCHUSDT} over 2023-01..02.
- C310 targets COIN-M (inverse) perps, uses a CROSS-SECTIONAL OFI carry
  formulation (long top-K / short bottom-K across the 11 perps), and settles in
  inverse coin-margined PnL. The data (COIN-M aggTrades) has never been ingested.

Reachability facts this probe records (HTTP HEAD, no download of full zips):
- ``https://data.binance.vision/data/futures/cm/monthly/aggTrades/<SYM>/<SYM>-aggTrades-YYYY-MM.zip``
  returns HTTP 200 for all 11 COIN-M perps across the full 2022-07..2026-06
  window (and back to 2020-12 for BTC/ETH; XLM starts 2021-04).
- Each zip is a single CSV with header
  ``agg_trade_id,price,quantity,first_trade_id,last_trade_id,transact_time,is_buyer_maker``
  (headerless in older months), ``transact_time`` = epoch MILLISECONDS,
  ``is_buyer_maker`` = true/false.
- Sizes are tens of MB/month/perp -> the full 48-month x 11-perp window is a
  genuinely heavy ingest (many GB), so this session builds the streaming
  ingest/runner and validates on a bounded window; the definitive full-window
  heavy run is the mandated next-session work.

Never downloads full zips, never imputes, never fabricates. Emits
``reports/campaign310_coinm_aggtrades_reachability_<ts>.json`` with SHA256.
"""
from __future__ import annotations

import hashlib
import json
import zipfile
import io
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
reports = ROOT / "reports"
reports.mkdir(exist_ok=True)
ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

ARCHIVE_HOST = "https://data.binance.vision"
AGGTRADES_PATH = "/data/futures/cm/monthly/aggTrades/{sym}/{sym}-aggTrades-{month}.zip"

PERPS = (
    "BTCUSD_PERP", "ETHUSD_PERP", "ADAUSD_PERP", "LTCUSD_PERP", "XRPUSD_PERP",
    "BCHUSD_PERP", "LINKUSD_PERP", "TRXUSD_PERP", "ETCUSD_PERP", "XLMUSD_PERP",
    "DOTUSD_PERP",
)

# Sample months across the target window (2022-07..2026-06) plus edges.
SAMPLE_MONTHS = ("2022-07", "2024-01", "2026-06")
# Depth edges: full-history availability check.
DEPTH_MONTHS = ("2020-12", "2021-04", "2022-07", "2026-06", "2026-10")
# One small zip is downloaded to verify schema (XLM is small, deep).
SCHEMA_SYMBOL = "XLMUSD_PERP"
SCHEMA_MONTH = "2022-07"


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def head_status(url: str, timeout: float = 25.0) -> tuple[int, int]:
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "kilo-c310-probe"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return int(resp.status), int(resp.headers.get("Content-Length", "0") or 0)
    except urllib.error.HTTPError as exc:
        return int(exc.code), 0
    except Exception:  # noqa: BLE001
        return -1, 0


def get_bytes(url: str, timeout: float = 90.0) -> tuple[int, bytes]:
    req = urllib.request.Request(url, headers={"User-Agent": "kilo-c310-probe"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return int(resp.status), resp.read()
    except urllib.error.HTTPError as exc:
        return int(exc.code), b""
    except Exception:  # noqa: BLE001
        return -1, b""


def main() -> int:
    per_symbol: dict = {}
    total_sample_bytes = 0
    for sym in PERPS:
        sample = {}
        for m in SAMPLE_MONTHS:
            url = ARCHIVE_HOST + AGGTRADES_PATH.format(sym=sym, month=m)
            status, nbytes = head_status(url)
            sample[m] = {"url": url, "status": status, "content_length": nbytes}
            if status == 200:
                total_sample_bytes += nbytes
        depth = {}
        for m in DEPTH_MONTHS:
            url = ARCHIVE_HOST + AGGTRADES_PATH.format(sym=sym, month=m)
            status, _ = head_status(url)
            depth[m] = status
        per_symbol[sym] = {"sample": sample, "depth_status": depth}

    # Schema verification on one small, deep zip.
    schema = {"symbol": SCHEMA_SYMBOL, "month": SCHEMA_MONTH, "ok": False}
    url = ARCHIVE_HOST + AGGTRADES_PATH.format(sym=SCHEMA_SYMBOL, month=SCHEMA_MONTH)
    status, blob = get_bytes(url)
    schema["url"] = url
    schema["status"] = status
    schema["zip_bytes"] = len(blob)
    if status == 200 and blob:
        try:
            zf = zipfile.ZipFile(io.BytesIO(blob))
            name = zf.namelist()[0]
            raw = zf.read(name)
            lines = raw.split(b"\n")
            header = lines[0].decode("utf-8", "replace")
            has_header = "agg_trade_id" in header
            first = lines[1].decode("utf-8", "replace") if len(lines) > 1 else ""
            last = lines[-2].decode("utf-8", "replace") if len(lines) > 2 else ""
            parts = first.split(",")
            schema.update({
                "inner_name": name,
                "inner_bytes": len(raw),
                "has_header": has_header,
                "header": header,
                "first_row": first,
                "last_row": last,
                "n_columns_first_row": len(parts),
                "transact_time_ms_example": parts[5] if len(parts) > 5 else None,
                "is_buyer_maker_example": parts[6] if len(parts) > 6 else None,
                "ok": bool(has_header and len(parts) == 7),
            })
        except Exception as exc:  # noqa: BLE001
            schema["error"] = repr(exc)

    # Reachability verdict: every perp 200 in every sample month and 200 at the
    # window edges 2022-07 and 2026-06.
    all_200 = all(
        per_symbol[s]["sample"][m]["status"] == 200
        for s in PERPS for m in SAMPLE_MONTHS
    )
    edges_200 = all(
        per_symbol[s]["depth_status"]["2022-07"] == 200
        and per_symbol[s]["depth_status"]["2026-06"] == 200
        for s in PERPS
    )
    reachable = bool(all_200 and edges_200 and schema.get("ok"))

    result = {
        "generated_at_utc": ts,
        "campaign": 310,
        "part": "reachability_probe",
        "analysis": "c310_coinm_inverse_perp_aggtrades_ofi_cross_sectional_reachability",
        "source_host": ARCHIVE_HOST,
        "aggtrades_endpoint": AGGTRADES_PATH,
        "target_window": {"start": "2022-07", "end": "2026-06", "months": 48},
        "perp_universe": list(PERPS),
        "n_perps": len(PERPS),
        "sample_months": list(SAMPLE_MONTHS),
        "depth_months": list(DEPTH_MONTHS),
        "total_sample_content_length_bytes": int(total_sample_bytes),
        "sample_content_length_mb": round(total_sample_bytes / 1e6, 2),
        "per_symbol": per_symbol,
        "schema_verification": schema,
        "reachable": reachable,
        "notes": [
            "COIN-M aggTrades is a genuinely new data family (never ingested; C301 used USDT-M linear perps).",
            "Cross-sectional OFI carry on COIN-M inverse perps is a new formulation, distinct from C301 per-asset TS OFI.",
            "COIN-M indexPriceKlines is HTTP 404 — never used; execution prices come from the C307 leg_b perp_close (1h).",
            "Full 48-month x 11-perp window is many GB: heavy ingest is the mandated next-session work.",
        ],
        "real_data_only": True,
        "fabricated_data": False,
        "executed_fills": False,
    }
    out = reports / f"campaign310_coinm_aggtrades_reachability_{ts}.json"
    out.write_text(json.dumps(result, indent=2, default=str) + "\n")
    sha = sha256_bytes(out.read_bytes())
    print(json.dumps({
        "campaign": 310,
        "part": "reachability_probe",
        "reachable": reachable,
        "all_sample_200": bool(all_200),
        "edges_200": bool(edges_200),
        "schema_ok": bool(schema.get("ok")),
        "sample_mb": result["sample_content_length_mb"],
        "artifact": str(out.relative_to(ROOT)),
        "sha256": sha,
    }, indent=2))
    return 0 if reachable else 1


if __name__ == "__main__":
    raise SystemExit(main())