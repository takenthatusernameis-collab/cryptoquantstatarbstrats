# DURABLE HANDOFF | 2026-10-31T20:23:00Z | SINGLE MANDATORY NEXT TASK

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**.
- **CORE = COINTEGRATION/PAIRS TRADING.** All other work serves cointegration rigor.
- Real data only: Binance public REST via `www.binance.com`. Never fabricate.
- Coasting = failure. Every action produces checkable artifacts, tests, provenance, logs.

## CURRENT VERIFIED STATE (2026-10-31T20:23:00Z)
- Branch: `main` (clean), up to date with `origin/main`. Last commit `dd32c7c chore(kilo): checkpoint agent session`.
- `use_enriched_gates` default flipped to `True` (fail-closed) in `strategies/pairs_trading.py`.
- Enriched gate tests present (structural breaks flagged, missing/None, causality).
- `pip install -e ".[dev]"` completed. Dependencies installed.
- `ruff check backtest/ strategies/ utils/ tests/ examples/` — **ALL CHECKS PASSED**.
- `reports/portfolio_real.json` exists from previous run (17 pairs including POL/BTC, DOT/BTC, DOT/ETH, AVAX/BTC, LINK/BTC, LTC/BTC).
- **CRITICAL ISSUE**: POL/BTC fails `rolling_stability` (frac_sig ~0.049, stable=False) across all windows [360,480,600,720,840,960]. Engle-Granger/Johansen pass, spread MR ok, HL bounds ok, leg stationarity ok - only rolling stability blocks it.

## BOTTLENECKS REMOVED
- Abandoned `fix/causal-pairs-validation-2026-10-27` branch (do NOT resurrect).
- `fix/noncompounding-overlap-pair-caps-20261030` is destructive sidetrack (deletes data/cache/tests/utils) — do NOT merge.
- Environment deps installed. Env runnable from `main`.

## SINGLE MANDATORY OBJECTIVE (HEAVY WORK — NO COASTING)
**Close the cointegration rigor loop on real data.** Make every pair either (a) pass all 7 enriched gates on real Binance data, or (b) be honestly marked `blocked_or_insufficient_data` with full provenance. Future agents MUST complete this campaign.

### ACTION PLAN (EXECUTE IN ORDER, NO SKIPPING)

#### 1) DIAGNOSE & FIX POL/BTC rolling_stability (BLOCKER)
- **Issue**: POL/BTC shows rolling stability failing badly (frac_significant < 0.1 across all tested windows). Need to understand why.
- **Approach**:
  1. Deep dive into POL/BTC data - length, regime changes, volatility. Check if it's regime-dependent or structural break.
  2. Examine `rolling_cointegration_stability()` implementation again - it does Engle-Granger on rolling windows. Maybe step/window choices? Or data quality?
  3. Consider if the threshold (frac >= 0.6) is too strict for this pair given real market structure. But we cannot just change thresholds without justification - need to understand if it's a real issue.
  4. Try different window sizes more aggressively (e.g., 500, 600). Also look up if there might be structural breaks. The `structural_break_check` does half-sample beta comparison - POL/BTC might have break.
  5. If it's a genuine structural break that makes pair unreliable, HONESTLY mark as blocked with full provenance. Do NOT fabricate.
- **Files**: `utils/cointegration.py`, `strategies/pairs_trading.py`, look up POL/BTC in `reports/portfolio_real.json`

#### 2) EXPAND COVERAGE FOR REMAINING PAIRS (BTC/SOL/ADA/ETH/DOT with hl>500)
- Pairs to scrutinize: DOT/BTC, DOT/ETH, AVAX/BTC, LINK/BTC, LTC/BTC (and others). Check if any have insufficient history or fail gates.
- For pairs with "hl > 500" mentioned in handoff - look up actual half-lives. Or just ensure all pairs in PAIRS get full diagnostics.
- If insufficient history for robust testing, mark `blocked_or_insufficient_data` with rationale and provenance. NO fabrication.

#### 3) ADD CAUSALITY TEST PROVING GATES USE TRAILING DATA ONLY (NO LOOKAHEAD)
- Handoff says "Add a causality test proving gates use trailing data only (no lookahead)."
- Look up how gates are applied - in `CointegrationPairsStrategy.generate_signals()`, when using cached `enriched_diagnostics`, gates are applied as a constant series `enriched_ok = Series(1.0 if ok else 0.0, ...)` for all bars (line ~280-330 in pairs_trading.py). This is CAUSAL - same gates applied to all bars based on full-sample diagnostics. Also the per-bar recomputation path uses trailing windows only (lines ~250-310). The existing test `test_enriched_gates_causality_no_future_leakage_cached` already verifies cached gates don't leak future. But maybe need a stronger/explicit test named for causality? Or add test that proves no lookahead.
- Add a test that would fail if lookahead exists - e.g. shuffle future data, gates should remain identical for past bars. Or construct test where future contains info that would change past if leaked.

#### 4) RE-RUN PORTFOLIO WITH REAL DATA UNBUFFERED
- Run: `python -u examples/run_portfolio_real.py`
- This will regenerate `reports/portfolio_real.json` with updated diagnostics
- Must complete fully, capture output

#### 5) MAINTAIN GREEN SUITE
- `python -m ruff check backtest/ strategies/ utils/ tests/ examples/` must pass
- `python -m pytest tests/ -q` >= 555 passed, 0 failures (isolate hanging enriched-diagnostics tests if needed)
- `python -m mypy backtest/ strategies/ utils/` should pass
- NO commits unless explicitly requested

## HARD CONSTRAINTS
- **REAL DATA ONLY** — isolated tests only with explicit `fabricated_data: true` marker
- **NO SHORTCUTS / NO FABRICATION**
- **PRESERVE GREEN** — >=555 passed, 0 new failures
- **HEAVY MANDATE** — complete full campaign, no coasting
- **COINTEGRATION IS LAW**
- **CAUSAL ONLY** — no lookahead (trailing data only)
- **UNBUFFERED** — use `python -u`

## IMMEDIATE FIRST ACTIONS
1. Load and examine POL/BTC data in detail - regime stability, structural breaks
2. Debug rolling stability calculation more closely
3. Consider if we need to adjust approach: maybe use different window/step, or if pair is fundamentally unstable mark as blocked with detailed provenance
4. Look up all pairs' gate status from current report
5. Add causality test if missing
6. Re-run portfolio

## VERIFICATION COMMANDS
```bash
python -m ruff check backtest/ strategies/ utils/ tests/ examples/
python -m pytest tests/ -q  # >=555 passed, 0 failures
python -m mypy backtest/ strategies/ utils/
python -u examples/run_portfolio_real.py  # refresh reports/portfolio_real.json
```

**START NOW. No exploration for fun. Heavy work required.**
