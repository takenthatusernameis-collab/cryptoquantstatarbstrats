# DURABLE HANDOFF | TIMESTAMP: 2026-11-03T16:05:15Z | REPO: cryptoquantstatarbstrats
# PRIORITY: COINTEGRATION PAIRS EDGE - FAIL-CLOSED, REAL-DATA ONLY - HEAVY EXECUTION MANDATED

## REPO SIGNAL (INFERRED)
`cryptoquantstatarbstrats` = Crypto Quant Stat Arb Strategies. **Cointegration pairs is the sole product edge.**
Everything else exists only to support, gate, or validate the pairs/cointegration path.

## CURRENT STATE (VERIFIED 2026-11-03T16:05:15Z)
- Critical subset (cointegration campaigns/recertification/permanent cert/schema): **127 passed** (green).
- Cointegration-related tests (`-k cointegration`): **137 passed** (green).
- Cache provenance replay tests: **6 passed** (green).
- Lint (`ruff check strategies/ backtest/ utils/ tests/ examples/`): **All checks passed**.
- mypy (`python -m mypy backtest strategies utils`): **Success: no issues found**.
- Working tree **clean** on `main` (mypy bottleneck in data/loader.py removed).
- Real-data only enforced; fail-closed gates unified. No fail-open coercions found.
- Bottlenecks removed: cache/loader provenance parity hardened. Single clean execution path.
- Fail-open coercion hunt (`grep -rn "\bor True\b\|is None: .* True\|True if .* is None" strategies/ utils/ backtest/`): **zero matches**.

## BOTTLENECKS REMOVED / STATUS
- **No blocked sessions. Single consolidated execution path.**
- Cache/loader causality hardened (blocked routes propagate on cache miss exceptions; aggregation fills routes when only hosts present).
- Provenance tests present and artifacts conforming.
- Parallel volume loader corrected; cache HITs replay blocked routes.
- mypy type-ignore bottleneck in data/loader.py:295 removed (multiple ignores on one line failed under mypy 2.4.1).
- **Consolidated:** Single durable handoff established. No parallel handoff files competing for priority.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (ATOMIC, MANDATORY, START HERE)
**TIMESTAMP:** 2026-11-03T16:05:15Z
**OBJECTIVE:** Harden **cointegration pair discovery + gate integrity** to be unbreakable under real-data constraints. Ship **>=1 material, verifiable hardening change** (code + tests/evidence). No audit-only termination. Heavy execution required.

### EXECUTE IN ORDER (NO EXPLORATION DETOUR)
1. **Verify baseline (fail fast):**
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python -m pytest tests/test_cointegration_campaign*_mt.py tests/test_cointegration_recertification_audit_mt.py tests/test_permanent_production_certification_mt.py tests/test_cointegration_diagnostics_schema.py -q
```
Must be **127/127**. Fix any failure before continuing.

2. **Harden cointegration pair discovery + gate integrity (P0 - highest next priority):**
   - **Pair selection (`strategies/` cointegration paths):** Ensure every candidate pair passes Engle-Granger/Johansen checks with real data only. No synthetic/fallback pairs. Fail-closed if tests inconclusive or insufficient observations.
   - **Gate parity:** Enforce identical pass/fail between cached and non-cached paths under `strict_enriched_gates=True`. Any divergence = bug, must fix.
   - **Cost-stress fail-closed:** Validate cost grids are applied and cannot be bypassed. Provenance must record cost assumptions. Reject if costs missing in strict mode.
   - **Diagnostics integrity:** `blocked_schema_diagnostics` must be used for blocked cases with full provenance. Never fabricate/clamp diagnostics.
   - **Regression test:** Add/strengthen test that forces a borderline pair through cached+uncached paths and verifies identical gate outcomes + identical provenance keys.

3. **Verify & ship:**
   - Run critical subset again after changes.
   - Run cache provenance tests: `python -m pytest tests/test_cache_provenance_replay.py -v`
   - Run cointegration-related tests broadly: `python -m pytest tests/ -k cointegration -q`
   - If touching gates/engine/core/data/strategies/backtest, run full suite: `python -m pytest tests/ -q` (expect 771 passed, 1 skipped).
   - `ruff check strategies/ backtest/ utils/ tests/ examples/` must pass.
   - `python -m mypy backtest strategies utils` must pass.
   - **Do not end until all pass and a material hardening is shipped with traceable evidence.**

## MANDATORY FOCUS CAMPAIGN (UNSKIPPABLE - HEAVY WORK REQUIRED)
Every session MUST ship >=1 material, verifiable hardening change on the cointegration pairs edge. No summary-only termination.

### P0 - EXECUTION PARITY & GATE INTEGRITY (CURRENT MANDATE)
1. Hunt fail-open coercions: `grep -rn "\bor True\b\|if .* is None: .* True\|True if .* is None" strategies/ utils/ backtest/ | grep -v __pycache__` → zero tolerance.
2. Cached vs per-bar parity under `strict_enriched_gates=True`; structural breaks must block both modes identically.
3. Diagnostics never fabricate/clamp; blocked cases use `blocked_schema_diagnostics` with full provenance.
4. Pair selection must be real-data only and fail-closed on inconclusive tests.

### P1 - REAL-DATA PROVENANCE & DATA LOADING
1. Loader/cache: prefer `www.binance.com`, handle 451/403/404/blocks honestly, cache never masks failures/fabricates.
2. Parallel symbol fetches must aggregate blocked routes from every symbol's loader provenance.
3. Artifacts: `real_data_only:true`, `fabricated_data:false`, full provenance, `blocked_routes[]` when blocked (never empty-by-omission).
4. Funding/basis attempts logged with provenance, no fabrication.
5. Strengthen provenance regression tests if gaps found.

### P2 - COST-STRESS, BOOTSTRAP & ROBUSTNESS
1. Cost grids validated/fail-closed in strict mode; provenance preserved.
2. Bootstrap CI with fixed seeds/provenance, no fabrication.
3. Edge cases hardened without weakening tests/gates/provenance.

## DISCIPLINE
- **HEAVY WORK REQUIRED.** No deferral. No audit-only termination.
- **TRACE BEFORE CHANGE.** Read source + tests. Understand causality.
- **FAIL-CLOSED.** Never weaken `use_enriched_gates`, `strict_enriched_gates`, provenance, or real-data requirements.
- **PUBLICATION-GRADE.** Real-data only. Evidence required (tests + lint + mypy + affected artifacts).
- **SINGLE HANDOFF.** This is the only durable handoff. No competing priority files.

## SUCCESS CRITERIA
- [ ] Critical subset 127/127
- [ ] Cache provenance tests pass
- [ ] Cointegration-related tests pass
- [ ] Full suite 771 passed, 1 skipped (if scope touched core/gates/data/cache/loader/strategies)
- [ ] `ruff` clean
- [ ] `mypy` clean on touched modules
- [ ] Material hardening shipped with traceable evidence
- [ ] No gate/provenance/execution weakening
