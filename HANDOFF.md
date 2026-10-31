# SINGLE DURABLE HANDOFF | 2026-10-31T22:03:00Z | INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**
- **CORE = COINTEGRATION/PAIRS TRADING.** All other work serves cointegration rigor.
- Real data only: Binance public REST via `www.binance.com`. Never fabricate.
- Coasting = failure. Every action must produce checkable artifacts, tests, provenance, logs.

## CURRENT VERIFIED STATE (2026-10-31T22:03:00Z)
- Branch: `main` (clean). Working tree may have unstaged changes.
- `use_enriched_gates` default `True` (fail-closed) in `strategies/pairs_trading.py`.
- Causality tested explicitly (`test_enriched_gates_causality_trailing_only_no_lookahead_explicit` passes).
- Cointegration diagnostics schema tests pass (10/10). Strategy tests healthy.
- `reports/portfolio_real.json` exists (767399 bytes). From diagnostics: only **POL/BTC** passes EG+Johansen+spread_mr+hl_bounds/leg_stationarity but **rolling_stability_ok=False** (frac_significant_0_05 ~0.049 across rolling windows; only ~9 windows pass out of ~184). All other pairs fail multiple gates.
- **PRIMARY BLOCKER:** POL/BTC rolling stability — cointegration appears regime/time-varying despite full-sample passing.

## IMMEDIATE INITIAL TASK (START HERE - NO DEVIATION)
**OBJECTIVE:** Close the cointegration rigor loop on real data. For every pair, either (a) pass ALL 7 enriched gates on real Binance data, or (b) be honestly marked `blocked_or_insufficient_data` with full provenance. Do not weaken thresholds. Do not fabricate.

**MANDATORY FIRST ACTION (EXECUTE NOW):**
1. **Investigate POL/BTC regime-dependence with real data.** Load POL/BTC from real Binance candles (use `data/loader.py` / `DataLoader.load_binance_data`). Split history into periods where rolling windows pass (windows around indices ~7,64,65,114,119,120,121,147,182 per current report). Analyze: hedge ratio stability across regimes, vol regimes, ADF/KPSS of spread per regime, structural breaks. Determine if cointegration is regime-dependent or fundamentally unstable.
2. **Test window sensitivity rigorously.** Try alternative window sizes/steps for `rolling_cointegration_stability` (e.g., 400, 500, 600, 800, 1000; steps 12, 24) but only to diagnose - do **NOT** change the pass criterion (>=60% significant at 5% is the bar) without ironclad justification backed by data. If criterion change is considered, it must be documented with evidence and still enforced strictly.
3. **Decide honestly.** If instability is fundamental (no regime makes it stable under strict bar), mark POL/BTC as `blocked_or_insufficient_data` in all artifacts with detailed rationale, full provenance, and `blocked_routes` as appropriate. If regime-dependent and tradeable only in specific regimes, you must design a causal regime filter (trailing-only, no lookahead) and prove it with tests - otherwise block it.
4. **Sweep all other failing pairs.** Systematically diagnose each failing pair and either fix data issues (real only) or block honestly with provenance.
5. **Re-run portfolio with real data, unbuffered.** `python -u examples/run_portfolio_real.py` must regenerate `reports/portfolio_real.json`.
6. **Verify green.** Run all verification commands below. All tests must remain green (>=555 passed, 0 failures).

## EXECUTION PLAN (NO SKIPPING)
### 1) POL/BTC DEEP DIVE (HIGHEST PRIORITY)
- **Files:** `utils/cointegration.py` (rolling_cointegration_stability, comprehensive_cointegration_diagnostics), `strategies/pairs_trading.py`, `data/loader.py`, `examples/run_portfolio_real.py`
- **Data:** Load full POL/BTC series from real Binance. Inspect the specific passing windows from `reports/portfolio_real.json` cointegration_diagnostics for POL/BTC.
- **Analysis:** For each regime (passing windows), test EG/Johansen on that subperiod, check hedge ratio stability, spread MR, HL. Look for regime shifts (vol, trend). Check if beta shifts correlate with instability.
- **Action:** If fundamentally unstable -> block with full provenance. If regime-dependent -> only implement causal regime filter if provably correct and tested.

### 2) SYSTEMATIC PAIR SWEEP
- Review all pairs in `reports/portfolio_real.json` cointegration_diagnostics. For each failing pair, diagnose root cause (insufficient history, EG fail, Johansen fail, spread MR fail, HL out of bounds, leg non-stationarity, rolling stability, structural breaks). Fix if possible with real data only; otherwise block honestly.

### 3) CAUSALITY & GATE ENFORCEMENT
- Verify enriched gates remain trailing-only/cached causally (already tested). Do not introduce lookahead. Fail-closed remains default.

### 4) REGENERATE ARTIFACTS
- `python -u examples/run_portfolio_real.py` to refresh `reports/portfolio_real.json` with updated diagnostics.

### 5) QUALITY GATES
- Lint, tests, schema validation all must pass.

## HARD CONSTRAINTS
- **REAL DATA ONLY** — isolated tests only with explicit `fabricated_data: true` marker
- **NO SHORTCUTS / NO FABRICATION**
- **PRESERVE GREEN** — >=555 passed, 0 new failures
- **HEAVY MANDATE** — complete full campaign, no coasting
- **COINTEGRATION IS LAW**
- **CAUSAL ONLY** — no lookahead (trailing data only)
- **UNBUFFERED** — use `python -u` for long runs
- **HONEST BLOCKING** — if a pair cannot pass all gates, mark blocked_or_insufficient_data with provenance

## VERIFICATION COMMANDS (MUST RUN)
```bash
python -m ruff check backtest/ strategies/ utils/ tests/ examples/
python -m pytest tests/test_cointegration_diagnostics_schema.py tests/test_strategies.py -v
python -m pytest tests/ -q  # >=555 passed, 0 failures
python -u examples/run_portfolio_real.py  # refresh reports/portfolio_real.json
```

## BOTTLENECK REMOVAL
- All previous sidetracks removed. Focus is singular: cointegration rigor.
- No network assumptions that block real data path via www.binance.com.
- Causality already proven; gates are fail-closed.

**START NOW. Focus on POL/BTC rolling stability first - it's the only pair close to passing. Heavy work required. No coasting.**
