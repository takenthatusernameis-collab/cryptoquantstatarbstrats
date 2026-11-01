# SINGLE DURABLE HANDOFF | 2026-11-01T09:08:32Z | INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**
- **CORE = COINTEGRATION / PAIRS TRADING.** Every other line of work serves cointegration rigor. Cointegration is law.
- Real data only: Binance public REST via `www.binance.com`. Never fabricate.
- Coasting = failure. Every action must produce checkable artifacts, tests, provenance, logs.

## CURRENT VERIFIED STATE (2026-11-01T09:08:32Z)
- Branch: `main`, working tree clean. Up to date with `origin/main`.
- `use_enriched_gates` default `True` (fail-closed) in `strategies/pairs_trading.py:47`. Enriched gates enforced strictly.
- **CAMPAIGN 1 DONE:** `reports/cointegration_diagnostics_real.json` written (2026-11-01T09:08:32Z) via `examples/run_cointegration_diagnostics_real.py`. Real cached 1h Binance candles (2026-04-01 to 2026-10-30, 5112 bars, all 11 symbols) — no network used. All 17 pairs diagnosed with full gates + `blocked_routes[]` + rationale + provenance.
- **POL/BTC confirmed:** `eg_pass=true`, `johansen_pass=true`, `spread_mr_pass=true`, `hl_bounds_pass=true`, `leg_stationarity_ok=true`, `rolling_stable_ok=false`. Blocked **only** on `rolling_stability` (`frac_significant_0_05≈0.049`, ~9/184 windows at p<0.05, window=720 step=24). All other gates pass on real data.
- **All other 16 pairs:** honestly `blocked_or_insufficient_data`. Every one fails `engle_granger` (no cointegration on this window) plus `rolling_stability`; several also fail `johansen`, `spread_mean_reversion`, `hl_bounds`. Non-empty `blocked_routes[]` recorded for each.
- `reports/portfolio_real.json` (~664KB) still has all 17 pairs `blocked_or_insufficient_data` (gates present but stale); the recomputed artifact is `reports/cointegration_diagnostics_real.json`.
- `reports/.portfolio_real_checkpoint.json` is **0 bytes** (empty). No `reports/portfolio_real_regen.log` exists.
- **REGEN IS NOT RUNNING.** No `run_portfolio_real.py` process. Do not wait for a regen that is not running. Do not block on full portfolio regeneration.
- **BOTTLENECK — TEST SUITE SPEED:** `python -m pytest tests/ -q` exceeds a 5-minute block (too slow for one session). Use targeted invocation instead: `python -m pytest tests/test_cointegration_diagnostics_schema.py tests/test_strategies.py -q` (102 passed, 0 failures) plus `python -m ruff check ...` (clean).

## BOTTLENECKS REMOVED
1. **Regen not running** — resolved by not waiting. Do not attempt to resume/interrupt `run_portfolio_real.py`. Use the fast targeted diagnostic sweep (done) instead of full portfolio/bootstrap.
2. **Empty gates / lost diagnostics** — resolved: `reports/cointegration_diagnostics_real.json` now has full per-pair gates + `blocked_routes[]` + rationale + provenance for all 17 pairs on real cached data. Locked in by tests in `tests/test_cointegration_diagnostics_schema.py` (artifact exists, real-data-only, all 17 pairs, full schema, honest-blocking invariant, POL/BTC blocked only on rolling_stability, no pair passes all gates).
3. **Network dependence** — removed: `DataLoader.fetch_with_provenance(use_cache=True)` reads from `data/cache/`. Diagnostics run locally without hitting Binance.
4. **Test-suite slowness** — mitigated: do not run the full suite in one session; run the targeted verification commands below.

## IMMEDIATE INITIAL TASK (START HERE — NO DEVIATION)
**OBJECTIVE:** Close the cointegration rigor loop. Campaign 1 is complete. Next: **POL/BTC deep dive (Campaign 2)** — decide whether POL/BTC is regime-filterable with a trailing-only causal filter (tradeable) or fundamentally/temporally unstable (keep honestly blocked). No threshold weakening without ironclad evidence+tests. No fabrication. No coasting.

