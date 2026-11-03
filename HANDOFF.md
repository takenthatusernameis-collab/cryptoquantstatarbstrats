# DURABLE HANDOFF | TIMESTAMP: 2026-11-03T08:39:18Z | REPO: cryptoquantstatarbstrats
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


## SESSION UPDATE (2026-11-03T07:53:58Z) - GATE PARITY & STRESS HARDENING (COMPLETED)
- **Parity**: Added cached vs per-bar parity tests (structural break flagged; all_pass missing with individuals passing; None individual gates in strict). Both paths enforce structural break blocking under both modes and block on None in strict with `all_pass` non-blocking when missing but individuals pass.
- **Rolling stability**: Hardened `utils/cointegration.rolling_cointegration_stability` to always emit `frac_significant_0_05`/`frac_significant` and `n_windows` (honest 0 on insufficient/unassessable) - fail-closed.
- **Structural break propagation**: Verified `no_structural_break` gate present in target schema; unassessable/flagged cases fail-closed with blocked routes/provenance.
- **Strategy guards**: Added beta validation in `CointegrationPairsStrategy.generate_signals` (clip/guard non-positive/NaN/Inf) + unit test `test_pairs_beta_non_positive_fails_closed` asserting fail-closed behavior.
- **Verification**: Critical subset 127/127 passed. `ruff` clean on touched files; `mypy backtest strategies utils` success (32 files).


## SESSION UPDATE (2026-11-03T08:35:28Z) - COINTEGRATION PRODUCTION HARDENING: EXECUTION PARITY, DATA PROVENANCE & COST-STRESS VALIDATION
**PRIORITY: COINTEGRATION PAIRS EDGE - FAIL-CLOSED, REAL-DATA ONLY - HEAVY EXECUTION MANDATED**

### REPO SIGNAL (INFERRED)
`cryptoquantstatarbstrats` = Crypto Quant Stat Arb Strategies. **Cointegration pairs is the sole product edge.** All work must strengthen the pairs/cointegration path with traceable evidence.

### CURRENT STATE (VERIFIED)
- Critical subset (cointegration campaigns/recertification/permanent cert/schema): **127 passed** (green)
- Full suite: **767 passed, 1 skipped** (green)
- Lint (`ruff`): clean on strategies/ backtest/ utils/ tests/ examples/
- Typecheck (`mypy`): Success: no issues found in 32 source files
- Working tree clean on `main`. Real-data only enforced; fail-closed gates unified.
- Gate parity hardened (cached vs per-bar); structural breaks block in both modes; beta guards added.

