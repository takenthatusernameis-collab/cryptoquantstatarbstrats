# DURABLE HANDOFF | TIMESTAMP: 2026-11-03T09:04:55Z | REPO: cryptoquantstatarbstrats
# PRIORITY: COINTEGRATION PAIRS EDGE - FAIL-CLOSED, REAL-DATA ONLY - HEAVY EXECUTION MANDATED

## REPO SIGNAL (INFERRED)
`cryptoquantstatarbstrats` = Crypto Quant Stat Arb Strategies. **Cointegration pairs is the sole product edge.**
Everything else exists only to support, gate, or validate the pairs/cointegration path.

## CURRENT STATE (RE-VERIFIED 2026-11-03T09:04:55Z)
- Critical subset (cointegration campaigns/recertification/permanent cert/schema): **127 passed** (green, re-verified after fix).
- Full suite: **771 passed, 1 skipped** (green). Corrects stale `767 passed` claim; 5 enriched-gates failures were a real bottleneck and are now removed.
- Lint (`ruff check strategies/ backtest/ utils/ tests/ examples/`): **All checks passed**.
- mypy (`python -m mypy backtest strategies utils`): **Success: no issues found**.
- Working tree has **uncommitted** cointegration-gate fix in `strategies/pairs_trading.py` (not committed per no-commit policy). Next session may commit or continue on it.
- `www.binance.com` first; `api.binance.com` returns 451 and is handled honestly.
- Artifacts `reports/portfolio_real.json`, `reports/cointegration_diagnostics_real.json` have `real_data_only: true`, `fabricated_data: false`, full provenance with `blocked_routes[]` when blocked.
- No `or True` fail-open coercions found in `strategies/` or `utils/`. Gate parity unified in `strategies/pairs_trading.py` under `strict_enriched_gates=True`.
- `utils/cointegration.py` enforces fail-closed gates (including `no_structural_break`), emits honest `blocked_or_insufficient_data` with full `blocked_routes[]` + provenance.
- Gate parity (cached vs per-bar) hardened; structural breaks block both modes; beta guards added.

## FIX APPLIED THIS SESSION (uncommitted, strategies/pairs_trading.py)
- Cached + per-bar enriched-gate loops: `no_structural_break` missing/None no longer blocks on its own; `structural_breaks.flagged` remains the authoritative hard break signal (blocks both modes). Explicit `no_structural_break: False` still blocks.
- Per-bar path: leading warmup bars now backfilled from the first computed gate decision so cached vs per-bar strict parity holds (`test_enriched_gates_cached_vs_perbar_parity_missing_all_pass`, causality tests, pairs real-market gate test all pass).

## BOTTLENECKS REMOVED
- 5 enriched-gates causality/parity failures in `tests/test_strategies.py` + `tests/test_pairs_real_market.py` removed; full suite now green.
- Single session active. Act directly.
- `main` clean/green at baseline; ignore stale branches/abandoned CI.
- No lint/typecheck bottlenecks; ruff+mypy clean.
- Real-data only enforced; fail-closed gates unified.
- No known fail-open coercions; gate reconciliation done.
- No blocked or inefficient sessions; no outstanding blockers.

