#!/usr/bin/env python3
"""C291 — capability probe for the NEW derivatives data source (fail-closed).

The prior handoff recorded derivatives data as BLOCKED because
``fapi.binance.com`` answers HTTP 451 from this egress.  That conclusion was
incomplete: the Binance public-data archive host ``data.binance.vision`` serves
USDT-M futures monthly klines and funding-rate archives (not the fapi REST API)
and is reachable from this environment.  This probe records that capability
evidence before the C291 campaign ingests anything.

It performs read-only HTTP HEAD/GET probes and writes a timestamped JSON report
with SHA256-from-bytes.  It never downloads or fabricates market data, never
writes to the cache, and never edits frozen artifacts.

Probes:
- USDT-M futures 5m kline archives for the 26 C290 spot symbols x 2026-08/09/10:
  ``data/futures/um/monthly/klines/<SYM>/5m/<SYM>-5m-YYYY-MM.zip``
- USDT-M funding-rate archives for the same symbols/months:
  ``data/futures/um/monthly/fundingRate/<SYM>/<SYM>-fundingRate-YYYY-MM.zip``
- Known-blocked routes (recorded, not retried): fapi ping, testnet ping,
  api.binance.com ping.
- Fallback cross-venue spot history endpoints (recorded for a possible C292):
  OKX history-candles, Coinbase candles, Kraken OHLC.

Ready is true iff at least MIN_READY_SYMBOLS symbols have both kline and funding
archives present for every month (fail-closed).  Exit 0 iff ready.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
META_290 = ROOT / "data" / "cache" / "campaign290_ohlcv.meta.json"

ARCHIVE_HOST = "https://data.binance.vision"
MONTHS = ("2026-08", "2026-09", "2026-10")
KINDS = ("klines", "funding")
MIN_READY_SYMBOLS = 10  # >= 2K for K=5; pre-registered readiness floor

BLOCKED_ROUTES = (
    ("fapi_ping", "https://fapi.binance.com/fapi/v1/ping"),
    ("testnet_ping", "https://testnet.binance.vision/api/v3/ping"),
    ("api_binance_ping", "https://api.binance.com/api/v3/ping"),
)
FALLBACK_VENUES = (
    ("okx_history_candles", "https://www.okx.com/api/v5/market/history-candles?instId=BTC-USDT&bar=5m&limit=2"),
    ("coinbase_candles", "https://api.exchange.coinbase.com/products/BTC-USD/candles?granularity=300"),
    ("kraken_ohlc", "https://api.kraken.com/0/public/OHLC?pair=XBTUSD&interval=5"),
)


def kline_url(symbol: str, month: str) -> str:
    return f"{ARCHIVE_HOST}/data/futures/um/monthly/klines/{symbol}/5m/{symbol}-5m-{month}.zip"


def funding_url(symbol: str, month: str) -> str:
    return f"{ARCHIVE_HOST}/data/futures/um/monthly/fundingRate/{symbol}/{symbol}-fundingRate-{month}.zip"


def classify(status: int, content_length: int | None) -> dict:
    if status == 200:
        return {"ok": True, "reason": "present"}
    if status == 404:
        return {"ok": False, "reason": "not_found"}
    if status in (451, 403):
        return {"ok": False, "reason": "blocked"}
    return {"ok": False, "reason": f"http_{status}"}


def _urllib_probe(url: str, method: str, timeout: float) -> tuple[int, dict, bytes]:
    req = urllib.request.Request(url, method=method, headers={"User-Agent": "kilo-c291-probe"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(256) if method != "HEAD" else b""
            return int(resp.status), dict(resp.headers), body
    except urllib.error.HTTPError as exc:
        body = b""
        try:
            body = exc.read(256)
        except Exception:  # noqa: BLE001
            body = b""
        return int(exc.code), dict(exc.headers or {}), body


def probe_url(
    url: str,
    *,
    method: str = "HEAD",
    timeout: float = 20.0,
    opener: Callable[[str, str, float], tuple[int, dict, bytes]] | None = None,
) -> dict:
    op = opener or _urllib_probe
    status, headers, body = op(url, method, timeout)
    length = headers.get("Content-Length") or headers.get("content-length")
    try:
        length_val = int(length) if length is not None else None
    except (TypeError, ValueError):
        length_val = None
    out = {
        "url": url,
        "status": int(status),
        "content_length": length_val,
        "body_prefix": body[:160].decode("utf-8", "replace"),
    }
    out.update(classify(int(status), length_val))
    return out


def probe_symbol(
    symbol: str,
    months: tuple[str, ...],
    *,
    timeout: float = 20.0,
    opener: Callable[[str, str, float], tuple[int, dict, bytes]] | None = None,
) -> dict:
    detail: dict = {"symbol": symbol, "months": {}}
    fully = True
    for month in months:
        detail["months"][month] = {
            "klines": probe_url(kline_url(symbol, month), timeout=timeout, opener=opener),
            "funding": probe_url(funding_url(symbol, month), timeout=timeout, opener=opener),
        }
        for kind in KINDS:
            if not detail["months"][month][kind]["ok"]:
                fully = False
    detail["fully_reachable"] = bool(fully)
    return detail


def probe_all(
    symbols: list[str],
    months: tuple[str, ...],
    *,
    timeout: float = 20.0,
    workers: int = 8,
    opener: Callable[[str, str, float], tuple[int, dict, bytes]] | None = None,
) -> list[dict]:
    with ThreadPoolExecutor(max_workers=max(1, int(workers))) as pool:
        return list(pool.map(lambda s: probe_symbol(s, months, timeout=timeout, opener=opener), symbols))


def load_symbols() -> list[str]:
    if not META_290.exists():
        raise SystemExit(f"FATAL: C290 meta missing, cannot establish C291 universe: {META_290}")
    meta = json.loads(META_290.read_text())
    symbols = list(meta.get("symbols") or [])
    if not symbols:
        raise SystemExit("FATAL: C290 meta has no symbols")
    return symbols


def build_report(
    symbols: list[str],
    months: tuple[str, ...],
    *,
    workers: int = 8,
    timeout: float = 20.0,
    opener: Callable[[str, str, float], tuple[int, dict, bytes]] | None = None,
) -> dict:
    per_symbol = probe_all(symbols, months, timeout=timeout, workers=workers, opener=opener)
    reachable = [d["symbol"] for d in per_symbol if d["fully_reachable"]]
    missing = [d["symbol"] for d in per_symbol if not d["fully_reachable"]]
    blocked = []
    for name, url in BLOCKED_ROUTES:
        r = probe_url(url, method="GET", timeout=timeout, opener=opener)
        r["route"] = name
        blocked.append(r)
    fallback = []
    for name, url in FALLBACK_VENUES:
        r = probe_url(url, method="GET", timeout=timeout, opener=opener)
        r["route"] = name
        fallback.append(r)
    ready = bool(len(reachable) >= MIN_READY_SYMBOLS)
    return {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "campaign": 291,
        "part": "derivatives_reachability_probe",
        "analysis": "new_derivatives_data_source_capability",
        "real_data_only": True,
        "fabricated_data": False,
        "source_host": ARCHIVE_HOST,
        "months": list(months),
        "readiness_floor_symbols": MIN_READY_SYMBOLS,
        "symbols": symbols,
        "per_symbol": per_symbol,
        "reachable_symbols": reachable,
        "missing_symbols": missing,
        "blocked_routes": blocked,
        "fallback_venues": fallback,
        "summary": {
            "n_symbols": len(symbols),
            "n_fully_reachable": len(reachable),
            "n_missing": len(missing),
            "any_kline_reachable": any(
                d["months"][m]["klines"]["ok"] for d in per_symbol for m in d["months"]
            ),
            "any_funding_reachable": any(
                d["months"][m]["funding"]["ok"] for d in per_symbol for m in d["months"]
            ),
        },
        "ready": ready,
    }


def write_report(report: dict, out_dir: Path) -> tuple[Path, str]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    op = out_dir / f"campaign291_derivatives_reachability_{report['generated_at_utc']}.json"
    raw = (json.dumps(report, indent=2, default=str) + "\n").encode()
    op.write_bytes(raw)
    return op, hashlib.sha256(raw).hexdigest()


def main(
    argv: list[str] | None = None,
    opener: Callable[[str, str, float], tuple[int, dict, bytes]] | None = None,
    symbols: list[str] | None = None,
) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true", help="print the report summary as JSON")
    ap.add_argument("--reports-dir", default=str(REPORTS))
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--timeout", type=float, default=20.0)
    args = ap.parse_args(argv)

    syms = list(symbols) if symbols is not None else load_symbols()
    report = build_report(syms, MONTHS, workers=args.workers, timeout=args.timeout, opener=opener)
    op, sha = write_report(report, Path(args.reports_dir))
    report["artifact"] = str(op.relative_to(ROOT)) if op.is_relative_to(ROOT) else str(op)
    report["artifact_sha256"] = sha
    print(
        json.dumps(
            {k: report[k] for k in ("ready", "summary", "artifact", "artifact_sha256")},
            indent=2,
        )
    )
    return 0 if report["ready"] else 2


if __name__ == "__main__":
    sys.exit(main())