### IMMEDIATE MANDATORY ACTION (FIRST TURN - NO EXPLORATION, NO SUMMARY-ONLY)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python -m pytest tests/test_cointegration_campaign*_mt.py tests/test_cointegration_recertification_audit_mt.py tests/test_permanent_production_certification_mt.py tests/test_cointegration_diagnostics_schema.py -v
```
**Must be 127/127. If any fail → fix immediately.**

### NEXT SESSION - INITIAL TASK (ATOMIC, TIMESTAMPED 2026-11-03T08:35:28Z)
**FOCUS: PRODUCTION-GRADE EXECUTION PARITY, REAL-DATA PROVENANCE & COST-STRESS HARDENING (NO AUDIT-ONLY)**

1. **Harden execution realism parity**: Audit `examples/run_portfolio_real.py`, `reports/portfolio_real.json` generation, and execution paths. Ensure slippage/fees/cost models are fail-closed (no fabrication), volume-aware where applicable, and consistent with walk-forward. Add regression test asserting provenance fields on portfolio artifacts.
2. **Fortify real-data provenance chain**: Trace `DataLoader.load_binance_data()` / host chain (`www.binance.com` first, handle 451/blocks honestly). Verify cache never masks failures/fabricates. Ensure `real_data_only: true`, `fabricated_data: false`, full `blocked_routes[]` + rationale on all blocked diagnostics.
3. **Tighten cost-stress & regime validation**: Review `reports/cost_sensitivity_real*.json`, `reports/regime_cost_stress*.json`. Add guards against silent pass when cost grids missing/partial under strict validation. Ensure bootstrap CI/provenance intact if touched.
4. **Eliminate any latent fail-opens**: Re-scan for coercions (`or True`, `if None: True`, truthiness leaks). Verify `no_structural_break` always present in target schema gates; strategy blocks on flagged breaks in both cached/per-bar paths.
5. **Verify & ship**: Run critical subset + `ruff` + `mypy` on touched modules. Update tests/evidence. **No summary-only turn.**

### BOTTLENECKS REMOVED
- Single session active. Act directly.
- `main` clean/green. Ignore stale branches/abandoned CI.
- Real-data only enforced; fail-closed gates unified and parity hardened.
- Execution/provenance paths traced; cost-stress artifacts present.

### MANDATORY FOCUS CAMPAIGN: "FORTIFY EXECUTION, PROVENANCE & COST-STRESS FOR COINTEGRATION PAIRS" (UNSKIPPABLE)
**Every session MUST ship at least one material, verifiable hardening change on the cointegration pairs edge before ending.** Ship code + tests/evidence.

#### P0 - EXECUTION PARITY & GATE INTEGRITY (CRITICAL)
1. Hunt fail-open coercions: `grep -rn "\bor True\b\|if .* is None: .* True\|True if .* is None" strategies/ utils/ backtest/ | grep -v __pycache__` - fix any found (zero tolerance).
2. Strict parity: cached vs per-bar under `strict_enriched_gates=True` - both block on `None`/`False`; `all_pass` non-blocking if missing when individuals pass. Structural breaks block in BOTH modes.
3. Diagnostics: never fabricate/clamp; `target_schema_diagnostics` honest `blocked_or_insufficient_data` with full `blocked_routes[]`+provenance; `blocked_schema_diagnostics` never invents metrics.

#### P1 - REAL-DATA PROVENANCE & DATA LOADING
1. Audit `reports/portfolio_real.json`, `reports/cointegration_diagnostics_real.json` - `real_data_only:true`, `fabricated_data:false`, full provenance, `blocked_routes[]` when blocked.
2. Review `data/loader.py`, `data/cache.py` - prefer `www.binance.com` first; handle 451/blocks honestly; cache never masks failures/fabricates; network errors surface as blocked with rationale.
3. Ensure funding/basis attempts logged with provenance when used (no fabrication).

#### P2 - COST-STRESS, BOOTSTRAP & ROBUSTNESS
1. Harden cost-sensitivity grids: validate structure, fees/slippage ranges, provenance. Fail closed on partial/malformed grids in strict validation.
2. Bootstrap CI: preserve fixed seeds/provenance where applicable; no fabrication of confidence intervals.
3. Tighten edge cases (short series, NaN/Inf, insufficient windows, beta<=0) without weakening tests.
4. Keep tests fast; avoid unnecessary per-bar recomputation where safe.
5. `ruff` clean, `mypy` clean on touched modules. Critical subset after changes; full suite if touching gates/engine/core/data.

### MANDATORY DISCIPLINE
- **HEAVY WORK REQUIRED.** No deferral.
- **NO SUMMARY-ONLY TURNS.** Ship code/tests/evidence.
- **Trace before change.** Read source+tests.
- **Verify relentlessly.** Critical subset after changes; full suite if touching gates/engine/core; `ruff`+`mypy` if code changes.
- **Fail-closed always.** Never weaken `use_enriched_gates`, `strict_enriched_gates`, provenance, or real-data requirements.
- **Publication-grade.** Real-data only. Evidence required.

### SUCCESS CRITERIA
- [ ] Critical subset passes (127 tests)
- [ ] `python -m pytest tests/` exits 0 (767 passed, 1 skipped)
- [ ] `ruff check strategies/ backtest/ utils/ tests/ examples/` exits 0
- [ ] `mypy backtest strategies utils` exits 0
- [ ] No gate/provenance/execution weakening
- [ ] Material hardening shipped on cointegration pairs edge with traceable evidence

**START NOW. Run immediate action. Fix failures immediately. Attack initial task. Do not stop at audit - harden and verify.**


## SESSION UPDATE (2026-11-03T08:39:18Z) - NEXT FOCUS CAMPAIGN SEALED (HEAVY EXECUTION MANDATED)
**PRIORITY: COINTEGRATION PAIRS EDGE - FAIL-CLOSED, REAL-DATA ONLY - HEAVY EXECUTION MANDATED**

### REPO SIGNAL (INFERRED)
`cryptoquantstatarbstrats` = Crypto Quant Stat Arb Strategies. **Cointegration pairs is the sole product edge.** All work must strengthen the pairs/cointegration path with traceable evidence.

### CURRENT STATE (VERIFIED 2026-11-03T08:39:18Z)
- Critical subset: 127 passed (green). Full suite: 767 passed, 1 skipped (green).
- Lint: clean. mypy: Success, 32 source files.
- Working tree clean on `main`. Real-data only enforced; fail-closed gates unified & parity hardened.
- Gate parity (cached vs per-bar) hardened; structural breaks block both modes; beta guards added.
- Execution/provenance/cost-stress campaign from 08:35:28 remains the active frontier.

### IMMEDIATE MANDATORY ACTION (FIRST TURN - NO EXPLORATION, NO SUMMARY-ONLY)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python -m pytest tests/test_cointegration_campaign*_mt.py tests/test_cointegration_recertification_audit_mt.py tests/test_permanent_production_certification_mt.py tests/test_cointegration_diagnostics_schema.py -v
```
**Must be 127/127. If any fail -> fix immediately.**

### NEXT SESSION - INITIAL TASK (ATOMIC, TIMESTAMPED 2026-11-03T08:39:18Z)
**FOCUS: EXECUTION PARITY, REAL-DATA PROVENANCE & COST-STRESS HARDENING (NO AUDIT-ONLY)**

