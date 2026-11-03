# DURABLE HANDOFF | TIMESTAMP: 2026-11-03T05:03:30Z | REPO: cryptoquantstatarbstrats
# PRIORITY: COINTEGRATION PAIRS EDGE - FAIL-CLOSED, REAL-DATA ONLY

## REPO SIGNAL (INFERRED)
`cryptoquantstatarbstrats` = Crypto Quant Stat Arb Strategies. **Cointegration pairs is the product edge.**
Everything else exists to support/gate/validate pairs. Treat it as publication-grade research code where fabrication is unacceptable.

## GROUND TRUTH (VERIFIED 2026-11-03T05:03:30Z)
- Critical subset: **125 passed** (`tests/test_cointegration_campaign*_mt.py`, `test_cointegration_recertification_audit_mt.py`, `test_permanent_production_certification_mt.py`, `test_cointegration_diagnostics_schema.py`)
- Full suite: **767 passed, 1 skipped** (`python -m pytest tests/`)
- Lint: `python -m ruff check strategies/ backtest/ utils/ tests/ examples/` → **All checks passed**
- mypy: `python -m mypy backtest strategies utils` → **Success: no issues found in 32 source files**
- Working tree clean. Network: `www.binance.com` serves public klines; loader handles `api.binance.com` 451 honestly.
- Reports verified: `reports/portfolio_real.json`, `reports/cointegration_diagnostics_real.json` contain `real_data_only: true`, `fabricated_data: false`, full provenance with `blocked_routes[]` for blocked pairs.

## IMMEDIATE INITIAL TASK (MUST DO FIRST TURN - NO EXPLORATION-ONLY)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python -m pytest tests/test_cointegration_campaign*_mt.py tests/test_cointegration_recertification_audit_mt.py tests/test_permanent_production_certification_mt.py tests/test_cointegration_diagnostics_schema.py -v
```
**If ANY fail → fix before doing anything else.** Only proceed if all pass. Current state: **ALL PASS**.

## BOTTLENECK REMOVAL (APPLY NOW)
- **Single session active** - no cross-session blockers. Do not wait on board; act.
- **No stale CI branch to chase.** main is green.
- **No data/network blocker.** Real-data paths operational (www.binance.com first; 451 handled).
- **Analysis paralysis removed:** act, not just audit. Trace → harden → verify with tests.
- **Gate-key reconciliation (RESOLVED):** `strategies/pairs_trading.py` skips strict-None check for derived `all_pass` (only explicit `False` blocks; missing `all_pass` not failure if six individual gates pass). Both cached (`enriched_diagnostics`) and per-bar paths unified. `utils/cointegration.py` emits full target-schema keys.

## NEXT FOCUS CAMPAIGN (HEAVY WORK - CANNOT BE AVOIDED)
**Campaign: "FORTIFY & STRESS-TEST COINTEGRATION GATES"**

### P0 - Gate Integrity (CRITICAL)
1. **Hunt fail-open coercions**: grep for `or True`, `if .* is None: .* True`, assignments setting gates to True on uncertainty. Fix to fail-closed.
2. **Trace end-to-end strict path**: verify every gate in `strategies/pairs_trading.py` blocks on None/False under `strict_enriched_gates=True`. Pay special attention to cached vs computed paths.
3. **Harden diagnostics**: ensure `utils/cointegration.py` never fabricates, never clamps hl/values to pass gates, and `blocked_or_insufficient_data` is used honestly with `blocked_routes[]`.

### P1 - Real-Data Provenance (CRITICAL)
1. **Audit artifacts**: spot-check `reports/portfolio_real.json` and `reports/cointegration_diagnostics_real.json` - ensure `real_data_only: true`, `fabricated_data: false`, full provenance, `blocked_routes[]` when blocked. Keep them honest.
2. **Harden loader/cache**: `data/loader.py`, `data/cache.py`. Prefer `www.binance.com` first; on 451/blocks write honest `blocked_or_insufficient_data` with rationale - **never fabricate**. Cache must not hide failures.

### P2 - Stress & Regression Guards (HIGH)
1. **Add/strengthen guard tests** if gaps found (without weakening existing tests).
2. **Cost/perf**: keep tests fast; avoid per-bar recomputation where possible.
3. **Quality gates:** `ruff` clean, `mypy` clean on touched modules.

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
- [ ] No gate/provenance weakening
- [ ] Any changes verified with traceable evidence

**START NOW. Run the initial task. Then do P0 item 1: search for fail-open coercions (`grep -rn "or True" strategies/ utils/ | grep -v __pycache__`) and fix any found. Heavy work required.**
