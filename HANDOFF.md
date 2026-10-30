# DURABLE HANDOFF (2026-10-30T20:35:50Z) — SINGLE MANDATORY NEXT TASK: CRYPTO QUANT STAT ARB HARDENING + SCALE-UP (FORCE HEAVY WORK)

## REPO IDENTITY (LAW)
- **REPO:** `cryptoquantstatarbstrats` — *Crypto Quant Stat Arb Strategies*
- **PRIORITY:** Real crypto statistical arbitrage, market microstructure, falsifiability, and ironclad provenance. Nothing else matters.
- **MANDATE:** Use **ONLY REAL market data** (Binance public REST). Never fabricate candles/IV/funding/basis. Synthetic only for isolated unit tests with explicit warnings.
- **COASTING = FAILURE.** Every action must produce checkable artifacts/tests/provenance. Future agents cannot avoid heavy work.

## VERIFIED GREEN STATE (PRESERVE)
- **Branch:** `main` (clean)
- **Tests:** `PYTHONPATH=. python -m pytest tests/ -q` → **527 passed, 1 skipped** (GREEN)
- **Types:** `python -m mypy backtest/ strategies/ utils/` → **Success: no issues found in 31 source files** (GREEN)
- **Lint:** `python -m ruff check backtest/ strategies/ utils/ tests/` → **All checks passed!** (GREEN)
- **Baseline:** `reports/portfolio_real.json` (real-only). Current portfolio ~ -4.54% total return, Sharpe ~ -2.05, max DD ~ -6.40% (5108 hourly bars 2026-04-01 to 2026-10-30), 10 pairs/6 symbols.

## BOTTLENECK ELIMINATION (DO FIRST, NO WORKAROUNDS)
Fix or enforce these immediately:
- **Unbuffered I/O:** Run all long jobs with `python -u`. Add explicit flushes where helpful.
- **Observability:** Per-pair/per-symbol/per-split/per-TF logging (counts, ranges, hosts, timings, failures). No silent loops.
- **Network resilience:** Exponential backoff + retries on public Binance endpoints. Log EVERY attempt/failure/host. Full attempt trail required.
- **Parallelize safely:** Batch independent fetches/sweeps where deterministic/network-safe. No shared-state cross-contamination.
- **Data completeness:** Exclude if insufficient overlapping real history for window/TF. EXCLUDE with full rationale + attempt log. NEVER backfill/fabricate.
- **Determinism:** Seeds for stochastic (bootstrap/MC). Log all seeds/config.
- **Zero regressions:** Fix lint/type/test breaks IMMEDIATELY.
- **No shortcuts:** If tempted to hardcode/synthesize/mask missing data → stop and document exhaustive attempts.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (TIMESTAMP: 2026-10-30T20:35:50Z)

**START NOW. DO NOT STOP EARLY. HEAVY WORK IS MANDATORY.**

### PRIMARY OBJECTIVE
Aggressively expand real-data universe, enforce true multi-timeframe walk-forward rigor (>= 12 rolling splits per TF on 1h/4h/1d), add bootstrap significance with 95% CIs, implement volume-aware execution realism + cost-stress grids, harden ironclad provenance, and make overfit impossible to coast. Every step must leave checkable artifacts/tests/provenance.

### MANDATORY SEQUENCE (IN ORDER, NO SKIPPING)

#### 0. UNBLOCK / RESTORE GREEN (BLOCKING)
```bash
python -m ruff check backtest/ strategies/ utils/ tests/ && \
PYTHONPATH=. python -m pytest tests/ -q && \
python -m mypy backtest/ strategies/ utils/
```
Do not proceed until ALL green. Fix first.

#### 1. BRUTALLY HONEST AUDIT (MAP BOTTLENECKS)
Read/audit:
- `examples/run_portfolio_real.py` (flow, risk controls, provenance)
- `reports/portfolio_real.json` (baseline)
- `tests/test_portfolio_real.py`, `tests/test_portfolio_risk_controls.py`
- `backtest/engine.py` (walk_forward_portfolio/run_portfolio)
- `utils/portfolio_risk.py`, `utils/regime.py`, `utils/monte_carlo.py`
- `data/loader.py`, `strategies/pairs_trading.py`, `backtest/sweep.py`

Fix bottlenecks on contact. Eliminate any logic that could mask missing real data.

#### 2. UNIVERSE EXPANSION (REAL-ONLY, PROVEN)
Aggressively attempt: **BNB/USDT-quoted majors + DOT, MATIC, AVAX, LINK, LTC, BCH, ETC, NEAR, ARB, OP, INJ** (and others only if liquid with full overlap). For EVERY candidate:
- Fetch real Binance spot history for full requested window per TF as needed (use `python -u`, retries, backoff, log hosts/attempts)
- Verify overlap, bar count, data quality
- Only include if passes cointegration/stability on full real window with full provenance

