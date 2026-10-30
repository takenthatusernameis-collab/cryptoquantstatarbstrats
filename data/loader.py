"""
Data loader for cryptocurrency market data
"""

from __future__ import annotations

import json
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

import numpy as np
import pandas as pd

from utils import clean_data as _clean_data


class DataLoader:
    """Load and preprocess cryptocurrency price data."""

    def __init__(self, data_source: str = "csv"):
        self.data_source = data_source

    @classmethod
    def load_csv(cls, path: str) -> pd.DataFrame:
        """Load data from a CSV file.

        Reads a CSV with a `timestamp` column + asset columns, parses
        timestamps, sets the index, and returns a DataFrame aligned with
        the engine's expected shape.
        """
        df = pd.read_csv(path)
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df = df.set_index("timestamp")
        elif "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
            df = df.set_index("date")
        elif "time" in df.columns:
            df["time"] = pd.to_datetime(df["time"])
            df = df.set_index("time")
        else:
            # Try to parse first column as datetime if it looks like it
            first_col = df.columns[0]
            try:
                df[first_col] = pd.to_datetime(df[first_col])
                df = df.set_index(first_col)
            except Exception:
                pass

        df = df.sort_index()
        return df

    def load_binance_data(
        self,
        symbols: list[str],
        start_date: str,
        end_date: str,
        interval: str = "1h",
        quote_asset: str = "USDT",
        timeout: float = 20.0,
    ) -> pd.DataFrame:
        """Load free public Binance spot closes without requiring an API key.

        Symbols may use base names such as BTC or Binance symbols such as BTCUSDT.
        Output columns retain the requested names. Timestamps are UTC candle-open
        timestamps, and the backtest engine executes generated signals one bar later.
        The supplied end timestamp is inclusive.
        """
        supported_intervals = {
            "1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h",
            "6h", "8h", "12h", "1d", "3d", "1w", "1M",
        }
        if interval not in supported_intervals:
            raise ValueError(
                f"Unsupported Binance interval {interval!r}. "
                f"Choose one of {sorted(supported_intervals)}."
            )
        if not symbols:
            raise ValueError("At least one symbol is required.")

        def as_utc_millis(value: str, *, include_date: bool = False) -> int:
            stamp = pd.Timestamp(value)
            # Date-only end values include the entire UTC calendar day; explicit
            # timestamps retain their exact inclusive moment.
            if include_date and isinstance(value, str) and len(value.strip()) == 10:
                stamp = stamp + pd.Timedelta(days=1) - pd.Timedelta(milliseconds=1)
            if stamp.tzinfo is None:
                stamp = stamp.tz_localize("UTC")
            else:
                stamp = stamp.tz_convert("UTC")
            return int(stamp.timestamp() * 1000)

        start_ms = as_utc_millis(start_date)
        end_ms = as_utc_millis(end_date, include_date=True)
        if end_ms < start_ms:
            raise ValueError("end_date must not precede start_date.")

        # Binance public spot klines. api.binance.com may be blocked (e.g. HTTP 451)
        # in some environments; www.binance.com serves the same public endpoint, so
        # try a ordered list of hosts and fall back until one succeeds.
        _binance_hosts = [
            "https://api.binance.com",
            "https://www.binance.com",
            "https://api1.binance.com",
            "https://api2.binance.com",
            "https://api3.binance.com",
        ]

        series_by_symbol: dict[str, pd.Series] = {}
        for requested_symbol in symbols:
            output_name = str(requested_symbol)
            market_symbol = output_name.upper().replace("/", "").replace("-", "")
            if not market_symbol.endswith(quote_asset.upper()):
                market_symbol = f"{market_symbol}{quote_asset.upper()}"

            cursor_ms = start_ms
            candles: list[tuple[int, float]] = []
            last_error: str | None = None
            while cursor_ms <= end_ms:
                query = urlencode({
                    "symbol": market_symbol,
                    "interval": interval,
                    "startTime": cursor_ms,
                    "endTime": end_ms,
                    "limit": 1000,
                })

                payload = None
                fetch_error: str | None = None
                for host in _binance_hosts:
                    url = f"{host}/api/v3/klines?{query}"
                    try:
                        with urlopen(url, timeout=timeout) as response:
                            payload = json.loads(response.read().decode("utf-8"))
                        fetch_error = None
                        break
                    except (HTTPError, URLError, TimeoutError, OSError) as exc:
                        fetch_error = f"{host}: {exc}"
                        payload = None
                        continue
                if fetch_error is not None:
                    raise RuntimeError(
                        f"Could not fetch Binance candles for {market_symbol}: {fetch_error}"
                    ) from None
                if not isinstance(payload, list):
                    raise RuntimeError(
                        f"Unexpected Binance response for {market_symbol}: {payload!r}"
                    )
                if not payload:
                    break

                for candle in payload:
                    open_ms = int(candle[0])
                    if start_ms <= open_ms <= end_ms:
                        candles.append((open_ms, float(candle[4])))

                last_open_ms = int(payload[-1][0])
                if len(payload) < 1000 or last_open_ms >= end_ms:
                    break
                next_cursor = last_open_ms + 1
                if next_cursor <= cursor_ms:
                    raise RuntimeError(
                        f"Binance pagination stalled for {market_symbol} at {cursor_ms}."
                    )
                cursor_ms = next_cursor

            if not candles:
                raise ValueError(
                    f"No Binance spot candles returned for {market_symbol} "
                    f"between {start_date} and {end_date}."
                )
            frame = pd.DataFrame(candles, columns=["timestamp", output_name])
            frame["timestamp"] = pd.to_datetime(frame["timestamp"], unit="ms", utc=True)
            frame = frame.drop_duplicates("timestamp").set_index("timestamp").sort_index()
            series_by_symbol[output_name] = frame[output_name]

        # Keep only genuinely observed timestamps shared by every symbol.
        # Forward-filling a missing candle would manufacture flat returns and
        # conceal gaps or listing-date differences in market data.
        data = pd.concat(series_by_symbol.values(), axis=1, join="inner")
        data.columns = list(series_by_symbol.keys())
        data = data.sort_index()
        if data.empty:
            raise ValueError(
                "The requested symbols have no shared Binance candle timestamps "
                "in the requested date range."
            )
        return data

    def load_data(
        self,
        symbols: list[str],
        start_date: str,
        end_date: str,
        freq: str = "1h",
    ) -> pd.DataFrame:
        """Generate synthetic prices for unit tests and demonstrations only.

        This function deliberately does not fetch historical market data.
        Use load_binance_data for public-market backtests.
        """
        dates = pd.date_range(start_date, end_date, freq=freq)
        data = pd.DataFrame(index=dates)

        for symbol in symbols:
            # Synthetic demonstration series; not evidence of market behavior.
            returns = np.random.randn(len(dates)) * 0.02
            prices = 100 * np.exp(np.cumsum(returns))
            data[symbol] = prices

        return data

    def clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Clean and preprocess data."""
        return _clean_data(data)

    def fetch_with_provenance(
        self,
        symbols: list[str],
        start_date: str,
        end_date: str,
        interval: str = "1h",
        quote_asset: str = "USDT",
        *,
        max_workers: int = 4,
        retries: int = 3,
        backoff_seconds: float = 1.5,
        use_cache: bool = True,
    ) -> tuple[pd.DataFrame, dict[str, Any]]:
        """Fetch real Binance data with retry/backoff and parallel symbols.

        Returns ``(data, provenance)`` where ``provenance`` records every host
        attempt, retry, failure, and the final bar count per symbol.  Symbols
        that fail after all retries are excluded with a documented reason; the
        returned frame only contains symbols that succeeded.  Nothing is ever
        fabricated.
        """
        from data.cache import load_cached

        provenance: dict[str, Any] = {
            "requested_symbols": list(symbols),
            "start": start_date,
            "end": end_date,
            "interval": interval,
            "quote_asset": quote_asset,
            "max_workers": max_workers,
            "retries": retries,
            "backoff_seconds": backoff_seconds,
            "per_symbol": {},
            "excluded": [],
            "cache": {},
        }

        try:
            data, cache_prov = load_cached(
                self,
                symbols,
                start_date,
                end_date,
                interval=interval,
                quote_asset=quote_asset,
                use_cache=use_cache,
            )
            provenance["cache"] = cache_prov
            for sym in list(data.columns):
                provenance["per_symbol"][sym] = {
                    "status": "ok",
                    "bars": int(data[sym].notna().sum()),
                    "first": str(data.index[0]) if len(data) else None,
                    "last": str(data.index[-1]) if len(data) else None,
                }
            return data, provenance
        except Exception as exc:
            provenance["cache"]["error"] = str(exc)[:120]

        # Fall back to a retry-capable per-symbol fetch so a single bad symbol
        # does not take the whole request down.
        import time
        from concurrent.futures import ThreadPoolExecutor, as_completed

        results: dict[str, pd.Series] = {}
        attempts_log: dict[str, list[dict[str, Any]]] = {}

        def _fetch_one(sym: str) -> tuple[str, pd.Series | None, list[dict[str, Any]]]:
            local_attempts: list[dict[str, Any]] = []
            last_err: str | None = None
            for attempt in range(1, retries + 1):
                try:
                    single = self.load_binance_data(
                        [sym], start_date, end_date, interval=interval, quote_asset=quote_asset
                    )
                    local_attempts.append(
                        {"attempt": attempt, "success": True, "bars": int(len(single))}
                    )
                    return sym, single[sym], local_attempts
                except Exception as exc:
                    last_err = str(exc)[:120]
                    local_attempts.append(
                        {"attempt": attempt, "success": False, "error": last_err}
                    )
                    if attempt < retries:
                        time.sleep(backoff_seconds * attempt)
            return sym, None, local_attempts

        with ThreadPoolExecutor(max_workers=max(1, max_workers)) as ex:
            futures = {ex.submit(_fetch_one, s): s for s in symbols}
            for fut in as_completed(futures):
                sym = futures[fut]
                try:
                    name, series, local_attempts = fut.result()
                except Exception as exc:
                    attempts_log[sym] = [
                        {"attempt": 0, "success": False, "error": str(exc)[:120]}
                    ]
                    provenance["excluded"].append(
                        {
                            "symbol": sym,
                            "reason": "unexpected_exception",
                            "error": str(exc)[:120],
                        }
                    )
                    continue
                attempts_log[sym] = local_attempts
                if series is None:
                    provenance["excluded"].append(
                        {
                            "symbol": sym,
                            "reason": "all_retries_failed",
                            "attempts": local_attempts,
                        }
                    )
                    continue
                results[name] = series

        provenance["per_symbol"] = {
            sym: {
                "status": "ok",
                "bars": int(series.notna().sum()),
                "attempts": attempts_log.get(sym, []),
            }
            for sym, series in results.items()
        }
        provenance["excluded"] = provenance["excluded"] + [
            {"symbol": s, "reason": "not_in_results", "attempts": attempts_log.get(s, [])}
            for s in symbols
            if s not in results
        ]

        if not results:
            raise RuntimeError(
                f"No real Binance data fetched for {symbols} "
                f"between {start_date} and {end_date} after {retries} retries."
            )

        data = pd.concat(list(results.values()), axis=1)
        data.columns = list(results.keys())
        data = data.sort_index()
        return data, provenance
