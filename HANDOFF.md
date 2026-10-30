# DURABLE HANDOFF (2026-10-30T16:56:15Z) — SINGLE MANDATORY NEXT TASK: CRYPTOQUANTSTATARBSTRATS MAXIMUM REAL-DATA HEAVY VALIDATION

## REPO NAME PRIORITIZATION (ABSOLUTE)
- **REPO:** `cryptoquantstatarbstrats` — *Crypto Quant Stat Arb Strategies*
- **INFERRED MANDATE (NON-NEGOTIABLE):** This repository exists to build, harden, and relentlessly validate crypto statistical-arbitrage strategies using **ONLY REAL market data**. Every subsequent agentic session MUST treat real-data validation as the primary objective with no dilution.
- **PRIORITY DIRECTIVE:** The repository name IS the law. If there is any ambiguity between convenience and heavier real-data work, ALWAYS choose the heavier real-data path. Coasting is categorically forbidden. Heavy validation must never cease.

## VERIFIED GREEN STATE (PRESERVE AT ALL COSTS) — re-confirmed 2026-10-30T16:56:15Z
- **Branch:** `main` (clean working tree)
- **Tests:** `PYTHONPATH=. python -m pytest tests/ -q` → **527 passed, 1 skipped**
- **Lint (authoritative scope):** `python -m ruff check backtest/ strategies/ utils/ tests/` → **All checks passed**
- **Types:** `python -m mypy backtest/ strategies/ utils/` → **Success: no issues found in 31 source files**
- **Data access:** Public Binance reachable via `DataLoader.load_binance_data()` (real candles only) — **REAL DATA ONLY. NEVER FABRICATE CANDLES, IV, FUNDING, OR BASIS.**
- **Key deliverables:** `examples/run_portfolio_real.py`, `reports/portfolio_real.json`, `tests/test_portfolio_real.py`, `tests/test_portfolio_risk_controls.py`

## BOTTLENECK ELIMINATION (MANDATORY)
- **OBSERVABILITY:** Long real-data jobs must use unbuffered output (`python -u`). Keep progress printing explicit.
- **NO BLOCKERS TOLERATED:** If any path is slow, redundant, unclear, or bottlenecking throughput/insight, **ELIMINATE IT IMMEDIATELY** before adding features. Do not work around inefficiencies.
- **REMOVE FRICTION:** Tighten schemas, harden tests, improve clarity, and remove anything that could allow a future agent to take an easy shortcut.
- **FORCE HEAVY WORK:** Design every step so that future agents cannot avoid substantial, measurable validation work.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (2026-10-30T16:56:15Z)

**OBJECTIVE:** Conduct a **MAXIMUM-INTENSITY, NO-COAST** hardening campaign for the multi-asset crypto stat arb portfolio using **100% REAL Binance data**. Future agents MUST be unable to avoid heavy working. Every action must demonstrably increase real-data validation rigor.

**MANDATORY EXECUTION SEQUENCE (DO NOT SKIP, DO IN ORDER):**

1. **DEEP AUDIT (BRUTALLY HONEST)**
   - Read `examples/run_portfolio_real.py`, `reports/portfolio_real.json`, `tests/test_portfolio_real.py`, `tests/test_portfolio_risk_controls.py`, `backtest/engine.py` (focus `walk_forward_portfolio` + `run_portfolio`), `utils/portfolio_risk.py`, `utils/regime.py`, `data/loader.py`.
   - Find EVERY gap vs the enrichment requirements below. Fix bottlenecks on contact.

2. **VERIFY GREEN (NON-NEGOTIABLE)**
   - `PYTHONPATH=. python -m pytest tests/ -q`
   - `python -m ruff check backtest/ strategies/ utils/ tests/`
   - `python -m mypy backtest/ strategies/ utils/`
   - If red for any reason, restore green before proceeding. Zero regressions.

