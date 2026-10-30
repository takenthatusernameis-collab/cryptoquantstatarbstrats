# DURABLE HANDOFF (2026-10-30T19:09:28Z) — SINGLE MANDATORY NEXT TASK: MAX-INTENSITY REAL-DATA EXPANSION CAMPAIGN

## REPO NAME IS THE LAW
- **REPO:** `cryptoquantstatarbstrats` — *Crypto Quant Stat Arb Strategies*
- **ABSOLUTE MANDATE:** This codebase exists SOLELY to research, build, harden, and relentlessly validate crypto statistical-arbitrage strategies using **ONLY REAL market data**.
- **NON-NEGOTIABLE PRIORITY:** Real-data validation > everything else. If torn between convenience and heavier real-data work, **ALWAYS choose the heavier path**. Coasting is FORBIDDEN.
- **IMPOSSIBLE TO AVOID:** Every session must produce measurable increases in real-data validation rigor. No exploratory toy work. No synthetic shortcuts.

## PRIOR CAMPAIGN COMPLETE (2026-10-30T17:03:41Z → 2026-10-30T17:32:50Z)
- All 11 steps of the prior "MAXIMUM REAL-DATA HEAVY VALIDATION" campaign executed.
- Artifact `reports/portfolio_real.json` regenerated from 100% real Binance spot candles (2026-04-01 → 2026-10-30, 5107 bars, 10 pairs, >=12 walk-forward splits).
- `examples/run_portfolio_real.py` hardened: regime-adaptive meta-selector, correlation-aware + CVaR-style risk controls, circuit breaker tested, funding/basis exhaustively attempted (no fabrication), cost-stress slices, per-asset contribution, turnover, leverage/exposure, correlation stability, regime-conditioned performance.
- `tests/test_portfolio_real.py` + `tests/test_portfolio_risk_controls.py` added (network-independent).

## VERIFIED GREEN STATE (MUST PRESERVE) — 2026-10-30T19:09:28Z (re-verified this session)
- **Branch:** `main` (clean)
- **Tests:** `PYTHONPATH=. python -m pytest tests/ -q` → **527 passed, 1 skipped**
- **Lint:** `python -m ruff check backtest/ strategies/ utils/ tests/` → **All checks passed**
- **Types:** `python -m mypy backtest/ strategies/ utils/` → **Success: no issues found in 31 source files**
- **Real data:** `DataLoader.load_binance_data()` uses public Binance REST (real spot candles only). **NEVER fabricate candles/IV/funding/basis.**
- **Key artifacts:** `examples/run_portfolio_real.py`, `reports/portfolio_real.json`, `tests/test_portfolio_real.py`, `tests/test_portfolio_risk_controls.py`

## BOTTLENECK ELIMINATION (MANDATORY IMMEDIATE ACTION)
- **OBSERVABILITY:** All long real-data jobs MUST use unbuffered output (`python -u`). Add explicit progress logging.
- **KILL FRICTION:** If any code path is slow/redundant/unclear, **ELIMINATE IT NOW**. Tighten schemas, harden tests, improve clarity.
- **FORCE HEAVY WORK:** Structure tasks so future agents cannot take shortcuts. Remove affordances for "quick" runs.
- **PARALLELIZE WHERE SAFE:** For independent pair sweeps/fetches, batch where network-safe and deterministic. Don't duplicate work.
- **NO WORKAROUNDS:** Omit+document only after EXHAUSTIVE attempts with full provenance.
- **NETWORK IS NOT AN EXCUSE:** Public Binance endpoints are available; retry with backoff, document every attempt.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (TIMESTAMP: 2026-10-30T19:09:28Z)

**THIS SESSION (2026-10-30T19:09:28Z):** Verified green state on `main` — 527 passed / 1 skipped, ruff clean, mypy clean (31 files). Working tree clean; nothing is blocked. The campaign below is the **STANDING MANDATORY FOCUS**. Run it immediately, in order, without early stop. **Coasting is FORBIDDEN.**

**OBJECTIVE:** Execute a **MAX-INTENSITY NO-COAST REAL-DATA EXPANSION CAMPAIGN** on the multi-asset crypto stat arb portfolio using **100% REAL Binance data**. Expand the universe to the full liquid majors, extend walk-forward to multi-timeframe/longer horizon, attach statistical-significance (bootstrap CI) to OOS portfolio performance, add volume-aware execution realism, and make it **IMPOSSIBLE** for subsequent agents to avoid substantial real-data validation.

### MANDATORY SEQUENCE (DO IN ORDER, NO SKIPPING)

1. **VERIFY GREEN (NON-NEGOTIABLE)**
   - `PYTHONPATH=. python -m pytest tests/ -q`
   - `python -m ruff check backtest/ strategies/ utils/ tests/`
   - `python -m mypy backtest/ strategies/ utils/`
   - If ANY regression → restore green BEFORE proceeding.

