# HANDOFF (SINGLE DURABLE) — 2026-11-05T06:13:25Z

## INITIAL TASK MESSAGE (for next agentic session)
"Next session: complete the two incomplete artifacts (closest-ledger with per-leg ADF p-values, impossibility memo with per-TF worst-leg distributions + top-10 closest pairs). Reuse utils/cointegration._leg_stationarity_detail; sort by max(leg1_pvalue, leg2_pvalue) asc; scan 55 pairs x 3 TFs on cached real Binance spot 2026-04-01..2026-10-30. No threshold weakening, real data only, fail-closed, causal trailing only. Leave >=1 new concrete artifact in reports/. Run pytest + ruff + mypy."
REPO: cryptoquantstatarbstrats | CORE EDGE: pairs/spreads/cointegration (MANDATORY PRIORITY #1). Real data only. Fail-closed. No threshold weakening. Causal trailing only.

## VERIFIED STATE (this session, direct measurement)
- **Leg stationarity is a genuine statistical blocker, NOT a tooling artifact.** Verified directly on cached real Binance 1h spot (2026-04-01..2026-10-30, n=5112 bars), `adf_test(regression='c')`:
  - BTC p=0.6502 | ETH p=0.6570 | SOL p=0.6707 | ADA p=0.4231 | XRP p=0.3223
  - All far above the 0.05 gate. Under `regression='c'` (constant+drift) crypto price levels are non-stationary. This is real data, not a bug.
- Existing artifacts confirmed present: `pairs_candidate_scan_20261105T050821Z.json` (165 pairs×TF, 0 pass), `pairs_blocked_summary_20261105T055351Z.json`, `pairs_leg_stationarity_closest_from_scan_20261105T060930Z.json` (165 entries, 0 pass), `pairs_leg_stationarity_impossibility_memo_20261105T060941Z.json`.
- Tests green: `pytest tests/test_cointegration_campaign31_mt.py tests/test_cointegration_diagnostics_schema.py tests/test_pairs_real_market.py` = 35 passed.
- Branch main clean, up to date, working tree clean.

## REMAINING WORK (the two artifacts are INCOMPLETE vs spec — this is the bottleneck)
The closest-ledger and impossibility-memo exist but **lack the per-leg ADF p-values that are the entire basis of the conclusion**. The ledger is sorted by `eg_pvalue`, not by `max(leg1_pvalue, leg2_pvalue)`, and `leg1_pvalue`/`leg2_pvalue` are absent. The memo lacks per-TF worst-leg distributions and top-10 closest pairs with exact p-values. Finish these two properly.

### TASK 1 — Rebuild the "closest to passing" ledger WITH per-leg p-values (REQUIRED)
Write `reports/pairs_leg_stationarity_closest_<UTC>.json`.
- Scan ALL pairs×TFs from cached real Binance spot (2026-04-01..2026-10-30), resample 1h→4h/1d exactly as `examples/run_pair_universe_scan.py` (11 symbols: ADA AVAX BNB BTC DOT ETH LINK LTC POL SOL XRP → 55 pairs × 3 TFs = 165).
- For each entry record: pair, tf, **leg1_pvalue, leg2_pvalue** (ADF, regression='c', autolag='AIC'), leg_stationarity_ok, eg_pass/johansen_pass/spread_mr_pass/hl_bounds_pass/rolling_stable_ok/no_structural_break/all_pass, eg_pvalue, frac_significant, n_windows, blocked_routes, plus full gate detail.
- **Sort by max(leg1_pvalue, leg2_pvalue) ascending** (closest to passing first). Include full gate details for top 50.
- Reuse `utils/cointegration._leg_stationarity_detail(adf1, adf2)` — it already returns leg1_pvalue/leg2_pvalue (cointegration.py:742). Do not recompute ADF inline; call the existing function.

### TASK 2 — Write the definitive impossibility memo (REQUIRED)
Write `reports/pairs_leg_stationarity_impossibility_memo_<UTC>.json` with:
- Per-TF (1h/4h/1d) distribution of worst-leg p-values (min/median/max, and count with p<=0.05).
- Top 10 closest pairs (by worst-leg p-value) with exact p-values and full statistics.
- Explicit confirmation that data cleaning (`loader.clean_data`), resampling (real `last()` aggregation), and causal trailing windows are correct.
- Concrete explanation of why impossible under current gates. **No threshold changes.**

### TASK 3 — Maintain parity & validate (REQUIRED)
- Keep `strategies/pairs_trading.py` causal per-bar enriched gates, interval caching parity, fail-closed.
- Keep `utils/cointegration.py` assessability intact (>=2 windows). Only fix correctness/assessability bugs.
- Run: `python -m pytest tests/test_cointegration_campaign31_mt.py tests/test_cointegration_diagnostics_schema.py tests/test_pairs_real_market.py -v`
- Lint/mypy: `python -m ruff check utils/cointegration.py strategies/pairs_trading.py && python -m mypy utils/cointegration.py strategies/pairs_trading.py`

## BOTTLENECKS
- **Leg stationarity (genuine, verified)**: BTC/ETH/SOL majors show leg p-values ~0.65 on real price levels. This is statistical reality on this window. Do heavy honest work to prove or disprove; never bypass. The fix is to COMPLETE the two artifacts with the p-value evidence, not to search for a passing pair (none exists on this universe/window).

## FILES TO FOCUS ON
- `utils/cointegration.py` (esp. `_leg_stationarity_detail` at :742, `target_schema_diagnostics` at :805, `adf_test` at :26)
- `examples/run_pair_universe_scan.py`, `data/cache.py`, `data/loader.py`
- `reports/` (required artifacts)

## RULES (NON-NEGOTIABLE)
- Real data only. Never fabricate.
- Fail-closed always.
- No threshold weakening (ADF p<=0.05 unchanged).
- Causal only (trailing). No full-history aggregates as per-bar gates.
- Every session leaves >=1 new concrete artifact in `reports/`. No investigation-only loops.
- Commit nothing unless explicitly asked.