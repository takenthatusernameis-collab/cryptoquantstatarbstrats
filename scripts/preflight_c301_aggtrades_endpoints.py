#!/usr/bin/env python3
"""C301 endpoint preflight: fail-closed HTTP HEAD verification of the six real
Binance USDT-M perpetual ``aggTrades`` monthly zips that feed the C301
order-flow-imbalance / trade-sign-autocorrelation per-asset time-series
stat-arb campaign (2023-01 .. 2023-02).

Bounded window (verified live this session, 2026-11-14):

- Source: ``https://data.binance.vision/data/futures/um/monthly/aggTrades/<SYM>/<SYM>-aggTrades-YYYY-MM.zip``
  (USDT-M perp; the ``fapi`` REST API is HTTP 451 and is not used).
- Universe: C299/C300's verified {BTCUSDT, ETHUSDT, BCHUSDT}.
- Months: 2023-01, 2023-02 (contiguous, 59 days, 16,992 native 5m bars).
- Exactly 6 zips, expected total 1,603,901,702 bytes:
    BTCUSDT 2023-01: 388,543,348 B
    ETHUSDT 2023-01: 349,468,307 B
    BCHUSDT 2023-01: 47,530,509 B
    BTCUSDT 2023-02: 432,051,041 B
    ETHUSDT 2023-02: 341,631,000 B
    BCHUSDT 2023-02: 44,677,497 B

The script only performs HTTP HEAD requests; it never downloads a body,
never imputes, never fabricates. Exit 0 iff every endpoint is HTTP 200 and the
Content-Length matches the recorded byte size exactly (ready:true). Any 404 /
451 / size mismatch is a fail-closed blocker with a recorded reason.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ARCHIVE_HOST = "https://data.binance.vision"
AGGTRADES_PATH = "/data/futures/um/monthly/aggTrades/{sym}/{sym}-aggTrades-{month}.zip"

UNIVERSE = ("BTCUSDT", "ETHUSDT", "BCHUSDT")
MONTHS = ("2023-01", "2023-02")

# Recorded expected byte sizes (verified live 2026-11-14T18:36Z, HTTP HEAD 200).
EXPECTED_BYTES = {
    ("BTCUSDT", "2023-01"): 388_543_348,
    ("ETHUSDT", "2023-01"): 349_468_307,
    ("BCHUSDT", "2023-01"): 47_530_509,
    ("BTCUSDT", "2023-02"): 432_051_041,
    ("ETHUSDT", "2023-02"): 341_631_000,
    ("BCHUSDT", "2023-02"): 44_677_497,
}

EXPECTED_TOTAL_BYTES = sum(EXPECTED_BYTES.values())  # 1,603,901,702


def sha256_file(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


def _head(url: str, timeout: float) -> tuple[int, int | None, str]:
    """Return (status, content_length, reason). Never reads a body."""
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "kilo-c301-preflight"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return int(resp.status), (int(resp.headers["Content-Length"]) if resp.headers.get("Content-Length") else None), "ok"
    except urllib.error.HTTPError as exc:
        return int(exc.code), None, f"http_{exc.code}"
    except Exception as exc:  # noqa: BLE001
        return 0, None, f"{type(exc).__name__}: {exc}"


def endpoint_url(sym: str, month: str) -> str:
    return ARCHIVE_HOST + AGGTRADES_PATH.format(sym=sym, month=month)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--timeout", type=float, default=30.0)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    endpoints: list[dict] = []
    blocked: list[str] = []
    for sym in UNIVERSE:
        for month in MONTHS:
            url = endpoint_url(sym, month)
            status, clen, reason = _head(url, args.timeout)
            expected = EXPECTED_BYTES[(sym, month)]
            size_ok = clen is not None and int(clen) == int(expected)
            ok = status == 200 and size_ok
            if not ok:
                blocked.append(f"{sym} {month}: status={status} reason={reason} content_length={clen} expected={expected}")
            endpoints.append({
                "symbol": sym,
                "month": month,
                "url": url,
                "status": status,
                "content_length": clen,
                "expected_bytes": int(expected),
                "size_ok": bool(size_ok),
                "ok": bool(ok),
            })

    total_expected = EXPECTED_TOTAL_BYTES
    total_recorded = int(sum(int(e["content_length"]) for e in endpoints if e["content_length"]))
    all_ok = not blocked and total_recorded == total_expected

    result = {
        "ready": bool(all_ok),
        "real_data_only": True,
        "fabricated_data": False,
        "executed_fills": False,
        "campaign": 301,
        "part": "preflight_aggtrades_endpoints",
        "generated_at_utc": ts,
        "source_host": ARCHIVE_HOST,
        "endpoint_template": AGGTRADES_PATH,
        "universe": list(UNIVERSE),
        "months": list(MONTHS),
        "n_endpoints": len(endpoints),
        "n_ok": sum(1 for e in endpoints if e["ok"]),
        "expected_total_bytes": int(total_expected),
        "recorded_total_bytes": int(total_recorded),
        "total_bytes_ok": bool(total_recorded == total_expected),
        "endpoints": endpoints,
        "blocked_reasons": blocked,
        "http_method": "HEAD (no body downloaded)",
    }
    print(json.dumps(result, indent=2))
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())