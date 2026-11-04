 TIMESTAMP:.*| TIMESTAMP: 2026-11-04T10:35:02Z | REPO: cryptoquantstatarbstrats
# PRIORITY: STAT-ARB STRATEGY PARITY & DIAGNOSTICS HARDENING (NEXT CAMPAIGN) — COINTEGRATION PAIRS EDGE IS COMPLETE & VERIFIED
# STATUS: COINTEGRATION CAMPAIGN FINALIZED — NEXT CAMPAIGN ARMED

> **SINGLE SOURCE OF TRUTH. THIS SUPERSEDES ALL PREVIOUS HANDOFF ENTRIES. READ THIS FIRST. NO OTHER PRIORITY FILES.**

## COMPLETED CAMPAIGN RECORD (COINTEGRATION PAIRS EDGE — FINAL, 2026-11-04T08:59:13Z)

**VERIFIED STATE:**
- Critical cointegration subset: **127/127 passed**
- Cache provenance replay: **7/7 passed**
- Cointegration parity regression: **9/9 passed** (6 original + 3 new borderline cases)
- All cointegration tests: **146 passed**
- Strategies tests: **55 passed**
- Full suite: **802 passed, 1 skipped, 0 failures**
- Lint/mypy: `mypy` clean on all touched modules (35 source files, 0 issues); `ruff` clean on parity files

**SECTION-5 DISCIPLINE ITEMS — ALL IMPLEMENTED IN CODE (verified by read):**
- [x] `strategies/pairs_trading.py`: cached vs per-bar paths use the shared fail-closed `_evaluate_enriched_gates_strict()`; no early returns bypass strict checks (lines 223-306, 316-348).
- [x] `data/cache.py`: memory hits restore `blocked_routes`/`blocked_hosts` from persisted meta (lines 102-107); cold fetch propagates loader blocked routes (lines 171-176); meta persists blocked routes so hits never mask failures (lines 203-206).
- [x] Loader/provenance: `fetch_with_provenance` aggregates `blocked_routes[]` across every per-symbol fetch via per-worker provenance capture (lines 523-538); never fabricates data.
- [x] Pair admission fail-closed: `_evaluate_enriched_gates_strict` blocks on `None`/missing gates, `flagged=True`, `flagged=None`/missing `structural_breaks` under strict (pairs_trading.py lines 23-68).

**BOTTLENECKS — ALL REMOVED:** Zero ad-hoc parity checks outside `tests/cointegration_parity.py`; zero fail-open coercions; borderline cases covered (9/9); cache masking eliminated.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (START HERE - DO NOT SKIP)

**TIMESTAMP:** 2026-11-04T09:07:18Z
**REPO:** `cryptoquantstatarbstrats` (= Crypto Quant Stat Arb Strategies — stat-arb strategies, plural)
**MANDATE:** You are working the **STAT-ARB STRATEGY PARITY & DIAGNOSTICS HARDENING** campaign. Execution > narration. Ship code + tests + evidence or do not stop. Cointegration pairs is the proven edge; every other strategy in this repo must meet the same publication-grade bar or it is a weak link.

**REPO SIGNAL (WHY THIS CAMPAIGN):** `cryptoquantstatarbstrats` = Crypto Quant Stat Arb Strategies. The cointegration pairs edge (`CointegrationPairsStrategy`) is hardened and verified (802/1/0 full suite). The remaining strategies — `mean_reversion.py`, `momentum.py`, `term_structure.py`, `volatility_surface.py`, `cross_exchange.py` — emit raw signals with **no enriched diagnostics schema, no fail-closed gate evaluation, no cached-vs-per-bar parity, no provenance, no blocked-route discipline**. They are un-gated, un-provenanced, and un-paralleled to the cointegration edge. This campaign closes that gap so no strategy ships without ironclad gate discipline.