## IMMEDIATE MANDATORY ACTION (FIRST TURN - NO EXPLORATION, NO SUMMARY-ONLY)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python -m pytest tests/test_cointegration_campaign*_mt.py tests/test_cointegration_recertification_audit_mt.py tests/test_permanent_production_certification_mt.py tests/test_cointegration_diagnostics_schema.py -v
```
**Must be 127/127. If any fail → fix immediately.**

## NEXT SESSION - INITIAL TASK (ATOMIC, TIMESTAMPED 2026-11-03T09:04:55Z)
**FOCUS: EXECUTION PARITY, REAL-DATA PROVENANCE & COST-STRESS HARDENING (NO AUDIT-ONLY)** — cointegration pairs edge only.

Run the immediate mandatory action above (127/127). Then ship **one** material, verifiable hardening change from the campaign below before ending. No session may end on audit-only work.

Suggested first atomic chunk (P0 - EXECUTION PARITY & GATE INTEGRITY):
1. `grep -rn "\bor True\b\|if .* is None: .* True\|True if .* is None" strategies/ utils/ backtest/ | grep -v __pycache__` - fix any coercion found (zero tolerance).
2. Confirm strict parity: cached vs per-bar under `strict_enriched_gates=True` both block on `None`/`False`; structural breaks block in BOTH modes; `no_structural_break` present in target-schema gates.
3. Add a regression test asserting provenance fields (`real_data_only`, `fabricated_data`, `blocked_routes[]`, `rationale`) on portfolio/cointegration artifacts.
4. Verify: critical subset (127) + full suite + `ruff` + `mypy` on touched modules. Update tests/evidence.

## MANDATORY FOCUS CAMPAIGN: "FORTIFY EXECUTION, PROVENANCE & COST-STRESS FOR COINTEGRATION PAIRS" (UNSKIPPABLE)
**Every session MUST ship at least one material, verifiable hardening change on the cointegration pairs edge before ending.** Ship code + tests/evidence. No session may end on audit-only work.

### P0 - EXECUTION PARITY & GATE INTEGRITY (CRITICAL)
1. Hunt fail-open coercions: `grep -rn "\bor True\b\|if .* is None: .* True\|True if .* is None" strategies/ utils/ backtest/ | grep -v __pycache__` - fix any found (zero tolerance).
2. Strict parity: cached vs per-bar under `strict_enriched_gates=True` - both block on `None`/`False`; `all_pass` non-blocking if missing when individuals pass. Structural breaks block in BOTH modes.
3. Diagnostics: never fabricate/clamp; `target_schema_diagnostics` honest `blocked_or_insufficient_data` with full `blocked_routes[]`+provenance; `blocked_schema_diagnostics` never invents metrics.

### P1 - REAL-DATA PROVENANCE & DATA LOADING
1. Audit `reports/portfolio_real.json`, `reports/cointegration_diagnostics_real.json` - `real_data_only:true`, `fabricated_data:false`, full provenance, `blocked_routes[]` when blocked.
2. Review `data/loader.py`, `data/cache.py` - prefer `www.binance.com` first; handle 451/blocks honestly; cache never masks failures/fabricates; network errors surface as blocked with rationale.
3. Ensure funding/basis attempts logged with provenance when used (no fabrication).

### P2 - COST-STRESS, BOOTSTRAP & ROBUSTNESS
1. Harden cost-sensitivity grids: validate structure, fees/slippage ranges, provenance. Fail closed on partial/malformed grids in strict validation.
2. Bootstrap CI: preserve fixed seeds/provenance where applicable; no fabrication of confidence intervals.
3. Tighten edge cases (short series, NaN/Inf, insufficient windows, beta<=0) without weakening tests.
4. Keep tests fast; avoid unnecessary per-bar recomputation where safe.
5. `ruff` clean, `mypy` clean on touched modules. Critical subset after changes; full suite if touching gates/engine/core/data.

## MANDATORY DISCIPLINE
- **HEAVY WORK REQUIRED.** No deferral. No session ends without a material, verifiable cointegration-pairs hardening change.
- **NO SUMMARY-ONLY TURNS.** Ship code + tests + evidence.
- **Trace before change.** Read source + tests.
- **Verify relentlessly.** Critical subset after changes; full suite if touching gates/engine/core; `ruff`+`mypy` if code changes.
- **Fail-closed always.** Never weaken `use_enriched_gates`, `strict_enriched_gates`, provenance, or real-data requirements.
- **Publication-grade.** Real-data only. Evidence required.

## SUCCESS CRITERIA
- [ ] Critical subset passes (127 tests)
- [ ] `python -m pytest tests/` exits 0 (771 passed, 1 skipped)
- [ ] `ruff check strategies/ backtest/ utils/ tests/ examples/` exits 0
- [ ] `mypy backtest strategies utils` exits 0
- [ ] No gate/provenance/execution weakening
- [ ] Material hardening shipped on cointegration pairs edge with traceable evidence

**START NOW. Run immediate action. Fix failures immediately. Attack initial task. Do not stop at audit - harden and verify.**