**MANDATORY FIRST ACTIONS (IN ORDER):**
1. **POL/BTC deep dive (highest ROI)** — Confirm POL/BTC passes EG (p<0.001), Johansen (rank>=1), leg stationarity, half-life bounds, spread mean reversion, and fails only `rolling_stability` (`frac_significant_0_05~0.049`, ~9/184 windows at p<0.05, window=720 step=24). Analyze passing vs failing windows: hedge ratio stability, vol regime, correlation, ADF/KPSS of spread per regime. Passing window start bars: 168, 1536, 1560, 2736, 2856, 2880, 2904, 3528, 4368.
2. **Decide POL/BTC fate** —
   - If regime-filterable with a **trailing-only, causal, no-lookahead** filter: design it, add to `strategies/pairs_trading.py` with tests proving no lookahead, verify it only allows trading in passing regimes, integrate with enriched gates.
   - If fundamentally/temporally unstable: keep `blocked_or_insufficient_data` with full provenance explaining why. Do NOT weaken `rolling_stability` threshold.
3. **(Optional, only after POL/BTC decision)** Revisit remaining 16 pairs: all fail EG on this window; honest blocking is correct. Record already persisted in `reports/cointegration_diagnostics_real.json`. Do not weaken thresholds to force pairs through.
4. **Verify** — Run targeted tests (`python -m pytest tests/test_cointegration_diagnostics_schema.py tests/test_strategies.py -q` = 102 passed, 0 failures), `python -m ruff check backtest/ strategies/ utils/ tests/ examples/` clean. Preserve green.

## FOCUS CAMPAIGN (HEAVY WORK REQUIRED — NON-OPTIONAL)
The future agent must not avoid this. Execute in order; each step produces a checkable artifact.

### Campaign 1: Cointegration diagnostics recompute (real data) — COMPLETE
- Files: `utils/cointegration.py`, `examples/run_cointegration_diagnostics_real.py`
- Deliverable: `reports/cointegration_diagnostics_real.json` with per-pair gate values + `blocked_routes[]` + provenance for all 17 pairs, persisted to disk. Tests added in `tests/test_cointegration_diagnostics_schema.py`.
- Gate: `all_pass` must be `True` to trade; otherwise `blocked_or_insufficient_data` with non-empty `blocked_routes`.

### Campaign 2: POL/BTC regime analysis + causal filter (if viable) — NEXT
- Files: `strategies/pairs_trading.py`, `utils/cointegration.py`
- Analyze hedge ratio stability in passing vs failing windows, vol regimes, correlation structure, ADF/KPSS of spread per regime.
- Question: regime-dependent (tradeable with causal filter) or temporally unstable (unfit)?
- If viable: trailing-only causal regime filter + tests proving no lookahead + integration with enriched gates.

### Campaign 3: Bottleneck removal / iteration speed
- Full `pytest tests/` is too slow for one session (>5 min). Keep using targeted test invocation. If any step blocks > one session on expensive compute, write a fast targeted script (reduce bootstrap, skip multi-timeframe, cache) or narrow scope to cointegration diagnostics only. Preserve schema. Parallelize/cache where possible.

## HARD CONSTRAINTS
- **REAL DATA ONLY** — no fabrication
- **NO WEAKENING THRESHOLDS** without ironclad justification + tests
- **PRESERVE GREEN** — targeted tests 102 passed, 0 failures; ruff clean
- **CAUSAL ONLY** — no lookahead
- **HONEST BLOCKING** — if cannot pass all gates, mark `blocked_or_insufficient_data` with full provenance, non-empty `blocked_routes`
- **HEAVY MANDATE** — no coasting, do the work

## VERIFICATION COMMANDS
```bash
python -m ruff check backtest/ strategies/ utils/ tests/ examples/
python -m pytest tests/test_cointegration_diagnostics_schema.py tests/test_strategies.py -q  # 102 passed, 0 failures
```

**START NOW.** POL/BTC regime analysis is the next task. Do not wait on a regen that is not running.
