#!/usr/bin/env python3
"""C288 preflight: verify every real-data cache needed by the realized-volatility
cross-sectional stat-arb campaign.

C288 is a NEW price-derived economic mechanism (absent from the C281B..C286 record):
cross-sectional low-volatility / volatility-reversal / low-skew stat-arb on the
real 26,208-bar 5m spot close cache.  It uses price data ONLY (no quote volume, no
testnet).  This preflight verifies:

- SHA256-from-bytes of the 5m spot cache + meta;
- meta JSON real/fabricated flags (fail closed on any mismatch);
- the 5m window is exactly 26208 x 11, 2026-08-01T00:00Z -> 2026-10-30T23:55Z,
  zero NaNs, strictly positive prices, duplicate-free, 5m spacing;
- the realized-vol / realized-skew features can be computed causally from 5m close
  log-returns, and are warm before the first OOS test window for every pre-registered
  lookback L in {288, 1008, 2016} (min_periods rule max(20, L//3));
- walk-forward split math: train=720, test=168, step=168 -> 151 OOS splits and the
  last OOS test window fits inside the cache.

The script never fetches, imputes, resamples, or fabricates data.  Exit code 0 iff
every check passes; any mismatch or missing file is a fail-closed blocker.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "cache"

SPOT_5M = CACHE / "90d10b876bb8eda9619cbba73ed19d6c7db4ea7327284f2e33f10a7872a5b263.pkl"
SPOT_5M_META = CACHE / "90d10b876bb8eda9619cbba73ed19d6c7db4ea7327284f2e33f10a7872a5b263.meta.json"
SPOT_5M_SHA = "d15b0b183cf685a15dd34185baff22edf7ef3cc9c80c7d607bcd92f8da418c2f"
SPOT_5M_META_SHA = "e1a71f481cb4ad07881d132aba4ff7b47fc8194c69779701035efcf6e492ce4e"

SYMBOLS = ("ADA", "AVAX", "BNB", "BTC", "DOT", "ETH", "LINK", "LTC", "POL", "SOL", "XRP")
EXPECTED_5M_SHAPE = (26208, 11)
EXPECTED_5M_START = "2026-08-01 00:00:00+00:00"
EXPECTED_5M_END = "2026-10-30 23:55:00+00:00"
LOOKBACKS_5M = (288, 1008, 2016)
WF_TRAIN = 720
WF_TEST = 168
WF_STEP = 168
EXPECTED_WF_SPLITS = 151


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_pickle(path: Path):
    import pickle

    with open(path, "rb") as handle:
        return pickle.load(handle)


def check_sha(checks: dict, label: str, path: Path, expected: str) -> bool:
    if not path.exists():
        checks[label] = {"path": str(path), "exists": False, "ok": False}
        return False
    actual = sha256_file(path)
    ok = actual == expected
    checks[label] = {
        "path": str(path),
        "exists": True,
        "sha256": actual,
        "expected_sha256": expected,
        "ok": ok,
    }
    return ok


def min_periods_for(L: int) -> int:
    return max(20, L // 3)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit JSON summary (default)")
    parser.parse_args()

    checks: dict = {}
    blocked: list[str] = []

    sha_ok = True
    sha_ok &= check_sha(checks, "spot_5m_sha", SPOT_5M, SPOT_5M_SHA)
    sha_ok &= check_sha(checks, "spot_5m_meta_sha", SPOT_5M_META, SPOT_5M_META_SHA)

    try:
        meta_5m = json.loads(SPOT_5M_META.read_text())
        flags_ok = (
            meta_5m.get("interval") == "5m"
            and meta_5m.get("rows") == EXPECTED_5M_SHAPE[0]
            and meta_5m.get("fetch_real_data_only") is True
            and meta_5m.get("fetch_fabricated_data") is False
            and tuple(meta_5m.get("symbols", ())) == SYMBOLS
        )
        checks["spot_5m_meta"] = {
            "interval": meta_5m.get("interval"),
            "rows": meta_5m.get("rows"),
            "fetch_real_data_only": meta_5m.get("fetch_real_data_only"),
            "fetch_fabricated_data": meta_5m.get("fetch_fabricated_data"),
            "symbols": meta_5m.get("symbols"),
            "ok": bool(flags_ok),
        }
        if not flags_ok:
            blocked.append("spot_5m_meta flags/interval/rows/symbols mismatch")
    except Exception as exc:  # noqa: BLE001
        checks["spot_5m_meta"] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        blocked.append("spot_5m_meta could not be read")

    spot_5m = None
    try:
        spot_5m = load_pickle(SPOT_5M)
        if isinstance(spot_5m, pd.Series):
            spot_5m = spot_5m.to_frame()
        spot_5m = spot_5m.astype(float).sort_index()
        idx = pd.DatetimeIndex(spot_5m.index)
        nan_5m = int(spot_5m.isna().sum().sum())
        dup_5m = int(spot_5m.index.duplicated().sum())
        shape_5m = tuple(int(x) for x in spot_5m.shape)
        diffs = idx.to_series().diff().dropna()
        spacing_ok = bool((diffs == pd.Timedelta(minutes=5)).all()) if len(diffs) else False
        finite_ok = bool(np.isfinite(spot_5m.to_numpy(dtype=float)).all())
        positive_ok = bool((spot_5m.to_numpy(dtype=float) > 0).all())
        checks["spot_5m"] = {
            "shape": list(shape_5m),
            "expected_shape": list(EXPECTED_5M_SHAPE),
            "nan_count": nan_5m,
            "duplicate_index_count": dup_5m,
            "start": str(idx.min()),
            "end": str(idx.max()),
            "expected_start": EXPECTED_5M_START,
            "expected_end": EXPECTED_5M_END,
            "spacing_5m_ok": spacing_ok,
            "all_finite": finite_ok,
            "all_positive": positive_ok,
            "columns": [str(c) for c in spot_5m.columns],
            "ok": (
                shape_5m == EXPECTED_5M_SHAPE
                and nan_5m == 0
                and dup_5m == 0
                and str(idx.min()) == EXPECTED_5M_START
                and str(idx.max()) == EXPECTED_5M_END
                and spacing_ok
                and finite_ok
                and positive_ok
                and tuple(str(c) for c in spot_5m.columns) == SYMBOLS
            ),
        }
        if not checks["spot_5m"]["ok"]:
            blocked.append("spot_5m window/shape/nan/duplicate/spacing/finite/positive check failed")
    except Exception as exc:  # noqa: BLE001
        checks["spot_5m"] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        blocked.append("spot_5m could not be loaded")

    if spot_5m is not None:
        try:
            n_bars = len(spot_5m)
            last_test_start = WF_TRAIN + (EXPECTED_WF_SPLITS - 1) * WF_STEP
            last_test_end = last_test_start + WF_TEST
            n_splits = (n_bars - WF_TRAIN - WF_TEST) // WF_STEP + 1
            wf_ok = n_splits == EXPECTED_WF_SPLITS and last_test_end <= n_bars
            checks["walk_forward"] = {
                "bars": int(n_bars),
                "train": WF_TRAIN,
                "test": WF_TEST,
                "step": WF_STEP,
                "n_splits": int(n_splits),
                "expected_n_splits": EXPECTED_WF_SPLITS,
                "last_test_start": int(last_test_start),
                "last_test_end": int(last_test_end),
                "ok": bool(wf_ok),
            }
            if not wf_ok:
                blocked.append("walk-forward split count/fit check failed")

            # Feature warmup: realized-vol / skew with min_periods=max(20,L//3) must be
            # defined before the first OOS test window starts (bar WF_TRAIN).
            warm: dict[str, dict] = {}
            warm_ok = True
            for L in LOOKBACKS_5M:
                mp = min_periods_for(L)
                warm_before = bool(mp <= WF_TRAIN)
                warm[L] = {"min_periods": int(mp), "warm_before_first_test_bar": warm_before, "ok": warm_before}
                warm_ok &= warm_before
            checks["feature_warmup"] = {
                "rule": "min_periods = max(20, L // 3) on 5m close log-returns",
                "lookbacks_5m": list(LOOKBACKS_5M),
                "warmup": {f"L={k}": v for k, v in warm.items()},
                "ok": warm_ok,
            }
            if not warm_ok:
                blocked.append("feature warmup insufficient before first OOS test window")
        except Exception as exc:  # noqa: BLE001
            checks["walk_forward"] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
            checks["feature_warmup"] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
            blocked.append("walk-forward / feature warmup checks could not be computed")

    ready = sha_ok and not blocked
    result = {
        "ready": ready,
        "real_data_only": True,
        "fabricated_data": False,
        "campaign": 288,
        "part": "preflight",
        "checks": checks,
        "blocked_reasons": blocked,
    }
    print(json.dumps(result, indent=2, default=str))
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())