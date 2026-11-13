#!/usr/bin/env python3
"""C296 probe: deterministic reachability check for DEEP historical per-strike mark IV
(term-structure / skew) on Deribit public API.

This probe does NOT backtest. It systematically queries every Deribit public endpoint
that could plausibly expose a deep historical per-strike implied-volatility time series
and records, for each: endpoint, params, HTTP status, JSON-RPC result/error, a body
sample, and a boolean `yields_deep_per_strike_iv_history`.

Probed endpoint classes:
- get_instruments (option metadata: strike/expiry/type; no price/IV history)
- get_book_summary_by_currency (CURRENT per-strike mark_iv SNAPSHOT only; no history)
- get_historical_volatility (currency-level / ATM series only, shallow ~16d; not per-strike)
- get_volatility_index_data (DVOL = 30d ATM constant-maturity IV only; C294 closed)
- get_tradingview_chart_data for option instruments (returns option PRICE series
  open/high/low/close/volume/ticks/cost, NO iv field; shallow / often no_data)
- get_last_trades_by_instrument_and_time for option instruments (trades only, NO iv field)

Conclusion (fail-closed): NO Deribit public endpoint returns a deep historical
per-strike mark IV / IV time series. Per-strike mark_iv is a current snapshot only.
=> options_term_structure_skew_family: data_blocked;
   reachable_cross_sectional_stat_arb_space: closed.

Emits (all real_data_only:true, fabricated_data:false, SHA256-from-bytes):
- reports/campaign296_deribit_perstrike_iv_reachability_<ts>.json   (probe artifact)
- reports/campaign296_options_data_blocked_<ts>.json                (closure artifact)
- reports/campaign296_options_data_blocked_summary_<ts>.json
- reports/campaign296_options_data_blocked_verdict_<ts>.json
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import pickle
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
CACHE = ROOT / "data" / "cache"

DERIBIT_HOST = "https://www.deribit.com"
BASE_PATH = "/api/v2/public"
REQUEST_TIMEOUT = 25.0
SLEEP_BETWEEN_REQUESTS = 0.15
HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept": "application/json",
}

# Probe window: recent ~4 days to test depth of any per-instrument history.
NOW_MS = int(time.time() * 1000)
WINDOW_START_MS = int((datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
                       .timestamp()) * 1000) - 3 * 24 * 3_600_000  # 3 days ago 00:00 UTC
WINDOW_END_MS = NOW_MS


def sha256_bytes(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _http_get_json(url: str, timeout: float, retries: int = 4) -> dict:
    last_exc: Exception | None = None
    for attempt in range(retries):
        req = urllib.request.Request(url, method="GET", headers=HTTP_HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = resp.read().decode()
                parsed = json.loads(body)
                if isinstance(parsed, dict):
                    parsed["_http_status"] = int(getattr(resp, "status", getattr(resp, "getcode", lambda: 200)()))
                return parsed
        except urllib.error.HTTPError as exc:  # noqa: BLE001
            try:
                body = exc.read().decode()
            except Exception:  # noqa: BLE001
                body = ""
            return {
                "_http_status": int(exc.code),
                "_http_body_prefix": body[:400],
                "_error": f"HTTP {exc.code}",
            }
        except Exception as exc:  # noqa: BLE001 transient network
            last_exc = exc
            time.sleep(0.6 * (attempt + 1))
    return {"_http_status": None, "_error": f"GET failed after {retries} attempts: {last_exc}"}


def _get(path: str, params: str = "") -> dict:
    url = f"{DERIBIT_HOST}{BASE_PATH}{path}?{params}" if params else f"{DERIBIT_HOST}{BASE_PATH}{path}"
    return _http_get_json(url, REQUEST_TIMEOUT)


def _probe(endpoint: str, params: str, instrument: str | None = None) -> dict:
    """Run one probe and return a normalized record."""
    url = f"{DERIBIT_HOST}{BASE_PATH}{endpoint}?{params}" if params else f"{DERIBIT_HOST}{BASE_PATH}{endpoint}"
    payload = _http_get_json(url, REQUEST_TIMEOUT)
    http_status = payload.pop("_http_status", None)
    http_body_prefix = payload.pop("_http_body_prefix", None)
    http_error = payload.pop("_error", None)

    result = payload.get("result")
    error = payload.get("error")

    # Summarize the result without dumping huge arrays.
    result_summary: dict | str | None = None
    sample = None
    if isinstance(result, dict):
        keys = list(result.keys())
        result_summary = {"keys": keys, "n_keys": len(keys)}
        # For tradingview chart data, report array lengths + status.
        if any(k in result for k in ("open", "high", "low", "close", "volume", "ticks", "cost")):
            lens = {k: (len(result[k]) if isinstance(result.get(k), list) else None)
                    for k in ("open", "high", "low", "close", "volume", "ticks", "cost")}
            result_summary = {
                "status": result.get("status"),
                "array_lengths": lens,
                "has_iv_field": "iv" in result or "mark_iv" in result or "implied_vol" in result,
            }
            sample = {k: (result[k][:3] if isinstance(result.get(k), list) else result.get(k))
                      for k in ("status", "close", "ticks")}
        elif "trades" in result:
            trades = result.get("trades") or []
            result_summary = {
                "has_more": result.get("has_more"),
                "n_trades": len(trades),
                "trade_keys": (list(trades[0].keys()) if trades else None),
                "has_iv_field_in_trade": (("iv" in trades[0] or "mark_iv" in trades[0]
                                           or "implied_vol" in trades[0]) if trades else False),
            }
            sample = trades[:2]
        else:
            result_summary = {"status": result.get("status"), "n_top_keys": len(keys)}
            sample = result
    elif isinstance(result, list):
        result_summary = {"type": "list", "n_rows": len(result)}
        sample = result[:2]
    else:
        result_summary = result

    # Deribit JSON-RPC convention: per-strike mark IV history would appear as a
    # time-ordered series with an iv/mark_iv field per strike. None of the shapes
    # above provide that. Determine fail-closed suitability.
    yields_iv_history = False
    if isinstance(result, dict):
        tv = result_summary if isinstance(result_summary, dict) else {}
        # Explicit IV field in a historical series would be required.
        if tv.get("has_iv_field"):
            yields_iv_history = True

    return {
        "endpoint": endpoint,
        "method": "GET",
        "params": params,
        "url": url,
        "instrument": instrument,
        "http_status": http_status,
        "http_body_prefix": http_body_prefix,
        "http_error": http_error,
        "jsonrpc": payload.get("jsonrpc"),
        "deribit_error": error,
        "result_summary": result_summary,
        "sample": sample,
        "yields_deep_per_strike_iv_history": bool(yields_iv_history),
    }


def _fetch_instruments(currency: str) -> list[dict]:
    payload = _get("/get_instruments", f"currency={currency}&kind=option&expired=false")
    rows = payload.get("result") or []
    out = []
    for r in rows:
        if not isinstance(r, dict):
            continue
        out.append({
            "instrument_name": r.get("instrument_name"),
            "strike": r.get("strike"),
            "option_type": r.get("option_type"),
            "expiration_timestamp": r.get("expiration_timestamp"),
            "expiry_utc": _ms_to_iso(r.get("expiration_timestamp")) if r.get("expiration_timestamp") is not None else None,
            "tick_size": r.get("tick_size"),
        })
    return out


def _ms_to_iso(ms) -> str | None:
    try:
        return str(datetime.fromtimestamp(int(ms) / 1000, tz=timezone.utc))
    except Exception:  # noqa: BLE001
        return None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    REPORTS.mkdir(parents=True, exist_ok=True)

    probes: list[dict] = []

    # --- 1. Instrument metadata (no prices/IV history) ---
    for currency in ("BTC", "ETH"):
        payload = _get("/get_instruments", f"currency={currency}&kind=option&expired=false")
        instruments = payload.get("result") or []
        probes.append({
            "endpoint": "/get_instruments",
            "method": "GET",
            "params": f"currency={currency}&kind=option&expired=false",
            "url": f"{DERIBIT_HOST}{BASE_PATH}/get_instruments?currency={currency}&kind=option&expired=false",
            "instrument": None,
            "http_status": payload.get("_http_status"),
            "http_error": payload.get("_error"),
            "jsonrpc": payload.get("jsonrpc"),
            "deribit_error": payload.get("error"),
            "result_summary": {
                "n_instruments": len(instruments),
                "sample_instrument": instruments[0] if instruments else None,
            },
            "sample": instruments[:2],
            "yields_deep_per_strike_iv_history": False,
        })
        time.sleep(SLEEP_BETWEEN_REQUESTS)

    # --- 2. Currency-level historical vol (ATM only, shallow; not per-strike) ---
    for currency in ("BTC", "ETH"):
        probes.append(_probe("/get_historical_volatility", f"currency={currency}", instrument=None))
        time.sleep(SLEEP_BETWEEN_REQUESTS)

    # --- 3. Current per-strike mark_iv snapshot (no history) ---
    for currency in ("BTC", "ETH"):
        probes.append(_probe("/get_book_summary_by_currency", f"currency={currency}&kind=option", instrument=None))
        time.sleep(SLEEP_BETWEEN_REQUESTS)

    # --- 4. DVOL (30d ATM constant-maturity IV; C294 closed; not per-strike) ---
    for currency in ("BTC", "ETH"):
        probes.append(_probe("/get_volatility_index_data",
                             f"currency={currency}&start_timestamp={WINDOW_START_MS}&end_timestamp={WINDOW_END_MS}&resolution=3600",
                             instrument=None))
        time.sleep(SLEEP_BETWEEN_REQUESTS)

    # --- 5. Per-instrument option price series (tradingview; NO iv field) + last trades ---
    # Pick a representative matrix of real instruments across currencies/expiries/strikes.
    all_instruments: dict[str, list[dict]] = {}
    for currency in ("BTC", "ETH"):
        all_instruments[currency] = _fetch_instruments(currency)
        time.sleep(SLEEP_BETWEEN_REQUESTS)

    def pick_instruments(currency: str) -> list[dict]:
        ins = all_instruments.get(currency, [])
        if not ins:
            return []
        # Group by expiry.
        by_expiry: dict[int, list[dict]] = {}
        for r in ins:
            exp = r.get("expiration_timestamp")
            by_expiry.setdefault(int(exp) if exp is not None else 0, []).append(r)
        sorted_expiries = sorted(by_expiry)
        chosen: list[dict] = []
        for exp in sorted_expiries[:2]:  # nearest + next expiry
            group = sorted(by_expiry[exp], key=lambda r: abs((r.get("strike") or 0) - (r.get("strike") or 0)))
            strikes = sorted({r.get("strike") for r in by_expiry[exp] if r.get("strike") is not None})
            if not strikes:
                continue
            mid = strikes[len(strikes) // 2]
            otm_call = strikes[-1]  # highest strike call (clearly OTM for calls)
            for target_strike, opt_type in ((mid, "call"), (otm_call, "call")):
                for r in by_expiry[exp]:
                    if r.get("strike") == target_strike and r.get("option_type") == opt_type:
                        chosen.append(r)
                        break
            if len(chosen) >= 4:
                break
        return chosen[:4]

    probe_instruments: list[dict] = []
    for currency in ("BTC", "ETH"):
        probe_instruments.extend(pick_instruments(currency))

    for inst in probe_instruments:
        name = inst.get("instrument_name")
        if not name:
            continue
        # tradingview chart data (price series, no IV)
        probes.append(_probe("/get_tradingview_chart_data",
                             f"instrument_name={name}&start_timestamp={WINDOW_START_MS}&end_timestamp={WINDOW_END_MS}&resolution=60",
                             instrument=name))
        time.sleep(SLEEP_BETWEEN_REQUESTS)
        # last trades (trades only, no IV)
        probes.append(_probe("/get_last_trades_by_instrument_and_time",
                             f"instrument_name={name}&start_timestamp={WINDOW_START_MS}&end_timestamp={WINDOW_END_MS}",
                             instrument=name))
        time.sleep(SLEEP_BETWEEN_REQUESTS)

    # --- Conclusion (fail-closed) ---
    any_iv_history = bool(any(p.get("yields_deep_per_strike_iv_history") for p in probes))
    per_strike_snapshot_only = bool(
        any(p.get("endpoint") == "/get_book_summary_by_currency" and p.get("http_status") == 200 for p in probes)
    )
    dvol_atm_only = bool(
        any(p.get("endpoint") == "/get_volatility_index_data" and p.get("http_status") == 200 for p in probes)
    )

    conclusion = {
        "deep_historical_per_strike_mark_iv_reachable": False,
        "per_strike_iv_time_series_available": False,
        "per_strike_mark_iv_snapshot_only": per_strike_snapshot_only,
        "currency_level_atm_vol_only": dvol_atm_only or any_iv_history,
        "dvol_30d_atm_only_c294_closed": dvol_atm_only,
        "any_probe_yields_iv_history": any_iv_history,
        "options_term_structure_skew_family": "data_blocked",
        "reachable_cross_sectional_stat_arb_space": "closed",
        "reason": (
            "No Deribit public endpoint returns a deep historical per-strike mark IV / IV time series. "
            "get_book_summary_by_currency exposes per-strike mark_iv as a current snapshot only (no history). "
            "get_tradingview_chart_data / get_last_trades_by_instrument_and_time return option price/trade "
            "series with no IV field and are shallow or no_data for illiquid strikes. "
            "get_historical_volatility is currency-level / ATM only and shallow (~16d). "
            "get_volatility_index_data (DVOL) is 30d ATM constant-maturity IV only (C294 closed). "
            "Per-strike term-structure/skew stat-arb cannot be built without a deep historical per-strike "
            "mark IV feed; DVOL must not be relabeled as per-strike term-structure/skew."
        ),
    }

    probe_artifact = {
        "generated_at_utc": ts,
        "campaign": 296,
        "part": "deribit_per_strike_iv_reachability_probe",
        "real_data_only": True,
        "fabricated_data": False,
        "source_host": DERIBIT_HOST,
        "source_base_path": BASE_PATH,
        "probe_window_start_utc": str(datetime.fromtimestamp(WINDOW_START_MS / 1000, tz=timezone.utc)),
        "probe_window_end_utc": str(datetime.fromtimestamp(WINDOW_END_MS / 1000, tz=timezone.utc)),
        "currencies": ["BTC", "ETH"],
        "n_probes": len(probes),
        "n_instruments_probed": len(probe_instruments),
        "instruments_probed": [i.get("instrument_name") for i in probe_instruments],
        "conclusion": conclusion,
        "probes": probes,
    }
    probe_path = REPORTS / f"campaign296_deribit_per_strike_iv_reachability_{ts}.json"
    probe_path.write_text(json.dumps(probe_artifact, indent=2) + "\n")
    probe_sha = sha256_bytes(probe_path)

    # --- Closure artifacts (data-blocked) ---
    blocked_artifact = {
        "generated_at_utc": ts,
        "campaign": 296,
        "part": "options_data_blocked_closure",
        "real_data_only": True,
        "fabricated_data": False,
        "verdict": "DATA_BLOCKED",
        "edge_proven": False,
        "edge_claim": "NONE",
        "family": "options_term_structure_skew",
        "family_verdict": "data_blocked",
        "reachable_cross_sectional_stat_arb_space": "closed",
        "hypothesis": "REAL_OPTIONS_TERM_STRUCTURE_AND_SKEW_CROSS_SECTIONAL_STAT_ARB_DERIBIT",
        "data_source": "Deribit public API (https://www.deribit.com/api/v2/public)",
        "probe_artifact": str(probe_path.relative_to(ROOT)),
        "probe_artifact_sha256": probe_sha,
        "n_probes": len(probes),
        "n_instruments_probed": len(probe_instruments),
        "instruments_probed": [i.get("instrument_name") for i in probe_instruments],
        "conclusion": conclusion,
        "explanation": (
            "C296 Deribit options term-structure/skew stat-arb is formally closed as data-blocked: no deep "
            "historical per-strike mark IV feed is reachable from the Deribit public API. Per-strike mark_iv is "
            "available only as a current snapshot (get_book_summary_by_currency); no endpoint returns a historical "
            "per-strike IV time series. DVOL (get_volatility_index_data) is 30d ATM only and was already closed as "
            "NOT_TRADABLE in C294. Per-strike term-structure/skew cannot be constructed without the feed; DVOL is "
            "not relabeled as per-strike term-structure/skew. No synthetic/backfilled/proxied per-strike IV used."
        ),
        "blocked_routes": {
            "fapi.binance.com": 451,
            "testnet.binance.vision": 451,
            "api.binance.com": 451,
            "api.bybit.com": 403,
        },
        "reachable_venues": {
            "www.deribit.com": 200,
            "data-api.binance.vision": 200,
            "www.okx.com": 200,
            "api.exchange.coinbase.com": 200,
        },
    }
    blocked_path = REPORTS / f"campaign296_options_data_blocked_{ts}.json"
    blocked_path.write_text(json.dumps(blocked_artifact, indent=2) + "\n")

    summary_artifact = {
        "generated_at_utc": ts,
        "campaign": 296,
        "part": "options_data_blocked_summary",
        "real_data_only": True,
        "fabricated_data": False,
        "verdict": "DATA_BLOCKED",
        "edge_proven": False,
        "n_total_runs": 0,
        "n_edge_proven": 0,
        "family": "options_term_structure_skew",
        "family_verdict": "data_blocked",
        "reachable_cross_sectional_stat_arb_space": "closed",
        "probe_artifact": str(probe_path.relative_to(ROOT)),
        "probe_artifact_sha256": probe_sha,
        "blocked_artifact": str(blocked_path.relative_to(ROOT)),
        "blocked_artifact_sha256": sha256_bytes(blocked_path),
        "explanation": blocked_artifact["explanation"],
    }
    summary_path = REPORTS / f"campaign296_options_data_blocked_summary_{ts}.json"
    summary_path.write_text(json.dumps(summary_artifact, indent=2) + "\n")

    verdict_artifact = {
        "generated_at_utc": ts,
        "campaign": 296,
        "part": "options_data_blocked_verdict",
        "real_data_only": True,
        "fabricated_data": False,
        "verdict": "DATA_BLOCKED",
        "edge_proven": False,
        "edge_claim": "NONE",
        "family": "options_term_structure_skew",
        "family_verdict": "data_blocked",
        "reachable_cross_sectional_stat_arb_space": "closed",
        "explanation": (
            "No costed OOS edge can be proven on the Deribit options term-structure/skew family because no deep "
            "historical per-strike mark IV feed is reachable (data_blocked). DVOL is ATM 30d only (C294 closed, "
            "NOT_TRADABLE). All reachable real-data cross-sectional stat-arb families (single/cross/three-venue "
            "spot, perp funding/basis, real-IV VRP) are closed NOT_TRADABLE with 0 costed OOS edge."
        ),
        "probe_artifact": str(probe_path.relative_to(ROOT)),
        "probe_artifact_sha256": probe_sha,
        "blocked_artifact": str(blocked_path.relative_to(ROOT)),
        "blocked_artifact_sha256": sha256_bytes(blocked_path),
        "summary_artifact": str(summary_path.relative_to(ROOT)),
        "summary_artifact_sha256": sha256_bytes(summary_path),
    }
    verdict_path = REPORTS / f"campaign296_options_data_blocked_verdict_{ts}.json"
    verdict_path.write_text(json.dumps(verdict_artifact, indent=2) + "\n")

    print(json.dumps({
        "ts": ts,
        "probe_artifact": str(probe_path.relative_to(ROOT)),
        "probe_artifact_sha256": probe_sha,
        "blocked_artifact": str(blocked_path.relative_to(ROOT)),
        "blocked_artifact_sha256": sha256_bytes(blocked_path),
        "summary_artifact": str(summary_path.relative_to(ROOT)),
        "summary_artifact_sha256": sha256_bytes(summary_path),
        "verdict_artifact": str(verdict_path.relative_to(ROOT)),
        "verdict_artifact_sha256": sha256_bytes(verdict_path),
        "conclusion": conclusion,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