2. **BRUTALLY HONEST AUDIT**
   - Re-read: `examples/run_portfolio_real.py`, `reports/portfolio_real.json`, `tests/test_portfolio_real.py`, `tests/test_portfolio_risk_controls.py`, `backtest/engine.py` (`walk_forward_portfolio` + `run_portfolio`), `utils/portfolio_risk.py`, `utils/regime.py`, `data/loader.py`
   - Fix EVERY bottleneck on contact. Document findings in commit/notes.
   - Eliminate any code that could enable shortcut runs.

3. **UNIVERSE EXPANSION TO FULL MAJORS (REAL-ONLY)**
   - Aggressively attempt additional real pairs: **BNB/USDT-quoted + liquid majors DOT, MATIC, AVAX, LINK** (+ any others with sufficient overlapping real history) via **ONLY** `DataLoader.load_binance_data()`.
   - Include only pairs passing cointegration/stability on the full real window. **Explicitly list EVERY omission with rationale in artifact. NEVER fabricate.**
   - Update `PAIRS` / `SYMBOLS` in `examples/run_portfolio_real.py` and regenerate artifact.
   - If adding pairs requires adjusting risk controls to remain stable, do it WITHOUT weakening real-data rigor.

4. **MULTI-TIMEFRAME WALK-FORWARD (>=12 SPLITS EACH)**
   - Run walk-forward portfolio validation on **1h, 4h, and 1d** timeframes, train≈1000/test≈200 where feasible, >=12 rolling splits each.
   - Capture full IS/OOS per split, stability metrics, degradation curves, regime-split performance per timeframe.
   - Make everything inspectable in artifact with complete provenance.

5. **STATISTICAL SIGNIFICANCE (BOOTSTRAP CI ON PORTFOLIO OOS)**
   - Bootstrap/shuffle Monte Carlo resampling of real-data portfolio OOS returns; confidence intervals for total return, Sharpe ratio, max drawdown (per timeframe and portfolio).
   - Report whether OOS edge is statistically distinguishable from zero and from transaction costs. **No fabricated returns.**
   - Use network-independent bootstrap in tests.

6. **VOLUME-AWARE EXECUTION REALISM**
   - Fetch real Binance volume per symbol (quote volume) for full window; build volume-aware slippage/participation cost model.
   - Cost-stress grid (fee × slippage × participation) with explicit assumptions.
   - Document assumptions explicitly; integrate into artifact cost section with provenance.

7. **ARTIFACT ENRICHMENT (COMPLETE)**
   - Enrich `reports/portfolio_real.json` (or `reports/portfolio_real_expanded.json`) with: per-timeframe IS/OOS per split + stability/degradation, bootstrap CI blocks, volume-aware execution assumptions + cost-stress grid, per-asset contribution, turnover, leverage/gross/net exposure, correlation matrix + correlation stability, tail metrics (VaR/CVaR/CDaR), regime-conditioned performance, funding/basis provenance (full attempts with errors/hosts), universe changes + exclusions with rationale.
   - JSON-serializable, schema-valid, backward compatible or tests updated. Include `real_data_only: true`, `fabricated_data: false`.

8. **TESTS + DOCS (HARDEN)**
   - Add **network-independent** stress tests for portfolio logic, risk controls, meta-selector, artifact schema, edge cases, bootstrap CI, execution model.
   - Update `README.md` with hardened findings, **concrete real-data numbers**, explicit **real-data-only provenance**, coverage summary. Make real-data mandate impossible to miss.
   - Ensure all new code is typed and lint-clean.

9. **VERIFY & DELIVER (ZERO REGRESSIONS)**
   - Regenerate artifact with **real data only** using `python -u examples/run_portfolio_real.py`.
   - `PYTHONPATH=. python -m pytest tests/ -q` (>=527 passed, 0 new failures)
   - `python -m ruff check backtest/ strategies/ utils/ tests/` (clean)
   - `python -m mypy backtest/ strategies/ utils/` (clean)
   - All deliverables present and valid. Working tree clean or changes committed only if explicitly requested.

### HARD CONSTRAINTS
- **REAL DATA ONLY** - No synthetic/fabricated data. Ever.
- **NO SHORTCUTS** - Omit+document if unavailable after exhaustive attempts with full provenance.
- **PRESERVE GREEN** - Zero regressions. Restore green before proceeding.
- **HEAVY MANDATE** - Substantial work required; complete full campaign. Do not stop early.
- **BOTTLENECK REMOVAL** - Eliminate inefficiencies immediately.
- **IMPOSSIBLE TO COAST** - Structure so future agents cannot avoid heavy validation.
- **UNBUFFERED OUTPUT** - Use `python -u` for all long-running real-data jobs.

**CAMPAIGN COMPLETE ONLY WHEN ALL CRITERIA MET. START IMMEDIATELY. EXECUTE WITHOUT EARLY STOP. HEAVY WORK IS THE ONLY ACCEPTABLE OUTCOME.**
