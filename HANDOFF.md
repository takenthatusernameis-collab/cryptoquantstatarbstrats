# DURABLE HANDOFF | TIMESTAMP: 2026-11-04T07:48:39Z | REPO: cryptoquantstatarbstrats
# PRIORITY: COINTEGRATION PAIRS EDGE - FAIL-CLOSED, REAL-DATA ONLY - HEAVY EXECUTION MANDATED

> **SINGLE SOURCE OF TRUTH. THIS SUPERSEDES ALL PREVIOUS HANDOFF ENTRIES. READ THIS FIRST. NO OTHER PRIORITY FILES.**

## NEXT AGENT SESSION - START HERE NOW (MANDATORY, TIMESTAMPED)

**TIMESTAMP:** 2026-11-04T07:48:39Z
**REPO:** `cryptoquantstatarbstrats` → **COINTEGRATION PAIRS (`CointegrationPairsStrategy`) IS THE SOLE PRODUCT EDGE**
**MODE:** HEAVY EXECUTION. NO AUDIT-ONLY. NO SUMMARY-ONLY TERMINATION. NO DEFERRAL.

**IMMEDIATE OBJECTIVE (DO NOT DEVIATE):**
Aggressively eliminate any remaining cached vs per-bar parity gaps, enforce fail-closed discipline, and **codify the parity invariant everywhere it matters**. Ship **>= 1 material, verifiable hardening change** (code + tests + evidence). This is mandatory for every future session until explicitly superseded in THIS file.

**EXECUTE IN THIS EXACT ORDER (NO EXPLORATION DETOUR):**

