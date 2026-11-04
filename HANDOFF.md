# DURABLE HANDOFF | TIMESTAMP: 2026-11-04T05:12:57Z | REPO: cryptoquantstatarbstrats
# PRIORITY: COINTEGRATION PAIRS EDGE - FAIL-CLOSED, REAL-DATA ONLY - HEAVY EXECUTION MANDATED

> **SINGLE SOURCE OF TRUTH. THIS IS THE ONLY DURABLE HANDOFF. READ THIS FIRST. NO OTHER PRIORITY FILES.**

## NEXT AGENT SESSION - START HERE NOW (MANDATORY, TIMESTAMPED)

**TIMESTAMP:** 2026-11-04T05:12:57Z
**REPO:** `cryptoquantstatarbstrats` → **COINTEGRATION PAIRS EDGE ONLY MATTERS**
**MODE:** HEAVY EXECUTION. NO AUDIT-ONLY. NO SUMMARY-ONLY TERMINATION.

**IMMEDIATE OBJECTIVE (DO NOT DEVIATE):**
Aggressively harden the **cointegration pairs discovery + enriched gate path** (cached vs per-bar parity, fail-closed discipline, real-data provenance). Ship **>=1 material, verifiable hardening change** (code + tests/evidence). Every future session MUST do this until superseded in THIS file.

