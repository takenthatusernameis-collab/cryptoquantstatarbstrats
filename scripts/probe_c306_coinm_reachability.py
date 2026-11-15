#!/usr/bin/env python3
"""C306 reachability prober — COIN-M (inverse / coin-margined) futures term structure.

Why this probe exists (bottleneck removal):
  The C305 "reachability exhaustion" probe only swept `futures/um` (USDT-M linear) and
  `spot/monthly`. It never touched `futures/cm` (COIN-M inverse). COIN-M is a genuinely
  different contract family: inverse settlement (PnL in coin, non-linear), dated
  quarterly futures that trade alongside a perpetual, and a calendar term-structure
  (basis) that is NOT consumed by any C281B-C305 campaign. This prober records, with
  timestamped HTTP evidence, whether that family is reachable and how deep.

Design constraints (repo non-negotiables):
  * stdlib only (urllib/json/hashlib/time) so it runs in the CI worker BEFORE the
    numpy/pandas/pytest bootstrap -- a missing-dependency run is never an excuse.
  * fail-closed: an endpoint counts as reachable only on HTTP 200; every 404/5xx/ERR
    is recorded with attempts + timestamps, never guessed.
  * retry-with-backoff: the archive host flip-flops 200<->404 under rapid access; a
    lone 404 is retryable, only exhausting all attempts records a definitive miss.
  * real_data_only:true, fabricated_data:false, executed_fills:false.

Outputs:
  data/cache/campaign306_coinm_reachability.json        (machine cache)
  data/cache/campaign306_coinm_reachability.provenance.json
  reports/c306_coinm_reachability_probe_<ts>.json       (evidence report)

Usage:
  python scripts/probe_c306_coinm_reachability.py [--json-out PATH] [--no-network]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import ssl
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://data.binance.vision"
REPO = Path(__file__).resolve().parent.parent

# COIN-M inverse perpetuals (BASEUSD_PERP, not BASEUSDT). EOSUSD_PERP is 404.
CM_PERPS = [
    "BTCUSD_PERP", "ETHUSD_PERP", "ADAUSD_PERP", "LTCUSD_PERP", "XRPUSD_PERP",
    "BCHUSD_PERP", "LINKUSD_PERP", "TRXUSD_PERP", "ETCUSD_PERP", "XLMUSD_PERP",
    "DOTUSD_PERP",
]

# Coverage months (depth + recency). COIN-M starts ~2020-12.
COIN_M_MONTHS = ["2020-12", "2021-06", "2022-01", "2023-01", "2024-01", "2025-01", "2026-06", "2026-10"]

# COIN-M inverse perpetual families on the monthly archive.
CM_PERP_FAMILIES = [
    ("klines_1h", "/data/futures/cm/monthly/klines/{s}/1h/{s}-1h-{m}.zip"),
    ("premiumIndexKlines_1h", "/data/futures/cm/monthly/premiumIndexKlines/{s}/1h/{s}-1h-{m}.zip"),
    ("markPriceKlines_1h", "/data/futures/cm/monthly/markPriceKlines/{s}/1h/{s}-1h-{m}.zip"),
    ("indexPriceKlines_1h", "/data/futures/cm/monthly/indexPriceKlines/{s}/1h/{s}-1h-{m}.zip"),
    ("fundingRate", "/data/futures/cm/monthly/fundingRate/{s}/{s}-fundingRate-{m}.zip"),
    ("aggTrades", "/data/futures/cm/monthly/aggTrades/{s}/{s}-aggTrades-{m}.zip"),
]

# COIN-M inverse DATED quarterly futures. Each contract's monthly archives are
# retained after expiry (verified), so a multi-cycle term-structure series is
# reconstructible from public archives.
CM_QUARTERLY = [
    ("BTCUSD_250627", ["2025-03", "2025-04", "2025-05", "2025-06"]),
    ("BTCUSD_250926", ["2025-09", "2025-10"]),
    ("BTCUSD_261225", ["2026-09", "2026-10"]),
    ("ETHUSD_261225", ["2026-10"]),
]


def _ctx() -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def probe_url(url: str, attempts: int = 5, timeout: float = 20.0) -> dict:
    """GET headers-only with retry-with-backoff; returns status + attempts + timing."""
    ctx = _ctx()
    backoff = 0.6
    last: dict = {}
    started = _now()
    for attempt in range(1, attempts + 1):
        t0 = time.time()
        try:
            req = urllib.request.Request(
                url, method="GET", headers={"User-Agent": "Mozilla/5.0 (c306-probe)"}
            )
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
                status = int(r.status)
                clen = r.headers.get("Content-Length", "?")
                r.close()
            dt = round(time.time() - t0, 3)
            if status == 200:
                return {
                    "url": url, "status": status, "content_length": clen,
                    "attempts": attempt, "started_utc": started,
                    "finished_utc": _now(), "elapsed_s": dt, "reachable": True,
                }
            last = {"status": status, "attempts": attempt}
        except urllib.error.HTTPError as e:
            last = {"status": int(e.code), "attempts": attempt}
        except Exception as e:  # noqa: BLE001 - record transport error, fail-closed
            last = {"status": "ERR", "error": str(e)[:160], "attempts": attempt}
        if attempt < attempts:
            time.sleep(round(backoff * attempt, 3))
    return {
        "url": url, "status": last.get("status", "ERR"),
        "error": last.get("error"), "content_length": None, "attempts": attempts,
        "started_utc": started, "finished_utc": _now(), "elapsed_s": None,
        "reachable": False,
    }


def run_matrix(no_network: bool = False) -> list[dict]:
    rows: list[dict] = []

    def record(bucket: str, family: str, asset: str, month: str, tmpl: str) -> None:
        url = BASE + tmpl.format(s=asset, m=month)
        if no_network:
            res = {"url": url, "status": "SKIPPED", "reachable": None, "attempts": 0}
        else:
            res = probe_url(url)
        res.update({"bucket": bucket, "family": family, "asset": asset, "month": month})
        rows.append(res)

    for family, tmpl in CM_PERP_FAMILIES:
        for asset in ["BTCUSD_PERP", "ETHUSD_PERP"]:
            for month in COIN_M_MONTHS:
                record("coin_m_perp_monthly", family, asset, month, tmpl)
                time.sleep(0.12)

    # Universe breadth at the most recent month (is the perp universe wide enough?)
    for asset in CM_PERPS:
        record("coin_m_perp_universe", "klines_1h", asset, "2026-10",
               "/data/futures/cm/monthly/klines/{s}/1h/{s}-1h-{m}.zip")
        time.sleep(0.12)

    # Dated quarterly futures (term structure).
    for contract, months in CM_QUARTERLY:
        for month in months:
            record("coin_m_quarterly_monthly", "klines_1h", contract, month,
                   "/data/futures/cm/monthly/klines/{s}/1h/{s}-1h-{m}.zip")
            time.sleep(0.12)

    return rows


def classify(rows: list[dict]) -> dict:
    fam: dict[tuple, dict] = {}
    for r in rows:
        key = (r.get("bucket"), r.get("family"), r.get("asset"))
        d = fam.setdefault(key, {
            "bucket": r.get("bucket"), "family": r.get("family"), "asset": r.get("asset"),
            "n_total": 0, "n_reachable": 0, "n_miss": 0,
        })
        d["n_total"] += 1
        if r.get("reachable") is True:
            d["n_reachable"] += 1
        elif r.get("reachable") is False:
            d["n_miss"] += 1

    for d in fam.values():
        if d["n_reachable"] == 0 and d["n_miss"] == d["n_total"]:
            d["classification"] = "UNAVAILABLE"
            d["note"] = f"HTTP 404 across all {d['n_total']} probes"
        elif d["n_reachable"] == d["n_total"]:
            d["classification"] = "REACHABLE"
        else:
            d["classification"] = "FLAKY_PARTIAL"
    return {f"{k[0]}|{k[1]}|{k[2]}": v for k, v in fam.items()}


def summarize(rows: list[dict]) -> dict:
    fam = classify(rows)

    def fam_reach(bucket: str, family: str, asset: str) -> bool:
        d = fam.get(f"{bucket}|{family}|{asset}")
        return bool(d and d["classification"] in ("REACHABLE", "FLAKY_PARTIAL"))

    perp_klines = fam_reach("coin_m_perp_monthly", "klines_1h", "BTCUSD_PERP")
    perp_premium = fam_reach("coin_m_perp_monthly", "premiumIndexKlines_1h", "BTCUSD_PERP")
    perp_mark = fam_reach("coin_m_perp_monthly", "markPriceKlines_1h", "BTCUSD_PERP")
    q_depth = fam.get("coin_m_quarterly_monthly|klines_1h|BTCUSD_250627", {})
    q_recent = fam.get("coin_m_quarterly_monthly|klines_1h|BTCUSD_261225", {})
    q_eth = fam.get("coin_m_quarterly_monthly|klines_1h|ETHUSD_261225", {})

    universe = [
        r["asset"] for r in rows
        if r["bucket"] == "coin_m_perp_universe" and r.get("reachable") is True
    ]
    quarterly_reachable = [
        c for c, months in CM_QUARTERLY
        if fam_reach("coin_m_quarterly_monthly", "klines_1h", c)
    ]

    new_families: list[str] = []
    if perp_klines and (q_recent.get("n_reachable", 0) > 0):
        new_families.append("coin_m_inverse_quarterly_futures_term_structure_carry")
    if perp_premium and perp_mark and len(universe) >= 2:
        new_families.append("coin_m_inverse_perp_premium_index_cross_sectional")

    return {
        "perp_klines_reachable": perp_klines,
        "perp_premium_index_reachable": perp_premium,
        "perp_mark_price_reachable": perp_mark,
        "perp_index_price_reachable": fam_reach("coin_m_perp_monthly", "indexPriceKlines_1h", "BTCUSD_PERP"),
        "perp_funding_rate_reachable": fam_reach("coin_m_perp_monthly", "fundingRate", "BTCUSD_PERP"),
        "perp_aggtrades_reachable": fam_reach("coin_m_perp_monthly", "aggTrades", "BTCUSD_PERP"),
        "perp_universe_reachable_n": len(universe),
        "perp_universe_reachable": universe,
        "quarterly_term_structure_reachable": q_recent.get("n_reachable", 0) > 0,
        "quarterly_contracts_reachable": quarterly_reachable,
        "quarterly_depth_months_btc_250627": q_depth.get("n_reachable", 0),
        "genuinely_new_reachable_families": new_families,
        "path_a_available": len(new_families) > 0,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="C306 COIN-M term-structure reachability probe")
    ap.add_argument("--no-network", action="store_true")
    ap.add_argument("--json-out", default=None)
    args = ap.parse_args(argv)

    rows = run_matrix(no_network=args.no_network)
    summary = summarize(rows)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report = {
        "campaign": "C306",
        "as_of_utc": _now(),
        "source": BASE + "/data/futures/cm/",
        "contract_family": "COIN-M inverse (coin-margined) perpetual + dated quarterly futures",
        "rows": rows,
        "summary": summary,
        "real_data_only": True,
        "fabricated_data": False,
        "executed_fills": False,
    }

    cache_path = REPO / "data/cache/campaign306_coinm_reachability.json"
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    blob = json.dumps(report, indent=1, sort_keys=True).encode()
    cache_path.write_bytes(blob)
    prov = {
        "cache": str(cache_path.relative_to(REPO)),
        "sha256": hashlib.sha256(blob).hexdigest(),
        "generated_utc": _now(),
        "real_data_only": True,
        "fabricated_data": False,
    }
    (REPO / "data/cache/campaign306_coinm_reachability.provenance.json").write_text(
        json.dumps(prov, indent=1, sort_keys=True) + "\n"
    )

    out = Path(args.json_out) if args.json_out else REPO / f"reports/c306_coinm_reachability_probe_{ts}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(blob)
    print(json.dumps({"report": str(out), "sha256": prov["sha256"], "summary": summary}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())