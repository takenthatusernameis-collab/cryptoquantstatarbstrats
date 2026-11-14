#!/usr/bin/env python3
"""Quick format verification for C300 zips before writing the full ingest."""
import io, urllib.request, zipfile
import pandas as pd

HOST = "https://data.binance.vision"
KLINE_COLUMNS = ["open_time","open","high","low","close","volume","close_time","quote_volume","count","taker_buy_volume","taker_buy_quote_volume","ignore"]

def read_zip_csv(zip_bytes, kind="klines"):
    zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    name = zf.namelist()[0]
    raw = zf.read(name)
    if kind == "funding":
        return pd.read_csv(io.BytesIO(raw)), name
    df = pd.read_csv(io.BytesIO(raw), header=None, names=KLINE_COLUMNS)
    header_row = len(df) and str(df["open_time"].iloc[0]) == "open_time"
    if header_row:
        df = df.iloc[1:].reset_index(drop=True)
    df["open_time"] = pd.to_numeric(df["open_time"], errors="coerce")
    df = df.dropna(subset=["open_time"])
    for c in ("open","high","low","close","volume"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df, name

def get(url, timeout=60):
    req = urllib.request.Request(url, method="GET", headers={"User-Agent":"kilo-c300-verify"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read()

checks = [
    ("perp 2020-01 (expect headerless)", f"{HOST}/data/futures/um/monthly/klines/BTCUSDT/5m/BTCUSDT-5m-2020-01.zip", "klines"),
    ("perp 2022-01 (expect header)", f"{HOST}/data/futures/um/monthly/klines/BTCUSDT/5m/BTCUSDT-5m-2022-01.zip", "klines"),
    ("spot 2020-01", f"{HOST}/data/spot/monthly/klines/BTCUSDT/5m/BTCUSDT-5m-2020-01.zip", "klines"),
    ("spot 2023-03 (gap month)", f"{HOST}/data/spot/monthly/klines/BTCUSDT/5m/BTCUSDT-5m-2023-03.zip", "klines"),
    ("spot 2026-10 (last month)", f"{HOST}/data/spot/monthly/klines/BTCUSDT/5m/BTCUSDT-5m-2026-10.zip", "klines"),
    ("funding 2020-01", f"{HOST}/data/futures/um/monthly/fundingRate/BTCUSDT/BTCUSDT-fundingRate-2020-01.zip", "funding"),
]
for label, url, kind in checks:
    try:
        status, data = get(url)
        df, name = read_zip_csv(data, kind)
        first = df.iloc[0].to_dict() if len(df) else {}
        last = df.iloc[-1].to_dict() if len(df) else {}
        print(f"[{status}] {label}: rows={len(df)} file={name}")
        print(f"   first open_time={first.get('open_time')} close={first.get('close')}")
        print(f"   last  open_time={last.get('open_time')} close={last.get('close')}")
        if kind == "funding":
            print(f"   cols={list(df.columns)} first_calc={first.get('calc_time')} interval={first.get('funding_interval_hours')} rate={first.get('last_funding_rate')}")
    except Exception as e:
        print(f"[ERR] {label}: {type(e).__name__}: {e}")