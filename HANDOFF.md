# DURABLE HANDOFF (2026-10-30T17:00:43Z) — SINGLE MANDATORY NEXT TASK: MAXIMUM REAL-DATA HEAVY VALIDATION

## REPO NAME IS THE LAW
- **REPO:** `cryptoquantstatarbstrats` — *Crypto Quant Stat Arb Strategies*
- **ABSOLUTE MANDATE:** This codebase exists SOLELY to research, build, harden, and relentlessly validate crypto statistical-arbitrage strategies using **ONLY REAL market data**.
- **NON-NEGOTIABLE PRIORITY:** Real-data validation > everything else. If torn between convenience and heavier real-data work, **ALWAYS choose the heavier path**. Coasting is FORBIDDEN.
- **IMPOSSIBLE TO AVOID:** Every session must produce measurable increases in real-data validation rigor. No exploratory toy work. No synthetic shortcuts.

## VERIFIED GREEN STATE (MUST PRESERVE) — 2026-10-30T17:00:43Z
- **Branch:** `main` (clean)
- **Tests:** `PYTHONPATH=. python -m pytest tests/ -q` → **527 passed, 1 skipped**
- **Lint:** `python -m ruff check backtest/ strategies/ utils/ tests/` → **All checks passed**
- **Types:** `python -m mypy backtest/ strategies/ utils/` → **Success: no issues found in 31 source files**
- **Real data:** `DataLoader.load_binance_data()` uses public Binance REST (real spot candles only). **NEVER fabricate candles/IV/funding/basis.**
- **Key artifacts:** `examples/run_portfolio_real.py`, `reports/portfolio_real.json`, `tests/test_portfolio_real.py`, `tests/test_portfolio_risk_controls.py`

## BOTTLENECK ELIMINATION (MANDATORY IMMEDIATE ACTION)
- **OBSERVABILITY:** All long real-data jobs MUST use unbuffered output (`python -u`). Add explicit progress.
- **KILL FRICTION:** If any code path is slow/redundant/unclear, **ELIMINATE IT NOW**. Tighten schemas, harden tests, improve clarity.
- **FORCE HEAVY WORK:** Structure tasks so future agents cannot take shortcuts. Remove affordances for "quick" runs.
- **PARALLELIZE WHERE SAFE:** For independent pair sweeps/fetches, batch where network-safe and deterministic. Don't duplicate work.
- **NO WORKAROUNDS:** Omit+document only after EXHAUSTIVE attempts with full provenance.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (TIMESTAMP: 2026-10-30T17:00:43Z)

**OBJECTIVE:** Execute a **MAXIMUM-INTENSITY NO-COAST HARDENING CAMPAIGN** on the multi-asset crypto stat arb portfolio using **100% REAL Binance data**. Make it IMPOSSIBLE for subsequent agents to avoid substantial real-data validation.

### MANDATORY SEQUENCE (DO IN ORDER, NO SKIPPING)
1. **BRUTALLY HONEST AUDIT**
   - Read: `examples/run_portfolio_real.py`, `reports/portfolio_real.json`, `tests/test_portfolio_real.py`, `tests/test_portfolio_risk_controls.py`, `backtest/engine.py` (focus `walk_forward_portfolio` + `run_portfolio`), `utils/portfolio_risk.py`, `utils/regime.py`, `data/loader.py`
   - Fix EVERY bottleneck on contact. Document findings.

2. **VERIFY GREEN (NON-NEGOTIABLE)**
   - `PYTHONPATH=. python -m pytest tests/ -q`
   - `python -m ruff check backtest/ strategies/ utils/ tests/`
   - `python -m mypy backtest/ strategies/ utils/`
   - If ANY regression → restore green BEFORE proceeding.

3. **REGENERATE FROM REAL DATA**
   - `python -u examples/run_portfolio_real.py` end-to-end on real Binance candles with **>= 12 walk-forward splits**
   - Verify `reports/portfolio_real.json` written, JSON-valid, `tests/test_portfolio_real.py` passes
   - Confirm n_splits>=10, per-asset gross <= correlation cap, circuit breaker tested, risk_controller is `correlation_aware_cvar_style`

4. **UNIVERSE EXPANSION (REAL-ONLY)**
   - Aggressively attempt additional real pairs (BNB/USDT-quoted + liquid majors: DOT/MATIC/AVAX/LINK/ADA/XRP/SOL etc.) via **ONLY** `DataLoader.load_binance_data()`
   - Include only pairs with sufficient overlapping real history. **Explicitly list EVERY omission with rationale. NEVER fabricate.**

5. **WALK-FORWARD RIGOR (>=12 SPLITS)**
   - Enforce >=12 splits with train≈1000/test≈200 where feasible
   - Capture full IS/OOS per split, stability metrics, degradation curves, regime-split performance
   - Make everything inspectable in artifact

6. **META-SELECTOR + RISK CONTROLS (HARDEN)**
   - Strengthen regime-adaptive multi-signal meta-selector using multiple real signals (vol/trend/mean-reversion) from real data; validate OOS
   - Harden correlation-aware + CVaR-aware limits; enforce hard caps (per-asset gross <= correlation cap). Thoroughly test circuit breaker on real history

7. **FUNDING/BASIS (EXHAUSTIVE, NO FABRICATION)**
   - Attempt real public Binance funding/basis from multiple public endpoints/hosts with full attempt timestamps/hosts/errors
   - If retrievable and sensible → integrate with provenance; else **comprehensively document**. **NEVER fabricate.**

8. **EXECUTION REALISM**
   - Add volume-aware/slippage/cost realism using real characteristics where possible; document assumptions explicitly

9. **ARTIFACT ENRICHMENT (COMPLETE)**
   - Enrich `reports/portfolio_real.json` with: per-asset contribution, turnover, leverage/gross/net exposure, correlation matrix + correlation stability, tail metrics (VaR/CVaR/CDaR), regime-conditioned performance, cost-stress slices, funding/basis provenance (full attempts), universe changes + exclusions with rationale, walk-forward IS/OOS per split + stability/degradation
   - JSON-serializable, schema-valid, backward compatible or tests updated

10. **TESTS + DOCS (HARDEN)**
   - Add **network-independent** stress tests for portfolio logic, risk controls, meta-selector, artifact schema, edge cases
   - Update `README.md` with hardened findings, **concrete real-data numbers**, explicit **real-data-only provenance**, coverage summary. Make real-data mandate impossible to miss

11. **VERIFY & DELIVER (ZERO REGRESSIONS)**
   - Regenerate artifact with **real data only**
   - `PYTHONPATH=. python -m pytest tests/ -q` (>=527 passed, 0 new failures)
   - `python -m ruff check backtest/ strategies/ utils/ tests/` (clean)
   - `python -m mypy backtest/ strategies/ utils/` (clean)
   - All deliverables present and valid

### HARD CONSTRAINTS
- **REAL DATA ONLY** - No synthetic/fabricated data
- **NO SHORTCUTS** - Omit+document if unavailable after exhaustive attempts
- **PRESERVE GREEN** - Zero regressions
- **HEAVY MANDATE** - Substantial work required; complete full campaign
- **BOTTLENECK REMOVAL** - Eliminate inefficiencies immediately
- **IMPOSSIBLE TO COAST** - Structure so future agents cannot avoid heavy validation

**CAMPAIGN COMPLETE ONLY WHEN ALL CRITERIA MET. START IMMEDIATELY. EXECUTE WITHOUT EARLY STOP.**
