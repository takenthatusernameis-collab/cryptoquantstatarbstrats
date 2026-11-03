# DURABLE HANDOFF | TIMESTAMP: 2026-11-03T20:18:00Z | REPO: cryptoquantstatarbstrats
# PRIORITY: COINTEGRATION PAIRS EDGE - FAIL-CLOSED, REAL-DATA ONLY - HEAVY EXECUTION MANDATED

## REPO SIGNAL (INFERRED)
`cryptoquantstatarbstrats` = Crypto Quant Stat Arb Strategies.
**Cointegration pairs (`CointegrationPairsStrategy` in `strategies/pairs_trading.py`) is the sole product edge.**
Everything else (momentum/mean-reversion/term-structure/cross-exchange/vol-surface) exists only to support, gate, validate, or instrument the pairs/cointegration path. Treat any change outside pairs as suspect unless it directly hardens the pairs gate/provenance/execution parity.

## CURRENT STATE (VERIFIED 2026-11-03T20:18:00Z)
- Critical subset (cointegration campaigns/recertification/permanent cert/schema): **127 passed** (green)
- Cointegration-related tests (`-k cointegration`): passing
- Cache provenance replay tests: **6 passed** (green)
- Strategy enriched-gate tests (spot-checked): **21 passed** (green)
- Lint (`ruff check strategies/ backtest/ utils/ tests/ examples/`): clean
- mypy (`python -m mypy backtest strategies utils`): clean
- Working tree **clean** on `main`
- Real-data only enforced. Fail-closed gates unified. No observed fail-open coercions.
- Key hardenings present: cached vs per-bar parity (structural breaks read from `structural_breaks.flagged`, blocks in both modes; missing/None gates block in strict), leg-stationarity is genuine (ADF p<=0.05, fail-closed), target-schema diagnostics compute `no_structural_break` gate and build full `blocked_routes[]` with provenance, `blocked_schema_diagnostics` complete, cache preserves `blocked_routes` on memory/disk hits, parallel loader aggregates blocked routes from all symbol fetches.

## BOTTLENECKS TO ELIMINATE NOW (ACTIVE)
1. **Cached vs uncached execution parity** - Any divergence in gate outcomes/provenance between cached replay and live/per-bar paths is unacceptable under `strict_enriched_gates=True`. Structural breaks must block in BOTH modes; individual gate None/missing blocks in strict.
2. **Gate integrity** - Every enrichment gate must be evaluated causally from trailing data only. Missing/None/false must block in strict mode. No clamping, no fabrication, no coercion to True. `no_structural_break` must be present in target-schema gates.
3. **Pair discovery discipline** - Only pairs that pass Engle-Granger/Johansen, spread mean-reversion, half-life bounds (1 < hl < 500), leg stationarity, rolling stability, and structural-break discipline with real data may be admitted. Inconclusive tests = reject.
4. **Provenance completeness** - `real_data_only`, `fabricated_data:false`, full provenance keys, `blocked_routes[]` on any blocked path. Cache must never mask failures. Artifacts must include rationale/computed_at.
5. **Cost-stress fail-closed** - Cost grids cannot be bypassed in strict mode; cost assumptions must be recorded in provenance.
6. **Diagnostics schema** - Blocked cases must use `blocked_schema_diagnostics` with complete, non-empty rationale/blocked_routes. Never fabricate/clamp diagnostics.
7. **Regression prevention** - Codify parity checks so future changes cannot reintroduce divergence.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (ATOMIC, MANDATORY, START HERE)
**TIMESTAMP:** 2026-11-03T20:18:00Z
**OBJECTIVE:** Make the **cointegration pairs discovery + enrichment gate path unbreakably fail-closed and execution-parity safe** under real-data constraints. Ship **>=1 material, verifiable hardening change** (code + tests/evidence). No audit-only termination. **Heavy execution required.**