3. **REGENERATE PORTFOLIO ARTIFACT FROM REAL DATA**
   - Run `python -u examples/run_portfolio_real.py` (end-to-end on real Binance candles with >=12 walk-forward splits).
   - Confirm `reports/portfolio_real.json` is written, JSON-serializable, and `tests/test_portfolio_real.py` passes (n_splits >= 10, per-asset gross <= correlation cap, circuit breaker tested, risk_controller `correlation_aware_cvar_style`).

4. **UNIVERSE EXPANSION (REAL-ONLY, DOCUMENTED)**
   - Aggressively attempt additional real pairs (prioritize BNB/USDT-quoted + liquid majors: DOT, MATIC, AVAX, LINK, etc.) via ONLY `DataLoader.load_binance_data()`.
   - Include only pairs with sufficient overlapping real history. **Explicitly list omissions with rationale**. Never fabricate data.

5. **WALK-FORWARD RIGOR (>=12 SPLITS)**
   - Enforce >= 12 splits with train≈1000/test≈200 where feasible. Capture full IS/OOS per split, stability metrics, degradation curves, and regime-split performance. Make all inspectable in artifact.

6. **META-SELECTOR + RISK CONTROLS (REAL-DRIVEN HARDENING)**
   - Strengthen regime-adaptive multi-signal meta-selector using multiple real signals (vol/trend/mean-reversion) derived from real data; validate OOS.
   - Harden correlation-aware + CVaR-aware limits; enforce hard caps (asset gross exposure <= correlation cap). Test circuit breaker thoroughly on real history.

7. **EXHAUSTIVE FUNDING/BASIS (NO FABRICATION)**
   - Attempt real public Binance funding/basis from multiple public endpoints/hosts with full attempt timestamps/hosts/errors.
   - If retrievable and sensible → integrate with provenance; else **comprehensively document**. **Never fabricate.**

8. **EXECUTION REALISM (GROUNDED)**
   - Add volume-aware/slippage/cost realism using real characteristics where possible; document assumptions explicitly.

9. **ARTIFACT ENRICHMENT (COMPLETE, VALID)**
   - Enrich `reports/portfolio_real.json` with ALL: per-asset contribution, turnover, leverage/gross/net exposure, correlation matrix + correlation stability context, tail metrics (VaR/CVaR/CDaR), regime-conditioned performance, cost-stress slices, funding/basis provenance (full attempts), universe changes + exclusions with rationale, walk-forward IS/OOS per split + stability/degradation.
   - JSON-serializable, schema valid, backward compatible or tests updated.

10. **TESTS + DOCS (HARDEN COVERAGE)**
    - Add **network-independent** stress tests for portfolio logic, risk controls, meta-selector, artifact schema, edge cases.
    - Update `README.md` with hardened findings, **concrete real-data numbers**, explicit **real-data-only provenance**, coverage summary. Make it impossible to miss the real-data mandate.

11. **VERIFY & DELIVER (ZERO REGRESSIONS)**
    - Regenerate `reports/portfolio_real.json` using **real data only**.
    - Final checks: `PYTHONPATH=. python -m pytest tests/ -q` (>=527 passed, 0 new failures), `python -m ruff check backtest/ strategies/ utils/ tests/` (clean), `python -m mypy backtest/ strategies/ utils/` (clean).
    - All deliverables present and valid.

**HARD CONSTRAINTS:**
- **REAL DATA ONLY.** No synthetic/fabricated data of any kind.
- **NO SHORTCUTS.** Omit+document if unavailable after exhaustive attempts.
- **PRESERVE GREEN.** Never introduce regressions.
- **HEAVY MANDATE.** Substantial hardening required - complete the full campaign.
- **BOTTLENECK REMOVAL.** Eliminate inefficiencies blocking progress immediately.
- **IMPOSSIBLE TO AVOID:** Structure work so next agents cannot coast.

**CAMPAIGN COMPLETE ONLY WHEN ALL CRITERIA MET. START IMMEDIATELY. EXECUTE FULL CAMPAIGN WITHOUT EARLY STOP.**
