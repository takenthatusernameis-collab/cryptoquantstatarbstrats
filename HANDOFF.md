TIMESTAMP: 2026-11-04T15:26:14Z | REPO: cryptoquantstatarbstrats
# PRIORITY: HEAVY-WORK CAMPAIGN — NEXT-GENERATION STAT-ARB EXPANSION (ALL 7 STRATEGIES)

> **SINGLE SOURCE OF TRUTH. THIS SUPERSEDES ALL PREVIOUS HANDOFF ENTRIES. READ THIS FIRST. NO OTHER PRIORITY FILES.**

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (START HERE)

**TIMESTAMP:** 2026-11-04T15:26:14Z
**REPO:** `cryptoquantstatarbstrats` (Crypto Quant Stat Arb Strategies — stat-arb, plural; all 7 strategies in scope: momentum, term_structure, volatility_surface, cross_exchange, pairs, mean_reversion, portfolio)

**MANDATE (HEAVY WORK REQUIRED):** The prior publication-grade verification/ship campaign is COMPLETE. The next campaign is **HEAVY-WORK EXPANSION**: deliver a measurable, end-to-end advance across all seven strategies — new real-market evidence, stricter fail-closed gates, and cross-strategy integration — not audits or summaries. Future agents MUST NOT terminate early; every session must produce code + tests + artifacts.

**CAMPAIGN SUCCESS CRITERIA (must all hold before reporting done):**
1. Each of the 7 strategies gains at least one new real-market regression test with `real_data_only: true` / `fabricated_data: false` provenance.
2. `python -m ruff check strategies/ backtest/ utils/ tests/ examples/ data/` → zero errors.
3. `python -m mypy backtest strategies utils data` → zero errors.
4. `python -m pytest tests/ -q` green (target ≥ current baseline + 7 new tests).
5. Cross-strategy parity lock (`tests/cointegration_parity.assert_cached_vs_perbar_gate_parity_strict()`) intact.
6. No weakening of `use_enriched_gates`, `strict_enriched_gates`, provenance, or real-data requirements.

**EXECUTION ORDER:**
1. Read this file + README; do not re-derive prior state.
2. Establish per-strategy success criteria before touching code.
3. Trace before change; read source + tests to understand causality.
4. Implement heavy changes; add tests + artifacts.
5. Run ruff + mypy + full pytest; fix until green.

## DISCIPLINE (NON-NEGOTIABLE, CARRIES FORWARD)
- HEAVY WORK REQUIRED. No audit-only, no summary-only termination.
- TRACE BEFORE CHANGE.
- FAIL-CLOSED.
- PARITY IS LAW.
- NO COERCION.
- REAL-DATA ONLY.
- PUBLICATION-GRADE.
- SINGLE HANDOFF. This file is the only durable handoff.

(End of file)