### EXECUTE IN ORDER (NO EXPLORATION DETOUR)
1. **Verify baseline (fail fast):**
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
/home/runner/work/_temp/kilo-home/.local/bin/pytest tests/test_cointegration_campaign*_mt.py tests/test_cointegration_recertification_audit_mt.py tests/test_permanent_production_certification_mt.py tests/test_cointegration_diagnostics_schema.py -q
```
Must be **127/127**. Fix any failure before continuing.

2. **Hunt and kill fail-open coercions (P0):**
```bash
grep -rn "\bor True\b\|if .* is None: .* True\|True if .* is None" strategies/ utils/ backtest/ | grep -v __pycache__
```
**Zero tolerance.** If any match found, fix causally (do not weaken gates/provenance) with a regression test.

3. **Enforce cached vs uncached parity + gate integrity (P0):**
   - Trace `CointegrationPairsStrategy` enriched gate path (cached replay vs per-bar). Identify any branch that can diverge under `strict_enriched_gates=True`.
   - Ensure structural breaks come from `structural_breaks.flagged` (or equivalent) and block in BOTH cached and per-bar paths.
   - Ensure individual gates that are missing/None block in strict mode (and do not get clamped). `all_pass` is not a substitute for explicit gates.
   - If divergence exists, fix it. Add/strengthen a test forcing borderline pairs through cached+uncached paths asserting identical gate outcomes and identical provenance.

4. **Harden pair discovery + diagnostics (P0):**
   - Ensure pair admission is real-data only, fail-closed on inconclusive diagnostics/tests.
   - Enforce use of `blocked_schema_diagnostics` for blocked cases with full provenance (`real_data_only`, `fabricated_data:false`, `blocked_routes[]`, `computed_at`, rationale).
   - Ensure `target_schema_diagnostics` always emits `gates.no_structural_break` and accurate `blocked_routes` on blocked pairs.
   - Ensure cost assumptions recorded when cost grids applied; in strict mode, missing cost assumptions must block.

5. **Verify & ship with evidence:**
   - Re-run critical subset: must stay **127/127**
   - `/home/runner/work/_temp/kilo-home/.local/bin/pytest tests/test_cache_provenance_replay.py -v` (must pass)
   - `/home/runner/work/_temp/kilo-home/.local/bin/pytest tests/ -k cointegration -q` (must pass)
   - `/home/runner/work/_temp/kilo-home/.local/bin/pytest tests/test_strategies.py -v` (focus on enriched-gate/parity tests)
   - If scope touched core/gates/data/cache/loader/strategies/backtest: run broader suite as time permits; target **771 passed, 1 skipped**
   - `ruff check strategies/ backtest/ utils/ tests/ examples/` must pass
   - `python -m mypy backtest strategies utils` must pass
   - **Do not end until all pass and a material hardening is shipped with traceable evidence (files changed + tests added/updated).**

## MANDATORY FOCUS CAMPAIGN (UNSKIPPABLE - HEAVY WORK REQUIRED)
Every agentic session MUST ship >=1 material, verifiable hardening change on the cointegration pairs edge. No summary-only termination. No deferral. No audit-only work.

### P0 - EXECUTION PARITY, GATE INTEGRITY (IMMEDIATE)
- [ ] Eliminate any cached/uncached parity gaps under `strict_enriched_gates=True` (structural breaks, None/missing gates)
- [ ] Zero fail-open coercions (`or True`, `is None -> True`, equivalent)
- [ ] Diagnostics never fabricate/clamp; blocked use `blocked_schema_diagnostics` with full provenance
- [ ] Pair admission real-data only; inconclusive = reject
- [ ] Leg stationarity and rolling stability fail-closed when unassessable

### P1 - REAL-DATA PROVENANCE & LOADING (HARDEN)
- [ ] Loader/cache: prefer real endpoints, handle blocks honestly; cache never masks failures/fabricates
- [ ] Parallel symbol fetches aggregate `blocked_routes[]` from all symbol loader provenances
- [ ] Artifacts enforce `real_data_only:true`, `fabricated_data:false`, complete provenance
- [ ] Funding/basis attempts logged with full provenance or explicitly blocked (never fabricated)

### P2 - COST-STRESS, ROBUSTNESS & DRIFT PREVENTION (HARDEN)
- [ ] Cost grids validated and fail-closed in strict mode; provenance preserved
- [ ] Bootstrap/robustness paths preserve provenance; no fabrication
- [ ] Parity regression test(s) for borderline pairs (cached+uncached) asserting gate+provenance equality
- [ ] Codify parity checks to prevent future regression (shared helper/assertion)

## DISCIPLINE (NON-NEGOTIABLE)
- **HEAVY WORK REQUIRED.** Execution > narration. Ship code+tests+evidence.
- **TRACE BEFORE CHANGE.** Read source + tests to understand causality. Do not guess.
- **FAIL-CLOSED.** Never weaken `use_enriched_gates`, `strict_enriched_gates`, provenance, or real-data requirements.
- **PUBLICATION-GRADE.** Real-data only. Evidence required (tests + lint + mypy + affected artifacts).
- **NO COERCION.** `or True`, `is None -> True`, or any equivalent fail-open pattern is forbidden.
- **SINGLE HANDOFF.** This file is the only durable handoff. No competing priority files.

## SUCCESS CRITERIA (MUST SATISFY)
- [ ] Critical subset: **127/127**
- [ ] Cache provenance: **all pass**
- [ ] Cointegration-related: **all pass**
- [ ] Full suite (if touched core/gates/data/cache/loader/strategies/backtest): **771 passed, 1 skipped**
- [ ] `ruff` clean
- [ ] `mypy` clean on touched modules
- [ ] Material hardening shipped with traceable evidence
- [ ] No gate/provenance/execution weakening detected
- [ ] Cached vs uncached parity verified for affected paths

(End of file - total 149 lines)
