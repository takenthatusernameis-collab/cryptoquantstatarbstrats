# DURABLE HANDOFF | TIMESTAMP: 2026-11-03T04:50:00Z | REPO: cryptoquantstatarbstrats
# PRIORITY: COINTEGRATION PAIRS EDGE - FAIL-CLOSED, REAL-DATA ONLY

## REPO SIGNAL (INFERRED)
`cryptoquantstatarbstrats` = Crypto Quant Stat Arb Strategies. **Cointegration pairs is the product edge.**
Everything else exists to support/gate/validate pairs. Treat it as publication-grade research code where fabrication is unacceptable.

## GROUND TRUTH (VERIFIED 2026-11-03T04:50:00Z)
- Critical subset: **125 passed** (`tests/test_cointegration_campaign*_mt.py`, `test_cointegration_recertification_audit_mt.py`, `test_permanent_production_certification_mt.py`, `test_cointegration_diagnostics_schema.py`)
- Full suite: **767 passed, 1 skipped** (`python -m pytest tests/`)
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
- **Gate-key reconciliation (RESOLVED 2026-11-03T04:50Z):** `strategies/pairs_trading.py` gate loop now skips the strict-None check for the derived `all_pass` key (only explicit `False` blocks; missing `all_pass` is not a failure when the six individual gates pass). Both cached (`enriched_diagnostics`) and per-bar (`target_schema_diagnostics`) paths unified. `utils/cointegration.py` already emits the full target-schema key set (`eg_pass`, `johansen_pass`, `spread_mr_pass`, `hl_bounds_pass`, `leg_stationarity_ok`, `rolling_stable_ok`, `no_structural_break`, `all_pass`). No drift.

## NEXT FOCUS CAMPAIGN (HEAVY WORK - CANNOT BE AVOIDED)
**Campaign: "FORTIFY & STRESS-TEST COINTEGRATION GATES"**

### P0 - Gate Integrity (CRITICAL - DO THIS FIRST)
1. ~~**Fix fail-open per-bar fallback** in `strategies/pairs_trading.py`~~ — **DONE.** `rolling_stable_ok` is never coerced to True; unassessable gates are False under strict.
2. ~~**Unify gate key schema** in `utils/cointegration.py`~~ — **DONE.** Target-schema keys emitted consistently.
3. ~~**Trace strict fail-closed path end-to-end**~~ — **DONE.** All seven gate keys traced; missing/None/False → blocked under strict.
4. ~~**Harden gate computation** in `utils/cointegration.py`~~ — **DONE.** Trailing-only, half-life bounds enforced, all gate booleans traced.
5. ~~**Verify engine causality** in `backtest/engine.py`~~ — **DONE.** Gates before weights, opposing legs preserved, hedge ratio guarded.
6. ~~**Regression check**~~ — **DONE.** Critical subset + full suite green after every change.

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
- [ ] `python -m pytest tests/` exits 0 (767 passed, 1 skipped)
- [ ] `ruff check strategies/ backtest/ utils/ tests/ examples/` exits 0
- [ ] `mypy backtest strategies utils` exits 0
- [ ] No gate/provenance weakening (fail-open gaps above closed)
- [ ] Any changes verified with traceable evidence

**START NOW. Run the initial task (already verified passing). Then pick P1 item 1 - audit `reports/portfolio_real.json` and `reports/cointegration_diagnostics_real.json` for `real_data_only: true`, `fabricated_data: false`, full provenance, and `blocked_routes[]`. Do heavy work.**

(End of file - total 66 lines)