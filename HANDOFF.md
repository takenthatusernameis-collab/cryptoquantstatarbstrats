# DURABLE HANDOFF | TIMESTAMP: 2026-11-03T02:47:51Z | REPO: cryptoquantstatarbstrats

## PRIMARY OBJECTIVE (NON-NEGOTIABLE)
**KEEP THE COINTEGRATION PAIRS STRATEGY PRODUCTION-READY AND REGRESSION-FREE.**

This repo is `cryptoquantstatarbstrats` - the cointegration/stat-arb edge IS the product. Everything else exists to support, gate, or validate it. The pairs path is fail-closed (`use_enriched_gates=True`, `strict_enriched_gates=True`) and real-data-only: no fabricated diagnostics, no synthetic evidence of real-market performance.

## CURRENT STATE SNAPSHOT (GROUND TRUTH, VERIFIED 2026-11-03T02:47:51Z)
- Full test suite: **765 passed, 1 skipped** - all green (`python -m pytest tests/`), exits 0 (246.89s, ~4 min; cost-sensitivity test ~2.5s after perf fix 69b1f17; no active bottlenecks remain)
- Cointegration campaign tests 29-38: **all pass** (102 passed)
- Recertification audit, production certification, all gating/signoff/live-deployment bridge tests: **all pass** (125 passed in critical gating path)
- Cointegration diagnostics schema (real_data_only, 17 pairs, full provenance, blocked_routes): **all pass**
- **Lint debt CLEARED** - `python -m ruff check strategies/ backtest/ utils/ tests/ examples/` exits 0 ("All checks passed!"), 0 E501 errors
- **Reports provenance verified**: `reports/portfolio_real.json` and `reports/cointegration_diagnostics_real.json` both have `real_data_only: True`, `fabricated_data` key present, no fabricated data
- **mypy NOT installed** in this environment (skip until available)
- Warnings only (non-failing): statsmodels `adfuller`/`kpss` result_object FutureWarning, pandas freq `'d'` deprecation, statsmodels ComplexWarning/CollinearityWarning/InterpolationWarning
- **Working tree clean** - no uncommitted changes

## BOTTLENECKS REMOVED (DO NOT REINTRODUCE)
1. **Failing campaign/gating tests** - were the gate to production clearance; now all pass. Do not let them rot.
2. **Checkpointing without closure** - recent git history is all "checkpoint agent session" commits. Stop checkpointing on red; fix failures until green, then commit.
3. **Test sprawl** - many overlapping `_mt` gating/signoff tests. They all pass; treat them as regression guards, not optional.
4. **Lint debt** - 5 ruff E501 errors cleared; `ruff check` now exits 0. Do not re-introduce long lines.
5. **Cost-sensitivity test slowness** - reduced from ~104s to ~2s in commit 69b1f17. Do not reintroduce per-bar gate recomputation.

## ACTIVE BOTTLENECKS (INVESTIGATE NEXT - unblock full-suite velocity)
- **None remaining.** Full suite now runs in ~4 min cleanly. Next: harden against regressions and keep gates green.

## NEXT FOCUS CAMPAIGN: "REGRESSION-PROOF & HEAVY-WORK DISCIPLINE"
**Goal:** Keep every cointegration/pairs test green, keep `ruff check` at 0 errors, and institutionalize the heavy-work discipline so the suite never silently turns red. Phases 1-3 COMPLETE.

### Phase 1: Clear lint debt (COMPLETE)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python -m ruff check strategies/ backtest/ utils/ tests/ examples/
# 0 errors. Reflow lines only; do not weaken assertions or gates.
```

### Phase 2: Remove test bottleneck (COMPLETE - commit 69b1f17)
- Cost-sensitivity test reduced from ~104s to ~2s. Full suite now runs in ~4 min.

### Phase 3: Regression-proof the suite (COMPLETE - verified 2026-11-03T02:47:51Z)
1. `python -m pytest tests/` - exits 0 (765 passed, 1 skipped). Allow ~4 min.
2. `python -m pytest tests/test_cointegration_campaign*_mt.py tests/test_cointegration_recertification_audit_mt.py tests/test_permanent_production_certification_mt.py tests/test_cointegration_diagnostics_schema.py -v` - exits 0 (125 passed).
3. Confirmed `reports/portfolio_real.json` and `reports/cointegration_diagnostics_real.json` show `real_data_only: True` with no fabricated data.
4. mypy not installed - skip until available.

### Phase 4: Heavy-work mandate (continuous)
- **Do heavy lifting.** Read actual source (`strategies/pairs_trading.py`, `utils/cointegration.py`, `backtest/engine.py`), trace code paths, understand schemas. Don't guess.
- **Don't stop at exploration.** Every turn must make progress: fix a lint error, add a regression guard, or verify a gate.
- **Remove bottlenecks systematically.** If you see a repeated pattern (e.g., long lines across test files), fix it across all affected files at once.
- **Be persistent.** Gates are fail-closed and publication-grade. Don't weaken gates to make tests pass unless the test contradicts documented README behavior AND you have evidence it's a test bug.
- **Verify with real data where specified.** Strict `real_data_only` and provenance rules. No fabrication.

## SUCCESS CRITERIA
- [x] `python -m pytest tests/` exits 0 (no new failures, no new skips beyond the existing 1)
- [x] `python -m ruff check strategies/ backtest/ utils/ tests/ examples/` exits 0 (0 E501 errors; lint debt cleared)
- [x] All `test_cointegration_campaign*_mt.py`, recertification, and production certification tests pass
- [x] No weakening of fail-closed gates or `real_data_only` provenance
- [x] No checkpointing-without-closure commits; every commit closes a failure or clears debt

## FILES MOST LIKELY TO NEED ATTENTION
- `strategies/pairs_trading.py` (pairs strategy entry)
- `utils/cointegration.py` (Engle-Granger/Johansen, spread MR, half-life, gates)
- `backtest/engine.py` (backtest engine applying gates causally)
- `reports/portfolio_real.json`, `reports/cointegration_diagnostics_real.json` (real-data provenance artifacts)

**START NOW.** Run `python -m pytest tests/test_cointegration_campaign*_mt.py tests/test_cointegration_recertification_audit_mt.py tests/test_permanent_production_certification_mt.py tests/test_cointegration_diagnostics_schema.py -v` (must exit 0), then run the full suite `python -m pytest tests/` (must exit 0; allow ~4 min). Do not write a summary and stop - fix it.