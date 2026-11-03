# DURABLE HANDOFF | TIMESTAMP: 2026-11-03T07:39:45Z | REPO: cryptoquantstatarbstrats
# PRIORITY: COINTEGRATION PAIRS EDGE - FAIL-CLOSED, REAL-DATA ONLY - HEAVY EXECUTION MANDATED

## REPO SIGNAL (INFERRED)
`cryptoquantstatarbstrats` = Crypto Quant Stat Arb Strategies. **Cointegration pairs is the sole product edge.**
Everything else exists only to support, gate, or validate the pairs/cointegration path.

## GROUND TRUTH (RE-VERIFIED 2026-11-03T07:39:45Z)
- Critical subset (cointegration campaigns/recertification/permanent cert/schema): **127 passed** (verified just now).
- Full suite: **767 passed, 1 skipped** (verified 2026-11-03T05:35:28Z).
- Lint: `python -m ruff check strategies/ backtest/ utils/ tests/ examples/` → **All checks passed**.
- mypy: `python -m mypy backtest strategies utils` → **Success: no issues found in 32 source files**.
- Working tree clean on `main`. `www.binance.com` first; `api.binance.com` returns 451 and is handled honestly.
- Artifacts: `reports/portfolio_real.json`, `reports/cointegration_diagnostics_real.json` have `real_data_only: true`, `fabricated_data: false`, full provenance with `blocked_routes[]` when blocked.
- No `or True` fail-open coercions found in `strategies/` or `utils/`. Gate parity unified in `strategies/pairs_trading.py` under `strict_enriched_gates=True` (cached + per-bar both block on `None`/`False`; `all_pass` non-blocking if missing when individuals pass).
- `utils/cointegration.py` enforces fail-closed gates (including `no_structural_break`), emits honest `blocked_or_insufficient_data` with full `blocked_routes[]` + provenance; `blocked_schema_diagnostics` never invents metrics.

## IMMEDIATE MANDATORY ACTION (FIRST TURN - NO EXPLORATION, NO SUMMARY-ONLY)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python -m pytest tests/test_cointegration_campaign*_mt.py tests/test_cointegration_recertification_audit_mt.py tests/test_permanent_production_certification_mt.py tests/test_cointegration_diagnostics_schema.py -v
```
**Must be 127/127. If any fail → fix immediately.**

## NEXT SESSION - INITIAL TASK (ATOMIC, TIMESTAMPED 2026-11-03T07:39:45Z)
**FOCUS: HARDEN PER-BAR ENRICHED GATE PARITY & STRESS GUARDS (NO AUDIT-ONLY)**

1. **Verify strict parity under load**: Trace both paths in `strategies/pairs_trading.py` again with `strict_enriched_gates=True`. Ensure cached dict path and per-bar `target_schema_diagnostics` path produce identical block decisions for the same gate states (especially `structural_breaks.flagged`, `None`/missing individual gates, and missing `all_pass`). Add a tight regression test if any ambiguity remains.
2. **Harden rolling stability edge cases**: In `utils/cointegration.py` `rolling_cointegration_stability`, tighten guards for short windows/insufficient data (never coerce to pass). Ensure `frac_significant`/`stable` remain honest; blocked routes propagate with provenance.
3. **Tighten structural break propagation**: Confirm `structural_break_check` never fabricates and `target_schema_diagnostics` always records `no_structural_break` in gates + blocked_routes when flagged/unassessable per fail-closed rules. Verify strategy blocks on flagged breaks in both strict/non-strict modes (already unified - stress test with a synthetic case).
4. **Add one concrete stress guard**: Add/strengthen at least one guard (e.g. beta<=0, NaN/Inf spread, empty/short sample) with a unit test that asserts fail-closed behavior. Do not weaken existing tests.
5. **Verify & ship**: Run critical subset + `ruff` + `mypy` on touched modules. Ship code+tests/evidence. **No summary-only turn.**

## BOTTLENECKS REMOVED
- Single session active. Act directly.
- `main` clean/green. Ignore stale branches/abandoned CI.
- Real-data only enforced; fail-closed gates unified.
- No known fail-open coercions; gate reconciliation done.

## MANDATORY FOCUS CAMPAIGN: "FORTIFY, STRESS-TEST & HARDEN COINTEGRATION GATES" (UNSKIPPABLE)
**Every session MUST ship at least one material, verifiable gate-hardening/validation change on the cointegration pairs edge before ending.** Ship code + tests/evidence.

### P0 - GATE INTEGRITY (CRITICAL)
1. Hunt fail-open coercions: `grep -rn "\bor True\b\|if .* is None: .* True\|True if .* is None" strategies/ utils/ | grep -v __pycache__` - fix any found (zero tolerance).
2. Strict parity: cached vs per-bar under `strict_enriched_gates=True` - both block on `None`/`False`; `all_pass` non-blocking if missing when individuals pass.
3. Diagnostics: never fabricate/clamp; `target_schema_diagnostics` honest `blocked_or_insufficient_data` with full `blocked_routes[]`+provenance; `blocked_schema_diagnostics` never invents metrics.

### P1 - REAL-DATA PROVENANCE
1. Audit `reports/portfolio_real.json`, `reports/cointegration_diagnostics_real.json` - `real_data_only:true`, `fabricated_data:false`, full provenance, `blocked_routes[]` when blocked.
2. Review `data/loader.py`, `data/cache.py` - prefer `www.binance.com` first; handle 451/blocks honestly; cache never masks failures/fabricates.

### P2 - STRESS, REGRESSION GUARDS & ROBUSTNESS
1. Tighten edge cases (short series, NaN/Inf, insufficient windows, beta<=0) without weakening tests.
2. Keep tests fast; avoid unnecessary per-bar recomputation where safe.
3. `ruff` clean, `mypy` clean on touched modules. Critical subset after changes; full suite if touching gates/engine/core.

## MANDATORY DISCIPLINE
- **HEAVY WORK REQUIRED.** No deferral.
- **NO SUMMARY-ONLY TURNS.** Ship code/tests/evidence.
- **Trace before change.** Read source+tests.
- **Verify relentlessly.** Critical subset after changes; full suite if touching gates/engine/core; `ruff`+`mypy` if code changes.
- **Fail-closed always.** Never weaken `use_enriched_gates`, `strict_enriched_gates`, provenance, or real-data requirements.
- **Publication-grade.** Real-data only. Evidence required.

## SUCCESS CRITERIA
- [ ] Critical subset passes (127 tests)
- [ ] `python -m pytest tests/` exits 0 (767 passed, 1 skipped)
- [ ] `ruff check strategies/ backtest/ utils/ tests/ examples/` exits 0
- [ ] `mypy backtest strategies utils` exits 0
- [ ] No gate/provenance weakening
- [ ] Material hardening shipped on cointegration pairs edge with traceable evidence

**START NOW. Run immediate action. Fix failures immediately. Attack initial task. Do not stop at audit - harden and verify.**
