"""Diagnostic: compute real gate values for BTC/ETH on cached Binance data."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd
from data.loader import DataLoader
from utils.cointegration import (
    adf_test,
    engle_granger_test,
    johansen_test,
    half_life_ou,
    estimate_hedge_ratio_ols,
    calculate_spread,
    rolling_cointegration_stability,
    structural_break_check,
    target_schema_diagnostics,
)


def main():
    loader = DataLoader()
    data = loader.load_binance_data(["BTC", "ETH"], "2026-04-01", "2026-10-28", interval="1h")
    data = loader.clean_data(data)
    p1 = data["BTC"].astype(float)
    p2 = data["ETH"].astype(float)
    print(f"n_bars={len(p1)}")

    # Full-sample diagnostics
    diag = target_schema_diagnostics(p1, p2, pair_name="BTC/ETH")
    print("\n=== FULL-SAMPLE GATES ===")
    print(json.dumps(diag["gates"], indent=2))
    print("status:", diag["status"])

    print("\n=== EG ===")
    print(json.dumps(diag["engle_granger"], indent=2, default=str))
    print("\n=== JOHANSEN ===")
    print(json.dumps(diag["johansen"], indent=2, default=str))
    print("\n=== SPREAD ===")
    print(json.dumps(diag["spread"], indent=2, default=str))
    print("\n=== LEG STATIONARITY ===")
    print(json.dumps(diag["leg_stationarity"], indent=2, default=str))
    print("\n=== ROLLING STABILITY ===")
    print(json.dumps(diag["rolling_stability"], indent=2, default=str))
    print("\n=== STRUCTURAL BREAKS ===")
    print(json.dumps(diag["structural_breaks"], indent=2, default=str))

    # Trailing 60-bar window diagnostics (what the strategy actually sees)
    print("\n=== TRAILING 60-BAR WINDOW (last) ===")
    s1 = p1.iloc[-60:]
    s2 = p2.iloc[-60:]
    d60 = target_schema_diagnostics(s1, s2, pair_name="BTC/ETH")
    print("gates:", json.dumps(d60["gates"], default=str))
    print("eg pvalue:", d60["engle_granger"].get("pvalue"))
    print("spread adf pvalue:", d60["spread"]["adf_spread"].get("pvalue"))
    print("hl:", d60["spread"].get("half_life_ou"))
    print("rolling available:", d60["rolling_stability"].get("available"))
    print("rolling notes:", d60["rolling_stability"].get("notes"))

    # Trailing 120-bar
    print("\n=== TRAILING 120-BAR WINDOW (last) ===")
    s1 = p1.iloc[-120:]
    s2 = p2.iloc[-120:]
    d120 = target_schema_diagnostics(s1, s2, pair_name="BTC/ETH")
    print("gates:", json.dumps(d120["gates"], default=str))
    print("rolling available:", d120["rolling_stability"].get("available"))
    print("rolling stable:", d120["rolling_stability"].get("stable"))
    print("rolling n_windows:", d120["rolling_stability"].get("n_windows"))

    # Trailing 720-bar
    print("\n=== TRAILING 720-BAR WINDOW (last) ===")
    s1 = p1.iloc[-720:]
    s2 = p2.iloc[-720:]
    d720 = target_schema_diagnostics(s1, s2, pair_name="BTC/ETH")
    print("gates:", json.dumps(d720["gates"], default=str))
    print("rolling stable:", d720["rolling_stability"].get("stable"))
    print("rolling frac_sig:", d720["rolling_stability"].get("frac_significant"))
    print("rolling n_windows:", d720["rolling_stability"].get("n_windows"))

    # Spread ADF over full sample
    beta = estimate_hedge_ratio_ols(p1, p2)
    spread = calculate_spread(p1, p2, beta)
    print(f"\nbeta={beta}")
    print("spread adf:", adf_test(spread))
    print("spread half_life:", half_life_ou(spread))
    print("structural break:", structural_break_check(p1, p2))


if __name__ == "__main__":
    main()