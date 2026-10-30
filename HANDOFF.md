# DURABLE HANDOFF (2026-10-30T19:18:24Z) — SINGLE MANDATORY NEXT TASK: CRYPTO STAT ARB MULTI-TIMEFRAME SCALE-UP + TRUE OOS RIGOR

## REPO NAME IS THE LAW
- **REPO:** `cryptoquantstatarbstrats` — *Crypto Quant Stat Arb Strategies*
- **ABSOLUTE MANDATE:** Research, build, harden, and relentlessly validate crypto statistical-arbitrage strategies using **ONLY REAL market data**.
- **PRIORITY:** Real-data validation > everything else. Coasting is FORBIDDEN. Every session must produce measurable increases in real-data validation rigor.
- **HEAVY WORK ONLY.** Future agents cannot avoid doing heavy work — every step must produce checkable artifacts/tests.

## VERIFIED GREEN STATE (PRESERVE AT ALL COSTS)
- **Branch:** `main` (clean)
- **Tests:** `PYTHONPATH=. python -m pytest tests/ -q` → **527 passed, 1 skipped** (GREEN)
- **Types:** `python -m mypy backtest/ strategies/ utils/` → **Success: no issues found in 31 source files** (GREEN)
- **Lint:** `python -m ruff check backtest/ strategies/ utils/ tests/` → **All checks passed!** (GREEN)
- **Real data only:** `DataLoader.load_binance_data()` uses public Binance REST (network verified live). Never fabricate candles/IV/funding/basis.
- **Latest artifact:** `reports/portfolio_real.json` generated via `python -u examples/run_portfolio_real.py` (real-only). Portfolio currently -4.54% total return, Sharpe -2.05, max DD -6.40% on 5108 hourly bars (2026-04-01 to 2026-10-30).

## BOTTLENECK ELIMINATION (DO FIRST, EVERY SESSION)
- **Unbuffered:** Use `python -u` for all long real-data jobs.
- **Progress:** Add explicit logging/progress for fetches/sweeps; print per-pair status.
- **Parallelize safely:** Batch independent pair fetches/sweeps where deterministic/network-safe.
- **Network resilience:** Retry with backoff on public Binance endpoints; log every attempt/failure/host.
- **No workarounds:** Omit+document only after exhaustive attempts with full provenance.
- **Zero regressions:** Fix any lint/type/test break immediately before moving forward.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (TIMESTAMP: 2026-10-30T19:18:24Z)

**START IMMEDIATELY. DO NOT STOP EARLY. HEAVY WORK IS THE ONLY ACCEPTABLE OUTCOME.**

### OBJECTIVE
Aggressively expand universe, enforce true multi-timeframe walk-forward rigor (>=12 splits per TF), add bootstrap significance with CIs, volume-aware execution realism, and ironclad provenance. Make the strategy demonstrably harder to overfit and impossible to coast.

### MANDATORY SEQUENCE (IN ORDER, NO SKIPPING)

**0. UNBLOCK / RESTORE GREEN**
```bash
python -m ruff check backtest/ strategies/ utils/ tests/ && \
PYTHONPATH=. python -m pytest tests/ -q && \
python -m mypy backtest/ strategies/ utils/
```
Do not proceed until all green.

**1. BRUTALLY HONEST AUDIT**
Read `examples/run_portfolio_real.py`, `reports/portfolio_real.json`, `tests/test_portfolio_real.py`, `tests/test_portfolio_risk_controls.py`, `backtest/engine.py` (walk_forward_portfolio/run_portfolio), `utils/portfolio_risk.py`, `utils/regime.py`, `data/loader.py`. Fix bottlenecks on contact. Eliminate shortcut affordances.

**2. UNIVERSE EXPANSION (REAL-ONLY)**
Aggressively attempt BNB/USDT-quoted + liquid majors (DOT, MATIC, AVAX, LINK, LTC, BCH, ETC). Only include if passing cointegration/stability on full real window with full provenance. Explicitly list EVERY omission with rationale. Update `PAIRS`/`SYMBOLS` in `examples/run_portfolio_real.py`. Never fabricate.

**3. MULTI-TIMEFRAME WALK-FORWARD (>=12 SPLITS EACH)**
Run walk-forward on 1h, 4h, 1d with train≈1000/test≈200 (adjust for TF length) >=12 rolling splits. Capture IS/OOS per split, stability, degradation, regime-split. Full provenance required.

**4. STATISTICAL SIGNIFICANCE (BOOTSTRAP CI)**
Bootstrap/shuffle Monte Carlo on real OOS portfolio returns; report 95% CIs for total return, Sharpe, max drawdown (per TF + portfolio). State distinguishability from zero and transaction costs. Network-independent.

**5. VOLUME-AWARE EXECUTION REALISM**
Fetch real Binance quote volume per symbol for full window. Build volume-aware slippage/participation model. Add cost-stress grid (fee × slippage × participation). Integrate with provenance.

**6. ARTIFACT ENRICHMENT**
Enrich `reports/portfolio_real_expanded.json` (or update `reports/portfolio_real.json`) with: per-TF IS/OOS per split + stability/degradation, bootstrap CI blocks, volume-aware execution + cost-stress, per-asset contribution, turnover, leverage/gross/net exposure, correlation matrix + stability, tail metrics (VaR/CVaR/CDaR), regime-conditioned performance, funding/basis provenance (full attempts/errors/hosts), universe changes + exclusions with rationale. Must be JSON-serializable, schema-valid, backward compatible or tests updated. Include `real_data_only: true`, `fabricated_data: false`.

**7. TESTS + DOCS HARDEN**
Add network-independent stress tests for portfolio logic, risk controls, meta-selector, artifact schema, edge cases, bootstrap CI, execution model. Update `README.md` with hardened findings, concrete real-data numbers, explicit real-data-only provenance, coverage summary.

**8. VERIFY & DELIVER (ZERO REGRESSIONS)**
```bash
python -u examples/run_portfolio_real.py
PYTHONPATH=. python -m pytest tests/ -q  # >=527 passed, 0 new failures
python -m ruff check backtest/ strategies/ utils/ tests/  # clean
python -m mypy backtest/ strategies/ utils/  # clean
```
All deliverables present/valid. Commit only if explicitly requested.

### HARD CONSTRAINTS
- **REAL DATA ONLY** — No synthetic/fabricated data. Ever.
- **NO SHORTCUTS** — Omit+document if unavailable after exhaustive attempts with full provenance.
- **PRESERVE GREEN** — Zero regressions. Restore green before proceeding.
- **HEAVY MANDATE** — Complete full campaign. Do not stop early.
- **BOTTLENECK REMOVAL** — Eliminate inefficiencies immediately.
- **IMPOSSIBLE TO COAST** — Structure so future agents cannot avoid heavy validation; every step produces a checkable artifact or test.
- **UNBUFFERED OUTPUT** — Use `python -u` for all long-running real-data jobs.

**CAMPAIGN COMPLETE ONLY WHEN ALL CRITERIA MET. START IMMEDIATELY.**
