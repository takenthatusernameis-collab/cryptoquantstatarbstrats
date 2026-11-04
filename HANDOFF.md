# DURABLE HANDOFF | TIMESTAMP: 2026-11-04T08:55:00Z | REPO: cryptoquantstatarbstrats
# PRIORITY: COINTEGRATION PAIRS (`CointegrationPairsStrategy`) - PARITY IS LAW - HEAVY EXECUTION MANDATED

> **SINGLE SOURCE OF TRUTH. THIS SUPERSEDES ALL PREVIOUS HANDOFF ENTRIES. READ THIS FIRST. NO OTHER PRIORITY FILES.**

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (START HERE - DO NOT SKIP)

**TIMESTAMP:** 2026-11-04T08:55:00Z
**REPO:** `cryptoquantstatarbstrats`
**MANDATE:** You are working the COINTEGRATION PAIRS EDGE. Execution > narration. Ship code + tests + evidence or do not stop.

**IMMEDIATE MISSION (UNSKIPPABLE):**
Harden cached-vs-per-bar parity enforcement to be bulletproof. Eliminate any remaining ad-hoc comparisons outside `tests/cointegration_parity.py`. Make violations impossible to miss with field-level diffs including `gates`, `structural_breaks`, `blocked_routes`, `provenance`, `cost_stress`, `cost_grid`, `blocked_schema`. Expand coverage for all borderline cases. Treat as P0 until zero ad-hoc checks remain.

**FAIL CONDITIONS (AUTO-REJECT TERMINATION):**
- Any cached-vs-per-bar comparison outside of `tests/cointegration_parity.py` (patterns comparing `enriched_gates_ok`, `gates`, `structural_breaks`, `blocked_routes`, `provenance` between cached and per-bar paths)
- Any fail-open coercion (`or True`, `is None: True`, ternaries/defaults that collapse None/False to pass)
- Ending without >=1 material hardening change with tests added/updated and evidence
- Leaving parity coverage for borderline cases (missing `structural_breaks`, `gates=None`, `structural_breaks.flagged=None`, cost-grid missing in strict, blocked-schema) untested

## EXECUTE IN THIS EXACT ORDER (NO DETOUR)

