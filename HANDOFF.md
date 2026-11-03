# DURABLE HANDOFF | TIMESTAMP: 2026-11-03T14:00:37Z | REPO: cryptoquantstatarbstrats
# PRIORITY: COINTEGRATION PAIRS EDGE - FAIL-CLOSED, REAL-DATA ONLY - HEAVY EXECUTION MANDATED

## REPO SIGNAL (INFERRED)
`cryptoquantstatarbstrats` = Crypto Quant Stat Arb Strategies. **Cointegration pairs is the sole product edge.**
Everything else exists only to support, gate, or validate the pairs/cointegration path.

## CURRENT STATE (VERIFIED 2026-11-03T14:00:32Z)
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
- Cache provenance replay tests green (memory/disk/block persistence). Loader aggregates blocked routes across parallel symbol fetches.

## BOTTLENECKS REMOVED / STATUS
- **No blocked sessions. Single clean execution path.**
- Gate parity/caching causality hardened.
- Provenance tests present and artifacts conforming.
- Parallel volume loader corrected to use full market symbols; blocked hosts skipped globally.
- Cache HITs (memory/disk) restore blocked_routes/blocked_hosts from persisted meta.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (ATOMIC, MANDATORY, START HERE)
**TIMESTAMP:** 2026-11-03T14:00:37Z
**OBJECTIVE:** Harden cache+loader provenance parity under failure conditions. Ship **>=1 material, verifiable hardening change** (code + tests/evidence). No audit-only termination.

### EXECUTE IN ORDER (NO EXPLORATION DETOUR)
1. **Verify baseline (fail fast):**
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python -m pytest tests/test_cointegration_campaign*_mt.py tests/test_cointegration_recertification_audit_mt.py tests/test_permanent_production_certification_mt.py tests/test_cointegration_diagnostics_schema.py -q
```
Must be **127/127**. Fix any failure before continuing.

2. **Harden provenance under cache/loader failure paths (P1 - highest next priority):**
   - **Loader:** In `fetch_with_provenance`, ensure blocked routes are aggregated from ALL symbol fetches (not just last) and propagate to `provenance["blocked_hosts"]`/`provenance["blocked_routes"]` even when some symbols fail. Verify `fetch_quote_volume` reports blocked routes in its provenance (currently sets them; ensure it survives aggregation).
   - **Cache:** Ensure `load_cached` copies blocked routes into returned provenance on BOTH memory and disk HITs (already done) and that when loader throws after cache miss, blocked routes from `loader.last_fetch_provenance` are still attached to the raised/propagated provenance context where possible.
   - **fetch_with_provenance + cache:** When cache returns data, also merge any blocked routes from loader/cache meta into the top-level provenance dict and ensure `provenance["cache"]` retains them.
   - **Regression:** Add/strengthen a test that simulates: (a) cold fetch hits blocked host for some symbols in parallel path, (b) cache written, (c) subsequent calls (memory + disk) still report identical `blocked_routes` and `blocked_hosts`. If gaps exist, fix code to make it impossible to lose them.
   - **Artifacts sanity:** Quickly verify `reports/portfolio_real.json` and `reports/cointegration_diagnostics_real.json` still conform to `tests/test_provenance_artifacts.py` (funding_basis has full provenance/attempts, pair provenance complete).

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