### 1) VERIFY BASELINE (FAIL FAST)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
/home/runner/work/_temp/kilo-home/.local/bin/pytest tests/test_cointegration_campaign*_mt.py tests/test_cointegration_recertification_audit_mt.py tests/test_permanent_production_certification_mt.py tests/test_cointegration_diagnostics_schema.py -q
```
**MUST BE 127/127.** Fix any failure before continuing. Do not proceed with a red baseline.

### 2) ELIMINATE FAIL-OPEN COERCIONS (P0 - ZERO TOLERANCE)
```bash
grep -rn "\bor True\b\|if .* is None: .* True\|True if .* is None" strategies/ utils/ backtest/ data/ tests/ | grep -v __pycache__ | grep -v ".pyc"
```
Any match is a **P0 defect**. Fix causally (tighten conditions, use explicit `if`/`else`, or restructure) without weakening gates, provenance, or real-data requirements. Add a regression test if the pattern was exploitable.

### 3) ENFORCE CACHED VS UNCACHED PARITY + GATE INTEGRITY (P0 - CRITICAL)
Trace and harden:
- `CointegrationPairsStrategy.enriched_diagnostics` (cached path) vs per-bar `target_schema_diagnostics` in `strategies/pairs_trading.py` under `strict_enriched_gates=True`.
- **Structural breaks:** `flagged=True` → block in **BOTH** paths. `flagged=None`/unassessable in strict → block. Missing `structural_breaks` in strict (cached or per-bar) → block.
- **Gates:** Missing/`None` gates in strict → block. `all_pass` alone is **insufficient**. `gates.no_structural_break` must be enforced identically in both paths.
- **Signals:** Identical `enriched_gates_ok`, identical long/short, identical blocked routes, identical provenance.
- **Cache:** `data/cache.py` must **never** mask blocked routes/failures. Memory hits must replay cold-fetch provenance exactly (see `test_memory_cache_hit_preserves_blocked_routes`).

**Action:** For any borderline case with divergence risk, use `tests/cointegration_parity.assert_cached_vs_perbar_gate_parity_strict()` from the shared helper. Do **not** re-implement ad-hoc parity checks.

### 4) CODIFY PARITY EVERYWHERE (P0 - REMOVE BOTTLENECK)
The shared helper exists (`tests/cointegration_parity.py`) and regression tests exist (`tests/test_cointegration_parity_regression.py`). This is **not optional** - extend it to be the enforcement surface:

- [ ] **Audit call sites:** Find all places that compare cached vs per-bar diagnostics/gates/signals and migrate them to the shared helper where feasible.
- [ ] **Harden the helper:** Make violations explicit with actionable messages (include pair keys, which field diverged: `enriched_gates_ok`, `gates`, `structural_breaks`, `blocked_routes`, `provenance`).
- [ ] **Expand coverage:** Add parity tests for borderline cases (missing `structural_breaks`, `gates=None`, `structural_breaks.flagged=None`, cost-grid missing in strict, blocked-schema cases). Prefer data-driven cases that would have slipped manual checks.
- [ ] **Prevent drift:** If duplication remains, consolidate into the helper. Parity must be unmissable on failure.

### 5) HARDEN DISCOVERY, PROVENANCE & COSTS (P0/P1)
- **Real-data only:** Pair admission must be fail-closed on inconclusive. Use `blocked_schema_diagnostics` for blocked cases with full provenance (`real_data_only`, `fabricated_data:false`, `blocked_routes[]`, `computed_at`, rationale).
- **Diagnostics schema:** `target_schema_diagnostics` must emit `gates.no_structural_break` and accurate `blocked_routes` on blocked pairs.
- **Loader/cache:** Parallel symbol fetches must aggregate `blocked_routes[]` from all loader provenances. Cache must never fabricate or mask failures.
- **Funding/basis:** Attempts logged with full provenance or explicitly blocked (never fabricated).
- **Cost-stress:** Cost grids cannot be bypassed in strict mode. Cost assumptions must be recorded in provenance; missing in strict → block.

### 6) VERIFY & SHIP WITH EVIDENCE (MANDATORY - DO NOT END EARLY)
```bash
/home/runner/work/_temp/kilo-home/.local/bin/pytest tests/test_cache_provenance_replay.py -v
/home/runner/work/_temp/kilo-home/.local/bin/pytest tests/test_cointegration_parity_regression.py -v
/home/runner/work/_temp/kilo-home/.local/bin/pytest tests/ -k cointegration -q
/home/runner/work/_temp/kilo-home/.local/bin/pytest tests/test_strategies.py -v
ruff check strategies/ backtest/ utils/ tests/ examples/ data/
python -m mypy backtest strategies utils data
```
**DO NOT END UNTIL:** all of the above pass, **>=1 material hardening change** is shipped (code + tests), parity is verified for affected paths, and evidence is traceable (files changed + tests added/updated).

## REPO SIGNAL (INFERRED)
`cryptoquantstatarbstrats` = Crypto Quant Stat Arb Strategies. **Cointegration pairs (`CointegrationPairsStrategy` in `strategies/pairs_trading.py`) is the sole product edge.** Everything else exists only to support, gate, validate, or instrument the pairs/cointegration path.

## CURRENT STATE (VERIFIED 2026-11-04T07:48:39Z)
- **Gate integrity:** Shared strict evaluator `_evaluate_enriched_gates_strict` enforced across cached and per-bar paths. Structural breaks block in both modes; missing gates/structural_breaks fail closed in strict mode. No coercions observed.
- **Parity tooling:** Shared helper `tests/cointegration_parity.assert_cached_vs_perbar_gate_parity_strict()` codified + regression tests present.
- **Critical subset (cointegration campaigns/recertification/permanent cert/schema):** **127 passed** (green)
- **Cache provenance replay:** **7 passed**
- **Cointegration parity regression:** **present and passing**
- **`tests/test_strategies.py` enriched-gate/parity:** **all passing**
- **Cointegration-related tests:** **all passing**
- **Lint (`ruff`):** **clean** on touched modules (strategies/, backtest/, utils/, data/, examples/, cointegration tests). Pre-existing ruff findings are confined to `tests/test_walk_forward_cost_sensitivity.py` (unused locals/import sort) and one E501 in `examples/` — outside the cointegration edge, not blocking.
- **mypy:** **clean** on touched modules (35 files, no issues)
- **Full suite baseline known:** **799 passed, 1 skipped, 0 failures** (re-verified at 2026-11-04T07:48:39Z; the previously-noted `test_cost_sensitivity_real.py::test_cost_sensitivity_real_provenance_is_honest` pre-existing failure is resolved — that file now passes 2/2)
- **Working tree:** clean
- **No known blocking test failures. Baseline is green.**

## BOTTLENECKS TO ELIMINATE NOW (ACTIVE)
1. **Parity drift risk (HIGH)** - The helper exists but must be **universally used**. Any manual cached/uncached comparison is a regression vector. **Action:** audit and migrate.
2. **Cache leakage (HIGH)** - Ensure memory cache never masks blocked routes/failures. Verify with targeted tests.
3. **Fail-open surfaces (HIGH)** - Zero coercions. Treat `or True`, `if X is None: True`, equivalent as P0.
4. **Discovery discipline (HIGH)** - Inconclusive pairs must be rejected. Provenance must be complete on blocked paths.
5. **Cost-stress bypass (MED-HIGH)** - Enforce in strict mode with recorded assumptions.
6. **Drift prevention (HIGH)** - **Codify parity into the shared helper and use it everywhere** to make future violations unmissable.

## MANDATORY FOCUS CAMPAIGN (UNSKIPPABLE - HEAVY WORK REQUIRED)
Every agentic session MUST ship **>=1 material, verifiable hardening change** on the cointegration pairs edge. No summary-only termination. No deferral. No audit-only work.

### P0 - EXECUTION PARITY, GATE INTEGRITY (IMMEDIATE)
- [ ] Eliminate any cached/uncached parity gaps under `strict_enriched_gates=True` (structural breaks, None/missing gates, `no_structural_break`)
- [ ] Zero fail-open coercions (`or True`, `is None -> True`, equivalent)
- [ ] Diagnostics never fabricate/clamp; blocked use `blocked_schema_diagnostics` with full provenance
- [ ] Pair admission real-data only; inconclusive = reject
- [ ] Leg stationarity and rolling stability fail-closed when unassessable

### P1 - REAL-DATA PROVENANCE, LOADING & CACHE (HARDEN)
- [ ] Loader/cache: prefer real endpoints, handle blocks honestly; cache never masks failures/fabricates
- [ ] Parallel symbol fetches aggregate `blocked_routes[]` from all symbol loader provenances
- [ ] Artifacts enforce `real_data_only:true`, `fabricated_data:false`, complete provenance
- [ ] Funding/basis attempts logged with full provenance or explicitly blocked (never fabricated)
- [ ] Memory cache parity verified for blocked routes

### P2 - COST-STRESS, ROBUSTNESS & DRIFT PREVENTION (HARDEN)
- [ ] Cost grids validated and fail-closed in strict mode; provenance preserved
- [ ] Bootstrap/robustness paths preserve provenance; no fabrication
- [ ] **Migrate ad-hoc parity checks to `tests/cointegration_parity.py` and harden the helper**
- [ ] **Add/strengthen parity regression tests for borderline cases (shared helper only)**
- [ ] **Codify parity checks to prevent future regression (shared helper/assertion) - PRIORITIZE THIS TO REMOVE BOTTLENECK**

## DISCIPLINE (NON-NEGOTIABLE)
- **HEAVY WORK REQUIRED.** Execution > narration. Ship code+tests+evidence.
- **TRACE BEFORE CHANGE.** Read source + tests to understand causality. Do not guess.
- **FAIL-CLOSED.** Never weaken `use_enriched_gates`, `strict_enriched_gates`, provenance, or real-data requirements.
- **PUBLICATION-GRADE.** Real-data only. Evidence required (tests + lint + mypy + affected artifacts).
- **NO COERCION.** `or True`, `is None -> True`, or any equivalent fail-open pattern is forbidden.
- **SHARED PARITY IS LAW.** Use `tests/cointegration_parity.assert_cached_vs_perbar_gate_parity_strict()` for cached vs per-bar gate parity. No bespoke parity assertions.
- **SINGLE HANDOFF.** This file is the only durable handoff. No competing priority files.

## SUCCESS CRITERIA (MUST SATISFY)
- [ ] Critical subset: **127/127**
- [ ] Cache provenance: **all pass**
- [ ] Cointegration parity regression: **all pass**
- [ ] Cointegration-related: **all pass**
- [ ] Full suite (if touched core/gates/data/cache/loader/strategies/backtest): maintain green baseline (**799 passed, 1 skipped, 0 failures**, no new regressions)
- [ ] `ruff` clean on touched modules
- [ ] `mypy` clean on touched modules
- [ ] **Material hardening shipped with traceable evidence** (files changed + tests added/updated)
- [ ] No gate/provenance/execution weakening detected
- [ ] **Cached vs uncached parity verified for all affected paths** using the shared helper
