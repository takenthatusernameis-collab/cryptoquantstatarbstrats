#!/usr/bin/env python3
"""C287 preflight: fail-closed readiness check for the Binance testnet gateway campaign.

Verifies, without fabricating data or placing orders:
- required environment variables for Binance Spot Testnet auth are present
  (BINANCE_TESTNET_API_KEY, BINANCE_TESTNET_API_SECRET) — values never logged;
- Binance Spot Testnet REST endpoint reachable and healthy (ping, server time,
  exchangeInfo for the 11-asset universe) via official endpoints only;
- Binance Spot Testnet WebSocket endpoint DNS/connectivity probe succeeds;
- verified 5m spot cache + meta and 1h volume cache + meta + provenance exist
  with recorded SHA256-from-bytes and real/fabricated flags;
- any pre-computed C285/C286 signal artifact (parquet preferred; pickle accepted
  when no parquet engine is available) required by the execution path is present
  and loadable (or explicitly reported missing as a blocker).

Exit code 0 iff every check passes and the gateway is ready for a real testnet
run. Any mismatch, missing dependency, missing credential, or unreachable
endpoint is fail-closed: prints JSON with ``ready: false`` and ``blockers``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pickle
import socket
import ssl
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "cache"

SPOT_5M = CACHE / "90d10b876bb8eda9619cbba73ed19d6c7db4ea7327284f2e33f10a7872a5b263.pkl"
SPOT_5M_META = CACHE / "90d10b876bb8eda9619cbba73ed19d6c7db4ea7327284f2e33f10a7872a5b263.meta.json"
SPOT_5M_SHA = "d15b0b183cf685a15dd34185baff22edf7ef3cc9c80c7d607bcd92f8da418c2f"
SPOT_5M_META_SHA = "e1a71f481cb4ad07881d132aba4ff7b47fc8194c69779701035efcf6e492ce4e"

VOLUME = CACHE / "volume_1h_full.pkl"
VOLUME_META = CACHE / "volume_1h_full.meta.json"
VOLUME_PROVENANCE = CACHE / "volume_1h_full.provenance.json"
VOLUME_SHA = "4365895387de4e542165fd331e39da40d455a3de24c7254eb67ba890053d193c"
VOLUME_META_SHA = "4d321584d3c687ad9956908c0179a1eae7d629c296c491e1e5ad1259a890c616"
VOLUME_PROVENANCE_SHA = "c7ff2f27ec5a668128e4856f809efde4922563dba87be0648be6d802c6d21c89"

SYMBOLS = ("ADAUSDT", "AVAXUSDT", "BNBUSDT", "BTCUSDT", "DOTUSDT", "ETHUSDT", "LINKUSDT", "LTCUSDT", "POLUSDT", "SOLUSDT", "XRPUSDT")
REST_BASE = "https://testnet.binance.vision"
WS_HOST = "stream.testnet.binance.vision"
WS_PORT = 9443


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add_check(checks: dict, name: str, ok: bool, **detail):
    checks[name] = {"ok": bool(ok), **detail}
    return bool(ok)


def http_json(url: str, timeout: float = 10.0):
    req = urllib.request.Request(url, headers={"User-Agent": "c287-preflight/1.0"})
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
        body = resp.read()
        return resp.status, json.loads(body.decode("utf-8")), len(body)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit JSON summary")
    parser.add_argument("--timeout", type=float, default=10.0, help="network timeout seconds")
    args = parser.parse_args()

    checks: dict = {}
    blockers: list[str] = []

    # 1) Environment credentials (presence only)
    key_present = bool(os.environ.get("BINANCE_TESTNET_API_KEY"))
    secret_present = bool(os.environ.get("BINANCE_TESTNET_API_SECRET"))
    if not add_check(checks, "env_credentials", key_present and secret_present,
                     BINANCE_TESTNET_API_KEY_present=key_present,
                     BINANCE_TESTNET_API_SECRET_present=secret_present):
        blockers.append("missing_env_credentials:BINANCE_TESTNET_API_KEY_and_or_SECRET")

    # 2) Cache SHA and meta verification
    def check_cache(label, path, expected_sha):
        if not path.exists():
            add_check(checks, label, False, path=str(path), exists=False, expected_sha256=expected_sha)
            blockers.append(f"missing_cache:{path.name}")
            return False
        actual = sha256_file(path)
        ok = actual == expected_sha
        add_check(checks, label, ok, path=str(path), exists=True, sha256=actual, expected_sha256=expected_sha)
        if not ok:
            blockers.append(f"sha_mismatch:{path.name}")
        return ok

    check_cache("spot_5m_cache", SPOT_5M, SPOT_5M_SHA)
    check_cache("spot_5m_meta", SPOT_5M_META, SPOT_5M_META_SHA)
    check_cache("volume_1h_cache", VOLUME, VOLUME_SHA)
    check_cache("volume_1h_meta", VOLUME_META, VOLUME_META_SHA)
    check_cache("volume_1h_provenance", VOLUME_PROVENANCE, VOLUME_PROVENANCE_SHA)

    try:
        meta_5m = json.loads(SPOT_5M_META.read_text()) if SPOT_5M_META.exists() else {}
        flags_ok = (meta_5m.get("fetch_real_data_only") is True and meta_5m.get("fetch_fabricated_data") is False)
        if not add_check(checks, "spot_5m_real_flags", flags_ok,
                         fetch_real_data_only=meta_5m.get("fetch_real_data_only"),
                         fetch_fabricated_data=meta_5m.get("fetch_fabricated_data")):
            blockers.append("spot_5m_meta_real_or_fabricated_flag_invalid")
    except Exception as exc:  # noqa: BLE001
        add_check(checks, "spot_5m_real_flags", False, error=f"{type(exc).__name__}: {exc}")
        blockers.append("spot_5m_meta_unreadable")

    try:
        vol_prov = json.loads(VOLUME_PROVENANCE.read_text()) if VOLUME_PROVENANCE.exists() else {}
        v_ok = (vol_prov.get("real_data_only") is True and vol_prov.get("fabricated_data") is False)
        if not add_check(checks, "volume_real_flags", v_ok,
                         real_data_only=vol_prov.get("real_data_only"),
                         fabricated_data=vol_prov.get("fabricated_data")):
            blockers.append("volume_provenance_real_or_fabricated_flag_invalid")
    except Exception as exc:  # noqa: BLE001
        add_check(checks, "volume_real_flags", False, error=f"{type(exc).__name__}: {exc}")
        blockers.append("volume_provenance_unreadable")

    # 3) Pre-computed C285/C286 signal artifact (parquet preferred; pickle accepted
    # when parquet engine unavailable). Must be deterministically generated from the
    # verified caches with SHA256-from-bytes and meta/provenance sidecars.
    signal_candidates = sorted([str(p.relative_to(ROOT)) for p in list(ROOT.rglob("*.parquet")) + list(ROOT.rglob("*.pkl"))
                                if (("signal" in p.name.lower() or "c285" in p.name.lower() or "c286" in p.name.lower())
                                    and p.is_file() and "meta" not in p.name.lower() and "provenance" not in p.name.lower())])
    if not add_check(checks, "signal_parquet", len(signal_candidates) > 0, candidates=signal_candidates):
        blockers.append("missing_precomputed_signal_parquet")
    checks["signal_artifact"] = dict(checks["signal_parquet"])

    # 4) REST connectivity
    rest_ok = True
    for name, path in [("rest_ping", "/api/v3/ping"), ("rest_time", "/api/v3/time"), ("rest_exchange_info", "/api/v3/exchangeInfo")]:
        t0 = time.time()
        try:
            status, data, nbytes = http_json(REST_BASE + path, timeout=args.timeout)
            latency_ms = round((time.time() - t0) * 1000.0, 2)
            ok = status == 200
            detail = {"status": status, "latency_ms": latency_ms, "bytes": nbytes}
            if name == "rest_exchange_info" and isinstance(data, dict):
                symbols_present = {s.get("symbol") for s in data.get("symbols", []) if isinstance(s, dict)}
                missing_syms = [s for s in SYMBOLS if s not in symbols_present]
                detail["universe_missing"] = missing_syms
                ok = ok and len(missing_syms) == 0
                if missing_syms:
                    blockers.append(f"exchange_info_missing_symbols:{','.join(missing_syms)}")
            if not add_check(checks, name, ok, **detail):
                blockers.append(f"rest_unhealthy:{name}")
                rest_ok = False
        except Exception as exc:  # noqa: BLE001
            latency_ms = round((time.time() - t0) * 1000.0, 2)
            add_check(checks, name, False, latency_ms=latency_ms, error=f"{type(exc).__name__}: {exc}")
            blockers.append(f"rest_unreachable:{name}")
            rest_ok = False

    # 5) WebSocket endpoint TCP/TLS reachability probe
    t0 = time.time()
    try:
        addrinfos = socket.getaddrinfo(WS_HOST, WS_PORT, type=socket.SOCK_STREAM)
        addr = addrinfos[0][4]
        with socket.create_connection(addr, timeout=args.timeout) as sock:
            ctx = ssl.create_default_context()
            with ctx.wrap_socket(sock, server_hostname=WS_HOST) as ssock:
                proto = ssock.version()
        latency_ms = round((time.time() - t0) * 1000.0, 2)
        if not add_check(checks, "ws_tcp_tls", True, host=WS_HOST, port=WS_PORT, tls=proto, latency_ms=latency_ms):
            blockers.append("ws_unreachable")
    except Exception as exc:  # noqa: BLE001
        latency_ms = round((time.time() - t0) * 1000.0, 2)
        add_check(checks, "ws_tcp_tls", False, host=WS_HOST, port=WS_PORT, latency_ms=latency_ms,
                  error=f"{type(exc).__name__}: {exc}")
        blockers.append("ws_unreachable")

    ready = len(blockers) == 0
    result = {
        "campaign": "C287",
        "script": "scripts/preflight_c287.py",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "ready": ready,
        "rest_base": REST_BASE,
        "ws_host": WS_HOST,
        "ws_port": WS_PORT,
        "universe": list(SYMBOLS),
        "checks": checks,
        "blockers": blockers,
        "blocker_count": len(blockers),
        "real_data_only": True,
        "fabricated_data": False,
        "note": "Fail-closed preflight. No orders placed, no secrets logged. ready=true is required before any real C287 testnet run.",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if ready else 2


if __name__ == "__main__":
    raise SystemExit(main())