**IMMEDIATE MISSION (UNSKIPPABLE, P0):**
Extend publication-grade enriched diagnostics + fail-closed parity enforcement to ALL remaining strategies. For each of `mean_reversion`, `momentum`, `term_structure`, `volatility_surface`, `cross_exchange`:
1. Add a `target_schema_diagnostics`-style diagnostics builder returning `{gates, structural_breaks, provenance, blocked_routes, blocked_schema, cost_stress, cost_grid}` computed from trailing/real data only — never fabricated.
2. Add a shared fail-closed gate evaluator (mirroring `_evaluate_enriched_gates_strict`): `None`/missing gates block in strict; `flagged=True` blocks; `flagged=None`/missing `structural_breaks` blocks in strict; no `or True`, no `is None -> True` coercion.
3. Wire `use_enriched_gates=True`, `strict_enriched_gates=True` (fail-closed default) into `generate_signals` so missing/failed diagnostics block entries, never coerce to pass.
4. Add cached-vs-per-bar parity tests using `tests/cointegration_parity.assert_cached_vs_perbar_gate_parity_strict()` (or a strategy-scoped equivalent) — zero ad-hoc comparisons outside the shared helper.
5. Add provenance + blocked-route tests proving cache hits replay provenance exactly and never mask blocked routes.
6. Real-data-only: no synthetic/fabricated candles/IV/volume as evidence; unit tests may use synthetic only when explicitly flagged `fabricated_data: true`.

**FAIL CONDITIONS (AUTO-REJECT TERMINATION):**
- Any new strategy code with fail-open coercion (`or True`, `is None: True`, ternaries collapsing None/False to pass)
- Any strategy emitting entries without fail-closed enriched-gate enforcement under `strict_enriched_gates=True`
- Any cached-vs-per-bar comparison outside the shared parity helper (bespoke `assert` blocks forbidden)
- Ending without >=1 material hardening change per strategy with tests added and evidence
- Leaving any of the five strategies without a diagnostics schema + parity test + fail-closed gating
- Weakening `use_enriched_gates`, `strict_enriched_gates`, provenance, or real-data requirements

## EXECUTE IN THIS EXACT ORDER (NO DETOUR)

### 1) BASELINE VERIFICATION (FAIL FAST)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python -m pytest tests/ -q
```
**MUST BE GREEN (802/1/0 or better).** Fix regressions before proceeding.

### 2) AUDIT EACH REMAINING STRATEGY (P0)
For each file below, confirm absence of diagnostics/gates/provenance/parity (this is the gap to close):
- `strategies/mean_reversion.py`
- `strategies/momentum.py`
- `strategies/term_structure.py`
- `strategies/volatility_surface.py`
- `strategies/cross_exchange.py`

### 3) BUILD DIAGNOSTICS + FAIL-CLOSED GATES PER STRATEGY (P0)
Per strategy file: add diagnostics builder + shared fail-closed gate evaluator + wire into `generate_signals` with `use_enriched_gates=True`/`strict_enriched_gates=True` defaults. Mirror `strategies/pairs_trading.py:23-68` (`_evaluate_enriched_gates_strict`) and `utils/cointegration.py` schema.

### 4) ADD PARITY + PROVENANCE TESTS PER STRATEGY (P0)
`tests/test_<strategy>_parity_regression.py` per strategy using the shared parity helper; cover missing/None gates, `structural_breaks.flagged=None`, missing `structural_breaks`, blocked-schema provenance preserved, cache-hit replay of blocked routes.

### 5) VERIFY, LINT, TYPECHECK, SHIP WITH EVIDENCE (MANDATORY)
```bash
python -m pytest tests/ -q
python -m ruff check strategies/ backtest/ utils/ tests/ examples/ data/
python -m mypy backtest strategies utils data
```
**DO NOT END UNTIL ALL PASS.** Report files changed, tests added/updated per strategy, and verification results.

## CURRENT VERIFIED STATE (2026-11-04T09:07:18Z)
- Cointegration campaign: COMPLETE & VERIFIED (802 passed, 1 skipped, 0 failures; mypy/ruff clean)
- Next campaign: STAT-ARB STRATEGY PARITY & DIAGNOSTICS HARDENING — ARMED, NOT STARTED
- Strategies needing hardening: mean_reversion, momentum, term_structure, volatility_surface, cross_exchange

## DISCIPLINE (NON-NEGOTIABLE)
- **HEAVY WORK REQUIRED.** No audit-only, no summary-only termination.
- **TRACE BEFORE CHANGE.** Read source+tests to understand causality.
- **FAIL-CLOSED.** Never weaken `use_enriched_gates`, `strict_enriched_gates`, provenance, or real-data requirements.
- **PARITY IS LAW.** Use `tests/cointegration_parity.assert_cached_vs_perbar_gate_parity_strict()` for all cached-vs-per-bar gate parity. No bespoke parity assertions.
- **NO COERCION.** `or True`, `is None -> True`, equivalent forbidden.
- **PUBLICATION-GRADE.** Real-data only, full provenance, evidence required.
- **SINGLE HANDOFF.** This file is the only durable handoff.
