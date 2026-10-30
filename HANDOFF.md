# DURABLE HANDOFF (2026-10-30T21:16:00Z) — SINGLE MANDATORY NEXT TASK: CRYPTO STAT ARB SCALE-UP (OPTIMIZED FOR HEAVY EXECUTION)

## REPO IDENTITY (LAW)
- **REPO:** `cryptoquantstatarbstrats` — *Crypto Quant Stat Arb Strategies*
- **PRIORITY:** Pure real-data crypto statistical arbitrage. Market microstructure, pair stability, and falsifiability take precedence over anything else.
- **MANDATE:** **ONLY REAL market data** (Binance public REST). Never fabricate candles, funding, basis, IV, or volume. Synthetic data is strictly limited to isolated unit tests with explicit `fabricated_data: true` warnings.
- **COASTING = FAILURE.** Every action must produce checkable artifacts, tests, provenance, and logs. Future agents cannot avoid heavy validation.

## VERIFIED GREEN STATE (PRESERVE)
- **Branch:** `main` (clean merge state in progress)
- **Tests:** `PYTHONPATH=. python -m pytest tests/ -q` → **527 passed, 1 skipped** (GREEN)
- **Types:** `python -m mypy backtest/ strategies/ utils/` → **Success: no issues found in 31 source files** (GREEN)
- **Lint:** `python -m ruff check backtest/ strategies/ utils/ tests/` → **All checks passed!** (GREEN)
- **Baseline:** `reports/portfolio_real.json` (real-only). ~ -4.54% total return, Sharpe ~ -2.05, max DD ~ -6.40% (5108 hourly bars 2026-04-01 to 2026-10-30), 10 pairs / 6 symbols.

## BOTTLENECKS TO ELIMINATE (DO FIRST)
These are the known friction points blocking scale. Fix them before expanding the universe:

- **I/O:** Run all long jobs with `python -u`. Add explicit `flush=True` where logs are critical.
- **Network:** Enforce exponential backoff + retries on all Binance calls. Log **every** attempt (host, endpoint, status, ms). Treat partial pages as failures if not fully accounted for. Do **one bounded Binance connectivity preflight** per material network-state change. Treat permanent HTTP 451/403/404 as a blocked route; do not repeat identical requests or exhaustively retry permanent responses.
- **Parallelism:** Batch independent fetches/sweeps safely with deterministic ordering and bounded concurrency. No cross-contamination of state between symbols/pairs. Persist each completed symbol/timeframe shard so restarts skip verified work.
- **Data Completeness:** If overlapping real history is insufficient for the window/TF, **EXCLUDE** with a full rationale + attempt log. Never backfill or interpolate. If not supported, label affected timeframe/symbol BLOCKED/INSUFFICIENT_HISTORY rather than waiting, inventing bars, or silently reducing standards.
- **Determinism:** Fix seeds for all stochastic code paths (bootstrap/MC). Log seeds + config in artifacts.
- **Observability:** Per-pair/per-symbol/per-TF/per-split logging (bar counts, date ranges, gaps, NaNs). No silent passes/failures.
- **Scheduling:** Convert work into a dependency-aware task graph. Start independent, network-independent work (tests/schema validation, cached-data analysis, bootstrap/risk/execution modeling) while data sources are blocked. Profile long phases and checkpoint intermediates. Run affected tests after each logical change; full gates once after coherent batch and at final acceptance.
- **Regressions:** If lint/type/test break at any point, fix immediately. Do not proceed until green.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (TIMESTAMP: 2026-10-30T21:16:00Z)

**START NOW. DO NOT STOP EARLY. HEAVY WORK IS MANDATORY.**

### PRIMARY OBJECTIVE
Harden and scale this real-data stat arb system to be **un-coastable**. Aggressively expand the universe with provable liquidity/overlap, enforce >=12 rolling splits across 1h/4h/1d, add bootstrap significance (95% CIs), model volume-aware execution + cost stress, and emit a fully schema-enriched `portfolio_real` artifact with ironclad provenance. Every step must leave verifiable artifacts and tests. Remove avoidable serial waiting while maintaining the same data/statistical standards.

### MANDATORY SEQUENCE (IN ORDER, NO SKIPPING)

#### 0. UNBLOCK / RESTORE GREEN (BLOCKING)
```bash
python -m ruff check backtest/ strategies/ utils/ tests/ && \
PYTHONPATH=. python -m pytest tests/ -q && \
python -m mypy backtest/ strategies/ utils/
```
Do not proceed until all three pass. Fix anything broken first.

#### 1. BRUTAL AUDIT (MAP BOTTLENECKS)
Read and attack:
- `examples/run_portfolio_real.py` (flow, risk controls, provenance)
- `reports/portfolio_real.json` (baseline)
- `tests/test_portfolio_real.py`, `tests/test_portfolio_risk_controls.py`
- `backtest/engine.py` (walk_forward_portfolio/run_portfolio)
- `utils/portfolio_risk.py`, `utils/regime.py`, `utils/monte_carlo.py`
- `data/loader.py`, `strategies/pairs_trading.py`, `backtest/sweep.py`

Eliminate any code path that could mask missing real data. Fix bottlenecks on contact. Identify independent workstreams to parallelize.

