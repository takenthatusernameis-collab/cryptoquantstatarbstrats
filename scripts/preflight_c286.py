#!/usr/bin/env python3
"""C286 preflight: verify every real-data cache needed by the 5m execution overlay.

C286 re-runs the C285 volume-conditioned cross-sectional signal with 5m
execution on the real 26,208-bar 5m spot cache.  This preflight verifies:

- SHA256-from-bytes of the 5m spot cache + meta, and of the 1h quote-volume
  cache + meta + provenance;
- meta JSON real/fabricated flags (fail closed on any mismatch);
- the 5m window is exactly 26208 x 11, 2026-08-01T00:00Z -> 2026-10-30T23:55Z,
  zero NaNs, duplicate-free, 5m spacing;
- the 1h quote-volume cache has 5112 finite, strictly positive bars per asset;
- causal alignment: a 1h volume observation at bar t is only usable at 5m bars
  at/after t+1h; the signal (which uses data up to t-1) is warm before the 5m
  window starts for every pre-registered lookback L in {168, 336, 720};
- walk-forward split math: train=720, test=168, step=168 -> 151 OOS splits and
  the last OOS test window fits inside the cache.

The script never fetches, imputes, resamples, or fabricates data.  Exit code 0
iff every check passes; any mismatch or missing file is a fail-closed blocker.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pickle
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

VOLUME = CACHE / "volume_1h_full.pkl"
VOLUME_META = CACHE / "volume_1h_full.meta.json"
VOLUME_PROVENANCE = CACHE / "volume_1h_full.provenance.json"
VOLUME_SHA = "4365895387de4e542165fd331e39da40d455a3de24c7254eb67ba890053d193c"
VOLUME_META_SHA = "4d321584d3c687ad9956908c0179a1eae7d629c296c491e1e5ad1259a890c616"
VOLUME_PROVENANCE_SHA = "c7ff2f27ec5a668128e4856f809efde4922563dba87be0648be6d802c6d21c89"

SYMBOLS = ("ADA", "AVAX", "BNB", "BTC", "DOT", "ETH", "LINK", "LTC", "POL", "SOL", "XRP")
EXPECTED_5M_SHAPE = (26208, 11)
EXPECTED_5M_START = "2026-08-01 00:00:00+00:00"
EXPECTED_5M_END = "2026-10-30 23:55:00+00:00"
EXPECTED_VOLUME_BARS = 5112
LOOKBACKS_1H = (168, 336, 720)
WF_TRAIN = 720
WF_TEST = 168
WF_STEP = 168
EXPECTED_WF_SPLITS = 151


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_pickle(path: Path):
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit JSON summary (default)")
    parser.parse_args()

    checks: dict = {}
    blocked: list[str] = []

    sha_ok = True
    sha_ok &= check_sha(checks, "spot_5m_sha", SPOT_5M, SPOT_5M_SHA)
    sha_ok &= check_sha(checks, "spot_5m_meta_sha", SPOT_5M_META, SPOT_5M_META_SHA)
    sha_ok &= check_sha(checks, "volume_1h_sha", VOLUME, VOLUME_SHA)
    sha_ok &= check_sha(checks, "volume_1h_meta_sha", VOLUME_META, VOLUME_META_SHA)
    sha_ok &= check_sha(checks, "volume_1h_provenance_sha", VOLUME_PROVENANCE, VOLUME_PROVENANCE_SHA)

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
            "ok": bool(flags_ok),
        }
        if not flags_ok:
            blocked.append("spot_5m_meta flags/interval/rows/symbols mismatch")
    except Exception as exc:  # noqa: BLE001
        checks["spot_5m_meta"] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        blocked.append("spot_5m_meta could not be read")

    try:
        meta_vol = json.loads(VOLUME_META.read_text())
        vol_flags_ok = (
            meta_vol.get("real_data_only") is True
            and meta_vol.get("fabricated_data") is False
        )
        checks["volume_1h_meta"] = {
            "real_data_only": meta_vol.get("real_data_only"),
            "fabricated_data": meta_vol.get("fabricated_data"),
            "ok": bool(vol_flags_ok),
        }
        if not vol_flags_ok:
            blocked.append("volume_1h_meta real/fabricated flags mismatch")
        prov = json.loads(VOLUME_PROVENANCE.read_text())
        prov_ok = (
            prov.get("real_data_only") is True
            and prov.get("fabricated_data") is False
            and prov.get("sha256_pkl") == VOLUME_SHA
        )
        checks["volume_1h_provenance"] = {
            "real_data_only": prov.get("real_data_only"),
            "fabricated_data": prov.get("fabricated_data"),
            "sha256_pkl_matches": prov.get("sha256_pkl") == VOLUME_SHA,
            "ok": bool(prov_ok),
        }
        if not prov_ok:
            blocked.append("volume_1h_provenance flags/sha mismatch")
    except Exception as exc:  # noqa: BLE001
        checks["volume_1h_meta"] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        checks["volume_1h_provenance"] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        blocked.append("volume meta/provenance could not be read")

    spot_5m = None
    volume = None

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
            "columns": [str(c) for c in spot_5m.columns],
            "ok": (
                shape_5m == EXPECTED_5M_SHAPE
                and nan_5m == 0
                and dup_5m == 0
                and str(idx.min()) == EXPECTED_5M_START
                and str(idx.max()) == EXPECTED_5M_END
                and spacing_ok
                and tuple(str(c) for c in spot_5m.columns) == SYMBOLS
            ),
        }
        if not checks["spot_5m"]["ok"]:
            blocked.append("spot_5m window/shape/nan/duplicate/spacing check failed")
    except Exception as exc:  # noqa: BLE001
        checks["spot_5m"] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        blocked.append("spot_5m could not be loaded")

    try:
        volume = load_pickle(VOLUME)
        if not isinstance(volume, dict):
            raise TypeError("volume cache is not a dict of symbol -> Series")
        per_symbol: dict[str, dict] = {}
        volume_ok = True
        for symbol in SYMBOLS:
            series = volume.get(symbol)
            if series is None:
                per_symbol[symbol] = {"present": False, "ok": False}
                volume_ok = False
                continue
            series = pd.Series(series).sort_index()
            bars = int(series.shape[0])
            nan_count = int(series.isna().sum())
            nonfinite = int((~np.isfinite(series.to_numpy(dtype=float))).sum())
            ok = (
                bars == EXPECTED_VOLUME_BARS
                and nan_count == 0
                and nonfinite == 0
                and bool((series.dropna() > 0).all())
            )
            per_symbol[symbol] = {
                "present": True,
                "bars": bars,
                "nan_count": nan_count,
                "nonfinite_count": nonfinite,
                "start": str(series.index.min()),
                "end": str(series.index.max()),
                "ok": ok,
            }
            volume_ok &= ok
        checks["volume_1h"] = {"symbols": per_symbol, "ok": volume_ok}
        if not volume_ok:
            blocked.append("volume_1h symbol/bar/finite/positive check failed")
    except Exception as exc:  # noqa: BLE001
        checks["volume_1h"] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        blocked.append("volume_1h could not be loaded")

    if spot_5m is not None and volume is not None:
        try:
            first_volume = next(iter(volume.values()))
            volume_index = pd.DatetimeIndex(pd.to_datetime(first_volume.index, utc=True)).sort_values()
            volume_start = volume_index.min()
            m5_index = pd.DatetimeIndex(spot_5m.index)
            alignment: dict[str, dict] = {}
            align_ok = True
            for lookback in LOOKBACKS_1H:
                signal_bar = volume_index[lookback]
                available_from = signal_bar + pd.Timedelta(hours=1)
                eligible = m5_index[m5_index >= available_from]
                warm_before_window = bool(available_from <= m5_index.min())
                first_eligible = eligible.min() if len(eligible) else None
                ok = len(eligible) > 0 and warm_before_window
                alignment[f"L={lookback}"] = {
                    "signal_bar": str(signal_bar),
                    "available_from_5m": str(available_from),
                    "eligible_5m_bars": int(len(eligible)),
                    "first_eligible_5m_bar": str(first_eligible) if first_eligible is not None else None,
                    "warm_before_5m_window": warm_before_window,
                    "ok": ok,
                }
                align_ok &= ok
            checks["causal_alignment_1h_to_5m"] = {
                "alignment": alignment,
                "ok": align_ok,
                "note": "1h volume at bar t is usable only at 5m bars >= t+1h; signal uses data through t-1.",
            }
            if not align_ok:
                blocked.append("causal 1h->5m alignment failed for at least one lookback")

            n_bars = len(m5_index)
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
        except Exception as exc:  # noqa: BLE001
            checks["causal_alignment_1h_to_5m"] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
            checks["walk_forward"] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
            blocked.append("causal alignment / walk-forward checks could not be computed")
    else:
        blocked.append("alignment skipped because a cache failed to load")

    ready = sha_ok and not blocked
    result = {
        "ready": ready,
        "real_data_only": True,
        "fabricated_data": False,
        "campaign": 286,
        "part": "preflight",
        "checks": checks,
        "blocked_reasons": blocked,
    }
    print(json.dumps(result, indent=2, default=str))
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())