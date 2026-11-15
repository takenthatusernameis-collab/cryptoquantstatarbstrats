"""Tests for the C305 reachability-exhaustion prober (stdlib only, fully offline).

Network is mocked so these are deterministic and CI-safe (no live egress).
pytest collects the test_* functions normally; the __main__ block lets them run
standalone before the numpy/pandas/pytest bootstrap.

Run standalone:  python tests/test_ingest_c305_program_closure.py
Run under CI:    python -m pytest tests/test_ingest_c305_program_closure.py -q
"""
from __future__ import annotations

import importlib.util
import pathlib
import urllib.error
from unittest import mock

_HERE = pathlib.Path(__file__).resolve().parent
_SPEC = importlib.util.spec_from_file_location(
    "ingest_c305_program_closure", _HERE.parent / "scripts" / "ingest_c305_program_closure.py"
)
assert _SPEC and _SPEC.loader, "cannot locate scripts/ingest_c305_program_closure.py"
mod = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(mod)  # type: ignore[union-attr]


class _FakeResp:
    def __init__(self, status: int, headers: dict | None = None):
        self.status = status
        self.headers = headers or {}

    def read(self, n: int = -1) -> bytes:
        return b""

    def close(self) -> None:
        pass

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _http_error(url: str, code: int) -> urllib.error.HTTPError:
    return urllib.error.HTTPError(url, code, "nf", {}, None)  # type: ignore[arg-type]


def test_url_templates_render():
    tmpl = "/data/futures/um/monthly/klines/{s}/1h/{s}-1h-{m}.zip"
    assert tmpl.format(s="BTCUSDT", m="2026-10") == (
        "/data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2026-10.zip"
    )


def test_probe_url_reachable_after_retries():
    calls = {"n": 0}

    def fake_urlopen(req, timeout=0, context=None):
        calls["n"] += 1
        if calls["n"] < 3:
            raise _http_error(req.full_url, 404)
        return _FakeResp(200, {"Content-Length": "123"})

    with mock.patch.object(mod.urllib.request, "urlopen", side_effect=fake_urlopen):
        res = mod.probe_url("https://x/y", attempts=5)
    assert res["reachable"] is True, res
    assert res["status"] == 200, res
    assert res["attempts"] == 3, res


def test_probe_url_exhausts_retries_fail_closed():
    def fake_urlopen(req, timeout=0, context=None):
        raise _http_error(req.full_url, 404)

    with mock.patch.object(mod.urllib.request, "urlopen", side_effect=fake_urlopen):
        res = mod.probe_url("https://x/y", attempts=3)
    assert res["reachable"] is False, res
    assert res["status"] == 404, res
    assert res["attempts"] == 3, res


def test_classify_unavailable_family():
    rows = [
        {"bucket": "futures_monthly", "family": "bookTicker", "interval": "quote",
         "reachable": False, "status": 404},
        {"bucket": "futures_monthly", "family": "bookTicker", "interval": "quote",
         "reachable": False, "status": 404},
    ]
    d = mod.classify(rows)[("futures_monthly", "bookTicker")]
    assert d["classification"] == "UNAVAILABLE", d
    assert d["n_miss"] == 2 and d["n_reachable"] == 0


def test_classify_consumed_family():
    rows = [
        {"bucket": "futures_monthly", "family": "klines_1h", "interval": "1h",
         "reachable": True, "status": 200},
        {"bucket": "futures_monthly", "family": "klines_1h", "interval": "1h",
         "reachable": True, "status": 200},
    ]
    d = mod.classify(rows)[("futures_monthly", "klines_1h")]
    assert d["classification"] == "CONSUMED", d
    assert "consumed_by" in d


def test_classify_trades_is_reskin():
    rows = [
        {"bucket": "futures_monthly", "family": "trades", "interval": "raw_trade",
         "reachable": True, "status": 200},
        {"bucket": "futures_monthly", "family": "trades", "interval": "raw_trade",
         "reachable": True, "status": 200},
    ]
    d = mod.classify(rows)[("futures_monthly", "trades")]
    assert d["classification"] == "NEW_BUT_RESKIN", d
    assert "C301" in d["note"]


def test_classify_daily_klines_is_reskin():
    rows = [
        {"bucket": "futures_daily", "family": "klines_1h_daily", "interval": "1h",
         "reachable": True, "status": 200},
    ]
    d = mod.classify(rows)[("futures_daily", "klines_1h_daily")]
    assert d["classification"] == "NEW_BUT_RESKIN", d


def test_classify_directory_listing_inaccessible():
    rows = [
        {"bucket": "directory_listing", "path": "/data/futures/um/monthly/",
         "reachable": False, "status": 404},
    ]
    d = mod.classify(rows)[("directory_listing", "/data/futures/um/monthly/")]
    assert d["classification"] == "DIRECTORY_LISTING_INACCESSIBLE", d


def test_no_network_build_is_fail_closed():
    report, rows = mod.build_report(no_network=True)
    assert report["no_network"] is True
    assert all(r["status"] == "SKIPPED" for r in rows)
    assert report["summary"]["genuinely_new_reachable_families"] == []
    assert report["summary"]["reachable_consumed"] == []


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(fns)} tests passed")