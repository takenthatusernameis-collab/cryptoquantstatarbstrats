# DURABLE HANDOFF | TIMESTAMP: 2026-11-03T03:53:01Z | REPO: cryptoquantstatarbstrats
# PRIORITY: COINTEGRATION PAIRS EDGE - FAIL-CLOSED, REAL-DATA ONLY

## REPO SIGNAL (INFERRED)
`cryptoquantstatarbstrats` = Crypto Quant Stat Arb Strategies. **Cointegration pairs is the product edge.**
Everything else exists to support/gate/validate pairs. Treat it as publication-grade research code where fabrication is unacceptable.

## GROUND TRUTH (VERIFIED 2026-11-03T03:53:01Z)
- Critical subset (campaign 29-38 + recertification + permanent cert + diagnostics schema): **125 passed** (`tests/test_cointegration_campaign*_mt.py`, `test_cointegration_recertification_audit_mt.py`, `test_permanent_production_certification_mt.py`, `test_cointegration_diagnostics_schema.py`)
- Lint: `python -m ruff check strategies/ backtest/ utils/ tests/ examples/` → **All checks passed**
- mypy: `python -m mypy backtest strategies utils` → **Success: no issues found in 32 source files**
- Working tree clean. Network: `www.binance.com` serves public klines; loader handles `api.binance.com` 451 honestly.

## IMMEDIATE INITIAL TASK (MUST DO FIRST TURN - NO EXPLORATION-ONLY)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python -m pytest tests/test_cointegration_campaign*_mt.py tests/test_cointegration_recertification_audit_mt.py tests/test_permanent_production_certification_mt.py tests/test_cointegration_diagnostics_schema.py -v
```
**If ANY fail → fix before doing anything else.** Only proceed if all pass. Current state: **ALL PASS**.

## BOTTLENECK REMOVAL (APPLY NOW)
- **Single session active** - no cross-session blockers. Do not wait on board; act.
- **No stale CI branch to chase.** main is green.
- **No data/network blocker.** Real-data paths operational.
- **Remove "analysis paralysis":** do not just audit - trace, harden, verify with tests.
- **Two concrete gaps found in review (fix these in P0):**
  1. `strategies/pairs_trading.py:273-277` per-bar fallback sets `rolling_stable_ok = True` when rolling stability reports `insufficient_data` and recomputes `all_pass` without it. Under `strict_enriched_gates=True`, an unassessable/missing gate must block entries, not pass. This is a fail-open weakening. Fix: never coerce an unassessable gate to True; missing/unknown → blocked under strict.
  2. `utils/cointegration.py:323-330` `comprehensive_cointegration_diagnostics` emits gate keys `engle_granger_pass`, `johansen_pass`, `half_life_pass`, `rolling_stability_pass`, `no_structural_break`, `all_pass`, but `strategies/pairs_trading.py:211-218` and `target_schema_diagnostics` expect `eg_pass`, `johansen_pass`, `spread_mr_pass`, `hl_bounds_pass`, `rolling_stable_ok`, `leg_stationarity_ok`, `all_pass`. Unify `comprehensive_cointegration_diagnostics` gates to the target-schema key set so any diagnostic fed into the strategy is read consistently (fail-closed on missing keys either way).

## NEXT FOCUS CAMPAIGN (HEAVY WORK - CANNOT BE AVOIDED)
**Campaign: "FORTIFY & STRESS-TEST COINTEGRATION GATES"**

### P0 - Gate Integrity (CRITICAL - DO THIS FIRST)
1. **Fix fail-open per-bar fallback** in `strategies/pairs_trading.py` (`CointegrationPairsStrategy.generate_signals`): remove the `rolling_stable_ok = True` coercion when rolling stability is `insufficient_data`; missing/unknown gate → `0.0`/blocked under strict. Add a regression test asserting an unassessable rolling gate blocks entries under strict mode.
2. **Unify gate key schema** in `utils/cointegration.py` `comprehensive_cointegration_diagnostics`: emit `eg_pass`, `johansen_pass`, `spread_mr_pass`, `hl_bounds_pass`, `leg_stationarity_ok`, `rolling_stable_ok`, `all_pass` to match the strategy gate loop and `target_schema_diagnostics`.
3. **Trace strict fail-closed path end-to-end** in `strategies/pairs_trading.py` (`__init__` defaults `use_enriched_gates=True`, `strict_enriched_gates=True`), `_get_enriched_gate()` / gate extraction, and `generate_signals()` entry logic. For every gate key (`eg_pass`, `johansen_pass`, `spread_mr_pass`, `hl_bounds_pass`, `leg_stationarity_ok`, `rolling_stable_ok`, `all_pass`): confirm missing/None/False → entry blocked under strict mode. No permissive fallthrough. Fix any ambiguity.
4. **Harden gate computation** in `utils/cointegration.py`. Enforce trailing-only data (no lookahead). Validate half-life bounds `1 < hl < 500`. Ensure EG/Johansen/spread MR/rolling stability/breaks/leg stationarity produce values strict mode cannot misread as "ok". Trace all code paths that return gate booleans.
5. **Verify engine causality** in `backtest/engine.py` - gates applied before weights; opposing legs preserved; hedge ratio guarded (>1e-18, clipped [1e-6,1e6]); weight normalization correct.
6. **Regression check:** run critical subset after every material change.

### P1 - Real-Data Provenance (CRITICAL)
1. **Audit artifacts**: `reports/portfolio_real.json`, `reports/cointegration_diagnostics_real.json` must have `real_data_only: true`, `fabricated_data: false`, full provenance, `blocked_routes[]` when blocked. Fix if any artifact drifts.
2. **Harden loader/cache**: `data/loader.py`, `data/cache.py`. Keep cache namespace clean. Prefer `www.binance.com` first; on 451/blocks write honest `blocked_or_insufficient_data` with rationale - **never fabricate**.
3. **Test:** `tests/test_cointegration_diagnostics_schema.py` must pass.

### P2 - Stress & Regression Guards (HIGH)
1. **Tighten where weak.** Look for any code path that could coerce None/False to True, or that uses future data. Fix systematically.
2. **Cost/perf.** Keep cost-sensitive tests fast; avoid per-bar recomputation.
3. **Quality gates:** `ruff` clean, `mypy` clean on touched modules. Fix by refactoring/types, never weaken gates.

## MANDATORY DISCIPLINE
- **NO SUMMARY-ONLY TURNS.** Every turn must fix/harden/verify something material on pairs/cointegration.
- **Trace before change.** Read source + relevant tests. Understand causality.
- **Verify relentlessly.** Critical subset after changes; full suite if touching gates/engine/core; always `ruff` + `mypy` if code changes.
- **Fail-closed always.** Never weaken `use_enriched_gates`, `strict_enriched_gates`, or provenance requirements.
- **Publication-grade.** Real-data only. Evidence required.

## SUCCESS CRITERIA (BEFORE STOPPING)
- [ ] Critical subset passes (125 tests)
- [ ] `python -m pytest tests/` exits 0 (765 passed, 1 skipped)
- [ ] `ruff check strategies/ backtest/ utils/ tests/ examples/` exits 0
- [ ] `mypy backtest strategies utils` exits 0
- [ ] No gate/provenance weakening (fail-open gaps above closed)
- [ ] Any changes verified with traceable evidence

**START NOW. Run the initial task (already verified passing). Then pick P0 item 1 - close the `rolling_stable_ok = True` fail-open gap in strategies/pairs_trading.py:273-277 and add a regression test. Do heavy work.**
