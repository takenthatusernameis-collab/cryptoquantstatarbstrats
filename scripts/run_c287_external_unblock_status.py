#!/usr/bin/env python3
"""C287 external-unblock status probe (fail-closed, deterministic record).

Records reachability for blocked/unblocked routes relevant to C287 and emits a
timestamped JSON artifact. No credentials used, no fills/orders, no fabricated
data. If routes remain 451/403/unreachable or credentials absent, status is
BLOCKED with explicit external action required.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import socket
import ssl
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"

ROUTES = [
    {"name": "binance_testnet_rest_ping", "url": "https://testnet.binance.vision/api/v3/ping", "kind": "blocked_candidate"},
    {"name": "binance_testnet_rest_time", "url": "https://testnet.binance.vision/api/v3/time", "kind": "blocked_candidate"},
    {"name": "binance_testnet_rest_exchangeInfo", "url": "https://testnet.binance.vision/api/v3/exchangeInfo", "kind": "blocked_candidate"},
    {"name": "fapi_ping", "url": "https://fapi.binance.com/fapi/v1/ping", "kind": "blocked_candidate"},
    {"name": "api_bybit_v5_time", "url": "https://api.bybit.com/v5/market/time", "kind": "blocked_candidate"},
    {"name": "deribit_public_time", "url": "https://www.deribit.com/api/v2/public/get_time", "kind": "reachable_candidate"},
    {"name": "binance_data_api_time", "url": "https://data-api.binance.vision/api/v3/time", "kind": "reachable_candidate"},
    {"name": "okx_time", "url": "https://www.okx.com/api/v5/public/time", "kind": "reachable_candidate"},
    {"name": "coinbase_time", "url": "https://api.exchange.coinbase.com/time", "kind": "reachable_candidate"},
]

WS_PROBES = [
    {"name": "binance_testnet_ws", "host": "stream.testnet.binance.vision", "port": 9443},
]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def probe_http(url: str, timeout: float = 10.0):
    t0 = time.time()
    req = urllib.request.Request(url, headers={"User-Agent": "c287-unblock-probe/1.0"})
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            body = resp.read(256)
            return {
                "ok": 200 <= resp.status < 300,
                "status": resp.status,
                "latency_ms": round((time.time() - t0) * 1000.0, 2),
                "body_prefix": body[:120].decode("utf-8", "replace"),
                "error": None,
            }
    except Exception as e:  # noqa: BLE001
        status = getattr(e, "code", None)
        body = b""
        try:
            body = e.read(256)  # type: ignore[attr-defined]
        except Exception:
            pass
        return {
            "ok": False,
            "status": status,
            "latency_ms": round((time.time() - t0) * 1000.0, 2),
            "body_prefix": body[:120].decode("utf-8", "replace") if body else "",
            "error": f"{type(e).__name__}: {e}",
        }


def probe_ws(host: str, port: int, timeout: float = 10.0):
    t0 = time.time()
    try:
        addrinfos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
        addr = addrinfos[0][4]
        with socket.create_connection(addr, timeout=timeout) as sock:
            ctx = ssl.create_default_context()
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                proto = ssock.version()
        return {"ok": True, "tls": proto, "latency_ms": round((time.time() - t0) * 1000.0, 2), "error": None}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "tls": None, "latency_ms": round((time.time() - t0) * 1000.0, 2), "error": f"{type(e).__name__}: {e}"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ts", default=None)
    ap.add_argument("--timeout", type=float, default=10.0)
    args = ap.parse_args()
    ts = args.ts or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    http_results = []
    for r in ROUTES:
        res = probe_http(r["url"], timeout=args.timeout)
        http_results.append({**r, **res})

    ws_results = []
    for w in WS_PROBES:
        res = probe_ws(w["host"], w["port"], timeout=args.timeout)
        ws_results.append({**w, **res})

    key_present = bool(os.environ.get("BINANCE_TESTNET_API_KEY"))
    secret_present = bool(os.environ.get("BINANCE_TESTNET_API_SECRET"))
    creds_present = key_present and secret_present

    blocked_reasons = []
    for r in http_results:
        if r["kind"] == "blocked_candidate":
            if r["status"] in (451, 403) or not r["ok"]:
                blocked_reasons.append(f"{r['name']}:{r['status'] or r['error']}")
    if not creds_present:
        blocked_reasons.append("missing_env_credentials:BINANCE_TESTNET_API_KEY_and_or_SECRET")

    still_blocked = len(blocked_reasons) > 0
    status = "BLOCKED" if still_blocked else "UNBLOCKED_CANDIDATE_REQUIRES_FURTHER_VERIFICATION"

    report = {
        "artifact": "c287_external_unblock_status",
        "generated_at_utc": ts,
        "real_data_only": True,
        "fabricated_data": False,
        "campaign": "C287",
        "decoupled_from_economic_progress": True,
        "status": status,
        "still_blocked": still_blocked,
        "credentials": {
            "BINANCE_TESTNET_API_KEY_present": key_present,
            "BINANCE_TESTNET_API_SECRET_present": secret_present,
        },
        "blocked_routes_expected": ["fapi.binance.com", "testnet.binance.vision", "api.bybit.com"],
        "http_probes": http_results,
        "ws_probes": ws_results,
        "blocked_reasons": blocked_reasons,
        "external_action_required": [
            "Provide valid Binance Spot Testnet credentials (BINANCE_TESTNET_API_KEY/SECRET) in environment",
            "Provide network egress not subject to Binance testnet 451 geographic block (non-451 route to testnet.binance.vision/fapi as applicable)",
        ] if still_blocked else [],
        "note": "Fail-closed probe record. No credentials used, no orders/fills placed, no fabricated data. C287 remains BLOCKED/DECOUPLED unless external credentials and non-451 egress are provided.",
    }

    REPORTS.mkdir(exist_ok=True)
    out_path = REPORTS / f"c287_external_unblock_status_{ts}.json"
    out_path.write_bytes(json.dumps(report, indent=2, sort_keys=True).encode("utf-8"))
    result = {
        "path": str(out_path.relative_to(ROOT)),
        "sha256": sha256_file(out_path),
        "status": status,
        "still_blocked": still_blocked,
        "blocked_reasons": blocked_reasons,
        "real_data_only": True,
        "fabricated_data": False,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
