# DURABLE HANDOFF | TIMESTAMP: 2026-11-03T13:56:42Z | REPO: cryptoquantstatarbstrats
# PRIORITY: COINTEGRATION PAIRS EDGE - FAIL-CLOSED, REAL-DATA ONLY - HEAVY EXECUTION MANDATED

## REPO SIGNAL (INFERRED)
`cryptoquantstatarbstrats` = Crypto Quant Stat Arb Strategies. **Cointegration pairs is the sole product edge.**
Everything else exists only to support, gate, or validate the pairs/cointegration path.

## CURRENT STATE (VERIFIED 2026-11-03T13:56:42Z)
- Critical subset (cointegration campaigns/recertification/permanent cert/schema): **127 passed** (green).
- Full suite: **771 passed, 1 skipped** (green).
- Lint (`ruff check strategies/ backtest/ utils/ tests/ examples/`): **All checks passed**.
- mypy (`python -m mypy backtest strategies utils`): **Success: no issues found**.
- Working tree **clean** on `main`.
- Real-data only enforced; fail-closed gates unified. No fail-open coercions found.
- `www.binance.com` first; `api.binance.com` 451 handled honestly.
- `data/loader.py` + `data/cache.py` propagate blocked routes; cache never masks failures.
- `utils/cointegration.py` enforces gates (incl. structural break); `strategies/pairs_trading.py` gate parity under `strict_enriched_gates=True`.
- Artifacts have full provenance with `real_data_only:true`, `fabricated_data:false`, `blocked_routes[]` when blocked.

## BOTTLENECKS REMOVED / STATUS
- No blocked sessions. Single clean path.
- Gate parity/caching causality hardened.
- Provenance tests present and artifacts conforming.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (ATOMIC, MANDATORY, START HERE)
**TIMESTAMP:** 2026-11-03T13:56:42Z
**OBJECTIVE:** Fortify real-data provenance/loading honesty for cointegration pairs edge. Ship **>=1 material, verifiable hardening change** (code + tests/evidence). No audit-only termination.

### EXECUTE IN ORDER (NO EXPLORATION DETOUR)
1. **Verify baseline (fail fast):**
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python -m pytest tests/test_cointegration_campaign*_mt.py tests/test_cointegration_recertification_audit_mt.py tests/test_permanent_production_certification_mt.py tests/test_cointegration_diagnostics_schema.py -q
```
Must be **127/127**. Fix any failure before continuing.

2. **Harden data loading provenance (P1 - highest next priority):**
   - Inspect `data/loader.py` (host order `www.binance.com` first, 451/403/404/blocked routes tracked, per-symbol attempts, excluded with reasons, fail-closed).
   - Inspect `data/cache.py` (disk/memory cache must preserve `blocked_hosts/blocked_routes` on hit, never fabricate, never mask failures; write full meta).
   - Ensure `fetch_with_provenance` propagates blocked routes from cache/loader.
   - Verify `reports/portfolio_real.json` and `reports/cointegration_diagnostics_real.json` conform to `test_provenance_artifacts.py`. Confirm `funding_basis` has full provenance, attempts logged, no fabrication.
   - **Action:** Add/strengthen a regression test if any provenance field is missing or cache-hit could mask blocked routes; harden code to enforce it. Make it impossible for cache to lose `blocked_routes`.

3. **Verify & ship:**
   - Run critical subset again after changes.
   - If touching gates/engine/core/data, run full suite `python -m pytest tests/ -q` (expect 771 passed, 1 skipped).
   - `ruff check strategies/ backtest/ utils/ tests/ examples/` must pass.
   - `python -m mypy backtest strategies utils` must pass.
   - Update evidence in commit/notes as appropriate. **Do not end until all pass and a material hardening is shipped.**

## MANDATORY FOCUS CAMPAIGN (UNSKIPPABLE)
Every session MUST ship >=1 material, verifiable hardening change on cointegration pairs edge.

### P0 - EXECUTION PARITY & GATE INTEGRITY
1. Hunt fail-open coercions: `grep -rn "\bor True\b\|if .* is None: .* True\|True if .* is None" strategies/ utils/ backtest/ | grep -v __pycache__` → zero tolerance.
2. Cached vs per-bar parity under `strict_enriched_gates=True`; structural breaks block both modes.
3. Diagnostics never fabricate/clamp; blocked cases use `blocked_schema_diagnostics` with full provenance.

### P1 - REAL-DATA PROVENANCE & DATA LOADING (CURRENT MANDATE)
1. Loader/cache: prefer `www.binance.com`, handle 451/blocks honestly, cache never masks failures/fabricates.
2. Artifacts: `real_data_only:true`, `fabricated_data:false`, full provenance, `blocked_routes[]` when blocked.
3. Funding/basis attempts logged with provenance, no fabrication.
4. Strengthen provenance regression tests if gaps found.

### P2 - COST-STRESS, BOOTSTRAP & ROBUSTNESS
1. Cost grids validated/fail-closed in strict mode; provenance preserved.
2. Bootstrap CI with fixed seeds/provenance, no fabrication.
3. Edge cases hardened without weakening tests.

## DISCIPLINE
- **HEAVY WORK REQUIRED.** No deferral. No summary-only termination.
- **TRACE BEFORE CHANGE.** Read source + tests.
- **FAIL-CLOSED.** Never weaken `use_enriched_gates`, `strict_enriched_gates`, provenance, or real-data requirements.
- **PUBLICATION-GRADE.** Real-data only. Evidence required.

## SUCCESS CRITERIA
- [ ] Critical subset 127/127
- [ ] Full suite 771 passed, 1 skipped (if scope touched core/gates/data)
- [ ] `ruff` clean
- [ ] `mypy` clean on touched modules
- [ ] Material hardening shipped with traceable evidence
- [ ] No gate/provenance/execution weakening