#### 2. UNIVERSE EXPANSION (REAL-ONLY, PROVEN)
Aggressively attempt expansion: **BNB/USDT, DOT/USDT, MATIC/USDT, AVAX/USDT, LINK/USDT, LTC/USDT, BCH/USDT, ETC/USDT, NEAR/USDT, ARB/USDT, OP/USDT, INJ/USDT** and others only if provably liquid with full overlap.

For **EVERY** candidate:
- Fetch real Binance spot history for required windows/TFs via `python -u` with retries, exponential backoff, full attempt logs (hosts/endpoints/timings/failures)
- Verify overlap, gap count, bar count, and basic quality
- Only admit if it passes cointegration/stability on the full real window with complete provenance

Update `PAIRS`/`SYMBOLS` in `examples/run_portfolio_real.py`. Record **every** inclusion/exclusion in `universe_changes` and `exclusions_with_rationale` with attempt counts and hosts. **Never fabricate.**

#### 3. MULTI-TIMEFRAME WALK-FORWARD RIGOR (>=12 SPLITS EACH)
Enforce true rolling walk-forward on **1h, 4h, 1d**:
- >= 12 rolling splits per TF (increase if fewer)
- Sensible train/test lengths per TF (document rationale)
- Per-split IS/OOS, stability, degradation, and regime-split
- Aggregate + per-pair/per-TF breakdowns
- Full provenance (params, windows, bar counts)

Emit under `multi_timeframe_walk_forward` with complete per-split detail.

#### 4. STATISTICAL SIGNIFICANCE (BOOTSTRAP CI)
Bootstrap/shuffle Monte Carlo on **real OOS portfolio returns**:
- >= 2000 simulations, fixed seed, reproducible
- 95% CIs for total return, Sharpe, max drawdown (per TF + portfolio)
- Distinguishability from zero + impact of transaction costs
- Network-independent execution
- Attach under `bootstrap_ci_portfolio_oos` with full config

#### 5. VOLUME-AWARE EXECUTION REALISM + COST-STRESS
- Fetch real Binance quote volume per symbol for the full window (exhaustive attempts, log hosts/failures). Omit only with full rationale if truly unavailable after exhaustive attempts.
- Build a volume-aware slippage/participation model (document assumptions, never fabricate)
- Add a broad **cost-stress grid** (fees × slippage × participation) integrated with provenance
- Include under `volume_aware_execution`

#### 6. ARTIFACT ENRICHMENT (COMPREHENSIVE, SCHEMA-VALID)
Enrich `reports/portfolio_real.json` (update in-place if compatible, else `reports/portfolio_real_expanded.json` with backward compatibility). Must include:
- `real_data_only: true`, `fabricated_data: false`
- Per-TF IS/OOS per split + stability/degradation
- Bootstrap CI blocks (95% CIs) for return/Sharpe/maxDD
- Volume-aware execution + full cost-stress grid
- Per-asset contribution, turnover, leverage/gross/net exposure
- Correlation matrix + rolling stability
- Tail metrics (VaR/CVaR/CDaR)
- Regime-conditioned performance
- Funding/basis provenance (full attempts/errors/hosts) — omit only after exhaustive attempts with rationale
- Universe changes + exclusions with rationale + attempt logs
- Risk controls applied, circuit breaker results
- Multi-timeframe results with >=12 splits each
- JSON-serializable and validated by tests

#### 7. TESTS + DOCS HARDEN (MAKE IT IMPOSSIBLE TO COAST)
- Add network-independent stress tests: portfolio logic, risk controls, meta-selector, artifact schema, bootstrap CI, execution model, edge cases
- Update `README.md` with hardened findings, concrete real-data numbers, explicit real-data-only provenance, coverage summary
- Strengthen assertions around `real_data_only`/`fabricated_data`
- Ensure new fields are validated or explicitly tested

#### 8. VERIFY & DELIVER (ZERO REGRESSIONS)
```bash
python -u examples/run_portfolio_real.py
PYTHONPATH=. python -m pytest tests/ -q  # >=527 passed, 0 new failures
python -m ruff check backtest/ strategies/ utils/ tests/  # clean
python -m mypy backtest/ strategies/ utils/  # clean
```
All deliverables must be present and valid. Commit only if explicitly requested.

## HARD CONSTRAINTS
- **REAL DATA ONLY** — No synthetic/fabricated data. Ever.
- **NO SHORTCUTS** — Omit+document if unavailable after exhaustive attempts with full provenance (hosts, endpoints, errors, counts).
- **PRESERVE GREEN** — Zero regressions. Restore green before proceeding.
- **HEAVY MANDATE** — Complete the full campaign. Do not stop early.
- **BOTTLENECK REMOVAL** — Eliminate inefficiencies immediately (parallelize, retry, log, unbuffer, checkpoint shards).
- **IMPOSSIBLE TO COAST** — Structure work so future agents cannot avoid heavy validation; every step must produce a checkable artifact/test/provenance.
- **UNBUFFERED OUTPUT** — Use `python -u` for all long-running real-data jobs.
- **REPRODUCIBILITY** — Seeds for stochastic parts; log all config.
- **NO ALTERATION OF LIVE/PAPER BOUNDARIES** — Do not change trading boundaries or commit policy.

**CAMPAIGN COMPLETE ONLY WHEN ALL CRITERIA MET. START IMMEDIATELY.**
