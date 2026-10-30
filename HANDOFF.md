# DURABLE HANDOFF (2026-10-30T19:11:23Z) — SINGLE MANDATORY NEXT TASK: CRYPTO STAT ARB UNIVERSE HARDENING + PORTFOLIO SCALE-UP

## REPO NAME IS THE LAW
- **REPO:** `cryptoquantstatarbstrats` — *Crypto Quant Stat Arb Strategies*
- **ABSOLUTE MANDATE:** Research, build, harden, and relentlessly validate crypto statistical-arbitrage strategies using **ONLY REAL market data**.
- **PRIORITY:** Real-data validation > everything else. Coasting is FORBIDDEN. Every session must produce measurable increases in real-data validation rigor.

## VERIFIED GREEN STATE (MUST PRESERVE)
- **Branch:** `main` (clean)
- **Tests:** `PYTHONPATH=. python -m pytest tests/ -q` → **527 passed, 1 skipped**
- **Lint:** `python -m ruff check backtest/ strategies/ utils/ tests/` → **All checks passed**
- **Types:** `python -m mypy backtest/ strategies/ utils/` → **Success: no issues found in 31 source files**
- **Real data only:** `DataLoader.load_binance_data()` uses public Binance REST. Never fabricate candles/IV/funding/basis.

## BOTTLENECK ELIMINATION (MANDATORY)
- **Unbuffered:** Use `python -u` for all long real-data jobs.
- **Progress:** Add explicit logging/progress for fetches/sweeps.
- **Parallelize safely:** Batch independent pair fetches/sweeps where deterministic/network-safe.
- **Kill friction:** Fix slow/unclear paths now; tighten schemas/tests.
- **No workarounds:** Omit+document only after exhaustive attempts with full provenance.
- **Network:** Retry with backoff on public Binance endpoints; log every attempt/failure.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (TIMESTAMP: 2026-10-30T19:11:23Z)

**START IMMEDIATELY. DO NOT STOP EARLY. HEAVY WORK IS THE ONLY ACCEPTABLE OUTCOME.**

### OBJECTIVE
Scale and harden the crypto stat arb portfolio to a broader real universe with multi-timeframe walk-forward, bootstrap significance, volume-aware execution realism, and ironclad provenance. Make it impossible for future agents to coast.

### MANDATORY SEQUENCE (IN ORDER, NO SKIPPING)

1. **VERIFY GREEN**
   `PYTHONPATH=. python -m pytest tests/ -q && python -m ruff check backtest/ strategies/ utils/ tests/ && python -m mypy backtest/ strategies/ utils/`
   Restore green before proceeding if anything regresses.

2. **BRUTALLY HONEST AUDIT**
   Read `examples/run_portfolio_real.py`, `reports/portfolio_real.json`, `tests/test_portfolio_real.py`, `tests/test_portfolio_risk_controls.py`, `backtest/engine.py` (walk_forward_portfolio/run_portfolio), `utils/portfolio_risk.py`, `utils/regime.py`, `data/loader.py`. Fix every bottleneck on contact. Eliminate shortcut affordances.

3. **UNIVERSE EXPANSION (REAL-ONLY)**
   Aggressively attempt additional real pairs via `DataLoader.load_binance_data()`: BNB/USDT-quoted + liquid majors (DOT, MATIC, AVAX, LINK) and any others with sufficient overlapping real history. Only include pairs passing cointegration/stability on the full real window. Explicitly list EVERY omission with rationale in the artifact. Never fabricate. Update `PAIRS`/`SYMBOLS` in `examples/run_portfolio_real.py`. Adjust risk controls if needed without weakening rigor.

4. **MULTI-TIMEFRAME WALK-FORWARD (>=12 SPLITS)**
   Run walk-forward on 1h, 4h, 1d with train≈1000/test≈200 where feasible, >=12 rolling splits each. Capture IS/OOS per split, stability, degradation, regime-split per timeframe. Make inspectable with full provenance.

5. **STATISTICAL SIGNIFICANCE (BOOTSTRAP CI)**
   Bootstrap/shuffle Monte Carlo on real OOS portfolio returns; report 95% CIs for total return, Sharpe, max drawdown (per timeframe + portfolio). State whether edge is distinguishable from zero and from transaction costs. Use network-independent bootstrap in tests.

6. **VOLUME-AWARE EXECUTION REALISM**
   Fetch real Binance quote volume per symbol for full window. Build volume-aware slippage/participation cost model. Add cost-stress grid (fee × slippage × participation) with explicit assumptions. Integrate into artifact with provenance.

7. **ARTIFACT ENRICHMENT**
   Enrich `reports/portfolio_real.json` (or `reports/portfolio_real_expanded.json`) with: per-timeframe IS/OOS per split + stability/degradation, bootstrap CI blocks, volume-aware execution + cost-stress, per-asset contribution, turnover, leverage/gross/net exposure, correlation matrix + stability, tail metrics (VaR/CVaR/CDaR), regime-conditioned performance, funding/basis provenance (full attempts/errors/hosts), universe changes + exclusions with rationale. Must be JSON-serializable, schema-valid, backward compatible or tests updated. Include `real_data_only: true`, `fabricated_data: false`.

8. **TESTS + DOCS HARDEN**
   Add network-independent stress tests for portfolio logic, risk controls, meta-selector, artifact schema, edge cases, bootstrap CI, execution model. Update `README.md` with hardened findings, concrete real-data numbers, explicit real-data-only provenance, coverage summary. Make mandate impossible to miss.

9. **VERIFY & DELIVER (ZERO REGRESSIONS)**
   Regenerate artifact with real data only: `python -u examples/run_portfolio_real.py`
   `PYTHONPATH=. python -m pytest tests/ -q` (>=527 passed, 0 new failures)
   `python -m ruff check backtest/ strategies/ utils/ tests/` (clean)
   `python -m mypy backtest/ strategies/ utils/` (clean)
   All deliverables present/valid. Commit only if explicitly requested.

### HARD CONSTRAINTS
- **REAL DATA ONLY** — No synthetic/fabricated data. Ever.
- **NO SHORTCUTS** — Omit+document if unavailable after exhaustive attempts with full provenance.
- **PRESERVE GREEN** — Zero regressions. Restore green before proceeding.
- **HEAVY MANDATE** — Complete full campaign. Do not stop early.
- **BOTTLENECK REMOVAL** — Eliminate inefficiencies immediately.
- **IMPOSSIBLE TO COAST** — Structure so future agents cannot avoid heavy validation.
- **UNBUFFERED OUTPUT** — Use `python -u` for all long-running real-data jobs.

**CAMPAIGN COMPLETE ONLY WHEN ALL CRITERIA MET. START IMMEDIATELY.**