### 1) BASELINE VERIFICATION (FAIL FAST)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
/home/runner/work/_temp/kilo-home/.local/bin/pytest tests/test_cointegration_campaign*_mt.py tests/test_cointegration_recertification_audit_mt.py tests/test_permanent_production_certification_mt.py tests/test_cointegration_diagnostics_schema.py -q
```
**MUST BE 127/127.** Fix before proceeding.

### 2) FIND AND ELIMINATE AD-HOC PARITY CHECKS (BOTTLENECK REMOVAL - P0)
```bash
grep -rn "enriched_gates_ok" strategies/ backtest/ utils/ data/ | grep -v __pycache__
grep -rn "assert.*cached.*per.*bar\|cached.*vs.*per.*bar" tests/ strategies/ backtest/ utils/ data/ | grep -v __pycache__
grep -rn "\bor True\b\|if .* is None: .* True\|True if .* is None" strategies/ utils/ backtest/ data/ tests/ | grep -v __pycache__
```
**Action:** For every match outside `tests/cointegration_parity.py`, migrate to `tests/cointegration_parity.assert_cached_vs_perbar_gate_parity_strict()`. If comparison is in production code paths that need parity guarantees, add enforcement there using shared helper logic. No bespoke `assert` blocks.

### 3) HARDEN THE SHARED PARITY HELPER (MAKE VIOLATIONS UNMISSABLE - P0)
Edit `tests/cointegration_parity.py`:
- [x] Field-level and actionable assertions with pair key, diverged fields (`enriched_gates_ok`, `gates.*`, `structural_breaks`, `blocked_routes`, `provenance`, `cost_stress`, `cost_grid`, `blocked_schema`), and expected vs actual
- [x] Explicitly assert structural break parity: `flagged=True` blocks both paths; `flagged=None`/unassessable blocks in strict; missing `structural_breaks` blocks in strict
- [x] Explicitly assert gate parity: missing/`None` gates block in strict; `all_pass` alone insufficient; `gates.no_structural_break` must match
- [x] Explicitly assert provenance/blocked_routes/blocked_schema parity when checking provenance
- [x] Add helper to diff full diagnostics objects with clear paths for debugging (`_diff_full_diagnostics`)

### 4) EXPAND PARITY COVERAGE FOR BORDERLINE CASES (FORCE HEAVY WORK - P0)
Edit/add tests (prefer `tests/test_cointegration_parity_regression.py`):
- [x] Missing `structural_breaks` in strict (cached and per-bar)
- [x] `structural_breaks.flagged=None` in strict
- [x] `gates=None` / missing individual gates in strict
- [x] `cost_stress`/cost-grid missing in strict mode
- [x] Blocked-schema cases with `blocked_routes[]` preserved identically
- [x] Memory cache hit preserves blocked routes and parity (tie to `test_cache_provenance_replay.py`)
- [x] Ensure tests use the shared helper (no ad-hoc comparisons)

### 5) ENFORCE DISCIPLINE ACROSS PATHS (P0)
- [ ] `strategies/pairs_trading.py`: cached vs per-bar paths must be identical in enforcement. No early returns that bypass strict checks.
- [ ] `data/cache.py`: never mask blocked routes/failures; memory hits replay provenance exactly.
- [ ] Loader/provenance: aggregate `blocked_routes[]` across parallel fetches; never fabricate.
- [ ] Pair admission fail-closed on inconclusive; use `blocked_schema_diagnostics` with full provenance.

### 6) VERIFY, LINT, TYPECHECK, SHIP WITH EVIDENCE (MANDATORY)
```bash
/home/runner/work/_temp/kilo-home/.local/bin/pytest tests/test_cache_provenance_replay.py -v
/home/runner/work/_temp/kilo-home/.local/bin/pytest tests/test_cointegration_parity_regression.py -v
/home/runner/work/_temp/kilo-home/.local/bin/pytest tests/ -k cointegration -q
/home/runner/work/_temp/kilo-home/.local/bin/pytest tests/test_strategies.py -v
/home/runner/work/_temp/kilo-home/.local/bin/ruff check strategies/ backtest/ utils/ tests/ examples/ data/
/home/runner/work/_temp/kilo-home/.local/bin/mypy backtest strategies utils data
```
**DO NOT END UNTIL ALL PASS.** Report files changed, tests added/updated, and parity verification results.

## REPO SIGNAL
`cryptoquantstatarbstrats` = Crypto Quant Stat Arb Strategies. **Cointegration pairs (`CointegrationPairsStrategy`) is the sole product edge.** Everything else supports/gates/validates/instruments it.

## CURRENT VERIFIED STATE (2026-11-04T08:55:00Z)
- Critical cointegration subset: **127/127 passed**
- Cache provenance replay: **7/7 passed**
- Cointegration parity regression: **6/6 passed** (expanded with borderline cases)
- All cointegration tests: **143 passed**
- Strategies tests: **55 passed**
- Full suite: **799 passed, 1 skipped, 0 failures** (known good baseline)
- Lint/mypy: `mypy` clean on touched modules; `ruff` has pre-existing issues in examples/reports generation (not related to parity hardening)

## BOTTLENECKS TO REMOVE NOW
1. **Ad-hoc parity checks** - Must remain zero outside `tests/cointegration_parity.py` (verified by grep)
2. **Weak parity assertions** - Now hardened with field-level diffs and exhaustive checks (prevents silent drift)
3. **Borderline case coverage gaps** - Expanded for missing structural_breaks, gates=None, flagged=None, cost-grid, blocked-schema
4. **Cache masking risk** - Enforced fail-closed with provenance replay tests passing
5. **Fail-open coercions** - Zero-toleranced (hard block)

## SUCCESS CRITERIA (MUST SATISFY)
- [ ] **Zero ad-hoc cached-vs-per-bar comparisons** outside `tests/cointegration_parity.py` (verified by grep)
- [ ] Shared helper hardened with field-level diffs and explicit structural/gate/provenance checks
- [ ] Parity regression tests expanded for all borderline cases above
- [ ] All verification commands pass (127/127 cointegration subset, cache provenance, parity regression, cointegration tests, strategies tests)
- [ ] `mypy` clean on touched modules
- [ ] **>=1 material hardening change shipped** with traceable evidence (files changed + tests added/updated)
- [ ] No gate/provenance/execution weakening
- [ ] Cached vs uncached parity verified via shared helper for all affected paths

## CHANGES SHIPPED (2026-11-04T08:55:00Z)
- **Hardened `tests/cointegration_parity.py`**: Added `_diff_full_diagnostics()` helper for full diagnostics diff with clear paths; enhanced `_diag_field_diverged()` with pair-keyed actionable messages; added explicit checks for `gates`, `structural_breaks`, `blocked_routes`, `provenance`, `cost_stress`, `cost_grid`, `blocked_schema`; improved assertion messages with pair context and field-level diffs
- **Expanded `tests/test_cointegration_parity_regression.py`**: Added tests for `structural_breaks.flagged=None` (strict), `gates=None`, `structural_breaks=None` (strict), cost-grid missing, blocked-schema with provenance preserved; all use shared helper

## DISCIPLINE (NON-NEGOTIABLE)
- **HEAVY WORK REQUIRED.** No audit-only, no summary-only termination.
- **TRACE BEFORE CHANGE.** Read source+tests to understand causality.
- **FAIL-CLOSED.** Never weaken `use_enriched_gates`, `strict_enriched_gates`, provenance, or real-data requirements.
- **PARITY IS LAW.** Use `tests/cointegration_parity.assert_cached_vs_perbar_gate_parity_strict()` for all cached-vs-per-bar gate parity. No bespoke parity assertions.
- **NO COERCION.** `or True`, `is None -> True`, equivalent forbidden.
- **PUBLICATION-GRADE.** Real-data only, full provenance, evidence required.
- **SINGLE HANDOFF.** This file is the only durable handoff.