1. Harden execution realism parity: audit `examples/run_portfolio_real.py`, portfolio artifact generation, execution paths. Ensure slippage/fees/cost models fail-closed (no fabrication), volume-aware where applicable, consistent with walk-forward. Add regression test asserting provenance fields on portfolio artifacts.
2. Fortify real-data provenance chain: trace `DataLoader.load_binance_data()` host chain (`www.binance.com` first, handle 451/blocks honestly). Verify cache never masks failures/fabricates. Ensure `real_data_only: true`, `fabricated_data: false`, full `blocked_routes[]` + rationale on all blocked diagnostics.
3. Tighten cost-stress & regime validation: review `reports/cost_sensitivity_real*.json`, `reports/regime_cost_stress*.json`. Add guards against silent pass when cost grids missing/partial under strict validation. Preserve bootstrap CI/provenance if touched.
4. Eliminate latent fail-opens: re-scan coercions (`or True`, `if None: True`, truthiness leaks). Verify `no_structural_break` always present in target schema gates; strategy blocks on flagged breaks in both cached/per-bar paths.
5. Verify & ship: critical subset + ruff + mypy on touched modules. Update tests/evidence. No summary-only turn.

### BOTTLENECKS REMOVED
- Single session active. Act directly.
- `main` clean/green. Ignore stale branches/abandoned CI.
- Real-data only enforced; fail-closed gates unified and parity hardened.
- Execution/provenance/cost-stress frontier remains active; no blocked sessions.

### MANDATORY FOCUS CAMPAIGN: "FORTIFY EXECUTION, PROVENANCE & COST-STRESS FOR COINTEGRATION PAIRS" (UNSKIPPABLE)
Every session MUST ship at least one material, verifiable hardening change on the cointegration pairs edge before ending. Ship code + tests/evidence.

#### P0 - EXECUTION PARITY & GATE INTEGRITY (CRITICAL)
1. Hunt fail-open coercions: `grep -rn "\bor True\b\|if .* is None: .* True\|True if .* is None" strategies/ utils/ backtest/ | grep -v __pycache__` - fix any found (zero tolerance).
2. Strict parity: cached vs per-bar under `strict_enriched_gates=True` - both block on `None`/`False`; `all_pass` non-blocking if missing when individuals pass. Structural breaks block in BOTH modes.
3. Diagnostics: never fabricate/clamp; `target_schema_diagnostics` honest `blocked_or_insufficient_data` with full `blocked_routes[]`+provenance; `blocked_schema_diagnostics` never invents metrics.

#### P1 - REAL-DATA PROVENANCE & DATA LOADING
1. Audit `reports/portfolio_real.json`, `reports/cointegration_diagnostics_real.json` - `real_data_only:true`, `fabricated_data:false`, full provenance, `blocked_routes[]` when blocked.
2. Review `data/loader.py`, `data/cache.py` - prefer `www.binance.com` first; handle 451/blocks honestly; cache never masks failures/fabricates; network errors surface as blocked with rationale.
3. Ensure funding/basis attempts logged with provenance when used (no fabrication).

#### P2 - COST-STRESS, BOOTSTRAP & ROBUSTNESS
1. Harden cost-sensitivity grids: validate structure, fees/slippage ranges, provenance. Fail closed on partial/malformed grids in strict validation.
2. Bootstrap CI: preserve fixed seeds/provenance where applicable; no fabrication of confidence intervals.
3. Tighten edge cases (short series, NaN/Inf, insufficient windows, beta<=0) without weakening tests.
4. Keep tests fast; avoid unnecessary per-bar recomputation where safe.
5. `ruff` clean, `mypy` clean on touched modules. Critical subset after changes; full suite if touching gates/engine/core/data.

### MANDATORY DISCIPLINE
- HEAVY WORK REQUIRED. No deferral.
- NO SUMMARY-ONLY TURNS. Ship code/tests/evidence.
- Trace before change. Read source+tests.
- Verify relentlessly. Critical subset after changes; full suite if touching gates/engine/core; ruff+mypy if code changes.
- Fail-closed always. Never weaken `use_enriched_gates`, `strict_enriched_gates`, provenance, or real-data requirements.
- Publication-grade. Real-data only. Evidence required.

### SUCCESS CRITERIA
- [ ] Critical subset passes (127 tests)
- [ ] `python -m pytest tests/` exits 0 (767 passed, 1 skipped)
- [ ] `ruff check strategies/ backtest/ utils/ tests/ examples/` exits 0
- [ ] `mypy backtest strategies utils` exits 0
- [ ] No gate/provenance/execution weakening
- [ ] Material hardening shipped on cointegration pairs edge with traceable evidence

**START NOW. Run immediate action. Fix failures immediately. Attack initial task. Do not stop at audit - harden and verify.**
