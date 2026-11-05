# HANDOFF (SINGLE DURABLE) — 2026-11-05T06:49:30Z

## INITIAL TASK MESSAGE (for next agentic session)
"PRIORITY 1 — CORE EDGE (pairs/spreads/cointegration). Complete the two incomplete artifacts on REAL Binance spot (cached, 2026-04-01..2026-10-30).
1) Rebuild `reports/pairs_leg_stationarity_closest_<UTC>.json` with per-leg ADF p-values (regression='c', autolag='AIC') for ALL 55 pairs × 3 TFs (1h/4h/1d). Reuse `utils.cointegration._leg_stationarity_detail(adf1,adf2)`. Sort by `max(leg1_pvalue, leg2_pvalue)` asc. Include `leg1_pvalue`, `leg2_pvalue`, `leg_stationarity_ok`, all gates, `eg_pvalue`, `frac_significant`, `n_windows`, `blocked_routes`, full details for top 50.
2) Rebuild `reports/pairs_leg_stationarity_impossibility_memo_<UTC>.json` with per-TF worst-leg distributions (min/median/max, count p<=0.05), top-10 closest pairs with exact p-values, explicit confirmation of `loader.clean_data`, real `last()` resampling, causal trailing windows, and concrete explanation why impossible under current gates (no threshold weakening).
Use `examples/run_pair_universe_scan.py` logic. Real data only, fail-closed, causal trailing only, no threshold weakening. Leave >=1 new concrete artifact. Run `pytest tests/test_cointegration_campaign31_mt.py tests/test_cointegration_diagnostics_schema.py tests/test_pairs_real_market.py -v` and `ruff`/`mypy` on `utils/cointegration.py strategies/pairs_trading.py`."

## VERIFIED STATE
- **Leg stationarity is a genuine blocker (verified).** Cached real 1h (2026-04-01..2026-10-30, n=5112): BTC p=0.6502, ETH p=0.6570, SOL p=0.6707, ADA p=0.4231, XRP p=0.3223 (all >> 0.05). Under `regression='c'` price levels are non-stationary. Real data, not tooling.
- Existing (incomplete): `pairs_candidate_scan_20261105T050821Z.json` (165×TF, 0 pass), `pairs_blocked_summary_20261105T055351Z.json`, `pairs_leg_stationarity_closest_from_scan_20261105T060930Z.json` (missing per-leg p-values, sorted by eg_pvalue), `pairs_leg_stationarity_impossibility_memo_20261105T060941Z.json` (missing per-TF worst-leg distributions + top-10).
- Tests green: 35 passed across the three cointegration/pairs test files. Branch clean.

## REMAINING WORK (BOTTLENECK)
Complete the two artifacts above with full p-value evidence. Do **not** search for a passing pair on this universe/window (none exists). Do **not** weaken gates. Prove/disprove honestly with artifacts.

## FILES TO FOCUS ON
- `utils/cointegration.py` (`_leg_stationarity_detail` :742, `target_schema_diagnostics`, `adf_test`)
- `examples/run_pair_universe_scan.py`
- `data/cache.py`, `data/loader.py`
- `reports/`

## RULES (NON-NEGOTIABLE)
- Real data only. Never fabricate.
- Fail-closed always.
- No threshold weakening (ADF p<=0.05 unchanged).
- Causal only (trailing). No full-history aggregates as per-bar gates.
- Every session leaves >=1 new concrete artifact in `reports/`. No investigation-only loops.
- Commit nothing unless explicitly asked.
