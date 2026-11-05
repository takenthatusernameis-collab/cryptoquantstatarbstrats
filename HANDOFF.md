# HANDOFF (SINGLE DURABLE) — 2026-11-05T06:05:00Z
REPO: cryptoquantstatarbstrats | CORE EDGE: pairs/spreads/cointegration (MANDATORY PRIORITY #1). Real data only. Fail-closed. No threshold weakening. Causal trailing only.

## INITIAL TASK (CLEAR, HEAVY WORK — DO NOT INVESTIGATE-ONLY)

EXECUTE IN THIS EXACT ORDER. EVERY SESSION MUST LEAVE >=1 CONCRETE ARTIFACT IN `reports/`.

### 1) CONFIRM CURRENT STATE (BLOCKERS ALREADY REMOVED/KNOWN)
- Fresh scan exists: `reports/pairs_candidate_scan_20261105T050821Z.json` (n_pairs_scanned_tf=165, n_pass_all_gates=0).
- Blocked summary exists: `reports/pairs_blocked_summary_20261105T055351Z.json`.
- Known: leg_stationarity_ok fails on ALL 165 (both legs need ADF p<=0.05). Rolling stability assessability fixed. Gates fail-closed and causal.

### 2) BUILD A DEFINITIVE "CLOSEST TO PASSING" LEDGER (REQUIRED)
Create `reports/pairs_leg_stationarity_closest_<UTC_TIMESTAMP>.json` by scanning ALL pairs×TFs from cached real Binance spot (2026-04-01..2026-10-30), resampling 1h→4h/1d as in `examples/run_pair_universe_scan.py`. For each entry record: pair, tf, leg1_pvalue, leg2_pvalue, leg_stationarity_ok, eg_pass/johansen_pass/spread_mr_pass/hl_bounds_pass/rolling_stable_ok/no_structural_break/all_pass, eg_pvalue, frac_significant, n_windows, blocked_routes. Sort by max(leg1_pvalue,leg2_pvalue). Include full gate details for top 50.

### 3) HEAVY CAMPAIGN: FIND ANY HONEST PATH TO PASS (NO WEAKENING)
**HARD CONSTRAINT:** Both legs MUST have ADF p<=0.05 (regression='c', autolag='AIC'). Do NOT change thresholds.
- If ANY pair has both legs stationary with causal trailing windows AND passes all other gates → build walk-forward OOS backtest with fresh proof under `reports/` (honest trades or honest zeros with full diagnostics, real data only).
- If NONE pass leg stationarity after exhaustive honest search across all TFs and the cached universe → write `reports/pairs_leg_stationarity_impossibility_memo_<UTC_TIMESTAMP>.json` with: per-TF distribution of worst-leg p-values, top 10 closest pairs with exact p-values/statistics, confirmation that data cleaning/resampling/causal windows are correct, and concrete explanation why impossible under current gates. No threshold changes.

### 4) MAINTAIN PARITY & VALIDATE
- Keep `strategies/pairs_trading.py` causal per-bar enriched gates, interval caching parity, fail-closed.
- Keep `utils/cointegration.py` assessability intact (>=2 windows). Only fix correctness/assessability bugs.
- Run: `python -m pytest tests/test_cointegration_campaign31_mt.py tests/test_cointegration_diagnostics_schema.py tests/test_pairs_real_market.py -v`
- Lint/mypy: `python -m ruff check utils/cointegration.py strategies/pairs_trading.py && python -m mypy utils/cointegration.py strategies/pairs_trading.py`

## CURRENT STATE
- Branch main clean, up to date. Tests passing (35). ruff/mypy clean on target files.
- 165/165 pairs blocked on leg stationarity. No passing candidates. Real data only, no fabrication.

## BOTTLENECKS
- **Leg stationarity (genuine)**: BTC/ETH/SOL majors and broader universe show leg p-values far above 0.05 on real price levels. This is statistical reality on this window. Do heavy honest work to prove or disprove; never bypass.

## FILES TO FOCUS ON
- `utils/cointegration.py`, `strategies/pairs_trading.py`
- `examples/run_pair_universe_scan.py`, `data/cache.py`, `data/loader.py`
- `reports/` (required artifacts)

## RULES (NON-NEGOTIABLE)
- Real data only. Never fabricate.
- Fail-closed always.
- No threshold weakening (ADF p<=0.05 unchanged).
- Causal only (trailing). No full-history aggregates as per-bar gates.
- Every session leaves >=1 new concrete artifact in `reports/`. No investigation-only loops.
- Commit nothing unless explicitly asked.
