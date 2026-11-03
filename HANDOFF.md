# DURABLE HANDOFF | TIMESTAMP: 2026-11-03T07:35:30Z | REPO: cryptoquantstatarbstrats
# PRIORITY: COINTEGRATION PAIRS EDGE - FAIL-CLOSED, REAL-DATA ONLY - HEAVY EXECUTION MANDATED

## REPO SIGNAL (INFERRED)
`cryptoquantstatarbstrats` = Crypto Quant Stat Arb Strategies. **Cointegration pairs is the sole product edge.**
This is publication-grade research code. Fabrication is categorically unacceptable. Everything else must exist only to support, gate, or validate the pairs/cointegration path.

## GROUND TRUTH (RE-VERIFIED 2026-11-03T06:06:42Z)
- Critical subset (cointegration campaigns/recertification/permanent cert/schema): **125 passed** — verified this session (2026-11-03T06:06:42Z).
- Full suite: **767 passed, 1 skipped** (verified 2026-11-03T05:35:28Z; tree clean on `main`).
- Lint: `python -m ruff check strategies/ backtest/ utils/ tests/ examples/` → **All checks passed**.
- mypy: `python -m mypy backtest strategies utils` → **Success: no issues found in 32 source files** (mypy 1.8 target). Do not weaken gates/provenance.
- Working tree clean. On `main`. `www.binance.com` first; `api.binance.com` returns 451 and is handled honestly.
- Artifacts: `reports/portfolio_real.json`, `reports/cointegration_diagnostics_real.json` have `real_data_only: true`, `fabricated_data: false`, full provenance with `blocked_routes[]` when blocked.
- Gate reconciliation: `strategies/pairs_trading.py` blocks only on explicit `False`; missing `all_pass` does not fail if individual gates pass. Cached (`enriched_diagnostics`) and per-bar paths unified and fail-closed under `strict_enriched_gates=True`.
- No `or True` fail-open coercions found in `strategies/` or `utils/`.

## IMMEDIATE MANDATORY ACTION (FIRST TURN - NO EXPLORATION, NO SUMMARY-ONLY)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python -m pytest tests/test_cointegration_campaign*_mt.py tests/test_cointegration_recertification_audit_mt.py tests/test_permanent_production_certification_mt.py tests/test_cointegration_diagnostics_schema.py -v
```
**If ANY test fails → FIX IT IMMEDIATELY. All 125 must pass. Then proceed to P0 without delay.**

## NEXT SESSION - INITIAL TASK (ATOMIC, TIMESTAMPED 2026-11-03T06:06:42Z)
1. Run the IMMEDIATE MANDATORY ACTION above. Confirm 125/125 pass.
2. Execute **P0 - GATE INTEGRITY**: hunt `or True` / fail-open coercions in `strategies/` and `utils/` (`grep -rn "\bor True\b\|if .* is None: .* True\|True if .* is None" strategies/ utils/ | grep -v __pycache__`); fix any found with zero tolerance.
3. Verify strict path parity in `strategies/pairs_trading.py` under `strict_enriched_gates=True` for both cached (`enriched_diagnostics`) and per-bar paths: both must block on `None`/`False`; `all_pass` must remain non-blocking when missing if individuals pass.
4. Harden `utils/cointegration.py` diagnostics: never fabricate/clamp values; `target_schema_diagnostics` emits honest `blocked_or_insufficient_data` with full `blocked_routes[]` + provenance; `blocked_schema_diagnostics` never invents metrics.
5. Ship at least one material, verifiable gate-hardening/validation change on the cointegration pairs edge (code + tests/evidence) before ending. Run `ruff` + `mypy` on touched modules; re-run critical subset.


## BOTTLENECKS REMOVED / DISCARDED
- Single session active. Act directly.
- `main` green, clean tree, no stashes.
- Ignore stale remote branches (`origin/fix/noncompounding-overlap-pair-caps-20261030`, `origin/pr2branch`). Ignore abandoned CI from `fix/causal-pairs-validation-2026-10-27`. Do not chase dead PRs/branches.
- Real-data paths operational. Fail closed on missing data; never fabricate.
- Gate reconciliation resolved. No ambiguity.
- **NO "audit only" turns. NO summary-only turns. Trace → harden → verify.**

## MANDATORY FOCUS CAMPAIGN: "FORTIFY, STRESS-TEST & HARDEN COINTEGRATION GATES" (UNSKIPPABLE)
**Every session MUST ship at least one material, verifiable gate-hardening/validation change on the cointegration pairs edge before ending.** Ship code + tests/evidence. Do not just report.

### P0 - GATE INTEGRITY (CRITICAL - BLOCKS EVERYTHING)
1. **Hunt fail-open coercions**: `grep -rn "\bor True\b\|if .* is None: .* True\|True if .* is None" strategies/ utils/ | grep -v __pycache__` - fix any found. Zero tolerance.
2. **Strict path parity**: End-to-end verify `strategies/pairs_trading.py` gates under `strict_enriched_gates=True` for cached (`enriched_diagnostics`) and per-bar paths. Both must block on `None`/`False`. `all_pass` must remain non-blocking if missing when individuals pass. No weakening.
3. **Diagnostics hardening**: In `utils/cointegration.py`, never fabricate/clamp values to pass gates. `target_schema_diagnostics` must emit honest `blocked_or_insufficient_data` with full `blocked_routes[]` and provenance. `blocked_schema_diagnostics` must never invent metrics.

### P1 - REAL-DATA PROVENANCE (CRITICAL)
1. **Artifact audit**: Spot-check `reports/portfolio_real.json` and `reports/cointegration_diagnostics_real.json` - `real_data_only: true`, `fabricated_data: false`, full provenance, `blocked_routes[]` present when blocked.
2. **Loader/cache hardening**: Review `data/loader.py`, `data/cache.py`. Prefer `www.binance.com` first; handle 451/blocks honestly with rationale. Cache must never mask failures or fabricate series.

### P2 - STRESS, REGRESSION GUARDS & ROBUSTNESS (HIGH)
1. **Tighten edge cases**: Add/strengthen guards for short series, NaN/Inf, insufficient windows (rolling stability), beta<=0, etc. without weakening existing tests.
2. **Performance**: Keep tests fast; avoid unnecessary per-bar recomputation where safe.
3. **Quality gates**: `ruff` clean, `mypy` clean on any touched modules. Run critical subset after changes; full suite if touching gates/engine/core.

## MANDATORY DISCIPLINE
- **HEAVY WORK REQUIRED.** Do not defer. Every turn must move the cointegration edge forward materially.
- **NO SUMMARY-ONLY TURNS.** Ship code, tests, or hardening. Status reports alone are insufficient.
- **Trace before change.** Read source + relevant tests to understand causality.
- **Verify relentlessly.** Critical subset after changes; full suite if touching gates/engine/core; always `ruff` + `mypy` if code changes.
- **Fail-closed always.** Never weaken `use_enriched_gates`, `strict_enriched_gates`, provenance, or real-data requirements.
- **Publication-grade.** Real-data only. Evidence required.

## SUCCESS CRITERIA
- [ ] Critical subset passes (125 tests)
- [ ] `python -m pytest tests/` exits 0 (767 passed, 1 skipped)
- [ ] `ruff check strategies/ backtest/ utils/ tests/ examples/` exits 0
- [ ] `mypy backtest strategies utils` exits 0
- [ ] No gate/provenance weakening
- [ ] Material hardening shipped on cointegration pairs edge with traceable evidence

**START NOW. Run the initial task. Fix failures immediately. Attack P0. Do not stop at audit - harden and verify.**
