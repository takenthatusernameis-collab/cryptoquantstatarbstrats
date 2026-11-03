# DURABLE HANDOFF | TIMESTAMP: 2026-11-03T14:07:44Z | REPO: cryptoquantstatarbstrats
# PRIORITY: COINTEGRATION PAIRS EDGE - FAIL-CLOSED, REAL-DATA ONLY - HEAVY EXECUTION MANDATED

## REPO SIGNAL (INFERRED)
`cryptoquantstatarbstrats` = Crypto Quant Stat Arb Strategies. **Cointegration pairs is the sole product edge.**
Everything else exists only to support, gate, or validate the pairs/cointegration path.

## CURRENT STATE (VERIFIED 2026-11-03T14:07:44Z)
- Critical subset (cointegration campaigns/recertification/permanent cert/schema): **127 passed** (green).
- Full suite: **771 passed, 1 skipped** (green).
- Lint (`ruff check strategies/ backtest/ utils/ tests/ examples/`): **All checks passed**.
- mypy (`python -m mypy backtest strategies utils`): **Success: no issues found**.
- Working tree **clean** on `main`.
- Real-data only enforced; fail-closed gates unified. No fail-open coercions found.
- Bottlenecks removed: cache/loader provenance parity hardened (blocked routes propagate on cache miss exceptions; aggregation fills routes when only hosts present).

## BOTTLENECKS REMOVED / STATUS
- **No blocked sessions. Single clean execution path.**
- Gate parity/caching causality hardened.
- Provenance tests present and artifacts conforming.
- Parallel volume loader corrected; cache HITs replay blocked routes.
- **Just shipped:** `data/cache.py` now attaches loader blocked routes on cold-fetch exception; `data/loader.py` ensures `blocked_routes` populated from aggregated hosts.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (ATOMIC, MANDATORY, START HERE)
**TIMESTAMP:** 2026-11-03T14:07:44Z
**OBJECTIVE:** Extend cache+loader provenance parity to ALL failure/partial paths for cointegration pairs edge. Ship **>=1 material, verifiable hardening change** (code + tests/evidence). No audit-only termination. Heavy execution required.

### EXECUTE IN ORDER (NO EXPLORATION DETOUR)
1. **Verify baseline (fail fast):**
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python -m pytest tests/test_cointegration_campaign*_mt.py tests/test_cointegration_recertification_audit_mt.py tests/test_permanent_production_certification_mt.py tests/test_cointegration_diagnostics_schema.py -q
```
Must be **127/127**. Fix any failure before continuing.

2. **Harden provenance under all failure/partial paths (P1 - highest next priority):**
   - **Loader (`fetch_with_provenance`)**: When cache throws, ensure blocked routes from loader/cache context are propagated into top-level provenance (and into `provenance["cache"]`) even if exception occurs mid-flow. Also ensure aggregation of blocked routes happens before raising "No real Binance data fetched..." and is attached to the error context where feasible.
   - **Loader (`load_binance_data`)**: If all symbols fail but blocked_hosts exist, ensure `last_fetch_provenance` has both `blocked_hosts` and `blocked_routes` (and they are non-empty). Consider attaching them to the raised RuntimeError message context via provenance attachment if possible.
   - **Cache**: On any exception path (read/write), never drop blocked routes. When re-storing in memory after disk HIT, merge blocked routes from meta/provenance. Ensure `load_cached` returns provenance with canonical keys.
   - **fetch_quote_volume**: Ensure blocked routes are aggregated across parallel fetches and reported in provenance (already sets `blocked_routes` from blocked_hosts; verify parity with price loader).
   - **Regression test**: Add/strengthen test simulating (a) parallel fetch where some symbols hit blocked host, (b) cache written with blocked routes, (c) subsequent memory+disk HITs identical, (d) failure path propagates blocked routes. If gaps exist, fix code.

3. **Verify & ship:**
   - Run critical subset again after changes.
   - Run cache provenance tests: `python -m pytest tests/test_cache_provenance_replay.py -v`
   - If touching gates/engine/core/data/cache/loader, run full suite: `python -m pytest tests/ -q` (expect 771 passed, 1 skipped).
   - `ruff check strategies/ backtest/ utils/ tests/ examples/` must pass.
   - `python -m mypy backtest strategies utils` must pass.
   - **Do not end until all pass and a material hardening is shipped with traceable evidence.**

## MANDATORY FOCUS CAMPAIGN (UNSKIPPABLE - HEAVY WORK REQUIRED)
Every session MUST ship >=1 material, verifiable hardening change on the cointegration pairs edge. No summary-only termination.

### P0 - EXECUTION PARITY & GATE INTEGRITY
1. Hunt fail-open coercions: `grep -rn "\bor True\b\|if .* is None: .* True\|True if .* is None" strategies/ utils/ backtest/ | grep -v __pycache__` → zero tolerance.
2. Cached vs per-bar parity under `strict_enriched_gates=True`; structural breaks must block both modes identically.
3. Diagnostics never fabricate/clamp; blocked cases use `blocked_schema_diagnostics` with full provenance.

### P1 - REAL-DATA PROVENANCE & DATA LOADING (CURRENT MANDATE)
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

## SUCCESS CRITERIA
- [ ] Critical subset 127/127
- [ ] Cache provenance tests pass
- [ ] Full suite 771 passed, 1 skipped (if scope touched core/gates/data/cache/loader)
- [ ] `ruff` clean
- [ ] `mypy` clean on touched modules
- [ ] Material hardening shipped with traceable evidence
- [ ] No gate/provenance/execution weakening
