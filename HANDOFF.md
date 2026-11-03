# DURABLE HANDOFF | TIMESTAMP: 2026-11-03T03:07:35Z | REPO: cryptoquantstatarbstrats

## PRIMARY OBJECTIVE (NON-NEGOTIABLE)
**KEEP THE COINTEGRATION PAIRS STRATEGY PRODUCTION-READY, REGRESSION-FREE, AND REAL-DATA ONLY.**

Repo `cryptoquantstatarbstrats` = Crypto Quant Stat Arb Strategies. The cointegration/stat-arb edge IS the product. Everything else supports, gates, or validates it. Pairs path is fail-closed (`use_enriched_gates=True`, `strict_enriched_gates=True`). No fabricated diagnostics, no synthetic evidence of real-market performance. `real_data_only` + full provenance is mandatory.

## CURRENT STATE SNAPSHOT (GROUND TRUTH - VERIFIED 2026-11-03T03:07:35Z)
- Full test suite: **765 passed, 1 skipped** - all green (`python -m pytest tests/`), exits 0 (~4 min)
- Critical gating: cointegration campaign tests 29-38 + loader, recertification audit, permanent production certification, all `_mt` gating/signoff/live-deployment bridge tests - **ALL PASS**
- Cointegration diagnostics schema (real_data_only, 17 pairs, full provenance, blocked_routes) - **ALL PASS**
- **Lint:** `python -m ruff check strategies/ backtest/ utils/ tests/ examples/` exits 0 ("All checks passed!")
- **mypy:** `python -m mypy backtest strategies utils` exits 0 ("Success: no issues found in 32 source files")
- Warnings only (non-failing): statsmodels FutureWarnings/ComplexWarning/CollinearityWarning/InterpolationWarning, pandas freq deprecation
- **Working tree clean** - no uncommitted changes
- Recent history: mostly checkpoint commits; **do not checkpoint on red - fix until green, then commit with purpose**

## IMMEDIATE MANDATE FOR NEXT AGENT (HEAVY WORK, NO EXPLORATION-ONLY)
**You MUST make substantive progress on the pairs/cointegration path.** Do not stop at reading. Every turn must fix, harden, or verify something material. Gates are fail-closed - never weaken them.

### Required verification (run first, must pass)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python -m pytest tests/test_cointegration_campaign*_mt.py tests/test_cointegration_recertification_audit_mt.py tests/test_permanent_production_certification_mt.py tests/test_cointegration_diagnostics_schema.py -v
```
If ANY of these fail -> fix immediately. Then run full suite.

### Campaign: "FORTIFY PAIRS GATES & REAL-DATA PROVENANCE"
Focus on hardening the cointegration edge with zero regressions.

#### Priority 1: Enforce causal, fail-closed gate integrity (CRITICAL)
- **Read & trace:** `strategies/pairs_trading.py` (defaults `use_enriched_gates=True`, `strict_enriched_gates=True`), `utils/cointegration.py` (EG/Johansen, spread MR, half-life bounds 1<hl<500, rolling stability, breaks, leg stationarity), `backtest/engine.py` (causal application).
- **Harden:** Ensure missing/None/False enriched gate values block entries under strict mode. No fallthrough to permissive defaults. Verify trailing-only data usage.
- **Verify:** All campaign/gating tests pass. No synthetic evidence injected into real-data paths.

#### Priority 2: Real-data provenance & diagnostics (CRITICAL)
- **Audit:** `reports/portfolio_real.json`, `reports/cointegration_diagnostics_real.json` - must show `real_data_only: true`, `fabricated_data: false`, full provenance, `blocked_routes` when applicable.
- **Harden loader:** `data/loader.py`, `data/cache.py`, `data/__init__.py` - keep `data.cache` import unambiguous (mypy/namespace). Network handling: prefer `www.binance.com` for public spot; never rely on api.binance.com returning data (451 possible). When reconstruction blocked -> honest `blocked_or_insufficient_data` with rationale, never fabricate.
- **Verify:** `tests/test_cointegration_diagnostics_schema.py` passes.

#### Priority 3: Regression guards & bottleneck prevention (HIGH)
- **Keep fast:** Cost-sensitivity tests must stay fast (already optimized). Don't reintroduce per-bar recomputation.
- **Lint/mypy:** Maintain `ruff` 0 errors, `mypy backtest strategies utils` 0 errors. Fix issues by reflowing/refactoring, never by weakening types/gates.
- **Systematic fixes:** If pattern repeats across files, fix all at once.

#### Priority 4: Heavy-work discipline (MANDATORY)
- **Do not checkpoint on exploration.** Only commit after closing a concrete failure or clearing measurable debt with verification.
- **Trace, don't guess.** Read source before changing. Understand schemas and causality.
- **Verify before committing:** Run critical subset + `ruff check` + `mypy backtest strategies utils`. Full suite if touching gates/engine/strategy core.
- **Publication-grade:** Treat as if results will be published. No fabrication. Evidence required.

## SUCCESS CRITERIA (MUST MEET BEFORE STOPPING)
- [ ] Critical subset passes: `tests/test_cointegration_campaign*_mt.py tests/test_cointegration_recertification_audit_mt.py tests/test_permanent_production_certification_mt.py tests/test_cointegration_diagnostics_schema.py`
- [ ] `python -m pytest tests/` exits 0 (765 passed, 1 skipped; no new failures/skips)
- [ ] `python -m ruff check strategies/ backtest/ utils/ tests/ examples/` exits 0
- [ ] `python -m mypy backtest strategies utils` exits 0
- [ ] No weakening of `use_enriched_gates`/`strict_enriched_gates` or `real_data_only` provenance
- [ ] Any fix is backed by traceable evidence from source/tests
- [ ] If commit made, it closes a real issue (no "checkpoint agent session" style unless justified by completed milestone)

## FILES MOST LIKELY TO NEED ATTENTION
- `strategies/pairs_trading.py` - pairs entry, gate defaults, fail-closed logic
- `utils/cointegration.py` - EG/Johansen, spread MR, half-life, stability/breaks, gate computation
- `backtest/engine.py` - causal application of gates/weights
- `data/loader.py`, `data/cache.py`, `data/__init__.py` - provenance, cache namespace, network
- `tests/test_cointegration_*_mt.py` - regression guards (treat as non-optional)
- `reports/portfolio_real.json`, `reports/cointegration_diagnostics_real.json` - provenance artifacts

**START NOW.** Run the critical subset first. If green, immediately look for hardenings: trace gate paths for any missing coverage, ensure strict mode blocks all None/False, verify real-data provenance in artifacts, and keep all gates tight. Do heavy work - no summary-only turn.

(End of file - total 71 lines)
