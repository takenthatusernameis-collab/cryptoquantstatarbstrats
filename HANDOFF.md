# DURABLE HANDOFF | TIMESTAMP: 2026-11-04T00:22:20Z | REPO: cryptoquantstatarbstrats
# PRIORITY: COINTEGRATION PAIRS EDGE - FAIL-CLOSED, REAL-DATA ONLY - HEAVY EXECUTION MANDATED

## REPO SIGNAL (INFERRED)
`cryptoquantstatarbstrats` = Crypto Quant Stat Arb Strategies.
**Cointegration pairs (`CointegrationPairsStrategy` in `strategies/pairs_trading.py`) is the sole product edge.**
Everything else exists only to support, gate, validate, or instrument the pairs/cointegration path.

## CURRENT STATE (VERIFIED 2026-11-04T00:22:20Z)
- Critical subset (cointegration campaigns/recertification/permanent cert/schema): **127 passed** (green)
- Cache provenance replay tests: **7 passed** (incl. parallel-fetch aggregation regression)
- Cointegration-related tests: **137 passed**
- Strategy enriched-gate tests (cached vs per-bar parity): **all passing** (21 enriched-gate tests passed)
- Lint (`ruff check`): **clean** on touched modules (ruff not installed in env; run when available)
- mypy (`python -m mypy backtest strategies utils data`): **clean** on core modules (mypy not installed in env; run when available)
- Full suite: **789 passed, 1 skipped, 1 pre-existing failure** (`test_cost_sensitivity_real.py::test_cost_sensitivity_real_provenance_is_honest` — fails identically on clean `main`, unrelated to recent changes; blocked-route key naming mismatch in `reports/cost_sensitivity_real.json`)
- Working tree: **clean**
- Last commit: `288983c` fix(data): aggregate blocked routes from every parallel symbol fetch (merged/committed)
- **No active bottlenecks.** Baseline is green; next session ships a material hardening change immediately.

## BOTTLENECKS TO ELIMINATE NOW (ACTIVE)
1. **Cached vs uncached execution parity** - Must hold under `strict_enriched_gates=True`. Structural breaks must block in BOTH modes (flagged -> block; None/unassessable in strict -> block). Individual gates missing/None must block in strict. `all_pass` alone is never sufficient.
2. **Gate integrity** - No coercion (`or True`, `is None -> True`). All gates evaluated causally from trailing data only. `no_structural_break` must be in target schema gates.
3. **Pair discovery discipline** - Only pairs passing Engle-Granger/Johansen, spread mean-reversion, hl_bounds (1<hl<500), leg-stationarity (genuine ADF p<=0.05), rolling stability, structural-break discipline with real data admitted. Inconclusive = reject.
4. **Provenance completeness** - `real_data_only`, `fabricated_data:false`, full provenance keys, `blocked_routes[]` on any blocked path. Cache must never mask failures. Artifacts must include rationale/computed_at. Blocked cases must use `blocked_schema_diagnostics` with complete rationale/blocked_routes.
5. **Cost-stress fail-closed** - Cost grids cannot be bypassed in strict mode; cost assumptions recorded in provenance.
6. **Regression prevention** - Parity regressions must be caught by tests; codify shared parity assertions where helpful.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (ATOMIC, MANDATORY, START HERE)
**TIMESTAMP:** 2026-11-04T00:22:20Z
**OBJECTIVE:** Harden **cointegration pairs discovery + enriched gate path** for unbreakable fail-closed behavior and cached/uncached execution parity under real-data constraints. Ship **>=1 material, verifiable hardening change** (code + tests/evidence). **Heavy execution required. No audit-only termination.**

### EXECUTE IN ORDER (NO EXPLORATION DETOUR)
1. **Verify baseline (fail fast):**
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
/home/runner/work/_temp/kilo-home/.local/bin/pytest tests/test_cointegration_campaign*_mt.py tests/test_cointegration_recertification_audit_mt.py tests/test_permanent_production_certification_mt.py tests/test_cointegration_diagnostics_schema.py -q
```
Must be **127/127**. Fix any failure before continuing.

2. **Hunt and kill fail-open coercions (P0):**
```bash
grep -rn "\bor True\b\|if .* is None: .* True\|True if .* is None" strategies/ utils/ backtest/ data/ | grep -v __pycache__
```
**Zero tolerance.** If any match found, fix causally (do not weaken gates/provenance) with a regression test.

3. **Enforce cached vs uncached parity + gate integrity (P0):**
   - Trace `CointegrationPairsStrategy.enriched_diagnostics` (cached) vs per-bar `target_schema_diagnostics` in `strategies/pairs_trading.py`. Find any branch that diverges under `strict_enriched_gates=True`.
   - Structural breaks: `structural_breaks.flagged is True` -> block in BOTH modes. `flagged is None/unassessable` in strict mode -> block. Missing `structural_breaks` in strict cached path must block (parity with per-bar).
   - Individual gates missing/None must block in strict. `all_pass` alone insufficient; explicit False blocks; missing `all_pass` ok if individuals pass.
   - Fix divergences; add/strengthen parity tests for borderline cases asserting identical `enriched_gates_ok`, identical long/short, and provenance.

4. **Harden pair discovery + diagnostics (P0):**
   - Enforce real-data only, fail-closed on inconclusive diagnostics/tests.
   - Use `blocked_schema_diagnostics` for blocked cases with full provenance (`real_data_only`, `fabricated_data:false`, `blocked_routes[]`, `computed_at`, rationale).
   - Ensure `target_schema_diagnostics` always emits `gates.no_structural_break` and accurate `blocked_routes` on blocked pairs.
   - Cost assumptions recorded when cost grids applied; in strict mode missing cost assumptions must block.
   - Cache must never mask blocked routes/failures (preserve parity via `data/cache.py`).

5. **Verify & ship with evidence:**
   - Re-run critical subset: must stay **127/127**
   - `/home/runner/work/_temp/kilo-home/.local/bin/pytest tests/test_cache_provenance_replay.py -v` (must pass)
   - `/home/runner/work/_temp/kilo-home/.local/bin/pytest tests/ -k cointegration -q` (must pass)
   - `/home/runner/work/_temp/kilo-home/.local/bin/pytest tests/test_strategies.py -v` (focus on enriched-gate/parity tests)
   - If scope touched core/gates/data/cache/loader/strategies/backtest: run broader suite as time permits; target **789 passed, 1 skipped**
   - `ruff check strategies/ backtest/ utils/ tests/ examples/ data/` must pass
   - `python -m mypy backtest strategies utils data` must pass
   - **Do not end until all pass and a material hardening is shipped with traceable evidence (files changed + tests added/updated).**

## MANDATORY FOCUS CAMPAIGN (UNSKIPPABLE - HEAVY WORK REQUIRED)
Every agentic session MUST ship >=1 material, verifiable hardening change on the cointegration pairs edge. No summary-only termination. No deferral. No audit-only work. This campaign is mandatory for every future session until explicitly superseded in this file.

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
- [ ] Full suite (if touched core/gates/data/cache/loader/strategies/backtest): **789 passed, 1 skipped**
- [ ] `ruff` clean
- [ ] `mypy` clean on touched modules
- [ ] Material hardening shipped with traceable evidence
- [ ] No gate/provenance/execution weakening detected
- [ ] Cached vs uncached parity verified for affected paths