Update `PAIRS`/`SYMBOLS` in `examples/run_portfolio_real.py`. Explicitly list **EVERY** inclusion/exclusion with rationale + attempt counts/hosts in `universe_changes` and `exclusions_with_rationale`. **Never fabricate.**

#### 3. MULTI-TIMEFRAME WALK-FORWARD RIGOR (>=12 SPLITS EACH)
Enforce true rolling walk-forward on **1h, 4h, 1d** with:
- >= 12 rolling splits per TF (increase if < 12)
- Sensible train/test lengths per TF (adapt to bars; document choices)
- Per-split IS/OOS returns, stability, degradation, regime-split
- Aggregate stats + per-pair/per-TF breakdowns
- Full provenance (params, windows, counts)
Emit under `multi_timeframe_walk_forward` with complete per-split detail.

#### 4. STATISTICAL SIGNIFICANCE (BOOTSTRAP CI)
Bootstrap/shuffle Monte Carlo on **real OOS portfolio returns**:
- >= 2000 simulations, fixed seed, reproducible
- Report **95% CIs** for total return, Sharpe, max drawdown (per TF + portfolio)
- Test distinguishability from zero; state impact of transaction costs
- Network-independent; document method
- Attach under `bootstrap_ci_portfolio_oos` with full config

#### 5. VOLUME-AWARE EXECUTION REALISM + COST-STRESS
- Fetch real Binance quote volume per symbol for full window (exhaustive attempts, log hosts/failures)
- Build volume-aware slippage/participation model (document assumptions; no fabrication)
- Add broad **cost-stress grid** (fee × slippage × participation) integrated with provenance
- Include in artifact under `volume_aware_execution`

#### 6. ARTIFACT ENRICHMENT (COMPREHENSIVE, SCHEMA-VALID)
Enrich `reports/portfolio_real.json` (or `reports/portfolio_real_expanded.json` if schema drift, prefer in-place update with backward compatibility). Must include:
- `real_data_only: true`, `fabricated_data: false`
- Per-TF IS/OOS per split + stability/degradation
- Bootstrap CI blocks (95% CIs) for return/Sharpe/maxDD
- Volume-aware execution + full cost-stress grid
- Per-asset contribution, turnover, leverage/gross/net exposure
- Correlation matrix + stability (rolling)
- Tail metrics (VaR/CVaR/CDaR)
- Regime-conditioned performance
- Funding/basis provenance (full attempts/errors/hosts) — omit only after exhaustive attempts with rationale
- Universe changes + exclusions with rationale + attempt logs
- Risk controls applied, circuit breaker results
- Multi-timeframe results with >=12 splits each
- JSON-serializable, tests still pass

#### 7. TESTS + DOCS HARDEN (MAKE IT IMPOSSIBLE TO COAST)
- Add network-independent stress tests for portfolio logic, risk controls, meta-selector, artifact schema, bootstrap CI, execution model, edge cases
- Update `README.md` with hardened findings, concrete real-data numbers, explicit real-data-only provenance, coverage summary
- Ensure new fields validated or tests updated
- Strengthen assertions around real-data-only flags

#### 8. VERIFY & DELIVER (ZERO REGRESSIONS)
```bash
python -u examples/run_portfolio_real.py
PYTHONPATH=. python -m pytest tests/ -q  # >=527 passed, 0 new failures
python -m ruff check backtest/ strategies/ utils/ tests/  # clean
python -m mypy backtest/ strategies/ utils/  # clean
```
All deliverables present/valid. Commit only if explicitly requested.

### HARD CONSTRAINTS
- **REAL DATA ONLY** — No synthetic/fabricated data. Ever.
- **NO SHORTCUTS** — Omit+document if unavailable after exhaustive attempts with full provenance (hosts, errors, counts).
- **PRESERVE GREEN** — Zero regressions. Restore green before proceeding.
- **HEAVY MANDATE** — Complete full campaign. Do not stop early.
- **BOTTLENECK REMOVAL** — Eliminate inefficiencies immediately (parallelize, retry, log, unbuffer).
- **IMPOSSIBLE TO COAST** — Structure so future agents cannot avoid heavy validation; every step produces checkable artifact/test/provenance.
- **UNBUFFERED OUTPUT** — Use `python -u` for all long-running real-data jobs.
- **REPRODUCIBILITY** — Seeds for stochastic parts; log all config.

**CAMPAIGN COMPLETE ONLY WHEN ALL CRITERIA MET. START IMMEDIATELY.**
