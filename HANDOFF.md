# DURABLE HANDOFF | TIMESTAMP: 2026-11-03T05:33:00Z | REPO: cryptoquantstatarbstrats
# PRIORITY: COINTEGRATION PAIRS EDGE - FAIL-CLOSED, REAL-DATA ONLY

## REPO SIGNAL (INFERRED)
`cryptoquantstatarbstrats` = Crypto Quant Stat Arb Strategies. **Cointegration pairs is the product edge.**
Treat this as publication-grade research code: fabrication is unacceptable. Everything else supports/gates/validates pairs.

## GROUND TRUTH (VERIFIED 2026-11-03T05:33:00Z)
- Critical subset (cointegration campaigns/recertification/permanent cert/schema): **125 passed**
- Full suite: **767 passed, 1 skipped** (`python -m pytest tests/`)
- Lint: `python -m ruff check strategies/ backtest/ utils/ tests/ examples/` → **All checks passed**
- mypy: `python -m mypy backtest strategies utils` → **Success: no issues found in 32 source files**
- Working tree clean. Network: `www.binance.com` serves public klines; `api.binance.com` returns 451 and is handled honestly.
- Artifacts: `reports/portfolio_real.json`, `reports/cointegration_diagnostics_real.json` have `real_data_only: true`, `fabricated_data: false`, full provenance with `blocked_routes[]` when blocked.
- Gate-key reconciliation: `strategies/pairs_trading.py` only blocks on explicit `False` for individual gates; missing `all_pass` does not fail if the six individual gates pass. Cached (`enriched_diagnostics`) and per-bar paths are unified and fail-closed under `strict_enriched_gates=True`.
- No `or True` fail-open coercions found in `strategies/` or `utils/`.

## INITIAL TASK (DO THIS ON FIRST TURN - NO DEEP EXPLORATION)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python -m pytest tests/test_cointegration_campaign*_mt.py tests/test_cointegration_recertification_audit_mt.py tests/test_permanent_production_certification_mt.py tests/test_cointegration_diagnostics_schema.py -v
```
**If ANY test fails, fix it before anything else.** All must pass.

## BOTTLENECKS REMOVED
- Single session active - no cross-session blocking. Act directly.
- `main` is green; no stale CI branch to chase.
- Real-data paths operational (www.binance.com first; 451 handled honestly).
- Gate reconciliation already applied - no ambiguity blocking entries.
- Analysis paralysis discouraged: trace → harden → verify with tests. No "audit only" turns.

## NEXT FOCUS CAMPAIGN (HEAVY WORK - DO NOT AVOID)
**Campaign: "FORTIFY & STRESS-TEST COINTEGRATION GATES"**

### P0 - Gate Integrity (CRITICAL)
1. **Hunt fail-open coercions**: `grep -rn "or True\|if .* is None: .* True\|True if .* is None" strategies/ utils/ | grep -v __pycache__` - fix any found (fail-closed only).
2. **Trace strict path end-to-end**: Verify every gate in `strategies/pairs_trading.py` blocks on `None`/`False` under `strict_enriched_gates=True`. Compare cached vs per-bar paths for parity.
3. **Harden diagnostics**: In `utils/cointegration.py`, never fabricate values, never clamp half-life/metrics to pass gates. `blocked_or_insufficient_data` must be used honestly with `blocked_routes[]` and full provenance.

### P1 - Real-Data Provenance (CRITICAL)
1. **Audit artifacts**: Spot-check `reports/portfolio_real.json` and `reports/cointegration_diagnostics_real.json` - `real_data_only: true`, `fabricated_data: false`, full provenance, `blocked_routes[]` when blocked.
2. **Harden loader/cache**: Review `data/loader.py`, `data/cache.py`. Prefer `www.binance.com` first; on 451/blocks write honest `blocked_or_insufficient_data` with rationale - **never fabricate**. Cache must not mask failures.

### P2 - Stress & Regression Guards (HIGH)
1. **Strengthen guards** if gaps found without weakening existing tests.
2. **Keep tests fast**; avoid per-bar recomputation where possible.
3. **Quality gates**: `ruff` clean, `mypy` clean on any touched modules. Run critical subset after changes; full suite if touching gates/engine/core.

## MANDATORY DISCIPLINE
- **NO SUMMARY-ONLY TURNS.** Every turn must fix/harden/verify something material on pairs/cointegration.
- **Trace before change.** Read source + relevant tests. Understand causality.
- **Verify relentlessly.** Critical subset after changes; full suite if touching gates/engine/core; always `ruff` + `mypy` if code changes.
- **Fail-closed always.** Never weaken `use_enriched_gates`, `strict_enriched_gates`, or provenance requirements.
- **Publication-grade.** Real-data only. Evidence required.

## SUCCESS CRITERIA
- [ ] Critical subset passes (125 tests)
- [ ] `python -m pytest tests/` exits 0 (767 passed, 1 skipped)
- [ ] `ruff check strategies/ backtest/ utils/ tests/ examples/` exits 0
- [ ] `mypy backtest strategies utils` exits 0
- [ ] No gate/provenance weakening
- [ ] Any changes verified with traceable evidence

**START NOW. Run the initial task above. Then do P0 item 1 (search for fail-open coercions). Heavy work required.**
