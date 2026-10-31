# SINGLE DURABLE HANDOFF | 2026-10-31T22:25:02Z | INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**
- **CORE = COINTEGRATION / PAIRS TRADING.** Every other line of work (mean reversion, paper trading, execution realism, Monte Carlo, regime/cost stress) serves cointegration rigor. Cointegration is law.
- Real data only: Binance public REST via `www.binance.com`. Never fabricate.
- Coasting = failure. Every action must produce checkable artifacts, tests, provenance, logs.

## CURRENT VERIFIED STATE (2026-10-31T22:21:50Z)
- Branch: `main`, working tree clean. `use_enriched_gates` default `True` (fail-closed) in `strategies/pairs_trading.py:47`.
- Causality tested explicitly (`test_enriched_gates_causality_trailing_only_no_lookahead_explicit` passes).
- Cointegration diagnostics schema tests pass (10/10).
- Ruff: clean (1 pre-existing E501 in `tests/test_strategies.py:747` fixed).
- `reports/portfolio_real.json` exists (767399 bytes), computed 2026-10-31T17:36:18Z, real_data_only=true, fabricated_data=false.
- From diagnostics: only **POL/BTC** passes EG+Johansen+spread_mr+hl_bounds+leg_stationarity but **rolling_stable_ok=False** (frac_significant_0_05 ~0.049; ~9 windows pass out of ~184; step 24; window 720 bars). All other 16 pairs fail multiple gates (EG mostly false).
- **PRIMARY BLOCKER:** POL/BTC rolling stability — cointegration appears regime/time-varying despite full-sample passing.
- **BOTTLENORE TO REMOVE:** `blocked_routes` is `[]` in `reports/portfolio_real.json` — no failing pair has been honestly marked `blocked_or_insufficient_data` with provenance. Every failing pair is currently left un-resolved. Fix this now.
- Full test suite target: >=555 passed, 0 failures (suite is network-heavy; run with `python -u` and allow time).

## IMMEDIATE INITIAL TASK (START HERE — NO DEVIATION)
**OBJECTIVE:** Close the cointegration rigor loop on real data. For every pair, either (a) pass ALL 7 enriched gates on real Binance data, or (b) be honestly marked `blocked_or_insufficient_data` with full provenance. Do not weaken thresholds. Do not fabricate.

**MANDATORY FIRST ACTIONS (EXECUTE IN ORDER, NO SKIPPING):**
1. **Fix the honest-blocking bottleneck.** Every pair in `reports/portfolio_real.json` cointegration_diagnostics with `all_pass=False` must carry `status: "blocked_or_insufficient_data"`, a non-empty `blocked_routes[]`, and a detailed `rationale` with full provenance (`source`, `real_data_only`, `fabricated_data:false`, `computed_at`). POL/BTC included until proven stable. Empty `blocked_routes` on a failing pair is a blocker itself — do not leave it.
2. **Investigate POL/BTC regime-dependence with real data.** Load POL/BTC from real Binance candles (`data/loader.py` / `DataLoader.load_binance_data`). Split history into periods where rolling windows pass (windows around indices ~7, 64, 65, 114, 119, 120, 121, 147, 182 per current report). Analyze: hedge ratio stability across regimes, vol regimes, ADF/KPSS of spread per regime, structural breaks. Determine if cointegration is regime-dependent or fundamentally unstable.
3. **Test window sensitivity rigorously.** Try alternative window sizes/steps for `rolling_cointegration_stability` (e.g., 400, 500, 600, 800, 1000; steps 12, 24) but only to diagnose — do **NOT** change the pass criterion (>=60% significant at 5% is the bar) without ironclad justification backed by data. If criterion change is considered, it must be documented with evidence and still enforced strictly.
4. **Decide honestly.** If instability is fundamental (no regime makes it stable under strict bar), mark POL/BTC as `blocked_or_insufficient_data` in all artifacts with detailed rationale, full provenance, and `blocked_routes`. If regime-dependent and tradeable only in specific regimes, you must design a causal regime filter (trailing-only, no lookahead) and prove it with tests — otherwise block it.
5. **Sweep all other failing pairs.** Systematically diagnose each failing pair and either fix data issues (real only) or block honestly with provenance.
6. **Re-run portfolio with real data, unbuffered.** `python -u examples/run_portfolio_real.py` must regenerate `reports/portfolio_real.json`.
7. **Verify green.** Run all verification commands below. All tests must remain green (>=555 passed, 0 failures). Ruff clean. mypy clean.

## EXECUTION PLAN (NO SKIPPING)
### 1) HONEST BLOCKING (HIGHEST PRIORITY — REMOVES THE BOTTLENECK)
- File: `reports/portfolio_real.json` cointegration_diagnostics + `blocked_routes`.
- Every failing pair gets `status: "blocked_or_insufficient_data"`, `blocked_routes[]`, `rationale`, provenance.

### 2) POL/BTC DEEP DIVE
- **Files:** `utils/cointegration.py` (rolling_cointegration_stability, comprehensive_cointegration_diagnostics), `strategies/pairs_trading.py`, `data/loader.py`, `examples/run_portfolio_real.py`
- **Data:** Load full POL/BTC series from real Binance. Inspect the specific passing windows from `reports/portfolio_real.json` cointegration_diagnostics for POL/BTC.
- **Analysis:** For each regime (passing windows), test EG/Johansen on that subperiod, check hedge ratio stability, spread MR, HL. Look for regime shifts (vol, trend). Check if beta shifts correlate with instability.
- **Action:** If fundamentally unstable → block with full provenance. If regime-dependent → only implement causal regime filter if provably correct and tested.

### 3) SYSTEMATIC PAIR SWEEP
- Review all pairs in `reports/portfolio_real.json` cointegration_diagnostics. For each failing pair, diagnose root cause (insufficient history, EG fail, Johansen fail, spread MR fail, HL out of bounds, leg non-stationarity, rolling stability, structural breaks). Fix if possible with real data only; otherwise block honestly.

### 4) CAUSALITY & GATE ENFORCEMENT
- Verify enriched gates remain trailing-only/cached causally (already tested). Do not introduce lookahead. Fail-closed remains default.

### 5) REGENERATE ARTIFACTS
- `python -u examples/run_portfolio_real.py` to refresh `reports/portfolio_real.json` with updated diagnostics.

### 6) QUALITY GATES
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
- **NO EMPTY blocked_routes** on a failing pair

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
- Env bottleneck removed: CI failures were caused by missing numpy/pandas in conda env and ruff lint; local venv has deps installed; run `python -m pip install -r requirements.txt` before tests if ModuleNotFoundError.
- **Empty blocked_routes bottleneck removed:** failing pairs must now be honestly blocked with provenance — no pair may skip this.
- **No ambiguity left:** the first action is honest blocking + POL/BTC deep dive. If you are unsure where to start, start there. Nothing else is permitted until that is resolved honestly.

**START NOW. Focus on honest blocking of every failing pair, then POL/BTC rolling stability first — it's the only pair close to passing. Heavy work required. No coasting.**
