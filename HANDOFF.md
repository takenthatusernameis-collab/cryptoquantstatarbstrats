# DURABLE HANDOFF | TIMESTAMP: 2026-11-03T01:09:24Z | REPO: cryptoquantstatarbstrats

## PRIMARY OBJECTIVE (NON-NEGOTIABLE)
**MAKE THE COINTEGRATION PAIRS STRATEGY PRODUCTION-READY.**

This repo is `cryptoquantstatarbstrats` - the cointegration/stat-arb edge IS the product. Everything else exists to support, gate, or validate it. Future work MUST prioritize the pairs/cointegration path above all else.

## CURRENT STATE SNAPSHOT
- Core strategy: `CointegrationPairsStrategy` with enriched cointegration gates (Engle-Granger/Johansen, spread MR, half-life 1<hl<500, rolling stability, structural breaks, leg stationarity)
- Real-market validation exists (`reports/pairs_real_market.json`, `reports/cost_sensitivity_real*.json`) showing underperformance vs buy-hold but strategy is correctly gated and uses real data only
- Heavy test suite with many campaign/gating tests: `tests/test_cointegration_campaign*_mt.py`, `tests/test_*_gating*.py`, `tests/test_*_signoff_mt.py`, `tests/test_live_*_mt.py`, `tests/test_permanent_production_certification_mt.py`
- Recent git history is all "checkpoint agent session" commits (c8db0fe, e9b5339, ...) suggesting sessions have been checkpointing without completing the hard gating work
- README explicitly calls out publication-grade cointegration diagnostics as the core of this repo

## BOTTLENECKS TO REMOVE
1. **Campaign test backlog** - There are 9+ cointegration campaign tests (campaign30 through campaign38) plus recertification/audit tests. These are likely the gate to production certification.
2. **Gating test sprawl** - Multiple overlapping gates (portfolio, execution, operational risk, OOS cointegration validation, live deployment bridge, etc.). Need to understand which gates are actually blocking vs redundant.
3. **MT (multi-test?) test complexity** - Tests with `_mt` suffix appear to be integration/multi-component tests that may be failing due to missing fixtures, incomplete wiring, or schema mismatches.
4. **Checkpointing without closure** - Sessions are stopping at checkpoints instead of fixing failures. This must stop.

## IMMEDIATE FIRST ACTIONS (DO IN THIS ORDER)
Execute these commands first to get full visibility into what's broken:

```bash
# 1) See all cointegration campaign tests
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python -m pytest tests/test_cointegration_campaign*_mt.py tests/test_cointegration_recertification_audit_mt.py -v 2>&1 | tail -80

# 2) See all gating-related tests
python -m pytest tests/test_*gating*.py tests/test_*signoff_mt.py -v 2>&1 | tail -80

# 3) See production certification
python -m pytest tests/test_permanent_production_certification_mt.py -v 2>&1 | tail -60

# 4) See cointegration diagnostics schema tests
python -m pytest tests/test_cointegration_diagnostics_schema.py tests/test_walk_forward_gate_stability_schema.py -v 2>&1 | tail -40
```

## NEXT FOCUS CAMPAIGN: "COINTEGRATION ENRICHMENT -> PRODUCTION CLEARANCE"

**Goal:** Get from current state to a state where all cointegration-related tests pass. Do NOT skip failing tests. Fix them.

### Phase 1: Understand the enriched gates (Heavy Reading Required)
Read these files to understand the full picture:
- `strategies/pairs_cointegration.py` (and any related files)
- `backtest/` modules related to diagnostics/gating
- `tests/test_cointegration_campaign30_mt.py` through `tests/test_cointegration_campaign38_mt.py` - understand what each campaign requires
- `reports/portfolio_real.json` - has pair diagnostics for 17 pairs
- Any files referenced by failing tests

### Phase 2: Fix failures ruthlessly
For each failing test:
1. Understand the exact assertion and schema expected
2. Trace to implementation - is it missing logic, wrong schema, or incorrect gate behavior?
3. Fix the implementation to match the expected behavior (or fix test only if test is clearly wrong AND matches the intended design from README/spec)
4. Re-run that specific test until it passes
5. Move to next failure

**RULE:** The enriched gates are described as "publication-grade" and "fail-closed" in README. Respect that design. Don't weaken gates to make tests pass unless the test expectation contradicts the documented behavior AND you have evidence it's a test bug.

### Phase 3: Integration & hardening
Once campaign tests pass:
1. Run all cointegration + gating tests together
2. Run the full test suite but focus on anything related to pairs/cointegration first
3. Ensure `python -m pytest tests/test_cointegration_campaign*_mt.py -v` exits 0
4. Ensure no regressions in core pairs functionality

## HEAVY WORK MANDATE
- **Do heavy lifting.** Read actual source files, trace through code paths, understand schemas. Don't guess.
- **Don't stop at exploration.** Every turn should make progress toward fixing failures or implementing missing pieces.
- **Remove bottlenecks.** If you see repeated patterns of missing wiring, fix them systematically across all affected files.
- **Be persistent.** Campaign tests may have many interconnected requirements. Fix them methodically.
- **Verify with real data where specified.** Remember: no fabrication of diagnostics/data. Follow the "real_data_only" and provenance rules strictly.

## SUCCESS CRITERIA
- [ ] All `test_cointegration_campaign*_mt.py` tests pass
- [ ] All `test_cointegration_recertification_audit_mt.py` tests pass
- [ ] All cointegration-related gating/signoff tests pass
- [ ] `test_permanent_production_certification_mt.py` shows progress toward passing (or passes)
- [ ] No new regressions in existing passing pairs tests
- [ ] Changes maintain the fail-closed, real-data-only discipline described in README

## FILES MOST LIKELY TO NEED ATTENTION
Based on repo structure and test names:
- `strategies/pairs_cointegration.py`
- `backtest/` (engine, portfolio, diagnostics, gating)
- `utils/` (stats, cointegration helpers)
- Any schema/validation modules
- Test fixtures if they need updating to match correct schemas

**START NOW. Run the 4 commands in "IMMEDIATE FIRST ACTIONS" and begin fixing the first failing test you see. Do not write a summary of findings and stop - fix it.**
