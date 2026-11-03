# DURABLE HANDOFF | TIMESTAMP: 2026-11-03T02:41:50Z | REPO: cryptoquantstatarbstrats

## PRIMARY OBJECTIVE (NON-NEGOTIABLE)
**KEEP THE COINTEGRATION PAIRS STRATEGY PRODUCTION-READY AND REGRESSION-FREE.**

This repo is `cryptoquantstatarbstrats` - the cointegration/stat-arb edge IS the product. Everything else exists to support, gate, or validate it. The pairs path is fail-closed (`use_enriched_gates=True`, `strict_enriched_gates=True`) and real-data-only: no fabricated diagnostics, no synthetic evidence of real-market performance.

## CURRENT STATE SNAPSHOT (GROUND TRUTH, VERIFIED 2026-11-03)
- Full test suite: **765 passed, 1 skipped** - all green (`python -m pytest tests/`), exits 0 (cost-sensitivity test now ~2.5s after perf fix 69b1f17; no active bottlenecks remain)
- Cointegration campaign tests 29-38: **all pass** (102 passed)
- Recertification audit, production certification, all gating/signoff/live-deployment bridge tests: **all pass** (38 passed)
- Cointegration diagnostics schema (real_data_only, 17 pairs, full provenance, blocked_routes): **all pass**
- Previous bottleneck (failing campaign/gating tests) is **REMOVED** - sessions were previously checkpointing on red tests; the suite is now green
- **Lint debt CLEARED** - 0 ruff E501 errors remain (`python -m ruff check strategies/ backtest/ utils/ tests/ examples/` exits 0). All 5 were in test files and were reflowed, not weakened.
- mypy is not installed in this environment (skip until available)
- Warnings only (non-failing): statsmodels `adfuller`/`kpss` result_object FutureWarning, pandas freq `'d'` deprecation, statsmodels ComplexWarning/CollinearityWarning/InterpolationWarning

## BOTTLENECKS REMOVED (DO NOT REINTRODUCE)
1. **Failing campaign/gating tests** - were the gate to production clearance; now all pass. Do not let them rot.
2. **Checkpointing without closure** - recent git history is all "checkpoint agent session" commits. Stop checkpointing on red; fix failures until green, then commit.
3. **Test sprawl** - many overlapping `_mt` gating/signoff tests. They all pass; treat them as regression guards, not optional.
4. **Lint debt** - 5 ruff E501 errors cleared; `ruff check` now exits 0. Do not re-introduce long lines.
5. **Cost-sensitivity test slowness** - reduced from ~104s to ~2s in commit 69b1f17. Do not reintroduce per-bar gate recomputation.

## ACTIVE BOTTLENECKS (INVESTIGATE NEXT - unblock full-suite velocity)
- **None remaining.** Full suite now runs in ~3-5 min cleanly. Next: harden against regressions and keep gates green.

## NEXT FOCUS CAMPAIGN: "REGRESSION-PROOF & HEAVY-WORK DISCIPLINE"
**Goal:** Keep every cointegration/pairs test green, keep `ruff check` at 0 errors, and institutionalize the heavy-work discipline so the suite never silently turns red. Phases 1-2 COMPLETE.

### Phase 1: Clear lint debt (COMPLETE)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python -m ruff check strategies/ backtest/ utils/ tests/ examples/
# 0 errors. Reflow lines only; do not weaken assertions or gates.
```

### Phase 2: Remove test bottleneck (COMPLETE - commit 69b1f17)
- Cost-sensitivity test reduced from ~104s to ~2s. Full suite now runs in ~3-5 min.

### Phase 3: Regression-proof the suite (next immediate work)
1. Run `python -m pytest tests/` - must exit 0 (765 passed, 1 skipped). Allow ~3-5 min.
2. Run `python -m pytest tests/test_cointegration_campaign*_mt.py tests/test_cointegration_recertification_audit_mt.py tests/test_permanent_production_certification_mt.py tests/test_cointegration_diagnostics_schema.py -v` - must exit 0 (these are the critical gating path; 125 passed).
3. Confirm `reports/portfolio_real.json` and `reports/cointegration_diagnostics_real.json` still show real_data_only provenance with no fabricated data
4. If mypy becomes available: `python -m mypy backtest/ strategies/ utils/` must exit 0

### Phase 4: Heavy-work mandate (continuous)
- **Do heavy lifting.** Read actual source (`strategies/pairs_trading.py`, `utils/cointegration.py`, `backtest/engine.py`), trace code paths, understand schemas. Don't guess.
- **Don't stop at exploration.** Every turn must make progress: fix a lint error, add a regression guard, or verify a gate.
- **Remove bottlenecks systematically.** If you see a repeated pattern (e.g., long lines across test files), fix it across all affected files at once.
- **Be persistent.** Gates are fail-closed and publication-grade. Don't weaken gates to make tests pass unless the test contradicts documented README behavior AND you have evidence it's a test bug.
- **Verify with real data where specified.** Strict `real_data_only` and provenance rules. No fabrication.

## SUCCESS CRITERIA
- [ ] `python -m pytest tests/` exits 0 (no new failures, no new skips beyond the existing 1)
- [ ] `python -m ruff check strategies/ backtest/ utils/ tests/ examples/` exits 0 (0 E501 errors; lint debt cleared)
- [ ] All `test_cointegration_campaign*_mt.py`, recertification, and production certification tests pass
- [ ] No weakening of fail-closed gates or `real_data_only` provenance
- [ ] No checkpointing-without-closure commits; every commit closes a failure or clears debt

## FILES MOST LIKELY TO NEED ATTENTION
- `strategies/pairs_trading.py` (pairs strategy entry)
- `utils/cointegration.py` (Engle-Granger/Johansen, spread MR, half-life, gates)
- `backtest/engine.py` (backtest engine applying gates causally)
- `reports/portfolio_real.json`, `reports/cointegration_diagnostics_real.json` (real-data provenance artifacts)

**START NOW.** Run `python -m pytest tests/test_cointegration_campaign*_mt.py tests/test_cointegration_recertification_audit_mt.py tests/test_permanent_production_certification_mt.py tests/test_cointegration_diagnostics_schema.py -v` (must exit 0), then run the full suite `python -m pytest tests/` (must exit 0; allow ~3-5 min). Do not write a summary and stop - fix it.
