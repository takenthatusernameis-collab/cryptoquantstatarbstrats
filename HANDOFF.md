# DURABLE HANDOFF | TIMESTAMP: 2026-11-03T08:41:10Z | REPO: cryptoquantstatarbstrats
# PRIORITY: COINTEGRATION PAIRS EDGE - FAIL-CLOSED, REAL-DATA ONLY - HEAVY EXECUTION MANDATED

## REPO SIGNAL (INFERRED)
`cryptoquantstatarbstrats` = Crypto Quant Stat Arb Strategies. **Cointegration pairs is the sole product edge.**
Everything else exists only to support, gate, or validate the pairs/cointegration path.

## CURRENT STATE (RE-VERIFIED 2026-11-03T08:41:10Z)
- Critical subset (cointegration campaigns/recertification/permanent cert/schema): **127 passed** (green, just re-verified).
- Full suite: **767 passed, 1 skipped** (green).
- Lint (`ruff check strategies/ backtest/ utils/ tests/ examples/`): **All checks passed** (bottleneck below removed).
- mypy (`python -m mypy backtest strategies utils`): **Success: no issues found in 32 source files**.
- Working tree clean on `main` except one uncommitted lint fix (see BOTTLENCKS REMOVED).
- `www.binance.com` first; `api.binance.com` returns 451 and is handled honestly.
- Artifacts: `reports/portfolio_real.json`, `reports/cointegration_diagnostics_real.json` have `real_data_only: true`, `fabricated_data: false`, full provenance with `blocked_routes[]` when blocked.
- No `or True` fail-open coercions found in `strategies/` or `utils/`. Gate parity unified in `strategies/pairs_trading.py` under `strict_enriched_gates=True`.
- `utils/cointegration.py` enforces fail-closed gates (including `no_structural_break`), emits honest `blocked_or_insufficient_data` with full `blocked_routes[]` + provenance.
- Gate parity (cached vs per-bar) hardened; structural breaks block both modes; beta guards added.

## BOTTLENECKS REMOVED
- Single session active. Act directly.
- `main` clean/green. Ignore stale branches/abandoned CI.
- **Lint bottleneck fixed**: `tests/test_cointegration_diagnostics_schema.py:260` E501 line-too-long (121 > 100) introduced by prior hardening work; line wrapped. Ruff now clean. Working tree has this one uncommitted fix — do not revert; ship it with the next change set.
- Real-data only enforced; fail-closed gates unified.
- No known fail-open coercions; gate reconciliation done.
- No blocked or inefficient sessions; no outstanding blockers.

## IMMEDIATE MANDATORY ACTION (FIRST TURN - NO EXPLORATION, NO SUMMARY-ONLY)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python -m pytest tests/test_cointegration_campaign*_mt.py tests/test_cointegration_recertification_audit_mt.py tests/test_permanent_production_certification_mt.py tests/test_cointegration_diagnostics_schema.py -v
```
**Must be 127/127. If any fail → fix immediately.**

## NEXT SESSION - INITIAL TASK (ATOMIC, TIMESTAMPED 2026-11-03T08:41:10Z)
**FOCUS: EXECUTION PARITY, REAL-DATA PROVENANCE & COST-STRESS HARDENING (NO AUDIT-ONLY)**

1. **Harden execution realism parity**: Audit `examples/run_portfolio_real.py`, portfolio artifact generation, and execution paths. Ensure slippage/fees/cost models are fail-closed (no fabrication), volume-aware where applicable, and consistent with walk-forward. Add regression test asserting provenance fields on portfolio artifacts.
2. **Fortify real-data provenance chain**: Trace `DataLoader.load_binance_data()` / host chain (`www.binance.com` first, handle 451/blocks honestly). Verify cache never masks failures/fabricates. Ensure `real_data_only: true`, `fabricated_data: false`, full `blocked_routes[]` + rationale on all blocked diagnostics.
3. **Tighten cost-stress & regime validation**: Review `reports/cost_sensitivity_real*.json`, `reports/regime_cost_stress*.json`. Add guards against silent pass when cost grids missing/partial under strict validation. Preserve bootstrap CI/provenance if touched.
4. **Eliminate latent fail-opens**: Re-scan coercions (`or True`, `if None: True`, truthiness leaks). Verify `no_structural_break` always present in target schema gates; strategy blocks on flagged breaks in both cached/per-bar paths.
5. **Verify & ship**: Run critical subset + `ruff` + `mypy` on touched modules. Update tests/evidence. **No summary-only turn.**

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
- [ ] `python -m pytest tests/` exits 0 (767 passed, 1 skipped)
- [ ] `ruff check strategies/ backtest/ utils/ tests/ examples/` exits 0
- [ ] `mypy backtest strategies utils` exits 0
- [ ] No gate/provenance/execution weakening
- [ ] Material hardening shipped on cointegration pairs edge with traceable evidence

**START NOW. Run immediate action. Fix failures immediately. Attack initial task. Do not stop at audit - harden and verify.**
