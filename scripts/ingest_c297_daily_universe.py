#!/usr/bin/env python3
"""C297 — ingest a real mainnet public Binance spot DAILY (1d) OHLCV universe over
a multi-year window.

C297 is a NEW economic regime absent from the entire C281B..C296 record: those
campaigns tested CROSS-SECTIONAL STAT-ARB at 5m / 1h horizons over a single
~3-month window (2026-08 .. 2026-10).  C297 tests the SAME cross-sectional
statistical-arbitrage mechanism at a **daily horizon over a multi-year window**
(2021-01-01 .. 2026-11-13) spanning multiple market regimes (2021 bull, 2022
bear, 2023-2024 recovery, 2025-2026).  Daily horizon => far lower turnover and a
different cost-sensitivity regime, so this is not a relabeling of a closed
5m/1h family.

Data step: fetch REAL mainnet public Binance spot daily klines
(open/high/low/close + base volume + quote volume) from
``data-api.binance.vision/api/v3/klines`` (host chain in
``data/real_feed_loader.py``).  Only symbols with EXACT full daily coverage over
the whole multi-year window (finite, positive, 1d spacing, exact index) are
eligible; the top TARGET_UNIVERSE by realized quote-volume sum are selected.

Persists:
- ``data/cache/campaign297_daily_ohlcv.pkl``         (aligned wide OHLCV frames)
- ``data/cache/campaign297_daily_ohlcv.meta.json``   (flags, shape, window, sha256)
- ``data/cache/campaign297_daily_ohlcv.provenance.json`` (host attempts, blocked
  routes, universe selection, per-symbol bar counts, exclusions)

Every artifact records ``real_data_only: true`` and ``fabricated_data: false``.
SHA256 is computed from the raw bytes of the pickle (SHA256-from-bytes).  No
synthetic data, no relabeled old caches, no resampling of a derived series, no
forward/back fill, no imputation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from data.real_feed_loader import _http_get_json, fetch_spot_ohlcv_klines  # noqa: E402

CACHE = ROOT / "data" / "cache"
OUT_PKL = CACHE / "campaign297_daily_ohlcv.pkl"
OUT_META = CACHE / "campaign297_daily_ohlcv.meta.json"
OUT_PROV = CACHE / "campaign297_daily_ohlcv.provenance.json"

START_UTC = "2021-01-01T00:00:00Z"
END_UTC = "2026-11-13T00:00:00Z"
INTERVAL = "1d"
TARGET_UNIVERSE = 24
MAX_CANDIDATES = 120
ONE_DAY = pd.Timedelta(days=1)

# Fiat-pegged stablecoins trade at ~constant price (near-zero volatility); they
# are not valid cross-sectional stat-arb legs and are excluded by name with a
# recorded reason (never silently).  This is a documented universe rule, not a
# threshold weakening.
STABLE_BASES = {
    "USDC", "USD1", "FDUSD", "RLUSD", "TUSD", "USDP", "USDD", "BUSD", "DAI",
    "GUSD", "PYUSD", "USDS", "USDG", "XUSD", "UST", "USTC", "BIDR", "IDRT",
    "AEUR", "EURI", "EUR", "USDT",
}

HOSTS = ["https://data-api.binance.vision"]


def sha256_bytes(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expected_index(start: str, end: str) -> pd.DatetimeIndex:
    idx = pd.date_range(start=pd.Timestamp(start), end=pd.Timestamp(end), freq="D", tz="UTC")
    return pd.DatetimeIndex(idx)


def fetch_exchange_info() -> tuple[dict, dict]:
    payload, meta = _http_get_json("https://data-api.binance.vision/api/v3/exchangeInfo", timeout=40.0)
    if not meta.get("ok") or not isinstance(payload, dict):
        raise SystemExit(f"FATAL: exchangeInfo unavailable: {meta}")
    quote_asset: dict[str, str] = {}
    spot_allowed: dict[str, bool] = {}
    status: dict[str, str] = {}
    for s in payload.get("symbols", []):
        sym = s.get("symbol")
        quote_asset[sym] = s.get("quoteAsset")
        spot_allowed[sym] = bool(s.get("isSpotTradingAllowed"))
        status[sym] = s.get("status")
    return {"quote_asset": quote_asset, "spot_allowed": spot_allowed, "status": status}, meta  # type: ignore[return-value]


def fetch_ticker() -> tuple[dict[str, float], dict]:
    payload, meta = _http_get_json("https://data-api.binance.vision/api/v3/ticker/24hr", timeout=40.0)
    if not meta.get("ok") or not isinstance(payload, list):
        raise SystemExit(f"FATAL: ticker/24hr unavailable: {meta}")
    qv = {row["symbol"]: float(row.get("quoteVolume") or 0.0) for row in payload}
    return qv, meta


def _pickle_bytes(payload: dict) -> bytes:
    import io
    import pickle

    buf = io.BytesIO()
    pickle.dump(payload, buf, protocol=pickle.HIGHEST_PROTOCOL)
    return buf.getvalue()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    CACHE.mkdir(parents=True, exist_ok=True)

    info, info_meta = fetch_exchange_info()
    qv_all, ticker_meta = fetch_ticker()

    # ---- universe selection (real, documented, deterministic) ----
    candidates: list[dict] = []
    for sym, qa in info["quote_asset"].items():  # type: ignore[index]
        if qa != "USDT":
            continue
        if info["status"].get(sym) != "TRADING":  # type: ignore[index]
            continue
        if not info["spot_allowed"].get(sym, False):  # type: ignore[index]
            continue
        base = sym[:-4] if sym.endswith("USDT") else sym
        if base in STABLE_BASES:
            continue
        candidates.append({"symbol": sym, "base": base, "quote_volume_24h": float(qv_all.get(sym, 0.0))})
    candidates.sort(key=lambda x: x["quote_volume_24h"], reverse=True)
    cand = candidates[:MAX_CANDIDATES]
    symbols = [c["symbol"] for c in cand]

    # ---- fetch true-1d OHLCV for candidates over the multi-year window ----
    frames, prov = fetch_spot_ohlcv_klines(symbols, START_UTC, END_UTC, interval=INTERVAL, hosts=HOSTS)

    exp_idx = expected_index(START_UTC, END_UTC)
    n_expected = len(exp_idx)

    per_symbol: dict[str, dict] = {}
    eligible: list[str] = []
    for c in cand:
        sym = c["symbol"]
        fr = frames.get(sym)
        if fr is None:
            per_symbol[sym] = {"status": "missing", "bars": 0, "coverage": 0.0, "eligible": False}
            continue
        bars = int(fr.shape[0])
        finite = bool(np.isfinite(fr.to_numpy(dtype=float)).all())
        positive = bool((fr.to_numpy(dtype=float) > 0).all())
        idx = pd.DatetimeIndex(fr.index)
        diffs = idx.to_series().diff().dropna()
        spacing = bool((diffs == ONE_DAY).all()) if len(diffs) else False
        exact_index = bool(fr.index.equals(exp_idx))
        full_coverage = exact_index and finite and positive and spacing
        qv_sum = float(fr["quote_volume"].sum())
        per_symbol[sym] = {
            "status": "ok",
            "bars": bars,
            "expected_bars": n_expected,
            "coverage": float(bars / n_expected) if n_expected else 0.0,
            "exact_expected_index": exact_index,
            "all_finite": finite,
            "all_positive": positive,
            "spacing_1d_ok": spacing,
            "quote_volume_sum": qv_sum,
            "quote_volume_24h": c["quote_volume_24h"],
            "eligible": bool(full_coverage),
        }
        if full_coverage:
            eligible.append(sym)

    # rank eligible by realized 1d quote-volume sum over the window, take top N
    eligible.sort(key=lambda s: per_symbol[s]["quote_volume_sum"], reverse=True)
    selected = eligible[:TARGET_UNIVERSE]

    if len(selected) < 8:
        raise SystemExit(
            "FATAL: fewer than 8 symbols had exact full daily coverage over the multi-year "
            f"window ({len(selected)}); cannot build a real daily universe."
        )

    # align wide frames on the exact expected index (all selected have full coverage)
    def wide(field: str) -> pd.DataFrame:
        return pd.concat({s: frames[s][field] for s in selected}, axis=1).reindex(exp_idx).astype(float)

    opens = wide("open")
    highs = wide("high")
    lows = wide("low")
    closes = wide("close")
    volumes = wide("volume")
    quote_volumes = wide("quote_volume")

    n_bars = int(len(exp_idx))
    if closes.shape != (n_bars, len(selected)):
        raise SystemExit(f"FATAL: aligned shape {closes.shape} != {(n_bars, len(selected))}")

    payload = {
        "interval": INTERVAL,
        "symbols": selected,
        "window_start_utc": START_UTC,
        "window_end_utc": END_UTC,
        "n_bars": n_bars,
        "opens": opens,
        "highs": highs,
        "lows": lows,
        "closes": closes,
        "volumes": volumes,
        "quote_volumes": quote_volumes,
    }
    OUT_PKL.write_bytes(_pickle_bytes(payload))

    pkl_sha = sha256_bytes(OUT_PKL)
    meta = {
        "generated_at_utc": ts,
        "campaign": 297,
        "interval": INTERVAL,
        "symbols": selected,
        "n_symbols": len(selected),
        "rows": n_bars,
        "columns_per_frame": ["open", "high", "low", "close", "volume", "quote_volume"],
        "window_start_utc": START_UTC,
        "window_end_utc": END_UTC,
        "expected_bars": n_expected,
        "real_data_only": True,
        "fabricated_data": False,
        "fetch_real_data_only": True,
        "fetch_fabricated_data": False,
        "source_host": "https://data-api.binance.vision",
        "source_endpoint": "/api/v3/klines",
        "horizon": "daily_1d_multi_year",
        "sha256_from_bytes": pkl_sha,
        "pkl_path": str(OUT_PKL.relative_to(ROOT)),
    }
    OUT_META.write_text(json.dumps(meta, indent=2) + "\n")

    provenance = {
        "generated_at_utc": ts,
        "campaign": 297,
        "part": "provenance",
        "real_data_only": True,
        "fabricated_data": False,
        "universe_rule": (
            "USDT spot TRADING symbols ranked by 24h quote volume (real mainnet ticker); "
            "fiat stablecoins excluded by documented denylist; top MAX_CANDIDATES fetched over "
            "the multi-year 1d window; only symbols with exact full 1d coverage (finite, positive, "
            "1d spacing, exact daily index) are eligible; top TARGET_UNIVERSE by realized 1d "
            "quote-volume sum selected. No impute/ffill/resample."
        ),
        "n_candidates_fetched": len(symbols),
        "n_eligible_full_coverage": len(eligible),
        "n_selected": len(selected),
        "selected_symbols": selected,
        "per_symbol": per_symbol,
        "per_symbol_selection": {s: per_symbol.get(s, {}) for s in selected},
        "exchange_info_meta": info_meta,
        "ticker_meta": ticker_meta,
        "kline_fetch_provenance": prov,
        "blocked_routes": prov.get("blocked_routes", []),
        "blocked_hosts": prov.get("blocked_hosts", []),
    }
    OUT_PROV.write_text(json.dumps(provenance, indent=2, default=str) + "\n")

    summary = {
        "ok": True,
        "campaign": 297,
        "real_data_only": True,
        "fabricated_data": False,
        "pkl": str(OUT_PKL.relative_to(ROOT)),
        "pkl_sha256": pkl_sha,
        "meta": str(OUT_META.relative_to(ROOT)),
        "meta_sha256": sha256_bytes(OUT_META),
        "provenance": str(OUT_PROV.relative_to(ROOT)),
        "provenance_sha256": sha256_bytes(OUT_PROV),
        "n_symbols": len(selected),
        "n_bars": n_bars,
        "window": {"start": START_UTC, "end": END_UTC},
        "selected_symbols": selected,
        "n_candidates_fetched": len(symbols),
        "n_eligible_full_coverage": len(eligible),
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())