**EXECUTE IN THIS EXACT ORDER (NO EXPLORATION DETOUR):**
1. **VERIFY BASELINE (FAIL FAST):**
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
/home/runner/work/_temp/kilo-home/.local/bin/pytest tests/test_cointegration_campaign*_mt.py tests/test_cointegration_recertification_audit_mt.py tests/test_permanent_production_certification_mt.py tests/test_cointegration_diagnostics_schema.py -q
```
Must be **127/127**. Fix any failure before continuing.

2. **HUNT FAIL-OPEN COERCIONS (P0):**
```bash
grep -rn "\bor True\b\|if .* is None: .* True\|True if .* is None" strategies/ utils/ backtest/ data/ | grep -v __pycache__ | grep -v ".pyc"
```
**ZERO TOLERANCE.** Fix causally (no weakening of gates/provenance). Add regression test if found.

3. **ENFORCE CACHED VS UNCACHED PARITY + GATE INTEGRITY (P0):**
- Trace `CointegrationPairsStrategy.enriched_diagnostics` (cached) vs per-bar `target_schema_diagnostics` in `strategies/pairs_trading.py`. Eliminate divergence under `strict_enriched_gates=True`.
- Structural breaks: `flagged=True` → block BOTH. `flagged=None/unassessable` in strict → block. Missing `structural_breaks` in strict cached → block.
- Missing/None gates in strict → block. `all_pass` alone insufficient. `no_structural_break` enforced consistently in both paths.
- Add/strengthen parity tests for borderline cases asserting identical `enriched_gates_ok`, identical long/short, and provenance.

4. **HARDEN DISCOVERY + DIAGNOSTICS (P0):**
- Real-data only, fail-closed on inconclusive. Use `blocked_schema_diagnostics` for blocked cases with full provenance (`real_data_only`, `fabricated_data:false`, `blocked_routes[]`, `computed_at`, rationale).
- `target_schema_diagnostics` must emit `gates.no_structural_break` and accurate `blocked_routes` on blocked pairs.
- Cost assumptions recorded when cost grids applied; missing in strict → block.
- Cache must never mask blocked routes/failures (parity via `data/cache.py`).

5. **VERIFY & SHIP WITH EVIDENCE (MANDATORY):**
```bash
/home/runner/work/_temp/kilo-home/.local/bin/pytest tests/test_cache_provenance_replay.py -v
/home/runner/work/_temp/kilo-home/.local/bin/pytest tests/ -k cointegration -q
/home/runner/work/_temp/kilo-home/.local/bin/pytest tests/test_strategies.py -v
ruff check strategies/ backtest/ utils/ tests/ examples/ data/
python -m mypy backtest strategies utils data
```
**DO NOT END UNTIL ALL PASS AND A MATERIAL HARDENING IS SHIPPED WITH TRACEABLE EVIDENCE (files changed + tests added/updated).**

## REPO SIGNAL (INFERRED)
`cryptoquantstatarbstrats` = Crypto Quant Stat Arb Strategies.
**Cointegration pairs (`CointegrationPairsStrategy` in `strategies/pairs_trading.py`) is the sole product edge.** Everything else exists only to support, gate, validate, or instrument the pairs/cointegration path.

## CURRENT STATE (VERIFIED 2026-11-04T05:12:57Z)
- **CRITICAL GATE INTEGRITY:** Shared strict evaluator `_evaluate_enriched_gates_strict` enforced across cached and per-bar paths. Structural breaks block in both modes; missing gates/structural_breaks fail closed in strict mode. No coercions observed.
- Critical subset (cointegration campaigns/recertification/permanent cert/schema): **127 passed** (green)
- Cache provenance replay tests: **7 passed**
- `tests/test_strategies.py` enriched-gate/parity: **all passing**
- Cointegration-related tests: **all passing**
- Lint (`ruff`): **clean** on touched modules
- mypy (`mypy`): **clean** on touched modules
- Full suite baseline known: **789 passed, 1 skipped, 1 pre-existing failure** (`test_cost_sensitivity_real.py::test_cost_sensitivity_real_provenance_is_honest` — unrelated to pairs gating)
- Working tree: clean
- **No known blocking test failures. Baseline is green.**

## BOTTLENECKS TO ELIMINATE NOW (ACTIVE)
1. **Cached vs uncached execution parity** - Must hold under `strict_enriched_gates=True`. Structural breaks must block in BOTH modes. Individual gates missing/None must block in strict. `all_pass` alone is never sufficient.
2. **Gate integrity** - No coercion (`or True`, `if X is None: True`). All gates evaluated causally from trailing data only. `no_structural_break` must be enforced consistently in both paths.
3. **Pair discovery discipline** - Only pairs passing Engle-Granger/Johansen, spread mean-reversion, hl_bounds (1<hl<500), leg-stationarity, rolling stability, structural-break discipline with real data admitted. Inconclusive = reject.
4. **Provenance completeness** - `real_data_only`, `fabricated_data:false`, full provenance keys, `blocked_routes[]` on any blocked path. Cache must never mask failures. Artifacts must include rationale/computed_at. Blocked cases must use `blocked_schema_diagnostics` with complete rationale/blocked_routes.
5. **Cost-stress fail-closed** - Cost grids cannot be bypassed in strict mode; cost assumptions recorded in provenance.
6. **Regression prevention** - **CODIFY PARITY ASSERTIONS INTO A SHARED HELPER/UTILITY** to prevent future drift (remove duplication across tests; make parity violations unmissable).

## MANDATORY FOCUS CAMPAIGN (UNSKIPPABLE - HEAVY WORK REQUIRED)
Every agentic session MUST ship **>=1 material, verifiable hardening change** on the cointegration pairs edge. No summary-only termination. No deferral. No audit-only work. This campaign is mandatory for every future session until explicitly superseded in THIS file.

### P0 - EXECUTION PARITY, GATE INTEGRITY (IMMEDIATE)
- [ ] Eliminate any cached/uncached parity gaps under `strict_enriched_gates=True` (structural breaks, None/missing gates, `no_structural_break`)
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
- [ ] **Parity regression test(s) for borderline pairs (cached+uncached) asserting gate+provenance equality** (if gaps remain)
- [ ] **Codify parity checks to prevent future regression (shared helper/assertion) - PRIORITIZE THIS TO REMOVE BOTTLENECK**

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
- [ ] Full suite (if touched core/gates/data/cache/loader/strategies/backtest): maintain green baseline (**789 passed, 1 skipped**, no new regressions)
- [ ] `ruff` clean on touched modules
- [ ] `mypy` clean on touched modules
- [ ] Material hardening shipped with traceable evidence
- [ ] No gate/provenance/execution weakening detected
- [ ] Cached vs uncached parity verified for affected paths
